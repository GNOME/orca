# Orca
#
# Copyright 2026 Igalia, S.L.
# Based on test_web_braille_selection.py.
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

"""Tests selection markers following a contracted input label."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_selection_mask_contracted_label(web_labelled_braille: BrowserSession) -> None:
    """Keep selection markers aligned after a contracted input label."""

    session = web_labelled_braille
    helpers.reset_web_state(session)
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", True)
    session.orca.set("BraillePresenter", "ContractionTable", "en-ueb-g2")
    session.orca.set("BraillePresenter", "ComputerBrailleAtCursorIsEnabled", False)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    for _ in range(7):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    _, brailled = helpers.capture(session)
    line = brailled[-1]
    assert line.full.startswith(',"n3 & ! p}son is gd')
    expected = "\x00" * 5 + "\xc0" * 3
    expected += "\x00" * (len(line.full) - len(expected))
    assert line.mask == expected
