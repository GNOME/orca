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

"""Shared helpers for Orca integration tests, both web and native-app."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, NamedTuple

from orca.output_reader import BrailleRecord, SpeechRecord

from .harness import keyboard

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .orca_fixtures import NativeAppSession

PAN_LEFT_COMMAND = "panBrailleLeftHandler"
PAN_RIGHT_COMMAND = "panBrailleRightHandler"


class BrailleLine(NamedTuple):
    """A braille line: cursor cell, full logical line, visible window, and full-line mask."""

    cursor_cell: int
    full: str
    visible: str
    mask: str | None = None


_PROMPT_QUIESCENCE = 0.1
_ASYNC_QUIESCENCE = 0.5


def _drain(
    session: NativeAppSession, quiescence: float | None, overall: float, wait_async: bool
) -> list:
    """Drains output, idle-gated for prompt output and patient for app-delayed output."""

    if wait_async:
        return session.reader.drain(
            quiescence_timeout=_ASYNC_QUIESCENCE if quiescence is None else quiescence,
            overall_timeout=overall,
            first_record_timeout=overall,
            idle_aware=False,
        )
    return session.reader.drain(
        quiescence_timeout=_PROMPT_QUIESCENCE if quiescence is None else quiescence,
        overall_timeout=overall,
    )


def speech(
    session: NativeAppSession,
    *,
    quiescence: float | None = None,
    overall: float = 2.0,
    wait_async: bool = False,
) -> list[str]:
    """Returns the speech captured until the output stream goes quiet."""

    records = _drain(session, quiescence, overall, wait_async)
    return [r.text for r in records if isinstance(r, SpeechRecord)]


def capture(
    session: NativeAppSession,
    *,
    quiescence: float | None = None,
    overall: float = 2.0,
    wait_async: bool = False,
) -> tuple[list[str], list[BrailleLine]]:
    """Returns the (speech, braille) captured until the output stream goes quiet."""

    records = _drain(session, quiescence, overall, wait_async)
    spoken = [r.text for r in records if isinstance(r, SpeechRecord)]
    brailled = [
        BrailleLine(r.cursor_cell, r.full, r.visible, r.mask)
        for r in records
        if isinstance(r, BrailleRecord)
    ]
    return spoken, brailled


def tab_and_swallow_presentation(session: NativeAppSession) -> None:
    """Tabs to the next control and throws away everything Orca presented about it."""

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    session.reader.drain(quiescence_timeout=0.1, overall_timeout=2.0)
    session.reader.reset()


def move_to_top(
    session: NativeAppSession, *, quiescence: float = 0.1, overall: float = 2.0
) -> None:
    """Moves to the top of the document and discards the resulting output."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=quiescence, overall_timeout=overall)
    session.reader.reset()


def move_to_bottom(
    session: NativeAppSession, *, quiescence: float = 0.1, overall: float = 2.0
) -> None:
    """Moves to the bottom of the document and discards the resulting output."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    session.reader.drain(quiescence_timeout=quiescence, overall_timeout=overall)
    session.reader.reset()


def toggle_flat_review(session: NativeAppSession) -> None:
    """Toggles flat review on or off and discards the announcement."""

    keyboard.tap_key(keyboard.KEYSYM_KP_SUBTRACT)
    session.reader.drain(quiescence_timeout=0.1, overall_timeout=2.0)
    session.reader.reset()


@contextlib.contextmanager
def bound_pan_keys(session: NativeAppSession) -> Iterator[tuple[str, str]]:
    """Binds pan-left/right to two free Orca keys for the block, yielding (left, right) keysyms."""

    (left_key, left_mods), (right_key, right_mods) = session.orca.available_keybindings(2)
    session.orca.bind_command(PAN_LEFT_COMMAND, left_key, left_mods)
    session.orca.bind_command(PAN_RIGHT_COMMAND, right_key, right_mods)
    session.orca.refresh_keybindings()
    try:
        yield left_key, right_key
    finally:
        session.orca.unbind_command(PAN_LEFT_COMMAND)
        session.orca.unbind_command(PAN_RIGHT_COMMAND)
        session.orca.refresh_keybindings()


def reset_web_state(session: NativeAppSession, *, web_app: bool = False) -> None:
    """Resets settings, focus mode, and caret position to give a web test a known baseline."""

    # Setting the active profile clears all runtime overrides back to their defaults.
    session.orca.set("ProfileManager", "ActiveProfile", "default")

    if not web_app:
        # Return to non-sticky browse mode. A user toggle only clears the sticky flag when
        # it actually changes mode, so sticky browse must round-trip through focus mode
        # rather than no-op on "set browse while already browsing".
        if not session.orca.get("DocumentPresenter", "InFocusMode") and session.orca.get(
            "DocumentPresenter", "BrowseModeIsSticky"
        ):
            session.orca.call("DocumentPresenter", "TogglePresentationMode", False)
        if session.orca.get("DocumentPresenter", "InFocusMode"):
            session.orca.call("DocumentPresenter", "TogglePresentationMode", False)

    move_to_top(session)
