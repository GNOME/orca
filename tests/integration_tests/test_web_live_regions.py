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

"""Tests announcement of aria-live region updates in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import capture, move_to_bottom, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom(web_live_regions: NativeAppSession) -> None:
    """Tests Down-arrow caret navigation through the page's buttons (layout mode on)."""

    session = web_live_regions
    reset_web_state(session)

    for expected in _TOP_TO_BOTTOM:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom_layout_off(web_live_regions: NativeAppSession) -> None:
    """Tests the same Down-arrow navigation with layout mode disabled."""

    session = web_live_regions
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    for expected in _TOP_TO_BOTTOM:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


_TOP_TO_BOTTOM = (
    ["Save", "button"],
    ["Break", "button"],
    ["Quiet", "button"],
    ["Remove", "button"],
    ["Removable"],
)


_BOTTOM_TO_TOP = (
    ["Remove", "button"],
    ["Quiet", "button"],
    ["Break", "button"],
    ["Save", "button"],
    ["Live regions", "heading 1"],
)


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top(web_live_regions: NativeAppSession) -> None:
    """Tests Up-arrow caret navigation from the bottom of the page (layout mode on)."""

    session = web_live_regions
    reset_web_state(session)
    move_to_bottom(session)

    for expected in _BOTTOM_TO_TOP:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top_layout_off(web_live_regions: NativeAppSession) -> None:
    """Tests the same Up-arrow navigation with layout mode disabled."""

    session = web_live_regions
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    move_to_bottom(session)
    for expected in _BOTTOM_TO_TOP:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_live_region_politeness(web_live_regions: NativeAppSession) -> None:
    """Tests that polite and assertive updates are announced while aria-live=off is silent."""

    session = web_live_regions
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Save", "button"]
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session, wait_async=True) == ["Changes saved"]

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Break", "button"]
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session, wait_async=True) == ["Connection lost"]

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Quiet", "button"]
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == []


@pytest.mark.native_app
def test_live_region_child_removal_is_silent(web_live_regions: NativeAppSession) -> None:
    """Tests that removing a child of a polite live region away from focus is not announced."""

    session = web_live_regions
    reset_web_state(session)

    for _ in range(4):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Remove", "button"]

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert capture(session, wait_async=True) == ([], [])
