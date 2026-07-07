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

from . import (
    dbus_service,
    debug,
    document_presenter,
    extension_loader,
    focus_manager,
    gsettings_registry,
    guilabels,
    input_event,
    messages,
    object_properties,
    output_recorder,
    phonnames,
    presentation_manager,
    pronunciation_dictionary_manager,
    say_all_presenter,
    speech_generator,
    speech_manager,
    speech_monitor,
    speech_presenter_command_definitions,
    speechserver,
)
from .acss import ACSS
from .ax_hypertext import AXHypertext
from .ax_text import AXText, AXTextAttribute
from .ax_utilities import AXUtilities
from .extension import Extension, SpeechOutput, SpeechOutputResult
from .speechserver import VoiceFamily
from .text_attribute_manager import TextAttributeChangeMode

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    import gi

    from .command import Command
    from .dbus_service import UInt32
    from .generator import PresentationReason
    from .speech_generator import SpeechGeneratorContext
    from .speech_presenter_preferences_grid import SpeechPreferencesGrid

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

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
    KEY_SPEAK_INDENTATION = "speak-indentation"
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
        self._output_recorder = output_recorder.OutputRecorder("speech")
        super().__init__()

    def _get_commands(self) -> list[Command]:
        """Returns commands for registration."""

        return speech_presenter_command_definitions.get_commands(self)

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
    def get_repeated_character_limit(self) -> UInt32:
        """Returns the count at which repeated, non-alphanumeric symbols will be described."""

        return self._get_setting(self.KEY_REPEATED_CHARACTER_LIMIT, "i", 4)

    @dbus_service.setter
    def set_repeated_character_limit(self, value: UInt32) -> bool:
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
    def get_progress_bar_speech_interval(self) -> UInt32:
        """Returns the speech progress bar update interval in seconds."""

        return self._get_setting(self.KEY_PROGRESS_BAR_SPEECH_INTERVAL, "i", 10)

    @dbus_service.setter
    def set_progress_bar_speech_interval(self, value: UInt32) -> bool:
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
    def get_progress_bar_speech_verbosity(self) -> UInt32:
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
    def set_progress_bar_speech_verbosity(self, value: UInt32) -> bool:
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
        key=KEY_SPEAK_INDENTATION,
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak indentation",
        migration_key="enableSpeechIndentation",
    )
    @dbus_service.getter
    def get_speak_indentation(self) -> bool:
        """Returns whether speaking of indentation is enabled."""

        return self._get_setting(self.KEY_SPEAK_INDENTATION, "b", False)

    @dbus_service.setter
    def set_speak_indentation(self, value: bool) -> bool:
        """Sets whether spoken indentation is enabled."""

        msg = f"SPEECH PRESENTER: Setting spoken indentation to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SPEAK_INDENTATION,
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
    def toggle_indentation(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles spoken indentation."""

        tokens = [
            "SPEECH PRESENTER: toggle_indentation. ",
            "Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        value = self.get_speak_indentation()
        self.set_speak_indentation(not value)
        if self.get_speak_indentation():
            full = messages.INDENTATION_ON_FULL
            brief = messages.INDENTATION_ON_BRIEF
        else:
            full = messages.INDENTATION_OFF_FULL
            brief = messages.INDENTATION_OFF_BRIEF
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

        if AXUtilities.is_web_element(obj):
            return line

        end_offset = start_offset + len(line)
        links = AXUtilities.get_all_links_in_range(obj, start_offset, end_offset)
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
        if AXUtilities.is_plain_text(document):
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

        if self.get_only_speak_displayed_text() or not self.get_speak_indentation():
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
        attributes = AXText.get_text_attributes_at_offset(obj, offset)[0]
        if AXUtilities.attributes_indicate_spelling_error(attributes):
            # TODO - JD: We're using the message here to preserve existing behavior.
            msg = messages.MISSPELLED
        elif AXUtilities.attributes_indicate_grammar_error(attributes):
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

    @dbus_service.testing_command
    def set_log_file_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        value: str = "",
        script: default.Script | None = None,  # pylint: disable=unused-argument
        event: input_event.InputEvent | None = None,  # pylint: disable=unused-argument
    ) -> bool:
        """Opens value for JSONL recording; an empty string closes any open file (test-only)."""

        msg = f"SPEECH PRESENTER: Setting log file to {value!r}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return self._output_recorder.set_path(value)

    def record_interrupt(self) -> None:
        """Records a marker so output observers can drop speech that was interrupted."""

        self._output_recorder.record(kind="interrupt")

    @gsettings_registry.get_registry().gsetting(
        key=KEY_MONITOR_FONT_SIZE,
        schema="speech",
        gtype="i",
        default=14,
        summary="Speech monitor font size",
        migration_key="speechMonitorFontSize",
    )
    @dbus_service.getter
    def get_monitor_font_size(self) -> UInt32:
        """Returns the speech monitor font size."""

        return self._get_setting(self.KEY_MONITOR_FONT_SIZE, "i", 14)

    @dbus_service.setter
    def set_monitor_font_size(self, value: UInt32) -> bool:
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
        """Appends an entry to the speech history buffer used for monitor replay."""

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
        """Flushes the group buffer as a single line to the live monitor and replay history."""

        buffered = self._group_buffer
        self._group_buffer = None
        if not buffered:
            return

        combined = " ".join(buffered)
        monitor = self._monitor_is_writable()
        if monitor is not None:
            monitor.write_text(combined)
        self._append_to_history("text", combined)

    def _record_speech(self, text: str, voice: ACSS) -> None:
        """Writes a per-utterance JSONL entry for test consumers."""

        family = voice.get(ACSS.FAMILY) or {}
        self._output_recorder.record(
            kind="speech",
            text=text,
            language=family.get(VoiceFamily.LANG, "") or "",
            dialect=family.get(VoiceFamily.DIALECT, "") or "",
        )

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

    def _process_speech_output(
        self,
        text: str,
        obj: Atspi.Accessible | None = None,
    ) -> tuple[str, bool]:
        """Lets extensions observe, replace, or consume outgoing speech."""

        handlers = extension_loader.get_loader().iter_speech_output_handlers()
        if not handlers:
            return text, False

        tokens = [
            "SPEECH OUTPUT HOOK: object:",
            obj,
            "text:",
            text,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        for handler in handlers:
            result = self._call_speech_output_handler(handler, SpeechOutput(text, obj))
            if result is None:
                tokens = [
                    "SPEECH OUTPUT HOOK: Extension",
                    handler.module_name,
                    "returned without consuming output.",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                continue
            if result.text is not None:
                tokens = [
                    "SPEECH OUTPUT HOOK: Extension",
                    handler.module_name,
                    "replaced text:",
                    result.text,
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                text = result.text
            if result.consume:
                tokens = [
                    "SPEECH OUTPUT HOOK: Extension",
                    handler.module_name,
                    "consumed output.",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return text, True
            tokens = [
                "SPEECH OUTPUT HOOK: Extension",
                handler.module_name,
                "returned without consuming output.",
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return text, False

    @staticmethod
    def _call_speech_output_handler(
        handler: Extension,
        output: SpeechOutput,
    ) -> SpeechOutputResult | None:
        """Calls a speech output handler and validates the result."""

        tokens = ["SPEECH OUTPUT HOOK: Calling extension:", handler.module_name]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        try:
            result = handler.on_speech_output(output)
        except Exception as error:  # pylint: disable=broad-exception-caught
            msg = (
                f"SPEECH PRESENTER: Extension {handler.module_name} "
                f"failed while handling speech output: {error}"
            )
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        if result is None:
            return None
        if not isinstance(result, SpeechOutputResult):
            msg = (
                f"SPEECH PRESENTER: Extension {handler.module_name} "
                f"returned unexpected speech output result: {result}"
            )
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None
        if result.text is not None and not isinstance(result.text, str):
            msg = (
                f"SPEECH PRESENTER: Extension {handler.module_name} "
                f"returned non-string speech text: {result.text}"
            )
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None
        return result

    def _speak_single(
        self,
        text: str,
        acss: ACSS | dict[str, Any] | None,
        obj: Atspi.Accessible | None = None,
    ) -> None:
        """Speaks an individual string using the given ACSS."""

        resolved_voice = speech_manager.get_manager().apply_voice_set(self._resolve_acss(acss))
        text, consumed = self._process_speech_output(text, obj)

        server = speech_manager.get_manager().get_server()
        if not server:
            msg = f"SPEECH OUTPUT: '{text}' {resolved_voice}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            if consumed:
                self._record_speech(text, resolved_voice)
                self.write_to_monitor(text)
            return

        msg = f"SPEECH OUTPUT: '{text}' {resolved_voice}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if not consumed:
            server.speak(text, resolved_voice)
        self._record_speech(text, resolved_voice)
        self.write_to_monitor(text)

    @staticmethod
    def _resolved_voice(voice: ACSS) -> ACSS:
        """Returns voice with the active voice set applied, for merge-boundary decisions."""

        candidate = ACSS(voice)
        if (voice_type := voice.get(ACSS.VOICE_TYPE)) is not None:
            candidate[ACSS.VOICE_TYPE] = voice_type
        return speech_manager.get_manager().apply_voice_set(candidate)

    def _speak_list(
        self,
        content: list,
        acss: ACSS | dict[str, Any] | None,
        obj: Atspi.Accessible | None,
    ) -> None:
        """Processes a list of speech content items."""

        valid_types = (str, list, speech_generator.Pause, ACSS)

        # to_speak holds text not yet claimed by a trailing ACSS. pending_text holds text
        # already claimed by active_voice, deferred so that a subsequent same-voice group
        # can be merged into one synthesizer call; each _speak_single call produces an
        # audible pause between utterances.
        to_speak: list[str] = []
        pending_text: list[str] = []
        active_voice = ACSS(acss) if acss is not None else acss

        for element in content:
            if not isinstance(element, valid_types):
                msg = f"SPEECH: Bad content sent to speak(): {element}"
                debug.print_message(debug.LEVEL_INFO, msg, True, True)
            elif isinstance(element, list):
                self._speak_list(element, acss, obj)
            elif isinstance(element, str):
                if element.strip(" "):
                    to_speak.append(element)
            elif isinstance(element, speech_generator.Pause):
                if to_speak and to_speak[-1] and to_speak[-1][-1].isalnum():
                    to_speak[-1] += "."
                pending_text.extend(to_speak)
                to_speak = []
                if pending_text:
                    self._speak_single(
                        " ".join(pending_text),
                        active_voice,
                        obj,
                    )
                    pending_text = []
            elif isinstance(element, ACSS):
                new_voice = ACSS(acss)
                new_voice.update(element)
                # Merge text only when the two voices resolve to the same voice once the
                # active voice set is applied. Otherwise a default-voiced name and a
                # system-voiced role (identical until the set overlays them) would be
                # spoken together in whichever voice came last.
                if pending_text and (
                    new_voice != active_voice
                    or self._resolved_voice(active_voice) != self._resolved_voice(new_voice)
                ):
                    tokens = [
                        "SPEECH: New voice",
                        new_voice,
                        " != active voice",
                        active_voice,
                    ]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    self._speak_single(
                        " ".join(pending_text),
                        active_voice,
                        obj,
                    )
                    pending_text = []
                pending_text.extend(to_speak)
                to_speak = []
                active_voice = new_voice

        pending_text.extend(to_speak)
        if pending_text:
            self._speak_single(" ".join(pending_text), active_voice, obj)

    def _speak(
        self,
        content: Any,
        acss: ACSS | dict[str, Any] | None = None,
        obj: Atspi.Accessible | None = None,
    ) -> None:
        """Speaks the given content, which can be a string or a list from the speech generator."""

        if speech_manager.get_manager().get_speech_is_muted():
            return

        if isinstance(content, str):
            msg = f"SPEECH: Speak '{content}' acss: {acss}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._speak_single(content, acss, obj)
            return

        if isinstance(content, list):
            tokens = ["SPEECH: Speak", content, ", acss:", acss]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._begin_monitor_group()
            try:
                self._speak_list(content, acss, obj)
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
        text, consumed = self._process_speech_output(event_string)

        server = speech_manager.get_manager().get_server()
        if server and not consumed:
            if text == event_string:
                server.speak_key_event(event, acss)
            else:
                server.speak(text, acss)
        self.write_key_to_monitor(text)

    def speak_accessible_text(
        self,
        obj: Atspi.Accessible | None,
        text: str,
        start_offset: int | None = None,
    ) -> None:
        """Speaks text from obj, using the specified start_offset for attribute presentation."""

        if obj is not None and start_offset is not None and (script := self._get_active_script()):
            end_offset = start_offset + len(text)
            generator = script.get_speech_generator()
            context = self._build_generator_context()
            if utterances := generator.generate_line(obj, start_offset, end_offset, text, context):
                self._speak(utterances, obj=obj)
                return

        voice = self._get_voice(text, obj)
        text = self.adjust_for_presentation(obj, text, start_offset)
        self._speak(
            text,
            voice[0] if voice else None,
            obj=obj,
        )

    def speak_message(self, text: str, voice_type: str = speechserver.VoiceType.SYSTEM) -> None:
        """Speaks a message using the given voice type (the system voice by default)."""

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
        voice = mgr.get_voice_properties(voice_type)
        if mgr.get_active_voice_set() != gsettings_registry.PRIMARY_VOICE_SET:
            voice[ACSS.VOICE_TYPE] = voice_type

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
        reason: PresentationReason | None = None,
        prior_obj: Atspi.Accessible | None = None,
        *,
        eliminate_pauses: bool = False,
        index: int | None = None,
        total: int | None = None,
    ) -> SpeechGeneratorContext:
        """Builds the settings context for speech generators."""

        from .generator import (  # pylint: disable=import-outside-toplevel
            ContentPosition,
            PresentationReason,
        )
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

        # Automatic language switching only applies while the global voice set is active,
        # regardless of the setting.
        auto_switch = speech_mgr.get_active_voice_set() == gsettings_registry.PRIMARY_VOICE_SET

        return SpeechGeneratorContext(
            enabled=speech_mgr.get_speech_is_enabled(),
            verbose=self.use_verbose_speech(),
            focus=mgr.get_locus_of_focus(),
            in_focus_mode=document_presenter.get_presenter().get_in_focus_mode(),
            active_mode=active_mode,
            reason=reason or PresentationReason.FOCUS_CHANGE,
            prior_obj=prior_obj,
            offset=None,
            leaving=False,
            ancestor_of=None,
            content_item=None,
            content_position=(
                ContentPosition(index=index, total=total)
                if index is not None and total is not None
                else None
            ),
            content_subject=None,
            resolved_role=None,
            role_subject=None,
            include_context=True,
            in_preferences_window=mgr.is_in_preferences_window(),
            auto_language_switching_content=speech_mgr.get_auto_language_switching()
            and auto_switch,
            only_switch_configured_languages=speech_mgr.get_only_switch_configured_languages(),
            voice_set_languages=tuple(speech_mgr.get_voice_set_names()),
            auto_language_switching_ui=speech_mgr.get_auto_language_switching_ui() and auto_switch,
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
            speak_indentation=self.get_speak_indentation(),
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
            language="",
            dialect="",
            eliminate_pauses=eliminate_pauses,
        )

    def generate_speech_contents(
        self,
        script: default.Script,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        *,
        prior_obj: Atspi.Accessible | None = None,
        eliminate_pauses: bool = False,
        index: int | None = None,
        total: int | None = None,
    ) -> list:
        """Generates speech utterances for contents without speaking them."""

        context = self._build_generator_context(
            prior_obj=prior_obj, eliminate_pauses=eliminate_pauses, index=index, total=total
        )
        return script.get_speech_generator().generate_contents(contents, context)

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
        *,
        reason: PresentationReason | None = None,
        prior_obj: Atspi.Accessible | None = None,
    ) -> None:
        """Speaks the specified contents."""

        tokens = ["SPEECH PRESENTER: Speaking", contents]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        if not (active_script := self._get_active_script()):
            return

        context = self._build_generator_context(reason, prior_obj=prior_obj)
        generator = active_script.get_speech_generator()
        utterances = generator.generate_contents(contents, context)
        obj = contents[0][0] if contents else None
        self._speak(utterances, obj=obj)

    def present_generated_speech(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        *,
        prior_obj: Atspi.Accessible | None = None,
        reason: PresentationReason | None = None,
    ) -> None:
        """Generates speech for obj using the script's speech generator and speaks it."""

        context = self._build_generator_context(
            reason,
            prior_obj=prior_obj,
        )
        utterances = script.get_speech_generator().generate_speech(obj, context)
        self._speak(utterances, obj=obj)

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
        self._speak(utterances, obj=obj)

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
        self._speak(utterances, obj=obj)

    def speak_word(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        offset: int,
    ) -> None:
        """Generates and speaks a word using the script's speech generator."""

        context = self._build_generator_context()
        utterances = script.get_speech_generator().generate_word(obj, offset, context)
        self._speak(utterances, obj=obj)

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
                resolved_voice = speech_manager.get_manager().apply_voice_set(
                    self._resolve_acss(acss)
                )
                text, consumed = self._process_speech_output(context.utterance, context.obj)
                output_context = context
                if text != context.utterance:
                    output_context = context.copy()
                    output_context.utterance = text
                self._record_speech(output_context.utterance, resolved_voice)
                self.write_to_monitor(output_context.utterance)
                if consumed:
                    progress_callback(output_context, speechserver.SayAllContext.COMPLETED)
                    continue
                yield output_context, resolved_voice

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
        acss = speech_manager.get_manager().apply_voice_set(
            self._resolve_acss(voice[0] if voice else None)
        )
        msg = f"SPEECH OUTPUT: '{character}'"
        tokens = [msg, acss]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        text, consumed = self._process_speech_output(character, obj)

        server = speech_manager.get_manager().get_server()
        if server and not consumed:
            if text == character and len(text) == 1:
                server.speak_character(character, acss=acss, cap_style=cap_style)
            else:
                server.speak(text, acss)
        self._record_speech(text, acss)
        self.write_to_monitor(text)

    def spell_item(
        self,
        text: str,
        obj: Atspi.Accessible | None = None,
        start_offset: int | None = None,
    ) -> None:
        """Speak the characters in the string one by one."""

        for i, character in enumerate(text):
            language, dialect = self._language_at_offset(obj, start_offset, i)
            self.speak_character(character, obj=obj, language=language, dialect=dialect)

    def spell_phonetically(
        self,
        item_string: str,
        obj: Atspi.Accessible | None = None,
        start_offset: int | None = None,
    ) -> None:
        """Phonetically spell item_string."""

        for i, character in enumerate(item_string):
            language, dialect = self._language_at_offset(obj, start_offset, i)
            voice = self._get_voice(text=character, obj=obj, language=language, dialect=dialect)
            phonetic_string = phonnames.get_phonetic_name(character.lower())
            self._speak(
                phonetic_string,
                voice[0] if voice else None,
                obj=obj,
            )

    @staticmethod
    def _language_at_offset(
        obj: Atspi.Accessible | None, start_offset: int | None, index: int = 0
    ) -> tuple[str, str]:
        """Returns (language, dialect) from text attributes at start_offset + index."""

        if obj is None or start_offset is None:
            return "", ""
        attrs = AXText.get_text_attributes_at_offset(obj, start_offset + index)[0]
        lang = attrs.get("language", "")
        if "-" in lang:
            language, dialect = lang.split("-", 1)
            return language, dialect
        return lang, ""

    def create_speech_preferences_grid(
        self,
        title_change_callback: Callable[[str], None] | None = None,
        app_name: str = "",
    ) -> SpeechPreferencesGrid:
        """Returns the GtkGrid containing the combined speech preferences UI."""

        # pylint: disable-next=import-outside-toplevel
        from .speech_presenter_preferences_grid import SpeechPreferencesGrid

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
