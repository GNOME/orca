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

"""Tests Orca-driven Atril selection in a two-page PDF."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import atril_helpers, helpers, version_helpers
from tests.integration_tests import caret_selection_helpers as commands
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import AtrilSession


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_by_character(atril: AtrilSession) -> None:
    """Checks selection by character."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["D", "selected"],
            helpers.BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
            ([(0, 1)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["o", "selected"],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            [" ", "selected"],
            helpers.BrailleLine(
                4, "Do headings work?", "Do headings work?", "\xc0" * 3 + "\x00" * 14
            ),
            ([(0, 3)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            [" ", "unselected"],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["o", "unselected"],
            helpers.BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
            ([(0, 1)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["D", "unselected"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=False,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_by_character_backward(atril: AtrilSession) -> None:
    """Checks selection by character backward."""

    with atril_helpers.selection_session(atril, native=False):
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
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["D", "selected"],
            helpers.BrailleLine(
                1, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["D", "unselected"],
            helpers.BrailleLine(
                2, "Do headings work?", "Do headings work?", "\x00" + "\xc0" + "\x00" * 15
            ),
            ([(1, 2)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["o", "unselected"],
            helpers.BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=False,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_by_word(atril: AtrilSession) -> None:
    """Checks selection by word."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["Do", "selected"],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["headings", "selected"],
            helpers.BrailleLine(
                12, "Do headings work?", "Do headings work?", "\xc0" * 11 + "\x00" * 6
            ),
            ([(0, 11)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["work?", "selected"],
            helpers.BrailleLine(18, "Do headings work?", "Do headings work?", "\xc0" * 17),
            ([(0, 17)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["work?", "unselected"],
            helpers.BrailleLine(
                13, "Do headings work?", "Do headings work?", "\xc0" * 12 + "\x00" * 5
            ),
            ([(0, 12)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["headings", "unselected"],
            helpers.BrailleLine(
                4, "Do headings work?", "Do headings work?", "\xc0" * 3 + "\x00" * 14
            ),
            ([(0, 3)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["Do", "unselected"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=False,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_by_word_backward(atril: AtrilSession) -> None:
    """Checks selection by word backward."""

    with atril_helpers.selection_session(atril, native=False):
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
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["headings", "selected"],
            helpers.BrailleLine(
                4, "Do headings work?", "Do headings work?", "\x00" * 3 + "\xc0" * 14
            ),
            ([(3, 17)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["Do", "selected"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 17),
            ([(0, 17)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["Do", "unselected"],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\x00" * 2 + "\xc0" * 15
            ),
            ([(2, 17)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["headings", "unselected"],
            helpers.BrailleLine(
                12, "Do headings work?", "Do headings work?", "\x00" * 11 + "\xc0" * 6
            ),
            ([(11, 17)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["work?", "unselected"],
            helpers.BrailleLine(18, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=False,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_by_line(atril: AtrilSession) -> None:
    """Checks selection by line."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Do headings work?", "selected"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Hello world.", "selected"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            ([(0, 30)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["I am a test.", "selected"],
            helpers.BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            ([(0, 43)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Look, a link! link In a PDF.", "selected"],
            helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            ([(0, 67)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Another one!", "selected"],
            helpers.BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            ([(0, 80)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Another one!", "unselected"],
            helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            ([(0, 67)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Look, a link! link In a PDF.", "unselected"],
            helpers.BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            ([(0, 43)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["I am a test.", "unselected"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            ([(0, 30)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Hello world.", "unselected"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Do headings work?", "unselected"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            ([], []),
            native=False,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_to_line_boundaries(atril: AtrilSession) -> None:
    """Checks selection to line boundaries."""

    with atril_helpers.selection_session(atril, native=False):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        helpers.capture(atril)
        atril_helpers.assert_step(
            atril,
            commands.END_OF_LINE,
            ["headings work?", "selected"],
            helpers.BrailleLine(
                18, "Do headings work?", "Do headings work?", "\x00" * 2 + "\xc0" * 15
            ),
            ([(2, 17)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.START_OF_LINE,
            [" headings work?", "unselected", "Do", "selected"],
            helpers.BrailleLine(
                1, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.END_OF_LINE,
            ["Do", "unselected", " headings work?", "selected"],
            helpers.BrailleLine(
                18, "Do headings work?", "Do headings work?", "\x00" * 2 + "\xc0" * 15
            ),
            ([(2, 17)], []),
            native=False,
        )
        assert helpers.say_selection(atril) == ["Selected text is:   headings work?"]


@pytest.mark.native_app
def test_selection_cleared_after_character_selection(atril: AtrilSession) -> None:
    """Checks selection cleared after character selection."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["D", "selected"],
            helpers.BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
            ([(0, 1)], []),
            native=False,
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

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["Do", "selected"],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=False,
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

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Do headings work?", "selected"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=False,
        )
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, brailled = helpers.capture(atril)
        assert atril_helpers.selected_ranges(atril) == ([], [])
        assert spoken == ["Text unselected.", "I am a test.\n"]
        assert brailled[-1] == helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12)
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_without_notification(atril: AtrilSession) -> None:
    """Checks selection without notification."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            [],
            helpers.BrailleLine(
                3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
            ),
            ([(0, 2)], []),
            native=False,
            notify_user=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            [],
            helpers.BrailleLine(
                12, "Do headings work?", "Do headings work?", "\xc0" * 11 + "\x00" * 6
            ),
            ([(0, 11)], []),
            native=False,
            notify_user=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            [],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            ([(0, 17)], []),
            native=False,
            notify_user=False,
        )
        assert helpers.say_selection(atril) == ["Selected text is:  Do headings work?"]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_words_on_second_page(atril: AtrilSession) -> None:
    """Checks words selection and reversal on a displayed second page."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["More", "selected"],
            helpers.BrailleLine(5, "More pages!", "More pages!", "\xc0" * 4 + "\x00" * 7),
            ([], [(0, 4)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["pages!", "selected"],
            helpers.BrailleLine(12, "More pages!", "More pages!", "\xc0" * 11),
            ([], [(0, 11)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["pages!", "unselected"],
            helpers.BrailleLine(6, "More pages!", "More pages!", "\xc0" * 5 + "\x00" * 6),
            ([], [(0, 5)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_WORD,
            ["More", "unselected"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([], []),
            native=False,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_lines_on_second_page(atril: AtrilSession) -> None:
    """Checks lines selection and reversal on a displayed second page."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["More pages!", "selected"],
            helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            ([], [(0, 11)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_LINE,
            ["Here’s a new page.", "selected"],
            helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\x00" * 20),
            ([], [(0, 30)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["Here’s a new page.", "unselected"],
            helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            ([], [(0, 11)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_LINE,
            ["More pages!", "unselected"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([], []),
            native=False,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_unicode_on_second_page(atril: AtrilSession) -> None:
    """Checks unicode selection and reversal on a displayed second page."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        for _ in range(4):
            keyboard.tap_key(keyboard.KEYSYM_RIGHT)
            helpers.capture(atril)
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["’", "selected"],
            helpers.BrailleLine(
                6, "Here’s a new page.", "Here’s a new page.", "\x00" * 4 + "\xc0" + "\x00" * 13
            ),
            ([], [(16, 17)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["s", "selected"],
            helpers.BrailleLine(
                7, "Here’s a new page.", "Here’s a new page.", "\x00" * 4 + "\xc0" * 2 + "\x00" * 12
            ),
            ([], [(16, 18)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["s", "unselected"],
            helpers.BrailleLine(
                6, "Here’s a new page.", "Here’s a new page.", "\x00" * 4 + "\xc0" + "\x00" * 13
            ),
            ([], [(16, 17)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["’", "unselected"],
            helpers.BrailleLine(5, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            ([], []),
            native=False,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_by_character_across_pages(atril: AtrilSession) -> None:
    """Extends into the displayed second page, then shrinks back to no selection."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        helpers.move_to_top(atril)
        for _ in range(5):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_END)
        helpers.capture(atril)
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["M", "selected"],
            helpers.BrailleLine(2, "More pages!", "More pages!", "\xc0" + "\x00" * 10),
            ([], [(0, 1)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["o", "selected"],
            helpers.BrailleLine(3, "More pages!", "More pages!", "\xc0" * 2 + "\x00" * 9),
            ([], [(0, 2)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["r", "selected"],
            helpers.BrailleLine(4, "More pages!", "More pages!", "\xc0" * 3 + "\x00" * 8),
            ([], [(0, 3)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.NEXT_CHARACTER,
            ["e", "selected"],
            helpers.BrailleLine(5, "More pages!", "More pages!", "\xc0" * 4 + "\x00" * 7),
            ([], [(0, 4)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["e", "unselected"],
            helpers.BrailleLine(4, "More pages!", "More pages!", "\xc0" * 3 + "\x00" * 8),
            ([], [(0, 3)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["r", "unselected"],
            helpers.BrailleLine(3, "More pages!", "More pages!", "\xc0" * 2 + "\x00" * 9),
            ([], [(0, 2)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["o", "unselected"],
            helpers.BrailleLine(2, "More pages!", "More pages!", "\xc0" + "\x00" * 10),
            ([], [(0, 1)]),
            native=False,
        )
        atril_helpers.assert_step(
            atril,
            commands.PREVIOUS_CHARACTER,
            ["M", "unselected"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            ([], []),
            native=False,
        )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_ranges_and_braille_pages_forward(atril: AtrilSession) -> None:
    """Checks both pages through extension and reversal with notifications disabled."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        helpers.move_to_top(atril)
        steps = [
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
                ([(0, 17)], []),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
                ([(0, 30)], []),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(
                    1,
                    "Look, a link! In a PDF.",
                    "Look, a link! In a PDF.",
                    "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
                ),
                ([(0, 43)], []),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
                ([(0, 67)], []),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "The end.", "The end.", "\x00" * 8),
                ([(0, 80)], []),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
                ([(0, 89)], []),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
                ([(0, 89)], [(0, 11)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\x00" * 20),
                ([(0, 89)], [(0, 30)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(
                    21, "I really like pages.", "I really like pages.", "\xc0" * 20
                ),
                ([(0, 89)], [(0, 51)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\x00" * 20),
                ([(0, 89)], [(0, 30)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
                ([(0, 89)], [(0, 11)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
                ([(0, 89)], []),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "The end.", "The end.", "\x00" * 8),
                ([(0, 80)], []),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
                ([(0, 67)], []),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(
                    1,
                    "Look, a link! In a PDF.",
                    "Look, a link! In a PDF.",
                    "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
                ),
                ([(0, 43)], []),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
                ([(0, 30)], []),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
                ([(0, 17)], []),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
                ([], []),
            ),
        ]
        for command, expected_braille, expected_ranges in steps:
            atril_helpers.assert_step(
                atril,
                command,
                [],
                expected_braille,
                expected_ranges,
                native=False,
                notify_user=False,
            )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_ranges_and_braille_pages_backward(atril: AtrilSession) -> None:
    """Checks both pages through extension and reversal with notifications disabled."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        helpers.move_to_top(atril)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
        helpers.capture(atril)
        steps = [
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\xc0" * 20),
                ([], [(31, 51)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\xc0" * 18),
                ([], [(12, 51)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "More pages!", "More pages!", "\xc0" * 11),
                ([], [(0, 51)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "The end.", "The end.", "\xc0" * 8),
                ([(81, 89)], [(0, 51)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "Another one!", "Another one!", "\xc0" * 12),
                ([(68, 89)], [(0, 51)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(
                    1, "Look, a link! In a PDF.", "Look, a link! In a PDF.", "\xc0" * 23
                ),
                ([(44, 89)], [(0, 51)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "I am a test.", "I am a test.", "\xc0" * 12),
                ([(31, 89)], [(0, 51)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "Hello world.", "Hello world.", "\xc0" * 12),
                ([(18, 89)], [(0, 51)]),
            ),
            (
                commands.PREVIOUS_LINE,
                helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 17),
                ([(0, 89)], [(0, 51)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "Hello world.", "Hello world.", "\xc0" * 12),
                ([(18, 89)], [(0, 51)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "I am a test.", "I am a test.", "\xc0" * 12),
                ([(31, 89)], [(0, 51)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(
                    1, "Look, a link! In a PDF.", "Look, a link! In a PDF.", "\xc0" * 23
                ),
                ([(44, 89)], [(0, 51)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "Another one!", "Another one!", "\xc0" * 12),
                ([(68, 89)], [(0, 51)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "The end.", "The end.", "\xc0" * 8),
                ([(81, 89)], [(0, 51)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "More pages!", "More pages!", "\xc0" * 11),
                ([], [(0, 51)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\xc0" * 18),
                ([], [(12, 51)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\xc0" * 20),
                ([], [(31, 51)]),
            ),
            (
                commands.NEXT_LINE,
                helpers.BrailleLine(
                    21, "I really like pages.", "I really like pages.", "\x00" * 20
                ),
                ([], []),
            ),
        ]
        for command, expected_braille, expected_ranges in steps:
            atril_helpers.assert_step(
                atril,
                command,
                [],
                expected_braille,
                expected_ranges,
                native=False,
                notify_user=False,
            )
        assert helpers.say_selection(atril) == ["No selected text."]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_selection_ranges_and_braille_file_boundaries(atril: AtrilSession) -> None:
    """Checks both pages through extension and reversal with notifications disabled."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        helpers.move_to_top(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_HOME)
        helpers.capture(atril)
        steps = [
            (
                commands.END_OF_FILE,
                helpers.BrailleLine(
                    21, "I really like pages.", "I really like pages.", "\xc0" * 20
                ),
                ([(18, 89)], [(0, 51)]),
            ),
            (
                commands.START_OF_FILE,
                helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 17),
                ([(0, 17)], []),
            ),
            (
                commands.END_OF_FILE,
                helpers.BrailleLine(
                    21, "I really like pages.", "I really like pages.", "\xc0" * 20
                ),
                ([(18, 89)], [(0, 51)]),
            ),
        ]
        for command, expected_braille, expected_ranges in steps:
            atril_helpers.assert_step(
                atril,
                command,
                [],
                expected_braille,
                expected_ranges,
                native=False,
                notify_user=False,
            )


@pytest.mark.native_app
@pytest.mark.parametrize(
    "command, _key, expected",
    [
        (commands.NEXT_CHARACTER, keyboard.KEYSYM_RIGHT, "D"),
        (commands.NEXT_WORD, keyboard.KEYSYM_RIGHT, "Do"),
        (commands.NEXT_LINE, keyboard.KEYSYM_DOWN, "Do headings work?"),
    ],
)
def test_say_selection(atril: AtrilSession, command: str, _key: int, expected: str) -> None:
    """Reports the actual selected text after character, word, and line selection."""

    with atril_helpers.selection_session(atril, native=False):
        atril.orca.select_with_caret_navigator(command)
        helpers.capture(atril)
        assert atril_helpers.selected_ranges(atril) == ([(0, len(expected))], [])
        assert helpers.say_selection(atril) == [f"Selected text is:  {expected}"]


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_line_selection_speech_pages_forward(atril: AtrilSession) -> None:
    """Announces each newly selected line while extending through both displayed pages."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        helpers.move_to_top(atril)
        steps = [
            (
                ["Do headings work?", "selected"],
                helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
                ([(0, 17)], []),
            ),
            (
                ["Hello world.", "selected"],
                helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
                ([(0, 30)], []),
            ),
            (
                ["I am a test.", "selected"],
                helpers.BrailleLine(
                    1,
                    "Look, a link! In a PDF.",
                    "Look, a link! In a PDF.",
                    "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
                ),
                ([(0, 43)], []),
            ),
            (
                ["Look, a link! link In a PDF.", "selected"],
                helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
                ([(0, 67)], []),
            ),
            (
                ["Another one!", "selected"],
                helpers.BrailleLine(1, "The end.", "The end.", "\x00" * 8),
                ([(0, 80)], []),
            ),
            (
                ["The end.", "selected"],
                helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
                ([(0, 89)], []),
            ),
            (
                ["More pages!", "selected"],
                helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
                ([(0, 89)], [(0, 11)]),
            ),
            (
                ["Here’s a new page.", "selected"],
                helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\x00" * 20),
                ([(0, 89)], [(0, 30)]),
            ),
            (
                ["I really like pages.", "selected"],
                helpers.BrailleLine(
                    21, "I really like pages.", "I really like pages.", "\xc0" * 20
                ),
                ([(0, 89)], [(0, 51)]),
            ),
        ]
        for spoken, brailled, ranges in steps:
            atril_helpers.assert_step(
                atril, commands.NEXT_LINE, spoken, brailled, ranges, native=False
            )


@pytest.mark.native_app
@version_helpers.requires_atril_version(1, 28, 7)
def test_line_selection_speech_pages_backward(atril: AtrilSession) -> None:
    """Announces each newly selected line while extending through both displayed pages."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        helpers.move_to_top(atril)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
        helpers.capture(atril)
        steps = [
            (
                ["I really like pages.", "selected"],
                helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\xc0" * 20),
                ([], [(31, 51)]),
            ),
            (
                ["Here’s a new page.", "selected"],
                helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\xc0" * 18),
                ([], [(12, 51)]),
            ),
            (
                ["More pages!", "selected"],
                helpers.BrailleLine(1, "More pages!", "More pages!", "\xc0" * 11),
                ([], [(0, 51)]),
            ),
            (
                ["The end.", "selected"],
                helpers.BrailleLine(1, "The end.", "The end.", "\xc0" * 8),
                ([(81, 89)], [(0, 51)]),
            ),
            (
                ["Another one! link", "selected"],
                helpers.BrailleLine(1, "Another one!", "Another one!", "\xc0" * 12),
                ([(68, 89)], [(0, 51)]),
            ),
            (
                ["Look, a link link! In a PDF.", "selected"],
                helpers.BrailleLine(
                    1, "Look, a link! In a PDF.", "Look, a link! In a PDF.", "\xc0" * 23
                ),
                ([(44, 89)], [(0, 51)]),
            ),
            (
                ["I am a test.", "selected"],
                helpers.BrailleLine(1, "I am a test.", "I am a test.", "\xc0" * 12),
                ([(31, 89)], [(0, 51)]),
            ),
            (
                ["Hello world.", "selected"],
                helpers.BrailleLine(1, "Hello world.", "Hello world.", "\xc0" * 12),
                ([(18, 89)], [(0, 51)]),
            ),
            (
                ["Do headings work?", "selected"],
                helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\xc0" * 17),
                ([(0, 89)], [(0, 51)]),
            ),
        ]
        for spoken, brailled, ranges in steps:
            atril_helpers.assert_step(
                atril, commands.PREVIOUS_LINE, spoken, brailled, ranges, native=False
            )
