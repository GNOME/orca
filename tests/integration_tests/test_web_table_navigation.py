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


def _orca_table_nav(session: NativeAppSession, key: int) -> None:
    session.orca.press_orca_key(
        key, extra_modifiers=[keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L]
    )


def _enter_third_table(session: NativeAppSession) -> None:
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_T)
        capture(session)
    keyboard.tap_key(keyboard.KEYSYM_T)


def _enter_fourth_table(session: NativeAppSession) -> None:
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_T)
        capture(session)
    keyboard.tap_key(keyboard.KEYSYM_T)


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
        ["Ada", "Engineer", "link", "London", "link"],
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
        "link",
        "London",
        "link",
        "Grace",
        "row 3",
        "column 1",
        "Admiral",
        "Boston",
        "link",
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
        "table with 5 rows 5 columns",
        "Standard",
        "column header",
        "Premium",
        "column header",
        "Input",
        "column header",
        "Output",
        "column header",
        "Input",
        "column header",
        "Output",
        "column header",
        "Gemini Pro",
        "row header",
        "1.00",
        "2.00",
        "3.00",
        "4.00",
        "Gemini Flash",
        "row header",
        "0.10",
        "0.20",
        "0.30",
        "0.40",
        "Gemini Nano",
        "row header",
        "0.01",
        "0.02",
        "0.03",
        "0.04",
        "leaving table.",
        "table with 4 rows 3 columns",
        "Student scores",
        "caption",
        "Pupil",
        "Score",
        "Grade",
        "Liu",
        "90",
        "A",
        "Park",
        "B",
        "Vega",
        "70",
        "C",
        "leaving table.",
        "After the tables.",
    ]


@pytest.mark.native_app
def test_first_and_last_cell(web_tables: NativeAppSession) -> None:
    """Tests jumping to the first and last cell of a table."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    capture(session)

    keyboard.press_chord([keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_HOME)
    assert capture(session) == (
        ["blank", "Row 1, column 1."],
        [
            BrailleLine(1, "Engineer", "Engineer", "\xc0" * 8),
            BrailleLine(1, "", "", None),
            BrailleLine(0, "Row 1, column 1.", "Row 1, column 1.", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    assert capture(session) == (
        ["Grace row header Office column header", "Boston", "link", "Row 4, column 4."],
        [
            BrailleLine(1, "", "", None),
            BrailleLine(1, "Boston", "Boston", "\xc0" * 6),
            BrailleLine(0, "Row 4, column 4.", "Row 4, column 4.", "\x00" * 16),
        ],
    )


@pytest.mark.native_app
def test_row_and_column_extremes(web_tables: NativeAppSession) -> None:
    """Tests jumping to the beginning/end of a row and top/bottom of a column."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    capture(session)

    _orca_table_nav(session, keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["Ada", "row header", "Row 2, column 1."],
        [
            BrailleLine(1, "Engineer", "Engineer", "\xc0" * 8),
            BrailleLine(1, "Ada", "Ada", "\x00" * 3),
            BrailleLine(0, "Row 2, column 1.", "Row 2, column 1.", "\x00" * 16),
        ],
    )

    _orca_table_nav(session, keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["Beginning of row."],
        [
            BrailleLine(1, "Ada", "Ada", "\x00" * 3),
            BrailleLine(0, "Beginning of row.", "Beginning of row.", "\x00" * 17),
        ],
    )

    _orca_table_nav(session, keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Office column header", "London", "link", "Row 2, column 3."],
        [
            BrailleLine(1, "Ada", "Ada", "\x00" * 3),
            BrailleLine(1, "London", "London", "\xc0" * 6),
            BrailleLine(0, "Row 2, column 3.", "Row 2, column 3.", "\x00" * 16),
        ],
    )

    _orca_table_nav(session, keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["End of row."],
        [
            BrailleLine(1, "London", "London", "\xc0" * 6),
            BrailleLine(0, "End of row.", "End of row.", "\x00" * 11),
        ],
    )

    _orca_table_nav(session, keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Office", "column header", "Row 1, column 3."],
        [
            BrailleLine(1, "London", "London", "\xc0" * 6),
            BrailleLine(1, "Office", "Office", "\x00" * 6),
            BrailleLine(0, "Row 1, column 3.", "Row 1, column 3.", "\x00" * 16),
        ],
    )

    _orca_table_nav(session, keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Top of column."],
        [
            BrailleLine(1, "Office", "Office", "\x00" * 6),
            BrailleLine(0, "Top of column.", "Top of column.", "\x00" * 14),
        ],
    )

    _orca_table_nav(session, keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Grace row header", "Boston", "link", "Row 3, column 3."],
        [
            BrailleLine(1, "Office", "Office", "\x00" * 6),
            BrailleLine(1, "Boston", "Boston", "\xc0" * 6),
            BrailleLine(0, "Row 3, column 3.", "Row 3, column 3.", "\x00" * 16),
        ],
    )

    _orca_table_nav(session, keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Bottom of column."],
        [
            BrailleLine(1, "Boston", "Boston", "\xc0" * 6),
            BrailleLine(0, "Bottom of column.", "Bottom of column.", "\x00" * 17),
        ],
    )


