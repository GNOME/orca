# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

"""Command definitions for profiles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .profile_manager import ProfileManager


def get_commands(owner: ProfileManager) -> list[Command]:
    """Returns commands for profiles."""

    return [
        KeyboardCommand(
            "cycleSettingsProfileHandler",
            owner.cycle_settings_profile,
            owner.GROUP_LABEL,
            cmdnames.CYCLE_SETTINGS_PROFILE,
        ),
        KeyboardCommand(
            "presentCurrentProfileHandler",
            owner.present_current_profile,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_CURRENT_PROFILE,
        ),
    ]
