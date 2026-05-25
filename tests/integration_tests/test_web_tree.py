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

"""Tests navigation, level, and expand/collapse of an ARIA tree in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


# Only one caret walk here: walking the ARIA tree leaves its roving-tabindex/DOM focus
# in a state that no keyboard reset clears, so a second caret walk in the same session
# (layout-off, or bottom-to-top) stalls after the first item. The layout-off and
# bottom-to-top paths are covered on the other pages.
@pytest.mark.native_app
def test_caret_navigation_top_to_bottom(web_tree: NativeAppSession) -> None:
    """Tests Down-arrow caret navigation through the whole page (layout mode on)."""

    session = web_tree
    reset_web_state(session)

    for expected in (
        ["Food", "tree", "Fruits", "expanded", "tree level 1"],
        ["Apple", "tree level 2"],
        ["Banana"],
        ["Vegetables", "collapsed", "tree level 1"],
        ["Carrot", "tree level 2"],
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


@pytest.mark.native_app
def test_tree_navigation_level_and_expansion(web_tree: NativeAppSession) -> None:
    """Tests tree item level, expand/collapse, and arrow navigation including a revealed child."""

    session = web_tree
    reset_web_state(session)

    # Tab focuses the tree's first item, an expanded level-1 node.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Fruits", "expanded", "tree level 1", "Focus mode"]

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert speech(session) == ["collapsed"]

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert speech(session) == ["expanded"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Apple", "tree level 2"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Banana"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Vegetables", "collapsed", "tree level 1"]

    # Expanding the collapsed node reveals its child, which Down then reaches.
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert speech(session) == ["expanded"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Carrot", "tree level 2"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Vegetables", "expanded", "tree level 1"]

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert speech(session) == ["collapsed"]
