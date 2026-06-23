# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

"""Command definitions for screen reader management."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .screen_reader_manager import ScreenReaderManager


def get_commands(owner: ScreenReaderManager) -> list[Command]:
    """Returns commands for screen reader management."""

    kb_orca_space = keybindings.KeyBinding("space", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_control_space = keybindings.KeyBinding(
        "space",
        keybindings.ORCA_CTRL_MODIFIER_MASK,
    )

    return [
        KeyboardCommand(
            "shutdownHandler",
            owner.quit,
            owner.GROUP_LABEL,
            cmdnames.QUIT_ORCA,
        ),
        KeyboardCommand(
            "preferencesSettingsHandler",
            owner.show_preferences_gui,
            owner.GROUP_LABEL,
            cmdnames.SHOW_PREFERENCES_GUI,
            desktop_keybinding=kb_orca_space,
            laptop_keybinding=kb_orca_space,
        ),
        KeyboardCommand(
            "appPreferencesSettingsHandler",
            owner.show_app_preferences_gui,
            owner.GROUP_LABEL,
            cmdnames.SHOW_APP_PREFERENCES_GUI,
            desktop_keybinding=kb_orca_control_space,
            laptop_keybinding=kb_orca_control_space,
        ),
    ]
