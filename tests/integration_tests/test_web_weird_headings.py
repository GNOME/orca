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

"""Tests presentation of headings authors have styled or labeled in unusual ways."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .caret_selection_helpers import NEXT_CHARACTER, PREVIOUS_CHARACTER
from .harness import keyboard
from .helpers import move_to_bottom, move_to_top, reset_web_state, say_selection, speech

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


# Heading navigation lands on each h2 in turn. Headings with presentable text speak it;
# those with none (empty, aria-label-only) fall back to the accessible name. The two
# whose sole content is an empty focusable child (button, div) present that child instead
# of the name -- a separate content-object presentation path, out of scope here.
_HEADINGS = [
    ["2", "Heading one", "heading 2"],
    ["2", "Heading two", "heading 2"],
    ["2", "You can't see me!", "heading 2"],
    ["2", "Heading four", "heading 2"],
    ["2", "Heading five", "heading 2"],
    ["2", "I've got an empty paragraph", "heading 2"],
    ["2", "button heading 2"],
    ["2", "heading 2"],
    ["2", "Image only heading", "heading 2"],
    [
        "2",
        "This\n",
        "is\nwhy",
        "link",
        "\nwe\n",
        "can't",
        "button",
        "\nhave\nnice\nthings\n!\n!\n",
        "heading 2",
    ],
    ["2", "Home", "link heading 2"],
    ["2", "Two empty paragraphs", "heading 2"],
    ["2", "Readable heading", "heading 2"],
]


@pytest.mark.native_app
def test_heading_navigation_across_weird_headings(web_weird_headings: BrowserSession) -> None:
    """Tests heading navigation presents each heading by its text or, if none, its name."""

    session = web_weird_headings
    reset_web_state(session)
    move_to_top(session)
    for expected in _HEADINGS:
        keyboard.tap_key(keyboard.KEYSYM_2)
        assert speech(session) == expected

    for expected in reversed(_HEADINGS[:-1]):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
        assert speech(session) == ["H", *expected[1:]]


@pytest.mark.parametrize(
    ("heading_number", "name", "preceding_character"),
    [
        (3, "You can't see me!", "e"),
        (6, "I've got an empty paragraph", "n"),
        (12, "Two empty paragraphs", "n"),
    ],
)
@pytest.mark.native_app
def test_empty_aria_heading_is_a_single_caret_stop(
    web_weird_headings: BrowserSession,
    heading_number: int,
    name: str,
    preceding_character: str,
) -> None:
    """Tests that a text-less aria-labeled heading is one caret stop with its name and role."""

    session = web_weird_headings
    reset_web_state(session)
    move_to_top(session)
    for _ in range(heading_number):
        keyboard.tap_key(keyboard.KEYSYM_2)
    assert speech(session) == ["2", name, "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert speech(session) == ["O"]
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert speech(session) == [name, "heading 2"]
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert speech(session) == [preceding_character]
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert speech(session) == [name, "heading 2"]


@pytest.mark.native_app
def test_names_with_empty_children_in_links_and_headers(
    web_weird_headings: BrowserSession,
) -> None:
    """Tests names survive empty children in links and both kinds of table header."""

    session = web_weird_headings
    reset_web_state(session)
    move_to_bottom(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_K)
    assert speech(session) == ["K", "Named empty link", "link"]
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_K)
    speech(session)
    keyboard.tap_key(keyboard.KEYSYM_K)
    assert speech(session) == ["k", "Named empty link", "link"]

    move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_T)
    assert speech(session) == [
        "t",
        "table with 2 rows 2 columns",
        "Named column",
        "column header",
    ]
    keyboard.press_chord([keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Named row", "row header", "Row 2, column 1."]
    keyboard.press_chord([keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_UP)
    assert speech(session) == ["Named column", "column header", "Row 1, column 1."]


@pytest.mark.native_app
def test_named_heading_with_text_remains_caret_navigable(
    web_weird_headings: BrowserSession,
) -> None:
    """Tests an author-provided name does not replace a heading's navigable text."""

    session = web_weird_headings
    reset_web_state(session)
    move_to_bottom(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert speech(session) == ["H", "Readable heading", "heading 2"]
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert speech(session) == ["e"]
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert speech(session) == ["R"]


@pytest.mark.parametrize(
    ("heading_number", "selected_text"),
    [(3, "Om"), (6, "Om"), (12, "Om"), (13, "Re")],
)
@pytest.mark.native_app
def test_heading_selection_uses_text_not_the_accessible_name(
    web_weird_headings: BrowserSession, heading_number: int, selected_text: str
) -> None:
    """Tests character selection uses exposed text rather than an author's label."""

    session = web_weird_headings
    reset_web_state(session)
    for _ in range(heading_number):
        keyboard.tap_key(keyboard.KEYSYM_2)
        speech(session)

    for character in selected_text:
        session.orca.select_with_caret_navigator(NEXT_CHARACTER)
        assert speech(session) == [character, "selected"]
    assert say_selection(session) == [f"Selected text is:  {selected_text}"]
    for character in reversed(selected_text):
        session.orca.select_with_caret_navigator(PREVIOUS_CHARACTER)
        assert speech(session) == [character, "unselected"]
    assert say_selection(session) == ["No selected text."]
