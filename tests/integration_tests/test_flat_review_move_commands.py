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

"""Tests the unbound flat review move-review-to-focus and move-focus-to-review commands."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, toggle_flat_review

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


def _review_first_entry_then_focus_second(session: NativeAppSession) -> None:
    """Reviews the first entry, then tabs to the second so review and focus differ."""

    session.orca.set("FlatReviewPresenter", "FocusTracking", 0)
    toggle_flat_review(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_move_review_to_focus(gtk3_two_entries: NativeAppSession) -> None:
    """Tests that move-review-to-focus jumps the review to the focused object."""

    session = gtk3_two_entries
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    with _bound(session, "move_review_to_focus") as key:
        _review_first_entry_then_focus_second(session)
        session.orca.press_bound_key(key)
        assert capture(session) == (
            ["recipe"],
            [
                BrailleLine(
                    20,
                    "Banana bread recipe $l",
                    "Banana bread recipe $l",
                    "\xc0" * 19 + "\x00" * 3,
                )
            ],
        )


@pytest.mark.native_app
def test_move_focus_to_review(gtk3_two_entries: NativeAppSession) -> None:
    """Tests that move-focus-to-review moves focus to the reviewed object."""

    session = gtk3_two_entries
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    with _bound(session, "move_focus_to_review") as key:
        _review_first_entry_then_focus_second(session)
        session.orca.press_bound_key(key)
        assert capture(session, wait_async=True) == (
            ["text", "Apple pie recipe"],
            [
                BrailleLine(11, "Apple pie recipe $l", "Apple pie recipe $l", "\x00" * 19),
                BrailleLine(
                    11,
                    "OrcaTwoEntries application frame Apple pie recipe $l",
                    "Apple pie recipe $l",
                    "\x00" * 52,
                ),
            ],
        )


@pytest.mark.native_app
def test_move_focus_to_review_location_unchanged(gtk3_two_entries: NativeAppSession) -> None:
    """Tests that routing focus to an object that cannot take the caret is announced."""

    session = gtk3_two_entries
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    with _bound(session, "move_focus_to_review") as key:
        keyboard.tap_key(keyboard.KEYSYM_TAB)  # second entry
        keyboard.tap_key(keyboard.KEYSYM_TAB)  # the button (no caret to move)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
        toggle_flat_review(session)
        keyboard.tap_key(keyboard.KEYSYM_KP_UP)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
        session.orca.press_bound_key(key)
        assert capture(session) == (
            ["Location unchanged"],
            [BrailleLine(0, "Location unchanged", "Location unchanged", "\x00" * 18)],
        )
