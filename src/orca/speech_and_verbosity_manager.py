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

"""Configures speech and verbosity settings and adjusts strings accordingly."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2025 Igalia, S.L."
__license__   = "LGPL"

import importlib
import locale
import queue
import re
import string
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable, TYPE_CHECKING

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject
from gi.repository import Gtk

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
from . import preferences_grid_base
from . import pronunciation_dictionary_manager
from . import settings
from . import speech
from . import speechserver
from .acss import ACSS
from .ax_document import AXDocument
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default
    from .speechserver import SpeechServer

class CapitalizationStyle(Enum):
    """Capitalization style enumeration with string values from settings."""

    NONE = settings.CAPITALIZATION_STYLE_NONE
    SPELL = settings.CAPITALIZATION_STYLE_SPELL
    ICON = settings.CAPITALIZATION_STYLE_ICON

class PunctuationStyle(Enum):
    """Punctuation style enumeration with int values from settings."""

    NONE = settings.PUNCTUATION_STYLE_NONE
    SOME = settings.PUNCTUATION_STYLE_SOME
    MOST = settings.PUNCTUATION_STYLE_MOST
    ALL = settings.PUNCTUATION_STYLE_ALL

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()

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

    def __init__(self, manager: SpeechAndVerbosityManager) -> None:
        (
            _general_prefs,
            _object_details_prefs,
            announcements_prefs,
        ) = manager.get_speech_preferences()

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[0].label,
                getter=announcements_prefs[0].getter,
                setter=announcements_prefs[0].setter,
                prefs_key=announcements_prefs[0].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[1].label,
                getter=announcements_prefs[1].getter,
                setter=announcements_prefs[1].setter,
                prefs_key=announcements_prefs[1].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[2].label,
                getter=announcements_prefs[2].getter,
                setter=announcements_prefs[2].setter,
                prefs_key=announcements_prefs[2].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[3].label,
                getter=announcements_prefs[3].getter,
                setter=announcements_prefs[3].setter,
                prefs_key=announcements_prefs[3].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[4].label,
                getter=announcements_prefs[4].getter,
                setter=announcements_prefs[4].setter,
                prefs_key=announcements_prefs[4].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=announcements_prefs[5].label,
                getter=announcements_prefs[5].getter,
                setter=announcements_prefs[5].setter,
                prefs_key=announcements_prefs[5].prefs_key,
                member_of=guilabels.ANNOUNCE_WHEN_ENTERING
            ),
        ]

        super().__init__(guilabels.ANNOUNCEMENTS, controls)


class ProgressBarsPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Progress Bars preferences page."""

    def __init__(self, manager: SpeechAndVerbosityManager) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.GENERAL_SPEAK_UPDATES,
                getter=manager.get_speak_progress_bar_updates,
                setter=manager.set_speak_progress_bar_updates,
                prefs_key="speakProgressBarUpdates"
            ),
            preferences_grid_base.IntRangePreferenceControl(
                label=guilabels.GENERAL_FREQUENCY_SECS,
                getter=manager.get_progress_bar_speech_interval,
                setter=manager.set_progress_bar_speech_interval,
                prefs_key="progressBarSpeechInterval",
                minimum=0,
                maximum=100
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.GENERAL_APPLIES_TO,
                getter=manager.get_progress_bar_speech_verbosity,
                setter=manager.set_progress_bar_speech_verbosity,
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
                ]
            ),
        ]

        super().__init__(guilabels.PROGRESS_BARS, controls)


class VerbosityPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Verbosity preferences page."""

    def __init__(self, manager: SpeechAndVerbosityManager) -> None:
        self._manager = manager
        (
            general_prefs,
            object_details_prefs,
            _announcements_prefs,
        ) = manager.get_speech_preferences()

        text_speak_blank_lines = SpeechPreference(
            "speakBlankLines",
            guilabels.SPEECH_SPEAK_BLANK_LINES,
            manager.get_speak_blank_lines,
            manager.set_speak_blank_lines,
        )
        text_speak_misspelled = SpeechPreference(
            "speakMisspelledIndicator",
            guilabels.SPEECH_SPEAK_MISSPELLED_WORD_INDICATOR,
            manager.get_speak_misspelled_indicator,
            manager.set_speak_misspelled_indicator,
        )
        text_speak_indentation = SpeechPreference(
            "enableSpeechIndentation",
            guilabels.SPEECH_SPEAK_INDENTATION_AND_JUSTIFICATION,
            manager.get_speak_indentation_and_justification,
            manager.set_speak_indentation_and_justification,
        )
        text_indentation_only_if_changed = SpeechPreference(
            "speakIndentationOnlyIfChanged",
            guilabels.SPEECH_INDENTATION_ONLY_IF_CHANGED,
            manager.get_speak_indentation_only_if_changed,
            manager.set_speak_indentation_only_if_changed,
        )

        self._only_speak_displayed_control = preferences_grid_base.BooleanPreferenceControl(
            label=object_details_prefs[0].label,
            getter=object_details_prefs[0].getter,
            setter=object_details_prefs[0].setter,
            prefs_key=object_details_prefs[0].prefs_key,
            member_of=guilabels.SPEECH_OBJECT_DETAILS
        )

        self._enable_indentation_control = preferences_grid_base.BooleanPreferenceControl(
            label=text_speak_indentation.label,
            getter=text_speak_indentation.getter,
            setter=text_speak_indentation.setter,
            prefs_key=text_speak_indentation.prefs_key,
            member_of=guilabels.SPEECH_OBJECT_DETAILS,
            determine_sensitivity=self._only_speak_displayed_text_is_off
        )

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=general_prefs[0].label,
                getter=general_prefs[0].getter,
                setter=general_prefs[0].setter,
                prefs_key=general_prefs[0].prefs_key,
                member_of=guilabels.GENERAL
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SPEECH_OBJECT_PRESENTATION_IS_DETAILED,
                getter=manager._get_verbosity_is_verbose,
                setter=manager._set_verbosity_from_bool,
                prefs_key="speechVerbosityLevel",
                member_of=guilabels.GENERAL
            ),
            self._only_speak_displayed_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=object_details_prefs[1].label,
                getter=object_details_prefs[1].getter,
                setter=object_details_prefs[1].setter,
                prefs_key=object_details_prefs[1].prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=object_details_prefs[2].label,
                getter=object_details_prefs[2].getter,
                setter=object_details_prefs[2].setter,
                prefs_key=object_details_prefs[2].prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=object_details_prefs[3].label,
                getter=object_details_prefs[3].getter,
                setter=object_details_prefs[3].setter,
                prefs_key=object_details_prefs[3].prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=object_details_prefs[4].label,
                getter=object_details_prefs[4].getter,
                setter=object_details_prefs[4].setter,
                prefs_key=object_details_prefs[4].prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=text_speak_blank_lines.label,
                getter=text_speak_blank_lines.getter,
                setter=text_speak_blank_lines.setter,
                prefs_key=text_speak_blank_lines.prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=text_speak_misspelled.label,
                getter=text_speak_misspelled.getter,
                setter=text_speak_misspelled.setter,
                prefs_key=text_speak_misspelled.prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._only_speak_displayed_text_is_off
            ),
            self._enable_indentation_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=text_indentation_only_if_changed.label,
                getter=text_indentation_only_if_changed.getter,
                setter=text_indentation_only_if_changed.setter,
                prefs_key=text_indentation_only_if_changed.prefs_key,
                member_of=guilabels.SPEECH_OBJECT_DETAILS,
                determine_sensitivity=self._indentation_enabled
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

    def __init__(self, manager: SpeechAndVerbosityManager) -> None:
        # Table preferences
        table_gui_rows = SpeechPreference(
            "readFullRowInGUITable",
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_GUI_TABLES,
            manager.get_speak_row_in_gui_table,
            manager.set_speak_row_in_gui_table,
        )
        table_doc_rows = SpeechPreference(
            "readFullRowInDocumentTable",
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_DOCUMENT_TABLES,
            manager.get_speak_row_in_document_table,
            manager.set_speak_row_in_document_table,
        )
        table_spreadsheet_rows = SpeechPreference(
            "readFullRowInSpreadSheet",
            guilabels.SPEECH_SPEAK_FULL_ROW_IN_SPREADSHEETS,
            manager.get_speak_row_in_spreadsheet,
            manager.set_speak_row_in_spreadsheet,
        )
        table_cell_headers = SpeechPreference(
            "speakCellHeaders",
            guilabels.TABLE_SPEAK_CELL_HEADER,
            manager.get_announce_cell_headers,
            manager.set_announce_cell_headers,
        )
        table_cell_coords = SpeechPreference(
            "speakCellCoordinates",
            guilabels.TABLE_SPEAK_CELL_COORDINATES,
            manager.get_announce_cell_coordinates,
            manager.set_announce_cell_coordinates,
        )
        table_spreadsheet_coords = SpeechPreference(
            "speakSpreadsheetCoordinates",
            guilabels.SPREADSHEET_SPEAK_CELL_COORDINATES,
            manager.get_announce_spreadsheet_cell_coordinates,
            manager.set_announce_spreadsheet_cell_coordinates,
        )
        table_cell_span = SpeechPreference(
            "speakCellSpan",
            guilabels.TABLE_SPEAK_CELL_SPANS,
            manager.get_announce_cell_span,
            manager.set_announce_cell_span,
        )
        table_selected_range = SpeechPreference(
            "alwaysSpeakSelectedSpreadsheetRange",
            guilabels.SPREADSHEET_SPEAK_SELECTED_RANGE,
            manager.get_always_announce_selected_range_in_spreadsheet,
            manager.set_always_announce_selected_range_in_spreadsheet,
        )

        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=table_gui_rows.label,
                getter=table_gui_rows.getter,
                setter=table_gui_rows.setter,
                prefs_key=table_gui_rows.prefs_key,
                member_of=guilabels.TABLE_ROW_NAVIGATION
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_doc_rows.label,
                getter=table_doc_rows.getter,
                setter=table_doc_rows.setter,
                prefs_key=table_doc_rows.prefs_key,
                member_of=guilabels.TABLE_ROW_NAVIGATION
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_spreadsheet_rows.label,
                getter=table_spreadsheet_rows.getter,
                setter=table_spreadsheet_rows.setter,
                prefs_key=table_spreadsheet_rows.prefs_key,
                member_of=guilabels.TABLE_ROW_NAVIGATION
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_cell_headers.label,
                getter=table_cell_headers.getter,
                setter=table_cell_headers.setter,
                prefs_key=table_cell_headers.prefs_key,
                member_of=guilabels.TABLE_CELL_NAVIGATION
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_cell_coords.label,
                getter=table_cell_coords.getter,
                setter=table_cell_coords.setter,
                prefs_key=table_cell_coords.prefs_key,
                member_of=guilabels.TABLE_CELL_NAVIGATION
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_spreadsheet_coords.label,
                getter=table_spreadsheet_coords.getter,
                setter=table_spreadsheet_coords.setter,
                prefs_key=table_spreadsheet_coords.prefs_key,
                member_of=guilabels.TABLE_CELL_NAVIGATION
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_cell_span.label,
                getter=table_cell_span.getter,
                setter=table_cell_span.setter,
                prefs_key=table_cell_span.prefs_key,
                member_of=guilabels.TABLE_CELL_NAVIGATION
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=table_selected_range.label,
                getter=table_selected_range.getter,
                setter=table_selected_range.setter,
                prefs_key=table_selected_range.prefs_key,
                member_of=guilabels.TABLE_CELL_NAVIGATION
            ),
        ]

        super().__init__(guilabels.TABLES, controls)


class VoicesPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing the Voice settings page."""

    class VoiceType(Enum):
        """Voice type enumeration for voice settings."""

        DEFAULT = 0
        UPPERCASE = 1
        HYPERLINK = 2
        SYSTEM = 3

    def __init__(self, manager: SpeechAndVerbosityManager) -> None:
        super().__init__(guilabels.SPEECH)
        self._manager = manager
        self._initializing = True

        voices = settings.voices
        self._default_voice = ACSS(voices.get(settings.DEFAULT_VOICE, {}))
        self._uppercase_voice = ACSS(voices.get(settings.UPPERCASE_VOICE, {}))
        self._hyperlink_voice = ACSS(voices.get(settings.HYPERLINK_VOICE, {}))
        self._system_voice = ACSS(voices.get(settings.SYSTEM_VOICE, {}))

        # All voice family dicts from server
        self._voice_families: list[speechserver.VoiceFamily] = []
        # Filtered families for each voice type
        self._default_family_choices: list[speechserver.VoiceFamily] = []
        self._hyperlink_family_choices: list[speechserver.VoiceFamily] = []
        self._uppercase_family_choices: list[speechserver.VoiceFamily] = []
        self._system_family_choices: list[speechserver.VoiceFamily] = []

        self._speech_systems_combo: Gtk.ComboBox
        self._speech_synthesizers_combo: Gtk.ComboBox
        self._punctuation_combo: Gtk.ComboBox
        self._capitalization_combo: Gtk.ComboBox
        self._global_frame: Gtk.Frame | None = None
        self._voice_types_frame: Gtk.Frame | None = None

        # Default voice widgets (created on-demand in dialogs)
        self._default_languages_combo: Gtk.ComboBox | None = None
        self._default_families_combo: Gtk.ComboBox | None = None
        self._default_rate_scale: Gtk.Scale | None = None
        self._default_pitch_scale: Gtk.Scale | None = None
        self._default_volume_scale: Gtk.Scale | None = None

        # Hyperlink voice widgets (created on-demand in dialogs)
        self._hyperlink_languages_combo: Gtk.ComboBox | None = None
        self._hyperlink_families_combo: Gtk.ComboBox | None = None
        self._hyperlink_rate_scale: Gtk.Scale | None = None
        self._hyperlink_pitch_scale: Gtk.Scale | None = None
        self._hyperlink_volume_scale: Gtk.Scale | None = None

        # Uppercase voice widgets (created on-demand in dialogs)
        self._uppercase_languages_combo: Gtk.ComboBox | None = None
        self._uppercase_families_combo: Gtk.ComboBox | None = None
        self._uppercase_rate_scale: Gtk.Scale | None = None
        self._uppercase_pitch_scale: Gtk.Scale | None = None
        self._uppercase_volume_scale: Gtk.Scale | None = None

        # System voice widgets (created on-demand in dialogs)
        self._system_languages_combo: Gtk.ComboBox | None = None
        self._system_families_combo: Gtk.ComboBox | None = None
        self._system_rate_scale: Gtk.Scale | None = None
        self._system_pitch_scale: Gtk.Scale | None = None
        self._system_volume_scale: Gtk.Scale | None = None

        self._families_sorted: bool = False

        self._build()
        self._populate_speech_systems()
        self.refresh()

    def _build(self) -> None:
        """Create the Gtk widgets composing the grid."""

        row = 0

        self._global_frame, global_content = self._create_frame(
            guilabels.VOICE_GLOBAL_VOICE_SETTINGS, margin_top=12)

        punctuation_model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_INT)
        punctuation_model.append([
            guilabels.PUNCTUATION_STYLE_NONE, settings.PUNCTUATION_STYLE_NONE])
        punctuation_model.append([
            guilabels.PUNCTUATION_STYLE_SOME, settings.PUNCTUATION_STYLE_SOME])
        punctuation_model.append([
            guilabels.PUNCTUATION_STYLE_MOST, settings.PUNCTUATION_STYLE_MOST])
        punctuation_model.append([
            guilabels.PUNCTUATION_STYLE_ALL, settings.PUNCTUATION_STYLE_ALL])

        capitalization_model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
        capitalization_model.append([
            guilabels.CAPITALIZATION_STYLE_NONE, settings.CAPITALIZATION_STYLE_NONE])
        capitalization_model.append([
            guilabels.CAPITALIZATION_STYLE_ICON, settings.CAPITALIZATION_STYLE_ICON])
        capitalization_model.append([
            guilabels.CAPITALIZATION_STYLE_SPELL, settings.CAPITALIZATION_STYLE_SPELL])

        global_listbox = preferences_grid_base.FocusManagedListBox()
        combo_size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        row_data = [
            (guilabels.VOICE_SPEECH_SYSTEM,
             Gtk.ListStore(GObject.TYPE_STRING),
             self._on_speech_system_changed),
            (guilabels.VOICE_SPEECH_SYNTHESIZER,
             Gtk.ListStore(GObject.TYPE_STRING),
             self._on_speech_synthesizer_changed),
            (guilabels.PUNCTUATION_STYLE,
             punctuation_model,
             self._on_punctuation_changed),
            (guilabels.VOICE_CAPITALIZATION_STYLE,
             capitalization_model,
             self._on_capitalization_changed),
        ]

        global_combos = []
        for label_text, model, changed_handler in row_data:
            # Don't include manual separators - FocusManagedListBox adds them automatically
            row_widget, combo, _label = self._create_combo_box_row(
                label_text, model, changed_handler, include_top_separator=False
            )
            combo_size_group.add_widget(combo)
            global_listbox.add_row_with_widget(row_widget, combo)
            global_combos.append(combo)

        self._speech_systems_combo = global_combos[0]
        self._speech_synthesizers_combo = global_combos[1]
        self._punctuation_combo = global_combos[2]
        self._capitalization_combo = global_combos[3]

        switch_data = [
            (guilabels.VOICE_SPEAK_NUMBERS_AS_DIGITS,
             self._on_speak_numbers_toggled,
             self._manager.get_speak_numbers_as_digits()),
            (guilabels.SPEECH_SPEAK_COLORS_AS_NAMES,
             self._on_use_color_names_toggled,
             self._manager.get_use_color_names()),
            (guilabels.SPEECH_BREAK_INTO_CHUNKS,
             self._on_enable_pause_breaks_toggled,
             self._manager.get_insert_pauses_between_utterances()),
            (guilabels.SPEECH_USE_PRONUNCIATION_DICTIONARY,
             self._on_use_pronunciation_dict_toggled,
             self._manager.get_use_pronunciation_dictionary()),
            (guilabels.AUTO_LANGUAGE_SWITCHING,
             self._on_auto_language_switching_toggled,
             self._manager.get_auto_language_switching()),
        ]

        switches = []
        for label_text, handler, state in switch_data:
            row_widget, switch, _label = self._create_switch_row(
                label_text, handler, state, include_top_separator=False
            )
            global_listbox.add_row_with_widget(row_widget, switch)
            switches.append(switch)

        self._speak_numbers_switch = switches[0]
        self._use_color_names_switch = switches[1]
        self._enable_pause_breaks_switch = switches[2]
        self._use_pronunciation_dict_switch = switches[3]
        self._auto_language_switching_switch = switches[4]

        global_content.add(global_listbox) # pylint: disable=no-member
        self.attach(self._global_frame, 0, row, 1, 1)
        row += 1

        self._voice_types_frame, voice_types_content = self._create_frame(
            guilabels.VOICE_VOICE_TYPE_SETTINGS, margin_top=12
        )

        voice_types_listbox, voice_buttons = self._create_button_listbox([
            (guilabels.SPEECH_VOICE_TYPE_DEFAULT, "applications-system-symbolic",
             lambda _btn: self._show_voice_settings_dialog(self.VoiceType.DEFAULT)),
            (guilabels.SPEECH_VOICE_TYPE_HYPERLINK, "applications-system-symbolic",
             lambda _btn: self._show_voice_settings_dialog(self.VoiceType.HYPERLINK)),
            (guilabels.SPEECH_VOICE_TYPE_UPPERCASE, "applications-system-symbolic",
             lambda _btn: self._show_voice_settings_dialog(self.VoiceType.UPPERCASE)),
            (guilabels.SPEECH_VOICE_TYPE_SYSTEM, "applications-system-symbolic",
             lambda _btn: self._show_voice_settings_dialog(self.VoiceType.SYSTEM)),
        ])

        voice_type_labels = [
            guilabels.SPEECH_VOICE_TYPE_DEFAULT,
            guilabels.SPEECH_VOICE_TYPE_HYPERLINK,
            guilabels.SPEECH_VOICE_TYPE_UPPERCASE,
            guilabels.SPEECH_VOICE_TYPE_SYSTEM,
        ]
        for button, voice_label in zip(voice_buttons, voice_type_labels):
            accessible_name = guilabels.VOICE_TYPE_SETTINGS % voice_label
            button.set_tooltip_text(accessible_name)
            accessible = button.get_accessible()
            if accessible:
                accessible.set_name(accessible_name)

        voice_types_content.add(voice_types_listbox) # pylint: disable=no-member
        self.attach(self._voice_types_frame, 0, row, 1, 1)

    def _show_voice_settings_dialog(self, voice_type: VoicesPreferencesGrid.VoiceType) -> None:
        """Show a dialog for editing settings for a specific voice type."""

        voice_type_labels = {
            self.VoiceType.DEFAULT: guilabels.SPEECH_VOICE_TYPE_DEFAULT,
            self.VoiceType.HYPERLINK: guilabels.SPEECH_VOICE_TYPE_HYPERLINK,
            self.VoiceType.UPPERCASE: guilabels.SPEECH_VOICE_TYPE_UPPERCASE,
            self.VoiceType.SYSTEM: guilabels.SPEECH_VOICE_TYPE_SYSTEM,
        }
        title = voice_type_labels.get(voice_type, "Voice Settings")

        # Save current ACSS state in case user cancels
        voice_acss = self._get_acss_for_voice_type(voice_type)
        saved_acss = ACSS(dict(voice_acss))

        dialog, ok_button = self._create_header_bar_dialog(
            title,
            guilabels.BTN_CANCEL,
            guilabels.BTN_OK
        )

        content_area = dialog.get_content_area()

        voice_listbox = preferences_grid_base.FocusManagedListBox()
        combo_size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        def on_language_changed(widget: Gtk.ComboBox) -> None:
            self._on_speech_language_changed(widget, voice_type)

        lang_row, lang_combo, _lang_label = self._create_combo_box_row(
            guilabels.VOICE_LANGUAGE,
            Gtk.ListStore(GObject.TYPE_STRING),
            on_language_changed,
            include_top_separator=False
        )
        combo_size_group.add_widget(lang_combo)
        voice_listbox.add_row_with_widget(lang_row, lang_combo)

        def on_family_changed(widget: Gtk.ComboBox) -> None:
            self._on_speech_family_changed(widget, voice_type)

        person_row, person_combo, _person_label = self._create_combo_box_row(
            guilabels.VOICE_PERSON,
            Gtk.ListStore(GObject.TYPE_STRING),
            on_family_changed,
            include_top_separator=False
        )
        combo_size_group.add_widget(person_combo)
        voice_listbox.add_row_with_widget(person_row, person_combo)

        def on_rate_changed(widget: Gtk.Scale) -> None:
            self._on_rate_changed(widget, voice_type)

        rate_adj = Gtk.Adjustment(value=50, lower=0, upper=100, step_increment=1, page_increment=10)
        rate_row, rate_scale, _rate_label = self._create_slider_row(
            guilabels.VOICE_RATE,
            rate_adj,
            changed_handler=on_rate_changed,
            include_top_separator=False
        )
        voice_listbox.add_row_with_widget(rate_row, rate_scale)

        def on_pitch_changed(widget: Gtk.Scale) -> None:
            self._on_pitch_changed(widget, voice_type)

        pitch_adj = Gtk.Adjustment(
            value=5.0, lower=0, upper=10, step_increment=0.1, page_increment=1)
        pitch_row, pitch_scale, _pitch_label = self._create_slider_row(
            guilabels.VOICE_PITCH,
            pitch_adj,
            changed_handler=on_pitch_changed,
            include_top_separator=False
        )
        voice_listbox.add_row_with_widget(pitch_row, pitch_scale)

        def on_volume_changed(widget: Gtk.Scale) -> None:
            self._on_volume_changed(widget, voice_type)

        volume_adj = Gtk.Adjustment(
            value=10.0, lower=0, upper=10, step_increment=0.1, page_increment=1)
        volume_row, volume_scale, _volume_label = self._create_slider_row(
            guilabels.VOICE_VOLUME,
            volume_adj,
            changed_handler=on_volume_changed,
            include_top_separator=False
        )
        voice_listbox.add_row_with_widget(volume_row, volume_scale)

        languages_combo = lang_combo
        families_combo = person_combo

        if voice_type == self.VoiceType.DEFAULT:
            self._default_languages_combo = languages_combo
            self._default_families_combo = families_combo
            self._default_rate_scale = rate_scale
            self._default_pitch_scale = pitch_scale
            self._default_volume_scale = volume_scale
        elif voice_type == self.VoiceType.HYPERLINK:
            self._hyperlink_languages_combo = languages_combo
            self._hyperlink_families_combo = families_combo
            self._hyperlink_rate_scale = rate_scale
            self._hyperlink_pitch_scale = pitch_scale
            self._hyperlink_volume_scale = volume_scale
        elif voice_type == self.VoiceType.UPPERCASE:
            self._uppercase_languages_combo = languages_combo
            self._uppercase_families_combo = families_combo
            self._uppercase_rate_scale = rate_scale
            self._uppercase_pitch_scale = pitch_scale
            self._uppercase_volume_scale = volume_scale
        elif voice_type == self.VoiceType.SYSTEM:
            self._system_languages_combo = languages_combo
            self._system_families_combo = families_combo
            self._system_rate_scale = rate_scale
            self._system_pitch_scale = pitch_scale
            self._system_volume_scale = volume_scale

        self._populate_languages_for_voice_type(voice_type)
        self._populate_families_for_voice_type(voice_type, apply_changes=False)

        self._initializing = True
        self._refresh_voice_widgets(voice_type, rate_scale, pitch_scale, volume_scale)
        self._initializing = False

        def on_response(dlg, response_id):
            if response_id in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
                # User cancelled - revert local copy and sync to settings.voices
                voice_acss.clear()
                voice_acss.update(saved_acss)
                self._sync_voice_to_settings(voice_type)
            else:
                # User clicked OK - changes already applied and synced
                self._has_unsaved_changes = True

            dlg.destroy()

        dialog.connect("response", on_response)

        parent = self.get_toplevel() # pylint: disable=no-member
        def on_parent_destroy(*_args):
            if not dialog.get_property("visible"):
                return
            # Trigger cancel response which will clean up and destroy the dialog
            dialog.response(Gtk.ResponseType.DELETE_EVENT)

        parent.connect("destroy", on_parent_destroy)

        content_area.pack_start(voice_listbox, True, True, 0)
        dialog.show_all() # pylint: disable=no-member
        ok_button.grab_default()

    # TODO - JD: Remove this function if it continues to prove unnecessary
    # pylint: disable-next=useless-parent-delegation
    def has_changes(self) -> bool:
        """Return True if there are unsaved changes."""

        return super().has_changes()

    def reload(self) -> None:
        """Reload settings from manager and refresh the UI."""

        voices = settings.voices
        self._default_voice = ACSS(voices.get(settings.DEFAULT_VOICE, {}))
        self._uppercase_voice = ACSS(voices.get(settings.UPPERCASE_VOICE, {}))
        self._hyperlink_voice = ACSS(voices.get(settings.HYPERLINK_VOICE, {}))
        self._system_voice = ACSS(voices.get(settings.SYSTEM_VOICE, {}))

        self._voice_families = self._manager.get_voice_families()
        self._families_sorted = False

        self._has_unsaved_changes = False
        self.refresh()

    def save_settings(self) -> dict[str, dict | list | int | str | bool]:
        """Save settings and return a dictionary of the current values for those settings."""

        result: dict[str, dict | list | int | str | bool] = {
            "voices": {
                settings.DEFAULT_VOICE: dict(self._default_voice),
                settings.UPPERCASE_VOICE: dict(self._uppercase_voice),
                settings.HYPERLINK_VOICE: dict(self._hyperlink_voice),
                settings.SYSTEM_VOICE: dict(self._system_voice),
            }
        }

        server_name = self._manager.get_current_server()
        synthesizer_id = self._manager.get_current_synthesizer()
        result["speechServerInfo"] = [server_name, synthesizer_id]

        result["verbalizePunctuationStyle"] = settings.verbalizePunctuationStyle
        result["capitalizationStyle"] = settings.capitalizationStyle

        # Save switch settings (already saved via handlers, just report them)
        result["speakNumbersAsDigits"] = self._manager.get_speak_numbers_as_digits()
        result["useColorNames"] = self._manager.get_use_color_names()
        result["enablePauseBreaks"] = self._manager.get_insert_pauses_between_utterances()
        result["usePronunciationDictionary"] = self._manager.get_use_pronunciation_dictionary()
        result["enableAutoLanguageSwitching"] = self._manager.get_auto_language_switching()

        self._has_unsaved_changes = False
        return result

    def refresh(self) -> None:
        """Update widget states to reflect current settings."""

        self._initializing = True

        self._populate_speech_systems()

        model = self._punctuation_combo.get_model()
        if model:
            for i, row in enumerate(model):
                if row[1] == settings.verbalizePunctuationStyle:
                    self._punctuation_combo.set_active(i)
                    break

        model = self._capitalization_combo.get_model()
        if model:
            for i, row in enumerate(model):
                if row[1] == settings.capitalizationStyle:
                    self._capitalization_combo.set_active(i)
                    break

        self._speak_numbers_switch.set_active(self._manager.get_speak_numbers_as_digits())
        self._use_color_names_switch.set_active(self._manager.get_use_color_names())
        self._enable_pause_breaks_switch.set_active(
            self._manager.get_insert_pauses_between_utterances())
        self._use_pronunciation_dict_switch.set_active(
            self._manager.get_use_pronunciation_dictionary())
        self._auto_language_switching_switch.set_active(
            self._manager.get_auto_language_switching())

        # Note: Voice type widgets are created on-demand in dialogs, so no need to refresh them here

        self._initializing = False

    def _refresh_voice_widgets(
        self,
        voice_type: VoicesPreferencesGrid.VoiceType,
        rate_scale: Gtk.Scale,
        pitch_scale: Gtk.Scale,
        volume_scale: Gtk.Scale
    ) -> None:
        """Update widgets for a specific voice type."""

        voice_acss = self._get_acss_for_voice_type(voice_type)

        rate = voice_acss.get(ACSS.RATE, 50)
        rate_scale.set_value(rate)

        pitch = voice_acss.get(ACSS.AVERAGE_PITCH, 5.0)
        pitch_scale.set_value(pitch)

        volume = voice_acss.get(ACSS.GAIN, 10.0)
        volume_scale.set_value(volume)

    def _get_acss_for_voice_type(self, voice_type: VoicesPreferencesGrid.VoiceType) -> ACSS:
        """Return the local ACSS copy for the given voice type.

        Returns the local copy that gets saved when Apply/OK is clicked.
        Script activation won't reload settings while the dialog is open,
        so these local copies won't be lost during editing.
        """

        if voice_type == self.VoiceType.DEFAULT:
            return self._default_voice
        if voice_type == self.VoiceType.UPPERCASE:
            return self._uppercase_voice
        if voice_type == self.VoiceType.HYPERLINK:
            return self._hyperlink_voice
        if voice_type == self.VoiceType.SYSTEM:
            return self._system_voice
        return self._default_voice

    def _get_widgets_for_voice_type(
        self,
        voice_type: VoicesPreferencesGrid.VoiceType
    ) -> tuple[Gtk.ComboBox, Gtk.ComboBox, list[speechserver.VoiceFamily]]:
        """Return the widgets and family choices for a given voice type."""

        if voice_type == self.VoiceType.DEFAULT:
            return (self._default_languages_combo,
                   self._default_families_combo,
                   self._default_family_choices)
        if voice_type == self.VoiceType.HYPERLINK:
            return (self._hyperlink_languages_combo,
                   self._hyperlink_families_combo,
                   self._hyperlink_family_choices)
        if voice_type == self.VoiceType.UPPERCASE:
            return (self._uppercase_languages_combo,
                   self._uppercase_families_combo,
                   self._uppercase_family_choices)
        if voice_type == self.VoiceType.SYSTEM:
            return (self._system_languages_combo,
                   self._system_families_combo,
                   self._system_family_choices)
        return (self._default_languages_combo,
               self._default_families_combo,
               self._default_family_choices)

    def _set_family_choices_for_voice_type(
        self,
        voice_type: VoicesPreferencesGrid.VoiceType,
        choices: list[speechserver.VoiceFamily]
    ) -> None:
        """Set the family choices for a given voice type."""

        if voice_type == self.VoiceType.DEFAULT:
            self._default_family_choices = choices
        elif voice_type == self.VoiceType.HYPERLINK:
            self._hyperlink_family_choices = choices
        elif voice_type == self.VoiceType.UPPERCASE:
            self._uppercase_family_choices = choices
        elif voice_type == self.VoiceType.SYSTEM:
            self._system_family_choices = choices


    def _populate_speech_systems(self) -> None:
        """Populate the speech systems combo."""

        self._initializing = True

        model = self._speech_systems_combo.get_model()
        if not model:
            model = Gtk.ListStore(str)
        self._speech_systems_combo.set_model(None)
        model.clear()

        available = self._manager.get_available_servers()
        for server_name in available:
            model.append([server_name])

        self._speech_systems_combo.set_model(model)

        current = self._manager.get_current_server()
        found = False
        selected_server = None
        for i, row in enumerate(model):
            if row[0] == current:
                self._speech_systems_combo.set_active(i)
                selected_server = current
                found = True
                break

        if not found and len(model) > 0:
            self._speech_systems_combo.set_active(0)
            tree_iter = model.get_iter_first()
            if tree_iter:
                selected_server = model.get_value(tree_iter, 0)

        if selected_server:
            self._manager.set_current_server(selected_server)

        self._initializing = False
        self._populate_speech_synthesizers()

    def _populate_speech_synthesizers(self) -> None:
        """Populate the speech synthesizers combo."""

        self._initializing = True

        model = self._speech_synthesizers_combo.get_model()
        if not model:
            model = Gtk.ListStore(str)
        self._speech_synthesizers_combo.set_model(None)
        model.clear()

        available = self._manager.get_available_synthesizers()
        for synth_name in available:
            model.append([synth_name])

        self._speech_synthesizers_combo.set_model(model)

        current = self._manager.get_current_synthesizer()
        found = False
        selected_synth = None
        for i, row in enumerate(model):
            if row[0] == current:
                self._speech_synthesizers_combo.set_active(i)
                selected_synth = current
                found = True
                break

        if not found and len(model) > 0:
            self._speech_synthesizers_combo.set_active(0)
            tree_iter = model.get_iter_first()
            if tree_iter:
                selected_synth = model.get_value(tree_iter, 0)

        if selected_synth:
            self._manager.set_current_synthesizer(selected_synth)

        self._voice_families = self._manager.get_voice_families()
        self._initializing = False
        # Note: Voice widgets are created on-demand in dialogs, so we don't populate them here

    def _populate_languages_for_voice_type(
        self,
        voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Populate the languages combo for a specific voice type."""

        languages_combo, _, _ = self._get_widgets_for_voice_type(voice_type)

        self._initializing = True

        model = languages_combo.get_model()
        if not model:
            model = Gtk.ListStore(str, str)
        languages_combo.set_model(None)
        model.clear()

        if len(self._voice_families) == 0:
            languages_combo.set_model(model)
            self._initializing = False
            return

        if not self._families_sorted:
            default_marker = guilabels.SPEECH_DEFAULT_VOICE.replace("%s", "").strip().lower()

            def _get_sort_key(family):
                variant = family.get(speechserver.VoiceFamily.VARIANT)
                name = family.get(speechserver.VoiceFamily.NAME, "")
                if default_marker in name.lower() or "default" in name.lower():
                    return (0, "")
                if variant not in (None, "none", "None"):
                    return (1, variant.lower())
                return (1, name.lower())

            self._voice_families.sort(key=_get_sort_key)
            self._families_sorted = True

        done = {}
        languages = []
        for family in self._voice_families:
            lang = family.get(speechserver.VoiceFamily.LANG, "")
            dialect = family.get(speechserver.VoiceFamily.DIALECT, "")

            if (lang, dialect) in done:
                continue
            done[(lang, dialect)] = True

            if dialect:
                language = f"{lang}-{dialect}"
            else:
                language = lang

            msg = language if language else "default language"
            languages.append(language)
            model.append([msg])

        languages_combo.set_model(model)

        voice_acss = self._get_acss_for_voice_type(voice_type)
        saved_family: speechserver.VoiceFamily | None = voice_acss.get(ACSS.FAMILY)
        selected_index = 0
        saved_language = ""

        if saved_family:
            lang = saved_family.get(speechserver.VoiceFamily.LANG, "")
            dialect = saved_family.get(speechserver.VoiceFamily.DIALECT, "")
            if dialect:
                saved_language = f"{lang}-{dialect}"
            else:
                saved_language = lang
        elif voice_type == self.VoiceType.DEFAULT:
            family_locale, _encoding = locale.getlocale(locale.LC_MESSAGES)
            if family_locale:
                locale_parts = family_locale.split("_")
                lang = locale_parts[0]
                dialect = locale_parts[1] if len(locale_parts) > 1 else ""
                saved_language = f"{lang}-{dialect}" if dialect else lang

        if saved_language:
            lang_only = saved_language.partition("-")[0]
            partial_match = -1
            for i, language in enumerate(languages):
                if language == saved_language:
                    selected_index = i
                    break
                if partial_match < 0:
                    if language == lang_only or language.startswith(f"{lang_only}-"):
                        partial_match = i
            else:
                if partial_match >= 0:
                    selected_index = partial_match

        if len(languages) > 0:
            languages_combo.set_active(selected_index)

        self._initializing = False

    def _populate_families_for_voice_type(
        self,
        voice_type: VoicesPreferencesGrid.VoiceType,
        apply_changes: bool = True
    ) -> None:
        """Populate the families/persons combo for a specific voice type."""

        languages_combo, families_combo, _ = self._get_widgets_for_voice_type(voice_type)

        self._initializing = True

        families_model = families_combo.get_model()
        if not families_model:
            families_model = Gtk.ListStore(str, str)
        families_combo.set_model(None)
        families_model.clear()

        active = languages_combo.get_active()
        if active < 0:
            families_combo.set_model(families_model)
            self._initializing = False
            return

        languages_model = languages_combo.get_model()
        tree_iter = languages_model.get_iter(active)
        current_language = languages_model.get_value(tree_iter, 0)

        family_choices = []
        for family in self._voice_families:
            lang = family.get(speechserver.VoiceFamily.LANG, "")
            dialect = family.get(speechserver.VoiceFamily.DIALECT, "")

            if dialect:
                language = f"{lang}-{dialect}"
            else:
                language = lang

            if language != current_language:
                continue

            name = family.get(speechserver.VoiceFamily.NAME, "")
            variant = family.get(speechserver.VoiceFamily.VARIANT, "")

            # Show variant if it exists and is not "none", otherwise show name
            display_name = name
            if variant and variant not in ("none", "None"):
                display_name = variant

            family_choices.append(family)
            families_model.append([display_name])

        families_combo.set_model(families_model)

        self._set_family_choices_for_voice_type(voice_type, family_choices)

        voice_acss = self._get_acss_for_voice_type(voice_type)
        saved_family: speechserver.VoiceFamily | None = voice_acss.get(ACSS.FAMILY)
        selected_index = 0

        if saved_family and len(family_choices) > 0:
            saved_name = saved_family.get(speechserver.VoiceFamily.NAME, "")

            for i, family in enumerate(family_choices):
                family_name = family.get(speechserver.VoiceFamily.NAME, "")
                if family_name == saved_name:
                    selected_index = i
                    break

        if len(family_choices) > 0:
            families_combo.set_active(selected_index)

            if apply_changes:
                family = family_choices[selected_index]
                voice_name = family.get(speechserver.VoiceFamily.NAME, "")

                voice_acss[ACSS.FAMILY] = family
                voice_acss["established"] = True

                # Sync to settings.voices so the voice change is heard immediately
                self._sync_voice_to_settings(voice_type)

                # Only set as current voice if this is the default voice type
                if voice_type == self.VoiceType.DEFAULT:
                    self._manager.set_current_voice(voice_name)

        self._initializing = False

    def _sync_voice_to_settings(self, voice_type: VoicesPreferencesGrid.VoiceType) -> None:
        """Sync local voice copy to settings.voices for immediate preview."""

        voice_map = {
            self.VoiceType.DEFAULT: (self._default_voice, settings.DEFAULT_VOICE),
            self.VoiceType.UPPERCASE: (self._uppercase_voice, settings.UPPERCASE_VOICE),
            self.VoiceType.HYPERLINK: (self._hyperlink_voice, settings.HYPERLINK_VOICE),
            self.VoiceType.SYSTEM: (self._system_voice, settings.SYSTEM_VOICE),
        }

        local_voice, settings_key = voice_map[voice_type]
        settings.voices[settings_key] = ACSS(local_voice)

        # Clear the speech server's cached voice properties so the new voice is applied
        server = speech.get_speech_server()
        if server is not None:
            server.clear_cached_voice_properties()

    def _on_rate_changed(
        self,
        widget: Gtk.Scale,
        voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Handle rate slider change for a specific voice type."""

        if self._initializing:
            return

        rate = widget.get_value()
        voice_acss = self._get_acss_for_voice_type(voice_type)
        voice_acss[ACSS.RATE] = rate
        voice_acss["established"] = True
        self._sync_voice_to_settings(voice_type)
        self._has_unsaved_changes = True

    def _on_pitch_changed(
        self,
        widget: Gtk.Scale,
        voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Handle pitch slider change for a specific voice type."""

        if self._initializing:
            return

        pitch = widget.get_value()
        voice_acss = self._get_acss_for_voice_type(voice_type)
        voice_acss[ACSS.AVERAGE_PITCH] = pitch
        voice_acss["established"] = True
        self._sync_voice_to_settings(voice_type)
        self._has_unsaved_changes = True

    def _on_volume_changed(
        self,
        widget: Gtk.Scale,
        voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Handle volume slider change for a specific voice type."""

        if self._initializing:
            return

        volume = widget.get_value()
        voice_acss = self._get_acss_for_voice_type(voice_type)
        voice_acss[ACSS.GAIN] = volume
        voice_acss["established"] = True
        self._sync_voice_to_settings(voice_type)
        self._has_unsaved_changes = True

    def _on_punctuation_changed(self, widget: Gtk.ComboBox) -> None:
        """Handle punctuation combo box change."""

        if self._initializing:
            return

        active = widget.get_active()
        if active < 0:
            return

        model = widget.get_model()
        tree_iter = model.get_iter(active)
        level = model.get_value(tree_iter, 1)

        settings.verbalizePunctuationStyle = level
        self._manager.update_punctuation_level()
        self._has_unsaved_changes = True

    def _on_capitalization_changed(self, widget: Gtk.ComboBox) -> None:
        """Handle capitalization combo box change."""

        if self._initializing:
            return

        active = widget.get_active()
        if active < 0:
            return

        model = widget.get_model()
        tree_iter = model.get_iter(active)
        style = model.get_value(tree_iter, 1)

        settings.capitalizationStyle = style
        self._manager.update_capitalization_style()
        self._has_unsaved_changes = True

    def _on_speak_numbers_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle speak numbers as digits switch change."""
        if self._initializing:
            return
        self._manager.set_speak_numbers_as_digits(switch.get_active())
        self._has_unsaved_changes = True

    def _on_use_color_names_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle use color names switch change."""
        if self._initializing:
            return
        self._manager.set_use_color_names(switch.get_active())
        self._has_unsaved_changes = True

    def _on_enable_pause_breaks_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle enable pause breaks switch change."""
        if self._initializing:
            return
        self._manager.set_insert_pauses_between_utterances(switch.get_active())
        self._has_unsaved_changes = True

    def _on_use_pronunciation_dict_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle use pronunciation dictionary switch change."""
        if self._initializing:
            return
        self._manager.set_use_pronunciation_dictionary(switch.get_active())
        self._has_unsaved_changes = True

    def _on_auto_language_switching_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle auto language switching switch change."""

        if self._initializing:
            return
        self._manager.set_auto_language_switching(switch.get_active())
        self._has_unsaved_changes = True

    def _on_speech_system_changed(self, widget: Gtk.ComboBox) -> None:
        """Handle speech system combo change."""

        if self._initializing:
            return

        active = widget.get_active()
        if active < 0:
            return

        model = widget.get_model()
        tree_iter = model.get_iter(active)
        server_name = model.get_value(tree_iter, 0)

        self._manager.set_current_server(server_name)

        self._populate_speech_synthesizers()
        self._has_unsaved_changes = True

    def _on_speech_synthesizer_changed(self, widget: Gtk.ComboBox) -> None:
        """Handle speech synthesizer combo change."""

        if self._initializing:
            return

        active = widget.get_active()
        if active < 0:
            return

        model = widget.get_model()
        tree_iter = model.get_iter(active)
        synth_name = model.get_value(tree_iter, 0)

        self._manager.set_current_synthesizer(synth_name)

        self._voice_families = self._manager.get_voice_families()
        self._families_sorted = False

        # Clear family for all voice types when synthesizer changes
        for voice_type in [self.VoiceType.DEFAULT, self.VoiceType.HYPERLINK,
                          self.VoiceType.UPPERCASE, self.VoiceType.SYSTEM]:
            voice_acss = self._get_acss_for_voice_type(voice_type)
            if ACSS.FAMILY in voice_acss:
                del voice_acss[ACSS.FAMILY]

        self._has_unsaved_changes = True

    def _on_speech_language_changed(
        self,
        widget: Gtk.ComboBox,
        voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Handle speech language combo change for a specific voice type."""

        if self._initializing:
            return

        self._populate_families_for_voice_type(voice_type)
        self._has_unsaved_changes = True

        if voice_type == self.VoiceType.DEFAULT:
            self._propagate_language_to_other_voices(widget)

    def _propagate_language_to_other_voices(self, _language_combo: Gtk.ComboBox) -> None:
        """Update other voice types to use the same voice family as the Default voice."""

        default_voice = self._get_acss_for_voice_type(self.VoiceType.DEFAULT)
        default_family = default_voice.get(ACSS.FAMILY)
        if not default_family:
            return

        voice_types = [self.VoiceType.HYPERLINK, self.VoiceType.UPPERCASE, self.VoiceType.SYSTEM]
        for voice_type in voice_types:
            voice_acss = self._get_acss_for_voice_type(voice_type)
            voice_acss[ACSS.FAMILY] = default_family
            voice_acss["established"] = True
            self._sync_voice_to_settings(voice_type)

    def _on_speech_family_changed(
        self,
        widget: Gtk.ComboBox,
        voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Handle speech family combo change for a specific voice type."""

        if self._initializing:
            return

        _, _, family_choices = self._get_widgets_for_voice_type(voice_type)

        active = widget.get_active()
        if active < 0 or active >= len(family_choices):
            return

        family = family_choices[active]
        voice_name = family.get(speechserver.VoiceFamily.NAME, "")

        voice_acss = self._get_acss_for_voice_type(voice_type)
        voice_acss[ACSS.FAMILY] = family
        voice_acss["established"] = True
        self._sync_voice_to_settings(voice_type)

        # Only set as current voice if this is the default voice type
        if voice_type == self.VoiceType.DEFAULT:
            self._manager.set_current_voice(voice_name)

        self._has_unsaved_changes = True

class SpeechPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """Main speech preferences grid with enable toggle and categorized settings."""

    def __init__(
        self,
        manager: SpeechAndVerbosityManager,
        title_change_callback: Callable[[str], None] | None = None
    ) -> None:
        super().__init__(guilabels.SPEECH)
        self._manager = manager
        self._initializing = True
        self._title_change_callback = title_change_callback

        # Create child grids (but don't attach them yet - they'll go in the stack detail)
        self._voices_grid = VoicesPreferencesGrid(manager)
        self._verbosity_grid = VerbosityPreferencesGrid(manager)
        self._tables_grid = TablesPreferencesGrid(manager)
        self._progress_bars_grid = ProgressBarsPreferencesGrid(manager)
        self._announcements_grid = AnnouncementsPreferencesGrid(manager)

        self._build()
        self._initializing = False

    def _build(self) -> None:
        row = 0

        categories = [
            (guilabels.VOICE, "voice", self._voices_grid),
            (guilabels.VERBOSITY, "verbosity", self._verbosity_grid),
            (guilabels.TABLES, "tables", self._tables_grid),
            (guilabels.PROGRESS_BARS, "progress-bars", self._progress_bars_grid),
            (guilabels.ANNOUNCEMENTS, "announcements", self._announcements_grid),
        ]

        enable_listbox, stack, _categories_listbox = self._create_multi_page_stack(
            enable_label=guilabels.SPEECH_ENABLE_SPEECH,
            enable_getter=self._manager.get_speech_is_enabled,
            enable_setter=self._manager.set_speech_is_enabled,
            categories=categories,
            title_change_callback=self._title_change_callback,
            main_title=guilabels.SPEECH
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
        self._initializing = False

    def save_settings(self) -> dict:
        """Save all settings from child grids."""

        result: dict[str, Any] = {}
        result["enableSpeech"] = self._manager.get_speech_is_enabled()
        result.update(self._voices_grid.save_settings())
        result.update(self._verbosity_grid.save_settings())
        result.update(self._tables_grid.save_settings())
        result.update(self._progress_bars_grid.save_settings())
        result.update(self._announcements_grid.save_settings())

        return result

    def has_changes(self) -> bool:
        """Check if any child grid has changes."""

        return (self._has_unsaved_changes or
                self._voices_grid.has_changes() or
                self._verbosity_grid.has_changes() or
                self._tables_grid.has_changes() or
                self._progress_bars_grid.has_changes() or
                self._announcements_grid.has_changes())

    def refresh(self) -> None:
        """Refresh all child grids."""

        self._initializing = True
        self._voices_grid.refresh()
        self._verbosity_grid.refresh()
        self._tables_grid.refresh()
        self._progress_bars_grid.refresh()
        self._announcements_grid.refresh()
        self._initializing = False


class SpeechAndVerbosityManager:
    """Configures speech and verbosity settings and adjusts strings accordingly."""

    def __init__(self) -> None:
        self._last_indentation_description: str = ""
        self._last_error_description: str = ""
        self._families_sorted: bool = False
        self._initialized: bool = False

        msg = "SPEECH AND VERBOSITY MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SpeechAndVerbosityManager", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_SPEECH_VERBOSITY

        # Common keybindings (same for desktop and laptop)
        kb_s = keybindings.KeyBinding("s", keybindings.ORCA_MODIFIER_MASK)
        kb_v = keybindings.KeyBinding("v", keybindings.ORCA_MODIFIER_MASK)
        kb_f11 = keybindings.KeyBinding("F11", keybindings.ORCA_MODIFIER_MASK)

        # (name, function, description, desktop_kb, laptop_kb)
        commands_data = [
            ("cycleCapitalizationStyleHandler", self.cycle_capitalization_style,
             cmdnames.CYCLE_CAPITALIZATION_STYLE, None, None),
            ("cycleSpeakingPunctuationLevelHandler", self.cycle_punctuation_level,
             cmdnames.CYCLE_PUNCTUATION_LEVEL, None, None),
            ("cycleSynthesizerHandler", self.cycle_synthesizer,
             cmdnames.CYCLE_SYNTHESIZER, None, None),
            ("changeNumberStyleHandler", self.change_number_style,
             cmdnames.CHANGE_NUMBER_STYLE, None, None),
            ("toggleSilenceSpeechHandler", self.toggle_speech,
             cmdnames.TOGGLE_SPEECH, kb_s, kb_s),
            ("toggleSpeechVerbosityHandler", self.toggle_verbosity,
             cmdnames.TOGGLE_SPEECH_VERBOSITY, kb_v, kb_v),
            ("toggleSpeakingIndentationJustificationHandler", self.toggle_indentation_and_justification,
             cmdnames.TOGGLE_SPOKEN_INDENTATION_AND_JUSTIFICATION, None, None),
            ("toggleTableCellReadModeHandler", self.toggle_table_cell_reading_mode,
             cmdnames.TOGGLE_TABLE_CELL_READ_MODE, kb_f11, kb_f11),
            ("decreaseSpeechRateHandler", self.decrease_rate,
             cmdnames.DECREASE_SPEECH_RATE, None, None),
            ("increaseSpeechRateHandler", self.increase_rate,
             cmdnames.INCREASE_SPEECH_RATE, None, None),
            ("decreaseSpeechPitchHandler", self.decrease_pitch,
             cmdnames.DECREASE_SPEECH_PITCH, None, None),
            ("increaseSpeechPitchHandler", self.increase_pitch,
             cmdnames.INCREASE_SPEECH_PITCH, None, None),
            ("decreaseSpeechVolumeHandler", self.decrease_volume,
             cmdnames.DECREASE_SPEECH_VOLUME, None, None),
            ("increaseSpeechVolumeHandler", self.increase_volume,
             cmdnames.INCREASE_SPEECH_VOLUME, None, None),
        ]

        for name, function, description, desktop_kb, laptop_kb in commands_data:
            manager.add_command(command_manager.KeyboardCommand(
                name, function, group_label, description,
                desktop_keybinding=desktop_kb, laptop_keybinding=laptop_kb))

        msg = "SPEECH AND VERBOSITY MANAGER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _get_server(self) -> SpeechServer | None:
        """Returns the speech server if it is responsive.."""

        result = speech.get_speech_server()
        if result is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Speech server is None."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        result_queue: queue.Queue[bool] = queue.Queue()

        def health_check_thread():
            result.get_output_module()
            result_queue.put(True)

        thread = threading.Thread(target=health_check_thread, daemon=True)
        thread.start()

        try:
            result_queue.get(timeout=2.0)
        except queue.Empty:
            msg = "SPEECH AND VERBOSITY MANAGER: Speech server health check timed out"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        tokens = ["SPEECH AND VERBOSITY MANAGER: Speech server is", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _get_available_servers(self) -> list[str]:
        """Returns a list of available speech servers."""

        return list(self._get_server_module_map().keys())

    def _get_server_module_map(self) -> dict[str, str]:
        """Returns a mapping of server names to module names."""

        result = {}
        for module_name in settings.speechFactoryModules:
            try:
                factory = importlib.import_module(f"orca.{module_name}")
            except ImportError:
                try:
                    factory = importlib.import_module(module_name)
                except ImportError:
                    continue

            try:
                speech_server_class = factory.SpeechServer
                if server_name := speech_server_class.get_factory_name():
                    result[server_name] = module_name

            except (AttributeError, TypeError, ImportError) as error:
                tokens = [f"SPEECH AND VERBOSITY MANAGER: {module_name} not available:", error]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

    def _switch_server(self, target_server: str) -> bool:
        """Switches to the specified server."""

        server_module_map = self._get_server_module_map()
        target_module = server_module_map.get(target_server)
        if not target_module:
            return False

        self.shutdown_speech()
        settings.speechServerFactory = target_module
        self.start_speech()
        return self.get_current_server() == target_server

    @dbus_service.getter
    def get_available_servers(self) -> list[str]:
        """Returns a list of available servers."""

        result = self._get_available_servers()
        msg = f"SPEECH AND VERBOSITY MANAGER: Available servers: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_current_server(self) -> str:
        """Returns the name of the current speech server (Speech Dispatcher or Spiel)."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        name = server.get_factory_name()
        msg = f"SPEECH AND VERBOSITY MANAGER: Server is: {name}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return name

    @dbus_service.setter
    def set_current_server(self, value: str) -> bool:
        """Sets the current speech server (e.g. Speech Dispatcher or Spiel)."""

        return self._switch_server(value)

    @dbus_service.getter
    def get_current_synthesizer(self) -> str:
        """Returns the current synthesizer of the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        result = server.get_output_module()
        msg = f"SPEECH AND VERBOSITY MANAGER: Synthesizer is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_current_synthesizer(self, value: str) -> bool:
        """Sets the current synthesizer of the active speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        available = self.get_available_synthesizers()
        if value not in available:
            tokens = [f"SPEECH AND VERBOSITY MANAGER: '{value}' is not in", available]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting synthesizer to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        server.set_output_module(value)
        return server.get_output_module() == value

    @dbus_service.getter
    def get_available_synthesizers(self) -> list[str]:
        """Returns a list of available synthesizers of the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        synthesizers = server.get_speech_servers()
        result = [s.get_info()[1] for s in synthesizers]
        msg = f"SPEECH AND VERBOSITY MANAGER: Available synthesizers: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_available_voices(self) -> list[str]:
        """Returns a list of available voices for the current synthesizer."""

        server = self._get_server()
        if server is None:
            return []

        voices = server.get_voice_families()
        if not voices:
            return []

        result = []
        for voice in voices:
            if voice_name := voice.get(speechserver.VoiceFamily.NAME, ""):
                result.append(voice_name)
        result = sorted(set(result))
        return result

    def get_voice_families(self) -> list[speechserver.VoiceFamily]:
        """Returns the full list of voice family dictionaries for the current synthesizer.
        Each dictionary contains NAME, LANG, DIALECT, and VARIANT fields."""

        server = self._get_server()
        if server is None:
            return []

        return server.get_voice_families() or []

    @dbus_service.parameterized_command
    def get_voices_for_language(
        self,
        language: str,
        variant: str = "",
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False
    ) -> list[tuple[str, str, str]]:
        """Returns a list of available voices for the specified language."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: get_voices_for_language. Language:", language,
                  "Variant:", variant, "Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            return []

        voices = server.get_voice_families_for_language(language=language, variant=variant)
        result = []
        for name, lang, var in voices:
            result.append((name, lang or "", var or ""))

        msg = f"SPEECH AND VERBOSITY MANAGER: Found {len(result)} voice(s) for '{language}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_current_voice(self) -> str:
        """Returns the current voice name."""

        server = self._get_server()
        if server is None:
            return ""

        result = ""
        if voice_family := server.get_voice_family():
            result = voice_family.get(speechserver.VoiceFamily.NAME, "")

        return result

    @dbus_service.setter
    def set_current_voice(self, voice_name: str) -> bool:
        """Sets the current voice for the active synthesizer."""

        server = self._get_server()
        if server is None:
            return False

        available = self.get_available_voices()
        if voice_name not in available:
            msg = f"SPEECH AND VERBOSITY MANAGER: '{voice_name}' is not in {available}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        voices = server.get_voice_families()
        if not voices:
            return False

        result = False
        for voice_family in voices:
            family_name = voice_family.get(speechserver.VoiceFamily.NAME, "")
            if family_name == voice_name:
                server.set_voice_family(voice_family)
                result = True
                break

        msg = f"SPEECH AND VERBOSITY MANAGER: Set voice to '{voice_name}': {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def get_current_speech_server_info(self) -> tuple[str, str]:
        """Returns the name and ID of the current speech server."""

        # TODO - JD: The result is not in sync with the current output module. Should it be?
        # TODO - JD: The only caller is the preferences dialog. And the useful functionality is in
        # the methods to get (and set) the output module. So why exactly do we need this?
        server = self._get_server()
        if server is None:
            return ("", "")

        server_name, server_id = server.get_info()
        msg = f"SPEECH AND VERBOSITY MANAGER: Speech server info: {server_name}, {server_id}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return server_name, server_id

    def check_speech_setting(self) -> None:
        """Checks the speech setting and initializes speech if necessary."""

        if not settings.enableSpeech:
            msg = "SPEECH AND VERBOSITY MANAGER: Speech is not enabled. Shutting down speech."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.shutdown_speech()
            return

        msg = "SPEECH AND VERBOSITY MANAGER: Speech is enabled."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.start_speech()

    @dbus_service.command
    def start_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False
    ) -> bool:
        """Starts the speech server."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: start_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        speech.init()
        return True

    @dbus_service.command
    def interrupt_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False
    ) -> bool:
        """Interrupts the speech server."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: interrupt_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if server := self._get_server():
            server.stop()

        return True

    @dbus_service.command
    def shutdown_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False
    ) -> bool:
        """Shuts down the speech server."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: shutdown_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if server := self._get_server():
            server.shutdown_active_servers()
            speech.deprecated_clear_server()

        return True

    @dbus_service.command
    def refresh_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False
    ) -> bool:
        """Shuts down and re-initializes speech."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: refresh_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.shutdown_speech()
        self.start_speech()
        return True

    @dbus_service.getter
    def get_rate(self) -> int:
        """Returns the current speech rate."""

        result = 50
        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.RATE in default_voice:
            result = default_voice[ACSS.RATE]

        msg = f"SPEECH AND VERBOSITY MANAGER: Current rate is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_rate(self, value: int) -> bool:
        """Sets the current speech rate (0-100, default: 50)."""

        if not isinstance(value, (int, float)):
            return False

        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.RATE in default_voice:
            default_voice[ACSS.RATE] = value

        msg = f"SPEECH AND VERBOSITY MANAGER: Set rate to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_rate(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Decreases the speech rate."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: decrease_rate. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_rate()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_SLOWER)

        return True

    @dbus_service.command
    def increase_rate(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Increases the speech rate."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: increase_rate. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increase_speech_rate()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_FASTER)

        return True

    @dbus_service.getter
    def get_pitch(self) -> float:
        """Returns the current speech pitch."""

        result = 5.0
        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.AVERAGE_PITCH in default_voice:
            result = default_voice[ACSS.AVERAGE_PITCH]

        msg = f"SPEECH AND VERBOSITY MANAGER: Current pitch is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_pitch(self, value: float) -> bool:
        """Sets the current speech pitch (0.0-10.0, default: 5.0)."""

        if not isinstance(value, (int, float)):
            return False

        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.AVERAGE_PITCH in default_voice:
            default_voice[ACSS.AVERAGE_PITCH] = value

        msg = f"SPEECH AND VERBOSITY MANAGER: Set pitch to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_pitch(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Decreases the speech pitch"""

        tokens = ["SPEECH AND VERBOSITY MANAGER: decrease_pitch. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_pitch()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_LOWER)

        return True

    @dbus_service.command
    def increase_pitch(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Increase the speech pitch"""

        tokens = ["SPEECH AND VERBOSITY MANAGER: increase_pitch. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increase_speech_pitch()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_HIGHER)

        return True

    @dbus_service.getter
    def get_volume(self) -> float:
        """Returns the current speech volume."""

        result = 10.0
        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.GAIN in default_voice:
            result = default_voice[ACSS.GAIN]

        msg = f"SPEECH AND VERBOSITY MANAGER: Current volume is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_volume(self, value: float) -> bool:
        """Sets the current speech volume (0.0-10.0, default: 10.0)."""

        if not isinstance(value, (int, float)):
            return False

        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.GAIN in default_voice:
            default_voice[ACSS.GAIN] = value

        msg = f"SPEECH AND VERBOSITY MANAGER: Set volume to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_volume(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Decreases the speech volume"""

        tokens = ["SPEECH AND VERBOSITY MANAGER: decrease_volume. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_volume()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_SOFTER)

        return True

    @dbus_service.command
    def increase_volume(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Increases the speech volume"""

        tokens = ["SPEECH AND VERBOSITY MANAGER: increase_volume. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increase_speech_volume()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_LOUDER)

        return True

    @dbus_service.getter
    def get_capitalization_style(self) -> str:
        """Returns the current capitalization style."""

        return settings.capitalizationStyle

    @dbus_service.setter
    def set_capitalization_style(self, value: str) -> bool:
        """Sets the capitalization style."""

        try:
            style = CapitalizationStyle[value.upper()]
        except KeyError:
            msg = f"SPEECH AND VERBOSITY MANAGER: Invalid capitalization style: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting capitalization style to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.capitalizationStyle = style.value
        self.update_capitalization_style()
        return True

    @dbus_service.command
    def cycle_capitalization_style(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Cycle through the speech-dispatcher capitalization styles."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: cycle_capitalization_style. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        current_style = settings.capitalizationStyle
        if current_style == settings.CAPITALIZATION_STYLE_NONE:
            new_style = settings.CAPITALIZATION_STYLE_SPELL
            full = messages.CAPITALIZATION_SPELL_FULL
            brief = messages.CAPITALIZATION_SPELL_BRIEF
        elif current_style == settings.CAPITALIZATION_STYLE_SPELL:
            new_style = settings.CAPITALIZATION_STYLE_ICON
            full = messages.CAPITALIZATION_ICON_FULL
            brief = messages.CAPITALIZATION_ICON_BRIEF
        else:
            new_style = settings.CAPITALIZATION_STYLE_NONE
            full = messages.CAPITALIZATION_NONE_FULL
            brief = messages.CAPITALIZATION_NONE_BRIEF

        settings.capitalizationStyle = new_style
        if script is not None and notify_user:
            script.present_message(full, brief)
        self.update_capitalization_style()
        return True

    def update_capitalization_style(self) -> bool:
        """Updates the capitalization style based on the value in settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.update_capitalization_style()
        return True

    @dbus_service.getter
    def get_punctuation_level(self) -> str:
        """Returns the current punctuation level."""

        return PunctuationStyle(settings.verbalizePunctuationStyle).string_name

    @dbus_service.setter
    def set_punctuation_level(self, value: str) -> bool:
        """Sets the punctuation level."""

        try:
            style = PunctuationStyle[value.upper()]
        except KeyError:
            msg = f"SPEECH AND VERBOSITY MANAGER: Invalid punctuation level: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting punctuation level to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.verbalizePunctuationStyle = style.value
        self.update_punctuation_level()
        return True

    @dbus_service.command
    def cycle_punctuation_level(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Cycles through punctuation levels for speech."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: cycle_punctuation_level. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        current_level = settings.verbalizePunctuationStyle
        if current_level == settings.PUNCTUATION_STYLE_NONE:
            new_level = settings.PUNCTUATION_STYLE_SOME
            full = messages.PUNCTUATION_SOME_FULL
            brief = messages.PUNCTUATION_SOME_BRIEF
        elif current_level == settings.PUNCTUATION_STYLE_SOME:
            new_level = settings.PUNCTUATION_STYLE_MOST
            full = messages.PUNCTUATION_MOST_FULL
            brief = messages.PUNCTUATION_MOST_BRIEF
        elif current_level == settings.PUNCTUATION_STYLE_MOST:
            new_level = settings.PUNCTUATION_STYLE_ALL
            full = messages.PUNCTUATION_ALL_FULL
            brief = messages.PUNCTUATION_ALL_BRIEF
        else:
            new_level = settings.PUNCTUATION_STYLE_NONE
            full = messages.PUNCTUATION_NONE_FULL
            brief = messages.PUNCTUATION_NONE_BRIEF

        settings.verbalizePunctuationStyle = new_level
        if script is not None and notify_user:
            script.present_message(full, brief)
        self.update_punctuation_level()
        return True

    def update_punctuation_level(self) -> bool:
        """Updates the punctuation level based on the value in settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.update_punctuation_level()
        return True

    def update_synthesizer(self, server_id: str | None = "") -> None:
        """Updates the synthesizer to the specified id or value from settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        active_id = server.get_output_module()
        info = settings.speechServerInfo or ["", ""]
        if not server_id and len(info) == 2:
            server_id = info[1]

        if server_id and server_id != active_id:
            msg = (
                f"SPEECH AND VERBOSITY MANAGER: Updating synthesizer from {active_id} "
                f"to {server_id}."
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            server.set_output_module(server_id)

    @dbus_service.command
    def cycle_synthesizer(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Cycles through available speech synthesizers."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: cycle_synthesizer. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        available = server.list_output_modules()
        if not available:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get output modules."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        current = server.get_output_module()
        if not current:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get current output module."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        try:
            index = available.index(current) + 1
            if index == len(available):
                index = 0
        except ValueError:
            index = 0

        server.set_output_module(available[index])
        if script is not None and notify_user:
            script.present_message(available[index])
        return True

    @dbus_service.getter
    def get_speak_misspelled_indicator(self) -> bool:
        """Returns whether the misspelled indicator is spoken."""

        return settings.speakMisspelledIndicator

    @dbus_service.setter
    def set_speak_misspelled_indicator(self, value: bool) -> bool:
        """Sets whether the misspelled indicator is spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak misspelled indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakMisspelledIndicator = value
        return True

    @dbus_service.getter
    def get_speak_description(self) -> bool:
        """Returns whether object descriptions are spoken."""

        return settings.speakDescription

    @dbus_service.setter
    def set_speak_description(self, value: bool) -> bool:
        """Sets whether object descriptions are spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak description to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakDescription = value
        return True

    @dbus_service.getter
    def get_speak_position_in_set(self) -> bool:
        """Returns whether the position and set size of objects are spoken."""

        return settings.enablePositionSpeaking

    @dbus_service.setter
    def set_speak_position_in_set(self, value: bool) -> bool:
        """Sets whether the position and set size of objects are spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak position in set to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enablePositionSpeaking = value
        return True

    @dbus_service.getter
    def get_speak_widget_mnemonic(self) -> bool:
        """Returns whether widget mnemonics are spoken."""

        return settings.enableMnemonicSpeaking

    @dbus_service.setter
    def set_speak_widget_mnemonic(self, value: bool) -> bool:
        """Sets whether widget mnemonics are spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak widget mnemonics to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableMnemonicSpeaking = value
        return True

    @dbus_service.getter
    def get_speak_tutorial_messages(self) -> bool:
        """Returns whether tutorial messages are spoken."""

        return settings.enableTutorialMessages

    @dbus_service.setter
    def set_speak_tutorial_messages(self, value: bool) -> bool:
        """Sets whether tutorial messages are spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak tutorial messages to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableTutorialMessages = value
        return True

    @dbus_service.getter
    def get_insert_pauses_between_utterances(self) -> bool:
        """Returns whether pauses are inserted between utterances, e.g. between name and role."""

        return settings.enablePauseBreaks

    @dbus_service.setter
    def set_insert_pauses_between_utterances(self, value: bool) -> bool:
        """Sets whether pauses are inserted between utterances, e.g. between name and role."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting insert pauses to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enablePauseBreaks = value
        return True

    @dbus_service.getter
    def get_repeated_character_limit(self) -> int:
        """Returns the count at which repeated, non-alphanumeric symbols will be described."""

        return settings.repeatCharacterLimit

    @dbus_service.setter
    def set_repeated_character_limit(self, value: int) -> bool:
        """Sets the count at which repeated, non-alphanumeric symbols will be described."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting repeated character limit to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.repeatCharacterLimit = value
        return True

    @dbus_service.getter
    def get_use_pronunciation_dictionary(self) -> bool:
        """Returns whether the user's pronunciation dictionary should be applied."""

        return settings.usePronunciationDictionary

    @dbus_service.setter
    def set_use_pronunciation_dictionary(self, value: bool) -> bool:
        """Sets whether the user's pronunciation dictionary should be applied."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting use pronunciation dictionary to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.usePronunciationDictionary = value
        return True

    @dbus_service.getter
    def get_speak_blank_lines(self) -> bool:
        """Returns whether blank lines will be spoken."""

        return settings.speakBlankLines

    @dbus_service.setter
    def set_speak_blank_lines(self, value: bool) -> bool:
        """Sets whether blank lines will be spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak blank lines to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakBlankLines = value
        return True

    @dbus_service.getter
    def get_speak_row_in_gui_table(self) -> bool:
        """Returns whether Up/Down in GUI tables speaks the row or just the cell."""

        return settings.readFullRowInGUITable

    @dbus_service.setter
    def set_speak_row_in_gui_table(self, value: bool) -> bool:
        """Sets whether Up/Down in GUI tables speaks the row or just the cell."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak row in GUI table to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.readFullRowInGUITable = value
        return True

    @dbus_service.getter
    def get_speak_row_in_document_table(self) -> bool:
        """Returns whether Up/Down in text-document tables speaks the row or just the cell."""

        return settings.readFullRowInDocumentTable

    @dbus_service.setter
    def set_speak_row_in_document_table(self, value: bool) -> bool:
        """Sets whether Up/Down in text-document tables speaks the row or just the cell."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak row in document table to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.readFullRowInDocumentTable = value
        return True

    @dbus_service.getter
    def get_speak_row_in_spreadsheet(self) -> bool:
        """Returns whether Up/Down in spreadsheets speaks the row or just the cell."""

        return settings.readFullRowInSpreadSheet

    @dbus_service.setter
    def set_speak_row_in_spreadsheet(self, value: bool) -> bool:
        """Sets whether Up/Down in spreadsheets speaks the row or just the cell."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak row in spreadsheet to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.readFullRowInSpreadSheet = value
        return True

    @dbus_service.getter
    def get_announce_cell_span(self) -> bool:
        """Returns whether cell spans are announced when greater than 1."""

        return settings.speakCellSpan

    @dbus_service.setter
    def set_announce_cell_span(self, value: bool) -> bool:
        """Sets whether cell spans are announced when greater than 1."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce cell spans to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakCellSpan = value
        return True

    @dbus_service.getter
    def get_announce_cell_coordinates(self) -> bool:
        """Returns whether (non-spreadsheet) cell coordinates are announced."""

        return settings.speakCellCoordinates

    @dbus_service.setter
    def set_announce_cell_coordinates(self, value: bool) -> bool:
        """Sets whether (non-spreadsheet) cell coordinates are announced."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce cell coordinates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakCellCoordinates = value
        return True

    @dbus_service.getter
    def get_announce_spreadsheet_cell_coordinates(self) -> bool:
        """Returns whether spreadsheet cell coordinates are announced."""

        return settings.speakSpreadsheetCoordinates

    @dbus_service.setter
    def set_announce_spreadsheet_cell_coordinates(self, value: bool) -> bool:
        """Sets whether spreadsheet cell coordinates are announced."""

        msg = (
            f"SPEECH AND VERBOSITY MANAGER: Setting announce spreadsheet cell coordinates to "
            f"{value}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakSpreadsheetCoordinates = value
        return True

    @dbus_service.getter
    def get_always_announce_selected_range_in_spreadsheet(self) -> bool:
        """Returns whether the selected range in spreadsheets is always announced."""

        return settings.alwaysSpeakSelectedSpreadsheetRange

    @dbus_service.setter
    def set_always_announce_selected_range_in_spreadsheet(self, value: bool) -> bool:
        """Sets whether the selected range in spreadsheets is always announced."""

        msg = (
            f"SPEECH AND VERBOSITY MANAGER: Setting always announce selected spreadsheet range to "
            f"{value}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.alwaysSpeakSelectedSpreadsheetRange = value
        return True

    @dbus_service.getter
    def get_announce_cell_headers(self) -> bool:
        """Returns whether cell headers are announced."""

        return settings.speakCellHeaders

    @dbus_service.setter
    def set_announce_cell_headers(self, value: bool) -> bool:
        """Sets whether cell headers are announced."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce cell headers to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakCellHeaders = value
        return True

    @dbus_service.getter
    def get_announce_blockquote(self) -> bool:
        """Returns whether blockquotes are announced when entered."""

        return settings.speakContextBlockquote

    @dbus_service.setter
    def set_announce_blockquote(self, value: bool) -> bool:
        """Sets whether blockquotes are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce blockquotes to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextBlockquote = value
        return True

    @dbus_service.getter
    def get_announce_form(self) -> bool:
        """Returns whether non-landmark forms are announced when entered."""

        return settings.speakContextNonLandmarkForm

    @dbus_service.setter
    def set_announce_form(self, value: bool) -> bool:
        """Sets whether non-landmark forms are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce forms to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextNonLandmarkForm = value
        return True

    @dbus_service.getter
    def get_announce_grouping(self) -> bool:
        """Returns whether groupings are announced when entered."""

        return settings.speakContextPanel

    @dbus_service.setter
    def set_announce_grouping(self, value: bool) -> bool:
        """Sets whether groupings are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce groupings to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextPanel = value
        return True

    @dbus_service.getter
    def get_announce_landmark(self) -> bool:
        """Returns whether landmarks are announced when entered."""

        return settings.speakContextLandmark

    @dbus_service.setter
    def set_announce_landmark(self, value: bool) -> bool:
        """Sets whether landmarks are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce landmarks to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextLandmark = value
        return True

    @dbus_service.getter
    def get_announce_list(self) -> bool:
        """Returns whether lists are announced when entered."""

        return settings.speakContextList

    @dbus_service.setter
    def set_announce_list(self, value: bool) -> bool:
        """Sets whether lists are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce lists to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextList = value
        return True

    @dbus_service.getter
    def get_announce_table(self) -> bool:
        """Returns whether tables are announced when entered."""

        return settings.speakContextTable

    @dbus_service.setter
    def set_announce_table(self, value: bool) -> bool:
        """Sets whether tables are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce tables to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakContextTable = value
        return True

    @dbus_service.getter
    def get_use_color_names(self) -> bool:
        """Returns whether colors are announced by name or as RGB values."""

        return settings.useColorNames

    @dbus_service.setter
    def set_use_color_names(self, value: bool) -> bool:
        """Sets whether colors are announced by name or as RGB values."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting use color names to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.useColorNames = value
        return True

    @dbus_service.getter
    def get_speak_numbers_as_digits(self) -> bool:
        """Returns whether numbers are spoken as digits."""

        return settings.speakNumbersAsDigits

    @dbus_service.setter
    def set_speak_numbers_as_digits(self, value: bool) -> bool:
        """Sets whether numbers are spoken as digits."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak numbers as digits to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakNumbersAsDigits = value
        return True

    @dbus_service.getter
    def get_auto_language_switching(self) -> bool:
        """Returns whether automatic language switching is enabled."""

        return settings.enableAutoLanguageSwitching

    @dbus_service.setter
    def set_auto_language_switching(self, value: bool) -> bool:
        """Sets whether automatic language switching is enabled."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting auto language switching to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableAutoLanguageSwitching = value
        return True

    @dbus_service.command
    def change_number_style(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Changes spoken number style between digits and words."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: change_number_style. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        speak_digits = self.get_speak_numbers_as_digits()
        if speak_digits:
            brief = messages.NUMBER_STYLE_WORDS_BRIEF
            full = messages.NUMBER_STYLE_WORDS_FULL
        else:
            brief = messages.NUMBER_STYLE_DIGITS_BRIEF
            full = messages.NUMBER_STYLE_DIGITS_FULL

        self.set_speak_numbers_as_digits(not speak_digits)
        if script is not None and notify_user:
            script.present_message(full, brief)
        return True

    def get_speech_is_enabled_and_not_muted(self) -> bool:
        """Returns whether speech is enabled and not muted."""

        return self.get_speech_is_enabled() and not self.get_speech_is_muted()

    @dbus_service.getter
    def get_speech_is_muted(self) -> bool:
        """Returns whether speech output is temporarily muted."""

        return settings.silenceSpeech

    @dbus_service.setter
    def set_speech_is_muted(self, value: bool) -> bool:
        """Sets whether speech output is temporarily muted."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speech muted to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.silenceSpeech = value
        return True

    @dbus_service.getter
    def get_speech_is_enabled(self) -> bool:
        """Returns whether the speech server is enabled. See also is-muted."""

        return settings.enableSpeech

    @dbus_service.setter
    def set_speech_is_enabled(self, value: bool) -> bool:
        """Sets whether the speech server is enabled. See also is-muted."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speech enabled to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        settings.enableSpeech = value
        if value:
            self.start_speech()
            speech.speak(messages.SPEECH_ENABLED)
        else:
            speech.speak(messages.SPEECH_DISABLED)
            self.shutdown_speech()

        return True

    @dbus_service.getter
    def get_only_speak_displayed_text(self) -> bool:
        """Returns whether only displayed text should be spoken."""

        return settings.onlySpeakDisplayedText

    @dbus_service.setter
    def set_only_speak_displayed_text(self, value: bool) -> bool:
        """Sets whether only displayed text should be spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting only speak displayed text to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.onlySpeakDisplayedText = value
        return True

    @dbus_service.getter
    def get_speak_progress_bar_updates(self) -> bool:
        """Returns whether speech progress bar updates are enabled."""

        return settings.speakProgressBarUpdates

    @dbus_service.setter
    def set_speak_progress_bar_updates(self, value: bool) -> bool:
        """Sets whether speech progress bar updates are enabled."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak progress bar updates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakProgressBarUpdates = value
        return True

    @dbus_service.getter
    def get_progress_bar_speech_interval(self) -> int:
        """Returns the speech progress bar update interval in seconds."""

        return settings.progressBarSpeechInterval

    @dbus_service.setter
    def set_progress_bar_speech_interval(self, value: int) -> bool:
        """Sets the speech progress bar update interval in seconds."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting progress bar speech interval to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.progressBarSpeechInterval = value
        return True

    @dbus_service.getter
    def get_progress_bar_speech_verbosity(self) -> int:
        """Returns the speech progress bar verbosity level."""

        return settings.progressBarSpeechVerbosity

    @dbus_service.setter
    def set_progress_bar_speech_verbosity(self, value: int) -> bool:
        """Sets the speech progress bar verbosity level."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting progress bar speech verbosity to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.progressBarSpeechVerbosity = value
        return True

    @dbus_service.command
    def toggle_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles speech on and off."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: toggle_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if script is not None:
            script.interrupt_presentation()
        if self.get_speech_is_muted():
            self.set_speech_is_muted(False)
            if script is not None and notify_user:
                script.present_message(messages.SPEECH_ENABLED)
        elif not settings.enableSpeech:
            settings.enableSpeech = True
            speech.init()
            if script is not None and notify_user:
                script.present_message(messages.SPEECH_ENABLED)
        else:
            if script is not None and notify_user:
                script.present_message(messages.SPEECH_DISABLED)
            self.set_speech_is_muted(True)
        return True

    @dbus_service.getter
    def get_messages_are_detailed(self) -> bool:
        """Returns whether informative messages will be detailed or brief."""

        return settings.messagesAreDetailed

    @dbus_service.setter
    def set_messages_are_detailed(self, value: bool) -> bool:
        """Sets whether informative messages will be detailed or brief."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting messages are detailed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.messagesAreDetailed = value
        return True

    def use_verbose_speech(self) -> bool:
        """Returns whether the speech verbosity level is set to verbose."""

        return settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE

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
            msg = f"SPEECH AND VERBOSITY MANAGER: Invalid verbosity level: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting verbosity level to {value}."
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

        return self.get_speech_is_enabled() and not self.get_only_speak_displayed_text()

    @dbus_service.command
    def toggle_verbosity(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles speech verbosity level between verbose and brief."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: toggle_verbosity. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_BRIEF:
            if script is not None and notify_user:
                script.present_message(messages.SPEECH_VERBOSITY_VERBOSE)
            settings.speechVerbosityLevel = settings.VERBOSITY_LEVEL_VERBOSE
        else:
            if script is not None and notify_user:
                script.present_message(messages.SPEECH_VERBOSITY_BRIEF)
            settings.speechVerbosityLevel = settings.VERBOSITY_LEVEL_BRIEF
        return True

    @dbus_service.getter
    def get_speak_indentation_and_justification(self) -> bool:
        """Returns whether speaking of indentation and justification is enabled."""

        return settings.enableSpeechIndentation

    @dbus_service.setter
    def set_speak_indentation_and_justification(self, value: bool) -> bool:
        """Sets whether speaking of indentation and justification is enabled."""

        msg = (
            f"SPEECH AND VERBOSITY MANAGER: Setting speak indentation and justification to {value}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableSpeechIndentation = value
        return True

    @dbus_service.getter
    def get_speak_indentation_only_if_changed(self) -> bool:
        """Returns whether indentation will be announced only if it has changed."""

        return settings.speakIndentationOnlyIfChanged

    @dbus_service.setter
    def set_speak_indentation_only_if_changed(self, value: bool) -> bool:
        """Sets whether indentation will be announced only if it has changed."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak indentation only if changed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.speakIndentationOnlyIfChanged = value
        return True

    @dbus_service.command
    def toggle_indentation_and_justification(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles the speaking of indentation and justification."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: toggle_indentation_and_justification. ",
                  "Script:", script, "Event:", event, "notify_user:", notify_user]
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
            script.present_message(full, brief)
        return True

    @dbus_service.command
    def toggle_table_cell_reading_mode(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles between speak cell and speak row."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: toggle_table_cell_reading_mode. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # TODO - JD: This is due to the requirement on script utilities.
        if script is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Toggling table cell reading mode requires script."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        table = AXTable.get_table(focus_manager.get_manager().get_locus_of_focus())
        if table is None and notify_user:
            script.present_message(messages.TABLE_NOT_IN_A)
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
            script.present_message(msg)
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
        if settings.verbalizePunctuationStyle in [settings.PUNCTUATION_STYLE_ALL,
                                                   settings.PUNCTUATION_STYLE_NONE]:
            return False

        return True

    @staticmethod
    def _adjust_for_verbalized_punctuation(obj: Atspi.Accessible, text: str) -> str:
        """Surrounds punctuation symbols with spaces to increase the likelihood of presentation."""

        if not SpeechAndVerbosityManager._should_verbalize_punctuation(obj):
            return text

        result = text
        punctuation = set(re.findall(r"[^\w\s]", result))
        for symbol in punctuation:
            result = result.replace(symbol, f" {symbol} ")

        return result

    def _apply_pronunciation_dictionary(self, text: str) -> str:
        """Applies the pronunciation dictionary to the text."""

        if not self.get_use_pronunciation_dictionary():
            return text

        manager = pronunciation_dictionary_manager.get_manager()
        words = re.split(r"(\W+)", text)
        return "".join(map(manager.get_pronunciation, words))

    def get_indentation_description(
        self,
        line: str,
        only_if_changed: bool | None = None
    ) -> str:
        """Returns a description of the indentation in the given line."""

        if self.get_only_speak_displayed_text() \
           or not self.get_speak_indentation_and_justification():
            return ""

        line = line.replace("\u00a0", " ")
        end = re.search("[^ \t]", line)
        if end:
            line = line[:end.start()]

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
        only_if_changed: bool | None = True
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
        self,
        obj: Atspi.Accessible,
        text: str,
        start_offset: int | None = None
    ) -> str:
        """Adjusts text for spoken presentation."""

        tokens = [f"SPEECH AND VERBOSITY MANAGER: Adjusting '{text}' from",
                  obj, f"start_offset: {start_offset}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXUtilities.is_math_related(obj):
            text = mathsymbols.adjust_for_speech(text)

        if start_offset is not None:
            text = self._adjust_for_links(obj, text, start_offset)

        text = self.adjust_for_digits(obj, text)
        text = self._adjust_for_repeats(text)
        text = self._adjust_for_verbalized_punctuation(obj, text)
        text = self._apply_pronunciation_dictionary(text)

        msg = F"SPEECH AND VERBOSITY MANAGER: Adjusted text: '{text}'"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return text

    def create_speech_preferences_grid(
        self,
        title_change_callback: Callable[[str], None] | None = None
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
                guilabels.SPEECH_SPEAK_OBJECT_MNEMONICS,
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

_manager: SpeechAndVerbosityManager = SpeechAndVerbosityManager()

def get_manager() -> SpeechAndVerbosityManager:
    """Returns the Speech and Verbosity Manager"""

    return _manager
