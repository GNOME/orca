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

"""Tests value-change announcements for a slider and a progress bar in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_bottom, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom(web_sliders: NativeAppSession) -> None:
    """Tests Down-arrow caret navigation through the whole page (layout mode on)."""

    session = web_sliders
    reset_web_state(session)

    # In layout mode the "Volume" label shares the slider's line.
    for expected in (
        ["Volume", "horizontal slider", "2", "50 percent."],
        ["Download"],
        ["30 percent."],
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom_layout_off(web_sliders: NativeAppSession) -> None:
    """Tests the same navigation with layout mode disabled: the label is its own line."""

    session = web_sliders
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    for expected in (
        ["Volume"],
        ["Volume", "horizontal slider", "2", "50 percent."],
        ["Download"],
        ["30 percent."],
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top(web_sliders: NativeAppSession) -> None:
    """Tests Up-arrow caret navigation from the bottom of the page (layout mode on)."""

    session = web_sliders
    reset_web_state(session)
    move_to_bottom(session)

    for expected in (
        ["Download"],
        ["Volume", "horizontal slider", "2", "50 percent."],
        ["Sliders", "heading 1"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top_layout_off(web_sliders: NativeAppSession) -> None:
    """Tests the same navigation with layout mode disabled: the label is its own line."""

    session = web_sliders
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    move_to_bottom(session)
    for expected in (
        ["Download"],
        ["Volume", "horizontal slider", "2", "50 percent."],
        ["Volume"],
        ["Sliders", "heading 1"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_slider_value_changes_and_progress_bar(web_sliders: NativeAppSession) -> None:
    """Tests slider value changes within min/max bounds and a progress bar's value."""

    session = web_sliders
    reset_web_state(session)

    # Tab gives the slider DOM focus, which switches Orca to focus mode so the
    # arrow keys change its value rather than moving the caret.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Volume", "horizontal slider", "2", "50 percent.", "Focus mode"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["3"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["4"]

    # Already at the maximum; pressing Up again changes nothing and says nothing.
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == []

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["3"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["2"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["1"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["0"]

    # Already at the minimum; pressing Down again changes nothing and says nothing.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == []

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    assert speech(session) == ["Browse mode"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Download"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["30 percent."]
