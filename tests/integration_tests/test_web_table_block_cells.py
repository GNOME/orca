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

"""Tests layout-mode line assembly for tables whose cells contain block-level content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_FTSE_ROW = "FTSE 100 10,908.41 +37.39"
_FTSE_MASK = "\xc0" * 8 + "\x00" * 17
_DAX_ROW = "DAX 24,235.31 -92.11"
_DAX_MASK = "\xc0" * 3 + "\x00" * 17
_HEADER_ROW = "Name Price Change"
_CLIPPED_HEADER_ROW = "TREND DIRECTION NAME PRICE CHANGE % CHG"
_NIKKEI_ROW = "Trending up arrow Nikkei 42,062.98 +112.50 0.27%"
_NIKKEI_MASK = "\x00" * 18 + "\xc0" * 6 + "\x00" * 24
_SENSEX_ROW = "Sensex 81,254.00 +64.20"
_RISING_ROW = "Rising +1.90"


def _drain_down(session: NativeAppSession, count: int) -> None:
    for _ in range(count):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(session)


@pytest.mark.native_app
def test_paragraph_wrapped_cells_are_read_as_a_full_row(
    web_table_block_cells: NativeAppSession,
) -> None:
    """Tests full-row reading when each cell wraps its content in a paragraph."""

    session = web_table_block_cells
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "table with 3 rows 3 columns",
            "Name column header",
            "Price column header",
            "column 2",
            "Change column header",
            "column 3",
        ],
        [BrailleLine(1, _HEADER_ROW, _HEADER_ROW, "\x00" * len(_HEADER_ROW))],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "Name column header",
            "FTSE 100",
            "link",
            "Price column header 10,908.41",
            "Change column header +37.39",
        ],
        [BrailleLine(1, _FTSE_ROW, _FTSE_ROW, _FTSE_MASK)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "Name column header",
            "DAX",
            "link",
            "Price column header 24,235.31",
            "Change column header -92.11",
        ],
        [BrailleLine(1, _DAX_ROW, _DAX_ROW, _DAX_MASK)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["leaving table.", "Ada"]


@pytest.mark.native_app
def test_upward_navigation_keeps_paragraph_wrapped_rows_intact(
    web_table_block_cells: NativeAppSession,
) -> None:
    """Tests full-row reading when arrowing up into paragraph-wrapped cells."""

    session = web_table_block_cells
    move_to_top(session)
    _drain_down(session, 4)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        [
            "table with 3 rows 3 columns",
            "Name column header",
            "DAX",
            "link",
            "Price column header 24,235.31",
            "Change column header -92.11",
        ],
        [BrailleLine(1, _DAX_ROW, _DAX_ROW, _DAX_MASK)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["FTSE 100", "link", "Price column header 10,908.41", "Change column header +37.39"],
        [BrailleLine(1, _FTSE_ROW, _FTSE_ROW, _FTSE_MASK)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        [
            "Name column header",
            "Price column header",
            "column 2",
            "Change column header",
            "column 3",
        ],
        [BrailleLine(1, _HEADER_ROW, _HEADER_ROW, "\x00" * len(_HEADER_ROW))],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["leaving table.", "Before the tables."]


@pytest.mark.native_app
def test_stacked_paragraphs_in_cells_are_not_combined(
    web_table_block_cells: NativeAppSession,
) -> None:
    """Tests that cells holding two paragraphs each yield one paragraph per line."""

    session = web_table_block_cells
    move_to_top(session)
    _drain_down(session, 3)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["leaving table.", "Ada"]

    for expected in ["Lovelace", "Engineer", "London", "Grace", "Hopper", "Admiral", "Boston"]:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == [expected]


@pytest.mark.native_app
def test_clipped_header_labels_join_the_visible_ones(
    web_table_block_cells: NativeAppSession,
) -> None:
    """Tests the row assembly of marketwatch.com's header, two of whose labels are clipped."""

    session = web_table_block_cells
    move_to_top(session)
    _drain_down(session, 19)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["table with 2 rows 5 columns", "TREND DIRECTION", "NAME", "PRICE", "CHANGE", "% CHG"],
        [
            BrailleLine(
                1,
                _CLIPPED_HEADER_ROW,
                _CLIPPED_HEADER_ROW[:32],
                "\x00" * len(_CLIPPED_HEADER_ROW),
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Trending up arrow", "Nikkei", "link", "42,062.98", "+112.50", "0.27%"],
        [BrailleLine(1, _NIKKEI_ROW, _NIKKEI_ROW[:32], _NIKKEI_MASK)],
    )


@pytest.mark.native_app
def test_line_breaks_in_cells_are_not_combined(web_table_block_cells: NativeAppSession) -> None:
    """Tests that a break inside a cell's paragraph, and inside the cell, splits the line."""

    session = web_table_block_cells
    move_to_top(session)
    _drain_down(session, 11)

    for expected in ["Alan", "Turing", "Analyst", "Wilmslow"]:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == [expected]

    for expected in ["Katherine", "Johnson", "Physicist", "Hampton"]:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == [expected]


@pytest.mark.native_app
def test_header_text_directly_in_the_cells(web_table_block_cells: NativeAppSession) -> None:
    """Tests a header row and its data row when the text is not wrapped in a block."""

    session = web_table_block_cells
    move_to_top(session)
    _drain_down(session, 21)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "leaving table.",
            "table with 2 rows 3 columns",
            "Name",
            "column header",
            "Price",
            "column header",
            "column 2",
            "Change",
            "column header",
            "column 3",
        ],
        [BrailleLine(1, _HEADER_ROW, _HEADER_ROW, "\x00" * len(_HEADER_ROW))],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "Name column header Sensex",
            "Price column header 81,254.00",
            "Change column header +64.20",
        ],
        [BrailleLine(1, _SENSEX_ROW, _SENSEX_ROW, "\x00" * len(_SENSEX_ROW))],
    )


