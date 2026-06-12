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

"""Tests flat review of web content whose text changes while review is active."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine, capture, toggle_flat_review

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_LONG_FULL = "alpha bravo charlie delta echo foxtrot golf $l"
_LONG_VISIBLE = "alpha bravo charlie delta echo f"
_SHORT_FULL = "alpha bravo $l"


def _long(cursor_cell: int) -> BrailleLine:
    return BrailleLine(cursor_cell, _LONG_FULL, _LONG_VISIBLE, "\x00" * len(_LONG_FULL))


def _short(cursor_cell: int) -> BrailleLine:
    return BrailleLine(cursor_cell, _SHORT_FULL, _SHORT_FULL, "\x00" * len(_SHORT_FULL))


def _command(session: NativeAppSession, name: str) -> tuple[list[str], list[BrailleLine]]:
    session.orca.call("FlatReviewPresenter", name, True)
    return capture(session)


@pytest.mark.native_app
def test_review_line_whose_text_shrinks(web_flat_review_shrink: NativeAppSession) -> None:
    """Tests reviewing a line word by word while its text shrinks underneath."""

    session = web_flat_review_shrink
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    # Activate the button to arm a delayed shrink, then return the caret to the
    # document so flat review parks on the paragraph rather than the button.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    helpers.move_to_top(session)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    toggle_flat_review(session)

    try:
        assert _command(session, "PresentItem") == (["alpha "], [_long(1)])
        assert _command(session, "GoNextItem") == (["bravo "], [_long(7)])
        assert _command(session, "GoNextItem") == (["charlie "], [_long(13)])

        # The paragraph's text shrinks from seven words to two after a delay long
        # enough that the word walk above always finishes first; sync on the live
        # region's "shrunk" announcement, waiting patiently for it to land.
        capture(session, wait_async=True, overall=10.0)

        assert _command(session, "PresentItem") == (["alpha "], [_short(1)])
        assert _command(session, "PresentLine") == (["alpha bravo"], [_short(1)])
    finally:
        toggle_flat_review(session)
