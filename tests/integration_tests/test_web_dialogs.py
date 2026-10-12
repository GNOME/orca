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

from .apps import browser
from .harness import keyboard
from .helpers import expected_for_browser, move_to_bottom, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom(web_dialogs: BrowserSession) -> None:
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
def test_caret_navigation_top_to_bottom_layout_off(web_dialogs: BrowserSession) -> None:
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
def test_caret_navigation_bottom_to_top(web_dialogs: BrowserSession) -> None:
    """Tests Up-arrow caret navigation from the bottom of the page (layout mode on)."""

    session = web_dialogs
    reset_web_state(session)
    move_to_bottom(session)

    for expected in _BOTTOM_TO_TOP:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top_layout_off(web_dialogs: BrowserSession) -> None:
    """Tests the same Up-arrow navigation with layout mode disabled."""

    session = web_dialogs
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    move_to_bottom(session)
    for expected in _BOTTOM_TO_TOP:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_dialog_appearance(web_dialogs: BrowserSession) -> None:
    """Tests that opening a modal dialog announces it and its default button."""

    session = web_dialogs
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Open dialog", "button"]

    # Opening the modal announces its content and lands on the autofocused default button.
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    # Firefox retains a space between the embedded buttons when we expand
    # the dialog text and exclude the buttons; Chromium has no such space.
    assert speech(session) == [
        expected_for_browser(session, "Delete this item?", firefox="Delete this item? "),
        "OK",
        "button",
    ]

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Cancel", "button"]

    # Close the modal so the rest of the page is reachable again.
    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
@pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason="Gecko maps ARIA alert to AT-SPI ALERT instead of NOTIFICATION: "
    "https://www.w3.org/TR/core-aam-1.2/#role-map-alert",
    raises=AssertionError,
    strict=True,
)
def test_alert_announcement(web_dialogs: BrowserSession) -> None:
    """Tests that activating Trigger alert announces the alert text."""

    session = web_dialogs
    reset_web_state(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Open dialog", "button"]

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Trigger alert", "button"]

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session, wait_async=True) == ["Item deleted"]