@pytest.mark.native_app
def test_both_lines_of_a_header_with_a_line_break(web_table_block_cells: NativeAppSession) -> None:
    """Tests that each line of a header holding a break is presented, in both directions."""

    session = web_table_block_cells
    move_to_top(session)
    _drain_down(session, 23)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["leaving table.", "table with 2 rows 2 columns", "Trend", "column header"],
        [BrailleLine(1, "Trend", "Trend", "\x00" * 5)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Direction"],
        [BrailleLine(1, "Direction", "Direction", "\x00" * 9)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Delta", "column header"],
        [BrailleLine(1, "Delta", "Delta", "\x00" * 5)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Trend\nDirection column header Rising", "Delta column header +1.90"],
        [BrailleLine(1, _RISING_ROW, _RISING_ROW, "\x00" * len(_RISING_ROW))],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Delta", "column header"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Direction", "column header"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Trend"]


@pytest.mark.native_app
def test_header_text_wrapped_in_a_paragraph(web_table_block_cells: NativeAppSession) -> None:
    """Tests the counterpart of test_header_text_directly_in_the_cells."""

    session = web_table_block_cells
    move_to_top(session)
    _drain_down(session, 27)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "leaving table.",
            "table with 2 rows 3 columns",
            "Name column header",
            "Price column header",
            "column 2",
            "Change column header",
            "column 3",
        ],
        [BrailleLine(1, _HEADER_ROW, _HEADER_ROW, "\x00" * len(_HEADER_ROW))],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "Name column header Sensex",
            "Price column header 81,254.00",
            "Change column header +64.20",
        ],
        [BrailleLine(1, _SENSEX_ROW, _SENSEX_ROW, "\x00" * len(_SENSEX_ROW))],
    )


@pytest.mark.native_app
def test_both_lines_of_a_paragraph_wrapped_header(web_table_block_cells: NativeAppSession) -> None:
    """Tests the counterpart of test_both_lines_of_a_header_with_a_line_break."""

    session = web_table_block_cells
    move_to_top(session)
    _drain_down(session, 29)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["leaving table.", "table with 2 rows 2 columns", "Trend column header"],
        [BrailleLine(1, "Trend", "Trend", "\x00" * 5)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Direction column header"],
        [BrailleLine(1, "Direction", "Direction", "\x00" * 9)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Delta column header"],
        [BrailleLine(1, "Delta", "Delta", "\x00" * 5)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Trend Direction column header Rising", "Delta column header +1.90"],
        [BrailleLine(1, _RISING_ROW, _RISING_ROW, "\x00" * len(_RISING_ROW))],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Delta column header"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Direction column header"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Trend column header"]
