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

"""Tests reorder announcements for a sortable ARIA table."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_row_reorder_announced(web_sortable_table: NativeAppSession) -> None:
    """Tests that activating the sort button announces the row reorder and sort order."""

    session = web_sortable_table
    move_to_top(session)

    # T lands focus on the in-table "Name" header button, so the reorder events
    # the sort fires have the focused table as their source.
    keyboard.tap_key(keyboard.KEYSYM_T)
    assert capture(session) == (
        ["t", "table with 4 rows 2 columns", "column header", "Name", "button"],
        [BrailleLine(1, "Name button", "Name button", "\x00" * 11)],
    )

    # Each Return re-sorts the rows: none -> ascending -> descending -> ascending.
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    assert capture(session, wait_async=True) == (
        ["Rows reordered", "Name. sorted ascending"],
        [
            BrailleLine(0, "Rows reordered", "Rows reordered", "\x00" * 14),
            BrailleLine(0, "Name. sorted ascending", "Name. sorted ascending", "\x00" * 22),
        ],
    )

    # Sorts after the first carry a leading "Name button" focus-repaint braille line.
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    assert capture(session, wait_async=True) == (
        ["Rows reordered", "Name. sorted descending"],
        [
            BrailleLine(1, "Name button", "Name button", "\x00" * 11),
            BrailleLine(0, "Rows reordered", "Rows reordered", "\x00" * 14),
            BrailleLine(0, "Name. sorted descending", "Name. sorted descending", "\x00" * 23),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    assert capture(session, wait_async=True) == (
        ["Rows reordered", "Name. sorted ascending"],
        [
            BrailleLine(1, "Name button", "Name button", "\x00" * 11),
            BrailleLine(0, "Rows reordered", "Rows reordered", "\x00" * 14),
            BrailleLine(0, "Name. sorted ascending", "Name. sorted ascending", "\x00" * 22),
        ],
    )


@pytest.mark.native_app
def test_column_reorder_announced(web_sortable_table: NativeAppSession) -> None:
    """Tests that toggling a row header's sort order announces the column reorder."""

    session = web_sortable_table
    move_to_top(session)

    # Chromium emits object:column-reordered when a row header's aria-sort changes,
    # so T twice reaches the second table's "Region" row-header button. The Name
    # header reports "sorted ascending" because test_row_reorder_announced ran first.
    keyboard.tap_key(keyboard.KEYSYM_T)
    assert capture(session) == (
        ["t", "table with 4 rows 2 columns", "column header sorted ascending", "Name", "button"],
        [BrailleLine(1, "Name button", "Name button", "\x00" * 11)],
    )

    keyboard.tap_key(keyboard.KEYSYM_T)
    assert capture(session) == (
        [
            "t",
            "Name",
            "column header sorted ascending",
            "leaving table.",
            "table with 2 rows 3 columns",
            "row header",
            "Region",
            "button",
        ],
        [BrailleLine(1, "Region button", "Region button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    assert capture(session, wait_async=True) == (
        ["Columns reordered", "Region. sorted ascending"],
        [
            BrailleLine(0, "Columns reordered", "Columns reordered", "\x00" * 17),
            BrailleLine(0, "Region. sorted ascending", "Region. sorted ascending", "\x00" * 24),
        ],
    )

    # Sorts after the first carry a leading "Region button" focus-repaint braille line.
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    assert capture(session, wait_async=True) == (
        ["Columns reordered", "Region. sorted descending"],
        [
            BrailleLine(1, "Region button", "Region button", "\x00" * 13),
            BrailleLine(0, "Columns reordered", "Columns reordered", "\x00" * 17),
            BrailleLine(0, "Region. sorted descending", "Region. sorted descending", "\x00" * 25),
        ],
    )
