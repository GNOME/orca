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

from tests.integration_tests import atril_helpers, helpers
from tests.integration_tests import caret_selection_helpers as commands
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import AtrilSession


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

    with atril_helpers.selection_session(atril, native=True):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["D", "selected"],
            helpers.BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
            ([(0, 1)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["o", "selected"],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            [" ", "selected"],
            helpers.BrailleLine(
                4, "Do headings work?", "Do headings work?", "\xc0" * 3 + "\x00" * 14
            ),
            ([(0, 3)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            [" ", "unselected"],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["o", "unselected"],
            helpers.BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
            ([(0, 1)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["D", "unselected"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=True,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_character_backward(atril: AtrilSession) -> None:
    """Checks selection by character backward."""

    with atril_helpers.selection_session(atril, native=True):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        helpers.capture(atril)
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["o", "selected"],
            helpers.BrailleLine(
                2, "Do headings work?", "Do headings work?", "\x00" + "\xc0" + "\x00" * 15
            ),
            ([(1, 2)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["D", "selected"],
            helpers.BrailleLine(
                1, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["D", "unselected"],
            helpers.BrailleLine(
                2, "Do headings work?", "Do headings work?", "\x00" + "\xc0" + "\x00" * 15
            ),
            ([(1, 2)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["o", "unselected"],
            helpers.BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=True,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_word(atril: AtrilSession) -> None:
    """Checks selection by word."""

    with atril_helpers.selection_session(atril, native=True):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["Do", "selected"],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            [" headings", "selected"],
            helpers.BrailleLine(
                12, "Do headings work?", "Do headings work?", "\xc0" * 11 + "\x00" * 6
            ),
            ([(0, 11)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            [" work", "selected"],
            helpers.BrailleLine(17, "Do headings work?", "Do headings work?", "\xc0" * 16 + "\x00"),
            ([(0, 16)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["work", "unselected"],
            helpers.BrailleLine(
                13, "Do headings work?", "Do headings work?", "\xc0" * 12 + "\x00" * 5
            ),
            ([(0, 12)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["headings ", "unselected"],
            helpers.BrailleLine(
                4, "Do headings work?", "Do headings work?", "\xc0" * 3 + "\x00" * 14
            ),
            ([(0, 3)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["Do ", "unselected"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=True,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_by_word_backward(atril: AtrilSession) -> None:
    """Checks selection by word backward."""

    with atril_helpers.selection_session(atril, native=True):
        keyboard.tap_key(keyboard.KEYSYM_END)
        helpers.capture(atril)
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["work?", "selected"],
            helpers.BrailleLine(
                13, "Do headings work?", "Do headings work?", "\x00" * 12 + "\xc0" * 5
            ),
            ([(12, 17)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["headings ", "selected"],
            helpers.BrailleLine(
                4, "Do headings work?", "Do headings work?", "\x00" * 3 + "\xc0" * 14
            ),
            ([(3, 17)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["Do ", "selected"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 17),
            ([(0, 17)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["Do", "unselected"],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\x00" * 2 + "\xc0" * 15
            ),
            ([(2, 17)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            [" headings", "unselected"],
            helpers.BrailleLine(
                12, "Do headings work?", "Do headings work?", "\x00" * 11 + "\xc0" * 6
            ),
            ([(11, 17)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            [" work", "unselected"],
            helpers.BrailleLine(17, "Do headings work?", "Do headings work?", "\x00" * 16 + "\xc0"),
            ([(16, 17)], []),
            native=True,
        )
        assert helpers.say_selection(atril) == ["Selected text is:  ?"]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_line(atril: AtrilSession) -> None:
    """Checks selection by line."""

    with atril_helpers.selection_session(atril, native=True):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Do headings work?", "selected"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nHello world.", "selected"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            ([(0, 30)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nI am a test.", "selected"],
            helpers.BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            ([(0, 43)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nLook, a link link! In a PDF.", "selected"],
            helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            ([(0, 67)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nAnother one! link", "selected"],
            helpers.BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            ([(0, 80)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nAnother one! link", "unselected"],
            helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            ([(0, 67)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nLook, a link link! In a PDF.", "unselected"],
            helpers.BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            ([(0, 43)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nI am a test.", "unselected"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            ([(0, 30)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nHello world.", "unselected"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Do headings work?", "unselected"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=True,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_line_across_pages(atril: AtrilSession) -> None:
    """Checks selection by line across pages."""

    with atril_helpers.selection_session(atril, native=True):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Do headings work?", "selected"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nHello world.", "selected"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            ([(0, 30)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nI am a test.", "selected"],
            helpers.BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            ([(0, 43)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nLook, a link link! In a PDF.", "selected"],
            helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            ([(0, 67)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nAnother one! link", "selected"],
            helpers.BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            ([(0, 80)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nThe end.", "selected", "Page 2"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([(0, 89)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["More pages!", "selected"],
            helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            ([(0, 89)], [(0, 11)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nHere’s a new page.", "selected"],
            helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\x00" * 20),
            ([(0, 89)], [(0, 30)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["\nI really like pages.", "selected"],
            helpers.BrailleLine(21, "I really like pages.", "I really like pages.", "\xc0" * 20),
            ([(0, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nI really like pages.", "unselected"],
            helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\x00" * 20),
            ([(0, 89)], [(0, 30)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nHere’s a new page.", "unselected"],
            helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            ([(0, 89)], [(0, 11)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["More pages!", "unselected"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([(0, 89)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            [".", "unselected", "Page 1"],
            helpers.BrailleLine(8, "The end.", "The end.", "\xc0" * 7 + "\x00"),
            ([(0, 88)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nAnother one! link\nThe end", "unselected"],
            helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            ([(0, 67)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nLook, a link link! In a PDF.", "unselected"],
            helpers.BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            ([(0, 43)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nI am a test.", "unselected"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            ([(0, 30)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["\nHello world.", "unselected"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Do headings work?", "unselected"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=True,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_line_backward_across_pages(atril: AtrilSession) -> None:
    """Checks selection by line backward across pages."""

    with atril_helpers.selection_session(atril, native=True, bottom=True):
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["I really like pages.", "selected"],
            helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\xc0" * 20),
            ([], [(31, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Here’s a new page.\n", "selected"],
            helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\xc0" * 18),
            ([], [(12, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["More pages!\n", "selected"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\xc0" * 11),
            ([], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            [".", "selected", "Page 1"],
            helpers.BrailleLine(8, "The end.", "The end.", "\x00" * 7 + "\xc0"),
            ([(88, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Another one! link\nThe end", "selected"],
            helpers.BrailleLine(1, "Another one!", "Another one!", "\xc0" * 12),
            ([(68, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Look, a link link! In a PDF.\n", "selected"],
            helpers.BrailleLine(
                1, "Look, a link! In a PDF.", "Look, a link! In a PDF.", "\xc0" * 23
            ),
            ([(44, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["I am a test.\n", "selected"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\xc0" * 12),
            ([(31, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Hello world.\n", "selected"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\xc0" * 12),
            ([(18, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Do headings work?\n", "selected"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 17),
            ([(0, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Do headings work?\n", "unselected"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\xc0" * 12),
            ([(18, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Hello world.\n", "unselected"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\xc0" * 12),
            ([(31, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["I am a test.\n", "unselected"],
            helpers.BrailleLine(
                1, "Look, a link! In a PDF.", "Look, a link! In a PDF.", "\xc0" * 23
            ),
            ([(44, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Look, a link link! In a PDF.\n", "unselected"],
            helpers.BrailleLine(1, "Another one!", "Another one!", "\xc0" * 12),
            ([(68, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Another one! link\n", "unselected"],
            helpers.BrailleLine(1, "The end.", "The end.", "\xc0" * 8),
            ([(81, 89)], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["The end.", "unselected", "Page 2"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\xc0" * 11),
            ([], [(0, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["More pages!\n", "unselected"],
            helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\xc0" * 18),
            ([], [(12, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Here’s a new page.\n", "unselected"],
            helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\xc0" * 20),
            ([], [(31, 51)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["I really like pages.", "unselected"],
            helpers.BrailleLine(21, "I really like pages.", "I really like pages.", "\x00" * 20),
            ([], []),
            native=True,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_to_line_boundaries(atril: AtrilSession) -> None:
    """Checks selection to line boundaries."""

    with atril_helpers.selection_session(atril, native=True):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        helpers.capture(atril)
        atril_helpers.assert_step(
            atril,
            commands.END_OF_LINE,
            [" headings work?", "selected"],
            helpers.BrailleLine(
                18, "Do headings work?", "Do headings work?", "\x00" * 2 + "\xc0" * 15
            ),
            ([(2, 17)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.START_OF_LINE,
            [" headings work?", "unselected", "Do", "selected"],
            helpers.BrailleLine(
                1, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.END_OF_LINE,
            ["Do", "unselected", " headings work?", "selected"],
            helpers.BrailleLine(
                18, "Do headings work?", "Do headings work?", "\x00" * 2 + "\xc0" * 15
            ),
            ([(2, 17)], []),
            native=True,
        )
        assert helpers.say_selection(atril) == ["Selected text is:   headings work?"]


@pytest.mark.native_app
@_COLLAPSED_SELECTION_BUG
def test_selection_by_character_across_pages(atril: AtrilSession) -> None:
    """Checks selection by character across pages."""

    with atril_helpers.selection_session(atril, native=True):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_END)
        helpers.capture(atril)
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["page More pages!", "Page 2"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["M", "selected"],
            helpers.BrailleLine(2, "More pages!", "More pages!", "\xc0" + "\x00" * 10),
            ([], [(0, 1)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["o", "selected"],
            helpers.BrailleLine(3, "More pages!", "More pages!", "\xc0" * 2 + "\x00" * 9),
            ([], [(0, 2)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["r", "selected"],
            helpers.BrailleLine(4, "More pages!", "More pages!", "\xc0" * 3 + "\x00" * 8),
            ([], [(0, 3)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["r", "unselected"],
            helpers.BrailleLine(3, "More pages!", "More pages!", "\xc0" * 2 + "\x00" * 9),
            ([], [(0, 2)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["o", "unselected"],
            helpers.BrailleLine(2, "More pages!", "More pages!", "\xc0" + "\x00" * 10),
            ([], [(0, 1)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["M", "unselected"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["page The end.", "Page 1"],
            helpers.BrailleLine(9, "The end.", "The end.", "\x00" * 8),
            ([], []),
            native=True,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


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

    with atril_helpers.selection_session(atril, native=True):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_HOME)
        helpers.capture(atril)
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["The", "selected"],
            helpers.BrailleLine(4, "The end.", "The end.", "\xc0" * 3 + "\x00" * 5),
            ([(81, 84)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            [" end", "selected"],
            helpers.BrailleLine(8, "The end.", "The end.", "\xc0" * 7 + "\x00"),
            ([(81, 88)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            [".", "selected", "More", "selected", "Page 2"],
            helpers.BrailleLine(5, "More pages!", "More pages!", "\xc0" * 4 + "\x00" * 7),
            ([(81, 89)], [(0, 4)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            [" pages", "selected"],
            helpers.BrailleLine(11, "More pages!", "More pages!", "\xc0" * 10 + "\x00"),
            ([(81, 89)], [(0, 10)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["!\nHere", "selected"],
            helpers.BrailleLine(
                5, "Here’s a new page.", "Here’s a new page.", "\xc0" * 4 + "\x00" * 14
            ),
            ([(81, 89)], [(0, 16)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["\nHere", "unselected"],
            helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            ([(81, 89)], [(0, 11)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["pages!", "unselected"],
            helpers.BrailleLine(6, "More pages!", "More pages!", "\xc0" * 5 + "\x00" * 6),
            ([(81, 89)], [(0, 5)]),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["More ", "unselected"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([(81, 89)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["end.", "unselected", "Page 1"],
            helpers.BrailleLine(5, "The end.", "The end.", "\xc0" * 4 + "\x00" * 4),
            ([(81, 85)], []),
            native=True,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["The ", "unselected"],
            helpers.BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            ([], []),
            native=True,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_cleared_after_character_selection(atril: AtrilSession) -> None:
    """Checks selection cleared after character selection."""

    with atril_helpers.selection_session(atril, native=True):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["D", "selected"],
            helpers.BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
            ([(0, 1)], []),
            native=True,
        )
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        spoken, brailled = helpers.capture(atril)
        assert atril_helpers.selected_ranges(atril) == ([], [])
        assert spoken == ["Text unselected.", "o"]
        assert brailled[-1] == helpers.BrailleLine(
            2, "Do headings work?", "Do headings work?", "\x00" * 17
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_cleared_after_word_selection(atril: AtrilSession) -> None:
    """Checks selection cleared after word selection."""

    with atril_helpers.selection_session(atril, native=True):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["Do", "selected"],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=True,
        )
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        spoken, brailled = helpers.capture(atril)
        assert atril_helpers.selected_ranges(atril) == ([], [])
        assert spoken == ["Text unselected.", " "]
        assert brailled[-1] == helpers.BrailleLine(
            3, "Do headings work?", "Do headings work?", "\x00" * 17
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_cleared_after_line_selection(atril: AtrilSession) -> None:
    """Checks selection cleared after line selection."""

    with atril_helpers.selection_session(atril, native=True):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Do headings work?", "selected"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=True,
        )
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, brailled = helpers.capture(atril)
        assert atril_helpers.selected_ranges(atril) == ([], [])
        assert spoken == ["Text unselected.", "I am a test.\n"]
        assert brailled[-1] == helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12)
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
def test_selection_of_entire_document(atril: AtrilSession) -> None:
    """Checks selection of entire document."""

    with atril_helpers.selection_session(atril, native=True):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
        spoken, brailled = helpers.capture(atril)
        assert spoken == ["entire document selected"]
        assert brailled[-1] == helpers.BrailleLine(
            1, "Do headings work?", "Do headings work?", "\xc0" * 17
        )


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

    with atril_helpers.selection_session(atril, native=True):
        modifiers = [keyboard.KEYSYM_SHIFT_L]
        if command == commands.NEXT_WORD:
            modifiers.insert(0, keyboard.KEYSYM_CONTROL_L)
        keyboard.press_chord(modifiers, key)
        helpers.capture(atril)
        assert atril_helpers.selected_ranges(atril) == ([(0, len(expected))], [])
        assert helpers.say_selection(atril) == [f"Selected text is:  {expected}"]
