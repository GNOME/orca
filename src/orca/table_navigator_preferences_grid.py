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


"""Preferences grid for table navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import guilabels, preferences_grid_base
from .help_metadata import (
    PreferenceControlDoc,
    PreferencePanelDoc,
)
from .table_navigator_settings import TableNavigationSettings

if TYPE_CHECKING:
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    from .table_navigator import TableNavigator


class TableNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for table navigation settings within the Documents page."""

    _gsettings_schema = "table-navigation"

    @classmethod
    def get_documentation(cls) -> PreferencePanelDoc:
        """Return documentation metadata for table navigation preferences."""

        return PreferencePanelDoc(
            title=guilabels.KB_GROUP_TABLE_NAVIGATION,
            panel_id="document_presenter.table-navigation",
            command_groups=("documents.table-navigation.commands",),
            target="documents.table-navigation",
            link_summary="Configure how Orca-controlled table navigation works.",
            schema="table-navigation",
            controls=(
                PreferenceControlDoc(
                    label=guilabels.KB_GROUP_TABLE_NAVIGATION,
                    kind="switch",
                    summary=("Controls whether Orca's table navigation commands are available."),
                    schema="table-navigation",
                    key=TableNavigationSettings.KEY_ENABLED,
                ),
                PreferenceControlDoc(
                    label=guilabels.TABLE_SKIP_BLANK_CELLS,
                    kind="switch",
                    summary=("Controls whether table navigation skips empty cells."),
                    schema="table-navigation",
                    key=TableNavigationSettings.KEY_SKIP_BLANK_CELLS,
                ),
            ),
        )

    def __init__(self, navigator: TableNavigator) -> None:
        # Child controls need to check the enabled switch's UI state (not runtime state)
        # because the enabled switch has apply_immediately=False.
        self._enabled_switch: Gtk.Switch | None = None

        def is_enabled() -> bool:
            if self._enabled_switch is not None:
                return self._enabled_switch.get_active()
            return navigator.get_is_enabled()

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.KB_GROUP_TABLE_NAVIGATION,
                getter=navigator.get_is_enabled,
                setter=navigator.set_is_enabled,
                prefs_key=TableNavigationSettings.KEY_ENABLED,
                apply_immediately=False,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.TABLE_SKIP_BLANK_CELLS,
                getter=navigator.get_skip_blank_cells,
                setter=navigator.set_skip_blank_cells,
                prefs_key=TableNavigationSettings.KEY_SKIP_BLANK_CELLS,
                determine_sensitivity=is_enabled,
            ),
        ]
        super().__init__(guilabels.KB_GROUP_TABLE_NAVIGATION, controls)

        self._enabled_switch = self._widgets[0]
