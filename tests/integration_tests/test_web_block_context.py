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

"""Tests line grouping for same-row siblings: block content stays separate, inline flexes merge."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import capture, move_to_top, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_LINES = [
    (["• Bread"], "• Bread"),
    (["leaving list.", "Cheese"], "Cheese"),
    (["code start", "Code one"], "Code one $l"),
    (["Code two", "code end"], "Code two $l"),
    (["After code"], "After code"),
    (
        ["banner", "Home", "image link", "Shop by category", "button"],
        "Home image Shop by category button",
    ),
    (
        [
            "leaving banner.",
            "navigation",
            "Categories",
            "List with 3 items",
            "Motors",
            "link",
            "Expand: Motors",
            "button",
            "Electronics",
            "link",
            "Expand: Electronics",
            "button",
            "Collectibles",
            "link",
            "Expand: Collectibles",
            "button",
        ],
        "Motors Expand: Motors button Electronics Expand: Electronics button "
        "Collectibles Expand: Collectibles button",
    ),
    (["leaving list.", "leaving navigation.", "The end."], "The end."),
]


@pytest.mark.native_app
def test_block_context_boundaries_stay_on_separate_lines(
    web_block_context: NativeAppSession,
) -> None:
    """Tests block content stays separate while flex rows of an image link and toggles group."""

    session = web_block_context
    reset_web_state(session)
    move_to_top(session)
    for expected_speech, expected_line in _LINES:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, braille = capture(session)
        assert spoken == expected_speech
        assert [line.full for line in braille] == [expected_line]
