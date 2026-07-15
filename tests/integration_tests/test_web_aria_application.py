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

"""Tests navigation into and out of an ARIA application and the document nested inside it."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _in_focus_mode(session: NativeAppSession) -> bool:
    return bool(session.orca.get("DocumentPresenter", "InFocusMode"))


def _reload(session: NativeAppSession) -> None:
    """Reloads the page to give each test the same starting state."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_R)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()
    reset_web_state(session)


@pytest.mark.native_app
def test_heading_navigation_enters_the_applications(
    web_aria_application: NativeAppSession,
) -> None:
    """Tests that next-heading reaches the headings inside the applications and the document."""

    session = web_aria_application
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Application heading", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Document heading", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Main heading two", "heading 1"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Focusable application heading", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Main heading three", "heading 1"]


@pytest.mark.native_app
def test_caret_navigation_skips_over_the_applications(
    web_aria_application: NativeAppSession,
) -> None:
    """Tests that line navigation presents each application as a single embedded object."""

    session = web_aria_application
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph before the application."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Embedded application", "embedded"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Main heading two", "heading 1"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph after the application."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Focusable application", "embedded"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Main heading three", "heading 1"]


@pytest.mark.native_app
def test_caret_navigation_inside_the_application(
    web_aria_application: NativeAppSession,
) -> None:
    """Tests line navigation from a heading structural navigation landed on in the application."""

    session = web_aria_application
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Application heading", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph inside the application."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Application button", "button"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Application link", "link"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Application entry", "entry"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Document heading", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph inside the document."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Main heading two", "heading 1"]


@pytest.mark.native_app
def test_tab_to_widget_in_application_switches_to_focus_mode(
    web_aria_application: NativeAppSession,
) -> None:
    """Tests the presentation mode as focus moves to the widgets inside the application."""

    session = web_aria_application
    _reload(session)
    assert not _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application button", "button", "Focus mode"]
    assert _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application link", "link"]
    assert _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application entry", "entry"]
    assert _in_focus_mode(session)


@pytest.mark.native_app
def test_tab_to_focusable_application_switches_to_focus_mode(
    web_aria_application: NativeAppSession,
) -> None:
    """Tests that the focusable application itself is treated as a focus mode widget."""

    session = web_aria_application
    _reload(session)
    assert not _in_focus_mode(session)

    # Shift+Tab from the top of the document wraps to the last focusable element.
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    assert speech(session) == ["Focusable application", "embedded", "Focus mode"]
    assert _in_focus_mode(session)

    # The author of an application is responsible for handling the arrow keys.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == []
    assert _in_focus_mode(session)


@pytest.mark.native_app
def test_tab_to_widget_in_application_from_the_application_switches_to_focus_mode(
    web_aria_application: NativeAppSession,
) -> None:
    """Tests the presentation mode when Tab follows line navigation onto the application."""

    session = web_aria_application
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph before the application."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Embedded application", "embedded"]
    assert not _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application button", "button", "Focus mode"]
    assert _in_focus_mode(session)


@pytest.mark.native_app
def test_structural_navigation_by_widget(web_aria_application: NativeAppSession) -> None:
    """Tests that next-button and next-entry reach the widgets inside the application."""

    session = web_aria_application
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == ["b", "Application button", "button"]
    assert not _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert speech(session) == ["e", "Application entry", "entry"]
    assert not _in_focus_mode(session)


@pytest.mark.native_app
def test_structural_navigation_to_widget_can_trigger_focus_mode(
    web_aria_application: NativeAppSession,
) -> None:
    """Tests next-button to a widget in the application when the setting enables focus mode."""

    session = web_aria_application
    _reload(session)
    session.orca.set("StructuralNavigator", "TriggersFocusMode", True)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == ["b", "Focus mode", "Application button", "button"]
    assert _in_focus_mode(session)


@pytest.mark.native_app
def test_tab_from_inside_the_application_switches_to_focus_mode(
    web_aria_application: NativeAppSession,
) -> None:
    """Tests that Tab from content in the application switches to focus mode."""

    session = web_aria_application
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Application heading", "heading 2"]
    assert not _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application button", "button", "Focus mode"]
    assert _in_focus_mode(session)


@pytest.mark.native_app
def test_browse_mode_the_user_turned_on_in_the_application_is_preserved(
    web_aria_application: NativeAppSession,
) -> None:
    """Tests that moving focus in the application does not undo the mode the user chose."""

    session = web_aria_application
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application button", "button", "Focus mode"]
    assert _in_focus_mode(session)

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    assert speech(session) == ["Browse mode"]
    assert not _in_focus_mode(session)

    # The link is not a focus mode widget, so only the application would put us in focus mode.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application link", "link"]
    assert not _in_focus_mode(session)

    # The role of the entry still decides, as it does everywhere else.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application entry", "entry", "Focus mode"]
    assert _in_focus_mode(session)
