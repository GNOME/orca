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
from enum import Enum
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

class DateFormat(Enum):
    """Date format enumeration with string values from messages."""

    LOCALE = messages.DATE_FORMAT_LOCALE
    NUMBERS_DM = messages.DATE_FORMAT_NUMBERS_DM
    NUMBERS_MD = messages.DATE_FORMAT_NUMBERS_MD
    NUMBERS_DMY = messages.DATE_FORMAT_NUMBERS_DMY
    NUMBERS_MDY = messages.DATE_FORMAT_NUMBERS_MDY
    NUMBERS_YMD = messages.DATE_FORMAT_NUMBERS_YMD
    FULL_DM = messages.DATE_FORMAT_FULL_DM
    FULL_MD = messages.DATE_FORMAT_FULL_MD
    FULL_DMY = messages.DATE_FORMAT_FULL_DMY
    FULL_MDY = messages.DATE_FORMAT_FULL_MDY
    FULL_YMD = messages.DATE_FORMAT_FULL_YMD
    ABBREVIATED_DM = messages.DATE_FORMAT_ABBREVIATED_DM
    ABBREVIATED_MD = messages.DATE_FORMAT_ABBREVIATED_MD
    ABBREVIATED_DMY = messages.DATE_FORMAT_ABBREVIATED_DMY
    ABBREVIATED_MDY = messages.DATE_FORMAT_ABBREVIATED_MDY
    ABBREVIATED_YMD = messages.DATE_FORMAT_ABBREVIATED_YMD

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()

class TimeFormat(Enum):
    """Time format enumeration with string values from messages."""

    LOCALE = messages.TIME_FORMAT_LOCALE
    TWELVE_HM = messages.TIME_FORMAT_12_HM
    TWELVE_HMS = messages.TIME_FORMAT_12_HMS
    TWENTYFOUR_HM = messages.TIME_FORMAT_24_HM
    TWENTYFOUR_HMS = messages.TIME_FORMAT_24_HMS
    TWENTYFOUR_HM_WITH_WORDS = messages.TIME_FORMAT_24_HM_WITH_WORDS
    TWENTYFOUR_HMS_WITH_WORDS = messages.TIME_FORMAT_24_HMS_WITH_WORDS

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()

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

    def _get_date_format_string(self) -> str:
        """Returns the current date format string for internal use."""

        return settings_manager.get_manager().get_setting("presentDateFormat")

    def _get_time_format_string(self) -> str:
        """Returns the current time format string for internal use."""

        return settings_manager.get_manager().get_setting("presentTimeFormat")

    @dbus_service.getter
    def get_date_format(self) -> str:
        """Returns the current date format name."""

        string_value = settings_manager.get_manager().get_setting("presentDateFormat")
        for fmt in DateFormat:
            if fmt.value == string_value:
                return fmt.string_name
        return string_value

    @dbus_service.setter
    def set_date_format(self, value: str) -> bool:
        """Sets the date format."""

        try:
            fmt = DateFormat[value.upper()]
        except KeyError:
            msg = f"SYSTEM INFORMATION PRESENTER: Invalid date format: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SYSTEM INFORMATION PRESENTER: Setting date format to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("presentDateFormat", fmt.value)
        return True

    @dbus_service.getter
    def get_available_date_formats(self) -> list[str]:
        """Returns a list of available date format names."""

        return [fmt.string_name for fmt in DateFormat]

    @dbus_service.getter
    def get_time_format(self) -> str:
        """Returns the current time format name."""

        string_value = settings_manager.get_manager().get_setting("presentTimeFormat")
        for fmt in TimeFormat:
            if fmt.value == string_value:
                return fmt.string_name
        return string_value

    @dbus_service.setter
    def set_time_format(self, value: str) -> bool:
        """Sets the time format."""

        try:
            fmt = TimeFormat[value.upper()]
        except KeyError:
            msg = f"SYSTEM INFORMATION PRESENTER: Invalid time format: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SYSTEM INFORMATION PRESENTER: Setting time format to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("presentTimeFormat", fmt.value)
        return True

    @dbus_service.getter
    def get_available_time_formats(self) -> list[str]:
        """Returns a list of available time format names."""

        return [fmt.string_name for fmt in TimeFormat]

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

        time_format = self._get_time_format_string()
        script.present_message(time.strftime(time_format, time.localtime()))
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

        date_format = self._get_date_format_string()
        script.present_message(time.strftime(date_format, time.localtime()))
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
            script.present_message(messages.BATTERY_STATUS_UNKNOWN)
            return True

        battery = psutil.sensors_battery()
        if battery.power_plugged:
            msg = f"{messages.BATTERY_LEVEL % battery.percent} {messages.BATTERY_PLUGGED_IN_TRUE}"
        else:
            msg = f"{messages.BATTERY_LEVEL % battery.percent} {messages.BATTERY_PLUGGED_IN_FALSE}"

        script.present_message(msg)
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
            script.present_message(messages.CPU_AND_MEMORY_USAGE_UNKNOWN)
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
        script.present_message(msg)
        return True


_presenter = SystemInformationPresenter()
def get_presenter() -> SystemInformationPresenter:
    """Returns the system-information-presenter singleton."""

    return _presenter
