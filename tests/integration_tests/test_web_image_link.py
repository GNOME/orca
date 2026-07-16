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

"""Tests presentation and navigation of links that contain images."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

# Chromium names the alt-less image with a version-dependent "missing image
# descriptions" annotation, so these tests pin Orca's stable role labels and the
# braille link mask rather than that name.


@pytest.mark.native_app
def test_tab_presents_image_only_link_as_a_link(web_image_link: NativeAppSession) -> None:
    """Tests that Tab reaches the image-only link and presents it as a link."""

    session = web_image_link
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session) == (
        ["Home page", "link"],
        [BrailleLine(1, "Home page", "Home page", "\xc0" * 9)],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    speech, braille = capture(session)
    assert speech[-1] == "link"
    assert set(braille[0].mask) == {"\xc0"}


@pytest.mark.native_app
def test_next_image_reaches_the_alt_less_image(web_image_link: NativeAppSession) -> None:
    """Tests that G (next image) reaches the alt-less image, so it is not filtered as useless."""

    session = web_image_link
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_G)
    speech, _braille = capture(session)
    assert speech[0] == "g"
    assert speech[-1] == "Unlabeled image"


@pytest.mark.native_app
def test_small_standalone_image_is_filtered_from_content(
    web_image_link: NativeAppSession,
) -> None:
    """Tests that a tiny unlabeled image is dropped from content but a larger one is presented."""

    session = web_image_link
    move_to_top(session)

    # _is_useless_image filters the tiny image (under the 25px threshold) out of
    # presented content, so Down navigation never lands on it; the larger image is
    # presented as its own line.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Intro paragraph."],
        [BrailleLine(1, "Intro paragraph.", "Intro paragraph.", "\x00" * 16)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Home page", "link"],
        [BrailleLine(1, "Home page", "Home page", "\xc0" * 9)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    speech, braille = capture(session)
    assert speech[-1] == "Unlabeled image"
    assert set(braille[0].mask) == {"\x00"}

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Unlabeled image"],
        [BrailleLine(1, "Unlabeled image", "Unlabeled image", "\x00" * 15)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Closing paragraph."],
        [BrailleLine(1, "Closing paragraph.", "Closing paragraph.", "\x00" * 18)],
    )


@pytest.mark.native_app
def test_named_icon_link_speaks_its_name(web_image_link: NativeAppSession) -> None:
    """Tests a link wrapping a named icon section speaks its name in browse mode, not bare."""

    session = web_image_link
    move_to_top(session)
    captured = None
    for _ in range(6):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        captured = capture(session)

    assert captured == (
        ["Your shopping cart contains 0 items", "link"],
        [
            BrailleLine(
                1,
                "Your shopping cart contains 0 items",
                "Your shopping cart contains 0 it",
                "\xc0" * 35,
            )
        ],
    )


@pytest.mark.native_app
def test_say_all_skips_the_useless_image(web_image_link: NativeAppSession) -> None:
    """Tests that Say All reads the navigable images but skips the useless small one."""

    move_to_top(web_image_link)
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    spoken = speech(web_image_link)
    # The link image and the large standalone image each read as "Unlabeled image";
    # the small useless image is filtered out, so there are two, not three.
    assert spoken.count("Unlabeled image") == 2
    assert "Intro paragraph." in spoken
    assert "Closing paragraph." in spoken
