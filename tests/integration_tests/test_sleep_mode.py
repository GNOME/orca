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

"""Tests the sleep-mode toggle command for an application."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_SLEEP_MODE_MODIFIERS = [
    keyboard.KEYSYM_SHIFT_L,
    keyboard.KEYSYM_ALT_L,
    keyboard.KEYSYM_CONTROL_L,
]


def _toggle_sleep_mode(session: NativeAppSession) -> list[str]:
    keyboard.press_chord(_SLEEP_MODE_MODIFIERS, keyboard.KEYSYM_Q)
    return speech(session)


@pytest.mark.native_app
def test_toggle_sleep_mode_for_application(gtk3_text_view: NativeAppSession) -> None:
    """Tests that the sleep-mode command enables and then disables sleep mode by app name."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _toggle_sleep_mode(session) == ["Sleep mode enabled for OrcaTextView."]
    assert _toggle_sleep_mode(session) == ["Sleep mode disabled for OrcaTextView."]
