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

"""Tests heading structural navigation, including the per-level number commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _next(session: NativeAppSession, keysym: int) -> list[str]:
    keyboard.tap_key(keysym)
    return speech(session)


def _previous(session: NativeAppSession, keysym: int) -> list[str]:
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keysym)
    return speech(session)


@pytest.mark.native_app
def test_heading_navigation_announces_level(web_headings: NativeAppSession) -> None:
    """Tests that h moves through every heading in order, announcing each level, with wrap."""

    session = web_headings
    move_to_top(session)

    assert _next(session, keyboard.KEYSYM_H) == ["h", "Section One", "heading 2"]
    assert _next(session, keyboard.KEYSYM_H) == ["h", "Sub A", "heading 3"]
    assert _next(session, keyboard.KEYSYM_H) == ["h", "Section Two", "heading 2"]
    assert _next(session, keyboard.KEYSYM_H) == ["h", "Sub B", "heading 3"]
    assert _next(session, keyboard.KEYSYM_H) == ["h", "Appendix", "heading 1"]
    assert _next(session, keyboard.KEYSYM_H) == [
        "h",
        "Wrapping to top.",
        "Doc Title",
        "heading 1",
    ]


@pytest.mark.native_app
def test_navigation_by_heading_level(web_headings: NativeAppSession) -> None:
    """Tests that the number keys navigate only among headings of that level, with wrap."""

    session = web_headings

    move_to_top(session)
    assert _next(session, keyboard.KEYSYM_1) == ["1", "Appendix", "heading 1"]
    assert _next(session, keyboard.KEYSYM_1) == [
        "1",
        "Wrapping to top.",
        "Doc Title",
        "heading 1",
    ]

    move_to_top(session)
    assert _next(session, keyboard.KEYSYM_2) == ["2", "Section One", "heading 2"]
    assert _next(session, keyboard.KEYSYM_2) == ["2", "Section Two", "heading 2"]

    move_to_top(session)
    assert _next(session, keyboard.KEYSYM_3) == ["3", "Sub A", "heading 3"]
    assert _next(session, keyboard.KEYSYM_3) == ["3", "Sub B", "heading 3"]


@pytest.mark.native_app
def test_no_more_headings_at_absent_level(web_headings: NativeAppSession) -> None:
    """Tests the absence message when navigating to a heading level the page lacks."""

    session = web_headings
    move_to_top(session)

    assert _next(session, keyboard.KEYSYM_4) == ["4", "No more headings at level 4."]


@pytest.mark.native_app
def test_heading_level_backward_wraps(web_headings: NativeAppSession) -> None:
    """Tests that Shift plus a level number navigates backward, wrapping to the bottom."""

    session = web_headings
    move_to_top(session)

    assert _previous(session, keyboard.KEYSYM_1) == [
        "!",
        "Wrapping to bottom.",
        "Appendix",
        "heading 1",
    ]


@pytest.mark.native_app
def test_no_wrapping_when_disabled(web_headings: NativeAppSession) -> None:
    """Tests that a boundary message replaces the wrap when navigation wrapping is off."""

    session = web_headings
    session.orca.set("StructuralNavigator", "NavigationWraps", False)
    try:
        move_to_top(session)
        for expected in (
            ["h", "Section One", "heading 2"],
            ["h", "Sub A", "heading 3"],
            ["h", "Section Two", "heading 2"],
            ["h", "Sub B", "heading 3"],
            ["h", "Appendix", "heading 1"],
        ):
            assert _next(session, keyboard.KEYSYM_H) == expected
        assert _next(session, keyboard.KEYSYM_H) == ["h", "No more headings."]

        move_to_top(session)
        assert _previous(session, keyboard.KEYSYM_H) == ["H", "No more headings."]

        move_to_top(session)
        assert _next(session, keyboard.KEYSYM_1) == ["1", "Appendix", "heading 1"]
        assert _next(session, keyboard.KEYSYM_1) == ["1", "No more headings at level 1."]
    finally:
        session.orca.set("StructuralNavigator", "NavigationWraps", True)
