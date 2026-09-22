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

"""Tests navigation and selection within image maps and SVGs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state, say_selection, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _move_before_image(session: NativeAppSession, section: int) -> None:
    reset_web_state(session)
    for _ in range(section):
        keyboard.tap_key(keyboard.KEYSYM_H)
        speech(session)
    keyboard.tap_key(keyboard.KEYSYM_P)
    speech(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    speech(session)


@pytest.mark.native_app
def test_tab_navigation_reaches_image_descendants(web_image_descendants: NativeAppSession) -> None:
    """Tests Tab and Shift+Tab reach image-map links and SVG controls."""

    session = web_image_descendants
    reset_web_state(session)
    expected = [
        ("North link", BrailleLine(1, "North", "North", "\xc0" * 5)),
        ("South link", BrailleLine(1, "South", "South", "\xc0" * 5)),
        ("Open link", BrailleLine(1, "Open", "Open", "\xc0" * 4)),
        ("Close button", BrailleLine(1, "Close button", "Close button", "\x00" * 12)),
    ]
    for spoken, braille in expected:
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        actual_spoken, actual_braille = capture(session)
        assert " ".join(actual_spoken) == spoken
        assert actual_braille[-1] == braille
    for spoken, braille in reversed(expected[:-1]):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
        actual_spoken, actual_braille = capture(session)
        assert " ".join(actual_spoken) == spoken
        assert actual_braille[-1] == braille


@pytest.mark.native_app
@pytest.mark.parametrize("by_word", [False, True], ids=["character", "word"])
@pytest.mark.parametrize(
    "section, characters, words",
    [
        (1, ["North link", "South link"], ["North link", "South link"]),
        (2, [*"Open", "Close button"], ["Open", "Close button"]),
        (3, list("Quiet river"), ["Quiet", "river"]),
    ],
    ids=["image-map", "interactive-svg", "svg-text"],
)
def test_caret_navigation_through_image_descendants(
    web_image_descendants: NativeAppSession,
    by_word: bool,
    section: int,
    characters: list[str],
    words: list[str],
) -> None:
    """Tests caret navigation enters the children and exits on either side."""

    session = web_image_descendants
    _move_before_image(session, section)
    expected = words if by_word else characters
    modifiers = [keyboard.KEYSYM_CONTROL_L] if by_word else []
    for item in expected:
        keyboard.press_chord(modifiers, keyboard.KEYSYM_RIGHT)
        spoken = " ".join(speech(session))
        assert (spoken.strip() if by_word else spoken) == item

    keyboard.press_chord(modifiers, keyboard.KEYSYM_RIGHT)
    assert " ".join(speech(session)).strip() == ("After" if by_word else "A")
    if by_word:
        keyboard.press_chord(modifiers, keyboard.KEYSYM_LEFT)
        assert " ".join(speech(session)).strip() == "After"
    for item in reversed(expected):
        keyboard.press_chord(modifiers, keyboard.KEYSYM_LEFT)
        spoken = " ".join(speech(session))
        assert (spoken.strip() if by_word else spoken) == item
    keyboard.press_chord(modifiers, keyboard.KEYSYM_LEFT)
    assert speech(session) == ["."]


@pytest.mark.native_app
def test_native_selection_within_svg_text(web_image_descendants: NativeAppSession) -> None:
    """Tests SVG text can be selected, reported, and unselected by character."""

    session = web_image_descendants
    _move_before_image(session, 3)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Quiet river"]
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    speech(session)

    for count, character in enumerate("Quiet", 1):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        spoken, brailled = capture(session)
        assert spoken == [character, "selected"]
        assert brailled[-1] == BrailleLine(
            count + 1, "Quiet river", "Quiet river", "\xc0" * count + "\x00" * (11 - count)
        )
    assert say_selection(session) == ["Selected text is:  Quiet"]

    for remaining, character in zip(range(4, -1, -1), reversed("Quiet"), strict=True):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_LEFT)
        spoken, brailled = capture(session)
        assert spoken == [character, "unselected"]
        assert brailled[-1] == BrailleLine(
            remaining + 1,
            "Quiet river",
            "Quiet river",
            "\xc0" * remaining + "\x00" * (11 - remaining),
        )
    assert say_selection(session) == ["No selected text."]
