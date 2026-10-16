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

"""Preferences grid for mouse presentation support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import guilabels, mouse_presenter, preferences_grid_base
from .help_metadata import (
    PreferenceCategoryDoc,
    PreferenceControlDoc,
    PreferencePanelDoc,
)

if TYPE_CHECKING:
    from .mouse_presenter import MousePresenter


class MousePreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Mouse preferences page."""

    _gsettings_schema = "mouse-review"
    _documentation_summary = (
        "Use these settings to control what Orca presents as the pointer moves."
    )

    @classmethod
    def get_documentation(cls) -> PreferencePanelDoc:
        """Return documentation metadata for mouse preferences."""

        return PreferencePanelDoc(
            title=guilabels.MOUSE,
            panel_id="mouse_presenter.mouse",
            category=PreferenceCategoryDoc(
                category_id="mouse",
                title="Mouse",
                description=(
                    "Mouse review presents the object under the pointer. Configure this "
                    "behavior and mouse-triggered tooltips."
                ),
                panels=("mouse_presenter.mouse",),
            ),
            command_groups=("commands.mouse",),
            schema="mouse-review",
            controls=(
                PreferenceControlDoc(
                    label=guilabels.GENERAL_PRESENT_TOOLTIPS,
                    kind="switch",
                    summary=(
                        "Controls whether Orca presents tooltips that appear when the "
                        "pointer hovers over an object. Tooltips requested from the keyboard, "
                        "such as with Ctrl+F1 in supported applications, are presented "
                        "regardless of this setting."
                    ),
                    schema="mouse-review",
                    key=mouse_presenter.MousePresenter.KEY_PRESENT_TOOLTIPS,
                ),
                PreferenceControlDoc(
                    label=guilabels.GENERAL_SPEAK_OBJECT_UNDER_MOUSE,
                    kind="switch",
                    summary=(
                        "Controls whether Orca speaks the object under the mouse pointer "
                        "as the pointer moves."
                    ),
                    schema="mouse-review",
                    key=mouse_presenter.MousePresenter.KEY_ENABLED,
                ),
            ),
        )

    def __init__(self, presenter: MousePresenter) -> None:
        """Initialize the preferences grid."""

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_PRESENT_TOOLTIPS,
                getter=presenter.get_present_tooltips,
                setter=presenter.set_present_tooltips,
                prefs_key=mouse_presenter.MousePresenter.KEY_PRESENT_TOOLTIPS,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_SPEAK_OBJECT_UNDER_MOUSE,
                getter=presenter.get_is_enabled,
                setter=presenter.set_is_enabled,
                prefs_key=mouse_presenter.MousePresenter.KEY_ENABLED,
            ),
        ]

        super().__init__(guilabels.MOUSE, controls, info_message=guilabels.MOUSE_WAYLAND_WARNING)
