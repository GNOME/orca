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

"""Tests paragraph navigation across the full-filtering cutoff."""

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
def test_paragraph_filter_cutoff(web_large_paragraphs: BrowserSession) -> None:
    """Tests paragraph navigation at 2500 candidates and after adding one more."""

    session = web_large_paragraphs
    # Key echo can be interrupted while the full paragraph filter runs.
    session.orca.set("TypingEchoPresenter", "KeyEchoEnabled", False)
    move_to_top(session)

    assert _next(session, keyboard.KEYSYM_P) == (
        ["main content", "First valid paragraph."],
        [BrailleLine(1, "First valid paragraph.", "First valid paragraph.", "\x00" * 22)],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["After short paragraphs."],
        [BrailleLine(1, "After short paragraphs.", "After short paragraphs.", "\x00" * 23)],
    )

    assert _previous(session, keyboard.KEYSYM_P) == (
        ["First valid paragraph."],
        [BrailleLine(1, "First valid paragraph.", "First valid paragraph.", "\x00" * 22)],
    )

    assert _next(session, keyboard.KEYSYM_U) == (
        ["Link in short paragraph", "link"],
        [BrailleLine(1, "Link in short paragraph", "Link in short paragraph", "\xc0" * 23)],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["After short paragraphs."],
        [BrailleLine(1, "After short paragraphs.", "After short paragraphs.", "\x00" * 23)],
    )

    assert _previous(session, keyboard.KEYSYM_B) == (
        ["leaving main content.", "Add one paragraph", "button"],
        [BrailleLine(1, "Add one paragraph button", "Add one paragraph button", "\x00" * 24)],
    )

    assert _next(session, keyboard.KEYSYM_RETURN) == ([], [])

    move_to_top(session)

    assert _next(session, keyboard.KEYSYM_P) == (
        ["main content", "First valid paragraph."],
        [BrailleLine(1, "First valid paragraph.", "First valid paragraph.", "\x00" * 22)],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["x"],
        [BrailleLine(1, "x", "x", "\x00")],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["xy"],
        [BrailleLine(1, "xy", "xy", "\x00" * 2)],
    )

    assert _next(session, keyboard.KEYSYM_U) == (
        ["Link in short paragraph", "link"],
        [BrailleLine(1, "Link in short paragraph", "Link in short paragraph", "\xc0" * 23)],
    )

    assert _previous(session, keyboard.KEYSYM_P) == (
        ["xy"],
        [BrailleLine(1, "xy", "xy", "\x00" * 2)],
    )

    assert _next(session, keyboard.KEYSYM_U) == (
        ["Link in short paragraph", "link"],
        [BrailleLine(1, "Link in short paragraph", "Link in short paragraph", "\xc0" * 23)],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["After short paragraphs."],
        [BrailleLine(1, "After short paragraphs.", "After short paragraphs.", "\x00" * 23)],
    )

    assert _next(session, keyboard.KEYSYM_U) == (
        ["Link in long paragraph", "link"],
        [BrailleLine(1, "Link in long paragraph", "Link in long paragraph", "\xc0" * 22)],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["Following accepted paragraph."],
        [
            BrailleLine(
                1, "Following accepted paragraph.", "Following accepted paragraph.", "\x00" * 29
            )
        ],
    )
