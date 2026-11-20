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

from tests.integration_tests import helpers, version_helpers, web_native_selection_helpers
from tests.integration_tests.apps import browser
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


@version_helpers.requires_browser_version("chromium", 156)
@pytest.mark.skipif(
    not web_native_selection_helpers.USES_DOCUMENT_SELECTION,
    reason="Button text selection requires document-selection ranges",
)
@pytest.mark.native_app
@pytest.mark.parametrize(
    "button_number, words",
    [(1, ["Save"]), (2, ["Save", "all", "changes"])],
    ids=["single-word", "multi-word"],
)
def test_word_selection_within_button(
    web_native_text_selection: BrowserSession,
    button_number: int,
    words: list[str],
) -> None:
    """Tests native word selection within buttons is announced in both directions."""

    session = web_native_text_selection

    with web_native_selection_helpers.native_selection(session):
        for _ in range(button_number):
            keyboard.tap_key(keyboard.KEYSYM_B)
            helpers.speech(session, wait_async=True)

        for word in words:
            assert web_native_selection_helpers.select_word(session, keyboard.KEYSYM_RIGHT) == [
                word,
                "selected",
            ]
        for word in reversed(words):
            assert web_native_selection_helpers.select_word(session, keyboard.KEYSYM_LEFT) == [
                word,
                "unselected",
            ]


# Gecko's native word selection stalls at the separator even without a screen reader.
# Our Text fallback also falsely announces unselection of text that remains selected.
@pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason=(
        "Gecko's native word selection stalls at the separator; our Text fallback loses boundaries"
    ),
    raises=pytest.fail.Exception,
    strict=True,
)
# Provisional minimum while selection failures are investigated.
@version_helpers.requires_browser_version(
    "chromium", 157, when=web_native_selection_helpers.USES_DOCUMENT_SELECTION
)
@pytest.mark.native_app
def test_word_selection_and_unselection(web_native_text_selection: BrowserSession) -> None:
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
        ["Save", "selected"]
        if web_native_selection_helpers.USES_DOCUMENT_SELECTION
        else ["selected"],
        [] if web_native_selection_helpers.USES_DOCUMENT_SELECTION else ["selected"],
        [],
        [],
        [],
    ]
    expected_unselected = [
        [],
        [],
        [],
        [] if web_native_selection_helpers.USES_DOCUMENT_SELECTION else ["unselected"],
        ["Save", "unselected"]
        if web_native_selection_helpers.USES_DOCUMENT_SELECTION
        else ["unselected"],
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

    with web_native_selection_helpers.native_selection(session):
        selected = [
            web_native_selection_helpers.select_word(session, keyboard.KEYSYM_RIGHT)
            for _ in expected_selected
        ]
        unselected = [
            web_native_selection_helpers.select_word(session, keyboard.KEYSYM_LEFT)
            for _ in expected_unselected
        ]

    web_native_selection_helpers.assert_walks(
        selected, unselected, expected_selected, expected_unselected
    )


# Gecko lacks the Document selection API: https://bugzilla.mozilla.org/show_bug.cgi?id=1879510
@pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason="Our Text fallback replaces complete selection boundaries with the button-only range",
    raises=pytest.fail.Exception,
    strict=True,
)
@version_helpers.requires_browser_version(
    "chromium", 157, when=web_native_selection_helpers.USES_DOCUMENT_SELECTION
)
@pytest.mark.native_app
def test_word_selection_and_unselection_from_bottom(
    web_native_text_selection: BrowserSession,
) -> None:
    """Tests native word selection through the final paragraph and preceding button, then back."""

    session = web_native_text_selection
    words = web_native_selection_helpers.LONG_PARAGRAPH.split()
    expected_selected = [[".", "selected"], ["controls", "selected"]]
    for word in reversed(words[:-1]):
        if word.endswith(","):
            expected_selected.extend([[",", "selected"], [word[:-1], "selected"]])
        else:
            expected_selected.append([word, "selected"])
    if web_native_selection_helpers.USES_DOCUMENT_SELECTION:
        # Chromium's native Ctrl+Shift+Left gets stuck at the start of "Next slide".
        # This also happens when Orca is not running.
        # Selection and unselection of content before the button are covered by
        # test_word_selection_and_unselection_from_image.
        expected_selected.extend([[], ["slide", "selected"], ["Next", "selected"]])
    expected_unselected = [
        [*output[:-1], "unselected"] if output else [] for output in reversed(expected_selected)
    ]

    with web_native_selection_helpers.native_selection(session):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
        selected = [
            web_native_selection_helpers.select_word(session, keyboard.KEYSYM_LEFT)
            for _ in expected_selected
        ]
        unselected = [
            web_native_selection_helpers.select_word(session, keyboard.KEYSYM_RIGHT)
            for _ in expected_unselected
        ]

    web_native_selection_helpers.assert_walks(
        selected, unselected, expected_selected, expected_unselected
    )


# Gecko's native word selection stalls at the separator even without a screen reader.
# Our Text fallback also falsely announces unselection of text that remains selected.
@pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason=(
        "Gecko's native word selection stalls at the separator; our Text fallback loses boundaries"
    ),
    raises=pytest.fail.Exception,
    strict=True,
)
@version_helpers.requires_browser_version(
    "chromium", 157, when=web_native_selection_helpers.USES_DOCUMENT_SELECTION
)
@pytest.mark.native_app
def test_word_selection_and_unselection_from_image(
    web_native_text_selection: BrowserSession,
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
    if not web_native_selection_helpers.USES_DOCUMENT_SELECTION:
        expected_unselected[-3:-1] = [[], ["Red square", "image", "unselected"]]

    with web_native_selection_helpers.native_selection(session):
        keyboard.tap_key(keyboard.KEYSYM_G)
        helpers.speech(session)
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        helpers.speech(session)
        keyboard.tap_key(keyboard.KEYSYM_END)
        helpers.speech(session)
        selected = [
            web_native_selection_helpers.select_word(session, keyboard.KEYSYM_LEFT)
            for _ in expected_selected
        ]
        unselected = [
            web_native_selection_helpers.select_word(session, keyboard.KEYSYM_RIGHT)
            for _ in expected_unselected
        ]

    web_native_selection_helpers.assert_walks(
        selected, unselected, expected_selected, expected_unselected
    )


@pytest.mark.native_app
def test_selection_after_modifier_release(web_native_text_selection: BrowserSession) -> None:
    """A caret event after modifier release does not cancel selection speech."""

    session = web_native_text_selection
    with web_native_selection_helpers.native_selection(session):
        for key in (keyboard.KEYSYM_G, keyboard.KEYSYM_RIGHT, keyboard.KEYSYM_END):
            keyboard.tap_key(key)
            helpers.speech(session)
        # Extend the selection backward across "before" and the image.
        for _ in range(3):
            web_native_selection_helpers.select_word(session, keyboard.KEYSYM_LEFT)

        keyboard.press_key(keyboard.KEYSYM_CONTROL_L)
        keyboard.press_key(keyboard.KEYSYM_SHIFT_L)
        try:
            keyboard.press_key(keyboard.KEYSYM_LEFT)
        finally:
            keyboard.release_key(keyboard.KEYSYM_LEFT)
            keyboard.release_key(keyboard.KEYSYM_SHIFT_L)
            keyboard.release_key(keyboard.KEYSYM_CONTROL_L)
        # Firefox's native selection includes more than Chromium's.
        assert helpers.speech(session, wait_async=True) == helpers.expected_for_browser(
            session, ["region", "selected"], firefox=["Clickable ", "selected"]
        )
