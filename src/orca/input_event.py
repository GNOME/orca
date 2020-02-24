# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2016 Igalia, S.L.
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

"""Provides support for handling input events."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2011-2016 Igalia, S.L."
__license__   = "LGPL"

import math
import pyatspi
import time
from gi.repository import Gdk
from gi.repository import GLib

from . import debug
from . import keybindings
from . import keynames
from . import messages
from . import orca_state
from . import script_manager
from . import settings

KEYBOARD_EVENT     = "keyboard"
BRAILLE_EVENT      = "braille"
MOUSE_BUTTON_EVENT = "mouse:button"

class InputEvent:

    def __init__(self, eventType):
        """Creates a new KEYBOARD_EVENT, BRAILLE_EVENT, or MOUSE_BUTTON_EVENT."""

        self.type = eventType
        self.time = time.time()
        self._clickCount = 0

    def getClickCount(self):
        """Return the count of the number of clicks a user has made."""

        return self._clickCount

    def setClickCount(self):
        """Updates the count of the number of clicks a user has made."""

        pass

class KeyboardEvent(InputEvent):

    duplicateCount = 0
    orcaModifierPressed = False

    # Whether last press of the Orca modifier was alone
    lastOrcaModifierAlone = False
    lastOrcaModifierAloneTime = None
    # Whether the current press of the Orca modifier is alone
    currentOrcaModifierAlone = False
    currentOrcaModifierAloneTime = None
    # When the second orca press happened
    secondOrcaModifierTime = None

    TYPE_UNKNOWN          = "unknown"
    TYPE_PRINTABLE        = "printable"
    TYPE_MODIFIER         = "modifier"
    TYPE_LOCKING          = "locking"
    TYPE_FUNCTION         = "function"
    TYPE_ACTION           = "action"
    TYPE_NAVIGATION       = "navigation"
    TYPE_DIACRITICAL      = "diacritical"
    TYPE_ALPHABETIC       = "alphabetic"
    TYPE_NUMERIC          = "numeric"
    TYPE_PUNCTUATION      = "punctuation"
    TYPE_SPACE            = "space"

    GDK_PUNCTUATION_KEYS = [Gdk.KEY_acute,
                            Gdk.KEY_ampersand,
                            Gdk.KEY_apostrophe,
                            Gdk.KEY_asciicircum,
                            Gdk.KEY_asciitilde,
                            Gdk.KEY_asterisk,
                            Gdk.KEY_at,
                            Gdk.KEY_backslash,
                            Gdk.KEY_bar,
                            Gdk.KEY_braceleft,
                            Gdk.KEY_braceright,
                            Gdk.KEY_bracketleft,
                            Gdk.KEY_bracketright,
                            Gdk.KEY_brokenbar,
                            Gdk.KEY_cedilla,
                            Gdk.KEY_cent,
                            Gdk.KEY_colon,
                            Gdk.KEY_comma,
                            Gdk.KEY_copyright,
                            Gdk.KEY_currency,
                            Gdk.KEY_degree,
                            Gdk.KEY_diaeresis,
                            Gdk.KEY_dollar,
                            Gdk.KEY_EuroSign,
                            Gdk.KEY_equal,
                            Gdk.KEY_exclam,
                            Gdk.KEY_exclamdown,
                            Gdk.KEY_grave,
                            Gdk.KEY_greater,
                            Gdk.KEY_guillemotleft,
                            Gdk.KEY_guillemotright,
                            Gdk.KEY_hyphen,
                            Gdk.KEY_less,
                            Gdk.KEY_macron,
                            Gdk.KEY_minus,
                            Gdk.KEY_notsign,
                            Gdk.KEY_numbersign,
                            Gdk.KEY_paragraph,
                            Gdk.KEY_parenleft,
                            Gdk.KEY_parenright,
                            Gdk.KEY_percent,
                            Gdk.KEY_period,
                            Gdk.KEY_periodcentered,
                            Gdk.KEY_plus,
                            Gdk.KEY_plusminus,
                            Gdk.KEY_question,
                            Gdk.KEY_questiondown,
                            Gdk.KEY_quotedbl,
                            Gdk.KEY_quoteleft,
                            Gdk.KEY_quoteright,
                            Gdk.KEY_registered,
                            Gdk.KEY_section,
                            Gdk.KEY_semicolon,
                            Gdk.KEY_slash,
                            Gdk.KEY_sterling,
                            Gdk.KEY_underscore,
                            Gdk.KEY_yen]

    GDK_ACCENTED_LETTER_KEYS = [Gdk.KEY_Aacute,
                                Gdk.KEY_aacute,
                                Gdk.KEY_Acircumflex,
                                Gdk.KEY_acircumflex,
                                Gdk.KEY_Adiaeresis,
                                Gdk.KEY_adiaeresis,
                                Gdk.KEY_Agrave,
                                Gdk.KEY_agrave,
                                Gdk.KEY_Aring,
                                Gdk.KEY_aring,
                                Gdk.KEY_Atilde,
                                Gdk.KEY_atilde,
                                Gdk.KEY_Ccedilla,
                                Gdk.KEY_ccedilla,
                                Gdk.KEY_Eacute,
                                Gdk.KEY_eacute,
                                Gdk.KEY_Ecircumflex,
                                Gdk.KEY_ecircumflex,
                                Gdk.KEY_Ediaeresis,
                                Gdk.KEY_ediaeresis,
                                Gdk.KEY_Egrave,
                                Gdk.KEY_egrave,
                                Gdk.KEY_Iacute,
                                Gdk.KEY_iacute,
                                Gdk.KEY_Icircumflex,
                                Gdk.KEY_icircumflex,
                                Gdk.KEY_Idiaeresis,
                                Gdk.KEY_idiaeresis,
                                Gdk.KEY_Igrave,
                                Gdk.KEY_igrave,
                                Gdk.KEY_Ntilde,
                                Gdk.KEY_ntilde,
                                Gdk.KEY_Oacute,
                                Gdk.KEY_oacute,
                                Gdk.KEY_Ocircumflex,
                                Gdk.KEY_ocircumflex,
                                Gdk.KEY_Odiaeresis,
                                Gdk.KEY_odiaeresis,
                                Gdk.KEY_Ograve,
                                Gdk.KEY_ograve,
                                Gdk.KEY_Ooblique,
                                Gdk.KEY_ooblique,
                                Gdk.KEY_Otilde,
                                Gdk.KEY_otilde,
                                Gdk.KEY_Uacute,
                                Gdk.KEY_uacute,
                                Gdk.KEY_Ucircumflex,
                                Gdk.KEY_ucircumflex,
                                Gdk.KEY_Udiaeresis,
                                Gdk.KEY_udiaeresis,
                                Gdk.KEY_Ugrave,
                                Gdk.KEY_ugrave,
                                Gdk.KEY_Yacute,
                                Gdk.KEY_yacute]

    def __init__(self, event):
        """Creates a new InputEvent of type KEYBOARD_EVENT.

        Arguments:
        - event: the AT-SPI keyboard event
        """

        super().__init__(KEYBOARD_EVENT)
        self.id = event.id
        self.type = event.type
        self.hw_code = event.hw_code
        self.modifiers = event.modifiers
        self.event_string = event.event_string
        self.keyval_name = Gdk.keyval_name(event.id)
        self.timestamp = event.timestamp
        self.is_duplicate = self in [orca_state.lastInputEvent,
                                     orca_state.lastNonModifierKeyEvent]
        self._script = orca_state.activeScript
        self._app = None
        self._window = orca_state.activeWindow
        self._obj = orca_state.locusOfFocus
        self._handler = None
        self._consumer = None
        self._should_consume = None
        self._consume_reason = None
        self._did_consume = None
        self._result_reason = None
        self._bypassOrca = None

        # Some implementors don't populate this field at all. More often than not,
        # the event_string and the keyval_name coincide for input events.
        if not self.event_string:
            self.event_string = self.keyval_name

        # Some implementors do populate the field, but with the keyname rather than
        # the printable character. This messes us up with punctuation and other symbols.
        if len(self.event_string) > 1 \
           and (self.id in KeyboardEvent.GDK_PUNCTUATION_KEYS or \
                self.id in KeyboardEvent.GDK_ACCENTED_LETTER_KEYS):
            self.event_string = chr(self.id)

        if self._script:
            self._app = self._script.app
            if not self._window:
                self._window = orca_state.activeWindow = self._script.utilities.activeWindow()
                msg = 'INPUT EVENT: Updated window and active window to %s' % self._window
                debug.println(debug.LEVEL_INFO, msg, True)

        if self._window and self._app != self._window.getApplication():
            self._script = script_manager.getManager().getScript(self._window.getApplication())
            self._app = self._script.app
            msg = 'INPUT EVENT: Updated script to %s' % self._script
            debug.println(debug.LEVEL_INFO, msg, True)

        if self.is_duplicate:
            KeyboardEvent.duplicateCount += 1
        else:
            KeyboardEvent.duplicateCount = 0

        self.keyType = None

        _isPressed = event.type == pyatspi.KEY_PRESSED_EVENT

        try:
            role = self._obj.getRole()
        except:
            role = None
        _mayEcho = _isPressed or role == pyatspi.ROLE_TERMINAL

        if not self.isOrcaModifier():
            if KeyboardEvent.orcaModifierPressed:
                KeyboardEvent.currentOrcaModifierAlone = False
                KeyboardEvent.currentOrcaModifierAloneTime = None
            else:
                KeyboardEvent.lastOrcaModifierAlone = False
                KeyboardEvent.lastOrcaModifierAloneTime = None

        if self.isNavigationKey():
            self.keyType = KeyboardEvent.TYPE_NAVIGATION
            self.shouldEcho = _mayEcho and settings.enableNavigationKeys
        elif self.isActionKey():
            self.keyType = KeyboardEvent.TYPE_ACTION
            self.shouldEcho = _mayEcho and settings.enableActionKeys
        elif self.isModifierKey():
            self.keyType = KeyboardEvent.TYPE_MODIFIER
            self.shouldEcho = _mayEcho and settings.enableModifierKeys
            if self.isOrcaModifier():
                now = time.time()
                if KeyboardEvent.lastOrcaModifierAlone:
                    if _isPressed:
                        KeyboardEvent.secondOrcaModifierTime = now
                    if KeyboardEvent.secondOrcaModifierTime < KeyboardEvent.lastOrcaModifierAloneTime + 0.5:
                        # double-orca, let the real action happen
                        self._bypassOrca = True
                    if not _isPressed:
                        KeyboardEvent.lastOrcaModifierAlone = False
                        KeyboardEvent.lastOrcaModifierAloneTime = False
                else:
                    KeyboardEvent.orcaModifierPressed = _isPressed
                    if _isPressed:
                        KeyboardEvent.currentOrcaModifierAlone = True
                        KeyboardEvent.currentOrcaModifierAloneTime = now
                    else:
                        KeyboardEvent.lastOrcaModifierAlone = KeyboardEvent.currentOrcaModifierAlone
                        KeyboardEvent.lastOrcaModifierAloneTime = KeyboardEvent.currentOrcaModifierAloneTime
        elif self.isFunctionKey():
            self.keyType = KeyboardEvent.TYPE_FUNCTION
            self.shouldEcho = _mayEcho and settings.enableFunctionKeys
        elif self.isDiacriticalKey():
            self.keyType = KeyboardEvent.TYPE_DIACRITICAL
            self.shouldEcho = _mayEcho and settings.enableDiacriticalKeys
        elif self.isLockingKey():
            self.keyType = KeyboardEvent.TYPE_LOCKING
            self.shouldEcho = settings.presentLockingKeys
            if self.shouldEcho is None:
                self.shouldEcho = not settings.onlySpeakDisplayedText
            self.shouldEcho = self.shouldEcho and _isPressed
        elif self.isAlphabeticKey():
            self.keyType = KeyboardEvent.TYPE_ALPHABETIC
            self.shouldEcho = _mayEcho \
                and (settings.enableAlphabeticKeys or settings.enableEchoByCharacter)
        elif self.isNumericKey():
            self.keyType = KeyboardEvent.TYPE_NUMERIC
            self.shouldEcho = _mayEcho \
                and (settings.enableNumericKeys or settings.enableEchoByCharacter)
        elif self.isPunctuationKey():
            self.keyType = KeyboardEvent.TYPE_PUNCTUATION
            self.shouldEcho = _mayEcho \
                and (settings.enablePunctuationKeys or settings.enableEchoByCharacter)
        elif self.isSpace():
            self.keyType = KeyboardEvent.TYPE_SPACE
            self.shouldEcho = _mayEcho \
                and (settings.enableSpace or settings.enableEchoByCharacter)
        else:
            self.keyType = KeyboardEvent.TYPE_UNKNOWN
            self.shouldEcho = False

        if not self.isLockingKey():
            self.shouldEcho = self.shouldEcho and settings.enableKeyEcho

        if not self.isModifierKey():
            self.setClickCount()

        if orca_state.bypassNextCommand and _isPressed:
            KeyboardEvent.orcaModifierPressed = False

        if KeyboardEvent.orcaModifierPressed:
            self.modifiers |= keybindings.ORCA_MODIFIER_MASK

        self._should_consume, self._consume_reason = self.shouldConsume()

    def setClickCount(self):
        """Updates the count of the number of clicks a user has made."""

        lastEvent = orca_state.lastNonModifierKeyEvent
        if not isinstance(lastEvent, KeyboardEvent) \
           or lastEvent.event_string != self.event_string \
           or self.time - lastEvent.time > settings.doubleClickTimeout:
            self._clickCount = 1
            return

        self._clickCount = lastEvent.getClickCount()
        if self.is_duplicate:
            return

        if self.type == pyatspi.KEY_RELEASED_EVENT:
            return

        if self._clickCount < 3:
            self._clickCount += 1
            return

        self._clickCount = 1

    def __eq__(self, other):
        if not other:
            return False

        if self.type == other.type and self.hw_code == other.hw_code:
            return self.timestamp == other.timestamp

        return False

    def __str__(self):
        return ("KEYBOARD_EVENT:  type=%d\n" % self.type) \
             + ("                 id=%d\n" % self.id) \
             + ("                 hw_code=%d\n" % self.hw_code) \
             + ("                 modifiers=%d\n" % self.modifiers) \
             + ("                 event_string=(%s)\n" % self.event_string) \
             + ("                 keyval_name=(%s)\n" % self.keyval_name) \
             + ("                 timestamp=%d\n" % self.timestamp) \
             + ("                 time=%f\n" % time.time()) \
             + ("                 keyType=%s\n" % self.keyType) \
             + ("                 clickCount=%s\n" % self._clickCount) \
             + ("                 shouldEcho=%s\n" % self.shouldEcho)

    def _isReleaseForLastNonModifierKeyEvent(self):
        last = orca_state.lastNonModifierKeyEvent
        if not last:
            return False

        if not last.isPressedKey() or self.isPressedKey():
            return False

        if self.id == last.id and self.hw_code == last.hw_code:
            return self.modifiers == last.modifiers

        return False

    def isReleaseFor(self, other):
        """Return True if this is the release event for other."""

        if not other:
            return False

        if not other.isPressedKey() or self.isPressedKey():
            return False

        return self.id == other.id \
            and self.hw_code == other.hw_code \
            and self.modifiers == other.modifiers \
            and self.event_string == other.event_string \
            and self.keyval_name == other.keyval_name \
            and self.keyType == other.keyType \
            and self._clickCount == other._clickCount

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

    def isAlphabeticKey(self):
        """Return True if this is an alphabetic key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_ALPHABETIC

        if not len(self.event_string) == 1:
            return False

        return self.event_string.isalpha()

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
             "F7", "F8", "F9", "F10", "F11", "F12"]

    def isLockingKey(self):
        """Return True if this is a locking key."""

        if self.keyType:
            return self.keyType in KeyboardEvent.TYPE_LOCKING

        lockingKeys = ["Caps_Lock", "Shift_Lock", "Num_Lock", "Scroll_Lock"]
        if not self.event_string in lockingKeys:
            return False

        if not orca_state.bypassNextCommand and not self._bypassOrca:
            return not self.event_string in settings.orcaModifierKeys

        return True

    def isModifierKey(self):
        """Return True if this is a modifier key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_MODIFIER

        if self.isOrcaModifier():
            return True

        return self.event_string in \
            ['Alt_L', 'Alt_R', 'Control_L', 'Control_R',
             'Shift_L', 'Shift_R', 'Meta_L', 'Meta_R',
             'ISO_Level3_Shift']

    def isNumericKey(self):
        """Return True if this is a numeric key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_NUMERIC

        if not len(self.event_string) == 1:
            return False

        return self.event_string.isnumeric()

    def isOrcaModifier(self, checkBypassMode=True):
        """Return True if this is the Orca modifier key."""

        if checkBypassMode and orca_state.bypassNextCommand:
            return False

        if self.event_string in settings.orcaModifierKeys:
            return True

        if self.keyval_name == "KP_0" \
           and "KP_Insert" in settings.orcaModifierKeys \
           and self.modifiers & keybindings.SHIFT_MODIFIER_MASK:
            return True

        return False

    def isOrcaModified(self):
        """Return True if this key is Orca modified."""

        if orca_state.bypassNextCommand:
            return False

        return self.modifiers & keybindings.ORCA_MODIFIER_MASK

    def isPrintableKey(self):
        """Return True if this is a printable key."""

        if self.event_string in ["space", " "]:
            return True

        if not len(self.event_string) == 1:
            return False

        return self.event_string.isprintable()

    def isPressedKey(self):
        """Returns True if the key is pressed"""

        return self.type == pyatspi.KEY_PRESSED_EVENT

    def isPunctuationKey(self):
        """Return True if this is a punctuation key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_PUNCTUATION

        if not len(self.event_string) == 1:
            return False

        if self.isAlphabeticKey() or self.isNumericKey():
            return False

        return self.event_string.isprintable() and not self.event_string.isspace()

    def isSpace(self):
        """Return True if this is the space key."""

        if self.keyType:
            return self.keyType == KeyboardEvent.TYPE_SPACE

        return self.event_string in ["space", " "]

    def isFromApplication(self, app):
        """Return True if this is associated with the specified app."""

        return self._app == app

    def isCharacterEchoable(self):
        """Returns True if the script will echo this event as part of
        character echo. We do this to not double-echo a given printable
        character."""

        if not self.isPrintableKey():
            return False

        if orca_state.learnModeEnabled:
            return False

        script = orca_state.activeScript
        return script and script.utilities.willEchoCharacter(self)

    def getLockingState(self):
        """Returns True if the event locked a locking key, False if the
        event unlocked a locking key, and None if we do not know or this
        is not a locking key."""

        if not self.isLockingKey():
            return None

        if self.event_string == "Caps_Lock":
            mod = pyatspi.MODIFIER_SHIFTLOCK
        elif self.event_string == "Shift_Lock":
            mod = pyatspi.MODIFIER_SHIFT
        elif self.event_string == "Num_Lock":
            mod = pyatspi.MODIFIER_NUMLOCK
        else:
            return None

        return not self.modifiers & (1 << mod)

    def getLockingStateString(self):
        """Returns the string which reflects the locking state we wish to
        include when presenting a locking key."""

        locked = self.getLockingState()
        if locked is None:
            return ''

        if not locked:
            return messages.LOCKING_KEY_STATE_OFF

        return messages.LOCKING_KEY_STATE_ON

    def getKeyName(self):
        """Returns the string to be used for presenting the key to the user."""

        return keynames.getKeyName(self.event_string)

    def getObject(self):
        """Returns the object believed to be associated with this key event."""

        return self._obj

    def _getUserHandler(self):
        # TODO - JD: This should go away once plugin support is in place.
        try:
            bindings = settings.keyBindingsMap.get(self._script.__module__)
        except:
            bindings = None
        if not bindings:
            try:
                bindings = settings.keyBindingsMap.get("default")
            except:
                bindings = None

        try:
            handler = bindings.getInputHandler(self)
        except:
            handler = None

        return handler

    def shouldConsume(self):
        """Returns True if this event should be consumed."""

        if not self.timestamp:
            return False, 'No timestamp'

        if not self._script:
            return False, 'No active script when received'

        if self.is_duplicate:
            return False, 'Is duplicate'

        if orca_state.capturingKeys:
            return False, 'Capturing keys'

        if orca_state.bypassNextCommand:
            return False, 'Bypass next command'

        self._handler = self._getUserHandler() \
            or self._script.keyBindings.getInputHandler(self)

        # TODO - JD: Right now we need to always call consumesKeyboardEvent()
        # because that method is updating state, even in instances where there
        # is no handler.
        scriptConsumes = self._script.consumesKeyboardEvent(self)

        if self._isReleaseForLastNonModifierKeyEvent():
            return scriptConsumes, 'Is release for last non-modifier keyevent'

        if orca_state.learnModeEnabled:
            if self.event_string == 'Escape':
                self._consumer = self._script.exitLearnMode
                return True, 'Exiting Learn Mode'

            if self.event_string == 'F1' and not self.modifiers:
                self._consumer = self._script.showHelp
                return True, 'Showing Help'

            if self.event_string in ['F2', 'F3'] and not self.modifiers:
                self._consumer = self._script.listOrcaShortcuts
                return True, 'Listing shortcuts'

            self._consumer = self._presentHandler
            return True, 'In Learn Mode'

        if self.isModifierKey():
            if not self.isOrcaModifier():
                return False, 'Non-Orca modifier not in Learn Mode'
            return True, 'Orca modifier'

        if orca_state.listNotificationsModeEnabled:
            self._consumer = self._script.listNotifications
            return True, 'Listing notifications'

        if not self._handler:
            return False, 'No handler'

        return scriptConsumes, 'Script indication'

    def didConsume(self):
        """Returns True if this event was consumed."""

        if self._did_consume is not None:
            return self._did_consume

        return False

    def isHandledBy(self, method):
        if not self._handler:
            return False

        return method.__func__ == self._handler.function

    def _present(self, inputEvent=None):
        if self.isPressedKey():
            self._script.presentationInterrupt()

        return self._script.presentKeyboardEvent(self)

    def _presentHandler(self, input_event=None):
        if not self._handler:
            return False

        if self._handler.learnModeEnabled and self._handler.description:
            self._script.presentMessage(self._handler.description)

        return True

    def process(self):
        """Processes this input event."""

        startTime = time.time()
        data = "'%s' (%d)" % (self.event_string, self.hw_code)
        if self.is_duplicate:
            data = '%s DUPLICATE EVENT #%i' % (data, KeyboardEvent.duplicateCount)

        msg = '\nvvvvv PROCESS %s: %s vvvvv' % (self.type.value_name.upper(), data)
        debug.println(debug.LEVEL_INFO, msg, False)

        msg = 'HOST_APP: %s' % self._app
        debug.println(debug.LEVEL_INFO, msg, True)

        msg = 'WINDOW:   %s' % self._window
        debug.println(debug.LEVEL_INFO, msg, True)

        msg = 'LOCATION: %s' % self._obj
        debug.println(debug.LEVEL_INFO, msg, True)

        msg = 'CONSUME:  %s (%s)' % (self._should_consume, self._consume_reason)
        debug.println(debug.LEVEL_INFO, msg, True)

        self._did_consume, self._result_reason = self._process()

        if self._should_consume != self._did_consume:
            msg = 'CONSUMED: %s (%s)' % (self._did_consume, self._result_reason)
            debug.println(debug.LEVEL_INFO, msg, True)

        msg = 'TOTAL PROCESSING TIME: %.4f' % (time.time() - startTime)
        debug.println(debug.LEVEL_INFO, msg, True)

        msg = '^^^^^ PROCESS %s: %s ^^^^^\n' % (self.type.value_name.upper(), data)
        debug.println(debug.LEVEL_INFO, msg, False)

        return self._did_consume

    def _process(self):
        """Processes this input event."""

        if self._bypassOrca:
            if (self.event_string == "Caps_Lock" \
                or self.event_string == "Shift_Lock") \
               and self.type == pyatspi.KEY_PRESSED_EVENT:
                    self._lock_mod()
                    self.keyType = KeyboardEvent.TYPE_LOCKING
                    self._present()
            return False, 'Bypassed orca modifier'

        orca_state.lastInputEvent = self
        if not self.isModifierKey():
            orca_state.lastNonModifierKeyEvent = self

        if not self._script:
            return False, 'No active script'

        if self.is_duplicate:
            return False, 'Is duplicate'

        self._present()

        if not self.isPressedKey():
            return self._should_consume, 'Consumed based on handler'

        if orca_state.capturingKeys:
            return False, 'Capturing keys'

        if self.isOrcaModifier():
            return True, 'Orca modifier'

        if orca_state.bypassNextCommand:
            if not self.isModifierKey():
                orca_state.bypassNextCommand = False
            return False, 'Bypass next command'

        if not self._should_consume:
            return False, 'Should not consume'

        if not (self._consumer or self._handler):
            return False, 'No consumer or handler'

        if self._consumer or self._handler.function:
            GLib.timeout_add(1, self._consume)
            return True, 'Will be consumed'

        return False, 'Unaddressed case'

    def _lock_mod(self):
        def lock_mod(modifiers, modifier):
            def lockit():
                try:
                    if modifiers & modifier:
                        lock = pyatspi.KEY_UNLOCKMODIFIERS
                        debug.println(debug.LEVEL_INFO, "Locking capslock", True)
                    else:
                        lock = pyatspi.KEY_LOCKMODIFIERS
                        debug.println(debug.LEVEL_INFO, "Unlocking capslock", True)
                    pyatspi.Registry.generateKeyboardEvent(modifier, None, lock)
                    debug.println(debug.LEVEL_INFO, "Done with capslock", True)
                except:
                    debug.println(debug.LEVEL_INFO, "Could not trigger capslock, " \
                        "at-spi2-core >= 2.32 is needed for triggering capslock", True)
                    pass
            return lockit
        if self.event_string == "Caps_Lock":
            modifier = 1 << pyatspi.MODIFIER_SHIFTLOCK
        elif self.event_string == "Shift_Lock":
            modifier = 1 << pyatspi.MODIFIER_SHIFT
        else:
            msg = "Unknown locking key %s" % self.event_string
            debug.println(debug.LEVEL_WARNING, msg, True)
            return
        debug.println(debug.LEVEL_INFO, "Scheduling capslock", True)
        GLib.timeout_add(1, lock_mod(self.modifiers, modifier))

    def _consume(self):
        startTime = time.time()
        data = "'%s' (%d)" % (self.event_string, self.hw_code)
        msg = 'vvvvv CONSUME %s: %s vvvvv' % (self.type.value_name.upper(), data)
        debug.println(debug.LEVEL_INFO, msg, False)

        if self._consumer:
            msg = 'INFO: Consumer is %s' % self._consumer.__name__
            debug.println(debug.LEVEL_INFO, msg, True)
            self._consumer(self)
        elif self._handler.function:
            msg = 'INFO: Handler is %s' % self._handler.description
            debug.println(debug.LEVEL_INFO, msg, True)
            self._handler.function(self._script, self)
        else:
            msg = 'INFO: No handler or consumer'
            debug.println(debug.LEVEL_INFO, msg, True)

        msg = 'TOTAL PROCESSING TIME: %.4f' % (time.time() - startTime)
        debug.println(debug.LEVEL_INFO, msg, True)

        msg = '^^^^^ CONSUME %s: %s ^^^^^' % (self.type.value_name.upper(), data)
        debug.println(debug.LEVEL_INFO, msg, False)

        return False

class BrailleEvent(InputEvent):

    def __init__(self, event):
        """Creates a new InputEvent of type BRAILLE_EVENT.

        Arguments:
        - event: the integer BrlTTY command for this event.
        """
        super().__init__(BRAILLE_EVENT)
        self.event = event

class MouseButtonEvent(InputEvent):

    try:
        display = Gdk.Display.get_default()
        seat = Gdk.Display.get_default_seat(display)
        _pointer = seat.get_pointer()
    except:
        _pointer = None

    def __init__(self, event):
        """Creates a new InputEvent of type MOUSE_BUTTON_EVENT."""

        super().__init__(MOUSE_BUTTON_EVENT)
        self.x = event.detail1
        self.y = event.detail2
        self.pressed = event.type.endswith('p')
        self.button = event.type[len("mouse:button:"):-1]
        self._script = orca_state.activeScript
        self.window = orca_state.activeWindow
        self.obj = None

        if self.pressed:
            self._validateCoordinates()

        if not self._script:
            return

        if not self._script.utilities.canBeActiveWindow(self.window):
            self.window = self._script.utilities.activeWindow()

        if not self.window:
            return

        self.obj = self._script.utilities.descendantAtPoint(
            self.window, self.x, self.y, event.any_data)

    def _validateCoordinates(self):
        if not self._pointer:
            return

        screen, x, y = self._pointer.get_position()
        if math.sqrt((self.x - x)**2 + (self.y - y)**2) < 25:
            return

        msg = "WARNING: Event coordinates (%i, %i) may be bogus. " \
              "Updating to (%i, %i)." % (self.x, self.y, x, y)
        debug.println(debug.LEVEL_INFO, msg, True)
        self.x, self.y = x, y

    def setClickCount(self):
        """Updates the count of the number of clicks a user has made."""

        if not self.pressed:
            return

        lastInputEvent = orca_state.lastInputEvent
        if not isinstance(lastInputEvent, MouseButtonEvent):
            self._clickCount = 1
            return

        if self.time - lastInputEvent.time < settings.doubleClickTimeout \
            and lastInputEvent.button == self.button:
            if self._clickCount < 2:
                self._clickCount += 1
                return

        self._clickCount = 1


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
        self.learnModeEnabled = learnModeEnabled

    def __eq__(self, other):
        """Compares one input handler to another."""

        if not other:
            return False

        return (self.function == other.function)

    def processInputEvent(self, script, inputEvent):
        """Processes an input event.  If learnModeEnabled is True,
        this will merely present the description of the input event via
        If learnModeEnabled is False, this will call the function bound
        to this InputEventHandler instance, passing the inputEvent as
        the sole argument to the function.

        This function is expected to return True if it consumes the
        event; otherwise it is expected to return False.

        Arguments:
        - script:     the script (if any) associated with this event
        - inputEvent: the input event to pass to the function bound
                      to this InputEventHandler instance.
        """

        consumed = False

        if orca_state.learnModeEnabled and self._learnModeEnabled:
            if self.description:
                script.presentMessage(self.description)
                consumed = True
        else:
            try:
                consumed = self.function(script, inputEvent)
            except:
                debug.printException(debug.LEVEL_SEVERE)

        return consumed
