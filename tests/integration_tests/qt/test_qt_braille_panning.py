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

"""Tests braille panning in a text view."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_pan_to_ancestry(qt_text_view: NativeAppSession) -> None:
    """Pans to the application and window names, then back to the text."""

    session = qt_text_view
    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    helpers.capture(session)
    helpers.move_to_top(session)
    with helpers.bound_pan_keys(session) as (left, right):
        for key, visible in (
            (left, "OrcaTextView frame Line one. $l"),
            (left, "OrcaTextView application OrcaTex"),
            (right, "OrcaTextView frame Line one. $l"),
            (right, "Line one. $l"),
        ):
            session.orca.press_bound_key(key)
            spoken, brailled = helpers.capture(session)
            assert spoken == []
            assert brailled[-1].visible == visible


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=(
        "Qt line ranges omit the wrapping space, so braille panning does not reach the next line"
    ),
    strict=True,
    raises=AssertionError,
)
def test_pan_across_wrapped_line(qt_text_view: NativeAppSession) -> None:
    """Pans along a long line and continues onto its wrapped continuation."""

    session = qt_text_view
    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Line two has additional words to make it long enough that the"]
    assert brailled[-1].visible == "Line two has additional words to"
    with helpers.bound_pan_keys(session) as (_left, right):
        session.orca.press_bound_key(right)
        spoken, brailled = helpers.capture(session)
        assert spoken == []
        assert brailled[-1].visible == "to make it long enough that the "
        session.orca.press_bound_key(right)
        spoken, brailled = helpers.capture(session)
        assert spoken == []
        assert brailled[-1].visible == "$l"
        session.orca.press_bound_key(right)
        spoken, brailled = helpers.capture(session)
        assert spoken == []
        assert brailled[-1].visible == "text view wraps it. $l"
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        spoken, brailled = helpers.capture(session)
        assert spoken == ["e"]
        assert brailled[-1].visible == "text view wraps it. $l"


@pytest.mark.native_app
def test_character_navigation_after_panning(qt_text_view: NativeAppSession) -> None:
    """Returns braille to the caret when character navigation follows panning."""

    session = qt_text_view
    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    helpers.capture(session)
    with helpers.bound_pan_keys(session) as (_left, right):
        session.orca.press_bound_key(right)
        helpers.capture(session)
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        spoken, brailled = helpers.capture(session)
        assert spoken == ["i"]
        assert brailled[-1].visible == "ine two has additional words to "
