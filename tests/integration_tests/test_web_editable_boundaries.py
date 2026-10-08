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

"""Tests that an editable block's line excludes neighboring controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
@pytest.mark.parametrize("layout", [0, 1], ids=["stacked", "floated"])
def test_editor_line_excludes_neighboring_button(
    web_editable_boundaries: BrowserSession, layout: int
) -> None:
    """Tests the editor's braille and line navigation after its button transfers focus."""

    session = web_editable_boundaries
    helpers.reset_web_state(session)
    session.orca.set("BraillePresenter", "FlashMessagesAreEnabled", False)
    try:
        for _ in range(layout + 1):
            keyboard.tap_key(keyboard.KEYSYM_B)
            helpers.capture(session)
        keyboard.tap_key(keyboard.KEYSYM_RETURN)
        _, braille = helpers.capture(session)
        assert braille[-1].full == "Editor text. $l"

        for key in (keyboard.KEYSYM_DOWN, keyboard.KEYSYM_UP):
            keyboard.tap_key(key)
            spoken, braille = helpers.capture(session)
            assert spoken == ["Editor text."]
            assert braille[-1].full == "Editor text. $l"
    finally:
        session.orca.set("BraillePresenter", "FlashMessagesAreEnabled", True)
