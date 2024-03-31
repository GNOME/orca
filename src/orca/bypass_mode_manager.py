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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

from . import cmdnames
from . import debug
from . import input_event
from . import keybindings
from . import messages
from . import orca_modifier_manager
from . import settings_manager


class BypassModeManager:
    """Provides means to pass keyboard events to the app being used."""

    def __init__(self):
        self._is_active = False
        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the bypass-mode-manager keybindings."""

        if refresh:
            msg = "BYPASS MODE MANAGER: Refreshing bindings."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the bypass-mode-manager handlers."""

        if refresh:
            msg = "BYPASS MODE MANAGER: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self):
        """Sets up and returns the bypass-mode-manager input event handlers."""

        self._handlers = {}

        self._handlers["bypass_mode_toggle"] = \
            input_event.InputEventHandler(
                self.toggle_enabled,
                cmdnames.BYPASS_MODE_TOGGLE)

    def _setup_bindings(self):
        """Sets up and returns the bypass-mode-manager key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "BackSpace",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ALT_MODIFIER_MASK,
                self._handlers.get("bypass_mode_toggle"),
                1,
                True))

        # This pulls in the user's overrides to alternative keys.
        self._bindings = settings_manager.get_manager().override_key_bindings(
            self._handlers, self._bindings, False)

    def is_active(self):
        """Returns True if bypass mode is active."""

        return self._is_active

    def toggle_enabled(self, script, event=None):
        """Toggles bypass mode."""

        self._is_active = not self._is_active
        if not self._is_active:
            if event is not None:
                script.presentMessage(messages.BYPASS_MODE_DISABLED)
            reason = "bypass mode disabled"
            script.add_key_grabs(reason)
            orca_modifier_manager.get_manager().refresh_orca_modifiers(reason)
            return True

        if event is not None:
            script.presentMessage(messages.BYPASS_MODE_ENABLED)

        reason = "bypass mode enabled"
        script.remove_key_grabs(reason)
        orca_modifier_manager.get_manager().unset_orca_modifiers(reason)
        for binding in self._bindings.key_bindings:
            script.key_bindings.add(binding, include_grabs=True)

        return True

_manager = BypassModeManager()
def get_manager():
    return _manager
