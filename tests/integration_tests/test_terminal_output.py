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

"""Integration tests for terminal command output presentation."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest

from . import helpers
from .apps import terminal
from .harness import keyboard
from .terminal_helpers import settle, type_text
from .version_helpers import requires_vte_version

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_command_output_is_spoken(terminal_shell: NativeAppSession) -> None:
    """Tests that the output of a command is spoken when the command completes."""

    session = terminal_shell
    settle(session)

    type_text("echo hi\n")
    assert helpers.speech(session) in (["hi\n$ "], ["hi", "$ "])
    type_text("echo hello world\n")
    assert helpers.speech(session) in (["hello world\n$ "], ["hello world", "$ "])


@pytest.mark.native_app
def test_multiline_command_output_is_spoken(terminal_shell: NativeAppSession) -> None:
    """Tests that multi-line command output is spoken."""

    if shutil.which("seq") is None:
        pytest.skip("seq is not available")

    session = terminal_shell
    settle(session)

    type_text("seq 3\n")
    assert helpers.speech(session) in (["1\n2\n3\n$ "], ["1\n2\n3", "$ "])


@pytest.mark.native_app
@requires_vte_version("3.91", 0, 85, 0, when=terminal.selected_toolkit() == "gtk4")
def test_scrolled_command_output_is_spoken(terminal_shell: NativeAppSession) -> None:
    """Tests that command output which scrolls the terminal is spoken."""

    if shutil.which("seq") is None:
        pytest.skip("seq is not available")

    session = terminal_shell
    settle(session)

    # GTK4 scrolling notifications are fixed in VTE commit 9d70a010761749a515876851b9e6c8bf578c2ac6.
    # The terminal is 8 rows, so seq 20 scrolls lines 1-13 off the top and only the
    # visible remainder is spoken.
    type_text("seq 20\n")
    assert helpers.speech(session) == ["14\n15\n16\n17\n18\n19\n20\n$ \n"]


@pytest.mark.native_app
@pytest.mark.parametrize("final_text", ["after1", "done"], ids=["overwrite", "shorten"])
def test_braille_shows_final_output_after_a_burst(
    terminal_shell: NativeAppSession, final_text: str
) -> None:
    """Tests that braille gets the final overwrite even when no more output follows."""

    session = terminal_shell
    settle(session)
    type_text(f"sleep .3; printf before; sleep .05; printf '\\r{final_text}\\033[K'; read")
    settle(session)
    keyboard.tap_key(keyboard.KEYSYM_RETURN)

    # The command waits for input, so no later prompt can trigger another refresh.
    _spoken, brailled = helpers.capture(session, wait_async=True, quiescence=0.4, overall=2.0)
    assert brailled[-1] == helpers.BrailleLine(
        len(final_text) + 1, final_text, final_text, "\x00" * len(final_text)
    )


@pytest.mark.native_app
def test_terminal_dimensions(terminal_shell: NativeAppSession) -> None:
    """Checks that the program sees the intended terminal grid."""

    session = terminal_shell
    settle(session)
    type_text("stty size")
    settle(session)
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    spoken, brailled = helpers.capture(session)
    assert "".join(spoken) == "8 40\n$ "
    assert brailled[-1] == helpers.BrailleLine(3, "$ ", "$ ", "\x00" * 2)
