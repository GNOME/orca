# Orca
#
# Copyright 2024-2026 Igalia, S.L.
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

"""Command definitions for sleep mode."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .sleep_mode_manager import SleepModeManager


def get_commands(owner: SleepModeManager) -> list[Command]:
    """Returns commands for sleep mode."""

    kb_shift_alt_ctrl_q = keybindings.KeyBinding("q", keybindings.SHIFT_ALT_CTRL_MODIFIER_MASK)
    return [
        KeyboardCommand(
            owner.COMMAND_NAME,
            owner.toggle_sleep_mode,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_SLEEP_MODE,
            desktop_keybinding=kb_shift_alt_ctrl_q,
            laptop_keybinding=kb_shift_alt_ctrl_q,
        ),
    ]
