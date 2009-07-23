# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Provides support for handling input events.  This provides several classes
to define input events (InputEvent, KeyboardEvent, BrailleEvent,
MouseButtonEvent, MouseMotionEvent, and SpeechEvent), and also provides a
InputEventHandler class.  It is intended that instances of InputEventHandler
will be used which should be used to handle all input events."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import debug
import settings
import time

KEYBOARD_EVENT     = "keyboard"
BRAILLE_EVENT      = "braille"
MOUSE_BUTTON_EVENT = "mouse:button"
MOUSE_MOTION_EVENT = "mouse:motion"
SPEECH_EVENT       = "speech"

class InputEvent:

    def __init__(self, eventType):
        """Creates a new input event of the given type.

        Arguments:
        - eventType: the input event type (one of KEYBOARD_EVENT, BRAILLE_EVENT,
                MOUSE_BUTTON_EVENT, MOUSE_MOTION_EVENT, SPEECH_EVENT).
        """

        self.type = eventType

class KeyboardEvent(InputEvent):

    def __init__(self, event):
        """Creates a new InputEvent of type KEYBOARD_EVENT.

        Arguments:
        - event: the AT-SPI keyboard event
        """

        # Control characters come through as control characters, so we
        # just turn them into their ASCII equivalent.  NOTE that the
        # upper case ASCII characters will be used (e.g., ctrl+a will
        # be turned into the string "A").  All these checks here are
        # to just do some sanity checking before doing the
        # conversion. [[[WDW - this is making assumptions about
        # mapping ASCII control characters to UTF-8.]]]
        #
        event_string = event.event_string
        if (event.modifiers & settings.CTRL_MODIFIER_MASK) \
            and (not event.is_text) and (len(event_string) == 1):
            value = ord(event.event_string[0])
            if value < 32:
                event_string = chr(value + 0x40)

        # Filter out the NUMLOCK modifier -- it always causes problems.
        #
        event.modifiers = event.modifiers \
                          & settings.ALL_BUT_NUMLOCK_MODIFIER_MASK

        InputEvent.__init__(self, KEYBOARD_EVENT)
        self.type = event.type
        self.hw_code = event.hw_code
        self.modifiers = event.modifiers
        self.event_string = event_string
        self.is_text = event.is_text
        self.time = time.time()
        self.timestamp = event.timestamp

class BrailleEvent(InputEvent):

    def __init__(self, event):
        """Creates a new InputEvent of type BRAILLE_EVENT.

        Arguments:
        - event: the integer BrlTTY command for this event.
        """
        InputEvent.__init__(self, BRAILLE_EVENT)
        self.event = event

class MouseButtonEvent(InputEvent):

    def __init__(self, event):
        """Creates a new InputEvent of type MOUSE_BUTTON_EVENT.
        """
        InputEvent.__init__(self, MOUSE_BUTTON_EVENT)
        self.x = event.detail1
        self.y = event.detail2
        self.pressed = event.type.endswith('p')
        self.button = event.type[len("mouse:button:"):-1]
        self.time = time.time()

class MouseMotionEvent(InputEvent):

    def __init__(self, event):
        """[[[TODO: WDW - undefined at the moment.]]]
        """
        InputEvent.__init__(self, MOUSE_MOTION_EVENT)
        self.event = event

class SpeechEvent(InputEvent):

    def __init__(self, event):
        """[[[TODO: WDW - undefined at the moment.]]]
        """
        InputEvent.__init__(self, SPEECH_EVENT)
        self.event = event

class InputEventHandler:

    def __init__(self, function, description, learnModeEnabled=True):
        """Creates a new InputEventHandler instance.  All bindings
        (e.g., key bindings and braille bindings) will be handled
        by an instance of an InputEventHandler.

        Arguments:
        - function: the function to call with an InputEvent instance as its
                    sole argument.  The function is expected to return True
                    if it consumes the event; otherwise it should return
                    False
        - description: a localized string describing what this InputEvent
                       does
        - learnModeEnabled: if True, the description will be spoken and
                            brailled if learn mode is enabled.  If False,
                            the function will be called no matter what.
        """

        self.function = function
        self.description = description
        self._learnModeEnabled = learnModeEnabled

    def __eq__(self, other):
        """Compares one input handler to another."""
        return (self.function == other.function)

    def processInputEvent(self, script, inputEvent):
        """Processes an input event.  If settings.learnModeEnabled is True,
        this will merely report the description of the input event to braille
        and speech.  If settings.learnModeEnabled is False, this will call the
        function bound to this InputEventHandler instance, passing the
        inputEvent as the sole argument to the function.

        This function is expected to return True if it consumes the
        event; otherwise it is expected to return False.

        Arguments:
        - script:     the script (if any) associated with this event
        - inputEvent: the input event to pass to the function bound
                      to this InputEventHandler instance.
        """

        consumed = False

        if settings.learnModeEnabled and self._learnModeEnabled:
            if self.description:
                # These imports are here to eliminate circular imports.
                #
                import braille
                import speech
                braille.displayMessage(self.description)
                speech.speak(self.description)
                consumed = True
        else:
            try:
                consumed = self.function(script, inputEvent)
            except:
                debug.printException(debug.LEVEL_SEVERE)

        return consumed

def keyEventToString(event):
    return ("KEYEVENT: type=%d\n" % event.type) \
        + ("          hw_code=%d\n" % event.hw_code) \
        + ("          modifiers=%d\n" % event.modifiers) \
        + ("          event_string=(%s)\n" % event.event_string) \
        + ("          is_text=%s\n" % event.is_text) \
        + ("          timestamp=%d\n" % event.timestamp) \
        + ("          time=%f" % time.time())
