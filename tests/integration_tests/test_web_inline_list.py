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

"""Tests layout-mode line assembly for an inline list versus a block list."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_inline_list_items_share_a_line(web_inline_list: NativeAppSession) -> None:
    """Tests that inline list items group onto one line while block items do not."""

    session = web_inline_list
    move_to_top(session)

    # Inline list items render on one visual row and are presented as a single line.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["List with 3 items", "one", "two", "three"]

    # A block list is the contrast: each item is its own line.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["leaving list.", "List with 2 items", "•  alpha"]
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["•  beta"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["leaving list.", "Tail paragraph."]
