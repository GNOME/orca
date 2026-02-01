# Orca
#
# Copyright 2024 Igalia, S.L.
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

# pylint: disable=wrong-import-position

"""Module for sleep mode"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


from typing import TYPE_CHECKING

from . import braille
from . import cmdnames
from . import command_manager
from . import dbus_service
from . import debug
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import script_manager
from .ax_object import AXObject

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class SleepModeManager:
    """Provides sleep mode implementation."""

    COMMAND_NAME = "toggle_sleep_mode"

    def __init__(self) -> None:
        self._apps: list[int] = []
        self._initialized: bool = False

        msg = "SLEEP MODE MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SleepModeManager", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_SLEEP_MODE
        kb = keybindings.KeyBinding("q", keybindings.SHIFT_ALT_CTRL_MODIFIER_MASK)

        manager.add_command(
            command_manager.KeyboardCommand(
                self.COMMAND_NAME,
                self.toggle_sleep_mode,
                group_label,
                cmdnames.TOGGLE_SLEEP_MODE,
                desktop_keybinding=kb,
                laptop_keybinding=kb,
            )
        )

        msg = "SLEEP MODE MANAGER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def is_active_for_app(self, app: Atspi.Accessible) -> bool:
        """Returns True if sleep mode is active for app."""

        result = bool(app and hash(app) in self._apps)
        if result:
            tokens = ["SLEEP MODE MANAGER: Is active for", app]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

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
            self._apps.remove(hash(script.app))
            new_script = _script_manager.get_script(script.app)
            if notify_user:
                new_script.present_message(
                    messages.SLEEP_MODE_DISABLED_FOR % AXObject.get_name(script.app)
                )
            _script_manager.set_active_script(new_script, "Sleep mode toggled off")
            return True

        braille.clear()
        if notify_user:
            script.present_message(messages.SLEEP_MODE_ENABLED_FOR % AXObject.get_name(script.app))
        _script_manager.set_active_script(
            _script_manager.get_or_create_sleep_mode_script(script.app), "Sleep mode toggled on"
        )
        self._apps.append(hash(script.app))
        return True


_manager: SleepModeManager = SleepModeManager()


def get_manager() -> SleepModeManager:
    """Returns the Sleep Mode Manager singleton."""
    return _manager
