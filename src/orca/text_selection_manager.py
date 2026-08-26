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

"""Manages accessible text selection."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import ax_cache_manager, debug, input_event_manager
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    from collections.abc import Hashable

    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from . import input_event
    from .scripts import default

    SelectionPosition = tuple[Atspi.Accessible | None, int]
    SelectionBoundaries = tuple[SelectionPosition, SelectionPosition]


@dataclass(frozen=True)
class _TextSelectionEndpoint:
    """An accessible object and offset forming one endpoint of a text selection."""

    accessible_object: Atspi.Accessible
    offset: int


@dataclass(frozen=True)
class _TextSelectionSnapshot:
    """Selection state captured before an Orca text-selection command."""

    selection_container: Atspi.Accessible | None
    focus: _TextSelectionEndpoint
    focus_object_selection_start: int
    focus_object_selection_end: int
    anchor: _TextSelectionEndpoint


@dataclass(frozen=True, kw_only=True)
class _PendingSelectionChange:
    """A requested selection change awaiting its reported result."""

    container: Atspi.Accessible
    anchor: _TextSelectionEndpoint
    focus: _TextSelectionEndpoint


@dataclass(frozen=True)
class _TextSelectionResult:
    """Result of an Orca text-selection command."""

    succeeded: bool
    objects: tuple[Atspi.Accessible, ...]
    anchor: _TextSelectionEndpoint | None
    pending_change: _PendingSelectionChange | None = None


class SelectionChangeState(enum.Enum):
    """Describes how a reported text-selection change should be handled."""

    NOT_ORCA = enum.auto()
    UNPRESENTABLE = enum.auto()
    PRESENTABLE = enum.auto()


@dataclass(frozen=True, kw_only=True)
class TextSelectionCommand:
    """An Orca command which changed text selection."""

    _event: input_event.InputEvent
    _objects: tuple[Atspi.Accessible, ...]
    _selection_container: Atspi.Accessible | None
    _selection_anchor: _TextSelectionEndpoint | None
    _selection_focus: _TextSelectionEndpoint | None
    _pending_change: _PendingSelectionChange | None
    _should_notify_user: bool

    def get_input_event(self) -> input_event.InputEvent:
        """Returns the input event which triggered this selection command."""

        return self._event

    def get_objects(self) -> tuple[Atspi.Accessible, ...]:
        """Returns the objects associated with this selection command."""

        return self._objects

    def get_selection_container(self) -> Atspi.Accessible | None:
        """Returns the container associated with this selection command."""

        return self._selection_container

    def get_selection_anchor(self) -> _TextSelectionEndpoint | None:
        """Returns the anchor associated with this selection command."""

        return self._selection_anchor

    def get_selection_focus(self) -> _TextSelectionEndpoint | None:
        """Returns the focus associated with this selection command."""

        return self._selection_focus

    def get_pending_change(self) -> _PendingSelectionChange | None:
        """Returns the selection change awaiting its reported result."""

        return self._pending_change

    def should_notify_user(self) -> bool:
        """Returns True if this selection command should be presented."""

        return self._should_notify_user


class TextSelectionManager:
    """Provides high-level text-selection operations independent of navigation modality."""

    SELECTION_BOUNDARIES = "TextSelectionManager.boundaries"

    def __init__(self) -> None:
        self._last_selection_command: TextSelectionCommand | None = None
        self._pending_page_change: tuple[TextSelectionCommand, int] | None = None
        manager = ax_cache_manager.get_manager()
        manager.register_cache(
            self,
            self.SELECTION_BOUNDARIES,
            lifetime=ax_cache_manager.Lifetime.OWNER,
            clear_on_demand=ax_cache_manager.ClearPolicy.PRESERVE,
            clear_interval_seconds=None,
        )
        self._selection_boundaries = manager.get_cache(
            self,
            self.SELECTION_BOUNDARIES,
        )

    def get_current_selection_command(
        self,
        obj: Atspi.Accessible | None = None,
    ) -> TextSelectionCommand | None:
        """Returns the Orca selection command associated with the current input event."""

        command = self._get_current_selection_command()
        if command is None:
            return None
        if obj is not None and not self._command_applies_to_object(command, obj):
            return None
        return command

    def _get_current_selection_command(self) -> TextSelectionCommand | None:
        """Returns the selection command associated with the current input event."""

        command = self._last_selection_command
        if command is None:
            return None

        event = command.get_input_event()
        manager = input_event_manager.get_manager()
        result = manager.last_event_equals_or_is_release_for_event(event)
        string = event.as_single_line_string()
        tokens = ["TEXT SELECTION MANAGER: Last selection event (", string, ") is current:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return command if result else None

    def get_selection_command_for_object(
        self,
        obj: Atspi.Accessible,
    ) -> TextSelectionCommand | None:
        """Returns the Orca command associated with a reported selection change."""

        command = self._last_selection_command
        if command is None or not self._command_applies_to_object(command, obj):
            return None
        if self._get_current_selection_command() is command:
            return command
        if command.get_pending_change() is None:
            self._clear_selection_command()
            return None
        return command

    def is_selection_change_from_selection_command(
        self,
        obj: Atspi.Accessible | None,
    ) -> bool:
        """Returns True if a selection command caused the reported change in obj."""

        if input_event_manager.get_manager().last_event_was_caret_selection():
            return True
        return bool(obj is not None and self.get_current_selection_command(obj) is not None)

    def defer_page_change_for_current_selection(self, page_number: int) -> bool:
        """Defers a page change associated with the current selection command."""

        command = self.get_current_selection_command()
        if command is None:
            self._pending_page_change = None
            return False

        self._pending_page_change = command, page_number
        tokens = ["TEXT SELECTION MANAGER: Deferred page", page_number, "for selection command."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return True

    def take_deferred_page_change_for_selection(
        self,
        obj: Atspi.Accessible,
    ) -> int | None:
        """Returns and clears the page change associated with obj's selection command."""

        pending = self._pending_page_change
        if pending is None:
            return None

        self._pending_page_change = None
        command, page_number = pending
        if self.get_selection_command_for_object(obj) is not command:
            return None
        return page_number

    def _clear_selection_command(self) -> None:
        """Clears the retained selection command and its pending page change."""

        self._last_selection_command = None
        self._pending_page_change = None

    @staticmethod
    def _command_applies_to_object(
        command: TextSelectionCommand,
        obj: Atspi.Accessible,
    ) -> bool:
        """Returns True if command applies to obj."""

        if obj in command.get_objects():
            return True

        container = command.get_selection_container()
        return bool(container is not None and AXUtilities.is_ancestor(obj, container, True))

    @staticmethod
    def _get_selected_text_with_eocs_expanded(obj: Atspi.Accessible) -> str:
        """Returns the selected text with embedded object characters expanded."""

        string, start_offset, end_offset = AXUtilities.get_selected_text(obj)
        if not string:
            return ""

        return AXUtilities.expand_eocs_in_range(
            obj,
            start_offset,
            obj,
            end_offset,
            include_start=True,
            include_end=False,
        )

    def get_all_selected_text(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
    ) -> str:
        """Returns all text in the logical selection containing obj."""

        if AXUtilities.is_spreadsheet_cell(obj):
            return self._get_selected_text_with_eocs_expanded(obj)

        document = (
            obj
            if AXUtilities.is_document(obj)
            else AXUtilities.find_ancestor(obj, AXUtilities.is_document)
        )
        if document is not None:
            success, strings = AXUtilities.get_document_selected_texts(document)
            if success:
                return " ".join(strings)

            start, end = AXUtilities.get_document_text_selection_endpoints(None, document)
            start_obj, start_offset = start
            end_obj, end_offset = end
            if start_obj is not None and end_obj is not None:
                expanded = AXUtilities.expand_eocs_in_range(
                    start_obj,
                    start_offset,
                    end_obj,
                    end_offset,
                    include_start=True,
                    include_end=False,
                )
                if expanded:
                    return expanded

        strings = []
        current = self._get_selected_text_with_eocs_expanded(obj)
        if current:
            strings.append(current)

        preceding_strings: list[str] = []
        previous_obj = script.utilities.find_previous_object(obj)
        while previous_obj is not None:
            selection = self._get_selected_text_with_eocs_expanded(previous_obj)
            if not selection:
                break
            preceding_strings.insert(0, selection)
            previous_obj = script.utilities.find_previous_object(previous_obj)

        next_obj = script.utilities.find_next_object(obj)
        while next_obj is not None:
            selection = self._get_selected_text_with_eocs_expanded(next_obj)
            if not selection:
                break
            strings.append(selection)
            next_obj = script.utilities.find_next_object(next_obj)

        return " ".join(preceding_strings + strings)

    def _get_selection_anchor_from_previous_command(
        self,
        selection_container: Atspi.Accessible | None,
    ) -> _TextSelectionEndpoint | None:
        """Returns the selection anchor saved by the previous Orca command."""

        command = self._last_selection_command
        anchor = command.get_selection_anchor() if command is not None else None
        if (
            command is None
            or command.get_selection_container() != selection_container
            or anchor is None
        ):
            return None
        if not AXObject.is_valid(anchor.accessible_object):
            msg = "TEXT SELECTION MANAGER: Discarding invalid retained selection anchor."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        return anchor

    def _clear_cached_selection_state(
        self,
        selection_root: Atspi.Accessible,
    ) -> SelectionBoundaries | None:
        """Clears and returns cached selection boundaries for selection_root."""

        key = ax_cache_manager.get_object_key(selection_root)
        boundaries_cache = self._selection_boundaries
        if boundaries_cache is None:
            return None

        boundaries = boundaries_cache.get(key, None)
        boundaries_cache.discard(key)
        if boundaries is None:
            return None
        tokens = [
            "TEXT SELECTION MANAGER: Cleared cached selection state for",
            selection_root,
            "Boundaries:",
            boundaries,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return boundaries

    def _get_selection_change_state(
        self,
        container: Atspi.Accessible | None,
        selection: SelectionBoundaries,
    ) -> tuple[SelectionChangeState, bool]:
        """Returns the state and whether stable selection data should be updated."""

        command = self._last_selection_command
        if command is None:
            return SelectionChangeState.NOT_ORCA, True

        pending_change = command.get_pending_change()
        if pending_change is None or pending_change.container != container:
            return SelectionChangeState.NOT_ORCA, True

        result_is_requested = self._selection_matches_pending_change(selection, pending_change)

        if self._get_current_selection_command() is command:
            if result_is_requested:
                return SelectionChangeState.PRESENTABLE, True
            return SelectionChangeState.UNPRESENTABLE, False

        self._clear_selection_command()
        if result_is_requested:
            msg = "TEXT SELECTION MANAGER: Ignoring change from previous selection command."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return SelectionChangeState.UNPRESENTABLE, True
        return SelectionChangeState.NOT_ORCA, True

    @staticmethod
    def _selection_matches_pending_change(
        selection: SelectionBoundaries,
        pending_change: _PendingSelectionChange,
    ) -> bool:
        """Returns True if selection matches the requested pending change."""

        anchor = pending_change.anchor
        focus = pending_change.focus
        comparison = AXUtilities.compare_text_positions(
            anchor.accessible_object,
            anchor.offset,
            focus.accessible_object,
            focus.offset,
        )
        start, end = selection
        if comparison == 0:
            return start[0] is None and end[0] is None
        if start[0] is None or end[0] is None:
            return False

        requested_start = anchor if comparison < 0 else focus
        requested_end = focus if comparison < 0 else anchor
        return AXUtilities.text_selection_positions_are_equivalent(
            start[0], start[1], requested_start.accessible_object, requested_start.offset
        ) and AXUtilities.text_selection_positions_are_equivalent(
            end[0], end[1], requested_end.accessible_object, requested_end.offset
        )

    @staticmethod
    def _get_document_and_selection_root(
        obj: Atspi.Accessible,
    ) -> tuple[Atspi.Accessible | None, Atspi.Accessible]:
        """Returns the document and selection root containing obj."""

        document = AXUtilities.find_outermost_ancestor_inclusive(obj, AXUtilities.is_document)
        selection_root = document or AXUtilities.get_text_selection_container(obj)
        return document, selection_root

    def has_known_selection(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj or its selection root is known to have selected text."""

        if AXUtilities.has_selected_text(obj):
            return True

        _document, selection_root = self._get_document_and_selection_root(obj)
        if selection_root is None:
            return False

        return self._has_cached_selection(ax_cache_manager.get_object_key(selection_root))

    def _has_pending_selection_change(self) -> bool:
        """Returns True if an Orca selection command is awaiting its reported result."""

        command = self._last_selection_command
        return command is not None and command.get_pending_change() is not None

    def _has_cached_selection(self, key: Hashable) -> bool:
        """Returns True if the cached boundaries for key describe selected text."""

        start, end = self._get_cached_selection(key)
        return start[0] is not None or end[0] is not None

    @staticmethod
    def _get_text_selection_endpoints(
        anchor: _TextSelectionEndpoint | None,
        focus: _TextSelectionEndpoint | None,
    ) -> SelectionBoundaries:
        """Returns the ordered endpoints, or empty endpoints when no selection exists."""

        if anchor is None or focus is None:
            return (None, -1), (None, -1)
        anchor_position = anchor.accessible_object, anchor.offset
        focus_position = focus.accessible_object, focus.offset
        if anchor_position == focus_position:
            return (None, -1), (None, -1)
        if AXUtilities.compare_text_positions(*anchor_position, *focus_position) > 0:
            return focus_position, anchor_position
        return anchor_position, focus_position

    def get_known_text_selection_endpoints(
        self,
        selection_root: Atspi.Accessible,
    ) -> SelectionBoundaries:
        """Returns selection endpoints already known for selection_root without querying it."""

        command = self._last_selection_command
        if command is not None and command.get_selection_container() == selection_root:
            return self._get_text_selection_endpoints(
                command.get_selection_anchor(),
                command.get_selection_focus(),
            )

        return self._get_cached_selection(ax_cache_manager.get_object_key(selection_root))

    def _get_cached_selection(self, key: Hashable) -> SelectionBoundaries:
        """Returns the cached selection boundaries for key."""

        if self._selection_boundaries is None:
            return (None, -1), (None, -1)
        return self._selection_boundaries.get(key, ((None, -1), (None, -1)))

    @staticmethod
    def _update_selected_text_caches(
        old_selection: SelectionBoundaries,
        selection: SelectionBoundaries,
        event_source: Atspi.Accessible | None = None,
    ) -> None:
        """Updates selected-text caches for objects in both selections."""

        old_start, old_end = old_selection
        start, end = selection
        reported_elements = AXUtilities.get_text_selection_elements(
            old_start[0],
            old_end[0],
        ) + AXUtilities.get_text_selection_elements(start[0], end[0])
        if event_source is not None:
            reported_elements.append(event_source)
        elements: list[Atspi.Accessible] = []
        for element in reported_elements:
            if element not in elements:
                elements.append(element)
        for element in elements:
            AXUtilities.update_cached_selected_text(element)

    def _store_selection_change(
        self,
        selection_root: Atspi.Accessible,
        key: Hashable,
        state: SelectionChangeState,
        selection: SelectionBoundaries,
    ) -> None:
        """Caches a reported selection change and updates related state."""

        if self._selection_boundaries is not None:
            self._selection_boundaries.put(key, selection)
        start, end = selection
        if state == SelectionChangeState.PRESENTABLE and start[0] is None and end[0] is None:
            self._clear_cached_selection_state(selection_root)

    def update_selection_state(
        self,
        obj: Atspi.Accessible,
    ) -> tuple[SelectionChangeState, SelectionBoundaries, SelectionBoundaries]:
        """Updates selection state for obj and returns its classification and boundaries."""

        document, selection_root = self._get_document_and_selection_root(obj)
        key = ax_cache_manager.get_object_key(selection_root)
        old_selection = self._get_cached_selection(key)
        old_start, old_end = old_selection
        search_text_objects = (
            self._has_pending_selection_change()
            or self._has_cached_selection(key)
            or AXUtilities.has_selected_text(obj)
        )
        start, end = AXUtilities.get_document_text_selection_endpoints(
            document, selection_root, search_text_objects
        )
        selection = (start, end)
        tokens = [
            "TEXT SELECTION MANAGER: Updating text selection state for",
            obj,
            "Selection root:",
            selection_root,
            "Old boundaries:",
            old_start,
            old_end,
            "New boundaries:",
            start,
            end,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        state, update_state = self._get_selection_change_state(
            selection_root,
            selection,
        )
        if start[0] is None and end[0] is None and AXUtilities.has_selected_text(selection_root):
            msg = "TEXT SELECTION MANAGER: Ignoring indeterminate selection boundaries."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            state = SelectionChangeState.UNPRESENTABLE
            update_state = False

        if update_state:
            self._store_selection_change(
                selection_root,
                key,
                state,
                selection,
            )
        if state == SelectionChangeState.UNPRESENTABLE:
            self._update_selected_text_caches(old_selection, selection, obj)
        return state, old_selection, selection

    def update_state_for_unpresentable_selection_change(
        self,
        obj: Atspi.Accessible,
    ) -> None:
        """Updates selection state and caches without presenting the reported change."""

        state, old_selection, selection = self.update_selection_state(obj)
        if state == SelectionChangeState.UNPRESENTABLE:
            return
        self._update_selected_text_caches(old_selection, selection, obj)

    def set_text_selection(
        self,
        selection_container: Atspi.Accessible | None,
        source_object: Atspi.Accessible,
        source_offset: int,
        destination_object: Atspi.Accessible,
        destination_offset: int,
        destination_context_object: Atspi.Accessible,
        *,
        selection_forward: bool,
        event: input_event.InputEvent | None,
        notify_user: bool,
    ) -> bool:
        """Sets text selection from the source position to the destination position."""

        snapshot = self._take_snapshot(
            selection_container,
            source_object,
            source_offset,
        )
        return self._apply_selection(
            snapshot,
            destination_object,
            destination_offset,
            destination_context_object,
            selection_forward=selection_forward,
            event=event,
            notify_user=notify_user,
        )

    def _take_snapshot(
        self,
        selection_container: Atspi.Accessible | None,
        focus_object: Atspi.Accessible,
        focus_offset: int,
    ) -> _TextSelectionSnapshot:
        """Captures state needed to apply an Orca text-selection command."""

        _selected_string, selection_start, selection_end = AXUtilities.get_selected_text(
            focus_object
        )
        focus = _TextSelectionEndpoint(focus_object, focus_offset)
        anchor_offset_in_focus = AXUtilities.get_selection_anchor_offset(
            focus.accessible_object,
            focus.offset,
            selection_start,
            selection_end,
        )
        anchor = self._get_selection_anchor(
            selection_container,
            focus,
            anchor_offset_in_focus,
            selection_start != selection_end,
        )

        return _TextSelectionSnapshot(
            selection_container,
            focus,
            selection_start,
            selection_end,
            anchor,
        )

    def _get_selection_anchor(
        self,
        selection_container: Atspi.Accessible | None,
        focus: _TextSelectionEndpoint,
        anchor_offset_in_focus: int,
        focus_object_has_selection: bool,
    ) -> _TextSelectionEndpoint:
        """Returns the fixed anchor for the selection."""

        previous_anchor = self._get_selection_anchor_from_previous_command(selection_container)
        if previous_anchor is not None:
            return previous_anchor

        default_anchor = _TextSelectionEndpoint(focus.accessible_object, anchor_offset_in_focus)
        if selection_container is None or not (
            focus_object_has_selection or AXUtilities.has_selected_text(selection_container)
        ):
            return default_anchor

        start, end = AXUtilities.get_document_text_selection_endpoints(
            selection_container,
            selection_container,
        )
        start_object, start_offset = start
        end_object, end_offset = end
        if start_object is None or end_object is None:
            return default_anchor
        if AXUtilities.text_selection_positions_are_equivalent(
            focus.accessible_object,
            focus.offset,
            start_object,
            start_offset,
        ):
            return _TextSelectionEndpoint(end_object, end_offset)
        if AXUtilities.text_selection_positions_are_equivalent(
            focus.accessible_object,
            focus.offset,
            end_object,
            end_offset,
        ):
            return _TextSelectionEndpoint(start_object, start_offset)
        return default_anchor

    @staticmethod
    def _get_selection_range_for_source_object(
        snapshot: _TextSelectionSnapshot,
        selection_forward: bool,
        character_count: int,
    ) -> tuple[int, int]:
        """Returns the range to select in the object being left."""

        anchor_offset_in_focus = TextSelectionManager._get_anchor_offset_in_focus(snapshot)
        if selection_forward:
            return anchor_offset_in_focus, character_count
        return 0, anchor_offset_in_focus

    @staticmethod
    def _get_anchor_offset_in_focus(snapshot: _TextSelectionSnapshot) -> int:
        """Returns the selection anchor mapped into snapshot's focus object."""

        if snapshot.anchor.accessible_object == snapshot.focus.accessible_object:
            return snapshot.anchor.offset
        return AXUtilities.get_selection_anchor_offset(
            snapshot.focus.accessible_object,
            snapshot.focus.offset,
            snapshot.focus_object_selection_start,
            snapshot.focus_object_selection_end,
        )

    @staticmethod
    def _get_selection_range_for_destination_object(
        current_selection_start: int,
        current_selection_end: int,
        new_focus_offset: int,
        selection_forward: bool,
        character_count: int,
    ) -> tuple[int, int]:
        """Returns the range to select in the object being entered."""

        selection_exists = current_selection_start != current_selection_end
        if selection_exists and selection_forward:
            return new_focus_offset, current_selection_end
        if selection_exists:
            return current_selection_start, new_focus_offset
        if selection_forward:
            return 0, new_focus_offset
        return new_focus_offset, character_count

    @staticmethod
    def _set_text_object_selection(
        obj: Atspi.Accessible,
        start: int,
        end: int,
    ) -> bool:
        """Sets or clears the selection in obj for the requested range."""

        if start == end:
            AXUtilities.clear_all_selected_text(obj)
            return True

        result = AXUtilities.set_selected_text(obj, start, end)
        tokens = ["TEXT SELECTION MANAGER: Set selection:", result, obj, (start, end)]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _apply_selection(
        self,
        snapshot: _TextSelectionSnapshot,
        new_focus_object: Atspi.Accessible,
        new_focus_offset: int,
        new_caret_context_object: Atspi.Accessible,
        *,
        selection_forward: bool,
        event: input_event.InputEvent | None,
        notify_user: bool,
    ) -> bool:
        """Applies the selection represented by snapshot and the new focus."""

        new_focus = _TextSelectionEndpoint(new_focus_object, new_focus_offset)
        tokens = [
            "TEXT SELECTION MANAGER: Selection anchor is",
            snapshot.anchor.accessible_object,
            snapshot.anchor.offset,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        result = self._apply_selection_with_document_interface(
            snapshot,
            new_focus,
            new_caret_context_object,
        )
        if result is None and new_focus.accessible_object == snapshot.focus.accessible_object:
            result = self._apply_selection_within_text_object(
                snapshot,
                new_focus,
                new_caret_context_object,
            )
        elif result is None:
            result = self._apply_selection_across_text_objects(
                snapshot,
                new_focus,
                new_caret_context_object,
                selection_forward,
            )

        if not result.succeeded:
            msg = "TEXT SELECTION MANAGER: Selection command failed."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        self._record_selection_command(
            event,
            result.objects,
            notify_user,
            selection_container=snapshot.selection_container,
            selection_anchor=result.anchor,
            selection_focus=new_focus if result.anchor is not None else None,
            pending_change=result.pending_change,
        )
        return True

    @staticmethod
    def _apply_selection_with_document_interface(
        snapshot: _TextSelectionSnapshot,
        new_focus: _TextSelectionEndpoint,
        new_caret_context_object: Atspi.Accessible,
    ) -> _TextSelectionResult | None:
        """Applies selection through the document interface when available."""

        selection_container = snapshot.selection_container
        if selection_container is None:
            return None

        selection_was_set = AXUtilities.set_document_text_selection_endpoints(
            selection_container,
            snapshot.anchor.accessible_object,
            snapshot.anchor.offset,
            new_focus.accessible_object,
            new_focus.offset,
        )
        if not selection_was_set:
            return None

        selection_exists = (
            snapshot.anchor.accessible_object,
            snapshot.anchor.offset,
        ) != (
            new_focus.accessible_object,
            new_focus.offset,
        )
        pending_change = _PendingSelectionChange(
            container=selection_container,
            anchor=snapshot.anchor,
            focus=new_focus,
        )
        return _TextSelectionResult(
            True,
            (new_caret_context_object,),
            snapshot.anchor if selection_exists else None,
            pending_change,
        )

    def _apply_selection_within_text_object(
        self,
        snapshot: _TextSelectionSnapshot,
        new_focus: _TextSelectionEndpoint,
        new_caret_context_object: Atspi.Accessible,
    ) -> _TextSelectionResult:
        """Applies selection within one object through AtspiText."""

        text_object = snapshot.focus.accessible_object
        anchor_offset_in_focus = self._get_anchor_offset_in_focus(snapshot)
        selection_container = snapshot.selection_container
        if selection_container is not None and snapshot.anchor.accessible_object != text_object:
            container_start, container_end = AXUtilities.get_document_text_selection_endpoints(
                selection_container,
                selection_container,
            )
            if container_start[0] == snapshot.anchor.accessible_object:
                anchor_offset_in_focus = 0
            elif container_end[0] == snapshot.anchor.accessible_object:
                anchor_offset_in_focus = AXText.get_character_count(text_object)
            tokens = [
                "TEXT SELECTION MANAGER: AtspiText fallback mapped container anchor to offset",
                anchor_offset_in_focus,
                "in",
                text_object,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        selection_exists = anchor_offset_in_focus != new_focus.offset
        if selection_exists:
            start, end = sorted((anchor_offset_in_focus, new_focus.offset))
            succeeded = AXUtilities.set_selected_text(text_object, start, end)
        else:
            AXUtilities.clear_all_selected_text(text_object)
            succeeded = True

        return _TextSelectionResult(
            succeeded,
            (new_caret_context_object,),
            snapshot.anchor if selection_exists else None,
        )

    def _apply_selection_across_text_objects(
        self,
        snapshot: _TextSelectionSnapshot,
        new_focus: _TextSelectionEndpoint,
        new_caret_context_object: Atspi.Accessible,
        selection_forward: bool,
    ) -> _TextSelectionResult:
        """Applies a cross-object selection through the AtspiText fallback."""

        source_object = snapshot.focus.accessible_object
        source_range = self._get_selection_range_for_source_object(
            snapshot,
            selection_forward,
            AXText.get_character_count(source_object),
        )
        destination_object = new_focus.accessible_object
        _string, destination_start, destination_end = AXUtilities.get_selected_text(
            new_focus.accessible_object
        )
        destination_range = self._get_selection_range_for_destination_object(
            destination_start,
            destination_end,
            new_focus.offset,
            selection_forward,
            AXText.get_character_count(destination_object),
        )

        old_source_range = (
            snapshot.focus_object_selection_start,
            snapshot.focus_object_selection_end,
        )
        source_range_is_empty = source_range[0] == source_range[1]
        old_source_range_is_empty = old_source_range[0] == old_source_range[1]
        source_range_changed = source_range != old_source_range and not (
            source_range_is_empty and old_source_range_is_empty
        )
        if source_range_changed:
            source_succeeded = self._set_text_object_selection(
                source_object,
                *source_range,
            )
            if not source_succeeded:
                self._set_text_object_selection(
                    source_object,
                    *old_source_range,
                )
                msg = "TEXT SELECTION MANAGER: Attempted to restore source after failure."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return _TextSelectionResult(False, (), None)

        old_destination_range = destination_start, destination_end
        destination_range_is_empty = destination_range[0] == destination_range[1]
        if not self._set_text_object_selection(
            destination_object,
            *destination_range,
        ):
            self._set_text_object_selection(
                destination_object,
                *old_destination_range,
            )
            if source_range_changed:
                self._set_text_object_selection(
                    source_object,
                    *old_source_range,
                )
            msg = "TEXT SELECTION MANAGER: Attempted to restore selection after failure."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return _TextSelectionResult(False, (), None)

        selection_exists = not source_range_is_empty or not destination_range_is_empty
        return _TextSelectionResult(
            True,
            (source_object, new_caret_context_object),
            snapshot.anchor if selection_exists else None,
        )

    def clear_selection_for_navigation(
        self,
        root: Atspi.Accessible | None,
        destination_obj: Atspi.Accessible,
    ) -> list[Atspi.Accessible]:
        """Clears selected text before ordinary navigation and returns affected objects."""

        command = self._last_selection_command
        self._clear_selection_command()
        selection_root = root or destination_obj
        cached_selection = self._clear_cached_selection_state(selection_root)
        candidates: list[Atspi.Accessible] = []

        def add_candidate(obj: Atspi.Accessible | None) -> None:
            if obj is not None and obj not in candidates:
                candidates.append(obj)

        def add_selection(boundaries: SelectionBoundaries) -> None:
            start, end = boundaries
            for endpoint_obj, _offset in (start, end):
                if endpoint_obj is not None:
                    add_candidate(AXUtilities.get_text_selection_container(endpoint_obj))
            for element in AXUtilities.get_text_selection_elements(start[0], end[0]):
                add_candidate(element)

        if cached_selection is not None:
            add_selection(cached_selection)
        if command is not None:
            add_selection(
                self._get_text_selection_endpoints(
                    command.get_selection_anchor(),
                    command.get_selection_focus(),
                )
            )
            for obj in command.get_objects():
                add_candidate(obj)

        destination_has_selection = AXUtilities.has_selected_text(destination_obj)
        if destination_has_selection and cached_selection is None and root is not None:
            start, end = AXUtilities.get_document_text_selection_endpoints(root, root)
            add_selection((start, end))
        add_candidate(destination_obj)

        cleared_selection_objs: list[Atspi.Accessible] = []
        for obj in candidates:
            if not AXObject.supports_text(obj):
                continue
            has_selection = (
                destination_has_selection
                if obj == destination_obj
                else AXUtilities.has_selected_text(obj)
            )
            if not has_selection:
                continue
            cleared_selection_objs.append(obj)
            AXUtilities.clear_all_selected_text(obj)
            AXUtilities.update_cached_selected_text(obj)
        return cleared_selection_objs

    def _record_selection_command(
        self,
        event: input_event.InputEvent | None,
        objects: tuple[Atspi.Accessible, ...],
        notify_user: bool,
        *,
        selection_container: Atspi.Accessible | None,
        selection_anchor: _TextSelectionEndpoint | None,
        selection_focus: _TextSelectionEndpoint | None,
        pending_change: _PendingSelectionChange | None,
    ) -> None:
        """Records an Orca selection command triggered by event."""

        if event is None:
            return

        self._pending_page_change = None
        self._last_selection_command = TextSelectionCommand(
            _event=event,
            _objects=objects,
            _selection_container=selection_container,
            _selection_anchor=selection_anchor,
            _selection_focus=selection_focus,
            _pending_change=pending_change,
            _should_notify_user=notify_user,
        )


_manager = TextSelectionManager()


def get_manager() -> TextSelectionManager:
    """Returns the singleton text selection manager."""

    return _manager
