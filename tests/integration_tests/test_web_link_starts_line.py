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

"""Tests line navigation through a wrapped paragraph whose link begins a line."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from .orca_fixtures import WebSession


@pytest.mark.web
def test_line_down_through_link_at_start_of_line(web_link_starts_line: WebSession) -> None:
    """Tests that the line whose first item is a link does not include the preceding line."""

    session = web_link_starts_line
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["The bank was the first building in the "],
        [
            BrailleLine(
                1,
                "The bank was the first building in the ",
                "The bank was the first building ",
                "\x00" * 39,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["city to be built in the "],
        [BrailleLine(1, "city to be built in the ", "city to be built in the ", "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["International Style", "link", ". It was commissioned "],
        [
            BrailleLine(
                1,
                "International Style. It was commissioned ",
                "International Style. It was comm",
                "\xc0" * 19 + "\x00" * 22,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["by the owners."],
        [BrailleLine(1, "by the owners.", "by the owners.", "\x00" * 14)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["This is the final line."],
        [BrailleLine(1, "This is the final line.", "This is the final line.", "\x00" * 23)],
    )
