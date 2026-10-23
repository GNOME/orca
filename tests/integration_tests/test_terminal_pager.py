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

"""Integration tests for native line navigation in a terminal pager."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .apps import terminal
from .harness import keyboard
from .terminal_helpers import settle

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
@pytest.mark.skipif(
    terminal.selected_toolkit() == "gtk4",
    reason="GTK4 VTE intermittently exposes stale text: "
    "https://gitlab.gnome.org/GNOME/vte/-/work_items/2972",
)
def test_pager_up_speaks_new_top_line(terminal_pager: NativeAppSession) -> None:
    """Tests that Up speaks newly revealed content while the caret stays on the status line."""

    session = terminal_pager
    settle(session)
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        settle(session)

    for number in (3, 2, 1):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        spoken, brailled = helpers.capture(session)
        assert brailled[-1] == helpers.BrailleLine(2, ":", ":", "\x00")
        assert spoken == [f"line {number:02d}\n"]
