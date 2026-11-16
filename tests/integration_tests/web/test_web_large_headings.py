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

"""Tests heading-level navigation in a large document."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests.harness import keyboard
from tests.integration_tests.helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


def _next(session: BrowserSession, keysym: int) -> tuple[list[str], list[BrailleLine]]:
    keyboard.tap_key(keysym)
    return capture(session)


def _previous(session: BrowserSession, keysym: int) -> tuple[list[str], list[BrailleLine]]:
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keysym)
    return capture(session)


@pytest.mark.native_app
def test_heading_levels_in_large_document(web_large_headings: BrowserSession) -> None:
    """Tests level-specific navigation with 3001 headings at each level."""

    session = web_large_headings
    move_to_top(session)

    assert _next(session, keyboard.KEYSYM_3) == (
        ["3", "Level three 0", "heading 3"],
        [BrailleLine(1, "Level three 0 h3", "Level three 0 h3", "\x00" * 16)],
    )

    assert _next(session, keyboard.KEYSYM_3) == (
        ["3", "Level three 1", "heading 3"],
        [BrailleLine(1, "Level three 1 h3", "Level three 1 h3", "\x00" * 16)],
    )

    assert _previous(session, keyboard.KEYSYM_3) == (
        ["#", "Level three 0", "heading 3"],
        [BrailleLine(1, "Level three 0 h3", "Level three 0 h3", "\x00" * 16)],
    )

    assert _next(session, keyboard.KEYSYM_2) == (
        ["2", "Level two 1", "heading 2"],
        [BrailleLine(1, "Level two 1 h2", "Level two 1 h2", "\x00" * 14)],
    )
