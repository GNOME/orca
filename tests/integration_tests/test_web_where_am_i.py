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

"""Tests basic Where Am I on web controls, reusing the per-shape content pages."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state, tab

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _where_am_i(session: NativeAppSession) -> tuple[list[str], list[tuple[int, str, str | None]]]:
    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    return capture(session)


@pytest.mark.native_app
def test_where_am_i_on_form_controls(web_form_fields: NativeAppSession) -> None:
    """Tests Where Am I on entry, combo box, checkbox, radio button, and button."""

    session = web_form_fields
    reset_web_state(session)

    tab(session)
    assert _where_am_i(session) == (
        ["entry", "Jane Doe", "selected"],
        [
            BrailleLine(
                14, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 5 + "\xc0" * 8 + "\x00" * 3
            ),
            BrailleLine(
                14, "Name Jane Doe $l", "Name Jane Doe $l", "\x00" * 5 + "\xc0" * 8 + "\x00" * 3
            ),
        ],
    )

    for _ in range(3):
        tab(session)
    assert _where_am_i(session) == (
        ["Fruit", "combo box", "Apple"],
        [BrailleLine(7, "Fruit Apple combo box", "Fruit Apple combo box", "\x00" * 21)],
    )

    tab(session)
    assert _where_am_i(session) == (
        ["Subscribe", "check box not checked"],
        [
            BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23),
            BrailleLine(1, "< > Subscribe check box", "< > Subscribe check box", "\x00" * 23),
        ],
    )

    tab(session)
    assert _where_am_i(session) == (
        ["Pick a color", "Red color", "not selected radio button"],
        [
            BrailleLine(
                14,
                " Pick a color& y Red color radio button",
                " Pick a color& y Red color radio",
                "\x00" * 39,
            )
        ],
    )

    for _ in range(2):
        tab(session)
    assert _where_am_i(session) == (
        ["Submit", "button"],
        [
            BrailleLine(1, "Submit button", "Submit button", "\x00" * 13),
            BrailleLine(1, "Submit button", "Submit button", "\x00" * 13),
        ],
    )


@pytest.mark.native_app
def test_where_am_i_on_slider(web_sliders: NativeAppSession) -> None:
    """Tests Where Am I on a horizontal slider."""

    session = web_sliders
    reset_web_state(session)

    tab(session)
    assert _where_am_i(session) == (
        ["Volume", "horizontal slider", "2", "50 percent."],
        [
            BrailleLine(1, "Volume 2 horizontal slider", "Volume 2 horizontal slider", "\x00" * 26),
            BrailleLine(1, "Volume 2 horizontal slider", "Volume 2 horizontal slider", "\x00" * 26),
        ],
    )


@pytest.mark.native_app
def test_where_am_i_on_link(web_landmarks: NativeAppSession) -> None:
    """Tests Where Am I on a link."""

    session = web_landmarks
    reset_web_state(session)

    tab(session)
    assert _where_am_i(session) == (
        ["https link Home", "different site"],
        [BrailleLine(1, "Home", "Home", "\xc0" * 4)],
    )
