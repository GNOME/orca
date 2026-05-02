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

from orca.output_reader import BrailleRecord, SpeechRecord

from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _move_to_top(session: NativeAppSession) -> None:
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _capture(
    session: NativeAppSession,
) -> tuple[list[str], list[tuple[int, str, str | None]]]:
    records = session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    spoken = [r.text for r in records if isinstance(r, SpeechRecord)]
    brailled = [
        (r.cursor_cell, r.string, r.mask) for r in records if isinstance(r, BrailleRecord)
    ]
    return spoken, brailled


@pytest.mark.native_app
def test_caret_navigation_presentation(gtk3_text_view: NativeAppSession) -> None:
    """Orca's announcements as the caret moves via arrows, word/line jumps, buffer endpoints."""

    session = gtk3_text_view
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Line two has additional words to make it long enough that "],
        [(1, "Line two has additional words to", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["the text view wraps it.\n"],
        [(1, "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Line three.\n"],
        [(1, "Line three. $l", "\x00" * 14)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert _capture(session) == (
        ["the text view wraps it.\n"],
        [(1, "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (
        ["h"],
        [(2, "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (
        ["the"],
        [(4, "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_END)
    assert _capture(session) == (
        ["blank"],
        [(24, "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert _capture(session) == (
        ["t"],
        [(1, "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    assert _capture(session) == (
        ["Last line."],
        [(11, "Last line. $l", "\x00" * 13)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert _capture(session) == (
        ["Line one.\n"],
        [(1, "Line one. $l", "\x00" * 12)],
    )


@pytest.mark.native_app
def test_caret_selection_presentation(gtk3_text_view: NativeAppSession) -> None:
    """Orca's announcements as selection changes by line, word, char, jumps, and select-all."""

    session = gtk3_text_view
    _move_to_top(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Line one.\n", "selected"],
        [(1, "Line two has additional words to", "\x00" * 32)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Line two has additional words to make it long enough that ", "selected"],
        [(1, "the text view wraps it. $l", "\x00" * 26)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["the text view wraps it.\n", "selected"],
        [(1, "Line three. $l", "\x00" * 14)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (
        ["L", "selected"],
        [(2, "Line three. $l", "\xc0" + "\x00" * 13)],
    )

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT,
    )
    assert _capture(session) == (
        ["ine", "selected"],
        [(5, "Line three. $l", "\xc0" * 4 + "\x00" * 10)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    assert _capture(session) == (
        [" three.", "selected"],
        [(12, "Line three. $l", "\xc0" * 11 + "\x00" * 3)],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert _capture(session) == (
        [
            "Selected text is:  Line one.\n"
            "Line two has additional words to make it long enough that the text view wraps it.\n"
            "Line three.",
        ],
        [],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_HOME)
    assert _capture(session) == (
        ["Line three.", "unselected"],
        [(1, "Line three. $l", "\x00" * 14)],
    )

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END,
    )
    assert _capture(session) == (
        [
            "Line three.\n"
            "Line four also has extra words to push it past the wrap boundary in the view.\n"
            "Last line.",
            "selected",
        ],
        [(11, "Last line. $l", "\xc0" * 10 + "\x00" * 3)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    assert _capture(session) == (
        [],
        [(1, "Line one. $l", "\xc0" * 9 + "\x00" * 3)],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert _capture(session) == (
        [
            "Selected text is:  Line one.\n"
            "Line two has additional words to make it long enough that the text view wraps it.\n"
            "Line three.\n"
            "Line four also has extra words to push it past the wrap boundary in the view.\n"
            "Last line.",
        ],
        [],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (
        ["Text unselected.", "blank"],
        [
            (11, "Last line. $l", "\x00" * 13),
            (11, "Last line. $l", "\x00" * 13),
        ],
    )
