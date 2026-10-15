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

"""Enums used by more than one part of Orca."""

from enum import Enum, StrEnum, auto


class ActivePresentationMode(StrEnum):
    """The mode responsible for Orca's current region of interest."""

    CARET_NAVIGATOR = "caret-navigator"
    CARET_TRACKING = "caret-tracking"
    FLAT_REVIEW = "flat-review"
    FOCUS_TRACKING = "focus-tracking"
    MATH_NAVIGATOR = "math-navigator"
    MOUSE_REVIEW = "mouse-review"
    OBJECT_NAVIGATOR = "object-navigator"
    SAY_ALL = "say-all"
    STRUCTURAL_NAVIGATOR = "structural-navigator"
    TABLE_NAVIGATOR = "table-navigator"


class BraillePanDirection(Enum):
    """Braille panning direction."""

    LEFT = "left"
    RIGHT = "right"


class CaretSetReason(Enum):
    """Enum representing the reason Orca set the caret offset."""

    BRAILLE_CUT = auto()
    BRAILLE_PANNING = auto()
    BRAILLE_ROUTING = auto()
    CARET_NAVIGATION = auto()
    FLAT_REVIEW = auto()
    LINE_PRESENTATION = auto()
    LIVE_REGION_NAVIGATION = auto()
    MATH_NAVIGATION = auto()
    OBJECT_PRESENTATION = auto()
    RESULT_NAVIGATION = auto()
    SAY_ALL_COMMAND = auto()
    SCROLL_INTO_VIEW = auto()
    STRUCTURAL_NAVIGATION = auto()
    TABLE_NAVIGATION = auto()
    TEXT_SELECTION_BY_CHARACTER = auto()
    TEXT_SELECTION_BY_LINE = auto()
    TEXT_SELECTION_BY_WORD = auto()
    TEXT_SELECTION_TO_FILE_BOUNDARY = auto()
    TEXT_SELECTION_TO_LINE_BOUNDARY = auto()

    def is_text_selection(self) -> bool:
        """Returns True if the caret was set while changing a text selection."""

        return self in {
            CaretSetReason.TEXT_SELECTION_BY_CHARACTER,
            CaretSetReason.TEXT_SELECTION_BY_LINE,
            CaretSetReason.TEXT_SELECTION_BY_WORD,
            CaretSetReason.TEXT_SELECTION_TO_FILE_BOUNDARY,
            CaretSetReason.TEXT_SELECTION_TO_LINE_BOUNDARY,
        }


class PresentationReason(Enum):
    """Why a presentation is being generated, beyond what active_mode captures."""

    FOCUS_CHANGE = "focus-change"
    STATE_CHANGE = "state-change"
    PROGRESS_BAR_UPDATE = "progress-bar-update"
    WHERE_AM_I_BASIC = "where-am-i-basic"
    WHERE_AM_I_DETAILED = "where-am-i-detailed"


class StructuralNavigationMode(Enum):
    """Represents the structural navigation modes available."""

    OFF = "OFF"
    DOCUMENT = "DOCUMENT"
    GUI = "GUI"


class TextEventReason(Enum):
    """Enum representing the reason for an object:text- event."""

    UNKNOWN = auto()
    AUTO_DELETION_PRESENTABLE = auto()
    AUTO_DELETION_UNPRESENTABLE = auto()
    AUTO_INSERTION_PRESENTABLE = auto()
    AUTO_INSERTION_UNPRESENTABLE = auto()
    AUTO_SELECTION = auto()
    AUTO_UNSELECTION = auto()
    BACKSPACE = auto()
    BRAILLE_PANNING = auto()
    CHILDREN_CHANGE = auto()
    CUT = auto()
    DELETE = auto()
    FOCUS_CHANGE = auto()
    LIVE_REGION_UPDATE = auto()
    MOUSE_MIDDLE_BUTTON = auto()
    MOUSE_PRIMARY_BUTTON = auto()
    NAVIGATION_BY_CHARACTER = auto()
    NAVIGATION_BY_LINE = auto()
    NAVIGATION_BY_PARAGRAPH = auto()
    NAVIGATION_BY_PAGE = auto()
    NAVIGATION_BY_WORD = auto()
    NAVIGATION_TO_FILE_BOUNDARY = auto()
    NAVIGATION_TO_LINE_BOUNDARY = auto()
    PAGE_SWITCH = auto()
    PASTE = auto()
    REDO = auto()
    SAY_ALL = auto()
    SEARCH_PRESENTABLE = auto()
    SEARCH_UNPRESENTABLE = auto()
    SELECT_ALL = auto()
    SELECTED_TEXT_DELETION = auto()
    SELECTED_TEXT_INSERTION = auto()
    SELECTED_TEXT_RESTORATION = auto()
    SELECTION_BY_CHARACTER = auto()
    SELECTION_BY_LINE = auto()
    SELECTION_BY_PARAGRAPH = auto()
    SELECTION_BY_PAGE = auto()
    SELECTION_BY_WORD = auto()
    SELECTION_UNPRESENTABLE = auto()
    SELECTION_TO_FILE_BOUNDARY = auto()
    SELECTION_TO_LINE_BOUNDARY = auto()
    SPIN_BUTTON_VALUE_CHANGE = auto()
    SYSTEM_UPDATE = auto()
    TERMINAL_LINE_NAVIGATION_REPAINT = auto()
    TYPING = auto()
    TYPING_ECHOABLE = auto()
    UI_UPDATE = auto()
    UNDO = auto()
    UNSPECIFIED_COMMAND = auto()
    UNSPECIFIED_NAVIGATION = auto()
    UNSPECIFIED_SELECTION = auto()


class TextUnit(Enum):
    """Text units that can be spoken."""

    CHAR = auto()
    WORD = auto()
    LINE = auto()
    PHRASE = auto()


class VoiceType(StrEnum):
    """Voice type identifiers. Values match GSettings path components."""

    DEFAULT = "default"
    UPPERCASE = "uppercase"
    HYPERLINK = "hyperlink"
    SYSTEM = "system"
