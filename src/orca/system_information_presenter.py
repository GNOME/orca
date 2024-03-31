# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016-2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

"""Module for presenting system information"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

try:
    import psutil
except ModuleNotFoundError:
    psutil = None

import time

from . import cmdnames
from . import debug
from . import input_event
from . import keybindings
from . import messages
from . import settings_manager


class SystemInformationPresenter:
    """Provides commands to present system information."""

    def __init__(self):
        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the system-information-presenter keybindings."""

        if refresh:
            msg = "SYSTEM INFORMATION PRESENTER: Refreshing bindings."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif self._bindings.isEmpty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the system-information-presenter handlers."""

        if refresh:
            msg = "SYSTEM INFORMATION PRESENTER: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self):
        """Sets up the system-information-presenter input event handlers."""

        self._handlers = {}

        self._handlers["presentTimeHandler"] = \
            input_event.InputEventHandler(
                self.present_time,
                cmdnames.PRESENT_CURRENT_TIME)

        self._handlers["presentDateHandler"] = \
            input_event.InputEventHandler(
                self.present_date,
                cmdnames.PRESENT_CURRENT_DATE)

        self._handlers["present_battery_status"] = \
            input_event.InputEventHandler(
                self.present_battery_status,
                cmdnames.PRESENT_BATTERY_STATUS)

        self._handlers["present_cpu_and_memory_usage"] = \
            input_event.InputEventHandler(
                self.present_cpu_and_memory_usage,
                cmdnames.PRESENT_CPU_AND_MEMORY_USAGE)

        msg = "SYSTEM INFORMATION PRESENTER: Handlers set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self):
        """Sets up the system-information-presenter key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("presentTimeHandler"),
                1))

        self._bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("presentDateHandler"),
                2))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("present_battery_status"),
                1))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("present_cpu_and_memory_usage"),
                1))

        msg = "SYSTEM INFORMATION PRESENTER: Bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def present_time(self, script, event=None):
        """Presents the current time."""

        time_format = settings_manager.get_manager().get_setting('presentTimeFormat')
        script.presentMessage(time.strftime(time_format, time.localtime()))
        return True

    def present_date(self, script, event=None):
        """Presents the current date."""

        data_format = settings_manager.get_manager().get_setting('presentDateFormat')
        script.presentMessage(time.strftime(data_format, time.localtime()))
        return True

    def present_battery_status(self, script, event=None):
        """Presents the battery status."""

        if not (psutil and psutil.sensors_battery()):
            script.presentMessage(messages.BATTERY_STATUS_UNKNOWN)
            return True

        battery = psutil.sensors_battery()
        if battery.power_plugged:
            msg = f"{messages.BATTERY_LEVEL % battery.percent} {messages.BATTERY_PLUGGED_IN_TRUE}"
        else:
            msg = f"{messages.BATTERY_LEVEL % battery.percent} {messages.BATTERY_PLUGGED_IN_FALSE}"

        script.presentMessage(msg)
        return True

    def present_cpu_and_memory_usage(self, script, event=None):
        """Presents the cpu and memory usage."""

        if psutil is None:
            script.presentMessage(messages.CPU_AND_MEMORY_USAGE_UNKNOWN)
            return True

        cpu_usage = round(psutil.cpu_percent())

        memory = psutil.virtual_memory()
        memory_percent= round(memory.percent)
        if memory.total > 1024 ** 3:
            details = messages.memoryUsageGB(memory.used / (1024 ** 3), memory.total / (1024 ** 3))
        else:
            details = messages.memoryUsageMB(memory.used / (1024 ** 2), memory.total / (1024 ** 2))

        msg = f"{messages.CPU_AND_MEMORY_USAGE_LEVELS % (cpu_usage, memory_percent)}. {details}"
        script.presentMessage(msg)
        return True


_presenter = SystemInformationPresenter()
def get_presenter():
    return _presenter
