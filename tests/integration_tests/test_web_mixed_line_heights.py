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

"""Tests that a differently-sized inline child does not fragment a line of web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


# A taller-than-text inline child (an image, a larger-font link/button) and a shorter-than-text
# one share the surrounding text's baseline, not its vertical midpoint, so the same-line test
# must key off vertical overlap. Each paragraph below is a single visual line; arrowing by line
# lands on it once with the whole line, whichever element is taller and wherever it sits.
_LINES = [
    (["Alpha ", "big square", "image", " beta."], "Alpha big square image beta."),
    (["big square", "image", " gamma here."], "big square image gamma here."),
    (["Delta then ", "big square", "image"], "Delta then big square image"),
    (["Epsilon ", "big link", "link", " zeta."], "Epsilon big link zeta."),
    (["big link", "link", " eta here."], "big link eta here."),
    (["Theta ", "big button", "button", " iota."], "Theta big button button iota."),
    (["big button", "button", " kappa here."], "big button button kappa here."),
    (["Lambda ", "small square", "image", " mu."], "Lambda small square image mu."),
    (["small square", "image", " nu here."], "small square image nu here."),
    (["Xi ", "small link", "link", " omicron."], "Xi small link omicron."),
    (["small link", "link", " pi here."], "small link pi here."),
    (["Rho ", "small button", "button", " sigma."], "Rho small button button sigma."),
    (["Final line."], "Final line."),
]

_HEADING = (["Mixed line heights", "heading 1"], "Mixed line heights h1")


def _assert_each_is_one_line(session, key, lines) -> None:
    """Arrows once per entry and asserts each landed on a single line with the whole content."""

    for expected_speech, expected_line in lines:
        keyboard.tap_key(key)
        spoken, braille = helpers.capture(session)
        assert spoken == expected_speech
        assert [line.full for line in braille] == [expected_line]


@pytest.mark.native_app
def test_line_down_keeps_mixed_height_elements_on_one_line(
    web_mixed_line_heights: NativeAppSession,
) -> None:
    """Tests that arrowing down by line presents each mixed-height paragraph as a single line."""

    session = web_mixed_line_heights
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    _assert_each_is_one_line(session, keyboard.KEYSYM_DOWN, _LINES)


@pytest.mark.native_app
def test_line_up_keeps_mixed_height_elements_on_one_line(
    web_mixed_line_heights: NativeAppSession,
) -> None:
    """Tests that arrowing up by line presents each mixed-height paragraph as a single line."""

    session = web_mixed_line_heights
    helpers.reset_web_state(session)
    helpers.move_to_bottom(session)
    helpers.capture(session)
    _assert_each_is_one_line(session, keyboard.KEYSYM_UP, [*reversed(_LINES[:-1]), _HEADING])
