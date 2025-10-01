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

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2011-2016 Igalia, S.L."
__license__   = "LGPL"

import inspect
import math
import time
import unicodedata
from typing import Callable, TYPE_CHECKING

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

if TYPE_CHECKING:
    from .scripts import default

KEYBOARD_EVENT     = "keyboard"
BRAILLE_EVENT      = "braille"
MOUSE_BUTTON_EVENT = "mouse:button"
REMOTE_CONTROLLER_EVENT = "remote controller"

class InputEvent:
    """Provides support for handling input events."""

    def __init__(self, event_type: str) -> None:
        """Creates a new KEYBOARD_EVENT, BRAILLE_EVENT, or MOUSE_BUTTON_EVENT."""

        self.type: str = event_type
        self.time: float = time.time()
        self._click_count: int = 0

    def get_click_count(self) -> int:
        """Return the count of the number of clicks a user has made."""

        return self._click_count

    def set_click_count(self, count: int) -> None:
        """Updates the count of the number of clicks a user has made."""

        self._click_count = count

    def as_single_line_string(self) -> str:
        """Returns a single-line string representation of this event."""

        return f"{self.type}"

class KeyboardEvent(InputEvent):
    """Provides support for handling keyboard events."""

    # pylint:disable=too-many-arguments
    # pylint:disable=too-many-positional-arguments
    def __init__(
        self,
        pressed: bool,
        keycode: int,
        keysym: int,
        modifiers: int,
        text: str
    ) -> None:
        """Creates a new InputEvent of type KEYBOARD_EVENT.

        Arguments:
        - pressed: True if this is a key press, False for a release.
        - keycode: the hardware keycode.
        - keysym: the translated keysym.
        - modifiers: a bitflag giving the active modifiers.
        - text: the text that would be inserted if this key is pressed.
        """

        super().__init__(KEYBOARD_EVENT)
        self.id: int = keysym
        self.type: Atspi.EventType = (
            Atspi.EventType.KEY_PRESSED_EVENT if pressed else Atspi.EventType.KEY_RELEASED_EVENT
        )
        self.hw_code: int = keycode
        self._text: str = text
        self.modifiers: int = modifiers & Gdk.ModifierType.MODIFIER_MASK # pylint: disable=no-member
        if modifiers & (1 << Atspi.ModifierType.NUMLOCK):
            self.modifiers |= (1 << Atspi.ModifierType.NUMLOCK)
        self.keyval_name: str = Gdk.keyval_name(keysym) or ""
        self.timestamp: float = time.time()
        self._script: default.Script | None = None
        self._window: Atspi.Accessible | None = None
        self._obj: Atspi.Accessible | None = None
        self._handler: InputEventHandler | None = None
        self._consumer: Callable[..., bool] | None = None
        self._is_kp_with_numlock: bool = False

        # Some implementors don't include numlock in the modifiers. Unfortunately,
        # trying to heuristically hack around this just by looking at the event
        # is not reliable. Ditto regarding asking Gdk for the numlock state.
        if self.keyval_name.startswith("KP"):
            if self.modifiers & (1 << Atspi.ModifierType.NUMLOCK):
                self._is_kp_with_numlock = True

        modifier_manager = orca_modifier_manager.get_manager()
        if self.is_orca_modifier():
            modifier_manager.set_pressed_state(pressed)
        if modifier_manager.get_pressed_state():
            self.modifiers |= keybindings.ORCA_MODIFIER_MASK

    # pylint:enable=too-many-arguments
    # pylint:enable=too-many-positional-arguments

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KeyboardEvent):
            return False

        if self.type == other.type and self.hw_code == other.hw_code:
            return self.timestamp == other.timestamp

        return False

    def __str__(self) -> str:
        if self.should_obscure():
            keyid = hw_code = modifiers = text = keyval_name = "*"
        else:
            keyid = str(self.id)
            hw_code = str(self.hw_code)
            modifiers = str(self.modifiers)
            keyval_name = self.keyval_name
            text = self._text

        return f"KEYBOARD_EVENT:  type={self.type.value_name.upper()}\n" \
             + f"                 id={keyid}\n" \
             + f"                 hw_code={hw_code}\n" \
             + f"                 modifiers={modifiers}\n" \
             + f"                 text='{text}'\n" \
             + f"                 keyval_name='{keyval_name}'\n" \
             + f"                 timestamp={self.timestamp}\n" \
             + f"                 clickCount={self._click_count}"

    def as_single_line_string(self) -> str:
        """Returns a single-line string representation of this event."""

        if self.should_obscure():
            return "(obscured)"

        return (
            f"'{self.keyval_name}' ({self.hw_code}) mods: {self.modifiers} "
            f"{self.type.value_nick}"
        )

    def is_alt_control_or_orca_modified(self) -> bool:
        """Return True if this key is Alt, Control, or Orca modified."""

        if self.modifiers & keybindings.CTRL_MODIFIER_MASK \
           or self.modifiers & keybindings.ALT_MODIFIER_MASK \
           or self.modifiers & keybindings.ORCA_MODIFIER_MASK:
            return True

        return False

    def should_obscure(self) -> bool:
        """Returns True if we should obscure the details of this event."""

        if not AXUtilities.is_password_text(self._obj):
            return False

        if not self.is_printable_key():
            return False

        if self.is_alt_control_or_orca_modified():
            return False

        return True

    def is_navigation_key(self) -> bool:
        """Return True if this is a navigation key."""

        keys = [
            Gdk.KEY_Down,
            Gdk.KEY_End,
            Gdk.KEY_Home,
            Gdk.KEY_Left,
            Gdk.KEY_Right,
            Gdk.KEY_Up,
        ]
        return self.id in keys

    def is_action_key(self) -> bool:
        """Return True if this is an action key."""

        keys = [
            Gdk.KEY_BackSpace,
            Gdk.KEY_Delete,
            Gdk.KEY_Escape,
            Gdk.KEY_KP_Enter,
            Gdk.KEY_Page_Down,
            Gdk.KEY_Page_Up,
            Gdk.KEY_Return,
            Gdk.KEY_Tab,
        ]
        return self.id in keys

    def is_alphabetic_key(self) -> bool:
        """Return True if this is an alphabetic key."""

        name = self.get_key_name()
        if not len(name) == 1:
            return False

        return name.isalpha()

    def is_diacritical_key(self) -> bool:
        """Return True if this is a non-spacing diacritical key."""

        keys = [
            Gdk.KEY_dead_A,
            Gdk.KEY_dead_a,
            Gdk.KEY_dead_abovecomma,
            Gdk.KEY_dead_abovedot,
            Gdk.KEY_dead_abovereversedcomma,
            Gdk.KEY_dead_abovering,
            Gdk.KEY_dead_aboveverticalline,
            Gdk.KEY_dead_acute,
            Gdk.KEY_dead_belowbreve,
            Gdk.KEY_dead_belowcircumflex,
            Gdk.KEY_dead_belowcomma,
            Gdk.KEY_dead_belowdiaeresis,
            Gdk.KEY_dead_belowdot,
            Gdk.KEY_dead_belowmacron,
            Gdk.KEY_dead_belowring,
            Gdk.KEY_dead_belowtilde,
            Gdk.KEY_dead_belowverticalline,
            Gdk.KEY_dead_breve,
            Gdk.KEY_dead_capital_schwa,
            Gdk.KEY_dead_caron,
            Gdk.KEY_dead_cedilla,
            Gdk.KEY_dead_circumflex,
            Gdk.KEY_dead_currency,
            Gdk.KEY_dead_dasia,
            Gdk.KEY_dead_diaeresis,
            Gdk.KEY_dead_doubleacute,
            Gdk.KEY_dead_doublegrave,
            Gdk.KEY_dead_E,
            Gdk.KEY_dead_e,
            Gdk.KEY_dead_grave,
            Gdk.KEY_dead_greek,
            Gdk.KEY_dead_hook,
            Gdk.KEY_dead_horn,
            Gdk.KEY_dead_I,
            Gdk.KEY_dead_i,
            Gdk.KEY_dead_invertedbreve,
            Gdk.KEY_dead_iota,
            Gdk.KEY_dead_longsolidusoverlay,
            Gdk.KEY_dead_lowline,
            Gdk.KEY_dead_macron,
            Gdk.KEY_dead_O,
            Gdk.KEY_dead_o,
            Gdk.KEY_dead_ogonek,
            Gdk.KEY_dead_perispomeni,
            Gdk.KEY_dead_psili,
            Gdk.KEY_dead_semivoiced_sound,
            Gdk.KEY_dead_small_schwa,
            Gdk.KEY_dead_stroke,
            Gdk.KEY_dead_tilde,
            Gdk.KEY_dead_U,
            Gdk.KEY_dead_u,
            Gdk.KEY_dead_voiced_sound,
        ]

        if self.id in keys:
            return True

        name = self.get_key_name()
        if len(name) == 1:
            category = unicodedata.category(name)
            # Mn = Mark, nonspacing; Mc = Mark, spacing combining; Me = Mark, enclosing
            if category in ("Mn", "Mc", "Me"):
                return True

        return False

    def is_function_key(self) -> bool:
        """Return True if this is a function key."""

        keys = [
            Gdk.KEY_F1,
            Gdk.KEY_F2,
            Gdk.KEY_F3,
            Gdk.KEY_F4,
            Gdk.KEY_F5,
            Gdk.KEY_F6,
            Gdk.KEY_F7,
            Gdk.KEY_F8,
            Gdk.KEY_F9,
            Gdk.KEY_F10,
            Gdk.KEY_F11,
            Gdk.KEY_F12,
        ]
        return self.id in keys

    def is_locking_key(self) -> bool:
        """Return True if this is a locking key."""

        if self.is_orca_modifier():
            return self._click_count == 2

        keys = [
            Gdk.KEY_Caps_Lock,
            Gdk.KEY_Num_Lock,
            Gdk.KEY_Scroll_Lock,
            Gdk.KEY_Shift_Lock,
        ]
        return self.id in keys

    def is_modifier_key(self) -> bool:
        """Return True if this is a modifier key."""

        keys = [
            Gdk.KEY_Alt_L,
            Gdk.KEY_Alt_R,
            Gdk.KEY_Control_L,
            Gdk.KEY_Control_R,
            Gdk.KEY_Meta_L,
            Gdk.KEY_Meta_R,
            Gdk.KEY_Shift_L,
            Gdk.KEY_Shift_R,
            Gdk.KEY_ISO_Level3_Shift,
        ]
        return self.id in keys or self.is_orca_modifier()

    def is_numeric_key(self) -> bool:
        """Return True if this is a numeric key."""

        keys = [
            Gdk.KEY_0,
            Gdk.KEY_1,
            Gdk.KEY_2,
            Gdk.KEY_3,
            Gdk.KEY_4,
            Gdk.KEY_5,
            Gdk.KEY_6,
            Gdk.KEY_7,
            Gdk.KEY_8,
            Gdk.KEY_9,
            Gdk.KEY_KP_0,
            Gdk.KEY_KP_1,
            Gdk.KEY_KP_2,
            Gdk.KEY_KP_3,
            Gdk.KEY_KP_4,
            Gdk.KEY_KP_5,
            Gdk.KEY_KP_6,
            Gdk.KEY_KP_7,
            Gdk.KEY_KP_8,
            Gdk.KEY_KP_9,
        ]
        return self.id in keys

    def is_orca_modifier(self) -> bool:
        """Return True if this is the Orca modifier key."""

        if self.id == Gdk.KEY_KP_0 and self.modifiers & keybindings.SHIFT_MODIFIER_MASK:
            return orca_modifier_manager.get_manager().is_orca_modifier("KP_Insert")

        return orca_modifier_manager.get_manager().is_orca_modifier(self.keyval_name)

    def is_orca_modified(self) -> bool:
        """Return True if this key is Orca modified."""

        if self.is_orca_modifier():
            return False

        return bool(self.modifiers & keybindings.ORCA_MODIFIER_MASK)

    def is_keypad_key_with_numlock_on(self) -> bool:
        """Return True if this is a key pad key with numlock on."""

        return self._is_kp_with_numlock

    def is_printable_key(self) -> bool:
        """Return True if this is a printable key."""

        name = self.get_key_name()
        if not len(name) == 1:
            return False

        return name.isprintable()

    def is_pressed_key(self) -> bool:
        """Returns True if the key is pressed"""

        return self.type == Atspi.EventType.KEY_PRESSED_EVENT

    def is_punctuation_key(self) -> bool:
        """Return True if this is a punctuation key."""

        keys = [
            Gdk.KEY_acute,
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
            Gdk.KEY_KP_Decimal,
            Gdk.KEY_KP_Add,
            Gdk.KEY_KP_Divide,
            Gdk.KEY_KP_Multiply,
            Gdk.KEY_KP_Subtract,
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
            Gdk.KEY_yen,
        ]
        return self.id in keys

    def is_space(self) -> bool:
        """Return True if this is the space key."""

        return self.id == Gdk.KEY_space

    def get_locking_state(self) -> bool | None:
        """Returns True if the event locked a locking key, False if the event unlocked it, and None
        if not a locking key."""

        if not self.is_locking_key():
            return None

        if self.id == Gdk.KEY_Caps_Lock:
            mod = Atspi.ModifierType.SHIFTLOCK
        elif self.id == Gdk.KEY_Shift_Lock:
            mod = Atspi.ModifierType.SHIFT
        elif self.id == Gdk.KEY_Num_Lock:
            mod = Atspi.ModifierType.NUMLOCK
        else:
            return None

        return not self.modifiers & (1 << mod)

    def get_locking_state_string(self) -> str:
        """Returns the string reflecting the locking state."""

        locked = self.get_locking_state()
        if locked is None:
            return ""

        if not locked:
            return messages.LOCKING_KEY_STATE_OFF

        return messages.LOCKING_KEY_STATE_ON

    def get_key_name(self) -> str:
        """Returns the string to be used for presenting the key."""

        if self._text.strip() and self._text.isprintable():
            return self._text

        name = keynames.get_key_name(self.keyval_name)
        if name is not None:
            return name

        unicode_codepoint = Gdk.keyval_to_unicode(self.id)
        if unicode_codepoint:
            char = chr(unicode_codepoint)
            if char.isprintable():
                return char

        return self.keyval_name

    def get_object(self) -> Atspi.Accessible | None:
        """Returns the object believed to be associated with this key event."""

        return self._obj

    def set_object(self, obj: Atspi.Accessible | None) -> None:
        """Sets the object believed to be associated with this key event."""

        module_name = inspect.getmodulename(inspect.stack()[1].filename)
        if not (module_name and module_name.startswith("input_event")):
            raise PermissionError("Unauthorized setter of input event property")

        self._obj = obj

    def get_window(self) -> Atspi.Accessible | None:
        """Returns the window believed to be associated with this key event."""

        return self._window

    def set_window(self, window: Atspi.Accessible | None) -> None:
        """Sets the window believed to be associated with this key event."""

        module_name = inspect.getmodulename(inspect.stack()[1].filename)
        if not (module_name and module_name.startswith("input_event")):
            raise PermissionError("Unauthorized setter of input event property")

        self._window = window

    def get_script(self) -> default.Script | None:
        """Returns the script believed to be associated with this key event."""

        return self._script

    def set_script(self, script: default.Script | None) -> None:
        """Sets the script believed to be associated with this key event."""

        module_name = inspect.getmodulename(inspect.stack()[1].filename)
        if not (module_name and module_name.startswith("input_event")):
            raise PermissionError("Unauthorized setter of input event property")

        self._script = script

    def get_handler(self) -> InputEventHandler | None:
        """Returns the handler associated with this key event."""

        return self._handler

    def _get_user_handler(self) -> InputEventHandler | None:
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

        if bindings is None:
            return None

        try:
            handler = bindings.get_input_handler(self)
        except Exception:
            handler = None

        return handler

    def _present(self) -> None:
        if not self._script:
            return

        if self.is_pressed_key():
            self._script.interrupt_presentation()

        if self._script.get_learn_mode_presenter().is_active():
            return

        self._script.present_keyboard_event(self)

    def process(self) -> None:
        """Processes this input event."""

        start_time = time.time()
        should_obscure = self.should_obscure()
        if not should_obscure:
            data = f"'{self.keyval_name}' ({self.hw_code})"
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
            if not should_obscure:
                tokens = ["HANDLER:", str(self._handler)]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            if self._script.get_learn_mode_presenter().is_active():
                self._consumer = self._script.get_learn_mode_presenter().handle_event
                tokens = ["CONSUMER:", str(self._consumer)]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self.is_orca_modifier() and self._click_count == 2:
            orca_modifier_manager.get_manager().toggle_modifier(self)

        self._present()

        if self.is_pressed_key() and (self._consumer \
           or (self._handler and self._handler.function is not None \
           and self._handler.is_enabled())):
            GLib.timeout_add(1, self._consume)

        msg = f"TOTAL PROCESSING TIME: {time.time() - start_time:.4f}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        msg = f"^^^^^ PROCESS {self.type.value_name.upper()}: {data} ^^^^^\n"
        debug.print_message(debug.LEVEL_INFO, msg, False)

    def _consume(self) -> bool:
        """Consumes this input event after a timeout. Returns False to stop the timeout."""

        start_time = time.time()
        data = f"'{self.keyval_name}' ({self.hw_code})"
        msg = f"\nvvvvv CONSUME {self.type.value_name.upper()}: {data} vvvvv"
        debug.print_message(debug.LEVEL_INFO, msg, False)

        if self._consumer:
            msg = f"KEYBOARD EVENT: Consumer is {self._consumer.__name__}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._consumer(self)
        elif self._handler and self._handler.function is not None and self._handler.is_enabled():
            msg = f"KEYBOARD EVENT: Handler is {self._handler}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            try:
                self._handler.function(self._script, self)
            except GLib.GError as error:
                msg = f"KEYBOARD EVENT: Exception calling handler function: {error}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)
        else:
            msg = "KEYBOARD EVENT: No enabled handler or consumer"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        msg = f"TOTAL PROCESSING TIME: {time.time() - start_time:.4f}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        msg = f"^^^^^ CONSUME {self.type.value_name.upper()}: {data} ^^^^^\n"
        debug.print_message(debug.LEVEL_INFO, msg, False)

        return False

