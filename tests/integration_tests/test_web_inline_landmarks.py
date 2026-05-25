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

"""Tests layout-mode line assembly for landmarks and links sharing a visual row."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_line_assembly_inline_landmarks_and_links(web_inline_landmarks: NativeAppSession) -> None:
    """Tests that landmarks and banner/skip links sharing a row stay on separate lines."""

    session = web_inline_landmarks
    move_to_top(session)

    # The banner link and the adjacent non-banner link render side by side, but
    # their differing banner ancestry keeps them on separate lines.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["leaving banner.", "Catalog", "link"]

    # Two ordinary links on one row do group onto a single line, proving the
    # splits here are the landmark/link rules and not blanket per-object lines.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Alpha", "Beta", "link"]

    # Two navigation landmarks side by side are never merged onto one line.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["navigation", "Primary Primary nav"]
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["navigation", "Secondary Secondary nav"]

    # Two links at the same position (the dynamic skip-link pattern) stay separate.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Skip to content", "link"]
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Skip to navigation", "link"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Tail paragraph."]


@pytest.mark.native_app
def test_banner_link_is_its_own_line(web_inline_landmarks: NativeAppSession) -> None:
    """Tests that the banner link forms its own line above its non-banner neighbor."""

    session = web_inline_landmarks
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["leaving banner.", "Catalog", "link"]
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["banner", "Home", "link"]
