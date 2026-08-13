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

from .harness import keyboard
from .web_native_selection_helpers import (
    native_selection,
    say_selection,
    select_line,
    select_word,
)

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_say_selected_text(web_native_text_selection: NativeAppSession) -> None:
    """Tests say selected text for a selection which spans several elements."""

    session = web_native_text_selection

    with native_selection(session):
        assert say_selection(session) == ["No selected text."]

        assert select_word(session, keyboard.KEYSYM_RIGHT) == ["Structural", "selected"]
        assert say_selection(session) == ["Selected text is:  Structural"]

        assert select_line(session, keyboard.KEYSYM_DOWN) == [
            "navigation Intro paragraph.",
            "selected",
        ]
        assert say_selection(session) == [
            "Selected text is:  Structural navigation Intro paragraph."
        ]

        assert select_line(session, keyboard.KEYSYM_DOWN) == ["Quoted text.", "selected"]
        assert say_selection(session) == [
            "Selected text is:  Structural navigation Intro paragraph. Quoted text."
        ]
