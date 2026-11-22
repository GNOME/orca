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


"""Preferences grid for structural navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import guilabels, preferences_grid_base
from .help_metadata import (
    PreferenceControlDoc,
    PreferencePanelDoc,
)
from .structural_navigator_settings import StructuralNavigationSettings

if TYPE_CHECKING:
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    from .structural_navigator import StructuralNavigator


class StructuralNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for structural navigation settings within the Documents page."""

    _gsettings_schema = "structural-navigation"

    @classmethod
    def get_documentation(cls) -> PreferencePanelDoc:
        """Return documentation metadata for structural navigation preferences."""

        return PreferencePanelDoc(
            title=guilabels.KB_GROUP_STRUCTURAL_NAVIGATION,
            panel_id="document_presenter.structural-navigation",
            command_groups=("documents.structural-navigation.commands",),
            target="documents.structural-navigation",
            link_summary=(
                "Configure how structural navigation works in document content and application "
                "interfaces."
            ),
            schema="structural-navigation",
            controls=(
                PreferenceControlDoc(
                    label=guilabels.KB_GROUP_STRUCTURAL_NAVIGATION,
                    kind="switch",
                    summary=(
                        "Controls whether Orca's structural navigation commands are available."
                    ),
                    schema="structural-navigation",
                    key=StructuralNavigationSettings.KEY_ENABLED,
                ),
                PreferenceControlDoc(
                    label=guilabels.AUTOMATIC_FOCUS_MODE,
                    kind="switch",
                    target="documents.structural-focus-mode",
                    summary=(
                        "Controls whether Orca switches to focus mode when structural "
                        "navigation lands on an interactive widget."
                    ),
                    schema="structural-navigation",
                    key=StructuralNavigationSettings.KEY_TRIGGERS_FOCUS_MODE,
                ),
                PreferenceControlDoc(
                    label=guilabels.STRUCTURAL_NAVIGATION_WRAP_AROUND,
                    kind="switch",
                    summary=(
                        "Controls whether structural navigation wraps to the other end "
                        "of the document."
                    ),
                    schema="structural-navigation",
                    key=StructuralNavigationSettings.KEY_WRAPS,
                ),
                PreferenceControlDoc(
                    label=guilabels.STRUCTURAL_NAVIGATION_LARGE_OBJECT_LENGTH,
                    kind="integer",
                    summary=(
                        "Sets the minimum number of characters in a text block for the "
                        "large-object structural navigation commands."
                    ),
                    schema="structural-navigation",
                    key=StructuralNavigationSettings.KEY_LARGE_OBJECT_TEXT_LENGTH,
                    minimum="1",
                    maximum="500",
                ),
                PreferenceControlDoc(
                    label=guilabels.STRUCTURAL_NAVIGATION_SKIP_UNLABELED_IMAGES,
                    kind="switch",
                    summary=(
                        "Controls whether image navigation skips images without accessible "
                        "names or descriptions."
                    ),
                    schema="structural-navigation",
                    key=StructuralNavigationSettings.KEY_SKIP_UNLABELED_IMAGES,
                ),
            ),
        )

    def __init__(self, navigator: StructuralNavigator) -> None:
        # Child controls need to check the enabled switch's UI state (not runtime state)
        # because the enabled switch has apply_immediately=False.
        self._enabled_switch: Gtk.Switch | None = None

        def is_enabled() -> bool:
            if self._enabled_switch is not None:
                return self._enabled_switch.get_active()
            return navigator.get_is_enabled()

        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.KB_GROUP_STRUCTURAL_NAVIGATION,
                getter=navigator.get_is_enabled,
                setter=navigator.set_is_enabled,
                prefs_key=StructuralNavigationSettings.KEY_ENABLED,
                apply_immediately=False,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTOMATIC_FOCUS_MODE,
                getter=navigator.get_triggers_focus_mode,
                setter=navigator.set_triggers_focus_mode,
                prefs_key=StructuralNavigationSettings.KEY_TRIGGERS_FOCUS_MODE,
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.STRUCTURAL_NAVIGATION_WRAP_AROUND,
                getter=navigator.get_navigation_wraps,
                setter=navigator.set_navigation_wraps,
                prefs_key=StructuralNavigationSettings.KEY_WRAPS,
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.STRUCTURAL_NAVIGATION_LARGE_OBJECT_LENGTH,
                minimum=1,
                maximum=500,
                getter=navigator.get_large_object_text_length,
                setter=navigator.set_large_object_text_length,
                prefs_key=StructuralNavigationSettings.KEY_LARGE_OBJECT_TEXT_LENGTH,
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.STRUCTURAL_NAVIGATION_SKIP_UNLABELED_IMAGES,
                getter=navigator.get_skip_unlabeled_images,
                setter=navigator.set_skip_unlabeled_images,
                prefs_key=StructuralNavigationSettings.KEY_SKIP_UNLABELED_IMAGES,
                determine_sensitivity=is_enabled,
            ),
        ]
        info = (
            f"{guilabels.STRUCTURAL_NAVIGATION_INFO}\n\n{guilabels.AUTOMATIC_FOCUS_MODE_INFO}"
            f"\n\n{guilabels.LARGE_OBJECT_INFO}"
        )
        super().__init__(guilabels.KB_GROUP_STRUCTURAL_NAVIGATION, controls, info_message=info)

        self._enabled_switch = self._widgets[0]
