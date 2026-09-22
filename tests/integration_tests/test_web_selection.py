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

"""Tests presentation of selection changes in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state, say_selection, speech
from .version_helpers import chromium_version, requires_version
from .web_native_selection_helpers import (
    USES_DOCUMENT_SELECTION,
    native_selection,
    select_character,
    select_word,
)

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_selecting_and_unselecting_an_option(web_selection: NativeAppSession) -> None:
    """Tests selecting and unselecting an option."""

    session = web_selection
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Toppings", "multi-select List with 2 items", "Olives", "Focus mode"]
    assert brailled[0] == BrailleLine(1, "Olives", "Olives", "\x00" * 6)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["selected"]
    assert brailled[-1] == BrailleLine(0, "selected", "selected", "\x00" * 8)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["unselected"]
    assert brailled[-1] == BrailleLine(0, "unselected", "unselected", "\x00" * 10)


@pytest.mark.native_app
def test_selecting_a_tree_item(web_selection: NativeAppSession) -> None:
    """Tests selecting a tree item."""

    session = web_selection
    reset_web_state(session)

    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        capture(session)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["selected"]
    assert brailled[-1] == BrailleLine(0, "selected", "selected", "\x00" * 8)


@requires_version("Chromium", chromium_version(), 156)
@pytest.mark.skipif(
    not USES_DOCUMENT_SELECTION, reason="Button text selection requires document-selection ranges"
)
@pytest.mark.native_app
@pytest.mark.parametrize("spaced", [False, True], ids=["unspaced", "spaced"])
def test_character_selection_across_inline_button(
    web_selection: NativeAppSession,
    spaced: bool,
) -> None:
    """Tests selection and unselection across both boundaries of an inline button."""

    session = web_selection

    with native_selection(session):
        for _ in range(2 if spaced else 1):
            keyboard.tap_key(keyboard.KEYSYM_B)
            speech(session, wait_async=True)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
        speech(session)

        text = "start Next slide finish" if spaced else "startNext slidefinish"
        for character in text:
            assert select_character(session, keyboard.KEYSYM_RIGHT) == [character, "selected"]
        assert say_selection(session) == [f"Selected text is:  {text}"]
        for character in reversed(text):
            assert select_character(session, keyboard.KEYSYM_LEFT) == [character, "unselected"]
        assert say_selection(session) == ["No selected text."]


@requires_version("Chromium", chromium_version(), 156)
@pytest.mark.skipif(
    not USES_DOCUMENT_SELECTION, reason="Button text selection requires document-selection ranges"
)
@pytest.mark.native_app
@pytest.mark.parametrize("forward", [True, False], ids=["forward", "backward"])
@pytest.mark.parametrize("spaced", [False, True], ids=["unspaced", "spaced"])
def test_selection_containing_whole_inline_button(
    web_selection: NativeAppSession,
    forward: bool,
    spaced: bool,
) -> None:
    """Tests selection includes button text when both endpoints are outside the button."""

    session = web_selection

    with native_selection(session):
        for _ in range(2 if spaced else 1):
            keyboard.tap_key(keyboard.KEYSYM_B)
            speech(session, wait_async=True)
        start, end = (
            (keyboard.KEYSYM_HOME, keyboard.KEYSYM_END)
            if forward
            else (keyboard.KEYSYM_END, keyboard.KEYSYM_HOME)
        )
        keyboard.tap_key(start)
        speech(session)

        text = "start Next slide finish" if spaced else "startNext slidefinish"
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], end)
        assert speech(session) == [text, "selected"]
        assert say_selection(session) == [f"Selected text is:  {text}"]

        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], start)
        assert speech(session) == [text, "unselected"]
        assert say_selection(session) == ["No selected text."]


@requires_version("Chromium", chromium_version(), 156)
@pytest.mark.skipif(
    not USES_DOCUMENT_SELECTION, reason="Button text selection requires document-selection ranges"
)
@pytest.mark.native_app
@pytest.mark.parametrize("spaced", [False, True], ids=["unspaced", "spaced"])
def test_word_selection_across_inline_button(
    web_selection: NativeAppSession,
    spaced: bool,
) -> None:
    """Tests word selection across button text and the following parent text."""

    session = web_selection

    with native_selection(session):
        for _ in range(2 if spaced else 1):
            keyboard.tap_key(keyboard.KEYSYM_B)
            speech(session, wait_async=True)
        keyboard.tap_key(keyboard.KEYSYM_END)
        speech(session)

        words = ["finish", "slide", "Next"] if spaced else ["slidefinish", "Next"]
        for word in words:
            assert select_word(session, keyboard.KEYSYM_LEFT) == [word, "selected"]
