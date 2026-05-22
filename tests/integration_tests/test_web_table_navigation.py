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

from orca.output_reader import BrailleRecord, SpeechRecord

from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _capture(
    session: NativeAppSession,
) -> tuple[list[str], list[tuple[int, str, str | None]]]:
    records = session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    spoken = [r.text for r in records if isinstance(r, SpeechRecord)]
    brailled = [(r.cursor_cell, r.string, r.mask) for r in records if isinstance(r, BrailleRecord)]
    return spoken, brailled


def _move_to_top(session: NativeAppSession) -> None:
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _table_nav(key: int) -> None:
    keyboard.press_chord([keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L], key)


@pytest.mark.native_app
def test_structural_navigation_by_table(web_tables: NativeAppSession) -> None:
    """Tests structural navigation by table."""

    session = web_tables
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    assert _capture(session) == (
        ["t", "table with 3 rows 3 columns", "Role", "Office"],
        [(1, "", None)],
    )

    keyboard.tap_key(keyboard.KEYSYM_T)
    assert _capture(session) == (
        ["t", "leaving table.", "table with 6 rows 3 columns", "P", "column header"],
        [(1, "P", "\x00")],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_T)
    assert _capture(session) == (
        ["T", "leaving table.", "table with 3 rows 3 columns"],
        [(1, "", None)],
    )


