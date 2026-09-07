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

"""Tests presentation of tri-state check boxes in a GTK window."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_PREFIX = "OrcaTriStateCheckbox application frame "


@pytest.mark.native_app
def test_tri_state_checkbox_cycling(gtk3_tri_state_checkbox: NativeAppSession) -> None:
    """Tests tri-state check box cycling."""

    session = gtk3_tri_state_checkbox

    for state, indicator in (
        ("partially checked", "<->"),
        ("checked", "<x>"),
        ("not checked", "< >"),
        ("partially checked", "<->"),
    ):
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        spoken, brailled = capture(session)
        assert spoken == [state]
        line = f"{_PREFIX}{indicator} Forward check box"
        assert brailled[-1] == BrailleLine(
            1, line, f"{indicator} Forward check box", "\x00" * len(line)
        )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Backward check box checked"]
    line = f"{_PREFIX}<x> Backward check box"
    assert brailled[-1] == BrailleLine(1, line, "<x> Backward check box", "\x00" * len(line))

    for state, indicator in (
        ("partially checked", "<->"),
        ("not checked", "< >"),
        ("checked", "<x>"),
        ("partially checked", "<->"),
    ):
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        spoken, brailled = capture(session)
        assert spoken == [state]
        line = f"{_PREFIX}{indicator} Backward check box"
        assert brailled[-1] == BrailleLine(
            1, line, f"{indicator} Backward check box", "\x00" * len(line)
        )
