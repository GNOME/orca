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

"""Tests native Atril caret navigation without selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .atril_helpers import assert_navigation, navigation_session
from .harness import keyboard
from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import AtrilSession


@pytest.mark.native_app
def test_lines_across_pages(atril: AtrilSession) -> None:
    """Checks lines across pages without creating a selection."""

    with navigation_session(atril, native=True):
        assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["Hello world.\n"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["I am a test.\n"],
            BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            (31, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["Look, a link link! In a PDF.\n"],
            BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (44, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["Another one! link\n"],
            BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            (68, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["The end."],
            BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            (81, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["More pages!\n"],
            BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            (-1, 0),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["Here’s a new page.\n"],
            BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 12),
        )
        # Speech is checked separately in test_last_line_speech.
        assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            None,
            BrailleLine(1, "I really like pages.", "I really like pages.", "\x00" * 20),
            (-1, 31),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["Here’s a new page.\n"],
            BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 12),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["More pages!\n"],
            BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            (-1, 0),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["The end."],
            BrailleLine(8, "The end.", "The end.", "\x00" * 8),
            (88, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["Another one! link\n"],
            BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            (68, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["Look, a link link! In a PDF.\n"],
            BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (44, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["I am a test.\n"],
            BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            (31, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["Hello world.\n"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["Do headings work?\n"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            (0, -1),
        )


@pytest.mark.native_app
def test_characters(atril: AtrilSession) -> None:
    """Checks characters without creating a selection."""

    with navigation_session(atril, native=True):
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["o"],
            BrailleLine(2, "Do headings work?", "Do headings work?", "\x00" * 17),
            (1, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            [" "],
            BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17),
            (2, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["h"],
            BrailleLine(4, "Do headings work?", "Do headings work?", "\x00" * 17),
            (3, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["e"],
            BrailleLine(5, "Do headings work?", "Do headings work?", "\x00" * 17),
            (4, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["h"],
            BrailleLine(4, "Do headings work?", "Do headings work?", "\x00" * 17),
            (3, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            [" "],
            BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17),
            (2, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["o"],
            BrailleLine(2, "Do headings work?", "Do headings work?", "\x00" * 17),
            (1, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["D"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            (0, -1),
        )


@pytest.mark.native_app
def test_words(atril: AtrilSession) -> None:
    """Checks words without creating a selection."""

    with navigation_session(atril, native=True):
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Do"],
            BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17),
            (2, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["headings"],
            BrailleLine(12, "Do headings work?", "Do headings work?", "\x00" * 17),
            (11, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["work"],
            BrailleLine(17, "Do headings work?", "Do headings work?", "\x00" * 17),
            (16, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["?\nHello"],
            BrailleLine(6, "Hello world.", "Hello world.", "\x00" * 12),
            (23, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["world"],
            BrailleLine(12, "Hello world.", "Hello world.", "\x00" * 12),
            (29, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["world"],
            BrailleLine(7, "Hello world.", "Hello world.", "\x00" * 12),
            (24, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Hello"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["work?"],
            BrailleLine(13, "Do headings work?", "Do headings work?", "\x00" * 17),
            (12, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["headings"],
            BrailleLine(4, "Do headings work?", "Do headings work?", "\x00" * 17),
            (3, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Do"],
            BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            (0, -1),
        )


@pytest.mark.native_app
def test_line_boundaries(atril: AtrilSession) -> None:
    """Checks line boundaries without creating a selection."""

    with navigation_session(atril, native=True):
        keyboard.press_chord([], keyboard.KEYSYM_DOWN)
        capture(atril)
        for _ in range(4):
            keyboard.press_chord([], keyboard.KEYSYM_RIGHT)
            capture(atril)
        assert_navigation(
            atril,
            keyboard.KEYSYM_END,
            [],
            ["blank"],
            BrailleLine(13, "Hello world.", "Hello world.", "\x00" * 12),
            (30, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_HOME,
            [],
            ["H"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_END,
            [],
            ["blank"],
            BrailleLine(13, "Hello world.", "Hello world.", "\x00" * 12),
            (30, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_HOME,
            [],
            ["H"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )


@pytest.mark.native_app
def test_characters_across_lines(atril: AtrilSession) -> None:
    """Checks characters across lines without creating a selection."""

    with navigation_session(atril, native=True):
        keyboard.press_chord([], keyboard.KEYSYM_END)
        capture(atril)
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["H"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["e"],
            BrailleLine(2, "Hello world.", "Hello world.", "\x00" * 12),
            (19, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["l"],
            BrailleLine(3, "Hello world.", "Hello world.", "\x00" * 12),
            (20, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["e"],
            BrailleLine(2, "Hello world.", "Hello world.", "\x00" * 12),
            (19, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["H"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["blank"],
            BrailleLine(18, "Do headings work?", "Do headings work?", "\x00" * 17),
            (17, -1),
        )


@pytest.mark.native_app
def test_words_across_lines(atril: AtrilSession) -> None:
    """Checks words across lines without creating a selection."""

    with navigation_session(atril, native=True):
        keyboard.press_chord([], keyboard.KEYSYM_END)
        capture(atril)
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Hello"],
            BrailleLine(6, "Hello world.", "Hello world.", "\x00" * 12),
            (23, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["world"],
            BrailleLine(12, "Hello world.", "Hello world.", "\x00" * 12),
            (29, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            [".\nI"],
            BrailleLine(2, "I am a test.", "I am a test.", "\x00" * 12),
            (32, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["I"],
            BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            (31, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["world."],
            BrailleLine(7, "Hello world.", "Hello world.", "\x00" * 12),
            (24, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Hello"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )


@pytest.mark.native_app
def test_characters_across_pages(atril: AtrilSession) -> None:
    """Checks characters across pages without creating a selection."""

    with navigation_session(atril, native=True):
        for _ in range(5):
            keyboard.press_chord([], keyboard.KEYSYM_DOWN)
            capture(atril)
        keyboard.press_chord([], keyboard.KEYSYM_END)
        capture(atril)
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["M"],
            BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            (-1, 0),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["o"],
            BrailleLine(2, "More pages!", "More pages!", "\x00" * 11),
            (-1, 1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["r"],
            BrailleLine(3, "More pages!", "More pages!", "\x00" * 11),
            (-1, 2),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["o"],
            BrailleLine(2, "More pages!", "More pages!", "\x00" * 11),
            (-1, 1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["M"],
            BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            (-1, 0),
        )
        # Speech is checked separately in test_previous_page_end_speech.
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            None,
            BrailleLine(9, "The end.", "The end.", "\x00" * 8),
            (89, -1),
        )


@pytest.mark.native_app
def test_words_across_pages(atril: AtrilSession) -> None:
    """Checks words across pages without creating a selection."""

    with navigation_session(atril, native=True):
        for _ in range(5):
            keyboard.press_chord([], keyboard.KEYSYM_DOWN)
            capture(atril)
        keyboard.press_chord([], keyboard.KEYSYM_HOME)
        capture(atril)
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["The"],
            BrailleLine(4, "The end.", "The end.", "\x00" * 8),
            (84, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["end"],
            BrailleLine(8, "The end.", "The end.", "\x00" * 8),
            (88, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["More"],
            BrailleLine(5, "More pages!", "More pages!", "\x00" * 11),
            (-1, 4),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["pages"],
            BrailleLine(11, "More pages!", "More pages!", "\x00" * 11),
            (-1, 10),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["!\nHere"],
            BrailleLine(5, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 16),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Here"],
            BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 12),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["pages!"],
            BrailleLine(6, "More pages!", "More pages!", "\x00" * 11),
            (-1, 5),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["More"],
            BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            (-1, 0),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["end."],
            BrailleLine(5, "The end.", "The end.", "\x00" * 8),
            (85, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["The"],
            BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            (81, -1),
        )


@pytest.mark.native_app
def test_unicode(atril: AtrilSession) -> None:
    """Checks unicode without creating a selection."""

    with navigation_session(atril, native=True):
        for _ in range(7):
            keyboard.press_chord([], keyboard.KEYSYM_DOWN)
            capture(atril)
        keyboard.press_chord([], keyboard.KEYSYM_HOME)
        capture(atril)
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["e"],
            BrailleLine(2, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 13),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["r"],
            BrailleLine(3, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 14),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["e"],
            BrailleLine(4, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 15),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["’"],
            BrailleLine(5, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 16),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["s"],
            BrailleLine(6, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 17),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            [" "],
            BrailleLine(7, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 18),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["s"],
            BrailleLine(6, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 17),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["’"],
            BrailleLine(5, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 16),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["e"],
            BrailleLine(4, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 15),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["r"],
            BrailleLine(3, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 14),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["e"],
            BrailleLine(2, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 13),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["H"],
            BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 12),
        )


@pytest.mark.native_app
def test_links(atril: AtrilSession) -> None:
    """Checks links without creating a selection."""

    with navigation_session(atril, native=True):
        for _ in range(3):
            keyboard.press_chord([], keyboard.KEYSYM_DOWN)
            capture(atril)
        keyboard.press_chord([], keyboard.KEYSYM_HOME)
        capture(atril)
        for _ in range(7):
            keyboard.press_chord([], keyboard.KEYSYM_RIGHT)
            capture(atril)
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["l"],
            BrailleLine(
                9,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (52, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["i"],
            BrailleLine(
                10,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (53, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["n"],
            BrailleLine(
                11,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (54, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["k"],
            BrailleLine(
                12,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (55, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["!"],
            BrailleLine(
                13,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (56, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            [" "],
            BrailleLine(
                14,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (57, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["I"],
            BrailleLine(
                15,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (58, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            [" "],
            BrailleLine(
                14,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (57, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["!"],
            BrailleLine(
                13,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (56, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["k"],
            BrailleLine(
                12,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (55, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["n"],
            BrailleLine(
                11,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (54, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["i"],
            BrailleLine(
                10,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (53, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["l"],
            BrailleLine(
                9,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (52, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            [" "],
            BrailleLine(
                8,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (51, -1),
        )


@pytest.mark.native_app
def test_start_boundary(atril: AtrilSession) -> None:
    """Checks start boundary without creating a selection."""

    with navigation_session(atril, native=True):
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            [],
            None,
            (0, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            [],
            None,
            (0, -1),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            [],
            None,
            (0, -1),
        )


@pytest.mark.native_app
def test_end_boundary(atril: AtrilSession) -> None:
    """Checks end boundary without creating a selection."""

    with navigation_session(atril, native=True, bottom=True):
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            [],
            None,
            (-1, 51),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            [],
            None,
            (-1, 51),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            [],
            None,
            (-1, 51),
        )
        assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["."],
            BrailleLine(20, "I really like pages.", "I really like pages.", "\x00" * 20),
            (-1, 50),
        )


@pytest.mark.native_app
@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "Atril returns the whole page and bounds (-1, -1) at the text end offset: "
        "https://github.com/mate-desktop/atril/issues/731"
    ),
)
def test_character_to_document_end(atril: AtrilSession) -> None:
    """Checks moving from the final character to the document end."""

    with navigation_session(atril, native=True, bottom=True):
        keyboard.press_chord([], keyboard.KEYSYM_LEFT)
        capture(atril)
        assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["blank"],
            BrailleLine(21, "I really like pages.", "I really like pages.", "\x00" * 20),
            (-1, 51),
        )


@pytest.mark.native_app
@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "Atril returns an attribute range excluding the final period of page 2: "
        "https://github.com/mate-desktop/atril/issues/733"
    ),
)
def test_last_line_speech(atril: AtrilSession) -> None:
    """Checks that native line navigation announces the complete final line."""

    with navigation_session(atril, native=True):
        for _ in range(7):
            keyboard.press_chord([], keyboard.KEYSYM_DOWN)
            capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert capture(atril)[0] == ["I really like pages."]


@pytest.mark.native_app
@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "Atril returns the whole page and bounds (-1, -1) at the text end offset: "
        "https://github.com/mate-desktop/atril/issues/731"
    ),
)
def test_previous_page_end_speech(atril: AtrilSession) -> None:
    """Checks speech when Left lands at the previous page's end offset."""

    with navigation_session(atril, native=True):
        for _ in range(6):
            keyboard.press_chord([], keyboard.KEYSYM_DOWN)
            capture(atril)
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        assert capture(atril)[0] == ["blank"]
