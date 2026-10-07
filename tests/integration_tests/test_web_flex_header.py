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

"""Tests line grouping of mixed controls in flex and floated layouts."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


# A flex item is transparent for line grouping, but the visual same-line check still governs: the
# horizontal header (inline logo, flex buttons, inline-block input, block select) is one line,
# while the stacked (flex-direction: column) header reflows to one item per line.
_DOWN_LINES = [
    (
        [
            "banner",
            "Home",
            "image link",
            "Shop by category",
            "button",
            "Search for anything",
            "entry",
            "Camera",
            "button",
            "Category",
            "combo box",
            "All Categories",
            "opens menu",
        ],
        (
            "Home image Shop by category button Search for anything  $l Camera button "
            "Category All Categories combo box"
        ),
    ),
    (["leaving banner.", "banner", "Stacked one", "button"], "Stacked one button"),
    (["Stacked two", "button"], "Stacked two button"),
    (["Stacked three", "button"], "Stacked three button"),
    (["leaving banner.", "After header."], "After header."),
]


@pytest.mark.native_app
def test_line_down_groups_flex_row_but_reflows_stacked_flex(
    web_flex_header: BrowserSession,
) -> None:
    """Tests the horizontal flex header is one line and the stacked flex is one item per line."""

    session = web_flex_header
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    for expected_speech, expected_line in _DOWN_LINES:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, braille = helpers.capture(session)
        assert spoken == expected_speech
        assert [line.full for line in braille] == [expected_line]


@pytest.mark.native_app
@pytest.mark.parametrize(
    "direction", [keyboard.KEYSYM_UP, keyboard.KEYSYM_DOWN], ids=["up", "down"]
)
def test_line_navigation_groups_floated_controls(
    web_flex_header: BrowserSession, direction: int
) -> None:
    """Tests floated links and buttons on one visual line are presented together."""

    session = web_flex_header
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_H)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_UP)
    helpers.capture(session)
    if direction == keyboard.KEYSYM_DOWN:
        for _ in range(2):
            keyboard.tap_key(keyboard.KEYSYM_UP)
            helpers.capture(session)

    keyboard.tap_key(direction)
    spoken, braille = helpers.capture(session)
    assert spoken == [
        "Link 1",
        "link",
        "Button 1",
        "button",
        "Link 2",
        "link",
        "Button 2",
        "button",
    ]
    assert braille[-1].full == "Link 1 Button 1 button Link 2 Button 2 button"


_LIST_LAYOUTS = [
    ("Floated list", True),
    ("Wrapped floated list", True),
    ("Wrapped inline-block list", True),
    ("Wrapped inline list", False),
    ("Wrapped grid list", False),
]


@pytest.mark.native_app
@pytest.mark.parametrize("layout", range(len(_LIST_LAYOUTS)), ids=[x[0] for x in _LIST_LAYOUTS])
@pytest.mark.parametrize(
    "direction", [keyboard.KEYSYM_UP, keyboard.KEYSYM_DOWN], ids=["up", "down"]
)
def test_line_navigation_groups_list_items_by_layout(
    web_flex_header: BrowserSession, layout: int, direction: int
) -> None:
    """Tests list layout controls line grouping, including links in block wrappers."""

    session = web_flex_header
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    heading, grouped = _LIST_LAYOUTS[layout]
    if direction == keyboard.KEYSYM_UP and layout == len(_LIST_LAYOUTS) - 1:
        helpers.move_to_bottom(session)
        helpers.capture(session)
    else:
        heading_count = layout + (2 if direction == keyboard.KEYSYM_UP else 1)
        for _ in range(heading_count):
            keyboard.tap_key(keyboard.KEYSYM_H)
            helpers.capture(session)
        if direction == keyboard.KEYSYM_UP:
            keyboard.tap_key(keyboard.KEYSYM_UP)
            helpers.capture(session)

    names = ["Home", "News", "Contact", "About"]
    lines = [names] if grouped else [[name] for name in names]
    if direction == keyboard.KEYSYM_UP:
        lines.reverse()
    for index, line in enumerate(lines):
        keyboard.tap_key(direction)
        spoken, braille = helpers.capture(session)
        expected = [part for name in line for part in (name, "link")]
        if index == 0:
            expected.insert(0, "List with 4 items")
        assert spoken == expected
        assert braille[-1].full == " ".join(line)

    keyboard.tap_key(direction)
    expected = (
        ["leaving list.", heading, "heading 2"]
        if direction == keyboard.KEYSYM_UP
        else ["leaving list.", "After navigation."]
    )
    assert helpers.speech(session) == expected
