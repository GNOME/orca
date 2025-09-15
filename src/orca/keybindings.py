# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

"""Provides support for defining keybindings and matching them to input events."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from typing import TYPE_CHECKING

import gi
gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Atspi
from gi.repository import Gdk

from . import debug
from . import input_event_manager
from . import settings
from .orca_i18n import _ # pylint: disable=import-error

if TYPE_CHECKING:
    from .input_event import KeyboardEvent, InputEventHandler

_keycode_cache = {}

MODIFIER_ORCA = 8
NO_MODIFIER_MASK              =  0
ALT_MODIFIER_MASK             =  1 << Atspi.ModifierType.ALT
CTRL_MODIFIER_MASK            =  1 << Atspi.ModifierType.CONTROL
ORCA_MODIFIER_MASK            =  1 << MODIFIER_ORCA
ORCA_ALT_MODIFIER_MASK        = (1 << MODIFIER_ORCA |
                                 1 << Atspi.ModifierType.ALT)
ORCA_CTRL_MODIFIER_MASK       = (1 << MODIFIER_ORCA |
                                 1 << Atspi.ModifierType.CONTROL)
ORCA_CTRL_ALT_MODIFIER_MASK   = (1 << MODIFIER_ORCA |
                                 1 << Atspi.ModifierType.CONTROL |
                                 1 << Atspi.ModifierType.ALT)
ORCA_SHIFT_MODIFIER_MASK      = (1 << MODIFIER_ORCA |
                                 1 << Atspi.ModifierType.SHIFT)
ORCA_ALT_SHIFT_MODIFIER_MASK  = (1 << MODIFIER_ORCA |
                                 1 << Atspi.ModifierType.ALT |
                                 1 << Atspi.ModifierType.SHIFT)
SHIFT_MODIFIER_MASK           =  1 << Atspi.ModifierType.SHIFT
SHIFT_ALT_MODIFIER_MASK       = (1 << Atspi.ModifierType.SHIFT |
                                 1 << Atspi.ModifierType.ALT)
CTRL_ALT_MODIFIER_MASK        = (1 << Atspi.ModifierType.CONTROL |
                                 1 << Atspi.ModifierType.ALT)
SHIFT_ALT_CTRL_MODIFIER_MASK  = (1 << Atspi.ModifierType.SHIFT |
                                 1 << Atspi.ModifierType.CONTROL |
                                 1 << Atspi.ModifierType.ALT)
COMMAND_MODIFIER_MASK         = (1 << Atspi.ModifierType.ALT |
                                 1 << Atspi.ModifierType.CONTROL |
                                 1 << Atspi.ModifierType.META2 |
                                 1 << Atspi.ModifierType.META3)
NON_LOCKING_MODIFIER_MASK     = (1 << Atspi.ModifierType.SHIFT |
                                 1 << Atspi.ModifierType.ALT |
                                 1 << Atspi.ModifierType.CONTROL |
                                 1 << Atspi.ModifierType.META2 |
                                 1 << Atspi.ModifierType.META3 |
                                 1 << MODIFIER_ORCA)
DEFAULT_MODIFIER_MASK = NON_LOCKING_MODIFIER_MASK

CAN_USE_KEYSYMS = Atspi.get_version() >= (2, 55, 0)

def get_keycodes(keysym: str) -> tuple[int, int]:
    """Converts an XKeysym string (e.g., 'KP_Enter') to a keycode that
    should match the event.hw_code for key events and to the corresponding
    event.keysym for newer AT-SPI2.

    This whole situation is caused by the fact that Solaris chooses
    to give us different keycodes for the same key, and the keypad
    is the primary place where this happens: if NumLock is not on,
    there is no telling the difference between keypad keys and the
    other navigation keys (e.g., arrows, page up/down, etc.).  One,
    for example, would expect to get KP_End for the '1' key on the
    keypad if NumLock were not on.  Instead, we get 'End' and the
    keycode for it matches the keycode for the other 'End' key.  Odd.
    If NumLock is on, we at least get KP_* keys.

    So...when setting up keybindings, we say we're interested in
    KeySyms, but those keysyms are carefully chosen so as to result
    in a keycode that matches the actual key on the keyboard.  This
    is why we use KP_1 instead of KP_End and so on in our keybindings.

    Arguments:
    - keysym: a string that is a valid representation of an XKeysym.

    Returns an integer representing a key code that should match the
    event.hw_code for key events.
    """

    # TODO - JD: According to the doc string above, one of the main motivators of the work here is
    # Solaris. If the situation stated does not apply to Linux, do we need to do this work?

    if not keysym:
        return (0, 0)

    if keysym not in _keycode_cache:
        keymap = Gdk.Keymap.get_default()

        # Find the numerical value of the keysym
        #
        keyval = Gdk.keyval_from_name(keysym)
        if keyval == 0:
            return (0, 0)

        # Now find the keycodes for the keysym.   Since a keysym can
        # be associated with more than one key, we'll shoot for the
        # keysym that's in group 0, regardless of shift level (each
        # entry is of the form [keycode, group, level]).
        #
        _keycode_cache[keysym] = (keyval, 0)
        _success, entries = keymap.get_entries_for_keyval(keyval)

        for entry in entries:
            if entry.group == 0:
                _keycode_cache[keysym] = (keyval, entry.keycode)
                break
            if _keycode_cache[keysym] == (0, 0):
                _keycode_cache[keysym] = (keyval, entries[0].keycode)

    return _keycode_cache[keysym]

def get_modifier_names(mods: int) -> str:
    """Returns the modifier names of a numeric modifier mask as a human-consumable string."""

    # TODO - JD: Consider moving these localized strings to one of the dedicated i18n files.

    text = ""
    if mods & ORCA_MODIFIER_MASK:
        if settings.keyboardLayout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            # Translators: this is presented in a GUI to represent the
            # "insert" key when used as the Orca modifier.
            text += _("Insert") + "+"
        else:
            # Translators: this is presented in a GUI to represent the
            # "caps lock" modifier.
            text += _("Caps_Lock") + "+"
    elif mods & (1 << Atspi.ModifierType.SHIFTLOCK):
        # Translators: this is presented in a GUI to represent the
        # "caps lock" modifier.
        #
        text += _("Caps_Lock") + "+"
    #if mods & (1 << Atspi.ModifierType.NUMLOCK):
    #    text += _("Num_Lock") + "+"
    if mods & 128:
        # Translators: this is presented in a GUI to represent the
        # "right alt" modifier.
        #
        text += _("Alt_R") + "+"
    if mods & (1 << Atspi.ModifierType.META3):
        # Translators: this is presented in a GUI to represent the
        # "super" modifier.
        #
        text += _("Super") + "+"
    if mods & (1 << Atspi.ModifierType.META2):
        # Translators: this is presented in a GUI to represent the
        # "meta 2" modifier.
        #
        text += _("Meta2") + "+"
    #if mods & (1 << Atspi.ModifierType.META):
    #    text += _("Meta") + "+"
    if mods & ALT_MODIFIER_MASK:
        # Translators: this is presented in a GUI to represent the
        # "alt" modifier.
        #
        text += _("Alt") + "+"
    if mods & CTRL_MODIFIER_MASK:
        # Translators: this is presented in a GUI to represent the
        # "control" modifier.
        #
        text += _("Ctrl") + "+"
    if mods & SHIFT_MODIFIER_MASK:
        # Translators: this is presented in a GUI to represent the
        # "shift " modifier.
        #
        text += _("Shift") + "+"
    return text

def get_click_count_string(count: int) -> str:
    """Returns a human-consumable string representing the number of clicks."""

    # TODO - JD: Consider moving these localized strings to one of the dedicated i18n files.

    if count == 2:
        # Translators: Orca keybindings support double and triple "clicks" or key presses, similar
        # to using a mouse.
        return _("double click")
    if count == 3:
        # Translators: Orca keybindings support double and triple "clicks" or key presses, similar
        # to using a mouse.
        return _("triple click")
    return ""


def create_key_definitions(keycode: int, keyval: int, modifiers: int) -> list[Atspi.KeyDefinition]:
    """Returns a list of Atspi key definitions for the given keycode, keyval, and modifiers."""

    ret = []
    if modifiers & ORCA_MODIFIER_MASK:
        modifier_list = []
        other_modifiers = modifiers & ~ORCA_MODIFIER_MASK
        manager = input_event_manager.get_manager()
        for key in settings.orcaModifierKeys:
            mod_keyval, mod_keycode = get_keycodes(key)
            if mod_keycode == 0 and key == "Shift_Lock":
                mod_keyval, mod_keycode = get_keycodes("Caps_Lock")
            if CAN_USE_KEYSYMS:
                mod = manager.map_keysym_to_modifier(mod_keyval)
            else:
                mod = manager.map_keycode_to_modifier(mod_keycode)
            if mod:
                modifier_list.append(mod | other_modifiers)
    else:
        modifier_list = [modifiers]
    for mod in modifier_list:
        kd = Atspi.KeyDefinition()
        if CAN_USE_KEYSYMS:
            kd.keysym = keyval
        else:
            kd.keycode = keycode
        kd.modifiers = mod
        ret.append(kd)
    return ret

class KeyBinding:
    """A single key binding, consisting of a keycode, modifier mask, and InputEventHandler."""

    # pylint: disable=too-many-positional-arguments
    def __init__(self, keysymstring: str, modifier_mask: int, modifiers: int,
                 handler: InputEventHandler, click_count: int = 1, enabled: bool = True):
        """Creates a new key binding.

        Arguments:
        - keysymstring: the keysymstring - this is typically a string
          from /usr/include/X11/keysymdef.h with the preceding 'XK_'
          removed (e.g., XK_KP_Enter becomes the string 'KP_Enter').
        - modifier_mask: bit mask where a set bit tells us what modifiers
          we care about (see Atspi.ModifierType.*)
        - modifiers: the state the modifiers we care about must be in for
          this key binding to match an input event (see also
          Atspi.ModifierType.*)
        - handler: the InputEventHandler for this key binding
        - enabled: Whether this binding can be bound and used, i.e. based
          on mode, the feature being enabled/active, etc.
        """

        self.keysymstring: str = keysymstring
        self.modifier_mask: int = modifier_mask
        self.modifiers: int = modifiers
        self.handler: InputEventHandler = handler
        self.click_count: int = click_count
        self.keycode: int = 0
        self.keyval: int = 0
        self._enabled: bool = enabled
        self._grab_ids: list[int] = []
    # pylint: enable=too-many-positional-arguments

    def __str__(self) -> str:
        if not self.keysymstring:
            return f"UNBOUND BINDING for '{self.handler}'"
        if self._enabled:
            string = f"ENABLED BINDING for '{self.handler}'"
        else:
            string = f"DISABLED BINDING for '{self.handler}'"
        return (
            f"{string}: {self.keysymstring} mods={self.modifiers} clicks={self.click_count} "
            f"grab ids={self._grab_ids}"
        )

    def matches(self, keyval: int, keycode: int, modifiers: int) -> bool:
        """Returns true if this key binding matches the given keycode and modifier state."""

        # We lazily bind the keycode.  The primary reason for doing this
        # is so that atspi does not have to be initialized before setting
        # keybindings in the user's preferences file.
        #
        if not self.keycode:
            self.keyval, self.keycode = get_keycodes(self.keysymstring)

        if self.keycode == keycode or self.keyval == keyval:
            result = modifiers & self.modifier_mask
            return result == self.modifiers

        return False

    def is_bound(self) -> bool:
        """Returns True if this KeyBinding is bound to a key"""

        return bool(self.keysymstring)

    def is_enabled(self) -> bool:
        """Returns True if this KeyBinding is enabled."""

        return self._enabled

    def set_enabled(self, enabled) -> None:
        """Set this KeyBinding's enabled state."""

        self._enabled = enabled

    def description(self) -> str:
        """Returns the description of this binding's functionality."""

        try:
            assert self.handler is not None
        except AssertionError:
            # TODO - JD: Under what conditions could this actually happen?
            msg = "ERROR: Handler is None"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        return self.handler.description

    def as_string(self) -> str:
        """Returns a more human-consumable string representing this binding."""

        mods = get_modifier_names(self.modifiers)
        click_count = get_click_count_string(self.click_count)
        keysym = self.keysymstring
        string = f"{mods}{keysym} {click_count}"
        return string.strip()

    def key_definitions(self) -> list[Atspi.KeyDefinition]:
        """return a list of Atspi key definitions for the given binding."""

        ret = []
        if not self.keycode:
            self.keyval, self.keycode = get_keycodes(self.keysymstring)
        ret.extend(create_key_definitions(self.keycode, self.keyval, self.modifiers))
        # If we are using keysyms, we need to bind the uppercase keysyms if requested,
        # as well as the lowercase ones, because keysyms represent characters, not key locations.
        if CAN_USE_KEYSYMS and self.modifiers & SHIFT_MODIFIER_MASK:
            if (upper_keyval := Gdk.keyval_to_upper(self.keyval)) != self.keyval:
                ret.extend(create_key_definitions(self.keycode, upper_keyval, self.modifiers))
        return ret

    def get_grab_ids(self) -> list[int]:
        """Returns the grab IDs for this KeyBinding."""

        return self._grab_ids

    def has_grabs(self) -> bool:
        """Returns True if there are existing grabs associated with this KeyBinding."""

        return bool(self._grab_ids)

    def add_grabs(self) -> None:
        """Adds key grabs for this KeyBinding."""

        self._grab_ids = input_event_manager.get_manager().add_grabs_for_keybinding(self)

    def remove_grabs(self) -> None:
        """Removes key grabs for this KeyBinding."""

        input_event_manager.get_manager().remove_grabs_for_keybinding(self)
        self._grab_ids = []

