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

"""Integration tests for braille panning in terminals."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .apps import terminal
from .terminal_helpers import WIDE_PROMPT_INPUT, WIDE_PROMPT_LINE, settle, type_text

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_pan_braille_across_terminal_line(terminal_shell: NativeAppSession) -> None:
    """Tests panning across a prompt line wider than the display, including the edge-walk."""

    session = terminal_shell
    settle(session)
    type_text(WIDE_PROMPT_INPUT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    with helpers.bound_pan_keys(session) as (left_key, right_key):
        mask = "\x00" * len(WIDE_PROMPT_LINE)
        # Pan-left slides the window back to the start of the line.
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [
                helpers.BrailleLine(
                    0,
                    WIDE_PROMPT_LINE,
                    "$ abcdefghij klmnopqrst uvwxy 01",
                    mask,
                )
            ],
        )
        # Pan-right slides the window to the end of the line.
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(9, WIDE_PROMPT_LINE, "01234567", mask)],
        )


@pytest.mark.native_app
@pytest.mark.skipif(
    terminal.selected_toolkit() == "gtk4",
    reason="GTK4 VTE intermittently exposes stale text: "
    "https://gitlab.gnome.org/GNOME/vte/-/work_items/2972",
)
def test_pan_braille_left_crosses_wide_line_in_pager(
    terminal_wide_pager: NativeAppSession,
) -> None:
    """Tests that panning left over a pager line wider than the display reaches the line above."""

    session = terminal_wide_pager
    settle(session)
    helpers.toggle_flat_review(session)

    wide = "this line is wider than the display now $l"
    wide_mask = "\x00" * len(wide)
    with helpers.bound_pan_keys(session) as (left_key, _right_key):
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(7, "bottom $l", "bottom $l", "\x00" * 9)],
        )
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(12, wide, "display now $l", wide_mask)],
        )
        # The start view is painted twice: by the pan, then by the flat-review zone-sync refresh.
        session.orca.press_bound_key(left_key)
        start_view = "this line is wider than the disp"
        assert helpers.capture(session) == (
            [],
            [
                helpers.BrailleLine(0, wide, start_view, wide_mask),
                helpers.BrailleLine(0, wide, start_view, wide_mask),
            ],
        )
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(4, "top $l", "top $l", "\x00" * 6)],
        )
