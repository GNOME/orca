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

"""Exercise Orca's announcements for caret navigation and selection in a TextView."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_caret_navigation_presentation(gtk3_text_view: NativeAppSession) -> None:
    """Orca's announcements as the caret moves via arrows, word/line jumps, buffer endpoints."""

    session = gtk3_text_view
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Line two has additional words to make it long enough that "],
        [
            BrailleLine(
                1,
                "Line two has additional words to make it long enough that  $l",
                "Line two has additional words to",
                "\x00" * 61,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["the text view wraps it.\n"],
        [BrailleLine(1, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Line three.\n"],
        [BrailleLine(1, "Line three. $l", "Line three. $l", "\x00" * 14)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["the text view wraps it.\n"],
        [BrailleLine(1, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["h"],
        [BrailleLine(2, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["the"],
        [BrailleLine(4, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_END)
    assert capture(session) == (
        ["blank"],
        [BrailleLine(24, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert capture(session) == (
        ["t"],
        [BrailleLine(1, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    assert capture(session) == (
        ["Last line."],
        [BrailleLine(11, "Last line. $l", "Last line. $l", "\x00" * 13)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert capture(session) == (
        ["Line one.\n"],
        [
            BrailleLine(
                1, "OrcaTextView application frame Line one. $l", "Line one. $l", "\x00" * 43
            )
        ],
    )


@pytest.mark.native_app
def test_caret_selection_presentation(gtk3_text_view: NativeAppSession) -> None:
    """Orca's announcements as selection changes by line, word, char, jumps, and select-all."""

    session = gtk3_text_view
    move_to_top(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Line one.\n", "selected"],
        [
            BrailleLine(
                1,
                "Line two has additional words to make it long enough that  $l",
                "Line two has additional words to",
                "\x00" * 61,
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Line two has additional words to make it long enough that ", "selected"],
        [BrailleLine(1, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["the text view wraps it.\n", "selected"],
        [BrailleLine(1, "Line three. $l", "Line three. $l", "\x00" * 14)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["L", "selected"],
        [BrailleLine(2, "Line three. $l", "Line three. $l", "\xc0" + "\x00" * 13)],
    )

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L],
        keyboard.KEYSYM_RIGHT,
    )
    assert capture(session) == (
        ["ine", "selected"],
        [BrailleLine(5, "Line three. $l", "Line three. $l", "\xc0" * 4 + "\x00" * 10)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    assert capture(session) == (
        [" three.", "selected"],
        [BrailleLine(12, "Line three. $l", "Line three. $l", "\xc0" * 11 + "\x00" * 3)],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert capture(session) == (
        [
            "Selected text is:  Line one.\n"
            "Line two has additional words to make it long enough that the text view wraps it.\n"
            "Line three."
        ],
        [],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_HOME)
    assert capture(session) == (
        ["Line three.", "unselected"],
        [BrailleLine(1, "Line three. $l", "Line three. $l", "\x00" * 14)],
    )

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L],
        keyboard.KEYSYM_END,
    )
    assert capture(session) == (
        [
            "Line three.\n"
            "Line four also has extra words to push it past the wrap boundary in the view.\n"
            "Last line.",
            "selected",
        ],
        [BrailleLine(11, "Last line. $l", "Last line. $l", "\xc0" * 10 + "\x00" * 3)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    assert capture(session) == (
        [],
        [
            BrailleLine(
                1,
                "OrcaTextView application frame Line one. $l",
                "Line one. $l",
                "\x00" * 31 + "\xc0" * 9 + "\x00" * 3,
            )
        ],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert capture(session) == (
        [
            "Selected text is:  Line one.\n"
            "Line two has additional words to make it long enough that the text view wraps it.\n"
            "Line three.\n"
            "Line four also has extra words to push it past the wrap boundary in the view.\n"
            "Last line."
        ],
        [],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Text unselected.", "blank"],
        [
            BrailleLine(11, "Last line. $l", "Last line. $l", "\x00" * 13),
            BrailleLine(11, "Last line. $l", "Last line. $l", "\x00" * 13),
        ],
    )
