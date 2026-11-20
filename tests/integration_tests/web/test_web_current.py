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

"""Tests presentation of links with aria-current."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_current_links(web_current: BrowserSession) -> None:
    """Arrow through links and hear and read which one is current."""

    session = web_current
    helpers.reset_web_state(session)
    for name, status in (
        ("Overview", "(Current page)"),
        ("Payment", "(Current step)"),
        ("Library", "(Current location)"),
        ("Monday", "(Current date)"),
        ("Noon", "(Current time)"),
        ("First draft", "(Current item)"),
        ("Revision", "(Current item)"),
        ("Receipt", ""),
        ("Notes", ""),
        ("Contact", ""),
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, brailled = helpers.capture(session)
        assert spoken == ([name, "link", status] if status else [name, "link"])
        line = f"{name} {status}" if status else name
        assert brailled[-1].visible == line
