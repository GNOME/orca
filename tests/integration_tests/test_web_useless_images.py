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

"""Tests that useless images are never presented, regardless of position or container."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_EXPECTED_SAY_ALL_SENTENCE = [
    "First paragraph.",
    "Inline before ",
    " inline after.",
    "End of paragraph image. ",
    "Last paragraph of text.",
    "Read more ",
    "link",
    "Submit",
    "button",
]
_EXPECTED_SAY_ALL_LINE = [
    "First paragraph.",
    "Inline before ",
    " inline after.",
    "End of paragraph image. ",
    "Last paragraph of text.",
    "Read more ",
    "link",
    "Submit",
    "button",
]


@pytest.mark.native_app
def test_say_all_by_sentence_omits_useless_images(web_useless_images: NativeAppSession) -> None:
    """Tests that Say All by sentence omits useless images in every position."""

    session = web_useless_images
    reset_web_state(session)
    session.orca.set("SayAllPresenter", "Style", "sentence")

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(session) == _EXPECTED_SAY_ALL_SENTENCE


@pytest.mark.native_app
def test_say_all_by_line_omits_useless_images(web_useless_images: NativeAppSession) -> None:
    """Tests that Say All by line omits useless images in every position."""

    session = web_useless_images
    reset_web_state(session)
    session.orca.set("SayAllPresenter", "Style", "line")

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(session) == _EXPECTED_SAY_ALL_LINE


@pytest.mark.native_app
def test_line_navigation_omits_useless_images(web_useless_images: NativeAppSession) -> None:
    """Tests that browsing by line presents each line, and each container, without its image."""

    move_to_top(web_useless_images)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(web_useless_images) == (
        ["Inline before ", " inline after."],
        [
            BrailleLine(
                1, "Inline before  inline after.", "Inline before  inline after.", "\x00" * 28
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(web_useless_images) == (
        ["End of paragraph image. "],
        [BrailleLine(1, "End of paragraph image.", "End of paragraph image.", "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(web_useless_images) == (
        ["Last paragraph of text."],
        [BrailleLine(1, "Last paragraph of text.", "Last paragraph of text.", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(web_useless_images) == (
        ["Read more ", "link"],
        [BrailleLine(1, "Read more", "Read more", "\xc0" * 9)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(web_useless_images) == (
        ["Submit", "button"],
        [BrailleLine(1, "Submit button", "Submit button", "\x00" * 13)],
    )


@pytest.mark.native_app
def test_tab_navigation_omits_useless_images_in_containers(
    web_useless_images: NativeAppSession,
) -> None:
    """Tests that tabbing to the link and button presents neither container's useless image."""

    reset_web_state(web_useless_images)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(web_useless_images) == (
        ["Read more", "link"],
        [BrailleLine(1, "Read more", "Read more", "\xc0" * 9)],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(web_useless_images) == (
        ["Submit", "button"],
        [BrailleLine(1, "Submit button", "Submit button", "\x00" * 13)],
    )
