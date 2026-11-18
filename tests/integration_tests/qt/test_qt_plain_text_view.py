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

"""Tests reading and editing in a plain-text editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_native_line_navigation(qt_plain_text_view: NativeAppSession) -> None:
    """Reads successive lines and returns to the previous line."""

    session = qt_plain_text_view
    helpers.move_to_top(session)
    for key, text in (
        (keyboard.KEYSYM_DOWN, "Second line."),
        (keyboard.KEYSYM_DOWN, "Third line."),
        (keyboard.KEYSYM_UP, "Second line."),
    ):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        assert spoken == [text]
        assert brailled[-1].visible == text + " $l"


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=(
        "QAccessibleTextWidget::characterRect() returns the same y "
        "coordinate for different QPlainTextEdit paragraphs: "
        "https://qt-project.atlassian.net/browse/QTBUG-152402"
    ),
    strict=True,
    raises=AssertionError,
)
def test_flat_review_lines(qt_plain_text_view: NativeAppSession) -> None:
    """Reviews separate paragraphs as separate lines."""

    session = qt_plain_text_view
    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["First line."]
    assert brailled[-1].full == "First line. $l"
    keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Second line."]
    assert brailled[-1].full == "Second line. $l"


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=(
        "Qt's QWidgetTextControlPrivate::_q_contentsChanged() replaces deleted "
        "text with spaces in AT-SPI text-change events: "
        "https://qt-project.atlassian.net/browse/QTBUG-152373"
    ),
    strict=True,
    raises=AssertionError,
)
def test_backspace(qt_plain_text_view: NativeAppSession) -> None:
    """Speaks the character removed by Backspace."""

    session = qt_plain_text_view
    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_BACKSPACE)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["F"]
    assert brailled[-1].visible == "irst line. $l"
