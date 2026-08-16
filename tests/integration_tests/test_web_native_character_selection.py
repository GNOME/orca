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

"""Tests speech for Chromium's native character selection in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .web_native_selection_helpers import (
    LONG_PARAGRAPH,
    assert_walks,
    native_selection,
    say_selection,
    select_character,
)

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _selection_expectations() -> tuple[list[list[str]], list[list[str]]]:
    """Returns expected speech for a full character walk down and back up the page."""

    selected: list[list[str]] = []

    def add_text(text: str) -> None:
        selected.extend([[char, "selected"] for char in text])

    add_text("Structural navigation")
    selected.append([])
    add_text("Intro paragraph.")
    selected.append([])
    add_text("Quoted text.")
    selected.extend([[], []])
    selected.extend([["selected"]] * 4)
    second_state_only_index = len(selected)
    selected.append([])
    selected.extend([[]] * 6)
    add_text("Fruit")
    selected.append([])
    combo_index = len(selected)
    selected.append(["Apple Pear", "selected"])
    selected.append([])
    add_text("City")
    selected.extend([[], []])
    selected.extend([[]] * 14)
    add_text("Name")
    selected.append([])
    add_text("Age")
    selected.append([])
    add_text("Ada")
    selected.append([])
    add_text("36")
    selected.extend([[], []])
    add_text("First link")
    selected.append([])
    add_text("Second link")
    selected.append([])
    add_text("Clickable region")
    selected.extend([[], ["Red square", "image", "selected"], []])
    add_text(LONG_PARAGRAPH)

    unselected = []
    for output in reversed(selected):
        if output:
            unselected.append([*output[:-1], "unselected"])
        else:
            unselected.append([])

    count = len(selected)
    unselected[count - 1 - combo_index] = []
    unselected[count - combo_index] = ["Apple Pear", "unselected"]
    unselected[count - 1 - second_state_only_index] = []

    return selected, unselected


@pytest.mark.native_app
def test_character_selection_and_unselection(
    web_native_text_selection: NativeAppSession,
) -> None:
    """Tests native character selection from the top to bottom, then back to the top."""

    session = web_native_text_selection
    expected_selected, expected_unselected = _selection_expectations()

    with native_selection(session):
        selected = [select_character(session, keyboard.KEYSYM_RIGHT) for _ in expected_selected]
        unselected = [select_character(session, keyboard.KEYSYM_LEFT) for _ in expected_unselected]

    assert_walks(selected, unselected, expected_selected, expected_unselected)


@pytest.mark.native_app
def test_selection_to_the_right_after_line_navigation(
    web_native_text_selection: NativeAppSession,
) -> None:
    """Tests selection to the right after line navigation."""

    session = web_native_text_selection

    with native_selection(session):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        assert select_character(session, keyboard.KEYSYM_RIGHT) == ["Q", "selected"]
        assert say_selection(session) == ["Selected text is:  Q"]


@pytest.mark.native_app
def test_selection_to_the_right_after_structural_navigation(
    web_native_text_selection: NativeAppSession,
) -> None:
    """Tests selection to the right after structural navigation."""

    session = web_native_text_selection

    with native_selection(session):
        keyboard.tap_key(ord("q"))
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        assert select_character(session, keyboard.KEYSYM_RIGHT) == ["Q", "selected"]
        assert say_selection(session) == ["Selected text is:  Q"]
