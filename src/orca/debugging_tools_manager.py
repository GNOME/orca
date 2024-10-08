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

# pylint: disable=wrong-import-position
# pylint: disable=broad-exception-caught

"""Provides debugging tools."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import subprocess
import time

from . import cmdnames
from . import debug
from . import focus_manager
from . import input_event
from . import keybindings
from . import messages
from . import settings_manager
from .ax_object import AXObject
from .ax_utilities import AXUtilities
from .ax_utilities_debugging import AXUtilitiesDebugging

class DebuggingToolsManager:
    """Provides debugging tools."""

    def __init__(self):
        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the debugging-tools-manager keybindings."""

        if refresh:
            msg = f"DEBUGGING TOOLS MANAGER: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the debugging-tools-manager handlers."""

        if refresh:
            msg = "DEBUGGING TOOLS MANAGER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self):
        """Sets up and returns the debugging-tools-manager input event handlers."""

        self._handlers = {}

        self._handlers["cycleDebugLevelHandler"] = \
            input_event.InputEventHandler(
                self._cycle_debug_level,
                cmdnames.DEBUG_CYCLE_LEVEL)

        self._handlers["clear_atspi_app_cache"] = \
            input_event.InputEventHandler(
                self._clear_atspi_app_cache,
                cmdnames.DEBUG_CLEAR_ATSPI_CACHE_FOR_APPLICATION)

        self._handlers["capture_snapshot"] = \
            input_event.InputEventHandler(
                self._capture_snapshot,
                cmdnames.DEBUG_CAPTURE_SNAPSHOT)

    def _setup_bindings(self):
        """Sets up and returns the debugging-tools-manager key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("cycleDebugLevelHandler"),
                1,
                True))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("clear_atspi_app_cache"),
                1,
                True))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("capture_snapshot"),
                1,
                True))

        # This pulls in the user's overrides to alternative keys.
        self._bindings = settings_manager.get_manager().override_key_bindings(
            self._handlers, self._bindings, False)

    def _cycle_debug_level(self, script, _event=None):
        """Cycles through the existing debug levels."""

        levels = {
            debug.LEVEL_ALL: "all",
            debug.LEVEL_INFO: "info",
            debug.LEVEL_WARNING: "warning",
            debug.LEVEL_SEVERE: "severe",
            debug.LEVEL_OFF: "off",
        }

        keys = list(levels.keys())
        next_level = keys.index(debug.debugLevel) + 1
        if next_level == len(keys):
            next_level = 0

        level = keys[next_level]
        brief = levels.get(level)
        debug.debugLevel = level
        script.presentMessage(f"Debug level {brief}.", brief)
        return True

    def _clear_atspi_app_cache(self, script, _event=None):
        """Clears the AT-SPI cache for the current application."""

        _mode, obj = focus_manager.get_manager().get_active_mode_and_object_of_interest()
        if obj is None:
            msg = "DEBUGGING TOOLS MANAGER: Cannot clear cache on null object of interest."
            debug.print_message(debug.debugLevel, msg, True)
            script.presentMessage(messages.DEBUG_CLEAR_CACHE_FAILED)
            return True

        app = AXObject.get_application(obj)
        if app is None:
            msg = "DEBUGGING TOOLS MANAGER: Cannot clear cache on null application."
            debug.print_message(debug.debugLevel, msg, True)
            script.presentMessage(messages.DEBUG_CLEAR_CACHE_FAILED)
            return True

        script.presentMessage(messages.DEBUG_CLEAR_CACHE)
        AXObject.clear_cache(app, recursive=True, reason="User request.")
        return True

    def _capture_snapshot(self, script, _event=None):
        """Clears the AT-SPI cache for the current application."""

        script.presentMessage(messages.DEBUG_CAPTURE_SNAPSHOT_START)

        old_level = debug.debugLevel
        debug.debugLevel = debug.LEVEL_SEVERE
        debug.print_message(debug.debugLevel, "DEBUGGING SNAPSHOT STARTING", True)
        self.print_running_applications()

        manager = settings_manager.get_manager()
        info = AXUtilitiesDebugging.as_string(manager.get_overridden_settings_for_debugging())
        msg = f"OVERRIDDEN SETTINGS: {info}"
        debug.print_message(debug.debugLevel, msg, True)

        info = AXUtilitiesDebugging.as_string(manager.customized_settings)
        msg = f"CUSTOMIZED SETTINGS: {info}"
        debug.print_message(debug.debugLevel, msg, True)

        debug.print_message(debug.debugLevel, "DEBUGGING SNAPSHOT FINISHED", True)
        script.presentMessage(messages.DEBUG_CAPTURE_SNAPSHOT_END)
        debug.debugLevel = old_level
        return True

    def _get_running_applications_as_string_iter(self, is_command_line):
        """Generator providing strings with basic details about the running accessible apps."""

        applications = AXUtilities.get_all_applications(exclude_unresponsive=False)
        msg = f"Desktop has {len(applications)} apps:"
        if not is_command_line:
            msg = f"DEBUGGING TOOLS MANAGER: {msg}"
        yield msg

        for i, app in enumerate(applications):
            pid = AXObject.get_process_id(app)
            if AXUtilities.is_application_unresponsive(app):
                name = "[UNRESPONSIVE]"
            else:
                name = AXObject.get_name(app) or "[DEAD]"
            try:
                cmdline = subprocess.getoutput(f"cat /proc/{pid}/cmdline")
            except Exception as error:
                cmdline = f"EXCEPTION: {error}"
            else:
                cmdline = cmdline.replace("\x00", " ")
            if is_command_line:
                prefix = f"{time.strftime('%H:%M:%S', time.localtime()):<12}"
            else:
                prefix = f"{i+1:3}."

            msg = f"{prefix} pid: {pid:<10} {name:<25} {cmdline}"
            yield msg

    def print_running_applications(self, force=False, is_command_line=False):
        """Prints basic details about the running accessible applications."""

        if force:
            level = debug.LEVEL_SEVERE
        else:
            level = debug.LEVEL_INFO

        if level < debug.debugLevel and not is_command_line:
            return

        for app_string in self._get_running_applications_as_string_iter(is_command_line):
            if is_command_line:
                print(app_string)
            else:
                debug.print_message(level, app_string, True)

_manager = DebuggingToolsManager()
def get_manager():
    """Returns the debugging tools manager."""

    return _manager
