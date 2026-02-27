# Utilities for performing tasks related to accessible actions.
#
# Copyright 2023-2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

"""Utilities for performing tasks related to accessible actions."""

import gi

gi.require_version("Atspi", "2.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atspi, GLib, Gtk

from . import debug, keynames
from .ax_action import AXAction
from .ax_object import AXObject


class AXUtilitiesAction:
    """Utilities for performing tasks related to accessible actions."""

    @staticmethod
    def get_action_names(obj: Atspi.Accessible) -> list[str]:
        """Returns the list of actions supported on obj."""

        results = []
        for i in range(AXAction.get_n_actions(obj)):
            name = AXAction.get_action_name(obj, i)
            if name:
                results.append(name)
        return results

    @staticmethod
    def get_action_index(obj: Atspi.Accessible, action_name: str) -> int:
        """Returns the index of the named action or -1 if unsupported."""

        action_name = AXAction.normalize_action_name(action_name)
        for i in range(AXAction.get_n_actions(obj)):
            if action_name == AXAction.get_action_name(obj, i):
                return i

        return -1

    @staticmethod
    def has_action(obj: Atspi.Accessible, action_name: str) -> bool:
        """Returns true if the named action is supported on obj."""

        return AXUtilitiesAction.get_action_index(obj, action_name) >= 0

    @staticmethod
    def do_named_action(obj: Atspi.Accessible, action_name: str) -> bool:
        """Invokes the named action on obj. The return value, if true, may be
        meaningless because most implementors return true without knowing if
        the action was successfully performed."""

        index = AXUtilitiesAction.get_action_index(obj, action_name)
        if index == -1:
            tokens = ["INFO:", action_name, "not an available action for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        return AXAction.do_action(obj, index)

    @staticmethod
    def has_matching_shortcut(obj: Atspi.Accessible, key: str) -> bool:
        """Returns True if any action shortcut on obj matches key."""

        if not key:
            return False

        for i in range(AXAction.get_n_actions(obj)):
            shortcuts = AXAction.get_action_key_binding(obj, i).split(";")
            if any(s.endswith(key.upper()) for s in shortcuts):
                return True
        return False

    @staticmethod
    def _find_first_action_with_keybinding(obj: Atspi.Accessible) -> int:
        """Returns the index of the first action with a keybinding on obj."""

        for i in range(AXAction.get_n_actions(obj)):
            if AXAction.get_action_key_binding(obj, i):
                return i
        return -1

    @staticmethod
    def _get_label_for_key_sequence(sequence: str) -> str:
        """Returns the human consumable label for the key sequence."""

        if not sequence:
            return ""

        # We get all sorts of variations in the keybinding string. Try to normalize it.
        if len(sequence) > 1 and not sequence.startswith("<") and "," not in sequence:
            tokens = sequence.split("+")
            sequence = "".join(f"<{part}>" for part in tokens[:-1]) + tokens[-1]

        # We use Gtk for conversion to handle things like <Primary>.
        try:
            key, mods = Gtk.accelerator_parse(sequence)
            result = Gtk.accelerator_get_label(key, mods)
        except GLib.GError as error:
            msg = f"AXUtilitiesAction: Exception in _get_label_for_key_sequence: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            sequence = sequence.replace("<", "").replace(">", " ").strip()
        else:
            if result and not result.endswith("+"):
                sequence = result

        return keynames.localize_key_sequence(sequence)

    @staticmethod
    def get_accelerator(obj: Atspi.Accessible) -> str:
        """Returns the accelerator/shortcut associated with obj."""

        attrs = AXObject.get_attributes_dict(obj)
        # The ARIA spec suggests a given shortcut's components should be separated by a "+".
        # Multiple shortcuts are apparently allowed and separated by a space.
        shortcuts = attrs.get("keyshortcuts", "").split(" ")
        if shortcuts and shortcuts[0]:
            result = " ".join(
                map(AXUtilitiesAction._get_label_for_key_sequence, shortcuts),
            ).strip()
            # Accelerators are typically modified and thus more than one character.
            if len(result) > 1:
                return result

        index = AXUtilitiesAction._find_first_action_with_keybinding(obj)
        if index == -1:
            return ""

        # This should be a string separated by semicolons and in the form:
        #     <mnemonic>;<full sequence>;<accelerator/shortcut> (optional)
        # In practice we get all sorts of variations.

        # If there's a third item, it's probably the accelerator.
        strings = AXAction.get_action_key_binding(obj, index).split(";")
        if len(strings) == 3:
            return AXUtilitiesAction._get_label_for_key_sequence(strings[2])

        # If the last thing has Ctrl in it, it's probably the accelerator.
        result = AXUtilitiesAction._get_label_for_key_sequence(strings[-1])
        if "Ctrl" in result:
            return result

        return ""

    @staticmethod
    def get_mnemonic(obj: Atspi.Accessible) -> str:
        """Returns the mnemonic associated with obj."""

        attrs = AXObject.get_attributes_dict(obj)
        # The ARIA spec suggests a given shortcut's components should be separated by a "+".
        # Multiple shortcuts are apparently allowed and separated by a space.
        shortcuts = attrs.get("keyshortcuts", "").split(" ")
        if shortcuts and shortcuts[0]:
            result = " ".join(
                map(AXUtilitiesAction._get_label_for_key_sequence, shortcuts),
            ).strip()
            # If it's not a single letter it's probably not the mnemonic.
            if len(result) == 1:
                return result

        index = AXUtilitiesAction._find_first_action_with_keybinding(obj)
        if index == -1:
            return ""

        # This should be a string separated by semicolons and in the form:
        #     <mnemonic>;<full sequence>;<accelerator/shortcut> (optional)
        # In practice we get all sorts of variations.

        strings = AXAction.get_action_key_binding(obj, index).split(";")
        result = AXUtilitiesAction._get_label_for_key_sequence(strings[0])
        # If Ctrl is in the result, it's probably the accelerator rather than the mnemonic.
        if "Ctrl" in result or "Control" in result:
            return ""

        # Don't treat space as a mnemonic.
        if result.lower() in [" ", "space", "<space>"]:
            return ""

        return result
