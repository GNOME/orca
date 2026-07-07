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

"""Tests presentation of headings authors have styled or labeled in unusual ways."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_top, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


# Heading navigation lands on each h2 in turn. Headings with presentable text speak it;
# those with none (empty, aria-label-only) fall back to the accessible name. The two
# whose sole content is an empty focusable child (button, div) present that child instead
# of the name -- a separate content-object presentation path, out of scope here.
_HEADINGS = [
    ["2", "Heading one", "heading 2"],
    ["2", "Heading two", "heading 2"],
    ["2", "You can't see me!", "heading 2"],
    ["2", "Heading four", "heading 2"],
    ["2", "Heading five", "heading 2"],
    ["2", "I've got an empty paragraph", "heading 2"],
    ["2", "button heading 2"],
    ["2", "heading 2"],
    ["2", "Image only heading", "heading 2"],
    [
        "2",
        "This\n",
        "is\nwhy",
        "link",
        "\nwe\n",
        "can't",
        "button",
        "\nhave\nnice\nthings\n!\n!\n",
        "heading 2",
    ],
    ["2", "Home", "link heading 2"],
]


@pytest.mark.native_app
def test_heading_navigation_across_weird_headings(web_weird_headings: NativeAppSession) -> None:
    """Tests heading navigation presents each heading by its text or, if none, its name."""

    session = web_weird_headings
    reset_web_state(session)
    move_to_top(session)
    for expected in _HEADINGS:
        keyboard.tap_key(keyboard.KEYSYM_2)
        assert speech(session) == expected


@pytest.mark.native_app
def test_empty_aria_heading_is_a_single_caret_stop(web_weird_headings: NativeAppSession) -> None:
    """Tests that a text-less aria-labeled heading is one caret stop that speaks its name."""

    session = web_weird_headings
    reset_web_state(session)
    move_to_top(session)
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_2)
    assert speech(session) == ["2", "You can't see me!", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert speech(session) == ["O"]
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert speech(session) == ["You can't see me!"]
