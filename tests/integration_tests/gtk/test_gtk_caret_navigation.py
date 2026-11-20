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

"""Exercise Orca's announcements for caret navigation and selection in a TextView."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers, version_helpers
from tests.integration_tests.apps import gtk
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


@pytest.mark.native_app
@version_helpers.requires_gtk_version("4.0", 4, 24, when=gtk.is_gtk4())
def test_caret_navigation_presentation(gtk_text_view: NativeAppSession) -> None:
    """Orca's announcements as the caret moves via arrows, word/line jumps, buffer endpoints."""

    session = gtk_text_view
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Line two has additional words to make it long enough that "],
        [
            helpers.BrailleLine(
                1,
                "Line two has additional words to make it long enough that  $l",
                "Line two has additional words to",
                "\x00" * 61,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        helpers.expected_for_gtk(["the text view wraps it.\n"], gtk4=["the text view wraps it."]),
        [
            helpers.BrailleLine(
                1, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        helpers.expected_for_gtk(["Line three.\n"], gtk4=["Line three."]),
        [helpers.BrailleLine(1, "Line three. $l", "Line three. $l", "\x00" * 14)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        helpers.expected_for_gtk(["the text view wraps it.\n"], gtk4=["the text view wraps it."]),
        [
            helpers.BrailleLine(
                1, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["h"],
        [
            helpers.BrailleLine(
                2, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["the"],
        [
            helpers.BrailleLine(
                4, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_END)
    assert helpers.capture(session) == (
        ["blank"],
        [
            helpers.BrailleLine(
                24, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    assert helpers.capture(session) == (
        ["t"],
        [
            helpers.BrailleLine(
                1, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    assert helpers.capture(session) == (
        ["Last line."],
        [helpers.BrailleLine(11, "Last line. $l", "Last line. $l", "\x00" * 13)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert helpers.capture(session) == (
        helpers.expected_for_gtk(["Line one.\n"], gtk4=["Line one."]),
        [
            helpers.BrailleLine(
                1, "OrcaTextView application frame Line one. $l", "Line one. $l", "\x00" * 43
            )
        ],
    )


@pytest.mark.native_app
@version_helpers.requires_gtk_version("4.0", 4, 24, when=gtk.is_gtk4())
def test_caret_selection_presentation(gtk_text_view: NativeAppSession) -> None:
    """Orca's announcements as selection changes by line, word, char, jumps, and select-all."""

    session = gtk_text_view
    helpers.move_to_top(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["Line one.\n", "selected"],
        [
            helpers.BrailleLine(
                1,
                "Line two has additional words to make it long enough that  $l",
                "Line two has additional words to",
                "\x00" * 61,
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["Line two has additional words to make it long enough that ", "selected"],
        [
            helpers.BrailleLine(
                1, "the text view wraps it. $l", "the text view wraps it. $l", "\x00" * 26
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["the text view wraps it.\n", "selected"],
        [helpers.BrailleLine(1, "Line three. $l", "Line three. $l", "\x00" * 14)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["L", "selected"],
        [helpers.BrailleLine(2, "Line three. $l", "Line three. $l", "\xc0" + "\x00" * 13)],
    )

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L],
        keyboard.KEYSYM_RIGHT,
    )
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["ine", "selected"],
        [helpers.BrailleLine(5, "Line three. $l", "Line three. $l", "\xc0" * 4 + "\x00" * 10)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        [" three.", "selected"],
        [helpers.BrailleLine(12, "Line three. $l", "Line three. $l", "\xc0" * 11 + "\x00" * 3)],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert helpers.capture(session) == (
        [
            (
                "Selected text is:  Line one.\n"
                "Line two has additional words to make it long enough that "
                "the text view wraps it.\n"
                "Line three."
            )
        ],
        [],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_HOME)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["Line three.", "unselected"],
        [helpers.BrailleLine(1, "Line three. $l", "Line three. $l", "\x00" * 14)],
    )

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L],
        keyboard.KEYSYM_END,
    )
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        [
            (
                "Line three.\n"
                "Line four also has extra words to push it past the wrap boundary in the view.\n"
                "Last line."
            ),
            "selected",
        ],
        [helpers.BrailleLine(11, "Last line. $l", "Last line. $l", "\xc0" * 10 + "\x00" * 3)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        [],
        [
            helpers.BrailleLine(
                1,
                "OrcaTextView application frame Line one. $l",
                "Line one. $l",
                "\x00" * 31 + "\xc0" * 9 + "\x00" * 3,
            )
        ],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert helpers.capture(session) == (
        [
            (
                "Selected text is:  Line one.\n"
                "Line two has additional words to make it long enough that "
                "the text view wraps it.\n"
                "Line three.\n"
                "Line four also has extra words to push it past the wrap boundary in the view.\n"
                "Last line."
            )
        ],
        [],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["Text unselected.", "blank"],
        helpers.expected_for_gtk(
            [
                helpers.BrailleLine(11, "Last line. $l", "Last line. $l", "\x00" * 13),
                helpers.BrailleLine(11, "Last line. $l", "Last line. $l", "\x00" * 13),
            ],
            gtk4=[helpers.BrailleLine(11, "Last line. $l", "Last line. $l", "\x00" * 13)],
        ),
    )


def _move_to_line_three(session: NativeAppSession) -> None:
    """Puts the caret at the start of the third line and discards the resulting output."""

    helpers.move_to_top(session)
    for _count in range(3):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.2, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
@pytest.mark.xfail(
    gtk.is_gtk4(),
    reason=(
        "GTK4 TextView omits text-selection-changed when the selection is cleared: "
        "https://gitlab.gnome.org/GNOME/gtk/-/work_items/8506"
    ),
    strict=True,
    raises=AssertionError,
)
def test_selection_by_line_down_then_up(gtk_text_view: NativeAppSession) -> None:
    """Tests selection by line down and then up."""

    session = gtk_text_view
    _move_to_line_three(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["Line three.\n", "selected"],
        [
            helpers.BrailleLine(
                1,
                "Line four also has extra words to push it past the wrap  $l",
                "Line four also has extra words t",
                "\x00" * 59,
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["Line four also has extra words to push it past the wrap ", "selected"],
        [
            helpers.BrailleLine(
                1, "boundary in the view. $l", "boundary in the view. $l", "\x00" * 24
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_UP)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["Line four also has extra words to push it past the wrap ", "unselected"],
        [
            helpers.BrailleLine(
                1,
                "Line four also has extra words to push it past the wrap  $l",
                "Line four also has extra words t",
                "\x00" * 59,
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_UP)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["Line three.\n", "unselected"],
        [helpers.BrailleLine(1, "Line three. $l", "Line three. $l", "\x00" * 14)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_UP)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["the text view wraps it.\n", "selected"],
        [
            helpers.BrailleLine(
                1,
                "the text view wraps it. $l",
                "the text view wraps it. $l",
                "\xc0" * 23 + "\x00" * 3,
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_UP)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["Line two has additional words to make it long enough that ", "selected"],
        [
            helpers.BrailleLine(
                1,
                "Line two has additional words to make it long enough that  $l",
                "Line two has additional words to",
                "\xc0" * 58 + "\x00" * 3,
            )
        ],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert helpers.capture(session) == (
        [
            (
                "Selected text is:  Line two has additional words to make it long enough that "
                "the text view wraps it.\n"
            )
        ],
        [],
    )


@pytest.mark.native_app
@version_helpers.requires_gtk_version("4.0", 4, 24, when=gtk.is_gtk4())
def test_selection_by_word_and_character(gtk_text_view: NativeAppSession) -> None:
    """Tests selection by word and by character."""

    session = gtk_text_view
    _move_to_line_three(session)

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
    )
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["Line", "selected"],
        [helpers.BrailleLine(5, "Line three. $l", "Line three. $l", "\xc0" * 4 + "\x00" * 10)],
    )

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
    )
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        [" three", "selected"],
        [helpers.BrailleLine(11, "Line three. $l", "Line three. $l", "\xc0" * 10 + "\x00" * 4)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_LEFT)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["three", "unselected"],
        [helpers.BrailleLine(6, "Line three. $l", "Line three. $l", "\xc0" * 5 + "\x00" * 9)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_LEFT)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        [" ", "unselected"],
        [helpers.BrailleLine(5, "Line three. $l", "Line three. $l", "\xc0" * 4 + "\x00" * 10)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        [" ", "selected"],
        [helpers.BrailleLine(6, "Line three. $l", "Line three. $l", "\xc0" * 5 + "\x00" * 9)],
    )


@pytest.mark.native_app
def test_selection_to_the_start_and_end(gtk_text_view: NativeAppSession) -> None:
    """Tests selection to the start of the text and then to the end."""

    session = gtk_text_view
    _move_to_line_three(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_HOME)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        [
            (
                "Line one.\n"
                "Line two has additional words to make it long enough that "
                "the text view wraps it.\n"
            ),
            "selected",
        ],
        [
            helpers.BrailleLine(
                1,
                "OrcaTextView application frame Line one. $l",
                "Line one. $l",
                "\x00" * 31 + "\xc0" * 9 + "\x00" * 3,
            )
        ],
    )

    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert helpers.capture(session) == (
        [
            (
                "Selected text is:  Line one.\n"
                "Line two has additional words to make it long enough that "
                "the text view wraps it.\n"
            )
        ],
        [],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        [
            (
                "Line one.\n"
                "Line two has additional words to make it long enough that "
                "the text view wraps it.\n"
            ),
            "unselected",
            (
                "Line three.\n"
                "Line four also has extra words to push it past the wrap boundary in the view.\n"
                "Last line."
            ),
            "selected",
        ],
        [helpers.BrailleLine(11, "Last line. $l", "Last line. $l", "\xc0" * 10 + "\x00" * 3)],
    )


@pytest.mark.native_app
def test_say_selected_text_when_nothing_is_selected(gtk_text_view: NativeAppSession) -> None:
    """Tests say selected text when nothing is selected."""

    session = gtk_text_view
    helpers.move_to_top(session)

    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert helpers.capture(session) == (["No selected text."], [])


@pytest.mark.native_app
@pytest.mark.xfail(
    gtk.is_gtk4(),
    reason=(
        "GTK4 TextView omits selection-changed when replacing selected text "
        "(https://gitlab.gnome.org/GNOME/gtk/-/work_items/8506). Caret-moved is also missing "
        "(https://gitlab.gnome.org/GNOME/gtk/-/work_items/7461)."
    ),
    strict=True,
    raises=AssertionError,
)
def test_typing_over_a_selection(gtk_text_view: NativeAppSession) -> None:
    """Tests typing over a selection."""

    # This test rewrites part of the buffer, so it must remain the last one in the file.
    session = gtk_text_view
    _move_to_line_three(session)

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
    )
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["Line", "selected"],
        [helpers.BrailleLine(5, "Line three. $l", "Line three. $l", "\xc0" * 4 + "\x00" * 10)],
    )

    keyboard.tap_key(ord("z"))
    spoken, brailled = helpers.capture(session)
    assert spoken == ["z", "Text unselected."]
    assert brailled[-1] == helpers.BrailleLine(2, "z three. $l", "z three. $l", "\x00" * 11)

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1:]) == (
        ["z"],
        [helpers.BrailleLine(1, "z three. $l", "z three. $l", "\x00" * 11)],
    )
