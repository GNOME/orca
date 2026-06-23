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

"""Tests that a slider updating only aria-valuetext (no aria-valuenow) is presented."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_slider_announces_valuetext_without_valuenow(
    web_pain_slider_no_valuenow: NativeAppSession,
) -> None:
    """Tests that each new aria-valuetext is announced even when aria-valuenow is absent."""

    session = web_pain_slider_no_valuenow
    reset_web_state(session)

    # With no aria-valuenow, Chromium repairs the value to the min/max midpoint ("50 percent").
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == [
        "Pain rating",
        "horizontal slider",
        "No pain",
        "50 percent.",
        "Focus mode",
    ]

    for expected in (
        "Hardly noticeable pain",
        "Somewhat distracting pain",
        "Pain interrupts some activities",
        "Pain prevents daily activities",
    ):
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        assert speech(session) == [expected]

    for expected in ("Pain interrupts some activities", "Somewhat distracting pain"):
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        assert speech(session) == [expected]
