# Orca
#
# Copyright 2026 Igalia, S.L.
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

"""Settings keys and values for system information."""

from __future__ import annotations

from enum import Enum

from . import messages


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


class SystemInformationSettings:
    """The system information settings keys."""

    KEY_DATE_FORMAT = "date-format"
    KEY_TIME_FORMAT = "time-format"
