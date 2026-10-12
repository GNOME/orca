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

"""Tests caret and word navigation within and across form controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .apps import browser
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


def _exit_focus_mode(session: BrowserSession) -> None:
    """Toggles from focus mode back to browse mode so the next test starts clean."""

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _capture_final(session: BrowserSession) -> tuple[list[str], helpers.BrailleLine]:
    """Returns speech and the settled braille line."""

    spoken, brailled = helpers.capture(session)
    return spoken, brailled[-1]


@pytest.mark.native_app
def test_word_navigation_in_editable_combo_box(web_form_fields: BrowserSession) -> None:
    """Tests native word navigation in an editable combo box speaks the word, not the combo name."""

    session = web_form_fields
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Search", "editable combo box", "opens listbox"],
        [helpers.BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    helpers.capture(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["foo "],
        [helpers.BrailleLine(11, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["bar "],
        [helpers.BrailleLine(15, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["baz"],
        [helpers.BrailleLine(19, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["baz"],
        [helpers.BrailleLine(16, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["bar "],
        [helpers.BrailleLine(12, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    _exit_focus_mode(session)


@pytest.mark.native_app
@helpers.xfail_firefox_caret_tab()
def test_character_navigation_in_editable_combo_box(web_form_fields: BrowserSession) -> None:
    """Tests that native character navigation in an editable combo box speaks the character."""

    session = web_form_fields
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    helpers.capture(session)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["o"],
        [helpers.BrailleLine(9, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["o"],
        [helpers.BrailleLine(10, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(11, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["o"],
        [helpers.BrailleLine(10, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    _exit_focus_mode(session)


@pytest.mark.native_app
@pytest.mark.parametrize("flash_messages", [True, False], ids=["flash", "no-flash"])
@helpers.skip_firefox_caret_tab()
def test_caret_navigation_in_text_entry(
    web_form_fields: BrowserSession, flash_messages: bool
) -> None:
    """Tests native word and character navigation in a single-line text entry."""

    session = web_form_fields
    previous = session.orca.get("BraillePresenter", "FlashMessagesAreEnabled")
    session.orca.set("BraillePresenter", "FlashMessagesAreEnabled", flash_messages)
    try:
        helpers.move_to_top(session)

        keyboard.tap_key(keyboard.KEYSYM_TAB)
        helpers.capture(session)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
        helpers.capture(session)

        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        assert helpers.capture(session) == (
            ["Jane "],
            [helpers.BrailleLine(10, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
        )

        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        assert helpers.capture(session) == (
            ["Doe"],
            [helpers.BrailleLine(14, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
        )

        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
        helpers.capture(session)

        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        assert helpers.capture(session) == (
            ["a"],
            [helpers.BrailleLine(7, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
        )

        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        assert helpers.capture(session) == (
            ["n"],
            [helpers.BrailleLine(8, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
        )

        _exit_focus_mode(session)

    finally:
        session.orca.set("BraillePresenter", "FlashMessagesAreEnabled", previous)


@pytest.mark.native_app
@pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason="Firefox's embedded-character range bounds include the next checkbox or radio button",
    raises=AssertionError,
    strict=True,
)
def test_browse_mode_line_navigation(web_form_fields: BrowserSession) -> None:
    """Tests Down-arrow line navigation in browse mode across every field type."""

    session = web_form_fields
    helpers.reset_web_state(session)

    # Spaces exposed by Firefox remain in braille after we filter redundant labels.
    # TODO: Review whitespace handling without changing braille cursor positions.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == helpers.expected_for_browser(
        session,
        (
            ["Name", "entry", "Jane Doe"],
            helpers.BrailleLine(0, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16),
        ),
        firefox=(
            ["Name", "entry", "Jane Doe"],
            helpers.BrailleLine(0, " Name Jane Doe $l", " Name Jane Doe $l", "\x00" * 17),
        ),
    )

    # Firefox exposes a click action on the Bio label; we announce "clickable".
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == helpers.expected_for_browser(
        session,
        (["Bio"], helpers.BrailleLine(1, "Bio", "Bio", "\x00" * 3)),
        firefox=(
            ["Bio", "clickable"],
            helpers.BrailleLine(1, "Bio ", "Bio ", "\xc0" * 3 + "\x00"),
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == helpers.expected_for_browser(
        session,
        (
            ["Bio", "entry", "First line of bio. "],
            helpers.BrailleLine(
                5, "Bio First line of bio.  $l", "Bio First line of bio.  $l", "\x00" * 26
            ),
        ),
        firefox=(
            ["Bio", "entry", "First line of bio. "],
            helpers.BrailleLine(
                1, " Bio First line of bio.  $l", " Bio First line of bio.  $l", "\x00" * 27
            ),
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Second sentence here."],
        helpers.BrailleLine(
            5, "Bio Second sentence here. $l", "Bio Second sentence here. $l", "\x00" * 28
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Search", "editable combo box", "opens listbox"],
        helpers.BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21),
    )

    # Firefox exposes HAS_POPUP without Chromium's typed haspopup=menu attribute.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == helpers.expected_for_browser(
        session,
        (
            ["Fruit", "combo box", "Apple", "opens menu"],
            helpers.BrailleLine(0, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21),
        ),
        firefox=(
            ["Fruit", "combo box", "Apple", "opens popup"],
            helpers.BrailleLine(0, " Fruit Apple combo box", " Fruit Apple combo box", "\x00" * 22),
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Preferred contact"],
        helpers.BrailleLine(1, "Preferred contact", "Preferred contact", "\x00" * 17),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Preferred contact", "combo box", "Email", "opens listbox"],
        helpers.BrailleLine(
            19, "Preferred contact Email combo box", "Preferred contact Email combo bo", "\x00" * 33
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Subscribe", "check box not checked"],
        helpers.BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["All topics", "check box partially checked"],
        helpers.BrailleLine(1, "<-> All topics check box", "<-> All topics check box", "\x00" * 24),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["News", "check box checked"],
        helpers.BrailleLine(1, "<x> News check box", "<x> News check box", "\x00" * 18),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Events", "check box not checked"],
        helpers.BrailleLine(1, "< > Events check box", "< > Events check box", "\x00" * 20),
    )

    # Firefox exposes the legend's text as its name; Chromium exposes a text child.
    # We consequently announce the panel and its name in different orders.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == helpers.expected_for_browser(
        session,
        (
            ["Pick a color", "panel"],
            helpers.BrailleLine(1, "Pick a color", "Pick a color", "\x00" * 12),
        ),
        firefox=(
            ["panel", "Pick a color"],
            helpers.BrailleLine(1, "Pick a color", "Pick a color", "\x00" * 12),
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Red color", "not selected radio button"],
        helpers.BrailleLine(
            1, "Pick a color & y Red color radio button", "& y Red color radio button", "\x00" * 39
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Green color", "not selected radio button"],
        helpers.BrailleLine(
            1,
            "Pick a color & y Green color radio button",
            "& y Green color radio button",
            "\x00" * 41,
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Blue color", "not selected radio button"],
        helpers.BrailleLine(
            1,
            "Pick a color & y Blue color radio button",
            "& y Blue color radio button",
            "\x00" * 40,
        ),
    )

    # The group's label is inside the group, as the APG example has it, so its text is
    # both the group's name and a line of content.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["leaving panel.", "Seat", "panel", "Seat"],
        helpers.BrailleLine(1, "Seat", "Seat", "\x00" * 4),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Aisle", "not selected radio button"],
        helpers.BrailleLine(
            1, "Seat & y Aisle radio button", "& y Aisle radio button", "\x00" * 27
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Middle", "not selected radio button"],
        helpers.BrailleLine(
            1, "Seat & y Middle radio button", "& y Middle radio button", "\x00" * 28
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Window", "not selected radio button"],
        helpers.BrailleLine(
            1, "Seat & y Window radio button", "& y Window radio button", "\x00" * 28
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == helpers.expected_for_browser(
        session,
        (
            ["leaving panel.", "Quantity", "spin button", "3"],
            helpers.BrailleLine(0, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 13),
        ),
        firefox=(
            ["leaving panel.", "Quantity", "spin button", "3"],
            helpers.BrailleLine(0, " Quantity 3 $l", " Quantity 3 $l", "\x00" * 14),
        ),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Submit", "button"],
        helpers.BrailleLine(1, "Submit button", "Submit button", "\x00" * 13),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Mute", "toggle button not pressed"],
        helpers.BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture_final(session) == (
        ["Wi-Fi", "off switch"],
        helpers.BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16),
    )


@pytest.mark.native_app
def test_word_navigation_into_text_input(web_form_fields: BrowserSession) -> None:
    """Tests browse-mode word navigation into the last word of a text input."""

    session = web_form_fields
    helpers.reset_web_state(session)

    # Firefox exposes the Name label separately before the input text.
    for _ in range(helpers.expected_for_browser(session, 3, firefox=4)):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["Doe"],
        helpers.expected_for_browser(
            session,
            [helpers.BrailleLine(14, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
            firefox=[helpers.BrailleLine(14, " Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 17)],
        ),
    )


@pytest.mark.native_app
def test_character_navigation_left_to_right(web_form_fields: BrowserSession) -> None:
    """Tests Right-arrow character navigation across form controls with focus mode off."""

    session = web_form_fields
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "TriggersFocusMode", False)

    text = "orm fieldsNameJane DoeBioFirst line of bio. Second sentence here.foo bar bazFruit"
    expected = (
        [[c] for c in text]
        + [["Fruit", "combo box", "Apple"]]
        + [[c] for c in "Preferred contact"]
        + [
            ["Preferred contact", "combo box", "Email"],
            ["Subscribe", "check box not checked"],
            ["All topics", "check box partially checked"],
            ["News", "check box checked"],
            ["Events", "check box not checked"],
        ]
        + [[c] for c in "Pick a color"]
        + [
            ["Red color", "not selected radio button"],
            ["Green color", "not selected radio button"],
            ["Blue color", "not selected radio button"],
        ]
        + [[c] for c in "Seat"]
        + [
            ["Aisle", "not selected radio button"],
            ["Middle", "not selected radio button"],
            ["Window", "not selected radio button"],
        ]
        + [[c] for c in "Quantity"]
        + [
            ["3"],
            ["Submit", "button"],
            ["Mute", "toggle button not pressed"],
            ["Wi-Fi", "off switch"],
        ]
    )

    # Firefox exposes separate text for native checkbox and radio button labels;
    # we present it during character navigation. Chromium omits that text.
    expected = helpers.expected_for_browser(
        session,
        expected,
        firefox=(
            [
                [c]
                for c in (
                    "orm fieldsName Jane DoeBio First line of bio. "
                    "Second sentence here.foo bar bazFruit "
                )
            ]
            + [["Fruit", "combo box", "Apple"]]
            + [[c] for c in "Preferred contact"]
            + [["Preferred contact", "combo box", "Email"], ["Subscribe", "check box not checked"]]
            + [[c] for c in " Subscribe"]
            + [
                ["All topics", "check box partially checked"],
                ["News", "check box checked"],
                ["Events", "check box not checked"],
            ]
            + [[c] for c in "Pick a color"]
            + [["Red color", "not selected radio button"]]
            + [[c] for c in " Red color"]
            + [["Green color", "not selected radio button"]]
            + [[c] for c in " Green color"]
            + [["Blue color", "not selected radio button"]]
            + [[c] for c in " Blue colorSeat"]
            + [
                ["Aisle", "not selected radio button"],
                ["Middle", "not selected radio button"],
                ["Window", "not selected radio button"],
            ]
            + [[c] for c in "Quantity 3"]
            + [["Submit", "button"], ["Mute", "toggle button not pressed"], ["Wi-Fi", "off switch"]]
        ),
    )
    result = []
    for _ in expected:
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        result.append(helpers.speech(session))
    assert result == expected


@pytest.mark.native_app
def test_character_navigation_right_to_left(web_form_fields: BrowserSession) -> None:
    """Tests Left-arrow character navigation back across form controls with focus mode off."""

    session = web_form_fields
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "TriggersFocusMode", False)
    helpers.move_to_bottom(session)

    forward = "Form fieldsNameJane DoeBioFirst line of bio. Second sentence here.foo bar bazFruit"
    expected = (
        [["Mute", "toggle button not pressed"], ["Submit", "button"], ["3"]]
        + [[c] for c in "Quantity"[::-1]]
        + [
            ["Window", "not selected radio button"],
            ["Middle", "not selected radio button"],
            ["Aisle", "not selected radio button"],
        ]
        + [[c] for c in "Seat"[::-1]]
        + [
            ["Blue color", "not selected radio button"],
            ["Green color", "not selected radio button"],
            ["Red color", "not selected radio button"],
        ]
        + [[c] for c in "Pick a color"[::-1]]
        + [
            ["Events", "check box not checked"],
            ["News", "check box checked"],
            ["All topics", "check box partially checked"],
            ["Subscribe", "check box not checked"],
            ["Preferred contact", "combo box", "Email"],
        ]
        + [[c] for c in "Preferred contact"[::-1]]
        + [["Fruit", "combo box", "Apple"]]
        + [[c] for c in forward[::-1]]
    )

    # Firefox exposes separate text for native checkbox and radio button labels;
    # we present it during character navigation. Chromium omits that text.
    expected = helpers.expected_for_browser(
        session,
        expected,
        firefox=(
            [["Mute", "toggle button not pressed"], ["Submit", "button"]]
            + [[c] for c in "Quantity 3"[::-1]]
            + [
                ["Window", "not selected radio button"],
                ["Middle", "not selected radio button"],
                ["Aisle", "not selected radio button"],
            ]
            + [[c] for c in " Blue colorSeat"[::-1]]
            + [["Blue color", "not selected radio button"]]
            + [[c] for c in " Green color"[::-1]]
            + [["Green color", "not selected radio button"]]
            + [[c] for c in " Red color"[::-1]]
            + [["Red color", "not selected radio button"]]
            + [[c] for c in "Pick a color"[::-1]]
            + [
                ["Events", "check box not checked"],
                ["News", "check box checked"],
                ["All topics", "check box partially checked"],
            ]
            + [[c] for c in " Subscribe"[::-1]]
            + [["Subscribe", "check box not checked"], ["Preferred contact", "combo box", "Email"]]
            + [[c] for c in "Preferred contact"[::-1]]
            + [["Fruit", "combo box", "Apple"]]
            + [
                [c]
                for c in (
                    "Form fieldsName Jane DoeBio First line of bio. "
                    "Second sentence here.foo bar bazFruit "
                )[::-1]
            ]
        ),
    )
    result = []
    for _ in expected:
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        result.append(helpers.speech(session))
    assert result == expected


@pytest.mark.native_app
def test_word_navigation_left_to_right(web_form_fields: BrowserSession) -> None:
    """Tests Ctrl+Right word navigation across the form fields."""

    session = web_form_fields
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "TriggersFocusMode", False)

    expected = [
        ["Form "],
        ["fields"],
        ["Jane "],
        ["Doe"],
        ["Bio"],
        ["First "],
        ["line "],
        ["of "],
        ["bio"],
        [". "],
        ["Second "],
        ["sentence "],
        ["here"],
        ["."],
        ["foo "],
        ["bar "],
        ["baz"],
        ["Fruit"],
        ["Fruit", "combo box", "Apple"],
        ["Preferred "],
        ["contact"],
        ["Preferred contact", "combo box", "Email"],
        ["Subscribe", "check box not checked"],
        ["All topics", "check box partially checked"],
        ["News", "check box checked"],
        ["Events", "check box not checked"],
        ["Pick "],
        ["a "],
        ["color"],
        ["Red color", "not selected radio button"],
        ["Green color", "not selected radio button"],
        ["Blue color", "not selected radio button"],
        ["Seat"],
        ["Aisle", "not selected radio button"],
        ["Middle", "not selected radio button"],
        ["Window", "not selected radio button"],
        ["3"],
        ["Submit", "button"],
        ["Mute", "toggle button not pressed"],
        ["Wi-Fi", "off switch"],
    ]

    # We present Name, Quantity, and checkbox/radio labels separately in Firefox.
    # Firefox's word ranges include the periods in "bio." and "here.".
    expected = helpers.expected_for_browser(
        session,
        expected,
        firefox=[
            ["Form "],
            ["fields"],
            ["Name"],
            ["Jane "],
            ["Doe"],
            ["Bio"],
            ["First "],
            ["line "],
            ["of "],
            ["bio. "],
            ["Second "],
            ["sentence "],
            ["here."],
            ["foo "],
            ["bar "],
            ["baz"],
            ["Fruit"],
            ["Fruit", "combo box", "Apple"],
            ["Preferred "],
            ["contact"],
            ["Preferred contact", "combo box", "Email"],
            ["Subscribe", "check box not checked"],
            ["Subscribe"],
            ["All topics", "check box partially checked"],
            ["News", "check box checked"],
            ["Events", "check box not checked"],
            ["Pick "],
            ["a "],
            ["color"],
            ["Red color", "not selected radio button"],
            ["Red "],
            ["color"],
            ["Green color", "not selected radio button"],
            ["Green "],
            ["color"],
            ["Blue color", "not selected radio button"],
            ["Blue "],
            ["color"],
            ["Seat"],
            ["Aisle", "not selected radio button"],
            ["Middle", "not selected radio button"],
            ["Window", "not selected radio button"],
            ["Quantity"],
            ["3"],
            ["Submit", "button"],
            ["Mute", "toggle button not pressed"],
            ["Wi-Fi", "off switch"],
        ],
    )
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        result.append(helpers.speech(session))
    assert result == expected


@pytest.mark.native_app
def test_word_navigation_right_to_left(web_form_fields: BrowserSession) -> None:
    """Tests Ctrl+Left word navigation back across the form fields."""

    session = web_form_fields
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "TriggersFocusMode", False)
    helpers.move_to_bottom(session)

    expected = [
        ["Mute", "toggle button not pressed"],
        ["Submit", "button"],
        ["3"],
        # Caret at the label start auto-focuses the spin button in Chromium.
        ["Quantity", "spin button", "3"],
        ["Window", "not selected radio button"],
        ["Middle", "not selected radio button"],
        ["Aisle", "not selected radio button"],
        ["Seat"],
        ["Blue color", "not selected radio button"],
        ["Green color", "not selected radio button"],
        ["Red color", "not selected radio button"],
        ["color"],
        ["a "],
        ["Pick "],
        ["Events", "check box not checked"],
        ["News", "check box checked"],
        ["All topics", "check box partially checked"],
        ["Subscribe", "check box not checked"],
        ["Preferred contact", "combo box", "Email"],
        ["contact"],
        ["Preferred "],
        ["Fruit", "combo box", "Apple"],
        ["Fruit"],
        ["baz"],
        ["bar "],
        ["foo "],
        ["."],
        ["here"],
        ["sentence "],
        ["Second "],
        [". "],
        ["bio"],
        ["of "],
        ["line "],
        ["First "],
        ["Bio"],
        ["Doe"],
        ["Jane "],
        ["Name Jane "],
        ["fields"],
        ["Form "],
    ]

    # We present Name, Quantity, and checkbox/radio labels separately in Firefox.
    # Firefox's word ranges include the periods in "bio." and "here.".
    expected = helpers.expected_for_browser(
        session,
        expected,
        firefox=[
            ["Mute", "toggle button not pressed"],
            ["Submit", "button"],
            ["3"],
            ["Quantity"],
            ["Window", "not selected radio button"],
            ["Middle", "not selected radio button"],
            ["Aisle", "not selected radio button"],
            ["Seat"],
            ["color"],
            ["Blue "],
            ["Blue color", "not selected radio button"],
            ["color"],
            ["Green "],
            ["Green color", "not selected radio button"],
            ["color"],
            ["Red "],
            ["Red color", "not selected radio button"],
            ["color"],
            ["a "],
            ["Pick "],
            ["Events", "check box not checked"],
            ["News", "check box checked"],
            ["All topics", "check box partially checked"],
            ["Subscribe"],
            ["Subscribe", "check box not checked"],
            ["Preferred contact", "combo box", "Email"],
            ["contact"],
            ["Preferred "],
            ["Fruit", "combo box", "Apple"],
            ["Fruit"],
            ["baz"],
            ["bar "],
            ["foo "],
            ["here."],
            ["sentence "],
            ["Second "],
            ["bio. "],
            ["of "],
            ["line "],
            ["First "],
            ["Bio"],
            ["Doe"],
            ["Jane "],
            ["Name"],
            ["fields"],
            ["Form "],
        ],
    )
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
        result.append(helpers.speech(session))
    assert result == expected
