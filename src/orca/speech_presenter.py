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

"""Configures verbosity settings and adjusts strings for speech presentation."""

from __future__ import annotations

import re
import string
import time
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Gtk", "3.0")

from . import (
    cmdnames,
    dbus_service,
    debug,
    document_presenter,
    focus_manager,
    gsettings_registry,
    guilabels,
    input_event,
    keybindings,
    messages,
    object_properties,
    phonnames,
    preferences_grid_base,
    presentation_manager,
    pronunciation_dictionary_manager,
    say_all_presenter,
    speech_generator,
    speech_manager,
    speech_monitor,
    speechserver,
)
from .acss import ACSS
from .ax_document import AXDocument
from .ax_hypertext import AXHypertext
from .ax_text import AXText, AXTextAttribute
from .ax_utilities import AXUtilities
from .command import Command, KeyboardCommand
from .extension import Extension
from .speechserver import VoiceFamily
from .text_attribute_manager import TextAttributeChangeMode

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from .generator import WhereAmI
    from .speech_generator import SpeechGeneratorContext

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi, Gio

    from .input_event import KeyboardEvent
    from .scripts import default


class VerbosityLevel(Enum):
    """Verbosity level enumeration."""

    BRIEF = 0
    VERBOSE = 1

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.ProgressBarVerbosity",
    values={"all": 0, "application": 1, "window": 2},
)
class ProgressBarVerbosity(Enum):
    """Progress bar verbosity level enumeration."""

    ALL = 0
    APPLICATION = 1
    WINDOW = 2


