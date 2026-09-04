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

"""Tests presentation of multithumb and vertical ARIA sliders in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_changing_the_value_of_each_slider(web_multithumb_slider: NativeAppSession) -> None:
    """Tests tabbing to each slider thumb and changing its value."""

    session = web_multithumb_slider
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Minimum price", "horizontal slider", "$25", "33 percent.", "Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["$26"]
    assert brailled[-1] == BrailleLine(
        1, "Minimum price $26 horizontal slider", "Minimum price $26 horizontal sli", "\x00" * 35
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["$27"]
    assert brailled[-1] == BrailleLine(
        1, "Minimum price $27 horizontal slider", "Minimum price $27 horizontal sli", "\x00" * 35
    )

    keyboard.tap_key(keyboard.KEYSYM_PAGE_UP)
    spoken, brailled = capture(session)
    assert spoken == ["$37"]
    assert brailled[-1] == BrailleLine(
        1, "Minimum price $37 horizontal slider", "Minimum price $37 horizontal sli", "\x00" * 35
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["Minimum price", "horizontal slider", "$37", "49 percent."]
    assert brailled[-1] == BrailleLine(
        1, "Minimum price $37 horizontal slider", "Minimum price $37 horizontal sli", "\x00" * 35
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Maximum price", "horizontal slider", "$75", "60 percent."]
    assert brailled[-1] == BrailleLine(
        1, "Maximum price $75 horizontal slider", "Maximum price $75 horizontal sli", "\x00" * 35
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = capture(session)
    assert spoken == ["$74"]
    assert brailled[-1] == BrailleLine(
        1, "Maximum price $74 horizontal slider", "Maximum price $74 horizontal sli", "\x00" * 35
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Temperature", "vertical slider", "68 degrees", "45 percent."]
    assert brailled[-1] == BrailleLine(
        1, "Temperature 68 degrees vertical slider", "Temperature 68 degrees vertical ", "\x00" * 38
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["69 degrees"]
    assert brailled[-1] == BrailleLine(
        1, "Temperature 69 degrees vertical slider", "Temperature 69 degrees vertical ", "\x00" * 38
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["68 degrees"]
    assert brailled[-1] == BrailleLine(
        1, "Temperature 68 degrees vertical slider", "Temperature 68 degrees vertical ", "\x00" * 38
    )
