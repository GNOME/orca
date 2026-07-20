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
from .terminal_helpers import settle

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _assert_single_spoken_line(
    session: NativeAppSession,
    line_number: int,
    blank_already_seen: bool,
) -> bool:
    """Asserts that the expected line is spoken once, ignoring nano status cleanup."""

    actual = helpers.speech(session, quiescence=0.4, overall=3.0)
    expected = f"line {line_number}"
    line_utterances = [utterance for utterance in actual if utterance.strip() == expected]
    assert len(line_utterances) == 1, actual
    assert all(utterance == "blank" or utterance.strip() == expected for utterance in actual), (
        actual
    )
    blank_count = actual.count("blank")
    assert blank_count <= 1, actual
    assert not (blank_count and blank_already_seen), actual
    return blank_already_seen or bool(blank_count)


@pytest.mark.native_app
def test_nano_line_navigation_repaint_speaks_each_line_once(
    gtk3_terminal_nano: NativeAppSession,
) -> None:
    """Tests line navigation through nano repaints speaks the current line exactly once."""

    session = gtk3_terminal_nano
    settle(session)

    blank_seen = False
    for line_number in range(2, 31):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        blank_seen = _assert_single_spoken_line(session, line_number, blank_seen)

    for line_number in range(29, 0, -1):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        blank_seen = _assert_single_spoken_line(session, line_number, blank_seen)


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

    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    assert helpers.capture(session) == (
        ["line 15\nline 16\nline 17\nline 18\nline 19\nline 20\n(END)"],
        [helpers.BrailleLine(6, "(END)", "(END)", "\x00" * 5)],
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    assert helpers.capture(session) == (
        ["07\nline 08\nline 09\nline 10\nline 11\nline 12\nline 13\n:"],
        [helpers.BrailleLine(2, ":", ":", "\x00")],
    )
