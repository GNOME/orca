# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

"""Command definitions for bypass mode."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .bypass_mode_manager import BypassModeManager


def get_commands(owner: BypassModeManager) -> list[Command]:
    """Returns commands for bypass mode."""

    kb_alt_backspace = keybindings.KeyBinding("BackSpace", keybindings.ALT_MODIFIER_MASK)
    return [
        KeyboardCommand(
            owner.COMMAND_NAME,
            owner.toggle_enabled,
            owner.GROUP_LABEL,
            cmdnames.BYPASS_MODE_TOGGLE,
            desktop_keybinding=kb_alt_backspace,
            laptop_keybinding=kb_alt_backspace,
        ),
    ]
