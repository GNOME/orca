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
from .helpers import BrailleLine, capture, move_to_top, reset_web_state, speech

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
        ["small link", "link", " sits mid paragraph "],
        ["before india juliet kilo lima "],
        ["mike november oscar papa "],
        ["quebec."],
        ["Plain words then bold here"],
        [" then slanted there then a bit "],
        ["of ", "inline code", " and water is "],
        ["H", "subscript", "two", "O and x", "superscript", "squared", " plus more "],
        ["trailing words that wrap "],
        ["onward."],
        ["List with 2 items", "• First list item that is "],
        ["long enough to wrap "],
        ["across two lines here."],
        ["• Second shorter item."],
        ["leaving list.", "block quote", "Quoted passage that "],
        ["also runs long enough "],
        ["to wrap onto a second "],
        ["visual line within "],
        ["the block."],
        ["leaving blockquote. code start", "code line one"],
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
            ["Plain words then bold here"],
            [" then slanted there then a bit "],
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
        [" then slanted there then a bit "],
        ["Plain words then bold here"],
        ["quebec."],
        ["mike november oscar papa "],
        ["before india juliet kilo lima "],
        ["small link", "link", " sits mid paragraph "],
        ["foxtrot golf hotel, then a "],
        ["Alpha bravo charlie delta echo "],
    ]


def _down_to_line(session: NativeAppSession, count: int) -> tuple[list[str], list[BrailleLine]]:
    result = None
    for _ in range(count):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        result = capture(session)
    assert result is not None
    return result


@pytest.mark.native_app
def test_eol_indicator_on_code_blocks_not_inline(web_wrapping_text: NativeAppSession) -> None:
    """Tests that the braille EOL indicator marks preformatted code lines but not inline code."""

    session = web_wrapping_text
    reset_web_state(session)
    assert session.orca.get("CaretNavigator", "LayoutMode") is True

    assert _down_to_line(session, 10) == (
        ["of ", "inline code", " and water is "],
        [
            BrailleLine(
                1, "of inline code and water is ", "of inline code and water is ", "\x00" * 28
            )
        ],
    )

    assert _down_to_line(session, 13) == (
        ["leaving blockquote. code start", "code line one"],
        [BrailleLine(1, "code line one $l", "code line one $l", "\x00" * 16)],
    )

    assert _down_to_line(session, 1) == (
        ["code line two", "code end"],
        [BrailleLine(1, "code line two $l", "code line two $l", "\x00" * 16)],
    )

    # A pre whose line ends in a link: the code block's $l belongs at the end of the
    # line, never mid-line after one of its fragments.
    assert _down_to_line(session, 4) == (
        ["code start", "see ", "the docs", "link"],
        [BrailleLine(1, "see the docs", "see the docs", "\x00" * 4 + "\xc0" * 8)],
    )
    assert _down_to_line(session, 1) == (
        ["code start", "see ", "the docs", "link"],
        [
            BrailleLine(
                1,
                "see the docs $l",
                "see the docs $l",
                "\x00" * 4 + "\xc0" * 8 + "\x00" * 3,
            )
        ],
    )
    assert _down_to_line(session, 1) == (
        ["plain last line", "code end"],
        [BrailleLine(1, "plain last line $l", "plain last line $l", "\x00" * 18)],
    )

    # A pre line whose last item is an inline child element still ends with the $l.
    assert _down_to_line(session, 4) == (
        ["code start", "mix ", "tail"],
        [BrailleLine(1, "mix tail $l", "mix tail $l", "\x00" * 11)],
    )
    assert _down_to_line(session, 1) == (
        ["code start", "mix ", "tail"],
        [BrailleLine(1, "mix tail $l", "mix tail $l", "\x00" * 11)],
    )
    assert _down_to_line(session, 1) == (
        ["plain end", "code end"],
        [BrailleLine(1, "plain end $l", "plain end $l", "\x00" * 12)],
    )


@pytest.mark.native_app
def test_fill_in_the_blank_line_assembly(web_wrapping_text: NativeAppSession) -> None:
    """Tests that an empty inline entry with text on both sides presents as one line."""

    session = web_wrapping_text
    reset_web_state(session)
    assert session.orca.get("CaretNavigator", "LayoutMode") is True

    # The entry's $l marks the end of its (empty) text; the first paragraph wraps
    # after ' to ', so 'continue.' is its own visual line. The second paragraph fits
    # on a single visual line.
    assert _down_to_line(session, 31) == (
        ["Fill in ", "answer", "entry", " to "],
        [BrailleLine(1, "Fill in answer  $l to ", "Fill in answer  $l to ", "\x00" * 12)],
    )
    assert _down_to_line(session, 1) == (
        ["continue."],
        [BrailleLine(1, "continue.", "continue.", "\x00" * 9)],
    )
    assert _down_to_line(session, 1) == (
        ["Pick ", "choice", "entry", " now."],
        [BrailleLine(1, "Pick choice  $l now.", "Pick choice  $l now.", "\x00" * 10)],
    )
