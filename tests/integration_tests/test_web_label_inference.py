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

"""Tests inferred names for unlabeled native web controls as focus tabs to each."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _focus_next(session: NativeAppSession) -> list[str]:
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    return speech(session)


@pytest.mark.native_app
def test_label_inference_on_tab(web_label_inference: NativeAppSession) -> None:
    """Tests that an unlabeled control's name is inferred from nearby text on focus."""

    session = web_label_inference
    reset_web_state(session)

    assert _focus_next(session) == ["Full name:", "entry", "Focus mode"]
    assert _focus_next(session) == ["Remember me", "check box not checked", "Browse mode"]
    assert _focus_next(session) == ["Blue", "not selected radio button"]
    assert _focus_next(session) == ["Quantity", "entry", "Focus mode"]
    assert _focus_next(session) == ["Password:", "password text"]
