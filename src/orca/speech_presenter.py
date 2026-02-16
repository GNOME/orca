# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2025 Igalia, S.L.
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
# pylint: disable=wrong-import-position
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches

"""Configures verbosity settings and adjusts strings for speech presentation."""

from __future__ import annotations

import re
import string
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable, TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")

from . import cmdnames
from . import command_manager
from . import dbus_service
from . import debug
from . import focus_manager
from . import guilabels
from . import input_event
from . import keybindings
from . import mathsymbols
from . import messages
from . import object_properties
from . import phonnames
from . import preferences_grid_base
from . import presentation_manager
from . import pronunciation_dictionary_manager
from . import settings
from . import speech
from . import speech_monitor
from .acss import ACSS
from .ax_document import AXDocument
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from . import gsettings_migrator
from . import gsettings_registry

if TYPE_CHECKING:
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .input_event import KeyboardEvent
    from .scripts import default


class VerbosityLevel(Enum):
    """Verbosity level enumeration with int values from settings."""

    BRIEF = settings.VERBOSITY_LEVEL_BRIEF
    VERBOSE = settings.VERBOSITY_LEVEL_VERBOSE

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


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
                label=announcements_prefs[0].label,
                getter=announcements_prefs[0].getter,
                setter=announcements_prefs[0].setter,
                prefs_key=announcements_prefs[0].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[1].label,
                getter=announcements_prefs[1].getter,
                setter=announcements_prefs[1].setter,
                prefs_key=announcements_prefs[1].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[2].label,
                getter=announcements_prefs[2].getter,
                setter=announcements_prefs[2].setter,
                prefs_key=announcements_prefs[2].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[3].label,
                getter=announcements_prefs[3].getter,
                setter=announcements_prefs[3].setter,
                prefs_key=announcements_prefs[3].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[4].label,
                getter=announcements_prefs[4].getter,
                setter=announcements_prefs[4].setter,
                prefs_key=announcements_prefs[4].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[5].label,
                getter=announcements_prefs[5].getter,
                setter=announcements_prefs[5].setter,
                prefs_key=announcements_prefs[5].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING,
            ),
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
                prefs_key="speakProgressBarUpdates",
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.GENERAL_FREQUENCY_SECS,
                getter=presenter.get_progress_bar_speech_interval,
                setter=presenter.set_progress_bar_speech_interval,
                prefs_key="progressBarSpeechInterval",
                minimum=0,
                maximum=100,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_APPLIES_TO,
                getter=presenter.get_progress_bar_speech_verbosity,
                setter=presenter.set_progress_bar_speech_verbosity,
                prefs_key="progressBarSpeechVerbosity",
                options=[
                    guilabels.PROGRESS_BAR_ALL,
                    guilabels.PROGRESS_BAR_APPLICATION,
                    guilabels.PROGRESS_BAR_WINDOW,
                ],
                values=[
                    settings.PROGRESS_BAR_ALL,
                    settings.PROGRESS_BAR_APPLICATION,
                    settings.PROGRESS_BAR_WINDOW,
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
            "speakBlankLines",
            guilabels.SPEECH_SPEAK_BLANK_LINES,
            presenter.get_speak_blank_lines,
            presenter.set_speak_blank_lines,
        )
        text_speak_misspelled = SpeechPreference(
            "speakMisspelledIndicator",
            guilabels.SPEECH_SPEAK_MISSPELLED_WORD_INDICATOR,
            presenter.get_speak_misspelled_indicator,
            presenter.set_speak_misspelled_indicator,
        )
        text_speak_indentation = SpeechPreference(
            "enableSpeechIndentation",
            guilabels.SPEECH_SPEAK_INDENTATION_AND_JUSTIFICATION,
            presenter.get_speak_indentation_and_justification,
            presenter.set_speak_indentation_and_justification,
        )
        text_indentation_only_if_changed = SpeechPreference(
            "speakIndentationOnlyIfChanged",
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

        controls = [
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
                prefs_key="speechVerbosityLevel",
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
            "readFullRowInGUITable",
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_GUI_TABLES,
            presenter.get_speak_row_in_gui_table,
            presenter.set_speak_row_in_gui_table,
        )
        table_doc_rows = SpeechPreference(
            "readFullRowInDocumentTable",
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_DOCUMENT_TABLES,
            presenter.get_speak_row_in_document_table,
            presenter.set_speak_row_in_document_table,
        )
        table_spreadsheet_rows = SpeechPreference(
            "readFullRowInSpreadSheet",
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_SPREADSHEETS,
            presenter.get_speak_row_in_spreadsheet,
            presenter.set_speak_row_in_spreadsheet,
        )
        table_cell_headers = SpeechPreference(
            "speakCellHeaders",
            guilabels.TABLE_SPEAK_CELL_HEADER,
            presenter.get_announce_cell_headers,
            presenter.set_announce_cell_headers,
        )
        table_cell_coords = SpeechPreference(
            "speakCellCoordinates",
            guilabels.TABLE_SPEAK_CELL_COORDINATES,
            presenter.get_announce_cell_coordinates,
            presenter.set_announce_cell_coordinates,
        )
        table_spreadsheet_coords = SpeechPreference(
            "speakSpreadsheetCoordinates",
            guilabels.SPREADSHEET_SPEAK_CELL_COORDINATES,
            presenter.get_announce_spreadsheet_cell_coordinates,
            presenter.set_announce_spreadsheet_cell_coordinates,
        )
        table_cell_span = SpeechPreference(
            "speakCellSpan",
            guilabels.TABLE_SPEAK_CELL_SPANS,
            presenter.get_announce_cell_span,
            presenter.set_announce_cell_span,
        )
        table_selected_range = SpeechPreference(
            "alwaysSpeakSelectedSpreadsheetRange",
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
                prefs_key="speechMonitorFontSize",
                minimum=8,
                maximum=72,
                apply_immediately=True,
            ),
            preferences_grid_base.ColorPreferenceControl(
                label=guilabels.SPEECH_MONITOR_FOREGROUND,
                getter=presenter.get_monitor_foreground,
                setter=presenter.set_monitor_foreground,
                prefs_key="speechMonitorForeground",
            ),
            preferences_grid_base.ColorPreferenceControl(
                label=guilabels.SPEECH_MONITOR_BACKGROUND,
                getter=presenter.get_monitor_background,
                setter=presenter.set_monitor_background,
                prefs_key="speechMonitorBackground",
            ),
        ]

        super().__init__(
            guilabels.ON_SCREEN_DISPLAY, controls, info_message=guilabels.SPEECH_MONITOR_INFO
        )


class SpeechPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """Main speech preferences grid with enable toggle and categorized settings."""

    def __init__(
        self,
        presenter: SpeechPresenter,
        title_change_callback: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(guilabels.SPEECH)
        self._presenter = presenter
        self._initializing = True
        self._title_change_callback = title_change_callback

        from . import speech_manager  # pylint: disable=import-outside-toplevel

        manager = speech_manager.get_manager()

        # Create child grids (but don't attach them yet - they'll go in the stack detail)
        self._voices_grid = manager.create_voices_preferences_grid()
        self._verbosity_grid = VerbosityPreferencesGrid(presenter)
        self._tables_grid = TablesPreferencesGrid(presenter)
        self._progress_bars_grid = ProgressBarsPreferencesGrid(presenter)
        self._announcements_grid = AnnouncementsPreferencesGrid(presenter)
        self._osd_grid = SpeechOSDPreferencesGrid(presenter)

        self._build()
        self._initializing = False

    def _build(self) -> None:
        row = 0

        from . import speech_manager  # pylint: disable=import-outside-toplevel

        manager = speech_manager.get_manager()

        categories = [
            (guilabels.VOICE, "voice", self._voices_grid),
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
        self._voices_grid.reload()
        self._verbosity_grid.reload()
        self._tables_grid.reload()
        self._progress_bars_grid.reload()
        self._announcements_grid.reload()
        self._osd_grid.reload()
        self._initializing = False

    def save_settings(self, profile: str = "", app_name: str = "") -> dict:
        """Save all settings from child grids."""

        from . import speech_manager  # pylint: disable=import-outside-toplevel

        manager = speech_manager.get_manager()

        result: dict[str, Any] = {}
        result["enableSpeech"] = manager.get_speech_is_enabled()
        result.update(self._voices_grid.save_settings())
        result.update(self._verbosity_grid.save_settings())
        result.update(self._tables_grid.save_settings())
        result.update(self._progress_bars_grid.save_settings())
        result.update(self._announcements_grid.save_settings())
        result.update(self._osd_grid.save_settings())

        if profile:
            registry = gsettings_registry.get_registry()
            if registry.is_enabled():
                aliased = dict(result)
                gsettings_migrator.apply_legacy_aliases(aliased)
                p = registry.sanitize_gsettings_path(profile)
                skip = not app_name and profile == "default"
                registry.save_schema_to_gsettings("speech", aliased, p, app_name, skip)
                voices = aliased.get("voices", {})
                for voice_type in gsettings_migrator.VOICE_TYPES:
                    voice_data = voices.get(voice_type, {})
                    if not voice_data:
                        continue
                    vt = gsettings_migrator.sanitize_gsettings_path(voice_type)
                    voice_gs = registry.get_settings("voice", p, f"voices/{vt}", app_name)
                    if voice_gs is not None:
                        gsettings_migrator.import_voice(voice_gs, voice_data, skip)

                speech_gs = registry.get_settings("speech", p, "speech", app_name)
                if speech_gs is not None:
                    gsettings_migrator.import_synthesizer(speech_gs, aliased)

        return result

    def has_changes(self) -> bool:
        """Return True if there are unsaved changes."""

        return (
            self._has_unsaved_changes
            or self._voices_grid.has_changes()
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
        self._verbosity_grid.refresh()
        self._tables_grid.refresh()
        self._progress_bars_grid.refresh()
        self._announcements_grid.refresh()
        self._osd_grid.refresh()
        self._initializing = False


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Speech", name="speech")
class SpeechPresenter:
    """Configures verbosity settings and adjusts strings for speech presentation."""

    def __init__(self) -> None:
        self._last_indentation_description: str = ""
        self._last_error_description: str = ""
        self._initialized: bool = False
        self._monitor: speech_monitor.SpeechMonitor | None = None
        self._monitor_enabled_override: bool | None = None
        self._speech_history: list[tuple[str, str]] = []
        self._group_buffer: list[str] | None = None

        msg = "SPEECH PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SpeechPresenter", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        speech.set_monitor_callbacks(
            write_text=self.write_to_monitor,
            write_key=self.write_key_to_monitor,
            write_character=self.write_character_to_monitor,
            begin_group=self._begin_monitor_group,
            end_group=self._end_monitor_group,
        )

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_SPEECH_VERBOSITY

        # Common keybindings (same for desktop and laptop)
        kb_v = keybindings.KeyBinding("v", keybindings.ORCA_MODIFIER_MASK)
        kb_f11 = keybindings.KeyBinding("F11", keybindings.ORCA_MODIFIER_MASK)
        kb_shift_d = keybindings.KeyBinding("d", keybindings.ORCA_SHIFT_MODIFIER_MASK)

        # (name, function, description, desktop_kb, laptop_kb)
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
        ]

        for name, function, description, desktop_kb, laptop_kb in commands_data:
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=desktop_kb,
                    laptop_keybinding=laptop_kb,
                )
            )

        msg = "SPEECH PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    @gsettings_registry.get_registry().gsetting(
        key="speak-misspelled-indicator",
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak misspelled word indicator",
        settings_key="speakMisspelledIndicator",
    )
    @dbus_service.getter
    def get_speak_misspelled_indicator(self) -> bool:
        """Returns whether the misspelled indicator is spoken."""

        return settings.speakMisspelledIndicator

    @dbus_service.setter
    def set_speak_misspelled_indicator(self, value: bool) -> bool:
        """Sets whether the misspelled indicator is spoken."""

        msg = f"SPEECH PRESENTER: Setting speak misspelled indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakMisspelledIndicator = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-description",
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak object descriptions",
        settings_key="speakDescription",
    )
    @dbus_service.getter
    def get_speak_description(self) -> bool:
        """Returns whether object descriptions are spoken."""

        return settings.speakDescription

    @dbus_service.setter
    def set_speak_description(self, value: bool) -> bool:
        """Sets whether object descriptions are spoken."""

        msg = f"SPEECH PRESENTER: Setting speak description to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakDescription = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-position-in-set",
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak position in set",
        settings_key="enablePositionSpeaking",
    )
    @dbus_service.getter
    def get_speak_position_in_set(self) -> bool:
        """Returns whether the position and set size of objects are spoken."""

        return settings.enablePositionSpeaking

    @dbus_service.setter
    def set_speak_position_in_set(self, value: bool) -> bool:
        """Sets whether the position and set size of objects are spoken."""

        msg = f"SPEECH PRESENTER: Setting speak position in set to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enablePositionSpeaking = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-widget-mnemonic",
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak widget mnemonics",
        settings_key="enableMnemonicSpeaking",
    )
    @dbus_service.getter
    def get_speak_widget_mnemonic(self) -> bool:
        """Returns whether widget mnemonics are spoken."""

        return settings.enableMnemonicSpeaking

    @dbus_service.setter
    def set_speak_widget_mnemonic(self, value: bool) -> bool:
        """Sets whether widget mnemonics are spoken."""

        msg = f"SPEECH PRESENTER: Setting speak widget mnemonics to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableMnemonicSpeaking = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-tutorial-messages",
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak tutorial messages",
        settings_key="enableTutorialMessages",
    )
    @dbus_service.getter
    def get_speak_tutorial_messages(self) -> bool:
        """Returns whether tutorial messages are spoken."""

        return settings.enableTutorialMessages

    @dbus_service.setter
    def set_speak_tutorial_messages(self, value: bool) -> bool:
        """Sets whether tutorial messages are spoken."""

        msg = f"SPEECH PRESENTER: Setting speak tutorial messages to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableTutorialMessages = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="repeated-character-limit",
        schema="speech",
        gtype="i",
        default=4,
        summary="Threshold for repeated character compression",
        settings_key="repeatCharacterLimit",
    )
    @dbus_service.getter
    def get_repeated_character_limit(self) -> int:
        """Returns the count at which repeated, non-alphanumeric symbols will be described."""

        return settings.repeatCharacterLimit

    @dbus_service.setter
    def set_repeated_character_limit(self, value: int) -> bool:
        """Sets the count at which repeated, non-alphanumeric symbols will be described."""

        msg = f"SPEECH PRESENTER: Setting repeated character limit to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.repeatCharacterLimit = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-blank-lines",
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak blank lines",
        settings_key="speakBlankLines",
    )
    @dbus_service.getter
    def get_speak_blank_lines(self) -> bool:
        """Returns whether blank lines will be spoken."""

        return settings.speakBlankLines

    @dbus_service.setter
    def set_speak_blank_lines(self, value: bool) -> bool:
        """Sets whether blank lines will be spoken."""

        msg = f"SPEECH PRESENTER: Setting speak blank lines to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakBlankLines = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-row-in-gui-table",
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak full row in GUI tables",
        settings_key="readFullRowInGUITable",
    )
    @dbus_service.getter
    def get_speak_row_in_gui_table(self) -> bool:
        """Returns whether Up/Down in GUI tables speaks the row or just the cell."""

        return settings.readFullRowInGUITable

    @dbus_service.setter
    def set_speak_row_in_gui_table(self, value: bool) -> bool:
        """Sets whether Up/Down in GUI tables speaks the row or just the cell."""

        msg = f"SPEECH PRESENTER: Setting speak row in GUI table to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.readFullRowInGUITable = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-row-in-document-table",
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak full row in document tables",
        settings_key="readFullRowInDocumentTable",
    )
    @dbus_service.getter
    def get_speak_row_in_document_table(self) -> bool:
        """Returns whether Up/Down in text-document tables speaks the row or just the cell."""

        return settings.readFullRowInDocumentTable

    @dbus_service.setter
    def set_speak_row_in_document_table(self, value: bool) -> bool:
        """Sets whether Up/Down in text-document tables speaks the row or just the cell."""

        msg = f"SPEECH PRESENTER: Setting speak row in document table to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.readFullRowInDocumentTable = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-row-in-spreadsheet",
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak full row in spreadsheets",
        settings_key="readFullRowInSpreadSheet",
    )
    @dbus_service.getter
    def get_speak_row_in_spreadsheet(self) -> bool:
        """Returns whether Up/Down in spreadsheets speaks the row or just the cell."""

        return settings.readFullRowInSpreadSheet

    @dbus_service.setter
    def set_speak_row_in_spreadsheet(self, value: bool) -> bool:
        """Sets whether Up/Down in spreadsheets speaks the row or just the cell."""

        msg = f"SPEECH PRESENTER: Setting speak row in spreadsheet to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.readFullRowInSpreadSheet = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-cell-span",
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce cell span",
        settings_key="speakCellSpan",
    )
    @dbus_service.getter
    def get_announce_cell_span(self) -> bool:
        """Returns whether cell spans are announced when greater than 1."""

        return settings.speakCellSpan

    @dbus_service.setter
    def set_announce_cell_span(self, value: bool) -> bool:
        """Sets whether cell spans are announced when greater than 1."""

        msg = f"SPEECH PRESENTER: Setting announce cell spans to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakCellSpan = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-cell-coordinates",
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce cell coordinates",
        settings_key="speakCellCoordinates",
    )
    @dbus_service.getter
    def get_announce_cell_coordinates(self) -> bool:
        """Returns whether (non-spreadsheet) cell coordinates are announced."""

        return settings.speakCellCoordinates

    @dbus_service.setter
    def set_announce_cell_coordinates(self, value: bool) -> bool:
        """Sets whether (non-spreadsheet) cell coordinates are announced."""

        msg = f"SPEECH PRESENTER: Setting announce cell coordinates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakCellCoordinates = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-spreadsheet-cell-coordinates",
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce spreadsheet cell coordinates",
        settings_key="speakSpreadsheetCoordinates",
    )
    @dbus_service.getter
    def get_announce_spreadsheet_cell_coordinates(self) -> bool:
        """Returns whether spreadsheet cell coordinates are announced."""

        return settings.speakSpreadsheetCoordinates

    @dbus_service.setter
    def set_announce_spreadsheet_cell_coordinates(self, value: bool) -> bool:
        """Sets whether spreadsheet cell coordinates are announced."""

        msg = f"SPEECH PRESENTER: Setting announce spreadsheet cell coordinates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakSpreadsheetCoordinates = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="always-announce-selected-range-in-spreadsheet",
        schema="speech",
        gtype="b",
        default=False,
        summary="Always announce selected range in spreadsheets",
        settings_key="alwaysSpeakSelectedSpreadsheetRange",
    )
    @dbus_service.getter
    def get_always_announce_selected_range_in_spreadsheet(self) -> bool:
        """Returns whether the selected range in spreadsheets is always announced."""

        return settings.alwaysSpeakSelectedSpreadsheetRange

    @dbus_service.setter
    def set_always_announce_selected_range_in_spreadsheet(self, value: bool) -> bool:
        """Sets whether the selected range in spreadsheets is always announced."""

        msg = f"SPEECH PRESENTER: Setting always announce selected spreadsheet range to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.alwaysSpeakSelectedSpreadsheetRange = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-cell-headers",
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce cell headers",
        settings_key="speakCellHeaders",
    )
    @dbus_service.getter
    def get_announce_cell_headers(self) -> bool:
        """Returns whether cell headers are announced."""

        return settings.speakCellHeaders

    @dbus_service.setter
    def set_announce_cell_headers(self, value: bool) -> bool:
        """Sets whether cell headers are announced."""

        msg = f"SPEECH PRESENTER: Setting announce cell headers to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakCellHeaders = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-blockquote",
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce blockquotes",
        settings_key="speakContextBlockquote",
    )
    @dbus_service.getter
    def get_announce_blockquote(self) -> bool:
        """Returns whether blockquotes are announced when entered."""

        return settings.speakContextBlockquote

    @dbus_service.setter
    def set_announce_blockquote(self, value: bool) -> bool:
        """Sets whether blockquotes are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce blockquotes to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextBlockquote = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-form",
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce forms",
        settings_key="speakContextNonLandmarkForm",
    )
    @dbus_service.getter
    def get_announce_form(self) -> bool:
        """Returns whether non-landmark forms are announced when entered."""

        return settings.speakContextNonLandmarkForm

    @dbus_service.setter
    def set_announce_form(self, value: bool) -> bool:
        """Sets whether non-landmark forms are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce forms to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextNonLandmarkForm = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-grouping",
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce groupings/panels",
        settings_key="speakContextPanel",
    )
    @dbus_service.getter
    def get_announce_grouping(self) -> bool:
        """Returns whether groupings are announced when entered."""

        return settings.speakContextPanel

    @dbus_service.setter
    def set_announce_grouping(self, value: bool) -> bool:
        """Sets whether groupings are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce groupings to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextPanel = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-landmark",
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce landmarks",
        settings_key="speakContextLandmark",
    )
    @dbus_service.getter
    def get_announce_landmark(self) -> bool:
        """Returns whether landmarks are announced when entered."""

        return settings.speakContextLandmark

    @dbus_service.setter
    def set_announce_landmark(self, value: bool) -> bool:
        """Sets whether landmarks are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce landmarks to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextLandmark = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-list",
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce lists",
        settings_key="speakContextList",
    )
    @dbus_service.getter
    def get_announce_list(self) -> bool:
        """Returns whether lists are announced when entered."""

        return settings.speakContextList

    @dbus_service.setter
    def set_announce_list(self, value: bool) -> bool:
        """Sets whether lists are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce lists to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextList = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-table",
        schema="speech",
        gtype="b",
        default=True,
        summary="Announce tables",
        settings_key="speakContextTable",
    )
    @dbus_service.getter
    def get_announce_table(self) -> bool:
        """Returns whether tables are announced when entered."""

        return settings.speakContextTable

    @dbus_service.setter
    def set_announce_table(self, value: bool) -> bool:
        """Sets whether tables are announced when entered."""

        msg = f"SPEECH PRESENTER: Setting announce tables to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextTable = value
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

        from . import speech_manager  # pylint: disable=import-outside-toplevel

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
        key="only-speak-displayed-text",
        schema="speech",
        gtype="b",
        default=False,
        summary="Only speak displayed text",
        settings_key="onlySpeakDisplayedText",
    )
    @dbus_service.getter
    def get_only_speak_displayed_text(self) -> bool:
        """Returns whether only displayed text should be spoken."""

        return settings.onlySpeakDisplayedText

    @dbus_service.setter
    def set_only_speak_displayed_text(self, value: bool) -> bool:
        """Sets whether only displayed text should be spoken."""

        msg = f"SPEECH PRESENTER: Setting only speak displayed text to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.onlySpeakDisplayedText = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-progress-bar-updates",
        schema="speech",
        gtype="b",
        default=True,
        summary="Speak progress bar updates",
        settings_key="speakProgressBarUpdates",
    )
    @dbus_service.getter
    def get_speak_progress_bar_updates(self) -> bool:
        """Returns whether speech progress bar updates are enabled."""

        return settings.speakProgressBarUpdates

    @dbus_service.setter
    def set_speak_progress_bar_updates(self, value: bool) -> bool:
        """Sets whether speech progress bar updates are enabled."""

        msg = f"SPEECH PRESENTER: Setting speak progress bar updates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakProgressBarUpdates = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="progress-bar-speech-interval",
        schema="speech",
        gtype="i",
        default=10,
        summary="Progress bar speech update interval in seconds",
        settings_key="progressBarSpeechInterval",
    )
    @dbus_service.getter
    def get_progress_bar_speech_interval(self) -> int:
        """Returns the speech progress bar update interval in seconds."""

        return settings.progressBarSpeechInterval

    @dbus_service.setter
    def set_progress_bar_speech_interval(self, value: int) -> bool:
        """Sets the speech progress bar update interval in seconds."""

        msg = f"SPEECH PRESENTER: Setting progress bar speech interval to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.progressBarSpeechInterval = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="progress-bar-speech-verbosity",
        schema="speech",
        genum="org.gnome.Orca.ProgressBarVerbosity",
        default="application",
        summary="Progress bar speech verbosity (all, application, window)",
        settings_key="progressBarSpeechVerbosity",
    )
    @dbus_service.getter
    def get_progress_bar_speech_verbosity(self) -> int:
        """Returns the speech progress bar verbosity level."""

        return settings.progressBarSpeechVerbosity

    @dbus_service.setter
    def set_progress_bar_speech_verbosity(self, value: int) -> bool:
        """Sets the speech progress bar verbosity level."""

        msg = f"SPEECH PRESENTER: Setting progress bar speech verbosity to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.progressBarSpeechVerbosity = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="messages-are-detailed",
        schema="speech",
        gtype="b",
        default=True,
        summary="Use detailed informative messages",
        settings_key="messagesAreDetailed",
    )
    @dbus_service.getter
    def get_messages_are_detailed(self) -> bool:
        """Returns whether informative messages will be detailed or brief."""

        return settings.messagesAreDetailed

    @dbus_service.setter
    def set_messages_are_detailed(self, value: bool) -> bool:
        """Sets whether informative messages will be detailed or brief."""

        msg = f"SPEECH PRESENTER: Setting messages are detailed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.messagesAreDetailed = value
        return True

    def use_verbose_speech(self) -> bool:
        """Returns whether the speech verbosity level is set to verbose."""

        return settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE

    @gsettings_registry.get_registry().gsetting(
        key="verbosity-level",
        schema="speech",
        genum="org.gnome.Orca.VerbosityLevel",
        default="verbose",
        summary="Speech verbosity level (brief, verbose)",
        settings_key="speechVerbosityLevel",
    )
    @dbus_service.getter
    def get_verbosity_level(self) -> str:
        """Returns the current speech verbosity level for object presentation."""

        return VerbosityLevel(settings.speechVerbosityLevel).string_name

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
        settings.speechVerbosityLevel = level.value
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

        from . import speech_manager  # pylint: disable=import-outside-toplevel

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

        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_BRIEF:
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(
                    messages.SPEECH_VERBOSITY_VERBOSE
                )
            settings.speechVerbosityLevel = settings.VERBOSITY_LEVEL_VERBOSE
        else:
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.SPEECH_VERBOSITY_BRIEF)
            settings.speechVerbosityLevel = settings.VERBOSITY_LEVEL_BRIEF
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-indentation-and-justification",
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak indentation and justification",
        settings_key="enableSpeechIndentation",
    )
    @dbus_service.getter
    def get_speak_indentation_and_justification(self) -> bool:
        """Returns whether speaking of indentation and justification is enabled."""

        return settings.enableSpeechIndentation

    @dbus_service.setter
    def set_speak_indentation_and_justification(self, value: bool) -> bool:
        """Sets whether speaking of indentation and justification is enabled."""

        msg = f"SPEECH PRESENTER: Setting speak indentation and justification to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableSpeechIndentation = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-indentation-only-if-changed",
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak indentation only if changed",
        settings_key="speakIndentationOnlyIfChanged",
    )
    @dbus_service.getter
    def get_speak_indentation_only_if_changed(self) -> bool:
        """Returns whether indentation will be announced only if it has changed."""

        return settings.speakIndentationOnlyIfChanged

    @dbus_service.setter
    def set_speak_indentation_only_if_changed(self, value: bool) -> bool:
        """Sets whether indentation will be announced only if it has changed."""

        msg = f"SPEECH PRESENTER: Setting speak indentation only if changed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakIndentationOnlyIfChanged = value
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

        table = AXTable.get_table(focus_manager.get_manager().get_locus_of_focus())
        if table is None and notify_user:
            presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        # TODO - JD: Use the new getters and setters for this.
        if not script.utilities.get_document_for_object(table):
            setting_name = "readFullRowInGUITable"
        elif script.utilities.is_spreadsheet_table(table):
            setting_name = "readFullRowInSpreadSheet"
        else:
            setting_name = "readFullRowInDocumentTable"

        speak_row = getattr(settings, setting_name)
        setattr(settings, setting_name, not speak_row)

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

        if not (settings.speakNumbersAsDigits or AXUtilities.is_text_input_telephone(obj)):
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

        ancestor = AXObject.find_ancestor_inclusive(obj, AXUtilities.is_code)
        if ancestor is None:
            return False

        document = AXObject.find_ancestor_inclusive(ancestor, AXUtilities.is_document)
        if AXDocument.is_plain_text(document):
            return False

        # If the user has set their punctuation level to All, then the synthesizer will
        # do the work for us. If the user has set their punctuation level to None, then
        # they really don't want punctuation and we mustn't override that.
        if settings.verbalizePunctuationStyle in [
            settings.PUNCTUATION_STYLE_ALL,
            settings.PUNCTUATION_STYLE_NONE,
        ]:
            return False

        return True

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

        from . import speech_manager  # pylint: disable=import-outside-toplevel

        if not speech_manager.get_manager().get_use_pronunciation_dictionary():
            return text

        manager = pronunciation_dictionary_manager.get_manager()
        words = re.split(r"(\W+)", text)
        return "".join(map(manager.get_pronunciation, words))

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
        self, obj: Atspi.Accessible, offset: int | None = None, only_if_changed: bool | None = True
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
        if AXText.string_has_spelling_error(obj, offset):
            # TODO - JD: We're using the message here to preserve existing behavior.
            msg = messages.MISSPELLED
        elif AXText.string_has_grammar_error(obj, offset):
            msg = object_properties.STATE_INVALID_GRAMMAR_SPEECH

        if only_if_changed and msg == self._last_error_description:
            return ""

        self._last_error_description = msg
        return msg

    def adjust_for_presentation(
        self, obj: Atspi.Accessible, text: str, start_offset: int | None = None
    ) -> str:
        """Adjusts text for spoken presentation."""

        tokens = [
            f"SPEECH PRESENTER: Adjusting '{text}' from",
            obj,
            f"start_offset: {start_offset}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXUtilities.is_math_related(obj):
            text = mathsymbols.adjust_for_speech(text)

        if start_offset is not None:
            text = self._adjust_for_links(obj, text, start_offset)

        text = self.adjust_for_digits(obj, text)
        text = self._adjust_for_repeats(text)
        text = self._adjust_for_verbalized_punctuation(obj, text)
        text = self._apply_pronunciation_dictionary(text)

        msg = f"SPEECH PRESENTER: Adjusted text: '{text}'"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return text

    def _get_active_script(self) -> default.Script | None:
        """Returns the active script."""

        from . import script_manager  # pylint: disable=import-outside-toplevel

        return script_manager.get_manager().get_active_script()

    def _get_voice(self, text: str = "") -> list[ACSS]:
        """Returns the voice to use for the given string."""

        if active_script := self._get_active_script():
            return active_script.speech_generator.voice(string=text)
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
        key="monitor-font-size",
        schema="speech",
        gtype="i",
        default=14,
        summary="Speech monitor font size",
        settings_key="speechMonitorFontSize",
    )
    @dbus_service.getter
    def get_monitor_font_size(self) -> int:
        """Returns the speech monitor font size."""

        return settings.speechMonitorFontSize

    @dbus_service.setter
    def set_monitor_font_size(self, value: int) -> bool:
        """Sets the speech monitor font size."""

        msg = f"SPEECH PRESENTER: Setting speech monitor font size to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speechMonitorFontSize = value
        if self._monitor is not None:
            self._monitor.set_font_size(value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="monitor-foreground",
        schema="speech",
        gtype="s",
        default="#ffffff",
        summary="Speech monitor foreground color",
        settings_key="speechMonitorForeground",
    )
    @dbus_service.getter
    def get_monitor_foreground(self) -> str:
        """Returns the speech monitor foreground color."""

        return settings.speechMonitorForeground

    @dbus_service.setter
    def set_monitor_foreground(self, value: str) -> bool:
        """Sets the speech monitor foreground color."""

        msg = f"SPEECH PRESENTER: Setting speech monitor foreground to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speechMonitorForeground = value
        if self._monitor is not None:
            self._monitor.reapply_css()
        return True

    @gsettings_registry.get_registry().gsetting(
        key="monitor-background",
        schema="speech",
        gtype="s",
        default="#000000",
        summary="Speech monitor background color",
        settings_key="speechMonitorBackground",
    )
    @dbus_service.getter
    def get_monitor_background(self) -> str:
        """Returns the speech monitor background color."""

        return settings.speechMonitorBackground

    @dbus_service.setter
    def set_monitor_background(self, value: str) -> bool:
        """Sets the speech monitor background color."""

        msg = f"SPEECH PRESENTER: Setting speech monitor background to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speechMonitorBackground = value
        if self._monitor is not None:
            self._monitor.reapply_css()
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
                on_close=lambda: self.set_monitor_is_enabled(False)
            )
            self._monitor.show_all()
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
            elif kind == "char":
                self._monitor.write_character(value)

    def _monitor_is_writable(self) -> speech_monitor.SpeechMonitor | None:
        """Returns the monitor if it exists, is enabled, and doesn't have focus."""

        monitor = self._ensure_monitor()
        if monitor is None:
            return None
        if monitor.has_toplevel_focus():
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

    def write_character_to_monitor(self, character: str) -> None:
        """Writes a character to the speech monitor if active and not focused."""

        monitor = self._monitor_is_writable()
        if monitor is not None:
            monitor.write_character(character)
        self._append_to_history("char", character)

    def present_key_event(self, event: KeyboardEvent) -> None:
        """Presents a key event via speech."""

        key_name = event.get_key_name() if event.is_printable_key() else None
        voice = self._get_voice(text=key_name or "")
        speech.speak_key_event(event, voice[0] if voice else None)

    def present_message(
        self,
        full: str,
        brief: str | None = None,
        voice: ACSS | None = None,
        reset_styles: bool = True,
        force: bool = False,
    ) -> None:
        """Speaks a message, choosing full or brief based on message detail setting."""

        from . import speech_manager  # pylint: disable=import-outside-toplevel

        mgr = speech_manager.get_manager()
        if not mgr.get_speech_is_enabled_and_not_muted():
            return

        if brief is None:
            brief = full

        if not self.get_messages_are_detailed():
            message = brief
        else:
            message = full
        if message:
            self.speak_message(message, voice=voice, reset_styles=reset_styles, force=force)

    def speak_message(
        self,
        text: str,
        voice: ACSS | list[ACSS] | None = None,
        interrupt: bool = True,
        reset_styles: bool = True,
        force: bool = False,
        obj: Atspi.Accessible | None = None,
    ) -> None:
        """Speaks a single string."""

        from . import speech_manager  # pylint: disable=import-outside-toplevel

        try:
            assert isinstance(text, str)
        except AssertionError:
            tokens = ["SPEECH PRESENTER: speak_message called with non-string:", text]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            debug.print_exception(debug.LEVEL_WARNING)
            return

        mgr = speech_manager.get_manager()
        if mgr.get_speech_is_muted() or (self.get_only_speak_displayed_text() and not force):
            return

        voices = settings.voices
        system_voice = voices.get(settings.SYSTEM_VOICE)
        if voice is None:
            voice = system_voice
        voice = voice or system_voice
        if voice == system_voice and reset_styles:
            cap_style = mgr.get_capitalization_style()
            mgr.set_capitalization_style("none")

            punct_style = mgr.get_punctuation_level()
            mgr.set_punctuation_level("some")

        text = self.adjust_for_presentation(obj, text)
        voice_to_use: ACSS | dict[str, Any] | None = None
        if isinstance(voice, list) and voice:
            voice_to_use = voice[0]
        elif not isinstance(voice, list):
            voice_to_use = voice
        speech.speak(text, voice_to_use)

        if voice == system_voice and reset_styles:
            mgr.set_capitalization_style(cap_style)
            mgr.set_punctuation_level(punct_style)

    def speak_contents(
        self, contents: list[tuple[Atspi.Accessible, int, int, str]], **args: Any
    ) -> None:
        """Speaks the specified contents."""

        tokens = ["SPEECH PRESENTER: Speaking", contents, args]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        if not (active_script := self._get_active_script()):
            return

        utterances = active_script.speech_generator.generate_contents(contents, **args)
        speech.speak(utterances)

    def present_generated_speech(
        self, script: default.Script, obj: Atspi.Accessible, **args: Any
    ) -> None:
        """Generates speech for obj using the script's speech generator and speaks it."""

        utterances = script.speech_generator.generate_speech(obj, **args)
        speech.speak(utterances)

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

        utterances = script.speech_generator.generate_line(obj, start_offset, end_offset, line)
        speech.speak(utterances)

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
            self.speak_character(phrase)
            return

        indentation = self.get_indentation_description(phrase)
        if indentation:
            self.speak_message(indentation)

        utterances = script.speech_generator.generate_phrase(obj, start_offset, end_offset, phrase)
        speech.speak(utterances)

    def speak_word(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        offset: int,
    ) -> None:
        """Generates and speaks a word using the script's speech generator."""

        utterances = script.speech_generator.generate_word(obj, offset)
        speech.speak(utterances)

    def speak_character_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        character: str,
    ) -> None:
        """Handles presentation of a character at the given offset."""

        if not character or character == "\r":
            character = "\n"

        if character == "\n":
            line_string = AXText.get_line_at_offset(obj, max(0, offset))[0]
            if not line_string or line_string == "\n":
                if self.get_speak_blank_lines():
                    self.speak_message(messages.BLANK, interrupt=False)
                return

        if character in ["\n", "\r\n"]:
            if self.get_speak_blank_lines():
                self.speak_message(messages.BLANK, interrupt=False)
            return

        if error := self.get_error_description(obj, offset):
            self.speak_message(error)

        self.speak_character(character)

    def speak_string(self, text: str, voice: ACSS | list[ACSS] | None = None) -> None:
        """Speaks a string using the specified voice."""

        voice_to_use: ACSS | dict[str, Any] | None = None
        if isinstance(voice, list) and voice:
            voice_to_use = voice[0]
        elif not isinstance(voice, list):
            voice_to_use = voice
        speech.speak(text, voice_to_use)

    def say_all(self, utterance_iterator: Any, progress_callback: Callable[..., Any]) -> None:
        """Speaks each item in the utterance_iterator."""

        speech.say_all(utterance_iterator, progress_callback)

    def speak_character(self, character: str) -> None:
        """Speaks a single character."""

        voice = self._get_voice(text=character)
        speech.speak_character(character, voice[0] if voice else None)

    def spell_item(self, text: str) -> None:
        """Speak the characters in the string one by one."""

        for character in text:
            self.speak_character(character)

    def spell_phonetically(self, item_string: str) -> None:
        """Phonetically spell item_string."""

        for character in item_string:
            voice = self._get_voice(text=character)
            phonetic_string = phonnames.get_phonetic_name(character.lower())
            self.speak_message(phonetic_string, voice)

    def create_speech_preferences_grid(
        self, title_change_callback: Callable[[str], None] | None = None
    ) -> SpeechPreferencesGrid:
        """Returns the GtkGrid containing the combined speech preferences UI."""

        return SpeechPreferencesGrid(self, title_change_callback)

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
                "messagesAreDetailed",
                guilabels.SPEECH_SYSTEM_MESSAGES_ARE_DETAILED,
                self.get_messages_are_detailed,
                self.set_messages_are_detailed,
            ),
        )

        object_details = (
            SpeechPreference(
                "onlySpeakDisplayedText",
                guilabels.SPEECH_ONLY_SPEAK_DISPLAYED_TEXT,
                self.get_only_speak_displayed_text,
                self.set_only_speak_displayed_text,
            ),
            SpeechPreference(
                "speakDescription",
                guilabels.SPEECH_SPEAK_DESCRIPTION,
                self.get_speak_description,
                self.set_speak_description,
            ),
            SpeechPreference(
                "enablePositionSpeaking",
                guilabels.SPEECH_SPEAK_CHILD_POSITION,
                self.get_speak_position_in_set,
                self.set_speak_position_in_set,
            ),
            SpeechPreference(
                "enableMnemonicSpeaking",
                guilabels.PRESENT_OBJECT_MNEMONICS,
                self.get_speak_widget_mnemonic,
                self.set_speak_widget_mnemonic,
            ),
            SpeechPreference(
                "enableTutorialMessages",
                guilabels.SPEECH_SPEAK_TUTORIAL_MESSAGES,
                self.get_speak_tutorial_messages,
                self.set_speak_tutorial_messages,
            ),
        )

        announcements = (
            SpeechPreference(
                "speakContextBlockquote",
                guilabels.ANNOUNCE_BLOCKQUOTES,
                self.get_announce_blockquote,
                self.set_announce_blockquote,
            ),
            SpeechPreference(
                "speakContextNonLandmarkForm",
                guilabels.ANNOUNCE_FORMS,
                self.get_announce_form,
                self.set_announce_form,
            ),
            SpeechPreference(
                "speakContextLandmark",
                guilabels.ANNOUNCE_LANDMARKS,
                self.get_announce_landmark,
                self.set_announce_landmark,
            ),
            SpeechPreference(
                "speakContextList",
                guilabels.ANNOUNCE_LISTS,
                self.get_announce_list,
                self.set_announce_list,
            ),
            SpeechPreference(
                "speakContextPanel",
                guilabels.ANNOUNCE_PANELS,
                self.get_announce_grouping,
                self.set_announce_grouping,
            ),
            SpeechPreference(
                "speakContextTable",
                guilabels.ANNOUNCE_TABLES,
                self.get_announce_table,
                self.set_announce_table,
            ),
        )

        return general, object_details, announcements

    def apply_speech_preferences(
        self, updates: Iterable[tuple[SpeechPreference, bool]]
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
