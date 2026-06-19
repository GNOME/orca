# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches

"""Preferences grids for speech presentation support."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import (
    gsettings_registry,
    guilabels,
    preferences_grid_base,
    speech_manager,
    speech_presenter,
    text_attribute_manager,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from gi.repository import Gio

    from .speech_presenter import SpeechPresenter


class AnnouncementsPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Container Announcements preferences page."""

    def __init__(self, presenter: SpeechPresenter) -> None:
        (
            _general_prefs,
            _object_details_prefs,
            announcements_prefs,
        ) = presenter.get_speech_preferences()

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=pref.label,
                getter=pref.getter,
                setter=pref.setter,
                prefs_key=pref.prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING,
            )
            for pref in announcements_prefs
        ]

        super().__init__(guilabels.ANNOUNCEMENTS, controls)


class ProgressBarsPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Progress Bars preferences page."""

    def __init__(self, presenter: SpeechPresenter) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_SPEAK_UPDATES,
                getter=presenter.get_speak_progress_bar_updates,
                setter=presenter.set_speak_progress_bar_updates,
                prefs_key=speech_presenter.SpeechPresenter.KEY_SPEAK_PROGRESS_BAR_UPDATES,
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.GENERAL_FREQUENCY_SECS,
                getter=presenter.get_progress_bar_speech_interval,
                setter=presenter.set_progress_bar_speech_interval,
                prefs_key=speech_presenter.SpeechPresenter.KEY_PROGRESS_BAR_SPEECH_INTERVAL,
                minimum=0,
                maximum=100,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_APPLIES_TO,
                getter=presenter.get_progress_bar_speech_verbosity,
                setter=presenter.set_progress_bar_speech_verbosity,
                prefs_key=speech_presenter.SpeechPresenter.KEY_PROGRESS_BAR_SPEECH_VERBOSITY,
                options=[
                    guilabels.PROGRESS_BAR_ALL,
                    guilabels.PROGRESS_BAR_APPLICATION,
                    guilabels.PROGRESS_BAR_WINDOW,
                ],
                values=[
                    speech_presenter.ProgressBarVerbosity.ALL.value,
                    speech_presenter.ProgressBarVerbosity.APPLICATION.value,
                    speech_presenter.ProgressBarVerbosity.WINDOW.value,
                ],
            ),
        ]

        super().__init__(guilabels.PROGRESS_BARS, controls)


class VerbosityPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Verbosity preferences page."""

    def __init__(self, presenter: SpeechPresenter) -> None:
        self._presenter = presenter
        (
            general_prefs,
            object_details_prefs,
            _announcements_prefs,
        ) = presenter.get_speech_preferences()

        text_speak_blank_lines = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_SPEAK_BLANK_LINES,
            guilabels.SPEECH_SPEAK_BLANK_LINES,
            presenter.get_speak_blank_lines,
            presenter.set_speak_blank_lines,
        )
        text_speak_misspelled = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_SPEAK_MISSPELLED_INDICATOR,
            guilabels.SPEECH_SPEAK_MISSPELLED_WORD_INDICATOR,
            presenter.get_speak_misspelled_indicator,
            presenter.set_speak_misspelled_indicator,
        )
        text_speak_indentation = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_SPEAK_INDENTATION,
            guilabels.SPEECH_SPEAK_INDENTATION,
            presenter.get_speak_indentation,
            presenter.set_speak_indentation,
        )
        text_indentation_only_if_changed = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_SPEAK_INDENTATION_ONLY_IF_CHANGED,
            guilabels.SPEECH_INDENTATION_ONLY_IF_CHANGED,
            presenter.get_speak_indentation_only_if_changed,
            presenter.set_speak_indentation_only_if_changed,
        )

        self._only_speak_displayed_control = preferences_grid_base.BooleanPreferenceControl(
            label=object_details_prefs[0].label,
            getter=object_details_prefs[0].getter,
            setter=object_details_prefs[0].setter,
            prefs_key=object_details_prefs[0].prefs_key,
            member_of=guilabels.SPEECH_OBJECT_DETAILS,
        )

        self._enable_indentation_control = preferences_grid_base.BooleanPreferenceControl(
            label=text_speak_indentation.label,
            getter=text_speak_indentation.getter,
            setter=text_speak_indentation.setter,
            prefs_key=text_speak_indentation.prefs_key,
            member_of=guilabels.SPEECH_OBJECT_DETAILS,
            determine_sensitivity=self._only_speak_displayed_text_is_off,
        )

        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=general_prefs[0].label,
                getter=general_prefs[0].getter,
                setter=general_prefs[0].setter,
                prefs_key=general_prefs[0].prefs_key,
                member_of=guilabels.GENERAL,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.OBJECT_PRESENTATION_IS_DETAILED,
                getter=presenter._get_verbosity_is_verbose,
                setter=presenter._set_verbosity_from_bool,
                member_of=guilabels.GENERAL,
            ),
            self._only_speak_displayed_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=object_details_prefs[1].label,
                getter=object_details_prefs[1].getter,
                setter=object_details_prefs[1].setter,
                prefs_key=object_details_prefs[1].prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=object_details_prefs[2].label,
                getter=object_details_prefs[2].getter,
                setter=object_details_prefs[2].setter,
                prefs_key=object_details_prefs[2].prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=object_details_prefs[3].label,
                getter=object_details_prefs[3].getter,
                setter=object_details_prefs[3].setter,
                prefs_key=object_details_prefs[3].prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=object_details_prefs[4].label,
                getter=object_details_prefs[4].getter,
                setter=object_details_prefs[4].setter,
                prefs_key=object_details_prefs[4].prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=text_speak_blank_lines.label,
                getter=text_speak_blank_lines.getter,
                setter=text_speak_blank_lines.setter,
                prefs_key=text_speak_blank_lines.prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=text_speak_misspelled.label,
                getter=text_speak_misspelled.getter,
                setter=text_speak_misspelled.setter,
                prefs_key=text_speak_misspelled.prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.TEXT_ATTRIBUTE_CHANGES,
                options=[
                    guilabels.TEXT_ATTRIBUTE_CHANGES_OFF,
                    guilabels.TEXT_ATTRIBUTE_CHANGES_EDITABLE,
                    guilabels.TEXT_ATTRIBUTE_CHANGES_ALWAYS,
                ],
                values=[
                    text_attribute_manager.TextAttributeChangeMode.OFF.value,
                    text_attribute_manager.TextAttributeChangeMode.EDITABLE_ONLY.value,
                    text_attribute_manager.TextAttributeChangeMode.ALWAYS.value,
                ],
                getter=presenter.get_text_attribute_change_mode_as_int,
                setter=presenter.set_text_attribute_change_mode_from_int,
                prefs_key=speech_presenter.SpeechPresenter.KEY_SPEAK_TEXT_ATTRIBUTE_CHANGES,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            self._enable_indentation_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=text_indentation_only_if_changed.label,
                getter=text_indentation_only_if_changed.getter,
                setter=text_indentation_only_if_changed.setter,
                prefs_key=text_indentation_only_if_changed.prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._indentation_enabled,
            ),
        ]

        super().__init__(guilabels.VERBOSITY, controls)

    def save_settings(self, profile: str = "", app_name: str = "") -> dict[str, Any]:
        """Save settings, writing the verbosity-level enum from the presenter."""

        result = super().save_settings(profile, app_name)
        result[speech_presenter.SpeechPresenter.KEY_VERBOSITY_LEVEL] = (
            self._presenter.get_verbosity_level()
        )
        return result

    def _only_speak_displayed_text_is_off(self) -> bool:
        """Returns True if only-speak-displayed-text is off in the UI."""

        only_displayed_widget = self.get_widget_for_control(self._only_speak_displayed_control)
        if only_displayed_widget:
            return not only_displayed_widget.get_active()
        return True

    def _indentation_enabled(self) -> bool:
        """Check if speak indentation is enabled in the UI (widget state, not settings)."""

        if not self._only_speak_displayed_text_is_off():
            return False
        widget = self.get_widget_for_control(self._enable_indentation_control)
        return widget.get_active() if widget else True


class TablesPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Tables preferences page."""

    def __init__(self, presenter: SpeechPresenter) -> None:
        # Table preferences
        table_gui_rows = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_SPEAK_ROW_IN_GUI_TABLE,
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_GUI_TABLES,
            presenter.get_speak_row_in_gui_table,
            presenter.set_speak_row_in_gui_table,
        )
        table_doc_rows = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_SPEAK_ROW_IN_DOCUMENT_TABLE,
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_DOCUMENT_TABLES,
            presenter.get_speak_row_in_document_table,
            presenter.set_speak_row_in_document_table,
        )
        table_spreadsheet_rows = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_SPEAK_ROW_IN_SPREADSHEET,
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_SPREADSHEETS,
            presenter.get_speak_row_in_spreadsheet,
            presenter.set_speak_row_in_spreadsheet,
        )
        table_cell_headers = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_ANNOUNCE_CELL_HEADERS,
            guilabels.TABLE_SPEAK_CELL_HEADER,
            presenter.get_announce_cell_headers,
            presenter.set_announce_cell_headers,
        )
        table_cell_coords = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_ANNOUNCE_CELL_COORDINATES,
            guilabels.TABLE_SPEAK_CELL_COORDINATES,
            presenter.get_announce_cell_coordinates,
            presenter.set_announce_cell_coordinates,
        )
        table_spreadsheet_coords = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_ANNOUNCE_SPREADSHEET_CELL_COORDINATES,
            guilabels.SPREADSHEET_SPEAK_CELL_COORDINATES,
            presenter.get_announce_spreadsheet_cell_coordinates,
            presenter.set_announce_spreadsheet_cell_coordinates,
        )
        table_cell_span = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_ANNOUNCE_CELL_SPAN,
            guilabels.TABLE_SPEAK_CELL_SPANS,
            presenter.get_announce_cell_span,
            presenter.set_announce_cell_span,
        )
        table_selected_range = speech_presenter.SpeechPreference(
            speech_presenter.SpeechPresenter.KEY_ALWAYS_ANNOUNCE_SELECTED_RANGE_IN_SPREADSHEET,
            guilabels.SPREADSHEET_SPEAK_SELECTED_RANGE,
            presenter.get_always_announce_selected_range_in_spreadsheet,
            presenter.set_always_announce_selected_range_in_spreadsheet,
        )

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=table_gui_rows.label,
                getter=table_gui_rows.getter,
                setter=table_gui_rows.setter,
                prefs_key=table_gui_rows.prefs_key,
                member_of=guilabels.TABLE_ROW_NAVIGATION,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_doc_rows.label,
                getter=table_doc_rows.getter,
                setter=table_doc_rows.setter,
                prefs_key=table_doc_rows.prefs_key,
                member_of=guilabels.TABLE_ROW_NAVIGATION,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_spreadsheet_rows.label,
                getter=table_spreadsheet_rows.getter,
                setter=table_spreadsheet_rows.setter,
                prefs_key=table_spreadsheet_rows.prefs_key,
                member_of=guilabels.TABLE_ROW_NAVIGATION,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_cell_headers.label,
                getter=table_cell_headers.getter,
                setter=table_cell_headers.setter,
                prefs_key=table_cell_headers.prefs_key,
                member_of=guilabels.TABLE_CELL_NAVIGATION,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_cell_coords.label,
                getter=table_cell_coords.getter,
                setter=table_cell_coords.setter,
                prefs_key=table_cell_coords.prefs_key,
                member_of=guilabels.TABLE_CELL_NAVIGATION,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_spreadsheet_coords.label,
                getter=table_spreadsheet_coords.getter,
                setter=table_spreadsheet_coords.setter,
                prefs_key=table_spreadsheet_coords.prefs_key,
                member_of=guilabels.TABLE_CELL_NAVIGATION,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_cell_span.label,
                getter=table_cell_span.getter,
                setter=table_cell_span.setter,
                prefs_key=table_cell_span.prefs_key,
                member_of=guilabels.TABLE_CELL_NAVIGATION,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_selected_range.label,
                getter=table_selected_range.getter,
                setter=table_selected_range.setter,
                prefs_key=table_selected_range.prefs_key,
                member_of=guilabels.TABLE_CELL_NAVIGATION,
            ),
        ]

        super().__init__(guilabels.TABLES, controls)


class SpeechOSDPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the speech on-screen display preferences page."""

    def __init__(self, presenter: SpeechPresenter) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.SPEECH_MONITOR_FONT_SIZE,
                getter=presenter.get_monitor_font_size,
                setter=presenter.set_monitor_font_size,
                prefs_key=speech_presenter.SpeechPresenter.KEY_MONITOR_FONT_SIZE,
                minimum=8,
                maximum=72,
                apply_immediately=True,
            ),
            preferences_grid_base.ColorPreferenceControl(
                label=guilabels.SPEECH_MONITOR_FOREGROUND,
                getter=presenter.get_monitor_foreground,
                setter=presenter.set_monitor_foreground,
                prefs_key=speech_presenter.SpeechPresenter.KEY_MONITOR_FOREGROUND,
            ),
            preferences_grid_base.ColorPreferenceControl(
                label=guilabels.SPEECH_MONITOR_BACKGROUND,
                getter=presenter.get_monitor_background,
                setter=presenter.set_monitor_background,
                prefs_key=speech_presenter.SpeechPresenter.KEY_MONITOR_BACKGROUND,
            ),
        ]

        super().__init__(
            guilabels.ON_SCREEN_DISPLAY,
            controls,
            info_message=guilabels.SPEECH_MONITOR_INFO,
        )


class SpeechPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """Main speech preferences grid with enable toggle and categorized settings."""

    _VOICE_PROPERTY_MAP = (
        ("rate", "rate", "i", 50),
        ("average-pitch", "pitch", "d", 5.0),
        ("pitch-range", "pitch-range", "d", 5.0),
        ("gain", "volume", "d", 10.0),
        ("established", "established", "b", False),
    )

    _VOICE_FAMILY_MAP = (
        ("name", "family-name"),
        ("lang", "family-lang"),
        ("dialect", "family-dialect"),
        ("gender", "family-gender"),
        ("variant", "family-variant"),
    )

    def __init__(
        self,
        presenter: SpeechPresenter,
        title_change_callback: Callable[[str], None] | None = None,
        app_name: str = "",
    ) -> None:
        super().__init__(guilabels.SPEECH)
        self._presenter = presenter
        self._initializing = True
        self._title_change_callback = title_change_callback

        manager = speech_manager.get_manager()

        # Create child grids (but don't attach them yet - they'll go in the stack detail)
        self._voices_grid = manager.create_voices_preferences_grid(app_name=app_name)
        self._voice_types_grid = manager.create_voice_types_preferences_grid(self._voices_grid)
        self._verbosity_grid = VerbosityPreferencesGrid(presenter)
        self._tables_grid = TablesPreferencesGrid(presenter)
        self._progress_bars_grid = ProgressBarsPreferencesGrid(presenter)
        self._announcements_grid = AnnouncementsPreferencesGrid(presenter)
        self._osd_grid = SpeechOSDPreferencesGrid(presenter)

        self._build()
        self._initializing = False

    def _build(self) -> None:
        row = 0

        manager = speech_manager.get_manager()

        categories = [
            (guilabels.VOICE_GLOBAL_VOICE_SETTINGS, "voice", self._voices_grid),
            (guilabels.LANGUAGE_VOICE_SETTINGS, "voice-sets", self._voice_types_grid),
            (guilabels.VERBOSITY, "verbosity", self._verbosity_grid),
            (guilabels.TABLES, "tables", self._tables_grid),
            (guilabels.PROGRESS_BARS, "progress-bars", self._progress_bars_grid),
            (guilabels.ANNOUNCEMENTS, "announcements", self._announcements_grid),
            (guilabels.ON_SCREEN_DISPLAY, "osd", self._osd_grid),
        ]

        enable_listbox, stack, _categories_listbox = self._create_multi_page_stack(
            enable_label=guilabels.SPEECH_ENABLE_SPEECH,
            enable_getter=manager.get_speech_is_enabled,
            enable_setter=manager.set_speech_is_enabled,
            categories=categories,
            title_change_callback=self._title_change_callback,
            main_title=guilabels.SPEECH,
        )

        self.attach(enable_listbox, 0, row, 1, 1)
        row += 1
        self.attach(stack, 0, row, 1, 1)

    def on_becoming_visible(self) -> None:
        """Reset to the categories view when this grid becomes visible."""

        self.multipage_on_becoming_visible()

    def reload(self) -> None:
        """Reload all child grids."""

        self._initializing = True
        self._has_unsaved_changes = False
        self._voices_grid.reload()
        self._voice_types_grid.reload()
        self._verbosity_grid.reload()
        self._tables_grid.reload()
        self._progress_bars_grid.reload()
        self._announcements_grid.reload()
        self._osd_grid.reload()
        self._initializing = False

    def _save_voice(self, voice_gs: Gio.Settings, voice_data: dict, skip_defaults: bool) -> None:
        """Save voice properties and family for a profile."""

        for acss_key, gs_key, gs_type, default in self._VOICE_PROPERTY_MAP:
            if acss_key not in voice_data:
                continue
            value = voice_data[acss_key]
            if skip_defaults:
                is_default = (
                    (gs_type == "i" and int(value) == default)
                    or (gs_type == "d" and float(value) == default)
                    or (gs_type == "b" and bool(value) == default)
                )
                if is_default:
                    voice_gs.reset(gs_key)
                    continue
            if gs_type == "i":
                voice_gs.set_int(gs_key, int(value))
            elif gs_type == "d":
                voice_gs.set_double(gs_key, float(value))
            else:
                voice_gs.set_boolean(gs_key, bool(value))

        family = voice_data.get("family", {})
        if isinstance(family, dict):
            for json_field, gs_key in self._VOICE_FAMILY_MAP:
                val = family.get(json_field)
                if val is not None and str(val):
                    voice_gs.set_string(gs_key, str(val))

    def _save_app_voice(
        self,
        voice_gs: Gio.Settings,
        voice_data: dict,
        profile_voice_gs: Gio.Settings,
        default_voice_gs: Gio.Settings | None,
    ) -> None:
        """Save voice properties for an app, only writing genuine overrides."""

        for acss_key, gs_key, gs_type, _default in self._VOICE_PROPERTY_MAP:
            if acss_key not in voice_data:
                continue
            value = voice_data[acss_key]
            profile_value = self._get_effective_voice_value(
                gs_key,
                profile_voice_gs,
                default_voice_gs,
                _default,
            )
            if gs_type == "i":
                matches = int(value) == profile_value
            elif gs_type == "d":
                matches = float(value) == profile_value
            else:
                matches = bool(value) == profile_value
            if matches:
                voice_gs.reset(gs_key)
            elif gs_type == "i":
                voice_gs.set_int(gs_key, int(value))
            elif gs_type == "d":
                voice_gs.set_double(gs_key, float(value))
            else:
                voice_gs.set_boolean(gs_key, bool(value))

        family = voice_data.get("family", {})
        if isinstance(family, dict):
            for json_field, gs_key in self._VOICE_FAMILY_MAP:
                val = family.get(json_field)
                if val is None or not str(val):
                    continue
                profile_val = self._get_effective_voice_value(
                    gs_key,
                    profile_voice_gs,
                    default_voice_gs,
                    "",
                )
                if str(val) == profile_val:
                    voice_gs.reset(gs_key)
                else:
                    voice_gs.set_string(gs_key, str(val))

    @staticmethod
    def _get_effective_voice_value(
        gs_key: str,
        profile_gs: Gio.Settings,
        default_gs: Gio.Settings | None,
        fallback: Any,
    ) -> Any:
        """Returns the effective profile voice value, checking default profile if needed."""

        if (val := profile_gs.get_user_value(gs_key)) is not None:
            return val.unpack()
        if default_gs is not None and (val := default_gs.get_user_value(gs_key)) is not None:
            return val.unpack()
        return fallback

    def save_settings(self, profile: str = "", app_name: str = "") -> dict:
        """Save all settings from child grids."""

        assert self._multipage_enable_switch is not None
        result: dict[str, Any] = {}
        result["enable"] = self._multipage_enable_switch.get_active()
        result.update(self._voices_grid.save_settings())
        result.update(self._voice_types_grid.save_settings())
        result.update(self._verbosity_grid.save_settings())
        result.update(self._tables_grid.save_settings())
        result.update(self._progress_bars_grid.save_settings())
        result.update(self._announcements_grid.save_settings())
        result.update(self._osd_grid.save_settings())

        if profile:
            registry = gsettings_registry.get_registry()
            p = registry.sanitize_gsettings_path(profile)
            skip = not app_name and profile == "default"

            # For app saves, remove synthesizer from result before save_schema
            # so it doesn't get written to the app dconf path unconditionally.
            # save_schema writes all matched keys, which would shadow the
            # profile-level synthesizer even when the user didn't change it.
            app_synth = result.pop("synthesizer", None) if app_name else None
            app_server = result.pop("speech-server", None) if app_name else None

            registry.save_schema("speech", result, p, app_name, skip)

            voices = result.get("voices", {})
            for voice_type, voice_data in voices.items():
                if not voice_data:
                    continue
                sub = gsettings_registry.get_registry().voice_set_sub_path(voice_type)
                voice_gs = registry.get_settings("voice", p, sub, app_name)
                if voice_gs is None:
                    continue
                if app_name:
                    profile_voice_gs = registry.get_settings("voice", p, sub)
                    if profile_voice_gs is None:
                        continue
                    default_voice_gs = None
                    if p != "default":
                        default_voice_gs = registry.get_settings("voice", "default", sub)
                    self._save_app_voice(
                        voice_gs,
                        voice_data,
                        profile_voice_gs,
                        default_voice_gs,
                    )
                else:
                    self._save_voice(voice_gs, voice_data, skip)

            if app_name and app_synth is not None:
                profile_synth = registry.layered_lookup("speech", "synthesizer", "s")
                if speech_gs := registry.get_settings("speech", p, "speech", app_name):
                    if app_synth != profile_synth:
                        speech_gs.set_string("synthesizer", app_synth)
                        speech_gs.set_string("speech-server", app_server or "")
                    elif speech_gs.get_user_value("synthesizer") is not None:
                        speech_gs.reset("synthesizer")
                        speech_gs.reset("speech-server")

        return result

    def has_changes(self) -> bool:
        """Return True if there are unsaved changes."""

        return (
            self._has_unsaved_changes
            or self._voices_grid.has_changes()
            or self._voice_types_grid.has_changes()
            or self._verbosity_grid.has_changes()
            or self._tables_grid.has_changes()
            or self._progress_bars_grid.has_changes()
            or self._announcements_grid.has_changes()
            or self._osd_grid.has_changes()
        )

    def refresh(self) -> None:
        """Refresh all child grids."""

        self._initializing = True
        self._voices_grid.refresh()
        self._voice_types_grid.refresh()
        self._verbosity_grid.refresh()
        self._tables_grid.refresh()
        self._progress_bars_grid.refresh()
        self._announcements_grid.refresh()
        self._osd_grid.refresh()
        self._initializing = False
