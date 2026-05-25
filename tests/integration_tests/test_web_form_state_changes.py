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

"""Tests presentation of state changes when activating web form controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech, tab

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_state_change_presentation(web_form_fields: NativeAppSession) -> None:
    """Tests that activating each control type announces its new state."""

    session = web_form_fields
    reset_web_state(session)

    # Tab past name, bio, and the editable combo box to reach the Fruit combo box.
    for _ in range(4):
        tab(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Banana"]
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Cherry"]

    tab(session)
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == ["checked"]
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == ["not checked"]

    # Tab past the radio group to reach the Quantity spin button.
    for _ in range(2):
        tab(session)
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["4"]
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["3"]

    # Tab past the Submit button to reach the Mute toggle button.
    for _ in range(2):
        tab(session)
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == ["pressed"]
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == ["not pressed"]

    tab(session)
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == ["pressed"]
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == ["not pressed"]
