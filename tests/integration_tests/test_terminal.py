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

"""Integration tests for terminal presentation: command output, typing, and pager navigation."""

from __future__ import annotations

import contextlib
import shutil
import time
from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .orca_fixtures import NativeAppSession


@contextlib.contextmanager
def _bound(session: NativeAppSession, handler: str) -> Iterator[str]:
    """Binds handler to a free key for the block, yielding the key to press."""

    ((key, mods),) = session.orca.available_keybindings(1)
    session.orca.bind_command(handler, key, mods)
    session.orca.refresh_keybindings()
    try:
        yield key
    finally:
        session.orca.unbind_command(handler)
        session.orca.refresh_keybindings()


def _type(text: str) -> None:
    for char in text:
        if char == " ":
            keyboard.tap_key(keyboard.KEYSYM_SPACE)
        elif char == "\n":
            keyboard.tap_key(keyboard.KEYSYM_RETURN)
        elif char.isupper():
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], ord(char.lower()))
        else:
            keyboard.tap_key(ord(char))


def _settle(session: NativeAppSession) -> None:
    """Waits for the spawned program to finish its initial paint, then resets the reader."""

    session.reader.drain(quiescence_timeout=0.5, overall_timeout=4.0)
    session.reader.reset()


_WIDE_PROMPT_INPUT = "abcdefghij klmnopqrst uvwxy 01234567"
_WIDE_PROMPT_LINE = "$ abcdefghij klmnopqrst uvwxy 01234567"


