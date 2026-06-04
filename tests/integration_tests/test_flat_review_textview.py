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

"""Tests flat review by line, word, and character in a GTK3 text view."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, toggle_flat_review

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_flat_review_by_line_word_and_character(gtk3_text_view: NativeAppSession) -> None:
    """Tests reviewing lines, words, and characters with the flat review keypad commands."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    # KP_Subtract toggles flat review on; discard its key echo and entry announcement.
    keyboard.tap_key(keyboard.KEYSYM_KP_SUBTRACT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert capture(session) == (
        ["Line one.\n"],
        [BrailleLine(1, "Line one. $l", "Line one. $l", "\x00" * 12)],
    )

    # The text view wraps line two, so review by line walks its first visual line.
    keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
    assert capture(session) == (
        ["Line two has additional words to make it long enough that "],
        [
            BrailleLine(
                1,
                "Line two has additional words to make it long enough that  $l",
                "Line two has additional words to",
                "\x00" * 61,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_HOME)
    assert capture(session) == (
        ["Line one.\n"],
        [BrailleLine(1, "Line one. $l", "Line one. $l", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_BEGIN)
    assert capture(session) == (
        ["Line "],
        [BrailleLine(1, "Line one. $l", "Line one. $l", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_RIGHT)
    assert capture(session) == (
        ["one.\n"],
        [BrailleLine(6, "Line one. $l", "Line one. $l", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_LEFT)
    assert capture(session) == (
        ["Line "],
        [BrailleLine(1, "Line one. $l", "Line one. $l", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_DOWN)
    assert capture(session) == (
        ["L"],
        [BrailleLine(1, "Line one. $l", "Line one. $l", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_DOWN)
    assert capture(session) == (
        ["i"],
        [BrailleLine(2, "Line one. $l", "Line one. $l", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_END)
    assert capture(session) == (
        ["L"],
        [BrailleLine(1, "Line one. $l", "Line one. $l", "\x00" * 12)],
    )


@pytest.mark.native_app
def test_focus_tracking_off_keeps_review_location(gtk3_text_view: NativeAppSession) -> None:
    """Tests that FocusTracking=off keeps the review location when the caret moves."""

    session = gtk3_text_view
    # The previous test leaves flat review on; exit then re-enter from a known position.
    toggle_flat_review(session)
    move_to_top(session)
    toggle_flat_review(session)

    session.orca.set("FlatReviewPresenter", "FocusTracking", 0)
    try:
        keyboard.tap_key(keyboard.KEYSYM_KP_UP)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        keyboard.tap_key(keyboard.KEYSYM_KP_UP)
        assert capture(session) == (
            ["Line one.\n"],
            [BrailleLine(1, "Line one. $l", "Line one. $l", "\x00" * 12)],
        )
    finally:
        session.orca.set("FlatReviewPresenter", "FocusTracking", 1)
        toggle_flat_review(session)


@pytest.mark.native_app
def test_focus_tracking_auto_follows_caret(gtk3_text_view: NativeAppSession) -> None:
    """Tests that FocusTracking=auto moves the review location when the caret moves."""

    session = gtk3_text_view
    move_to_top(session)
    toggle_flat_review(session)

    session.orca.set("FlatReviewPresenter", "FocusTracking", 1)
    try:
        keyboard.tap_key(keyboard.KEYSYM_KP_UP)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        keyboard.tap_key(keyboard.KEYSYM_KP_UP)
        assert capture(session) == (
            ["Line two has additional words to make it long enough that "],
            [
                BrailleLine(
                    1,
                    "Line two has additional words to make it long enough that  $l",
                    "Line two has additional words to",
                    "\x00" * 61,
                )
            ],
        )
    finally:
        session.orca.set("FlatReviewPresenter", "FocusTracking", 1)
        toggle_flat_review(session)


def _move_focus_to_review_after(session: NativeAppSession, nav: int) -> list[str]:
    """Reviews from the top of the text view, navigates by nav, routes focus, returns speech."""

    ((key, mods),) = session.orca.available_keybindings(1)
    session.orca.bind_command("move_focus_to_review", key, mods)
    session.orca.refresh_keybindings()
    try:
        move_to_top(session)
        toggle_flat_review(session)
        keyboard.tap_key(keyboard.KEYSYM_KP_UP)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
        keyboard.tap_key(nav)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
        session.orca.press_bound_key(key)
        spoken, _braille = capture(session)
        return spoken
    finally:
        toggle_flat_review(session)
        session.orca.unbind_command("move_focus_to_review")
        session.orca.refresh_keybindings()


@pytest.mark.native_app
def test_move_focus_to_review_announces_line(gtk3_text_view: NativeAppSession) -> None:
    """Tests that move-focus-to-review announces the line when the review crossed lines."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    assert _move_focus_to_review_after(session, keyboard.KEYSYM_KP_PAGE_UP) == [
        "Line two has additional words to make it long enough that "
    ]


@pytest.mark.native_app
def test_move_focus_to_review_announces_word(gtk3_text_view: NativeAppSession) -> None:
    """Tests that move-focus-to-review announces the word when the review crossed words."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    assert _move_focus_to_review_after(session, keyboard.KEYSYM_KP_RIGHT) == ["one.\n"]


@pytest.mark.native_app
def test_move_focus_to_review_announces_character(gtk3_text_view: NativeAppSession) -> None:
    """Tests that move-focus-to-review announces the character within the same word."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    assert _move_focus_to_review_after(session, keyboard.KEYSYM_KP_PAGE_DOWN) == ["i"]
