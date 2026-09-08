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

"""Tests line navigation in and out of blockquotes followed by different kinds of content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import capture, move_to_top, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_LINES_DOWN = [
    (["block quote", "foo"], "foo block quote"),
    (["bar"], "bar block quote"),
    (["baz"], "baz block quote"),
    (["leaving blockquote.", "after"], "after"),
    (["block quote", "quoted before div"], "quoted before div block quote"),
    (["more quoted before div"], "more quoted before div block quote"),
    (["leaving blockquote.", "after div"], "after div"),
    (["block quote", "quoted before paragraph"], "quoted before paragraph block quote"),
    (["more quoted before paragraph"], "more quoted before paragraph block quote"),
    (["leaving blockquote.", "after paragraph"], "after paragraph"),
    (["block quote", "quoted before heading"], "quoted before heading block quote"),
    (["more quoted before heading"], "more quoted before heading block quote"),
    (["leaving blockquote.", "After heading", "heading 2"], "After heading h2"),
    (["block quote", "quoted before link"], "quoted before link block quote"),
    (["more quoted before link"], "more quoted before link block quote"),
    (["leaving blockquote.", "after link", "link"], "after link"),
    (["block quote", "quoted before blank line"], "quoted before blank line block quote"),
    (["more quoted before blank line"], "more quoted before blank line block quote"),
    (["leaving blockquote.", "blank"], ""),
    (["after blank line"], "after blank line"),
    (["block quote", "quoted before break"], "quoted before break block quote"),
    (["more quoted before break"], "more quoted before break block quote"),
    (["leaving blockquote.", "blank"], ""),
    (["after break"], "after break"),
]

_LINES_UP = [
    ["blank"],
    ["block quote", "more quoted before break"],
    ["quoted before break"],
    ["leaving blockquote.", "after blank line"],
    ["blank"],
    ["block quote", "more quoted before blank line"],
    ["quoted before blank line"],
    ["leaving blockquote.", "after link", "link"],
    ["block quote", "more quoted before link"],
    ["quoted before link"],
    ["leaving blockquote.", "After heading", "heading 2"],
    ["block quote", "more quoted before heading"],
    ["quoted before heading"],
    ["leaving blockquote.", "after paragraph"],
    ["block quote", "more quoted before paragraph"],
    ["quoted before paragraph"],
    ["leaving blockquote.", "after div"],
    ["block quote", "more quoted before div"],
    ["quoted before div"],
    ["leaving blockquote.", "after"],
    ["block quote", "baz"],
    ["bar"],
    ["foo"],
    ["leaving blockquote.", "before"],
]


@pytest.mark.native_app
def test_line_navigation_down(web_blockquote_line_breaks: NativeAppSession) -> None:
    """Tests line navigation down."""

    session = web_blockquote_line_breaks
    reset_web_state(session)
    move_to_top(session)

    for expected_speech, expected_line in _LINES_DOWN:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, brailled = capture(session)
        assert spoken == expected_speech
        assert [line.full for line in brailled] == [expected_line]


@pytest.mark.native_app
def test_line_navigation_up(web_blockquote_line_breaks: NativeAppSession) -> None:
    """Tests line navigation up."""

    session = web_blockquote_line_breaks
    reset_web_state(session)
    move_to_top(session)
    for _i in range(len(_LINES_DOWN)):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        speech(session)

    for expected_speech in _LINES_UP:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected_speech
