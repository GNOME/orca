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

"""Tests navigation on a basic web page."""

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
    brailled = [(r.cursor_cell, r.string, r.mask) for r in records if isinstance(r, BrailleRecord)]
    return spoken, brailled


@pytest.mark.native_app
def test_structural_navigation_by_heading(web_basic: NativeAppSession) -> None:
    """Tests structural navigation by heading."""

    session = web_basic
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert _capture(session) == (
        ["h", "Fruit list heading 2"],
        [(1, "Fruit list h2", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert _capture(session) == (
        ["h", "Steps heading 2"],
        [(1, "Steps h2", "\x00" * 8)],
    )

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert _capture(session) == (
        ["h", "Pick a color heading 2"],
        [(1, "Pick a color h2", "\x00" * 15)],
    )

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert _capture(session) == (
        ["h", "Wrapping to top.", "Welcome heading 1"],
        [(0, "Wrapping to top.", "\x00" * 16), (1, "Welcome h1", "\x00" * 10)],
    )

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert _capture(session) == (
        ["h", "Fruit list heading 2"],
        [(1, "Fruit list h2", "\x00" * 13)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert _capture(session) == (
        ["H", "Welcome heading 1"],
        [(1, "Welcome h1", "\x00" * 10)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert _capture(session) == (
        ["H", "Wrapping to bottom.", "Pick a color heading 2"],
        [(0, "Wrapping to bottom.", "\x00" * 19), (1, "Pick a color h2", "\x00" * 15)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert _capture(session) == (
        ["H", "Steps heading 2"],
        [(1, "Steps h2", "\x00" * 8)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert _capture(session) == (
        ["H", "Fruit list heading 2"],
        [(1, "Fruit list h2", "\x00" * 13)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert _capture(session) == (
        ["H", "Welcome heading 1"],
        [(1, "Welcome h1", "\x00" * 10)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_link(web_basic: NativeAppSession) -> None:
    """Tests structural navigation by link."""

    session = web_basic
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_K)
    assert _capture(session) == (
        ["k", "First link link"],
        [(1, "First link", "\xc0" * 10)],
    )

    keyboard.tap_key(keyboard.KEYSYM_K)
    assert _capture(session) == (
        ["k", "second link link"],
        [(1, "second link", "\xc0" * 11)],
    )

    keyboard.tap_key(keyboard.KEYSYM_K)
    assert _capture(session) == (
        ["k", "Wrapping to top.", "First link link"],
        [(0, "Wrapping to top.", "\x00" * 16), (1, "First link", "\xc0" * 10)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_K)
    assert _capture(session) == (
        ["K", "Wrapping to bottom.", "second link link"],
        [(0, "Wrapping to bottom.", "\x00" * 19), (1, "second link", "\xc0" * 11)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_K)
    assert _capture(session) == (
        ["K", "First link link"],
        [(1, "First link", "\xc0" * 10)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_K)
    assert _capture(session) == (
        ["K", "Wrapping to bottom.", "second link link"],
        [(0, "Wrapping to bottom.", "\x00" * 19), (1, "second link", "\xc0" * 11)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_list(web_basic: NativeAppSession) -> None:
    """Tests structural navigation by list."""

    session = web_basic
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert _capture(session) == (
        ["l", "List with 3 items •  Apple item"],
        [(1, "• Apple item", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert _capture(session) == (
        ["l", "leaving list. List with 2 items 1.  First step"],
        [(1, "1. First step", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert _capture(session) == (
        ["l", "Wrapping to top.", "leaving list. List with 3 items •  Apple item"],
        [(0, "Wrapping to top.", "\x00" * 16), (1, "• Apple item", "\x00" * 12)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    assert _capture(session) == (
        ["L", "Wrapping to bottom.", "leaving list. List with 2 items 1.  First step"],
        [(0, "Wrapping to bottom.", "\x00" * 19), (1, "1. First step", "\x00" * 13)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    assert _capture(session) == (
        ["L", "leaving list. List with 3 items •  Apple item"],
        [(1, "• Apple item", "\x00" * 12)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    assert _capture(session) == (
        ["L", "Wrapping to bottom.", "leaving list. List with 2 items 1.  First step"],
        [(0, "Wrapping to bottom.", "\x00" * 19), (1, "1. First step", "\x00" * 13)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_form_field(web_basic: NativeAppSession) -> None:
    """Tests structural navigation by form field."""

    session = web_basic
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Pick a color panel Red color not selected radio button"],
        [(14, " Pick a color& y Red color radio", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Green color not selected radio button"],
        [(14, " Pick a color& y Green color rad", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Blue color not selected radio button"],
        [(14, " Pick a color& y Blue color radi", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Wrapping to top.", "Red color not selected radio button"],
        [
            (0, "Wrapping to top.", "\x00" * 16),
            (14, " Pick a color& y Red color radio", "\x00" * 32),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["F", "Wrapping to bottom.", "Blue color not selected radio button"],
        [
            (0, "Wrapping to bottom.", "\x00" * 19),
            (14, " Pick a color& y Blue color radi", "\x00" * 32),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["F", "Green color not selected radio button"],
        [(14, " Pick a color& y Green color rad", "\x00" * 32)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["F", "Red color not selected radio button"],
        [(14, " Pick a color& y Red color radio", "\x00" * 32)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["F", "Wrapping to bottom.", "Blue color not selected radio button"],
        [
            (0, "Wrapping to bottom.", "\x00" * 19),
            (14, " Pick a color& y Blue color radi", "\x00" * 32),
        ],
    )


@pytest.mark.native_app
def test_caret_navigation(web_basic: NativeAppSession) -> None:
    """Tests caret navigation."""

    session = web_basic
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["First link  and  second link ."],
        [
            (
                1,
                "First link and second link.",
                "\xc0" * 10 + "\x00" * 5 + "\xc0" * 11 + "\x00",
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Fruit list heading 2"],
        [(1, "Fruit list h2", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["List with 3 items •  Apple item"],
        [(1, "• Apple item", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["•  Banana item"],
        [(1, "• Banana item", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["•  Cherry item"],
        [(1, "• Cherry item", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["leaving list. Steps heading 2"],
        [(1, "Steps h2", "\x00" * 8)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert _capture(session) == (
        ["List with 3 items •  Cherry item"],
        [(1, "• Cherry item", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert _capture(session) == (
        ["•  Banana item"],
        [(1, "• Banana item", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert _capture(session) == (
        ["•  Apple item"],
        [(1, "• Apple item", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert _capture(session) == (
        ["leaving list. Fruit list heading 2"],
        [(1, "Fruit list h2", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert _capture(session) == (
        ["First link  and  second link ."],
        [
            (
                1,
                "First link and second link.",
                "\xc0" * 10 + "\x00" * 5 + "\xc0" * 11 + "\x00",
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert _capture(session) == (
        ["Welcome heading 1"],
        [(1, "Welcome h1", "\x00" * 10)],
    )


@pytest.mark.native_app
def test_radio_group_in_focus_mode(web_basic: NativeAppSession) -> None:
    """Tests presentation in a radio button group in focus mode."""

    session = web_basic
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Pick a color panel Red color not selected radio button"],
        [(14, " Pick a color& y Red color radio", "\x00" * 32)],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    assert _capture(session) == (
        ["Focus mode"],
        [(0, "Focus mode", "\x00" * 10)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Green color selected radio button"],
        [
            (14, " Pick a color& y Red color radio", "\x00" * 32),
            (14, " Pick a color&=y Green color rad", "\x00" * 32),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Blue color selected radio button"],
        [(14, " Pick a color&=y Blue color radi", "\x00" * 32)],
    )
