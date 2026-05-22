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

"""Integration tests for navigating a GTK tree view presented as a table."""

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
    assert _capture(session) == (
        ["Grace", "Admiral", "Boston"],
        [(1, "Grace Admiral Boston", "\x00" * 20)],
    )
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Alan", "Analyst", "Manchester"],
        [(1, "Alan Analyst Manchester", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (
        ["Role column header Analyst"],
        [(1, "Analyst", "\x00" * 7)],
    )
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (
        ["Office column header Manchester"],
        [(1, "Manchester", "\x00" * 10)],
    )
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert _capture(session) == (
        ["Role column header Analyst"],
        [(1, "Analyst", "\x00" * 7)],
    )


@pytest.mark.native_app
def test_table_selection_where_am_i_and_endpoints(gtk3_tree_view: NativeAppSession) -> None:
    """Tests selection state, Where Am I, and first/last-row movement in a GTK table."""

    session = gtk3_tree_view
    _reset_to_first_cell(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Grace", "Admiral", "Boston", "selected"],
        [(1, "Grace Admiral Boston", "\x00" * 20)],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert _capture(session) == (
        ["Ada", "Engineer", "London", "selected"],
        [(1, "Ada Engineer London", "\x00" * 19)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert _capture(session) == (
        ["Name Ada", "column 1 of 3 row 1 of 3"],
        [(1, "Ada", "\x00" * 3)],
    )
    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert _capture(session) == (
        [
            "table with 3 rows 3 columns",
            "Ada",
            "Engineer",
            "London",
            "1 of 3",
            "column 1 of 3 row 1 of 3",
        ],
        [(1, "Ada Engineer London", "\x00" * 19)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Grace", "not selected Admiral", "not selected Boston", "not selected"],
        [(1, "Grace Admiral Boston", "\x00" * 20)],
    )
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Alan", "not selected Analyst", "not selected Manchester", "not selected"],
        [(1, "Alan Analyst Manchester", "\x00" * 23)],
    )
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_UP)
    assert _capture(session) == (
        ["Grace", "not selected Admiral", "not selected Boston", "not selected"],
        [(1, "Grace Admiral Boston", "\x00" * 20)],
    )

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert _capture(session) == (
        ["Ada", "Engineer", "London"],
        [(1, "Ada Engineer London", "\x00" * 19)],
    )
    keyboard.tap_key(keyboard.KEYSYM_END)
    assert _capture(session) == (
        ["Alan", "Analyst", "Manchester"],
        [(1, "Alan Analyst Manchester", "\x00" * 23)],
    )
