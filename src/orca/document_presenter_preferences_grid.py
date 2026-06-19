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

# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments,
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-return-statements

"""Preferences grids for document presentation and navigation settings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import (
    caret_navigator,
    document_presenter,
    guilabels,
    math_presenter,
    preferences_grid_base,
    structural_navigator,
    table_navigator,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    import gi

    from .document_presenter import DocumentPresenter

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk


class CaretNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for caret navigation settings within the Documents page."""

    _gsettings_schema = "caret-navigation"

    def __init__(self) -> None:
        nav = caret_navigator.get_navigator()

        # Child controls need to check the enabled switch's UI state (not runtime state)
        # because the enabled switch has apply_immediately=False.
        self._enabled_switch: Gtk.Switch | None = None

        def is_enabled() -> bool:
            if self._enabled_switch is not None:
                return self._enabled_switch.get_active()
            return nav.get_is_enabled()

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.KB_GROUP_CARET_NAVIGATION,
                getter=nav.get_is_enabled,
                setter=nav.set_is_enabled,
                prefs_key=caret_navigator.CaretNavigator.KEY_ENABLED,
                apply_immediately=False,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTOMATIC_FOCUS_MODE,
                getter=nav.get_triggers_focus_mode,
                setter=nav.set_triggers_focus_mode,
                prefs_key=caret_navigator.CaretNavigator.KEY_TRIGGERS_FOCUS_MODE,
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CONTENT_LAYOUT_MODE,
                getter=nav.get_layout_mode,
                setter=nav.set_layout_mode,
                prefs_key=caret_navigator.CaretNavigator.KEY_LAYOUT_MODE,
                determine_sensitivity=is_enabled,
            ),
        ]
        info = (
            f"{guilabels.CARET_NAVIGATION_INFO}\n\n{guilabels.AUTOMATIC_FOCUS_MODE_INFO}"
            f"\n\n{guilabels.LAYOUT_MODE_INFO}"
        )
        super().__init__(guilabels.KB_GROUP_CARET_NAVIGATION, controls, info_message=info)

        self._enabled_switch = self._widgets[0]


class StructuralNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for structural navigation settings within the Documents page."""

    _gsettings_schema = "structural-navigation"

    def __init__(self) -> None:
        nav = structural_navigator.get_navigator()

        # Child controls need to check the enabled switch's UI state (not runtime state)
        # because the enabled switch has apply_immediately=False.
        self._enabled_switch: Gtk.Switch | None = None

        def is_enabled() -> bool:
            if self._enabled_switch is not None:
                return self._enabled_switch.get_active()
            return nav.get_is_enabled()

        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.KB_GROUP_STRUCTURAL_NAVIGATION,
                getter=nav.get_is_enabled,
                setter=nav.set_is_enabled,
                prefs_key=structural_navigator.StructuralNavigator.KEY_ENABLED,
                apply_immediately=False,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTOMATIC_FOCUS_MODE,
                getter=nav.get_triggers_focus_mode,
                setter=nav.set_triggers_focus_mode,
                prefs_key=structural_navigator.StructuralNavigator.KEY_TRIGGERS_FOCUS_MODE,
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.STRUCTURAL_NAVIGATION_WRAP_AROUND,
                getter=nav.get_navigation_wraps,
                setter=nav.set_navigation_wraps,
                prefs_key=structural_navigator.StructuralNavigator.KEY_WRAPS,
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.STRUCTURAL_NAVIGATION_LARGE_OBJECT_LENGTH,
                minimum=1,
                maximum=500,
                getter=nav.get_large_object_text_length,
                setter=nav.set_large_object_text_length,
                prefs_key=structural_navigator.StructuralNavigator.KEY_LARGE_OBJECT_TEXT_LENGTH,
                determine_sensitivity=is_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.STRUCTURAL_NAVIGATION_SKIP_UNLABELED_IMAGES,
                getter=nav.get_skip_unlabeled_images,
                setter=nav.set_skip_unlabeled_images,
                prefs_key=structural_navigator.StructuralNavigator.KEY_SKIP_UNLABELED_IMAGES,
                determine_sensitivity=is_enabled,
            ),
        ]
        info = (
            f"{guilabels.STRUCTURAL_NAVIGATION_INFO}\n\n{guilabels.AUTOMATIC_FOCUS_MODE_INFO}"
            f"\n\n{guilabels.LARGE_OBJECT_INFO}"
        )
        super().__init__(guilabels.KB_GROUP_STRUCTURAL_NAVIGATION, controls, info_message=info)

        self._enabled_switch = self._widgets[0]


class TableNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for table navigation settings within the Documents page."""

    _gsettings_schema = "table-navigation"

    def __init__(self) -> None:
        nav = table_navigator.get_navigator()

        # Child controls need to check the enabled switch's UI state (not runtime state)
        # because the enabled switch has apply_immediately=False.
        self._enabled_switch: Gtk.Switch | None = None

        def is_enabled() -> bool:
            if self._enabled_switch is not None:
                return self._enabled_switch.get_active()
            return nav.get_is_enabled()

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.KB_GROUP_TABLE_NAVIGATION,
                getter=nav.get_is_enabled,
                setter=nav.set_is_enabled,
                prefs_key=table_navigator.TableNavigator.KEY_ENABLED,
                apply_immediately=False,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.TABLE_SKIP_BLANK_CELLS,
                getter=nav.get_skip_blank_cells,
                setter=nav.set_skip_blank_cells,
                prefs_key=table_navigator.TableNavigator.KEY_SKIP_BLANK_CELLS,
                determine_sensitivity=is_enabled,
            ),
        ]
        super().__init__(guilabels.KB_GROUP_TABLE_NAVIGATION, controls)

        self._enabled_switch = self._widgets[0]


class NativeNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for native navigation settings within the Documents page."""

    _gsettings_schema = "document"

    def __init__(self, presenter: DocumentPresenter) -> None:
        self._presenter = presenter
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTOMATIC_FOCUS_MODE,
                getter=presenter.get_native_nav_triggers_focus_mode,
                setter=presenter.set_native_nav_triggers_focus_mode,
                prefs_key=document_presenter.DocumentPresenter.KEY_NATIVE_NAV_TRIGGERS_FOCUS_MODE,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTO_STICKY_FOCUS_MODE,
                getter=presenter.get_auto_sticky_focus_mode_for_web_apps,
                setter=presenter.set_auto_sticky_focus_mode_for_web_apps,
                prefs_key=document_presenter.DocumentPresenter.KEY_AUTO_STICKY_FOCUS_MODE,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.FIND_SPEAK_RESULTS,
                getter=presenter.get_speak_find_results,
                setter=presenter.set_speak_find_results,
                member_of=guilabels.FIND_OPTIONS,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.FIND_ONLY_SPEAK_CHANGED_LINES,
                getter=presenter.get_only_speak_changed_lines,
                setter=presenter.set_only_speak_changed_lines,
                determine_sensitivity=presenter.get_speak_find_results,
                member_of=guilabels.FIND_OPTIONS,
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.FIND_MINIMUM_MATCH_LENGTH,
                minimum=0,
                maximum=20,
                getter=presenter.get_find_results_minimum_length,
                setter=presenter.set_find_results_minimum_length,
                prefs_key=document_presenter.DocumentPresenter.KEY_FIND_RESULTS_MINIMUM_LENGTH,
                member_of=guilabels.FIND_OPTIONS,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.READ_PAGE_UPON_LOAD,
                getter=presenter.get_say_all_on_load,
                setter=presenter.set_say_all_on_load,
                prefs_key=document_presenter.DocumentPresenter.KEY_SAY_ALL_ON_LOAD,
                member_of=guilabels.PAGE_LOAD,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.PAGE_SUMMARY_UPON_LOAD,
                getter=presenter.get_page_summary_on_load,
                setter=presenter.set_page_summary_on_load,
                prefs_key=document_presenter.DocumentPresenter.KEY_PAGE_SUMMARY_ON_LOAD,
                member_of=guilabels.PAGE_LOAD,
            ),
        ]
        info = (
            f"{guilabels.NATIVE_NAVIGATION_INFO}\n\n"
            f"{guilabels.AUTOMATIC_FOCUS_MODE_INFO}\n\n"
            f"{guilabels.AUTO_STICKY_FOCUS_MODE_INFO}"
        )
        super().__init__(guilabels.NATIVE_NAVIGATION, controls, info_message=info)

    def save_settings(self, profile: str = "", app_name: str = "") -> dict[str, Any]:
        """Save settings, writing the find-results enum from the presenter."""

        result = super().save_settings(profile, app_name)
        verbosity = self._presenter.get_find_results_verbosity_name()
        result[document_presenter.DocumentPresenter.KEY_FIND_RESULTS_VERBOSITY] = verbosity
        self._write_gsettings(
            {document_presenter.DocumentPresenter.KEY_FIND_RESULTS_VERBOSITY: verbosity},
            profile,
            app_name,
        )
        return result


class DocumentPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """Main document preferences grid with categorized navigation settings."""

    def __init__(
        self,
        presenter: DocumentPresenter,
        title_change_callback: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(guilabels.DOCUMENTS)
        self._presenter = presenter
        self._initializing = True
        self._title_change_callback = title_change_callback

        self._caret_grid = CaretNavigationPreferencesGrid()
        self._structural_grid = StructuralNavigationPreferencesGrid()
        self._table_grid = TableNavigationPreferencesGrid()
        self._native_grid = NativeNavigationPreferencesGrid(presenter)
        self._math_grid = math_presenter.get_presenter().create_preferences_grid()

        self._build()
        self._initializing = False

    def _build(self) -> None:
        categories = [
            (guilabels.KB_GROUP_CARET_NAVIGATION, "caret", self._caret_grid),
            (guilabels.KB_GROUP_STRUCTURAL_NAVIGATION, "structural", self._structural_grid),
            (guilabels.KB_GROUP_TABLE_NAVIGATION, "table", self._table_grid),
            (guilabels.NATIVE_NAVIGATION, "native", self._native_grid),
            (guilabels.MATH_PRESENTATION, "math", self._math_grid),
        ]

        if not math_presenter.get_presenter().is_available():
            categories.remove((guilabels.MATH_PRESENTATION, "math", self._math_grid))

        _enable_listbox, stack, _categories_listbox = self._create_multi_page_stack(
            enable_label=None,
            enable_getter=None,
            enable_setter=None,
            categories=categories,
            title_change_callback=self._title_change_callback,
            main_title=guilabels.DOCUMENTS,
        )

        self.attach(stack, 0, 0, 1, 1)

    def on_becoming_visible(self) -> None:
        """Reset to the categories view when this grid becomes visible."""

        self.multipage_on_becoming_visible()

    def reload(self) -> None:
        """Reload all child grids."""

        self._initializing = True
        self._has_unsaved_changes = False
        self._caret_grid.reload()
        self._structural_grid.reload()
        self._table_grid.reload()
        self._native_grid.reload()
        self._math_grid.reload()
        self._initializing = False

    def save_settings(self, profile: str = "", app_name: str = "") -> dict:
        """Save all settings from child grids."""

        result = {}
        result.update(self._caret_grid.save_settings(profile, app_name))
        result.update(self._structural_grid.save_settings(profile, app_name))
        result.update(self._table_grid.save_settings(profile, app_name))
        result.update(self._native_grid.save_settings(profile, app_name))
        result.update(self._math_grid.save_settings(profile, app_name))

        return result

    def has_changes(self) -> bool:
        """Check if any child grid has changes."""

        return (
            self._has_unsaved_changes
            or self._caret_grid.has_changes()
            or self._structural_grid.has_changes()
            or self._table_grid.has_changes()
            or self._native_grid.has_changes()
            or self._math_grid.has_changes()
        )

    def refresh(self) -> None:
        """Refresh all child grids."""

        self._initializing = True
        self._caret_grid.refresh()
        self._structural_grid.refresh()
        self._table_grid.refresh()
        self._native_grid.refresh()
        self._math_grid.refresh()
        self._initializing = False
