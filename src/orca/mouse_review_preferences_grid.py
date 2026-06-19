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

"""Preferences grid for mouse review support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import guilabels, mouse_review, preferences_grid_base

if TYPE_CHECKING:
    from .mouse_review import MouseReviewer


class MousePreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Mouse preferences page."""

    _gsettings_schema = "mouse-review"

    def __init__(self, reviewer: MouseReviewer) -> None:
        """Initialize the preferences grid."""

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_PRESENT_TOOLTIPS,
                getter=reviewer.get_present_tooltips,
                setter=reviewer.set_present_tooltips,
                prefs_key=mouse_review.MouseReviewer.KEY_PRESENT_TOOLTIPS,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_SPEAK_OBJECT_UNDER_MOUSE,
                getter=reviewer.get_is_enabled,
                setter=reviewer.set_is_enabled,
                prefs_key=mouse_review.MouseReviewer.KEY_ENABLED,
            ),
        ]

        super().__init__(guilabels.MOUSE, controls, info_message=guilabels.MOUSE_WAYLAND_WARNING)
