# Orca
#
# Copyright 2024-2026 Igalia, S.L.
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

"""Preferences grid for sleep mode settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # pylint: disable=no-name-in-module

from . import gsettings_registry, guilabels, preferences_grid_base

if TYPE_CHECKING:
    from .sleep_mode_manager import SleepModeManager


class SleepModePreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """Preferences grid for sleep mode settings."""

    def __init__(self, manager: SleepModeManager) -> None:
        super().__init__(guilabels.KB_GROUP_SLEEP_MODE)
        self._manager: SleepModeManager = manager
        self._app_switches: list[tuple[str, Gtk.Switch]] = []
        self._listbox: preferences_grid_base.FocusManagedListBox | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        """Create the Gtk widgets composing the grid."""

        row = 0

        info_listbox = self._create_info_listbox(guilabels.SLEEP_MODE_INFO)
        info_listbox.set_margin_bottom(12)
        self.attach(info_listbox, 0, row, 1, 1)
        row += 1

        header_label = Gtk.Label(label=guilabels.SLEEP_MODE_APPS, xalign=0)
        header_label.get_style_context().add_class("heading")
        header_label.set_margin_bottom(6)
        self.attach(header_label, 0, row, 1, 1)
        row += 1

        self._scrolled = self._create_scrolled_window(Gtk.Box())
        self.attach(self._scrolled, 0, row, 1, 1)
        self._scrolled_row = row

    def _create_app_row(self, app_name: str, is_enabled: bool) -> None:
        """Create a switch row for an app and add it to the listbox."""

        assert self._listbox is not None
        row, switch, _label = self._create_switch_row(
            app_name,
            self._on_switch_toggled,
            is_enabled,
            include_top_separator=False,
        )
        self._listbox.add_row_with_widget(row, switch)
        self._app_switches.append((app_name, switch))

    def _on_switch_toggled(self, _switch: Gtk.Switch, _pspec: object) -> None:
        """Handle switch toggle."""

        self._has_unsaved_changes = True

    def reload(self) -> None:
        """Reload settings and refresh the UI."""

        self._has_unsaved_changes = False
        self.refresh()

    def refresh(self) -> None:
        """Rebuild the app list with a fresh FocusManagedListBox."""

        # pylint: disable=no-member
        self._app_switches.clear()
        self._listbox = preferences_grid_base.FocusManagedListBox()
        self._listbox.get_accessible().set_name(guilabels.SLEEP_MODE_APPS)

        saved_apps = set(self._manager.get_sleep_mode_apps())
        running_apps = set(self._manager.get_running_app_names())
        all_apps = running_apps | saved_apps

        for name in sorted(all_apps, key=lambda n: (n not in saved_apps, n.lower())):
            self._create_app_row(name, is_enabled=name in saved_apps)

        child = self._scrolled.get_child()
        if child is not None:
            self._scrolled.remove(child)
        self._scrolled.add(self._listbox)
        self._scrolled.show_all()
        # pylint: enable=no-member

    def save_settings(self, profile: str = "", app_name: str = "") -> dict[str, list[str]]:
        """Save the list of sleep-mode apps to dconf."""

        enabled_apps = [name for name, switch in self._app_switches if switch.get_active()]
        self._manager.set_sleep_mode_apps(enabled_apps)
        self._has_unsaved_changes = False

        if profile:
            registry = gsettings_registry.get_registry()
            registry.save_schema(
                "sleep-mode",
                {"apps": enabled_apps},
                profile,
                app_name,
            )

        return {"apps": enabled_apps}
