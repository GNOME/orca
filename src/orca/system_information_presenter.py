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

# pylint: disable=wrong-import-position

"""Module for presenting system information"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import time
from typing import TYPE_CHECKING

_PSUTIL_AVAILABLE = False
try:
    import psutil  # type: ignore
    _PSUTIL_AVAILABLE = True
except ModuleNotFoundError:
    pass

from . import cmdnames
from . import dbus_service
from . import debug
from . import input_event
from . import keybindings
from . import messages
from . import settings_manager

if TYPE_CHECKING:
    from .scripts import default

class SystemInformationPresenter:
    """Provides commands to present system information."""

    def __init__(self) -> None:
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()

        msg = "SYSTEM INFORMATION PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SystemInformationPresenter", self)

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the system-information-presenter keybindings."""

        if refresh:
            msg = f"SYSTEM INFORMATION PRESENTER: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("SYSTEM INFORMATION PRESENTER: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the system-information-presenter handlers."""

        if refresh:
            msg = "SYSTEM INFORMATION PRESENTER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self) -> None:
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
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self) -> None:
        """Sets up the system-information-presenter key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["presentTimeHandler"],
                1))

        self._bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["presentDateHandler"],
                2))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["present_battery_status"],
                1))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["present_cpu_and_memory_usage"],
                1))

        msg = "SYSTEM INFORMATION PRESENTER: Bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    @dbus_service.command
    def present_time(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current time."""

        tokens = ["SYSTEM INFORMATION PRESENTER: present_time. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        time_format = settings_manager.get_manager().get_setting('presentTimeFormat')
        script.presentMessage(time.strftime(time_format, time.localtime()))
        return True

    @dbus_service.command
    def present_date(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the current date."""

        tokens = ["SYSTEM INFORMATION PRESENTER: present_date. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        data_format = settings_manager.get_manager().get_setting('presentDateFormat')
        script.presentMessage(time.strftime(data_format, time.localtime()))
        return True

    @dbus_service.command
    def present_battery_status(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the battery status."""

        tokens = ["SYSTEM INFORMATION PRESENTER: present_battery_status. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (_PSUTIL_AVAILABLE and psutil.sensors_battery()):
            script.presentMessage(messages.BATTERY_STATUS_UNKNOWN)
            return True

        battery = psutil.sensors_battery()
        if battery.power_plugged:
            msg = f"{messages.BATTERY_LEVEL % battery.percent} {messages.BATTERY_PLUGGED_IN_TRUE}"
        else:
            msg = f"{messages.BATTERY_LEVEL % battery.percent} {messages.BATTERY_PLUGGED_IN_FALSE}"

        script.presentMessage(msg)
        return True

    @dbus_service.command
    def present_cpu_and_memory_usage(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the cpu and memory usage."""

        tokens = ["SYSTEM INFORMATION PRESENTER: present_cpu_and_memory_usage. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not _PSUTIL_AVAILABLE:
            script.presentMessage(messages.CPU_AND_MEMORY_USAGE_UNKNOWN)
            return True

        cpu_usage = round(psutil.cpu_percent())

        memory = psutil.virtual_memory()
        memory_percent= round(memory.percent)
        if memory.total > 1024 ** 3:
            details = messages.memory_usage_gb(
                memory.used / (1024 ** 3), memory.total / (1024 ** 3))
        else:
            details = messages.memory_usage_mb(
                memory.used / (1024 ** 2), memory.total / (1024 ** 2))

        msg = f"{messages.CPU_AND_MEMORY_USAGE_LEVELS % (cpu_usage, memory_percent)}. {details}"
        script.presentMessage(msg)
        return True


_presenter = SystemInformationPresenter()
def get_presenter() -> SystemInformationPresenter:
    """Returns the system-information-presenter singleton."""

    return _presenter
