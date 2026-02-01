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

"""Provides means to pass keyboard events to the app being used."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


from typing import TYPE_CHECKING

from . import cmdnames
from . import command_manager
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import orca_modifier_manager

if TYPE_CHECKING:
    from .scripts import default


class BypassModeManager:
    """Provides means to pass keyboard events to the app being used."""

    COMMAND_NAME = "bypass_mode_toggle"

    def __init__(self) -> None:
        self._is_active: bool = False
        self._initialized: bool = False
        self._saved_commands: dict[str, command_manager.KeyboardCommand] = {}

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_DEFAULT
        kb = keybindings.KeyBinding("BackSpace", keybindings.ALT_MODIFIER_MASK)

        manager.add_command(
            command_manager.KeyboardCommand(
                self.COMMAND_NAME,
                self.toggle_enabled,
                group_label,
                cmdnames.BYPASS_MODE_TOGGLE,
                desktop_keybinding=kb,
                laptop_keybinding=kb,
            )
        )

    def is_active(self) -> bool:
        """Returns True if bypass mode is active."""

        return self._is_active

    def toggle_enabled(
        self, script: default.Script, event: input_event.InputEvent | None = None
    ) -> bool:
        """Toggles bypass mode."""

        self._is_active = not self._is_active
        manager = command_manager.get_manager()
        if not self._is_active:
            if event is not None:
                script.present_message(messages.BYPASS_MODE_DISABLED)
            reason = "bypass mode disabled"
            manager.set_active_commands(self._saved_commands, reason)
            orca_modifier_manager.get_manager().refresh_orca_modifiers(reason)
            return True

        if event is not None:
            script.present_message(messages.BYPASS_MODE_ENABLED)

        reason = "bypass mode enabled"
        self._saved_commands = manager.get_keyboard_commands()
        bypass_cmd = manager.get_keyboard_command(self.COMMAND_NAME)
        bypass_commands = {self.COMMAND_NAME: bypass_cmd} if bypass_cmd else {}
        manager.set_active_commands(bypass_commands, reason)
        orca_modifier_manager.get_manager().unset_orca_modifiers(reason)

        return True


_manager: BypassModeManager = BypassModeManager()


def get_manager() -> BypassModeManager:
    """Returns the bypass-mode-manager singleton."""

    return _manager
