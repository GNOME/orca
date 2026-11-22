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


"""Preferences grid for caret navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import guilabels, preferences_grid_base
from .caret_navigator_settings import CaretNavigationSettings
from .help_metadata import (
    PreferenceControlDoc,
    PreferencePanelDoc,
)

if TYPE_CHECKING:
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    from .caret_navigator import CaretNavigator


class CaretNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for caret navigation settings within the Documents page."""

    _gsettings_schema = "caret-navigation"

    @classmethod
    def get_documentation(cls) -> PreferencePanelDoc:
        """Return documentation metadata for caret navigation preferences."""

        return PreferencePanelDoc(
            title=guilabels.KB_GROUP_CARET_NAVIGATION,
            panel_id="document_presenter.caret-navigation",
            command_groups=("documents.caret-navigation.commands",),
            target="documents.caret-navigation",
            link_summary=(
                "Configure how caret navigation works in text and how lines are presented."
            ),
            schema="caret-navigation",
            controls=(
                PreferenceControlDoc(
                    label=guilabels.KB_GROUP_CARET_NAVIGATION,
                    kind="switch",
                    summary=(
                        "Controls whether Orca provides text navigation using the arrow "
                        "keys, Home, and End."
                    ),
                    schema="caret-navigation",
                    key=CaretNavigationSettings.KEY_ENABLED,
                ),
                PreferenceControlDoc(
                    label=guilabels.AUTOMATIC_FOCUS_MODE,
                    kind="switch",
                    target="documents.caret-focus-mode",
                    summary=(
                        "Controls whether Orca switches to focus mode when caret "
                        "navigation lands on an interactive widget."
                    ),
                    schema="caret-navigation",
                    key=CaretNavigationSettings.KEY_TRIGGERS_FOCUS_MODE,
                ),
                PreferenceControlDoc(
                    label=guilabels.CARET_SELECTION_ENABLED,
                    kind="switch",
                    summary=(
                        "Lets Orca manage text selection when you hold Shift while using its "
                        "caret navigation commands. Not all applications provide the support "
                        "Orca needs. Avoid enabling this globally; enable it in "
                        "application-specific preferences only where Orca's selection support "
                        "is needed and you have verified it works."
                    ),
                    schema="caret-navigation",
                    key=CaretNavigationSettings.KEY_SELECTION_ENABLED,
                    since="52",
                ),
                PreferenceControlDoc(
                    label=guilabels.CONTENT_LAYOUT_MODE,
                    kind="switch",
                    summary=(
                        "Controls whether Orca presents each full visual line or treats "
                        "each object as if it were on a separate line."
                    ),
                    schema="caret-navigation",
                    key=CaretNavigationSettings.KEY_LAYOUT_MODE,
                ),
            ),
        )

    def __init__(self, navigator: CaretNavigator) -> None:
        # Child controls need to check the enabled switch's UI state (not runtime state)
        # because the enabled switch has apply_immediately=False.
        self._enabled_switch: Gtk.Switch | None = None

        def is_enabled() -> bool:
            if self._enabled_switch is not None:
                return self._enabled_switch.get_active()
            return navigator.get_is_enabled()

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.KB_GROUP_CARET_NAVIGATION,
                getter=navigator.get_is_enabled,
                setter=navigator.set_is_enabled,
                prefs_key=CaretNavigationSettings.KEY_ENABLED,
                apply_immediately=False,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTOMATIC_FOCUS_MODE,
                getter=navigator.get_triggers_focus_mode,
                setter=navigator.set_triggers_focus_mode,
                prefs_key=CaretNavigationSettings.KEY_TRIGGERS_FOCUS_MODE,
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CARET_SELECTION_ENABLED,
                getter=navigator.get_selection_enabled,
                setter=navigator.set_selection_enabled,
                prefs_key=CaretNavigationSettings.KEY_SELECTION_ENABLED,
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CONTENT_LAYOUT_MODE,
                getter=navigator.get_layout_mode,
                setter=navigator.set_layout_mode,
                prefs_key=CaretNavigationSettings.KEY_LAYOUT_MODE,
                determine_sensitivity=is_enabled,
            ),
        ]
        caret_info = f"{guilabels.CARET_NAVIGATION_INFO} {guilabels.CARET_SELECTION_INFO}"
        info = (
            f"{caret_info}\n\n{guilabels.AUTOMATIC_FOCUS_MODE_INFO}\n\n{guilabels.LAYOUT_MODE_INFO}"
        )
        super().__init__(guilabels.KB_GROUP_CARET_NAVIGATION, controls, info_message=info)

        self._enabled_switch = self._widgets[0]
