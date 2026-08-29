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

"""Tests Say All in a GTK text view."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_say_all_by_sentence_skips_blank_line(
    gtk3_text_view_blank_line: NativeAppSession,
) -> None:
    """Tests sentence-mode Say All with a blank line between sentences."""

    session = gtk3_text_view_blank_line
    session.orca.set("SayAllPresenter", "Style", "sentence")
    session.orca.set("SayAllPresenter", "OnlySpeakDisplayedText", True)
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(session, quiescence=0.4, overall=10.0) == [
        "First sentence.\n\n",
        "Second sentence.\n",
    ]
