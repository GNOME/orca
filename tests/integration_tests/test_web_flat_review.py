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

"""Tests flat review word/line review of web document content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine, capture, toggle_flat_review

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _line(full: str, cursor_cell: int) -> BrailleLine:
    return BrailleLine(cursor_cell, full, full, "\x00" * len(full))


def _command(session: NativeAppSession, name: str) -> tuple[list[str], list[BrailleLine]]:
    session.orca.call("FlatReviewPresenter", name, True)
    return capture(session)


@pytest.mark.native_app
def test_review_heading_word_by_word(web_flat_review: NativeAppSession) -> None:
    """Tests word-by-word flat review of a web heading."""

    session = web_flat_review
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_2)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    toggle_flat_review(session)

    full = "Fruit list $l"
    try:
        assert _command(session, "PresentItem") == (["Fruit "], [_line(full, 1)])
        assert _command(session, "GoNextItem") == (["list"], [_line(full, 7)])
        assert _command(session, "PresentLine") == (["Fruit list"], [_line(full, 7)])
    finally:
        toggle_flat_review(session)


@pytest.mark.native_app
def test_review_uppercase_and_repeated_word(web_flat_review: NativeAppSession) -> None:
    """Tests flat review of a word that is an acronym and one with repeated letters."""

    session = web_flat_review
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    toggle_flat_review(session)

    full = "NASA AAAA done. $l"
    try:
        assert _command(session, "PresentItem") == (["NASA "], [_line(full, 1)])
        assert _command(session, "GoNextItem") == (["AAAA "], [_line(full, 6)])
        assert _command(session, "GoNextItem") == (["done."], [_line(full, 11)])
        assert _command(session, "PresentLine") == (["NASA AAAA done."], [_line(full, 11)])
    finally:
        toggle_flat_review(session)


@pytest.mark.native_app
def test_review_hyphenated_word(web_flat_review: NativeAppSession) -> None:
    """Tests that a hyphenated word is reviewed as a single word."""

    session = web_flat_review
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    toggle_flat_review(session)

    full = "a one-two b. $l"
    try:
        assert _command(session, "PresentItem") == (["a "], [_line(full, 1)])
        assert _command(session, "GoNextItem") == (["one-two "], [_line(full, 3)])
        assert _command(session, "GoNextItem") == (["b."], [_line(full, 11)])
        assert _command(session, "PresentLine") == (["a one-two b."], [_line(full, 11)])
    finally:
        toggle_flat_review(session)


@pytest.mark.native_app
def test_spell_and_phonetic_word(web_flat_review: NativeAppSession) -> None:
    """Tests spelling and phonetically spelling a reviewed web word."""

    session = web_flat_review
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    toggle_flat_review(session)

    full = "NASA AAAA done. $l"
    try:
        assert _command(session, "SpellItem") == (["N", "A", "S", "A", " "], [_line(full, 1)])
        assert _command(session, "PhoneticItem") == (
            ["november", "alpha", "sierra", "alpha", " "],
            [_line(full, 1)],
        )
    finally:
        toggle_flat_review(session)
