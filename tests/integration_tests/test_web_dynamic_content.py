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

"""Tests Orca's handling of DOM mutations and page reload in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_button_navigation(web_dynamic_content: NativeAppSession) -> None:
    """Tests Tab navigation through the page's four action buttons."""

    session = web_dynamic_content
    reset_web_state(session)

    for expected in (
        ["Add", "button"],
        ["Remove", "button"],
        ["Toggle", "button"],
        ["Reload", "button"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        assert speech(session) == expected


@pytest.mark.native_app
def test_adding_list_items_is_silent(web_dynamic_content: NativeAppSession) -> None:
    """Tests that appending list items while focus is on the button is not announced."""

    session = web_dynamic_content
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Add", "button"]

    # The list is not an ancestor of focus, so Orca refreshes its cache silently.
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == []
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == []


@pytest.mark.native_app
def test_removing_list_items_is_silent(web_dynamic_content: NativeAppSession) -> None:
    """Tests that removing list items while focus is on the button is not announced."""

    session = web_dynamic_content
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Add", "button"]
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == []

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Remove", "button"]
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == []


@pytest.mark.native_app
def test_toggling_panel_is_silent(web_dynamic_content: NativeAppSession) -> None:
    """Tests that showing and hiding a display:none panel is not announced."""

    session = web_dynamic_content
    reset_web_state(session)

    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Toggle", "button"]

    # The panel is added to and removed from the a11y tree; with focus on the
    # button (not inside the panel), Orca refreshes its cache silently.
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == []
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == []


@pytest.mark.native_app
def test_reload_rereads_page(web_dynamic_content: NativeAppSession) -> None:
    """Tests that reloading the page presents its contents anew (busy + load-complete)."""

    session = web_dynamic_content
    reset_web_state(session)

    for _ in range(4):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Reload", "button"]

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session, overall=4.0) == [
        "Dynamic content",
        "heading 1",
        "Add",
        "button",
        "Remove",
        "button",
        "Toggle",
        "button",
        "Reload",
        "button",
    ]
