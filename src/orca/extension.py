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

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from . import command_manager, dbus_service, debug, gsettings_registry

if TYPE_CHECKING:
    from .command import Command


@dataclass(frozen=True)
class SpeechOutput:
    """Text Orca is about to send to the active speech provider."""

    text: str
    obj: Any | None = None


@dataclass(frozen=True)
class SpeechOutputResult:
    """Result returned by an extension speech-output hook."""

    text: str | None = None
    consume: bool = False

    @classmethod
    def replace(cls, text: str) -> SpeechOutputResult:
        """Returns a result that replaces the text Orca will speak."""

        return cls(text=text)

    @classmethod
    def consume_output(cls) -> SpeechOutputResult:
        """Returns a result indicating that the extension handled speech output."""

        return cls(consume=True)


class ExtensionSettings:
    """Settings scoped to one extension."""

    _SCHEMA = "extensions"
    _KEY = "settings"
    _SETTING_NAME = re.compile(r"^[A-Za-z0-9_.-]+$")

    def __init__(self, namespace: str) -> None:
        self._namespace = self._sanitize_namespace(namespace)

    @staticmethod
    def _sanitize_namespace(namespace: str) -> str:
        """Return a stable namespace for settings keys."""

        sanitized = gsettings_registry.GSettingsRegistry.sanitize_gsettings_path(namespace)
        return sanitized or "extension"

    def set_namespace(self, namespace: str) -> None:
        """Set the namespace used to store this extension's settings."""

        self._namespace = self._sanitize_namespace(namespace)

    def _sub_path(self) -> str:
        """Return the relocatable settings path for this extension."""

        return f"extensions/{self._namespace}"

    def _validate_key(self, key: str) -> str:
        """Return the storage key if it is valid."""

        if not key or not self._SETTING_NAME.fullmatch(key):
            raise ValueError(f"Invalid extension setting key: {key!r}")
        return key

    def _get_local_settings(self) -> dict[str, Any]:
        """Return the active profile's extension settings."""

        registry = gsettings_registry.get_registry()
        gs = registry.get_settings(
            self._SCHEMA,
            registry.get_active_profile(),
            self._sub_path(),
        )
        if gs is None:
            return {}
        variant = gs.get_user_value(self._KEY)
        if variant is None:
            return {}
        return dict(variant.unpack())

    def get(self, key: str, default: Any = None) -> Any:
        """Return a setting value using Orca's layered settings lookup."""

        settings = gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self._KEY,
            "a{sv}",
            sub_path=self._sub_path(),
            default={},
        )
        return settings.get(self._validate_key(key), default)

    def set(self, key: str, value: Any) -> bool:
        """Persist a setting value in the active profile."""

        settings = self._get_local_settings()
        settings[self._validate_key(key)] = value
        return gsettings_registry.get_registry().set_dict(
            self._SCHEMA,
            self._KEY,
            "a{sv}",
            settings,
            sub_path=self._sub_path(),
        )

    def reset(self, key: str) -> bool:
        """Remove a setting value from the active profile."""

        settings = self._get_local_settings()
        settings.pop(self._validate_key(key), None)
        return gsettings_registry.get_registry().set_dict(
            self._SCHEMA,
            self._KEY,
            "a{sv}",
            settings,
            sub_path=self._sub_path(),
        )


class Extension:
    """Base class for Orca extensions."""

    GROUP_LABEL: ClassVar[str]
    DESCRIPTION: ClassVar[str] = ""
    VERSION: ClassVar[str] = ""
    AUTHOR: ClassVar[str] = ""
    ORGANIZATION: ClassVar[str] = ""
    COPYRIGHT: ClassVar[str] = ""
    WEBSITE: ClassVar[str] = ""

    def __init__(self) -> None:
        self._commands_initialized: bool = False
        self._is_user_extension: bool = False
        self._disabled: bool = False
        self._registered_command_names: list[str] = []
        self.module_name: str = type(self).__name__
        self.settings = ExtensionSettings(self.module_name)
        self.controller = dbus_service.get_remote_controller()
        msg = f"EXTENSION: {self.module_name} Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.controller.register_decorated_module(self.module_name, self)

    def disable(self) -> None:
        """Disables this extension, preventing command registration."""

        self._disabled = True
        msg = f"EXTENSION: {self.module_name} has been disabled."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        manager = command_manager.get_manager()
        manager.remove_commands(
            self._registered_command_names,
            f"disabled extension {self.module_name}",
        )
        self._registered_command_names.clear()
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
            self._registered_command_names.append(cmd.get_name())

        msg = f"EXTENSION: {self.module_name} {len(commands)} command(s) registered."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def mark_as_user_extension(self, settings_namespace: str | None = None) -> None:
        """Marks this extension as user-provided so commands get wrapped."""

        self._is_user_extension = True
        command_manager.get_manager().register_user_extension(self)
        if settings_namespace is not None:
            self.settings.set_namespace(settings_namespace)

    def _get_commands(self) -> list[Command]:
        """Override to provide commands for registration."""

        return []

    def on_speech_output(self, output: SpeechOutput) -> SpeechOutputResult | None:
        """Called before Orca sends speech to the active speech provider."""

        return None

    def on_shutdown(self) -> None:
        """Called when Orca is shutting down."""

    @staticmethod
    def _wrap_function(func):
        """Wraps a user extension method so it accepts and discards script and event."""

        def wrapper(_script, _event):
            return func()

        return wrapper
