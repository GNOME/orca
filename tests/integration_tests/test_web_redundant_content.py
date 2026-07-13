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

"""Tests that redundant content is not presented in speech or braille."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_bottom, move_to_top, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_say_all_omits_redundant_content(web_redundant_content: NativeAppSession) -> None:
    """Tests that Say All omits all the redundant content."""

    session = web_redundant_content
    reset_web_state(session)
    # Warm the line-contents caches: the first Say All after load can halt in editable content.
    move_to_bottom(session)
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    # KNOWN ISSUE: the wrapping link is dropped, leaving only its image.
    assert speech(session) == [
        "Visit ",
        "house",
        "image",
        " now.",
        "Status: ",
        "entry",
        "x",
        "invalid entry: Field is required.",
        " done.",
        "Notes",
        "A ",
        "one",
        "image",
        "two",
        "image",
        "x ",
        "Red square",
        "image",
        "Blue square",
        "image",
        " y",
        "p ",
        "Green square",
        "image",
        "Cyan square",
        "image",
        " q",
        "The end.",
    ]


@pytest.mark.native_app
def test_line_navigation_drops_error_message_from_content(
    web_redundant_content: NativeAppSession,
) -> None:
    """Tests that the inline error message is dropped from the line's speech and braille."""

    move_to_top(web_redundant_content)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(web_redundant_content) == (
        ["Status: ", "entry", "x", "invalid entry: Field is required.", " done."],
        [
            BrailleLine(
                1,
                "Status: x invalid: Field is required.  done.",
                "Status: x invalid: Field is requ",
                "\x00" * 44,
            )
        ],
    )


@pytest.mark.native_app
def test_line_navigation_drops_useless_image_in_editable(
    web_redundant_content: NativeAppSession,
) -> None:
    """Tests that the useless image between the meaningful images is dropped in speech/braille."""

    move_to_top(web_redundant_content)

    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(web_redundant_content)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(web_redundant_content) == (
        ["Notes", "Icons", "x ", "Red square", "image", "Blue square", "image", " y"],
        [
            BrailleLine(
                1,
                "x  $l Red square image Blue square image y $l",
                "x  $l Red square image Blue squa",
                "\x00" * 45,
            )
        ],
    )
