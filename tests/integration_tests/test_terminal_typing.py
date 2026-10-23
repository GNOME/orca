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

"""Integration tests for typing and editing in terminals."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .terminal_helpers import settle, type_text

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _enable_key_echo(session: NativeAppSession) -> None:
    """Enables key echo while disabling the higher-level echo modes."""

    session.orca.set("TypingEchoPresenter", "KeyEchoEnabled", True)
    session.orca.set("TypingEchoPresenter", "WordEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "SentenceEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "CharacterEchoEnabled", False)


@pytest.mark.native_app
def test_typed_characters_are_echoed(terminal_shell: NativeAppSession) -> None:
    """Tests that key echo speaks each character as it is typed at the prompt."""

    session = terminal_shell
    _enable_key_echo(session)
    settle(session)

    type_text("a")
    assert helpers.capture(session) == (
        ["a"],
        [
            helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3),
            helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3),
        ],
    )
    type_text("b")
    assert helpers.capture(session) == (
        ["b"],
        [
            helpers.BrailleLine(5, "$ ab", "$ ab", "\x00" * 4),
            helpers.BrailleLine(5, "$ ab", "$ ab", "\x00" * 4),
        ],
    )


@pytest.mark.native_app
def test_backspace_and_delete_at_the_prompt(terminal_shell: NativeAppSession) -> None:
    """Tests Backspace and Delete at the bash prompt with key echo on."""

    session = terminal_shell
    _enable_key_echo(session)
    settle(session)

    type_text("abc")
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.capture(session) == (["c"], [helpers.BrailleLine(5, "$ ab", "$ ab", "\x00" * 4)])
    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.capture(session) == (["b"], [helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3)])

    # Re-type and Left so Delete has something forward to act on.
    type_text("d")
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (["d"], [helpers.BrailleLine(4, "$ ad", "$ ad", "\x00" * 4)])

    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    assert helpers.capture(session) == (["\n"], [helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3)])


@pytest.mark.native_app
def test_key_echo_while_typing_in_vim(terminal_vim: NativeAppSession) -> None:
    """Tests that key echo speaks each character typed in Vim, which redraws as you type."""

    session = terminal_vim
    _enable_key_echo(session)
    session.reader.drain(quiescence_timeout=0.6, overall_timeout=6.0)
    session.reader.reset()

    keyboard.tap_key(ord("i"))  # enter insert mode
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    type_text("a")
    assert helpers.speech(session) == ["a"]
    type_text("b")
    assert helpers.speech(session) == ["b"]


@pytest.mark.native_app
def test_ctrl_backspace_at_the_prompt(terminal_shell: NativeAppSession) -> None:
    """Tests that Ctrl+BackSpace at the bash prompt deletes a single character."""

    session = terminal_shell
    _enable_key_echo(session)
    settle(session)

    type_text("foo bar")
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_BACKSPACE)
    assert helpers.speech(session) == ["r"]


@pytest.mark.native_app
def test_caret_movement_at_the_prompt(terminal_shell: NativeAppSession) -> None:
    """Checks speech and braille cursor movement in both directions."""

    session = terminal_shell
    settle(session)
    type_text("ab")
    settle(session)
    for key, expected, cursor in (
        (keyboard.KEYSYM_LEFT, "b", 4),
        (keyboard.KEYSYM_RIGHT, "blank", 5),
    ):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        assert spoken == [expected]
        assert brailled[-1] == helpers.BrailleLine(cursor, "$ ab", "$ ab", "\x00" * 4)
