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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from . import braille
from . import cmdnames
from . import dbus_service
from . import debug
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

    def __init__(self) -> None:
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._apps: list[int] = []

        msg = "SLEEP MODE MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SleepModeManager", self)

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the sleep-mode-manager keybindings."""

        if refresh:
            msg = f"SLEEP MODE MANAGER: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("SLEEP MODE MANAGER: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the sleep-mode-manager handlers."""

        if refresh:
            msg = "SLEEP MODE MANAGER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def is_active_for_app(self, app: Atspi.Accessible) -> bool:
        """Returns True if sleep mode is active for app."""

        result = bool(app and hash(app) in self._apps)
        if result:
            tokens = ["SLEEP MODE MANAGER: Is active for", app]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _setup_handlers(self) -> None:
        """Sets up and returns the sleep-mode-manager input event handlers."""

        self._handlers = {}

        self._handlers["toggle_sleep_mode"] = \
            input_event.InputEventHandler(
                self.toggle_sleep_mode,
                cmdnames.TOGGLE_SLEEP_MODE)

        msg = "SLEEP MODE MANAGER: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self) -> None:
        """Sets up and returns the sleep-mode-manager key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "q",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_CTRL_MODIFIER_MASK,
                self._handlers["toggle_sleep_mode"]))

        msg = "SLEEP MODE MANAGER: Bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    @dbus_service.command
    def toggle_sleep_mode(
        self,
        script: default.Script | None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles sleep mode for the active application."""

        tokens = ["SLEEP MODE MANAGER: toggle_sleep_mode. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (script and script.app):
            return True

        _script_manager = script_manager.get_manager()
        if self.is_active_for_app(script.app):
            self._apps.remove(hash(script.app))
            new_script = _script_manager.get_script(script.app)
            if notify_user:
                new_script.present_message(
                    messages.SLEEP_MODE_DISABLED_FOR % AXObject.get_name(script.app))
            _script_manager.set_active_script(new_script, "Sleep mode toggled off")
            return True

        braille.clear()
        if notify_user:
            script.present_message(messages.SLEEP_MODE_ENABLED_FOR % AXObject.get_name(script.app))
        _script_manager.set_active_script(
            _script_manager.get_or_create_sleep_mode_script(script.app), "Sleep mode toggled on")
        self._apps.append(hash(script.app))
        return True


_manager: SleepModeManager = SleepModeManager()

def get_manager() -> SleepModeManager:
    """Returns the Sleep Mode Manager singleton."""
    return _manager
