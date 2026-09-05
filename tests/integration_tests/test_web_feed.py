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

"""Tests presentation of an ARIA feed and its articles in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_paging_through_feed_articles(web_feed: NativeAppSession) -> None:
    """Tests caret navigation into the feed and paging through its articles."""

    session = web_feed
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Search trails", "button"]
    assert brailled[-1] == BrailleLine(
        1, "Search trails button", "Search trails button", "\x00" * 20
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Feed with 3 articles", "Trail reports", "heading 2"]
    assert brailled[-1] == BrailleLine(1, "Trail reports h2", "Trail reports h2", "\x00" * 16)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["article", "Fell Lane", "heading 3"]
    assert brailled[-1] == BrailleLine(1, "Fell Lane h3", "Fell Lane h3", "\x00" * 12)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Wet underfoot after the bridge."]
    assert brailled[-1] == BrailleLine(
        1, "Wet underfoot after the bridge.", "Wet underfoot after the bridge.", "\x00" * 31
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Mill Path The stile at the top is broken."]
    assert brailled[-1] == BrailleLine(
        1,
        "Mill Path article The stile at the top is broken.",
        "Mill Path article The stile at t",
        "\x00" * 49,
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Quarry Loop Waymarked as far as the gate."]
    assert brailled[-1] == BrailleLine(
        1,
        "Quarry Loop article Waymarked as far as the gate.",
        "Quarry Loop article Waymarked as",
        "\x00" * 49,
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    spoken, brailled = capture(session)
    assert spoken == []
    assert brailled == []

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["Quarry Loop", "heading 3", "Waymarked as far as the gate."]
    assert brailled[-1] == BrailleLine(
        1,
        "Quarry Loop h3 Waymarked as far as the gate.",
        "Quarry Loop h3 Waymarked as far ",
        "\x00" * 44,
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    spoken, brailled = capture(session)
    assert spoken == ["Mill Path The stile at the top is broken."]
    assert brailled[-1] == BrailleLine(
        1,
        "Mill Path article The stile at the top is broken.",
        "Mill Path article The stile at t",
        "\x00" * 49,
    )


@pytest.mark.native_app
def test_moving_out_of_the_feed_in_browse_mode(web_feed: NativeAppSession) -> None:
    """Tests the feed pattern's move-out keys while in browse mode."""

    session = web_feed
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Search trails", "button"]
    assert brailled[-1] == BrailleLine(
        1, "Search trails button", "Search trails button", "\x00" * 20
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == [
        "Trail reports",
        "Feed with 3 articles",
        "Fell Lane Wet underfoot after the bridge.",
    ]
    assert brailled[-1] == BrailleLine(
        1,
        "Fell Lane article Wet underfoot after the bridge.",
        "Fell Lane article Wet underfoot ",
        "\x00" * 49,
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["leaving feed.", "Text after the feed."]
    assert brailled[-1] == BrailleLine(
        21, "Text after the feed.", "Text after the feed.", "\x00" * 20
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["Feed", "heading 1"]
    assert brailled[-1] == BrailleLine(1, "Feed h1", "Feed h1", "\x00" * 7)


@pytest.mark.native_app
def test_moving_after_the_feed_in_focus_mode(web_feed: NativeAppSession) -> None:
    """Tests the key the feed pattern defines for moving past the feed."""

    session = web_feed
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Search trails", "button"]
    assert brailled[-1] == BrailleLine(
        1, "Search trails button", "Search trails button", "\x00" * 20
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == [
        "Trail reports",
        "Feed with 3 articles",
        "Fell Lane Wet underfoot after the bridge.",
    ]
    assert brailled[-1] == BrailleLine(
        1,
        "Fell Lane article Wet underfoot after the bridge.",
        "Fell Lane article Wet underfoot ",
        "\x00" * 49,
    )

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    spoken, brailled = capture(session)
    assert spoken == ["Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["leaving feed.", "Add a report", "button", "Browse mode"]
    assert brailled[-1] == BrailleLine(0, "Browse mode", "Browse mode", "\x00" * 11)


@pytest.mark.native_app
def test_moving_before_the_feed_in_focus_mode(web_feed: NativeAppSession) -> None:
    """Tests the key the feed pattern defines for moving ahead of the feed."""

    session = web_feed
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Search trails", "button"]
    assert brailled[-1] == BrailleLine(
        1, "Search trails button", "Search trails button", "\x00" * 20
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == [
        "Trail reports",
        "Feed with 3 articles",
        "Fell Lane Wet underfoot after the bridge.",
    ]
    assert brailled[-1] == BrailleLine(
        1,
        "Fell Lane article Wet underfoot after the bridge.",
        "Fell Lane article Wet underfoot ",
        "\x00" * 49,
    )

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    spoken, brailled = capture(session)
    assert spoken == ["Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["leaving feed.", "Search trails", "button", "Browse mode"]
    assert brailled[-1] == BrailleLine(0, "Browse mode", "Browse mode", "\x00" * 11)
