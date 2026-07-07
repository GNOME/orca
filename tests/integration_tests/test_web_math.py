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
    """Tests inline MathML riding its text line while a standalone expression is its own line."""

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
    assert speech(session) == ["MathCAT on.", _FRACTION]
