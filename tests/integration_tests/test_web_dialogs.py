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

"""Tests announcement of a modal dialog and an alert in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_bottom, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom(web_dialogs: NativeAppSession) -> None:
    """Tests Down-arrow caret navigation through the page's buttons (layout mode on)."""

    session = web_dialogs
    reset_web_state(session)

    for expected in (
        ["Open dialog", "button"],
        ["Trigger alert", "button"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom_layout_off(web_dialogs: NativeAppSession) -> None:
    """Tests the same Down-arrow navigation with layout mode disabled."""

    session = web_dialogs
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    for expected in (
        ["Open dialog", "button"],
        ["Trigger alert", "button"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


_BOTTOM_TO_TOP = (
    ["Trigger alert", "button"],
    ["Open dialog", "button"],
    ["Dialogs", "heading 1"],
)


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top(web_dialogs: NativeAppSession) -> None:
    """Tests Up-arrow caret navigation from the bottom of the page (layout mode on)."""

    session = web_dialogs
    reset_web_state(session)
    move_to_bottom(session)

    for expected in _BOTTOM_TO_TOP:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top_layout_off(web_dialogs: NativeAppSession) -> None:
    """Tests the same Up-arrow navigation with layout mode disabled."""

    session = web_dialogs
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    move_to_bottom(session)
    for expected in _BOTTOM_TO_TOP:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_dialog_appearance_and_alert(web_dialogs: NativeAppSession) -> None:
    """Tests that opening a modal dialog announces it and its default button, plus an alert."""

    session = web_dialogs
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Open dialog", "button"]

    # Opening the modal announces its content and lands on the autofocused default button.
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == ["Delete this item? ", "OK", "button"]

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Cancel", "button"]

    # Close the modal so the rest of the page is reachable again.
    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    reset_web_state(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Open dialog", "button"]

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Trigger alert", "button"]

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session, wait_async=True) == ["Item deleted"]
