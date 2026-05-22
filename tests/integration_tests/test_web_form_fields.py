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

from orca.output_reader import BrailleRecord, SpeechRecord

from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _capture(
    session: NativeAppSession,
) -> tuple[list[str], list[tuple[int, str, str | None]]]:
    records = session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    spoken = [r.text for r in records if isinstance(r, SpeechRecord)]
    brailled = [(r.cursor_cell, r.string, r.mask) for r in records if isinstance(r, BrailleRecord)]
    return spoken, brailled


def _move_to_top(session: NativeAppSession) -> None:
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _exit_focus_mode(session: NativeAppSession) -> None:
    """Toggles from focus mode back to browse mode so the next test starts clean."""

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_structural_navigation_by_form_field(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by form field across every field type."""

    session = web_form_fields
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Name", "entry", "Jane Doe"],
        [(6, "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Bio", "entry", "First line of bio. "],
        [(5, "Bio First line of bio.  $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Search", "editable combo box", "opens listbox"],
        [(8, "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Fruit", "combo box", "Apple", "opens menu"],
        [(7, "Fruit Apple combo box", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Subscribe", "check box not checked"],
        [(1, "< > Subscribe check box", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Pick a color", "panel", "Red color", "not selected radio button"],
        [(14, " Pick a color& y Red color radio", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Green color", "not selected radio button"],
        [(14, " Pick a color& y Green color rad", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Blue color", "not selected radio button"],
        [(14, " Pick a color& y Blue color radi", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "leaving panel.", "leaving panel.", "Quantity", "spin button", "3"],
        [(10, "Quantity 3 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Submit", "button"],
        [(1, "Submit button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Mute", "toggle button not pressed"],
        [(1, "& y Mute toggle button", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Wi-Fi", "switch not pressed"],
        [(1, "& y Wi-Fi switch", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["f", "Wrapping to top.", "Name", "entry", "Jane Doe"],
        [
            (0, "Wrapping to top.", "\x00" * 16),
            (6, "Name Jane Doe $l", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["F", "Wrapping to bottom.", "Wi-Fi", "switch not pressed"],
        [
            (0, "Wrapping to bottom.", "\x00" * 19),
            (1, "& y Wi-Fi switch", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F)
    assert _capture(session) == (
        ["F", "Mute", "toggle button not pressed"],
        [(1, "& y Mute toggle button", "\x00" * 22)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_entry(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by entry, which includes the spin button."""

    session = web_form_fields
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert _capture(session) == (
        ["e", "Name", "entry", "Jane Doe"],
        [(6, "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert _capture(session) == (
        ["e", "Bio", "entry", "First line of bio. "],
        [(5, "Bio First line of bio.  $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert _capture(session) == (
        ["e", "Search", "editable combo box", "opens listbox"],
        [(8, "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert _capture(session) == (
        ["e", "Quantity", "spin button", "3"],
        [(10, "Quantity 3 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert _capture(session) == (
        ["e", "Wrapping to top.", "Name", "entry", "Jane Doe"],
        [
            (0, "Wrapping to top.", "\x00" * 16),
            (6, "Name Jane Doe $l", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_E)
    assert _capture(session) == (
        ["E", "Wrapping to bottom.", "Quantity", "spin button", "3"],
        [
            (0, "Wrapping to bottom.", "\x00" * 19),
            (10, "Quantity 3 $l", "\x00" * 13),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_E)
    assert _capture(session) == (
        ["E", "Search", "editable combo box", "opens listbox"],
        [(8, "Search foo bar baz $l", "\x00" * 21)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_checkbox(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by checkbox, including the wrap announcement."""

    session = web_form_fields
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_X)
    assert _capture(session) == (
        ["x", "Subscribe", "check box not checked"],
        [(1, "< > Subscribe check box", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_X)
    assert _capture(session) == (
        ["x", "Wrapping to top.", "Subscribe", "not checked"],
        [
            (0, "Wrapping to top.", "\x00" * 16),
            (1, "< > Subscribe check box", "\x00" * 23),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_X)
    assert _capture(session) == (
        ["X", "Wrapping to bottom.", "Subscribe", "not checked"],
        [
            (0, "Wrapping to bottom.", "\x00" * 19),
            (1, "< > Subscribe check box", "\x00" * 23),
        ],
    )


@pytest.mark.native_app
def test_structural_navigation_by_radio_button(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by radio button, including the wrap announcement."""

    session = web_form_fields
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert _capture(session) == (
        ["r", "Pick a color", "panel", "Red color", "not selected radio button"],
        [(14, " Pick a color& y Red color radio", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert _capture(session) == (
        ["r", "Green color", "not selected radio button"],
        [(14, " Pick a color& y Green color rad", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert _capture(session) == (
        ["r", "Blue color", "not selected radio button"],
        [(14, " Pick a color& y Blue color radi", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_R)
    assert _capture(session) == (
        ["r", "Wrapping to top.", "Red color", "not selected radio button"],
        [
            (0, "Wrapping to top.", "\x00" * 16),
            (14, " Pick a color& y Red color radio", "\x00" * 32),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_R)
    assert _capture(session) == (
        ["R", "Wrapping to bottom.", "Blue color", "not selected radio button"],
        [
            (0, "Wrapping to bottom.", "\x00" * 19),
            (14, " Pick a color& y Blue color radi", "\x00" * 32),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_R)
    assert _capture(session) == (
        ["R", "Green color", "not selected radio button"],
        [(14, " Pick a color& y Green color rad", "\x00" * 32)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_button(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by button, including toggle button and switch."""

    session = web_form_fields
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert _capture(session) == (
        ["b", "Submit", "button"],
        [(1, "Submit button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert _capture(session) == (
        ["b", "Mute", "toggle button not pressed"],
        [(1, "& y Mute toggle button", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert _capture(session) == (
        ["b", "Wi-Fi", "switch not pressed"],
        [(1, "& y Wi-Fi switch", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert _capture(session) == (
        ["b", "Wrapping to top.", "Submit", "button"],
        [
            (0, "Wrapping to top.", "\x00" * 16),
            (1, "Submit button", "\x00" * 13),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_B)
    assert _capture(session) == (
        ["B", "Wrapping to bottom.", "Wi-Fi", "switch not pressed"],
        [
            (0, "Wrapping to bottom.", "\x00" * 19),
            (1, "& y Wi-Fi switch", "\x00" * 16),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_B)
    assert _capture(session) == (
        ["B", "Mute", "toggle button not pressed"],
        [(1, "& y Mute toggle button", "\x00" * 22)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_combo_box(web_form_fields: NativeAppSession) -> None:
    """Tests structural navigation by combo box across the editable and select variants."""

    session = web_form_fields
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_C)
    assert _capture(session) == (
        ["c", "Search", "editable combo box", "opens listbox"],
        [(8, "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_C)
    assert _capture(session) == (
        ["c", "Fruit", "combo box", "Apple", "opens menu"],
        [(7, "Fruit Apple combo box", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_C)
    assert _capture(session) == (
        ["c", "Wrapping to top.", "Search", "editable combo box", "opens listbox"],
        [
            (0, "Wrapping to top.", "\x00" * 16),
            (8, "Search foo bar baz $l", "\x00" * 21),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_C)
    assert _capture(session) == (
        ["C", "Wrapping to bottom.", "Fruit", "combo box", "Apple", "opens menu"],
        [
            (0, "Wrapping to bottom.", "\x00" * 19),
            (7, "Fruit Apple combo box", "\x00" * 21),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_C)
    assert _capture(session) == (
        ["C", "Search", "editable combo box", "opens listbox"],
        [(8, "Search foo bar baz $l", "\x00" * 21)],
    )


@pytest.mark.native_app
def test_word_navigation_in_editable_combo_box(web_form_fields: NativeAppSession) -> None:
    """Tests that native word navigation in an editable combo box speaks the word.

    Regression test: navigating by word used to speak the combo box name (e.g. "Search")
    instead of the word at the caret.
    """

    session = web_form_fields
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    _capture(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    _capture(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert _capture(session) == (
        ["Search", "editable combo box", "opens listbox"],
        [(8, "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    _capture(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (["foo "], [(11, "Search foo bar baz $l", "\x00" * 21)])

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (["bar "], [(15, "Search foo bar baz $l", "\x00" * 21)])

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (["baz"], [(19, "Search foo bar baz $l", "\x00" * 21)])

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
    assert _capture(session) == (["baz"], [(16, "Search foo bar baz $l", "\x00" * 21)])

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_LEFT)
    assert _capture(session) == (["bar "], [(12, "Search foo bar baz $l", "\x00" * 21)])

    _exit_focus_mode(session)


@pytest.mark.native_app
def test_character_navigation_in_editable_combo_box(web_form_fields: NativeAppSession) -> None:
    """Tests that native character navigation in an editable combo box speaks the character."""

    session = web_form_fields
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    _capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    _capture(session)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (["o"], [(9, "Search foo bar baz $l", "\x00" * 21)])

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (["o"], [(10, "Search foo bar baz $l", "\x00" * 21)])

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == ([" "], [(11, "Search foo bar baz $l", "\x00" * 21)])

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert _capture(session) == (["o"], [(10, "Search foo bar baz $l", "\x00" * 21)])

    _exit_focus_mode(session)


@pytest.mark.native_app
def test_caret_navigation_in_text_entry(web_form_fields: NativeAppSession) -> None:
    """Tests native word and character navigation in a single-line text entry."""

    session = web_form_fields
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    _capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    _capture(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (["Jane "], [(10, "Name Jane Doe $l", "\x00" * 16)])

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (["Doe"], [(14, "Name Jane Doe $l", "\x00" * 16)])

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    _capture(session)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (["a"], [(7, "Name Jane Doe $l", "\x00" * 16)])

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert _capture(session) == (["n"], [(8, "Name Jane Doe $l", "\x00" * 16)])

    _exit_focus_mode(session)


@pytest.mark.native_app
def test_browse_mode_line_navigation(web_form_fields: NativeAppSession) -> None:
    """Tests Down-arrow line navigation in browse mode across every field type."""

    session = web_form_fields
    _move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Name", "entry", "Jane Doe"],
        [(0, "Name Jane Doe $l", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (["Bio"], [(1, "Bio", "\x00" * 3)])

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Bio", "entry", "First line of bio. "],
        [(5, "Bio First line of bio.  $l", "\x00" * 26)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Second sentence here."],
        [(5, "Bio Second sentence here. $l", "\x00" * 28)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Search", "editable combo box", "opens listbox"],
        [(8, "Search foo bar baz $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Fruit", "combo box", "Apple", "opens menu"],
        [(0, "Fruit Apple combo box", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Subscribe", "check box not checked"],
        [(1, "< > Subscribe check box", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Pick a color", "panel"],
        [(1, "Pick a color", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Red color", "not selected radio button"],
        [(14, " Pick a color& y Red color radio", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Green color", "not selected radio button"],
        [(14, " Pick a color& y Green color rad", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Blue color", "not selected radio button"],
        [(14, " Pick a color& y Blue color radi", "\x00" * 32)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["leaving panel.", "leaving panel.", "Quantity", "spin button", "3"],
        [(0, "Quantity 3 $l", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Submit", "button"],
        [(1, "Submit button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Mute", "toggle button not pressed"],
        [(1, "& y Mute toggle button", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert _capture(session) == (
        ["Wi-Fi", "switch not pressed"],
        [(1, "& y Wi-Fi switch", "\x00" * 16)],
    )


@pytest.mark.native_app
def test_fieldset_legend_role_only_on_entry(web_form_fields: NativeAppSession) -> None:
    """The group's role is announced when entering via the legend, but not when revisited."""

    session = web_form_fields
    _move_to_top(session)

    for _ in range(9):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        _capture(session)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert _capture(session) == (["Pick a color"], [(1, "Pick a color", "\x00" * 12)])
