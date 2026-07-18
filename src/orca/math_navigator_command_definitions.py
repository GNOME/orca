# Orca
#
# Copyright 2026 Igalia, S.L.
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

"""Command definitions for math navigation."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .math_navigator import MathNavigator


PLACE_MARKER_PREFIXES = ("MoveTo", "SetPlacemarker", "Read", "Describe")

COMMAND_SPECS = (
    ("math_move_next", "MoveNext", cmdnames.MATH_NAV_MOVE_NEXT, "Right", "none"),
    ("math_move_previous", "MovePrevious", cmdnames.MATH_NAV_MOVE_PREVIOUS, "Left", "none"),
    ("math_zoom_in", "ZoomIn", cmdnames.MATH_NAV_ZOOM_IN, "Down", "none"),
    ("math_zoom_out", "ZoomOut", cmdnames.MATH_NAV_ZOOM_OUT, "Up", "none"),
    ("math_zoom_in_all", "ZoomInAll", cmdnames.MATH_NAV_ZOOM_IN_ALL, "Down", "ctrl_shift"),
    ("math_zoom_out_all", "ZoomOutAll", cmdnames.MATH_NAV_ZOOM_OUT_ALL, "Up", "ctrl_shift"),
    ("math_move_start", "MoveStart", cmdnames.MATH_NAV_MOVE_START, "Home", "none"),
    ("math_move_end", "MoveEnd", cmdnames.MATH_NAV_MOVE_END, "End", "none"),
    ("math_move_line_start", "MoveLineStart", cmdnames.MATH_NAV_MOVE_LINE_START, "Home", "ctrl"),
    ("math_move_line_end", "MoveLineEnd", cmdnames.MATH_NAV_MOVE_LINE_END, "End", "ctrl"),
    (
        "math_move_column_start",
        "MoveColumnStart",
        cmdnames.MATH_NAV_MOVE_COLUMN_START,
        "Home",
        "shift",
    ),
    (
        "math_move_column_end",
        "MoveColumnEnd",
        cmdnames.MATH_NAV_MOVE_COLUMN_END,
        "End",
        "shift",
    ),
    (
        "math_move_cell_previous",
        "MoveCellPrevious",
        cmdnames.MATH_NAV_MOVE_CELL_PREVIOUS,
        "Left",
        "ctrl",
    ),
    (
        "math_move_cell_next",
        "MoveCellNext",
        cmdnames.MATH_NAV_MOVE_CELL_NEXT,
        "Right",
        "ctrl",
    ),
    ("math_move_cell_up", "MoveCellUp", cmdnames.MATH_NAV_MOVE_CELL_UP, "Up", "ctrl"),
    (
        "math_move_cell_down",
        "MoveCellDown",
        cmdnames.MATH_NAV_MOVE_CELL_DOWN,
        "Down",
        "ctrl",
    ),
    (
        "math_move_last_location",
        "MoveLastLocation",
        cmdnames.MATH_NAV_MOVE_LAST_LOCATION,
        "BackSpace",
        "none",
    ),
    (
        "math_toggle_zoom_lock_up",
        "ToggleZoomLockUp",
        cmdnames.MATH_NAV_TOGGLE_ZOOM_LOCK_UP,
        "Up",
        "shift",
    ),
    (
        "math_toggle_zoom_lock_down",
        "ToggleZoomLockDown",
        cmdnames.MATH_NAV_TOGGLE_ZOOM_LOCK_DOWN,
        "Down",
        "shift",
    ),
    (
        "math_toggle_speech_mode",
        "ToggleSpeakMode",
        cmdnames.MATH_NAV_TOGGLE_SPEECH_MODE,
        "space",
        "shift",
    ),
    ("math_read_previous", "ReadPrevious", cmdnames.MATH_NAV_READ_PREVIOUS, "Left", "shift"),
    ("math_read_next", "ReadNext", cmdnames.MATH_NAV_READ_NEXT, "Right", "shift"),
    ("math_read_current", "ReadCurrent", cmdnames.MATH_NAV_READ_CURRENT, "space", "none"),
    (
        "math_read_cell_current",
        "ReadCellCurrent",
        cmdnames.MATH_NAV_READ_CELL_CURRENT,
        "space",
        "ctrl",
    ),
    (
        "math_describe_previous",
        "DescribePrevious",
        cmdnames.MATH_NAV_DESCRIBE_PREVIOUS,
        "Left",
        "ctrl_shift",
    ),
    (
        "math_describe_next",
        "DescribeNext",
        cmdnames.MATH_NAV_DESCRIBE_NEXT,
        "Right",
        "ctrl_shift",
    ),
    (
        "math_describe_current",
        "DescribeCurrent",
        cmdnames.MATH_NAV_DESCRIBE_CURRENT,
        "space",
        "ctrl_shift",
    ),
    ("math_where_am_i", "WhereAmI", cmdnames.MATH_NAV_WHERE_AM_I, "", "unbound"),
    ("math_where_am_i_all", "WhereAmIAll", cmdnames.MATH_NAV_WHERE_AM_I_ALL, "", "unbound"),
    ("math_exit", "Exit", cmdnames.MATH_NAV_EXIT, "Escape", "none"),
    ("math_copy", "Copy", cmdnames.MATH_NAV_COPY, "", "unbound"),
)

MODIFIER_MASKS = {
    "none": keybindings.NO_MODIFIER_MASK,
    "ctrl": keybindings.CTRL_MODIFIER_MASK,
    "shift": keybindings.SHIFT_MODIFIER_MASK,
    "ctrl_shift": keybindings.CTRL_SHIFT_MODIFIER_MASK,
}


def _keybinding(key: str, modifier_name: str) -> keybindings.KeyBinding | None:
    """Returns the keybinding for key and modifier_name."""

    if modifier_name == "unbound":
        return None
    return keybindings.KeyBinding(key, MODIFIER_MASKS[modifier_name])


def get_supported_commands() -> list[str]:
    """Returns MathCAT navigation commands supported by the math navigator."""

    commands = [mathcat_command for _name, mathcat_command, _desc, _key, _mod in COMMAND_SPECS]
    for digit in range(10):
        commands.extend(f"{prefix}{digit}" for prefix in PLACE_MARKER_PREFIXES)
    return commands


def get_commands(owner: MathNavigator) -> list[Command]:
    """Returns commands for math navigation."""

    enter_binding = keybindings.KeyBinding("m", keybindings.ORCA_ALT_MODIFIER_MASK)
    commands: list[Command] = [
        KeyboardCommand(
            "math_enter",
            owner.enter_math_mode_command,
            owner.GROUP_LABEL,
            cmdnames.MATH_NAV_ENTER,
            desktop_keybinding=enter_binding,
            laptop_keybinding=enter_binding,
            is_group_toggle=True,
        )
    ]
    for name, mathcat_command, description, key, modifier_name in COMMAND_SPECS:
        if mathcat_command == "Exit":
            handler = owner.exit_math_mode
        elif mathcat_command == "Copy":
            handler = owner.copy_to_clipboard
        else:
            handler = partial(owner._execute_command, mathcat_command)  # pylint: disable=protected-access
        binding = _keybinding(key, modifier_name)
        commands.append(
            KeyboardCommand(
                name,
                handler,
                owner.GROUP_LABEL,
                description,
                desktop_keybinding=binding,
                laptop_keybinding=binding,
            )
        )

    marker_types = (
        ("none", PLACE_MARKER_PREFIXES[0], cmdnames.MATH_NAV_GOTO_PLACE_MARKER),
        ("ctrl", PLACE_MARKER_PREFIXES[1], cmdnames.MATH_NAV_SET_PLACE_MARKER),
        ("shift", PLACE_MARKER_PREFIXES[2], cmdnames.MATH_NAV_READ_PLACE_MARKER),
        (
            "ctrl_shift",
            PLACE_MARKER_PREFIXES[3],
            cmdnames.MATH_NAV_DESCRIBE_PLACE_MARKER,
        ),
    )
    for digit in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0"):
        for modifier_name, command_prefix, description in marker_types:
            binding = keybindings.KeyBinding(digit, MODIFIER_MASKS[modifier_name])
            commands.append(
                KeyboardCommand(
                    f"math_{command_prefix.lower()}_{digit}",
                    partial(owner._execute_command, f"{command_prefix}{digit}"),  # pylint: disable=protected-access
                    owner.GROUP_LABEL,
                    description,
                    desktop_keybinding=binding,
                    laptop_keybinding=binding,
                )
            )

    return commands
