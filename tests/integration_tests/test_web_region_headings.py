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

"""Tests headings that label their own aria-labelledby region, and a heading split by a link."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


# The heading and its edit link share a visual row but have different block
# ancestors, so they present as separate lines.
_TOP_TO_BOTTOM = (
    ["Cause", "heading 2"],
    ["[", "edit", "link", "]"],
    ["Cause text."],
    ["leaving region.", "Aftermath", "heading 2"],
    ["[", "edit", "link", "]"],
    ["Aftermath text."],
    ["leaving region.", "Before ", "middle", "link", " after", "heading 2"],
    ["Closing paragraph."],
)


@pytest.mark.native_app
def test_caret_navigation_through_heading_labelled_regions(
    web_region_headings: NativeAppSession,
) -> None:
    """Tests Down-arrow caret navigation through regions labelled by their own heading."""

    session = web_region_headings
    helpers.reset_web_state(session)

    for expected in _TOP_TO_BOTTOM:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.speech(session) == expected


@pytest.mark.native_app
def test_structural_navigation_by_heading_skips_region_chatter(
    web_region_headings: NativeAppSession,
) -> None:
    """Tests forward structural navigation by heading across the page, with wrap."""

    session = web_region_headings
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert helpers.speech(session) == ["h", "Cause", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert helpers.speech(session) == ["h", "Aftermath", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert helpers.speech(session) == [
        "h",
        "Before ",
        "middle",
        "link",
        " after",
        "heading 2",
    ]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert helpers.speech(session) == ["h", "Wrapping to top.", "Cause", "heading 2"]


@pytest.mark.native_app
def test_inline_link_heading_announces_level_once(web_region_headings: NativeAppSession) -> None:
    """Tests that a heading split into fragments by a mid-text link announces its level once."""

    session = web_region_headings
    helpers.reset_web_state(session)

    for _ in range(7):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == [
        "leaving region.",
        "Before ",
        "middle",
        "link",
        " after",
        "heading 2",
    ]


@pytest.mark.native_app
def test_say_all_heading_labelled_regions(web_region_headings: NativeAppSession) -> None:
    """Tests the utterances Say All speaks for a page of headings that label their own region."""

    session = web_region_headings
    helpers.reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert helpers.speech(session) == [
        "Intro paragraph.",
        "Cause",
        "heading 2",
        "edit",
        "link",
        "Cause text.",
        "leaving region.",
        "Aftermath",
        "heading 2",
        "edit",
        "link",
        "Aftermath text.",
        "leaving region.",
        "Before ",
        "heading 2",
        "middle",
        "link",
        " after",
        "heading 2",
        "Closing paragraph.",
    ]
