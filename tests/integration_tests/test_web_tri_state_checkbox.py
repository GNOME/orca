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

"""Tests presentation of tri-state check boxes in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_tri_state_checkbox_cycling(web_tri_state_checkbox: NativeAppSession) -> None:
    """Tests tri-state check box cycling."""

    session = web_tri_state_checkbox
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Forward", "check box not checked"]
    assert brailled[-1] == BrailleLine(
        1, "< > Forward check box", "< > Forward check box", "\x00" * 21
    )

    for state, indicator in (
        ("partially checked", "<->"),
        ("checked", "<x>"),
        ("not checked", "< >"),
        ("partially checked", "<->"),
    ):
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        spoken, brailled = capture(session)
        assert spoken == [state]
        line = f"{indicator} Forward check box"
        assert brailled[-1] == BrailleLine(1, line, line, "\x00" * 21)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Backward", "check box checked"]
    assert brailled[-1] == BrailleLine(
        1, "<x> Backward check box", "<x> Backward check box", "\x00" * 22
    )

    for state, indicator in (
        ("partially checked", "<->"),
        ("not checked", "< >"),
        ("checked", "<x>"),
        ("partially checked", "<->"),
    ):
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        spoken, brailled = capture(session)
        assert spoken == [state]
        line = f"{indicator} Backward check box"
        assert brailled[-1] == BrailleLine(1, line, line, "\x00" * 22)
