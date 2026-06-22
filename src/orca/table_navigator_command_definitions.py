# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2011-2023 Igalia, S.L.
# Copyright 2023 GNOME Foundation Inc.
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

"""Command definitions for table navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .table_navigator import TableNavigator


def get_commands(owner: TableNavigator) -> list[Command]:  # pylint: disable=too-many-locals
    """Returns commands for table navigation."""

    kb_orca_shift_t = keybindings.KeyBinding("t", keybindings.ORCA_SHIFT_MODIFIER_MASK)
    kb_shift_alt_left = keybindings.KeyBinding("Left", keybindings.SHIFT_ALT_MODIFIER_MASK)
    kb_shift_alt_right = keybindings.KeyBinding("Right", keybindings.SHIFT_ALT_MODIFIER_MASK)
    kb_shift_alt_up = keybindings.KeyBinding("Up", keybindings.SHIFT_ALT_MODIFIER_MASK)
    kb_shift_alt_down = keybindings.KeyBinding("Down", keybindings.SHIFT_ALT_MODIFIER_MASK)
    kb_shift_alt_home = keybindings.KeyBinding("Home", keybindings.SHIFT_ALT_MODIFIER_MASK)
    kb_shift_alt_end = keybindings.KeyBinding("End", keybindings.SHIFT_ALT_MODIFIER_MASK)
    kb_orca_alt_shift_left = keybindings.KeyBinding(
        "Left",
        keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK,
    )
    kb_orca_alt_shift_right = keybindings.KeyBinding(
        "Right",
        keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK,
    )
    kb_orca_alt_shift_up = keybindings.KeyBinding(
        "Up",
        keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK,
    )
    kb_orca_alt_shift_down = keybindings.KeyBinding(
        "Down",
        keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK,
    )
    kb_orca_shift_r = keybindings.KeyBinding("r", keybindings.ORCA_SHIFT_MODIFIER_MASK)
    kb_orca_shift_r_2 = keybindings.KeyBinding(
        "r",
        keybindings.ORCA_SHIFT_MODIFIER_MASK,
        click_count=2,
    )
    kb_orca_shift_c = keybindings.KeyBinding("c", keybindings.ORCA_SHIFT_MODIFIER_MASK)
    kb_orca_shift_c_2 = keybindings.KeyBinding(
        "c",
        keybindings.ORCA_SHIFT_MODIFIER_MASK,
        click_count=2,
    )

    return [
        KeyboardCommand(
            "table_navigator_toggle_enabled",
            owner.toggle_enabled,
            owner.GROUP_LABEL,
            cmdnames.TABLE_NAVIGATION_TOGGLE,
            desktop_keybinding=kb_orca_shift_t,
            laptop_keybinding=kb_orca_shift_t,
            is_group_toggle=True,
        ),
        KeyboardCommand(
            "table_cell_left",
            owner.move_left,
            owner.GROUP_LABEL,
            cmdnames.TABLE_CELL_LEFT,
            desktop_keybinding=kb_shift_alt_left,
            laptop_keybinding=kb_shift_alt_left,
        ),
        KeyboardCommand(
            "table_cell_right",
            owner.move_right,
            owner.GROUP_LABEL,
            cmdnames.TABLE_CELL_RIGHT,
            desktop_keybinding=kb_shift_alt_right,
            laptop_keybinding=kb_shift_alt_right,
        ),
        KeyboardCommand(
            "table_cell_up",
            owner.move_up,
            owner.GROUP_LABEL,
            cmdnames.TABLE_CELL_UP,
            desktop_keybinding=kb_shift_alt_up,
            laptop_keybinding=kb_shift_alt_up,
        ),
        KeyboardCommand(
            "table_cell_down",
            owner.move_down,
            owner.GROUP_LABEL,
            cmdnames.TABLE_CELL_DOWN,
            desktop_keybinding=kb_shift_alt_down,
            laptop_keybinding=kb_shift_alt_down,
        ),
        KeyboardCommand(
            "table_cell_first",
            owner.move_to_first_cell,
            owner.GROUP_LABEL,
            cmdnames.TABLE_CELL_FIRST,
            desktop_keybinding=kb_shift_alt_home,
            laptop_keybinding=kb_shift_alt_home,
        ),
        KeyboardCommand(
            "table_cell_last",
            owner.move_to_last_cell,
            owner.GROUP_LABEL,
            cmdnames.TABLE_CELL_LAST,
            desktop_keybinding=kb_shift_alt_end,
            laptop_keybinding=kb_shift_alt_end,
        ),
        KeyboardCommand(
            "table_cell_beginning_of_row",
            owner.move_to_beginning_of_row,
            owner.GROUP_LABEL,
            cmdnames.TABLE_CELL_BEGINNING_OF_ROW,
            desktop_keybinding=kb_orca_alt_shift_left,
            laptop_keybinding=kb_orca_alt_shift_left,
        ),
        KeyboardCommand(
            "table_cell_end_of_row",
            owner.move_to_end_of_row,
            owner.GROUP_LABEL,
            cmdnames.TABLE_CELL_END_OF_ROW,
            desktop_keybinding=kb_orca_alt_shift_right,
            laptop_keybinding=kb_orca_alt_shift_right,
        ),
        KeyboardCommand(
            "table_cell_top_of_column",
            owner.move_to_top_of_column,
            owner.GROUP_LABEL,
            cmdnames.TABLE_CELL_TOP_OF_COLUMN,
            desktop_keybinding=kb_orca_alt_shift_up,
            laptop_keybinding=kb_orca_alt_shift_up,
        ),
        KeyboardCommand(
            "table_cell_bottom_of_column",
            owner.move_to_bottom_of_column,
            owner.GROUP_LABEL,
            cmdnames.TABLE_CELL_BOTTOM_OF_COLUMN,
            desktop_keybinding=kb_orca_alt_shift_down,
            laptop_keybinding=kb_orca_alt_shift_down,
        ),
        KeyboardCommand(
            "set_dynamic_column_headers_row",
            owner.set_dynamic_column_headers_row,
            owner.GROUP_LABEL,
            cmdnames.DYNAMIC_COLUMN_HEADER_SET,
            desktop_keybinding=kb_orca_shift_r,
            laptop_keybinding=kb_orca_shift_r,
        ),
        KeyboardCommand(
            "clear_dynamic_column_headers_row",
            owner.clear_dynamic_column_headers_row,
            owner.GROUP_LABEL,
            cmdnames.DYNAMIC_COLUMN_HEADER_CLEAR,
            desktop_keybinding=kb_orca_shift_r_2,
            laptop_keybinding=kb_orca_shift_r_2,
        ),
        KeyboardCommand(
            "set_dynamic_row_headers_column",
            owner.set_dynamic_row_headers_column,
            owner.GROUP_LABEL,
            cmdnames.DYNAMIC_ROW_HEADER_SET,
            desktop_keybinding=kb_orca_shift_c,
            laptop_keybinding=kb_orca_shift_c,
        ),
        KeyboardCommand(
            "clear_dynamic_row_headers_column",
            owner.clear_dynamic_row_headers_column,
            owner.GROUP_LABEL,
            cmdnames.DYNAMIC_ROW_HEADER_CLEAR,
            desktop_keybinding=kb_orca_shift_c_2,
            laptop_keybinding=kb_orca_shift_c_2,
        ),
    ]
