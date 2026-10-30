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

"""Settings keys and values for flat review."""

from __future__ import annotations

from enum import Enum

from . import gsettings_registry


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.FocusTracking",
    values={"off": 0, "auto": 1, "on": 2},
)
class FocusTracking(Enum):
    """How closely flat review follows the focus/caret location."""

    OFF = 0
    AUTO = 1
    ON = 2


class FlatReviewSettings:
    """The flat review settings keys."""

    KEY_DISPLAY_UPDATES = "display-updates"
    KEY_FOCUS_TRACKING = "focus-tracking"
    KEY_RESTRICTED = "restricted"
    KEY_SPEAK_UPDATES = "speak-updates"
