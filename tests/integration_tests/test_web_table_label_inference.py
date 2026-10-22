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

"""Tests table-header label inference for unlabeled controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


_ACCOUNT = BrailleLine(
    16, "Account Current $l", "Account Current $l", "\x00" * 8 + "\xc0" * 7 + "\x00" * 3
)
_EDITABLE = BrailleLine(9, "Editable $l", "Editable $l", "\xc0" * 8 + "\x00" * 3)
_EARLY = BrailleLine(6, "Early $l", "Early $l", "\xc0" * 5 + "\x00" * 3)
_LATE = BrailleLine(5, "Late $l", "Late $l", "\xc0" * 4 + "\x00" * 3)


@pytest.mark.native_app
def test_table_header_labels_on_tab(web_table_label_inference: BrowserSession) -> None:
    """Uses the correct header column and rejects editable headers and mixed controls."""

    session = web_table_label_inference
    helpers.reset_web_state(session)

    # The preceding row contains controls, so the label must come from the first row.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        [
            "table with 3 rows 2 columns",
            "row 3",
            "column 2",
            "Account",
            "entry",
            "Current",
            "selected",
            "Focus mode",
        ],
        [_ACCOUNT, BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)],
    )

    forward = (
        (
            ["leaving table.", "table with 3 rows 2 columns", "entry", "Editable", "selected"],
            _EDITABLE,
        ),
        (
            [
                "leaving table.",
                "table with 3 rows 1 column",
                "column 1",
                "entry",
                "Early",
                "selected",
            ],
            _EARLY,
        ),
        (["leaving table.", "table with 4 rows 1 column", "entry", "Late", "selected"], _LATE),
    )
    for expected_speech, expected_braille in forward:
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        spoken, brailled = helpers.capture(session)
        assert spoken == expected_speech
        assert brailled[-1] == expected_braille

    backward = (
        (["leaving table.", "table with 3 rows 1 column", "entry", "Early", "selected"], _EARLY),
        (
            [
                "leaving table.",
                "table with 3 rows 2 columns",
                "column 2",
                "entry",
                "Editable",
                "selected",
            ],
            _EDITABLE,
        ),
        (
            [
                "leaving table.",
                "table with 3 rows 2 columns",
                "Account",
                "entry",
                "Current",
                "selected",
            ],
            _ACCOUNT,
        ),
    )
    for expected_speech, expected_braille in backward:
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
        spoken, brailled = helpers.capture(session)
        assert spoken == expected_speech
        assert brailled[-1] == expected_braille
