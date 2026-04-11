# Orca
#
# Copyright 2025-2026 Igalia, S.L.
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

"""Command classes for Orca's commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from . import input_event, keybindings
    from .scripts import default


class Command:
    """Base class for Orca commands.

    Commands have two independent activity states:

    enabled: User preference for whether this command should be active.
        - Set via user settings or toggle commands (e.g., "toggle caret navigation")
        - Persists across sessions
        - Example: User prefers caret navigation on

    suspended: Temporary system override that deactivates the command.
        - Set by Orca modes (e.g., focus mode suspends browse-mode commands)
        - Does NOT change the user's enabled preference
        - When suspension is lifted, command returns to its enabled state
        - Example: Focus mode suspends structural navigation; leaving focus
          mode automatically restores it
    """

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        name: str,
        function: Callable[..., bool],
        group_label: str,
        description: str = "",
        enabled: bool = True,
        suspended: bool = False,
    ) -> None:
        """Initializes a command."""

        self._name = name
        self._function = function
        self._group_label = group_label
        self._description = description
        self._enabled = enabled
        self._suspended = suspended

    def __str__(self) -> str:
        """Returns a string representation of the command."""

        parts = [f"Command({self._name})"]
        if self._suspended:
            parts.append("SUSPENDED")
        return " ".join(parts)

    def get_name(self) -> str:
        """Returns the command name."""

        return self._name

    def get_function(self) -> Callable[..., bool]:
        """Returns the command function."""

        return self._function

    def set_function(self, function: Callable[..., bool]) -> None:
        """Sets the command function."""

        self._function = function

    def get_group_label(self) -> str:
        """Returns the group label for display grouping."""

        return self._group_label

    def get_description(self) -> str:
        """Returns the command description."""

        return self._description

    def set_group_label(self, group_label: str) -> None:
        """Sets the group label."""

        self._group_label = group_label

    def is_enabled(self) -> bool:
        """Returns True if the user has enabled this command."""

        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        """Sets whether the user has enabled this command."""

        self._enabled = enabled

    def is_suspended(self) -> bool:
        """Returns True if this command is temporarily suspended by the system."""

        return self._suspended

    def set_suspended(self, suspended: bool) -> None:
        """Sets whether this command is temporarily suspended by the system."""

        self._suspended = suspended

    def execute(self, script: default.Script, event: input_event.InputEvent | None = None) -> bool:
        """Executes this command's function and returns True if handled."""

        return self._function(script, event)


class KeyboardCommand(Command):  # pylint: disable=too-many-instance-attributes
    """A command that can be bound to keyboard keys."""

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        name: str,
        function: Callable[..., bool],
        group_label: str,
        description: str = "",
        desktop_keybinding: keybindings.KeyBinding | None = None,
        laptop_keybinding: keybindings.KeyBinding | None = None,
        enabled: bool = True,
        suspended: bool = False,
        is_group_toggle: bool = False,
    ) -> None:
        """Initializes a keyboard command."""

        super().__init__(name, function, group_label, description, enabled, suspended)

        # The default bindings.
        self._desktop_keybinding = desktop_keybinding
        self._laptop_keybinding = laptop_keybinding

        # The actual binding, taking into account user overrides.
        self._keybinding: keybindings.KeyBinding | None = None
        self._is_group_toggle = is_group_toggle

    def __str__(self) -> str:
        """Returns a string representation of the command."""

        parts = [f"KeyboardCommand({self._name})"]
        if self._keybinding:
            parts.append(str(self._keybinding))
        else:
            parts.append("UNBOUND")
        if self._suspended:
            parts.append("SUSPENDED")
        return " ".join(parts)

    def get_keybinding(self) -> keybindings.KeyBinding | None:
        """Returns the current key binding, or None if unbound."""

        return self._keybinding

    def get_default_keybinding(self, is_desktop: bool) -> keybindings.KeyBinding | None:
        """Returns the default key binding for the specified layout."""

        return self._desktop_keybinding if is_desktop else self._laptop_keybinding

    def has_default_keybinding(self) -> bool:
        """Returns True if this command has a default keybinding for either layout."""

        return self._desktop_keybinding is not None or self._laptop_keybinding is not None

    def set_keybinding(self, keybinding: keybindings.KeyBinding | None) -> None:
        """Sets the current key binding."""

        self._keybinding = keybinding

    def is_group_toggle(self) -> bool:
        """Returns True if this command toggles its group's enabled state."""

        return self._is_group_toggle

    def is_active(self) -> bool:
        """Returns True if this command should respond to key events."""

        return self._enabled and not self._suspended and self._keybinding is not None


class BrailleCommand(Command):
    """A command that can only be triggered by braille hardware."""

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        name: str,
        function: Callable[..., bool],
        group_label: str,
        description: str = "",
        enabled: bool = True,
        suspended: bool = False,
        braille_bindings: tuple[int, ...] = (),
        executes_in_learn_mode: bool = False,
    ) -> None:
        """Initializes a braille command."""

        super().__init__(name, function, group_label, description, enabled, suspended)
        self._braille_bindings = braille_bindings
        self._executes_in_learn_mode = executes_in_learn_mode

    def __str__(self) -> str:
        """Returns a string representation of the command."""

        parts = [f"BrailleCommand({self._name})"]
        if self._braille_bindings:
            parts.append(f"braille={self._braille_bindings}")
        if self._suspended:
            parts.append("SUSPENDED")
        return " ".join(parts)

    def get_braille_bindings(self) -> tuple[int, ...]:
        """Returns the braille bindings (BrlAPI key codes)."""

        return self._braille_bindings

    def executes_in_learn_mode(self) -> bool:
        """Returns True if this command should execute in learn mode (e.g., pan commands)."""

        return self._executes_in_learn_mode
