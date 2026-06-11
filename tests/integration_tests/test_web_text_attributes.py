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

"""Tests semantic inline markup and the opt-in formatting-change announcements during caret nav."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import (
    BrailleLine,
    capture,
    move_to_bottom,
    reset_web_state,
    speech,
    toggle_flat_review,
)

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _line_down(
    session: NativeAppSession,
) -> tuple[list[str], list[tuple[int, str, str | None]]]:
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    return capture(session)


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom(web_text_attributes: NativeAppSession) -> None:
    """Tests Down-arrow caret nav with layout mode on: inline markup groups onto its line."""

    session = web_text_attributes
    reset_web_state(session)
    session.orca.set("SpeechPresenter", "SpeakTextAttributeChanges", "off")

    for expected in (
        ["A ", "deletion start", "removed", "deletion end", " word."],
        ["An ", "insertion start", "added", "insertion end", " word."],
        ["A ", "marked", " word."],
        ["A ", "subscript", "lower", " word."],
        ["A ", "superscript", "higher", " word."],
        ["A ", "linked", "link", " word."],
        ["Normal  heavy  then  slanted  then  lined  then normal."],
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom_layout_off(web_text_attributes: NativeAppSession) -> None:
    """Tests Down-arrow caret nav with layout mode off: inline markup isolates per line."""

    session = web_text_attributes
    reset_web_state(session)
    session.orca.set("SpeechPresenter", "SpeakTextAttributeChanges", "off")
    session.orca.set("CaretNavigator", "LayoutMode", False)
    for expected in (
        ["A "],
        ["deletion start", "removed", "deletion end"],
        [" word."],
        ["An "],
        ["insertion start", "added", "insertion end"],
        [" word."],
        ["A "],
        ["marked"],
        [" word."],
        ["A "],
        ["subscript", "lower"],
        [" word."],
        ["A "],
        ["superscript", "higher"],
        [" word."],
        ["A "],
        ["linked", "link"],
        [" word."],
        ["Normal  heavy  then  slanted  then  lined  then normal."],
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top(web_text_attributes: NativeAppSession) -> None:
    """Tests Up-arrow caret nav with layout mode on: inline markup groups onto its line."""

    session = web_text_attributes
    reset_web_state(session)
    session.orca.set("SpeechPresenter", "SpeakTextAttributeChanges", "off")
    move_to_bottom(session)

    for expected in (
        ["A ", "linked", "link", " word."],
        ["A ", "superscript", "higher", " word."],
        ["A ", "subscript", "lower", " word."],
        ["A ", "marked", " word."],
        ["An ", "insertion start", "added", "insertion end", " word."],
        ["A ", "deletion start", "removed", "deletion end", " word."],
        ["Text attributes", "heading 1"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top_layout_off(web_text_attributes: NativeAppSession) -> None:
    """Tests Up-arrow caret nav with layout mode off: inline markup isolates per line."""

    session = web_text_attributes
    reset_web_state(session)
    session.orca.set("SpeechPresenter", "SpeakTextAttributeChanges", "off")
    session.orca.set("CaretNavigator", "LayoutMode", False)
    move_to_bottom(session)
    for expected in (
        [" word."],
        ["linked", "link"],
        ["A "],
        [" word."],
        ["superscript", "higher"],
        ["A "],
        [" word."],
        ["subscript", "lower"],
        ["A "],
        [" word."],
        ["marked"],
        ["A "],
        [" word."],
        ["insertion start", "added", "insertion end"],
        ["An "],
        [" word."],
        ["deletion start", "removed", "deletion end"],
        ["A "],
        ["Text attributes", "heading 1"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_inline_markup_presentation(web_text_attributes: NativeAppSession) -> None:
    """Tests deletion, insertion, highlight, subscript, superscript, and link markup."""

    session = web_text_attributes
    reset_web_state(session)
    session.orca.set("SpeechPresenter", "SpeakTextAttributeChanges", "off")

    assert _line_down(session) == (
        ["A ", "deletion start", "removed", "deletion end", " word."],
        [
            BrailleLine(
                1,
                "A removed content deletion word.",
                "A removed content deletion word.",
                "\x00" * 32,
            )
        ],
    )

    assert _line_down(session) == (
        ["An ", "insertion start", "added", "insertion end", " word."],
        [
            BrailleLine(
                1,
                "An added content insertion word.",
                "An added content insertion word.",
                "\x00" * 32,
            )
        ],
    )

    assert _line_down(session) == (
        ["A ", "marked", " word."],
        [BrailleLine(1, "A marked word.", "A marked word.", "\x00" * 14)],
    )

    assert _line_down(session) == (
        ["A ", "subscript", "lower", " word."],
        [BrailleLine(1, "A lower subscript word.", "A lower subscript word.", "\x00" * 23)],
    )

    assert _line_down(session) == (
        ["A ", "superscript", "higher", " word."],
        [BrailleLine(1, "A higher superscript word.", "A higher superscript word.", "\x00" * 26)],
    )

    assert _line_down(session) == (
        ["A ", "linked", "link", " word."],
        [BrailleLine(1, "A linked word.", "A linked word.", "\x00" * 2 + "\xc0" * 6 + "\x00" * 6)],
    )


@pytest.mark.native_app
def test_formatting_change_announcements(web_text_attributes: NativeAppSession) -> None:
    """Tests bold/italic/underline/highlight announced once the setting is enabled."""

    session = web_text_attributes
    reset_web_state(session)
    session.orca.set("SpeechPresenter", "SpeakTextAttributeChanges", "always")

    _line_down(session)  # deletion line
    _line_down(session)  # insertion line
    assert _line_down(session) == (
        ["A ", "background color: yellow", "marked", "background color: white", " word."],
        [BrailleLine(1, "A marked word.", "A marked word.", "\x00" * 14)],
    )

    _line_down(session)  # subscript line
    _line_down(session)  # superscript line
    _line_down(session)  # link line
    assert _line_down(session) == (
        [
            "Normal ",
            "bold",
            "heavy",
            "bold off",
            " then ",
            "italic",
            "slanted",
            "italic off",
            " then ",
            "underline",
            "lined",
            "underline off",
            " then normal.",
        ],
        [
            BrailleLine(
                1,
                "Normal heavy then slanted then lined then normal.",
                "Normal heavy then slanted then l",
                "\x00" * 49,
            )
        ],
    )


@pytest.mark.native_app
def test_flat_review_markup_lines(web_text_attributes: NativeAppSession) -> None:
    """Tests flat review reads each inline-markup line once (guards the doubling fix)."""

    session = web_text_attributes
    reset_web_state(session)
    session.orca.set("SpeechPresenter", "SpeakTextAttributeChanges", "off")
    toggle_flat_review(session)
    try:
        keyboard.tap_key(keyboard.KEYSYM_KP_UP)
        assert capture(session) == (
            ["Text attributes"],
            [BrailleLine(1, "Text attributes $l", "Text attributes $l", "\x00" * 18)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
        assert capture(session) == (
            ["A  removed  word."],
            [BrailleLine(1, "A  removed  word. $l", "A  removed  word. $l", "\x00" * 20)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
        assert capture(session) == (
            ["An  added  word."],
            [BrailleLine(1, "An  added  word. $l", "An  added  word. $l", "\x00" * 19)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
        assert capture(session) == (
            ["A  marked  word."],
            [BrailleLine(1, "A  marked  word. $l", "A  marked  word. $l", "\x00" * 19)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_HOME)
        assert capture(session) == (
            ["An  added  word."],
            [BrailleLine(1, "An  added  word. $l", "An  added  word. $l", "\x00" * 19)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_DOWN)
        assert capture(session) == (
            ["A"],
            [BrailleLine(1, "An  added  word. $l", "An  added  word. $l", "\x00" * 19)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_DOWN)
        assert capture(session) == (
            ["n"],
            [BrailleLine(2, "An  added  word. $l", "An  added  word. $l", "\x00" * 19)],
        )
    finally:
        toggle_flat_review(session)
