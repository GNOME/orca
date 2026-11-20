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

"""Tests text selection in web content when Orca controls the caret."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import caret_selection_helpers, helpers, version_helpers
from tests.integration_tests.apps import browser
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession

_HEADING = "Structural navigation h1"
_PARAGRAPH = "Intro paragraph."
_QUOTE = "Quoted text. block quote"


@version_helpers.requires_browser_version("chromium", 153)
@pytest.mark.native_app
def test_selection_by_character(web_structural_navigation: BrowserSession) -> None:
    """Tests selection by character."""

    session = web_structural_navigation
    helpers.reset_web_state(session)

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.NEXT_CHARACTER
    )
    assert spoken == ["S", "selected"]
    assert brailled == helpers.BrailleLine(2, _HEADING, _HEADING, "\xc0" + "\x00" * 23)

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.NEXT_CHARACTER
    )
    assert spoken == ["t", "selected"]
    assert brailled == helpers.BrailleLine(3, _HEADING, _HEADING, "\xc0" * 2 + "\x00" * 22)

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.NEXT_CHARACTER
    )
    assert spoken == ["r", "selected"]
    assert brailled == helpers.BrailleLine(4, _HEADING, _HEADING, "\xc0" * 3 + "\x00" * 21)
    assert helpers.say_selection(session) == ["Selected text is:  Str"]

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.PREVIOUS_CHARACTER
    )
    assert spoken == ["r", "unselected"]
    assert brailled == helpers.BrailleLine(3, _HEADING, _HEADING, "\xc0" * 2 + "\x00" * 22)

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.PREVIOUS_CHARACTER
    )
    assert spoken == ["t", "unselected"]
    assert brailled == helpers.BrailleLine(2, _HEADING, _HEADING, "\xc0" + "\x00" * 23)
    assert helpers.say_selection(session) == ["Selected text is:  S"]

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.PREVIOUS_CHARACTER
    )
    assert spoken == ["S", "unselected"]
    assert brailled == helpers.BrailleLine(1, _HEADING, _HEADING, "\x00" * 24)
    assert helpers.say_selection(session) == ["No selected text."]


@version_helpers.requires_browser_version("chromium", 153)
@pytest.mark.native_app
def test_selection_by_word(web_structural_navigation: BrowserSession) -> None:
    """Tests selection by word."""

    session = web_structural_navigation
    helpers.reset_web_state(session)

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_WORD)
    assert spoken == ["Structural", "selected"]
    assert brailled == helpers.BrailleLine(11, _HEADING, _HEADING, "\xc0" * 10 + "\x00" * 14)

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_WORD)
    assert spoken == ["navigation", "selected"]
    assert brailled == helpers.BrailleLine(22, _HEADING, _HEADING, "\xc0" * 21 + "\x00" * 3)
    assert helpers.say_selection(session) == ["Selected text is:  Structural navigation"]

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.PREVIOUS_WORD
    )
    assert spoken == ["navigation", "unselected"]
    assert brailled == helpers.BrailleLine(12, _HEADING, _HEADING, "\xc0" * 11 + "\x00" * 13)
    assert helpers.say_selection(session) == ["Selected text is:  Structural "]


@version_helpers.requires_browser_version("chromium", 153)
@pytest.mark.native_app
def test_selection_to_the_line_boundaries(web_structural_navigation: BrowserSession) -> None:
    """Tests selection to the end and to the start of the line."""

    session = web_structural_navigation
    helpers.reset_web_state(session)

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_WORD)
    assert spoken == ["Structural", "selected"]
    assert brailled == helpers.BrailleLine(11, _HEADING, _HEADING, "\xc0" * 10 + "\x00" * 14)

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.END_OF_LINE)
    assert spoken == ["navigation", "selected"]
    assert brailled == helpers.BrailleLine(22, _HEADING, _HEADING, "\xc0" * 21 + "\x00" * 3)
    assert helpers.say_selection(session) == ["Selected text is:  Structural navigation"]

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.START_OF_LINE
    )
    assert spoken == ["Structural navigation", "unselected"]
    assert brailled == helpers.BrailleLine(1, _HEADING, _HEADING, "\x00" * 24)
    assert helpers.say_selection(session) == ["No selected text."]


@version_helpers.requires_browser_version("chromium", 153)
@pytest.mark.native_app
def test_selection_in_a_paragraph(web_structural_navigation: BrowserSession) -> None:
    """Tests selection in a paragraph below the heading."""

    session = web_structural_navigation
    helpers.reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert spoken == [_PARAGRAPH]
    assert brailled[-1] == helpers.BrailleLine(1, _PARAGRAPH, _PARAGRAPH, "\x00" * 16)

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.NEXT_CHARACTER
    )
    assert spoken == ["I", "selected"]
    assert brailled == helpers.BrailleLine(2, _PARAGRAPH, _PARAGRAPH, "\xc0" + "\x00" * 15)

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.NEXT_CHARACTER
    )
    assert spoken == ["n", "selected"]
    assert brailled == helpers.BrailleLine(3, _PARAGRAPH, _PARAGRAPH, "\xc0" * 2 + "\x00" * 14)
    assert helpers.say_selection(session) == ["Selected text is:  In"]

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.END_OF_LINE)
    assert spoken == ["tro paragraph.", "selected"]
    assert brailled == helpers.BrailleLine(17, _PARAGRAPH, _PARAGRAPH, "\xc0" * 16)
    assert helpers.say_selection(session) == ["Selected text is:  Intro paragraph."]


@version_helpers.requires_browser_version("chromium", 153)
@pytest.mark.native_app
def test_selection_retains_anchor_at_paragraph_start(
    web_structural_navigation: BrowserSession,
) -> None:
    """Tests that an empty selection in the new focus does not discard the anchor."""

    session = web_structural_navigation
    helpers.reset_web_state(session)

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_LINE)
    assert spoken == ["Structural navigation", "selected"]
    assert brailled == helpers.BrailleLine(1, _PARAGRAPH, _PARAGRAPH, "\x00" * 16)

    # The paragraph has no selected text, but the heading must remain selected.
    for _ in range(2):
        session.orca.select_with_caret_navigator(caret_selection_helpers.START_OF_LINE)
        assert helpers.capture(session)[0] == []
    assert helpers.say_selection(session) == ["Selected text is:  Structural navigation"]

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_WORD)
    assert spoken == ["Intro", "selected"]
    assert brailled == helpers.BrailleLine(6, _PARAGRAPH, _PARAGRAPH, "\xc0" * 5 + "\x00" * 11)
    assert helpers.say_selection(session) == ["Selected text is:  Structural navigation Intro"]


@version_helpers.requires_browser_version("chromium", 153)
@pytest.mark.native_app
@pytest.mark.parametrize(
    "reverse",
    [
        pytest.param(False, id="forward"),
        pytest.param(
            True,
            id="reverse",
            marks=pytest.mark.xfail(
                browser.selected_browser() == "firefox",
                reason=(
                    "Firefox reads object-local selection indices "
                    "but modifies document-wide indices"
                ),
                raises=AssertionError,
                strict=True,
            ),
        ),
    ],
)
def test_selection_across_objects(web_structural_navigation: BrowserSession, reverse: bool) -> None:
    """Tests selection which spans more than one text object."""

    session = web_structural_navigation
    helpers.reset_web_state(session)

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.END_OF_LINE)
    assert spoken == ["Structural navigation", "selected"]
    assert brailled == helpers.BrailleLine(22, _HEADING, _HEADING, "\xc0" * 21 + "\x00" * 3)

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_LINE)
    assert spoken == [_PARAGRAPH, "selected"]
    assert brailled == helpers.BrailleLine(17, _PARAGRAPH, _PARAGRAPH, "\xc0" * 16)
    assert helpers.say_selection(session) == [
        "Selected text is:  Structural navigation Intro paragraph."
    ]

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_LINE)
    assert spoken == ["Quoted text.", "selected"]
    assert brailled == helpers.BrailleLine(13, _QUOTE, _QUOTE, "\xc0" * 12 + "\x00" * 12)
    assert helpers.say_selection(session) == [
        "Selected text is:  Structural navigation Intro paragraph. Quoted text."
    ]

    if not reverse:
        return

    spoken, brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.PREVIOUS_LINE
    )
    assert spoken == ["Quoted text.", "unselected"]
    assert brailled == helpers.BrailleLine(1, _QUOTE, _QUOTE, "\x00" * 24)
    assert helpers.say_selection(session) == [
        "Selected text is:  Structural navigation Intro paragraph."
    ]

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_WORD)
    assert spoken == ["Quoted", "selected"]
    assert brailled == helpers.BrailleLine(7, _QUOTE, _QUOTE, "\xc0" * 6 + "\x00" * 18)
    assert helpers.say_selection(session) == [
        "Selected text is:  Structural navigation Intro paragraph. Quoted"
    ]


@version_helpers.requires_browser_version("chromium", 153)
@pytest.mark.native_app
def test_selection_without_notifying_the_user(
    web_structural_navigation: BrowserSession,
) -> None:
    """Tests selection which the caller asked Orca not to present."""

    session = web_structural_navigation
    helpers.reset_web_state(session)

    spoken, brailled = caret_selection_helpers.select_without_notifying(
        session, caret_selection_helpers.NEXT_WORD
    )
    assert spoken == []
    assert brailled[-1] == helpers.BrailleLine(11, _HEADING, _HEADING, "\xc0" * 10 + "\x00" * 14)
    assert helpers.say_selection(session) == ["Selected text is:  Structural"]

    spoken, brailled = caret_selection_helpers.select_without_notifying(
        session, caret_selection_helpers.NEXT_WORD
    )
    assert spoken == []
    assert brailled[-1] == helpers.BrailleLine(22, _HEADING, _HEADING, "\xc0" * 21 + "\x00" * 3)
    assert helpers.say_selection(session) == ["Selected text is:  Structural navigation"]

    spoken, brailled = caret_selection_helpers.select_without_notifying(
        session, caret_selection_helpers.START_OF_LINE
    )
    assert spoken == []
    assert brailled[-1] == helpers.BrailleLine(1, _HEADING, _HEADING, "\x00" * 24)
    assert helpers.say_selection(session) == ["No selected text."]


@version_helpers.requires_browser_version("chromium", 153)
@pytest.mark.native_app
def test_selection_removed_by_caret_navigation(
    web_structural_navigation: BrowserSession,
) -> None:
    """Tests removing a selection with the caret navigation commands."""

    session = web_structural_navigation
    helpers.reset_web_state(session)

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_WORD)
    assert spoken == ["Structural", "selected"]
    assert brailled == helpers.BrailleLine(11, _HEADING, _HEADING, "\xc0" * 10 + "\x00" * 14)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Text unselected.", " "]
    assert brailled[-1] == helpers.BrailleLine(11, _HEADING, _HEADING, "\x00" * 24)
    assert helpers.say_selection(session) == ["No selected text."]

    spoken, brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_WORD)
    assert spoken == ["navigation", "selected"]
    assert brailled == helpers.BrailleLine(
        22, _HEADING, _HEADING, "\x00" * 10 + "\xc0" * 11 + "\x00" * 3
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Text unselected.", _PARAGRAPH]
    assert brailled[-1] == helpers.BrailleLine(1, _PARAGRAPH, _PARAGRAPH, "\x00" * 16)
    assert helpers.say_selection(session) == ["No selected text."]

    helpers.reset_web_state(session)
    spoken, _brailled = caret_selection_helpers.select(session, caret_selection_helpers.NEXT_WORD)
    assert spoken == ["Structural", "selected"]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    spoken, _brailled = helpers.capture(session)
    assert spoken == ["Text unselected.", "navigation"]
    assert helpers.say_selection(session) == ["No selected text."]

    spoken, _brailled = caret_selection_helpers.select(
        session, caret_selection_helpers.PREVIOUS_WORD
    )
    assert spoken == ["navigation", "selected"]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
    spoken, _brailled = helpers.capture(session)
    assert spoken == ["Text unselected.", "Structural "]
    assert helpers.say_selection(session) == ["No selected text."]
