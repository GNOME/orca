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

"""Tests how the flat review focus-tracking setting reacts to a window change.

The text view being reviewed is the same object focus returns to after the
window round trip, so these tests isolate the window:activate handling from the
within-window focus-change handling covered in test_flat_review_focus_tracking.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, toggle_flat_review

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _review_second_line_then_switch_away_and_back(session: NativeAppSession) -> None:
    """Reviews the second line, switches to the other window, and returns to this one."""

    toggle_flat_review(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
    assert capture(session) == (
        ["Second line.\n"],
        [BrailleLine(1, "Second line. $l", "Second line. $l", "\x00" * 15)],
    )

    # F2 activates the second window; F3 returns to the first.
    keyboard.tap_key(keyboard.KEYSYM_F2)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_F3)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_focus_tracking_on_resets_review_on_window_change(
    gtk3_two_windows: NativeAppSession,
) -> None:
    """Tests that FocusTracking=on resets the review location after a window change."""

    session = gtk3_two_windows
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.set("FlatReviewPresenter", "FocusTracking", 2)
    _review_second_line_then_switch_away_and_back(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert capture(session) == (
        ["First line.\n"],
        [BrailleLine(1, "First line. $l", "First line. $l", "\x00" * 14)],
    )


@pytest.mark.native_app
def test_focus_tracking_off_keeps_review_on_window_change(
    gtk3_two_windows: NativeAppSession,
) -> None:
    """Tests that FocusTracking=off keeps the review location after a window change."""

    session = gtk3_two_windows
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.set("FlatReviewPresenter", "FocusTracking", 0)
    _review_second_line_then_switch_away_and_back(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert capture(session) == (
        ["Second line.\n"],
        [BrailleLine(1, "Second line. $l", "Second line. $l", "\x00" * 15)],
    )


@pytest.mark.native_app
def test_focus_tracking_auto_keeps_review_on_window_change(
    gtk3_two_windows: NativeAppSession,
) -> None:
    """Tests that FocusTracking=auto keeps the review location after a brief window change."""

    session = gtk3_two_windows
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.set("FlatReviewPresenter", "FocusTracking", 1)
    _review_second_line_then_switch_away_and_back(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert capture(session) == (
        ["Second line.\n"],
        [BrailleLine(1, "Second line. $l", "Second line. $l", "\x00" * 15)],
    )


@pytest.mark.native_app
def test_reviewing_after_window_switch_presents_the_new_window(
    gtk3_two_windows: NativeAppSession,
) -> None:
    """Tests that reviewing after activating another window reviews that window."""

    session = gtk3_two_windows
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.set("FlatReviewPresenter", "FocusTracking", 0)

    toggle_flat_review(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_F2)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert capture(session) == (
        ["Second Second window entry"],
        [
            BrailleLine(
                20,
                "Second Second window entry $l",
                "Second window entry $l",
                "\x00" * 7 + "\xc0" * 19 + "\x00" * 3,
            )
        ],
    )
