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

"""Tests navigation on a web page with tables."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _table_nav(key: int) -> None:
    keyboard.press_chord([keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L], key)


@pytest.mark.native_app
def test_structural_navigation_by_table(web_tables: NativeAppSession) -> None:
    """Tests structural navigation by table."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    assert capture(session) == (
        ["t", "table with 3 rows 3 columns", "Role", "Office"],
        [BrailleLine(1, "", "", None)],
    )

    keyboard.tap_key(keyboard.KEYSYM_T)
    assert capture(session) == (
        ["t", "leaving table.", "table with 6 rows 3 columns", "P", "column header"],
        [BrailleLine(1, "P", "P", "\x00")],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_T)
    assert capture(session) == (
        ["T", "leaving table.", "table with 3 rows 3 columns"],
        [BrailleLine(1, "", "", None)],
    )


@pytest.mark.native_app
def test_table_navigation_by_column(web_tables: NativeAppSession) -> None:
    """Tests cell-by-cell table navigation across columns."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    assert capture(session) == (
        ["t", "table with 3 rows 3 columns", "Role", "Office"],
        [BrailleLine(1, "", "", None)],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Ada", "row header", "Row 2, column 1."],
        [
            BrailleLine(1, "Ada", "Ada", "\x00" * 3),
            BrailleLine(0, "Row 2, column 1.", "Row 2, column 1.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Role column header", "Engineer", "link", "Row 2, column 2."],
        [
            BrailleLine(1, "Ada", "Ada", "\x00" * 3),
            BrailleLine(1, "Engineer", "Engineer", "\xc0" * 8),
            BrailleLine(0, "Row 2, column 2.", "Row 2, column 2.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Office column header", "London", "link", "Row 2, column 3."],
        [
            BrailleLine(1, "Engineer", "Engineer", "\xc0" * 8),
            BrailleLine(1, "London", "London", "\xc0" * 6),
            BrailleLine(0, "Row 2, column 3.", "Row 2, column 3.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["Role column header", "Engineer", "link", "Row 2, column 2."],
        [
            BrailleLine(1, "London", "London", "\xc0" * 6),
            BrailleLine(1, "Engineer", "Engineer", "\xc0" * 8),
            BrailleLine(0, "Row 2, column 2.", "Row 2, column 2.", "\x00" * 16),
        ],
    )


@pytest.mark.native_app
def test_table_navigation_by_row(web_tables: NativeAppSession) -> None:
    """Tests cell-by-cell table navigation across rows."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    assert capture(session) == (
        ["t", "table with 3 rows 3 columns", "Role", "Office"],
        [BrailleLine(1, "", "", None)],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Ada", "row header", "Row 2, column 1."],
        [
            BrailleLine(1, "Ada", "Ada", "\x00" * 3),
            BrailleLine(0, "Row 2, column 1.", "Row 2, column 1.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Role column header", "Engineer", "link", "Row 2, column 2."],
        [
            BrailleLine(1, "Ada", "Ada", "\x00" * 3),
            BrailleLine(1, "Engineer", "Engineer", "\xc0" * 8),
            BrailleLine(0, "Row 2, column 2.", "Row 2, column 2.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Grace row header Admiral", "Row 3, column 2."],
        [
            BrailleLine(1, "Engineer", "Engineer", "\xc0" * 8),
            BrailleLine(1, "Admiral", "Admiral", "\x00" * 7),
            BrailleLine(0, "Row 3, column 2.", "Row 3, column 2.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Ada row header", "Engineer", "link", "Row 2, column 2."],
        [
            BrailleLine(1, "Admiral", "Admiral", "\x00" * 7),
            BrailleLine(1, "Engineer", "Engineer", "\xc0" * 8),
            BrailleLine(0, "Row 2, column 2.", "Row 2, column 2.", "\x00" * 16),
        ],
    )


@pytest.mark.native_app
def test_table_navigation_across_spanned_cells(web_tables: NativeAppSession) -> None:
    """Tests table navigation onto cells that span rows and/or columns."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_T)
    assert capture(session) == (
        ["t", "leaving table.", "table with 6 rows 3 columns", "P", "column header"],
        [BrailleLine(1, "P", "P", "\x00")],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Block", "Row 2, column 1.", "Cell spans 2 rows 2 columns"],
        [
            BrailleLine(1, "Block", "Block", "\x00" * 5),
            BrailleLine(0, "Row 2, column 1.", "Row 2, column 1.", "\x00" * 16),
            BrailleLine(
                0, "Cell spans 2 rows 2 columns", "Cell spans 2 rows 2 columns", "\x00" * 27
            ),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Q column header Wide", "Row 4, column 2.", "Cell spans 2 columns"],
        [
            BrailleLine(1, "Three", "Three", "\x00" * 5),
            BrailleLine(1, "Wide", "Wide", "\x00" * 4),
            BrailleLine(0, "Row 4, column 2.", "Row 4, column 2.", "\x00" * 16),
            BrailleLine(0, "Cell spans 2 columns", "Cell spans 2 columns", "\x00" * 20),
        ],
    )

    _table_nav(keyboard.KEYSYM_LEFT)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Tall", "Row 5, column 1.", "Cell spans 2 rows"],
        [
            BrailleLine(1, "Three", "Three", "\x00" * 5),
            BrailleLine(1, "Tall", "Tall", "\x00" * 4),
            BrailleLine(0, "Row 5, column 1.", "Row 5, column 1.", "\x00" * 16),
            BrailleLine(0, "Cell spans 2 rows", "Cell spans 2 rows", "\x00" * 17),
        ],
    )


@pytest.mark.native_app
def test_caret_navigation_in_a_table(web_tables: NativeAppSession) -> None:
    """Tests caret navigation into, through, and out of a table."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Before the tables."],
        [BrailleLine(1, "Before the tables.", "Before the tables.", "\x00" * 18)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "table with 3 rows 3 columns",
            "Role",
            "column header",
            "Office",
            "column header",
            "column 3",
        ],
        [BrailleLine(1, "Role Office", "Role Office", "\x00" * 11)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Ada", "Engineer", "London", "link"],
        [
            BrailleLine(
                1,
                "Ada Engineer London",
                "Ada Engineer London",
                "\x00" * 4 + "\xc0" * 8 + "\x00" + "\xc0" * 6,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Grace", "Role column header Admiral", "Boston", "link"],
        [BrailleLine(1, "Grace Admiral Boston", "Grace Admiral Boston", "\x00" * 14 + "\xc0" * 6)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "Grace row header Office column header",
            "row 3",
            "column 3",
            "leaving table.",
            "table with 6 rows 3 columns",
            "P",
            "column header",
            "Q",
            "column header",
            "column 2",
            "R",
            "column header",
            "column 3",
        ],
        [BrailleLine(1, "P Q R", "P Q R", "\x00" * 5)],
    )


@pytest.mark.native_app
def test_table_cell_where_am_i(web_tables: NativeAppSession) -> None:
    """Tests basic Where Am I in a table cell."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert capture(session) == (
        ["Grace Role Admiral", "column 2 of 3 row 3 of 3"],
        [
            BrailleLine(1, "Admiral", "Admiral", "\x00" * 7),
            BrailleLine(1, "Admiral", "Admiral", "\x00" * 7),
        ],
    )


@pytest.mark.native_app
def test_table_cell_detailed_where_am_i(web_tables: NativeAppSession) -> None:
    """Tests detailed Where Am I in a table cell."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert capture(session) == (
        ["Grace", "Admiral", "Boston", "1 of 2", "column 2 of 3 row 3 of 3"],
        [
            BrailleLine(1, "Admiral", "Admiral", "\x00" * 7),
            BrailleLine(1, "Admiral", "Admiral", "\x00" * 7),
            BrailleLine(1, "Admiral", "Admiral", "\x00" * 7),
        ],
    )


@pytest.mark.native_app
def test_row_header_where_am_i(web_tables: NativeAppSession) -> None:
    """Tests basic Where Am I on a row header."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert capture(session) == (
        ["Ada", "row header"],
        [BrailleLine(1, "Ada", "Ada", "\x00" * 3), BrailleLine(1, "Ada", "Ada", "\x00" * 3)],
    )


@pytest.mark.native_app
def test_column_header_where_am_i(web_tables: NativeAppSession) -> None:
    """Tests basic Where Am I on a column header."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert capture(session) == (
        ["Role", "column header"],
        [BrailleLine(1, "Role", "Role", "\x00" * 4), BrailleLine(1, "Role", "Role", "\x00" * 4)],
    )


@pytest.mark.native_app
def test_heading_where_am_i(web_tables: NativeAppSession) -> None:
    """Tests basic Where Am I on a heading."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert capture(session) == (
        ["Tables", "heading 1"],
        [BrailleLine(1, "Tables h1", "Tables h1", "\x00" * 9)],
    )


@pytest.mark.native_app
def test_word_navigation_stays_within_table_cell(web_tables: NativeAppSession) -> None:
    """Tests that Ctrl+Right word navigation does not cross into an adjacent table cell."""

    session = web_tables
    move_to_top(session)

    # Eleven Down arrows reach the row with "Four" and "Five" in adjacent cells.
    for _ in range(11):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

    # Both cells share a braille line, but the word stops at the cell boundary.
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Four"],
        [BrailleLine(5, "Four Five", "Four Five", "\x00" * 9)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Five"],
        [BrailleLine(5, "Four Five", "Five", "\x00" * 9)],
    )


@pytest.mark.native_app
def test_say_all_over_tables(web_tables: NativeAppSession) -> None:
    """Tests the utterances Say All speaks for a page of tables, from the top."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(session) == [
        "Tables",
        "Before the tables.",
        "table with 3 rows 3 columns",
        "Role",
        "column header",
        "Office",
        "column header",
        "Ada",
        "row header",
        "Engineer",
        "London",
        "Grace",
        "row 3",
        "column 1",
        "Admiral",
        "Boston",
        "P",
        "column header",
        "row 1",
        "column 1",
        "Q",
        "column header",
        "R",
        "column header",
        "Block",
        "One",
        "Two",
        "Three",
        "Wide",
        "Tall",
        "Four",
        "Five",
        "Six",
        "Seven",
        "leaving table.",
        "After the tables.",
    ]
