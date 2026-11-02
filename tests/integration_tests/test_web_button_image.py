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

"""Tests caret navigation to a button whose only child is an image."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_end_of_document_on_button_image(web_button_image: BrowserSession) -> None:
    """Tests moving to the end of a document which ends with a button containing an image."""

    session = web_button_image
    move_to_top(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    assert capture(session) == (
        ["Search", "button"],
        [BrailleLine(1, "Search button", "Search button", "\x00" * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert speech(session) == ["."]
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert speech(session) == ["Search", "button"]
