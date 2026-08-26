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

"""Tests text selection in a terminal when Orca controls the caret."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .caret_selection_helpers import (
    END_OF_LINE,
    NEXT_CHARACTER,
    NEXT_LINE,
    NEXT_WORD,
    PREVIOUS_CHARACTER,
    PREVIOUS_LINE,
    select,
)
from .harness import keyboard
from .helpers import BrailleLine, capture, say_selection, speech
from .terminal_helpers import settle

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_ORCA_CONTROLS = "The screen reader is controlling the caret."
_APP_CONTROLS = "The application is controlling the caret."

# VTE reports the terminal cursor on the pager status line throughout these selections.
_STATUS_LINE = BrailleLine(8, "doc.txt", "doc.txt", "\x00" * 7)


def _move_to_the_second_line(session: NativeAppSession) -> None:
    """Puts the caret at the start of the second line of the document."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.1, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["line 02\n"],
        [BrailleLine(1, "line 02", "line 02", "\x00" * 7)],
    )


@pytest.mark.native_app
def test_selection_by_character(gtk3_terminal_pager: NativeAppSession) -> None:
    """Tests selection by character."""

    session = gtk3_terminal_pager
    settle(session)

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    _move_to_the_second_line(session)

    assert select(session, NEXT_CHARACTER) == (["l", "selected"], _STATUS_LINE)
    assert select(session, NEXT_CHARACTER) == (["i", "selected"], _STATUS_LINE)
    assert say_selection(session) == ["Selected text is:  li"]

    assert select(session, PREVIOUS_CHARACTER) == (["i", "unselected"], _STATUS_LINE)
    assert say_selection(session) == ["Selected text is:  l"]

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_selection_by_word_and_line(gtk3_terminal_pager: NativeAppSession) -> None:
    """Tests selection by word and by line."""

    session = gtk3_terminal_pager
    settle(session)

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    _move_to_the_second_line(session)

    assert select(session, NEXT_WORD) == (["line", "selected"], _STATUS_LINE)
    assert select(session, END_OF_LINE) == ([" 02", "selected"], _STATUS_LINE)
    assert say_selection(session) == ["Selected text is:  line 02"]

    assert select(session, NEXT_LINE) == (["\n", "selected"], _STATUS_LINE)
    assert say_selection(session) == ["Selected text is:  line 02\n"]

    assert select(session, PREVIOUS_LINE) == (["line 02\n", "unselected"], _STATUS_LINE)
    assert say_selection(session) == ["No selected text."]

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_selection_removed_by_caret_navigation(gtk3_terminal_pager: NativeAppSession) -> None:
    """Tests removing a selection with the caret navigation commands."""

    session = gtk3_terminal_pager
    settle(session)

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert speech(session) == ["line 01\n"]

    assert select(session, NEXT_WORD) == (["line", "selected"], _STATUS_LINE)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Text unselected.", "line 02\n"]
    assert say_selection(session) == ["No selected text."]

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]
