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

"""Tests that removing the focused option from an ARIA listbox presents the new option."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_focused_option_removed(web_option_removal: NativeAppSession) -> None:
    """Tests that removing the active-descendant option announces the new option."""

    session = web_option_removal
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session) == (
        ["Items", "List with 3 items", "Option A", "Focus mode"],
        [
            BrailleLine(1, "Option A", "Option A", "\x00" * 8),
            BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10),
        ],
    )

    # Delete moves aria-activedescendant to the next option and removes the old one.
    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    assert capture(session, wait_async=True) == (
        ["Option B"],
        [
            BrailleLine(1, "Option A", "Option A", "\x00" * 8),
            BrailleLine(1, "Option B", "Option B", "\x00" * 8),
        ],
    )
