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
from .apps import browser
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


def _quantity_line(session: BrowserSession, value: int) -> helpers.BrailleLine:
    # Firefox exposes the value through Text; Chromium uses Value presentation.
    text = helpers.expected_for_browser(
        session, f"Quantity {value} spin button", firefox=f"Quantity {value}"
    )
    cursor_cell = helpers.expected_for_browser(session, 1, firefox=9)
    return helpers.BrailleLine(cursor_cell, text, text, "\x00" * len(text))


@pytest.mark.native_app
def test_quantity_focus_and_arrow(web_aria_spinbutton: BrowserSession) -> None:
    """Tests Tab focus and Up/Down on the non-editable ARIA spinbutton."""

    session = web_aria_spinbutton
    helpers.reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Quantity", "spin button", "3", "Focus mode"],
        [
            _quantity_line(session, 3),
            helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10),
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["4"]
    assert brailled[-1] == _quantity_line(session, 4)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["3"]
    assert brailled[-1] == _quantity_line(session, 3)


@pytest.mark.native_app
@helpers.skip_firefox_caret_tab()
def test_quantity_page_home_end_and_boundaries(web_aria_spinbutton: BrowserSession) -> None:
    """Tests PageUp/Down, Home/End, and clamping at min/max on the non-editable spinbutton."""

    session = web_aria_spinbutton
    helpers.reset_web_state(session)
    helpers.tab_and_swallow_presentation(session)

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["10"]
    assert brailled[-1] == _quantity_line(session, 10)
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == ([], [])
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["0"]
    assert brailled[-1] == _quantity_line(session, 0)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == ([], [])
    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["10"]
    assert brailled[-1] == _quantity_line(session, 10)
    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["0"]
    assert brailled[-1] == _quantity_line(session, 0)


@pytest.mark.native_app
@helpers.skip_firefox_caret_tab()
def test_rating_focus_and_arrow(web_aria_spinbutton: BrowserSession) -> None:
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


def _tab_to_rating(session: BrowserSession) -> None:
    helpers.tab_and_swallow_presentation(session)  # Quantity
    helpers.tab_and_swallow_presentation(session)  # Bump Quantity button
    helpers.tab_and_swallow_presentation(session)  # Rating


def _reload(session: BrowserSession) -> None:
    """Reloads the page so spinbutton values return to the defaults from the HTML."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_R)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()


@pytest.mark.native_app
@helpers.skip_firefox_caret_tab()
def test_rating_page_home_end_and_boundaries(web_aria_spinbutton: BrowserSession) -> None:
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
    spoken, brailled = helpers.capture(session)
    assert spoken == ["0"]
    assert brailled[-1] == helpers.BrailleLine(8, "Rating 0 $l", "Rating 0 $l", "\x00" * 11)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == ([], [])


@pytest.mark.native_app
def test_rating_caret_navigation(web_aria_spinbutton: BrowserSession) -> None:
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
def test_rating_shift_selection(web_aria_spinbutton: BrowserSession) -> None:
    """Tests Shift+Left/Right selection on the editable spinbutton's "75" text."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_rating(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_LEFT)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        [],
        [helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12)],
    )
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == ([], [])
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["7", "selected"],
        [
            helpers.BrailleLine(
                9, "Rating 75 $l", "Rating 75 $l", "\x00" * 7 + "\xc0" + "\x00" * 4
            ),
        ],
    )
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["5", "selected"],
        [
            helpers.BrailleLine(
                10, "Rating 75 $l", "Rating 75 $l", "\x00" * 7 + "\xc0\xc0" + "\x00" * 3
            ),
        ],
    )


@pytest.mark.native_app
def test_rating_backspace_delete(web_aria_spinbutton: BrowserSession) -> None:
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
def test_rating_typing(web_aria_spinbutton: BrowserSession) -> None:
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
    # aria-valuenow clamps at the max, but the changed value text ("8075") should still
    # be announced.
    assert helpers.capture(session) == (
        ["8075"],
        [
            helpers.BrailleLine(10, "Rating 8075 $l", "Rating 8075 $l", "\x00" * 14),
            helpers.BrailleLine(10, "Rating 8075 $l", "Rating 8075 $l", "\x00" * 14),
        ],
    )


