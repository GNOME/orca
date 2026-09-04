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

"""Tests presentation of focusable ARIA separators used as window splitters in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_moving_the_splitters(web_window_splitter: NativeAppSession) -> None:
    """Tests tabbing to a vertical and a horizontal splitter and moving each one."""

    session = web_window_splitter
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Notes pane size", "vertical splitter", "50", "50 percent.", "Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["60"]
    assert brailled[-1] == BrailleLine(
        1, "Notes pane size 60 vertical splitter", "Notes pane size 60 vertical spli", "\x00" * 36
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = capture(session)
    assert spoken == ["50"]
    assert brailled[-1] == BrailleLine(
        1, "Notes pane size 50 vertical splitter", "Notes pane size 50 vertical spli", "\x00" * 36
    )

    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["100"]
    assert brailled[-1] == BrailleLine(
        1, "Notes pane size 100 vertical splitter", "Notes pane size 100 vertical spl", "\x00" * 37
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["Notes pane size", "vertical splitter", "100", "100 percent."]
    assert brailled[-1] == BrailleLine(
        1, "Notes pane size 100 vertical splitter", "Notes pane size 100 vertical spl", "\x00" * 37
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Message list size", "horizontal splitter", "40", "40 percent."]
    assert brailled[-1] == BrailleLine(
        1,
        "Message list size 40 horizontal splitter",
        "Message list size 40 horizontal ",
        "\x00" * 40,
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["50"]
    assert brailled[-1] == BrailleLine(
        1,
        "Message list size 50 horizontal splitter",
        "Message list size 50 horizontal ",
        "\x00" * 40,
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["40"]
    assert brailled[-1] == BrailleLine(
        1,
        "Message list size 40 horizontal splitter",
        "Message list size 40 horizontal ",
        "\x00" * 40,
    )

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["0"]
    assert brailled[-1] == BrailleLine(
        1,
        "Message list size 0 horizontal splitter",
        "Message list size 0 horizontal s",
        "\x00" * 39,
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["Message list size", "horizontal splitter", "0", "0 percent."]
    assert brailled[-1] == BrailleLine(
        1,
        "Message list size 0 horizontal splitter",
        "Message list size 0 horizontal s",
        "\x00" * 39,
    )
