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

"""Tests presentation of ARIA switches in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_toggling_switches(web_switch: NativeAppSession) -> None:
    """Tests tabbing to each switch and toggling it with space."""

    session = web_switch
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Dark theme", "off switch"]
    assert brailled[-1] == BrailleLine(
        1, "& y Dark theme switch", "& y Dark theme switch", "\x00" * 21
    )

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["on"]
    assert brailled[-1] == BrailleLine(
        1, "&=y Dark theme switch", "&=y Dark theme switch", "\x00" * 21
    )

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["off"]
    assert brailled[-1] == BrailleLine(
        1, "& y Dark theme switch", "& y Dark theme switch", "\x00" * 21
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Sound effects", "off switch"]
    assert brailled[-1] == BrailleLine(
        1, "& y Sound effects switch", "& y Sound effects switch", "\x00" * 24
    )

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["on"]
    assert brailled[-1] == BrailleLine(
        1, "&=y Sound effects switch", "&=y Sound effects switch", "\x00" * 24
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["Sound effects", "on switch"]
    assert brailled[-1] == BrailleLine(
        1, "&=y Sound effects switch", "&=y Sound effects switch", "\x00" * 24
    )

    # A toggle button that is not a switch keeps the pressed wording.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Bold", "toggle button not pressed"]
    assert brailled[-1] == BrailleLine(
        1, "& y Bold toggle button", "& y Bold toggle button", "\x00" * 22
    )