class KeyBindings:
    """Structure that maintains a set of KeyBinding instances."""

    def __init__(self):
        self.key_bindings = []

    def __str__(self) -> str:
        return "\n".join(map(str, self.key_bindings))

    def get_bindings_with_grabs_for_debugging(self) -> list[KeyBinding]:
        """Returns a list of key bindings that have active grabs for debugging purposes."""

        return [binding for binding in self.key_bindings if binding.has_grabs()]

    def add(self, key_binding: KeyBinding, include_grabs: bool = False) -> None:
        """Adds KeyBinding instance to this set of keybindings, optionally updating grabs."""

        if key_binding.keysymstring and self.has_key_binding(key_binding, "keysNoMask"):
            msg = (
               f"KEYBINDINGS: '{key_binding.as_string()}' "
               f"({key_binding.description()}) already in keybindings"
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)

        self.key_bindings.append(key_binding)
        if include_grabs:
            key_binding.add_grabs()

    def remove(self, key_binding: KeyBinding, include_grabs: bool = False) -> None:
        """Removes KeyBinding from this set of keybindings, optionally updating grabs."""

        if key_binding not in self.key_bindings:
            candidates = self.get_bindings_for_handler(key_binding.handler)
            # If there are no candidates, we could be in a situation where we went from outside
            # of web content to inside web content in focus mode. When that occurs, refreshing
            # keybindings will attempt to remove grabs for browse-mode commands that were already
            # removed due to leaving document content. That should be harmless.
            if not candidates:
                return

            # TODO - JD: This shouldn't happen, but it does when trying to remove an overridden
            # binding. This function gets called with the original binding.
            tokens = ["KEYBINDINGS: Warning: No binding in set to remove for", key_binding,
                      "Alternates:", candidates]
            debug.print_tokens(debug.LEVEL_WARNING, tokens, True)
            for candidate in self.get_bindings_for_handler(key_binding.handler):
                self.remove(candidate, include_grabs)
            return

        if key_binding.has_grabs():
            if include_grabs:
                key_binding.remove_grabs()
            else:
                # TODO - JD: This better not happen. Be sure that is indeed the case.
                tokens = ["KEYBINDINGS: Warning:", key_binding, "will be removed but has grabs."]
                debug.print_tokens(debug.LEVEL_WARNING, tokens, True)

        self.key_bindings.remove(key_binding)

    def is_empty(self) -> bool:
        """Returns True if there are no bindings in this set of keybindings."""

        return not self.key_bindings

    def add_key_grabs(self, reason: str = "") -> None:
        """Adds grabs for all enabled bindings in this set of keybindings."""

        msg = "KEYBINDINGS: Adding key grabs"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True, not reason)

        count = 0
        for binding in self.key_bindings:
            if binding.is_enabled() and not binding.has_grabs():
                count += 1
                binding.add_grabs()

        msg = f"KEYBINDINGS: {count} key grabs added (total bindings: {len(self.key_bindings)})."
        debug.print_message(debug.LEVEL_INFO, msg, True, not reason)

    def remove_key_grabs(self, reason: str = "") -> None:
        """Removes all grabs for this set of keybindings."""

        msg = "KEYBINDINGS: Removing key grabs"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True, not reason)

        count = 0
        for binding in self.key_bindings:
            if binding.has_grabs():
                count += 1
                binding.remove_grabs()

        msg = f"KEYBINDINGS: {count} key grabs removed (total bindings: {len(self.key_bindings)})."
        debug.print_message(debug.LEVEL_INFO, msg, True, not reason)

    def has_handler(self, handler: "InputEventHandler") -> bool:
        """Returns True if the handler is found in this set of keybindings."""

        for binding in self.key_bindings:
            if binding.handler == handler:
                return True

        return False

    def has_enabled_handler(self, handler: "InputEventHandler") -> bool:
        """Returns True if the handler is found in this set of keybindings and is enabled."""

        for binding in self.key_bindings:
            if binding.handler == handler and binding.handler.is_enabled():
                return True

        return False

    def has_key_binding(self, key_binding: KeyBinding, type_of_search: str = "strict") -> bool:
        """Return True if binding is already in self.key_bindings.

           The type_of_search can be:
              "strict":      matches description, modifiers, key, and click count
              "description": matches only description
              "keys":        matches the modifiers, key, modifier mask, and click count
              "keysNoMask":  matches the modifiers, key, and click count
        """

        # pylint:disable=too-many-boolean-expressions
        for binding in self.key_bindings:
            if type_of_search == "strict":
                if binding.handler and key_binding.handler \
                   and binding.handler.description == key_binding.handler.description \
                   and binding.keysymstring == key_binding.keysymstring \
                   and binding.modifier_mask == key_binding.modifier_mask \
                   and binding.modifiers == key_binding.modifiers \
                   and binding.click_count == key_binding.click_count:
                    return True
            elif type_of_search == "description":
                if binding.handler and key_binding.handler \
                   and binding.handler.description == key_binding.handler.description:
                    return True
            elif type_of_search == "keys":
                if binding.keysymstring == key_binding.keysymstring \
                   and binding.modifier_mask == key_binding.modifier_mask \
                   and binding.modifiers == key_binding.modifiers \
                   and binding.click_count == key_binding.click_count:
                    return True
            elif type_of_search == "keysNoMask":
                if binding.keysymstring == key_binding.keysymstring \
                   and binding.modifiers == key_binding.modifiers \
                   and binding.click_count == key_binding.click_count:
                    return True

        return False

    def get_bound_bindings(self) -> list[KeyBinding]:
        """Returns the KeyBinding instances which are bound to a keystroke."""

        bound = [kb for kb in self.key_bindings if kb.keysymstring]
        bindings: dict[str, str] = {}
        for kb in bound:
            string = kb.as_string()
            match = bindings.get(string)
            if match is not None:
                tokens = ["WARNING: '", string, "' (", kb.description(), ") also matches:", match]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            bindings[string] = kb.description()

        return bound

    def get_bindings_for_handler(self, handler: "InputEventHandler") -> list[KeyBinding]:
        """Returns the KeyBinding instances associated with handler."""

        return [kb for kb in self.key_bindings if kb.handler == handler]

    def _check_matching_bindings(
        self, keyboard_event: "KeyboardEvent", result: list[KeyBinding]
    ) -> None:
        if debug.debugLevel > debug.LEVEL_INFO:
            return

        # If we don't have multiple matches, we're good.
        if len(result) <= 1:
            return

        # If we have multiple matches, but they have unique click counts, we're good.
        if len(set(map(lambda x: x.click_count, result))) == len(result):
            return

        def to_string(x: KeyBinding) -> str:
            return f"{x.handler} ({x.click_count}x)"

        msg = (
            f"KEYBINDINGS: '{keyboard_event.as_single_line_string()}' "
            f"matches multiple handlers: {', '.join(map(to_string, result))}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def get_input_handler(self, event: KeyboardEvent) -> InputEventHandler | None:
        """Returns the input handler matching keyboardEvent)"""

        matches: list[KeyBinding] = []
        candidates: list[KeyBinding] = []
        click_count = event.get_click_count()
        for binding in self.key_bindings:
            if binding.matches(event.id, event.hw_code, event.modifiers):
                # Checking the modifier mask ensures we don't consume flat review commands
                # when NumLock is on.
                if binding.modifier_mask == event.modifiers and binding.click_count == click_count:
                    matches.append(binding)
                # If there's no keysymstring, it's unbound and cannot be a match.
                if binding.keysymstring:
                    candidates.append(binding)

        tokens = [f"KEYBINDINGS: {event.as_single_line_string()} matches", matches]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._check_matching_bindings(event, matches)
        if matches:
            return matches[0].handler

        if event.is_keypad_key_with_numlock_on():
            return None

        tokens = [f"KEYBINDINGS: {event.as_single_line_string()} {len(candidates)}",
                  "fallback candidate(s):"]
        if not event.should_obscure():
            tokens.append(candidates)
        else:
            tokens.append("(obscured)")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # If we're still here, we don't have an exact match. Prefer the one whose click count is
        # closest to, but does not exceed, the actual click count.
        candidates.sort(key=lambda x: x.click_count, reverse=True)
        self._check_matching_bindings(event, candidates)
        for candidate in candidates:
            if candidate.click_count <= click_count:
                return candidate.handler

        return None
