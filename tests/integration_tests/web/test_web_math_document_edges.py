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

"""Tests moving to the start and end of a document which starts and ends with math."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers, version_helpers
from tests.integration_tests.apps import browser
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


pytestmark = pytest.mark.skipif(
    not helpers.mathcat_is_installed(), reason="MathCAT (libmathcat_py) is not installed"
)

_FRACTION = "the fraction with numerator; x plus 1; and denominator y minus 2"


@pytest.mark.native_app
@pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason="Firefox's embedded MathML range bounds include the following line of text",
    raises=AssertionError,
    strict=True,
)
def test_start_of_document_on_math(web_math_document_edges: BrowserSession) -> None:
    """Tests moving to the start of a document which starts with math."""

    session = web_math_document_edges
    helpers.move_to_bottom(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    fraction = (
        "⠹⠭⠬⠂⠌⠽⠤⠆⠼"
        if session.browser == "firefox" and not version_helpers.firefox_is_nightly()
        else "⠹⠰⠭⠬⠂⠌⠰⠽⠤⠆⠼"
    )
    assert helpers.capture(session) == (
        [_FRACTION],
        [helpers.BrailleLine(1, fraction, fraction, "\x00" * len(fraction))],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.speech(session) == ["T"]
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.speech(session) == [_FRACTION]


@pytest.mark.native_app
def test_end_of_document_on_math(web_math_document_edges: BrowserSession) -> None:
    """Tests moving to the end of a document which ends with math."""

    session = web_math_document_edges
    helpers.move_to_top(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    fraction = (
        "⠹⠭⠬⠂⠌⠽⠤⠆⠼"
        if session.browser == "firefox" and not version_helpers.firefox_is_nightly()
        else "⠹⠰⠭⠬⠂⠌⠰⠽⠤⠆⠼"
    )
    line = f"A fraction at the end: {fraction}"
    assert helpers.capture(session) == (
        ["A fraction at the end: ", _FRACTION],
        [helpers.BrailleLine(1, line, fraction, "\x00" * len(line))],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.speech(session) == [" "]
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.speech(session) == [_FRACTION]
