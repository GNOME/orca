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

"""Tests which web elements can and cannot hold a browse-mode caret context."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_bottom, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _down(session: NativeAppSession) -> tuple[list[str], list[BrailleLine]]:
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    return capture(session)


@pytest.mark.native_app
def test_caret_navigation_skips_empty_and_hidden_content(
    web_caret_context: NativeAppSession,
) -> None:
    """Tests that caret navigation presents real paragraphs and skips empty/hidden ones."""

    reset_web_state(web_caret_context)

    # The empty paragraph (rejected by _can_have_caret_context), the aria-hidden
    # paragraph and span (pruned by Chromium), and the unfocused focusable span
    # (also pruned until focused) all sit between paragraphs one and three.
    assert _down(web_caret_context) == (
        ["Paragraph one."],
        [BrailleLine(1, "Paragraph one.", "Paragraph one.", "\x00" * 14)],
    )
    assert _down(web_caret_context) == (
        ["Paragraph three."],
        [BrailleLine(1, "Paragraph three.", "Paragraph three.", "\x00" * 16)],
    )
    assert _down(web_caret_context) == (
        ["Paragraph four."],
        [BrailleLine(1, "Paragraph four.", "Paragraph four.", "\x00" * 15)],
    )
    # The off-screen label is skipped; the next line is the input it names.
    assert _down(web_caret_context) == (
        ["Off-screen label", "entry"],
        [BrailleLine(18, "Off-screen label  $l", "Off-screen label  $l", None)],
    )


@pytest.mark.native_app
def test_hidden_content_never_reaches_speech(web_caret_context: NativeAppSession) -> None:
    """Tests that the hidden paragraph and span are never spoken during caret navigation."""

    reset_web_state(web_caret_context)

    spoken: list[str] = []
    for _ in range(4):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        utterances, _braille = capture(web_caret_context)
        spoken.extend(utterances)

    # "Off-screen label" appears only as the input's name, not as hidden content.
    assert "Hidden paragraph." not in spoken
    assert "Hidden span." not in spoken
    assert spoken == [
        "Paragraph one.",
        "Paragraph three.",
        "Paragraph four.",
        "Off-screen label",
        "entry",
    ]


@pytest.mark.native_app
def test_offscreen_label_is_skipped_during_caret_navigation(
    web_caret_context: NativeAppSession,
) -> None:
    """Tests that an off-screen label naming a control is skipped during caret navigation."""

    reset_web_state(web_caret_context)

    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
    speech, braille = capture(web_caret_context)
    assert speech == ["Paragraph four."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    speech, braille = capture(web_caret_context)
    assert speech == ["Off-screen label", "entry"]
    assert braille == [BrailleLine(18, "Off-screen label  $l", "Off-screen label  $l", None)]


@pytest.mark.native_app
def test_say_all_skips_empty_and_hidden_content(web_caret_context: NativeAppSession) -> None:
    """Tests that Say All reads the real paragraphs and skips the empty and hidden content."""

    reset_web_state(web_caret_context)
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(web_caret_context) == [
        "Caret context",
        "Paragraph one.",
        "Paragraph three.",
        "Paragraph four.",
    ]


@pytest.mark.native_app
def test_character_navigation_left_to_right(web_caret_context: NativeAppSession) -> None:
    """Tests Right-arrow character navigation across paragraphs, skipping aria-hidden content."""

    session = web_caret_context
    reset_web_state(session)
    stream = "aret contextParagraph one.Paragraph three.Paragraph four."
    for char in stream:
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        assert speech(session) == [char]
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert speech(session) == ["blank"]


@pytest.mark.native_app
def test_character_navigation_right_to_left(web_caret_context: NativeAppSession) -> None:
    """Tests Left-arrow character navigation back across paragraphs from the end."""

    session = web_caret_context
    reset_web_state(session)
    for _ in range(70):
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        speech(session)
    stream = ".ruof hpargaraP.eerht hpargaraP.eno hpargaraPtxetnoc teraC"
    for char in stream:
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        assert speech(session) == [char]


@pytest.mark.native_app
def test_word_navigation_left_to_right(web_caret_context: NativeAppSession) -> None:
    """Tests Ctrl+Right word navigation across paragraphs, skipping aria-hidden content."""

    session = web_caret_context
    reset_web_state(session)

    expected = [
        ["Caret "],
        ["context"],
        ["Paragraph "],
        ["one"],
        ["Paragraph "],
        ["three"],
        ["Paragraph "],
        ["four"],
    ]
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        result.append(speech(session))
    assert result == expected


@pytest.mark.native_app
def test_word_navigation_right_to_left(web_caret_context: NativeAppSession) -> None:
    """Tests Ctrl+Left word navigation back across paragraphs from the end."""

    session = web_caret_context
    reset_web_state(session)
    move_to_bottom(session)

    expected = [
        ["."],
        ["four"],
        ["Paragraph "],
        ["."],
        ["three"],
        ["Paragraph "],
        ["."],
        ["one"],
        ["Paragraph "],
        ["context"],
        ["Caret "],
    ]
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
        result.append(speech(session))
    assert result == expected


# Keep this test last: focusing the span dirties caret context in a way reset_web_state
# does not fully clear, which would break a later top-of-document test.
@pytest.mark.native_app
def test_focusable_aria_hidden_span_is_exposed_on_focus(
    web_caret_context: NativeAppSession,
) -> None:
    """Tests that focusing the aria-hidden span makes Chromium expose it, so Orca presents it."""

    reset_web_state(web_caret_context)

    # A focusable element cannot be hidden: on Tab, Chromium drops the aria-hidden
    # and adds the span to the tree (children-changed:add), so it is announced even
    # though browse-mode caret navigation above never reaches it.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(web_caret_context) == (
        ["Focusable hidden span."],
        [BrailleLine(0, "Focusable hidden span.", "Focusable hidden span.", "\x00" * 22)],
    )
