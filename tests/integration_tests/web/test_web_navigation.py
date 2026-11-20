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

"""Tests navigation on a basic web page."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


def _boundary(session: BrowserSession, keysym: int, steps: int) -> list[str]:
    """Navigates past the last matching element with wrapping off and returns the message."""

    for _ in range(steps):
        keyboard.tap_key(keysym)
        helpers.speech(session)
    keyboard.tap_key(keysym)
    return helpers.speech(session)


@pytest.mark.native_app
def test_structural_navigation_by_heading(web_basic: BrowserSession) -> None:
    """Tests structural navigation by heading."""

    session = web_basic
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert helpers.capture(session) == (
        ["h", "Fruit list", "heading 2"],
        [helpers.BrailleLine(1, "Fruit list h2", "Fruit list h2", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert helpers.capture(session) == (
        ["h", "Steps", "heading 2"],
        [helpers.BrailleLine(1, "Steps h2", "Steps h2", "\x00" * 8)],
    )

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert helpers.capture(session) == (
        ["h", "Pick a color", "heading 2"],
        [helpers.BrailleLine(1, "Pick a color h2", "Pick a color h2", "\x00" * 15)],
    )

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert helpers.capture(session) == (
        ["h", "Wrapping to top.", "Welcome", "heading 1"],
        [
            helpers.BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            helpers.BrailleLine(1, "Welcome h1", "Welcome h1", "\x00" * 10),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert helpers.capture(session) == (
        ["h", "Fruit list", "heading 2"],
        [helpers.BrailleLine(1, "Fruit list h2", "Fruit list h2", "\x00" * 13)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert helpers.capture(session) == (
        ["H", "Welcome", "heading 1"],
        [helpers.BrailleLine(1, "Welcome h1", "Welcome h1", "\x00" * 10)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert helpers.capture(session) == (
        ["H", "Wrapping to bottom.", "Pick a color", "heading 2"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(1, "Pick a color h2", "Pick a color h2", "\x00" * 15),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert helpers.capture(session) == (
        ["H", "Steps", "heading 2"],
        [helpers.BrailleLine(1, "Steps h2", "Steps h2", "\x00" * 8)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert helpers.capture(session) == (
        ["H", "Fruit list", "heading 2"],
        [helpers.BrailleLine(1, "Fruit list h2", "Fruit list h2", "\x00" * 13)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert helpers.capture(session) == (
        ["H", "Welcome", "heading 1"],
        [helpers.BrailleLine(1, "Welcome h1", "Welcome h1", "\x00" * 10)],
    )


@pytest.mark.native_app
def test_heading_where_am_i(web_basic: BrowserSession) -> None:
    """Tests basic Where Am I on a heading."""

    session = web_basic
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Welcome", "heading 1"]
    assert brailled[-1] == helpers.BrailleLine(1, "Welcome h1", "Welcome h1", "\x00" * 10)


@pytest.mark.native_app
def test_structural_navigation_by_link(web_basic: BrowserSession) -> None:
    """Tests structural navigation by link."""

    session = web_basic
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_K)
    assert helpers.capture(session) == (
        ["k", "First link", "link"],
        [helpers.BrailleLine(1, "First link", "First link", "\xc0" * 10)],
    )

    keyboard.tap_key(keyboard.KEYSYM_K)
    assert helpers.capture(session) == (
        ["k", "second link", "link"],
        [helpers.BrailleLine(1, "second link", "second link", "\xc0" * 11)],
    )

    keyboard.tap_key(keyboard.KEYSYM_K)
    assert helpers.capture(session) == (
        ["k", "Wrapping to top.", "First link", "link"],
        [
            helpers.BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            helpers.BrailleLine(1, "First link", "First link", "\xc0" * 10),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_K)
    assert helpers.capture(session) == (
        ["K", "Wrapping to bottom.", "second link", "link"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(1, "second link", "second link", "\xc0" * 11),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_K)
    assert helpers.capture(session) == (
        ["K", "First link", "link"],
        [helpers.BrailleLine(1, "First link", "First link", "\xc0" * 10)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_K)
    assert helpers.capture(session) == (
        ["K", "Wrapping to bottom.", "second link", "link"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(1, "second link", "second link", "\xc0" * 11),
        ],
    )


@pytest.mark.native_app
def test_structural_navigation_by_list(web_basic: BrowserSession) -> None:
    """Tests structural navigation by list."""

    session = web_basic
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["l", "List with 3 items", "• Apple item"],
        [helpers.BrailleLine(1, "• Apple item", "• Apple item", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["l", "leaving list.", "List with 2 items", "1. First step"],
        [helpers.BrailleLine(1, "1. First step", "1. First step", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["l", "Wrapping to top.", "leaving list.", "List with 3 items", "• Apple item"],
        [
            helpers.BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            helpers.BrailleLine(1, "• Apple item", "• Apple item", "\x00" * 12),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["L", "Wrapping to bottom.", "leaving list.", "List with 2 items", "1. First step"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(1, "1. First step", "1. First step", "\x00" * 13),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["L", "leaving list.", "List with 3 items", "• Apple item"],
        [helpers.BrailleLine(1, "• Apple item", "• Apple item", "\x00" * 12)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    assert helpers.capture(session) == (
        ["L", "Wrapping to bottom.", "leaving list.", "List with 2 items", "1. First step"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(1, "1. First step", "1. First step", "\x00" * 13),
        ],
    )


@pytest.mark.native_app
def test_structural_navigation_by_form_field(web_basic: BrowserSession) -> None:
    """Tests structural navigation by form field."""

    session = web_basic
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "form", "Pick a color", "panel", "Red color", "not selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color & y Red color radio button",
                "& y Red color radio button",
                "\x00" * 39,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Green color", "not selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color & y Green color radio button",
                "& y Green color radio button",
                "\x00" * 41,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Blue color", "not selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color & y Blue color radio button",
                "& y Blue color radio button",
                "\x00" * 40,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Wrapping to top.", "Red color", "not selected radio button"],
        [
            helpers.BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            helpers.BrailleLine(
                1,
                "Pick a color & y Red color radio button",
                "& y Red color radio button",
                "\x00" * 39,
            ),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["F", "Wrapping to bottom.", "Blue color", "not selected radio button"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(
                1,
                "Pick a color & y Blue color radio button",
                "& y Blue color radio button",
                "\x00" * 40,
            ),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["F", "Green color", "not selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color & y Green color radio button",
                "& y Green color radio button",
                "\x00" * 41,
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["F", "Red color", "not selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color & y Red color radio button",
                "& y Red color radio button",
                "\x00" * 39,
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["F", "Wrapping to bottom.", "Blue color", "not selected radio button"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(
                1,
                "Pick a color & y Blue color radio button",
                "& y Blue color radio button",
                "\x00" * 40,
            ),
        ],
    )


@pytest.mark.native_app
def test_caret_navigation(web_basic: BrowserSession) -> None:
    """Tests caret navigation."""

    session = web_basic
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["First link", "link", " and ", "second link", "link", "."],
        [
            helpers.BrailleLine(
                1,
                "First link and second link.",
                "First link and second link.",
                "\xc0" * 10 + "\x00" * 5 + "\xc0" * 11 + "\x00",
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Fruit list", "heading 2"],
        [helpers.BrailleLine(1, "Fruit list h2", "Fruit list h2", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["List with 3 items", "• Apple item"],
        [helpers.BrailleLine(1, "• Apple item", "• Apple item", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["• Banana item"],
        [helpers.BrailleLine(1, "• Banana item", "• Banana item", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["• Cherry item"],
        [helpers.BrailleLine(1, "• Cherry item", "• Cherry item", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["leaving list.", "Steps", "heading 2"],
        [helpers.BrailleLine(1, "Steps h2", "Steps h2", "\x00" * 8)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["List with 3 items", "• Cherry item"],
        [helpers.BrailleLine(1, "• Cherry item", "• Cherry item", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["• Banana item"],
        [helpers.BrailleLine(1, "• Banana item", "• Banana item", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["• Apple item"],
        [helpers.BrailleLine(1, "• Apple item", "• Apple item", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["leaving list.", "Fruit list", "heading 2"],
        [helpers.BrailleLine(1, "Fruit list h2", "Fruit list h2", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["First link", "link", " and ", "second link", "link", "."],
        [
            helpers.BrailleLine(
                1,
                "First link and second link.",
                "First link and second link.",
                "\xc0" * 10 + "\x00" * 5 + "\xc0" * 11 + "\x00",
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["Welcome", "heading 1"],
        [helpers.BrailleLine(1, "Welcome h1", "Welcome h1", "\x00" * 10)],
    )


@pytest.mark.native_app
def test_word_navigation_across_blank_line(web_basic: BrowserSession) -> None:
    """Tests that forward word navigation does not skip the word before a blank line."""

    session = web_basic
    helpers.move_to_top(session)

    # Reach the start of "Hey there\n\nThis is fixed." by line so setup does not depend
    # on browser-specific word boundaries in the preceding radio button labels.
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    for key in (keyboard.KEYSYM_UP, keyboard.KEYSYM_UP, keyboard.KEYSYM_HOME):
        keyboard.tap_key(key)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["Hey "],
        [helpers.BrailleLine(4, "Hey there", "Hey there", "\x00" * 9)],
    )

    # The word before the blank line must be announced, with the caret left on it rather than
    # skipped ahead onto the blank line.
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["there"],
        [helpers.BrailleLine(10, "Hey there", "Hey there", "\x00" * 9)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["This "],
        [helpers.BrailleLine(5, "This is fixed.", "This is fixed.", "\x00" * 14)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["is "],
        [helpers.BrailleLine(8, "This is fixed.", "This is fixed.", "\x00" * 14)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    # Firefox's AT-SPI word boundary includes the period; Chromium's excludes it.
    # TODO: Determine the preferred boundary and report or fix the browser discrepancy.
    assert helpers.capture(session) == helpers.expected_for_browser(
        session,
        (
            ["fixed"],
            [helpers.BrailleLine(14, "This is fixed.", "This is fixed.", "\x00" * 14)],
        ),
        firefox=(
            ["fixed."],
            [helpers.BrailleLine(15, "This is fixed.", "This is fixed.", "\x00" * 14)],
        ),
    )


@pytest.mark.native_app
def test_radio_group_in_focus_mode(web_basic: BrowserSession) -> None:
    """Tests presentation in a radio button group in focus mode."""

    session = web_basic
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "form", "Pick a color", "panel", "Red color", "not selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color & y Red color radio button",
                "& y Red color radio button",
                "\x00" * 39,
            )
        ],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    assert helpers.capture(session) == (
        ["Focus mode"],
        [helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Green color", "selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color & y Red color radio button",
                "& y Red color radio button",
                "\x00" * 39,
            ),
            helpers.BrailleLine(
                1,
                "Pick a color &=y Green color radio button",
                "&=y Green color radio button",
                "\x00" * 41,
            ),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Blue color", "selected radio button"],
        [
            helpers.BrailleLine(
                1,
                "Pick a color &=y Blue color radio button",
                "&=y Blue color radio button",
                "\x00" * 40,
            )
        ],
    )


@pytest.mark.native_app
def test_no_wrapping_when_disabled(web_basic: BrowserSession) -> None:
    """Tests that each navigator reports a boundary instead of wrapping when wrapping is off."""

    session = web_basic
    helpers.reset_web_state(session)
    session.orca.set("StructuralNavigator", "NavigationWraps", False)
    try:
        helpers.move_to_top(session)
        assert _boundary(session, keyboard.KEYSYM_H, 3) == ["h", "No more headings."]
        helpers.move_to_top(session)
        assert _boundary(session, keyboard.KEYSYM_K, 2) == ["k", "No more links."]
        helpers.move_to_top(session)
        assert _boundary(session, keyboard.KEYSYM_L, 2) == ["l", "No more lists."]
        helpers.move_to_top(session)
        assert _boundary(session, keyboard.KEYSYM_F, 3) == ["f", "No more form fields."]
    finally:
        session.orca.set("StructuralNavigator", "NavigationWraps", True)


@pytest.mark.native_app
@pytest.mark.parametrize("click_count", [1, 2], ids=["basic", "detailed"])
def test_where_am_i_preserves_caret_position(web_basic: BrowserSession, click_count: int) -> None:
    """Tests that querying a heading does not move the caret back to its start."""

    session = web_basic
    helpers.move_to_top(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        helpers.capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=click_count)
    spoken, brailled = helpers.capture(session)
    assert "Welcome" in spoken
    assert brailled[-1] == helpers.BrailleLine(3, "Welcome h1", "Welcome h1", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, _brailled = helpers.capture(session)
    assert spoken == ["c"]
