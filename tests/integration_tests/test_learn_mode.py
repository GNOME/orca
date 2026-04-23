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

"""Exercise Orca's learn mode via the Orca+H / Orca+T / Escape sequence."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_learn_mode_announces_orca_t_binding(gtk3_text_view: NativeAppSession) -> None:
    """Orca+H enters learn mode, Orca+T announces its binding, Escape exits."""

    session = gtk3_text_view
    session.reader.reset()

    session.orca.press_orca_key(keyboard.KEYSYM_H)
    session.reader.wait_for_speech("Entering learn mode")
    session.reader.wait_for_braille("Learn mode")

    session.orca.press_orca_key(keyboard.KEYSYM_T)
    session.reader.wait_for_speech("Present current time")
    session.reader.wait_for_braille("Present current time")

    keyboard.press_key(keyboard.KEYSYM_ESCAPE)
    keyboard.release_key(keyboard.KEYSYM_ESCAPE)
    session.reader.wait_for_speech("Exiting learn mode")
    session.reader.wait_for_braille("Exiting learn mode")
