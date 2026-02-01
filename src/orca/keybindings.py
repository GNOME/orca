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


import gi
gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Atspi
from gi.repository import Gdk

from . import input_event_manager
from . import keynames
from . import settings

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
NON_LOCKING_MODIFIER_MASK     = (1 << Atspi.ModifierType.SHIFT |
                                 1 << Atspi.ModifierType.ALT |
                                 1 << Atspi.ModifierType.CONTROL |
                                 1 << Atspi.ModifierType.META3 |
                                 1 << MODIFIER_ORCA)
DEFAULT_MODIFIER_MASK = NON_LOCKING_MODIFIER_MASK

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

    text = ""
    if mods & ORCA_MODIFIER_MASK:
        name = keynames.get_key_name("Orca")
        assert name
        text += name + "+"
    if mods & (1 << Atspi.ModifierType.META3):
        name = keynames.get_key_name("Super")
        assert name
        text += name + "+"
    if mods & ALT_MODIFIER_MASK:
        name = keynames.get_key_name("Alt")
        assert name
        text += name + "+"
    if mods & CTRL_MODIFIER_MASK:
        name = keynames.get_key_name("Control")
        assert name
        text += name + "+"
    if mods & SHIFT_MODIFIER_MASK:
        name = keynames.get_key_name("Shift")
        assert name
        text += name + "+"
    return text

class KeyBinding:
    """A single key binding, consisting of a keysymstring, modifiers, and click count."""

    def __init__(self, keysymstring: str, modifiers: int, click_count: int=1):
        self.keysymstring: str = keysymstring
        self.modifier_mask: int = DEFAULT_MODIFIER_MASK
        self.modifiers: int = modifiers
        self.click_count: int = click_count
        self.keycode: int = 0
        self.keyval: int = 0
        self._grab_ids: list[int] = []

    def __str__(self) -> str:
        return (
            f"BINDING: {self.keysymstring} mods={self.modifiers} "
            f"clicks={self.click_count} grab ids={self._grab_ids}"
        )

    @staticmethod
    def _create_key_definitions(keyval: int, modifiers: int) -> list[Atspi.KeyDefinition]:
        """Returns a list of Atspi key definitions for the given keyval and modifiers."""

        ret = []
        if modifiers & ORCA_MODIFIER_MASK:
            modifier_list = []
            other_modifiers = modifiers & ~ORCA_MODIFIER_MASK
            manager = input_event_manager.get_manager()
            for key in settings.orcaModifierKeys:
                mod_keyval, mod_keycode = get_keycodes(key)
                if mod_keycode == 0 and key == "Shift_Lock":
                    mod_keyval, mod_keycode = get_keycodes("Caps_Lock")
                mod = manager.map_keysym_to_modifier(mod_keyval)
                if mod:
                    modifier_list.append(mod | other_modifiers)
        else:
            modifier_list = [modifiers]
        for mod in modifier_list:
            kd = Atspi.KeyDefinition()
            kd.keysym = keyval
            kd.modifiers = mod
            ret.append(kd)
        return ret

    def matches(self, keyval: int, keycode: int, modifiers: int) -> bool:
        """Returns true if this key binding matches the given keycode and modifier state."""

        # We lazily bind the keycode. This is needed because in some environments
        # (e.g., when the AT-SPI device isn't available), grabs may not be added
        # and keyval/keycode won't be populated via key_definitions().
        if not self.keycode:
            self.keyval, self.keycode = get_keycodes(self.keysymstring)

        if self.keycode == keycode or self.keyval == keyval:
            result = modifiers & self.modifier_mask
            return result == self.modifiers

        return False

    def as_string(self) -> str:
        """Returns a more human-consumable string representing this binding."""

        mods = get_modifier_names(self.modifiers)
        click_count = keynames.get_click_count_string(self.click_count)
        keysym = self.keysymstring
        string = f"{mods}{keysym} {click_count}"
        return string.strip()

    def key_definitions(self) -> list[Atspi.KeyDefinition]:
        """return a list of Atspi key definitions for the given binding."""

        ret = []
        if not self.keycode:
            self.keyval, self.keycode = get_keycodes(self.keysymstring)
        ret.extend(self._create_key_definitions(self.keyval, self.modifiers))
        # We need to bind the uppercase keysyms if requested, as well as the lowercase
        # ones, because keysyms represent characters, not key locations.
        if self.modifiers & SHIFT_MODIFIER_MASK:
            if (upper_keyval := Gdk.keyval_to_upper(self.keyval)) != self.keyval:
                ret.extend(self._create_key_definitions(upper_keyval, self.modifiers))
        return ret

    def get_grab_ids(self) -> list[int]:
        """Returns the grab IDs for this KeyBinding."""

        return self._grab_ids

    def set_grab_ids(self, grab_ids: list[int]) -> None:
        """Sets the grab IDs for this KeyBinding."""

        self._grab_ids = grab_ids

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
