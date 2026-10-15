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

"""Tests native Atril selection in a two-page PDF."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import caret_selection_helpers as commands
from .atril_helpers import assert_step, selected_ranges, selection_session
from .harness import keyboard
from .helpers import BrailleLine, capture, say_selection

if TYPE_CHECKING:
    from .orca_fixtures import AtrilSession


_COLLAPSED_SELECTION_BUG = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "Atril retains invalid selection ranges after native selection collapses: "
        "https://github.com/mate-desktop/atril/issues/735"
    ),
)


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_character(atril: AtrilSession) -> None:
    """Checks selection by character."""

    with selection_session(atril, native=True):
        assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["D", "selected"],
            BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
            ([(0, 1)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["o", "selected"],
            BrailleLine(3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15),
            ([(0, 2)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_CHARACTER,
            [" ", "selected"],
            BrailleLine(4, "Do headings work?", "Do headings work?", "\xc0" * 3 + "\x00" * 14),
            ([(0, 3)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            [" ", "unselected"],
            BrailleLine(3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15),
            ([(0, 2)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["o", "unselected"],
            BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
            ([(0, 1)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["D", "unselected"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=True,
        )
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_character_backward(atril: AtrilSession) -> None:
    """Checks selection by character backward."""

    with selection_session(atril, native=True):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        capture(atril)
        assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["o", "selected"],
            BrailleLine(2, "Do headings work?", "Do headings work?", "\x00" + "\xc0" + "\x00" * 15),
            ([(1, 2)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["D", "selected"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15),
            ([(0, 2)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["D", "unselected"],
            BrailleLine(2, "Do headings work?", "Do headings work?", "\x00" + "\xc0" + "\x00" * 15),
            ([(1, 2)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["o", "unselected"],
            BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=True,
        )
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_word(atril: AtrilSession) -> None:
    """Checks selection by word."""

    with selection_session(atril, native=True):
        assert_step(
            atril,
            commands.NEXT_WORD,
            ["Do", "selected"],
            BrailleLine(3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15),
            ([(0, 2)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_WORD,
            [" headings", "selected"],
            BrailleLine(12, "Do headings work?", "Do headings work?", "\xc0" * 11 + "\x00" * 6),
            ([(0, 11)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_WORD,
            [" work", "selected"],
            BrailleLine(17, "Do headings work?", "Do headings work?", "\xc0" * 16 + "\x00"),
            ([(0, 16)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["work", "unselected"],
            BrailleLine(13, "Do headings work?", "Do headings work?", "\xc0" * 12 + "\x00" * 5),
            ([(0, 12)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["headings ", "unselected"],
            BrailleLine(4, "Do headings work?", "Do headings work?", "\xc0" * 3 + "\x00" * 14),
            ([(0, 3)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["Do ", "unselected"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=True,
        )
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_by_word_backward(atril: AtrilSession) -> None:
    """Checks selection by word backward."""

    with selection_session(atril, native=True):
        keyboard.tap_key(keyboard.KEYSYM_END)
        capture(atril)
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["work?", "selected"],
            BrailleLine(13, "Do headings work?", "Do headings work?", "\x00" * 12 + "\xc0" * 5),
            ([(12, 17)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["headings ", "selected"],
            BrailleLine(4, "Do headings work?", "Do headings work?", "\x00" * 3 + "\xc0" * 14),
            ([(3, 17)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["Do ", "selected"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 17),
            ([(0, 17)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_WORD,
            ["Do", "unselected"],
            BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 2 + "\xc0" * 15),
            ([(2, 17)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_WORD,
            [" headings", "unselected"],
            BrailleLine(12, "Do headings work?", "Do headings work?", "\x00" * 11 + "\xc0" * 6),
            ([(11, 17)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_WORD,
            [" work", "unselected"],
            BrailleLine(17, "Do headings work?", "Do headings work?", "\x00" * 16 + "\xc0"),
            ([(16, 17)], []),
            native=True,
        )
        assert say_selection(atril) == ["Selected text is:  ?"]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_line(atril: AtrilSession) -> None:
    """Checks selection by line."""

    with selection_session(atril, native=True):
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["Do headings work?", "selected"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nHello world.", "selected"],
            BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            ([(0, 30)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nI am a test.", "selected"],
            BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            ([(0, 43)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nLook, a link link! In a PDF.", "selected"],
            BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            ([(0, 67)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nAnother one! link", "selected"],
            BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            ([(0, 80)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nAnother one! link", "unselected"],
            BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            ([(0, 67)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nLook, a link link! In a PDF.", "unselected"],
            BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            ([(0, 43)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nI am a test.", "unselected"],
            BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            ([(0, 30)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nHello world.", "unselected"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Do headings work?", "unselected"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=True,
        )
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_line_across_pages(atril: AtrilSession) -> None:
    """Checks selection by line across pages."""

    with selection_session(atril, native=True):
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["Do headings work?", "selected"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nHello world.", "selected"],
            BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            ([(0, 30)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nI am a test.", "selected"],
            BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            ([(0, 43)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nLook, a link link! In a PDF.", "selected"],
            BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            ([(0, 67)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nAnother one! link", "selected"],
            BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            ([(0, 80)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nThe end.", "selected", "Page 2"],
            BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([(0, 89)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["More pages!", "selected"],
            BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            ([(0, 89)], [(0, 11)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nHere’s a new page.", "selected"],
            BrailleLine(1, "I really like pages.", "I really like pages.", "\x00" * 20),
            ([(0, 89)], [(0, 30)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nI really like pages.", "selected"],
            BrailleLine(21, "I really like pages.", "I really like pages.", "\xc0" * 20),
            ([(0, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nI really like pages.", "unselected"],
            BrailleLine(1, "I really like pages.", "I really like pages.", "\x00" * 20),
            ([(0, 89)], [(0, 30)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nHere’s a new page.", "unselected"],
            BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            ([(0, 89)], [(0, 11)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["More pages!", "unselected"],
            BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([(0, 89)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            [".", "unselected", "Page 1"],
            BrailleLine(8, "The end.", "The end.", "\xc0" * 7 + "\x00"),
            ([(0, 88)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nAnother one! link\nThe end", "unselected"],
            BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            ([(0, 67)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nLook, a link link! In a PDF.", "unselected"],
            BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            ([(0, 43)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nI am a test.", "unselected"],
            BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            ([(0, 30)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nHello world.", "unselected"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Do headings work?", "unselected"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=True,
        )
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_line_backward_across_pages(atril: AtrilSession) -> None:
    """Checks selection by line backward across pages."""

    with selection_session(atril, native=True, bottom=True):
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["I really like pages.", "selected"],
            BrailleLine(1, "I really like pages.", "I really like pages.", "\xc0" * 20),
            ([], [(31, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Here’s a new page.\n", "selected"],
            BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\xc0" * 18),
            ([], [(12, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["More pages!\n", "selected"],
            BrailleLine(1, "More pages!", "More pages!", "\xc0" * 11),
            ([], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            [".", "selected", "Page 1"],
            BrailleLine(8, "The end.", "The end.", "\x00" * 7 + "\xc0"),
            ([(88, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Another one! link\nThe end", "selected"],
            BrailleLine(1, "Another one!", "Another one!", "\xc0" * 12),
            ([(68, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Look, a link link! In a PDF.\n", "selected"],
            BrailleLine(1, "Look, a link! In a PDF.", "Look, a link! In a PDF.", "\xc0" * 23),
            ([(44, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["I am a test.\n", "selected"],
            BrailleLine(1, "I am a test.", "I am a test.", "\xc0" * 12),
            ([(31, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Hello world.\n", "selected"],
            BrailleLine(1, "Hello world.", "Hello world.", "\xc0" * 12),
            ([(18, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Do headings work?\n", "selected"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 17),
            ([(0, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["Do headings work?\n", "unselected"],
            BrailleLine(1, "Hello world.", "Hello world.", "\xc0" * 12),
            ([(18, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["Hello world.\n", "unselected"],
            BrailleLine(1, "I am a test.", "I am a test.", "\xc0" * 12),
            ([(31, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["I am a test.\n", "unselected"],
            BrailleLine(1, "Look, a link! In a PDF.", "Look, a link! In a PDF.", "\xc0" * 23),
            ([(44, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["Look, a link link! In a PDF.\n", "unselected"],
            BrailleLine(1, "Another one!", "Another one!", "\xc0" * 12),
            ([(68, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["Another one! link\n", "unselected"],
            BrailleLine(1, "The end.", "The end.", "\xc0" * 8),
            ([(81, 89)], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["The end.", "unselected", "Page 2"],
            BrailleLine(1, "More pages!", "More pages!", "\xc0" * 11),
            ([], [(0, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["More pages!\n", "unselected"],
            BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\xc0" * 18),
            ([], [(12, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["Here’s a new page.\n", "unselected"],
            BrailleLine(1, "I really like pages.", "I really like pages.", "\xc0" * 20),
            ([], [(31, 51)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["I really like pages.", "unselected"],
            BrailleLine(21, "I really like pages.", "I really like pages.", "\x00" * 20),
            ([], []),
            native=True,
        )
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_to_line_boundaries(atril: AtrilSession) -> None:
    """Checks selection to line boundaries."""

    with selection_session(atril, native=True):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        capture(atril)
        assert_step(
            atril,
            commands.END_OF_LINE,
            [" headings work?", "selected"],
            BrailleLine(18, "Do headings work?", "Do headings work?", "\x00" * 2 + "\xc0" * 15),
            ([(2, 17)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.START_OF_LINE,
            [" headings work?", "unselected", "Do", "selected"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15),
            ([(0, 2)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.END_OF_LINE,
            ["Do", "unselected", " headings work?", "selected"],
            BrailleLine(18, "Do headings work?", "Do headings work?", "\x00" * 2 + "\xc0" * 15),
            ([(2, 17)], []),
            native=True,
        )
        assert say_selection(atril) == ["Selected text is:   headings work?"]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_character_across_pages(atril: AtrilSession) -> None:
    """Checks selection by character across pages."""

    with selection_session(atril, native=True):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_END)
        capture(atril)
        assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["page More pages!", "Page 2"],
            BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["M", "selected"],
            BrailleLine(2, "More pages!", "More pages!", "\xc0" + "\x00" * 10),
            ([], [(0, 1)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["o", "selected"],
            BrailleLine(3, "More pages!", "More pages!", "\xc0" * 2 + "\x00" * 9),
            ([], [(0, 2)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["r", "selected"],
            BrailleLine(4, "More pages!", "More pages!", "\xc0" * 3 + "\x00" * 8),
            ([], [(0, 3)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["r", "unselected"],
            BrailleLine(3, "More pages!", "More pages!", "\xc0" * 2 + "\x00" * 9),
            ([], [(0, 2)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["o", "unselected"],
            BrailleLine(2, "More pages!", "More pages!", "\xc0" + "\x00" * 10),
            ([], [(0, 1)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["M", "unselected"],
            BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["page The end.", "Page 1"],
            BrailleLine(9, "The end.", "The end.", "\x00" * 8),
            ([], []),
            native=True,
        )
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "Atril native word selection can include an extra character on page two; "
        "collapsing it also leaves invalid selection ranges: "
        "https://github.com/mate-desktop/atril/issues/735"
    ),
)
def test_selection_by_word_across_pages(atril: AtrilSession) -> None:
    """Checks selection by word across pages."""

    with selection_session(atril, native=True):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_HOME)
        capture(atril)
        assert_step(
            atril,
            commands.NEXT_WORD,
            ["The", "selected"],
            BrailleLine(4, "The end.", "The end.", "\xc0" * 3 + "\x00" * 5),
            ([(81, 84)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_WORD,
            [" end", "selected"],
            BrailleLine(8, "The end.", "The end.", "\xc0" * 7 + "\x00"),
            ([(81, 88)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_WORD,
            [".", "selected", "More", "selected", "Page 2"],
            BrailleLine(5, "More pages!", "More pages!", "\xc0" * 4 + "\x00" * 7),
            ([(81, 89)], [(0, 4)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_WORD,
            [" pages", "selected"],
            BrailleLine(11, "More pages!", "More pages!", "\xc0" * 10 + "\x00"),
            ([(81, 89)], [(0, 10)]),
            native=True,
        )
        assert_step(
            atril,
            commands.NEXT_WORD,
            ["!\nHere", "selected"],
            BrailleLine(5, "Here’s a new page.", "Here’s a new page.", "\xc0" * 4 + "\x00" * 14),
            ([(81, 89)], [(0, 16)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["\nHere", "unselected"],
            BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            ([(81, 89)], [(0, 11)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["pages!", "unselected"],
            BrailleLine(6, "More pages!", "More pages!", "\xc0" * 5 + "\x00" * 6),
            ([(81, 89)], [(0, 5)]),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["More ", "unselected"],
            BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([(81, 89)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["end.", "unselected", "Page 1"],
            BrailleLine(5, "The end.", "The end.", "\xc0" * 4 + "\x00" * 4),
            ([(81, 85)], []),
            native=True,
        )
        assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["The ", "unselected"],
            BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            ([], []),
            native=True,
        )
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_cleared_after_character_selection(atril: AtrilSession) -> None:
    """Checks selection cleared after character selection."""

    with selection_session(atril, native=True):
        assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["D", "selected"],
            BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
            ([(0, 1)], []),
            native=True,
        )
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        spoken, brailled = capture(atril)
        assert selected_ranges(atril) == ([], [])
        assert spoken == ["Text unselected.", "o"]
        assert brailled[-1] == BrailleLine(2, "Do headings work?", "Do headings work?", "\x00" * 17)
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_cleared_after_word_selection(atril: AtrilSession) -> None:
    """Checks selection cleared after word selection."""

    with selection_session(atril, native=True):
        assert_step(
            atril,
            commands.NEXT_WORD,
            ["Do", "selected"],
            BrailleLine(3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15),
            ([(0, 2)], []),
            native=True,
        )
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        spoken, brailled = capture(atril)
        assert selected_ranges(atril) == ([], [])
        assert spoken == ["Text unselected.", " "]
        assert brailled[-1] == BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17)
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_cleared_after_line_selection(atril: AtrilSession) -> None:
    """Checks selection cleared after line selection."""

    with selection_session(atril, native=True):
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["Do headings work?", "selected"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=True,
        )
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, brailled = capture(atril)
        assert selected_ranges(atril) == ([], [])
        assert spoken == ["Text unselected.", "I am a test.\n"]
        assert brailled[-1] == BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12)
        assert say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_of_entire_document(atril: AtrilSession) -> None:
    """Checks selection of entire document."""

    with selection_session(atril, native=True):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
        spoken, brailled = capture(atril)
        assert selected_ranges(atril) == ([(0, 89)], [(0, 51)])
        assert spoken == ["entire document selected"]
        assert brailled[-1] == BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 17)


@pytest.mark.native_app
@pytest.mark.parametrize(
    "command, key, expected",
    [
        (commands.NEXT_CHARACTER, keyboard.KEYSYM_RIGHT, "D"),
        (commands.NEXT_WORD, keyboard.KEYSYM_RIGHT, "Do"),
        (commands.NEXT_LINE, keyboard.KEYSYM_DOWN, "Do headings work?"),
    ],
)
def test_say_selection(atril: AtrilSession, command: str, key: int, expected: str) -> None:
    """Reports the actual selected text after character, word, and line selection."""

    with selection_session(atril, native=True):
        modifiers = [keyboard.KEYSYM_SHIFT_L]
        if command == commands.NEXT_WORD:
            modifiers.insert(0, keyboard.KEYSYM_CONTROL_L)
        keyboard.press_chord(modifiers, key)
        capture(atril)
        assert selected_ranges(atril) == ([(0, len(expected))], [])
        assert say_selection(atril) == [f"Selected text is:  {expected}"]
