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

"""Tests Tab landings (incl. focus-mode entry/exit) and state changes per form control."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_tab_navigation_and_state_changes(web_form_fields: NativeAppSession) -> None:
    """Tests Tab landings (incl. focus-mode entry/exit) and state changes per form control."""

    session = web_form_fields
    helpers.reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Name", "entry", "Jane Doe", "selected", "Focus mode"],
        [
            helpers.BrailleLine(
                14,
                "Name Jane Doe $l",
                "Name Jane Doe $l",
                "\x00" * 5 + "\xc0" * 8 + "\x00" * 3,
            ),
            helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10),
        ],
    )

    # Tabbing away repaints the Name line before the Bio line, and whether that repaint still
    # shows Jane Doe as selected depends on whether Chromium has cleared the entry's selection
    # yet: the mask comes from a live AXText.get_selected_ranges() call at paint time, so both
    # outcomes are correct. Assert the braille the display lands on.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Bio", "entry", "First line of bio. "]
    assert brailled[-1] == helpers.BrailleLine(
        5,
        "Bio First line of bio.  $l",
        "Bio First line of bio.  $l",
        "\x00" * 26,
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Search", "editable combo box", "opens listbox"],
        [helpers.BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Fruit", "combo box", "Apple", "opens menu"],
        [helpers.BrailleLine(7, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Banana"],
        [helpers.BrailleLine(7, "Fruit Banana combo box", "Fruit Banana combo box", "\x00" * 22)],
    )
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Cherry"],
        [helpers.BrailleLine(7, "Fruit Cherry combo box", "Fruit Cherry combo box", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Preferred contact", "combo box", "Email", "opens listbox"],
        [
            helpers.BrailleLine(
                19,
                "Preferred contact Email combo box",
                "Preferred contact Email combo bo",
                "\x00" * 33,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Subscribe", "check box not checked", "Browse mode"],
        [
            helpers.BrailleLine(
                1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23
            ),
            helpers.BrailleLine(0, "Browse mode", "Browse mode", "\x00" * 11),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.capture(session) == (
        ["checked"],
        [
            helpers.BrailleLine(
                1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23
            ),
            helpers.BrailleLine(
                1, "<x> Subscribe check box", "<x> Subscribe check box", "\x00" * 23
            ),
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.capture(session) == (
        ["not checked"],
        [helpers.BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["All topics", "check box partially checked"],
        [
            helpers.BrailleLine(
                1, "<-> All topics check box", "<-> All topics check box", "\x00" * 24
            )
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.capture(session) == (
        ["checked"],
        [
            helpers.BrailleLine(
                1, "<x> All topics check box", "<x> All topics check box", "\x00" * 24
            )
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.capture(session) == (
        ["not checked"],
        [
            helpers.BrailleLine(
                1, "< > All topics check box", "< > All topics check box", "\x00" * 24
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["News", "check box not checked"],
        [helpers.BrailleLine(1, "< > News check box", "< > News check box", "\x00" * 18)],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Events", "check box not checked"],
        [helpers.BrailleLine(1, "< > Events check box", "< > Events check box", "\x00" * 20)],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Pick a color", "panel", "Red color", "not selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color & y Red color radio button",
                "& y Red color radio button",
                "\x00" * 39,
            ),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["leaving panel.", "Seat", "panel", "Aisle", "not selected radio button"],
        [
            helpers.BrailleLine(
                1, "Seat & y Aisle radio button", "& y Aisle radio button", "\x00" * 27
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["leaving panel.", "Quantity", "spin button", "3", "Focus mode"],
        [
            helpers.BrailleLine(
                11,
                "Quantity 3 $l",
                "Quantity 3 $l",
                "\x00" * 9 + "\xc0" + "\x00" * 3,
            ),
            helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10),
        ],
    )

    # The prior value is repainted before the new one, and whether it still shows as selected
    # depends on Chromium's timing, same as the Name line above.
    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["4"]
    assert brailled[-1] == helpers.BrailleLine(11, "Quantity 4 $l", "Quantity 4 $l", "\x00" * 13)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["3"],
        [helpers.BrailleLine(11, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Submit", "button", "Browse mode"],
        [
            helpers.BrailleLine(1, "Submit button", "Submit button", "\x00" * 13),
            helpers.BrailleLine(0, "Browse mode", "Browse mode", "\x00" * 11),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Mute", "toggle button not pressed"],
        [
            helpers.BrailleLine(1, "Submit button", "Submit button", "\x00" * 13),
            helpers.BrailleLine(
                1,
                "& y Mute toggle button",
                "& y Mute toggle button",
                "\x00" * 22,
            ),
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.capture(session) == (
        ["pressed"],
        [helpers.BrailleLine(1, "&=y Mute toggle button", "&=y Mute toggle button", "\x00" * 22)],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.capture(session) == (
        ["not pressed"],
        [helpers.BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Wi-Fi", "off switch"],
        [helpers.BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16)],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.capture(session) == (
        ["on"],
        [helpers.BrailleLine(1, "&=y Wi-Fi switch", "&=y Wi-Fi switch", "\x00" * 16)],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.capture(session) == (
        ["off"],
        [helpers.BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16)],
    )


@pytest.mark.native_app
def test_arrowing_a_native_radio_group_in_browse_mode(
    web_form_fields: NativeAppSession,
) -> None:
    """Tests arrowing through a native radio group in browse mode."""

    session = web_form_fields
    helpers.reset_web_state(session)
    for _ in range(10):
        helpers.tab_and_swallow_presentation(session)

    # The arrow keys are Orca's caret navigation here, so the browser never sees them
    # and no radio button is selected.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Green color", "not selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color & y Green color radio button",
                "& y Green color radio button",
                "\x00" * 41,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["Red color", "not selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color & y Red color radio button",
                "& y Red color radio button",
                "\x00" * 39,
            )
        ],
    )


@pytest.mark.native_app
def test_arrowing_an_aria_radio_group_in_focus_mode(
    web_form_fields: NativeAppSession,
) -> None:
    """Tests arrowing through an ARIA radio group in focus mode."""

    session = web_form_fields
    helpers.reset_web_state(session)
    for _ in range(11):
        helpers.tab_and_swallow_presentation(session)

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    assert helpers.speech(session) == ["Focus mode"]

    # In focus mode the arrow keys reach the page, so the group selects as it moves.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session)[0] == ["Middle", "selected radio button"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Window", "selected radio button"],
        [
            helpers.BrailleLine(
                1, "Seat &=y Window radio button", "&=y Window radio button", "\x00" * 28
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["Middle", "selected radio button"],
        [
            helpers.BrailleLine(
                1, "Seat &=y Middle radio button", "&=y Middle radio button", "\x00" * 28
            )
        ],
    )
