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

"""Tests presentation of widgets whose container shares their name."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_DETAILS_LINE = "OrcaRedundantNames application frame panel Details button"
_OPTIONS_LINE = "OrcaRedundantNames application frame Options panel Save button"
_WEATHER_LINE = "OrcaRedundantNames application frame Weather button"


@pytest.mark.native_app
def test_container_name_matching_focused_widget(gtk3_redundant_names: NativeAppSession) -> None:
    """Tests that a container is not announced by name when its child has that name."""

    session = gtk3_redundant_names

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert capture(session) == (
        ["Details button"],
        [BrailleLine(1, _DETAILS_LINE, "Details button", "\x00" * 57)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert capture(session) == (
        ["panel", "Details button"],
        [
            BrailleLine(1, _DETAILS_LINE, "Details button", "\x00" * 57),
            BrailleLine(1, _DETAILS_LINE, "Details button", "\x00" * 57),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session) == (
        ["Options panel", "Save button"],
        [BrailleLine(1, _OPTIONS_LINE, "Save button", "\x00" * 62)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert capture(session) == (
        ["Options panel", "Save button"],
        [
            BrailleLine(1, _OPTIONS_LINE, "Save button", "\x00" * 62),
            BrailleLine(1, _OPTIONS_LINE, "Save button", "\x00" * 62),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session) == (
        ["Weather button"],
        [BrailleLine(1, _WEATHER_LINE, "Weather button", "\x00" * 51)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert capture(session) == (
        ["Weather button"],
        [
            BrailleLine(1, _WEATHER_LINE, "Weather button", "\x00" * 51),
            BrailleLine(1, _WEATHER_LINE, "Weather button", "\x00" * 51),
        ],
    )
