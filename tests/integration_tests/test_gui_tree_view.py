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

"""GtkTreeView coverage."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _reset_to_first_cell(session: NativeAppSession) -> None:
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)


@pytest.mark.native_app
def test_table_navigation(gtk3_tree_view: NativeAppSession) -> None:
    """Tests row reading and per-cell reading with column headers in a GTK table."""

    session = gtk3_tree_view
    _reset_to_first_cell(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Grace", "Admiral", "Boston", "Done check box checked"],
        [
            BrailleLine(
                1,
                " Name column header Grace Admiral Boston <x> check boxDone",
                "Grace Admiral Boston <x> check b",
                "\x00" * 58,
            )
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Alan", "Analyst", "Manchester", "Done check box not checked"],
        [
            BrailleLine(
                1,
                " Name column header Alan Analyst Manchester < > check boxDone",
                "Alan Analyst Manchester < > chec",
                "\x00" * 61,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Role column header Analyst"],
        [BrailleLine(1, " Role column header Analyst", "Analyst", "\x00" * 27)],
    )
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Office column header Manchester"],
        [BrailleLine(1, " Office column header Manchester", "Manchester", "\x00" * 32)],
    )
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["Role column header Analyst"],
        [BrailleLine(1, " Role column header Analyst", "Analyst", "\x00" * 27)],
    )


@pytest.mark.native_app
def test_table_selection_where_am_i_and_endpoints(gtk3_tree_view: NativeAppSession) -> None:
    """Tests selection state, Where Am I, and first/last-row movement in a GTK table."""

    session = gtk3_tree_view
    _reset_to_first_cell(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Grace", "Admiral", "Boston", "Done check box checked"],
        [
            BrailleLine(
                1,
                " Name column header Grace Admiral Boston <x> check boxDone",
                "Grace Admiral Boston <x> check b",
                "\x00" * 58,
            )
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Ada", "Engineer", "London", "Done check box not checked"],
        [
            BrailleLine(
                1,
                " Name column header Ada Engineer London < > check boxDone",
                "Ada Engineer London < > check bo",
                "\x00" * 57,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert capture(session) == (
        ["Name Ada", "column 1 of 4 row 1 of 3"],
        [BrailleLine(1, " Name column header Ada", "Ada", "\x00" * 23)],
    )
    session.orca.call("WhereAmIPresenter", "WhereAmIDetailed", True)
    assert capture(session) == (
        [
            "table with 3 rows 4 columns",
            "Ada",
            "Engineer",
            "London",
            "Done check box not checked",
            "1 of 3",
            "column 1 of 4 row 1 of 3",
        ],
        [
            BrailleLine(
                1,
                " Name column header Ada Engineer London < > check boxDone",
                "Ada Engineer London < > check bo",
                "\x00" * 57,
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "Grace",
            "not selected Admiral",
            "not selected Boston",
            "not selected Done check box checked",
            "not selected",
        ],
        [
            BrailleLine(
                1,
                " Name column header Grace Admiral Boston <x> check boxDone",
                "Grace Admiral Boston <x> check b",
                "\x00" * 58,
            )
        ],
    )
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [
            "Alan",
            "not selected Analyst",
            "not selected Manchester",
            "not selected Done check box not checked",
            "not selected",
        ],
        [
            BrailleLine(
                1,
                " Name column header Alan Analyst Manchester < > check boxDone",
                "Alan Analyst Manchester < > chec",
                "\x00" * 61,
            )
        ],
    )
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_UP)
    assert capture(session) == (
        [
            "Grace",
            "not selected Admiral",
            "not selected Boston",
            "not selected Done check box checked",
            "not selected",
        ],
        [
            BrailleLine(
                1,
                " Name column header Grace Admiral Boston <x> check boxDone",
                "Grace Admiral Boston <x> check b",
                "\x00" * 58,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert capture(session) == (
        ["Ada", "Engineer", "London", "Done check box not checked"],
        [
            BrailleLine(
                1,
                " Name column header Ada Engineer London < > check boxDone",
                "Ada Engineer London < > check bo",
                "\x00" * 57,
            )
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_END)
    assert capture(session) == (
        ["Alan", "Analyst", "Manchester", "Done check box not checked"],
        [
            BrailleLine(
                1,
                " Name column header Alan Analyst Manchester < > check boxDone",
                "Alan Analyst Manchester < > chec",
                "\x00" * 61,
            )
        ],
    )


@pytest.mark.native_app
def test_toggle_cell(gtk3_tree_view: NativeAppSession) -> None:
    """Tests presenting a toggleable cell and toggling it with Space."""

    session = gtk3_tree_view
    _reset_to_first_cell(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Grace", "Admiral", "Boston", "Done check box checked"],
        [
            BrailleLine(
                1,
                " Name column header Grace Admiral Boston <x> check boxDone",
                "Grace Admiral Boston <x> check b",
                "\x00" * 58,
            )
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Role column header Admiral"],
        [BrailleLine(1, " Role column header Admiral", "Admiral", "\x00" * 27)],
    )
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Office column header Boston"],
        [BrailleLine(1, " Office column header Boston", "Boston", "\x00" * 28)],
    )
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Done check box checked"],
        [BrailleLine(1, " Done <x> check boxDone", "<x> check boxDone", "\x00" * 23)],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert capture(session) == (
        ["not checked"],
        [BrailleLine(1, " Done < > check boxDone", "< > check boxDone", "\x00" * 23)],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert capture(session) == (
        ["checked"],
        [BrailleLine(1, " Done <x> check boxDone", "<x> check boxDone", "\x00" * 23)],
    )


@pytest.mark.native_app
def test_toggle_table_cell_read_mode(gtk3_tree_view: NativeAppSession) -> None:
    """Tests that toggling table cell read mode in a table announces cell vs row."""

    session = gtk3_tree_view
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.call("SpeechPresenter", "ToggleTableCellReadingMode", True)
    assert capture(session) == (
        ["Speak cell"],
        [BrailleLine(0, "Speak cell", "Speak cell", "\x00" * 10)],
    )
    session.orca.call("SpeechPresenter", "ToggleTableCellReadingMode", True)
    assert capture(session) == (
        ["Speak row"],
        [BrailleLine(0, "Speak row", "Speak row", "\x00" * 9)],
    )


@pytest.mark.native_app
def test_word_wrap_ends_table_row_window_at_word_boundary(gtk3_tree_view: NativeAppSession) -> None:
    """Tests that braille word wrap ends a table row's visible window on a word boundary."""

    session = gtk3_tree_view
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.set("BraillePresenter", "WordWrapIsEnabled", True)
    try:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        # The window ends after the whole word "check" rather than cutting "box" to "b".
        assert capture(session) == (
            ["Grace", "Admiral", "Boston", "Done check box checked"],
            [
                BrailleLine(
                    1,
                    " Name column header Grace Admiral Boston <x> check boxDone",
                    "Grace Admiral Boston <x> check ",
                    "\x00" * 58,
                )
            ],
        )
    finally:
        session.orca.set("BraillePresenter", "WordWrapIsEnabled", False)
