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

"""Line navigation through a line-numbered code block containing a blank line."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_blank_line_loops_to_top(web_code_block: NativeAppSession) -> None:
    """Down from the blank line loops back to the top instead of reaching the last line."""

    session = web_code_block
    helpers.reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    helpers.speech(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["blank"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    looped = " ".join(helpers.speech(session))
    # Chromium bug crbug.com/536662914: loops to line 1 ("DPY - 1"), not the last line.
    assert "DPY - 1" in looped