@pytest.mark.native_app
def test_navigation_boundary_messages(web_tables: NativeAppSession) -> None:
    """Tests the boundary messages reached by plain cell-by-cell navigation."""

    session = web_tables
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)

    _table_nav(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["Beginning of row."],
        [
            BrailleLine(1, "Ada", "Ada", "\x00" * 3),
            BrailleLine(0, "Beginning of row.", "Beginning of row.", "\x00" * 17),
        ],
    )

    _table_nav(keyboard.KEYSYM_RIGHT)
    capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["End of row."],
        [
            BrailleLine(1, "London", "London", "\xc0" * 6),
            BrailleLine(0, "End of row.", "End of row.", "\x00" * 11),
        ],
    )

    _table_nav(keyboard.KEYSYM_UP)
    capture(session)
    _table_nav(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Top of column."],
        [
            BrailleLine(1, "Office", "Office", "\x00" * 6),
            BrailleLine(0, "Top of column.", "Top of column.", "\x00" * 14),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Bottom of column."],
        [
            BrailleLine(1, "Boston", "Boston", "\xc0" * 6),
            BrailleLine(0, "Bottom of column.", "Bottom of column.", "\x00" * 17),
        ],
    )


@pytest.mark.native_app
def test_toggle_table_navigation(web_tables: NativeAppSession) -> None:
    """Tests disabling and re-enabling table navigation from inside a table."""

    session = web_tables
    move_to_top(session)

    try:
        keyboard.tap_key(keyboard.KEYSYM_T)
        capture(session)
        _table_nav(keyboard.KEYSYM_DOWN)
        capture(session)

        session.orca.press_orca_key(keyboard.KEYSYM_T, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
        assert capture(session) == (
            ["Table navigation disabled."],
            [
                BrailleLine(1, "Ada", "Ada", "\x00" * 3),
                BrailleLine(
                    0,
                    "Table navigation disabled.",
                    "Table navigation disabled.",
                    "\x00" * 26,
                ),
            ],
        )

        _table_nav(keyboard.KEYSYM_RIGHT)
        assert capture(session) == ([], [BrailleLine(1, "Ada", "Ada", "\x00" * 3)])

        session.orca.press_orca_key(keyboard.KEYSYM_T, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
        assert capture(session) == (
            ["Table navigation enabled."],
            [
                BrailleLine(
                    0,
                    "Table navigation enabled.",
                    "Table navigation enabled.",
                    "\x00" * 25,
                )
            ],
        )
    finally:
        session.orca.set("TableNavigator", "IsEnabled", True)


@pytest.mark.native_app
def test_nested_header_corner_boundaries(web_tables: NativeAppSession) -> None:
    """Tests the boundary messages at the empty corner of the nested-header table."""

    session = web_tables
    move_to_top(session)

    _enter_third_table(session)
    assert capture(session) == (
        ["t", "leaving table.", "table with 5 rows 5 columns"],
        [BrailleLine(1, "", "", None)],
    )

    _table_nav(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["Beginning of row."],
        [BrailleLine(0, "Beginning of row.", "Beginning of row.", "\x00" * 17)],
    )

    _table_nav(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Top of column."],
        [
            BrailleLine(1, "", "", None),
            BrailleLine(0, "Top of column.", "Top of column.", "\x00" * 14),
        ],
    )

    _table_nav(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["Beginning of row."],
        [
            BrailleLine(1, "", "", None),
            BrailleLine(0, "Beginning of row.", "Beginning of row.", "\x00" * 17),
        ],
    )

    _table_nav(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Top of column."],
        [
            BrailleLine(1, "", "", None),
            BrailleLine(0, "Top of column.", "Top of column.", "\x00" * 14),
        ],
    )


@pytest.mark.native_app
def test_nested_column_headers_into_body(web_tables: NativeAppSession) -> None:
    """Tests that Down from a multi-level column header enters the table body."""

    session = web_tables
    move_to_top(session)

    _enter_third_table(session)
    capture(session)
    _table_nav(keyboard.KEYSYM_LEFT)
    capture(session)
    _table_nav(keyboard.KEYSYM_UP)
    capture(session)

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Standard", "column header", "Row 1, column 2.", "Cell spans 2 columns"],
        [
            BrailleLine(1, "", "", None),
            BrailleLine(1, "Standard", "Standard", "\x00" * 8),
            BrailleLine(0, "Row 1, column 2.", "Row 1, column 2.", "\x00" * 16),
            BrailleLine(0, "Cell spans 2 columns", "Cell spans 2 columns", "\x00" * 20),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Input", "column header", "Row 2, column 2."],
        [
            BrailleLine(1, "Standard", "Standard", "\x00" * 8),
            BrailleLine(1, "Input", "Input", "\x00" * 5),
            BrailleLine(0, "Row 2, column 2.", "Row 2, column 2.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Gemini Pro row header 1.00", "Row 3, column 2."],
        [
            BrailleLine(1, "Input", "Input", "\x00" * 5),
            BrailleLine(1, "1.00", "1.00", "\x00" * 4),
            BrailleLine(0, "Row 3, column 2.", "Row 3, column 2.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Gemini Flash row header 0.10", "Row 4, column 2."],
        [
            BrailleLine(1, "1.00", "1.00", "\x00" * 4),
            BrailleLine(1, "0.10", "0.10", "\x00" * 4),
            BrailleLine(0, "Row 4, column 2.", "Row 4, column 2.", "\x00" * 16),
        ],
    )


@pytest.mark.native_app
def test_nested_header_corner_through_row_headers(web_tables: NativeAppSession) -> None:
    """Tests that Down from the corner moves down the row-header column into the body."""

    session = web_tables
    move_to_top(session)

    _enter_third_table(session)
    capture(session)
    _table_nav(keyboard.KEYSYM_LEFT)
    capture(session)
    _table_nav(keyboard.KEYSYM_UP)
    capture(session)

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["blank", "Row 2, column 1."],
        [
            BrailleLine(1, "", "", None),
            BrailleLine(1, "", "", None),
            BrailleLine(0, "Row 2, column 1.", "Row 2, column 1.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Gemini Pro", "row header", "Row 3, column 1."],
        [
            BrailleLine(1, "", "", None),
            BrailleLine(1, "Gemini Pro", "Gemini Pro", "\x00" * 10),
            BrailleLine(0, "Row 3, column 1.", "Row 3, column 1.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Gemini Flash", "row header", "Row 4, column 1."],
        [
            BrailleLine(1, "Gemini Pro", "Gemini Pro", "\x00" * 10),
            BrailleLine(1, "Gemini Flash", "Gemini Flash", "\x00" * 12),
            BrailleLine(0, "Row 4, column 1.", "Row 4, column 1.", "\x00" * 16),
        ],
    )


@pytest.mark.native_app
def test_multi_level_header_order(web_tables: NativeAppSession) -> None:
    """Tests that a body cell's two column headers are announced group-then-subheader."""

    session = web_tables
    move_to_top(session)

    _enter_third_table(session)
    capture(session)
    _table_nav(keyboard.KEYSYM_LEFT)
    capture(session)
    _table_nav(keyboard.KEYSYM_UP)
    capture(session)
    for _ in range(3):
        _table_nav(keyboard.KEYSYM_DOWN)
        capture(session)

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Standard. Input column header 0.10", "Row 4, column 2."],
        [
            BrailleLine(1, "Gemini Flash", "Gemini Flash", "\x00" * 12),
            BrailleLine(1, "0.10", "0.10", "\x00" * 4),
            BrailleLine(0, "Row 4, column 2.", "Row 4, column 2.", "\x00" * 16),
        ],
    )


@pytest.mark.native_app
def test_dynamic_column_headers(web_tables: NativeAppSession) -> None:
    """Tests setting and clearing the row used as dynamic column headers."""

    session = web_tables
    move_to_top(session)

    try:
        _enter_fourth_table(session)
        capture(session)
        _table_nav(keyboard.KEYSYM_DOWN)
        capture(session)

        _table_nav(keyboard.KEYSYM_RIGHT)
        assert capture(session) == (
            ["90", "Row 2, column 2."],
            [
                BrailleLine(1, "Liu", "Liu", "\x00" * 3),
                BrailleLine(1, "90", "90", "\x00" * 2),
                BrailleLine(0, "Row 2, column 2.", "Row 2, column 2.", "\x00" * 16),
            ],
        )

        _table_nav(keyboard.KEYSYM_UP)
        capture(session)
        _table_nav(keyboard.KEYSYM_LEFT)
        capture(session)

        session.orca.press_orca_key(keyboard.KEYSYM_R, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
        assert capture(session) == (
            ["Dynamic column header set for row 1"],
            [
                BrailleLine(1, "Pupil", "Pupil", "\x00" * 5),
                BrailleLine(
                    0,
                    "Dynamic column header set for row 1",
                    "Dynamic column header set for ro",
                    "\x00" * 35,
                ),
            ],
        )

        _table_nav(keyboard.KEYSYM_DOWN)
        capture(session)

        _table_nav(keyboard.KEYSYM_RIGHT)
        assert capture(session) == (
            ["Score column header 90", "Row 2, column 2."],
            [
                BrailleLine(1, "Liu", "Liu", "\x00" * 3),
                BrailleLine(1, "90", "90", "\x00" * 2),
                BrailleLine(0, "Row 2, column 2.", "Row 2, column 2.", "\x00" * 16),
            ],
        )

        session.orca.call("TableNavigator", "ClearDynamicColumnHeadersRow", True)
        assert capture(session) == (
            ["Dynamic column header cleared."],
            [
                BrailleLine(1, "90", "90", "\x00" * 2),
                BrailleLine(
                    0,
                    "Dynamic column header cleared.",
                    "Dynamic column header cleared.",
                    "\x00" * 30,
                ),
            ],
        )

        _table_nav(keyboard.KEYSYM_DOWN)
        assert capture(session) == (
            ["blank", "Row 3, column 2."],
            [
                BrailleLine(1, "90", "90", "\x00" * 2),
                BrailleLine(1, "", "", None),
                BrailleLine(0, "Row 3, column 2.", "Row 3, column 2.", "\x00" * 16),
            ],
        )
    finally:
        session.orca.call("TableNavigator", "ClearDynamicColumnHeadersRow", False)


@pytest.mark.native_app
def test_dynamic_row_headers(web_tables: NativeAppSession) -> None:
    """Tests setting and clearing the column used as dynamic row headers."""

    session = web_tables
    move_to_top(session)

    try:
        _enter_fourth_table(session)
        capture(session)

        session.orca.press_orca_key(keyboard.KEYSYM_C, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
        assert capture(session) == (
            ["Dynamic row header set for column 1"],
            [
                BrailleLine(
                    0,
                    "Dynamic row header set for column 1",
                    "Dynamic row header set for colum",
                    "\x00" * 35,
                )
            ],
        )

        _table_nav(keyboard.KEYSYM_RIGHT)
        capture(session)

        _table_nav(keyboard.KEYSYM_DOWN)
        assert capture(session) == (
            ["Liu row header 90", "Row 2, column 2."],
            [
                BrailleLine(1, "Score", "Score", "\x00" * 5),
                BrailleLine(1, "90", "90", "\x00" * 2),
                BrailleLine(0, "Row 2, column 2.", "Row 2, column 2.", "\x00" * 16),
            ],
        )

        session.orca.call("TableNavigator", "ClearDynamicRowHeadersColumn", True)
        assert capture(session) == (
            ["Dynamic row header cleared."],
            [
                BrailleLine(1, "90", "90", "\x00" * 2),
                BrailleLine(
                    0,
                    "Dynamic row header cleared.",
                    "Dynamic row header cleared.",
                    "\x00" * 27,
                ),
            ],
        )

        _table_nav(keyboard.KEYSYM_DOWN)
        assert capture(session) == (
            ["blank", "Row 3, column 2."],
            [
                BrailleLine(1, "90", "90", "\x00" * 2),
                BrailleLine(1, "", "", None),
                BrailleLine(0, "Row 3, column 2.", "Row 3, column 2.", "\x00" * 16),
            ],
        )
    finally:
        session.orca.call("TableNavigator", "ClearDynamicRowHeadersColumn", False)


@pytest.mark.native_app
def test_skip_blank_cells(web_tables: NativeAppSession) -> None:
    """Tests that skip-blank-cells skips an empty mid-column cell when enabled."""

    session = web_tables
    move_to_top(session)

    _enter_fourth_table(session)
    capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    capture(session)

    _table_nav(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["blank", "Row 3, column 2."],
        [
            BrailleLine(1, "90", "90", "\x00" * 2),
            BrailleLine(1, "", "", None),
            BrailleLine(0, "Row 3, column 2.", "Row 3, column 2.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_UP)
    capture(session)

    session.orca.set("TableNavigator", "SkipBlankCells", True)
    try:
        _table_nav(keyboard.KEYSYM_DOWN)
        assert capture(session) == (
            ["70", "Row 4, column 2."],
            [
                BrailleLine(1, "90", "90", "\x00" * 2),
                BrailleLine(1, "70", "70", "\x00" * 2),
                BrailleLine(0, "Row 4, column 2.", "Row 4, column 2.", "\x00" * 16),
            ],
        )
    finally:
        session.orca.set("TableNavigator", "SkipBlankCells", False)


@pytest.mark.native_app
def test_character_navigation_crosses_table_cells(web_tables: NativeAppSession) -> None:
    """Tests Right-arrow character navigation across cell boundaries within a table."""

    session = web_tables
    move_to_top(session)

    # Cell text runs together with no boundary announcement, the same as block text.
    stream = "ablesBefore the tables.RoleOfficeAdaEngineerLondonGraceAdmiralBoston"
    for char in stream:
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        assert speech(session) == [char]


@pytest.mark.native_app
def test_character_navigation_crosses_table_cells_backward(web_tables: NativeAppSession) -> None:
    """Tests Left-arrow character navigation back across cell boundaries within a table."""

    session = web_tables
    move_to_top(session)
    for _ in range(3):  # onto the row with Ada, Engineer, and London
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        speech(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    speech(session)

    # Walk back across the Ada / Engineer / London cell boundaries.
    stream = "nodnoLreenignEadA"
    for char in stream:
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        assert speech(session) == [char]


@pytest.mark.native_app
def test_word_navigation_across_table_cells(web_tables: NativeAppSession) -> None:
    """Tests Ctrl+Right word navigation visiting each cell, including headers and links."""

    session = web_tables
    move_to_top(session)

    expected = [
        ["Tables"],
        ["Before "],
        ["the "],
        ["tables"],
        ["Role"],
        ["Office"],
        ["Ada"],
        ["Engineer"],
        ["London"],
        ["Grace"],
        ["Admiral"],
        ["Boston"],
    ]
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        result.append(speech(session))
    assert result == expected


@pytest.mark.native_app
def test_word_navigation_across_table_cells_backward(web_tables: NativeAppSession) -> None:
    """Tests Ctrl+Left word navigation visiting each cell, including headers and links."""

    session = web_tables
    move_to_top(session)
    for _ in range(12):  # to the last cell of the first table
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        speech(session)

    expected = [
        ["Boston"],
        ["Admiral"],
        ["Grace"],
        ["London"],
        ["Engineer"],
        ["Ada"],
        ["Office"],
        ["Role"],
    ]
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
        result.append(speech(session))
    assert result == expected


@pytest.mark.native_app
def test_word_navigation_across_spanned_cells(web_tables: NativeAppSession) -> None:
    """Tests Ctrl+Right word navigation visiting each cell of a table with spanned cells."""

    session = web_tables
    move_to_top(session)
    for _ in range(12):  # past the first table
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        speech(session)

    expected = [
        ["P"],
        ["Q"],
        ["R"],
        ["Block"],
        ["One"],
        ["Two"],
        ["Three"],
        ["Wide"],
        ["Tall"],
        ["Four"],
        ["Five"],
        ["Six"],
        ["Seven"],
    ]
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        result.append(speech(session))
    assert result == expected


@pytest.mark.native_app
def test_word_navigation_across_spanned_cells_backward(web_tables: NativeAppSession) -> None:
    """Tests Ctrl+Left word navigation visiting each cell of a table with spanned cells."""

    session = web_tables
    move_to_top(session)
    for _ in range(25):  # to the last cell of the spanned table
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        speech(session)

    expected = [
        ["Seven"],
        ["Six"],
        ["Five"],
        ["Four"],
        ["Tall"],
        ["Wide"],
        ["Three"],
        ["Two"],
        ["One"],
        ["Block"],
        ["R"],
        ["Q"],
        ["P"],
    ]
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
        result.append(speech(session))
    assert result == expected
