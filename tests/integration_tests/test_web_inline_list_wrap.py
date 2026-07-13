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

"""Tests that a wrapped inline list item does not cause its line to be re-read."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


# The last item of this inline "Recently featured" list wraps across two visual lines.
# Arrowing down through the box must reach the line below it without re-reading the list
# line: the second visual line advances to "Line below", it does not rebuild the first.
#
# Chromium gives us the full link as the line at offset even though the text wraps.
_DOWN_LINES = [
    (
        [
            "Recently featured: ",
            "List with 3 items",
            "The Path to Rome",
            "link",
            " ·",
            "Morris Park Aerodrome",
            "link",
            " ·",
            '"',
            "The One Where ",
            "link",
        ],
        "Recently featured: The Path to Rome · Morris Park Aerodrome · "
        '"The One Where Michael Leaves',
    ),
    (["Michael Leaves", '"'], 'The One Where Michael Leaves "'),
    (["leaving list.", "Line below the box."], "Line below the box."),
]


@pytest.mark.native_app
def test_line_down_past_wrapped_inline_list(web_inline_list_wrap: NativeAppSession) -> None:
    """Tests that arrowing down past a wrapped inline list does not re-read the list line."""

    session = web_inline_list_wrap
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    for expected_speech, expected_line in _DOWN_LINES:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, braille = helpers.capture(session)
        assert spoken == expected_speech
        assert [line.full for line in braille] == [expected_line]
