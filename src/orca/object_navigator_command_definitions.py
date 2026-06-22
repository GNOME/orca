# Orca
#
# Copyright 2023 The Orca Team
# Author: Rynhardt Kruger <rynkruger@gmail.com>
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

"""Command definitions for object navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .object_navigator import ObjectNavigator


def get_commands(owner: ObjectNavigator) -> list[Command]:
    """Returns commands for object navigation."""

    kb_orca_ctrl_up = keybindings.KeyBinding("Up", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_orca_ctrl_down = keybindings.KeyBinding("Down", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_orca_ctrl_right = keybindings.KeyBinding("Right", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_orca_ctrl_left = keybindings.KeyBinding("Left", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_orca_ctrl_return = keybindings.KeyBinding("Return", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_orca_ctrl_s = keybindings.KeyBinding("s", keybindings.ORCA_CTRL_MODIFIER_MASK)

    return [
        KeyboardCommand(
            "object_navigator_up",
            owner.move_to_parent,
            owner.GROUP_LABEL,
            cmdnames.NAVIGATOR_UP,
            desktop_keybinding=kb_orca_ctrl_up,
            laptop_keybinding=kb_orca_ctrl_up,
        ),
        KeyboardCommand(
            "object_navigator_down",
            owner.move_to_first_child,
            owner.GROUP_LABEL,
            cmdnames.NAVIGATOR_DOWN,
            desktop_keybinding=kb_orca_ctrl_down,
            laptop_keybinding=kb_orca_ctrl_down,
        ),
        KeyboardCommand(
            "object_navigator_next",
            owner.move_to_next_sibling,
            owner.GROUP_LABEL,
            cmdnames.NAVIGATOR_NEXT,
            desktop_keybinding=kb_orca_ctrl_right,
            laptop_keybinding=kb_orca_ctrl_right,
        ),
        KeyboardCommand(
            "object_navigator_previous",
            owner.move_to_previous_sibling,
            owner.GROUP_LABEL,
            cmdnames.NAVIGATOR_PREVIOUS,
            desktop_keybinding=kb_orca_ctrl_left,
            laptop_keybinding=kb_orca_ctrl_left,
        ),
        KeyboardCommand(
            "object_navigator_perform_action",
            owner.perform_action,
            owner.GROUP_LABEL,
            cmdnames.NAVIGATOR_PERFORM_ACTION,
            desktop_keybinding=kb_orca_ctrl_return,
            laptop_keybinding=kb_orca_ctrl_return,
        ),
        KeyboardCommand(
            "object_navigator_toggle_simplify",
            owner.toggle_simplify,
            owner.GROUP_LABEL,
            cmdnames.NAVIGATOR_TOGGLE_SIMPLIFIED,
            desktop_keybinding=kb_orca_ctrl_s,
            laptop_keybinding=kb_orca_ctrl_s,
        ),
    ]
