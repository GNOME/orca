# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

"""Command definitions for debugging tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .debugging_tools_manager import DebuggingToolsManager


def get_commands(owner: DebuggingToolsManager) -> list[Command]:
    """Returns commands for debugging tools."""

    return [
        KeyboardCommand(
            "cycleDebugLevelHandler",
            owner._cycle_debug_level,  # pylint: disable=protected-access
            owner.GROUP_LABEL,
            cmdnames.DEBUG_CYCLE_LEVEL,
        ),
        KeyboardCommand(
            "clear_atspi_app_cache",
            owner._clear_atspi_app_cache,  # pylint: disable=protected-access
            owner.GROUP_LABEL,
            cmdnames.DEBUG_CLEAR_ATSPI_CACHE_FOR_APPLICATION,
        ),
    ]
