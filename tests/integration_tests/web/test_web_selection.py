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

"""Tests presentation of selection changes in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers, version_helpers, web_native_selection_helpers
from tests.integration_tests.apps import browser
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_selecting_and_unselecting_an_option(web_selection: BrowserSession) -> None:
    """Tests selecting and unselecting an option."""

    session = web_selection
    helpers.reset_web_state(session)

    # Firefox includes the list bullet in the option's name and text.
    olives = helpers.expected_for_browser(session, "Olives", firefox="• Olives")
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Toppings", "multi-select List with 2 items", olives, "Focus mode"]
    assert brailled[0] == helpers.BrailleLine(1, olives, olives, "\x00" * len(olives))

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["selected"]
    assert brailled[-1] == helpers.BrailleLine(0, "selected", "selected", "\x00" * 8)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["unselected"]
    assert brailled[-1] == helpers.BrailleLine(0, "unselected", "unselected", "\x00" * 10)


@pytest.mark.native_app
@helpers.skip_firefox_caret_tab()
def test_selecting_a_tree_item(web_selection: BrowserSession) -> None:
    """Tests selecting a tree item."""

    session = web_selection
    helpers.reset_web_state(session)

    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        helpers.capture(session)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["selected"]
    assert brailled[-1] == helpers.BrailleLine(0, "selected", "selected", "\x00" * 8)


# Gecko lacks the Document selection API: https://bugzilla.mozilla.org/show_bug.cgi?id=1879510
@pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason="Our Text fallback replaces complete selection boundaries with the button-only range",
    raises=AssertionError,
    strict=True,
)
@version_helpers.requires_browser_version("chromium", 156)
@pytest.mark.skipif(
    not web_native_selection_helpers.USES_DOCUMENT_SELECTION,
    reason="Button text selection requires document-selection ranges",
)
@pytest.mark.native_app
@pytest.mark.parametrize("spaced", [False, True], ids=["unspaced", "spaced"])
def test_character_selection_across_inline_button(
    web_selection: BrowserSession,
    spaced: bool,
) -> None:
    """Tests selection and unselection across both boundaries of an inline button."""

    session = web_selection

    with web_native_selection_helpers.native_selection(session):
        for _ in range(2 if spaced else 1):
            keyboard.tap_key(keyboard.KEYSYM_B)
            helpers.speech(session, wait_async=True)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
        helpers.speech(session)

        text = "start Next slide finish" if spaced else "startNext slidefinish"
        for character in text:
            assert web_native_selection_helpers.select_character(
                session, keyboard.KEYSYM_RIGHT
            ) == [character, "selected"]
        assert helpers.say_selection(session) == [f"Selected text is:  {text}"]
        for character in reversed(text):
            assert web_native_selection_helpers.select_character(session, keyboard.KEYSYM_LEFT) == [
                character,
                "unselected",
            ]
        assert helpers.say_selection(session) == ["No selected text."]


@version_helpers.requires_browser_version("chromium", 156)
@pytest.mark.skipif(
    not web_native_selection_helpers.USES_DOCUMENT_SELECTION,
    reason="Button text selection requires document-selection ranges",
)
@pytest.mark.native_app
@pytest.mark.parametrize("forward", [True, False], ids=["forward", "backward"])
@pytest.mark.parametrize("spaced", [False, True], ids=["unspaced", "spaced"])
def test_selection_containing_whole_inline_button(
    web_selection: BrowserSession,
    forward: bool,
    spaced: bool,
) -> None:
    """Tests selection includes button text when both endpoints are outside the button."""

    session = web_selection

    with web_native_selection_helpers.native_selection(session):
        for _ in range(2 if spaced else 1):
            keyboard.tap_key(keyboard.KEYSYM_B)
            helpers.speech(session, wait_async=True)
        start, end = (
            (keyboard.KEYSYM_HOME, keyboard.KEYSYM_END)
            if forward
            else (keyboard.KEYSYM_END, keyboard.KEYSYM_HOME)
        )
        keyboard.tap_key(start)
        helpers.speech(session)

        text = "start Next slide finish" if spaced else "startNext slidefinish"
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], end)
        assert helpers.speech(session) == [text, "selected"]
        assert helpers.say_selection(session) == [f"Selected text is:  {text}"]

        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], start)
        assert helpers.speech(session) == [text, "unselected"]
        assert helpers.say_selection(session) == ["No selected text."]


# Gecko lacks the Document selection API: https://bugzilla.mozilla.org/show_bug.cgi?id=1879510
@pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason="Our Text fallback replaces complete selection boundaries with the button-only range",
    raises=AssertionError,
    strict=True,
)
@version_helpers.requires_browser_version("chromium", 156)
@pytest.mark.skipif(
    not web_native_selection_helpers.USES_DOCUMENT_SELECTION,
    reason="Button text selection requires document-selection ranges",
)
@pytest.mark.native_app
@pytest.mark.parametrize("spaced", [False, True], ids=["unspaced", "spaced"])
def test_word_selection_across_inline_button(
    web_selection: BrowserSession,
    spaced: bool,
) -> None:
    """Tests word selection across button text and the following parent text."""

    session = web_selection

    with web_native_selection_helpers.native_selection(session):
        for _ in range(2 if spaced else 1):
            keyboard.tap_key(keyboard.KEYSYM_B)
            helpers.speech(session, wait_async=True)
        keyboard.tap_key(keyboard.KEYSYM_END)
        helpers.speech(session)

        words = ["finish", "slide", "Next"] if spaced else ["slidefinish", "Next"]
        for word in words:
            assert web_native_selection_helpers.select_word(session, keyboard.KEYSYM_LEFT) == [
                word,
                "selected",
            ]
