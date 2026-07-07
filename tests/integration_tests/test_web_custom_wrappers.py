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

"""Tests line assembly for custom-element wrappers sharing a visual row."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_line_assembly_custom_element_wrappers(web_custom_wrappers: NativeAppSession) -> None:
    """Tests that widgets nested in custom-element wrappers on one row share one line."""

    session = web_custom_wrappers
    move_to_top(session)

    # A block-level link and an inline verified badge, each buried under [OBJ]-only
    # custom-element wrappers (yt-formatted-string, badge-shape), share one line; the
    # braille mask marks Ahrix as the link.
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["Ahrix", "Verified", "image"],
        [
            BrailleLine(
                cursor_cell=1,
                full="Ahrix Verified image",
                visible="Ahrix Verified image",
                mask="\xc0\xc0\xc0\xc0\xc0" + "\x00" * 15,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["213 thousand subscribers"],
        [
            BrailleLine(
                cursor_cell=1,
                full="213 thousand subscribers",
                visible="213 thousand subscribers",
                mask="\x00" * 24,
            )
        ],
    )

    # The like/dislike toggle buttons (nested two wrappers deep in a segmented
    # view-model) and the share/save/more buttons all group onto one line.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    speech, braille = capture(session)
    assert speech == [
        "like this video along with 407,992 other people",
        "toggle button not pressed",
        "Dislike this video",
        "toggle button not pressed",
        "Share",
        "button",
        "Save to playlist",
        "button",
        "More actions",
        "button",
    ]
    assert braille[0].full == (
        "& y like this video along with 407,992 other people toggle button "
        "& y Dislike this video toggle button Share button Save to playlist "
        "button More actions button"
    )
