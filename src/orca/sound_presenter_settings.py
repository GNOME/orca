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

"""Settings keys and values for sound."""

from __future__ import annotations

from enum import Enum

from . import gsettings_registry


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.ProgressBarVerbosity",
    values={"all": 0, "application": 1, "window": 2},
)
class ProgressBarVerbosity(Enum):
    """Progress bar verbosity level enumeration."""

    ALL = 0
    APPLICATION = 1
    WINDOW = 2


class SoundSettings:
    """The sound settings keys."""

    KEY_BEEP_PROGRESS_BAR_UPDATES = "beep-progress-bar-updates"
    KEY_ENABLED = "enabled"
    KEY_PROGRESS_BAR_BEEP_INTERVAL = "progress-bar-beep-interval"
    KEY_PROGRESS_BAR_BEEP_VERBOSITY = "progress-bar-beep-verbosity"
    KEY_VOLUME = "volume"
