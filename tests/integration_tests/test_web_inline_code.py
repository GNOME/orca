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

"""Tests independent inline code announcements during navigation and Say All."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


_LINES = [
    (["Before snippets."], "Before snippets.", "\x00" * 16),
    (
        [
            "Use ",
            "code",
            "git",
            " or ",
            "code",
            "difflib",
            " today.",
        ],
        "Use git or difflib today.",
        "\x00" * 25,
    ),
    (
        ["Run ", "code", "alpha ", "beta", "code end", " now."],
        "Run alpha beta now.",
        "\x00" * 19,
    ),
    (
        ["Read ", "code", "linked", "link", " next."],
        "Read linked next.",
        "\x00" * 5 + "\xc0" * 6 + "\x00" * 6,
    ),
    (
        ["Try ", "code", "one ", "two", "link", " three", "code end", " next."],
        "Try one two three next.",
        "\x00" * 8 + "\xc0" * 3 + "\x00" * 12,
    ),
    (["Use ", "code", "role code", "code end", " here."], "Use role code here.", "\x00" * 19),
    (["Plain text here."], "Plain text here.", "\x00" * 16),
    (
        ["Nested ", "code", "inner", " tail", "code end", " ends."],
        "Nested inner tail ends.",
        "\x00" * 23,
    ),
    (["code", "block sample"], "block sample $l", "\x00" * 15),
    (["After snippets."], "After snippets.", "\x00" * 15),
]


def _set_announcements(session: BrowserSession, inline: bool, blocks: bool, *, say_all=False):
    helpers.reset_web_state(session)
    presenter = "SayAllPresenter" if say_all else "SpeechPresenter"
    other = "SpeechPresenter" if say_all else "SayAllPresenter"
    session.orca.set(presenter, "AnnounceInlineCode", inline)
    session.orca.set(other, "AnnounceInlineCode", not inline)
    session.orca.set(presenter, "AnnounceCodeBlock", blocks)
    session.orca.set(other, "AnnounceCodeBlock", not blocks)


def _speech(
    utterances: list[str], inline: bool, blocks: bool, *, code_block: bool = False
) -> list[str]:
    return [
        item
        for item in utterances
        if ((blocks if code_block else inline) or item not in ("code", "code end"))
        and (blocks or item != "leaving code.")
    ]


def _say_all_speech(inline: bool, blocks: bool) -> list[str]:
    result = [
        item
        for index, (spoken, _, _) in enumerate(_LINES[:-1])
        for item in _speech(spoken, inline, blocks, code_block=index == 8)
    ]
    result.extend(_speech(["leaving code.", "After snippets."], inline, blocks))
    return result


@pytest.mark.native_app
@pytest.mark.parametrize("inline", [False, True])
@pytest.mark.parametrize("blocks", [False, True])
def test_inline_code_line_navigation(web_inline_code: BrowserSession, inline: bool, blocks: bool):
    """Inline settings preserve block announcements and braille in both directions."""

    session = web_inline_code
    _set_announcements(session, inline, blocks)
    for key, indices in (
        (keyboard.KEYSYM_DOWN, range(1, len(_LINES))),
        (keyboard.KEYSYM_UP, range(len(_LINES) - 2, -1, -1)),
    ):
        for index in indices:
            spoken, text, mask = _LINES[index]
            if (key == keyboard.KEYSYM_DOWN and index == 9) or (
                key == keyboard.KEYSYM_UP and index == 7
            ):
                spoken = ["leaving code.", *spoken]
            keyboard.tap_key(key)
            assert helpers.capture(session) == (
                _speech(spoken, inline, blocks, code_block=index == 8),
                [BrailleLine(1, text, text, mask)],
            )


@pytest.mark.native_app
@pytest.mark.parametrize("inline", [False, True])
@pytest.mark.parametrize("blocks", [False, True])
@pytest.mark.parametrize("style", ["line", "sentence"])
def test_inline_code_say_all(
    web_inline_code: BrowserSession, inline: bool, blocks: bool, style: str
):
    """Both Say All styles use their independent inline and block settings."""

    session = web_inline_code
    _set_announcements(session, inline, blocks, say_all=True)
    session.orca.set("SayAllPresenter", "Style", style)
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert helpers.speech(session) == _say_all_speech(inline, blocks)


@pytest.mark.native_app
@pytest.mark.parametrize("inline", [False, True])
@pytest.mark.parametrize(
    "line, text",
    [(1, "Use git or difflib today."), (5, "Use role code here.")],
)
def test_inline_code_character_navigation(
    web_inline_code: BrowserSession, inline: bool, line: int, text: str
):
    """Character navigation speaks just the character, as with other inline markup."""

    session = web_inline_code
    _set_announcements(session, inline, True)
    for _ in range(line):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(session)
    for key, offsets in (
        (keyboard.KEYSYM_RIGHT, range(1, len(text))),
        (keyboard.KEYSYM_LEFT, range(len(text) - 2, -1, -1)),
    ):
        for offset in offsets:
            keyboard.tap_key(key)
            assert helpers.speech(session) == [text[offset]]


@pytest.mark.native_app
@pytest.mark.parametrize("inline", [False, True])
def test_inline_code_word_navigation(web_inline_code: BrowserSession, inline: bool):
    """Forward and backward word navigation presents inline code independently of blocks."""

    session = web_inline_code
    _set_announcements(session, inline, False)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    helpers.capture(session)
    words = [
        ["Use "],
        ["code", "git"],
        ["or "],
        ["code", "difflib"],
        [helpers.expected_for_browser(session, "today", firefox="today.")],
    ]
    for key, expected_words in (
        (keyboard.KEYSYM_RIGHT, words),
        (keyboard.KEYSYM_LEFT, reversed(words)),
    ):
        for expected in expected_words:
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], key)
            assert helpers.speech(session) == _speech(expected, inline, False)


@pytest.mark.native_app
def test_inline_code_only_displayed_text(web_inline_code: BrowserSession):
    """Only-speak-displayed-text suppresses inline boundary announcements."""

    session = web_inline_code
    _set_announcements(session, True, True)
    session.orca.set("SpeechPresenter", "OnlySpeakDisplayedText", True)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert "".join(helpers.speech(session)) == "Use git or difflib today."
    for expected in ("s", "e", " ", "g", "i", "t"):
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        assert helpers.speech(session) == [expected]
