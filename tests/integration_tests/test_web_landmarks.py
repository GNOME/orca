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

"""Tests landmark navigation: structural (all ARIA types, fwd/back/wrap), caret, flat review."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import (
    BrailleLine,
    capture,
    move_to_bottom,
    move_to_top,
    reset_web_state,
    speech,
    toggle_flat_review,
)

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_TOP_TO_BOTTOM = (
    ["leaving banner.", "navigation", "Primary", "Home", "link"],
    ["leaving navigation.", "navigation", "Secondary", "Help", "link"],
    ["leaving navigation.", "search", "Search "],
    ["Search", "entry"],
    ["leaving search.", "main content", "Main content", "heading 1"],
    ["Body paragraph."],
    ["leaving main content.", "complementary content", "Sidebar", "Aside text."],
    ["leaving complementary content.", "form", "Newsletter signup", "Email "],
    ["Email", "entry"],
    ["leaving form.", "Related links", "landmark", "Region text."],
    ["leaving region.", "Status updates", "landmark", "Status text."],
    ["leaving region.", "information", "Footer text."],
)


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom(web_landmarks: NativeAppSession) -> None:
    """Tests Down-arrow caret navigation top to bottom (layout mode on)."""

    session = web_landmarks
    reset_web_state(session)

    for expected in _TOP_TO_BOTTOM:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_top_to_bottom_layout_off(web_landmarks: NativeAppSession) -> None:
    """Tests the same Down-arrow navigation with layout mode disabled."""

    session = web_landmarks
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    for expected in _TOP_TO_BOTTOM:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert speech(session) == expected


_BOTTOM_TO_TOP = (
    ["leaving information.", "Status updates", "landmark", "Status text."],
    ["leaving region.", "Related links", "landmark", "Region text."],
    ["leaving region.", "form", "Newsletter signup", "Email", "entry"],
    ["leaving form.", "complementary content", "Sidebar", "Aside text."],
    ["leaving complementary content.", "main content", "Body paragraph."],
    ["Main content", "heading 1"],
    ["leaving main content.", "search", "Search", "entry"],
    ["leaving search.", "navigation", "Secondary", "Help", "link"],
    ["leaving navigation.", "navigation", "Primary", "Home", "link"],
    ["leaving navigation.", "banner", "Site banner text."],
)
# Layout off splits each entry's label onto its own line, so two extra stops appear.
_BOTTOM_TO_TOP_LAYOUT_OFF = (
    ["leaving information.", "Status updates", "landmark", "Status text."],
    ["leaving region.", "Related links", "landmark", "Region text."],
    ["leaving region.", "form", "Newsletter signup", "Email", "entry"],
    ["Email "],
    ["leaving form.", "complementary content", "Sidebar", "Aside text."],
    ["leaving complementary content.", "main content", "Body paragraph."],
    ["Main content", "heading 1"],
    ["leaving main content.", "search", "Search", "entry"],
    ["Search "],
    ["leaving search.", "navigation", "Secondary", "Help", "link"],
    ["leaving navigation.", "navigation", "Primary", "Home", "link"],
    ["leaving navigation.", "banner", "Site banner text."],
)


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top(web_landmarks: NativeAppSession) -> None:
    """Tests Up-arrow caret navigation from the bottom (layout mode on)."""

    session = web_landmarks
    reset_web_state(session)
    move_to_bottom(session)

    for expected in _BOTTOM_TO_TOP:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_caret_navigation_bottom_to_top_layout_off(web_landmarks: NativeAppSession) -> None:
    """Tests the same Up-arrow navigation with layout mode disabled."""

    session = web_landmarks
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", False)
    move_to_bottom(session)
    for expected in _BOTTOM_TO_TOP_LAYOUT_OFF:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert speech(session) == expected


@pytest.mark.native_app
def test_flat_review_by_line_and_character(web_landmarks: NativeAppSession) -> None:
    """Tests flat review by line and character over the rendered web page."""

    session = web_landmarks
    move_to_top(session)
    toggle_flat_review(session)
    try:
        keyboard.tap_key(keyboard.KEYSYM_KP_UP)
        assert capture(session) == (
            ["Site banner text."],
            [BrailleLine(1, "Site banner text. $l", "Site banner text. $l", "\x00" * 20)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_DOWN)
        assert capture(session) == (
            ["S"],
            [BrailleLine(1, "Site banner text. $l", "Site banner text. $l", "\x00" * 20)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_DOWN)
        assert capture(session) == (
            ["i"],
            [BrailleLine(2, "Site banner text. $l", "Site banner text. $l", "\x00" * 20)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
        assert capture(session) == (
            ["Primary Home"],
            [BrailleLine(1, "Primary Home $l", "Primary Home $l", "\x00" * 15)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
        assert capture(session) == (
            ["Secondary Help"],
            [BrailleLine(1, "Secondary Help $l", "Secondary Help $l", "\x00" * 17)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
        assert capture(session) == (
            ["Search"],
            [BrailleLine(1, "Search $l", "Search $l", "\x00" * 9)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_HOME)
        assert capture(session) == (
            ["Secondary Help"],
            [BrailleLine(1, "Secondary Help $l", "Secondary Help $l", "\x00" * 17)],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_HOME)
        assert capture(session) == (
            ["Primary Home"],
            [BrailleLine(1, "Primary Home $l", "Primary Home $l", "\x00" * 15)],
        )
    finally:
        toggle_flat_review(session)


@pytest.mark.native_app
def test_structural_navigation_by_landmark_forward(web_landmarks: NativeAppSession) -> None:
    """Tests forward structural navigation across every landmark type, with wrap."""

    session = web_landmarks
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "leaving banner.", "navigation", "Primary", "Home", "link"],
        [BrailleLine(0, "Home", "Home", "\xc0" * 4)],
    )

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "leaving navigation.", "navigation", "Secondary", "Help", "link"],
        [BrailleLine(0, "Help", "Help", "\xc0" * 4)],
    )

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "leaving navigation.", "search", "Search "],
        [BrailleLine(0, "Search", "Search", "\x00" * 7)],
    )

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "leaving search.", "main content", "Main content", "heading 1"],
        [BrailleLine(0, "Main content h1", "Main content h1", "\x00" * 15)],
    )

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "leaving main content.", "complementary content", "Sidebar", "Aside text."],
        [BrailleLine(0, "Aside text.", "Aside text.", "\x00" * 11)],
    )

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "leaving complementary content.", "form", "Newsletter signup", "Email "],
        [BrailleLine(0, "Email", "Email", "\x00" * 6)],
    )

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "leaving form.", "Related links", "landmark", "Region text."],
        [BrailleLine(0, "Region text.", "Region text.", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "leaving region.", "Status updates", "landmark", "Status text."],
        [BrailleLine(0, "Status text.", "Status text.", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "leaving region.", "information", "Footer text."],
        [BrailleLine(0, "Footer text.", "Footer text.", "\x00" * 12)],
    )

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "Wrapping to top.", "leaving information.", "banner", "Site banner text."],
        [
            BrailleLine(0, "Wrapping to top.", "Wrapping to top.", "\x00" * 16),
            BrailleLine(0, "Site banner text.", "Site banner text.", "\x00" * 17),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_M)
    assert capture(session) == (
        ["m", "leaving banner.", "navigation", "Primary", "Home", "link"],
        [BrailleLine(0, "Home", "Home", "\xc0" * 4)],
    )


@pytest.mark.native_app
def test_structural_navigation_by_landmark_backward(web_landmarks: NativeAppSession) -> None:
    """Tests backward structural navigation across every landmark type, with wrap."""

    session = web_landmarks
    move_to_top(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "Wrapping to bottom.", "leaving banner.", "information", "Footer text."],
        [
            BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            BrailleLine(0, "Footer text.", "Footer text.", "\x00" * 12),
        ],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "leaving information.", "Status updates", "landmark", "Status text."],
        [BrailleLine(0, "Status text.", "Status text.", "\x00" * 12)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "leaving region.", "Related links", "landmark", "Region text."],
        [BrailleLine(0, "Region text.", "Region text.", "\x00" * 12)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "leaving region.", "form", "Newsletter signup", "Email "],
        [BrailleLine(0, "Email", "Email", "\x00" * 6)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "leaving form.", "complementary content", "Sidebar", "Aside text."],
        [BrailleLine(0, "Aside text.", "Aside text.", "\x00" * 11)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "leaving complementary content.", "main content", "Main content", "heading 1"],
        [BrailleLine(0, "Main content h1", "Main content h1", "\x00" * 15)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "leaving main content.", "search", "Search "],
        [BrailleLine(0, "Search", "Search", "\x00" * 7)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "leaving search.", "navigation", "Secondary", "Help", "link"],
        [BrailleLine(0, "Help", "Help", "\xc0" * 4)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "leaving navigation.", "navigation", "Primary", "Home", "link"],
        [BrailleLine(0, "Home", "Home", "\xc0" * 4)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "leaving navigation.", "banner", "Site banner text."],
        [BrailleLine(0, "Site banner text.", "Site banner text.", "\x00" * 17)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
    assert capture(session) == (
        ["M", "Wrapping to bottom.", "leaving banner.", "information", "Footer text."],
        [
            BrailleLine(0, "Wrapping to bottom.", "Wrapping to bottom.", "\x00" * 19),
            BrailleLine(0, "Footer text.", "Footer text.", "\x00" * 12),
        ],
    )


@pytest.mark.native_app
def test_no_wrapping_when_disabled(web_landmarks: NativeAppSession) -> None:
    """Tests that a boundary message replaces the wrap when navigation wrapping is off."""

    session = web_landmarks
    session.orca.set("StructuralNavigator", "NavigationWraps", False)
    try:
        move_to_top(session)
        for _ in range(9):
            keyboard.tap_key(keyboard.KEYSYM_M)
            speech(session)
        keyboard.tap_key(keyboard.KEYSYM_M)
        assert speech(session) == ["m", "No more landmarks."]

        move_to_top(session)
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_M)
        assert speech(session) == ["M", "No more landmarks."]
    finally:
        session.orca.set("StructuralNavigator", "NavigationWraps", True)
