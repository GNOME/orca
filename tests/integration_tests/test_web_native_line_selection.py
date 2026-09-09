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
from .helpers import say_selection
from .web_native_selection_helpers import (
    assert_walks,
    native_selection,
    select_line,
)

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
        ["Fruit Apple Pear", "selected"],
        ["City", "selected"],
        [],
        [],
        ["Name", "selected"],
        ["Age", "selected"],
        ["Ada", "selected"],
        ["36", "selected"],
        ["First link", "selected"],
        ["Second link", "selected"],
        ["Clickable region", "selected"],
        ["Red square", "image", "selected"],
        [
            (
                "This is a sufficiently long paragraph of body text so that it qualifies as a "
                "large object for structural navigation, which"
            ),
            "selected",
        ],
        [
            (
                "targets substantial chunks of readable prose rather than short fragments or "
                "individual controls."
            ),
            "selected",
        ],
        [],
    ]
    expected_unselected = [
        [
            (
                "This is a sufficiently long paragraph of body text so that it qualifies as a "
                "large object for structural navigation, which targets substantial chunks of "
                "readable prose rather than short fragments or individual controls."
            ),
            "unselected",
        ],
        ["Red square", "image", "unselected"],
        ["Clickable region", "unselected"],
        ["Second link", "unselected"],
        ["First link", "unselected"],
        ["36", "unselected"],
        ["Ada", "unselected"],
        ["Age", "unselected"],
        ["Name", "unselected"],
        [],
        [],
        ["City", "unselected"],
        ["Fruit Apple Pear", "unselected"],
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


@pytest.mark.native_app
def test_selected_text_has_no_added_trailing_space(
    web_native_text_selection: NativeAppSession,
) -> None:
    """Tests that joining selected blocks does not append an unselected separator."""

    session = web_native_text_selection

    with native_selection(session):
        select_line(session, keyboard.KEYSYM_DOWN)
        select_line(session, keyboard.KEYSYM_DOWN)
        assert say_selection(session) == [
            "Selected text is:  Structural navigation Intro paragraph."
        ]


@pytest.mark.native_app
def test_selection_by_line_up_then_down(web_native_text_selection: NativeAppSession) -> None:
    """Tests selection by line up and then down."""

    session = web_native_text_selection

    with native_selection(session):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        assert select_line(session, keyboard.KEYSYM_UP) == ["paragraph.", "selected"]
        assert select_line(session, keyboard.KEYSYM_UP) == [
            "ructural navigation Intro",
            "selected",
        ]
        assert say_selection(session) == ["Selected text is:  ructural navigation Intro paragraph."]

        assert select_line(session, keyboard.KEYSYM_DOWN) == [
            "ructural navigation Intro",
            "unselected",
        ]
        assert select_line(session, keyboard.KEYSYM_DOWN) == ["paragraph.", "unselected"]
        assert say_selection(session) == ["No selected text."]

        assert select_line(session, keyboard.KEYSYM_DOWN) == ["Quoted text.", "selected"]
        assert say_selection(session) == ["Selected text is:  Quoted text."]
