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
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

"""Utilities for accessible events."""

from __future__ import annotations

import enum
import re
import time
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import ax_cache_manager, debug, focus_manager
from .ax_object import AXObject
from .ax_selection import AXSelection
from .ax_text import AXText
from .ax_utilities_collection import AXUtilitiesCollection
from .ax_utilities_component import AXUtilitiesComponent
from .ax_utilities_object import AXUtilitiesObject
from .ax_utilities_relation import AXUtilitiesRelation
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState
from .ax_utilities_text import AXUtilitiesText, CaretSetReason
from .ax_value import AXValue

if TYPE_CHECKING:
    from .input_event_manager import InputEventManager


class TextEventReason(enum.Enum):
    """Enum representing the reason for an object:text- event."""

    UNKNOWN = enum.auto()
    AUTO_DELETION_PRESENTABLE = enum.auto()
    AUTO_DELETION_UNPRESENTABLE = enum.auto()
    AUTO_INSERTION_PRESENTABLE = enum.auto()
    AUTO_INSERTION_UNPRESENTABLE = enum.auto()
    AUTO_SELECTION = enum.auto()
    AUTO_UNSELECTION = enum.auto()
    BACKSPACE = enum.auto()
    BRAILLE_PANNING = enum.auto()
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
    SYSTEM_UPDATE = enum.auto()
    TYPING = enum.auto()
    TYPING_ECHOABLE = enum.auto()
    UI_UPDATE = enum.auto()
    UNDO = enum.auto()
    UNSPECIFIED_COMMAND = enum.auto()
    UNSPECIFIED_NAVIGATION = enum.auto()
    UNSPECIFIED_SELECTION = enum.auto()


