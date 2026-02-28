# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

"""Utilities for accessible events."""

from __future__ import annotations

import enum
import threading
import time
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug, focus_manager
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities_collection import AXUtilitiesCollection
from .ax_utilities_component import AXUtilitiesComponent
from .ax_utilities_object import AXUtilitiesObject
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState
from .ax_utilities_text import AXUtilitiesText
from .ax_value import AXValue

if TYPE_CHECKING:
    from typing import ClassVar

    from .input_event_manager import InputEventManager


class TextEventReason(enum.Enum):
    """Enum representing the reason for an object:text- event."""

    UNKNOWN = enum.auto()
    AUTO_DELETION = enum.auto()
    AUTO_INSERTION_PRESENTABLE = enum.auto()
    AUTO_INSERTION_UNPRESENTABLE = enum.auto()
    BACKSPACE = enum.auto()
    CHILDREN_CHANGE = enum.auto()
    CUT = enum.auto()
    DELETE = enum.auto()
    FOCUS_CHANGE = enum.auto()
    LIVE_REGION_UPDATE = enum.auto()
    MOUSE_MIDDLE_BUTTON = enum.auto()
    MOUSE_PRIMARY_BUTTON = enum.auto()
    NAVIGATION_BY_CHARACTER = enum.auto()
    NAVIGATION_BY_LINE = enum.auto()
    NAVIGATION_BY_PARAGRAPH = enum.auto()
    NAVIGATION_BY_PAGE = enum.auto()
    NAVIGATION_BY_WORD = enum.auto()
    NAVIGATION_TO_FILE_BOUNDARY = enum.auto()
    NAVIGATION_TO_LINE_BOUNDARY = enum.auto()
    PAGE_SWITCH = enum.auto()
    PASTE = enum.auto()
    REDO = enum.auto()
    SAY_ALL = enum.auto()
    SEARCH_PRESENTABLE = enum.auto()
    SEARCH_UNPRESENTABLE = enum.auto()
    SELECT_ALL = enum.auto()
    SELECTED_TEXT_DELETION = enum.auto()
    SELECTED_TEXT_INSERTION = enum.auto()
    SELECTED_TEXT_RESTORATION = enum.auto()
    SELECTION_BY_CHARACTER = enum.auto()
    SELECTION_BY_LINE = enum.auto()
    SELECTION_BY_PARAGRAPH = enum.auto()
    SELECTION_BY_PAGE = enum.auto()
    SELECTION_BY_WORD = enum.auto()
    SELECTION_TO_FILE_BOUNDARY = enum.auto()
    SELECTION_TO_LINE_BOUNDARY = enum.auto()
    SPIN_BUTTON_VALUE_CHANGE = enum.auto()
    TYPING = enum.auto()
    TYPING_ECHOABLE = enum.auto()
    UI_UPDATE = enum.auto()
    UNDO = enum.auto()
    UNSPECIFIED_COMMAND = enum.auto()
    UNSPECIFIED_NAVIGATION = enum.auto()
    UNSPECIFIED_SELECTION = enum.auto()


