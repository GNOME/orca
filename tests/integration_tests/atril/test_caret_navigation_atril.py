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

"""Tests Orca-controlled Atril caret navigation without selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import atril_helpers, helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import AtrilSession


@pytest.mark.native_app
def test_lines_across_pages(atril: AtrilSession) -> None:
    """Checks lines across pages without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["Hello world.\n"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["I am a test.\n"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            (31, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["Look, a link! In a PDF.\n"],
            helpers.BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (44, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["Another one!\n"],
            helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            (68, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["The end."],
            helpers.BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            (81, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["More pages!\n", "Page 2"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            (-1, 0),
            helpers.BrailleLine(0, "Page 2", "Page 2", "\x00" * 6),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["Here’s a new page.\n"],
            helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 12),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["I really like pages."],
            helpers.BrailleLine(1, "I really like pages.", "I really like pages.", "\x00" * 20),
            (-1, 31),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["Here’s a new page.\n"],
            helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 12),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["More pages!\n"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            (-1, 0),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["The end.", "page", "Page 1"],
            helpers.BrailleLine(1, "The end.", "The end.", "\x00" * 8),
            (81, -1),
            helpers.BrailleLine(0, "Page 1", "Page 1", "\x00" * 6),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["Another one!\n"],
            helpers.BrailleLine(1, "Another one!", "Another one!", "\x40" * 12),
            (68, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["Look, a link! In a PDF.\n"],
            helpers.BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (44, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["I am a test.\n"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            (31, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["Hello world.\n"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            ["Do headings work?\n"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            (0, -1),
        )


@pytest.mark.native_app
def test_characters(atril: AtrilSession) -> None:
    """Checks characters without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["o"],
            helpers.BrailleLine(2, "Do headings work?", "Do headings work?", "\x00" * 17),
            (1, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            [" "],
            helpers.BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17),
            (2, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["h"],
            helpers.BrailleLine(4, "Do headings work?", "Do headings work?", "\x00" * 17),
            (3, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["e"],
            helpers.BrailleLine(5, "Do headings work?", "Do headings work?", "\x00" * 17),
            (4, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["h"],
            helpers.BrailleLine(4, "Do headings work?", "Do headings work?", "\x00" * 17),
            (3, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            [" "],
            helpers.BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17),
            (2, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["o"],
            helpers.BrailleLine(2, "Do headings work?", "Do headings work?", "\x00" * 17),
            (1, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["D"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            (0, -1),
        )


@pytest.mark.native_app
def test_words(atril: AtrilSession) -> None:
    """Checks words without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Do"],
            helpers.BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17),
            (2, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["headings"],
            helpers.BrailleLine(12, "Do headings work?", "Do headings work?", "\x00" * 17),
            (11, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["work?"],
            helpers.BrailleLine(18, "Do headings work?", "Do headings work?", "\x00" * 17),
            (17, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Hello"],
            helpers.BrailleLine(6, "Hello world.", "Hello world.", "\x00" * 12),
            (23, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["world."],
            helpers.BrailleLine(13, "Hello world.", "Hello world.", "\x00" * 12),
            (30, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["world."],
            helpers.BrailleLine(7, "Hello world.", "Hello world.", "\x00" * 12),
            (24, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Hello"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["work?"],
            helpers.BrailleLine(13, "Do headings work?", "Do headings work?", "\x00" * 17),
            (12, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["headings"],
            helpers.BrailleLine(4, "Do headings work?", "Do headings work?", "\x00" * 17),
            (3, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Do"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            (0, -1),
        )


@pytest.mark.native_app
def test_line_boundaries(atril: AtrilSession) -> None:
    """Checks line boundaries without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        keyboard.press_chord([], keyboard.KEYSYM_DOWN)
        helpers.capture(atril)
        for _ in range(4):
            keyboard.press_chord([], keyboard.KEYSYM_RIGHT)
            helpers.capture(atril)
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_END,
            [],
            ["blank"],
            helpers.BrailleLine(13, "Hello world.", "Hello world.", "\x00" * 12),
            (30, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_HOME,
            [],
            ["H"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_END,
            [],
            ["blank"],
            helpers.BrailleLine(13, "Hello world.", "Hello world.", "\x00" * 12),
            (30, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_HOME,
            [],
            ["H"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )


@pytest.mark.native_app
def test_characters_across_lines(atril: AtrilSession) -> None:
    """Checks characters across lines without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        keyboard.press_chord([], keyboard.KEYSYM_END)
        helpers.capture(atril)
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["H"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["e"],
            helpers.BrailleLine(2, "Hello world.", "Hello world.", "\x00" * 12),
            (19, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["l"],
            helpers.BrailleLine(3, "Hello world.", "Hello world.", "\x00" * 12),
            (20, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["e"],
            helpers.BrailleLine(2, "Hello world.", "Hello world.", "\x00" * 12),
            (19, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["H"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["blank"],
            helpers.BrailleLine(18, "Do headings work?", "Do headings work?", "\x00" * 17),
            (17, -1),
        )


@pytest.mark.native_app
def test_words_across_lines(atril: AtrilSession) -> None:
    """Checks words across lines without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        keyboard.press_chord([], keyboard.KEYSYM_END)
        helpers.capture(atril)
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Hello"],
            helpers.BrailleLine(6, "Hello world.", "Hello world.", "\x00" * 12),
            (23, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["world."],
            helpers.BrailleLine(13, "Hello world.", "Hello world.", "\x00" * 12),
            (30, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["I"],
            helpers.BrailleLine(2, "I am a test.", "I am a test.", "\x00" * 12),
            (32, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["I"],
            helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
            (31, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["world."],
            helpers.BrailleLine(7, "Hello world.", "Hello world.", "\x00" * 12),
            (24, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Hello"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )


@pytest.mark.native_app
def test_characters_across_pages(atril: AtrilSession) -> None:
    """Checks characters across pages without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        for _ in range(5):
            keyboard.press_chord([], keyboard.KEYSYM_DOWN)
            helpers.capture(atril)
        keyboard.press_chord([], keyboard.KEYSYM_END)
        helpers.capture(atril)
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["M", "Page 2"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            (-1, 0),
            helpers.BrailleLine(0, "Page 2", "Page 2", "\x00" * 6),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["o"],
            helpers.BrailleLine(2, "More pages!", "More pages!", "\x00" * 11),
            (-1, 1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["r"],
            helpers.BrailleLine(3, "More pages!", "More pages!", "\x00" * 11),
            (-1, 2),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["o"],
            helpers.BrailleLine(2, "More pages!", "More pages!", "\x00" * 11),
            (-1, 1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["M"],
            helpers.BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
            (-1, 0),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            [".", "Page 1"],
            helpers.BrailleLine(8, "The end.", "The end.", "\x00" * 8),
            (88, -1),
            helpers.BrailleLine(0, "Page 1", "Page 1", "\x00" * 6),
        )


@pytest.mark.native_app
@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "Atril page accessibles return index -1, preventing word navigation between pages: "
        "https://github.com/mate-desktop/atril/issues/732"
    ),
)
def test_words_to_next_page(atril: AtrilSession) -> None:
    """Checks words across pages without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        for _ in range(5):
            keyboard.press_chord([], keyboard.KEYSYM_DOWN)
            helpers.capture(atril)
        keyboard.press_chord([], keyboard.KEYSYM_HOME)
        helpers.capture(atril)
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["The"],
            helpers.BrailleLine(4, "The end.", "The end.", "\x00" * 8),
            (84, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["end."],
            helpers.BrailleLine(9, "The end.", "The end.", "\x00" * 8),
            (89, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["More", "Page 2"],
            helpers.BrailleLine(5, "More pages!", "More pages!", "\x00" * 11),
            (-1, 4),
            helpers.BrailleLine(0, "Page 2", "Page 2", "\x00" * 6),
        )


@pytest.mark.native_app
def test_unicode(atril: AtrilSession) -> None:
    """Checks unicode without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        for _ in range(7):
            keyboard.press_chord([], keyboard.KEYSYM_DOWN)
            helpers.capture(atril)
        keyboard.press_chord([], keyboard.KEYSYM_HOME)
        helpers.capture(atril)
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["e"],
            helpers.BrailleLine(2, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 13),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["r"],
            helpers.BrailleLine(3, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 14),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["e"],
            helpers.BrailleLine(4, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 15),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["’"],
            helpers.BrailleLine(5, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 16),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["s"],
            helpers.BrailleLine(6, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 17),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            [" "],
            helpers.BrailleLine(7, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 18),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["s"],
            helpers.BrailleLine(6, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 17),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["’"],
            helpers.BrailleLine(5, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 16),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["e"],
            helpers.BrailleLine(4, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 15),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["r"],
            helpers.BrailleLine(3, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 14),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["e"],
            helpers.BrailleLine(2, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 13),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["H"],
            helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            (-1, 12),
        )


@pytest.mark.native_app
def test_links(atril: AtrilSession) -> None:
    """Checks links without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        for _ in range(3):
            keyboard.press_chord([], keyboard.KEYSYM_DOWN)
            helpers.capture(atril)
        keyboard.press_chord([], keyboard.KEYSYM_HOME)
        helpers.capture(atril)
        for _ in range(7):
            keyboard.press_chord([], keyboard.KEYSYM_RIGHT)
            helpers.capture(atril)
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["l"],
            helpers.BrailleLine(
                9,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (52, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["i"],
            helpers.BrailleLine(
                10,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (53, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["n"],
            helpers.BrailleLine(
                11,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (54, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["k"],
            helpers.BrailleLine(
                12,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (55, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["!"],
            helpers.BrailleLine(
                13,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (56, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            [" "],
            helpers.BrailleLine(
                14,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (57, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["I"],
            helpers.BrailleLine(
                15,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (58, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            [" "],
            helpers.BrailleLine(
                14,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (57, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["!"],
            helpers.BrailleLine(
                13,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (56, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["k"],
            helpers.BrailleLine(
                12,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (55, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["n"],
            helpers.BrailleLine(
                11,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (54, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["i"],
            helpers.BrailleLine(
                10,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (53, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["l"],
            helpers.BrailleLine(
                9,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (52, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            [" "],
            helpers.BrailleLine(
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

    with atril_helpers.navigation_session(atril, native=False):
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            [],
            None,
            (0, -1),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_UP,
            [],
            [],
            None,
            (0, -1),
        )
        atril_helpers.assert_navigation(
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

    with atril_helpers.navigation_session(atril, native=False, bottom=True):
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            [],
            helpers.BrailleLine(21, "I really like pages.", "I really like pages.", "\x00" * 20),
            (-1, 51),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            [],
            None,
            (-1, 51),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [keyboard.KEYSYM_CONTROL_L],
            ["pages."],
            helpers.BrailleLine(21, "I really like pages.", "I really like pages.", "\x00" * 20),
            (-1, 51),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [],
            ["."],
            helpers.BrailleLine(20, "I really like pages.", "I really like pages.", "\x00" * 20),
            (-1, 50),
        )


@pytest.mark.native_app
def test_file_boundaries(atril: AtrilSession) -> None:
    """Checks file boundaries without creating a selection."""

    with atril_helpers.navigation_session(atril, native=False):
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_END,
            [keyboard.KEYSYM_CONTROL_L],
            ["I really like pages.", "Page 2"],
            helpers.BrailleLine(21, "I really like pages.", "I really like pages.", "\x00" * 20),
            (-1, 51),
            helpers.BrailleLine(0, "Page 2", "Page 2", "\x00" * 6),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_HOME,
            [keyboard.KEYSYM_CONTROL_L],
            ["Do headings work?\n", "Page 1"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            (0, -1),
            helpers.BrailleLine(0, "Page 1", "Page 1", "\x00" * 6),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_END,
            [keyboard.KEYSYM_CONTROL_L],
            ["I really like pages.", "Page 2"],
            helpers.BrailleLine(21, "I really like pages.", "I really like pages.", "\x00" * 20),
            (-1, 51),
            helpers.BrailleLine(0, "Page 2", "Page 2", "\x00" * 6),
        )
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_HOME,
            [keyboard.KEYSYM_CONTROL_L],
            ["Do headings work?\n", "Page 1"],
            helpers.BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
            (0, -1),
            helpers.BrailleLine(0, "Page 1", "Page 1", "\x00" * 6),
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

    with atril_helpers.navigation_session(atril, native=False, bottom=True):
        keyboard.press_chord([], keyboard.KEYSYM_LEFT)
        helpers.capture(atril)
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_RIGHT,
            [],
            ["blank"],
            helpers.BrailleLine(21, "I really like pages.", "I really like pages.", "\x00" * 20),
            (-1, 51),
        )


@pytest.mark.native_app
def test_word_to_previous_page(atril: AtrilSession) -> None:
    """Checks backward word navigation across the page boundary."""

    with atril_helpers.navigation_session(atril, native=False):
        for _ in range(6):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            helpers.capture(atril)
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["end.", "Page 1"],
            helpers.BrailleLine(5, "The end.", "The end.", "\x00" * 8),
            (85, -1),
            helpers.BrailleLine(0, "Page 1", "Page 1", "\x00" * 6),
        )


@pytest.mark.native_app
def test_toggle_caret_navigation(atril: AtrilSession) -> None:
    """Checks that native and Orca navigation resume from the same caret."""

    with atril_helpers.navigation_session(atril, native=False):
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["Hello world.\n"],
            helpers.BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
            (18, -1),
        )
        atril.orca.press_orca_key(keyboard.KEYSYM_F12)
        try:
            assert helpers.capture(atril)[0] == ["The application is controlling the caret."]
            atril_helpers.assert_navigation(
                atril,
                keyboard.KEYSYM_DOWN,
                [],
                ["I am a test.\n"],
                helpers.BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
                (31, -1),
            )
        finally:
            atril.orca.press_orca_key(keyboard.KEYSYM_F12)
            assert helpers.capture(atril)[0] == ["The screen reader is controlling the caret."]
        atril_helpers.assert_navigation(
            atril,
            keyboard.KEYSYM_DOWN,
            [],
            ["Look, a link! In a PDF.\n"],
            helpers.BrailleLine(
                1,
                "Look, a link! In a PDF.",
                "Look, a link! In a PDF.",
                "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
            ),
            (44, -1),
        )
