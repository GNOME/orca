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

"""Tests say selected text in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers, web_native_selection_helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_say_selected_text(web_native_text_selection: BrowserSession) -> None:
    """Tests say selected text for a selection which spans several elements."""

    session = web_native_text_selection

    with web_native_selection_helpers.native_selection(session):
        assert helpers.say_selection(session) == ["No selected text."]

        assert web_native_selection_helpers.select_word(session, keyboard.KEYSYM_RIGHT) == [
            "Structural",
            "selected",
        ]
        assert helpers.say_selection(session) == ["Selected text is:  Structural"]

        assert web_native_selection_helpers.select_line(session, keyboard.KEYSYM_DOWN) == [
            "navigation Intro paragraph.",
            "selected",
        ]
        assert helpers.say_selection(session) == [
            "Selected text is:  Structural navigation Intro paragraph."
        ]

        assert web_native_selection_helpers.select_line(session, keyboard.KEYSYM_DOWN) == [
            "Quoted text.",
            "selected",
        ]
        assert helpers.say_selection(session) == [
            "Selected text is:  Structural navigation Intro paragraph. Quoted text."
        ]
