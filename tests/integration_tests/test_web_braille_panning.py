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

"""Tests braille panning on a wide line, and that navigation snaps the window back to the caret."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_FULL_LONG = (
    "The quick brown fox jumps over the lazy dog and then keeps running across the wide "
    "open field for a very"
)
_VISIBLE_LONG = "The quick brown fox jumps over t"
_LONG_MASK = "\x00" * (len(_FULL_LONG) + 1)

_FULL_RICH = (
    "Plain leading words and filler before a middle link followed by "
    "bold and slanted trailing filler words"
)
_RICH_MASK = "\x00" * 40 + "\xc0" * 11 + "\x00" * 52

_PAN_LINE_CONTRACTED = (
    "_the qk br{n fox jumps ov} ! lazy dog & !n keeps runn+ acr ! wide op5 field =a v"
)


def _reset(session: NativeAppSession) -> None:
    """Resets state and moves to the top of the document."""

    helpers.reset_web_state(session)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_navigate_by_character_snaps_braille_back(web_long_line: NativeAppSession) -> None:
    """Tests that navigating by character pulls a panned-away window back onto the caret."""

    session = web_long_line
    _reset(session)
    with helpers.bound_pan_keys(session) as (_left_key, right_key):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(session)
        session.orca.press_bound_key(right_key)  # pan the window off the caret
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _FULL_LONG, "the lazy dog and then keeps runn", _LONG_MASK)],
        )
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        assert helpers.capture(session) == (
            ["h"],
            [helpers.BrailleLine(2, _FULL_LONG, _VISIBLE_LONG, _LONG_MASK)],
        )
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        assert helpers.capture(session) == (
            ["e"],
            [helpers.BrailleLine(3, _FULL_LONG, _VISIBLE_LONG, _LONG_MASK)],
        )


@pytest.mark.native_app
def test_navigate_by_word_snaps_braille_back(web_long_line: NativeAppSession) -> None:
    """Tests that navigating by word pulls a panned-away window back onto the caret."""

    session = web_long_line
    _reset(session)
    with helpers.bound_pan_keys(session) as (_left_key, right_key):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(session)
        session.orca.press_bound_key(right_key)  # pan the window off the caret
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _FULL_LONG, "the lazy dog and then keeps runn", _LONG_MASK)],
        )
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        assert helpers.capture(session) == (
            ["The "],
            [helpers.BrailleLine(4, _FULL_LONG, _VISIBLE_LONG, _LONG_MASK)],
        )
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
        assert helpers.capture(session) == (
            ["quick "],
            [helpers.BrailleLine(10, _FULL_LONG, _VISIBLE_LONG, _LONG_MASK)],
        )


@pytest.mark.native_app
def test_navigate_by_line_snaps_braille_back(web_long_line: NativeAppSession) -> None:
    """Tests that navigating by line pulls a panned-away window back onto the caret."""

    session = web_long_line
    _reset(session)
    with helpers.bound_pan_keys(session) as (_left_key, right_key):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(session)
        session.orca.press_bound_key(right_key)  # pan the window off the caret
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _FULL_LONG, "the lazy dog and then keeps runn", _LONG_MASK)],
        )
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.capture(session) == (
            ["long time."],
            [helpers.BrailleLine(1, "long time.", "long time.", "\x00" * 10)],
        )
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.capture(session) == (
            ["Second paragraph line."],
            [
                helpers.BrailleLine(
                    1, "Second paragraph line.", "Second paragraph line.", "\x00" * 22
                )
            ],
        )


@pytest.mark.native_app
def test_pan_braille_right_then_left(web_long_line: NativeAppSession) -> None:
    """Tests that pan-right/pan-left slide the 32-cell window along the wide line."""

    session = web_long_line
    _reset(session)
    with helpers.bound_pan_keys(session) as (left_key, right_key):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(session)

        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _FULL_LONG, "the lazy dog and then keeps runn", _LONG_MASK)],
        )
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _FULL_LONG, "running across the wide open fie", _LONG_MASK)],
        )
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _FULL_LONG, "the lazy dog and then keeps runn", _LONG_MASK)],
        )


@pytest.mark.native_app
def test_pan_left_with_word_wrap_returns_to_intermediate_range(
    web_long_line: NativeAppSession,
) -> None:
    """Tests that with word wrap on, pan-left reveals the previously panned-over range."""

    session = web_long_line
    _reset(session)
    session.orca.set("BraillePresenter", "WordWrapIsEnabled", True)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    try:
        with helpers.bound_pan_keys(session) as (left_key, right_key):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            helpers.capture(session)

            session.orca.press_bound_key(right_key)
            assert helpers.capture(session) == (
                [],
                [helpers.BrailleLine(0, _FULL_LONG, "the lazy dog and then keeps ", _LONG_MASK)],
            )
            session.orca.press_bound_key(right_key)
            assert helpers.capture(session) == (
                [],
                [helpers.BrailleLine(0, _FULL_LONG, "running across the wide open ", _LONG_MASK)],
            )
            session.orca.press_bound_key(left_key)
            assert helpers.capture(session) == (
                [],
                [helpers.BrailleLine(0, _FULL_LONG, "the lazy dog and then keeps ", _LONG_MASK)],
            )
    finally:
        session.orca.set("BraillePresenter", "WordWrapIsEnabled", False)


@pytest.mark.native_app
def test_pan_left_after_crossing_forward(
    web_long_line: NativeAppSession,
) -> None:
    """Documents a known bug: pan-left after a forward line cross jumps past the previous line."""

    session = web_long_line
    _reset(session)
    session.orca.set("BraillePresenter", "WordWrapIsEnabled", True)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    try:
        with helpers.bound_pan_keys(session) as (left_key, right_key):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            helpers.capture(session)

            for _ in range(3):
                session.orca.press_bound_key(right_key)
                helpers.capture(session)
            session.orca.press_bound_key(right_key)
            next_line = helpers.BrailleLine(1, "long time.", "long time.", "\x00" * 10)
            assert helpers.capture(session) == ([], [next_line, next_line])

            # KNOWN BUG (Chromium and Gecko): pan-left should land on the previous line's tail,
            # but set_caret_position produces a spurious text-caret-moved that Orca trusts,
            # lacking a TextEventReason to mark it a side effect of panning. To be fixed later.
            heading = helpers.BrailleLine(1, "Long line h1", "Long line h1", "\x00" * 12)
            session.orca.press_bound_key(left_key)
            assert helpers.capture(session) == ([], [heading, heading])
    finally:
        session.orca.set("BraillePresenter", "WordWrapIsEnabled", False)


@pytest.mark.native_app
def test_pan_left_at_line_start_moves_to_previous_line(web_long_line: NativeAppSession) -> None:
    """Tests the web override: pan-left at the line start walks to the previous line."""

    session = web_long_line
    _reset(session)
    with helpers.bound_pan_keys(session) as (left_key, _right_key):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(session)

        session.orca.press_bound_key(left_key)
        heading = helpers.BrailleLine(1, "Long line h1", "Long line h1", "\x00" * 12)
        assert helpers.capture(session) == ([], [heading, heading])


@pytest.mark.native_app
def test_pan_requires_grab_refresh(web_long_line: NativeAppSession) -> None:
    """Tests that a bound pan key does nothing until the grabs are refreshed."""

    session = web_long_line
    _reset(session)
    ((right_key, right_mods),) = session.orca.available_keybindings(1)
    session.orca.bind_command(helpers.PAN_RIGHT_COMMAND, right_key, right_mods)
    try:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.capture(session)

        # Bound but not refreshed: no grab, so the press neither pans nor is presented.
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == ([], [])

        # After refreshing grabs, the same press pans.
        session.orca.refresh_keybindings()
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _FULL_LONG, "the lazy dog and then keeps runn", _LONG_MASK)],
        )
    finally:
        session.orca.unbind_command(helpers.PAN_RIGHT_COMMAND)
        session.orca.refresh_keybindings()


@pytest.mark.native_app
def test_pan_braille_over_assembled_link_line(web_long_line: NativeAppSession) -> None:
    """Tests panning a layout-mode line assembled from text + an inline link + styled spans."""

    session = web_long_line
    _reset(session)
    with helpers.bound_pan_keys(session) as (left_key, right_key):
        # Reach the wide rich paragraph's first visual line (heading, the two long-line rows,
        # the second paragraph, the blank line, then the "See the link" line).
        for _ in range(6):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            helpers.capture(session)

        # The mask stays pinned to "middle link" as the window slides; a regression that
        # re-introduced a stray link cell elsewhere would change it.
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _FULL_RICH, "before a middle link followed by", _RICH_MASK)],
        )
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _FULL_RICH, "by bold and slanted trailing fil", _RICH_MASK)],
        )
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _FULL_RICH, "before a middle link followed by", _RICH_MASK)],
        )


@pytest.mark.native_app
def test_pan_contracted_line_walks_to_next_visual_line(web_long_line: NativeAppSession) -> None:
    """Pans a contracted line to its end, then onto the next visual line."""

    session = web_long_line
    _reset(session)
    session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", True)
    session.orca.set("BraillePresenter", "ContractionTable", "en-us-g2")
    session.reader.drain(quiescence_timeout=0.4, overall_timeout=2.0)
    session.reader.reset()
    contracted_mask = "\x00" * len(_PAN_LINE_CONTRACTED)
    with helpers.bound_pan_keys(session) as (_left_key, right_key):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.capture(session) == (
            [
                "The quick brown fox jumps over the lazy dog and then keeps running "
                "across the wide open field for a very "
            ],
            [
                helpers.BrailleLine(
                    1, _PAN_LINE_CONTRACTED, "_the qk br{n fox jumps ov} ! laz", contracted_mask
                )
            ],
        )
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [
                helpers.BrailleLine(
                    0, _PAN_LINE_CONTRACTED, "lazy dog & !n keeps runn+ acr ! ", contracted_mask
                )
            ],
        )
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, _PAN_LINE_CONTRACTED, "wide op5 field =a v", contracted_mask)],
        )
        # Panning past the end walks to the next visual line ("long time.").
        session.orca.press_bound_key(right_key)
        next_line = helpers.BrailleLine(1, 'long "t4', 'long "t4', "\x00" * 8)
        assert helpers.capture(session) == ([], [next_line, next_line])
