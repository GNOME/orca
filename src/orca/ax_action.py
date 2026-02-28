# Orca
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

"""Wrapper for the Atspi.Action interface."""

import re

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from .ax_object import AXObject


class AXAction:
    """Wrapper for the Atspi.Action interface."""

    @staticmethod
    def get_n_actions(obj: Atspi.Accessible) -> int:
        """Returns the number of actions supported on obj."""

        if not AXObject.supports_action(obj):
            return 0

        try:
            count = Atspi.Action.get_n_actions(obj)
        except GLib.GError as error:
            msg = f"AXAction: Exception in get_n_actions: {error}"
            AXObject.handle_error(obj, error, msg)
            return 0

        return count

    @staticmethod
    def normalize_action_name(action_name: str) -> str:
        """Adjusts the name to account for differences in implementations."""

        if not action_name:
            return ""

        name = re.sub(r"(?<=[a-z])([A-Z])", r"-\1", action_name).lower()
        name = re.sub("[!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~]", "-", name)
        return name

    @staticmethod
    def get_action_name(obj: Atspi.Accessible, i: int) -> str:
        """Returns the name of obj's action at index i."""

        if not 0 <= i < AXAction.get_n_actions(obj):
            return ""

        try:
            name = Atspi.Action.get_action_name(obj, i)
        except GLib.GError as error:
            msg = f"AXAction: Exception in get_action_name: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return AXAction.normalize_action_name(name)

    @staticmethod
    def get_action_description(obj: Atspi.Accessible, i: int) -> str:
        """Returns the description of obj's action at index i."""

        if not 0 <= i < AXAction.get_n_actions(obj):
            return ""

        try:
            description = Atspi.Action.get_action_description(obj, i)
        except GLib.GError as error:
            msg = f"AXAction: Exception in get_action_description: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return description

    @staticmethod
    def get_action_localized_name(obj: Atspi.Accessible, i: int) -> str:
        """Returns the localized name of obj's action at index i."""

        if not 0 <= i < AXAction.get_n_actions(obj):
            return ""

        try:
            name = Atspi.Action.get_localized_name(obj, i)
        except GLib.GError as error:
            msg = f"AXAction: Exception in get_action_localized_name: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return name

    @staticmethod
    def get_action_key_binding(obj: Atspi.Accessible, i: int) -> str:
        """Returns the key binding string of obj's action at index i."""

        if not 0 <= i < AXAction.get_n_actions(obj):
            return ""

        try:
            keybinding = Atspi.Action.get_key_binding(obj, i)
        except GLib.GError as error:
            msg = f"AXAction: Exception in get_action_key_binding: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        # GTK4 does this.
        if keybinding == "<VoidSymbol>":
            return ""
        return keybinding

    @staticmethod
    def do_action(obj: Atspi.Accessible, i: int) -> bool:
        """Invokes obj's action at index i. The return value, if true, may be
        meaningless because most implementors return true without knowing if
        the action was successfully performed."""

        if not 0 <= i < AXAction.get_n_actions(obj):
            return False

        try:
            result = Atspi.Action.do_action(obj, i)
        except GLib.GError as error:
            msg = f"AXAction: Exception in do_action: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return result
