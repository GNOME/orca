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

"""Tests caret navigation in a text view when Orca controls the caret."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_ORCA_CONTROLS = "The screen reader is controlling the caret."
_APP_CONTROLS = "The application is controlling the caret."
_LINE_TWO = "Line two has additional words to make it long enough that  $l"
_LINE_TWO_VISIBLE = "Line two has additional words to"
_WRAPPED = "the text view wraps it. $l"
_LAST_LINE = "Last line. $l"
_FIRST_LINE = "OrcaTextView application frame Line one. $l"


@pytest.mark.native_app
def test_toggling_caret_control(gtk3_text_view: NativeAppSession) -> None:
    """Tests toggling caret control between Orca and the application."""

    session = gtk3_text_view
    move_to_top(session)

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session) == (
        [_ORCA_CONTROLS],
        [BrailleLine(0, _ORCA_CONTROLS, "The screen reader is controlling", "\x00" * 43)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Line two has additional words to make it long enough that "]
    assert brailled[-1] == BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61)

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session) == (
        [_APP_CONTROLS],
        [BrailleLine(0, _APP_CONTROLS, "The application is controlling t", "\x00" * 41)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["the text view wraps it.\n"]
    assert brailled[-1] == BrailleLine(1, _WRAPPED, _WRAPPED, "\x00" * 26)


@pytest.mark.native_app
def test_caret_navigation_by_character_word_and_line(gtk3_text_view: NativeAppSession) -> None:
    """Tests caret navigation by character, by word, and by line."""

    session = gtk3_text_view
    move_to_top(session)
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Line two has additional words to make it long enough that "]
    assert brailled[-1] == BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["the text view wraps it.\n"],
        [BrailleLine(1, _WRAPPED, _WRAPPED, "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Line three.\n"],
        [BrailleLine(1, "Line three. $l", "Line three. $l", "\x00" * 14)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["the text view wraps it.\n"],
        [BrailleLine(1, _WRAPPED, _WRAPPED, "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (["h"], [BrailleLine(2, _WRAPPED, _WRAPPED, "\x00" * 26)])

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (["the"], [BrailleLine(4, _WRAPPED, _WRAPPED, "\x00" * 26)])

    keyboard.tap_key(keyboard.KEYSYM_END)
    assert capture(session) == (["blank"], [BrailleLine(24, _WRAPPED, _WRAPPED, "\x00" * 26)])

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert capture(session) == (["t"], [BrailleLine(1, _WRAPPED, _WRAPPED, "\x00" * 26)])

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [" "],
        [BrailleLine(28, _LINE_TWO, "to make it long enough that  $l", "\x00" * 61)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["that"],
        [BrailleLine(24, _LINE_TWO, "to make it long enough that  $l", "\x00" * 61)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert capture(session) == (
        ["Line one.\n"],
        [BrailleLine(1, _FIRST_LINE, "Line one. $l", "\x00" * 43)],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_caret_navigation_at_the_start_and_end(gtk3_text_view: NativeAppSession) -> None:
    """Tests caret navigation at the start and end of the text."""

    session = gtk3_text_view
    move_to_top(session)
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["Last line."]
    assert brailled[-1] == BrailleLine(11, _LAST_LINE, _LAST_LINE, "\x00" * 13)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == ([], [])

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == ([], [])

    keyboard.tap_key(keyboard.KEYSYM_END)
    assert capture(session) == (["blank"], [BrailleLine(11, _LAST_LINE, _LAST_LINE, "\x00" * 13)])

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert capture(session) == (["L"], [BrailleLine(1, _LAST_LINE, _LAST_LINE, "\x00" * 13)])

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["boundary in the view.\n"],
        [BrailleLine(1, "boundary in the view. $l", "boundary in the view. $l", "\x00" * 24)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert capture(session) == (
        ["Line one.\n"],
        [BrailleLine(1, _FIRST_LINE, "Line one. $l", "\x00" * 43)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == ([], [])

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == ([], [])

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_selection_with_shift_plus_arrows(gtk3_text_view: NativeAppSession) -> None:
    """Tests selection with shift plus the arrow keys."""

    session = gtk3_text_view
    move_to_top(session)
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Line one.\n", "selected"]
    assert brailled[-1] == BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["L", "selected"],
        [BrailleLine(2, _LINE_TWO, _LINE_TWO_VISIBLE, "\xc0" + "\x00" * 60)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    assert capture(session) == (
        ["ine two has additional words to make it long enough that", "selected"],
        [BrailleLine(32, _LINE_TWO, "rds to make it long enough that ", "\xc0" * 57 + "\x00" * 4)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Text unselected.", "the text view wraps it.\n"]
    assert brailled[-1] == BrailleLine(1, _WRAPPED, _WRAPPED, "\x00" * 26)

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_say_all_and_where_am_i(gtk3_text_view: NativeAppSession) -> None:
    """Tests say all and where am I."""

    session = gtk3_text_view
    move_to_top(session)
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Line two has additional words to make it long enough that "]
    assert brailled[-1] == BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert capture(session) == (
        ["text", "Line two has additional words to make it long enough that "],
        [BrailleLine(1, _LINE_TWO, _LINE_TWO_VISIBLE, "\x00" * 61)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(session, quiescence=0.4, overall=10.0) == [
        "Line two has additional words to make it long enough that the text view wraps it.\n",
        "Line three.\n",
        "Line four also has extra words to push it past the wrap boundary in the view.\n",
        "Last line.",
    ]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["boundary in the view.\n"],
        [BrailleLine(1, "boundary in the view. $l", "boundary in the view. $l", "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Last line."],
        [BrailleLine(1, _LAST_LINE, _LAST_LINE, "\x00" * 13)],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_toggling_layout_mode(gtk3_text_view: NativeAppSession) -> None:
    """Tests toggling layout mode."""

    session = gtk3_text_view
    move_to_top(session)
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]
    assert session.orca.get("CaretNavigator", "LayoutMode") is True

    ((key, mods),) = session.orca.available_keybindings(1)
    with session.orca.bound_command("toggle_layout_mode", key, mods):
        session.orca.press_bound_key(key)
        spoken, brailled = capture(session)
        assert spoken == ["Object mode."]
        assert brailled[-1] == BrailleLine(0, "Object mode.", "Object mode.", "\x00" * 12)
        assert session.orca.get("CaretNavigator", "LayoutMode") is False

        session.orca.press_bound_key(key)
        spoken, brailled = capture(session)
        assert spoken == ["Layout mode."]
        assert brailled[-1] == BrailleLine(0, "Layout mode.", "Layout mode.", "\x00" * 12)
        assert session.orca.get("CaretNavigator", "LayoutMode") is True

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_typing_and_deleting(gtk3_text_view: NativeAppSession) -> None:
    """Tests typing and deleting text."""

    # This test adds a line to the buffer, so it must remain the last one in the file.
    session = gtk3_text_view
    move_to_top(session)
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["Last line."]
    assert brailled[-1] == BrailleLine(11, _LAST_LINE, _LAST_LINE, "\x00" * 13)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    spoken, brailled = capture(session)
    assert spoken == []
    assert brailled[-1] == BrailleLine(1, " $l", " $l", "\x00" * 3)

    keyboard.tap_key(ord("a"))
    spoken, brailled = capture(session)
    assert spoken == ["a"]
    assert brailled[-1] == BrailleLine(2, "a $l", "a $l", "\x00" * 4)

    keyboard.tap_key(ord("b"))
    spoken, brailled = capture(session)
    assert spoken == ["b"]
    assert brailled[-1] == BrailleLine(3, "ab $l", "ab $l", "\x00" * 5)

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (["b"], [BrailleLine(2, "ab $l", "ab $l", "\x00" * 5)])

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert capture(session) == (["a"], [BrailleLine(1, "ab $l", "ab $l", "\x00" * 5)])

    keyboard.tap_key(keyboard.KEYSYM_END)
    assert capture(session) == (["blank"], [BrailleLine(3, "ab $l", "ab $l", "\x00" * 5)])

    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert capture(session) == (["b"], [BrailleLine(2, "a $l", "a $l", "\x00" * 4)])

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (["a"], [BrailleLine(1, "a $l", "a $l", "\x00" * 4)])

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Last line.\n"],
        [BrailleLine(1, _LAST_LINE, _LAST_LINE, "\x00" * 13)],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]
