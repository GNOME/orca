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

"""Tests terminal repaint presentation when a deletion follows an insertion."""

from __future__ import annotations

import signal
import time
from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .terminal_helpers import settle

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
@pytest.mark.parametrize("backlog", [False, True], ids=["live", "queued"])
def test_navigation_with_trailing_deletion(
    terminal_trailing_deletion: NativeAppSession, backlog: bool
) -> None:
    """The last deletion must not leave braille showing the previous line."""

    session = terminal_trailing_deletion
    settle(session)
    captures = []
    for key, text in ((keyboard.KEYSYM_UP, "new line"), (keyboard.KEYSYM_DOWN, "old line")):
        keyboard.tap_key(key)
        if backlog:
            # Let both terminal updates arrive before this isolated Orca processes them.
            process = session.orca._process  # pylint: disable=protected-access
            assert process is not None
            process.send_signal(signal.SIGSTOP)
            try:
                time.sleep(0.6)
            finally:
                process.send_signal(signal.SIGCONT)
        _spoken, brailled = helpers.capture(session, wait_async=True, overall=3.0)
        captures.append((text, brailled))
    for text, brailled in captures:
        assert brailled, f"No braille update for {text!r}"
        assert brailled[-1] == helpers.BrailleLine(1, text, text, "\x00" * len(text))
