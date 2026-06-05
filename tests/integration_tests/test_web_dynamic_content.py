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


@pytest.mark.native_app
def test_reload_presents_page_summary(web_dynamic_content: NativeAppSession) -> None:
    """Tests that the page-summary-on-load setting presents a structural summary on reload."""

    session = web_dynamic_content
    reset_web_state(session)

    # The summary is presented in _on_busy_changed right before the on-load Say All.
    # With Say All enabled (the default) the summary is immediately interrupted by the
    # page re-read, so disable it here to observe the summary itself.
    say_all_before = session.orca.get("DocumentPresenter", "SayAllOnLoad")
    summary_before = session.orca.get("DocumentPresenter", "PageSummaryOnLoad")
    session.orca.set("DocumentPresenter", "SayAllOnLoad", False)
    session.orca.set("DocumentPresenter", "PageSummaryOnLoad", True)
    try:
        for _ in range(4):
            keyboard.tap_key(keyboard.KEYSYM_TAB)
        assert speech(session) == ["Reload", "button"]

        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        assert speech(session, wait_async=True, overall=6.0) == [
            "Orca Web Dynamic Content ready",
            "document web",
            "Page has 1 heading.",
            "Dynamic content",
            "heading 1",
        ]
    finally:
        session.orca.set("DocumentPresenter", "SayAllOnLoad", say_all_before)
        session.orca.set("DocumentPresenter", "PageSummaryOnLoad", summary_before)