class _AXUtilitiesEventCache:
    """Provides event-specific access to manager-backed cached values."""

    LAST_KNOWN_DESCRIPTION = "AXUtilitiesEvent.last-known-description"
    LAST_KNOWN_NAME = "AXUtilitiesEvent.last-known-name"
    LAST_KNOWN_CHECKED = "AXUtilitiesEvent.last-known-checked"
    LAST_KNOWN_EXPANDED = "AXUtilitiesEvent.last-known-expanded"
    LAST_KNOWN_INDETERMINATE = "AXUtilitiesEvent.last-known-indeterminate"
    LAST_KNOWN_INVALID_ENTRY = "AXUtilitiesEvent.last-known-invalid-entry"
    LAST_KNOWN_PRESSED = "AXUtilitiesEvent.last-known-pressed"
    LAST_KNOWN_SELECTED = "AXUtilitiesEvent.last-known-selected"
    LAST_KNOWN_VALUE = "AXUtilitiesEvent.last-known-value"
    LAST_KNOWN_VALUE_TEXT = "AXUtilitiesEvent.last-known-value-text"
    IGNORE_NAME_CHANGES_FOR = "AXUtilitiesEvent.ignore-name-changes-for"
    TEXT_EVENT_REASON = "AXUtilitiesEvent.text-event-reason"

    _NAMESPACES = (
        LAST_KNOWN_DESCRIPTION,
        LAST_KNOWN_NAME,
        LAST_KNOWN_CHECKED,
        LAST_KNOWN_EXPANDED,
        LAST_KNOWN_INDETERMINATE,
        LAST_KNOWN_INVALID_ENTRY,
        LAST_KNOWN_PRESSED,
        LAST_KNOWN_SELECTED,
        LAST_KNOWN_VALUE,
        LAST_KNOWN_VALUE_TEXT,
        IGNORE_NAME_CHANGES_FOR,
        TEXT_EVENT_REASON,
    )

    def __init__(self) -> None:
        self._manager = ax_cache_manager.get_manager()
        for namespace in self._NAMESPACES:
            self._manager.register_cache(
                self,
                namespace,
                lifetime=ax_cache_manager.Lifetime.PROCESS,
            )
        self._caches = {
            namespace: self._manager.get_cache(self, namespace) for namespace in self._NAMESPACES
        }

    def get_description(self, obj: Atspi.Accessible) -> str | None:
        """Returns the cached description for obj."""

        cache = self._caches.get(self.LAST_KNOWN_DESCRIPTION)
        if cache is None:
            return None

        return cache.get(ax_cache_manager.get_object_key(obj), None)

    def set_description(self, obj: Atspi.Accessible, description: str) -> None:
        """Stores the description for obj."""

        cache = self._caches.get(self.LAST_KNOWN_DESCRIPTION)
        if cache is not None:
            cache.put(ax_cache_manager.get_object_key(obj), description)

    def get_name(self, obj: Atspi.Accessible) -> str | None:
        """Returns the cached name for obj."""

        cache = self._caches.get(self.LAST_KNOWN_NAME)
        if cache is None:
            return None

        return cache.get(ax_cache_manager.get_object_key(obj), None)

    def set_name(self, obj: Atspi.Accessible, name: str) -> None:
        """Stores the name for obj."""

        cache = self._caches.get(self.LAST_KNOWN_NAME)
        if cache is not None:
            cache.put(ax_cache_manager.get_object_key(obj), name)

    def get_state(self, namespace: str, obj: Atspi.Accessible) -> bool | None:
        """Returns the cached state for obj."""

        cache = self._caches.get(namespace)
        if cache is None:
            return None

        return cache.get(ax_cache_manager.get_object_key(obj), None)

    def set_state(self, namespace: str, obj: Atspi.Accessible, state: bool) -> None:
        """Stores the state for obj."""

        cache = self._caches.get(namespace)
        if cache is not None:
            cache.put(ax_cache_manager.get_object_key(obj), state)

    def get_value(self, obj: Atspi.Accessible) -> float | None:
        """Returns the cached value for obj."""

        cache = self._caches.get(self.LAST_KNOWN_VALUE)
        if cache is None:
            return None

        return cache.get(ax_cache_manager.get_object_key(obj), None)

    def set_value(self, obj: Atspi.Accessible, value: float) -> None:
        """Stores the value for obj."""

        cache = self._caches.get(self.LAST_KNOWN_VALUE)
        if cache is not None:
            cache.put(ax_cache_manager.get_object_key(obj), value)

    def get_value_text(self, obj: Atspi.Accessible) -> str | None:
        """Returns the cached value text for obj."""

        cache = self._caches.get(self.LAST_KNOWN_VALUE_TEXT)
        if cache is None:
            return None

        return cache.get(ax_cache_manager.get_object_key(obj), None)

    def set_value_text(self, obj: Atspi.Accessible, value_text: str) -> None:
        """Stores the value text for obj."""

        cache = self._caches.get(self.LAST_KNOWN_VALUE_TEXT)
        if cache is not None:
            cache.put(ax_cache_manager.get_object_key(obj), value_text)

    def get_text_event_reason(self, event: Atspi.Event) -> TextEventReason | None:
        """Returns the cached reason for event."""

        cache = self._caches.get(self.TEXT_EVENT_REASON)
        if cache is None:
            return None

        return cache.get(event, None)

    def set_text_event_reason(self, event: Atspi.Event, reason: TextEventReason) -> None:
        """Stores the reason for event."""

        cache = self._caches.get(self.TEXT_EVENT_REASON)
        if cache is not None:
            cache.put(event, reason)

    def is_ignoring_name_changes_for(self, obj: Atspi.Accessible) -> bool:
        """Returns True if name changes should be ignored for obj."""

        cache = self._caches.get(self.IGNORE_NAME_CHANGES_FOR)
        if cache is None:
            return False

        return cache.get(ax_cache_manager.get_object_key(obj), False)

    def ignore_name_changes_for(self, obj: Atspi.Accessible) -> None:
        """Stores that name changes should be ignored for obj."""

        cache = self._caches.get(self.IGNORE_NAME_CHANGES_FOR)
        if cache is not None:
            cache.put(ax_cache_manager.get_object_key(obj), True)


