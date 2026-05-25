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

"""Integration tests for the echo modes (key/word/sentence/character) while typing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, speech

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


def _fresh_line(session: NativeAppSession) -> None:
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    _quiet(session)


@pytest.mark.native_app
def test_cycle_key_echo(gtk3_text_view: NativeAppSession) -> None:
    """Tests cycling the echo mode through its six states and back to the default."""

    session = gtk3_text_view
    _quiet(session)

    for message in [
        "Echo set to word.",
        "Echo set to sentence.",
        "Echo set to key and word.",
        "Echo set to word and sentence.",
        "Echo set to None.",
        "Echo set to key.",
    ]:
        session.orca.call("TypingEchoPresenter", "CycleKeyEcho", True)
        assert capture(session) == (
            [message],
            [BrailleLine(0, message, message, "\x00" * len(message))],
        )


@pytest.mark.native_app
def test_key_echo(gtk3_text_view: NativeAppSession) -> None:
    """Tests that key echo speaks each character as it is typed."""

    session = gtk3_text_view
    _set_echo(session, key=True, word=False, sentence=False, character=False)
    _quiet(session)

    _type("a")
    assert speech(session) == ["a"]
    _type("b")
    assert speech(session) == ["b"]


@pytest.mark.native_app
def test_word_echo(gtk3_text_view: NativeAppSession) -> None:
    """Tests that word echo speaks a word once it is completed by a space."""

    session = gtk3_text_view
    _set_echo(session, key=False, word=True, sentence=False, character=False)
    _fresh_line(session)

    _type("cat ")
    assert speech(session) == ["cat "]


@pytest.mark.native_app
def test_word_echo_completed_by_newline(gtk3_text_view: NativeAppSession) -> None:
    """Tests that word echo speaks a word when it is completed by a newline."""

    session = gtk3_text_view
    _set_echo(session, key=False, word=True, sentence=False, character=False)
    _fresh_line(session)

    _type("dog\n")
    assert speech(session) == ["dog\n"]


@pytest.mark.native_app
def test_sentence_echo(gtk3_text_view: NativeAppSession) -> None:
    """Tests that sentence echo speaks each completed sentence, not the whole line."""

    session = gtk3_text_view
    _set_echo(session, key=False, word=False, sentence=True, character=False)
    _fresh_line(session)

    _type("Hello world. ")
    assert speech(session) == ["Hello world. "]
    _type("The end. ")
    assert speech(session) == ["The end. "]


@pytest.mark.native_app
def test_sentence_echo_completed_by_newline(gtk3_text_view: NativeAppSession) -> None:
    """Tests that sentence echo speaks a sentence when it is completed by a newline."""

    session = gtk3_text_view
    _set_echo(session, key=False, word=False, sentence=True, character=False)
    _fresh_line(session)

    _type("Done.\n")
    assert speech(session) == ["Done.\n"]


@pytest.mark.native_app
def test_character_echo_with_key_echo_off(gtk3_text_view: NativeAppSession) -> None:
    """Tests that character echo speaks the inserted character with key echo off."""

    session = gtk3_text_view
    _set_echo(session, key=False, word=False, sentence=False, character=True)
    _quiet(session)

    _type("z")
    assert speech(session) == ["z"]


@pytest.mark.native_app
def test_character_echo_with_key_echo_on(gtk3_text_view: NativeAppSession) -> None:
    """Tests that key and character echo together speak the character once, not twice."""

    session = gtk3_text_view
    _set_echo(session, key=True, word=False, sentence=False, character=True)
    _quiet(session)

    _type("q")
    assert speech(session) == ["q"]