class AXUtilitiesEvent:
    """Utilities for accessible events."""

    LAST_KNOWN_DESCRIPTION: ClassVar[dict[int, str]] = {}
    LAST_KNOWN_NAME: ClassVar[dict[int, str]] = {}

    LAST_KNOWN_CHECKED: ClassVar[dict[int, bool]] = {}
    LAST_KNOWN_EXPANDED: ClassVar[dict[int, bool]] = {}
    LAST_KNOWN_INDETERMINATE: ClassVar[dict[int, bool]] = {}
    LAST_KNOWN_INVALID_ENTRY: ClassVar[dict[int, bool]] = {}
    LAST_KNOWN_PRESSED: ClassVar[dict[int, bool]] = {}
    LAST_KNOWN_SELECTED: ClassVar[dict[int, bool]] = {}
    LAST_KNOWN_VALUE: ClassVar[dict[int, float]] = {}

    IGNORE_NAME_CHANGES_FOR: ClassVar[list[int]] = []

    TEXT_EVENT_REASON: ClassVar[dict[Atspi.Event, TextEventReason]] = {}

    _lock = threading.Lock()

    @staticmethod
    def _strings_are_redundant(str1: str | None, str2: str | None, threshold: float = 0.85) -> bool:
        """Returns True if str2 is redundant to str1 based on the similarity threshold."""

        if not (str1 and str2):
            return False

        similarity = round(SequenceMatcher(None, str1.lower(), str2.lower()).ratio(), 2)
        msg = (
            f"AXUtilitiesEvent: Similarity between '{str1}', '{str2}': {similarity} "
            f"(threshold: {threshold})"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return similarity >= threshold

    @staticmethod
    def _clear_stored_data() -> None:
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(60)
            AXUtilitiesEvent._clear_all_dictionaries()

    @staticmethod
    def _clear_all_dictionaries(reason: str = "") -> None:
        msg = "AXUtilitiesEvent: Clearing local cache."
        if reason:
            msg += f" Reason: {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION.clear()
        AXUtilitiesEvent.LAST_KNOWN_NAME.clear()
        AXUtilitiesEvent.LAST_KNOWN_CHECKED.clear()
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED.clear()
        AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE.clear()
        AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY.clear()
        AXUtilitiesEvent.LAST_KNOWN_PRESSED.clear()
        AXUtilitiesEvent.LAST_KNOWN_SELECTED.clear()
        AXUtilitiesEvent.LAST_KNOWN_VALUE.clear()
        AXUtilitiesEvent.TEXT_EVENT_REASON.clear()
        AXUtilitiesEvent.IGNORE_NAME_CHANGES_FOR.clear()

    @staticmethod
    def clear_cache_now(reason: str = "") -> None:
        """Clears all cached information immediately."""

        AXUtilitiesEvent._clear_all_dictionaries(reason)

    @staticmethod
    def save_object_info_for_events(obj: Atspi.Accessible) -> None:
        """Saves properties, states, etc. of obj for later use in event processing."""

        if obj is None:
            return

        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION[hash(obj)] = AXObject.get_description(obj)
        AXUtilitiesEvent.LAST_KNOWN_NAME[hash(obj)] = AXObject.get_name(obj)
        AXUtilitiesEvent.LAST_KNOWN_CHECKED[hash(obj)] = AXUtilitiesState.is_checked(obj)
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED[hash(obj)] = AXUtilitiesState.is_expanded(obj)
        AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE[hash(obj)] = AXUtilitiesState.is_indeterminate(
            obj,
        )
        AXUtilitiesEvent.LAST_KNOWN_PRESSED[hash(obj)] = AXUtilitiesState.is_pressed(obj)
        AXUtilitiesEvent.LAST_KNOWN_SELECTED[hash(obj)] = AXUtilitiesState.is_selected(obj)

        window = focus_manager.get_manager().get_active_window()
        AXUtilitiesEvent.LAST_KNOWN_NAME[hash(window)] = AXObject.get_name(window)
        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION[hash(window)] = AXObject.get_description(window)

    @staticmethod
    def start_cache_clearing_thread() -> None:
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=AXUtilitiesEvent._clear_stored_data)
        thread.daemon = True
        thread.start()

    @staticmethod
    def get_text_event_reason(event: Atspi.Event) -> TextEventReason:
        """Returns the TextEventReason for the given event."""

        reason = AXUtilitiesEvent.TEXT_EVENT_REASON.get(event)
        if reason is not None:
            tokens = ["AXUtilitiesEvent: Cached reason for", event, f": {reason}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return reason

        reason = TextEventReason.UNKNOWN
        if event.type.startswith("object:text-changed:insert"):
            reason = AXUtilitiesEvent._get_text_insertion_event_reason(event)
        elif event.type.startswith("object:text-caret-moved"):
            reason = AXUtilitiesEvent._get_caret_moved_event_reason(event)
        elif event.type.startswith("object:text-changed:delete"):
            reason = AXUtilitiesEvent._get_text_deletion_event_reason(event)
        elif event.type.startswith("object:text-selection-changed"):
            reason = AXUtilitiesEvent._get_text_selection_changed_event_reason(event)
        else:
            raise ValueError(f"Unexpected event type: {event.type}")

        AXUtilitiesEvent.TEXT_EVENT_REASON[event] = reason
        tokens = ["AXUtilitiesEvent: Reason for", event, f": {reason}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return reason

    @staticmethod
    def _get_selection_navigation_reason(mgr: InputEventManager) -> TextEventReason:
        """Returns the selection-granularity reason based on the last input event."""

        if mgr.last_event_was_line_navigation():
            reason = TextEventReason.SELECTION_BY_LINE
        elif mgr.last_event_was_word_navigation():
            reason = TextEventReason.SELECTION_BY_WORD
        elif mgr.last_event_was_character_navigation():
            reason = TextEventReason.SELECTION_BY_CHARACTER
        elif mgr.last_event_was_page_navigation():
            reason = TextEventReason.SELECTION_BY_PAGE
        elif mgr.last_event_was_line_boundary_navigation():
            reason = TextEventReason.SELECTION_TO_LINE_BOUNDARY
        elif mgr.last_event_was_file_boundary_navigation():
            reason = TextEventReason.SELECTION_TO_FILE_BOUNDARY
        else:
            reason = TextEventReason.UNSPECIFIED_SELECTION
        return reason

    @staticmethod
    def _get_caret_navigation_reason(mgr: InputEventManager) -> TextEventReason:
        """Returns the caret-navigation-granularity reason based on the last input event."""

        if mgr.last_event_was_line_navigation():
            reason = TextEventReason.NAVIGATION_BY_LINE
        elif mgr.last_event_was_word_navigation():
            reason = TextEventReason.NAVIGATION_BY_WORD
        elif mgr.last_event_was_character_navigation():
            reason = TextEventReason.NAVIGATION_BY_CHARACTER
        elif mgr.last_event_was_page_navigation():
            reason = TextEventReason.NAVIGATION_BY_PAGE
        elif mgr.last_event_was_line_boundary_navigation():
            reason = TextEventReason.NAVIGATION_TO_LINE_BOUNDARY
        elif mgr.last_event_was_file_boundary_navigation():
            reason = TextEventReason.NAVIGATION_TO_FILE_BOUNDARY
        else:
            reason = TextEventReason.UNSPECIFIED_NAVIGATION
        return reason

    @staticmethod
    def _get_editing_reason(mgr: InputEventManager) -> TextEventReason:
        """Returns the editing-operation reason based on the last input event."""

        if mgr.last_event_was_backspace():
            reason = TextEventReason.BACKSPACE
        elif mgr.last_event_was_delete():
            reason = TextEventReason.DELETE
        elif mgr.last_event_was_cut():
            reason = TextEventReason.CUT
        elif mgr.last_event_was_paste():
            reason = TextEventReason.PASTE
        elif mgr.last_event_was_undo():
            reason = TextEventReason.UNDO
        elif mgr.last_event_was_redo():
            reason = TextEventReason.REDO
        else:
            reason = TextEventReason.UNKNOWN
        return reason

    @staticmethod
    def _get_caret_moved_editable_reason(mgr: InputEventManager) -> TextEventReason:
        """Returns the reason for a caret-moved event in an editable or terminal."""

        reason = AXUtilitiesEvent._get_editing_reason(mgr)
        if reason != TextEventReason.UNKNOWN:
            return reason
        if mgr.last_event_was_page_switch():
            return TextEventReason.PAGE_SWITCH
        if mgr.last_event_was_command():
            return TextEventReason.UNSPECIFIED_COMMAND
        if mgr.last_event_was_printable_key():
            return TextEventReason.TYPING
        return TextEventReason.UNKNOWN

    @staticmethod
    def _get_caret_moved_event_reason(event: Atspi.Event) -> TextEventReason:
        """Returns the TextEventReason for the given event."""

        from . import input_event_manager  # pylint: disable=import-outside-toplevel

        mgr = input_event_manager.get_manager()

        obj = event.source
        mode, focus = focus_manager.get_manager().get_active_mode_and_object_of_interest()
        if mode == focus_manager.SAY_ALL:
            reason = TextEventReason.SAY_ALL
        elif focus != obj and AXUtilitiesRole.is_text_input_search(focus):
            if mgr.last_event_was_backspace() or mgr.last_event_was_delete():
                reason = TextEventReason.SEARCH_UNPRESENTABLE
            else:
                reason = TextEventReason.SEARCH_PRESENTABLE
        elif mgr.last_event_was_caret_selection():
            reason = AXUtilitiesEvent._get_selection_navigation_reason(mgr)
        elif mgr.last_event_was_caret_navigation():
            reason = AXUtilitiesEvent._get_caret_navigation_reason(mgr)
        elif mgr.last_event_was_select_all():
            reason = TextEventReason.SELECT_ALL
        elif mgr.last_event_was_primary_click_or_release():
            reason = TextEventReason.MOUSE_PRIMARY_BUTTON
        elif AXUtilitiesState.is_editable(obj) or AXUtilitiesRole.is_terminal(obj):
            reason = AXUtilitiesEvent._get_caret_moved_editable_reason(mgr)
        elif mgr.last_event_was_tab_navigation():
            reason = TextEventReason.FOCUS_CHANGE
        elif AXUtilitiesObject.find_ancestor(obj, AXUtilitiesRole.children_are_presentational):
            reason = TextEventReason.UI_UPDATE
        else:
            reason = TextEventReason.UNKNOWN
        return reason

    @staticmethod
    def _get_deletion_editable_reason(
        event: Atspi.Event,
        mgr: InputEventManager,
    ) -> TextEventReason:
        """Returns the reason for a text-deletion event in an editable or terminal."""

        reason = AXUtilitiesEvent._get_editing_reason(mgr)
        if reason != TextEventReason.UNKNOWN:
            return reason

        obj = event.source
        if mgr.last_event_was_command():
            reason = TextEventReason.UNSPECIFIED_COMMAND
        elif mgr.last_event_was_printable_key():
            reason = TextEventReason.TYPING
        elif mgr.last_event_was_up_or_down() or mgr.last_event_was_page_up_or_page_down():
            if AXUtilitiesRole.is_spin_button(obj) or AXUtilitiesObject.find_ancestor(
                obj,
                AXUtilitiesRole.is_spin_button,
            ):
                reason = TextEventReason.SPIN_BUTTON_VALUE_CHANGE
            else:
                reason = TextEventReason.AUTO_DELETION
        else:
            selected_text, _start, _end = AXUtilitiesText.get_cached_selected_text(obj)
            if selected_text and event.any_data.strip() == selected_text.strip():
                reason = TextEventReason.SELECTED_TEXT_DELETION
        return reason

    @staticmethod
    def _get_text_deletion_event_reason(event: Atspi.Event) -> TextEventReason:
        """Returns the TextEventReason for the given event."""

        from . import input_event_manager  # pylint: disable=import-outside-toplevel

        mgr = input_event_manager.get_manager()

        obj = event.source
        if AXObject.get_role(obj) in AXUtilitiesRole.get_text_ui_roles():
            reason = TextEventReason.UI_UPDATE
        elif AXUtilitiesRole.is_live_region(obj):
            reason = TextEventReason.LIVE_REGION_UPDATE
        elif mgr.last_event_was_page_switch():
            reason = TextEventReason.PAGE_SWITCH
        elif AXUtilitiesState.is_editable(obj) or AXUtilitiesRole.is_terminal(obj):
            reason = AXUtilitiesEvent._get_deletion_editable_reason(event, mgr)
        elif mgr.last_event_was_command():
            reason = TextEventReason.UNSPECIFIED_COMMAND
        elif "\ufffc" in event.any_data and not event.any_data.replace("\ufffc", ""):
            reason = TextEventReason.CHILDREN_CHANGE
        else:
            reason = TextEventReason.UNKNOWN
        return reason

    @staticmethod
    def _get_insertion_editable_reason(
        event: Atspi.Event,
        mgr: InputEventManager,
    ) -> TextEventReason:
        """Returns the reason for a text-insertion event in an editable or terminal."""

        obj = event.source
        selected_text, _start, _end = AXUtilitiesText.get_selected_text(obj)
        has_selected = bool(selected_text and event.any_data == selected_text)

        reason = AXUtilitiesEvent._get_insertion_editing_reason(mgr, has_selected)
        if reason != TextEventReason.UNKNOWN:
            return reason
        reason = AXUtilitiesEvent._get_insertion_typing_reason(event, mgr, obj, has_selected)
        if reason != TextEventReason.UNKNOWN:
            return reason
        if has_selected:
            return TextEventReason.SELECTED_TEXT_INSERTION
        return TextEventReason.UNKNOWN

    @staticmethod
    def _get_insertion_editing_reason(
        mgr: InputEventManager,
        has_selected: bool,
    ) -> TextEventReason:
        """Returns the editing-operation reason for a text insertion, if applicable."""

        if mgr.last_event_was_backspace():
            reason = TextEventReason.BACKSPACE
        elif mgr.last_event_was_delete():
            reason = TextEventReason.DELETE
        elif mgr.last_event_was_cut():
            reason = TextEventReason.CUT
        elif mgr.last_event_was_paste():
            reason = TextEventReason.PASTE
        elif mgr.last_event_was_undo():
            if has_selected:
                reason = TextEventReason.SELECTED_TEXT_RESTORATION
            else:
                reason = TextEventReason.UNDO
        elif mgr.last_event_was_redo():
            if has_selected:
                reason = TextEventReason.SELECTED_TEXT_RESTORATION
            else:
                reason = TextEventReason.REDO
        elif mgr.last_event_was_command():
            reason = TextEventReason.UNSPECIFIED_COMMAND
        else:
            reason = TextEventReason.UNKNOWN
        return reason

    @staticmethod
    def _get_insertion_text_key_reason(
        event: Atspi.Event,
        mgr: InputEventManager,
        obj: Atspi.Accessible,
        has_selected: bool,
    ) -> TextEventReason:
        """Returns the reason when the last event was a text-producing key."""

        if mgr.last_event_was_space() and not AXUtilitiesRole.is_password_text(obj):
            if event.any_data == "\n":
                reason = TextEventReason.AUTO_INSERTION_UNPRESENTABLE
            else:
                reason = TextEventReason.TYPING
        elif mgr.last_event_was_tab() or mgr.last_event_was_return():
            if not event.any_data.strip():
                reason = TextEventReason.TYPING
            else:
                reason = AXUtilitiesEvent._get_insertion_fallback_reason(event, mgr)
        elif mgr.last_event_was_printable_key() or mgr.last_event_was_space():
            if has_selected:
                reason = TextEventReason.AUTO_INSERTION_PRESENTABLE
            else:
                reason = AXUtilitiesEvent._get_typing_echo_reason(obj)
        else:
            reason = TextEventReason.UNKNOWN
        return reason

    @staticmethod
    def _get_insertion_typing_reason(
        event: Atspi.Event,
        mgr: InputEventManager,
        obj: Atspi.Accessible,
        has_selected: bool,
    ) -> TextEventReason:
        """Returns the typing/auto-insertion reason for a text insertion."""

        reason = AXUtilitiesEvent._get_insertion_text_key_reason(event, mgr, obj, has_selected)
        if reason != TextEventReason.UNKNOWN:
            return reason

        if mgr.last_event_was_middle_click() or mgr.last_event_was_middle_release():
            reason = TextEventReason.MOUSE_MIDDLE_BUTTON
        elif mgr.last_event_was_up_or_down() or mgr.last_event_was_page_up_or_page_down():
            if AXUtilitiesRole.is_spin_button(obj) or AXUtilitiesObject.find_ancestor(
                obj,
                AXUtilitiesRole.is_spin_button,
            ):
                reason = TextEventReason.SPIN_BUTTON_VALUE_CHANGE
            else:
                reason = TextEventReason.AUTO_INSERTION_PRESENTABLE
        else:
            reason = AXUtilitiesEvent._get_insertion_fallback_reason(event, mgr)
        return reason

    @staticmethod
    def _get_typing_echo_reason(obj: Atspi.Accessible) -> TextEventReason:
        """Returns TYPING_ECHOABLE if echo is enabled, otherwise TYPING."""

        from . import typing_echo_presenter  # pylint: disable=import-outside-toplevel

        presenter = typing_echo_presenter.get_presenter()
        if AXUtilitiesRole.is_password_text(obj):
            echo = presenter.get_key_echo_enabled()
        else:
            echo = presenter.get_character_echo_enabled()
        if echo:
            return TextEventReason.TYPING_ECHOABLE
        return TextEventReason.TYPING

    @staticmethod
    def _get_insertion_fallback_reason(
        event: Atspi.Event,
        mgr: InputEventManager,
    ) -> TextEventReason:
        """Returns the reason for unclassified text insertions."""

        if len(event.any_data) == 1:
            return TextEventReason.UNKNOWN
        if mgr.last_event_was_tab() and event.any_data != "\t":
            return TextEventReason.AUTO_INSERTION_PRESENTABLE
        if mgr.last_event_was_return() and event.any_data != "\n":
            if AXUtilitiesState.is_single_line(event.source):
                return TextEventReason.AUTO_INSERTION_UNPRESENTABLE
            return TextEventReason.AUTO_INSERTION_PRESENTABLE
        return TextEventReason.UNKNOWN

    @staticmethod
    def _get_text_insertion_event_reason(event: Atspi.Event) -> TextEventReason:
        """Returns the TextEventReason for the given event."""

        from . import input_event_manager  # pylint: disable=import-outside-toplevel

        mgr = input_event_manager.get_manager()

        obj = event.source
        if AXObject.get_role(obj) in AXUtilitiesRole.get_text_ui_roles():
            reason = TextEventReason.UI_UPDATE
        elif AXUtilitiesRole.is_live_region(obj):
            reason = TextEventReason.LIVE_REGION_UPDATE
        elif mgr.last_event_was_page_switch():
            reason = TextEventReason.PAGE_SWITCH
        elif AXUtilitiesState.is_editable(obj) or AXUtilitiesRole.is_terminal(obj):
            reason = AXUtilitiesEvent._get_insertion_editable_reason(event, mgr)
        elif mgr.last_event_was_command():
            reason = TextEventReason.UNSPECIFIED_COMMAND
        elif "\ufffc" in event.any_data and not event.any_data.replace("\ufffc", ""):
            reason = TextEventReason.CHILDREN_CHANGE
        else:
            reason = TextEventReason.UNKNOWN
        return reason

    @staticmethod
    def _get_selection_changed_editable_reason(
        obj: Atspi.Accessible,
        mgr: InputEventManager,
    ) -> TextEventReason:
        """Returns the reason for a text-selection-changed event in an editable or terminal."""

        reason = AXUtilitiesEvent._get_editing_reason(mgr)
        if reason != TextEventReason.UNKNOWN:
            return reason
        if mgr.last_event_was_page_switch():
            return TextEventReason.PAGE_SWITCH
        if mgr.last_event_was_command():
            return TextEventReason.UNSPECIFIED_COMMAND
        if mgr.last_event_was_printable_key():
            return TextEventReason.TYPING
        if mgr.last_event_was_up_or_down() or mgr.last_event_was_page_up_or_page_down():
            if AXUtilitiesRole.is_spin_button(obj) or AXUtilitiesObject.find_ancestor(
                obj,
                AXUtilitiesRole.is_spin_button,
            ):
                return TextEventReason.SPIN_BUTTON_VALUE_CHANGE
        return TextEventReason.UNKNOWN

    @staticmethod
    def _get_text_selection_changed_event_reason(event: Atspi.Event) -> TextEventReason:
        """Returns the TextEventReason for the given event."""

        from . import input_event_manager  # pylint: disable=import-outside-toplevel

        mgr = input_event_manager.get_manager()

        obj = event.source
        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus != obj and AXUtilitiesRole.is_text_input_search(focus):
            if mgr.last_event_was_backspace() or mgr.last_event_was_delete():
                reason = TextEventReason.SEARCH_UNPRESENTABLE
            else:
                reason = TextEventReason.SEARCH_PRESENTABLE
        elif mgr.last_event_was_caret_selection():
            reason = AXUtilitiesEvent._get_selection_navigation_reason(mgr)
        elif mgr.last_event_was_caret_navigation():
            reason = AXUtilitiesEvent._get_caret_navigation_reason(mgr)
        elif mgr.last_event_was_select_all():
            reason = TextEventReason.SELECT_ALL
        elif mgr.last_event_was_primary_click_or_release():
            reason = TextEventReason.MOUSE_PRIMARY_BUTTON
        elif AXUtilitiesState.is_editable(obj) or AXUtilitiesRole.is_terminal(obj):
            reason = AXUtilitiesEvent._get_selection_changed_editable_reason(obj, mgr)
        else:
            reason = TextEventReason.UNKNOWN
        return reason

    @staticmethod
    def is_presentable_active_descendant_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as an active-descendant change."""

        if not event.any_data:
            msg = "AXUtilitiesEvent: No any_data."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not (
            AXUtilitiesState.is_focused(event.source) or AXUtilitiesState.is_focused(event.any_data)
        ):
            msg = "AXUtilitiesEvent: Neither source nor child have focused state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilitiesRole.is_table_cell(focus):
            table = AXUtilitiesObject.find_ancestor(focus, AXUtilitiesRole.is_tree_or_tree_table)
            if table is not None and table != event.source:
                msg = "AXUtilitiesEvent: Event is from a different tree or tree table."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_checked_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as a checked-state change."""

        old_state = AXUtilitiesEvent.LAST_KNOWN_CHECKED.get(hash(event.source))
        new_state = AXUtilitiesState.is_checked(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent.LAST_KNOWN_CHECKED[hash(event.source)] = new_state
        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.source != focus:
            if not AXUtilitiesObject.is_ancestor(event.source, focus):
                msg = "AXUtilitiesEvent: The source is not the locus of focus or its descendant."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False
            if not (AXUtilitiesRole.is_list_item(focus) or AXUtilitiesRole.is_tree_item(focus)):
                msg = "AXUtilitiesEvent: The source descends from non-interactive-item focus."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

        from . import input_event_manager  # pylint: disable=import-outside-toplevel

        mgr = input_event_manager.get_manager()

        # Radio buttons normally change their state when you arrow to them, so we handle the
        # announcement of their state changes in the focus handling code.
        if AXUtilitiesRole.is_radio_button(event.source) and not mgr.last_event_was_space():
            msg = "AXUtilitiesEvent: Only presentable for this role if toggled by user."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def _is_changed_description_to_present(event: Atspi.Event) -> bool:
        """Returns True if the description data warrants further presentability checks."""

        if not isinstance(event.any_data, str):
            msg = "AXUtilitiesEvent: The any_data is not a string."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        old_description = AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION.get(hash(event.source))
        new_description = event.any_data
        if old_description == new_description:
            msg = "AXUtilitiesEvent: The new description matches the old description."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilitiesEvent._strings_are_redundant(old_description, new_description):
            msg = (
                f"AXUtilitiesEvent: The new description ('{new_description}') "
                f"is too similar to the old description ('{old_description}')."
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION[hash(event.source)] = new_description
        if not new_description:
            msg = "AXUtilitiesEvent: The description is empty."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return True

    @staticmethod
    def is_presentable_description_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as a description change."""

        if not AXUtilitiesEvent._is_changed_description_to_present(event):
            return False

        if not AXUtilitiesState.is_showing(event.source):
            msg = "AXUtilitiesEvent: The event source is not showing."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.source != focus and not AXUtilitiesObject.is_ancestor(focus, event.source):
            msg = "AXUtilitiesEvent: The event is not from the locus of focus or ancestor."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_expanded_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as an expanded-state change."""

        old_state = AXUtilitiesEvent.LAST_KNOWN_EXPANDED.get(hash(event.source))
        new_state = AXUtilitiesState.is_expanded(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent.LAST_KNOWN_EXPANDED[hash(event.source)] = new_state
        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.source == focus:
            msg = "AXUtilitiesEvent: Event is presentable, from the locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not event.detail1 and not AXUtilitiesObject.is_ancestor(focus, event.source):
            msg = "AXUtilitiesEvent: Event is not from the locus of focus or ancestor."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilitiesRole.is_table_row(event.source) or AXUtilitiesRole.is_list_box(event.source):
            msg = "AXUtilitiesEvent: Event is presentable based on role."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilitiesRole.is_combo_box(event.source) or AXUtilitiesRole.is_button(event.source):
            if not AXUtilitiesState.is_focused(event.source):
                msg = "AXUtilitiesEvent: Only presentable for this role if focused."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_indeterminate_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as an indeterminate-state change."""

        old_state = AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE.get(hash(event.source))
        new_state = AXUtilitiesState.is_indeterminate(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE[hash(event.source)] = new_state

        # If this state is cleared, the new state will become checked or unchecked
        # and we should get object:state-changed:checked events for those cases.
        if not new_state:
            msg = "AXUtilitiesEvent: The new state should be presented as a checked-change."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if event.source != focus_manager.get_manager().get_locus_of_focus():
            msg = "AXUtilitiesEvent: The event is not from the locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_invalid_entry_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as an invalid-entry-state change."""

        old_state = AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY.get(hash(event.source))
        new_state = AXUtilitiesState.is_invalid_entry(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY[hash(event.source)] = new_state
        if event.source != focus_manager.get_manager().get_locus_of_focus():
            msg = "AXUtilitiesEvent: The event is not from the locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def _is_presentable_frame_name_change(event: Atspi.Event) -> bool:
        """Returns True if a frame's name-change event should be presented."""

        if event.source != focus_manager.get_manager().get_active_window():
            msg = "AXUtilitiesEvent: Event is for frame other than the active window."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        # Example: Typing the subject in an email client causing the window name to change.
        focus = focus_manager.get_manager().get_locus_of_focus()
        if (
            AXUtilitiesState.is_editable(focus)
            and AXText.get_character_count(focus)
            and AXText.get_all_text(focus) in event.any_data
        ):
            msg = "AXUtilitiesEvent: Event is redundant notification for the locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def _is_changed_name_to_present(event: Atspi.Event) -> bool:
        """Returns True if the name data warrants further presentability checks."""

        if hash(event.source) in AXUtilitiesEvent.IGNORE_NAME_CHANGES_FOR:
            msg = "AXUtilitiesEvent: Ignoring name change for this source."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not isinstance(event.any_data, str):
            msg = "AXUtilitiesEvent: The any_data is not a string."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        old_name = AXUtilitiesEvent.LAST_KNOWN_NAME.get(hash(event.source))
        new_name = event.any_data
        if old_name == new_name:
            msg = "AXUtilitiesEvent: The new name matches the old name."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilitiesEvent._strings_are_redundant(old_name, new_name):
            msg = (
                f"AXUtilitiesEvent: The new name ('{new_name}') "
                f"is too similar to the old name ('{old_name}')."
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent.LAST_KNOWN_NAME[hash(event.source)] = new_name
        if not new_name:
            msg = "AXUtilitiesEvent: The name is empty."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return True

    @staticmethod
    def is_presentable_name_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as a name change."""

        if not AXUtilitiesEvent._is_changed_name_to_present(event):
            return False

        if not AXUtilitiesState.is_showing(event.source):
            msg = "AXUtilitiesEvent: The event source is not showing."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            if event.source != focus_manager.get_manager().get_locus_of_focus():
                return False

        if AXUtilitiesRole.is_frame(event.source):
            return AXUtilitiesEvent._is_presentable_frame_name_change(event)

        if event.source != focus_manager.get_manager().get_locus_of_focus():
            msg = "AXUtilitiesEvent: The event is not from the locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilitiesRole.is_list_item(event.source):
            # Inspired by Firefox's downloads list in which the list item's name changes to show
            # download progress. It's super chatty and stomps on the progress bar announcements.
            if AXObject.supports_collection(event.source):
                has_progress_bar = (
                    AXUtilitiesCollection.find_first_with_role(
                        event.source, [Atspi.Role.PROGRESS_BAR]
                    )
                    is not None
                )
            else:
                has_progress_bar = (
                    AXUtilitiesObject.find_descendant(event.source, AXUtilitiesRole.is_progress_bar)
                    is not None
                )
            if has_progress_bar:
                msg = "AXUtilitiesEvent: The list item contains a progress bar."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                AXUtilitiesEvent.IGNORE_NAME_CHANGES_FOR.append(hash(event.source))
                return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_pressed_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as a pressed-state change."""

        old_state = AXUtilitiesEvent.LAST_KNOWN_PRESSED.get(hash(event.source))
        new_state = AXUtilitiesState.is_pressed(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent.LAST_KNOWN_PRESSED[hash(event.source)] = new_state
        if event.source != focus_manager.get_manager().get_locus_of_focus():
            msg = "AXUtilitiesEvent: The event is not from the locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_selected_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as a selected-state change."""

        old_state = AXUtilitiesEvent.LAST_KNOWN_SELECTED.get(hash(event.source))
        new_state = AXUtilitiesState.is_selected(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent.LAST_KNOWN_SELECTED[hash(event.source)] = new_state
        if event.source != focus_manager.get_manager().get_locus_of_focus():
            msg = "AXUtilitiesEvent: The event is not from the locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_selection_change(event: Atspi.Event) -> bool:
        """Returns True if this object:selection-changed event should be presented."""

        from . import input_event_manager  # pylint: disable=import-outside-toplevel

        if input_event_manager.get_manager().last_event_was_space():
            msg = "AXUtilitiesEvent: Selection toggled via space; handled elsewhere."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilitiesState.manages_descendants(event.source):
            msg = "AXUtilitiesEvent: Source manages descendants; handled elsewhere."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilitiesRole.is_combo_box(event.source) and not AXUtilitiesState.is_expanded(
            event.source
        ):
            text_input = AXUtilitiesObject.find_descendant(
                event.source, AXUtilitiesRole.is_text_input
            )
            if text_input is not None and AXUtilitiesState.is_focused(text_input):
                msg = "AXUtilitiesEvent: Combo box text input is focused; not a user selection."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.source != focus and not (
            AXUtilitiesState.is_showing(event.source) and AXUtilitiesState.is_visible(event.source)
        ):
            combobox = AXUtilitiesObject.find_ancestor(event.source, AXUtilitiesRole.is_combo_box)
            if combobox != focus and event.source != AXObject.get_parent(focus):
                tokens = ["AXUtilitiesEvent: Source lacks showing + visible:", event.source]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return False

        active_window = focus_manager.get_manager().get_active_window()
        if not AXUtilitiesObject.is_ancestor(event.source, active_window):
            tokens = ["AXUtilitiesEvent:", event.source, "is not inside", active_window]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_value_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as a value change."""

        old_value = AXUtilitiesEvent.LAST_KNOWN_VALUE.get(hash(event.source))
        new_value = AXValue.get_current_value(event.source)
        AXUtilitiesEvent.LAST_KNOWN_VALUE[hash(event.source)] = new_value
        if old_value == new_value:
            msg = "AXUtilitiesEvent: The new value matches the old value."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilitiesRole.is_progress_bar(event.source):
            if AXUtilitiesComponent.has_no_size(event.source):
                tokens = ["AXUtilitiesEvent:", event.source, "has no size."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return False
            if AXUtilitiesObject.find_ancestor(event.source, AXUtilitiesRole.is_status_bar):
                tokens = ["AXUtilitiesEvent:", event.source, "is in a status bar."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def _is_presentable_text_event(event: Atspi.Event) -> bool:
        """Returns True if this text event should be presented."""

        if not (
            AXUtilitiesState.is_editable(event.source) or AXUtilitiesRole.is_terminal(event.source)
        ):
            msg = "AXUtilitiesEvent: The source is neither editable nor a terminal."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus != event.source and not AXUtilitiesState.is_focused(event.source):
            msg = "AXUtilitiesEvent: The source is neither focused, nor the locus of focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)

            # This can happen in web content where the focus is a contenteditable element and a
            # new child element is created for new or changed text.
            if AXUtilitiesObject.is_ancestor(event.source, focus):
                msg = "AXUtilitiesEvent: The locus of focus is an ancestor of the source."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_text_attributes_change(event: Atspi.Event) -> bool:
        """Returns True if this text-attributes-change event should be presented."""

        return AXUtilitiesEvent._is_presentable_text_event(event)

    @staticmethod
    def is_presentable_text_deletion(event: Atspi.Event) -> bool:
        """Returns True if this text-deletion event should be presented."""

        return AXUtilitiesEvent._is_presentable_text_event(event)

    @staticmethod
    def is_presentable_text_insertion(event: Atspi.Event) -> bool:
        """Returns True if this text-insertion event should be presented."""

        return AXUtilitiesEvent._is_presentable_text_event(event)


AXUtilitiesEvent.start_cache_clearing_thread()
