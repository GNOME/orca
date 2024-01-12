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

"""Module for sleep mode"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L."
__license__   = "LGPL"

from . import cmdnames
from . import debug
from . import input_event
from . import keybindings
from . import messages
from . import script_manager
from .ax_object import AXObject


class SleepModeManager:
    """Provides sleep mode implementation."""

    def __init__(self):
        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()
        self._apps = []

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the sleep-mode-manager keybindings."""

        if refresh:
            msg = "SLEEP MODE MANAGER: Refreshing bindings."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif self._bindings.isEmpty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the sleep-mode-manager handlers."""

        if refresh:
            msg = "SLEEP MODE MANAGER: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def is_active_for_app(self, app):
        """Returns True if sleep mode is active for app."""

        result = app and hash(app) in self._apps
        if result:
            tokens = ["SLEEP MODE MANAGER: Is active for", app]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _setup_handlers(self):
        """Sets up and returns the sleep-mode-manager input event handlers."""

        self._handlers = {}

        self._handlers["toggle_sleep_mode"] = \
            input_event.InputEventHandler(
                self.toggle_sleep_mode,
                cmdnames.TOGGLE_SLEEP_MODE)

        msg = "SLEEP MODE MANAGER: Handlers set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self):
        """Sets up and returns the sleep-mode-manager key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "q",
                keybindings.defaultModifierMask,
                keybindings.SHIFT_ALT_CTRL_MODIFIER_MASK,
                self._handlers.get("toggle_sleep_mode")))

        msg = "SLEEP MODE MANAGER: Bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def toggle_sleep_mode(self, script, event=None):
        """Toggles sleep mode."""

        if not (script and script.app):
            return True

        _script_manager = script_manager.getManager()
        if self.is_active_for_app(script.app):
            self._apps.remove(hash(script.app))
            new_script = _script_manager.getScript(script.app)
            new_script.presentMessage(
                messages.SLEEP_MODE_DISABLED_FOR % AXObject.get_name(script.app))
            _script_manager.setActiveScript(new_script, "Sleep mode toggled off")
            return True

        script.clearBraille()
        script.presentMessage(messages.SLEEP_MODE_ENABLED_FOR % AXObject.get_name(script.app))
        _script_manager.setActiveScript(_script_manager.getOrCreateSleepModeScript(script.app),
                                        "Sleep mode toggled on")
        self._apps.append(hash(script.app))
        return True


_manager = SleepModeManager()
def getManager():
    return _manager
