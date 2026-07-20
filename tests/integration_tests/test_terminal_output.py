# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

"""Integration tests for terminal command output presentation."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest

from . import helpers
from .terminal_helpers import settle, type_text

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_command_output_is_spoken(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that the output of a command is spoken when the command completes."""

    session = gtk3_terminal_shell
    settle(session)

    type_text("echo hi\n")
    assert helpers.speech(session) == ["hi\n$ "]
    type_text("echo hello world\n")
    assert helpers.speech(session) == ["hello world\n$ "]


@pytest.mark.native_app
def test_multiline_command_output_is_spoken(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that multi-line command output is spoken."""

    if shutil.which("seq") is None:
        pytest.skip("seq is not available")

    session = gtk3_terminal_shell
    settle(session)

    type_text("seq 3\n")
    assert helpers.speech(session) == ["1\n2\n3\n$ "]


@pytest.mark.native_app
def test_scrolled_command_output_is_spoken(gtk3_terminal_shell: NativeAppSession) -> None:
    """Tests that command output which scrolls the terminal is spoken."""

    if shutil.which("seq") is None:
        pytest.skip("seq is not available")

    session = gtk3_terminal_shell
    settle(session)

    # The terminal is 8 rows, so seq 20 scrolls lines 1-13 off the top and only the
    # visible remainder is spoken.
    type_text("seq 20\n")
    assert helpers.speech(session) == ["14\n15\n16\n17\n18\n19\n20\n$ \n"]
