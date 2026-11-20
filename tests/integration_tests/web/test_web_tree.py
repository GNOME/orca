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

"""Tests ARIA tree presentation and keyboard navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_caret_navigation_treats_tree_as_whole(web_tree: BrowserSession) -> None:
    """Tests that ordinary browse mode presents the tree without descending it."""

    session = web_tree
    helpers.reset_web_state(session)

    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.speech(session) == ["Food", "tree"]
        assert not session.orca.get("DocumentPresenter", "InFocusMode")

        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert helpers.speech(session) == ["Tree", "heading 1"]


@pytest.mark.native_app
def test_tree_navigation_level_and_expansion(web_tree: BrowserSession) -> None:
    """Tests tree item level, expand/collapse, and arrow navigation including a revealed child."""

    session = web_tree
    helpers.reset_web_state(session)

    # Firefox includes list bullets in tree item names; Chromium omits them.
    fruits = helpers.expected_for_browser(session, "Fruits", firefox="• Fruits")
    apple = helpers.expected_for_browser(session, "Apple", firefox="◦ Apple")
    banana = helpers.expected_for_browser(session, "Banana", firefox="◦ Banana")
    vegetables = helpers.expected_for_browser(session, "Vegetables", firefox="• Vegetables")
    carrot = helpers.expected_for_browser(session, "Carrot", firefox="◦ Carrot")

    # Tab focuses the tree's first item, an expanded level-1 node.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.speech(session) == [fruits, "expanded", "tree level 1", "Focus mode"]

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.speech(session) == ["collapsed"]

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.speech(session) == ["expanded"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == [apple, "tree level 2"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == [banana]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == [vegetables, "collapsed", "tree level 1"]

    # Expanding the collapsed node reveals its child, which Down then reaches.
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.speech(session) == ["expanded"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == [carrot, "tree level 2"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.speech(session) == [vegetables, "expanded", "tree level 1"]

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.speech(session) == ["collapsed"]


@pytest.mark.native_app
@pytest.mark.parametrize(
    "index, name, state, indicator",
    [
        (0, "Notebook", "not checked", "< >"),
        (1, "Water bottle", "checked", "<x>"),
        (2, "Supplies", "partially checked", "<->"),
    ],
)
def test_checkable_tree_item_navigation(
    web_tree: BrowserSession, index: int, name: str, state: str, indicator: str
) -> None:
    """Presents a tree item's checked state when it gains focus."""

    session = web_tree
    helpers.reset_web_state(session)
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    for _ in range(index):
        helpers.capture(session)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert spoken == [name, state]
    text = f"{indicator} {name} TREE LEVEL 1"
    assert brailled[-1] == helpers.BrailleLine(1, text, text, "\x00" * len(text))


@pytest.mark.native_app
@pytest.mark.parametrize("index, name", [(0, "Notebook"), (1, "Water bottle")])
def test_checkable_tree_item_toggle(web_tree: BrowserSession, index: int, name: str) -> None:
    """Presents both checked states when Space toggles a tree item."""

    session = web_tree
    helpers.reset_web_state(session)
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    helpers.capture(session)
    for _ in range(index):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(session)
    states = [("checked", "<x>"), ("not checked", "< >")]
    if index:
        states.reverse()
    for state, indicator in states:
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        spoken, brailled = helpers.capture(session)
        assert spoken == [state]
        text = f"{indicator} {name} TREE LEVEL 1"
        assert brailled[-1] == helpers.BrailleLine(1, text, text, "\x00" * len(text))


@pytest.mark.native_app
def test_checkable_expandable_tree_item(web_tree: BrowserSession) -> None:
    """Speaks only the changed state while braille retains both tree-item states."""

    session = web_tree
    helpers.reset_web_state(session)
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Bag", "checked", "collapsed"]
    text = "<x> Bag collapsed TREE LEVEL 1"
    assert brailled[-1] == helpers.BrailleLine(1, text, text, "\x00" * len(text))

    for key, state, indicator, expansion in (
        (keyboard.KEYSYM_RIGHT, "expanded", "<x>", "expanded"),
        (keyboard.KEYSYM_SPACE, "not checked", "< >", "expanded"),
        (keyboard.KEYSYM_SPACE, "checked", "<x>", "expanded"),
        (keyboard.KEYSYM_LEFT, "collapsed", "<x>", "collapsed"),
        (keyboard.KEYSYM_SPACE, "not checked", "< >", "collapsed"),
        (keyboard.KEYSYM_RIGHT, "expanded", "< >", "expanded"),
        (keyboard.KEYSYM_SPACE, "checked", "<x>", "expanded"),
        (keyboard.KEYSYM_LEFT, "collapsed", "<x>", "collapsed"),
    ):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        assert spoken == [state]
        text = f"{indicator} Bag {expansion} TREE LEVEL 1"
        assert brailled[-1] == helpers.BrailleLine(1, text, text, "\x00" * len(text))
