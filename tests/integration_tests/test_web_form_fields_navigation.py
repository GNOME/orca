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
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _exit_focus_mode(session: NativeAppSession) -> None:
    """Toggles from focus mode back to browse mode so the next test starts clean."""

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_word_navigation_in_editable_combo_box(web_form_fields: NativeAppSession) -> None:
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
def test_character_navigation_in_editable_combo_box(web_form_fields: NativeAppSession) -> None:
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
def test_caret_navigation_in_text_entry(web_form_fields: NativeAppSession) -> None:
    """Tests native word and character navigation in a single-line text entry."""

    session = web_form_fields
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


@pytest.mark.native_app
def test_browse_mode_line_navigation(web_form_fields: NativeAppSession) -> None:
    """Tests Down-arrow line navigation in browse mode across every field type."""

    session = web_form_fields
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Name", "entry", "Jane Doe"],
        [helpers.BrailleLine(0, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Bio"],
        [helpers.BrailleLine(1, "Bio", "Bio", "\x00" * 3)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Bio", "entry", "First line of bio. "],
        [
            helpers.BrailleLine(
                5, "Bio First line of bio.  $l", "Bio First line of bio.  $l", "\x00" * 26
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Second sentence here."],
        [
            helpers.BrailleLine(
                5, "Bio Second sentence here. $l", "Bio Second sentence here. $l", "\x00" * 28
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Search", "editable combo box", "opens listbox"],
        [helpers.BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Fruit", "combo box", "Apple", "opens menu"],
        [helpers.BrailleLine(0, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Subscribe", "check box not checked"],
        [helpers.BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Pick a color", "panel"],
        [helpers.BrailleLine(1, "Pick a color", "Pick a color", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Red color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Green color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Green color radio button",
                " Pick a color& y Green color rad",
                "\x00" * 41,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Blue color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Blue color radio button",
                " Pick a color& y Blue color radi",
                "\x00" * 40,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["leaving panel.", "Quantity", "spin button", "3"],
        [helpers.BrailleLine(0, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Submit", "button"],
        [helpers.BrailleLine(1, "Submit button", "Submit button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Mute", "toggle button not pressed"],
        [helpers.BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Wi-Fi", "switch not pressed"],
        [helpers.BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16)],
    )


@pytest.mark.native_app
def test_word_navigation_stays_within_text_input(web_form_fields: NativeAppSession) -> None:
    """Tests that Ctrl+Right word navigation stays within a text input at its boundary."""

    session = web_form_fields
    helpers.reset_web_state(session)

    # Three word-jumps land on "Doe", the last word inside the Name input.
    for _ in range(3):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["Doe"],
        [helpers.BrailleLine(14, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )


@pytest.mark.native_app
def test_character_navigation_left_to_right(web_form_fields: NativeAppSession) -> None:
    """Tests Right-arrow character navigation across form controls with focus mode off."""

    session = web_form_fields
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "TriggersFocusMode", False)

    text = "orm fieldsNameJane DoeBioFirst line of bio. Second sentence here.foo bar bazFruit"
    expected = (
        [[c] for c in text]
        + [["Fruit Apple"], ["Subscribe", "not checked"]]
        + [[c] for c in "Pick a color"]
        + [
            ["Red color", "not selected"],
            ["Green color", "not selected"],
            ["Blue color", "not selected"],
        ]
        + [[c] for c in "Quantity"]
        + [["3"], ["Submit"], ["Mute", "not pressed"], ["Wi-Fi", "not pressed"]]
    )
    result = []
    for _ in expected:
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        result.append(helpers.speech(session))
    assert result == expected


@pytest.mark.native_app
def test_character_navigation_right_to_left(web_form_fields: NativeAppSession) -> None:
    """Tests Left-arrow character navigation back across form controls with focus mode off."""

    session = web_form_fields
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "TriggersFocusMode", False)
    helpers.move_to_bottom(session)

    forward = "Form fieldsNameJane DoeBioFirst line of bio. Second sentence here.foo bar bazFruit"
    expected = (
        [["Mute", "not pressed"], ["Submit"], ["3"]]
        + [[c] for c in "Quantity"[::-1]]
        + [
            ["Blue color", "not selected"],
            ["Green color", "not selected"],
            ["Red color", "not selected"],
        ]
        + [[c] for c in "Pick a color"[::-1]]
        + [["Subscribe", "not checked"], ["Fruit Apple"]]
        + [[c] for c in forward[::-1]]
    )
    result = []
    for _ in expected:
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        result.append(helpers.speech(session))
    assert result == expected


@pytest.mark.native_app
def test_word_navigation_left_to_right(web_form_fields: NativeAppSession) -> None:
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
        ["Second "],
        ["sentence "],
        ["here"],
        ["foo "],
        ["bar "],
        ["baz"],
        ["Fruit"],
        ["Fruit Apple"],
        ["Subscribe", "not checked"],
        ["Pick "],
        ["a "],
        ["color"],
        ["Red color", "not selected"],
        ["Green color", "not selected"],
        ["Blue color", "not selected"],
        ["3"],
        ["Submit"],
        ["Mute", "not pressed"],
        ["Wi-Fi", "not pressed"],
    ]
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        result.append(helpers.speech(session))
    assert result == expected


@pytest.mark.native_app
def test_word_navigation_right_to_left(web_form_fields: NativeAppSession) -> None:
    """Tests Ctrl+Left word navigation back across the form fields."""

    session = web_form_fields
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "TriggersFocusMode", False)
    helpers.move_to_bottom(session)

    expected = [
        ["Mute", "not pressed"],
        ["Submit"],
        ["3"],
        # Caret at the label start auto-focuses the spin button in Chromium.
        ["Quantity", "spin button", "3"],
        ["Blue color", "not selected"],
        ["Green color", "not selected"],
        ["Red color", "not selected"],
        ["color"],
        ["a "],
        ["Pick "],
        ["Subscribe", "not checked"],
        ["Fruit Apple"],
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
    result = []
    for _ in expected:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
        result.append(helpers.speech(session))
    assert result == expected
