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

"""Exercise caret-movement announcements via arrow-key navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_arrow_down_announces_next_line(gtk3_text_view: NativeAppSession) -> None:
    """Pressing Down moves the caret to the next line and Orca announces it."""

    session = gtk3_text_view
    session.reader.reset()

    keyboard.press_key(keyboard.KEYSYM_DOWN)
    keyboard.release_key(keyboard.KEYSYM_DOWN)
    session.reader.wait_for_speech("Second line.")
    session.reader.wait_for_braille("Second line.")
