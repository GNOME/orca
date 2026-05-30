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

"""Tests presentation of ARIA spinbuttons (one non-editable, one contenteditable)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _quantity_line(value: int) -> helpers.BrailleLine:
    text = f"Quantity {value} spin button"
    return helpers.BrailleLine(1, text, text, "\x00" * len(text))


@pytest.mark.native_app
def test_quantity_focus_and_arrow(web_aria_spinbutton: NativeAppSession) -> None:
    """Tests Tab focus and Up/Down on the non-editable ARIA spinbutton."""

    session = web_aria_spinbutton
    helpers.reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Quantity", "spin button", "3", "Focus mode"],
        [
            _quantity_line(3),
            helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10),
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["4"],
        [_quantity_line(3), _quantity_line(4)],
    )
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["3"],
        [_quantity_line(3)],
    )


@pytest.mark.native_app
def test_quantity_page_home_end_and_boundaries(web_aria_spinbutton: NativeAppSession) -> None:
    """Tests PageUp/Down, Home/End, and clamping at min/max on the non-editable spinbutton."""

    session = web_aria_spinbutton
    helpers.reset_web_state(session)
    helpers.tab_and_swallow_presentation(session)

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    assert helpers.capture(session) == (
        ["10"],
        [_quantity_line(3), _quantity_line(10)],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == ([], [])
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert helpers.capture(session) == (["0"], [_quantity_line(0)])
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == ([], [])
    keyboard.tap_key(keyboard.KEYSYM_END)
    assert helpers.capture(session) == (["10"], [_quantity_line(10)])
    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    assert helpers.capture(session) == (["0"], [_quantity_line(0)])


@pytest.mark.native_app
def test_rating_focus_and_arrow(web_aria_spinbutton: NativeAppSession) -> None:
    """Tests Tab focus and Up/Down on the editable ARIA spinbutton (Rating)."""

    session = web_aria_spinbutton
    helpers.reset_web_state(session)
    helpers.tab_and_swallow_presentation(session)  # Quantity
    helpers.tab_and_swallow_presentation(session)  # Bump Quantity button
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Rating", "spin button", "75", "Focus mode"],
        [
            helpers.BrailleLine(
                1,
                "Bump Quantity in 1000 ms button",
                "Bump Quantity in 1000 ms button",
                "\x00" * 31,
            ),
            helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12),
            helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10),
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["76"],
        [
            helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12),
            helpers.BrailleLine(8, "Rating 76 $l", "Rating 76 $l", "\x00" * 12),
            helpers.BrailleLine(8, "Rating 76 $l", "Rating 76 $l", "\x00" * 12),
            helpers.BrailleLine(8, "Rating 76 $l", "Rating 76 $l", "\x00" * 12),
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["75"],
        [
            helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12),
            helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12),
            helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12),
        ],
    )


def _tab_to_rating(session: NativeAppSession) -> None:
    helpers.tab_and_swallow_presentation(session)  # Quantity
    helpers.tab_and_swallow_presentation(session)  # Bump Quantity button
    helpers.tab_and_swallow_presentation(session)  # Rating


def _reload(session: NativeAppSession) -> None:
    """Reloads the page so spinbutton values return to the defaults from the HTML."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_R)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()


@pytest.mark.native_app
def test_rating_page_home_end_and_boundaries(web_aria_spinbutton: NativeAppSession) -> None:
    """Tests PageUp/Down, Home/End, and clamping at min/max on the editable spinbutton."""

    session = web_aria_spinbutton
    helpers.reset_web_state(session)
    _tab_to_rating(session)

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    assert helpers.capture(session) == (
        ["85"],
        [
            helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12),
            helpers.BrailleLine(8, "Rating 85 $l", "Rating 85 $l", "\x00" * 12),
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    assert helpers.capture(session) == (
        ["75"],
        [helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12)],
    )
    keyboard.tap_key(keyboard.KEYSYM_END)
    assert helpers.capture(session) == (
        ["100"],
        [
            helpers.BrailleLine(8, "Rating 100 $l", "Rating 100 $l", "\x00" * 13),
            helpers.BrailleLine(8, "Rating 100 $l", "Rating 100 $l", "\x00" * 13),
            helpers.BrailleLine(8, "Rating 100 $l", "Rating 100 $l", "\x00" * 13),
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == ([], [])
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert helpers.capture(session) == (
        ["0"],
        [
            helpers.BrailleLine(8, "Rating 0 $l", "Rating 0 $l", "\x00" * 11),
            helpers.BrailleLine(8, "Rating 0 $l", "Rating 0 $l", "\x00" * 11),
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == ([], [])


@pytest.mark.native_app
def test_rating_caret_navigation(web_aria_spinbutton: NativeAppSession) -> None:
    """Tests Left/Right caret navigation within the editable spinbutton's text."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_rating(session)

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [],
        [helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12)],
    )
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == ([], [])
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["5"],
        [helpers.BrailleLine(9, "Rating 75 $l", "Rating 75 $l", "\x00" * 12)],
    )
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["75"],
        [helpers.BrailleLine(10, "Rating 75 $l", "Rating 75 $l", "\x00" * 12)],
    )


@pytest.mark.native_app
def test_rating_shift_selection(web_aria_spinbutton: NativeAppSession) -> None:
    """Tests Shift+Left/Right selection on the editable spinbutton's "75" text."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_rating(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [],
        [helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12)],
    )
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == ([], [])
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["7", "selected"],
        [
            helpers.BrailleLine(
                9, "Rating 75 $l", "Rating 75 $l", "\x00" * 7 + "\xc0" + "\x00" * 4
            ),
        ],
    )
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["5", "selected"],
        [
            helpers.BrailleLine(
                10, "Rating 75 $l", "Rating 75 $l", "\x00" * 7 + "\xc0\xc0" + "\x00" * 3
            ),
        ],
    )


