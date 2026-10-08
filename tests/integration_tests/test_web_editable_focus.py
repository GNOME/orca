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

"""Tests embedded links when an application moves focus into an editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


_LINE = ["2. Two pages: ", "first page", "link", " and ", "second page", "link", " end."]
_BRAILLE = "2. Two pages:  $l first page and  $l second page end. $l"


@pytest.mark.native_app
@pytest.mark.parametrize(
    "button_count, speech_prefix, braille_prefix",
    [
        (1, [], ""),
        (2, ["Message group"], ""),
        (3, ["Message"], "Message "),
        (4, ["Message group", "Message"], "Message "),
    ],
    ids=["unnamed", "named-group", "named-editor", "named-editor-in-named-group"],
)
def test_focus_editor_with_links(
    web_editable_focus: BrowserSession,
    button_count: int,
    speech_prefix: list[str],
    braille_prefix: str,
) -> None:
    """Tests editor entry and dialog return present names once and the complete line."""

    session = web_editable_focus
    helpers.reset_web_state(session)
    session.orca.set("BraillePresenter", "FlashMessagesAreEnabled", False)
    try:
        for _ in range(button_count):
            keyboard.tap_key(keyboard.KEYSYM_B)
            helpers.capture(session)
        keyboard.tap_key(keyboard.KEYSYM_RETURN)
        presentations = {"entry": helpers.capture(session, wait_async=True)}

        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
        helpers.capture(session)
        keyboard.tap_key(keyboard.KEYSYM_RETURN)
        presentations["re-entry"] = helpers.capture(session, wait_async=True)

        keyboard.tap_key(keyboard.KEYSYM_F2)
        assert helpers.speech(session, wait_async=True) == [
            "Editor dialog",
            "dialog",
            "Close",
            "button",
            "Browse mode",
        ]
        keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
        presentations["dialog return"] = helpers.capture(session, wait_async=True)

        for action, (spoken, braille) in presentations.items():
            assert spoken == [*speech_prefix, *_LINE, "Focus mode"], action
            assert braille[-1].full == braille_prefix + _BRAILLE, action
    finally:
        session.orca.set("BraillePresenter", "FlashMessagesAreEnabled", True)


@pytest.mark.native_app
def test_dialog_return_to_editor_starting_with_link(web_editable_focus: BrowserSession) -> None:
    """Tests editor context precedes the line and is not repeated between links."""

    session = web_editable_focus
    helpers.reset_web_state(session)
    session.orca.set("BraillePresenter", "FlashMessagesAreEnabled", False)
    try:
        for _ in range(5):
            keyboard.tap_key(keyboard.KEYSYM_B)
            helpers.capture(session)
        keyboard.tap_key(keyboard.KEYSYM_RETURN)
        helpers.capture(session, wait_async=True)
        keyboard.tap_key(keyboard.KEYSYM_F2)
        assert helpers.speech(session, wait_async=True) == [
            "Editor dialog",
            "dialog",
            "Close",
            "button",
            "Browse mode",
        ]
        keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
        spoken, braille = helpers.capture(session, wait_async=True)
        assert spoken == [
            "Message group",
            "Message",
            *_LINE[1:],
            "Focus mode",
        ]
        assert braille[-1].full == "Message first page and  $l second page end. $l"
    finally:
        session.orca.set("BraillePresenter", "FlashMessagesAreEnabled", True)
