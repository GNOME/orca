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

"""Tests Say All in nested blockquotes containing multiple sentences."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_say_all_reads_all_nested_blockquote_sentences(
    web_nested_blockquotes: NativeAppSession,
) -> None:
    """Tests that Say All does not skip text inside nested blockquotes."""

    session = web_nested_blockquotes
    reset_web_state(session)
    session.orca.set("SayAllPresenter", "Style", "sentence")

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    spoken = [utterance.strip() for utterance in speech(session)]
    assert spoken == [
        "Top post.",
        "block quote",
        "First quoted sentence.",
        "Second quoted sentence.",
        "block quote",
        "First nested sentence.",
        "Second nested sentence.",
        "Final outer sentence.",
        "leaving blockquote.",
        "After replies.",
    ]