@pytest.mark.native_app
def test_rating_backspace_delete(web_aria_spinbutton: NativeAppSession) -> None:
    """Tests Backspace and Delete in the editable spinbutton."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_rating(session)

    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.capture(session) == (
        [],
        [helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12)],
    )
    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.capture(session) == ([], [])

    keyboard.tap_key(keyboard.KEYSYM_8)
    assert helpers.capture(session) == (
        ["875"],
        [
            helpers.BrailleLine(9, "Rating 875 $l", "Rating 875 $l", "\x00" * 13),
            helpers.BrailleLine(9, "Rating 875 $l", "Rating 875 $l", "\x00" * 13),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["8"],
        [helpers.BrailleLine(8, "Rating 875 $l", "Rating 875 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    assert helpers.capture(session) == (
        ["75"],
        [
            helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12),
            helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12),
        ],
    )


@pytest.mark.native_app
def test_rating_typing(web_aria_spinbutton: NativeAppSession) -> None:
    """Tests typing digits at the caret position in the editable spinbutton."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_rating(session)

    keyboard.tap_key(keyboard.KEYSYM_8)
    assert helpers.capture(session) == (
        ["875"],
        [
            helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12),
            helpers.BrailleLine(9, "Rating 875 $l", "Rating 875 $l", "\x00" * 13),
            helpers.BrailleLine(9, "Rating 875 $l", "Rating 875 $l", "\x00" * 13),
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_0)
    assert helpers.capture(session) == (
        ["0"],
        [helpers.BrailleLine(10, "Rating 8075 $l", "Rating 8075 $l", "\x00" * 14)],
    )


@pytest.mark.native_app
def test_volume_readonly_input_spinbutton(web_aria_spinbutton: NativeAppSession) -> None:
    """Tests a readonly <input role='spinbutton'>: text-object path with text exposed."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    for _ in range(4):
        helpers.tab_and_swallow_presentation(session)

    value_selected = "\x00" * 7 + "\xc0\xc0" + "\x00" * 7
    volume_50 = helpers.BrailleLine(10, "Volume 50 rdonly", "Volume 50 rdonly", value_selected)
    bump_rating = "Bump Rating in 1000 ms button"
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Volume", "spin button", "50", "grayed", "Focus mode"],
        [
            helpers.BrailleLine(1, bump_rating, bump_rating, "\x00" * len(bump_rating)),
            volume_50,
            helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == ([], [volume_50])

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == ([], [])

    keyboard.tap_key(keyboard.KEYSYM_5)
    assert helpers.capture(session) == (["5"], [])


def _tab_to_bump_button(session: NativeAppSession, *, target_quantity: bool) -> None:
    """Tabs to the Quantity or Rating bump button."""

    tab_count = 2 if target_quantity else 4
    for _ in range(tab_count):
        helpers.tab_and_swallow_presentation(session)


@pytest.mark.native_app
def test_quantity_programmatic_change_focus_on_bump_button(
    web_aria_spinbutton: NativeAppSession,
) -> None:
    """Tests that an off-focus ARIA value bump is speech-silent for Quantity."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_bump_button(session, target_quantity=True)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    bump_label = "Bump Quantity in 1000 ms button"
    assert helpers.capture(session, quiescence=1.5, overall=3.5, wait_async=True) == (
        [],
        [helpers.BrailleLine(1, bump_label, bump_label, "\x00" * len(bump_label))],
    )


@pytest.mark.native_app
def test_quantity_programmatic_change_focus_on_spinbutton(
    web_aria_spinbutton: NativeAppSession,
) -> None:
    """Tests an in-focus ARIA value bump on Quantity: new value announced."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_bump_button(session, target_quantity=True)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    bump_label = "Bump Quantity in 1000 ms button"
    assert helpers.capture(session, quiescence=1.5, overall=3.5, wait_async=True) == (
        ["4"],
        [
            helpers.BrailleLine(1, bump_label, bump_label, "\x00" * len(bump_label)),
            _quantity_line(3),
            helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10),
            _quantity_line(3),
            _quantity_line(4),
        ],
    )


@pytest.mark.native_app
def test_rating_programmatic_change_focus_on_bump_button(
    web_aria_spinbutton: NativeAppSession,
) -> None:
    """Tests an off-focus ARIA value bump on the editable Rating."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_bump_button(session, target_quantity=False)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    bump_label = "Bump Rating in 1000 ms button"
    assert helpers.capture(session, quiescence=1.5, overall=3.5, wait_async=True) == (
        ["76"],
        [
            helpers.BrailleLine(1, bump_label, bump_label, "\x00" * len(bump_label)),
            helpers.BrailleLine(8, "Rating 76 $l", "Rating 76 $l", "\x00" * 12),
        ],
    )


@pytest.mark.native_app
def test_rating_programmatic_change_focus_on_spinbutton(
    web_aria_spinbutton: NativeAppSession,
) -> None:
    """Tests an in-focus ARIA value bump on the editable Rating: new value announced."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_bump_button(session, target_quantity=False)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    bump_label = "Bump Rating in 1000 ms button"
    rating_76 = helpers.BrailleLine(8, "Rating 76 $l", "Rating 76 $l", "\x00" * 12)
    assert helpers.capture(session, quiescence=1.5, overall=3.5, wait_async=True) == (
        ["76"],
        [
            helpers.BrailleLine(1, bump_label, bump_label, "\x00" * len(bump_label)),
            helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12),
            helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10),
            rating_76,
            rating_76,
            rating_76,
        ],
    )
