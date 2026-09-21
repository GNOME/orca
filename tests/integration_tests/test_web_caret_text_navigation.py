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
from .helpers import move_to_top, reset_web_state, speech

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
    """Tests character navigation treats controls as whole objects and speaks their roles."""

    session = web_structural_navigation
    reset_web_state(session)
    for _ in range(6):
        _word_right(session)
    assert _right(session) == ["Save", "button"]
    assert _right(session) == ["Agree", "check box not checked"]
    assert _left(session) == ["Save", "button"]
    assert _left(session) == ["."]


@pytest.mark.native_app
def test_character_navigation_onto_embedded_image(
    web_structural_navigation: NativeAppSession,
) -> None:
    """Tests that Right-arrow onto an embedded image speaks the image."""

    session = web_structural_navigation
    reset_web_state(session)
    for _ in range(24):
        _word_right(session)
    assert _right(session) == ["Red square", "image"]


@pytest.mark.native_app
def test_line_start_and_end(web_structural_navigation: NativeAppSession) -> None:
    """Tests Home and End moving the caret to the start and end of the current line."""

    session = web_structural_navigation
    reset_web_state(session)
    move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert speech(session) == ["I"]
    keyboard.tap_key(keyboard.KEYSYM_END)
    assert speech(session) == ["Intro paragraph."]


@pytest.mark.native_app
def test_file_start_and_end(web_structural_navigation: NativeAppSession) -> None:
    """Tests Ctrl+End and Ctrl+Home moving the caret to the end and start of the document."""

    session = web_structural_navigation
    reset_web_state(session)
    move_to_top(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    assert speech(session) == [
        (
            "targets substantial chunks of readable prose rather than short fragments or "
            "individual controls."
        ),
    ]
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert speech(session) == ["Structural navigation", "heading 1"]


@pytest.mark.native_app
@pytest.mark.parametrize(
    "skip, before, object_speech, after",
    [
        (0, "before", "Save all changes button", "after"),
        (3, "left", "Red square image", "right"),
        (6, "spaced", "Green square image", "apart"),
    ],
    ids=["multi-word-button", "image-between-paragraphs", "image-with-spaces"],
)
def test_word_navigation_through_whole_object(
    web_structural_navigation: NativeAppSession,
    skip: int,
    before: str,
    object_speech: str,
    after: str,
) -> None:
    """Tests each object is one word-navigation unit, with its role, in both directions."""

    session = web_structural_navigation
    reset_web_state(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_B)
        speech(session)
    assert " ".join(_word_left(session)).strip() == "before"
    for _ in range(skip):
        _word_right(session)

    assert " ".join(_word_right(session)).strip() == before
    assert " ".join(_word_right(session)).strip() == object_speech
    assert " ".join(_word_right(session)).strip() == after
    assert " ".join(_word_left(session)).strip() == after
    assert " ".join(_word_left(session)).strip() == object_speech
    assert " ".join(_word_left(session)).strip() == before


@pytest.mark.native_app
@pytest.mark.parametrize("navigation", ["structural", "character", "word"])
@pytest.mark.parametrize("only_displayed_text", [False, True])
@pytest.mark.parametrize(
    "button_number, name, role",
    [(2, "Save all changes", "button"), (3, "Next slide", "slide control")],
    ids=["native-role", "custom-role"],
)
def test_role_respects_displayed_text_preference(
    web_structural_navigation: NativeAppSession,
    navigation: str,
    only_displayed_text: bool,
    button_number: int,
    name: str,
    role: str,
) -> None:
    """Tests native and custom role names both respect the displayed-text-only preference."""

    session = web_structural_navigation
    reset_web_state(session)
    session.orca.set("SpeechPresenter", "OnlySpeakDisplayedText", only_displayed_text)

    for _ in range(button_number):
        keyboard.tap_key(keyboard.KEYSYM_B)
        spoken = speech(session)

    expected = ["b", name]
    if not only_displayed_text:
        expected.append(role)
    assert spoken == expected

    if navigation == "structural":
        return

    forward, backward = (_word_right, _word_left) if navigation == "word" else (_right, _left)
    backward(session)
    if navigation == "word":
        forward(session)
    expected_navigation = " ".join(expected[1:])
    assert " ".join(forward(session)).strip() == expected_navigation

    forward(session)
    if navigation == "word":
        backward(session)
    assert " ".join(backward(session)).strip() == expected_navigation


@pytest.mark.native_app
@pytest.mark.parametrize("by_word", [True, False], ids=["word", "line"])
def test_navigation_with_only_displayed_text(
    web_structural_navigation: NativeAppSession,
    by_word: bool,
) -> None:
    """Tests navigation uses the current displayed-text-only preference."""

    session = web_structural_navigation
    reset_web_state(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_B)
        speech(session)
    assert " ".join(_word_left(session)).strip() == "before"
    assert " ".join(_word_right(session)).strip() == "before"
    session.orca.set("SpeechPresenter", "OnlySpeakDisplayedText", True)

    if by_word:
        spoken = " ".join(_word_right(session)).strip()
    else:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken = " ".join(speech(session)).strip()
    assert spoken == "Save all changes"
