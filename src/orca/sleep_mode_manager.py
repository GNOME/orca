# Orca
#
# Copyright 2024-2026 Igalia, S.L.
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

"""Module for sleep mode"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from . import (
    cmdnames,
    dbus_service,
    debug,
    gsettings_registry,
    guilabels,
    input_event,
    keybindings,
    messages,
    presentation_manager,
    script_manager,
)
from .ax_object import AXObject
from .ax_utilities import AXUtilities
from .command import Command, KeyboardCommand
from .extension import Extension

if TYPE_CHECKING:
    from gi.repository import Atspi

    from .scripts import default
    from .sleep_mode_manager_preferences_grid import SleepModePreferencesGrid


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.SleepMode",
    name="sleep-mode",
)
class SleepModeManager(Extension):
    """Provides sleep mode implementation."""

    GROUP_LABEL = guilabels.KB_GROUP_SLEEP_MODE
    COMMAND_NAME = "toggle_sleep_mode"
    _SCHEMA = "sleep-mode"

    def __init__(self) -> None:
        self._apps: list[int] = []
        self._runtime_exceptions: set[str] = set()
        super().__init__()

    def _get_commands(self) -> list[Command]:
        """Returns commands for registration."""

        kb = keybindings.KeyBinding("q", keybindings.SHIFT_ALT_CTRL_MODIFIER_MASK)

        return [
            KeyboardCommand(
                self.COMMAND_NAME,
                self.toggle_sleep_mode,
                self.GROUP_LABEL,
                cmdnames.TOGGLE_SLEEP_MODE,
                desktop_keybinding=kb,
                laptop_keybinding=kb,
            ),
        ]

    def _is_on_persistent_list(self, app: Atspi.Accessible) -> bool:
        """Returns True if the app is on the persistent sleep mode list."""

        app_name = AXObject.get_name(app)
        if not app_name:
            return False
        return app_name in self.get_sleep_mode_apps()

    def is_active_for_app(self, app: Atspi.Accessible) -> bool:
        """Returns True if sleep mode is active for app."""

        if not app:
            return False

        app_name = AXObject.get_name(app)
        if app_name in self._runtime_exceptions:
            tokens = ["SLEEP MODE MANAGER: Skipping (runtime exception for", app, ")"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if hash(app) in self._apps:
            tokens = ["SLEEP MODE MANAGER: Is active for", app, "(runtime toggle)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if self._is_on_persistent_list(app):
            tokens = ["SLEEP MODE MANAGER: Is active for", app, "(persistent setting)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def on_app_deactivated(self, app: Atspi.Accessible) -> None:
        """Clears any runtime exception so persistent sleep re-engages on return."""

        app_name = AXObject.get_name(app)
        if app_name and app_name in self._runtime_exceptions:
            self._runtime_exceptions.discard(app_name)
            tokens = ["SLEEP MODE MANAGER: Cleared runtime exception for", app]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    @gsettings_registry.get_registry().gsetting(
        key="apps",
        schema="sleep-mode",
        gtype="as",
        default=[],
        summary="Applications that automatically use sleep mode",
    )
    @dbus_service.getter
    def get_sleep_mode_apps(self) -> list[str]:
        """Returns the list of apps that should automatically use sleep mode."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            "apps",
            "as",
            default=[],
        )

    @dbus_service.setter
    def set_sleep_mode_apps(self, apps: list[str]) -> bool:
        """Sets the list of apps that should automatically use sleep mode."""

        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "apps",
            apps,
        )
        return True

    def get_running_app_names(self) -> list[str]:
        """Returns sorted names of running applications with windows, excluding Orca."""

        orca_pid = os.getpid()
        names: set[str] = set()
        for app in AXUtilities.get_all_applications(must_have_window=True):
            if AXUtilities.get_process_id(app) == orca_pid:
                continue
            name = AXObject.get_name(app)
            if name:
                names.add(name)
        return sorted(names)

    def create_preferences_grid(self) -> SleepModePreferencesGrid:
        """Returns the preferences grid for sleep mode settings."""

        # pylint: disable-next=import-outside-toplevel
        from .sleep_mode_manager_preferences_grid import SleepModePreferencesGrid

        return SleepModePreferencesGrid(self)

    @dbus_service.command
    def toggle_sleep_mode(
        self,
        script: default.Script | None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles sleep mode for the active application."""

        tokens = [
            "SLEEP MODE MANAGER: toggle_sleep_mode. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (script and script.app):
            return True

        _script_manager = script_manager.get_manager()
        if self.is_active_for_app(script.app):
            app_name = AXObject.get_name(script.app)
            if hash(script.app) in self._apps:
                self._apps.remove(hash(script.app))
            if self._is_on_persistent_list(script.app) and app_name:
                self._runtime_exceptions.add(app_name)
            new_script = _script_manager.get_script(script.app)
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.SLEEP_MODE_DISABLED_FOR % app_name,
                )
            _script_manager.set_active_script(new_script, "Sleep mode toggled off")
            return True

        if notify_user:
            msg = messages.SLEEP_MODE_ENABLED_FOR % AXObject.get_name(script.app)
            manager = presentation_manager.get_manager()
            manager.speak_message(msg)

            # Don't restore previous braille content because Orca is no longer active.
            manager.present_braille_message(msg, restore_previous=False)
        _script_manager.set_active_script(
            _script_manager.get_or_create_sleep_mode_script(script.app),  # type: ignore[arg-type]
            "Sleep mode toggled on",
        )
        self._apps.append(hash(script.app))
        return True


_manager: SleepModeManager = SleepModeManager()


def get_manager() -> SleepModeManager:
    """Returns the Sleep Mode Manager singleton."""
    return _manager
