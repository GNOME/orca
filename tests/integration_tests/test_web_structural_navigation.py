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

"""Tests single-key structural navigation to each role beyond the heading/link/list set.

Complements test_web_navigation (which covers heading/link/list/form-field on a
basic page). Here the page holds one of every other navigable role: paragraph,
blockquote, button, checkbox, combo box, entry, radio button, separator, table,
links, clickable, image, and a large object.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_LARGE_OBJECT_TEXT = (
    "This is a sufficiently long paragraph of body text so that it qualifies as a "
    "large object for structural navigation, which targets substantial chunks of "
    "readable prose rather than short fragments or individual controls."
)


def _next(session: NativeAppSession, keysym: int) -> list[str]:
    keyboard.tap_key(keysym)
    return speech(session)


def _previous(session: NativeAppSession, keysym: int) -> list[str]:
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keysym)
    return speech(session)


@pytest.mark.native_app
def test_forward_navigation_by_role(web_structural_navigation: NativeAppSession) -> None:
    """Tests forward single-key navigation landing on each role in document order."""

    session = web_structural_navigation
    move_to_top(session)

    assert _next(session, keyboard.KEYSYM_P) == ["p", "Intro paragraph."]
    assert _next(session, keyboard.KEYSYM_Q) == ["q", "block quote", "Quoted text."]
    assert _next(session, keyboard.KEYSYM_B) == ["b", "leaving blockquote.", "Save", "button"]
    assert _next(session, keyboard.KEYSYM_X) == ["x", "Agree", "check box not checked"]
    assert _next(session, keyboard.KEYSYM_C) == ["c", "Fruit", "combo box", "Apple", "opens menu"]
    assert _next(session, keyboard.KEYSYM_E) == ["e", "City", "entry"]
    assert _next(session, keyboard.KEYSYM_R) == ["r", "Option A", "not selected radio button"]
    assert _next(session, keyboard.KEYSYM_S) == ["s", "separator", "blank"]
    assert _next(session, keyboard.KEYSYM_T) == [
        "t",
        "table with 2 rows 2 columns",
        "Name",
        "column header",
    ]
    assert _next(session, keyboard.KEYSYM_U) == ["u", "leaving table.", "First link", "link"]
    assert _next(session, keyboard.KEYSYM_A) == ["a", "Clickable region", "clickable"]
    assert _next(session, keyboard.KEYSYM_G) == ["g", "Red square", "image"]
    assert _next(session, keyboard.KEYSYM_O) == ["o", _LARGE_OBJECT_TEXT]


@pytest.mark.native_app
def test_absence_message(web_structural_navigation: NativeAppSession) -> None:
    """Tests the absence message for a role the page lacks."""

    session = web_structural_navigation
    move_to_top(session)
    assert _next(session, keyboard.KEYSYM_L) == ["l", "No more lists."]


@pytest.mark.native_app
def test_wrapping(web_structural_navigation: NativeAppSession) -> None:
    """Tests wrap announcements navigating past the only instance of a role, both directions."""

    session = web_structural_navigation

    move_to_top(session)
    assert _next(session, keyboard.KEYSYM_B) == ["b", "Save", "button"]
    assert _next(session, keyboard.KEYSYM_B) == ["b", "Wrapping to top.", "Save"]

    move_to_top(session)
    assert _previous(session, keyboard.KEYSYM_P) == ["P", "Wrapping to bottom.", _LARGE_OBJECT_TEXT]

    move_to_top(session)
    assert _previous(session, keyboard.KEYSYM_U) == [
        "U",
        "Wrapping to bottom.",
        "Second link",
        "link",
    ]


@pytest.mark.native_app
def test_no_wrapping_when_disabled(web_structural_navigation: NativeAppSession) -> None:
    """Tests boundary messages replace wrapping when navigation wrapping is off."""

    session = web_structural_navigation
    session.orca.set("StructuralNavigator", "NavigationWraps", False)
    try:
        move_to_top(session)
        assert _next(session, keyboard.KEYSYM_B) == ["b", "Save", "button"]
        assert _next(session, keyboard.KEYSYM_B) == ["b", "No more buttons."]

        move_to_top(session)
        assert _previous(session, keyboard.KEYSYM_P) == ["P", "No more paragraphs."]
    finally:
        session.orca.set("StructuralNavigator", "NavigationWraps", True)
