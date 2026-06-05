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

"""Tests presentation of an alert inserted into web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_inserted_alertdialog_is_presented(web_alert: NativeAppSession) -> None:
    """Tests that appending a role=alertdialog element into a plain container presents it."""

    session = web_alert
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Submit", "button"]

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert capture(session, wait_async=True) == (
        ["alert", "Notice", "Form submitted"],
        [BrailleLine(1, "Notice alert", "Notice alert", "\x00" * 12)],
    )
