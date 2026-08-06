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

"""Tests speech for Chromium's native word selection in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .web_native_selection_helpers import (
    LONG_PARAGRAPH,
    assert_walks,
    native_selection,
    select_word,
)

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_word_selection_and_unselection(web_native_text_selection: NativeAppSession) -> None:
    """Tests native word selection from the top into the form controls, then back."""

    session = web_native_text_selection
    expected_selected = [
        ["Structural", "selected"],
        [" navigation", "selected"],
        ["Intro "],
        ["Intro", "selected"],
        [" paragraph", "selected"],
        [".", "selected"],
        ["Quoted "],
        ["Quoted", "selected"],
        [" text", "selected"],
        [".", "selected"],
        [],
        ["selected"],
        ["blank"],
        [],
        [],
        ["Fruit"],
    ]
    expected_unselected = [
        [],
        [],
        ["blank"],
        [],
        ["Text unselected."],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    ]

    with native_selection(session):
        selected = [select_word(session, keyboard.KEYSYM_RIGHT) for _ in expected_selected]
        unselected = [select_word(session, keyboard.KEYSYM_LEFT) for _ in expected_unselected]

    assert_walks(selected, unselected, expected_selected, expected_unselected)


@pytest.mark.native_app
def test_word_selection_and_unselection_from_bottom(
    web_native_text_selection: NativeAppSession,
) -> None:
    """Tests native word selection from the bottom toward the form controls, then back."""

    session = web_native_text_selection
    words = LONG_PARAGRAPH.split()
    expected_selected = [[".", "selected"], ["controls", "selected"]]
    for word in reversed(words[:-1]):
        if word.endswith(","):
            expected_selected.extend([[", ", "selected"], [word[:-1], "selected"]])
        else:
            expected_selected.append([f"{word} ", "selected"])
    expected_selected.extend(
        [
            [],
            [],
            [],
            ["Clickable ", "selected"],
            ["link"],
            ["link", "selected"],
            ["Second ", "selected"],
            ["link"],
            ["link", "selected"],
            ["First ", "selected"],
            ["36"],
            ["36", "selected"],
            ["Ada"],
            ["Ada", "selected"],
            ["Age"],
            ["Age", "selected"],
            ["Name"],
            ["Name", "selected"],
        ]
    )
    expected_unselected = [
        ["Text unselected.", "Name"],
        [],
        ["Text unselected.", "Age"],
        [],
        ["Text unselected.", "Ada"],
        [],
        ["Text unselected.", "36"],
        [],
        ["First", "unselected"],
        ["Text unselected.", "link"],
        [],
        ["Second", "unselected"],
        ["Text unselected.", "link"],
        [],
        ["Clickable", "unselected"],
        ["Text unselected.", "region"],
        [],
        [],
        [],
        ["This", "unselected"],
    ]
    for word in words[1:-1]:
        if word.endswith(","):
            expected_unselected.extend([[f" {word[:-1]}", "unselected"], [",", "unselected"]])
        else:
            expected_unselected.append([f" {word}", "unselected"])

    with native_selection(session):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
        selected = [select_word(session, keyboard.KEYSYM_LEFT) for _ in expected_selected]
        unselected = [select_word(session, keyboard.KEYSYM_RIGHT) for _ in expected_unselected]

    assert_walks(selected, unselected, expected_selected, expected_unselected)
