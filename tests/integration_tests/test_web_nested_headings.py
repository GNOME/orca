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

"""Tests structural navigation out of a heading nested inside another heading."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_backward_navigation_escapes_nested_heading(web_nested_headings: NativeAppSession) -> None:
    """Tests that previous-heading from an inner heading does not get stuck on the outer one."""

    session = web_nested_headings
    move_to_top(session)

    # Forward navigation lands on the outer heading, then the third heading.
    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Inner heading", " outer tail", "heading 2"]
    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Third heading", "heading 2"]

    # Backward from the third heading reaches the inner (level 3) heading.
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert speech(session) == ["H", "Inner heading", "heading 3"]

    # Backward from the inner heading must escape to the heading before the outer
    # one. Without the nested-heading guard the caret would land back on the inner
    # heading and structural navigation would be stuck on the outer heading.
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert speech(session) == ["H", "First heading", "heading 1"]

    # Navigation keeps making progress (wraps to the bottom), proving it is not stuck.
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert speech(session) == ["H", "Wrapping to bottom.", "Third heading", "heading 2"]
