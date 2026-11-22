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

from . import guilabels, preferences_grid_base
from .document_presenter_settings import DocumentSettings
from .help_metadata import (
    PreferenceCategoryDoc,
    PreferenceControlDoc,
    PreferencePanelDoc,
    PreferenceValueDoc,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    import gi

    from .caret_navigator_preferences_grid import CaretNavigationPreferencesGrid
    from .document_presenter import DocumentPresenter
    from .math_presenter_preferences_grid import MathPreferencesGrid
    from .structural_navigator_preferences_grid import StructuralNavigationPreferencesGrid
    from .table_navigator_preferences_grid import TableNavigationPreferencesGrid

    gi.require_version("Gtk", "3.0")


class NativeNavigationPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for native navigation settings within the Documents page."""

    _gsettings_schema = "document"

    @classmethod
    def get_documentation(cls) -> PreferencePanelDoc:
        """Return documentation metadata for native navigation preferences."""

        return PreferencePanelDoc(
            title=guilabels.NATIVE_NAVIGATION,
            panel_id="document_presenter.native-navigation",
            link_summary=(
                "Configure automatic focus mode, find results, and page-load behavior for "
                "application-provided navigation."
            ),
            target="documents.native-navigation",
            schema="document",
            controls=(
                PreferenceControlDoc(
                    label=guilabels.AUTOMATIC_FOCUS_MODE,
                    kind="switch",
                    target="documents.native-focus-mode",
                    summary=(
                        "Controls whether Orca switches to focus mode when native "
                        "navigation, such as Tab or Shift+Tab, lands on an interactive widget."
                    ),
                    schema="document",
                    key=DocumentSettings.KEY_NATIVE_NAV_TRIGGERS_FOCUS_MODE,
                ),
                PreferenceControlDoc(
                    label=guilabels.AUTO_STICKY_FOCUS_MODE,
                    kind="switch",
                    target="documents.sticky-focus-mode",
                    summary=(
                        "Starts web applications, including desktop applications built with "
                        "Electron, in sticky focus mode so their own keyboard interactions "
                        "work."
                    ),
                    schema="document",
                    key=DocumentSettings.KEY_AUTO_STICKY_FOCUS_MODE,
                ),
                PreferenceControlDoc(
                    label=guilabels.FIND_OPTIONS,
                    kind="group",
                    summary=(
                        "Controls what Orca speaks while you use an application's Find toolbar."
                    ),
                    controls=(
                        PreferenceControlDoc(
                            label=guilabels.FIND_SPEAK_RESULTS,
                            kind="switch",
                            schema="document",
                            key=DocumentSettings.KEY_FIND_RESULTS_VERBOSITY,
                            default_labels=(PreferenceValueDoc("on", "all"),),
                            summary=(
                                "Controls whether Orca speaks the line containing each find result."
                            ),
                        ),
                        PreferenceControlDoc(
                            label=guilabels.FIND_ONLY_SPEAK_CHANGED_LINES,
                            kind="switch",
                            schema="document",
                            key=DocumentSettings.KEY_FIND_RESULTS_VERBOSITY,
                            default_labels=(PreferenceValueDoc("off", "all"),),
                            summary=(
                                "Controls whether Orca speaks a find result only when it is "
                                "on a different line than the previous result."
                            ),
                        ),
                        PreferenceControlDoc(
                            label=guilabels.FIND_MINIMUM_MATCH_LENGTH,
                            kind="integer",
                            summary=(
                                "Sets the minimum number of matching characters required "
                                "before Orca speaks the find result."
                            ),
                            schema="document",
                            key=(DocumentSettings.KEY_FIND_RESULTS_MINIMUM_LENGTH),
                            minimum="0",
                            maximum="20",
                        ),
                    ),
                ),
                PreferenceControlDoc(
                    label=guilabels.PAGE_LOAD,
                    kind="group",
                    summary=(
                        "Controls what Orca does when a document or web page finishes loading."
                    ),
                    controls=(
                        PreferenceControlDoc(
                            label=guilabels.READ_PAGE_UPON_LOAD,
                            kind="switch",
                            summary=(
                                "Controls whether Orca automatically performs Say All when "
                                "a document or web page first loads."
                            ),
                            schema="document",
                            key=DocumentSettings.KEY_SAY_ALL_ON_LOAD,
                        ),
                        PreferenceControlDoc(
                            label=guilabels.PAGE_SUMMARY_UPON_LOAD,
                            kind="switch",
                            summary=(
                                "Controls whether Orca presents a summary, such as the "
                                "number of headings, landmarks, and links, when a document "
                                "or web page first loads."
                            ),
                            schema="document",
                            key=DocumentSettings.KEY_PAGE_SUMMARY_ON_LOAD,
                        ),
                    ),
                ),
            ),
        )

    def __init__(self, presenter: DocumentPresenter) -> None:
        self._presenter = presenter
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTOMATIC_FOCUS_MODE,
                getter=presenter.get_native_nav_triggers_focus_mode,
                setter=presenter.set_native_nav_triggers_focus_mode,
                prefs_key=DocumentSettings.KEY_NATIVE_NAV_TRIGGERS_FOCUS_MODE,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.AUTO_STICKY_FOCUS_MODE,
                getter=presenter.get_auto_sticky_focus_mode_for_web_apps,
                setter=presenter.set_auto_sticky_focus_mode_for_web_apps,
                prefs_key=DocumentSettings.KEY_AUTO_STICKY_FOCUS_MODE,
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
                prefs_key=DocumentSettings.KEY_FIND_RESULTS_MINIMUM_LENGTH,
                member_of=guilabels.FIND_OPTIONS,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.READ_PAGE_UPON_LOAD,
                getter=presenter.get_say_all_on_load,
                setter=presenter.set_say_all_on_load,
                prefs_key=DocumentSettings.KEY_SAY_ALL_ON_LOAD,
                member_of=guilabels.PAGE_LOAD,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.PAGE_SUMMARY_UPON_LOAD,
                getter=presenter.get_page_summary_on_load,
                setter=presenter.set_page_summary_on_load,
                prefs_key=DocumentSettings.KEY_PAGE_SUMMARY_ON_LOAD,
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
        result[DocumentSettings.KEY_FIND_RESULTS_VERBOSITY] = verbosity
        self._write_gsettings(
            {DocumentSettings.KEY_FIND_RESULTS_VERBOSITY: verbosity},
            profile,
            app_name,
        )
        return result


class DocumentPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """Main document preferences grid with categorized navigation settings."""

    @classmethod
    def get_documentation(cls) -> PreferencePanelDoc:
        """Return documentation metadata for the documents preferences landing page."""

        return PreferencePanelDoc(
            title=guilabels.DOCUMENTS,
            panel_id="document_presenter.documents",
            category=PreferenceCategoryDoc(
                category_id="documents",
                title="Documents",
                description=(
                    "Configure navigation and presentation of documents, web pages, tables, and "
                    "mathematical content."
                ),
                panels=(
                    "document_presenter.documents",
                    "document_presenter.caret-navigation",
                    "document_presenter.structural-navigation",
                    "document_presenter.table-navigation",
                    "document_presenter.native-navigation",
                    "math_presenter.math-presentation",
                ),
            ),
            target="documents",
            show_available_settings=False,
            controls=(
                PreferenceControlDoc(
                    label=guilabels.KB_GROUP_CARET_NAVIGATION,
                    kind="page",
                    summary="Opens settings for caret navigation in document content.",
                ),
                PreferenceControlDoc(
                    label=guilabels.KB_GROUP_STRUCTURAL_NAVIGATION,
                    kind="page",
                    summary=(
                        "Opens settings for navigation by headings, landmarks, links, "
                        "and other structures."
                    ),
                ),
                PreferenceControlDoc(
                    label=guilabels.KB_GROUP_TABLE_NAVIGATION,
                    kind="page",
                    summary=(
                        "Opens settings for table navigation in documents and application tables."
                    ),
                ),
                PreferenceControlDoc(
                    label=guilabels.NATIVE_NAVIGATION,
                    kind="page",
                    summary=(
                        "Opens settings for application-provided navigation, find results, "
                        "and page loading."
                    ),
                ),
                PreferenceControlDoc(
                    label=guilabels.MATH_PRESENTATION,
                    kind="page",
                    summary="Opens settings for presenting and navigating math content.",
                ),
            ),
        )

    def __init__(
        self,
        presenter: DocumentPresenter,
        caret_grid: CaretNavigationPreferencesGrid,
        structural_grid: StructuralNavigationPreferencesGrid,
        table_grid: TableNavigationPreferencesGrid,
        math_grid: MathPreferencesGrid | None,
        title_change_callback: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(guilabels.DOCUMENTS)
        self._presenter = presenter
        self._initializing = True
        self._title_change_callback = title_change_callback

        self._caret_grid = caret_grid
        self._structural_grid = structural_grid
        self._table_grid = table_grid
        self._native_grid = NativeNavigationPreferencesGrid(presenter)
        self._math_grid = math_grid
        self._grids: list[preferences_grid_base.PreferencesGridBase] = [
            caret_grid,
            structural_grid,
            table_grid,
            self._native_grid,
        ]
        if math_grid is not None:
            self._grids.append(math_grid)

        self._build()
        self._initializing = False

    def _build(self) -> None:
        categories: list[tuple[str, str, preferences_grid_base.PreferencesGridBase]] = [
            (guilabels.KB_GROUP_CARET_NAVIGATION, "caret", self._caret_grid),
            (guilabels.KB_GROUP_STRUCTURAL_NAVIGATION, "structural", self._structural_grid),
            (guilabels.KB_GROUP_TABLE_NAVIGATION, "table", self._table_grid),
            (guilabels.NATIVE_NAVIGATION, "native", self._native_grid),
        ]

        if self._math_grid is not None:
            categories.append((guilabels.MATH_PRESENTATION, "math", self._math_grid))

        _enable_listbox, stack, _categories_listbox = self._create_child_grid_preferences_stack(
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
        for grid in self._grids:
            grid.reload()
        self._initializing = False

    def save_settings(self, profile: str = "", app_name: str = "") -> dict:
        """Save all settings from child grids."""

        result = {}
        for grid in self._grids:
            result.update(grid.save_settings(profile, app_name))

        return result

    def has_changes(self) -> bool:
        """Check if any child grid has changes."""

        return self._has_unsaved_changes or any(grid.has_changes() for grid in self._grids)

    def refresh(self) -> None:
        """Refresh all child grids."""

        self._initializing = True
        for grid in self._grids:
            grid.refresh()
        self._initializing = False
