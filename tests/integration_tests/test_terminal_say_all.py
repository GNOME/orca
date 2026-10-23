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

"""Tests Say All after terminal content changes."""

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
@pytest.mark.parametrize(
    "run_say_all",
    [
        pytest.param(False, id="fresh"),
        pytest.param(
            True,
            id="after-say-all",
            marks=pytest.mark.xfail(
                terminal.selected_toolkit() == "gtk4",
                reason="GTK4 VTE exposes stale text: https://gitlab.gnome.org/GNOME/vte/-/work_items/2972",
                raises=AssertionError,
                strict=True,
            ),
        ),
    ],
)
def test_say_all_after_vim_page_forward(
    terminal_vim_pages: NativeAppSession,
    run_say_all: bool,
) -> None:
    """Tests that Say All starts at the current caret after Vim redraws a page."""

    session = terminal_vim_pages
    settle(session)
    session.orca.set("SayAllPresenter", "Style", "line")
    if run_say_all:
        keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
        spoken = helpers.speech(session, quiescence=0.5, overall=10.0)
        assert spoken[:7] == [f"line {number:02d}\n" for number in range(1, 8)]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], ord("f"))
    settle(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    actual = helpers.speech(session, quiescence=0.5, overall=10.0)
    assert actual == [f"line {number:02d}\n" for number in range(6, 13)]
