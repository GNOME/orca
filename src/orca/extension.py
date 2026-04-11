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

"""Base class for Orca extensions."""

from typing import ClassVar

from . import command_manager, dbus_service, debug


class Extension:
    """Base class for Orca modules and extensions."""

    MODULE_NAME: ClassVar[str]
    GROUP_LABEL: ClassVar[str]

    def __init__(self) -> None:
        self._commands_initialized: bool = False
        msg = f"EXTENSION: {self.MODULE_NAME} Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module(self.MODULE_NAME, self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._commands_initialized:
            return
        self._commands_initialized = True
        self._register_commands()

    def _register_commands(self) -> None:
        """Registers the commands returned by _get_commands."""

        commands = self._get_commands()
        if not commands:
            msg = f"EXTENSION: {self.MODULE_NAME} No commands to register."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        manager = command_manager.get_manager()
        for cmd in commands:
            manager.add_command(cmd)

        msg = f"EXTENSION: {self.MODULE_NAME} {len(commands)} command(s) registered."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _get_commands(self) -> list[command_manager.Command]:
        """Override to provide commands for registration."""

        return []
