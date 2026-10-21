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

"""Tests focus entry and arrow navigation through replaced editor text."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .helpers import BrailleLine
    from .orca_fixtures import BrowserSession


def _reload(session: BrowserSession) -> tuple[list[str], list[BrailleLine]]:
    """Reloads with Orca running so the page's initial focus events are captured."""

    session.orca.set("BraillePresenter", "FlashMessagesAreEnabled", False)
    helpers.capture(session, wait_async=True)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_R)
    return helpers.capture(session, wait_async=True)


@pytest.mark.native_app
def test_editor_focused_on_load(web_contenteditable_replacement: BrowserSession) -> None:
    """Tests that the initial line announcement survives subsequent page events."""

    session = web_contenteditable_replacement
    spoken, _brailled = _reload(session)
    assert spoken == ["Line one."]


@pytest.mark.native_app
def test_replaced_lines_down_and_up(web_contenteditable_replacement: BrowserSession) -> None:
    """Tests that each arrow press announces only the replacement line, once."""

    session = web_contenteditable_replacement
    _reload(session)

    for key, line in (
        (keyboard.KEYSYM_DOWN, "Line two."),
        (keyboard.KEYSYM_DOWN, "Line three."),
        (keyboard.KEYSYM_UP, "Line two."),
        (keyboard.KEYSYM_UP, "Line one."),
    ):
        keyboard.tap_key(key)
        # Normal capture drops interrupted speech, which can hide duplicate announcements.
        assert session.reader.wait_for_speech("").text == line
        assert helpers.speech(session, wait_async=True) == []
