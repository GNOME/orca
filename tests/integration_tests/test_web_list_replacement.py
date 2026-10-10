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

"""Tests list-item navigation after replacing the list's children."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_list_item_navigation_after_replacement(web_list_replacement: BrowserSession) -> None:
    """Tests next and previous list items before and after replacing the list's children."""

    session = web_list_replacement
    helpers.reset_web_state(session)

    pages = [("Alpha", "Beta", "Gamma"), ("Delta", "Epsilon", "Zeta"), ("Alpha", "Beta", "Gamma")]
    for page, titles in enumerate(pages):
        for index, title in enumerate(titles):
            keyboard.tap_key(keyboard.KEYSYM_I)
            spoken, brailled = helpers.capture(session)
            expected = ["i"]
            if index == 0:
                if page:
                    expected.append("Wrapping to top.")
                expected.append("List with 3 items")
            assert spoken == [*expected, title, "link"]
            assert brailled[-1] == BrailleLine(1, title, title, "\xc0" * len(title))

        for title in reversed(titles[:-1]):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_I)
            spoken, brailled = helpers.capture(session)
            assert spoken == ["I", title, "link"]
            assert brailled[-1] == BrailleLine(1, title, title, "\xc0" * len(title))

        if page == len(pages) - 1:
            break

        keyboard.tap_key(keyboard.KEYSYM_B)
        spoken, brailled = helpers.capture(session)
        assert spoken == ["b", "leaving list.", "Next page", "button"]
        assert brailled[-1] == BrailleLine(1, "Next page button", "Next page button", "\x00" * 16)

        keyboard.tap_key(keyboard.KEYSYM_RETURN)
        helpers.capture(session)