@dataclass(frozen=True)
class SpeechPreference:
    """Descriptor for a single preference."""

    prefs_key: str
    label: str
    getter: Callable[[], bool]
    setter: Callable[[bool], bool]


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
                prefs_key=SpeechPresenter.KEY_SPEAK_PROGRESS_BAR_UPDATES,
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.GENERAL_FREQUENCY_SECS,
                getter=presenter.get_progress_bar_speech_interval,
                setter=presenter.set_progress_bar_speech_interval,
                prefs_key=SpeechPresenter.KEY_PROGRESS_BAR_SPEECH_INTERVAL,
                minimum=0,
                maximum=100,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_APPLIES_TO,
                getter=presenter.get_progress_bar_speech_verbosity,
                setter=presenter.set_progress_bar_speech_verbosity,
                prefs_key=SpeechPresenter.KEY_PROGRESS_BAR_SPEECH_VERBOSITY,
                options=[
                    guilabels.PROGRESS_BAR_ALL,
                    guilabels.PROGRESS_BAR_APPLICATION,
                    guilabels.PROGRESS_BAR_WINDOW,
                ],
                values=[
                    ProgressBarVerbosity.ALL.value,
                    ProgressBarVerbosity.APPLICATION.value,
                    ProgressBarVerbosity.WINDOW.value,
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

        text_speak_blank_lines = SpeechPreference(
            SpeechPresenter.KEY_SPEAK_BLANK_LINES,
            guilabels.SPEECH_SPEAK_BLANK_LINES,
            presenter.get_speak_blank_lines,
            presenter.set_speak_blank_lines,
        )
        text_speak_misspelled = SpeechPreference(
            SpeechPresenter.KEY_SPEAK_MISSPELLED_INDICATOR,
            guilabels.SPEECH_SPEAK_MISSPELLED_WORD_INDICATOR,
            presenter.get_speak_misspelled_indicator,
            presenter.set_speak_misspelled_indicator,
        )
        text_speak_indentation = SpeechPreference(
            SpeechPresenter.KEY_SPEAK_INDENTATION_AND_JUSTIFICATION,
            guilabels.SPEECH_SPEAK_INDENTATION_AND_JUSTIFICATION,
            presenter.get_speak_indentation_and_justification,
            presenter.set_speak_indentation_and_justification,
        )
        text_indentation_only_if_changed = SpeechPreference(
            SpeechPresenter.KEY_SPEAK_INDENTATION_ONLY_IF_CHANGED,
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
                    TextAttributeChangeMode.OFF.value,
                    TextAttributeChangeMode.EDITABLE_ONLY.value,
                    TextAttributeChangeMode.ALWAYS.value,
                ],
                getter=presenter.get_text_attribute_change_mode_as_int,
                setter=presenter.set_text_attribute_change_mode_from_int,
                prefs_key=SpeechPresenter.KEY_SPEAK_TEXT_ATTRIBUTE_CHANGES,
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
        result[SpeechPresenter.KEY_VERBOSITY_LEVEL] = self._presenter.get_verbosity_level()
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
        table_gui_rows = SpeechPreference(
            SpeechPresenter.KEY_SPEAK_ROW_IN_GUI_TABLE,
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_GUI_TABLES,
            presenter.get_speak_row_in_gui_table,
            presenter.set_speak_row_in_gui_table,
        )
        table_doc_rows = SpeechPreference(
            SpeechPresenter.KEY_SPEAK_ROW_IN_DOCUMENT_TABLE,
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_DOCUMENT_TABLES,
            presenter.get_speak_row_in_document_table,
            presenter.set_speak_row_in_document_table,
        )
        table_spreadsheet_rows = SpeechPreference(
            SpeechPresenter.KEY_SPEAK_ROW_IN_SPREADSHEET,
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_SPREADSHEETS,
            presenter.get_speak_row_in_spreadsheet,
            presenter.set_speak_row_in_spreadsheet,
        )
        table_cell_headers = SpeechPreference(
            SpeechPresenter.KEY_ANNOUNCE_CELL_HEADERS,
            guilabels.TABLE_SPEAK_CELL_HEADER,
            presenter.get_announce_cell_headers,
            presenter.set_announce_cell_headers,
        )
        table_cell_coords = SpeechPreference(
            SpeechPresenter.KEY_ANNOUNCE_CELL_COORDINATES,
            guilabels.TABLE_SPEAK_CELL_COORDINATES,
            presenter.get_announce_cell_coordinates,
            presenter.set_announce_cell_coordinates,
        )
        table_spreadsheet_coords = SpeechPreference(
            SpeechPresenter.KEY_ANNOUNCE_SPREADSHEET_CELL_COORDINATES,
            guilabels.SPREADSHEET_SPEAK_CELL_COORDINATES,
            presenter.get_announce_spreadsheet_cell_coordinates,
            presenter.set_announce_spreadsheet_cell_coordinates,
        )
        table_cell_span = SpeechPreference(
            SpeechPresenter.KEY_ANNOUNCE_CELL_SPAN,
            guilabels.TABLE_SPEAK_CELL_SPANS,
            presenter.get_announce_cell_span,
            presenter.set_announce_cell_span,
        )
        table_selected_range = SpeechPreference(
            SpeechPresenter.KEY_ALWAYS_ANNOUNCE_SELECTED_RANGE_IN_SPREADSHEET,
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
                prefs_key=SpeechPresenter.KEY_MONITOR_FONT_SIZE,
                minimum=8,
                maximum=72,
                apply_immediately=True,
            ),
            preferences_grid_base.ColorPreferenceControl(
                label=guilabels.SPEECH_MONITOR_FOREGROUND,
                getter=presenter.get_monitor_foreground,
                setter=presenter.set_monitor_foreground,
                prefs_key=SpeechPresenter.KEY_MONITOR_FOREGROUND,
            ),
            preferences_grid_base.ColorPreferenceControl(
                label=guilabels.SPEECH_MONITOR_BACKGROUND,
                getter=presenter.get_monitor_background,
                setter=presenter.set_monitor_background,
                prefs_key=SpeechPresenter.KEY_MONITOR_BACKGROUND,
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


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Speech", name="speech")
class SpeechPresenter(Extension):
    """Configures verbosity settings and adjusts strings for speech presentation."""

    GROUP_LABEL = guilabels.KB_GROUP_SPEECH_VERBOSITY

    _SCHEMA = "speech"

    KEY_SPEAK_MISSPELLED_INDICATOR = "speak-misspelled-indicator"
    KEY_SPEAK_DESCRIPTION = "speak-description"
    KEY_SPEAK_POSITION_IN_SET = "speak-position-in-set"
    KEY_SPEAK_WIDGET_MNEMONIC = "speak-widget-mnemonic"
    KEY_SPEAK_TUTORIAL_MESSAGES = "speak-tutorial-messages"
    KEY_REPEATED_CHARACTER_LIMIT = "repeated-character-limit"
    KEY_SPEAK_BLANK_LINES = "speak-blank-lines"
    KEY_SPEAK_ROW_IN_GUI_TABLE = "speak-row-in-gui-table"
    KEY_SPEAK_ROW_IN_DOCUMENT_TABLE = "speak-row-in-document-table"
    KEY_SPEAK_ROW_IN_SPREADSHEET = "speak-row-in-spreadsheet"
    KEY_ANNOUNCE_CELL_SPAN = "announce-cell-span"
    KEY_ANNOUNCE_CELL_COORDINATES = "announce-cell-coordinates"
    KEY_ANNOUNCE_SPREADSHEET_CELL_COORDINATES = "announce-spreadsheet-cell-coordinates"
    KEY_ALWAYS_ANNOUNCE_SELECTED_RANGE_IN_SPREADSHEET = (
        "always-announce-selected-range-in-spreadsheet"
    )
    KEY_ANNOUNCE_CELL_HEADERS = "announce-cell-headers"
    KEY_ANNOUNCE_ARTICLE = "announce-article"
    KEY_ANNOUNCE_BLOCKQUOTE = "announce-blockquote"
    KEY_ANNOUNCE_CODE_BLOCK = "announce-code-block"
    KEY_ANNOUNCE_FORM = "announce-form"
    KEY_ANNOUNCE_GROUPING = "announce-grouping"
    KEY_ANNOUNCE_LANDMARK = "announce-landmark"
    KEY_ANNOUNCE_LIST = "announce-list"
    KEY_ANNOUNCE_TABLE = "announce-table"
    KEY_ANNOUNCE_TRACKED_CHANGES = "announce-tracked-changes"
    KEY_ONLY_SPEAK_DISPLAYED_TEXT = "only-speak-displayed-text"
    KEY_SPEAK_PROGRESS_BAR_UPDATES = "speak-progress-bar-updates"
    KEY_PROGRESS_BAR_SPEECH_INTERVAL = "progress-bar-speech-interval"
    KEY_PROGRESS_BAR_SPEECH_VERBOSITY = "progress-bar-speech-verbosity"
    KEY_MESSAGES_ARE_DETAILED = "messages-are-detailed"
    KEY_VERBOSITY_LEVEL = "verbosity-level"
    KEY_SPEAK_INDENTATION_AND_JUSTIFICATION = "speak-indentation-and-justification"
    KEY_SPEAK_INDENTATION_ONLY_IF_CHANGED = "speak-indentation-only-if-changed"
    KEY_SPEAK_TEXT_ATTRIBUTE_CHANGES = "speak-text-attribute-changes"
    KEY_MONITOR_FONT_SIZE = "monitor-font-size"
    KEY_MONITOR_FOREGROUND = "monitor-foreground"
    KEY_MONITOR_BACKGROUND = "monitor-background"

    def _get_setting(self, key: str, gtype: str, default: Any) -> Any:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            key,
            gtype,
            default=default,
        )

    def __init__(self) -> None:
        self._last_indentation_description: str = ""
        self._last_error_description: str = ""
        self._monitor: speech_monitor.SpeechMonitor | None = None
        self._monitor_enabled_override: bool | None = None
        self._speech_history: list[tuple[str, str]] = []
        self._group_buffer: list[str] | None = None
        self._progress_bar_cache: dict = {}
        self._text_attribute_change_mode_override: TextAttributeChangeMode | None = None
        super().__init__()

    def _get_commands(self) -> list[Command]:
        """Returns commands for registration."""

        kb_v = keybindings.KeyBinding("v", keybindings.ORCA_MODIFIER_MASK)
        kb_f11 = keybindings.KeyBinding("F11", keybindings.ORCA_MODIFIER_MASK)
        kb_shift_d = keybindings.KeyBinding("d", keybindings.ORCA_SHIFT_MODIFIER_MASK)

        commands_data = [
            (
                "changeNumberStyleHandler",
                self.change_number_style,
                cmdnames.CHANGE_NUMBER_STYLE,
                None,
                None,
            ),
            (
                "toggleSpeechVerbosityHandler",
                self.toggle_verbosity,
                cmdnames.TOGGLE_SPEECH_VERBOSITY,
                kb_v,
                kb_v,
            ),
            (
                "toggleSpeakingIndentationJustificationHandler",
                self.toggle_indentation_and_justification,
                cmdnames.TOGGLE_SPOKEN_INDENTATION_AND_JUSTIFICATION,
                None,
                None,
            ),
            (
                "toggleTableCellReadModeHandler",
                self.toggle_table_cell_reading_mode,
                cmdnames.TOGGLE_TABLE_CELL_READ_MODE,
                kb_f11,
                kb_f11,
            ),
            (
                "toggle_speech_monitor",
                self.toggle_monitor,
                cmdnames.TOGGLE_SPEECH_MONITOR,
                kb_shift_d,
                kb_shift_d,
            ),
            (
                "cycle_text_attribute_change_mode",
                self.cycle_text_attribute_change_mode,
                cmdnames.CYCLE_TEXT_ATTRIBUTE_CHANGE_MODE,
                None,
                None,
            ),
        ]

        return [
            KeyboardCommand(
                name,
                function,
                self.GROUP_LABEL,
                description,
                desktop_keybinding=desktop_kb,
                laptop_keybinding=laptop_kb,
            )
            for name, function, description, desktop_kb, laptop_kb in commands_data
        ]

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_MISSPELLED_INDICATOR,
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak misspelled word indicator",
        migration_key="speakMisspelledIndicator",
    )
    @dbus_service.getter
    def get_speak_misspelled_indicator(self) -> bool:
        """Returns whether the misspelled indicator is spoken."""

        return self._get_setting(self.KEY_SPEAK_MISSPELLED_INDICATOR, "b", True)

    @dbus_service.setter
    def set_speak_misspelled_indicator(self, value: bool) -> bool:
        """Sets whether the misspelled indicator is spoken."""

        msg = f"SPEECH PRESENTER: Setting speak misspelled indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_MISSPELLED_INDICATOR,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_DESCRIPTION,
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak object descriptions",
        migration_key="speakDescription",
    )
    @dbus_service.getter
    def get_speak_description(self) -> bool:
        """Returns whether object descriptions are spoken."""

        return self._get_setting(self.KEY_SPEAK_DESCRIPTION, "b", True)

    @dbus_service.setter
    def set_speak_description(self, value: bool) -> bool:
        """Sets whether object descriptions are spoken."""

        msg = f"SPEECH PRESENTER: Setting speak description to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_DESCRIPTION,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_POSITION_IN_SET,
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak position in set",
        migration_key="enablePositionSpeaking",
    )
    @dbus_service.getter
    def get_speak_position_in_set(self) -> bool:
        """Returns whether the position and set size of objects are spoken."""

        return self._get_setting(self.KEY_SPEAK_POSITION_IN_SET, "b", False)

    @dbus_service.setter
    def set_speak_position_in_set(self, value: bool) -> bool:
        """Sets whether the position and set size of objects are spoken."""

        msg = f"SPEECH PRESENTER: Setting speak position in set to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_POSITION_IN_SET,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_WIDGET_MNEMONIC,
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak widget mnemonics",
        migration_key="enableMnemonicSpeaking",
    )
    @dbus_service.getter
    def get_speak_widget_mnemonic(self) -> bool:
        """Returns whether widget mnemonics are spoken."""

        return self._get_setting(self.KEY_SPEAK_WIDGET_MNEMONIC, "b", True)

    @dbus_service.setter
    def set_speak_widget_mnemonic(self, value: bool) -> bool:
        """Sets whether widget mnemonics are spoken."""

        msg = f"SPEECH PRESENTER: Setting speak widget mnemonics to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_WIDGET_MNEMONIC,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_TUTORIAL_MESSAGES,
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak tutorial messages",
        migration_key="enableTutorialMessages",
    )
    @dbus_service.getter
    def get_speak_tutorial_messages(self) -> bool:
        """Returns whether tutorial messages are spoken."""

        return self._get_setting(self.KEY_SPEAK_TUTORIAL_MESSAGES, "b", True)

    @dbus_service.setter
    def set_speak_tutorial_messages(self, value: bool) -> bool:
        """Sets whether tutorial messages are spoken."""

        msg = f"SPEECH PRESENTER: Setting speak tutorial messages to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_TUTORIAL_MESSAGES,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_REPEATED_CHARACTER_LIMIT,
        schema="speech",
        gtype="i",
        default=4,
        summary="Threshold for repeated character compression",
        migration_key="repeatCharacterLimit",
    )
    @dbus_service.getter
    def get_repeated_character_limit(self) -> int:
        """Returns the count at which repeated, non-alphanumeric symbols will be described."""

        return self._get_setting(self.KEY_REPEATED_CHARACTER_LIMIT, "i", 4)

    @dbus_service.setter
    def set_repeated_character_limit(self, value: int) -> bool:
        """Sets the count at which repeated, non-alphanumeric symbols will be described."""

        msg = f"SPEECH PRESENTER: Setting repeated character limit to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_REPEATED_CHARACTER_LIMIT,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_BLANK_LINES,
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak blank lines",
        migration_key="speakBlankLines",
    )
    @dbus_service.getter
    def get_speak_blank_lines(self) -> bool:
        """Returns whether blank lines will be spoken."""

        return self._get_setting(self.KEY_SPEAK_BLANK_LINES, "b", True)

    @dbus_service.setter
    def set_speak_blank_lines(self, value: bool) -> bool:
        """Sets whether blank lines will be spoken."""

        msg = f"SPEECH PRESENTER: Setting speak blank lines to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_BLANK_LINES,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_ROW_IN_GUI_TABLE,
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak full row in GUI tables",
        migration_key="readFullRowInGUITable",
    )
    @dbus_service.getter
    def get_speak_row_in_gui_table(self) -> bool:
        """Returns whether Up/Down in GUI tables speaks the row or just the cell."""

        return self._get_setting(self.KEY_SPEAK_ROW_IN_GUI_TABLE, "b", True)

    @dbus_service.setter
    def set_speak_row_in_gui_table(self, value: bool) -> bool:
        """Sets whether Up/Down in GUI tables speaks the row or just the cell."""

        msg = f"SPEECH PRESENTER: Setting speak row in GUI table to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_ROW_IN_GUI_TABLE,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_ROW_IN_DOCUMENT_TABLE,
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak full row in document tables",
        migration_key="readFullRowInDocumentTable",
    )
    @dbus_service.getter
    def get_speak_row_in_document_table(self) -> bool:
        """Returns whether Up/Down in text-document tables speaks the row or just the cell."""

        return self._get_setting(self.KEY_SPEAK_ROW_IN_DOCUMENT_TABLE, "b", True)

    @dbus_service.setter
    def set_speak_row_in_document_table(self, value: bool) -> bool:
        """Sets whether Up/Down in text-document tables speaks the row or just the cell."""

        msg = f"SPEECH PRESENTER: Setting speak row in document table to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_ROW_IN_DOCUMENT_TABLE,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_ROW_IN_SPREADSHEET,
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak full row in spreadsheets",
        migration_key="readFullRowInSpreadSheet",
    )
    @dbus_service.getter
    def get_speak_row_in_spreadsheet(self) -> bool:
        """Returns whether Up/Down in spreadsheets speaks the row or just the cell."""

        return self._get_setting(self.KEY_SPEAK_ROW_IN_SPREADSHEET, "b", False)

    @dbus_service.setter
    def set_speak_row_in_spreadsheet(self, value: bool) -> bool:
        """Sets whether Up/Down in spreadsheets speaks the row or just the cell."""

        msg = f"SPEECH PRESENTER: Setting speak row in spreadsheet to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_ROW_IN_SPREADSHEET,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_CELL_SPAN,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce cell span",
        migration_key="speakCellSpan",
    )
    @dbus_service.getter
    def get_announce_cell_span(self) -> bool:
        """Returns whether cell spans are announced when greater than 1."""

        return self._get_setting(self.KEY_ANNOUNCE_CELL_SPAN, "b", True)

    @dbus_service.setter
    def set_announce_cell_span(self, value: bool) -> bool:
        """Sets whether cell spans are announced when greater than 1."""

        msg = f"SPEECH PRESENTER: Setting announce cell spans to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ANNOUNCE_CELL_SPAN,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_CELL_COORDINATES,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce cell coordinates",
        migration_key="speakCellCoordinates",
    )
    @dbus_service.getter
    def get_announce_cell_coordinates(self) -> bool:
        """Returns whether (non-spreadsheet) cell coordinates are announced."""

        return self._get_setting(self.KEY_ANNOUNCE_CELL_COORDINATES, "b", True)

    @dbus_service.setter
    def set_announce_cell_coordinates(self, value: bool) -> bool:
        """Sets whether (non-spreadsheet) cell coordinates are announced."""

        msg = f"SPEECH PRESENTER: Setting announce cell coordinates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ANNOUNCE_CELL_COORDINATES,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_SPREADSHEET_CELL_COORDINATES,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce spreadsheet cell coordinates",
        migration_key="speakSpreadsheetCoordinates",
    )
    @dbus_service.getter
    def get_announce_spreadsheet_cell_coordinates(self) -> bool:
        """Returns whether spreadsheet cell coordinates are announced."""

        return self._get_setting(self.KEY_ANNOUNCE_SPREADSHEET_CELL_COORDINATES, "b", True)

    @dbus_service.setter
    def set_announce_spreadsheet_cell_coordinates(self, value: bool) -> bool:
        """Sets whether spreadsheet cell coordinates are announced."""

        msg = f"SPEECH PRESENTER: Setting announce spreadsheet cell coordinates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ANNOUNCE_SPREADSHEET_CELL_COORDINATES,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ALWAYS_ANNOUNCE_SELECTED_RANGE_IN_SPREADSHEET,
        schema="speech",
        gtype="b",
        default=False,
        summary="Always announce selected range in spreadsheets",
        migration_key="alwaysSpeakSelectedSpreadsheetRange",
    )
    @dbus_service.getter
    def get_always_announce_selected_range_in_spreadsheet(self) -> bool:
        """Returns whether the selected range in spreadsheets is always announced."""

        return self._get_setting(
            self.KEY_ALWAYS_ANNOUNCE_SELECTED_RANGE_IN_SPREADSHEET,
            "b",
            False,
        )

    @dbus_service.setter
    def set_always_announce_selected_range_in_spreadsheet(self, value: bool) -> bool:
        """Sets whether the selected range in spreadsheets is always announced."""

        msg = f"SPEECH PRESENTER: Setting always announce selected spreadsheet range to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ALWAYS_ANNOUNCE_SELECTED_RANGE_IN_SPREADSHEET,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_CELL_HEADERS,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce cell headers",
        migration_key="speakCellHeaders",
    )
    @dbus_service.getter
    def get_announce_cell_headers(self) -> bool:
        """Returns whether cell headers are announced."""

        return self._get_setting(self.KEY_ANNOUNCE_CELL_HEADERS, "b", True)

    @dbus_service.setter
    def set_announce_cell_headers(self, value: bool) -> bool:
        """Sets whether cell headers are announced."""

        msg = f"SPEECH PRESENTER: Setting announce cell headers to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ANNOUNCE_CELL_HEADERS,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_ARTICLE,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce articles",
    )
    @dbus_service.getter
    def get_announce_article(self) -> bool:
        """Returns whether articles are announced when entered."""

        return self._get_setting(self.KEY_ANNOUNCE_ARTICLE, "b", True)

    @dbus_service.setter
    def set_announce_article(self, value: bool) -> bool:
        """Sets whether articles are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce articles to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ANNOUNCE_ARTICLE,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_BLOCKQUOTE,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce blockquotes",
        migration_key="speakContextBlockquote",
    )
    @dbus_service.getter
    def get_announce_blockquote(self) -> bool:
        """Returns whether blockquotes are announced when entered."""

        return self._get_setting(self.KEY_ANNOUNCE_BLOCKQUOTE, "b", True)

    @dbus_service.setter
    def set_announce_blockquote(self, value: bool) -> bool:
        """Sets whether blockquotes are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce blockquotes to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ANNOUNCE_BLOCKQUOTE,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_CODE_BLOCK,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce code blocks",
    )
    @dbus_service.getter
    def get_announce_code_block(self) -> bool:
        """Returns whether code blocks are announced when entered."""

        return self._get_setting(self.KEY_ANNOUNCE_CODE_BLOCK, "b", True)

    @dbus_service.setter
    def set_announce_code_block(self, value: bool) -> bool:
        """Sets whether code blocks are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce code blocks to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ANNOUNCE_CODE_BLOCK,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_FORM,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce forms",
        migration_key="speakContextNonLandmarkForm",
    )
    @dbus_service.getter
    def get_announce_form(self) -> bool:
        """Returns whether non-landmark forms are announced when entered."""

        return self._get_setting(self.KEY_ANNOUNCE_FORM, "b", True)

    @dbus_service.setter
    def set_announce_form(self, value: bool) -> bool:
        """Sets whether non-landmark forms are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce forms to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, self.KEY_ANNOUNCE_FORM, value
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_GROUPING,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce groupings/panels",
        migration_key="speakContextPanel",
    )
    @dbus_service.getter
    def get_announce_grouping(self) -> bool:
        """Returns whether groupings are announced when entered."""

        return self._get_setting(self.KEY_ANNOUNCE_GROUPING, "b", True)

    @dbus_service.setter
    def set_announce_grouping(self, value: bool) -> bool:
        """Sets whether groupings are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce groupings to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ANNOUNCE_GROUPING,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_LANDMARK,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce landmarks",
        migration_key="speakContextLandmark",
    )
    @dbus_service.getter
    def get_announce_landmark(self) -> bool:
        """Returns whether landmarks are announced when entered."""

        return self._get_setting(self.KEY_ANNOUNCE_LANDMARK, "b", True)

    @dbus_service.setter
    def set_announce_landmark(self, value: bool) -> bool:
        """Sets whether landmarks are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce landmarks to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ANNOUNCE_LANDMARK,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_LIST,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce lists",
        migration_key="speakContextList",
    )
    @dbus_service.getter
    def get_announce_list(self) -> bool:
        """Returns whether lists are announced when entered."""

        return self._get_setting(self.KEY_ANNOUNCE_LIST, "b", True)

    @dbus_service.setter
    def set_announce_list(self, value: bool) -> bool:
        """Sets whether lists are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce lists to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, self.KEY_ANNOUNCE_LIST, value
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_TABLE,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce tables",
        migration_key="speakContextTable",
    )
    @dbus_service.getter
    def get_announce_table(self) -> bool:
        """Returns whether tables are announced when entered."""

        return self._get_setting(self.KEY_ANNOUNCE_TABLE, "b", True)

    @dbus_service.setter
    def set_announce_table(self, value: bool) -> bool:
        """Sets whether tables are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce tables to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, self.KEY_ANNOUNCE_TABLE, value
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ANNOUNCE_TRACKED_CHANGES,
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce tracked changes",
    )
    @dbus_service.getter
    def get_announce_tracked_changes(self) -> bool:
        """Returns whether tracked changes are announced when entered."""

        return self._get_setting(self.KEY_ANNOUNCE_TRACKED_CHANGES, "b", True)

    @dbus_service.setter
    def set_announce_tracked_changes(self, value: bool) -> bool:
        """Sets whether tracked changes are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce tracked changes to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ANNOUNCE_TRACKED_CHANGES,
            value,
        )
        return True

    @dbus_service.command
    def change_number_style(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Changes spoken number style between digits and words."""

        tokens = [
            "SPEECH PRESENTER: change_number_style. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        mgr = speech_manager.get_manager()
        speak_digits = mgr.get_speak_numbers_as_digits()
        if speak_digits:
            brief = messages.NUMBER_STYLE_WORDS_BRIEF
            full = messages.NUMBER_STYLE_WORDS_FULL
        else:
            brief = messages.NUMBER_STYLE_DIGITS_BRIEF
            full = messages.NUMBER_STYLE_DIGITS_FULL

        mgr.set_speak_numbers_as_digits(not speak_digits)
        if script is not None and notify_user:
            presentation_manager.get_manager().present_message(full, brief)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ONLY_SPEAK_DISPLAYED_TEXT,
        schema="speech",
        gtype="b",
        default=False,
        summary="Only speak displayed text",
        migration_key="onlySpeakDisplayedText",
    )
    @dbus_service.getter
    def get_only_speak_displayed_text(self) -> bool:
        """Returns whether only displayed text should be spoken."""

        return self._get_setting(self.KEY_ONLY_SPEAK_DISPLAYED_TEXT, "b", False)

    @dbus_service.setter
    def set_only_speak_displayed_text(self, value: bool) -> bool:
        """Sets whether only displayed text should be spoken."""

        msg = f"SPEECH PRESENTER: Setting only speak displayed text to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ONLY_SPEAK_DISPLAYED_TEXT,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_PROGRESS_BAR_UPDATES,
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak progress bar updates",
        migration_key="speakProgressBarUpdates",
    )
    @dbus_service.getter
    def get_speak_progress_bar_updates(self) -> bool:
        """Returns whether speech progress bar updates are enabled."""

        return self._get_setting(self.KEY_SPEAK_PROGRESS_BAR_UPDATES, "b", True)

    @dbus_service.setter
    def set_speak_progress_bar_updates(self, value: bool) -> bool:
        """Sets whether speech progress bar updates are enabled."""

        msg = f"SPEECH PRESENTER: Setting speak progress bar updates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_PROGRESS_BAR_UPDATES,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_PROGRESS_BAR_SPEECH_INTERVAL,
        schema="speech",
        gtype="i",
        default=10,
        summary="Progress bar speech update interval in seconds",
        migration_key="progressBarSpeechInterval",
    )
    @dbus_service.getter
    def get_progress_bar_speech_interval(self) -> int:
        """Returns the speech progress bar update interval in seconds."""

        return self._get_setting(self.KEY_PROGRESS_BAR_SPEECH_INTERVAL, "i", 10)

    @dbus_service.setter
    def set_progress_bar_speech_interval(self, value: int) -> bool:
        """Sets the speech progress bar update interval in seconds."""

        msg = f"SPEECH PRESENTER: Setting progress bar speech interval to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_PROGRESS_BAR_SPEECH_INTERVAL,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_PROGRESS_BAR_SPEECH_VERBOSITY,
        schema="speech",
        genum="org.gnome.Orca.ProgressBarVerbosity",
        default="application",
        summary="Progress bar speech verbosity (all, application, window)",
        migration_key="progressBarSpeechVerbosity",
    )
    @dbus_service.getter
    def get_progress_bar_speech_verbosity(self) -> int:
        """Returns the speech progress bar verbosity level."""

        value = gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_PROGRESS_BAR_SPEECH_VERBOSITY,
            "",
            genum="org.gnome.Orca.ProgressBarVerbosity",
            default="application",
        )
        return ProgressBarVerbosity[value.upper()].value

    @dbus_service.setter
    def set_progress_bar_speech_verbosity(self, value: int) -> bool:
        """Sets the speech progress bar verbosity level."""

        msg = f"SPEECH PRESENTER: Setting progress bar speech verbosity to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        level = ProgressBarVerbosity(value)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_PROGRESS_BAR_SPEECH_VERBOSITY,
            level.name.lower(),
        )
        return True

    def should_present_progress_bar_update(
        self,
        obj: Atspi.Accessible,
        percent: int | None,
        is_same_app: bool,
        is_same_window: bool,
    ) -> bool:
        """Returns True if the progress bar update should be spoken."""

        if not self.get_speak_progress_bar_updates():
            return False

        last_time, last_value = self._progress_bar_cache.get(id(obj), (0.0, None))
        if percent == last_value:
            return False

        if percent != 100:
            interval = int(time.time() - last_time)
            if interval < self.get_progress_bar_speech_interval():
                return False

        verbosity = self.get_progress_bar_speech_verbosity()
        if verbosity == ProgressBarVerbosity.ALL.value:
            present = True
        elif verbosity == ProgressBarVerbosity.APPLICATION.value:
            present = is_same_app
        elif verbosity == ProgressBarVerbosity.WINDOW.value:
            present = is_same_window
        else:
            present = True

        if present:
            self._progress_bar_cache[id(obj)] = (time.time(), percent)

        return present

    @gsettings_registry.get_registry().gsetting(
        key=KEY_MESSAGES_ARE_DETAILED,
        schema="speech",
        gtype="b",
        default=True,
        summary="Use detailed informative messages",
        migration_key="messagesAreDetailed",
    )
    @dbus_service.getter
    def get_messages_are_detailed(self) -> bool:
        """Returns whether informative messages will be detailed or brief."""

        return self._get_setting(self.KEY_MESSAGES_ARE_DETAILED, "b", True)

    @dbus_service.setter
    def set_messages_are_detailed(self, value: bool) -> bool:
        """Sets whether informative messages will be detailed or brief."""

        msg = f"SPEECH PRESENTER: Setting messages are detailed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_MESSAGES_ARE_DETAILED,
            value,
        )
        return True

    def use_verbose_speech(self) -> bool:
        """Returns whether the speech verbosity level is set to verbose."""

        return self.get_verbosity_level() == "verbose"

    @gsettings_registry.get_registry().gsetting(
        key=KEY_VERBOSITY_LEVEL,
        schema="speech",
        genum="org.gnome.Orca.VerbosityLevel",
        default="verbose",
        summary="Speech verbosity level (brief, verbose)",
        migration_key="speechVerbosityLevel",
    )
    @dbus_service.getter
    def get_verbosity_level(self) -> str:
        """Returns the current speech verbosity level for object presentation."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_VERBOSITY_LEVEL,
            "",
            genum="org.gnome.Orca.VerbosityLevel",
            default="verbose",
        )

    @dbus_service.setter
    def set_verbosity_level(self, value: str) -> bool:
        """Sets the speech verbosity level for object presentation."""

        try:
            level = VerbosityLevel[value.upper()]
        except KeyError:
            msg = f"SPEECH PRESENTER: Invalid verbosity level: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH PRESENTER: Setting verbosity level to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_VERBOSITY_LEVEL,
            level.string_name,
        )
        return True

    def _get_verbosity_is_verbose(self) -> bool:
        """Returns True if verbosity level is VERBOSE, False if BRIEF."""

        return self.get_verbosity_level() == VerbosityLevel.VERBOSE.string_name

    def _set_verbosity_from_bool(self, value: bool) -> bool:
        """Sets verbosity level to VERBOSE if True, BRIEF if False."""

        if value:
            level_name = VerbosityLevel.VERBOSE.string_name
        else:
            level_name = VerbosityLevel.BRIEF.string_name
        return self.set_verbosity_level(level_name)

    def _speech_enabled_and_only_speak_displayed_text_is_off(self) -> bool:
        """Returns True if speech is enabled AND only-speak-displayed-text is off."""

        return (
            speech_manager.get_manager().get_speech_is_enabled()
            and not self.get_only_speak_displayed_text()
        )

    @dbus_service.command
    def toggle_verbosity(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles speech verbosity level between verbose and brief."""

        tokens = [
            "SPEECH PRESENTER: toggle_verbosity. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self.get_verbosity_level() == VerbosityLevel.BRIEF.string_name:
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(
                    messages.SPEECH_VERBOSITY_VERBOSE,
                )
            self.set_verbosity_level(VerbosityLevel.VERBOSE.string_name)
        else:
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.SPEECH_VERBOSITY_BRIEF)
            self.set_verbosity_level(VerbosityLevel.BRIEF.string_name)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_INDENTATION_AND_JUSTIFICATION,
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak indentation and justification",
        migration_key="enableSpeechIndentation",
    )
    @dbus_service.getter
    def get_speak_indentation_and_justification(self) -> bool:
        """Returns whether speaking of indentation and justification is enabled."""

        return self._get_setting(self.KEY_SPEAK_INDENTATION_AND_JUSTIFICATION, "b", False)

    @dbus_service.setter
    def set_speak_indentation_and_justification(self, value: bool) -> bool:
        """Sets whether speaking of indentation and justification is enabled."""

        msg = f"SPEECH PRESENTER: Setting speak indentation and justification to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_INDENTATION_AND_JUSTIFICATION,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_INDENTATION_ONLY_IF_CHANGED,
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak indentation only if changed",
        migration_key="speakIndentationOnlyIfChanged",
    )
    @dbus_service.getter
    def get_speak_indentation_only_if_changed(self) -> bool:
        """Returns whether indentation will be announced only if it has changed."""

        return self._get_setting(self.KEY_SPEAK_INDENTATION_ONLY_IF_CHANGED, "b", False)

    @dbus_service.setter
    def set_speak_indentation_only_if_changed(self, value: bool) -> bool:
        """Sets whether indentation will be announced only if it has changed."""

        msg = f"SPEECH PRESENTER: Setting speak indentation only if changed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_INDENTATION_ONLY_IF_CHANGED,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_TEXT_ATTRIBUTE_CHANGES,
        schema="speech",
        genum="org.gnome.Orca.TextAttributeChangeMode",
        default="off",
        summary="When to speak text attribute changes during navigation",
    )
    @dbus_service.getter
    def get_speak_text_attribute_changes(self) -> str:
        """Returns when text attribute changes are spoken during navigation."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_SPEAK_TEXT_ATTRIBUTE_CHANGES,
            "",
            genum="org.gnome.Orca.TextAttributeChangeMode",
            default="off",
        )

    @dbus_service.setter
    def set_speak_text_attribute_changes(self, value: str) -> bool:
        """Sets when text attribute changes are spoken during navigation."""

        msg = f"SPEECH PRESENTER: Setting speak text attribute changes to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_TEXT_ATTRIBUTE_CHANGES,
            value,
        )
        return True

    def get_text_attribute_change_mode(self) -> TextAttributeChangeMode:
        """Returns the text attribute change mode enum."""

        name = self.get_speak_text_attribute_changes().upper().replace("-", "_")
        for mode in TextAttributeChangeMode:
            if mode.name == name:
                return mode
        return TextAttributeChangeMode.OFF

    def get_text_attribute_change_mode_as_int(self) -> int:
        """Returns the text attribute change mode as an int for the UI."""

        return self.get_text_attribute_change_mode().value

    def set_text_attribute_change_mode_from_int(self, value: int) -> bool:
        """Sets the text attribute change mode from an int for the UI."""

        name = TextAttributeChangeMode(value).name.lower().replace("_", "-")
        return self.set_speak_text_attribute_changes(name)

    def should_speak_text_attribute_changes(self, obj: Atspi.Accessible) -> bool:
        """Returns True if text attribute changes should be spoken for obj."""

        if self._text_attribute_change_mode_override is not None:
            mode = self._text_attribute_change_mode_override
        elif focus_manager.get_manager().in_say_all():
            mode = say_all_presenter.get_presenter().get_text_attribute_change_mode()
        else:
            mode = self.get_text_attribute_change_mode()

        if mode == TextAttributeChangeMode.OFF:
            return False
        if mode == TextAttributeChangeMode.ALWAYS:
            return True
        return AXUtilities.is_editable(obj)

    @dbus_service.command
    def cycle_text_attribute_change_mode(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Cycles through text attribute change announcement modes."""

        tokens = [
            "SPEECH PRESENTER: cycle_text_attribute_change_mode. ",
            "Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self._text_attribute_change_mode_override is not None:
            mode = self._text_attribute_change_mode_override
        elif focus_manager.get_manager().in_say_all():
            mode = say_all_presenter.get_presenter().get_text_attribute_change_mode()
        else:
            mode = self.get_text_attribute_change_mode()

        mode_cycle = {
            TextAttributeChangeMode.OFF: TextAttributeChangeMode.EDITABLE_ONLY,
            TextAttributeChangeMode.EDITABLE_ONLY: TextAttributeChangeMode.ALWAYS,
            TextAttributeChangeMode.ALWAYS: TextAttributeChangeMode.OFF,
        }
        self._text_attribute_change_mode_override = mode_cycle[mode]
        new_mode = self._text_attribute_change_mode_override

        msg_map = {
            TextAttributeChangeMode.OFF: messages.TEXT_ATTRIBUTE_CHANGES_OFF,
            TextAttributeChangeMode.EDITABLE_ONLY: messages.TEXT_ATTRIBUTE_CHANGES_EDITABLE_ONLY,
            TextAttributeChangeMode.ALWAYS: messages.TEXT_ATTRIBUTE_CHANGES_ON,
        }
        if notify_user:
            presentation_manager.get_manager().present_message(msg_map[new_mode])
        return True

    @dbus_service.command
    def toggle_indentation_and_justification(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles the speaking of indentation and justification."""

        tokens = [
            "SPEECH PRESENTER: toggle_indentation_and_justification. ",
            "Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        value = self.get_speak_indentation_and_justification()
        self.set_speak_indentation_and_justification(not value)
        if self.get_speak_indentation_and_justification():
            full = messages.INDENTATION_JUSTIFICATION_ON_FULL
            brief = messages.INDENTATION_JUSTIFICATION_ON_BRIEF
        else:
            full = messages.INDENTATION_JUSTIFICATION_OFF_FULL
            brief = messages.INDENTATION_JUSTIFICATION_OFF_BRIEF
        if script is not None and notify_user:
            presentation_manager.get_manager().present_message(full, brief)
        return True

    @dbus_service.command
    def toggle_table_cell_reading_mode(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles between speak cell and speak row."""

        tokens = [
            "SPEECH PRESENTER: toggle_table_cell_reading_mode. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # TODO - JD: This is due to the requirement on script utilities.
        if script is None:
            msg = "SPEECH PRESENTER: Toggling table cell reading mode requires script."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        table = AXUtilities.get_table(focus_manager.get_manager().get_locus_of_focus())
        if table is None and notify_user:
            presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        if not script.utilities.get_document_for_object(table):
            getter = self.get_speak_row_in_gui_table
            setter = self.set_speak_row_in_gui_table
        elif AXUtilities.is_spreadsheet_table(table):
            getter = self.get_speak_row_in_spreadsheet
            setter = self.set_speak_row_in_spreadsheet
        else:
            getter = self.get_speak_row_in_document_table
            setter = self.set_speak_row_in_document_table

        speak_row = getter()
        setter(not speak_row)

        if not speak_row:
            msg = messages.TABLE_MODE_ROW
        else:
            msg = messages.TABLE_MODE_CELL

        if notify_user:
            presentation_manager.get_manager().present_message(msg)
        return True

    @dbus_service.command
    def toggle_monitor(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles the speech monitor on and off."""

        tokens = [
            "SPEECH PRESENTER: toggle_monitor. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self.get_monitor_is_enabled():
            self.set_monitor_is_enabled(False)
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.SPEECH_MONITOR_DISABLED)
        else:
            self.set_monitor_is_enabled(True)
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.SPEECH_MONITOR_ENABLED)
        return True

    @staticmethod
    def adjust_for_digits(obj: Atspi.Accessible, text: str) -> str:
        """Adjusts text to present numbers as digits."""

        def _convert(word):
            if word.isnumeric():
                word = " ".join(list(word))
            return word

        speak_digits = gsettings_registry.get_registry().layered_lookup(
            "speech",
            "speak-numbers-as-digits",
            "b",
            default=False,
        )
        if not (speak_digits or AXUtilities.is_text_input_telephone(obj)):
            return text

        return " ".join(map(_convert, text.split()))

    @staticmethod
    def _adjust_for_links(obj: Atspi.Accessible, line: str, start_offset: int) -> str:
        """Adjust line to include the word "link" after any hypertext links."""

        # This adjustment should only be made in cases where there is only presentable text.
        # In content where embedded objects are present, "link" is presented as the role of any
        # embedded link children.
        if "\ufffc" in line:
            return line

        end_offset = start_offset + len(line)
        links = AXHypertext.get_all_links_in_range(obj, start_offset, end_offset)
        offsets = [AXHypertext.get_link_end_offset(link) for link in links]
        offsets = sorted([offset - start_offset for offset in offsets], reverse=True)
        tokens = list(line)
        for o in offsets:
            if 0 <= o <= len(tokens):
                text = f" {messages.LINK}"
                if o < len(tokens) and tokens[o].isalnum():
                    text += " "
                tokens[o:o] = text
        return "".join(tokens)

    def _adjust_for_repeats(self, text: str) -> str:
        """Adjust line to include a description of repeated symbols."""

        def replacement(match):
            char = match.group(1)
            count = len(match.group(0))
            if match.start() > 0 and text[match.start() - 1].isalnum():
                return f" {messages.repeated_char_count(char, count)}"
            return messages.repeated_char_count(char, count)

        limit = self.get_repeated_character_limit()
        if len(text) < 4 or limit < 4:
            return text

        pattern = re.compile(r"([^a-zA-Z0-9\s])\1{" + str(limit - 1) + ",}")
        return re.sub(pattern, replacement, text)

    @staticmethod
    def _should_verbalize_punctuation(obj: Atspi.Accessible) -> bool:
        """Returns True if punctuation should be verbalized."""

        ancestor = AXUtilities.find_ancestor_inclusive(obj, AXUtilities.is_code)
        if ancestor is None:
            return False

        document = AXUtilities.find_ancestor_inclusive(ancestor, AXUtilities.is_document)
        if AXDocument.is_plain_text(document):
            return False

        # If the user has set their punctuation level to All, then the synthesizer will
        # do the work for us. If the user has set their punctuation level to None, then
        # they really don't want punctuation and we mustn't override that.

        punct_level = speech_manager.get_manager().get_punctuation_level()
        return punct_level not in ("all", "none")

    @staticmethod
    def _adjust_for_verbalized_punctuation(obj: Atspi.Accessible, text: str) -> str:
        """Surrounds punctuation symbols with spaces to increase the likelihood of presentation."""

        if not SpeechPresenter._should_verbalize_punctuation(obj):
            return text

        result = text
        punctuation = set(re.findall(r"[^\w\s]", result))
        for symbol in punctuation:
            result = result.replace(symbol, f" {symbol} ")

        return result

    def _apply_pronunciation_dictionary(self, text: str) -> str:
        """Applies the pronunciation dictionary to the text."""

        if not speech_manager.get_manager().get_use_pronunciation_dictionary():
            return text

        manager = pronunciation_dictionary_manager.get_manager()
        words = re.split(r"(\W+)", text)
        return manager.apply_to_words(words)

    def get_indentation_description(self, line: str, only_if_changed: bool | None = None) -> str:
        """Returns a description of the indentation in the given line."""

        if (
            self.get_only_speak_displayed_text()
            or not self.get_speak_indentation_and_justification()
        ):
            return ""

        line = line.replace("\u00a0", " ")
        end = re.search("[^ \t]", line)
        if end:
            line = line[: end.start()]

        result = ""
        spaces = [m.span() for m in re.finditer(" +", line)]
        tabs = [m.span() for m in re.finditer("\t+", line)]
        spans = sorted(spaces + tabs)
        for span in spans:
            if span in spaces:
                result += f"{messages.spaces_count(span[1] - span[0])} "
            else:
                result += f"{messages.tabs_count(span[1] - span[0])} "

        if only_if_changed is None:
            only_if_changed = self.get_speak_indentation_only_if_changed()

        if only_if_changed:
            if self._last_indentation_description == result:
                return ""

            if not result and self._last_indentation_description:
                self._last_indentation_description = ""
                return messages.spaces_count(0)

        self._last_indentation_description = result
        return result

    def get_error_description(
        self,
        obj: Atspi.Accessible,
        offset: int | None = None,
        only_if_changed: bool | None = True,
    ) -> str:
        """Returns a description of the error at the current offset."""

        if not self.get_speak_misspelled_indicator():
            return ""

        # If we're on whitespace or punctuation, we cannot be on an error.
        char = AXText.get_character_at_offset(obj, offset)[0]
        if char in string.punctuation + string.whitespace + "\u00a0":
            self._last_error_description = ""
            return ""

        msg = ""
        if AXUtilities.string_has_spelling_error(obj, offset):
            # TODO - JD: We're using the message here to preserve existing behavior.
            msg = messages.MISSPELLED
        elif AXUtilities.string_has_grammar_error(obj, offset):
            msg = object_properties.STATE_INVALID_GRAMMAR_SPEECH

        if only_if_changed and msg == self._last_error_description:
            return ""

        self._last_error_description = msg
        return msg

    def present_text_attribute_state(
        self,
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> None:
        """Presents error indicators and text attribute changes at the given offset."""

        if error := self.get_error_description(obj, offset):
            self.speak_message(error)

        if not self.should_speak_text_attribute_changes(obj):
            return

        for attr, _old, new in AXUtilities.get_text_attribute_changes(obj, offset):
            if attr == AXTextAttribute.INVALID:
                continue
            if attr == AXTextAttribute.LANGUAGE and self._language_switch_is_active(new):
                continue
            if desc := attr.get_change_description(new):
                self.speak_message(desc)

    def _language_switch_is_active(self, language_value: str | None) -> bool:
        """Returns True if auto language switching is enabled and supported for the language."""

        if not language_value or not speech_manager.get_manager().get_auto_language_switching():
            return False

        parts = language_value.lower().split("-", 1)
        lang = parts[0]
        dialect = parts[1] if len(parts) > 1 else ""
        full = f"{lang}-{dialect}" if dialect else lang

        mgr = speech_manager.get_manager()
        voice_set_names = mgr.get_voice_set_names()
        if full in voice_set_names or lang in voice_set_names:
            return True

        primary = mgr.get_voice_properties()
        primary_family = primary.get(ACSS.FAMILY, {})
        primary_lang = primary_family.get(VoiceFamily.LANG, "").lower()
        return lang == primary_lang

    def adjust_for_presentation(
        self,
        obj: Atspi.Accessible | None,
        text: str,
        start_offset: int | None = None,
    ) -> str:
        """Adjusts text for spoken presentation."""

        tokens = [
            f"SPEECH PRESENTER: Adjusting '{text}' from",
            obj,
            f"start_offset: {start_offset}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if start_offset is not None and obj is not None:
            text = self._adjust_for_links(obj, text, start_offset)

        if obj is not None:
            text = self.adjust_for_digits(obj, text)
        text = self._adjust_for_repeats(text)
        if obj is not None:
            text = self._adjust_for_verbalized_punctuation(obj, text)
        text = self._apply_pronunciation_dictionary(text)

        msg = f"SPEECH PRESENTER: Adjusted text: '{text}'"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return text

    def _get_active_script(self) -> default.Script | None:
        """Returns the active script."""

        from . import script_manager  # pylint: disable=import-outside-toplevel

        return script_manager.get_manager().get_active_script()

    def _get_voice(
        self,
        text: str = "",
        obj: Atspi.Accessible | None = None,
        language: str = "",
        dialect: str = "",
    ) -> list[ACSS]:
        """Returns the voice to use for the given string."""

        if active_script := self._get_active_script():
            generator = active_script.get_speech_generator()
            context = self._build_generator_context()
            return generator.voice(
                obj=obj, string=text, context=context, language=language, dialect=dialect
            )
        return []

    @dbus_service.getter
    def get_monitor_is_enabled(self) -> bool:
        """Returns whether the speech monitor is enabled."""

        return self._monitor_enabled_override or False

    @dbus_service.setter
    def set_monitor_is_enabled(self, value: bool) -> bool:
        """Sets whether the speech monitor is enabled."""

        msg = f"SPEECH PRESENTER: Setting enable speech monitor to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._monitor_enabled_override = value
        if not value:
            self.destroy_monitor()
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_MONITOR_FONT_SIZE,
        schema="speech",
        gtype="i",
        default=14,
        summary="Speech monitor font size",
        migration_key="speechMonitorFontSize",
    )
    @dbus_service.getter
    def get_monitor_font_size(self) -> int:
        """Returns the speech monitor font size."""

        return self._get_setting(self.KEY_MONITOR_FONT_SIZE, "i", 14)

    @dbus_service.setter
    def set_monitor_font_size(self, value: int) -> bool:
        """Sets the speech monitor font size."""

        msg = f"SPEECH PRESENTER: Setting speech monitor font size to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_MONITOR_FONT_SIZE,
            value,
        )
        if self._monitor is not None:
            self._monitor.set_font_size(value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_MONITOR_FOREGROUND,
        schema="speech",
        gtype="s",
        default="#ffffff",
        summary="Speech monitor foreground color",
        migration_key="speechMonitorForeground",
    )
    @dbus_service.getter
    def get_monitor_foreground(self) -> str:
        """Returns the speech monitor foreground color."""

        return self._get_setting(self.KEY_MONITOR_FOREGROUND, "s", "#ffffff")

    @dbus_service.setter
    def set_monitor_foreground(self, value: str) -> bool:
        """Sets the speech monitor foreground color."""

        msg = f"SPEECH PRESENTER: Setting speech monitor foreground to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_MONITOR_FOREGROUND,
            value,
        )
        if self._monitor is not None:
            self._monitor.reapply_css(foreground=value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_MONITOR_BACKGROUND,
        schema="speech",
        gtype="s",
        default="#000000",
        summary="Speech monitor background color",
        migration_key="speechMonitorBackground",
    )
    @dbus_service.getter
    def get_monitor_background(self) -> str:
        """Returns the speech monitor background color."""

        return self._get_setting(self.KEY_MONITOR_BACKGROUND, "s", "#000000")

    @dbus_service.setter
    def set_monitor_background(self, value: str) -> bool:
        """Sets the speech monitor background color."""

        msg = f"SPEECH PRESENTER: Setting speech monitor background to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_MONITOR_BACKGROUND,
            value,
        )
        if self._monitor is not None:
            self._monitor.reapply_css(background=value)
        return True

    def init_monitor(self) -> None:
        """Shows the speech monitor if enabled in settings. Called at startup."""

        self._ensure_monitor()

    def _ensure_monitor(self) -> speech_monitor.SpeechMonitor | None:
        """Creates the speech monitor on demand if enabled, returns it or None."""

        if not self.get_monitor_is_enabled():
            return None

        if self._monitor is None:
            self._monitor = speech_monitor.SpeechMonitor(
                font_size=self.get_monitor_font_size(),
                foreground=self.get_monitor_foreground(),
                background=self.get_monitor_background(),
                on_close=lambda: self.set_monitor_is_enabled(False),
            )
            self._monitor.show_all()  # pylint: disable=no-member
            self._monitor.present_with_time(time.time())
            self._replay_history()

        return self._monitor

    def destroy_monitor(self) -> None:
        """Destroys the speech monitor widget if it exists."""

        if self._monitor is not None:
            self._monitor.destroy()
            self._monitor = None

    def _append_to_history(self, kind: str, value: str) -> None:
        """Appends an entry to the speech history buffer."""

        self._speech_history.append((kind, value))
        if len(self._speech_history) > 500:
            self._speech_history = self._speech_history[-500:]

    def _replay_history(self) -> None:
        """Replays stored speech history into the current monitor."""

        if self._monitor is None or not self._speech_history:
            return
        for kind, value in self._speech_history:
            if kind == "text":
                self._monitor.write_text(value)
            elif kind == "key":
                self._monitor.write_key_event(value)

    def _monitor_is_writable(self) -> speech_monitor.SpeechMonitor | None:
        """Returns the monitor if it exists, is enabled, and doesn't have focus."""

        monitor = self._ensure_monitor()
        if monitor is None:
            return None
        if monitor.has_toplevel_focus():  # pylint: disable=no-member
            return None
        return monitor

    def _begin_monitor_group(self) -> None:
        """Begins buffering speech monitor writes for grouped output."""

        self._group_buffer = []

    def _end_monitor_group(self) -> None:
        """Flushes the group buffer as a single line to the monitor and history."""

        buffered = self._group_buffer
        self._group_buffer = None
        if not buffered:
            return

        combined = " ".join(buffered)
        monitor = self._monitor_is_writable()
        if monitor is not None:
            monitor.write_text(combined)
        self._append_to_history("text", combined)

    def write_to_monitor(self, text: str) -> None:
        """Writes spoken text to the speech monitor if active and not focused."""

        if self._group_buffer is not None:
            self._group_buffer.append(text)
            return

        monitor = self._monitor_is_writable()
        if monitor is not None:
            monitor.write_text(text)
        self._append_to_history("text", text)

    def write_key_to_monitor(self, key_description: str) -> None:
        """Writes a key event to the speech monitor if active and not focused."""

        monitor = self._monitor_is_writable()
        if monitor is not None:
            monitor.write_key_event(key_description)
        self._append_to_history("key", key_description)

    @staticmethod
    def _resolve_acss(acss: ACSS | dict[str, Any] | list[dict[str, Any]] | None = None) -> ACSS:
        """Normalizes various voice property formats to an ACSS instance."""

        if isinstance(acss, ACSS):
            family = acss.get(acss.FAMILY)
            if family is not None:
                try:
                    family = VoiceFamily(family)
                except (TypeError, ValueError):
                    family = VoiceFamily({})
                acss[acss.FAMILY] = family
            return acss
        if isinstance(acss, list) and len(acss) == 1:
            return ACSS(acss[0])
        if isinstance(acss, dict):
            return ACSS(acss)
        return ACSS({})

    def _apply_voice_set_overrides(self, voice: ACSS) -> ACSS:
        """Applies voice set overrides if a matching set exists for the voice's language."""

        family = voice.get(ACSS.FAMILY)
        if not family:
            return voice

        lang = family.get(VoiceFamily.LANG, "")
        if not lang:
            return voice

        dialect = family.get(VoiceFamily.DIALECT, "")
        language = f"{lang}-{dialect}".lower() if dialect else lang.lower()

        mgr = speech_manager.get_manager()
        voice_set_names = mgr.get_voice_set_names()
        if language not in voice_set_names:
            language = lang.lower()
        if language not in voice_set_names:
            return voice

        voice_type = voice.pop(ACSS.VOICE_TYPE, speechserver.VoiceType.DEFAULT)
        config = mgr.get_voice_properties(voice_type, voice_set=language)
        if not config or not config.get("established"):
            return voice

        msg = f"SPEECH PRESENTER: Applying voice set overrides for {language} ({voice_type})"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if ACSS.FAMILY in config:
            family.update(config[ACSS.FAMILY])
            voice[ACSS.FAMILY] = family
        for prop in (ACSS.RATE, ACSS.AVERAGE_PITCH, ACSS.PITCH_RANGE, ACSS.GAIN):
            if prop in config:
                voice[prop] = config[prop]

        return voice

    def _speak_single(self, text: str, acss: ACSS | dict[str, Any] | None) -> None:
        """Speaks an individual string using the given ACSS."""

        server = speech_manager.get_manager().get_server()
        if not server:
            msg = f"SPEECH OUTPUT: '{text}' {acss}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        resolved_voice = self._apply_voice_set_overrides(self._resolve_acss(acss))
        msg = f"SPEECH OUTPUT: '{text}' {resolved_voice}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        server.speak(text, resolved_voice)
        self.write_to_monitor(text)

    # pylint: disable-next=too-many-branches
    def _speak_list(self, content: list, acss: ACSS | dict[str, Any] | None) -> None:
        """Processes a list of speech content items."""

        valid_types = (str, list, speech_generator.Pause, ACSS)

        to_speak: list[str] = []
        active_voice = ACSS(acss) if acss is not None else acss

        for element in content:
            if not isinstance(element, valid_types):
                msg = f"SPEECH: Bad content sent to speak(): {element}"
                debug.print_message(debug.LEVEL_INFO, msg, True, True)
            elif isinstance(element, list):
                self._speak_list(element, acss)
            elif isinstance(element, str):
                if element:
                    to_speak.append(element)
            elif to_speak:
                new_voice = ACSS(acss)
                new_items_to_speak: list[str] = []
                if isinstance(element, speech_generator.Pause):
                    if to_speak[-1] and to_speak[-1][-1].isalnum():
                        to_speak[-1] += "."
                elif isinstance(element, ACSS):
                    new_voice.update(element)
                    if active_voice is None:
                        active_voice = new_voice
                    if new_voice == active_voice:
                        continue
                    tokens = ["SPEECH: New voice", new_voice, " != active voice", active_voice]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    new_items_to_speak.append(to_speak.pop())

                if to_speak:
                    self._speak_single(" ".join(to_speak), active_voice)
                active_voice = new_voice
                to_speak = new_items_to_speak

        if to_speak:
            self._speak_single(" ".join(to_speak), active_voice)

    def _speak(self, content: Any, acss: ACSS | dict[str, Any] | None = None) -> None:
        """Speaks the given content, which can be a string or a list from the speech generator."""

        if speech_manager.get_manager().get_speech_is_muted():
            return

        if isinstance(content, str):
            msg = f"SPEECH: Speak '{content}' acss: {acss}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._speak_single(content, acss)
            return

        if isinstance(content, list):
            tokens = ["SPEECH: Speak", content, ", acss:", acss]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._begin_monitor_group()
            try:
                self._speak_list(content, acss)
            finally:
                self._end_monitor_group()
            return

        if not isinstance(content, (speech_generator.Pause, ACSS)):
            msg = f"SPEECH: Bad content sent to speak(): {content}"
            debug.print_message(debug.LEVEL_INFO, msg, True, True)

    def present_key_event(self, event: KeyboardEvent) -> None:
        """Presents a key event via speech."""

        if speech_manager.get_manager().get_speech_is_muted():
            return

        key_name = event.get_key_name() if event.is_printable_key() else None
        voice = self._get_voice(text=key_name or "")
        acss = self._resolve_acss(voice[0] if voice else None)

        event_string = event.get_key_name()
        locking_state_string = event.get_locking_state_string()
        event_string = f"{event_string} {locking_state_string}".strip()
        msg = f"SPEECH OUTPUT: '{event_string}' {acss}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        server = speech_manager.get_manager().get_server()
        if server:
            server.speak_key_event(event, acss)
        if key_name:
            self.write_key_to_monitor(key_name)
        else:
            self.write_key_to_monitor(event.get_key_name())

    def speak_accessible_text(self, obj: Atspi.Accessible | None, text: str) -> None:
        """Speaks text from an accessible object, determining voice automatically."""

        voice = self._get_voice(text, obj)
        text = self.adjust_for_presentation(obj, text)
        self._speak(text, voice[0] if voice else None)

    def speak_message(self, text: str) -> None:
        """Speaks a message using the system voice."""

        try:
            assert isinstance(text, str)
        except AssertionError:
            tokens = ["SPEECH PRESENTER: speak_message called with non-string:", text]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            debug.print_exception(debug.LEVEL_WARNING)
            return

        if self.get_only_speak_displayed_text():
            return

        mgr = speech_manager.get_manager()
        voice = mgr.get_voice_properties(speechserver.VoiceType.SYSTEM)

        server = mgr.get_server()
        if server is not None:
            server.update_capitalization_style("none")
            user_level = speechserver.PunctuationStyle[mgr.get_punctuation_level().upper()]
            level = max(user_level, speechserver.PunctuationStyle.SOME, key=lambda s: s.value)
            server.update_punctuation_level(level)

        text = self.adjust_for_presentation(None, text)
        self._speak(text, voice)

        if server is not None:
            mgr.update_capitalization_style()
            mgr.update_punctuation_level()

    def _build_generator_context(
        self,
        where_am_i_type: WhereAmI | None = None,
    ) -> SpeechGeneratorContext:
        """Builds the settings context for speech generators."""

        from .speech_generator import (  # pylint: disable=import-outside-toplevel
            SpeechGeneratorContext,
        )

        mgr = focus_manager.get_manager()
        in_say_all = mgr.in_say_all()
        if in_say_all:
            p = say_all_presenter.get_presenter()
        else:
            p = self  # type: ignore[assignment]

        active_mode, _obj = mgr.get_active_mode_and_object_of_interest()
        speech_mgr = speech_manager.get_manager()

        return SpeechGeneratorContext(
            enabled=speech_mgr.get_speech_is_enabled(),
            verbose=self.use_verbose_speech(),
            focus=mgr.get_locus_of_focus(),
            in_say_all=in_say_all,
            in_focus_mode=document_presenter.get_presenter().get_in_focus_mode(),
            active_mode=active_mode,
            where_am_i_type=where_am_i_type,
            in_preferences_window=mgr.is_in_preferences_window(),
            auto_language_switching_content=speech_mgr.get_auto_language_switching(),
            only_switch_configured_languages=speech_mgr.get_only_switch_configured_languages(),
            voice_set_languages=tuple(speech_mgr.get_voice_set_names()),
            auto_language_switching_ui=speech_mgr.get_auto_language_switching_ui(),
            insert_pauses_between_utterances=speech_mgr.get_insert_pauses_between_utterances(),
            punctuation_level=speech_mgr.get_punctuation_level(),
            voices={vt: speech_mgr.get_voice_properties(vt) for vt in speechserver.VoiceType},
            speech_server=speech_mgr.get_server(),
            only_displayed_text=self.get_only_speak_displayed_text(),
            speak_description=self.get_speak_description(),
            speak_tutorial_messages=self.get_speak_tutorial_messages(),
            speak_position_in_set=self.get_speak_position_in_set(),
            speak_widget_mnemonic=self.get_speak_widget_mnemonic(),
            speak_blank_lines=self.get_speak_blank_lines(),
            speak_indentation=self.get_speak_indentation_and_justification(),
            announce_cell_headers=self.get_announce_cell_headers(),
            announce_cell_coordinates=self.get_announce_cell_coordinates(),
            announce_spreadsheet_cell_coordinates=self.get_announce_spreadsheet_cell_coordinates(),
            announce_article=p.get_announce_article(),
            announce_blockquote=p.get_announce_blockquote(),
            announce_code_block=p.get_announce_code_block(),
            announce_form=p.get_announce_form(),
            announce_grouping=p.get_announce_grouping(),
            announce_landmark=p.get_announce_landmark(),
            announce_list=p.get_announce_list(),
            announce_table=p.get_announce_table(),
            announce_tracked_changes=p.get_announce_tracked_changes(),
            text_attribute_change_mode=self._text_attribute_change_mode_override.value
            if self._text_attribute_change_mode_override is not None
            else p.get_text_attribute_change_mode().value,
            speak_misspelled_indicator=self.get_speak_misspelled_indicator(),
        )

    def generate_speech_contents(
        self,
        script: default.Script,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        **args: Any,
    ) -> list:
        """Generates speech utterances for contents without speaking them."""

        context = self._build_generator_context()
        return script.get_speech_generator().generate_contents(contents, context, **args)

    def generate_speech_string(self, script: default.Script, obj: Atspi.Accessible) -> str:
        """Generates speech for obj and returns it as a string."""

        context = self._build_generator_context()
        generator = script.get_speech_generator()
        utterances = generator.generate_speech(obj, context)
        return generator.utterances_to_string(utterances)

    def generate_window_title_strings(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
    ) -> list[str]:
        """Returns the window title as a list of strings."""

        context = self._build_generator_context()
        return [s for s, _ in script.get_speech_generator().generate_window_title(obj, context)]

    def speak_contents(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        **args: Any,
    ) -> None:
        """Speaks the specified contents."""

        tokens = ["SPEECH PRESENTER: Speaking", contents, args]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        if not (active_script := self._get_active_script()):
            return

        where_am_i_type = args.pop("where_am_i_type", None)
        context = self._build_generator_context(where_am_i_type)
        generator = active_script.get_speech_generator()
        utterances = generator.generate_contents(contents, context, **args)
        self._speak(utterances)

    def present_generated_speech(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        **args: Any,
    ) -> None:
        """Generates speech for obj using the script's speech generator and speaks it."""

        where_am_i_type = args.pop("where_am_i_type", None)
        context = self._build_generator_context(where_am_i_type)
        utterances = script.get_speech_generator().generate_speech(obj, context, **args)
        self._speak(utterances)

    def speak_line(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        start_offset: int,
        end_offset: int,
        line: str,
    ) -> None:
        """Generates and speaks a line using the script's speech generator."""

        indentation = self.get_indentation_description(line)
        if indentation:
            self.speak_message(indentation)

        context = self._build_generator_context()
        generator = script.get_speech_generator()
        utterances = generator.generate_line(obj, start_offset, end_offset, line, context)
        self._speak(utterances)

    def speak_phrase(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        start_offset: int,
        end_offset: int,
        phrase: str,
    ) -> None:
        """Generates and speaks a phrase using the script's speech generator."""

        if len(phrase) <= 1 and not phrase.isalnum():
            attrs = AXText.get_text_attributes_at_offset(obj, start_offset)[0]
            lang = attrs.get("language", "")
            dialect = ""
            if "-" in lang:
                lang, dialect = lang.split("-", 1)
            self.speak_character(phrase, obj=obj, language=lang, dialect=dialect)
            return

        indentation = self.get_indentation_description(phrase)
        if indentation:
            self.speak_message(indentation)

        context = self._build_generator_context()
        generator = script.get_speech_generator()
        utterances = generator.generate_phrase(obj, start_offset, end_offset, phrase, context)
        self._speak(utterances)

    def speak_word(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        offset: int,
    ) -> None:
        """Generates and speaks a word using the script's speech generator."""

        context = self._build_generator_context()
        utterances = script.get_speech_generator().generate_word(obj, offset, context)
        self._speak(utterances)

    def speak_character_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        character: str,
        cap_style: speechserver.CapitalizationStyle | None = None,
    ) -> None:
        """Handles presentation of a character at the given offset."""

        if not character or character == "\r":
            character = "\n"

        if character == "\n":
            line_string = AXText.get_line_at_offset(obj, max(0, offset))[0]
            if not line_string or line_string == "\n":
                if self.get_speak_blank_lines():
                    self.speak_message(messages.BLANK)
                return

        if character in ["\n", "\r\n"]:
            if self.get_speak_blank_lines():
                self.speak_message(messages.BLANK)
            return

        self.present_text_attribute_state(obj, offset)

        attrs = AXText.get_text_attributes_at_offset(obj, offset)[0]
        lang = attrs.get("language", "")
        dialect = ""
        if "-" in lang:
            lang, dialect = lang.split("-", 1)

        self.speak_character(
            character,
            voice_from=character,
            cap_style=cap_style,
            obj=obj,
            language=lang,
            dialect=dialect,
        )

    def say_all(self, utterance_iterator: Any, progress_callback: Callable[..., Any]) -> None:
        """Speaks each item in the utterance_iterator."""

        if speech_manager.get_manager().get_speech_is_muted():
            return

        def _with_monitor(iterator: Any) -> Any:
            for context, acss in iterator:
                self.write_to_monitor(context.utterance)
                yield context, acss

        server = speech_manager.get_manager().get_server()
        if server:
            server.say_all(_with_monitor(utterance_iterator), progress_callback)
        else:
            for context, _acss in utterance_iterator:
                msg = f"SPEECH OUTPUT: '{context.utterance}'"
                debug.print_message(debug.LEVEL_INFO, msg, True)

    def speak_character(
        self,
        character: str,
        voice_from: str = "",
        cap_style: speechserver.CapitalizationStyle | None = None,
        obj: Atspi.Accessible | None = None,
        language: str = "",
        dialect: str = "",
    ) -> None:
        """Speaks a single character using the voice for voice_from."""

        if speech_manager.get_manager().get_speech_is_muted():
            return

        voice = self._get_voice(
            text=voice_from or character, obj=obj, language=language, dialect=dialect
        )
        acss = self._apply_voice_set_overrides(self._resolve_acss(voice[0] if voice else None))
        msg = f"SPEECH OUTPUT: '{character}'"
        tokens = [msg, acss]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = speech_manager.get_manager().get_server()
        if server:
            server.speak_character(character, acss=acss, cap_style=cap_style)
        self.write_to_monitor(character)

    def spell_item(self, text: str) -> None:
        """Speak the characters in the string one by one."""

        for character in text:
            self.speak_character(character)

    def spell_phonetically(self, item_string: str) -> None:
        """Phonetically spell item_string."""

        for character in item_string:
            voice = self._get_voice(text=character)
            phonetic_string = phonnames.get_phonetic_name(character.lower())
            self._speak(phonetic_string, voice[0] if voice else None)

    def create_speech_preferences_grid(
        self,
        title_change_callback: Callable[[str], None] | None = None,
        app_name: str = "",
    ) -> SpeechPreferencesGrid:
        """Returns the GtkGrid containing the combined speech preferences UI."""

        return SpeechPreferencesGrid(self, title_change_callback, app_name=app_name)

    def get_speech_preferences(
        self,
    ) -> tuple[
        tuple[SpeechPreference, ...],  # general
        tuple[SpeechPreference, ...],  # object_details
        tuple[SpeechPreference, ...],  # announcements
    ]:
        """Return descriptors for speech preferences, organized by section."""

        general = (
            SpeechPreference(
                self.KEY_MESSAGES_ARE_DETAILED,
                guilabels.SPEECH_SYSTEM_MESSAGES_ARE_DETAILED,
                self.get_messages_are_detailed,
                self.set_messages_are_detailed,
            ),
        )

        object_details = (
            SpeechPreference(
                self.KEY_ONLY_SPEAK_DISPLAYED_TEXT,
                guilabels.SPEECH_ONLY_SPEAK_DISPLAYED_TEXT,
                self.get_only_speak_displayed_text,
                self.set_only_speak_displayed_text,
            ),
            SpeechPreference(
                self.KEY_SPEAK_DESCRIPTION,
                guilabels.SPEECH_SPEAK_DESCRIPTION,
                self.get_speak_description,
                self.set_speak_description,
            ),
            SpeechPreference(
                self.KEY_SPEAK_POSITION_IN_SET,
                guilabels.SPEECH_SPEAK_CHILD_POSITION,
                self.get_speak_position_in_set,
                self.set_speak_position_in_set,
            ),
            SpeechPreference(
                self.KEY_SPEAK_WIDGET_MNEMONIC,
                guilabels.PRESENT_OBJECT_MNEMONICS,
                self.get_speak_widget_mnemonic,
                self.set_speak_widget_mnemonic,
            ),
            SpeechPreference(
                self.KEY_SPEAK_TUTORIAL_MESSAGES,
                guilabels.SPEECH_SPEAK_TUTORIAL_MESSAGES,
                self.get_speak_tutorial_messages,
                self.set_speak_tutorial_messages,
            ),
        )

        announcements = (
            SpeechPreference(
                self.KEY_ANNOUNCE_ARTICLE,
                guilabels.ANNOUNCE_ARTICLES,
                self.get_announce_article,
                self.set_announce_article,
            ),
            SpeechPreference(
                self.KEY_ANNOUNCE_BLOCKQUOTE,
                guilabels.ANNOUNCE_BLOCKQUOTES,
                self.get_announce_blockquote,
                self.set_announce_blockquote,
            ),
            SpeechPreference(
                self.KEY_ANNOUNCE_CODE_BLOCK,
                guilabels.ANNOUNCE_CODE_BLOCKS,
                self.get_announce_code_block,
                self.set_announce_code_block,
            ),
            SpeechPreference(
                self.KEY_ANNOUNCE_FORM,
                guilabels.ANNOUNCE_FORMS,
                self.get_announce_form,
                self.set_announce_form,
            ),
            SpeechPreference(
                self.KEY_ANNOUNCE_LANDMARK,
                guilabels.ANNOUNCE_LANDMARKS,
                self.get_announce_landmark,
                self.set_announce_landmark,
            ),
            SpeechPreference(
                self.KEY_ANNOUNCE_LIST,
                guilabels.ANNOUNCE_LISTS,
                self.get_announce_list,
                self.set_announce_list,
            ),
            SpeechPreference(
                self.KEY_ANNOUNCE_GROUPING,
                guilabels.ANNOUNCE_PANELS,
                self.get_announce_grouping,
                self.set_announce_grouping,
            ),
            SpeechPreference(
                self.KEY_ANNOUNCE_TABLE,
                guilabels.ANNOUNCE_TABLES,
                self.get_announce_table,
                self.set_announce_table,
            ),
            SpeechPreference(
                self.KEY_ANNOUNCE_TRACKED_CHANGES,
                guilabels.ANNOUNCE_TRACKED_CHANGES,
                self.get_announce_tracked_changes,
                self.set_announce_tracked_changes,
            ),
        )

        return general, object_details, announcements

    def apply_speech_preferences(
        self,
        updates: Iterable[tuple[SpeechPreference, bool]],
    ) -> dict[str, bool]:
        """Apply the provided speech preference values."""

        result = {}
        for descriptor, value in updates:
            descriptor.setter(value)
            result[descriptor.prefs_key] = value
        return result


_presenter: SpeechPresenter = SpeechPresenter()


def get_presenter() -> SpeechPresenter:
    """Returns the Speech Presenter"""

    return _presenter
