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


import time
from enum import Enum
from typing import Any, TYPE_CHECKING

_PSUTIL_AVAILABLE = False
try:
    import psutil  # type: ignore

    _PSUTIL_AVAILABLE = True
except ModuleNotFoundError:
    pass

from . import cmdnames
from . import command_manager
from . import dbus_service
from . import debug
from . import gsettings_registry
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import preferences_grid_base
from . import presentation_manager
from . import settings


class DateFormat(Enum):
    """Date format enumeration with format strings."""

    LOCALE = "%x"
    NUMBERS_DM = "%d/%m"
    NUMBERS_MD = "%m/%d"
    NUMBERS_DMY = "%d/%m/%Y"
    NUMBERS_MDY = "%m/%d/%Y"
    NUMBERS_YMD = "%Y/%m/%d"
    FULL_DM = "%A, %-d %B"
    FULL_MD = "%A, %B %-d"
    FULL_DMY = "%A, %-d %B, %Y"
    FULL_MDY = "%A, %B %-d, %Y"
    FULL_YMD = "%Y. %B %-d, %A"
    ABBREVIATED_DM = "%a, %-d %b"
    ABBREVIATED_MD = "%a, %b %-d"
    ABBREVIATED_DMY = "%a, %-d %b, %Y"
    ABBREVIATED_MDY = "%a, %b %-d, %Y"
    ABBREVIATED_YMD = "%Y. %b %-d, %a"

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


class TimeFormat(Enum):
    """Time format enumeration with format strings."""

    LOCALE = "%X"
    TWELVE_HM = "%I:%M %p"
    TWELVE_HMS = "%I:%M:%S %p"
    TWENTYFOUR_HM = "%H:%M"
    TWENTYFOUR_HMS = "%H:%M:%S"
    TWENTYFOUR_HM_WITH_WORDS = messages.TIME_FORMAT_24_HM_WITH_WORDS
    TWENTYFOUR_HMS_WITH_WORDS = messages.TIME_FORMAT_24_HMS_WITH_WORDS

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


class TimeAndDatePreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Time and Date preferences page."""

    _gsettings_schema = "system-information"

    def __init__(self, presenter: "SystemInformationPresenter") -> None:
        """Initialize the preferences grid."""

        # Generate display options (strftime examples) and values (format strings)
        date_options = []
        date_values = []
        for fmt in DateFormat:
            example = time.strftime(fmt.value, time.localtime())
            date_options.append(example)
            date_values.append(fmt.value)

        time_options = []
        time_values = []
        for time_fmt in TimeFormat:
            example = time.strftime(time_fmt.value, time.localtime())
            time_options.append(example)
            time_values.append(time_fmt.value)

        controls = [
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_DATE_FORMAT,
                options=date_options,
                values=date_values,
                getter=presenter._get_date_format_string,
                setter=presenter._set_date_format_string,
                prefs_key="presentDateFormat",
                member_of=guilabels.TIME_AND_DATE,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_TIME_FORMAT,
                options=time_options,
                values=time_values,
                getter=presenter._get_time_format_string,
                setter=presenter._set_time_format_string,
                prefs_key="presentTimeFormat",
                member_of=guilabels.TIME_AND_DATE,
            ),
        ]

        super().__init__(guilabels.KB_GROUP_SYSTEM_INFORMATION, controls)


if TYPE_CHECKING:
    from .scripts import default


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.SystemInformation",
    name="system-information",
)
class SystemInformationPresenter:
    """Provides commands to present system information."""

    _SCHEMA = "system-information"

    def _get_setting(self, key: str, gtype: str, fallback: Any) -> Any:
        """Returns the dconf value for key, or fallback if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA, key, gtype, fallback=fallback
        )

    def __init__(self) -> None:
        self._initialized: bool = False

        msg = "SYSTEM INFORMATION PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SystemInformationPresenter", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_SYSTEM_INFORMATION

        # Keybindings (same for desktop and laptop)
        kb_t = keybindings.KeyBinding("t", keybindings.ORCA_MODIFIER_MASK)
        kb_t_2 = keybindings.KeyBinding("t", keybindings.ORCA_MODIFIER_MASK, click_count=2)

        # (name, function, description, keybinding)
        commands_data = [
            ("presentTimeHandler", self.present_time, cmdnames.PRESENT_CURRENT_TIME, kb_t),
            ("presentDateHandler", self.present_date, cmdnames.PRESENT_CURRENT_DATE, kb_t_2),
            (
                "present_battery_status",
                self.present_battery_status,
                cmdnames.PRESENT_BATTERY_STATUS,
                None,
            ),
            (
                "present_cpu_and_memory_usage",
                self.present_cpu_and_memory_usage,
                cmdnames.PRESENT_CPU_AND_MEMORY_USAGE,
                None,
            ),
        ]

        for name, function, description, kb in commands_data:
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=kb,
                    laptop_keybinding=kb,
                )
            )

        msg = "SYSTEM INFORMATION PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def create_time_and_date_preferences_grid(self) -> TimeAndDatePreferencesGrid:
        """Returns the GtkGrid containing the time and date preferences UI."""

        return TimeAndDatePreferencesGrid(self)

    def _get_date_format_string(self) -> str:
        """Returns the current date format string for internal use."""

        return self._get_setting("date-format", "s", settings.presentDateFormat)

    def _get_time_format_string(self) -> str:
        """Returns the current time format string for internal use."""

        return self._get_setting("time-format", "s", settings.presentTimeFormat)

    def _set_date_format_string(self, value: str) -> bool:
        """Sets the date format string directly for internal use."""

        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "date-format", value)
        return True

    def _set_time_format_string(self, value: str) -> bool:
        """Sets the time format string directly for internal use."""

        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "time-format", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="date-format",
        schema="system-information",
        gtype="s",
        default="%x",
        summary="Date format string",
        settings_key="presentDateFormat",
    )
    @dbus_service.getter
    def get_date_format(self) -> str:
        """Returns the current date format name."""

        string_value = self._get_date_format_string()
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
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "date-format", fmt.value)
        return True

    @dbus_service.getter
    def get_available_date_formats(self) -> list[str]:
        """Returns a list of available date format names."""

        return [fmt.string_name for fmt in DateFormat]

    @gsettings_registry.get_registry().gsetting(
        key="time-format",
        schema="system-information",
        gtype="s",
        default="%X",
        summary="Time format string",
        settings_key="presentTimeFormat",
    )
    @dbus_service.getter
    def get_time_format(self) -> str:
        """Returns the current time format name."""

        string_value = self._get_time_format_string()
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
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "time-format", fmt.value)
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
        notify_user: bool = True,
    ) -> bool:
        """Presents the current time."""

        tokens = [
            "SYSTEM INFORMATION PRESENTER: present_time. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        time_format = self._get_time_format_string()
        presentation_manager.get_manager().present_message(
            time.strftime(time_format, time.localtime())
        )
        return True

    @dbus_service.command
    def present_date(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the current date."""

        tokens = [
            "SYSTEM INFORMATION PRESENTER: present_date. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        date_format = self._get_date_format_string()
        presentation_manager.get_manager().present_message(
            time.strftime(date_format, time.localtime())
        )
        return True

    @dbus_service.command
    def present_battery_status(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the battery status."""

        tokens = [
            "SYSTEM INFORMATION PRESENTER: present_battery_status. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        battery = psutil.sensors_battery() if _PSUTIL_AVAILABLE else None
        if battery is None:
            presentation_manager.get_manager().present_message(messages.BATTERY_STATUS_UNKNOWN)
            return True
        if battery.power_plugged:
            msg = f"{messages.BATTERY_LEVEL % battery.percent} {messages.BATTERY_PLUGGED_IN_TRUE}"
        else:
            msg = f"{messages.BATTERY_LEVEL % battery.percent} {messages.BATTERY_PLUGGED_IN_FALSE}"

        presentation_manager.get_manager().present_message(msg)
        return True

    @dbus_service.command
    def present_cpu_and_memory_usage(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the cpu and memory usage."""

        tokens = [
            "SYSTEM INFORMATION PRESENTER: present_cpu_and_memory_usage. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not _PSUTIL_AVAILABLE:
            presentation_manager.get_manager().present_message(
                messages.CPU_AND_MEMORY_USAGE_UNKNOWN
            )
            return True

        cpu_usage = round(psutil.cpu_percent())

        memory = psutil.virtual_memory()
        memory_percent = round(memory.percent)
        if memory.total > 1024**3:
            details = messages.memory_usage_gb(memory.used / (1024**3), memory.total / (1024**3))
        else:
            details = messages.memory_usage_mb(memory.used / (1024**2), memory.total / (1024**2))

        msg = f"{messages.CPU_AND_MEMORY_USAGE_LEVELS % (cpu_usage, memory_percent)}. {details}"
        presentation_manager.get_manager().present_message(msg)
        return True


_presenter = SystemInformationPresenter()


def get_presenter() -> SystemInformationPresenter:
    """Returns the system-information-presenter singleton."""

    return _presenter
