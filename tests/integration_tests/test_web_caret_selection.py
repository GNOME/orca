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

"""Tests text selection in web content when Orca controls the caret."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .caret_selection_helpers import (
    END_OF_LINE,
    NEXT_CHARACTER,
    NEXT_LINE,
    NEXT_WORD,
    PREVIOUS_CHARACTER,
    PREVIOUS_LINE,
    PREVIOUS_WORD,
    START_OF_LINE,
    select,
    select_without_notifying,
)
from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state, say_selection
from .orca_fixtures import chromium_is_at_least, chromium_major_version

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_HEADING = "Structural navigation h1"
_PARAGRAPH = "Intro paragraph."
_QUOTE = "Quoted text. block quote"

_SELECTION_SPANS_OBJECTS = pytest.mark.skipif(
    not chromium_is_at_least(153),
    reason=f"needs Chromium with Document.SetTextSelections; this is {chromium_major_version()}",
)
_SELECTION_IS_PER_OBJECT = pytest.mark.skipif(
    chromium_is_at_least(153),
    reason=f"needs Chromium without Document.SetTextSelections; this is {chromium_major_version()}",
)


# Chromium 152 emits inconsistent selection-change events.
_SPEECH_IS_STABLE = chromium_is_at_least(153)


def _assert_speech(spoken: list[str], expected: list[str]) -> None:
    """Checks the utterances, on the browsers which report a selection change consistently."""

    if _SPEECH_IS_STABLE:
        assert spoken == expected


@pytest.mark.native_app
def test_selection_by_character(web_structural_navigation: NativeAppSession) -> None:
    """Tests selection by character."""

    session = web_structural_navigation
    reset_web_state(session)

    spoken, brailled = select(session, NEXT_CHARACTER)
    _assert_speech(spoken, ["S", "selected"])
    assert brailled == BrailleLine(2, _HEADING, _HEADING, "\xc0" + "\x00" * 23)

    spoken, brailled = select(session, NEXT_CHARACTER)
    _assert_speech(spoken, ["t", "selected"])
    assert brailled == BrailleLine(3, _HEADING, _HEADING, "\xc0" * 2 + "\x00" * 22)

    spoken, brailled = select(session, NEXT_CHARACTER)
    _assert_speech(spoken, ["r", "selected"])
    assert brailled == BrailleLine(4, _HEADING, _HEADING, "\xc0" * 3 + "\x00" * 21)
    assert say_selection(session) == ["Selected text is:  Str"]

    spoken, brailled = select(session, PREVIOUS_CHARACTER)
    _assert_speech(spoken, ["r", "unselected"])
    assert brailled == BrailleLine(3, _HEADING, _HEADING, "\xc0" * 2 + "\x00" * 22)

    spoken, brailled = select(session, PREVIOUS_CHARACTER)
    _assert_speech(spoken, ["t", "unselected"])
    assert brailled == BrailleLine(2, _HEADING, _HEADING, "\xc0" + "\x00" * 23)
    assert say_selection(session) == ["Selected text is:  S"]


@pytest.mark.native_app
def test_selection_by_word(web_structural_navigation: NativeAppSession) -> None:
    """Tests selection by word."""

    session = web_structural_navigation
    reset_web_state(session)

    spoken, brailled = select(session, NEXT_WORD)
    _assert_speech(spoken, ["Structural", "selected"])
    assert brailled == BrailleLine(11, _HEADING, _HEADING, "\xc0" * 10 + "\x00" * 14)

    spoken, brailled = select(session, NEXT_WORD)
    _assert_speech(spoken, ["navigation", "selected"])
    assert brailled == BrailleLine(22, _HEADING, _HEADING, "\xc0" * 21 + "\x00" * 3)
    assert say_selection(session) == ["Selected text is:  Structural navigation"]

    spoken, brailled = select(session, PREVIOUS_WORD)
    _assert_speech(spoken, ["navigation", "unselected"])
    assert brailled == BrailleLine(12, _HEADING, _HEADING, "\xc0" * 11 + "\x00" * 13)
    assert say_selection(session) == ["Selected text is:  Structural "]


@pytest.mark.native_app
def test_selection_to_the_line_boundaries(web_structural_navigation: NativeAppSession) -> None:
    """Tests selection to the end and to the start of the line."""

    session = web_structural_navigation
    reset_web_state(session)

    spoken, brailled = select(session, NEXT_WORD)
    _assert_speech(spoken, ["Structural", "selected"])
    assert brailled == BrailleLine(11, _HEADING, _HEADING, "\xc0" * 10 + "\x00" * 14)

    spoken, brailled = select(session, END_OF_LINE)
    _assert_speech(spoken, ["navigation", "selected"])
    assert brailled == BrailleLine(22, _HEADING, _HEADING, "\xc0" * 21 + "\x00" * 3)
    assert say_selection(session) == ["Selected text is:  Structural navigation"]

    spoken, brailled = select(session, START_OF_LINE)
    _assert_speech(spoken, ["Structural navigation", "unselected"])
    assert brailled == BrailleLine(1, _HEADING, _HEADING, "\x00" * 24)
    assert say_selection(session) == ["No selected text."]


@pytest.mark.native_app
def test_selection_in_a_paragraph(web_structural_navigation: NativeAppSession) -> None:
    """Tests selection in a paragraph below the heading."""

    session = web_structural_navigation
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == [_PARAGRAPH]
    assert brailled[-1] == BrailleLine(1, _PARAGRAPH, _PARAGRAPH, "\x00" * 16)

    spoken, brailled = select(session, NEXT_CHARACTER)
    _assert_speech(spoken, ["I", "selected"])
    assert brailled == BrailleLine(2, _PARAGRAPH, _PARAGRAPH, "\xc0" + "\x00" * 15)

    spoken, brailled = select(session, NEXT_CHARACTER)
    _assert_speech(spoken, ["n", "selected"])
    assert brailled == BrailleLine(3, _PARAGRAPH, _PARAGRAPH, "\xc0" * 2 + "\x00" * 14)
    assert say_selection(session) == ["Selected text is:  In"]

    spoken, brailled = select(session, END_OF_LINE)
    _assert_speech(spoken, ["tro paragraph.", "selected"])
    assert brailled == BrailleLine(17, _PARAGRAPH, _PARAGRAPH, "\xc0" * 16)
    assert say_selection(session) == ["Selected text is:  Intro paragraph."]


@_SELECTION_SPANS_OBJECTS
@pytest.mark.native_app
def test_selection_across_objects(web_structural_navigation: NativeAppSession) -> None:
    """Tests selection which spans more than one text object."""

    session = web_structural_navigation
    reset_web_state(session)

    spoken, brailled = select(session, END_OF_LINE)
    _assert_speech(spoken, ["Structural navigation", "selected"])
    assert brailled == BrailleLine(22, _HEADING, _HEADING, "\xc0" * 21 + "\x00" * 3)

    spoken, brailled = select(session, NEXT_LINE)
    _assert_speech(spoken, [_PARAGRAPH, "selected"])
    assert brailled == BrailleLine(17, _PARAGRAPH, _PARAGRAPH, "\xc0" * 16)
    assert say_selection(session) == ["Selected text is:  Structural navigation Intro paragraph."]

    spoken, brailled = select(session, NEXT_LINE)
    _assert_speech(spoken, ["Quoted text.", "selected"])
    assert brailled == BrailleLine(13, _QUOTE, _QUOTE, "\xc0" * 12 + "\x00" * 12)
    assert say_selection(session) == [
        "Selected text is:  Structural navigation Intro paragraph. Quoted text."
    ]

    spoken, brailled = select(session, PREVIOUS_LINE)
    _assert_speech(spoken, ["Quoted text.", "unselected"])
    assert brailled == BrailleLine(1, _QUOTE, _QUOTE, "\x00" * 24)
    assert say_selection(session) == ["Selected text is:  Structural navigation Intro paragraph."]

    spoken, brailled = select(session, NEXT_WORD)
    _assert_speech(spoken, ["Quoted", "selected"])
    assert brailled == BrailleLine(7, _QUOTE, _QUOTE, "\xc0" * 6 + "\x00" * 18)
    assert say_selection(session) == [
        "Selected text is:  Structural navigation Intro paragraph. Quoted"
    ]


@_SELECTION_IS_PER_OBJECT
@pytest.mark.native_app
def test_selection_across_objects_one_object_at_a_time(
    web_structural_navigation: NativeAppSession,
) -> None:
    """Tests selection which spans more than one text object, set through AtspiText."""

    session = web_structural_navigation
    reset_web_state(session)

    _spoken, brailled = select(session, END_OF_LINE)
    assert brailled == BrailleLine(22, _HEADING, _HEADING, "\xc0" * 21 + "\x00" * 3)

    _spoken, brailled = select(session, NEXT_LINE)
    assert brailled == BrailleLine(17, _PARAGRAPH, _PARAGRAPH, "\xc0" * 16)
    assert say_selection(session) == ["Selected text is:  Intro paragraph."]

    _spoken, brailled = select(session, NEXT_CHARACTER)
    assert brailled == BrailleLine(2, _QUOTE, _QUOTE, "\xc0" + "\x00" * 23)
    assert say_selection(session) == ["Selected text is:  Q"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Text unselected.", "leaving blockquote.", "Save", "button"]
    assert brailled[-1] == BrailleLine(1, "Save button", "Save button", "\x00" * 11)
    assert say_selection(session) == ["No selected text."]


@pytest.mark.native_app
def test_selection_without_notifying_the_user(
    web_structural_navigation: NativeAppSession,
) -> None:
    """Tests selection which the caller asked Orca not to present."""

    session = web_structural_navigation
    reset_web_state(session)

    spoken, brailled = select_without_notifying(session, NEXT_WORD)
    assert spoken == []
    assert brailled[-1] == BrailleLine(11, _HEADING, _HEADING, "\xc0" * 10 + "\x00" * 14)
    assert say_selection(session) == ["Selected text is:  Structural"]

    spoken, brailled = select_without_notifying(session, NEXT_WORD)
    assert spoken == []
    assert brailled[-1] == BrailleLine(22, _HEADING, _HEADING, "\xc0" * 21 + "\x00" * 3)
    assert say_selection(session) == ["Selected text is:  Structural navigation"]


@pytest.mark.native_app
def test_selection_removed_by_caret_navigation(
    web_structural_navigation: NativeAppSession,
) -> None:
    """Tests removing a selection with the caret navigation commands."""

    session = web_structural_navigation
    reset_web_state(session)

    spoken, brailled = select(session, NEXT_WORD)
    _assert_speech(spoken, ["Structural", "selected"])
    assert brailled == BrailleLine(11, _HEADING, _HEADING, "\xc0" * 10 + "\x00" * 14)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Text unselected.", " "]
    assert brailled[-1] == BrailleLine(11, _HEADING, _HEADING, "\x00" * 24)
    assert say_selection(session) == ["No selected text."]

    spoken, brailled = select(session, NEXT_WORD)
    _assert_speech(spoken, ["navigation", "selected"])
    assert brailled == BrailleLine(22, _HEADING, _HEADING, "\x00" * 10 + "\xc0" * 11 + "\x00" * 3)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Text unselected.", _PARAGRAPH]
    assert brailled[-1] == BrailleLine(1, _PARAGRAPH, _PARAGRAPH, "\x00" * 16)
    assert say_selection(session) == ["No selected text."]

    reset_web_state(session)
    spoken, _brailled = select(session, NEXT_WORD)
    _assert_speech(spoken, ["Structural", "selected"])

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    spoken, _brailled = capture(session)
    assert spoken == ["Text unselected.", "navigation"]
    assert say_selection(session) == ["No selected text."]

    spoken, _brailled = select(session, PREVIOUS_WORD)
    _assert_speech(spoken, ["navigation", "selected"])

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
    spoken, _brailled = capture(session)
    assert spoken == ["Text unselected.", "Structural "]
    assert say_selection(session) == ["No selected text."]