class AXUtilitiesEvent:
    """Utilities for accessible events."""

    # How recent a caret set must be for its resulting event to be attributed to it.
    CARET_SET_EVENT_WINDOW_SECONDS = 1.0

    _CACHE = _AXUtilitiesEventCache()

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
    def save_object_info_for_events(obj: Atspi.Accessible) -> None:
        """Saves properties, states, etc. of obj for later use in event processing."""

        if obj is None:
            return

        state_set = AXObject.get_state_set(obj)
        AXUtilitiesEvent._CACHE.set_description(obj, AXObject.get_description(obj))
        AXUtilitiesEvent._CACHE.set_name(obj, AXObject.get_name(obj))
        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_CHECKED,
            obj,
            AXUtilitiesState.is_checked(obj, state_set),
        )
        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_EXPANDED,
            obj,
            AXUtilitiesState.is_expanded(obj, state_set),
        )
        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_INDETERMINATE,
            obj,
            AXUtilitiesState.is_indeterminate(obj, state_set),
        )
        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_PRESSED,
            obj,
            AXUtilitiesState.is_pressed(obj, state_set),
        )
        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_SELECTED,
            obj,
            AXUtilitiesState.is_selected(obj, state_set),
        )

        window = focus_manager.get_manager().get_active_window()
        AXUtilitiesEvent._CACHE.set_name(window, AXObject.get_name(window))
        AXUtilitiesEvent._CACHE.set_description(window, AXObject.get_description(window))

    @staticmethod
    def get_text_event_reason(event: Atspi.Event) -> TextEventReason:
        """Returns the TextEventReason for the given event."""

        reason = AXUtilitiesEvent._CACHE.get_text_event_reason(event)
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

        AXUtilitiesEvent._CACHE.set_text_event_reason(event, reason)
        tokens = ["AXUtilitiesEvent: Reason for", event, f": {reason}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return reason

    @staticmethod
    def _is_terminal_being_flat_reviewed(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a terminal currently being flat-reviewed."""

        if not AXUtilitiesRole.is_terminal(obj):
            return False
        mode, acc = focus_manager.get_manager().get_active_mode_and_object_of_interest()
        return mode == focus_manager.FLAT_REVIEW and obj == acc

    @staticmethod
    def _is_terminal_escape_sequence(string: str) -> bool:
        """Returns True if string is an escape sequence the terminal displayed as literal text."""

        return bool(re.fullmatch(r"\s*ESC\[[\d;]*[A-Za-z~]?\s*", string))

    @staticmethod
    def _is_spin_button_descendant(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a spin button or descends from one."""

        if AXUtilitiesRole.is_spin_button(obj):
            return True
        return AXUtilitiesObject.find_ancestor(obj, AXUtilitiesRole.is_spin_button) is not None

    @staticmethod
    def _did_line_change(obj: Atspi.Accessible) -> bool:
        """Returns True if the last known line in obj differs from the current line."""

        last_obj, last_offset = focus_manager.get_manager().get_last_cursor_position()
        if obj != last_obj:
            return False

        return not AXUtilitiesText.offset_is_on_current_line(obj, last_offset)

    @staticmethod
    def _get_obj_type_reason_or_none(
        event: Atspi.Event,
        mgr: InputEventManager,
    ) -> TextEventReason | None:
        """Returns the reason if obj-type or event-type dictates one, else None to continue."""

        obj = event.source
        if AXUtilitiesRole.is_live_region(obj):
            return TextEventReason.LIVE_REGION_UPDATE
        if AXObject.get_role(obj) in AXUtilitiesRole.get_text_ui_roles():
            return TextEventReason.UI_UPDATE
        if event.type.endswith("system"):
            return TextEventReason.SYSTEM_UPDATE
        if mgr.last_event_was_page_switch():
            return TextEventReason.PAGE_SWITCH
        return None

    @staticmethod
    def _get_non_editable_reason(
        event: Atspi.Event,
        mgr: InputEventManager,
    ) -> TextEventReason:
        """Returns the reason for an insert/delete in a non-editable, non-terminal object."""

        if mgr.last_event_was_command():
            return TextEventReason.UNSPECIFIED_COMMAND
        if "\ufffc" in event.any_data and not event.any_data.replace("\ufffc", ""):
            return TextEventReason.CHILDREN_CHANGE
        return TextEventReason.UNKNOWN

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
    def _get_caret_moved_event_reason(event: Atspi.Event) -> TextEventReason:
        """Returns the TextEventReason for the given event."""

        from . import input_event_manager  # pylint: disable=import-outside-toplevel

        mgr = input_event_manager.get_manager()
        obj = event.source
        last_caret_set = AXUtilitiesText.get_last_caret_set()
        # Some toolkits report the resulting event's offset as -1 rather than what we set.
        if (
            last_caret_set is not None
            and last_caret_set.reason == CaretSetReason.BRAILLE_PANNING
            and obj == last_caret_set.obj
            and event.detail1 in (last_caret_set.offset, -1)
            and time.time() - last_caret_set.time < AXUtilitiesEvent.CARET_SET_EVENT_WINDOW_SECONDS
        ):
            return TextEventReason.BRAILLE_PANNING

        mode, focus = focus_manager.get_manager().get_active_mode_and_object_of_interest()
        if mode == focus_manager.SAY_ALL:
            return TextEventReason.SAY_ALL
        if focus != obj and AXUtilitiesRole.is_text_input_search(focus):
            if mgr.last_event_was_backspace() or mgr.last_event_was_delete():
                return TextEventReason.SEARCH_UNPRESENTABLE
            return TextEventReason.SEARCH_PRESENTABLE
        is_terminal = AXUtilitiesRole.is_terminal(obj)
        if is_terminal:
            line, _start, _end = AXText.get_line_at_offset(obj)
            if AXUtilitiesEvent._is_terminal_escape_sequence(line):
                return TextEventReason.AUTO_INSERTION_UNPRESENTABLE
        if (
            mgr.last_event_was_up_or_down() or mgr.last_event_was_page_up_or_page_down()
        ) and AXUtilitiesEvent._is_spin_button_descendant(obj):
            return TextEventReason.SPIN_BUTTON_VALUE_CHANGE
        if mgr.last_event_was_caret_selection():
            return AXUtilitiesEvent._get_selection_navigation_reason(mgr)
        if mgr.last_event_was_caret_navigation():
            result = AXUtilitiesEvent._get_caret_navigation_reason(mgr)
            # For performance purposes, the input event manager does very little sanity checking
            # when determining whether an input event was line navigation. A terminal presents new
            # content via the insertion event, so a caret move that is a side effect of its redraw
            # should not be treated as navigation: paging (Less and Vim park the cursor on the
            # status line, whose transient content would otherwise be read), or auto-inserted text
            # at the prompt that looks like line navigation (e.g. pressing Up at the prompt).
            if is_terminal and (
                result == TextEventReason.NAVIGATION_BY_PAGE
                or (
                    result == TextEventReason.NAVIGATION_BY_LINE
                    and not AXUtilitiesEvent._did_line_change(obj)
                )
            ):
                result = TextEventReason.AUTO_INSERTION_UNPRESENTABLE
            return result
        if mgr.last_event_was_select_all():
            return TextEventReason.SELECT_ALL
        if mgr.last_event_was_primary_click_or_release():
            return TextEventReason.MOUSE_PRIMARY_BUTTON
        if AXUtilitiesState.is_editable(obj) or is_terminal:
            reason = AXUtilitiesEvent._get_editing_reason(mgr)
            if reason != TextEventReason.UNKNOWN:
                return reason
            if mgr.last_event_was_page_switch():
                return TextEventReason.PAGE_SWITCH
            if mgr.last_event_was_command() or mgr.last_event_was_escape():
                if focus != obj and AXUtilitiesState.is_focused(obj):
                    return TextEventReason.FOCUS_CHANGE
                return TextEventReason.UNSPECIFIED_COMMAND
            if mgr.last_event_was_printable_key():
                return TextEventReason.TYPING
            if AXUtilitiesEvent._is_terminal_being_flat_reviewed(obj):
                return TextEventReason.AUTO_INSERTION_UNPRESENTABLE
            return TextEventReason.UNKNOWN
        if mgr.last_event_was_tab_navigation():
            return TextEventReason.FOCUS_CHANGE
        if AXUtilitiesObject.find_ancestor(obj, AXUtilitiesRole.children_are_presentational):
            return TextEventReason.UI_UPDATE
        return TextEventReason.UNKNOWN

    @staticmethod
    def _get_text_deletion_event_reason(event: Atspi.Event) -> TextEventReason:
        """Returns the TextEventReason for the given event."""

        from . import input_event_manager  # pylint: disable=import-outside-toplevel

        mgr = input_event_manager.get_manager()
        reason = AXUtilitiesEvent._get_obj_type_reason_or_none(event, mgr)
        if reason is not None:
            return reason

        obj = event.source
        if not (AXUtilitiesState.is_editable(obj) or AXUtilitiesRole.is_terminal(obj)):
            return AXUtilitiesEvent._get_non_editable_reason(event, mgr)

        reason = AXUtilitiesEvent._get_editing_reason(mgr)
        if reason != TextEventReason.UNKNOWN:
            return reason
        if mgr.last_event_was_command():
            return TextEventReason.UNSPECIFIED_COMMAND
        if mgr.last_event_was_printable_key():
            return TextEventReason.TYPING
        if mgr.last_event_was_up_or_down() or mgr.last_event_was_page_up_or_page_down():
            if AXUtilitiesEvent._is_spin_button_descendant(obj):
                return TextEventReason.SPIN_BUTTON_VALUE_CHANGE
            return TextEventReason.AUTO_DELETION_UNPRESENTABLE

        selected_text, _start, _end = AXUtilitiesText.get_cached_selected_text(obj)
        if selected_text and event.any_data.strip() == selected_text.strip():
            return TextEventReason.SELECTED_TEXT_DELETION
        if AXUtilitiesEvent._is_terminal_being_flat_reviewed(obj):
            return TextEventReason.AUTO_DELETION_UNPRESENTABLE
        return TextEventReason.UNKNOWN

    @staticmethod
    def _get_text_insertion_event_reason(event: Atspi.Event) -> TextEventReason:
        """Returns the TextEventReason for the given event."""

        from . import (
            input_event_manager,  # pylint: disable=import-outside-toplevel
            typing_echo_presenter,  # pylint: disable=import-outside-toplevel
        )

        mgr = input_event_manager.get_manager()
        reason = AXUtilitiesEvent._get_obj_type_reason_or_none(event, mgr)
        if reason is not None:
            return reason

        obj = event.source
        is_terminal = AXUtilitiesRole.is_terminal(obj)
        if not (AXUtilitiesState.is_editable(obj) or is_terminal):
            return AXUtilitiesEvent._get_non_editable_reason(event, mgr)

        if is_terminal and AXUtilitiesEvent._is_terminal_escape_sequence(event.any_data):
            return TextEventReason.AUTO_INSERTION_UNPRESENTABLE

        selected_text, _start, _end = AXUtilitiesText.get_selected_text(obj)
        has_selected = bool(selected_text and event.any_data == selected_text)

        if mgr.last_event_was_backspace():
            return TextEventReason.BACKSPACE
        if mgr.last_event_was_delete():
            return TextEventReason.DELETE
        if mgr.last_event_was_cut():
            return TextEventReason.CUT
        if mgr.last_event_was_paste():
            return TextEventReason.PASTE
        if mgr.last_event_was_undo():
            return (
                TextEventReason.SELECTED_TEXT_RESTORATION if has_selected else TextEventReason.UNDO
            )
        if mgr.last_event_was_redo():
            return (
                TextEventReason.SELECTED_TEXT_RESTORATION if has_selected else TextEventReason.REDO
            )
        if mgr.last_event_was_command():
            return TextEventReason.UNSPECIFIED_COMMAND
        if mgr.last_event_was_space() and not AXUtilitiesRole.is_password_text(obj):
            if event.any_data == "\n":
                return TextEventReason.AUTO_INSERTION_UNPRESENTABLE
            return TextEventReason.TYPING
        if mgr.last_event_was_tab() or mgr.last_event_was_return():
            if not event.any_data.strip():
                return TextEventReason.TYPING
            if mgr.last_event_was_tab():
                return TextEventReason.AUTO_INSERTION_PRESENTABLE
            if AXUtilitiesState.is_single_line(obj):
                return TextEventReason.AUTO_INSERTION_UNPRESENTABLE
            return TextEventReason.AUTO_INSERTION_PRESENTABLE
        if mgr.last_event_was_printable_key() or mgr.last_event_was_space():
            if has_selected:
                return TextEventReason.AUTO_INSERTION_PRESENTABLE
            presenter = typing_echo_presenter.get_presenter()
            if AXUtilitiesRole.is_password_text(obj):
                echo = presenter.get_key_echo_enabled()
            else:
                echo = presenter.get_character_echo_enabled()
            return TextEventReason.TYPING_ECHOABLE if echo else TextEventReason.TYPING
        if mgr.last_event_was_middle_click() or mgr.last_event_was_middle_release():
            return TextEventReason.MOUSE_MIDDLE_BUTTON
        if mgr.last_event_was_up_or_down() or mgr.last_event_was_page_up_or_page_down():
            if AXUtilitiesEvent._is_spin_button_descendant(obj):
                return TextEventReason.SPIN_BUTTON_VALUE_CHANGE
            return TextEventReason.AUTO_INSERTION_PRESENTABLE
        if has_selected:
            return TextEventReason.SELECTED_TEXT_INSERTION
        if AXUtilitiesEvent._is_terminal_being_flat_reviewed(obj):
            return TextEventReason.AUTO_INSERTION_UNPRESENTABLE
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
                return TextEventReason.SEARCH_UNPRESENTABLE
            return TextEventReason.SEARCH_PRESENTABLE
        if mgr.last_event_was_caret_selection():
            return AXUtilitiesEvent._get_selection_navigation_reason(mgr)
        if mgr.last_event_was_caret_navigation():
            return AXUtilitiesEvent._get_caret_navigation_reason(mgr)
        if mgr.last_event_was_select_all():
            return TextEventReason.SELECT_ALL
        if mgr.last_event_was_primary_click_or_release():
            return TextEventReason.MOUSE_PRIMARY_BUTTON
        if not (AXUtilitiesState.is_editable(obj) or AXUtilitiesRole.is_terminal(obj)):
            return TextEventReason.UNKNOWN

        reason = AXUtilitiesEvent._get_editing_reason(mgr)
        if reason != TextEventReason.UNKNOWN:
            return reason
        if mgr.last_event_was_page_switch():
            return TextEventReason.PAGE_SWITCH
        if mgr.last_event_was_command():
            return TextEventReason.UNSPECIFIED_COMMAND
        if mgr.last_event_was_printable_key():
            cached_text, old_start, old_end = AXUtilitiesText.get_cached_selected_text(obj)
            if not cached_text:
                _current, new_start, new_end = AXUtilitiesText.get_selected_text(obj)
                if new_start < new_end:
                    return TextEventReason.AUTO_SELECTION
            else:
                _current, new_start, new_end = AXUtilitiesText.get_selected_text(obj)
                if new_start == old_start + 1 and new_end == old_end:
                    return TextEventReason.AUTO_UNSELECTION
            return TextEventReason.TYPING
        if mgr.last_event_was_up_or_down() or mgr.last_event_was_page_up_or_page_down():
            if AXUtilitiesEvent._is_spin_button_descendant(obj):
                return TextEventReason.SPIN_BUTTON_VALUE_CHANGE
        return TextEventReason.UNKNOWN

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

        old_state = AXUtilitiesEvent._CACHE.get_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_CHECKED,
            event.source,
        )
        new_state = AXUtilitiesState.is_checked(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_CHECKED,
            event.source,
            new_state,
        )
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

        old_description = AXUtilitiesEvent._CACHE.get_description(event.source)
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

        AXUtilitiesEvent._CACHE.set_description(event.source, new_description)
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

        manager = focus_manager.get_manager()
        focus = manager.get_locus_of_focus()
        if event.source != focus and not AXUtilitiesObject.is_ancestor(focus, event.source):
            msg = "AXUtilitiesEvent: The event is not from the locus of focus or ancestor."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        window = manager.get_active_window()
        if event.source != window and event.any_data == AXObject.get_name(window):
            msg = "AXUtilitiesEvent: The new description matches the active window's name."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_expanded_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as an expanded-state change."""

        old_state = AXUtilitiesEvent._CACHE.get_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_EXPANDED,
            event.source,
        )
        new_state = AXUtilitiesState.is_expanded(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_EXPANDED,
            event.source,
            new_state,
        )
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

        old_state = AXUtilitiesEvent._CACHE.get_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_INDETERMINATE,
            event.source,
        )
        new_state = AXUtilitiesState.is_indeterminate(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_INDETERMINATE,
            event.source,
            new_state,
        )

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

        old_state = AXUtilitiesEvent._CACHE.get_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_INVALID_ENTRY,
            event.source,
        )
        new_state = AXUtilitiesState.is_invalid_entry(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_INVALID_ENTRY,
            event.source,
            new_state,
        )
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

        if AXUtilitiesRole.is_terminal(focus):
            text = AXText.get_line_at_offset(focus)[0].strip()
            if AXUtilitiesEvent._strings_are_redundant(text, event.any_data):
                msg = (
                    f"AXUtilitiesEvent: The new name ('{event.any_data}') "
                    f"is too similar to the text at offset ('{text}')."
                )
                debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def _is_changed_name_to_present(event: Atspi.Event) -> bool:
        """Returns True if the name data warrants further presentability checks."""

        if AXUtilitiesEvent._CACHE.is_ignoring_name_changes_for(event.source):
            msg = "AXUtilitiesEvent: Ignoring name change for this source."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not isinstance(event.any_data, str):
            msg = "AXUtilitiesEvent: The any_data is not a string."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        old_name = AXUtilitiesEvent._CACHE.get_name(event.source)
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

        AXUtilitiesEvent._CACHE.set_name(event.source, new_name)
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
                AXUtilitiesEvent._CACHE.ignore_name_changes_for(event.source)
                return False

        msg = "AXUtilitiesEvent: Event is presentable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_pressed_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as a pressed-state change."""

        old_state = AXUtilitiesEvent._CACHE.get_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_PRESSED,
            event.source,
        )
        new_state = AXUtilitiesState.is_pressed(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_PRESSED,
            event.source,
            new_state,
        )
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

        old_state = AXUtilitiesEvent._CACHE.get_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_SELECTED,
            event.source,
        )
        new_state = AXUtilitiesState.is_selected(event.source)
        if old_state == new_state:
            msg = "AXUtilitiesEvent: The new state matches the old state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        AXUtilitiesEvent._CACHE.set_state(
            AXUtilitiesEvent._CACHE.LAST_KNOWN_SELECTED,
            event.source,
            new_state,
        )
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

        source_states = AXObject.get_state_set(event.source)
        if AXUtilitiesState.manages_descendants(event.source, source_states):
            msg = "AXUtilitiesEvent: Source manages descendants; handled elsewhere."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilitiesRole.is_menu(event.source):
            if AXUtilitiesState.is_showing_and_visible(event.source, source_states):
                msg = "AXUtilitiesEvent: Event is presentable: Source is a menu."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            # This is a sad workaround for GTK2 menu items with submenus losing their showing state
            # when submenu children become selected.
            child = AXSelection.get_selected_child(event.source, 0)
            if child is not None and AXUtilitiesState.is_showing_and_visible(child):
                tokens = [
                    "AXUtilitiesEvent: Event is presentable: Selected child",
                    child,
                    "is showing and visible",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return True

            tokens = ["AXUtilitiesEvent: Menu lacks showing + visible:", event.source]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilitiesRole.is_combo_box(event.source) and not AXUtilitiesState.is_expanded(
            event.source, source_states
        ):
            text_input = AXUtilitiesObject.find_descendant(
                event.source, AXUtilitiesRole.is_text_input
            )
            if text_input is not None and AXUtilitiesState.is_focused(text_input):
                msg = "AXUtilitiesEvent: Combo box text input is focused; not a user selection."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

        focus = focus_manager.get_manager().get_locus_of_focus()

        mgr = input_event_manager.get_manager()
        if (
            AXUtilitiesState.supports_autocompletion(focus)
            and not mgr.last_event_was_up_or_down()
            and not mgr.last_event_was_page_up_or_page_down()
        ):
            if AXUtilitiesRelation.object_is_controlled_by(event.source, focus):
                msg = "AXUtilitiesEvent: Source is autocomplete for focused widget; not presenting."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False
        if event.source != focus and not AXUtilitiesState.is_showing_and_visible(
            event.source, source_states
        ):
            combobox = AXUtilitiesObject.find_ancestor(event.source, AXUtilitiesRole.is_combo_box)
            if combobox != focus and event.source != AXObject.get_parent(focus):
                tokens = ["AXUtilitiesEvent: Source lacks showing + visible:", event.source]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return False

        active_window = focus_manager.get_manager().get_active_window()
        if active_window and not AXUtilitiesObject.is_ancestor(event.source, active_window):
            tokens = ["AXUtilitiesEvent:", event.source, "is not inside", active_window]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        msg = "AXUtilitiesEvent: Event is presentable: Not ruled out by any checks."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @staticmethod
    def is_presentable_value_change(event: Atspi.Event) -> bool:
        """Returns True if this event should be presented as a value change."""

        old_value = AXUtilitiesEvent._CACHE.get_value(event.source)
        new_value = AXValue.get_current_value(event.source)
        AXUtilitiesEvent._CACHE.set_value(event.source, new_value)

        old_value_text = AXUtilitiesEvent._CACHE.get_value_text(event.source)
        new_value_text = AXValue.get_current_value_text(event.source)
        AXUtilitiesEvent._CACHE.set_value_text(event.source, new_value_text)

        if old_value == new_value and old_value_text == new_value_text:
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

        source_states = AXObject.get_state_set(event.source)
        if not (
            AXUtilitiesState.is_editable(event.source, source_states)
            or AXUtilitiesRole.is_terminal(event.source)
        ):
            msg = "AXUtilitiesEvent: The source is neither editable nor a terminal."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus != event.source and not AXUtilitiesState.is_focused(event.source, source_states):
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
