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

"""Line navigation across an inline link that wraps across a visual line boundary."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_line_navigation_across_wrapped_link(web_wrapped_link: NativeAppSession) -> None:
    """Tests line down then up across a two-word link split over a visual line boundary."""

    session = web_wrapped_link
    helpers.reset_web_state(session)
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["The group included star ", "Kelly ", "link"],
        [
            helpers.BrailleLine(
                1,
                "The group included star Kelly Rowland",
                "The group included star Kelly Ro",
                "\x00" * 24 + "\xc0" * 13,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Rowland", " plus others here."],
        [
            helpers.BrailleLine(
                1,
                "Kelly Rowland plus others here.",
                "Kelly Rowland plus others here.",
                "\xc0" * 13 + "\x00" * 18,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["This is the final line."],
        [helpers.BrailleLine(1, "This is the final line.", "This is the final line.", "\x00" * 23)],
    )

    # Setting the caret into the wrapped link makes Chromium report its whole text as one line.
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["Kelly Rowland", "link", " plus others here."],
        [
            helpers.BrailleLine(
                1,
                "Kelly Rowland plus others here.",
                "Kelly Rowland plus others here.",
                "\xc0" * 13 + "\x00" * 18,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["The group included star ", "Kelly Rowland", "link"],
        [
            helpers.BrailleLine(
                1,
                "The group included star Kelly Rowland",
                "The group included star Kelly Ro",
                "\x00" * 24 + "\xc0" * 13,
            )
        ],
    )
