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

"""Tests navigation and presentation of form fields on a web page."""

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


# Keep first: after the later form-field tests, Say All starts mid-document instead of
# at the top (root cause not yet pinned down).
@pytest.mark.native_app
def test_say_all_over_form_fields(web_form_fields: NativeAppSession) -> None:
    """Tests the utterances Say All speaks for a page of form controls, from the top."""

    session = web_form_fields
    helpers.reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert helpers.speech(session) == [
        "Form fields",
        "Name",
        "entry",
        "Jane Doe",
        "Bio",
        "entry",
        "First line of bio. ",
        "Second sentence here.",
        "Search",
        "editable combo box",
        "opens listbox",
        "Fruit",
        "combo box",
        "Apple",
        "opens menu",
        "Subscribe",
        "check box",
        "not checked",
        "Red color",
        "not selected",
        "radio button",
        "Green color",
        "not selected",
        "radio button",
        "Blue color",
        "not selected",
        "radio button",
        "Quantity",
        "spin button",
        "3",
        "Submit",
        "button",
        "Mute",
        "toggle button",
        "not pressed",
        "Wi-Fi",
        "switch",
        "not pressed",
    ]


@pytest.mark.native_app
def test_structural_navigation_by_form_field(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by form field across every field type."""

    session = web_form_fields
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Name", "entry", "Jane Doe"],
        [helpers.BrailleLine(6, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Bio", "entry", "First line of bio. "],
        [
            helpers.BrailleLine(
                5, "Bio First line of bio.  $l", "Bio First line of bio.  $l", "\x00" * 26
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Search", "editable combo box", "opens listbox"],
        [helpers.BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Fruit", "combo box", "Apple", "opens menu"],
        [helpers.BrailleLine(7, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Subscribe", "check box not checked"],
        [helpers.BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Pick a color", "panel", "Red color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Green color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Green color radio button",
                " Pick a color& y Green color rad",
                "\x00" * 41,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Blue color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Blue color radio button",
                " Pick a color& y Blue color radi",
                "\x00" * 40,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "leaving panel.", "Quantity", "spin button", "3"],
        [helpers.BrailleLine(10, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Submit", "button"],
        [helpers.BrailleLine(1, "Submit button", "Submit button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Mute", "toggle button not pressed"],
        [helpers.BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Wi-Fi", "switch not pressed"],
        [helpers.BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["f", "Wrapping to top.", "Name", "entry", "Jane Doe"],
        [
            helpers.BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            helpers.BrailleLine(6, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["F", "Wrapping to bottom.", "Wi-Fi", "switch not pressed"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert helpers.capture(session) == (
        ["F", "Mute", "toggle button not pressed"],
        [helpers.BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_entry(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by entry, which includes the spin button."""

    session = web_form_fields
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert helpers.capture(session) == (
        ["e", "Name", "entry", "Jane Doe"],
        [helpers.BrailleLine(6, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert helpers.capture(session) == (
        ["e", "Bio", "entry", "First line of bio. "],
        [
            helpers.BrailleLine(
                5, "Bio First line of bio.  $l", "Bio First line of bio.  $l", "\x00" * 26
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert helpers.capture(session) == (
        ["e", "Search", "editable combo box", "opens listbox"],
        [helpers.BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert helpers.capture(session) == (
        ["e", "Quantity", "spin button", "3"],
        [helpers.BrailleLine(10, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert helpers.capture(session) == (
        ["e", "Wrapping to top.", "Name", "entry", "Jane Doe"],
        [
            helpers.BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            helpers.BrailleLine(6, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_E)
    assert helpers.capture(session) == (
        ["E", "Wrapping to bottom.", "Quantity", "spin button", "3"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(10, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 13),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_E)
    assert helpers.capture(session) == (
        ["E", "Search", "editable combo box", "opens listbox"],
        [helpers.BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_checkbox(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by checkbox, including the wrap announcement."""

    session = web_form_fields
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_X)
    assert helpers.capture(session) == (
        ["x", "Subscribe", "check box not checked"],
        [helpers.BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_X)
    assert helpers.capture(session) == (
        ["x", "Wrapping to top.", "Subscribe", "not checked"],
        [
            helpers.BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            helpers.BrailleLine(
                1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23
            ),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_X)
    assert helpers.capture(session) == (
        ["X", "Wrapping to bottom.", "Subscribe", "not checked"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(
                1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23
            ),
        ],
    )


@pytest.mark.native_app
def test_structural_navigation_by_radio_button(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by radio button, including the wrap announcement."""

    session = web_form_fields
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert helpers.capture(session) == (
        ["r", "Pick a color", "panel", "Red color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert helpers.capture(session) == (
        ["r", "Green color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Green color radio button",
                " Pick a color& y Green color rad",
                "\x00" * 41,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert helpers.capture(session) == (
        ["r", "Blue color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Blue color radio button",
                " Pick a color& y Blue color radi",
                "\x00" * 40,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert helpers.capture(session) == (
        ["r", "Wrapping to top.", "Red color", "not selected radio button"],
        [
            helpers.BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            helpers.BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            ),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_R)
    assert helpers.capture(session) == (
        ["R", "Wrapping to bottom.", "Blue color", "not selected radio button"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(
                14,
                " Pick a color& y Blue color radio button",
                " Pick a color& y Blue color radi",
                "\x00" * 40,
            ),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_R)
    assert helpers.capture(session) == (
        ["R", "Green color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Green color radio button",
                " Pick a color& y Green color rad",
                "\x00" * 41,
            )
        ],
    )


@pytest.mark.native_app
def test_structural_navigation_by_button(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by button, including toggle button and switch."""

    session = web_form_fields
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert helpers.capture(session) == (
        ["b", "Submit", "button"],
        [helpers.BrailleLine(1, "Submit button", "Submit button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert helpers.capture(session) == (
        ["b", "Mute", "toggle button not pressed"],
        [helpers.BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert helpers.capture(session) == (
        ["b", "Wi-Fi", "switch not pressed"],
        [helpers.BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert helpers.capture(session) == (
        ["b", "Wrapping to top.", "Submit", "button"],
        [
            helpers.BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            helpers.BrailleLine(1, "Submit button", "Submit button", "\x00" * 13),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_B)
    assert helpers.capture(session) == (
        ["B", "Wrapping to bottom.", "Wi-Fi", "switch not pressed"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_B)
    assert helpers.capture(session) == (
        ["B", "Mute", "toggle button not pressed"],
        [helpers.BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_combo_box(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by combo box across the editable and select variants."""

    session = web_form_fields
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_C)
    assert helpers.capture(session) == (
        ["c", "Search", "editable combo box", "opens listbox"],
        [helpers.BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_C)
    assert helpers.capture(session) == (
        ["c", "Fruit", "combo box", "Apple", "opens menu"],
        [helpers.BrailleLine(7, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_C)
    assert helpers.capture(session) == (
        ["c", "Wrapping to top.", "Search", "editable combo box", "opens listbox"],
        [
            helpers.BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            helpers.BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_C)
    assert helpers.capture(session) == (
        ["C", "Wrapping to bottom.", "Fruit", "combo box", "Apple", "opens menu"],
        [
            helpers.BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            helpers.BrailleLine(7, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_C)
    assert helpers.capture(session) == (
        ["C", "Search", "editable combo box", "opens listbox"],
        [helpers.BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )


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
def test_fieldset_legend_role_only_on_entry(web_form_fields: NativeAppSession) -> None:
    """The group's role is announced when entering via the legend, but not when revisited."""

    session = web_form_fields
    helpers.move_to_top(session)

    for _ in range(9):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(session)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["Pick a color"],
        [helpers.BrailleLine(1, "Pick a color", "Pick a color", "\x00" * 12)],
    )


def _where_am_i(session: NativeAppSession) -> tuple[list[str], list[tuple[int, str, str | None]]]:
    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    return helpers.capture(session)


@pytest.mark.native_app
def test_where_am_i_on_form_controls(web_form_fields: NativeAppSession) -> None:
    """Tests Where Am I on entry, combo box, checkbox, radio button, and button."""

    session = web_form_fields
    helpers.reset_web_state(session)

    helpers.tab_and_swallow_presentation(session)
    assert _where_am_i(session) == (
        ["entry", "Jane Doe", "selected"],
        [
            helpers.BrailleLine(
                14, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 5 + "\xc0" * 8 + "\x00" * 3
            ),
            helpers.BrailleLine(
                14, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 5 + "\xc0" * 8 + "\x00" * 3
            ),
        ],
    )

    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    assert _where_am_i(session) == (
        ["Fruit", "combo box", "Apple"],
        [helpers.BrailleLine(7, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21)],
    )

    helpers.tab_and_swallow_presentation(session)
    assert _where_am_i(session) == (
        ["Subscribe", "check box not checked"],
        [
            helpers.BrailleLine(
                1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23
            ),
            helpers.BrailleLine(
                1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23
            ),
        ],
    )

    helpers.tab_and_swallow_presentation(session)
    assert _where_am_i(session) == (
        ["Pick a color", "Red color", "not selected radio button"],
        [
            helpers.BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            )
        ],
    )

    for _ in range(2):
        helpers.tab_and_swallow_presentation(session)
    assert _where_am_i(session) == (
        ["Submit", "button"],
        [
            helpers.BrailleLine(1, "Submit button", "Submit button", "\x00" * 13),
            helpers.BrailleLine(1, "Submit button", "Submit button", "\x00" * 13),
        ],
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