@pytest.mark.native_app
def test_command_output_is_spoken(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that the output of a command is spoken when the command completes."""

    session = gtk3_terminal_shell
    _settle(session)

    _type("echo hi\n")
    assert helpers.speech(session) == ["hi\n$ "]
    _type("echo hello world\n")
    assert helpers.speech(session) == ["hello world\n$ "]


@pytest.mark.native_app
def test_multiline_command_output_is_spoken(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that multi-line command output is spoken."""

    if shutil.which("seq") is None:
        pytest.skip("seq is not available")

    session = gtk3_terminal_shell
    _settle(session)

    _type("seq 3\n")
    assert helpers.speech(session) == ["1\n2\n3\n$ "]


@pytest.mark.native_app
def test_typed_characters_are_echoed(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that key echo speaks each character as it is typed at the prompt."""

    session = gtk3_terminal_shell
    session.orca.set("TypingEchoPresenter", "KeyEchoEnabled", True)
    session.orca.set("TypingEchoPresenter", "WordEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "SentenceEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "CharacterEchoEnabled", False)
    _settle(session)

    _type("a")
    assert helpers.capture(session) == (
        ["a"],
        [
            helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3),
            helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3),
        ],
    )
    _type("b")
    assert helpers.capture(session) == (
        ["b"],
        [
            helpers.BrailleLine(5, "$ ab", "$ ab", "\x00" * 4),
            helpers.BrailleLine(5, "$ ab", "$ ab", "\x00" * 4),
        ],
    )


@pytest.mark.native_app
def test_backspace_and_delete_at_the_prompt(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests Backspace and Delete at the bash prompt with key echo on."""

    session = gtk3_terminal_shell
    session.orca.set("TypingEchoPresenter", "KeyEchoEnabled", True)
    session.orca.set("TypingEchoPresenter", "WordEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "SentenceEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "CharacterEchoEnabled", False)
    _settle(session)

    _type("abc")
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.capture(session) == (["c"], [helpers.BrailleLine(5, "$ ab", "$ ab", "\x00" * 4)])
    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    assert helpers.capture(session) == (["b"], [helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3)])

    # Re-type and Left so Delete has something forward to act on.
    _type("d")
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (["d"], [helpers.BrailleLine(4, "$ ad", "$ ad", "\x00" * 4)])

    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    assert helpers.capture(session) == (["\n"], [helpers.BrailleLine(4, "$ a", "$ a", "\x00" * 3)])


@pytest.mark.native_app
def test_key_echo_while_typing_in_vim(gtk3_terminal_vim: NativeAppSession) -> None:
    """Tests that key echo speaks each character typed in Vim, which redraws as you type."""

    session = gtk3_terminal_vim
    session.orca.set("TypingEchoPresenter", "KeyEchoEnabled", True)
    session.orca.set("TypingEchoPresenter", "WordEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "SentenceEchoEnabled", False)
    session.orca.set("TypingEchoPresenter", "CharacterEchoEnabled", False)
    session.reader.drain(quiescence_timeout=0.6, overall_timeout=6.0)
    session.reader.reset()

    keyboard.tap_key(ord("i"))  # enter insert mode
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    _type("a")
    assert helpers.speech(session) == ["a"]
    _type("b")
    assert helpers.speech(session) == ["b"]


@pytest.mark.native_app
def test_pager_navigation_speaks_each_page(gtk3_terminal_pager: NativeAppSession) -> None:
    """Tests that paging through Less forward and back speaks each newly shown page."""

    session = gtk3_terminal_pager
    _settle(session)

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


def _review_top_line(session: NativeAppSession) -> tuple[list[str], list[helpers.BrailleLine]]:
    """Moves flat review to the top of the screen and returns the (speech, braille) for it."""

    session.orca.call("FlatReviewPresenter", "GoHome", True)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.call("FlatReviewPresenter", "PresentLine", True)
    return helpers.capture(session)


@pytest.mark.native_app
def test_flat_review_reflects_new_page(gtk3_terminal_pager: NativeAppSession) -> None:
    """Tests that reviewing the page's top line shows the new page after paging, not stale text."""

    session = gtk3_terminal_pager
    _settle(session)
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
def test_pan_braille_across_terminal_line(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests panning across a prompt line wider than the display, including the edge-walk."""

    session = gtk3_terminal_shell
    _settle(session)
    _type(_WIDE_PROMPT_INPUT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    with helpers.bound_pan_keys(session) as (left_key, right_key):
        mask = "\x00" * len(_WIDE_PROMPT_LINE)
        # Pan-left slides the window back to the start of the line.
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _WIDE_PROMPT_LINE, "$ abcdefghij klmnopqrst uvwxy 01", mask)],
        )
        # Pan-right slides the window to the end of the line.
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(9, _WIDE_PROMPT_LINE, "01234567", mask)],
        )


@pytest.mark.native_app
def test_pan_braille_left_crosses_wide_line_in_pager(
    gtk3_terminal_wide_pager: NativeAppSession,
) -> None:
    """Tests that panning left over a pager line wider than the display reaches the line above."""

    session = gtk3_terminal_wide_pager
    _settle(session)
    helpers.toggle_flat_review(session)

    wide = "this line is wider than the display now $l"
    wide_mask = "\x00" * len(wide)
    with helpers.bound_pan_keys(session) as (left_key, _right_key):
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(7, "bottom $l", "bottom $l", "\x00" * 9)],
        )
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(12, wide, "display now $l", wide_mask)],
        )
        # The start view is painted twice: by the pan, then by the flat-review zone-sync refresh.
        session.orca.press_bound_key(left_key)
        start_view = "this line is wider than the disp"
        assert helpers.capture(session) == (
            [],
            [
                helpers.BrailleLine(0, wide, start_view, wide_mask),
                helpers.BrailleLine(0, wide, start_view, wide_mask),
            ],
        )
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(4, "top $l", "top $l", "\x00" * 6)],
        )


def _navigate_to_c1_line(session: NativeAppSession) -> None:
    """Moves flat review to the c1/c2 output line and discards the output."""

    session.orca.call("FlatReviewPresenter", "GoHome", True)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.call("FlatReviewPresenter", "GoNextLine", True)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_flat_review_speaks_live_update(gtk3_terminal_flatrev: NativeAppSession) -> None:
    """Tests that a terminal line changing in place is spoken when SpeaksUpdates is on."""

    session = gtk3_terminal_flatrev
    _settle(session)

    _type("bash t.sh")
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    time.sleep(0.5)

    session.orca.set("FlatReviewPresenter", "SpeaksUpdates", True)
    helpers.toggle_flat_review(session)
    _navigate_to_c1_line(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["c1\n"],
        [helpers.BrailleLine(1, "c1 $l", "c1 $l", "\x00" * 5)],
    )

    assert helpers.capture(session, wait_async=True, overall=5.0) == (
        ["c2\n"],
        [
            helpers.BrailleLine(1, "c2 $l", "c2 $l", "\x00" * 5),
            helpers.BrailleLine(1, "c2 $l", "c2 $l", "\x00" * 5),
        ],
    )

    session.orca.set("FlatReviewPresenter", "SpeaksUpdates", False)
    helpers.toggle_flat_review(session)


@pytest.mark.native_app
def test_flat_review_silent_live_update_when_disabled(
    gtk3_terminal_flatrev: NativeAppSession,
) -> None:
    """Tests that a terminal line changing in place is not spoken when SpeaksUpdates is off."""

    session = gtk3_terminal_flatrev
    _settle(session)

    _type("bash t.sh")
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    time.sleep(0.5)

    helpers.toggle_flat_review(session)
    _navigate_to_c1_line(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["c1\n"],
        [helpers.BrailleLine(1, "c1 $l", "c1 $l", "\x00" * 5)],
    )

    assert helpers.capture(session, wait_async=True, overall=5.0) == (
        [],
        [
            helpers.BrailleLine(1, "c2 $l", "c2 $l", "\x00" * 5),
            helpers.BrailleLine(1, "c2 $l", "c2 $l", "\x00" * 5),
        ],
    )

    helpers.toggle_flat_review(session)


@pytest.mark.native_app
def test_move_focus_to_review_location_unchanged(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that move-focus-to-review fails when the terminal won't let us set the caret."""

    session = gtk3_terminal_shell
    _settle(session)

    _type("echo aaa bbb ccc\n")
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    with _bound(session, "move_focus_to_review") as key:
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
    _settle(session)
    _type("clear; printf 'alpha bravo charlie delta echo\\n'; read; clear; printf 'alpha bravo\\n'")
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
