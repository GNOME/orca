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

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

"""Provides support for defining keybindings and matching them to input events."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"


import functools
import gi
gi.require_version('Atspi', '2.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Atspi
from gi.repository import Gdk

from . import debug
from . import input_event_manager
from . import settings

from .orca_i18n import _

_keycodeCache = {}

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

def get_keycode(keysym):
    """Converts an XKeysym string (e.g., 'KP_Enter') to a keycode that
    should match the event.hw_code for key events.

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

    if not keysym:
        return 0

    if keysym not in _keycodeCache:
        keymap = Gdk.Keymap.get_default()

        # Find the numerical value of the keysym
        #
        keyval = Gdk.keyval_from_name(keysym)
        if keyval == 0:
            return 0

        # Now find the keycodes for the keysym.   Since a keysym can
        # be associated with more than one key, we'll shoot for the
        # keysym that's in group 0, regardless of shift level (each
        # entry is of the form [keycode, group, level]).
        #
        _keycodeCache[keysym] = 0
        _success, entries = keymap.get_entries_for_keyval(keyval)

        for entry in entries:
            if entry.group == 0:
                _keycodeCache[keysym] = entry.keycode
                break
            if _keycodeCache[keysym] == 0:
                _keycodeCache[keysym] = entries[0].keycode

        #print keysym, keyval, entries, _keycodeCache[keysym]

    return _keycodeCache[keysym]

def get_modifier_names(mods):
    """Gets the modifier names of a numeric modifier mask as a human
    consumable string.
    """

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

def get_click_count_string(count):
    """Returns a human-consumable string representing the number of
    clicks, such as 'double click' and 'triple click'."""

    if count == 2:
        # Translators: Orca keybindings support double
        # and triple "clicks" or key presses, similar to
        # using a mouse.
        #
        return _("double click")
    if count == 3:
        # Translators: Orca keybindings support double
        # and triple "clicks" or key presses, similar to
        # using a mouse.
        #
        return _("triple click")
    return ""

class KeyBinding:
    """A single key binding, consisting of a keycode, a modifier mask,
    and the InputEventHandler.
    """

    def __init__(self, keysymstring, modifier_mask, modifiers, handler,
                 click_count = 1, enabled=True):
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

        self.keysymstring = keysymstring
        self.modifier_mask = modifier_mask
        self.modifiers = modifiers
        self.handler = handler
        self.click_count = click_count
        self.keycode = None
        self._enabled = enabled
        self._grab_ids = []

    def __str__(self):
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

    def matches(self, keycode, modifiers):
        """Returns true if this key binding matches the given keycode and
        modifier state.
        """

        # We lazily bind the keycode.  The primary reason for doing this
        # is so that atspi does not have to be initialized before setting
        # keybindings in the user's preferences file.
        #
        if not self.keycode:
            self.keycode = get_keycode(self.keysymstring)

        if self.keycode == keycode:
            result = modifiers & self.modifier_mask
            return result == self.modifiers

        return False

    def is_bound(self):
        """Returns True if this KeyBinding is bound to a key"""

        return bool(self.keysymstring)

    def is_enabled(self):
        """Returns True if this KeyBinding is enabled."""

        return self._enabled

    def set_enabled(self, enabled):
        """Set this KeyBinding's enabled state."""

        self._enabled = enabled

    def description(self):
        """Returns the description of this binding's functionality."""

        try:
            return self.handler.description
        except Exception:
            return ''

    def as_string(self):
        """Returns a more human-consumable string representing this binding."""

        mods = get_modifier_names(self.modifiers)
        click_count = get_click_count_string(self.click_count)
        keysym = self.keysymstring
        string = f'{mods}{keysym} {click_count}'

        return string.strip()

    def key_definitions(self):
        """return a list of Atspi key definitions for the given binding."""

        ret = []
        if not self.keycode:
            self.keycode = get_keycode(self.keysymstring)

        if self.modifiers & ORCA_MODIFIER_MASK:
            modifier_list = []
            other_modifiers = self.modifiers & ~ORCA_MODIFIER_MASK
            manager = input_event_manager.get_manager()
            for key in settings.orcaModifierKeys:
                keycode = get_keycode(key)
                if keycode == 0 and key == "Shift_Lock":
                    keycode = get_keycode("Caps_Lock")
                mod = manager.map_keycode_to_modifier(keycode)
                if mod:
                    modifier_list.append(mod | other_modifiers)
        else:
            modifier_list = [self.modifiers]
        for mod in modifier_list:
            kd = Atspi.KeyDefinition()
            kd.keycode = self.keycode
            kd.modifiers = mod
            ret.append(kd)
        return ret

    def get_grab_ids(self):
        """Returns the grab IDs for this KeyBinding."""

        return self._grab_ids

    def has_grabs(self):
        """Returns True if there are existing grabs associated with this KeyBinding."""

        return bool(self._grab_ids)

    def add_grabs(self):
        """Adds key grabs for this KeyBinding."""

        self._grab_ids = input_event_manager.get_manager().add_grabs_for_keybinding(self)

    def remove_grabs(self):
        """Removes key grabs for this KeyBinding."""

        input_event_manager.get_manager().remove_grabs_for_keybinding(self)
        self._grab_ids = []

