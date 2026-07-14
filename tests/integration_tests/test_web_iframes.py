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

"""Tests navigation into and out of the content of an iframe."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_top, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_heading_navigation_enters_and_leaves_the_iframe(web_iframes: NativeAppSession) -> None:
    """Tests that next-heading treats the heading in the iframe as part of the document."""

    session = web_iframes
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Frame heading", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Main heading two", "heading 1"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Wrapping to top.", "Main heading one", "heading 1"]


@pytest.mark.native_app
def test_backward_heading_navigation_enters_and_leaves_the_iframe(
    web_iframes: NativeAppSession,
) -> None:
    """Tests that previous-heading treats the heading in the iframe as part of the document."""

    session = web_iframes
    move_to_top(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert speech(session) == ["H", "Wrapping to bottom.", "Main heading two", "heading 1"]

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert speech(session) == ["H", "Frame heading", "heading 2"]

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_H)
    assert speech(session) == ["H", "Main heading one", "heading 1"]


@pytest.mark.native_app
def test_caret_navigation_enters_and_leaves_the_iframe(web_iframes: NativeAppSession) -> None:
    """Tests that line navigation reads the content of the iframe in document order."""

    session = web_iframes
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph before the frame."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Frame heading", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph inside the frame."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Frame button", "button", "Frame entry", "entry"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Main heading two", "heading 1"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph after the frame."]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Main heading two", "heading 1"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Frame button", "button", "Frame entry", "entry"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Paragraph inside the frame."]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Frame heading", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Paragraph before the frame."]


@pytest.mark.native_app
def test_structural_navigation_by_widget(web_iframes: NativeAppSession) -> None:
    """Tests that next-button and next-entry reach the widgets inside the iframe."""

    session = web_iframes
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == ["b", "Frame button", "button"]

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert speech(session) == ["e", "Frame entry", "entry"]


@pytest.mark.native_app
def test_structural_navigation_focus_mode_setting_uses_the_role(
    web_iframes: NativeAppSession,
) -> None:
    """Tests that the role of the widget in the iframe decides the mode when the setting is on."""

    session = web_iframes
    reset_web_state(session)
    session.orca.set("StructuralNavigator", "TriggersFocusMode", True)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == ["b", "Frame button", "button"]
    assert not session.orca.get("DocumentPresenter", "InFocusMode")

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert speech(session) == ["e", "Focus mode", "Frame entry", "entry"]
    assert session.orca.get("DocumentPresenter", "InFocusMode")
