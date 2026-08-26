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

"""Helpers for the caret navigator's text-selection commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

NEXT_CHARACTER = "SelectNextCharacterForTesting"
PREVIOUS_CHARACTER = "SelectPreviousCharacterForTesting"
NEXT_WORD = "SelectNextWordForTesting"
PREVIOUS_WORD = "SelectPreviousWordForTesting"
NEXT_LINE = "SelectNextLineForTesting"
PREVIOUS_LINE = "SelectPreviousLineForTesting"
START_OF_LINE = "SelectStartOfLineForTesting"
END_OF_LINE = "SelectEndOfLineForTesting"
START_OF_FILE = "SelectStartOfFileForTesting"
END_OF_FILE = "SelectEndOfFileForTesting"


def select(session: NativeAppSession, command: str) -> tuple[list[str], BrailleLine]:
    """Runs a selection command and returns its speech and its settled braille line."""

    session.orca.select_with_caret_navigator(command)
    spoken, brailled = capture(session)
    return spoken, brailled[-1]


def select_without_notifying(session: NativeAppSession, command: str) -> tuple[list[str], list]:
    """Runs a selection command which is not meant to present anything to the user."""

    session.orca.select_with_caret_navigator(command, notify_user=False)
    return capture(session)