@pytest.mark.native_app
def test_table_navigation_by_column(web_tables: NativeAppSession) -> None:
    """Tests cell-by-cell table navigation across columns."""

    session = web_tables
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    assert _capture(session) == (
        ["t", "table with 3 rows 3 columns", "Role", "Office"],
        [(1, "", None)],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Ada", "row header", "Row 2, column 1."],
        [(1, "Ada", "\x00" * 3), (0, "Row 2, column 1.", "\x00" * 16)],
    )

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (
        ["Role column header", "Engineer", "link", "Row 2, column 2."],
        [(1, "Ada", "\x00" * 3), (1, "Engineer", "\xc0" * 8), (0, "Row 2, column 2.", "\x00" * 16)],
    )

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (
        ["Office column header", "London", "link", "Row 2, column 3."],
        [
            (1, "Engineer", "\xc0" * 8),
            (1, "London", "\xc0" * 6),
            (0, "Row 2, column 3.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_LEFT)
    assert _capture(session) == (
        ["Role column header", "Engineer", "link", "Row 2, column 2."],
        [
            (1, "London", "\xc0" * 6),
            (1, "Engineer", "\xc0" * 8),
            (0, "Row 2, column 2.", "\x00" * 16),
        ],
    )


@pytest.mark.native_app
def test_table_navigation_by_row(web_tables: NativeAppSession) -> None:
    """Tests cell-by-cell table navigation across rows."""

    session = web_tables
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    assert _capture(session) == (
        ["t", "table with 3 rows 3 columns", "Role", "Office"],
        [(1, "", None)],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Ada", "row header", "Row 2, column 1."],
        [(1, "Ada", "\x00" * 3), (0, "Row 2, column 1.", "\x00" * 16)],
    )

    _table_nav(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (
        ["Role column header", "Engineer", "link", "Row 2, column 2."],
        [(1, "Ada", "\x00" * 3), (1, "Engineer", "\xc0" * 8), (0, "Row 2, column 2.", "\x00" * 16)],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Grace row header Admiral", "Row 3, column 2."],
        [
            (1, "Engineer", "\xc0" * 8),
            (1, "Admiral", "\x00" * 7),
            (0, "Row 3, column 2.", "\x00" * 16),
        ],
    )

    _table_nav(keyboard.KEYSYM_UP)
    assert _capture(session) == (
        ["Ada row header", "Engineer", "link", "Row 2, column 2."],
        [
            (1, "Admiral", "\x00" * 7),
            (1, "Engineer", "\xc0" * 8),
            (0, "Row 2, column 2.", "\x00" * 16),
        ],
    )


@pytest.mark.native_app
def test_table_navigation_across_spanned_cells(web_tables: NativeAppSession) -> None:
    """Tests table navigation onto cells that span rows and/or columns."""

    session = web_tables
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    _capture(session)
    keyboard.tap_key(keyboard.KEYSYM_T)
    assert _capture(session) == (
        ["t", "leaving table.", "table with 6 rows 3 columns", "P", "column header"],
        [(1, "P", "\x00")],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Block", "Row 2, column 1.", "Cell spans 2 rows 2 columns"],
        [
            (1, "Block", "\x00" * 5),
            (0, "Row 2, column 1.", "\x00" * 16),
            (0, "Cell spans 2 rows 2 columns", "\x00" * 27),
        ],
    )

    _table_nav(keyboard.KEYSYM_DOWN)
    _capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (
        ["Q column header Wide", "Row 4, column 2.", "Cell spans 2 columns"],
        [
            (1, "Three", "\x00" * 5),
            (1, "Wide", "\x00" * 4),
            (0, "Row 4, column 2.", "\x00" * 16),
            (0, "Cell spans 2 columns", "\x00" * 20),
        ],
    )

    _table_nav(keyboard.KEYSYM_LEFT)
    _capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Tall", "Row 5, column 1.", "Cell spans 2 rows"],
        [
            (1, "Three", "\x00" * 5),
            (1, "Tall", "\x00" * 4),
            (0, "Row 5, column 1.", "\x00" * 16),
            (0, "Cell spans 2 rows", "\x00" * 17),
        ],
    )


@pytest.mark.native_app
def test_caret_navigation_in_a_table(web_tables: NativeAppSession) -> None:
    """Tests caret navigation into, through, and out of a table."""

    session = web_tables
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Before the tables."],
        [(1, "Before the tables.", "\x00" * 18)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        [
            "table with 3 rows 3 columns",
            "Role",
            "column header",
            "Office",
            "column header",
            "column 3",
        ],
        [(1, "Role Office", "\x00" * 11)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Ada", "Engineer", "London", "link"],
        [(1, "Ada Engineer London", "\x00" * 4 + "\xc0" * 8 + "\x00" + "\xc0" * 6)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Grace", "Role column header Admiral", "Boston", "link"],
        [(1, "Grace Admiral Boston", "\x00" * 14 + "\xc0" * 6)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
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
        [(1, "P Q R", "\x00" * 5)],
    )


@pytest.mark.native_app
def test_table_cell_where_am_i(web_tables: NativeAppSession) -> None:
    """Tests basic Where Am I in a table cell."""

    session = web_tables
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    _capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    _capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    _capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    _capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert _capture(session) == (
        ["Grace Role Admiral", "column 2 of 3 row 3 of 3"],
        [(1, "Admiral", "\x00" * 7), (1, "Admiral", "\x00" * 7)],
    )


@pytest.mark.native_app
def test_table_cell_detailed_where_am_i(web_tables: NativeAppSession) -> None:
    """Tests detailed Where Am I in a table cell."""

    session = web_tables
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    _capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    _capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    _capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    _capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert _capture(session) == (
        [
            "Grace",
            "Admiral",
            "Boston",
            "1 of 2",
            "column 2 of 3 row 3 of 3",
        ],
        [
            (1, "Admiral", "\x00" * 7),
            (1, "Admiral", "\x00" * 7),
            (1, "Admiral", "\x00" * 7),
        ],
    )


@pytest.mark.native_app
def test_row_header_where_am_i(web_tables: NativeAppSession) -> None:
    """Tests basic Where Am I on a row header."""

    session = web_tables
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    _capture(session)
    _table_nav(keyboard.KEYSYM_DOWN)
    _capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert _capture(session) == (
        ["Ada", "row header"],
        [(1, "Ada", "\x00" * 3), (1, "Ada", "\x00" * 3)],
    )


@pytest.mark.native_app
def test_column_header_where_am_i(web_tables: NativeAppSession) -> None:
    """Tests basic Where Am I on a column header."""

    session = web_tables
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_T)
    _capture(session)
    _table_nav(keyboard.KEYSYM_RIGHT)
    _capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert _capture(session) == (
        ["Role", "column header"],
        [(1, "Role", "\x00" * 4), (1, "Role", "\x00" * 4)],
    )


@pytest.mark.native_app
def test_heading_where_am_i(web_tables: NativeAppSession) -> None:
    """Tests basic Where Am I on a heading."""

    session = web_tables
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    _capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert _capture(session) == (
        ["Tables", "heading 1"],
        [(1, "Tables h1", "\x00" * 9)],
    )
