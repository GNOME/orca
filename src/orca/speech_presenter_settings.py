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

"""Settings keys and values for speech."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from . import gsettings_registry

if TYPE_CHECKING:
    from collections.abc import Callable


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


class SpeechSettings:
    """The speech settings keys."""

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
    KEY_ANNOUNCE_DOCUMENT = "announce-document"
    KEY_ANNOUNCE_FORM = "announce-form"
    KEY_ANNOUNCE_GROUPING = "announce-grouping"
    KEY_ANNOUNCE_HEADER_AND_FOOTER = "announce-header-and-footer"
    KEY_ANNOUNCE_INLINE_CODE = "announce-inline-code"
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
