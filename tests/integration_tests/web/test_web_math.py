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

"""Tests line-navigation presentation of inline and standalone MathML expressions."""

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
def test_line_navigation_over_inline_and_standalone_math(web_math: BrowserSession) -> None:
    """Tests inline and standalone math are presented correctly."""

    session = web_math
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    # Nightly enables mathml.legacy_mathvariant_attribute.disabled: like Chromium,
    # it exposes italic 𝑥/𝑦, for which MathCAT adds English-letter indicators.
    # Release Firefox exposes plain x/y. Keep the MathCAT difference visible.
    fraction = (
        "⠹⠭⠬⠂⠌⠽⠤⠆⠼"
        if session.browser == "firefox" and not version_helpers.firefox_is_nightly()
        else "⠹⠰⠭⠬⠂⠌⠰⠽⠤⠆⠼"
    )
    line = f"A fraction surrounded by text: {fraction} is a lovely thing!"
    assert helpers.capture(session) == (
        ["A fraction surrounded by text: ", _FRACTION, " is a lovely thing!"],
        [helpers.BrailleLine(1, line, "A fraction surrounded by text: ⠹", "\x00" * len(line))],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["A fraction on its own line:"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == [_FRACTION]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["Text after the math."]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.speech(session) == [_FRACTION]


@pytest.mark.native_app
def test_standalone_math_voiced_by_character_and_word_navigation(
    web_math: BrowserSession,
) -> None:
    """Tests character and word navigation onto standalone math are not silent."""

    session = web_math
    helpers.move_to_top(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.speech(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    helpers.speech(session)
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.speech(session) == [_FRACTION]

    helpers.move_to_top(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.speech(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    helpers.speech(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.speech(session) == [_FRACTION]


@pytest.mark.native_app
def test_math_navigation_activation_and_restart(web_math: BrowserSession) -> None:
    """Tests Orca+Alt+M enters math navigation and, pressed again, restarts at the top."""

    session = web_math
    helpers.move_to_top(session)
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.speech(session)

    # The caret is on the standalone fraction. Navigation already read it, so the command
    # only confirms the mode rather than repeating the whole expression.
    session.orca.press_orca_key(keyboard.KEYSYM_M, extra_modifiers=[keyboard.KEYSYM_ALT_L])
    assert helpers.speech(session) == ["MathCAT on."]

    # Move down into the fraction and across to its denominator.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["in numerator; x plus 1"]
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.speech(session) == ["in denominator; y minus 2"]

    # Pressing the command again restarts at the outermost element and re-presents the whole
    # expression; reading the current node then confirms we are back at the root.
    session.orca.press_orca_key(keyboard.KEYSYM_M, extra_modifiers=[keyboard.KEYSYM_ALT_L])
    assert helpers.speech(session) == [_FRACTION]
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert helpers.speech(session) == [_FRACTION]

    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    assert helpers.speech(session) == ["MathCAT off."]

    # Off the math, the command reports there is nothing to navigate.
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.speech(session) == ["A fraction on its own line:"]
    session.orca.press_orca_key(keyboard.KEYSYM_M, extra_modifiers=[keyboard.KEYSYM_ALT_L])
    assert helpers.speech(session) == ["Not in math."]


@pytest.mark.native_app
def test_say_all_over_math(web_math: BrowserSession) -> None:
    """Tests Say All over math."""

    session = web_math
    helpers.move_to_top(session)
    helpers.speech(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert helpers.speech(session) == [
        "Text before the math.",
        "A fraction surrounded by text: ",
        _FRACTION,
        " is a lovely thing!",
        "A fraction on its own line:",
        _FRACTION,
        "Text after the math.",
        "A fraction in a live region: ",
        _FRACTION,
    ]
