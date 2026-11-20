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

"""Tests flat review when focus moves between windows."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


def _review_second_line_then_switch_away_and_back(session: NativeAppSession) -> None:
    """Reviews the second line, switches to the other window, and returns to this one."""
    helpers.toggle_flat_review(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
    assert helpers.capture(session) == (
        ["Second line."],
        [helpers.BrailleLine(1, "Second line. $l", "Second line. $l", "\x00" * 15)],
    )
    keyboard.tap_key(keyboard.KEYSYM_F2)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_F3)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=(
        "Qt's GetStringAtOffset(LINE) omits newlines, preventing flat "
        "review from advancing to the next line: "
        "https://qt-project.atlassian.net/browse/QTBUG-152403"
    ),
    strict=True,
    raises=AssertionError,
)
def test_focus_tracking_on_resets_review_on_window_change(
    qt_two_windows: NativeAppSession,
) -> None:
    """Tests that FocusTracking=on resets the review location after a window change."""
    session = qt_two_windows
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.set("FlatReviewPresenter", "FocusTracking", 2)
    _review_second_line_then_switch_away_and_back(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["First line."],
        [helpers.BrailleLine(1, "First line. $l", "First line. $l", "\x00" * 14)],
    )


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=(
        "Qt's GetStringAtOffset(LINE) omits newlines, preventing flat "
        "review from advancing to the next line: "
        "https://qt-project.atlassian.net/browse/QTBUG-152403"
    ),
    strict=True,
    raises=AssertionError,
)
def test_focus_tracking_off_keeps_review_on_window_change(
    qt_two_windows: NativeAppSession,
) -> None:
    """Tests that FocusTracking=off keeps the review location after a window change."""
    session = qt_two_windows
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.set("FlatReviewPresenter", "FocusTracking", 0)
    _review_second_line_then_switch_away_and_back(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["Second line."],
        [helpers.BrailleLine(1, "Second line. $l", "Second line. $l", "\x00" * 15)],
    )


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=(
        "Qt's GetStringAtOffset(LINE) omits newlines, preventing flat "
        "review from advancing to the next line: "
        "https://qt-project.atlassian.net/browse/QTBUG-152403"
    ),
    strict=True,
    raises=AssertionError,
)
def test_focus_tracking_auto_keeps_review_on_window_change(
    qt_two_windows: NativeAppSession,
) -> None:
    """Tests that FocusTracking=auto keeps the review location after a brief window change."""
    session = qt_two_windows
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.set("FlatReviewPresenter", "FocusTracking", 1)
    _review_second_line_then_switch_away_and_back(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["Second line."],
        [helpers.BrailleLine(1, "Second line. $l", "Second line. $l", "\x00" * 15)],
    )


@pytest.mark.native_app
def test_reviewing_after_window_switch_presents_the_new_window(
    qt_two_windows: NativeAppSession,
) -> None:
    """Tests that reviewing after activating another window reviews that window."""
    session = qt_two_windows
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.set("FlatReviewPresenter", "FocusTracking", 0)
    helpers.toggle_flat_review(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_F2)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["Second Second window entry"],
        [
            helpers.BrailleLine(
                20,
                "Second Second window entry $l",
                "Second window entry $l",
                "\x00" * 29,
            )
        ],
    )
