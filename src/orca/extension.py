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

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from . import command_manager, dbus_service, debug

if TYPE_CHECKING:
    from .command import Command


class Extension:
    """Base class for Orca extensions."""

    GROUP_LABEL: ClassVar[str]

    def __init__(self) -> None:
        self._commands_initialized: bool = False
        self._is_user_extension: bool = False
        self._disabled: bool = False
        self.module_name: str = type(self).__name__
        self.controller = dbus_service.get_remote_controller()
        msg = f"EXTENSION: {self.module_name} Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.controller.register_decorated_module(self.module_name, self)

    def disable(self) -> None:
        """Disables this extension, preventing command registration."""

        self._disabled = True
        msg = f"EXTENSION: {self.module_name} has been disabled."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.controller.deregister_module_commands(self.module_name)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._disabled or self._commands_initialized:
            return
        self._commands_initialized = True
        self._register_commands()

    def _register_commands(self) -> None:
        """Registers the commands returned by _get_commands."""

        commands = self._get_commands()
        if not commands:
            msg = f"EXTENSION: {self.module_name} No commands to register."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        manager = command_manager.get_manager()
        for cmd in commands:
            if self._is_user_extension:
                cmd.set_function(self._wrap_function(cmd.get_function()))
            manager.add_command(cmd)

        msg = f"EXTENSION: {self.module_name} {len(commands)} command(s) registered."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def mark_as_user_extension(self) -> None:
        """Marks this extension as user-provided so commands get wrapped."""

        self._is_user_extension = True

    def _get_commands(self) -> list[Command]:
        """Override to provide commands for registration."""

        return []

    @staticmethod
    def _wrap_function(func):
        """Wraps a user extension method so it accepts and discards script and event."""

        def wrapper(_script, _event):
            return func()

        return wrapper
