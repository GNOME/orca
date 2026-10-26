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

"""Tests presenting and reviewing notifications sent with notify-send."""

from __future__ import annotations

import contextlib
import re
import subprocess
from typing import TYPE_CHECKING

import pytest

from .helpers import BrailleLine, capture, speech

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .orca_fixtures import NativeAppSession

_COMMANDS = (
    "present_last_notification",
    "present_previous_notification",
    "present_next_notification",
    "show_notification_list",
)

_AGE = re.compile(r" (1 second|([02-9]|\d{2,}) seconds) ago$")


def _send_notification(summary: str, body: str) -> None:
    # notification-daemon shows one notification at a time, so a short expiry lets the
    # next one appear sooner.
    subprocess.run(["notify-send", "--expire-time=1000", summary, body], check=True)


def _speech_without_age(session: NativeAppSession) -> list[str]:
    """Returns the speech with how long ago the notification arrived removed."""

    spoken = speech(session)
    text, count = _AGE.subn("", spoken[-1])
    assert count == 1, spoken
    return [*spoken[:-1], text]


@contextlib.contextmanager
def _bound_commands(session: NativeAppSession) -> Iterator[tuple[str, ...]]:
    """Binds the notification commands to free keys for the block, yielding the keys."""

    keybindings = session.orca.available_keybindings(len(_COMMANDS))
    for command, (key, modifiers) in zip(_COMMANDS, keybindings, strict=True):
        session.orca.bind_command(command, key, modifiers)
    session.orca.refresh_keybindings()
    try:
        yield tuple(key for key, _modifiers in keybindings)
    finally:
        for command in _COMMANDS:
            session.orca.unbind_command(command)
        session.orca.refresh_keybindings()


@pytest.mark.native_app
def test_sending_notification(notification_daemon: NativeAppSession) -> None:
    """Tests sending a notification."""

    session = notification_daemon
    _send_notification("Meeting", "Starts in five minutes")
    spoken, brailled = capture(session, wait_async=True)
    assert spoken == ["Notification Meeting Starts in five minutes"]
    assert brailled[-1] == BrailleLine(
        0,
        "Notification Meeting Starts in five minutes",
        "Notification Meeting Starts in f",
        "\x00" * 43,
    )


@pytest.mark.native_app
def test_reviewing_notifications(notification_daemon: NativeAppSession) -> None:
    """Tests reviewing notifications."""

    session = notification_daemon
    _send_notification("Meeting", "Starts in five minutes")
    assert speech(session, wait_async=True) == ["Notification Meeting Starts in five minutes"]
    _send_notification("Build", "Finished")
    assert speech(session, wait_async=True, overall=5.0) == ["Notification Build Finished"]

    with _bound_commands(session) as (last_key, previous_key, next_key, _list_key):
        session.orca.press_bound_key(last_key)
        assert _speech_without_age(session) == ["Notification Build Finished"]
        session.orca.press_bound_key(previous_key)
        assert _speech_without_age(session) == ["Notification Meeting Starts in five minutes"]
        session.orca.press_bound_key(previous_key)
        assert _speech_without_age(session) == [
            "Top",
            "Notification Meeting Starts in five minutes",
        ]
        session.orca.press_bound_key(next_key)
        assert _speech_without_age(session) == ["Notification Build Finished"]
        session.orca.press_bound_key(next_key)
        assert _speech_without_age(session) == ["Bottom", "Notification Build Finished"]


@pytest.mark.native_app
def test_reviewing_with_no_notifications(notification_daemon: NativeAppSession) -> None:
    """Tests reviewing with no notifications."""

    session = notification_daemon
    with _bound_commands(session) as keys:
        for key in keys:
            session.orca.press_bound_key(key)
            spoken, brailled = capture(session)
            assert spoken == ["No notification messages"]
            assert brailled[-1] == BrailleLine(
                0, "No notification messages", "No notification messages", "\x00" * 24
            )
