# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

"""Integration tests for flat review in terminals."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .terminal_helpers import bound_command, settle, type_text

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _review_top_line(session: NativeAppSession) -> tuple[list[str], list[helpers.BrailleLine]]:
    """Moves flat review to the top of the screen and returns the presentation."""

    session.orca.call("FlatReviewPresenter", "GoHome", True)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.call("FlatReviewPresenter", "PresentLine", True)
    return helpers.capture(session)


@pytest.mark.native_app
def test_flat_review_reflects_new_page(gtk3_terminal_pager: NativeAppSession) -> None:
    """Tests that reviewing the page's top line shows the new page after paging, not stale text."""

    session = gtk3_terminal_pager
    settle(session)
    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)
    keyboard.tap_key(keyboard.KEYSYM_PAGE_DOWN)  # to the last page (lines 14-20)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()

    helpers.toggle_flat_review(session)
    assert _review_top_line(session) == (
        ["line 14\n"],
        [helpers.BrailleLine(1, "line 14 $l", "line 14 $l", "\x00" * 10)],
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()
    assert _review_top_line(session) == (
        ["line 07\n"],
        [helpers.BrailleLine(1, "line 07 $l", "line 07 $l", "\x00" * 10)],
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()
    assert _review_top_line(session) == (
        ["line 01\n"],
        [helpers.BrailleLine(1, "line 01 $l", "line 01 $l", "\x00" * 10)],
    )
    helpers.toggle_flat_review(session)


@pytest.mark.native_app
def test_move_focus_to_review_location_unchanged(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that move-focus-to-review fails when the terminal won't let us set the caret."""

    session = gtk3_terminal_shell
    settle(session)

    type_text("echo aaa bbb ccc\n")
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    with bound_command(session, "move_focus_to_review") as key:
        helpers.toggle_flat_review(session)
        session.orca.call("FlatReviewPresenter", "GoHome", True)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
        # VTE's GTK3 AtkText.set_caret_offset always returns FALSE, so we cannot set the caret.
        # https://gitlab.gnome.org/GNOME/vte/-/work_items/2953
        session.orca.press_bound_key(key)
        assert helpers.capture(session) == (
            ["Location unchanged"],
            [helpers.BrailleLine(0, "Location unchanged", "Location unchanged", "\x00" * 18)],
        )
        helpers.toggle_flat_review(session)


@pytest.mark.native_app
def test_review_line_that_shrinks(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests reviewing a line word by word, then after it is overwritten with shorter text."""

    session = gtk3_terminal_shell
    settle(session)
    type_text(
        "clear; printf 'alpha bravo charlie delta echo\\n'; read; clear; printf 'alpha bravo\\n'"
    )
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=4.0)
    session.reader.reset()

    full = "alpha bravo charlie delta echo $l"
    visible = "alpha bravo charlie delta echo $"
    helpers.toggle_flat_review(session)
    try:
        session.orca.call("FlatReviewPresenter", "GoHome", True)
        assert helpers.capture(session) == (
            ["alpha bravo charlie delta echo\n"],
            [helpers.BrailleLine(1, full, visible, "\x00" * 33)],
        )
        session.orca.call("FlatReviewPresenter", "PresentItem", True)
        assert helpers.capture(session) == (
            ["alpha "],
            [helpers.BrailleLine(1, full, visible, "\x00" * 33)],
        )
        session.orca.call("FlatReviewPresenter", "GoNextItem", True)
        assert helpers.capture(session) == (
            ["bravo "],
            [helpers.BrailleLine(7, full, visible, "\x00" * 33)],
        )
        session.orca.call("FlatReviewPresenter", "GoNextItem", True)
        assert helpers.capture(session) == (
            ["charlie "],
            [helpers.BrailleLine(13, full, visible, "\x00" * 33)],
        )

        keyboard.tap_key(keyboard.KEYSYM_RETURN)
        session.reader.drain(quiescence_timeout=0.5, overall_timeout=4.0)
        session.reader.reset()

        session.orca.call("FlatReviewPresenter", "GoHome", True)
        assert helpers.capture(session) == (
            ["alpha bravo\n"],
            [helpers.BrailleLine(1, "alpha bravo $l", "alpha bravo $l", "\x00" * 14)],
        )
    finally:
        helpers.toggle_flat_review(session)
