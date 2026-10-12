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

"""Tests a grid where selection does not follow focus."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
@pytest.mark.parametrize("table_navigation", [False, True], ids=["application", "orca-table"])
def test_select_and_unselect_grid_cells(
    web_grid_selection: BrowserSession, table_navigation: bool
) -> None:
    """Tests selecting cells independently and unselecting them after moving focus."""

    session = web_grid_selection
    reset_web_state(session)
    modifiers = [keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L] if table_navigation else []
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == [
        "Activities",
        "table with 3 rows 2 columns",
        "Morning column header Reading",
        "not selected",
        "Focus mode",
    ]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    # Writing starts selected; moving focus around the grid must preserve selection.
    for key, text, header, row, column, selected in (
        (keyboard.KEYSYM_RIGHT, "Writing", "Afternoon", 2, 2, True),
        (keyboard.KEYSYM_DOWN, "Art", "Afternoon", 3, 2, False),
        (keyboard.KEYSYM_LEFT, "Music", "Morning", 3, 1, False),
        (keyboard.KEYSYM_UP, "Reading", "Morning", 2, 1, False),
    ):
        keyboard.press_chord(modifiers, key)
        spoken, brailled = capture(session)
        horizontal = key in (keyboard.KEYSYM_LEFT, keyboard.KEYSYM_RIGHT)
        expected = [f"{header} column header {text}" if horizontal else text]
        if not selected:
            expected.append("not selected")
        if table_navigation:
            coordinates = f"Row {row}, column {column}."
            line = BrailleLine(0, coordinates, coordinates, "\x00" * len(coordinates))
        else:
            coordinates = f"column {column}" if horizontal else f"row {row}"
            full = f" {header} column header {text}"
            line = BrailleLine(1, full, text, "\x00" * len(full))
        expected.append(coordinates)
        assert " ".join(spoken) == " ".join(expected)
        assert brailled[-1] == line

    for key, text, header, column, expected in (
        (None, "Reading", "Morning", 1, "selected"),
        (keyboard.KEYSYM_RIGHT, "Writing", "Afternoon", 2, "unselected"),
        (keyboard.KEYSYM_LEFT, "Reading", "Morning", 1, "unselected"),
        (keyboard.KEYSYM_RIGHT, "Writing", "Afternoon", 2, "selected"),
    ):
        if key is not None:
            keyboard.press_chord(modifiers, key)
            spoken, brailled = capture(session)
            if table_navigation:
                coordinates = f"Row 2, column {column}."
                line = BrailleLine(0, coordinates, coordinates, "\x00" * len(coordinates))
            else:
                coordinates = f"column {column}"
                full = f" {header} column header {text}"
                line = BrailleLine(1, full, text, "\x00" * len(full))
            state = "not selected " if expected == "selected" else ""
            assert " ".join(spoken) == f"{header} column header {text} {state}{coordinates}"
            assert brailled[-1] == line
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        spoken, brailled = capture(session)
        assert spoken == [expected]
        assert brailled[-1] == BrailleLine(0, expected, expected, "\x00" * len(expected))

    keyboard.press_chord(modifiers, keyboard.KEYSYM_LEFT)
    spoken, brailled = capture(session)
    coordinates = "Row 2, column 1." if table_navigation else "column 1"
    assert " ".join(spoken) == f"Morning column header Reading not selected {coordinates}"
    if table_navigation:
        assert brailled[-1] == BrailleLine(0, coordinates, coordinates, "\x00" * len(coordinates))
    else:
        assert brailled[-1] == BrailleLine(
            1, " Morning column header Reading", "Reading", "\x00" * 30
        )
