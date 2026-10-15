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

"""Navigation and selection helpers for the fixed two-page Atril document."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import caret_selection_helpers as commands
from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .orca_fixtures import AtrilSession

FIRST_PAGE = (
    "Do headings work?\nHello world.\nI am a test.\nLook, a link! In a PDF.\nAnother one!\nThe end."
)
SECOND_PAGE = "More pages!\nHere’s a new page.\nI really like pages."


@contextmanager
def navigation_session(
    session: AtrilSession, *, native: bool, bottom: bool = False, clear_selection: bool = False
) -> Iterator[None]:
    """Positions the caret, starting and finishing with Orca navigation enabled."""

    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    session.orca.set("BraillePresenter", "LinkIndicator", "dot7")
    if clear_selection:
        for page in session.pages:
            for index in reversed(range(Atspi.Text.get_n_selections(page))):
                assert Atspi.Text.remove_selection(page, index)
        capture(session)
    # Native Ctrl+Home/End scrolls pages without moving the caret. Use Orca to position it.
    move_to_top(session)
    if bottom:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
        capture(session)
    if native:
        session.orca.press_orca_key(keyboard.KEYSYM_F12)
        assert capture(session)[0] == ["The application is controlling the caret."]
        # Move away and back: a no-op does not reset Atril's column for Up/Down.
        keys = (
            (keyboard.KEYSYM_HOME, keyboard.KEYSYM_END)
            if bottom
            else (keyboard.KEYSYM_END, keyboard.KEYSYM_HOME)
        )
        for key in keys:
            keyboard.tap_key(key)
            capture(session)
    try:
        yield
    finally:
        if native:
            session.orca.press_orca_key(keyboard.KEYSYM_F12)
            assert capture(session)[0] == ["The screen reader is controlling the caret."]


@contextmanager
def selection_session(
    session: AtrilSession, *, native: bool, bottom: bool = False
) -> Iterator[None]:
    """Clears both pages' selections, then sets the caret and navigation mode."""

    with navigation_session(session, native=native, bottom=bottom, clear_selection=True):
        yield


def display_second_page(session: AtrilSession) -> None:
    """Moves from the document start to page two using Atril's native caret.

    Requires Orca caret navigation and Atril's native caret to be enabled.
    """

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == ["The application is controlling the caret."]
    try:
        keyboard.tap_key(keyboard.KEYSYM_END)
        capture(session)
        keyboard.tap_key(keyboard.KEYSYM_HOME)
        capture(session)
        for _ in range(6):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            capture(session)
    finally:
        session.orca.press_orca_key(keyboard.KEYSYM_F12)
        assert capture(session)[0] == ["The screen reader is controlling the caret."]


def selected_ranges(session: AtrilSession) -> tuple[list[tuple[int, int]], ...]:
    """Returns all reported selection ranges, including invalid bounds, from the cached pages."""
    result = []
    for page in session.pages:
        ranges = []
        for index in range(Atspi.Text.get_n_selections(page)):
            selection = Atspi.Text.get_selection(page, index)
            ranges.append((selection.start_offset, selection.end_offset))
        result.append(ranges)
    return tuple(result)


def assert_step(
    session: AtrilSession,
    command: str,
    spoken: list[str],
    brailled: BrailleLine | None,
    ranges: tuple[list[tuple[int, int]], ...],
    *,
    native: bool,
    notify_user: bool = True,
) -> None:
    """Checks presentation and the actual selection on both pages after one command."""
    if native:
        modifiers = [keyboard.KEYSYM_SHIFT_L]
        if command in (commands.NEXT_WORD, commands.PREVIOUS_WORD):
            modifiers.insert(0, keyboard.KEYSYM_CONTROL_L)
        key = {
            commands.NEXT_CHARACTER: keyboard.KEYSYM_RIGHT,
            commands.PREVIOUS_CHARACTER: keyboard.KEYSYM_LEFT,
            commands.NEXT_WORD: keyboard.KEYSYM_RIGHT,
            commands.PREVIOUS_WORD: keyboard.KEYSYM_LEFT,
            commands.NEXT_LINE: keyboard.KEYSYM_DOWN,
            commands.PREVIOUS_LINE: keyboard.KEYSYM_UP,
            commands.START_OF_LINE: keyboard.KEYSYM_HOME,
            commands.END_OF_LINE: keyboard.KEYSYM_END,
        }[command]
        keyboard.press_chord(modifiers, key)
    else:
        session.orca.select_with_caret_navigator(command, notify_user=notify_user)
    actual_speech, actual_braille = capture(session)
    actual_ranges = selected_ranges(session)
    assert actual_ranges == ranges, (command, actual_ranges, ranges)
    assert actual_speech == spoken, (command, actual_speech, spoken)
    actual_line = actual_braille[-1] if actual_braille else None
    assert actual_line == brailled, (command, actual_line, brailled)


def assert_navigation(
    session: AtrilSession,
    key: int,
    modifiers: list[int],
    spoken: list[str] | None,
    brailled: BrailleLine | None,
    offsets: tuple[int, int],
    message: BrailleLine | None = None,
) -> None:
    """Checks navigation, presentation, and absence of selection on both cached pages.

    A page-change message can temporarily replace the braille content. Check both.
    Speech may be checked separately when an application bug affects only speech.
    """

    keyboard.press_chord(modifiers, key)
    actual_speech, actual_braille = capture(session)
    actual_offsets = tuple(Atspi.Text.get_caret_offset(page) for page in session.pages)
    assert actual_offsets == offsets, (actual_offsets, offsets)
    assert selected_ranges(session) == ([], [])
    if spoken is not None:
        assert actual_speech == spoken, (actual_speech, spoken)
    if message is not None:
        assert brailled in actual_braille, (actual_braille, brailled)
    actual_line = actual_braille[-1] if actual_braille else None
    expected_line = message if message is not None else brailled
    assert actual_line == expected_line, (actual_line, expected_line)
