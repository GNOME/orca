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
from .helpers import speech
from .version_helpers import chromium_version, requires_version
from .web_native_selection_helpers import (
    LONG_PARAGRAPH,
    USES_DOCUMENT_SELECTION,
    assert_walks,
    native_selection,
    select_word,
)

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@requires_version("Chromium", chromium_version(), 156)
@pytest.mark.skipif(
    not USES_DOCUMENT_SELECTION, reason="Button text selection requires document-selection ranges"
)
@pytest.mark.native_app
@pytest.mark.parametrize(
    "button_number, words",
    [(1, ["Save"]), (2, ["Save", "all", "changes"])],
    ids=["single-word", "multi-word"],
)
def test_word_selection_within_button(
    web_native_text_selection: NativeAppSession,
    button_number: int,
    words: list[str],
) -> None:
    """Tests native word selection within buttons is announced in both directions."""

    session = web_native_text_selection

    with native_selection(session):
        for _ in range(button_number):
            keyboard.tap_key(keyboard.KEYSYM_B)
            speech(session, wait_async=True)

        for word in words:
            assert select_word(session, keyboard.KEYSYM_RIGHT) == [word, "selected"]
        for word in reversed(words):
            assert select_word(session, keyboard.KEYSYM_LEFT) == [word, "unselected"]


@requires_version("Chromium", chromium_version(), 156, when=USES_DOCUMENT_SELECTION)
@pytest.mark.native_app
def test_word_selection_and_unselection(web_native_text_selection: NativeAppSession) -> None:
    """Tests native word selection from the top into the form controls, then back."""

    session = web_native_text_selection
    expected_selected = [
        ["Structural", "selected"],
        ["navigation", "selected"],
        [],
        ["Intro", "selected"],
        ["paragraph", "selected"],
        [".", "selected"],
        [],
        ["Quoted", "selected"],
        ["text", "selected"],
        [".", "selected"],
        [],
        ["Save", "selected"] if USES_DOCUMENT_SELECTION else ["selected"],
        ["selected"],
        [],
        [],
        [],
    ]
    expected_unselected = [
        [],
        [],
        [],
        ["unselected"],
        ["Save", "unselected"] if USES_DOCUMENT_SELECTION else ["unselected"],
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


# Provisional minimum: the build used to verify the collapsed-whitespace selection fix.
@requires_version("Chromium", chromium_version(), 156, 0, 8067, 0, when=USES_DOCUMENT_SELECTION)
@pytest.mark.native_app
def test_word_selection_and_unselection_from_bottom(
    web_native_text_selection: NativeAppSession,
) -> None:
    """Tests native word selection through the final paragraph and preceding button, then back."""

    session = web_native_text_selection
    words = LONG_PARAGRAPH.split()
    expected_selected = [[".", "selected"], ["controls", "selected"]]
    for word in reversed(words[:-1]):
        if word.endswith(","):
            expected_selected.extend([[",", "selected"], [word[:-1], "selected"]])
        else:
            expected_selected.append([word, "selected"])
    if USES_DOCUMENT_SELECTION:
        # Chromium's native Ctrl+Shift+Left gets stuck at the start of "Next slide".
        # This also happens when Orca is not running.
        # Selection and unselection of content before the button are covered by
        # test_word_selection_and_unselection_from_image.
        expected_selected.extend([["selected"], ["slide", "selected"], ["Next", "selected"]])
    expected_unselected = [[*output[:-1], "unselected"] for output in reversed(expected_selected)]

    with native_selection(session):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
        selected = [select_word(session, keyboard.KEYSYM_LEFT) for _ in expected_selected]
        unselected = [select_word(session, keyboard.KEYSYM_RIGHT) for _ in expected_unselected]

    assert_walks(selected, unselected, expected_selected, expected_unselected)


@requires_version("Chromium", chromium_version(), 156, 0, 8067, 0, when=USES_DOCUMENT_SELECTION)
@pytest.mark.native_app
def test_word_selection_and_unselection_from_image(
    web_native_text_selection: NativeAppSession,
) -> None:
    """Tests native word selection through the image, links, and table, then back."""

    session = web_native_text_selection
    expected_selected = [
        ["before", "selected"],
        [],
        ["Red square", "image", "selected"],
        ["region", "selected"],
        ["Clickable", "selected"],
        [],
        ["link", "selected"],
        ["Second", "selected"],
        [],
        ["link", "selected"],
        ["First", "selected"],
        [],
        ["36", "selected"],
        [],
        ["Ada", "selected"],
        [],
        ["Age", "selected"],
        [],
        ["Name", "selected"],
    ]
    expected_unselected = [
        ["Name", "unselected"],
        [],
        ["Age", "unselected"],
        [],
        ["Ada", "unselected"],
        [],
        ["36", "unselected"],
        [],
        ["First", "unselected"],
        ["link", "unselected"],
        [],
        ["Second", "unselected"],
        ["link", "unselected"],
        [],
        ["Clickable", "unselected"],
        ["region", "unselected"],
        [],
        ["Red square", "image", "unselected"],
        [],
        ["before", "unselected"],
    ]
    if not USES_DOCUMENT_SELECTION:
        expected_unselected[-3:-1] = [[], ["Red square", "image", "unselected"]]

    with native_selection(session):
        keyboard.tap_key(keyboard.KEYSYM_G)
        speech(session)
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        speech(session)
        keyboard.tap_key(keyboard.KEYSYM_END)
        speech(session)
        selected = [select_word(session, keyboard.KEYSYM_LEFT) for _ in expected_selected]
        unselected = [select_word(session, keyboard.KEYSYM_RIGHT) for _ in expected_unselected]

    assert_walks(selected, unselected, expected_selected, expected_unselected)
