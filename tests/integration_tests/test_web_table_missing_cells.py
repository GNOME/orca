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

"""Tests table navigation around a missing cell."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _table_nav(key: int) -> None:
    keyboard.press_chord([keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L], key)


@pytest.mark.native_app
def test_navigation_around_a_missing_cell(web_missing_cells: NativeAppSession) -> None:
    """Tests cell navigation across a missing cell from each side."""

    session = web_missing_cells
    move_to_top(session)

    # The body has a hole: the first body row holds only the rowspan'd "Gemini Pro" in
    # column 1, so the cells under "Type"/"Price" in that row do not exist.
    keyboard.tap_key(keyboard.KEYSYM_T)
    assert capture(session) == (
        ["t", "table with 4 rows 3 columns", "Model", "column header"],
        [BrailleLine(1, "Model", "Model", "\x00" * 5)],
    )

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Type", "column header", "Row 1, column 2."],
        [
            BrailleLine(1, "Type", "Type", "\x00" * 4),
            BrailleLine(0, "Row 1, column 2.", "Row 1, column 2.", "\x00" * 16),
        ],
    )

    # Down from the "Type" header skips the missing cell to the body cell below it.
    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Type column header Input", "Row 3, column 2."],
        [
            BrailleLine(1, "Type", "Type", "\x00" * 4),
            BrailleLine(1, "Input", "Input", "\x00" * 5),
            BrailleLine(0, "Row 3, column 2.", "Row 3, column 2.", "\x00" * 16),
        ],
    )

    # Up from "Input" skips the missing cell back to the header above it.
    _table_nav(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Type", "column header", "Row 1, column 2."],
        [
            BrailleLine(1, "Input", "Input", "\x00" * 5),
            BrailleLine(1, "Type", "Type", "\x00" * 4),
            BrailleLine(0, "Row 1, column 2.", "Row 1, column 2.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["Model", "column header", "Row 1, column 1."],
        [
            BrailleLine(1, "Type", "Type", "\x00" * 4),
            BrailleLine(1, "Model", "Model", "\x00" * 5),
            BrailleLine(0, "Row 1, column 1.", "Row 1, column 1.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Gemini Pro", "Row 2, column 1.", "Cell spans 3 rows"],
        [
            BrailleLine(1, "Model", "Model", "\x00" * 5),
            BrailleLine(1, "Gemini Pro", "Gemini Pro", "\x00" * 10),
            BrailleLine(0, "Row 2, column 1.", "Row 2, column 1.", "\x00" * 16),
            BrailleLine(0, "Cell spans 3 rows", "Cell spans 3 rows", "\x00" * 17),
        ],
    )

    # Right from "Gemini Pro" skips the missing cells in its own row to the first real cell
    # to its right, which lives in a lower row of the cell's span.
    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Input", "Row 3, column 2."],
        [
            BrailleLine(1, "Gemini Pro", "Gemini Pro", "\x00" * 10),
            BrailleLine(1, "Input", "Input", "\x00" * 5),
            BrailleLine(0, "Row 3, column 2.", "Row 3, column 2.", "\x00" * 16),
        ],
    )
