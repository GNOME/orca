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

"""Tests speech for Chromium's native line selection in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .web_native_selection_helpers import assert_walks, native_selection, select_line

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_line_selection_and_unselection(web_native_text_selection: NativeAppSession) -> None:
    """Tests native line selection through varied content, then back to the top."""

    session = web_native_text_selection
    expected_selected = [
        ["Structural navigation", "selected"],
        ["Intro paragraph.", "selected"],
        ["Quoted text.", "selected"],
        ["selected"],
        [],
        ["Fruit", "Apple", "Pear", "selected"],
        ["City"],
        [],
        [],
        ["Name", "selected"],
        [],
        [],
        [],
        ["Age", "36", "First link", "selected"],
        ["Second link", "selected"],
        ["Clickable region", "selected"],
        [],
        [
            "This is a sufficiently long paragraph of body text so that it qualifies as a "
            "large object for structural navigation, which targets substantial chunks of "
            "readable ",
            "selected",
        ],
        ["prose rather than short fragments or individual controls.", "selected"],
        [],
    ]
    expected_unselected = [
        [
            "This is a sufficiently long paragraph of body text so that it qualifies as a "
            "large object for structural navigation, which targets substantial chunks of "
            "readable prose rather than short fragments or individual controls.",
            "unselected",
        ],
        [],
        ["Clickable region", "unselected"],
        ["Second link", "unselected"],
        ["First link", "unselected"],
        [],
        [],
        [],
        [],
        [],
        [" "],
        ["City"],
        ["Fruit", "Apple", "Pear", "unselected"],
        [],
        ["unselected"],
        ["Quoted text.", "unselected"],
        ["Intro paragraph.", "unselected"],
        ["Structural navigation", "unselected"],
        [],
        [],
    ]

    with native_selection(session):
        selected = [select_line(session, keyboard.KEYSYM_DOWN) for _ in expected_selected]
        unselected = [select_line(session, keyboard.KEYSYM_UP) for _ in expected_unselected]

    assert_walks(selected, unselected, expected_selected, expected_unselected)
