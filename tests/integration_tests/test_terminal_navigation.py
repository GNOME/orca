# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

"""Integration tests for terminal-hosted pager and editor navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .terminal_helpers import settle, type_text

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_NANO_LINE_COUNT = 30
_NANO_LINES = frozenset(f"line {number}" for number in range(1, _NANO_LINE_COUNT + 1))
_VIM_BOTTOM_LINES = (*(f"line {number:02d}" for number in range(1, 13)), "same", "same")


def _spoken_lines(utterances: list[str]) -> list[str]:
    """Returns the spoken text as individual lines, ignoring how it was divided up."""

    lines = (line.strip() for utterance in utterances for line in utterance.split("\n"))
    return [line for line in lines if line]


def _assert_single_spoken_line(
    session: NativeAppSession,
    line_number: int,
    blank_in_previous: bool,
) -> bool:
    """Asserts that the expected line is spoken once, ignoring nano status cleanup."""

    actual = helpers.speech(session, quiescence=0.4, overall=3.0)
    # A repaint can redraw more than the current line, and whether that arrives as one
    # utterance or several is not something to assert on.
    spoken = _spoken_lines(actual)
    assert spoken.count(f"line {line_number}") == 1, actual
    assert all(line == "blank" or line in _NANO_LINES for line in spoken), actual
    blank_count = spoken.count("blank")
    assert blank_count <= 1, actual
    # nano blanks its status area from time to time. Announcing that is only a problem if it
    # happens on navigation after navigation, so reject consecutive blanks rather than any.
    assert not (blank_count and blank_in_previous), actual
    return bool(blank_count)


@pytest.mark.native_app
def test_nano_line_navigation_repaint_speaks_each_line_once(
    gtk3_terminal_nano: NativeAppSession,
) -> None:
    """Tests line navigation through nano repaints speaks the current line exactly once."""

    session = gtk3_terminal_nano
    settle(session)

    blank_in_previous = False
    for line_number in range(2, _NANO_LINE_COUNT + 1):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        blank_in_previous = _assert_single_spoken_line(session, line_number, blank_in_previous)

    for line_number in range(_NANO_LINE_COUNT - 1, 0, -1):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        blank_in_previous = _assert_single_spoken_line(session, line_number, blank_in_previous)


@pytest.mark.native_app
def test_vim_line_navigation_speaks_only_the_current_line(
    gtk3_terminal_vim_scroll: NativeAppSession,
) -> None:
    """Tests that scrolling line navigation in Vim speaks the caret's line and nothing else."""

    session = gtk3_terminal_vim_scroll
    settle(session)

    # Each arrow key repaints Vim's pending command area and ruler, and scrolls a row in.
    for line_number in range(2, 13):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        actual = helpers.speech(session, quiescence=0.4, overall=3.0)
        assert _spoken_lines(actual) == [f"line {line_number:02d}"], actual

    for line_number in range(11, 1, -1):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        actual = helpers.speech(session, quiescence=0.4, overall=3.0)
        assert _spoken_lines(actual) == [f"line {line_number:02d}"], actual


@pytest.mark.native_app
def test_vim_line_navigation_from_bottom_row_omits_the_ruler(
    gtk3_terminal_vim_bottom: NativeAppSession,
) -> None:
    """Tests that a scroll which repaints the caret's line and the ruler speaks only the line."""

    session = gtk3_terminal_vim_bottom
    settle(session)

    for line in _VIM_BOTTOM_LINES[1:]:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        actual = helpers.speech(session, quiescence=0.4, overall=3.0)
        assert _spoken_lines(actual) == [line], actual

    for line in reversed(_VIM_BOTTOM_LINES[:-1]):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        actual = helpers.speech(session, quiescence=0.4, overall=3.0)
        assert _spoken_lines(actual) == [line], actual


@pytest.mark.native_app
def test_shell_history_recall_speaks_the_recalled_command(
    gtk3_terminal_shell: NativeAppSession,
) -> None:
    """Tests that recalling a command from the shell's history speaks what was recalled."""

    session = gtk3_terminal_shell
    settle(session)

    type_text("echo hi\n")
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.speech(session) == ["echo hi"]


@pytest.mark.native_app
def test_pager_navigation_speaks_each_page(gtk3_terminal_pager: NativeAppSession) -> None:
    """Tests that paging through Less forward and back speaks each newly shown page."""

    session = gtk3_terminal_pager
    settle(session)

    # The first page-down leaves the initial filename-status paint behind; discard it
    # so the asserted pages start from a settled prompt-status state.
    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()

    # Less repaints the page and its status line together. Whether Orca sends the speech as
    # one utterance or several, and how many intermediate braille paints it makes on the way,
    # both vary with timing, so assert the text and the braille the display lands on.
    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    spoken, brailled = helpers.capture(session)
    assert _spoken_lines(spoken) == [
        "line 15",
        "line 16",
        "line 17",
        "line 18",
        "line 19",
        "line 20",
        "(END)",
    ]
    assert brailled[-1] == helpers.BrailleLine(6, "(END)", "(END)", "\x00" * 5)

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    spoken, brailled = helpers.capture(session)
    assert _spoken_lines(spoken) == [
        "07",
        "line 08",
        "line 09",
        "line 10",
        "line 11",
        "line 12",
        "line 13",
        ":",
    ]
    assert brailled[-1] == helpers.BrailleLine(2, ":", ":", "\x00")
