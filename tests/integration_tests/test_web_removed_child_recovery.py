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

"""Tests that Orca recovers the caret when the line it is reading is removed from the DOM."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_navigation_continues_after_focused_line_removed(
    web_removed_child_recovery: NativeAppSession,
) -> None:
    """Tests that navigation stays correct after the line under the caret is removed."""

    session = web_removed_child_recovery
    reset_web_state(session)

    # Arrow right into the doomed paragraph; reaching offset 1 makes the page delete it.
    # The transitional output as it vanishes is not asserted (its timing varies); the
    # two assertions below verify the outcome instead.
    for _ in range(4):
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        capture(session, wait_async=True)
    capture(session, wait_async=True)

    # Down still advances to a real line: Orca recovered the caret.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session, wait_async=True) == (
        ["After the doomed one."],
        [BrailleLine(1, "After the doomed one.", "After the doomed one.", "\x00" * 21)],
    )

    # Up reaches the heading, not "Doomed.": the line really was removed.
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session, wait_async=True) == (
        ["Go.", "heading 1"],
        [BrailleLine(1, "Go. h1", "Go. h1", "\x00" * 6)],
    )
