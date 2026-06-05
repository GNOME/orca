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

"""Tests activating same-page links (anchors to a fragment in the same document)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_LONG_LINE = (
    "The quick brown fox jumps over the lazy dog and then keeps running across the wide "
    "open field for a very "
)
_LONG_VISIBLE = "The quick brown fox jumps over t"
_SECOND_LINE = "Second paragraph line."


def _reset_to_top(session: NativeAppSession) -> None:
    """Resets web state and moves to the top of the document."""

    helpers.reset_web_state(session)
    helpers.move_to_top(session)


def _next_link(session: NativeAppSession) -> None:
    """Moves to the next link with structural navigation and discards the output."""

    keyboard.tap_key(keyboard.KEYSYM_K)
    session.reader.drain(quiescence_timeout=0.1, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_activate_same_page_link_to_paragraph(web_long_line: NativeAppSession) -> None:
    """Tests activating a same-page link whose target id is a paragraph."""

    session = web_long_line
    _reset_to_top(session)

    _next_link(session)  # The "link" anchored to #long.
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    assert helpers.capture(session, wait_async=True) == (
        [_LONG_LINE],
        [helpers.BrailleLine(0, _LONG_LINE, _LONG_VISIBLE, "\x00" * len(_LONG_LINE))],
    )


@pytest.mark.native_app
def test_activate_same_page_link_to_second_paragraph(web_long_line: NativeAppSession) -> None:
    """Tests activating a same-page link whose target id is a different paragraph."""

    session = web_long_line
    _reset_to_top(session)

    _next_link(session)  # The "link" anchored to #long.
    _next_link(session)  # The "middle link" anchored to #second.
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    assert helpers.capture(session, wait_async=True) == (
        [_SECOND_LINE],
        [helpers.BrailleLine(0, _SECOND_LINE, _SECOND_LINE, "\x00" * len(_SECOND_LINE))],
    )
