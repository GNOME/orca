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

"""Tests Orca navigation and selection with Atril's native caret disabled."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import caret_selection_helpers as commands
from .atril_helpers import assert_navigation, assert_step, selection_session
from .harness import keyboard
from .helpers import BrailleLine, capture, say_selection
from .version_helpers import requires_atril_version

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .orca_fixtures import AtrilSession


@pytest.fixture
def native_caret_disabled(atril: AtrilSession) -> Iterator[AtrilSession]:
    """Disables Atril's native caret before establishing Orca's caret context."""

    keyboard.tap_key(keyboard.KEYSYM_F7)
    capture(atril)
    try:
        with selection_session(atril, native=False):
            assert tuple(Atspi.Text.get_caret_offset(page) for page in atril.pages) == (-1, -1)
            yield atril
    finally:
        keyboard.tap_key(keyboard.KEYSYM_F7)
        capture(atril)


@pytest.mark.native_app
@pytest.mark.parametrize(
    "forward,backward,modifiers,spoken,reverse_spoken,brailled",
    [
        (
            keyboard.KEYSYM_RIGHT,
            keyboard.KEYSYM_LEFT,
            [],
            ["o"],
            ["D"],
            BrailleLine(2, "Do headings work?", "Do headings work?", "\x00" * 17),
        ),
        (
            keyboard.KEYSYM_RIGHT,
            keyboard.KEYSYM_LEFT,
            [keyboard.KEYSYM_CONTROL_L],
            ["Do"],
            ["Do"],
            BrailleLine(3, "Do headings work?", "Do headings work?", "\x00" * 17),
        ),
        (
            keyboard.KEYSYM_DOWN,
            keyboard.KEYSYM_UP,
            [],
            ["Hello world.\n"],
            ["Do headings work?\n"],
            BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
        ),
    ],
    ids=["character", "word", "line"],
)
def test_navigation(
    native_caret_disabled: AtrilSession,
    forward: int,
    backward: int,
    modifiers: list[int],
    spoken: list[str],
    reverse_spoken: list[str],
    brailled: BrailleLine,
) -> None:
    """Checks forward and reverse movement without a native caret or selection."""

    session = native_caret_disabled
    # Atril reports -1 for both offsets while its native caret is disabled.
    assert_navigation(
        session,
        forward,
        modifiers,
        spoken,
        brailled,
        (-1, -1),
    )
    assert_navigation(
        session,
        backward,
        modifiers,
        reverse_spoken,
        BrailleLine(1, "Do headings work?", "Do headings work?", "\x00" * 17),
        (-1, -1),
    )


@pytest.mark.native_app
def test_navigation_between_pages(native_caret_disabled: AtrilSession) -> None:
    """Checks crossing a page boundary in both directions without the native caret."""

    session = native_caret_disabled
    for spoken, text, mask in (
        ("Hello world.\n", "Hello world.", "\x00" * 12),
        ("I am a test.\n", "I am a test.", "\x00" * 12),
        (
            "Look, a link! In a PDF.\n",
            "Look, a link! In a PDF.",
            "\x00" * 8 + "\x40" * 4 + "\x00" * 11,
        ),
        ("Another one!\n", "Another one!", "\x40" * 12),
        ("The end.", "The end.", "\x00" * 8),
    ):
        assert_navigation(
            session,
            keyboard.KEYSYM_DOWN,
            [],
            [spoken],
            BrailleLine(1, text, text, mask),
            (-1, -1),
        )
    assert_navigation(
        session,
        keyboard.KEYSYM_DOWN,
        [],
        ["More pages!\n", "Page 2"],
        BrailleLine(1, "More pages!", "More pages!", "\x00" * 11),
        (-1, -1),
        BrailleLine(0, "Page 2", "Page 2", "\x00" * 6),
    )
    assert_navigation(
        session,
        keyboard.KEYSYM_UP,
        [],
        ["The end.", "page", "Page 1"],
        BrailleLine(1, "The end.", "The end.", "\x00" * 8),
        (-1, -1),
        BrailleLine(0, "Page 1", "Page 1", "\x00" * 6),
    )


@pytest.mark.native_app
@pytest.mark.parametrize(
    "forward,backward,steps,selected_text",
    [
        (
            commands.NEXT_CHARACTER,
            commands.PREVIOUS_CHARACTER,
            [
                (
                    ["D", "selected"],
                    BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
                    1,
                ),
                (
                    ["o", "selected"],
                    BrailleLine(
                        3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
                    ),
                    2,
                ),
                (
                    ["o", "unselected"],
                    BrailleLine(2, "Do headings work?", "Do headings work?", "\xc0" + "\x00" * 16),
                    1,
                ),
            ],
            "D",
        ),
        (
            commands.NEXT_WORD,
            commands.PREVIOUS_WORD,
            [
                (
                    ["Do", "selected"],
                    BrailleLine(
                        3, "Do headings work?", "Do headings work?", "\xc0" * 2 + "\x00" * 15
                    ),
                    2,
                ),
                (
                    ["headings", "selected"],
                    BrailleLine(
                        12, "Do headings work?", "Do headings work?", "\xc0" * 11 + "\x00" * 6
                    ),
                    11,
                ),
                (
                    ["headings", "unselected"],
                    BrailleLine(
                        4, "Do headings work?", "Do headings work?", "\xc0" * 3 + "\x00" * 14
                    ),
                    3,
                ),
            ],
            "Do ",
        ),
        (
            commands.NEXT_LINE,
            commands.PREVIOUS_LINE,
            [
                (
                    ["Do headings work?", "selected"],
                    BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
                    17,
                ),
                (
                    ["Hello world.", "selected"],
                    BrailleLine(1, "I am a test.", "I am a test.", "\x00" * 12),
                    30,
                ),
                (
                    ["Hello world.", "unselected"],
                    BrailleLine(1, "Hello world.", "Hello world.", "\x00" * 12),
                    17,
                ),
            ],
            "Do headings work?",
        ),
    ],
    ids=["character", "word", "line"],
)
@requires_atril_version(1, 28, 7)
def test_selection(
    native_caret_disabled: AtrilSession,
    forward: str,
    backward: str,
    steps: list[tuple[list[str], BrailleLine, int]],
    selected_text: str,
) -> None:
    """Checks extending, shrinking, and querying selection without the native caret."""

    session = native_caret_disabled
    for command, (spoken, brailled, end) in zip((forward, forward, backward), steps, strict=True):
        assert_step(session, command, spoken, brailled, ([(0, end)], []), native=False)
    assert say_selection(session) == [f"Selected text is:  {selected_text}"]
