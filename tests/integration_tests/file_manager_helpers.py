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

"""Shared test data and keyboard setup for file-manager tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.integration_tests.harness import keyboard
from tests.integration_tests.helpers import capture

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import FileManagerSession

LONG_NAME = "long filename for testing braille panning and file navigation.txt"


def start_at_first_file(session: FileManagerSession) -> None:
    """Presses End then Home to start on the first item."""

    for key in (keyboard.KEYSYM_END, keyboard.KEYSYM_HOME):
        keyboard.tap_key(key)
        capture(session)
