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

"""Tests line navigation through a heading and a link which span several lines."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_bottom, move_to_top, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import WebSession

_PLAIN = "\x00"
_LINK = "\xc0"


@pytest.mark.web
def test_line_navigation_through_a_multi_line_heading(
    web_multi_line_content: WebSession,
) -> None:
    """Tests line navigation through a multi-line heading."""

    session = web_multi_line_content
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["foo\n", "heading 1"],
        [BrailleLine(1, "foo h1", "foo h1", _PLAIN * 6)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["bar\n", "heading 1"],
        [BrailleLine(1, "bar h1", "bar h1", _PLAIN * 6)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["baz", "heading 1"],
        [BrailleLine(1, "baz h1", "baz h1", _PLAIN * 6)],
    )


@pytest.mark.web
def test_line_navigation_through_a_multi_line_link(
    web_multi_line_content: WebSession,
) -> None:
    """Tests line navigation through a multi-line link."""

    session = web_multi_line_content
    move_to_top(session)
    for _ in range(4):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["one\n", "link"],
        [BrailleLine(1, "one two three", "one two three", _LINK * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["two\n", "link"],
        [BrailleLine(1, "one two three", "one two three", _LINK * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["three", "link"],
        [BrailleLine(1, "one two three", "one two three", _LINK * 13)],
    )


@pytest.mark.web
def test_say_all_over_a_multi_line_heading_and_link(
    web_multi_line_content: WebSession,
) -> None:
    """Tests Say All over a multi-line heading and link."""

    session = web_multi_line_content
    reset_web_state(session)
    move_to_bottom(session)
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(session) == [
        "Before.",
        "foo\nbar\nbaz",
        "heading 1",
        "Between.",
        "one\ntwo\nthree",
        "link",
        "alpha\nbeta\ngamma",
        "link",
        "heading 1",
        "delta\nepsilon\nzeta",
        "heading 1",
        "link",
        "After.",
    ]


@pytest.mark.web
def test_upward_line_navigation_through_a_multi_line_link(
    web_multi_line_content: WebSession,
) -> None:
    """Tests upward line navigation through a multi-line link."""

    session = web_multi_line_content
    move_to_top(session)
    for _ in range(8):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(session)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["three", "link"],
        [BrailleLine(1, "one two three", "one two three", _LINK * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["two\n", "link"],
        [BrailleLine(1, "one two three", "one two three", _LINK * 13)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["one\n", "link"],
        [BrailleLine(1, "one two three", "one two three", _LINK * 13)],
    )


@pytest.mark.web
def test_upward_line_navigation_through_a_multi_line_heading(
    web_multi_line_content: WebSession,
) -> None:
    """Tests upward line navigation through a multi-line heading."""

    session = web_multi_line_content
    move_to_top(session)
    for _ in range(4):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(session)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["baz", "heading 1"],
        [BrailleLine(1, "baz h1", "baz h1", _PLAIN * 6)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["bar\n", "heading 1"],
        [BrailleLine(1, "bar h1", "bar h1", _PLAIN * 6)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["foo\n", "heading 1"],
        [BrailleLine(1, "foo h1", "foo h1", _PLAIN * 6)],
    )


@pytest.mark.web
def test_line_navigation_through_a_multi_line_link_in_a_heading(
    web_multi_line_content: WebSession,
) -> None:
    """Tests line navigation through a multi-line link in a heading."""

    session = web_multi_line_content
    move_to_top(session)
    for _ in range(7):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["alpha\n", "link heading 1"],
        [BrailleLine(1, "alpha beta gamma h1", "alpha beta gamma h1", _LINK * 16 + _PLAIN * 3)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["beta\n", "link heading 1"],
        [BrailleLine(1, "alpha beta gamma h1", "alpha beta gamma h1", _LINK * 16 + _PLAIN * 3)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["gamma", "link heading 1"],
        [BrailleLine(1, "alpha beta gamma h1", "alpha beta gamma h1", _LINK * 16 + _PLAIN * 3)],
    )


@pytest.mark.web
def test_line_navigation_through_a_multi_line_heading_in_a_link(
    web_multi_line_content: WebSession,
) -> None:
    """Tests line navigation through a multi-line heading in a link."""

    session = web_multi_line_content
    move_to_top(session)
    for _ in range(10):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["delta\n", "heading 1 link"],
        [BrailleLine(1, "delta h1", "delta h1", _LINK * 5 + _PLAIN * 3)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["epsilon\n", "heading 1 link"],
        [BrailleLine(1, "epsilon h1", "epsilon h1", _LINK * 7 + _PLAIN * 3)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["zeta", "heading 1 link"],
        [BrailleLine(1, "zeta h1", "zeta h1", _LINK * 4 + _PLAIN * 3)],
    )


@pytest.mark.web
def test_upward_line_navigation_through_a_multi_line_link_in_a_heading(
    web_multi_line_content: WebSession,
) -> None:
    """Tests upward line navigation through a multi-line link in a heading."""

    session = web_multi_line_content
    move_to_top(session)
    for _ in range(11):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        capture(session)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["gamma", "link heading 1"],
        [BrailleLine(1, "alpha beta gamma h1", "alpha beta gamma h1", _LINK * 16 + _PLAIN * 3)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["beta\n", "link heading 1"],
        [BrailleLine(1, "alpha beta gamma h1", "alpha beta gamma h1", _LINK * 16 + _PLAIN * 3)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["alpha\n", "link heading 1"],
        [BrailleLine(1, "alpha beta gamma h1", "alpha beta gamma h1", _LINK * 16 + _PLAIN * 3)],
    )


@pytest.mark.web
def test_upward_line_navigation_through_a_multi_line_heading_in_a_link(
    web_multi_line_content: WebSession,
) -> None:
    """Tests upward line navigation through a multi-line heading in a link."""

    session = web_multi_line_content
    move_to_bottom(session)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["zeta", "heading 1 link"],
        [BrailleLine(1, "zeta h1", "zeta h1", _LINK * 4 + _PLAIN * 3)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["epsilon\n", "heading 1 link"],
        [BrailleLine(1, "epsilon h1", "epsilon h1", _LINK * 7 + _PLAIN * 3)],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["delta\n", "heading 1 link"],
        [BrailleLine(1, "delta h1", "delta h1", _LINK * 5 + _PLAIN * 3)],
    )
