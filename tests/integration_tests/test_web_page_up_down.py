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
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_page_down_then_up(web_page_up_down: NativeAppSession) -> None:
    """Tests that Page Down moves the caret a page down and Page Up returns toward the top."""

    session = web_page_up_down
    helpers.reset_web_state(session)
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    assert helpers.capture(session) == (
        ["Line twenty."],
        [BrailleLine(1, "Line twenty.", "Line twenty.", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    assert helpers.capture(session) == (
        ["Line thirty-nine."],
        [BrailleLine(1, "Line thirty-nine.", "Line thirty-nine.", "\x00" * 17)],
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    assert helpers.capture(session) == (
        ["Line twenty."],
        [BrailleLine(1, "Line twenty.", "Line twenty.", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    assert helpers.capture(session) == (
        ["Line one."],
        [BrailleLine(1, "Line one.", "Line one.", "\x00" * 9)],
    )
