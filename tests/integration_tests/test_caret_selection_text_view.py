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

"""Tests text selection in a text view when Orca controls the caret."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .caret_selection_helpers import (
    END_OF_FILE,
    END_OF_LINE,
    NEXT_CHARACTER,
    NEXT_LINE,
    NEXT_WORD,
    PREVIOUS_CHARACTER,
    PREVIOUS_LINE,
    PREVIOUS_WORD,
    START_OF_FILE,
    START_OF_LINE,
    select,
    select_without_notifying,
)
from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, say_selection

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_ORCA_CONTROLS = "The screen reader is controlling the caret."
_APP_CONTROLS = "The application is controlling the caret."
_FIRST_LINE = "OrcaTextView application frame Line one. $l"
_FIRST_LINE_VISIBLE = "Line one. $l"
_LINE_TWO = "Line two has additional words to make it long enough that  $l"
_LINE_TWO_VISIBLE = "Line two has additional words to"
_WRAPPED = "the text view wraps it. $l"
_LAST_LINE = "Last line. $l"
_WHOLE_LINE_TWO = "Line two has additional words to make it long enough that "
_TO_THE_END_OF_LINE_TWO = " two has additional words to make it long enough that"
_REST_OF_THE_FILE = (
    "Line two has additional words to make it long enough that the text view wraps it.\n"
    "Line three.\n"
    "Line four also has extra words to push it past the wrap boundary in the view.\n"
    "Last line."
)


def _take_control(session: NativeAppSession) -> None:
    """Moves to the top of the text view and gives Orca the caret."""

    move_to_top(session)
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]


def _release_control(session: NativeAppSession) -> None:
    """Gives the caret back to the application."""

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]


def _move_into_line_two(session: NativeAppSession) -> None:
    """Puts the caret after the first word of the second line."""

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == [_WHOLE_LINE_TWO]
    assert brailled[-1] == BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Line"]
    assert brailled[-1] == BrailleLine(5, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61)


@pytest.mark.native_app
def test_selection_by_character(gtk3_text_view: NativeAppSession) -> None:
    """Tests selection by character."""

    session = gtk3_text_view
    _take_control(session)

    assert select(session, NEXT_CHARACTER) == (
        ["L", "selected"],
        BrailleLine(2, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" + "\x00" * 11),
    )

    assert select(session, NEXT_CHARACTER) == (
        ["i", "selected"],
        BrailleLine(3, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" * 2 + "\x00" * 10),
    )

    assert select(session, NEXT_CHARACTER) == (
        ["n", "selected"],
        BrailleLine(4, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" * 3 + "\x00" * 9),
    )
    assert say_selection(session) == ["Selected text is:  Lin"]

    assert select(session, PREVIOUS_CHARACTER) == (
        ["n", "unselected"],
        BrailleLine(3, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" * 2 + "\x00" * 10),
    )

    assert select(session, PREVIOUS_CHARACTER) == (
        ["i", "unselected"],
        BrailleLine(2, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" + "\x00" * 11),
    )
    assert say_selection(session) == ["Selected text is:  L"]

    assert select(session, PREVIOUS_CHARACTER) == (
        ["L", "unselected"],
        BrailleLine(1, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 43),
    )
    assert say_selection(session) == ["No selected text."]

    _release_control(session)


@pytest.mark.native_app
def test_selection_by_word(gtk3_text_view: NativeAppSession) -> None:
    """Tests selection by word."""

    session = gtk3_text_view
    _take_control(session)

    assert select(session, NEXT_WORD) == (
        ["Line", "selected"],
        BrailleLine(5, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" * 4 + "\x00" * 8),
    )

    assert select(session, NEXT_WORD) == (
        [" one.", "selected"],
        BrailleLine(10, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" * 9 + "\x00" * 3),
    )
    assert say_selection(session) == ["Selected text is:  Line one."]

    assert select(session, PREVIOUS_WORD) == (
        ["one.", "unselected"],
        BrailleLine(6, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" * 5 + "\x00" * 7),
    )
    assert say_selection(session) == ["Selected text is:  Line "]

    _release_control(session)


@pytest.mark.native_app
def test_selection_by_line(gtk3_text_view: NativeAppSession) -> None:
    """Tests selection by line."""

    session = gtk3_text_view
    _take_control(session)

    assert select(session, NEXT_LINE) == (
        ["Line one.\n", "selected"],
        BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61),
    )
    assert say_selection(session) == ["Selected text is:  Line one.\n"]

    assert select(session, NEXT_LINE) == (
        [_WHOLE_LINE_TWO, "selected"],
        BrailleLine(1, _WRAPPED, _WRAPPED, "\x00" * 26),
    )
    assert say_selection(session) == [f"Selected text is:  Line one.\n{_WHOLE_LINE_TWO}"]

    assert select(session, PREVIOUS_LINE) == (
        [_WHOLE_LINE_TWO, "unselected"],
        BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61),
    )
    assert say_selection(session) == ["Selected text is:  Line one.\n"]

    _release_control(session)


@pytest.mark.native_app
def test_selection_to_the_line_boundaries(gtk3_text_view: NativeAppSession) -> None:
    """Tests selection to the end and to the start of the line."""

    session = gtk3_text_view
    _take_control(session)
    _move_into_line_two(session)

    assert select(session, END_OF_LINE) == (
        [_TO_THE_END_OF_LINE_TWO, "selected"],
        BrailleLine(
            32,
            _LINE_TWO,
            "rds to make it long enough that ",
            "\x00" * 4 + "\xc0" * 53 + "\x00" * 4,
        ),
    )
    assert say_selection(session) == [f"Selected text is:  {_TO_THE_END_OF_LINE_TWO}"]

    assert select(session, START_OF_LINE) == (
        [_TO_THE_END_OF_LINE_TWO, "unselected", "Line", "selected"],
        BrailleLine(1, _LINE_TWO, " two has additional words to mak", "\xc0" * 4 + "\x00" * 57),
    )
    assert say_selection(session) == ["Selected text is:  Line"]

    _release_control(session)


@pytest.mark.native_app
def test_selection_to_the_file_boundaries(gtk3_text_view: NativeAppSession) -> None:
    """Tests selection to the end and to the start of the file."""

    session = gtk3_text_view
    _take_control(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == [_WHOLE_LINE_TWO]
    assert brailled[-1] == BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61)

    assert select(session, END_OF_FILE) == (
        [_REST_OF_THE_FILE, "selected"],
        BrailleLine(11, _LAST_LINE, _LAST_LINE, "\xc0" * 10 + "\x00" * 3),
    )
    assert say_selection(session) == [f"Selected text is:  {_REST_OF_THE_FILE}"]

    assert select(session, START_OF_FILE) == (
        [_REST_OF_THE_FILE, "unselected", "Line one.\n", "selected"],
        BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61),
    )
    assert say_selection(session) == ["Selected text is:  Line one.\n"]

    _release_control(session)


@pytest.mark.native_app
def test_selection_backward_from_the_caret(gtk3_text_view: NativeAppSession) -> None:
    """Tests selection backward from a caret with nothing selected."""

    session = gtk3_text_view
    _take_control(session)
    _move_into_line_two(session)

    assert select(session, PREVIOUS_CHARACTER) == (
        ["e", "selected"],
        BrailleLine(5, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 3 + "\xc0" + "\x00" * 57),
    )
    assert say_selection(session) == ["Selected text is:  e"]

    assert select(session, PREVIOUS_CHARACTER) == (
        ["n", "selected"],
        BrailleLine(5, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 2 + "\xc0" * 2 + "\x00" * 57),
    )
    assert say_selection(session) == ["Selected text is:  ne"]

    assert select(session, PREVIOUS_CHARACTER) == (
        ["i", "selected"],
        BrailleLine(5, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" + "\xc0" * 3 + "\x00" * 57),
    )
    assert say_selection(session) == ["Selected text is:  ine"]

    assert select(session, PREVIOUS_WORD) == (
        ["L", "selected"],
        BrailleLine(5, _LINE_TWO, _LINE_TWO_VISIBLE, "\xc0" * 4 + "\x00" * 57),
    )
    assert say_selection(session) == ["Selected text is:  Line"]

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = capture(session)
    assert spoken == ["Text unselected.", "L"]
    assert brailled[-1] == BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61)

    _release_control(session)


@pytest.mark.native_app
def test_selection_without_notifying_the_user(gtk3_text_view: NativeAppSession) -> None:
    """Tests selection which the caller asked Orca not to present."""

    session = gtk3_text_view
    _take_control(session)

    spoken, brailled = select_without_notifying(session, NEXT_WORD)
    assert spoken == []
    assert brailled[-1] == BrailleLine(
        5, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" * 4 + "\x00" * 8
    )
    assert say_selection(session) == ["Selected text is:  Line"]

    spoken, brailled = select_without_notifying(session, NEXT_WORD)
    assert spoken == []
    assert brailled[-1] == BrailleLine(
        10, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" * 9 + "\x00" * 3
    )
    assert say_selection(session) == ["Selected text is:  Line one."]

    spoken, brailled = select_without_notifying(session, NEXT_LINE)
    assert spoken == []
    assert brailled[-1] == BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61)
    assert say_selection(session) == ["Selected text is:  Line one.\n"]

    _release_control(session)


@pytest.mark.native_app
def test_selection_removed_by_caret_navigation(gtk3_text_view: NativeAppSession) -> None:
    """Tests removing a selection with the caret navigation commands."""

    session = gtk3_text_view
    _take_control(session)

    assert select(session, NEXT_WORD) == (
        ["Line", "selected"],
        BrailleLine(5, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 31 + "\xc0" * 4 + "\x00" * 8),
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Text unselected.", " "]
    assert brailled[-1] == BrailleLine(5, _FIRST_LINE, _FIRST_LINE_VISIBLE, "\x00" * 43)
    assert say_selection(session) == ["No selected text."]

    assert select(session, NEXT_LINE) == (
        [" one.\n", "selected"],
        BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Text unselected.", "the text view wraps it.\n"]
    assert brailled[-1] == BrailleLine(1, _WRAPPED, _WRAPPED, "\x00" * 26)
    assert say_selection(session) == ["No selected text."]

    _release_control(session)
