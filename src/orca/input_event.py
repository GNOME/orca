# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011 Igalia, S.L.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
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
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2010-2011 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import time
import unicodedata

import debug
import orca_state
import settings

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

    TYPE_UNKNOWN          = "unknown"
    TYPE_PRINTABLE        = "printable"
    TYPE_MODIFIER         = "modifier"
    TYPE_LOCKING          = "locking"
    TYPE_FUNCTION         = "function"
    TYPE_ACTION           = "action"
    TYPE_NAVIGATION       = "navigation"
    TYPE_DIACRITICAL      = "diacritical"

    def __init__(self, event):
        """Creates a new InputEvent of type KEYBOARD_EVENT.

        Arguments:
        - event: the AT-SPI keyboard event
        """

        InputEvent.__init__(self, KEYBOARD_EVENT)
        self.id = event.id
        self.type = event.type
        self.hw_code = event.hw_code
        self.modifiers = event.modifiers
        self.event_string = event.event_string
        self.is_text = event.is_text
        self.time = time.time()
        self.timestamp = event.timestamp

        # Add an empty field for the keyval_name because there are a number
        # of places we might want to know this information, and we don't
        # want to have to keep calculating it. The default calculation will
        # take place in script.checkKeyboardEventData.
        #
        self.keyval_name = ""

        # Call the specific toolkit method, to ensure that all fields
        # are filled.
        #
        script = orca_state.activeScript
        if script:
            script.checkKeyboardEventData(self)

        # Control characters come through as control characters, so we
        # just turn them into their ASCII equivalent.  NOTE that the
        # upper case ASCII characters will be used (e.g., ctrl+a will
        # be turned into the string "A").  All these checks here are
        # to just do some sanity checking before doing the
        # conversion. [[[WDW - this is making assumptions about
        # mapping ASCII control characters to UTF-8.]]]
        #
        if (self.modifiers & settings.CTRL_MODIFIER_MASK) \
            and (not self.is_text) and (len(self.event_string) == 1):
            value = ord(self.event_string[0])
            if value < 32:
                self.event_string = chr(value + 0x40)

        self.keyType = None
        if self.isNavigationKey():
            self.keyType = KeyboardEvent.TYPE_NAVIGATION
            self.shouldEcho = settings.enableNavigationKeys
        elif self.isActionKey():
            self.keyType = KeyboardEvent.TYPE_ACTION
            self.shouldEcho = settings.enableActionKeys
        elif self.isModifierKey():
            self.keyType = KeyboardEvent.TYPE_MODIFIER
            self.shouldEcho = settings.enableModifierKeys
        elif self.isFunctionKey():
            self.keyType = KeyboardEvent.TYPE_FUNCTION
            self.shouldEcho = settings.enableFunctionKeys
        elif self.isDiacriticalKey():
            self.keyType = KeyboardEvent.TYPE_DIACRITICAL
            self.shouldEcho = settings.enableDiacriticalKeys
        elif self.isLockingKey():
            self.keyType = KeyboardEvent.TYPE_LOCKING
            self.shouldEcho = settings.enableLockingKeys
        elif self.isPrintableKey():
            self.keyType = KeyboardEvent.TYPE_PRINTABLE
            self.shouldEcho = \
                settings.enablePrintableKeys or settings.enableEchoByCharacter
        else:
            self.keyType = KeyboardEvent.TYPE_UNKNOWN
            self.shouldEcho = False

        # Never echo if the user doesn't want any echo, as defined by
        # preferences and whether or not we are in a password field.
        self.shouldEcho = self.shouldEcho and settings.enableKeyEcho
        if self.shouldEcho:
            try:
                role = orca_state.locusOfFocus.getRole()
            except:
                pass
            else:
                self.shouldEcho = role != pyatspi.ROLE_PASSWORD_TEXT

    def toString(self):
        return ("KEYBOARDEVENT: type=%d\n" % self.type) \
            + ("                id=%d\n" % self.id) \
            + ("                hw_code=%d\n" % self.hw_code) \
            + ("                modifiers=%d\n" % self.modifiers) \
            + ("                event_string=(%s)\n" % self.event_string) \
            + ("                keyval_name=(%s)\n" % self.keyval_name) \
            + ("                is_text=%s\n" % self.is_text) \
            + ("                timestamp=%d\n" % self.timestamp) \
            + ("                time=%f\n" % time.time()) \
            + ("                keyType=%s\n" % self.keyType) \
            + ("                shouldEcho=%s\n" % self.shouldEcho)

    def isNavigationKey(self):
        """Return True if this is a navigation key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_NAVIGATION

        return self.event_string in \
            ["Left", "Right", "Up", "Down", "Home", "End"]

    def isActionKey(self):
        """Return True if this is an action key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_ACTION

        return self.event_string in \
            ["Return", "Escape", "Tab", "BackSpace", "Delete",
             "Page_Up", "Page_Down"]

    def isDiacriticalKey(self):
        """Return True if this is a non-spacing diacritical key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_DIACRITICAL

        return self.event_string.startswith("dead_")

    def isFunctionKey(self):
        """Return True if this is a function key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_FUNCTION

        return self.event_string in \
            ["F1", "F2", "F3", "F4", "F5", "F6",
             "F7","F8", "F9", "F10", "F11", "F12"]

    def isLockingKey(self):
        """Return True if this is a locking key."""

        if self.keyType:
            return self.keyType in KeyboardEvent.TYPE_LOCKING

        lockingKeys = ["Caps_Lock", "Num_Lock", "Scroll_Lock"]
        if not self.event_string in lockingKeys:
            return False

        if not orca_state.bypassNextCommand:
            return not self.event_string in settings.orcaModifierKeys

        return True

    def isModifierKey(self):
        """Return True if this is a modifier key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_MODIFIER

        modifierKeys = ['Alt_L', 'Alt_R', 'Control_L', 'Control_R',
                        'Shift_L', 'Shift_R', 'Meta_L', 'Meta_R']

        if not orca_state.bypassNextCommand:
            orcaMods = settings.orcaModifierKeys
            try:
                orcaMods = map(lambda x: x.encode('UTF-8'), orcaMods)
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass
            modifierKeys.extend(orcaMods)

        string = self.event_string
        if isinstance(string, unicode):
            string = string.encode('UTF-8')

        return string in modifierKeys

    def isPrintableKey(self):
        """Return True if this is a printable key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_PRINTABLE

        if self.event_string == "space":
            return True

        unicodeString = self.event_string.decode("UTF-8")
        if not len(unicodeString) == 1:
            return False

        if unicodeString.isalnum() or unicodeString.isspace():
            return True

        return unicodedata.category(unicodeString)[0] in ('P', 'S')

    def isCharacterEchoable(self):
        """Returns True if the script will echo this event as part of
        character echo. We do this to not double-echo a given printable
        character."""

        if not self.isPrintableKey():
            return False

        script = orca_state.activeScript
        return script and script.utilities.willEchoCharacter(self)

    def getLockingState(self):
        """Returns True if the event locked a locking key, False if the
        event unlocked a locking key, and None if we do not know or this
        is not a locking key."""

        if self.event_string == "Caps_Lock":
            mod = pyatspi.MODIFIER_SHIFTLOCK
        elif self.event_string == "Num_Lock":
            mod = pyatspi.MODIFIER_NUMLOCK
        else:
            return None

        return not self.modifiers & (1 << mod)

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
                script.presentMessage(self.description)
                consumed = True
        else:
            try:
                consumed = self.function(script, inputEvent)
            except:
                debug.printException(debug.LEVEL_SEVERE)

        return consumed

def keyEventToString(event):
    return ("KEYEVENT: type=%d\n" % event.type) \
        + ("          id=%d\n" % event.id) \
        + ("          hw_code=%d\n" % event.hw_code) \
        + ("          modifiers=%d\n" % event.modifiers) \
        + ("          event_string=(%s)\n" % event.event_string) \
        + ("          is_text=%s\n" % event.is_text) \
        + ("          timestamp=%d\n" % event.timestamp) \
        + ("          time=%f" % time.time())
