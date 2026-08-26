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

"""Helpers for Chromium native text-selection integration tests."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .orca_fixtures import NativeAppSession

LONG_PARAGRAPH = (
    "This is a sufficiently long paragraph of body text so that it qualifies as a "
    "large object for structural navigation, which targets substantial chunks of "
    "readable prose rather than short fragments or individual controls."
)


@contextlib.contextmanager
def native_selection(session: NativeAppSession) -> Iterator[None]:
    """Runs the block in browse mode, where Chromium's own caret performs the selection."""

    reset_web_state(session)
    assert not session.orca.get("DocumentPresenter", "InFocusMode")
    yield


def select_character(session: NativeAppSession, key: str) -> list[str]:
    """Extends or retracts Chromium's native selection by one character."""

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], key)
    return speech(session)


def select_word(session: NativeAppSession, key: str) -> list[str]:
    """Extends or retracts Chromium's native selection by one word."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], key)
    return speech(session)


def select_line(session: NativeAppSession, key: str) -> list[str]:
    """Extends or retracts Chromium's native selection by one line."""

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], key)
    return speech(session)


def assert_walks(
    selected: list[list[str]],
    unselected: list[list[str]],
    expected_selected: list[list[str]],
    expected_unselected: list[list[str]],
) -> None:
    """Asserts both walks after all keystrokes have been sent."""

    if (selected, unselected) != (expected_selected, expected_unselected):
        pytest.fail(
            f"Selected speech:\n{selected!r}\n\nUnselected speech:\n{unselected!r}",
            pytrace=False,
        )
