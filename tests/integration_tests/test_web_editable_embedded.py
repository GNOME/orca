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

"""Tests navigating and editing a contenteditable region that contains embedded objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_LINK_LINE_MASK = "\x00" * 8 + "\xc0" * 8 + "\x00" * 10


@pytest.mark.native_app
def test_line_navigation_down_and_up(web_editable_embedded: NativeAppSession) -> None:
    """Tests reading a contenteditable's lines (one with an embedded link) down then back up."""

    session = web_editable_embedded
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session, wait_async=True) == (
        ["Focus mode"],
        [
            BrailleLine(0, "First line of notes. $l", "First line of notes. $l", "\x00" * 23),
            BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["See ", "the link", "link", " below."],
        [
            BrailleLine(0, "First line of notes. $l", "First line of notes. $l", "\x00" * 23),
            BrailleLine(
                1, "See  $l the link below. $l", "See  $l the link below. $l", _LINK_LINE_MASK
            ),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Last line of notes."],
        [BrailleLine(1, "Last line of notes. $l", "Last line of notes. $l", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["See ", "the link", "link", " below."],
        [
            BrailleLine(
                1, "See  $l the link below. $l", "See  $l the link below. $l", _LINK_LINE_MASK
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["First line of notes."],
        [BrailleLine(1, "First line of notes. $l", "First line of notes. $l", "\x00" * 23)],
    )


@pytest.mark.native_app
def test_word_navigation_onto_embedded_link(web_editable_embedded: NativeAppSession) -> None:
    """Tests that word-navigating onto an embedded link in a contenteditable announces it."""

    session = web_editable_embedded
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session, wait_async=True)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    capture(session, wait_async=True)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["See "],
        [
            BrailleLine(
                4, "See  $l the link below. $l", "See  $l the link below. $l", _LINK_LINE_MASK
            )
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["the link", "link"],
        [BrailleLine(1, "the link", "the link", "\xc0" * 8)],
    )


@pytest.mark.native_app
def test_character_navigation_into_embedded_link(web_editable_embedded: NativeAppSession) -> None:
    """Tests that character-navigating into an embedded link switches braille to the link."""

    session = web_editable_embedded
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session, wait_async=True)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    capture(session, wait_async=True)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["t"],
        [
            BrailleLine(
                5, "See  $l the link below. $l", "See  $l the link below. $l", _LINK_LINE_MASK
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["h"],
        [BrailleLine(1, "the link", "the link", "\xc0" * 8)],
    )


@pytest.mark.native_app
def test_character_deletion_and_insertion(web_editable_embedded: NativeAppSession) -> None:
    """Tests presentation of character deletion and insertion in a contenteditable."""

    session = web_editable_embedded
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session, wait_async=True)

    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    assert capture(session) == (
        ["i"],
        [
            BrailleLine(0, "First line of notes. $l", "First line of notes. $l", "\x00" * 23),
            BrailleLine(1, "irst line of notes. $l", "irst line of notes. $l", "\x00" * 22),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], ord("f"))
    assert capture(session) == (
        ["F"],
        [BrailleLine(2, "First line of notes. $l", "First line of notes. $l", "\x00" * 23)],
    )


@pytest.mark.native_app
def test_navigation_after_edit_reads_fresh_content(web_editable_embedded: NativeAppSession) -> None:
    """Tests that arrowing to an edited line reads its current text rather than a stale cache."""

    session = web_editable_embedded
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session, wait_async=True)
    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["irst line of notes."],
        [BrailleLine(1, "irst line of notes. $l", "irst line of notes. $l", "\x00" * 22)],
    )

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], ord("f"))
    capture(session)
