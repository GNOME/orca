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

"""Tests reading a plain-text (text/plain) document such as a viewed .txt file."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_line_navigation_in_plain_text_document(web_plain_text: NativeAppSession) -> None:
    """Tests that browsing a plain-text document presents each line."""

    move_to_top(web_plain_text)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(web_plain_text) == (
        ["Second line of the file.\n"],
        [BrailleLine(1, "Second line of the file. $l", "Second line of the file. $l", "\x00" * 27)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(web_plain_text) == (
        ["Third line of the file.\n"],
        [BrailleLine(1, "Third line of the file. $l", "Third line of the file. $l", "\x00" * 26)],
    )
