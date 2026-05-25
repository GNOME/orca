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

"""Tests presentation of required, invalid, described, and disclosure field states."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _tab(session: NativeAppSession) -> list[str]:
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    return speech(session)


@pytest.mark.native_app
def test_field_state_announcements_on_focus(web_field_states: NativeAppSession) -> None:
    """Tests that required, invalid, and described states are announced as fields gain focus."""

    session = web_field_states
    reset_web_state(session)

    assert _tab(session) == ["Name", "entry required", "Focus mode"]
    assert _tab(session) == ["Email", "entry", "invalid entry"]
    assert _tab(session) == ["Password", "password text", "At least eight characters."]
    assert _tab(session) == ["More options", "toggle button collapsed"]


@pytest.mark.native_app
def test_disclosure_expand_and_collapse(web_field_states: NativeAppSession) -> None:
    """Tests that activating a disclosure widget announces the expanded and collapsed states."""

    session = web_field_states
    reset_web_state(session)

    for _ in range(4):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    assert speech(session) == ["expanded"]
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    assert speech(session) == ["collapsed"]