class KeyBindings:
    """Structure that maintains a set of KeyBinding instances."""

    def __init__(self):
        self.key_bindings = []

    def __str__(self):
        return "\n".join(map(str, self.key_bindings))

    def add(self, key_binding, include_grabs=False):
        """Adds KeyBinding instance to this set of keybindings, optionally updating grabs."""

        if key_binding.keysymstring and self.has_key_binding(key_binding, "keysNoMask"):
            msg = (
               f"KEYBINDINGS: '{key_binding.as_string()}' "
               f"({key_binding.description()}) already in keybindings"
            )
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        self.key_bindings.append(key_binding)
        if include_grabs:
            key_binding.add_grabs()

    def remove(self, key_binding, include_grabs=False):
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
            debug.printTokens(debug.LEVEL_WARNING, tokens, True)
            for candidate in self.get_bindings_for_handler(key_binding.handler):
                self.remove(candidate, include_grabs)
            return

        if key_binding.has_grabs():
            if include_grabs:
                key_binding.remove_grabs()
            else:
                # TODO - JD: This better not happen. Be sure that is indeed the case.
                tokens = ["KEYBINDINGS: Warning:", key_binding, "will be removed but has grabs."]
                debug.printTokens(debug.LEVEL_WARNING, tokens, True)

        self.key_bindings.remove(key_binding)

    def is_empty(self):
        """Returns True if there are no bindings in this set of keybindings."""

        return not self.key_bindings

    def add_key_grabs(self, reason=""):
        """Adds grabs for all enabled bindings in this set of keybindings."""

        msg = "KEYBINDINGS: Adding key grabs"
        if reason:
            msg += f": {reason}"
        debug.printMessage(debug.LEVEL_INFO, msg, True, not reason)

        count = 0
        for binding in self.key_bindings:
            if binding.is_enabled() and not binding.has_grabs():
                count += 1
                binding.add_grabs()

        msg = f"KEYBINDINGS: {count} key grabs out of {len(self.key_bindings)} added."
        debug.printMessage(debug.LEVEL_INFO, msg, True, not reason)

    def remove_key_grabs(self, reason=""):
        """Removes all grabs for this set of keybindings."""

        msg = "KEYBINDINGS: Removing key grabs"
        if reason:
            msg += f": {reason}"
        debug.printMessage(debug.LEVEL_INFO, msg, True, not reason)

        count = 0
        for binding in self.key_bindings:
            if binding.has_grabs():
                count += 1
                binding.remove_grabs()

        msg = f"KEYBINDINGS: {count} key grabs out of {len(self.key_bindings)} removed."
        debug.printMessage(debug.LEVEL_INFO, msg, True, not reason)

    def has_handler(self, handler):
        """Returns True if the handler is found in this set of keybindings."""

        for binding in self.key_bindings:
            if binding.handler == handler:
                return True

        return False

    def has_enabled_handler(self, handler):
        """Returns True if the handler is found in this set of keybindings and is enabled."""

        for binding in self.key_bindings:
            if binding.handler == handler and binding.handler.is_enabled():
                return True

        return False

    def has_key_binding(self, key_binding, type_of_search="strict"):
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

    def get_bound_bindings(self):
        """Returns the KeyBinding instances which are bound to a keystroke."""

        bound = [kb for kb in self.key_bindings if kb.keysymstring]
        bindings = {}
        for kb in bound:
            string = kb.as_string()
            match = bindings.get(string)
            if match is not None:
                tokens = ["WARNING: '", string, "' (", kb.description(), ") also matches:", match]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
            bindings[string] = kb.description()

        return bound

    def get_bindings_for_handler(self, handler):
        """Returns the KeyBinding instances associated with handler."""

        return [kb for kb in self.key_bindings if kb.handler == handler]

    def _check_matching_bindings(self, keyboard_event, result):
        if debug.debugLevel > debug.LEVEL_INFO:
            return

        # If we don't have multiple matches, we're good.
        if len(result) <= 1:
            return

        # If we have multiple matches, but they have unique click counts, we're good.
        if len(set(map(lambda x: x.click_count, result))) == len(result):
            return

        def to_string(x):
            return f"{x.handler} ({x.click_count}x)"

        msg = (
            f"KEYBINDINGS: '{keyboard_event.as_single_line_string()}' "
            f"matches multiple handlers: {', '.join(map(to_string, result))}"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def get_input_handler(self, event):
        """Returns the input handler matching keyboardEvent)"""

        matches = []
        candidates = []
        click_count = event.get_click_count()
        for binding in self.key_bindings:
            if binding.matches(event.hw_code, event.modifiers):
                # Checking the modifier mask ensures we don't consume flat review commands
                # when NumLock is on.
                if binding.modifier_mask == event.modifiers and binding.click_count == click_count:
                    matches.append(binding)
                # If there's no keysymstring, it's unbound and cannot be a match.
                if binding.keysymstring:
                    candidates.append(binding)

        tokens = [f"KEYBINDINGS: {event.as_single_line_string()} matches", matches]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        self._check_matching_bindings(event, matches)
        if matches:
            return matches[0].handler

        if event.is_keypad_key_with_numlock_on():
            return None

        tokens = [f"KEYBINDINGS: {event.as_single_line_string()} fallback candidates", candidates]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        # If we're still here, we don't have an exact match. Prefer the one whose click count is
        # closest to, but does not exceed, the actual click count.
        candidates.sort(key=functools.cmp_to_key(lambda x, y: y.click_count - x.click_count))
        self._check_matching_bindings(event, candidates)
        for candidate in candidates:
            if candidate.click_count <= click_count:
                return candidate.handler

        return None
