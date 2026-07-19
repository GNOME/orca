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

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Bio", "entry", "First line of bio. "],
        [
            # The Name line keeps a stale selected-text mask: the braille line-info cache is not
            # invalidated when Chromium clears the selection on blur.
            helpers.BrailleLine(
                14, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 5 + "\xc0" * 8 + "\x00" * 3
            ),
            helpers.BrailleLine(
                5,
                "Bio First line of bio.  $l",
                "Bio First line of bio.  $l",
                "\x00" * 26,
            ),
        ],
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
        ["Pick a color", "panel", "Red color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            ),
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

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["4"],
        [
            # Stale selected-text mask on the prior value (see the Name line above).
            helpers.BrailleLine(
                11, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 9 + "\xc0" + "\x00" * 3
            ),
            helpers.BrailleLine(11, "Quantity 4 $l", "Quantity 4 $l", "\x00" * 13),
        ],
    )
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
        ["Wi-Fi", "switch not pressed"],
        [helpers.BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16)],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.capture(session) == (
        ["pressed"],
        [helpers.BrailleLine(1, "&=y Wi-Fi switch", "&=y Wi-Fi switch", "\x00" * 16)],
    )
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.capture(session) == (
        ["not pressed"],
        [helpers.BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16)],
    )
