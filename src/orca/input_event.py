# Orca
#
# Copyright 2005 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Provides support for handling input events.  This provides several classes
to define input events (InputEvent, KeyboardEvent, BrailleEvent,
MouseButtonEvent, MouseMotionEvent, and SpeechEvent), and also provides a
InputEventHandler class.  It is intended that instances of InputEventHandler
will be used which should be used to handle all input events.
"""

import braille
import debug
import settings
import speech
import time

KEYBOARD_EVENT     = "keyboard"
BRAILLE_EVENT      = "braille"
MOUSE_BUTTON_EVENT = "mouse:button"
MOUSE_MOTION_EVENT = "mouse:motion"
SPEECH_EVENT       = "speech"

class InputEvent:
    
    def __init__(self, type):
        """Creates a new input event of the given type.

        Arguments:
        - type: the input event type (one of KEYBOARD_EVENT, BRAILLE_EVENT,
                MOUSE_BUTTON_EVENT, MOUSE_MOTION_EVENT, SPEECH_EVENT).
        """

        self.type = type


class KeyboardEvent(InputEvent):

    def __init__(self, event):
        """Creates a new InputEvent of type KEYBOARD_EVENT.

        Arguments:
        - event: the AT-SPI keyboard event
        """
        
        InputEvent.__init__(self, KEYBOARD_EVENT)
        self.type = event.type
        self.hw_code = event.hw_code
        self.modifiers = event.modifiers
        self.event_string = event.event_string
        self.is_text = event.is_text
        self.time = time.time()


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
        """[[[TODO: WDW - undefined at the moment.]]]
        """
        InputEvent.__init__(self, MOUSE_BUTTON_EVENT)
        self.event = event

        
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

    def __init__(self, function, description):
        """Creates a new InputEventHandler instance.  All bindings
        (e.g., key bindings and braille bindings) will be handled
        by an instance of an InputEventHandler.

        Arguments:
        - function: the function to call with an InputEvent instance as its
                    sole argument
        - description: a localized string describing what this InputEvent
                       does
        """
        
        self._function = function
        self._description = description


    def processInputEvent(self, inputEvent):
        """Processes an input event.  If settings.learnModeEnabled is True,
        this will merely report the description of the input event to braille
        and speech.  If settings.learnModeEnabled is False, this will call the
        function bound to this InputEventHandler instance, passing the
        inputEvent as the sole argument to the function.

        This function is expected to return True if it consumes the
        event; otherwise it is expected to return False.
        
        Arguments:
        - inputEvent: the input event to pass to the function bound
                      to this InputEventHandler instance.
        """
        
        consumed = False
        
        if settings.getSetting("learnModeEnabled", False):
            if self._description:
                braille.displayMessage(self._description)
                speech.say("default", self._description)
                consumed = True
        else:
            try:
                consumed = self._function(inputEvent)
            except:
                debug.printException(debug.LEVEL_SEVERE)

        return consumed
