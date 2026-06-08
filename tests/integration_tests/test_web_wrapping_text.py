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

"""Characterizes how line contents are assembled while navigating rich web content.

The fixture pins the font so visual wrapping is deterministic. Layout mode (on by
default) pieces multiple objects onto each visual line; these tests are the safety
net for that logic. The layout-off counterpart shows the contrast: one object per
line.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_top, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _walk(session: NativeAppSession, count: int) -> list[list[str]]:
    lines = []
    for _ in range(count):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        lines.append(speech(session))
    return lines


@pytest.mark.native_app
def test_line_assembly_layout_mode_on(web_wrapping_text: NativeAppSession) -> None:
    """Tests visual-line assembly in layout mode (the default): inline runs group per line."""

    session = web_wrapping_text
    reset_web_state(session)
    assert session.orca.get("CaretNavigator", "LayoutMode") is True

    assert _walk(session, 27) == [
        ["leaving banner.", "main content", "Wrapping text", "heading 1"],
        ["Alpha bravo charlie delta echo "],
        ["foxtrot golf hotel, then a "],
        ["small link", " sits mid paragraph "],
        ["before india juliet kilo lima "],
        ["mike november oscar papa "],
        ["quebec."],
        ["Plain words then  bold here"],
        [" then  slanted there  then a bit "],
        ["of ", "inline code", " and water is "],
        ["H", "subscript", "two", "O and x", "superscript", "squared", " plus more "],
        ["trailing words that wrap "],
        ["onward."],
        ["List with 2 items", "•  First list item that is "],
        ["long enough to wrap "],
        ["across two lines here."],
        ["•  Second shorter item."],
        ["leaving list.", "block quote", "Quoted passage that "],
        ["also runs long enough "],
        ["to wrap onto a second "],
        ["visual line within "],
        ["the block."],
        ["leaving blockquote. code start", "code line one\n"],
        ["code line two", "code end"],
        ["Final paragraph after the "],
        ["preformatted block to confirm "],
        ["the separation."],
    ]


@pytest.mark.native_app
def test_line_assembly_layout_mode_off(web_wrapping_text: NativeAppSession) -> None:
    """Tests that with layout mode off each object is its own line; inline runs do not group."""

    session = web_wrapping_text
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    try:
        assert _walk(session, 20) == [
            ["leaving banner.", "main content", "Wrapping text", "heading 1"],
            ["Alpha bravo charlie delta echo "],
            ["foxtrot golf hotel, then a "],
            ["small link", "link"],
            [" sits mid paragraph "],
            ["before india juliet kilo lima "],
            ["mike november oscar papa "],
            ["quebec."],
            ["Plain words then  bold here"],
            [" then  slanted there  then a bit "],
            ["of "],
            ["inline code"],
            [" and water is "],
            ["H"],
            ["subscript", "two"],
            ["O and x"],
            ["superscript", "squared"],
            [" plus more "],
            ["trailing words that wrap "],
            ["onward."],
        ]
    finally:
        session.orca.set("CaretNavigator", "LayoutMode", True)


@pytest.mark.native_app
def test_line_assembly_walking_up(web_wrapping_text: NativeAppSession) -> None:
    """Tests that Up-arrow presents each wrapped visual line once, not in backward fragments."""

    session = web_wrapping_text
    reset_web_state(session)
    assert session.orca.get("CaretNavigator", "LayoutMode") is True

    move_to_top(session)
    _walk(session, 13)

    up_lines = []
    for _ in range(11):
        keyboard.tap_key(keyboard.KEYSYM_UP)
        up_lines.append(speech(session))

    assert up_lines == [
        ["trailing words that wrap "],
        ["H", "subscript", "two", "O and x", "superscript", "squared", " plus more "],
        ["of ", "inline code", " and water is "],
        [" then  slanted there  then a bit "],
        ["Plain words then  bold here"],
        ["quebec."],
        ["mike november oscar papa "],
        ["before india juliet kilo lima "],
        ["small link", " sits mid paragraph "],
        ["foxtrot golf hotel, then a "],
        ["Alpha bravo charlie delta echo "],
    ]
