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

"""Tests line reading of emoji text and inline links in an attributed-string block."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_line_reading_emoji_text_and_inline_links(web_emoji_links: NativeAppSession) -> None:
    """Tests that emoji-led text lines are read, not dropped as blank, amid inline links."""

    session = web_emoji_links
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["🎧 Streaming links:"],
        [BrailleLine(1, "🎧 Streaming links:", "🎧 Streaming links:", "\x00" * 18)],
    )

    # The trailing newline rides along in braille but is filtered from speech.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["https://push.fm/link/htlecq2o", "link"],
        [
            BrailleLine(
                1,
                "https://push.fm/link/htlecq2o ",
                "https://push.fm/link/htlecq2o ",
                "\xc0" * 29 + "\x00",
            )
        ],
    )

    # The source has a "\n\n\n" run after the link, so two blank lines follow.
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert capture(session) == (["blank"], [BrailleLine(1, "", "", None)])

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    text = "🎵 Follow me on Spotify to get notified whenever I release something!"
    assert capture(session) == (
        [text + "\n"],
        [BrailleLine(1, text, "🎵 Follow me on Spotify to get no", "\x00" * len(text))],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["https://open.spotify.com/artist/0kXCd..", "link", "."],
        [
            BrailleLine(
                1,
                "https://open.spotify.com/artist/0kXCd.. .",
                "https://open.spotify.com/artist/",
                "\xc0" * 39 + "\x00\x00",
            )
        ],
    )
