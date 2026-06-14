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

"""Tests navigation of ordered, unordered, and nested lists in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_TOP_TO_BOTTOM = (
    ["List with 3 items", "• Apple"],
    ["• Bread"],
    ["• Cheese"],
    ["leaving list.", "List with 3 items", "1. Wash"],
    ["2. Rinse"],
    ["3. Dry"],
    ["leaving list.", "List with 2 items", "• Produce"],
    ["List with 2 items Nesting level 1", "◦ Carrot"],
    ["◦ Onion"],
    ["leaving list.", "List with 2 items", "• Dairy"],
)


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom(web_lists: NativeAppSession) -> None:
    """Tests Down-arrow caret navigation through the whole page (layout mode on)."""

    session = web_lists
    helpers.reset_web_state(session)

    for expected in _TOP_TO_BOTTOM:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.capture(session)[0] == expected


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom_layout_off(web_lists: NativeAppSession) -> None:
    """Tests the same Down-arrow navigation with layout mode disabled."""

    session = web_lists
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    for expected in _TOP_TO_BOTTOM:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.capture(session)[0] == expected


_BOTTOM_TO_TOP = (
    ["List with 2 items Nesting level 1", "◦ Onion"],
    ["◦ Carrot"],
    ["leaving list.", "• Produce"],
    ["leaving list.", "List with 3 items", "3. Dry"],
    ["2. Rinse"],
    ["1. Wash"],
    ["leaving list.", "List with 3 items", "• Cheese"],
    ["• Bread"],
    ["• Apple"],
    ["leaving list.", "Grocery lists", "heading 1"],
)


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top(web_lists: NativeAppSession) -> None:
    """Tests Up-arrow caret navigation through the whole page (layout mode on)."""

    session = web_lists
    helpers.reset_web_state(session)
    helpers.move_to_bottom(session)

    for expected in _BOTTOM_TO_TOP:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert helpers.capture(session)[0] == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top_layout_off(web_lists: NativeAppSession) -> None:
    """Tests the same Up-arrow navigation with layout mode disabled."""

    session = web_lists
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    helpers.move_to_bottom(session)
    for expected in _BOTTOM_TO_TOP:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert helpers.capture(session)[0] == expected


@pytest.mark.native_app
def test_structural_navigation_by_list(web_lists: NativeAppSession) -> None:
    """Tests structural navigation across unordered, ordered, and nested lists."""

    session = web_lists
    helpers.reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["l", "List with 3 items", "• Apple"],
        [BrailleLine(1, "• Apple", "• Apple", "\x00" * 7)],
    )

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["l", "leaving list.", "List with 3 items", "1. Wash"],
        [BrailleLine(1, "1. Wash", "1. Wash", "\x00" * 7)],
    )

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["l", "leaving list.", "List with 2 items", "• Produce"],
        [BrailleLine(1, "• Produce", "• Produce", "\x00" * 9)],
    )

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["l", "List with 2 items Nesting level 1", "◦ Carrot"],
        [BrailleLine(1, "◦ Carrot", "◦ Carrot", "\x00" * 8)],
    )

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["l", "Wrapping to top.", "leaving list.", "List with 3 items", "• Apple"],
        [
            BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            BrailleLine(1, "• Apple", "• Apple", "\x00" * 7),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        [
            "L",
            "Wrapping to bottom.",
            "leaving list.",
            "List with 2 items Nesting level 1",
            "◦ Carrot",
        ],
        [
            BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            BrailleLine(1, "◦ Carrot", "◦ Carrot", "\x00" * 8),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["L", "leaving list.", "• Produce"],
        [BrailleLine(1, "• Produce", "• Produce", "\x00" * 9)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["L", "leaving list.", "List with 3 items", "1. Wash"],
        [BrailleLine(1, "1. Wash", "1. Wash", "\x00" * 7)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["L", "leaving list.", "List with 3 items", "• Apple"],
        [BrailleLine(1, "• Apple", "• Apple", "\x00" * 7)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_list_item(web_lists: NativeAppSession) -> None:
    """Tests structural navigation item-by-item, including into and out of a nested list."""

    session = web_lists
    helpers.reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "List with 3 items", "• Apple"],
        [BrailleLine(1, "• Apple", "• Apple", "\x00" * 7)],
    )

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "• Bread"],
        [BrailleLine(1, "• Bread", "• Bread", "\x00" * 7)],
    )

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "• Cheese"],
        [BrailleLine(1, "• Cheese", "• Cheese", "\x00" * 8)],
    )

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "leaving list.", "List with 3 items", "1. Wash"],
        [BrailleLine(1, "1. Wash", "1. Wash", "\x00" * 7)],
    )

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "2. Rinse"],
        [BrailleLine(1, "2. Rinse", "2. Rinse", "\x00" * 8)],
    )

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "3. Dry"],
        [BrailleLine(1, "3. Dry", "3. Dry", "\x00" * 6)],
    )

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "leaving list.", "List with 2 items", "• Produce"],
        [BrailleLine(1, "• Produce", "• Produce", "\x00" * 9)],
    )

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "List with 2 items Nesting level 1", "◦ Carrot"],
        [BrailleLine(1, "◦ Carrot", "◦ Carrot", "\x00" * 8)],
    )

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "◦ Onion"],
        [BrailleLine(1, "◦ Onion", "◦ Onion", "\x00" * 7)],
    )

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "leaving list.", "List with 2 items", "• Dairy"],
        [BrailleLine(1, "• Dairy", "• Dairy", "\x00" * 7)],
    )

    keyboard.tap_key(keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["i", "Wrapping to top.", "leaving list.", "List with 3 items", "• Apple"],
        [
            BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            BrailleLine(1, "• Apple", "• Apple", "\x00" * 7),
        ],
    )

    helpers.reset_web_state(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["I", "Wrapping to bottom.", "List with 2 items", "• Dairy"],
        [
            BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            BrailleLine(1, "• Dairy", "• Dairy", "\x00" * 7),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["I", "List with 2 items Nesting level 1", "◦ Onion"],
        [BrailleLine(1, "◦ Onion", "◦ Onion", "\x00" * 7)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["I", "◦ Carrot"],
        [BrailleLine(1, "◦ Carrot", "◦ Carrot", "\x00" * 8)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["I", "leaving list.", "• Produce"],
        [BrailleLine(1, "• Produce", "• Produce", "\x00" * 9)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_I)
    assert helpers.capture(session) == (
        ["I", "leaving list.", "List with 3 items", "3. Dry"],
        [BrailleLine(1, "3. Dry", "3. Dry", "\x00" * 6)],
    )


@pytest.mark.native_app
def test_say_all_lists(web_lists: NativeAppSession) -> None:
    """Tests the utterances Say All speaks for a page of lists, from the top."""

    session = web_lists
    helpers.reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert helpers.speech(session) == [
        "Grocery lists",
        "List with 3 items",
        "• Apple",
        "• Bread",
        "• Cheese",
        "leaving list.",
        "List with 3 items",
        "1. Wash",
        "2. Rinse",
        "3. Dry",
        "leaving list.",
        "List with 2 items",
        "• Produce",
        "List with 2 items",
        "Nesting level 1",
        "◦ Carrot",
        "◦ Onion",
        "leaving list.",
        "List with 2 items",
        "• Dairy",
    ]
