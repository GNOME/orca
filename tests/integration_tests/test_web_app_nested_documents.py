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

"""Tests the presentation mode for documents nested inside an ARIA application."""

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
    """Reloads the page so that each test starts with the same focus and caret location."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_R)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()
    reset_web_state(session)


@pytest.mark.native_app
def test_tab_to_widget_in_application_switches_to_focus_mode(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that Tab to the widget inside the application switches to focus mode."""

    session = web_app_nested_documents
    _reload(session)
    assert not _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application button", "button", "Focus mode"]
    assert _in_focus_mode(session)


@pytest.mark.native_app
def test_tab_to_frame_document_in_application_switches_to_browse_mode(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that the document of a frame inside the application is treated as content."""

    session = web_app_nested_documents
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application button", "button", "Focus mode"]
    assert _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["document web", "Browse mode"]
    assert not _in_focus_mode(session)


@pytest.mark.native_app
def test_tab_to_aria_document_in_application_switches_to_browse_mode(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that a focusable ARIA document inside the application is treated as content."""

    session = web_app_nested_documents
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Application button", "button", "Focus mode"]

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["document web", "Browse mode"]

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Embedded document", "document frame"]
    assert not _in_focus_mode(session)


@pytest.mark.native_app
def test_tab_to_widgets_in_the_aria_document_uses_the_role_to_decide(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that the widgets inside the ARIA document are treated as document content."""

    session = web_app_nested_documents
    _reload(session)

    for _i in range(3):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        speech(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Document button", "button"]
    assert not _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Document entry", "entry", "Focus mode"]
    assert _in_focus_mode(session)


@pytest.mark.native_app
def test_caret_navigation_skips_over_the_application(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that line navigation presents the application as a single embedded object."""

    session = web_app_nested_documents
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph before the application."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Embedded application", "embedded"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Main heading two", "heading 1"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph after the application."]


@pytest.mark.native_app
def test_structural_navigation_by_widget(web_app_nested_documents: NativeAppSession) -> None:
    """Tests that next-button and next-entry reach the widgets and preserve browse mode."""

    session = web_app_nested_documents
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == ["b", "Application button", "button"]
    assert not _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == [
        "b",
        "Embedded document",
        "document frame",
        "Document button",
        "button",
    ]
    assert not _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert speech(session) == ["e", "Document entry", "entry"]
    assert not _in_focus_mode(session)


@pytest.mark.native_app
def test_structural_navigation_to_application_widget_can_trigger_focus_mode(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests next-button to a widget in the application when the setting enables focus mode."""

    session = web_app_nested_documents
    _reload(session)
    session.orca.set("StructuralNavigator", "TriggersFocusMode", True)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == ["b", "Focus mode", "Application button", "button"]
    assert _in_focus_mode(session)


@pytest.mark.native_app
def test_structural_navigation_in_the_document_uses_the_role_to_decide(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that the widgets in the nested document decide the mode by role, not by the app."""

    session = web_app_nested_documents
    _reload(session)
    session.orca.set("StructuralNavigator", "TriggersFocusMode", True)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == ["b", "Focus mode", "Application button", "button"]

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    assert speech(session) == ["Browse mode"]

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == [
        "b",
        "Embedded document",
        "document frame",
        "Document button",
        "button",
    ]
    assert not _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_E)
    assert speech(session) == ["e", "Focus mode", "Document entry", "entry"]
    assert _in_focus_mode(session)


@pytest.mark.native_app
def test_caret_navigation_to_the_application_can_trigger_focus_mode(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests line navigation onto the application when the setting enables focus mode."""

    session = web_app_nested_documents
    _reload(session)
    session.orca.set("CaretNavigator", "TriggersFocusMode", True)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph before the application."]
    assert not _in_focus_mode(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Focus mode", "Embedded application", "embedded"]
    assert _in_focus_mode(session)


@pytest.mark.native_app
def test_structural_navigation_is_confined_to_the_nested_document(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that structural navigation inside the nested document stays within it."""

    session = web_app_nested_documents
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Frame heading", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == [
        "h",
        "Embedded document",
        "document frame",
        "Document heading",
        "heading 2",
    ]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Document subheading", "heading 3"]

    # Past the last heading, navigation wraps within the document instead of
    # escaping to "Main heading two" in the surrounding page.
    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Wrapping to top.", "Document heading", "heading 2"]

    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == ["b", "Application button", "button"]

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == [
        "b",
        "Embedded document",
        "document frame",
        "Document button",
        "button",
    ]

    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == ["b", "Second document button", "button"]

    # Past the last button, navigation wraps within the document instead of
    # escaping to "Application button" in the application body.
    keyboard.tap_key(keyboard.KEYSYM_B)
    assert speech(session) == ["b", "Wrapping to top.", "Document button", "button"]


@pytest.mark.native_app
def test_caret_navigation_reads_out_of_the_nested_document(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that caret navigation, unlike structural navigation, can leave the nested document."""

    session = web_app_nested_documents
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Frame heading", "heading 2"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == [
        "h",
        "Embedded document",
        "document frame",
        "Document heading",
        "heading 2",
    ]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Paragraph inside the document."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Document button", "button", "Document entry", "entry"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Document subheading", "heading 3"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["More text inside the document."]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Second document button", "button"]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["leaving document.", "Main heading two", "heading 1"]


@pytest.mark.native_app
def test_file_boundary_navigation_is_confined_to_the_nested_document(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that Ctrl+Home and Ctrl+End stay within the nested document."""

    session = web_app_nested_documents
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == [
        "h",
        "Embedded document",
        "document frame",
        "Document heading",
        "heading 2",
    ]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    assert speech(session) == ["Second document button", "button"]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert speech(session) == ["Document heading", "heading 2"]


@pytest.mark.native_app
def test_file_boundary_navigation_reaches_the_page_boundaries(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that Ctrl+Home and Ctrl+End reach the page when not inside a nested document."""

    session = web_app_nested_documents
    _reload(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    assert speech(session) == ["Paragraph after the application."]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert speech(session) == ["Main heading one", "heading 1"]


@pytest.mark.native_app
def test_embedded_document_announcements_can_be_disabled(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that disabling the setting silences the enter and leave announcements."""

    session = web_app_nested_documents
    _reload(session)
    session.orca.set("SpeechPresenter", "AnnounceDocument", False)

    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Frame heading", "heading 2"]

    # Entering the document no longer announces "Embedded document, document frame".
    keyboard.tap_key(keyboard.KEYSYM_H)
    assert speech(session) == ["h", "Document heading", "heading 2"]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    assert speech(session) == ["Second document button", "button"]

    # Leaving the document no longer says "leaving document".
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Main heading two", "heading 1"]


@pytest.mark.native_app
def test_say_all_is_confined_to_the_nested_document(
    web_app_nested_documents: NativeAppSession,
) -> None:
    """Tests that Say All started inside the nested document stops at its boundary."""

    session = web_app_nested_documents
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    keyboard.tap_key(keyboard.KEYSYM_H)
    speech(session)

    # Say All reads to the end of the document and stops instead of spilling into the page.
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(session) == [
        "Document heading",
        "Paragraph inside the document.",
        "Document button",
        "button",
        "Document subheading",
        "heading 3",
        "More text inside the document.",
        "Second document button",
        "button",
    ]
