# Orca
#
# Copyright 2023 Igalia, S.L.
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

"""Command definitions for the action presenter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .action_presenter import ActionPresenter


def get_commands(owner: ActionPresenter) -> list[Command]:
    """Returns commands for the action presenter."""

    kb_orca_shift_a = keybindings.KeyBinding("a", keybindings.ORCA_SHIFT_MODIFIER_MASK)
    return [
        KeyboardCommand(
            "show_actions_list",
            owner.show_actions_list,
            owner.GROUP_LABEL,
            cmdnames.SHOW_ACTIONS_LIST,
            desktop_keybinding=kb_orca_shift_a,
            laptop_keybinding=kb_orca_shift_a,
        ),
    ]
