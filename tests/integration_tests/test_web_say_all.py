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

"""Tests Say All over web content of different shapes, reusing the per-shape pages."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_say_all_lists(web_lists: NativeAppSession) -> None:
    """Tests the utterances Say All speaks for a page of lists, from the top."""

    session = web_lists
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(session) == [
        "Grocery lists",
        "List with 3 items",
        "• ",
        "Apple",
        "• ",
        "Bread",
        "• ",
        "Cheese",
        "leaving list.",
        "List with 3 items",
        "1. ",
        "Wash",
        "2. ",
        "Rinse",
        "3. ",
        "Dry",
        "leaving list.",
        "List with 2 items",
        "• ",
        "Produce",
        "List with 2 items",
        "Nesting level 1",
        "◦ ",
        "Carrot",
        "◦ ",
        "Onion",
        "leaving list.",
        "List with 2 items",
        "• ",
        "Dairy",
    ]


@pytest.mark.native_app
def test_say_all_landmarks(web_landmarks: NativeAppSession) -> None:
    """Tests the utterances Say All speaks for a page of landmarks, from the top."""

    session = web_landmarks
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(session) == [
        "Site banner text.",
        "leaving banner.",
        "navigation",
        "Primary",
        "Home",
        "Help",
        "leaving navigation.",
        "main content",
        "Main content",
        "heading 1",
        "Body paragraph.",
        "leaving main content.",
        "complementary content",
        "Sidebar",
        "Aside text.",
        "leaving complementary content.",
        "Related links",
        "landmark",
        "Region text.",
        "leaving region.",
        "Status updates",
        "landmark",
        "Status text.",
        "leaving region.",
        "information",
        "Footer text.",
    ]
