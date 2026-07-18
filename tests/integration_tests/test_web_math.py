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

import glob
import os
import shutil
from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _mathcat_available() -> bool:
    binary = os.environ.get("ORCA_TEST_BINARY") or shutil.which("orca") or ""
    if not binary:
        return False
    prefix = os.path.dirname(os.path.dirname(os.path.realpath(binary)))
    pattern = os.path.join(prefix, "lib*", "python*", "*-packages", "orca", "libmathcat_py*")
    return bool(glob.glob(pattern))


pytestmark = pytest.mark.skipif(
    not _mathcat_available(), reason="MathCAT (libmathcat_py) is not installed"
)

_FRACTION = "the fraction with numerator; x plus 1; and denominator y minus 2"


@pytest.mark.native_app
def test_line_navigation_over_inline_and_standalone_math(web_math: NativeAppSession) -> None:
    """Tests inline and standalone math are presented correctly."""

    session = web_math
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["A fraction surrounded by text: ", _FRACTION, " is a lovely thing!"],
        [
            BrailleLine(
                1,
                "A fraction surrounded by text: ⠹⠰⠭⠬⠂⠌⠰⠽⠤⠆⠼ is a lovely thing!",
                "A fraction surrounded by text: ⠹",
                "\x00" * 61,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["A fraction on its own line:"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == [_FRACTION]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Text after the math."]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == [_FRACTION]


@pytest.mark.native_app
def test_standalone_math_voiced_by_character_and_word_navigation(
    web_math: NativeAppSession,
) -> None:
    """Tests character and word navigation onto standalone math are not silent."""

    session = web_math
    move_to_top(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        speech(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    speech(session)
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert speech(session) == [_FRACTION]

    move_to_top(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        speech(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    speech(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert speech(session) == [_FRACTION]


@pytest.mark.native_app
def test_math_navigation_activation_and_restart(web_math: NativeAppSession) -> None:
    """Tests Orca+Alt+M enters math navigation and, pressed again, restarts at the top."""

    session = web_math
    move_to_top(session)
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        speech(session)

    # The caret is on the standalone fraction. Navigation already read it, so the command
    # only confirms the mode rather than repeating the whole expression.
    session.orca.press_orca_key(keyboard.KEYSYM_M, extra_modifiers=[keyboard.KEYSYM_ALT_L])
    assert speech(session) == ["MathCAT on."]

    # Move down into the fraction and across to its denominator.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["in numerator; x plus 1"]
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert speech(session) == ["in denominator; y minus 2"]

    # Pressing the command again restarts at the outermost element and re-presents the whole
    # expression; reading the current node then confirms we are back at the root.
    session.orca.press_orca_key(keyboard.KEYSYM_M, extra_modifiers=[keyboard.KEYSYM_ALT_L])
    assert speech(session) == [_FRACTION]
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == [_FRACTION]

    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    assert speech(session) == ["MathCAT off."]

    # Off the math, the command reports there is nothing to navigate.
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["A fraction on its own line:"]
    session.orca.press_orca_key(keyboard.KEYSYM_M, extra_modifiers=[keyboard.KEYSYM_ALT_L])
    assert speech(session) == ["Not in math."]
