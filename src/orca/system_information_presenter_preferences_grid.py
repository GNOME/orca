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

if TYPE_CHECKING:
    from .system_information_presenter import SystemInformationPresenter


class TimeAndDatePreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Time and Date preferences page."""

    _gsettings_schema = "system-information"

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
