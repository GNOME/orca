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

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes

"""Provides support for handling input events."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2011-2016 Igalia, S.L."
__license__   = "LGPL"

import inspect
import math
import time

import gi
gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Atspi
from gi.repository import Gdk
from gi.repository import GLib

from . import debug
from . import focus_manager
from . import keybindings
from . import keynames
from . import messages
from . import orca_modifier_manager
from . import script_manager
from . import settings
from .ax_utilities import AXUtilities

KEYBOARD_EVENT     = "keyboard"
BRAILLE_EVENT      = "braille"
MOUSE_BUTTON_EVENT = "mouse:button"

class InputEvent:
    """Provides support for handling input events."""

    def __init__(self, event_type):
        """Creates a new KEYBOARD_EVENT, BRAILLE_EVENT, or MOUSE_BUTTON_EVENT."""

        self.type = event_type
        self.time = time.time()
        self._click_count = 0

    def get_click_count(self):
        """Return the count of the number of clicks a user has made."""

        return self._click_count

    def set_click_count(self, count):
        """Updates the count of the number of clicks a user has made."""

        self._click_count = count

    def as_single_line_string(self):
        """Returns a single-line string representation of this event."""

        return f"{self.type}"

class KeyboardEvent(InputEvent):
    """Provides support for handling keyboard events."""

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

    # pylint:disable=too-many-arguments
    # pylint:disable=too-many-branches
    # pylint:disable=too-many-statements
    def __init__(self, pressed, keycode, keysym, modifiers, text):
        """Creates a new InputEvent of type KEYBOARD_EVENT.

        Arguments:
        - pressed: True if this is a key press, False for a release.
        - keycode: the hardware keycode.
        - keysym: the translated keysym.
        - modifiers: a bitflag giving the active modifiers.
        - text: the text that would be inserted if this key is pressed.
        """

        super().__init__(KEYBOARD_EVENT)
        self.id = keysym
        if pressed:
            self.type = Atspi.EventType.KEY_PRESSED_EVENT
        else:
            self.type = Atspi.EventType.KEY_RELEASED_EVENT
        self.hw_code = keycode
        self.modifiers = modifiers & Gdk.ModifierType.MODIFIER_MASK
        if modifiers & (1 << Atspi.ModifierType.NUMLOCK):
            self.modifiers |= (1 << Atspi.ModifierType.NUMLOCK)
        self.event_string = text
        self.keyval_name = Gdk.keyval_name(keysym)
        if self.event_string in ("", " "):
            self.event_string = self.keyval_name
        self.timestamp = time.time()
        self._script = None
        self._window = None
        self._obj = None
        self._handler = None
        self._consumer = None
        self._did_consume = None
        self._result_reason = None
        self._is_kp_with_numlock = False

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

        # Some implementors don't include numlock in the modifiers. Unfortunately,
        # trying to heuristically hack around this just by looking at the event
        # is not reliable. Ditto regarding asking Gdk for the numlock state.
        if self.keyval_name.startswith("KP"):
            if self.modifiers & (1 << Atspi.ModifierType.NUMLOCK):
                self._is_kp_with_numlock = True

        modifier_manager = orca_modifier_manager.get_manager()

        self.key_type = None
        if self.is_navigation_key():
            self.key_type = KeyboardEvent.TYPE_NAVIGATION
        elif self.is_action_key():
            self.key_type = KeyboardEvent.TYPE_ACTION
        elif self.is_modifier_key():
            self.key_type = KeyboardEvent.TYPE_MODIFIER
            if self.is_orca_modifier():
                modifier_manager.set_pressed_state(pressed)
        elif self.is_function_key():
            self.key_type = KeyboardEvent.TYPE_FUNCTION
        elif self.is_diacritical_key():
            self.key_type = KeyboardEvent.TYPE_DIACRITICAL
        elif self.is_locking_key():
            self.key_type = KeyboardEvent.TYPE_LOCKING
        elif self.is_alphabetic_key():
            self.key_type = KeyboardEvent.TYPE_ALPHABETIC
        elif self.is_numeric_key():
            self.key_type = KeyboardEvent.TYPE_NUMERIC
        elif self.is_punctuation_key():
            self.key_type = KeyboardEvent.TYPE_PUNCTUATION
        elif self.is_space():
            self.key_type = KeyboardEvent.TYPE_SPACE
        else:
            self.key_type = KeyboardEvent.TYPE_UNKNOWN

        if modifier_manager.get_pressed_state():
            self.modifiers |= keybindings.ORCA_MODIFIER_MASK

    # pylint:enable=too-many-arguments
    # pylint:enable=too-many-branches
    # pylint:enable=too-many-statements

    def __eq__(self, other):
        if not other:
            return False

        if self.type == other.type and self.hw_code == other.hw_code:
            return self.timestamp == other.timestamp

        return False

    def __str__(self):
        if self._should_obscure():
            keyid = hw_code = modifiers = event_string = keyval_name = key_type = "*"
        else:
            keyid = self.id
            hw_code = self.hw_code
            modifiers = self.modifiers
            event_string = self.event_string
            keyval_name = self.keyval_name
            key_type = self.key_type

        return (f"KEYBOARD_EVENT:  type={self.type.value_name.upper()}\n") \
             + f"                 id={keyid}\n" \
             + f"                 hw_code={hw_code}\n" \
             + f"                 modifiers={modifiers}\n" \
             + f"                 event_string=({event_string})\n" \
             + f"                 keyval_name=({keyval_name})\n" \
             + f"                 timestamp={self.timestamp}\n" \
             + f"                 time={time.time():f}\n" \
             + f"                 key_type={key_type}\n" \
             + f"                 clickCount={self._click_count}\n" \

    def as_single_line_string(self):
        """Returns a single-line string representation of this event."""

        if self._should_obscure():
            return "(obscured)"

        return (
            f"'{self.keyval_name}' ({self.hw_code}) mods: {self.modifiers} "
            f"{self.type.value_nick}"
        )

    def _should_obscure(self):
        if not AXUtilities.is_password_text(self._obj):
            return False

        if not self.is_printable_key():
            return False

        if self.modifiers & keybindings.CTRL_MODIFIER_MASK \
           or self.modifiers & keybindings.ALT_MODIFIER_MASK \
           or self.modifiers & keybindings.ORCA_MODIFIER_MASK:
            return False

        return True

    def is_navigation_key(self):
        """Return True if this is a navigation key."""

        if self.key_type:
            return self.key_type == KeyboardEvent.TYPE_NAVIGATION

        return self.event_string in \
            ["Left", "Right", "Up", "Down", "Home", "End"]

    def is_action_key(self):
        """Return True if this is an action key."""

        if self.key_type:
            return self.key_type == KeyboardEvent.TYPE_ACTION

        return self.event_string in \
            ["Return", "Escape", "Tab", "BackSpace", "Delete",
             "Page_Up", "Page_Down"]

    def is_alphabetic_key(self):
        """Return True if this is an alphabetic key."""

        if self.key_type:
            return self.key_type == KeyboardEvent.TYPE_ALPHABETIC

        if not len(self.event_string) == 1:
            return False

        return self.event_string.isalpha()

    def is_diacritical_key(self):
        """Return True if this is a non-spacing diacritical key."""

        if self.key_type:
            return self.key_type == KeyboardEvent.TYPE_DIACRITICAL

        return self.event_string.startswith("dead_")

    def is_function_key(self):
        """Return True if this is a function key."""

        if self.key_type:
            return self.key_type == KeyboardEvent.TYPE_FUNCTION

        return self.event_string in \
            ["F1", "F2", "F3", "F4", "F5", "F6",
             "F7", "F8", "F9", "F10", "F11", "F12"]

    def is_locking_key(self):
        """Return True if this is a locking key."""

        if self.key_type:
            return self.key_type in KeyboardEvent.TYPE_LOCKING

        locking_keys = ["Caps_Lock", "Shift_Lock", "Num_Lock", "Scroll_Lock"]
        if self.event_string not in locking_keys:
            return False

        return True

    def is_modifier_key(self):
        """Return True if this is a modifier key."""

        if self.key_type:
            return self.key_type == KeyboardEvent.TYPE_MODIFIER

        if self.is_orca_modifier():
            return True

        return self.event_string in \
            ['Alt_L', 'Alt_R', 'Control_L', 'Control_R',
             'Shift_L', 'Shift_R', 'Meta_L', 'Meta_R',
             'ISO_Level3_Shift']

    def is_numeric_key(self):
        """Return True if this is a numeric key."""

        if self.key_type:
            return self.key_type == KeyboardEvent.TYPE_NUMERIC

        if not len(self.event_string) == 1:
            return False

        return self.event_string.isnumeric()

    def is_orca_modifier(self):
        """Return True if this is the Orca modifier key."""

        if self.keyval_name == "KP_0" and self.modifiers & keybindings.SHIFT_MODIFIER_MASK:
            return orca_modifier_manager.get_manager().is_orca_modifier("KP_Insert")

        return orca_modifier_manager.get_manager().is_orca_modifier(self.keyval_name)

    def is_orca_modified(self):
        """Return True if this key is Orca modified."""

        if self.is_orca_modifier():
            return False

        return self.modifiers & keybindings.ORCA_MODIFIER_MASK

    def is_keypad_key_with_numlock_on(self):
        """Return True if this is a key pad key with numlock on."""

        return self._is_kp_with_numlock

    def is_printable_key(self):
        """Return True if this is a printable key."""

        if self.event_string in ["space", " "]:
            return True

        if not len(self.event_string) == 1:
            return False

        return self.event_string.isprintable()

    def is_pressed_key(self):
        """Returns True if the key is pressed"""

        return self.type == Atspi.EventType.KEY_PRESSED_EVENT

    def is_punctuation_key(self):
        """Return True if this is a punctuation key."""

        if self.key_type:
            return self.key_type == KeyboardEvent.TYPE_PUNCTUATION

        if not len(self.event_string) == 1:
            return False

        if self.is_alphabetic_key() or self.is_numeric_key():
            return False

        return self.event_string.isprintable() and not self.event_string.isspace()

    def is_space(self):
        """Return True if this is the space key."""

        if self.key_type:
            return self.key_type == KeyboardEvent.TYPE_SPACE

        return self.event_string in ["space", " "]

    def is_character_echoable(self):
        """Returns True if the script will echo this event as part of
        character echo. We do this to not double-echo a given printable
        character."""

        if not self.is_printable_key():
            return False

        script = script_manager.get_manager().get_active_script()
        return script and script.utilities.willEchoCharacter(self)

    def get_locking_state(self):
        """Returns True if the event locked a locking key, False if the
        event unlocked a locking key, and None if we do not know or this
        is not a locking key."""

        if not self.is_locking_key():
            return None

        if self.event_string == "Caps_Lock":
            mod = Atspi.ModifierType.SHIFTLOCK
        elif self.event_string == "Shift_Lock":
            mod = Atspi.ModifierType.SHIFT
        elif self.event_string == "Num_Lock":
            mod = Atspi.ModifierType.NUMLOCK
        else:
            return None

        return not self.modifiers & (1 << mod)

    def get_locking_state_string(self):
        """Returns the string which reflects the locking state we wish to
        include when presenting a locking key."""

        locked = self.get_locking_state()
        if locked is None:
            return ''

        if not locked:
            return messages.LOCKING_KEY_STATE_OFF

        return messages.LOCKING_KEY_STATE_ON

    def get_key_name(self):
        """Returns the string to be used for presenting the key to the user."""

        return keynames.get_key_name(self.event_string)

    def get_object(self):
        """Returns the object believed to be associated with this key event."""

        return self._obj

    def set_object(self, obj):
        """Sets the object believed to be associated with this key event."""

        if not inspect.getmodulename(inspect.stack()[1].filename).startswith("input_event"):
            raise PermissionError("Unauthorized setter of input event property")

        self._obj = obj

    def get_window(self):
        """Returns the window believed to be associated with this key event."""

        return self._window

    def set_window(self, window):
        """Sets the window believed to be associated with this key event."""

        if not inspect.getmodulename(inspect.stack()[1].filename).startswith("input_event"):
            raise PermissionError("Unauthorized setter of input event property")

        self._window = window

    def get_script(self):
        """Returns the script believed to be associated with this key event."""

        return self._script

    def set_script(self, script):
        """Sets the script believed to be associated with this key event."""

        if not inspect.getmodulename(inspect.stack()[1].filename).startswith("input_event"):
            raise PermissionError("Unauthorized setter of input event property")

        self._script = script

    def get_handler(self):
        """Returns the handler associated with this key event."""

        return self._handler

    def _get_user_handler(self):
        # TODO - JD: This should go away once plugin support is in place.
        try:
            bindings = settings.keyBindingsMap.get(self._script.__module__)
        except Exception:
            bindings = None
        if not bindings:
            try:
                bindings = settings.keyBindingsMap.get("default")
            except Exception:
                bindings = None

        try:
            handler = bindings.get_input_handler(self)
        except Exception:
            handler = None

        return handler

    def _present(self):
        if not self._script:
            return False

        if self.is_pressed_key():
            self._script.presentationInterrupt()

        if self._script.get_learn_mode_presenter().is_active():
            return False

        return self._script.presentKeyboardEvent(self)

    # pylint:disable=too-many-branches
    # pylint:disable=too-many-return-statements
    def should_echo(self):
        """Returns True if this input event should be echoed."""

        if not (self.is_pressed_key() or AXUtilities.is_terminal(self._obj)):
            return False

        if self.is_locking_key():
            if settings.presentLockingKeys is None:
                return not settings.onlySpeakDisplayedText
            return settings.presentLockingKeys

        if not settings.enableKeyEcho:
            return False

        if self.is_navigation_key():
            return settings.enableNavigationKeys
        if self.is_action_key():
            return settings.enableActionKeys
        if self.is_modifier_key():
            return settings.enableModifierKeys
        if self.is_function_key():
            return settings.enableFunctionKeys
        if self.is_diacritical_key():
            if settings.enableDiacriticalKeys is None:
                return not settings.onlySpeakDisplayedText
            return settings.enableDiacriticalKeys
        if self.is_alphabetic_key():
            return settings.enableAlphabeticKeys or settings.enableEchoByCharacter
        if self.is_numeric_key():
            return settings.enableNumericKeys or settings.enableEchoByCharacter
        if self.is_punctuation_key():
            return settings.enablePunctuationKeys or settings.enableEchoByCharacter
        if self.is_space():
            return settings.enableSpace or settings.enableEchoByCharacter

        return False
    # pylint:enable=too-many-branches
    # pylint:enable=too-many-return-statements

    def process(self):
        """Processes this input event."""

        start_time = time.time()
        if not self._should_obscure():
            data = f"'{self.event_string}' ({self.hw_code})"
        else:
            data = "(obscured)"

        debug.print_message(debug.LEVEL_INFO, f"\n{self}")

        msg = f'\nvvvvv PROCESS {self.type.value_name.upper()}: {data} vvvvv'
        debug.print_message(debug.LEVEL_INFO, msg, False)

        tokens = ["SCRIPT:", self._script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        tokens = ["WINDOW:", self._window]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        tokens = ["LOCATION:", self._obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self._script:
            self._handler = self._get_user_handler() \
                or self._script.key_bindings.get_input_handler(self)
            tokens = ["HANDLER:", self._handler]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            if self._script.get_learn_mode_presenter().is_active():
                self._consumer = self._script.get_learn_mode_presenter().handle_event
                tokens = ["CONSUMER:", self._consumer]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._did_consume, self._result_reason = self._process()
        tokens = ["CONSUMED:", self._did_consume, self._result_reason]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        msg = f"TOTAL PROCESSING TIME: {time.time() - start_time:.4f}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        msg = f"^^^^^ PROCESS {self.type.value_name.upper()}: {data} ^^^^^\n"
        debug.print_message(debug.LEVEL_INFO, msg, False)

        return self._did_consume

    def _process(self):
        """Processes this input event."""

        if self.is_orca_modifier() and self._click_count == 2:
            orca_modifier_manager.get_manager().toggle_modifier(self)
            if self.keyval_name in ["Caps_Lock", "Shift_Lock"]:
                self.key_type = KeyboardEvent.TYPE_LOCKING

        self._present()

        if self.is_orca_modifier():
            return True, 'Orca modifier'

        if not (self._consumer or self._handler):
            return False, 'No consumer or handler'

        if self._consumer or (self._handler.function and self._handler.is_enabled()):
            if self.is_pressed_key():
                GLib.timeout_add(1, self._consume)
                return True, 'Will be consumed'
            return True, 'Is release for consumed handler'

        return False, 'Unaddressed case'

    def _consume(self):
        start_time = time.time()
        data = f"'{self.event_string}' ({self.hw_code})"
        msg = f'\nvvvvv CONSUME {self.type.value_name.upper()}: {data} vvvvv'
        debug.print_message(debug.LEVEL_INFO, msg, False)

        if self._consumer:
            msg = f'KEYBOARD EVENT: Consumer is {self._consumer.__name__}'
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._consumer(self)
        elif self._handler.function and self._handler.is_enabled():
            msg = f'KEYBOARD EVENT: Handler is {self._handler}'
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._handler.function(self._script, self)
        else:
            msg = 'KEYBOARD EVENT: No enabled handler or consumer'
            debug.print_message(debug.LEVEL_INFO, msg, True)

        msg = f'TOTAL PROCESSING TIME: {time.time() - start_time:.4f}'
        debug.print_message(debug.LEVEL_INFO, msg, True)

        msg = f'^^^^^ CONSUME {self.type.value_name.upper()}: {data} ^^^^^\n'
        debug.print_message(debug.LEVEL_INFO, msg, False)

        return False

class BrailleEvent(InputEvent):
    """Provides support for handling braille events."""

    def __init__(self, event):
        super().__init__(BRAILLE_EVENT)
        self.event = event
        self._script = script_manager.get_manager().get_active_script()

    def __str__(self):
        return f"{self.type.upper()} {self.event}"

    def get_handler(self):
        """Returns the handler associated with this event."""

        command = self.event["command"]
        user_bindings = None
        user_bindings_map = settings.brailleBindingsMap
        if self._script.name in user_bindings_map:
            user_bindings = user_bindings_map[self._script.name]
        else:
            user_bindings = user_bindings_map.get("default")

        if user_bindings and command in user_bindings:
            handler = user_bindings[command]
            tokens = [f"BRAILLE EVENT: User handler for command {command} is", handler]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return handler

        handler = self._script.braille_bindings.get(command)
        tokens = [f"BRAILLE EVENT: Handler for command {command} is", handler]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return handler

    def process(self):
        """Processes this event."""

        tokens = ["\nvvvvv PROCESS", self, "vvvvv"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, False)

        start_time = time.time()
        result = self._process()
        msg = f"TOTAL PROCESSING TIME: {time.time() - start_time:.4f}"
        debug.print_message(debug.LEVEL_INFO, msg, False)

        tokens = ["^^^^^ PROCESS", self, "^^^^^"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, False)
        return result

    def _process(self):
        handler = self.get_handler()
        if not handler:
            if self._script.get_learn_mode_presenter().is_active():
                tokens = ["BRAILLE EVENT: Learn mode presenter handles", self]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return True

            tokens = ["BRAILLE EVENT: No handler found for", self]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if handler.function:
            tokens = ["BRAILLE EVENT: Handler is:", handler]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            handler.function(self._script, self)

        return True

class MouseButtonEvent(InputEvent):
    """Provides support for handling mouse button events."""

    try:
        display = Gdk.Display.get_default()
        seat = Gdk.Display.get_default_seat(display)
        _pointer = seat.get_pointer()
    except Exception:
        _pointer = None

    def __init__(self, event):
        super().__init__(MOUSE_BUTTON_EVENT)
        self.x = event.detail1
        self.y = event.detail2
        self.pressed = event.type.endswith('p')
        self.button = event.type[len("mouse:button:"):-1]
        self._script = script_manager.get_manager().get_active_script()
        self.window = focus_manager.get_manager().get_active_window()
        self.app = None

        if self.pressed:
            self._validate_coordinates()

        if not self._script:
            return

        if not AXUtilities.can_be_active_window(self.window):
            self.window = AXUtilities.find_active_window()

        if not self.window:
            return

        self.app = AXUtilities.get_application(self.window)

    def _validate_coordinates(self):
        if not self._pointer:
            return

        x, y = self._pointer.get_position()[1:]
        if math.sqrt((self.x - x)**2 + (self.y - y)**2) < 25:
            return

        msg = (
            f"WARNING: Event coordinates ({self.x}, {self.y}) may be bogus. "
            f"Updating to ({x}, {y})"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.x, self.y = x, y

class InputEventHandler:
    """A handler for an input event."""

    def __init__(self, function, description, learn_mode_enabled=True, enabled=True):
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
        - learn_mode_enabled: if True, the description will be spoken and
                            brailled if learn mode is enabled.  If False,
                            the function will be called no matter what.
        - enabled: Whether this hander can be used, i.e. based on mode, the
          feature being enabled/active, etc.
        """

        self.function = function
        self.description = description
        self.learn_mode_enabled = learn_mode_enabled
        self._enabled = enabled

    def __eq__(self, other):
        """Compares one input handler to another."""

        if not other:
            return False

        return self.function == other.function

    def __str__(self):
        return f"{self.description} (enabled: {self._enabled})"

    def is_enabled(self):
        """Returns True if this handler is enabled."""

        msg = f"INPUT EVENT HANDLER: {self.description} is enabled: {self._enabled}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return self._enabled

    def set_enabled(self, enabled):
        """Sets this handler's enabled state."""

        self._enabled = enabled
