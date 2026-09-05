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

"""Tests presentation of an ARIA data grid navigated with its own arrow keys in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_arrow_navigation_through_grid_cells(web_data_grid: NativeAppSession) -> None:
    """Tests arrowing through the grid's cells and jumping to the last and first one."""

    session = web_data_grid
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == [
        "table with 3 rows 3 columns",
        "Month",
        "column header",
        "row 1",
        "column 1",
        "Focus mode",
    ]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Station", "column header", "column 2"]
    assert brailled[-1] == BrailleLine(
        1, "Station column header", "Station column header", "\x00" * 21
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Kendal", "row 2"]
    assert brailled[-1] == BrailleLine(1, " Station column header Kendal", "Kendal", "\x00" * 29)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Truro", "row 3"]
    assert brailled[-1] == BrailleLine(1, " Station column header Truro", "Truro", "\x00" * 28)

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["Month column header February", "column 1"]
    assert brailled[-1] == BrailleLine(1, " Month column header February", "February", "\x00" * 29)

    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["Millimetres column header 61", "column 3"]
    assert brailled[-1] == BrailleLine(1, " Millimetres column header 61", "61", "\x00" * 29)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["Millimetres 61", "column 3 of 3 row 3 of 3"]
    assert brailled[-1] == BrailleLine(1, " Millimetres column header 61", "61", "\x00" * 29)

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = capture(session)
    assert spoken == ["Station column header Truro", "column 2"]
    assert brailled[-1] == BrailleLine(1, " Station column header Truro", "Truro", "\x00" * 28)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["Kendal", "row 2"]
    assert brailled[-1] == BrailleLine(1, " Station column header Kendal", "Kendal", "\x00" * 29)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["Millimetres column header 61", "row 3 column 3"]
    assert brailled[-1] == BrailleLine(1, " Millimetres column header 61", "61", "\x00" * 29)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["Month", "column header", "row 1", "column 1"]
    assert brailled[-1] == BrailleLine(1, "Month column header", "Month column header", "\x00" * 19)
