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

"""Tests editing (insertion, deletion, selection) in web text fields."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _set_echo(
    session: NativeAppSession, *, key: bool, word: bool, sentence: bool, character: bool
) -> None:
    session.orca.set("TypingEchoPresenter", "KeyEchoEnabled", key)
    session.orca.set("TypingEchoPresenter", "WordEchoEnabled", word)
    session.orca.set("TypingEchoPresenter", "SentenceEchoEnabled", sentence)
    session.orca.set("TypingEchoPresenter", "CharacterEchoEnabled", character)


def _type(text: str) -> None:
    for ch in text:
        if ch == " ":
            keyboard.tap_key(keyboard.KEYSYM_SPACE)
        elif ch == "\n":
            keyboard.tap_key(keyboard.KEYSYM_RETURN)
        elif ch.isupper():
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], ord(ch.lower()))
        else:
            keyboard.tap_key(ord(ch))


def _quiet(session: NativeAppSession) -> None:
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _focus_field(session: NativeAppSession, tab_count: int) -> None:
    """Resets state, tabs into a field, clears it, and quiets the output."""

    helpers.reset_web_state(session)
    for _ in range(tab_count):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
    _quiet(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    _quiet(session)


@pytest.mark.native_app
def test_key_echo_insertion_in_textarea(web_editing: NativeAppSession) -> None:
    """Tests that key echo speaks each character inserted into a textarea."""

    session = web_editing
    _focus_field(session, tab_count=1)
    _set_echo(session, key=True, word=False, sentence=False, character=False)

    _type("a")
    assert helpers.speech(session) == ["a"]
    _type("b")
    assert helpers.speech(session) == ["b"]
    _type("c")
    assert helpers.speech(session) == ["c"]


@pytest.mark.native_app
def test_word_echo_insertion_in_textarea(web_editing: NativeAppSession) -> None:
    """Tests that word echo speaks each word as a space completes it in a textarea."""

    session = web_editing
    _focus_field(session, tab_count=1)
    _set_echo(session, key=False, word=True, sentence=False, character=False)

    _type("cat ")
    assert helpers.speech(session) == ["cat "]
    _type("dog ")
    assert helpers.speech(session) == ["dog "]


@pytest.mark.native_app
def test_backspace_and_delete_in_textarea(web_editing: NativeAppSession) -> None:
    """Tests that Backspace and Delete in a textarea announce the affected character."""

    session = web_editing
    _focus_field(session, tab_count=1)
    _set_echo(session, key=True, word=False, sentence=False, character=False)

    _type("abc")
    _quiet(session)

    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.speech(session) == ["c"]
    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.speech(session) == ["b"]

    # Re-type and move Left so Delete has a character ahead of the caret to remove.
    _type("z")
    _quiet(session)
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.speech(session) == ["z"]
    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    assert helpers.speech(session) == [""]


@pytest.mark.native_app
def test_selection_change_in_textarea(web_editing: NativeAppSession) -> None:
    """Tests that selecting and unselecting characters in a textarea is announced."""

    session = web_editing
    _focus_field(session, tab_count=1)
    _set_echo(session, key=False, word=False, sentence=False, character=False)

    _type("cat dog ")
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    _quiet(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    assert helpers.speech(session) == ["c", "selected"]
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    assert helpers.speech(session) == ["a", "selected"]
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    assert helpers.speech(session) == ["t", "selected"]
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_LEFT)
    assert helpers.speech(session) == ["t", "unselected"]


@pytest.mark.native_app
def test_line_navigation_in_textarea(web_editing: NativeAppSession) -> None:
    """Tests that Up/Down arrow line navigation in a textarea speaks each line."""

    session = web_editing
    _focus_field(session, tab_count=1)
    _set_echo(session, key=False, word=False, sentence=False, character=False)

    _type("first line\nsecond line\nthird line")
    _quiet(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    _quiet(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["second line\n"]
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["third line"]
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.speech(session) == ["second line\n"]


@pytest.mark.native_app
def test_key_echo_insertion_in_contenteditable(web_editing: NativeAppSession) -> None:
    """Tests that key echo speaks characters inserted into a contenteditable div."""

    session = web_editing
    _focus_field(session, tab_count=2)
    _set_echo(session, key=True, word=False, sentence=False, character=False)

    _type("x")
    assert helpers.speech(session) == ["x"]
    _type("y")
    assert helpers.speech(session) == ["y"]
    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.speech(session) == ["y"]
