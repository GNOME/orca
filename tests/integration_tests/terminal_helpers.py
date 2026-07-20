# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

"""Shared helpers for terminal integration tests."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from .harness import keyboard

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .orca_fixtures import NativeAppSession


WIDE_PROMPT_INPUT = "abcdefghij klmnopqrst uvwxy 01234567"
WIDE_PROMPT_LINE = "$ abcdefghij klmnopqrst uvwxy 01234567"


@contextlib.contextmanager
def bound_command(session: NativeAppSession, handler: str) -> Iterator[str]:
    """Binds handler to a free key for the block, yielding the key to press."""

    ((key, mods),) = session.orca.available_keybindings(1)
    session.orca.bind_command(handler, key, mods)
    session.orca.refresh_keybindings()
    try:
        yield key
    finally:
        session.orca.unbind_command(handler)
        session.orca.refresh_keybindings()


def type_text(text: str) -> None:
    """Types text using synthesized keyboard events."""

    for char in text:
        if char == " ":
            keyboard.tap_key(keyboard.KEYSYM_SPACE)
        elif char == "\n":
            keyboard.tap_key(keyboard.KEYSYM_RETURN)
        elif char.isupper():
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], ord(char.lower()))
        else:
            keyboard.tap_key(ord(char))


def settle(session: NativeAppSession) -> None:
    """Waits for the spawned program to finish its initial paint and resets the reader."""

    session.reader.drain(quiescence_timeout=0.5, overall_timeout=4.0)
    session.reader.reset()