class BrailleEvent(InputEvent):
    """Provides support for handling braille events."""

    def __init__(self, event: dict) -> None:
        super().__init__(BRAILLE_EVENT)
        self.event: dict = event
        self._script: default.Script | None = script_manager.get_manager().get_active_script()

    def __str__(self) -> str:
        return f"{self.type.upper()} {self.event}"

    def get_handler(self) -> InputEventHandler | None:
        """Returns the handler associated with this event."""

        try:
            assert self._script is not None
        except AssertionError:
            tokens = ["BRAILLE EVENT: No active script found for", self]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        command: str = self.event["command"]
        user_bindings: dict | None = None
        user_bindings_map: dict = settings.brailleBindingsMap
        if self._script.name in user_bindings_map:
            user_bindings = user_bindings_map[self._script.name]
        else:
            user_bindings = user_bindings_map.get("default")

        if user_bindings and command in user_bindings:
            handler: InputEventHandler | None = user_bindings[command]
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

    # TODO - JD: Remove this and the validation logic once we have a fix for
    # https://gitlab.gnome.org/GNOME/at-spi2-core/-/issues/194.
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

class RemoteControllerEvent(InputEvent):
    """A simple input event whose main purpose is identification of the origin."""

    def __init__(self):
        super().__init__(REMOTE_CONTROLLER_EVENT)

class InputEventHandler:
    """A handler for an input event."""

    def __init__(
        self,
        function: Callable[..., bool],
        description: str,
        learn_mode_enabled: bool = True,
        enabled: bool = True
    ) -> None:
        self.function: Callable[..., bool] = function
        self.description: str = description
        self.learn_mode_enabled: bool = learn_mode_enabled
        self._enabled: bool = enabled

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InputEventHandler):
            return False
        return self.function == other.function

    def __str__(self) -> str:
        return f"{self.description} (enabled: {self._enabled})"

    def is_enabled(self) -> bool:
        """Returns True if this handler is enabled."""

        msg = f"INPUT EVENT HANDLER: {self.description} is enabled: {self._enabled}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        """Sets enabled state of this handler."""

        self._enabled = enabled
