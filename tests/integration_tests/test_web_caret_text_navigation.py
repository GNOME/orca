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

"""Tests caret navigation by character and by word through web document text."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _right(session: NativeAppSession) -> list[str]:
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    return speech(session)


def _word_right(session: NativeAppSession) -> list[str]:
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    return speech(session)


def _left(session: NativeAppSession) -> list[str]:
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    return speech(session)


def _word_left(session: NativeAppSession) -> list[str]:
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
    return speech(session)


def _into_heading(session: NativeAppSession, count: int) -> None:
    for _ in range(count):
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_character_navigation(web_structural_navigation: NativeAppSession) -> None:
    """Tests Right-arrow announcing each character it moves onto across the first heading."""

    session = web_structural_navigation
    reset_web_state(session)

    # The caret starts before the heading, so Right announces the character to its
    # right; the leading "S" of "Structural navigation" is therefore not spoken.
    assert [_right(session) for _ in range(8)] == [
        ["t"],
        ["r"],
        ["u"],
        ["c"],
        ["t"],
        ["u"],
        ["r"],
        ["a"],
    ]


@pytest.mark.native_app
def test_word_navigation(web_structural_navigation: NativeAppSession) -> None:
    """Tests Control+Right announcing each word, crossing from the heading into paragraphs."""

    session = web_structural_navigation
    reset_web_state(session)

    assert [_word_right(session) for _ in range(6)] == [
        ["Structural "],
        ["navigation"],
        ["Intro "],
        ["paragraph"],
        ["Quoted "],
        ["text"],
    ]


@pytest.mark.native_app
def test_character_navigation_backward(web_structural_navigation: NativeAppSession) -> None:
    """Tests Left-arrow announcing each character, reaching the leading "S" forward skipped."""

    session = web_structural_navigation
    reset_web_state(session)
    _into_heading(session, 9)

    assert [_left(session) for _ in range(9)] == [
        ["a"],
        ["r"],
        ["u"],
        ["t"],
        ["c"],
        ["u"],
        ["r"],
        ["t"],
        ["S"],
    ]


@pytest.mark.native_app
def test_word_navigation_backward(web_structural_navigation: NativeAppSession) -> None:
    """Tests Control+Left announcing each word back across the paragraphs and heading."""

    session = web_structural_navigation
    reset_web_state(session)
    for _ in range(7):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    # Going back, Control+Left also stops on the sentence-ending periods.
    assert [_word_left(session) for _ in range(7)] == [
        ["."],
        ["text"],
        ["Quoted "],
        ["."],
        ["paragraph"],
        ["Intro "],
        ["navigation"],
    ]


@pytest.mark.native_app
def test_character_navigation_onto_embedded_button(
    web_structural_navigation: NativeAppSession,
) -> None:
    """Tests that Right-arrow onto an embedded button speaks the button."""

    session = web_structural_navigation
    reset_web_state(session)
    for _ in range(6):
        _word_right(session)
    assert _right(session) == ["Save"]


@pytest.mark.native_app
def test_character_navigation_onto_embedded_image(
    web_structural_navigation: NativeAppSession,
) -> None:
    """Tests that Right-arrow onto an embedded image speaks the image."""

    session = web_structural_navigation
    reset_web_state(session)
    for _ in range(24):
        _word_right(session)
    assert _right(session) == ["Red square"]