def _tab_to_volume(session: BrowserSession) -> None:
    """Reloads the page and focuses the read-only Volume spinbutton."""

    _reload(session)
    helpers.reset_web_state(session)
    for _ in range(4):
        helpers.tab_and_swallow_presentation(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)


@pytest.mark.native_app
def test_volume_readonly_input_spinbutton(web_aria_spinbutton: BrowserSession) -> None:
    """Tests focus and key presentation for a read-only input spinbutton."""

    session = web_aria_spinbutton
    _tab_to_volume(session)
    # Chromium omits SENSITIVE on this read-only control; Firefox retains it.
    assert helpers.speech(session) == helpers.expected_for_browser(
        session,
        ["Volume", "spin button", "50", "grayed", "Focus mode"],
        firefox=["Volume", "spin button", "50", "Focus mode"],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.speech(session) == []

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == ([], [])

    keyboard.tap_key(keyboard.KEYSYM_5)
    assert helpers.capture(session) == (["5"], [])


# Required state mapping: https://www.w3.org/TR/core-aam-1.2/#ariaReadonlyTrue
@pytest.mark.native_app
@pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason="Firefox's ATK state mapping does not expose READ_ONLY: "
    "https://bugzilla.mozilla.org/show_bug.cgi?id=1356018",
    raises=AssertionError,
    strict=True,
)
def test_volume_readonly_braille(web_aria_spinbutton: BrowserSession) -> None:
    """Tests that braille identifies the Volume spinbutton as read-only."""

    session = web_aria_spinbutton
    _tab_to_volume(session)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_UP)
    _, brailled = helpers.capture(session)
    value_selected = "\x00" * 7 + "\xc0\xc0" + "\x00" * 7
    assert brailled[-1] == helpers.BrailleLine(
        10, "Volume 50 rdonly", "Volume 50 rdonly", value_selected
    )


def _tab_to_bump_button(session: BrowserSession, *, target_quantity: bool) -> None:
    """Tabs to the Quantity or Rating bump button."""

    tab_count = 2 if target_quantity else 4
    for _ in range(tab_count):
        helpers.tab_and_swallow_presentation(session)


@pytest.mark.native_app
def test_quantity_programmatic_change_focus_on_bump_button(
    web_aria_spinbutton: BrowserSession,
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
    web_aria_spinbutton: BrowserSession,
) -> None:
    """Tests an in-focus ARIA value bump on Quantity: new value announced."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_bump_button(session, target_quantity=True)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session, quiescence=1.5, overall=3.5, wait_async=True)
    assert spoken == ["4"]
    assert brailled[-1] == _quantity_line(session, 4)


@pytest.mark.native_app
def test_rating_programmatic_change_focus_on_bump_button(
    web_aria_spinbutton: BrowserSession,
) -> None:
    """Tests that an off-focus Rating update preserves focus and subsequent navigation."""

    session = web_aria_spinbutton
    _reload(session)
    helpers.reset_web_state(session)
    _tab_to_bump_button(session, target_quantity=False)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    bump_label = "Bump Rating in 1000 ms button"
    spoken, brailled = helpers.capture(session, quiescence=1.5, overall=3.5, wait_async=True)
    assert spoken == []
    assert brailled[-1] == helpers.BrailleLine(1, bump_label, bump_label, "\x00" * len(bump_label))

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Rating", "spin button", "76", "Focus mode"]
    assert brailled[-1] == helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)
    assert session.orca.get("DocumentPresenter", "InFocusMode")

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["75"]
    assert brailled[-1] == helpers.BrailleLine(8, "Rating 75 $l", "Rating 75 $l", "\x00" * 12)


@pytest.mark.native_app
def test_rating_programmatic_change_focus_on_spinbutton(
    web_aria_spinbutton: BrowserSession,
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
