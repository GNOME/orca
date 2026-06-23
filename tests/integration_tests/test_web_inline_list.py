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

"""Tests layout-mode line assembly for an inline list versus a block list."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_bottom, move_to_top, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_inline_list_items_share_a_line(web_inline_list: NativeAppSession) -> None:
    """Tests that inline list items group onto one line while block items do not."""

    session = web_inline_list
    move_to_top(session)

    # Inline list items render on one visual row and are presented as a single line.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["List with 3 items", "one", "two", "three"]

    # A block list is the contrast: each item is its own line.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["leaving list.", "List with 2 items", "• alpha"]
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["• beta"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["leaving list.", "Tail paragraph."]


@pytest.mark.native_app
def test_character_navigation_left_to_right(web_inline_list: NativeAppSession) -> None:
    """Tests Right-arrow character navigation across inline list items and a block list."""

    session = web_inline_list
    reset_web_state(session)
    stream = "nline listonetwothree• alpha• betaTail paragraph."
    for char in stream:
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        assert speech(session) == [char]


@pytest.mark.native_app
def test_character_navigation_right_to_left(web_inline_list: NativeAppSession) -> None:
    """Tests Left-arrow character navigation back across inline list items and a block list."""

    session = web_inline_list
    reset_web_state(session)
    for _ in range(60):
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        speech(session)
    stream = "hpargarap liaTateb •ahpla •eerhtowtenotsil enilnI"
    for char in stream:
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        assert speech(session) == [char]


@pytest.mark.native_app
def test_end_of_file_then_caret_left(web_inline_list: NativeAppSession) -> None:
    """Tests Ctrl+End at the document end, then Left walking back through the last line."""

    session = web_inline_list
    reset_web_state(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    assert speech(session) == ["Tail paragraph."]

    for char in "paragraph."[::-1]:
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        assert speech(session) == [char]


@pytest.mark.native_app
def test_word_navigation_left_to_right(web_inline_list: NativeAppSession) -> None:
    """Tests Ctrl+Right word navigation across inline list items and a block list."""

    session = web_inline_list
    reset_web_state(session)

    expected = [
        ["Inline "],
        ["list"],
        ["one"],
        ["two"],
        ["three"],
        ["• "],
        ["alpha"],
        ["• "],
        ["beta"],
        ["Tail "],
        ["paragraph"],
    ]
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        result.append(speech(session))
    assert result == expected


@pytest.mark.native_app
def test_word_navigation_right_to_left(web_inline_list: NativeAppSession) -> None:
    """Tests Ctrl+Left word navigation back across inline list items and a block list."""

    session = web_inline_list
    reset_web_state(session)
    move_to_bottom(session)

    expected = [
        ["."],
        ["paragraph"],
        ["Tail "],
        ["beta"],
        ["• "],
        ["alpha"],
        ["• "],
        ["three"],
        ["two"],
        ["one"],
        ["list"],
        ["Inline "],
    ]
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
        result.append(speech(session))
    assert result == expected
