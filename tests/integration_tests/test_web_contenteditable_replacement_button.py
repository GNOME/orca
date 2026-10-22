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

"""Tests tabbing into an editor and navigating replaced text."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


def _reload(session: BrowserSession) -> tuple[list[str], list[BrailleLine]]:
    """Reloads with Orca running so the page's initial focus events are captured."""

    session.orca.set("BraillePresenter", "FlashMessagesAreEnabled", False)
    # Keep focus on Start until Tab moves it into the editor.
    session.orca.set("DocumentPresenter", "SayAllOnLoad", False)
    helpers.capture(session, wait_async=True)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_R)
    return helpers.capture(session, wait_async=True)


@pytest.mark.native_app
def test_tab_into_editor(web_contenteditable_replacement_button: BrowserSession) -> None:
    """Tests that the initial line announcement survives subsequent page events."""

    session = web_contenteditable_replacement_button
    _reload(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, _brailled = helpers.capture(session, wait_async=True)
    assert spoken == ["Line one.", "Focus mode"]


@pytest.mark.native_app
@pytest.mark.parametrize("presentation", ["speech", "braille"])
def test_replaced_lines_down_and_up(
    web_contenteditable_replacement_button: BrowserSession,
    presentation: str,
) -> None:
    """Tests that replacement text is presented while moving in both directions."""

    session = web_contenteditable_replacement_button
    _reload(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    helpers.capture(session, wait_async=True)

    lines = ["Line two.", "Line three.", "Line two.", "Line one."]
    spoken_lines = []
    brailled_lines = []
    for key in (keyboard.KEYSYM_DOWN, keyboard.KEYSYM_DOWN, keyboard.KEYSYM_UP, keyboard.KEYSYM_UP):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session, wait_async=True)
        spoken_lines.append(spoken)
        brailled_lines.append(brailled[-1] if brailled else None)

    if presentation == "speech":
        assert spoken_lines == [[line] for line in lines]
    else:
        assert brailled_lines == [
            BrailleLine(1, f"{line} $l", f"{line} $l", "\x00" * (len(line) + 3)) for line in lines
        ]
