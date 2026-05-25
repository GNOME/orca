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

"""Tests arrow navigation across the tool buttons of a GTK toolbar."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _tool_button(name: str, length: int) -> tuple[list[str], list[BrailleLine]]:
    return (
        [f"{name} button"],
        [
            BrailleLine(
                1,
                f"OrcaToolbar application frame tool bar {name} button",
                f"{name} button",
                "\x00" * length,
            )
        ],
    )


def _press(session: NativeAppSession, keysym: int) -> tuple[list[str], list[BrailleLine]]:
    keyboard.tap_key(keysym)
    return capture(session)


@pytest.mark.native_app
def test_toolbar_arrow_navigation(gtk3_toolbar: NativeAppSession) -> None:
    """Tests that arrowing across a toolbar announces each tool button in its tool bar."""

    session = gtk3_toolbar
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _press(session, keyboard.KEYSYM_RIGHT) == _tool_button("Copy", 50)
    assert _press(session, keyboard.KEYSYM_RIGHT) == _tool_button("Paste", 51)
    assert _press(session, keyboard.KEYSYM_LEFT) == _tool_button("Copy", 50)
    assert _press(session, keyboard.KEYSYM_LEFT) == _tool_button("Cut", 49)
