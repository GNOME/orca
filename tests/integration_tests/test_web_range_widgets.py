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

"""Tests sliders, progress bars, and meters in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


# Firefox omits the native range's orientation state; Chromium exposes HORIZONTAL.
def _slider_role(session: BrowserSession) -> str:
    return helpers.expected_for_browser(session, "horizontal slider", firefox="slider")


def _meter_value(session: BrowserSession) -> str:
    # Firefox exposes the native meter's fallback text as its value text.
    # Both browsers expose the same numeric value of 50.
    return helpers.expected_for_browser(session, "50", firefox="50 gigabytes")


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom(web_range_widgets: BrowserSession) -> None:
    """Tests Down-arrow caret navigation through the whole page (layout mode on)."""

    session = web_range_widgets
    helpers.reset_web_state(session)

    # In layout mode the "Volume" label shares the slider's line.
    for expected in (
        ["Volume", _slider_role(session), "2", "50 percent."],
        ["Download"],
        ["30 percent."],
        ["Disk usage", "level bar", _meter_value(session)],
        ["Battery charge", "level bar", "80 percent"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom_layout_off(web_range_widgets: BrowserSession) -> None:
    """Tests the same navigation with layout mode disabled: the label is its own line."""

    session = web_range_widgets
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    # Firefox exposes click actions on labels and spaces between labels and controls.
    # With layout mode disabled, we move the caret to these spaces without speaking.
    for expected in (
        helpers.expected_for_browser(session, ["Volume"], firefox=["Volume", "clickable"]),
        *helpers.expected_for_browser(session, [], firefox=[[]]),
        ["Volume", _slider_role(session), "2", "50 percent."],
        ["Download"],
        ["30 percent."],
        helpers.expected_for_browser(
            session,
            ["Disk usage"],
            firefox=["Disk usage", "clickable"],
        ),
        *helpers.expected_for_browser(session, [], firefox=[[]]),
        ["Disk usage", "level bar", _meter_value(session)],
        ["Battery charge", "level bar", "80 percent"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top(web_range_widgets: BrowserSession) -> None:
    """Tests Up-arrow caret navigation from the bottom of the page (layout mode on)."""

    session = web_range_widgets
    helpers.reset_web_state(session)
    helpers.move_to_bottom(session)

    for expected in (
        ["Disk usage", "level bar", _meter_value(session)],
        ["30 percent."],
        ["Download"],
        ["Volume", _slider_role(session), "2", "50 percent."],
        ["Range widgets", "heading 1"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert helpers.speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top_layout_off(web_range_widgets: BrowserSession) -> None:
    """Tests the same navigation with layout mode disabled: the label is its own line."""

    session = web_range_widgets
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    helpers.move_to_bottom(session)
    # Firefox exposes click actions on labels and spaces between labels and controls.
    # With layout mode disabled, we move the caret to these spaces without speaking.
    for expected in (
        ["Disk usage", "level bar", _meter_value(session)],
        *helpers.expected_for_browser(session, [], firefox=[[]]),
        helpers.expected_for_browser(
            session,
            ["Disk usage"],
            firefox=["Disk usage", "clickable"],
        ),
        ["30 percent."],
        ["Download"],
        ["Volume", _slider_role(session), "2", "50 percent."],
        *helpers.expected_for_browser(session, [], firefox=[[]]),
        helpers.expected_for_browser(session, ["Volume"], firefox=["Volume", "clickable"]),
        ["Range widgets", "heading 1"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert helpers.speech(session) == expected


@pytest.mark.native_app
def test_slider_value_changes_and_progress_bar(web_range_widgets: BrowserSession) -> None:
    """Tests slider value changes within min/max bounds and a progress bar's value."""

    session = web_range_widgets
    helpers.reset_web_state(session)

    # Tab gives the slider DOM focus, which switches Orca to focus mode so the
    # arrow keys change its value rather than moving the caret.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.speech(session) == [
        "Volume",
        _slider_role(session),
        "2",
        "50 percent.",
        "Focus mode",
    ]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.speech(session) == ["3"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.speech(session) == ["4"]

    # Already at the maximum; pressing Up again changes nothing and says nothing.
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.speech(session) == []

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["3"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["2"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["1"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["0"]

    # Already at the minimum; pressing Down again changes nothing and says nothing.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == []

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    assert helpers.speech(session) == ["Browse mode"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["Download"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["30 percent."]


def _where_am_i(session: BrowserSession) -> tuple[list[str], list[BrailleLine]]:
    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    return helpers.capture(session)


@pytest.mark.native_app
def test_where_am_i_on_slider(web_range_widgets: BrowserSession) -> None:
    """Tests Where Am I on a horizontal slider (at its current value of 0)."""

    session = web_range_widgets
    helpers.reset_web_state(session)

    helpers.tab_and_swallow_presentation(session)
    spoken, brailled = _where_am_i(session)
    assert spoken == ["Volume", _slider_role(session), "0", "0 percent."]
    line = helpers.expected_for_browser(
        session,
        "Volume 0 horizontal slider",
        firefox="Volume 0 slider",
    )
    assert brailled[-1] == BrailleLine(1, line, line, "\x00" * len(line))


@pytest.mark.native_app
@pytest.mark.parametrize("click_count", [1, 2], ids=["basic", "detailed"])
def test_where_am_i_on_native_meter(web_range_widgets: BrowserSession, click_count: int) -> None:
    """Tests Where Am I on a native meter."""

    session = web_range_widgets
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    helpers.move_to_bottom(session)
    keyboard.tap_key(keyboard.KEYSYM_UP)
    helpers.capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=click_count)
    spoken, brailled = helpers.capture(session)
    value = helpers.expected_for_browser(session, "50", firefox="50 gigabytes")
    assert spoken == ["Disk usage", "level bar", value]
    line = f"Disk usage {value} level bar"
    assert brailled[-1] == BrailleLine(1, line, line[:32], "\x00" * len(line))


@pytest.mark.native_app
@pytest.mark.parametrize("click_count", [1, 2], ids=["basic", "detailed"])
def test_where_am_i_on_aria_meter(web_range_widgets: BrowserSession, click_count: int) -> None:
    """Tests Where Am I on an ARIA meter with value text."""

    session = web_range_widgets
    helpers.reset_web_state(session)
    helpers.move_to_bottom(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=click_count)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Battery charge", "level bar", "80 percent"]
    line = "Battery charge 80 percent level bar"
    assert brailled[-1] == BrailleLine(1, line, line[:32], "\x00" * len(line))
