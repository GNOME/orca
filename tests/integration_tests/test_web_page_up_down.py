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

"""Browse-mode Page Down / Page Up caret navigation through a tall web document."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_page_down_then_up(web_page_up_down: BrowserSession) -> None:
    """Tests that Page Down moves the caret a page down and Page Up returns toward the top."""

    session = web_page_up_down
    helpers.reset_web_state(session)
    helpers.move_to_top(session)

    # Native Page Down/Up distances differ despite matching viewport and line heights.
    lines = helpers.expected_for_browser(
        session,
        [("Line twenty.", 1), ("Line thirty-nine.", 1), ("Line twenty.", 1), ("Line one.", 1)],
        firefox=[
            ("Line twenty-two.", 1),
            ("Line forty.", 12),
            ("Line nineteen.", 15),
            ("Line one.", 1),
        ],
    )
    keys = [
        keyboard.KEYSYM_PAGE_DOWN,
        keyboard.KEYSYM_PAGE_DOWN,
        keyboard.KEYSYM_PAGE_UP,
        keyboard.KEYSYM_PAGE_UP,
    ]
    for key, (line, cursor) in zip(keys, lines, strict=True):
        keyboard.tap_key(key)
        assert helpers.capture(session) == (
            [line],
            [BrailleLine(cursor, line, line, "\x00" * len(line))],
        )


@pytest.mark.native_app
def test_end_of_file_then_caret_left(web_page_up_down: BrowserSession) -> None:
    """Tests Ctrl+End landing at the true end of the last line, then Left walking back."""

    session = web_page_up_down
    helpers.reset_web_state(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    assert helpers.speech(session) == ["Line forty."]

    for char in "Line forty."[::-1]:
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        assert helpers.speech(session) == [char]
