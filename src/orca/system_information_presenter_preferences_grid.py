# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016-2026 Igalia, S.L.
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

"""Preferences grid for system information support."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from . import guilabels, preferences_grid_base, system_information_presenter
from .help_metadata import (
    PreferenceCategoryDoc,
    PreferenceControlDoc,
    PreferencePanelDoc,
    PreferenceValueDoc,
)

if TYPE_CHECKING:
    from .system_information_presenter import SystemInformationPresenter


class TimeAndDatePreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Time and Date preferences page."""

    _gsettings_schema = "system-information"

    @classmethod
    def get_documentation(cls) -> PreferencePanelDoc:
        """Return documentation metadata for system-information preferences."""

        return PreferencePanelDoc(
            title=guilabels.KB_GROUP_SYSTEM_INFORMATION,
            panel_id="system_information_presenter.system-information",
            category=PreferenceCategoryDoc(
                category_id="system-information",
                title="System information",
                description=(
                    "Present the date, time, battery status, and resource usage, and "
                    "configure date and time formats."
                ),
                panels=("system_information_presenter.system-information",),
            ),
            command_groups=("commands.system-information",),
            controls=(
                PreferenceControlDoc(
                    label=guilabels.TIME_AND_DATE,
                    kind="group",
                    summary="Controls how Orca presents the current date and time.",
                    controls=(
                        PreferenceControlDoc(
                            label=guilabels.GENERAL_DATE_FORMAT,
                            default_labels=(
                                PreferenceValueDoc("the system locale's format", "%x"),
                            ),
                            kind="choice",
                            summary=(
                                "Selects the format Orca uses when presenting the current date."
                            ),
                            schema="system-information",
                            # pylint: disable-next=line-too-long
                            key=system_information_presenter.SystemInformationPresenter.KEY_DATE_FORMAT,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.GENERAL_TIME_FORMAT,
                            default_labels=(
                                PreferenceValueDoc("the system locale's format", "%X"),
                            ),
                            kind="choice",
                            summary=(
                                "Selects the format Orca uses when presenting the current time."
                            ),
                            schema="system-information",
                            # pylint: disable-next=line-too-long
                            key=system_information_presenter.SystemInformationPresenter.KEY_TIME_FORMAT,
                        ),
                    ),
                ),
            ),
        )

    def __init__(self, presenter: SystemInformationPresenter) -> None:
        """Initialize the preferences grid."""

        # Generate display options (strftime examples) and values (format strings)
        date_options = []
        date_values = []
        for fmt in system_information_presenter.DateFormat:
            example = time.strftime(fmt.value, time.localtime())
            date_options.append(example)
            date_values.append(fmt.value)

        time_options = []
        time_values = []
        for time_fmt in system_information_presenter.TimeFormat:
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
                prefs_key=system_information_presenter.SystemInformationPresenter.KEY_DATE_FORMAT,
                member_of=guilabels.TIME_AND_DATE,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_TIME_FORMAT,
                options=time_options,
                values=time_values,
                getter=presenter._get_time_format_string,
                setter=presenter._set_time_format_string,
                prefs_key=system_information_presenter.SystemInformationPresenter.KEY_TIME_FORMAT,
                member_of=guilabels.TIME_AND_DATE,
            ),
        ]

        super().__init__(guilabels.KB_GROUP_SYSTEM_INFORMATION, controls)
