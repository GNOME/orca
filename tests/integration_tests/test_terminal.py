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

"""Integration tests for terminal presentation: command output, typing, and pager navigation."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _type(text: str) -> None:
    for char in text:
        if char == " ":
            keyboard.tap_key(keyboard.KEYSYM_SPACE)
        elif char == "\n":
            keyboard.tap_key(keyboard.KEYSYM_RETURN)
        elif char.isupper():
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], ord(char.lower()))
        else:
            keyboard.tap_key(ord(char))


def _settle(session: NativeAppSession) -> None:
    """Waits for the spawned program to finish its initial paint, then resets the reader."""

    session.reader.drain(quiescence_timeout=0.5, overall_timeout=4.0)
    session.reader.reset()


@pytest.mark.native_app
def test_command_output_is_spoken(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that the output of a command is spoken when the command completes."""

    session = gtk3_terminal_shell
    _settle(session)

    _type("echo hi\n")
    assert helpers.speech(session) == ["hi\n$ "]
    _type("echo hello world\n")
    assert helpers.speech(session) == ["hello world\n$ "]


@pytest.mark.native_app
def test_multiline_command_output_is_spoken(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that multi-line command output is spoken."""

    if shutil.which("seq") is None:
        pytest.skip("seq is not available")

    session = gtk3_terminal_shell
    _settle(session)

    _type("seq 3\n")
    assert helpers.speech(session) == ["1\n2\n3\n$ "]


@pytest.mark.native_app
def test_typed_characters_are_echoed(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that key echo speaks each character as it is typed at the prompt."""

    session = gtk3_terminal_shell
    session.orca.set("TypingEchoPresenter", "KeyEchoEnabled", True)
    session.orca.set("TypingEchoPresenter", "WordEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "SentenceEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "CharacterEchoEnabled", False)
    _settle(session)

    _type("a")
    assert helpers.capture(session) == (
        ["a"],
        [
            helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3),
            helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3),
        ],
    )
    _type("b")
    assert helpers.capture(session) == (
        ["b"],
        [
            helpers.BrailleLine(5, "$ ab", "$ ab", "\x00" * 4),
            helpers.BrailleLine(5, "$ ab", "$ ab", "\x00" * 4),
        ],
    )


@pytest.mark.native_app
def test_backspace_and_delete_at_the_prompt(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests Backspace and Delete at the bash prompt with key echo on."""

    session = gtk3_terminal_shell
    session.orca.set("TypingEchoPresenter", "KeyEchoEnabled", True)
    session.orca.set("TypingEchoPresenter", "WordEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "SentenceEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "CharacterEchoEnabled", False)
    _settle(session)

    _type("abc")
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.capture(session) == (["c"], [helpers.BrailleLine(5, "$ ab", "$ ab", "\x00" * 4)])
    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.capture(session) == (["b"], [helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3)])

    # Re-type and Left so Delete has something forward to act on.
    _type("d")
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (["d"], [helpers.BrailleLine(4, "$ ad", "$ ad", "\x00" * 4)])

    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    assert helpers.capture(session) == (["\n"], [helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3)])


@pytest.mark.native_app
def test_key_echo_while_typing_in_vim(gtk3_terminal_vim: NativeAppSession) -> None:
    """Tests that key echo speaks each character typed in Vim, which redraws as you type."""

    session = gtk3_terminal_vim
    session.orca.set("TypingEchoPresenter", "KeyEchoEnabled", True)
    session.orca.set("TypingEchoPresenter", "WordEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "SentenceEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "CharacterEchoEnabled", False)
    session.reader.drain(quiescence_timeout=0.6, overall_timeout=6.0)
    session.reader.reset()

    keyboard.tap_key(ord("i"))  # enter insert mode
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    _type("a")
    assert helpers.speech(session) == ["a"]
    _type("b")
    assert helpers.speech(session) == ["b"]


@pytest.mark.native_app
def test_pager_navigation_speaks_each_page(gtk3_terminal_pager: NativeAppSession) -> None:
    """Tests that paging through Less forward and back speaks each newly shown page."""

    session = gtk3_terminal_pager
    _settle(session)

    # The first page-down leaves the initial filename-status paint behind; discard it
    # so the asserted pages start from a settled prompt-status state.
    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    assert helpers.capture(session) == (
        ["line 15\nline 16\nline 17\nline 18\nline 19\nline 20\n(END)"],
        [helpers.BrailleLine(6, "(END)", "(END)", "\x00" * 5)],
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    assert helpers.capture(session) == (
        ["07\nline 08\nline 09\nline 10\nline 11\nline 12\nline 13\n:"],
        [helpers.BrailleLine(2, ":", ":", "\x00")],
    )


def _review_top_line(session: NativeAppSession) -> tuple[list[str], list[helpers.BrailleLine]]:
    """Moves flat review to the top of the screen and returns the (speech, braille) for it."""

    session.orca.call("FlatReviewPresenter", "GoHome", True)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.call("FlatReviewPresenter", "PresentLine", True)
    return helpers.capture(session)


@pytest.mark.native_app
def test_flat_review_reflects_new_page(gtk3_terminal_pager: NativeAppSession) -> None:
    """Tests that reviewing the page's top line shows the new page after paging, not stale text."""

    session = gtk3_terminal_pager
    _settle(session)
    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)  # to the last page (lines 14-20)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()

    helpers.toggle_flat_review(session)
    assert _review_top_line(session) == (
        ["line 14\n"],
        [helpers.BrailleLine(1, "line 14 $l", "line 14 $l", "\x00" * 10)],
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()
    assert _review_top_line(session) == (
        ["line 07\n"],
        [helpers.BrailleLine(1, "line 07 $l", "line 07 $l", "\x00" * 10)],
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()
    assert _review_top_line(session) == (
        ["line 01\n"],
        [helpers.BrailleLine(1, "line 01 $l", "line 01 $l", "\x00" * 10)],
    )
    helpers.toggle_flat_review(session)
