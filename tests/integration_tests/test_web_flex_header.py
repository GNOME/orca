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

"""Tests a flex row of mixed-display items groups on one line, but a stacked flex reflows."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


# A flex item is transparent for line grouping, but the visual same-line check still governs: the
# horizontal header (inline logo, flex buttons, inline-block input, block select) is one line,
# while the stacked (flex-direction: column) header reflows to one item per line.
_DOWN_LINES = [
    (
        [
            "banner",
            "Home",
            "image link",
            "Shop by category",
            "button",
            "Search for anything",
            "entry",
            "Camera",
            "button",
            "Category",
            "combo box",
            "All Categories",
            "opens menu",
        ],
        "Home image Shop by category button Search for anything  $l Camera button "
        "Category All Categories combo box",
    ),
    (["leaving banner.", "banner", "Stacked one", "button"], "Stacked one button"),
    (["Stacked two", "button"], "Stacked two button"),
    (["Stacked three", "button"], "Stacked three button"),
    (["leaving banner.", "After header."], "After header."),
]


@pytest.mark.native_app
def test_line_down_groups_flex_row_but_reflows_stacked_flex(
    web_flex_header: NativeAppSession,
) -> None:
    """Tests the horizontal flex header is one line and the stacked flex is one item per line."""

    session = web_flex_header
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    for expected_speech, expected_line in _DOWN_LINES:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, braille = helpers.capture(session)
        assert spoken == expected_speech
        assert [line.full for line in braille] == [expected_line]
