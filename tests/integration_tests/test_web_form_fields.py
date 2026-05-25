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

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _exit_focus_mode(session: NativeAppSession) -> None:
    """Toggles from focus mode back to browse mode so the next test starts clean."""

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_structural_navigation_by_form_field(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by form field across every field type."""

    session = web_form_fields
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Name", "entry", "Jane Doe"],
        [BrailleLine(6, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Bio", "entry", "First line of bio. "],
        [BrailleLine(5, "Bio First line of bio.  $l", "Bio First line of bio.  $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Search", "editable combo box", "opens listbox"],
        [BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Fruit", "combo box", "Apple", "opens menu"],
        [BrailleLine(7, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Subscribe", "check box not checked"],
        [BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Pick a color", "panel", "Red color", "not selected radio button"],
        [
            BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Green color", "not selected radio button"],
        [
            BrailleLine(
                14,
                " Pick a color& y Green color radio button",
                " Pick a color& y Green color rad",
                "\x00" * 41,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Blue color", "not selected radio button"],
        [
            BrailleLine(
                14,
                " Pick a color& y Blue color radio button",
                " Pick a color& y Blue color radi",
                "\x00" * 40,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "leaving panel.", "leaving panel.", "Quantity", "spin button", "3"],
        [BrailleLine(10, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Submit", "button"],
        [BrailleLine(1, "Submit button", "Submit button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Mute", "toggle button not pressed"],
        [BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Wi-Fi", "switch not pressed"],
        [BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert capture(session) == (
        ["f", "Wrapping to top.", "Name", "entry", "Jane Doe"],
        [
            BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            BrailleLine(6, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert capture(session) == (
        ["F", "Wrapping to bottom.", "Wi-Fi", "switch not pressed"],
        [
            BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert capture(session) == (
        ["F", "Mute", "toggle button not pressed"],
        [BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_entry(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by entry, which includes the spin button."""

    session = web_form_fields
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert capture(session) == (
        ["e", "Name", "entry", "Jane Doe"],
        [BrailleLine(6, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert capture(session) == (
        ["e", "Bio", "entry", "First line of bio. "],
        [BrailleLine(5, "Bio First line of bio.  $l", "Bio First line of bio.  $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert capture(session) == (
        ["e", "Search", "editable combo box", "opens listbox"],
        [BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert capture(session) == (
        ["e", "Quantity", "spin button", "3"],
        [BrailleLine(10, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert capture(session) == (
        ["e", "Wrapping to top.", "Name", "entry", "Jane Doe"],
        [
            BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            BrailleLine(6, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_E)
    assert capture(session) == (
        ["E", "Wrapping to bottom.", "Quantity", "spin button", "3"],
        [
            BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            BrailleLine(10, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 13),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_E)
    assert capture(session) == (
        ["E", "Search", "editable combo box", "opens listbox"],
        [BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_checkbox(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by checkbox, including the wrap announcement."""

    session = web_form_fields
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_X)
    assert capture(session) == (
        ["x", "Subscribe", "check box not checked"],
        [BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_X)
    assert capture(session) == (
        ["x", "Wrapping to top.", "Subscribe", "not checked"],
        [
            BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_X)
    assert capture(session) == (
        ["X", "Wrapping to bottom.", "Subscribe", "not checked"],
        [
            BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23),
        ],
    )


@pytest.mark.native_app
def test_structural_navigation_by_radio_button(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by radio button, including the wrap announcement."""

    session = web_form_fields
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert capture(session) == (
        ["r", "Pick a color", "panel", "Red color", "not selected radio button"],
        [
            BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert capture(session) == (
        ["r", "Green color", "not selected radio button"],
        [
            BrailleLine(
                14,
                " Pick a color& y Green color radio button",
                " Pick a color& y Green color rad",
                "\x00" * 41,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert capture(session) == (
        ["r", "Blue color", "not selected radio button"],
        [
            BrailleLine(
                14,
                " Pick a color& y Blue color radio button",
                " Pick a color& y Blue color radi",
                "\x00" * 40,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert capture(session) == (
        ["r", "Wrapping to top.", "Red color", "not selected radio button"],
        [
            BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            ),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_R)
    assert capture(session) == (
        ["R", "Wrapping to bottom.", "Blue color", "not selected radio button"],
        [
            BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            BrailleLine(
                14,
                " Pick a color& y Blue color radio button",
                " Pick a color& y Blue color radi",
                "\x00" * 40,
            ),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_R)
    assert capture(session) == (
        ["R", "Green color", "not selected radio button"],
        [
            BrailleLine(
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
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert capture(session) == (
        ["b", "Submit", "button"],
        [BrailleLine(1, "Submit button", "Submit button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert capture(session) == (
        ["b", "Mute", "toggle button not pressed"],
        [BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert capture(session) == (
        ["b", "Wi-Fi", "switch not pressed"],
        [BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert capture(session) == (
        ["b", "Wrapping to top.", "Submit", "button"],
        [
            BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            BrailleLine(1, "Submit button", "Submit button", "\x00" * 13),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_B)
    assert capture(session) == (
        ["B", "Wrapping to bottom.", "Wi-Fi", "switch not pressed"],
        [
            BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_B)
    assert capture(session) == (
        ["B", "Mute", "toggle button not pressed"],
        [BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_combo_box(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by combo box across the editable and select variants."""

    session = web_form_fields
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_C)
    assert capture(session) == (
        ["c", "Search", "editable combo box", "opens listbox"],
        [BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_C)
    assert capture(session) == (
        ["c", "Fruit", "combo box", "Apple", "opens menu"],
        [BrailleLine(7, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_C)
    assert capture(session) == (
        ["c", "Wrapping to top.", "Search", "editable combo box", "opens listbox"],
        [
            BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_C)
    assert capture(session) == (
        ["C", "Wrapping to bottom.", "Fruit", "combo box", "Apple", "opens menu"],
        [
            BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            BrailleLine(7, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_C)
    assert capture(session) == (
        ["C", "Search", "editable combo box", "opens listbox"],
        [BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )


@pytest.mark.native_app
def test_word_navigation_in_editable_combo_box(web_form_fields: NativeAppSession) -> None:
    """Tests native word navigation in an editable combo box speaks the word, not the combo name."""

    session = web_form_fields
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session) == (
        ["Search", "editable combo box", "opens listbox"],
        [BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    capture(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["foo "],
        [BrailleLine(11, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["bar "],
        [BrailleLine(15, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["baz"],
        [BrailleLine(19, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["baz"],
        [BrailleLine(16, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["bar "],
        [BrailleLine(12, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    _exit_focus_mode(session)


@pytest.mark.native_app
def test_character_navigation_in_editable_combo_box(web_form_fields: NativeAppSession) -> None:
    """Tests that native character navigation in an editable combo box speaks the character."""

    session = web_form_fields
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["o"],
        [BrailleLine(9, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["o"],
        [BrailleLine(10, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [" "],
        [BrailleLine(11, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["o"],
        [BrailleLine(10, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    _exit_focus_mode(session)


@pytest.mark.native_app
def test_caret_navigation_in_text_entry(web_form_fields: NativeAppSession) -> None:
    """Tests native word and character navigation in a single-line text entry."""

    session = web_form_fields
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    capture(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Jane "],
        [BrailleLine(10, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Doe"],
        [BrailleLine(14, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["a"],
        [BrailleLine(7, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["n"],
        [BrailleLine(8, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )

    _exit_focus_mode(session)


@pytest.mark.native_app
def test_browse_mode_line_navigation(web_form_fields: NativeAppSession) -> None:
    """Tests Down-arrow line navigation in browse mode across every field type."""

    session = web_form_fields
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Name", "entry", "Jane Doe"],
        [BrailleLine(0, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Bio"],
        [BrailleLine(1, "Bio", "Bio", "\x00" * 3)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Bio", "entry", "First line of bio. "],
        [BrailleLine(5, "Bio First line of bio.  $l", "Bio First line of bio.  $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Second sentence here."],
        [
            BrailleLine(
                5, "Bio Second sentence here. $l", "Bio Second sentence here. $l", "\x00" * 28
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Search", "editable combo box", "opens listbox"],
        [BrailleLine(8, "Search foo bar baz $l", "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Fruit", "combo box", "Apple", "opens menu"],
        [BrailleLine(0, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Subscribe", "check box not checked"],
        [BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Pick a color", "panel"],
        [BrailleLine(1, "Pick a color", "Pick a color", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Red color", "not selected radio button"],
        [
            BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Green color", "not selected radio button"],
        [
            BrailleLine(
                14,
                " Pick a color& y Green color radio button",
                " Pick a color& y Green color rad",
                "\x00" * 41,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Blue color", "not selected radio button"],
        [
            BrailleLine(
                14,
                " Pick a color& y Blue color radio button",
                " Pick a color& y Blue color radi",
                "\x00" * 40,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["leaving panel.", "leaving panel.", "Quantity", "spin button", "3"],
        [BrailleLine(0, "Quantity 3 $l", "Quantity 3 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Submit", "button"],
        [BrailleLine(1, "Submit button", "Submit button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Mute", "toggle button not pressed"],
        [BrailleLine(1, "& y Mute toggle button", "& y Mute toggle button", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Wi-Fi", "switch not pressed"],
        [BrailleLine(1, "& y Wi-Fi switch", "& y Wi-Fi switch", "\x00" * 16)],
    )


@pytest.mark.native_app
def test_fieldset_legend_role_only_on_entry(web_form_fields: NativeAppSession) -> None:
    """The group's role is announced when entering via the legend, but not when revisited."""

    session = web_form_fields
    move_to_top(session)

    for _ in range(9):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(session)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Pick a color"],
        [BrailleLine(1, "Pick a color", "Pick a color", "\x00" * 12)],
    )
