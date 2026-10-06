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

"""Tests repeated-symbol speech in a GTK text view."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
@pytest.mark.parametrize("line_number", [1, 2], ids=["plain", "zero-width-spaces"])
def test_repeated_emoji_with_and_without_zero_width_spaces(
    gtk3_text_view_repeated_symbols: NativeAppSession, line_number: int
) -> None:
    """Tests that U+FEFF does not prevent repeated emoji from being counted."""

    session = gtk3_text_view_repeated_symbols
    move_to_top(session)
    for _ in range(line_number - 1):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        speech(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["10 🎵 characters\n"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    speech(session)
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["10 🎵 characters\n"]
