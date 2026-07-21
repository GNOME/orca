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

"""Tests navigation in an ARIA grid whose cells take their name from their contents."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_TITLE = "quarterly-report.pdf"
_URL = "From https://example.com"
_ACTIONS = "Copy download link Show in folder Delete from history"


def _table_nav(key: int) -> None:
    keyboard.press_chord([keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L], key)


@pytest.mark.native_app
def test_table_navigation_across_grid_cells(web_grid_named_cells: NativeAppSession) -> None:
    """Tests cell-by-cell navigation in focus mode, where the cells are presented as a whole."""

    session = web_grid_named_cells
    reset_web_state(session)
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    assert capture(session) == (
        [
            "t",
            "table with 2 rows 3 columns",
            "Yesterday quarterly-report.pdf From https://example.com Copy download link "
            "Show in folder Delete from history",
        ],
        [BrailleLine(1, _TITLE, _TITLE, "\x00" * 20)],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    assert capture(session) == (
        ["Focus mode"],
        [BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)],
    )

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [_URL, "Row 1, column 2."],
        [
            BrailleLine(1, _TITLE, _TITLE, "\x00" * 20),
            BrailleLine(0, _URL, _URL, "\x00" * 24),
            BrailleLine(0, "Row 1, column 2.", "Row 1, column 2.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [_ACTIONS, "Row 1, column 3."],
        [
            BrailleLine(0, _URL, _URL, "\x00" * 24),
            BrailleLine(0, _ACTIONS, "Copy download link Show in folde", "\x00" * 53),
            BrailleLine(0, "Row 1, column 3.", "Row 1, column 3.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [_URL, "Row 1, column 2."],
        [
            BrailleLine(0, _ACTIONS, "Copy download link Show in folde", "\x00" * 53),
            BrailleLine(0, _URL, _URL, "\x00" * 24),
            BrailleLine(0, "Row 1, column 2.", "Row 1, column 2.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [_TITLE, "Row 1, column 1."],
        [
            BrailleLine(0, _URL, _URL, "\x00" * 24),
            BrailleLine(0, _TITLE, _TITLE, "\x00" * 20),
            BrailleLine(0, "Row 1, column 1.", "Row 1, column 1.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["meeting-notes.pdf", "Row 2, column 1."],
        [
            BrailleLine(0, _TITLE, _TITLE, "\x00" * 20),
            BrailleLine(0, "meeting-notes.pdf", "meeting-notes.pdf", "\x00" * 17),
            BrailleLine(0, "Row 2, column 1.", "Row 2, column 1.", "\x00" * 16),
        ],
    )
