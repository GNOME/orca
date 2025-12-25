# Orca
#
# Copyright 2025 Igalia, S.L.
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

"""Manager for script commands and keybindings."""

from __future__ import annotations

__id__ = "$Id$"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2025 Igalia, S.L."
__license__ = "LGPL"

from typing import Any

from . import input_event
from . import keybindings


class Command:
    """Represents an Orca command with its handler and optional key binding."""

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        handler_name: str,
        handler: input_event.InputEventHandler,
        group_label: str,
        description: str = "",
        keybinding: keybindings.KeyBinding | None = None,
        learn_mode_enabled: bool = True
    ) -> None:
        """Initializes a command."""

        self._handler_name = handler_name
        self._handler = handler
        self._group_label = group_label
        self._description = description
        self._default_keybinding = keybinding
        self._keybinding = keybinding
        self._learn_mode_enabled = learn_mode_enabled

    def get_handler_name(self) -> str:
        """Returns the handler name."""

        return self._handler_name

    def get_handler(self) -> input_event.InputEventHandler:
        """Returns the input event handler."""

        return self._handler

    def get_group_label(self) -> str:
        """Returns the group label for display grouping."""

        return self._group_label

    def get_description(self) -> str:
        """Returns the command description."""

        return self._description

    def get_keybinding(self) -> keybindings.KeyBinding | None:
        """Returns the current key binding, or None if unbound."""

        return self._keybinding

    def get_default_keybinding(self) -> keybindings.KeyBinding | None:
        """Returns the default (uncustomized) key binding, or None if unbound by default."""

        return self._default_keybinding

    def get_learn_mode_enabled(self) -> bool:
        """Returns whether this command is enabled in learn mode."""

        return self._learn_mode_enabled

    def set_keybinding(self, keybinding: keybindings.KeyBinding | None) -> None:
        """Sets the current key binding."""

        self._keybinding = keybinding

    def set_default_keybinding(self, keybinding: keybindings.KeyBinding | None) -> None:
        """Sets the default (uncustomized) key binding."""

        self._default_keybinding = keybinding

    def set_group_label(self, group_label: str) -> None:
        """Sets the group label."""

        self._group_label = group_label

    def set_learn_mode_enabled(self, enabled: bool) -> None:
        """Sets whether this command is enabled in learn mode."""

        self._learn_mode_enabled = enabled


class CommandManager:
    """Singleton manager for coordinating commands between scripts and UI."""

    def __init__(self) -> None:
        """Initializes the command manager."""

        self._commands_by_name: dict[str, Command] = {}

    def add_command(self, command: Command) -> None:
        """Adds a command to the registry."""

        self._commands_by_name[command.get_handler_name()] = command

    def get_command(self, handler_name: str) -> Command | None:
        """Returns the command with the specified handler name, or None."""

        return self._commands_by_name.get(handler_name)

    def get_all_commands(self) -> tuple[Command, ...]:
        """Returns all registered commands."""

        return tuple(self._commands_by_name.values())

    def get_commands_by_group_label(self, group_label: str) -> tuple[Command, ...]:
        """Returns all commands with the specified group label."""

        return tuple(
            cmd for cmd in self._commands_by_name.values()
            if cmd.get_group_label() == group_label
        )

    def clear_commands(self) -> None:
        """Removes all commands from the registry."""

        self._commands_by_name.clear()

    def set_default_bindings_from_module(
        self,
        handlers: dict[str, input_event.InputEventHandler],
        module_bindings: keybindings.KeyBindings,
        skip_handlers: frozenset[str]
    ) -> None:
        """Sets default keybindings on Commands from module bindings before user customization."""

        for kb in module_bindings.key_bindings:
            for name, handler in handlers.items():
                if name in skip_handlers:
                    continue
                if handler.function == kb.handler.function:
                    if cmd := self.get_command(name):
                        if cmd.get_default_keybinding() is None:
                            cmd.set_default_keybinding(kb)
                            cmd.set_keybinding(kb)
                    break

    def clear_deleted_bindings(
        self,
        handlers: dict[str, input_event.InputEventHandler],
        profile_keybindings: dict[str, Any],
        skip_handlers: frozenset[str]
    ) -> None:
        """Clears keybindings for handlers explicitly unbound in profile settings."""

        for name in handlers:
            if name in skip_handlers:
                continue
            if name in profile_keybindings:
                if profile_keybindings[name] == []:
                    if cmd := self.get_command(name):
                        cmd.set_keybinding(None)

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def apply_customized_bindings(
        self,
        handlers: dict[str, input_event.InputEventHandler],
        customized: keybindings.KeyBindings,
        group_label: str,
        skip_handlers: frozenset[str],
        update_group_label: bool = True
    ) -> None:
        """Updates or adds Commands from customized keybindings."""

        for kb in customized.key_bindings:
            for name, handler in handlers.items():
                if name in skip_handlers:
                    continue
                if handler.function == kb.handler.function:
                    if cmd := self.get_command(name):
                        cmd.set_keybinding(kb)
                        if group_label and update_group_label:
                            cmd.set_group_label(group_label)
                    else:
                        self.add_command(Command(
                            name, handler, group_label, handler.description,
                            kb, handler.learn_mode_enabled))
                    break


_manager: CommandManager = CommandManager()


def get_manager() -> CommandManager:
    """Returns the CommandManager singleton."""

    return _manager
