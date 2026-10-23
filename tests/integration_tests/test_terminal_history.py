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

"""Integration tests for navigating shell command history."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .terminal_helpers import settle, type_text

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_shell_history_navigation(terminal_shell: NativeAppSession) -> None:
    """Tests speech and braille when recalling commands in both directions."""

    session = terminal_shell
    settle(session)
    commands = ("echo foo", "printf 'bar\\n'", "echo baz", "echo whatever")
    for command in commands:
        type_text(command + "\n")
        settle(session)

    # KNOWN ISSUE: https://gitlab.gnome.org/GNOME/vte/-/work_items/2975
    steps = (
        (keyboard.KEYSYM_UP, "echo whatever", "echo whatever"),
        (keyboard.KEYSYM_UP, "echo baz", "baz"),
        (keyboard.KEYSYM_UP, "printf 'bar\\n'", "printf 'bar\\n'"),
        (keyboard.KEYSYM_UP, "echo foo", "echo foo"),
        (keyboard.KEYSYM_DOWN, "printf 'bar\\n'", "printf 'bar\\n'"),
        (keyboard.KEYSYM_DOWN, "echo baz", "echo baz"),
        (keyboard.KEYSYM_DOWN, "echo whatever", "whatever"),
    )
    for key, command, expected_speech in steps:
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        line = "$ " + command
        assert brailled[-1] == helpers.BrailleLine(len(line) + 1, line, line, "\x00" * len(line))
        assert spoken == [expected_speech]
