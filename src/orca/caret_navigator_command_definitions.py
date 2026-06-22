# Orca
#
# Copyright 2013-2025 Igalia, S.L.
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

"""Command definitions for caret navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .caret_navigator import CaretNavigator


def get_commands(owner: CaretNavigator) -> list[Command]:
    """Returns commands for caret navigation."""

    kb_orca_f12 = keybindings.KeyBinding("F12", keybindings.ORCA_MODIFIER_MASK)
    kb_unmodified_right = keybindings.KeyBinding("Right", keybindings.NO_MODIFIER_MASK)
    kb_unmodified_left = keybindings.KeyBinding("Left", keybindings.NO_MODIFIER_MASK)
    kb_ctrl_right = keybindings.KeyBinding("Right", keybindings.CTRL_MODIFIER_MASK)
    kb_ctrl_left = keybindings.KeyBinding("Left", keybindings.CTRL_MODIFIER_MASK)
    kb_unmodified_down = keybindings.KeyBinding("Down", keybindings.NO_MODIFIER_MASK)
    kb_unmodified_up = keybindings.KeyBinding("Up", keybindings.NO_MODIFIER_MASK)
    kb_unmodified_end = keybindings.KeyBinding("End", keybindings.NO_MODIFIER_MASK)
    kb_unmodified_home = keybindings.KeyBinding("Home", keybindings.NO_MODIFIER_MASK)
    kb_ctrl_end = keybindings.KeyBinding("End", keybindings.CTRL_MODIFIER_MASK)
    kb_ctrl_home = keybindings.KeyBinding("Home", keybindings.CTRL_MODIFIER_MASK)

    enabled = owner.get_is_enabled() and not owner._suspended  # pylint: disable=protected-access
    toggle_enabled = not owner._suspended  # pylint: disable=protected-access

    return [
        KeyboardCommand(
            "toggle_enabled",
            owner.toggle_enabled,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_TOGGLE,
            desktop_keybinding=kb_orca_f12,
            laptop_keybinding=kb_orca_f12,
            enabled=toggle_enabled,
            is_group_toggle=True,
        ),
        KeyboardCommand(
            "next_character",
            owner.next_character,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_NEXT_CHAR,
            desktop_keybinding=kb_unmodified_right,
            laptop_keybinding=kb_unmodified_right,
            enabled=enabled,
        ),
        KeyboardCommand(
            "previous_character",
            owner.previous_character,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_PREV_CHAR,
            desktop_keybinding=kb_unmodified_left,
            laptop_keybinding=kb_unmodified_left,
            enabled=enabled,
        ),
        KeyboardCommand(
            "next_word",
            owner.next_word,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_NEXT_WORD,
            desktop_keybinding=kb_ctrl_right,
            laptop_keybinding=kb_ctrl_right,
            enabled=enabled,
        ),
        KeyboardCommand(
            "previous_word",
            owner.previous_word,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_PREV_WORD,
            desktop_keybinding=kb_ctrl_left,
            laptop_keybinding=kb_ctrl_left,
            enabled=enabled,
        ),
        KeyboardCommand(
            "next_line",
            owner.next_line,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_NEXT_LINE,
            desktop_keybinding=kb_unmodified_down,
            laptop_keybinding=kb_unmodified_down,
            enabled=enabled,
        ),
        KeyboardCommand(
            "previous_line",
            owner.previous_line,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_PREV_LINE,
            desktop_keybinding=kb_unmodified_up,
            laptop_keybinding=kb_unmodified_up,
            enabled=enabled,
        ),
        KeyboardCommand(
            "start_of_file",
            owner.start_of_file,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_FILE_START,
            desktop_keybinding=kb_ctrl_home,
            laptop_keybinding=kb_ctrl_home,
            enabled=enabled,
        ),
        KeyboardCommand(
            "end_of_file",
            owner.end_of_file,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_FILE_END,
            desktop_keybinding=kb_ctrl_end,
            laptop_keybinding=kb_ctrl_end,
            enabled=enabled,
        ),
        KeyboardCommand(
            "start_of_line",
            owner.start_of_line,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_LINE_START,
            desktop_keybinding=kb_unmodified_home,
            laptop_keybinding=kb_unmodified_home,
            enabled=enabled,
        ),
        KeyboardCommand(
            "end_of_line",
            owner.end_of_line,
            owner.GROUP_LABEL,
            cmdnames.CARET_NAVIGATION_LINE_END,
            desktop_keybinding=kb_unmodified_end,
            laptop_keybinding=kb_unmodified_end,
            enabled=enabled,
        ),
        KeyboardCommand(
            "toggle_layout_mode",
            owner.toggle_layout_mode,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_LAYOUT_MODE,
            enabled=enabled,
        ),
    ]
