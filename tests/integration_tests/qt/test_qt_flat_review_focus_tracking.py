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

"""Tests how the flat review focus-tracking setting follows focus across objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


def _review_first_entry_then_tab_to_second(session: NativeAppSession) -> None:
    """Reviews the first entry, confirms the location, then tabs to the second entry."""
    helpers.toggle_flat_review(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["Apple pie recipe"],
        [helpers.BrailleLine(17, "Apple pie recipe $l", "Apple pie recipe $l", "\x00" * 19)],
    )
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_empty_entry_includes_role(qt_two_entries: NativeAppSession) -> None:
    """Tests role fallback when reviewing an unnamed empty entry."""
    session = qt_two_entries
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    helpers.capture(session)
    helpers.toggle_flat_review(session)
    try:
        keyboard.tap_key(keyboard.KEYSYM_KP_UP)
        assert helpers.capture(session) == (
            ["text"],
            [helpers.BrailleLine(1, "text $l", "text $l", "\x00" * 7)],
        )
    finally:
        helpers.toggle_flat_review(session)


@pytest.mark.native_app
def test_focus_tracking_off_keeps_review_on_unfocused_object(
    qt_two_entries: NativeAppSession,
) -> None:
    """Tests that FocusTracking=off keeps the review location when focus moves away."""
    session = qt_two_entries
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.set("FlatReviewPresenter", "FocusTracking", 0)
    _review_first_entry_then_tab_to_second(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["Apple pie recipe"],
        [helpers.BrailleLine(11, "Apple pie recipe $l", "Apple pie recipe $l", "\x00" * 19)],
    )


@pytest.mark.native_app
def test_focus_tracking_auto_follows_focus_to_new_object(qt_two_entries: NativeAppSession) -> None:
    """Tests that FocusTracking=auto moves the review location to the newly focused object."""
    session = qt_two_entries
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.set("FlatReviewPresenter", "FocusTracking", 1)
    _review_first_entry_then_tab_to_second(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["Banana bread recipe"],
        [
            helpers.BrailleLine(
                20, "Banana bread recipe $l", "Banana bread recipe $l", "\xc0" * 19 + "\x00" * 3
            )
        ],
    )


@pytest.mark.native_app
def test_focus_tracking_on_follows_focus_to_new_object(qt_two_entries: NativeAppSession) -> None:
    """Tests that FocusTracking=on moves the review location to the newly focused object."""
    session = qt_two_entries
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.set("FlatReviewPresenter", "FocusTracking", 2)
    _review_first_entry_then_tab_to_second(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["Banana bread recipe"],
        [
            helpers.BrailleLine(
                20, "Banana bread recipe $l", "Banana bread recipe $l", "\xc0" * 19 + "\x00" * 3
            )
        ],
    )
