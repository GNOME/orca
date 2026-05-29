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

"""Tests braille panning over GTK content, including panning the ancestry prefix into view."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_LINE_ONE = "OrcaTextView application frame Line one. $l"
_LINE_TWO = "Line two has additional words to make it long enough that  $l"
_LINE_TWO_WRAP = "the text view wraps it. $l"
_LINE_THREE = "Line three. $l"


def _reset(session: NativeAppSession) -> None:
    """Discards any pending output to give the test a clean baseline."""

    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_pan_braille_reveals_ancestry(gtk3_text_view: NativeAppSession) -> None:
    """Tests that pan-left brings the off-web ancestry prefix into the visible window."""

    session = gtk3_text_view
    _reset(session)
    with helpers.bound_pan_keys(session) as (left_key, right_key):
        # Move off line one, then back to it, so it is freshly presented with its ancestry prefix.
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        _reset(session)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
        mask = "\x00" * len(_LINE_ONE)
        assert helpers.capture(session) == (
            ["Line one.\n"],
            [helpers.BrailleLine(1, _LINE_ONE, "Line one. $l", mask)],
        )
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(32, _LINE_ONE, "OrcaTextView application frame L", mask)],
        )
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(1, _LINE_ONE, "Line one. $l", mask)],
        )


@pytest.mark.native_app
def test_pan_braille_walks_to_next_line(gtk3_text_view: NativeAppSession) -> None:
    """Tests within-line panning and the edge-walk to the following line on a wide line."""

    session = gtk3_text_view
    _reset(session)
    with helpers.bound_pan_keys(session) as (_left_key, right_key):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
        helpers.capture(session)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.capture(session) == (
            ["Line two has additional words to make it long enough that "],
            [
                helpers.BrailleLine(
                    1, _LINE_TWO, "Line two has additional words to", "\x00" * len(_LINE_TWO)
                )
            ],
        )
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [
                helpers.BrailleLine(
                    0, _LINE_TWO, "to make it long enough that  $l", "\x00" * len(_LINE_TWO)
                )
            ],
        )
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(1, _LINE_TWO_WRAP, _LINE_TWO_WRAP, "\x00" * len(_LINE_TWO_WRAP))],
        )
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(1, _LINE_THREE, _LINE_THREE, "\x00" * len(_LINE_THREE))],
        )


def _pan_line_two_off_caret(session: NativeAppSession, right_key: str) -> None:
    """Moves onto the wide second line and pans the window off the caret."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    helpers.capture(session)
    session.orca.press_bound_key(right_key)
    assert helpers.capture(session) == (
        [],
        [
            helpers.BrailleLine(
                0, _LINE_TWO, "to make it long enough that  $l", "\x00" * len(_LINE_TWO)
            )
        ],
    )


@pytest.mark.native_app
def test_navigate_by_character_snaps_braille_back(gtk3_text_view: NativeAppSession) -> None:
    """Tests that navigating by character pulls a panned-away window back onto the caret."""

    session = gtk3_text_view
    _reset(session)
    with helpers.bound_pan_keys(session) as (_left_key, right_key):
        _pan_line_two_off_caret(session, right_key)
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        assert helpers.capture(session) == (
            ["i"],
            [
                helpers.BrailleLine(
                    1, _LINE_TWO, "ine two has additional words to ", "\x00" * len(_LINE_TWO)
                )
            ],
        )


@pytest.mark.native_app
def test_navigate_by_word_snaps_braille_back(gtk3_text_view: NativeAppSession) -> None:
    """Tests that navigating by word pulls a panned-away window back onto the caret."""

    session = gtk3_text_view
    _reset(session)
    with helpers.bound_pan_keys(session) as (_left_key, right_key):
        _pan_line_two_off_caret(session, right_key)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        assert helpers.capture(session) == (
            ["Line"],
            [
                helpers.BrailleLine(
                    1, _LINE_TWO, " two has additional words to mak", "\x00" * len(_LINE_TWO)
                )
            ],
        )


@pytest.mark.native_app
def test_navigate_by_line_snaps_braille_back(gtk3_text_view: NativeAppSession) -> None:
    """Tests that navigating by line pulls a panned-away window back onto the caret."""

    session = gtk3_text_view
    _reset(session)
    with helpers.bound_pan_keys(session) as (_left_key, right_key):
        _pan_line_two_off_caret(session, right_key)
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.capture(session) == (
            ["the text view wraps it.\n"],
            [
                helpers.BrailleLine(
                    1, _LINE_TWO_WRAP, "the text view wraps it. $l", "\x00" * len(_LINE_TWO_WRAP)
                )
            ],
        )
