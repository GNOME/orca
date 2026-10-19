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

"""Tests Say All across PDF page boundaries."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .atril_helpers import FIRST_PAGE, SECOND_PAGE, navigation_session
from .harness import keyboard
from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import AtrilSession


@pytest.mark.native_app
@pytest.mark.parametrize("style", ["line", "sentence"])
def test_say_all_across_pages(atril: AtrilSession, style: str) -> None:
    """Checks that Say All reads both pages once and finishes on the second page."""

    previous_style = atril.orca.get("SayAllPresenter", "Style")
    try:
        with navigation_session(atril, native=False):
            atril.orca.set("SayAllPresenter", "Style", style)
            keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
            spoken, brailled = capture(atril, quiescence=0.4, overall=10.0)

            # The page-change notification can arrive between utterances.
            assert spoken.count("Page 2") == 1
            spoken.remove("Page 2")
            expected = " ".join((FIRST_PAGE + " " + SECOND_PAGE).split())
            assert " ".join(" ".join(spoken).split()) == expected

            last_line = SECOND_PAGE.splitlines()[-1 if style == "line" else -2]
            assert brailled[-1] == BrailleLine(1, last_line, last_line, "\x00" * len(last_line))
    finally:
        atril.orca.set("SayAllPresenter", "Style", previous_style)
