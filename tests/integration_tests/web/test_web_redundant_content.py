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

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_say_all_omits_redundant_content(web_redundant_content: BrowserSession) -> None:
    """Tests that Say All omits all the redundant content."""

    session = web_redundant_content
    helpers.reset_web_state(session)
    # Ensure we're really at the top of the page.
    helpers.move_to_bottom(session)
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert helpers.speech(session) == [
        "Visit ",
        "Home ",
        "house",
        "image",
        "link",
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
    web_redundant_content: BrowserSession,
) -> None:
    """Tests that the inline error message is dropped from the line's speech and braille."""

    helpers.move_to_top(web_redundant_content)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    # Firefox exposes this ARIA textbox as editable; Chromium does not, so it omits $l.
    assert helpers.capture(web_redundant_content) == (
        ["Status: ", "entry", "x", "invalid entry: Field is required.", " done."],
        helpers.expected_for_browser(
            web_redundant_content,
            [
                helpers.BrailleLine(
                    1,
                    "Status: x invalid: Field is required.  done.",
                    "Status: x invalid: Field is requ",
                    "\x00" * 44,
                )
            ],
            firefox=[
                helpers.BrailleLine(
                    1,
                    "Status: x $l invalid: Field is required.  done.",
                    "Status: x $l invalid: Field is r",
                    "\x00" * 47,
                )
            ],
        ),
    )


@pytest.mark.native_app
def test_line_navigation_drops_useless_image_in_editable(
    web_redundant_content: BrowserSession,
) -> None:
    """Tests that the useless image between the meaningful images is dropped in speech/braille."""

    helpers.move_to_top(web_redundant_content)

    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(web_redundant_content)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(web_redundant_content) == (
        ["Icons", "x ", "Red square", "image", "Blue square", "image", " y"],
        [
            helpers.BrailleLine(
                1,
                "x  $l Red square image Blue square image y $l",
                "x  $l Red square image Blue squa",
                "\x00" * 45,
            )
        ],
    )
