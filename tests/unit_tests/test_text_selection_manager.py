# Unit tests for text_selection_manager.py methods.
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

# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel

"""Unit tests for text_selection_manager.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import call

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestTextSelectionManager:
    """Test TextSelectionManager methods."""

    @staticmethod
    def _setup_dependencies(test_context: OrcaTestContext) -> None:
        additional_modules = ["orca.ax_cache_manager", "orca.input_event_manager"]
        test_context.setup_shared_dependencies(additional_modules)

    def test_get_all_selected_text_for_spreadsheet_cell(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test spreadsheet-cell selection does not traverse adjacent objects."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        script = test_context.Mock()
        cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "is_spreadsheet_cell", return_value=True)
        test_context.patch_object(
            AXUtilities, "get_selected_text", return_value=("cell text", 2, 11)
        )
        expand_selected_text = test_context.patch_object(
            AXUtilities, "expand_eocs_in_range", return_value="cell text"
        )

        assert manager.get_all_selected_text(script, cell) == "cell text"
        expand_selected_text.assert_called_once_with(
            cell, 2, cell, 11, include_start=True, include_end=False
        )
        script.utilities.find_previous_object.assert_not_called()
        script.utilities.find_next_object.assert_not_called()

    def test_get_all_selected_text_prefers_document_selection(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test document selections take precedence over per-object selections."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        script = test_context.Mock()
        obj = test_context.Mock(spec=Atspi.Accessible)
        document = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "is_spreadsheet_cell", return_value=False)
        test_context.patch_object(AXUtilities, "is_document", return_value=False)
        test_context.patch_object(AXUtilities, "find_ancestor", return_value=document)
        get_document_selected_texts = test_context.patch_object(
            AXUtilities,
            "get_document_selected_texts",
            return_value=(True, ["First selection", "Second selection"]),
        )
        get_selected_text = test_context.patch_object(AXUtilities, "get_selected_text")
        expand_selected_text = test_context.patch_object(AXUtilities, "expand_eocs_in_range")

        assert manager.get_all_selected_text(script, obj) == "First selection Second selection"
        get_document_selected_texts.assert_called_once_with(document)
        get_selected_text.assert_not_called()
        expand_selected_text.assert_not_called()
        script.utilities.find_previous_object.assert_not_called()
        script.utilities.find_next_object.assert_not_called()

    def test_get_all_selected_text_uses_adjacent_text_objects_as_fallback(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test failed document retrieval falls back to adjacent selected text objects."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        script = test_context.Mock()
        obj = test_context.Mock(spec=Atspi.Accessible)
        previous_obj = test_context.Mock(spec=Atspi.Accessible)
        next_obj = test_context.Mock(spec=Atspi.Accessible)
        document = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "is_spreadsheet_cell", return_value=False)
        test_context.patch_object(AXUtilities, "is_document", return_value=False)
        test_context.patch_object(AXUtilities, "find_ancestor", return_value=document)
        test_context.patch_object(
            AXUtilities,
            "get_document_selected_texts",
            return_value=(False, []),
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((None, -1), (None, -1)),
        )
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            side_effect=[
                ("current text", 0, 12),
                ("previous text", 0, 13),
                ("next text", 0, 9),
            ],
        )
        test_context.patch_object(
            AXUtilities,
            "expand_eocs_in_range",
            side_effect=[
                "current text",
                "previous text",
                "next text",
            ],
        )
        script.utilities.find_previous_object.side_effect = [previous_obj, None]
        script.utilities.find_next_object.side_effect = [next_obj, None]

        assert manager.get_all_selected_text(script, obj) == (
            "previous text current text next text"
        )

    def test_get_all_selected_text_fallback_spans_non_text_widget(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test fallback expands the document range across an intervening non-text widget."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        script = test_context.Mock()
        obj = test_context.Mock(spec=Atspi.Accessible)
        document = test_context.Mock(spec=Atspi.Accessible)
        start_obj = test_context.Mock(spec=Atspi.Accessible)
        end_obj = test_context.Mock(spec=Atspi.Accessible)
        start = (start_obj, 0)
        end = (end_obj, 4)
        test_context.patch_object(AXUtilities, "is_spreadsheet_cell", return_value=False)
        test_context.patch_object(AXUtilities, "is_document", return_value=False)
        test_context.patch_object(AXUtilities, "find_ancestor", return_value=document)
        test_context.patch_object(
            AXUtilities,
            "get_document_selected_texts",
            return_value=(False, []),
        )
        get_endpoints = test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=(start, end),
        )
        expand = test_context.patch_object(
            AXUtilities,
            "expand_eocs_in_range",
            return_value="Structural navigation Intro paragraph. Save Fruit Apple Pear",
        )

        result = manager.get_all_selected_text(script, obj)

        assert result == "Structural navigation Intro paragraph. Save Fruit Apple Pear"
        get_endpoints.assert_called_once_with(None, document)
        expand.assert_called_once_with(
            start_obj,
            0,
            end_obj,
            4,
            include_start=True,
            include_end=False,
        )
        script.utilities.find_previous_object.assert_not_called()
        script.utilities.find_next_object.assert_not_called()

    @pytest.mark.parametrize(
        "obj_has_selection,cached_boundaries,expected",
        [
            pytest.param(True, None, True, id="object_reports_selected_text"),
            pytest.param(False, "recorded", True, id="root_has_recorded_boundaries"),
            pytest.param(False, None, False, id="nothing_selected"),
        ],
    )
    def test_has_known_selection(
        self,
        test_context: OrcaTestContext,
        obj_has_selection: bool,
        cached_boundaries: str | None,
        expected: bool,
    ) -> None:
        """Test reporting whether obj or its selection root has a known selection."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        boundaries_cache = test_context.Mock()
        manager._selection_boundaries = boundaries_cache
        document = test_context.Mock(spec=Atspi.Accessible)
        obj = test_context.Mock(spec=Atspi.Accessible)
        recorded = ((test_context.Mock(spec=Atspi.Accessible), 0), (document, 4))
        boundaries_cache.get.return_value = (
            recorded if cached_boundaries else ((None, -1), (None, -1))
        )
        test_context.patch_object(
            AXUtilities, "find_outermost_ancestor_inclusive", return_value=document
        )
        get_endpoints = test_context.patch_object(
            AXUtilities, "get_document_text_selection_endpoints"
        )
        test_context.patch_object(AXUtilities, "has_selected_text", return_value=obj_has_selection)

        assert manager.has_known_selection(obj) is expected
        get_endpoints.assert_not_called()

    def test_get_known_text_selection_endpoints_returns_cached_state(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test known endpoints are returned without querying the accessible application."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXUtilities,
            TextSelectionManager,
            ax_cache_manager,
        )

        manager = TextSelectionManager()
        root = test_context.Mock(spec=Atspi.Accessible)
        start = (test_context.Mock(spec=Atspi.Accessible), 2)
        end = (test_context.Mock(spec=Atspi.Accessible), 8)
        boundaries_cache = test_context.Mock()
        boundaries_cache.get.return_value = (start, end)
        manager._selection_boundaries = boundaries_cache
        test_context.patch_object(ax_cache_manager, "get_object_key", return_value="root-key")
        has_selected_text = test_context.patch_object(AXUtilities, "has_selected_text")
        get_endpoints = test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
        )

        assert manager.get_known_text_selection_endpoints(root) == (start, end)
        boundaries_cache.get.assert_called_once_with(
            "root-key",
            ((None, -1), (None, -1)),
        )
        has_selected_text.assert_not_called()
        get_endpoints.assert_not_called()

    def test_get_known_text_selection_endpoints_prefers_command_state(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test command endpoints take precedence over older cached endpoints."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXUtilities,
            TextSelectionCommand,
            TextSelectionManager,
            _TextSelectionEndpoint,
        )

        manager = TextSelectionManager()
        root = test_context.Mock(spec=Atspi.Accessible)
        anchor_obj = test_context.Mock(spec=Atspi.Accessible)
        focus_obj = test_context.Mock(spec=Atspi.Accessible)
        anchor = _TextSelectionEndpoint(anchor_obj, 8)
        focus = _TextSelectionEndpoint(focus_obj, 2)
        manager._last_selection_command = TextSelectionCommand(
            _event=test_context.Mock(),
            _objects=(anchor_obj, focus_obj),
            _selection_container=root,
            _selection_anchor=anchor,
            _selection_focus=focus,
            _pending_change=None,
            _should_notify_user=True,
        )
        boundaries_cache = test_context.Mock()
        manager._selection_boundaries = boundaries_cache
        test_context.patch_object(AXUtilities, "compare_text_positions", return_value=1)

        assert manager.get_known_text_selection_endpoints(root) == (
            (focus_obj, 2),
            (anchor_obj, 8),
        )
        boundaries_cache.get.assert_not_called()

    def test_update_selection_state_updates_boundaries(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test the manager obtains and retains document-scoped selection boundaries."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXUtilities,
            SelectionChangeState,
            TextSelectionManager,
            ax_cache_manager,
        )

        manager = TextSelectionManager()
        boundaries_cache = test_context.Mock()
        manager._selection_boundaries = boundaries_cache
        document = test_context.Mock(spec=Atspi.Accessible)
        event_source = test_context.Mock(spec=Atspi.Accessible)
        start = (test_context.Mock(spec=Atspi.Accessible), 0)
        end = (test_context.Mock(spec=Atspi.Accessible), 8)
        no_selection = ((None, -1), (None, -1))
        boundaries_cache.get.return_value = no_selection
        get_object_key = test_context.patch_object(
            ax_cache_manager,
            "get_object_key",
            return_value="root-key",
        )
        get_document = test_context.patch_object(
            AXUtilities,
            "find_outermost_ancestor_inclusive",
            return_value=document,
        )
        get_endpoints = test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=(start, end),
        )
        test_context.patch_object(AXUtilities, "has_selected_text", return_value=True)
        state, old_selection, selection = manager.update_selection_state(event_source)

        assert state == SelectionChangeState.NOT_ORCA
        assert old_selection == no_selection
        assert selection == (start, end)
        get_object_key.assert_called_once_with(document)
        get_document.assert_called_once_with(event_source, AXUtilities.is_document)
        get_endpoints.assert_called_once_with(document, document, True)
        boundaries_cache.put.assert_called_once_with("root-key", (start, end))

    @pytest.mark.parametrize(
        "obj_has_selection,cached_boundaries,expected",
        [
            pytest.param(True, None, True, id="object_reports_selected_text"),
            pytest.param(False, "recorded", True, id="root_has_recorded_boundaries"),
            pytest.param(False, None, False, id="nothing_selected"),
        ],
    )
    def test_update_selection_state_searches_text_objects_only_when_needed(
        self,
        test_context: OrcaTestContext,
        obj_has_selection: bool,
        cached_boundaries: str | None,
        expected: bool,
    ) -> None:
        """Test the manager only searches text objects if selected text might be found."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXUtilities,
            TextSelectionManager,
            ax_cache_manager,
        )

        manager = TextSelectionManager()
        boundaries_cache = test_context.Mock()
        manager._selection_boundaries = boundaries_cache
        document = test_context.Mock(spec=Atspi.Accessible)
        event_source = test_context.Mock(spec=Atspi.Accessible)
        recorded = ((test_context.Mock(spec=Atspi.Accessible), 0), (document, 4))
        boundaries_cache.get.return_value = (
            recorded if cached_boundaries else ((None, -1), (None, -1))
        )
        test_context.patch_object(ax_cache_manager, "get_object_key", return_value="root-key")
        test_context.patch_object(
            AXUtilities, "find_outermost_ancestor_inclusive", return_value=document
        )
        get_endpoints = test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((None, -1), (None, -1)),
        )
        test_context.patch_object(AXUtilities, "has_selected_text", return_value=obj_has_selection)
        test_context.patch_object(AXUtilities, "update_cached_selected_text")
        manager.update_selection_state(event_source)

        get_endpoints.assert_called_once_with(document, document, expected)

    def test_unpresentable_selection_change_updates_boundaries_and_text_caches(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test an unpresentable change updates all manager-owned selection state."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXUtilities,
            TextSelectionManager,
            ax_cache_manager,
        )

        manager = TextSelectionManager()
        boundaries_cache = test_context.Mock()
        manager._selection_boundaries = boundaries_cache
        document = test_context.Mock(spec=Atspi.Accessible)
        event_source = test_context.Mock(spec=Atspi.Accessible)
        old_obj = test_context.Mock(spec=Atspi.Accessible)
        new_obj = test_context.Mock(spec=Atspi.Accessible)
        old_selection = ((old_obj, 0), (old_obj, 4))
        selection = ((old_obj, 0), (new_obj, 8))
        boundaries_cache.get.return_value = old_selection
        test_context.patch_object(ax_cache_manager, "get_object_key", return_value="root-key")
        test_context.patch_object(
            AXUtilities,
            "find_outermost_ancestor_inclusive",
            return_value=document,
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=selection,
        )
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_elements",
            side_effect=[[old_obj], [old_obj, new_obj]],
        )
        update_cache = test_context.patch_object(AXUtilities, "update_cached_selected_text")

        manager.update_state_for_unpresentable_selection_change(event_source)

        boundaries_cache.put.assert_called_once_with("root-key", selection)
        assert update_cache.call_count == 3
        update_cache.assert_any_call(old_obj)
        update_cache.assert_any_call(new_obj)
        update_cache.assert_any_call(event_source)

    def test_intermediate_selection_change_updates_only_text_caches(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test an intermediate report preserves stable boundaries and refreshes text caches."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXUtilities,
            TextSelectionManager,
            _PendingSelectionChange,
            _TextSelectionEndpoint,
            ax_cache_manager,
            input_event_manager,
        )

        manager = TextSelectionManager()
        boundaries_cache = test_context.Mock()
        manager._selection_boundaries = boundaries_cache
        document = test_context.Mock(spec=Atspi.Accessible)
        event_source = test_context.Mock(spec=Atspi.Accessible)
        anchor_obj = test_context.Mock(spec=Atspi.Accessible)
        old_end_obj = test_context.Mock(spec=Atspi.Accessible)
        intermediate_end_obj = test_context.Mock(spec=Atspi.Accessible)
        requested_end_obj = test_context.Mock(spec=Atspi.Accessible)
        old_selection = ((anchor_obj, 0), (old_end_obj, 4))
        intermediate_selection = ((anchor_obj, 0), (intermediate_end_obj, 6))
        boundaries_cache.get.return_value = old_selection
        test_context.patch_object(ax_cache_manager, "get_object_key", return_value="root-key")
        test_context.patch_object(
            AXUtilities,
            "find_outermost_ancestor_inclusive",
            return_value=document,
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=intermediate_selection,
        )
        test_context.patch_object(AXUtilities, "compare_text_positions", return_value=-1)
        test_context.patch_object(
            AXUtilities,
            "text_selection_positions_are_equivalent",
            side_effect=[True, False],
        )
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_elements",
            side_effect=[[anchor_obj, old_end_obj], [anchor_obj, intermediate_end_obj]],
        )
        update_cache = test_context.patch_object(AXUtilities, "update_cached_selected_text")
        event = test_context.Mock()
        event.as_single_line_string.return_value = "Shift+Down"
        manager._record_selection_command(
            event,
            (event_source,),
            True,
            selection_container=document,
            selection_anchor=_TextSelectionEndpoint(anchor_obj, 0),
            selection_focus=_TextSelectionEndpoint(requested_end_obj, 8),
            pending_change=_PendingSelectionChange(
                container=document,
                anchor=_TextSelectionEndpoint(anchor_obj, 0),
                focus=_TextSelectionEndpoint(requested_end_obj, 8),
            ),
        )
        input_manager = input_event_manager.get_manager.return_value
        input_manager.last_event_equals_or_is_release_for_event.return_value = True

        manager.update_state_for_unpresentable_selection_change(event_source)

        boundaries_cache.put.assert_not_called()
        assert update_cache.call_count == 4
        update_cache.assert_any_call(anchor_obj)
        update_cache.assert_any_call(old_end_obj)
        update_cache.assert_any_call(intermediate_end_obj)
        update_cache.assert_any_call(event_source)

    def test_update_selection_state_suppresses_previous_command(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a completed change from the previous command updates state without presentation."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXUtilities,
            SelectionChangeState,
            TextSelectionManager,
            _PendingSelectionChange,
            _TextSelectionEndpoint,
            ax_cache_manager,
            input_event_manager,
        )

        manager = TextSelectionManager()
        boundaries_cache = test_context.Mock()
        manager._selection_boundaries = boundaries_cache
        document = test_context.Mock(spec=Atspi.Accessible)
        event_source = test_context.Mock(spec=Atspi.Accessible)
        start = (test_context.Mock(spec=Atspi.Accessible), 0)
        old_end = (event_source, 4)
        end = (event_source, 8)
        boundaries_cache.get.return_value = (start, old_end)
        test_context.patch_object(ax_cache_manager, "get_object_key", return_value="root-key")
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=(start, end),
        )
        test_context.patch_object(
            AXUtilities,
            "find_outermost_ancestor_inclusive",
            return_value=document,
        )
        test_context.patch_object(
            AXUtilities,
            "compare_text_positions",
            return_value=-1,
        )
        test_context.patch_object(
            AXUtilities,
            "text_selection_positions_are_equivalent",
            return_value=True,
        )
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_elements",
            side_effect=[[event_source], [event_source]],
        )
        update_cache = test_context.patch_object(
            AXUtilities,
            "update_cached_selected_text",
        )
        event = test_context.Mock()
        event.as_single_line_string.return_value = "Shift+Down"
        manager._record_selection_command(
            event,
            (event_source,),
            True,
            selection_container=document,
            selection_anchor=_TextSelectionEndpoint(start[0], start[1]),
            selection_focus=_TextSelectionEndpoint(end[0], end[1]),
            pending_change=_PendingSelectionChange(
                container=document,
                anchor=_TextSelectionEndpoint(start[0], start[1]),
                focus=_TextSelectionEndpoint(end[0], end[1]),
            ),
        )
        input_manager = input_event_manager.get_manager.return_value
        input_manager.last_event_equals_or_is_release_for_event.return_value = False

        state, old_selection, selection = manager.update_selection_state(event_source)

        assert state == SelectionChangeState.UNPRESENTABLE
        assert old_selection == (start, old_end)
        assert selection == (start, end)
        boundaries_cache.put.assert_called_once_with("root-key", (start, end))
        update_cache.assert_called_once_with(event_source)
        assert manager.get_selection_command_for_object(event_source) is None

    @pytest.mark.parametrize(
        "selection,source_offset,expected_anchor",
        [
            pytest.param(("", 0, 0), 5, 5, id="no_selection"),
            pytest.param(("abc", 3, 6), 3, 6, id="active_at_start"),
            pytest.param(("abc", 3, 6), 6, 3, id="active_at_end"),
            pytest.param(("abc", 3, 6), 7, 3, id="newline_after_reported_end"),
        ],
    )
    def test_take_snapshot_derives_opposite_anchor(
        self,
        test_context: OrcaTestContext,
        selection: tuple[str, int, int],
        source_offset: int,
        expected_anchor: int,
    ) -> None:
        """Test the snapshot uses the endpoint opposite the active endpoint as anchor."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "get_selected_text", return_value=selection)
        get_anchor_offset = test_context.patch_object(
            AXUtilities,
            "get_selection_anchor_offset",
            return_value=expected_anchor,
        )

        snapshot = manager._take_snapshot(None, obj, source_offset)

        assert snapshot.anchor.accessible_object == obj
        assert snapshot.anchor.offset == expected_anchor
        get_anchor_offset.assert_called_once_with(
            obj,
            source_offset,
            selection[1],
            selection[2],
        )

    def test_new_selection_does_not_search_container_for_endpoints(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test starting a selection avoids an unnecessary container-wide search."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        container = test_context.Mock(spec=Atspi.Accessible)
        source_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "get_selected_text", return_value=("", 0, 0))
        test_context.patch_object(AXUtilities, "has_selected_text", return_value=False)
        get_endpoints = test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
        )

        snapshot = manager._take_snapshot(container, source_obj, 0)

        assert snapshot.anchor.accessible_object == source_obj
        assert snapshot.anchor.offset == 0
        get_endpoints.assert_not_called()

    def test_continued_selection_reuses_anchor_from_previous_command(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test consecutive commands retain the original anchor across text objects."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXUtilities,
            SelectionChangeState,
            TextSelectionManager,
            input_event_manager,
        )

        manager = TextSelectionManager()
        container = test_context.Mock(spec=Atspi.Accessible)
        first_obj = test_context.Mock(spec=Atspi.Accessible)
        second_obj = test_context.Mock(spec=Atspi.Accessible)
        third_obj = test_context.Mock(spec=Atspi.Accessible)
        event = test_context.Mock()
        test_context.patch_object(AXUtilities, "get_selected_text", return_value=("", 0, 0))
        test_context.patch_object(AXUtilities, "has_selected_text", return_value=False)
        get_endpoints = test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
        )
        set_selection = test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=True,
        )
        positions = {first_obj: 0, second_obj: 1, third_obj: 2}
        test_context.patch_object(
            AXUtilities,
            "compare_text_positions",
            side_effect=lambda obj1, _offset1, obj2, _offset2: positions[obj1] - positions[obj2],
        )

        snapshot = manager._take_snapshot(container, first_obj, 0)
        assert manager._apply_selection(
            snapshot,
            second_obj,
            0,
            second_obj,
            selection_forward=True,
            event=event,
            notify_user=True,
        )

        snapshot = manager._take_snapshot(container, second_obj, 0)
        assert snapshot.anchor.accessible_object == first_obj
        assert snapshot.anchor.offset == 0
        assert manager._apply_selection(
            snapshot,
            third_obj,
            0,
            third_obj,
            selection_forward=True,
            event=event,
            notify_user=True,
        )

        assert set_selection.call_args_list == [
            call(container, first_obj, 0, second_obj, 0),
            call(container, first_obj, 0, third_obj, 0),
        ]
        get_endpoints.assert_not_called()

        input_manager = input_event_manager.get_manager.return_value
        input_manager.last_event_equals_or_is_release_for_event.return_value = False
        assert manager.get_selection_command_for_object(container) is not None
        no_endpoint = (None, -1)
        assert manager._get_selection_change_state(
            container,
            (no_endpoint, no_endpoint),
        ) == (SelectionChangeState.NOT_ORCA, True)
        snapshot = manager._take_snapshot(container, third_obj, 0)
        assert snapshot.anchor.accessible_object == third_obj

    def test_continued_selection_does_not_reuse_invalid_anchor(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a defunct retained anchor is replaced by the current focus position."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXObject,
            AXUtilities,
            TextSelectionManager,
            _TextSelectionEndpoint,
        )

        manager = TextSelectionManager()
        container = test_context.Mock(spec=Atspi.Accessible)
        invalid_anchor_obj = test_context.Mock(spec=Atspi.Accessible)
        focus_obj = test_context.Mock(spec=Atspi.Accessible)
        event = test_context.Mock()
        manager._record_selection_command(
            event,
            (focus_obj,),
            True,
            selection_container=container,
            selection_anchor=_TextSelectionEndpoint(invalid_anchor_obj, 2),
            selection_focus=None,
            pending_change=None,
        )
        test_context.patch_object(
            AXObject,
            "is_valid",
            side_effect=lambda obj: obj != invalid_anchor_obj,
        )
        test_context.patch_object(AXUtilities, "get_selected_text", return_value=("", 0, 0))
        test_context.patch_object(AXUtilities, "get_selection_anchor_offset", return_value=4)
        test_context.patch_object(AXUtilities, "has_selected_text", return_value=False)

        snapshot = manager._take_snapshot(container, focus_obj, 4)

        assert snapshot.anchor.accessible_object == focus_obj
        assert snapshot.anchor.offset == 4

    @pytest.mark.parametrize(
        "selection,source_offset,active_offset,expected_range",
        [
            pytest.param(("", 0, 0), 5, 6, (5, 6), id="starts_selection"),
            pytest.param(("abc", 3, 6), 6, 5, (3, 5), id="shrinks_from_end"),
            pytest.param(("abc", 3, 6), 3, 4, (4, 6), id="shrinks_from_start"),
            pytest.param(("abc", 3, 6), 6, 3, None, id="collapses_selection"),
        ],
    )
    def test_apply_selection_within_text_object(
        self,
        test_context: OrcaTestContext,
        selection: tuple[str, int, int],
        source_offset: int,
        active_offset: int,
        expected_range: tuple[int, int] | None,
    ) -> None:
        """Test extending or retracting a selection within one text object."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "get_selected_text", return_value=selection)
        expected_anchor = source_offset
        if selection[1] != selection[2]:
            expected_anchor = selection[1] if source_offset == selection[2] else selection[2]
        test_context.patch_object(
            AXUtilities,
            "get_selection_anchor_offset",
            return_value=expected_anchor,
        )
        set_selected_text = test_context.patch_object(AXUtilities, "set_selected_text")
        clear_selected_text = test_context.patch_object(
            AXUtilities,
            "clear_all_selected_text",
        )
        snapshot = manager._take_snapshot(None, obj, source_offset)

        assert manager._apply_selection(
            snapshot,
            obj,
            active_offset,
            obj,
            selection_forward=True,
            event=None,
            notify_user=True,
        )

        if expected_range is None:
            set_selected_text.assert_not_called()
            clear_selected_text.assert_called_once_with(obj)
        else:
            set_selected_text.assert_called_once_with(obj, *expected_range)
            clear_selected_text.assert_not_called()

    def test_failed_text_object_selection_is_not_recorded(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a failed AtspiText operation fails the command without retaining its anchor."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        obj = test_context.Mock(spec=Atspi.Accessible)
        event = test_context.Mock()
        test_context.patch_object(AXUtilities, "get_selected_text", return_value=("", 0, 0))
        test_context.patch_object(
            AXUtilities,
            "get_selection_anchor_offset",
            return_value=5,
        )
        test_context.patch_object(AXUtilities, "set_selected_text", return_value=False)
        snapshot = manager._take_snapshot(None, obj, 5)

        assert not manager._apply_selection(
            snapshot,
            obj,
            6,
            obj,
            selection_forward=True,
            event=event,
            notify_user=True,
        )
        assert manager.get_current_selection_command() is None

    def test_apply_selection_uses_document_interface_and_reported_anchor(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test document selection uses the endpoint opposite the reported active endpoint."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXUtilities,
            SelectionChangeState,
            TextSelectionManager,
        )

        manager = TextSelectionManager()
        event = test_context.Mock()
        document = test_context.Mock(spec=Atspi.Accessible)
        anchor_obj = test_context.Mock(spec=Atspi.Accessible)
        source_obj = test_context.Mock(spec=Atspi.Accessible)
        active_obj = test_context.Mock(spec=Atspi.Accessible)
        active_context_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("selection", 0, 10),
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((anchor_obj, 2), (source_obj, 10)),
        )
        test_context.patch_object(
            AXUtilities,
            "get_selection_anchor_offset",
            return_value=0,
        )
        set_document_selection = test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=True,
        )
        positions = {
            (anchor_obj, 2): 0,
            (active_obj, 4): 1,
            (active_obj, 5): 2,
        }
        test_context.patch_object(
            AXUtilities,
            "compare_text_positions",
            side_effect=lambda obj1, offset1, obj2, offset2: (
                positions[(obj1, offset1)] - positions[(obj2, offset2)]
            ),
        )
        test_context.patch_object(
            AXUtilities,
            "text_selection_positions_are_equivalent",
            side_effect=lambda obj1, offset1, obj2, offset2: (obj1, offset1) == (obj2, offset2),
        )
        snapshot = manager._take_snapshot(document, source_obj, 10)

        assert manager._apply_selection(
            snapshot,
            active_obj,
            5,
            active_context_obj,
            selection_forward=True,
            event=event,
            notify_user=False,
        )

        set_document_selection.assert_called_once_with(
            document,
            anchor_obj,
            2,
            active_obj,
            5,
        )
        assert manager.get_current_selection_command(document) is not None
        no_endpoint = (None, -1)
        assert manager._get_selection_change_state(
            document,
            ((anchor_obj, 2), (active_obj, 4)),
        ) == (SelectionChangeState.UNPRESENTABLE, False)
        assert manager._get_selection_change_state(
            document,
            (no_endpoint, no_endpoint),
        ) == (SelectionChangeState.UNPRESENTABLE, False)
        assert manager._get_selection_change_state(
            document,
            ((anchor_obj, 2), (active_obj, 5)),
        ) == (SelectionChangeState.PRESENTABLE, True)

        assert manager._apply_selection(
            snapshot,
            active_obj,
            4,
            active_context_obj,
            selection_forward=False,
            event=event,
            notify_user=True,
        )
        assert manager._get_selection_change_state(
            document,
            ((anchor_obj, 2), (active_obj, 4)),
        ) == (SelectionChangeState.PRESENTABLE, True)

        assert manager._apply_selection(
            snapshot,
            anchor_obj,
            2,
            active_context_obj,
            selection_forward=False,
            event=event,
            notify_user=True,
        )
        assert manager._get_selection_change_state(
            document,
            ((anchor_obj, 2), (active_obj, 4)),
        ) == (SelectionChangeState.UNPRESENTABLE, False)
        assert manager._get_selection_change_state(
            document,
            (no_endpoint, no_endpoint),
        ) == (SelectionChangeState.PRESENTABLE, True)

    @pytest.mark.parametrize(
        "selection_forward,source_offset,source_count,source_selection,expected_range",
        [
            pytest.param(
                True,
                81,
                89,
                ("Selected through previous line", 0, 80),
                (0, 89),
                id="forward",
            ),
            pytest.param(
                False,
                12,
                51,
                ("Selected after first line", 12, 51),
                (0, 51),
                id="backward",
            ),
        ],
    )
    def test_cross_object_fallback_completes_source_object(
        self,
        test_context: OrcaTestContext,
        selection_forward: bool,
        source_offset: int,
        source_count: int,
        source_selection: tuple[str, int, int],
        expected_range: tuple[int, int],
    ) -> None:
        """Test cross-object fallback includes the rest of the source object."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXText, AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        document = test_context.Mock(spec=Atspi.Accessible)
        source_obj = test_context.Mock(spec=Atspi.Accessible)
        active_obj = test_context.Mock(spec=Atspi.Accessible)
        completed_selection = ("completed source", *expected_range)
        empty_selection = ("", 0, 0)
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            side_effect=[
                source_selection,
                empty_selection,
                completed_selection,
                completed_selection,
                empty_selection,
            ],
        )
        test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=False,
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((None, -1), (None, -1)),
        )
        test_context.patch_object(
            AXUtilities,
            "get_selection_anchor_offset",
            return_value=0 if selection_forward else source_count,
        )
        set_selected_text = test_context.patch_object(
            AXUtilities,
            "set_selected_text",
            return_value=True,
        )
        clear_selected_text = test_context.patch_object(
            AXUtilities,
            "clear_all_selected_text",
        )
        test_context.patch_object(
            AXText,
            "get_character_count",
            side_effect=lambda obj: source_count if obj == source_obj else 20,
        )
        snapshot = manager._take_snapshot(document, source_obj, source_offset)

        assert manager._apply_selection(
            snapshot,
            active_obj,
            0 if selection_forward else 20,
            active_obj,
            selection_forward=selection_forward,
            event=None,
            notify_user=True,
        )

        set_selected_text.assert_called_once_with(source_obj, *expected_range)
        clear_selected_text.assert_called_once_with(active_obj)

    @pytest.mark.parametrize(
        "selection_forward,anchor_offset,expected_range",
        [
            pytest.param(True, 7, (7, 10), id="forward_past_backward_selection_anchor"),
            pytest.param(False, 3, (0, 3), id="backward_past_forward_selection_anchor"),
        ],
    )
    def test_source_range_when_selection_crosses_anchor(
        self,
        test_context: OrcaTestContext,
        selection_forward: bool,
        anchor_offset: int,
        expected_range: tuple[int, int],
    ) -> None:
        """Test crossing objects retains the range from the anchor to the source edge."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            TextSelectionManager,
            _TextSelectionEndpoint,
            _TextSelectionSnapshot,
        )

        obj = test_context.Mock(spec=Atspi.Accessible)
        focus_offset = 3 if selection_forward else 7
        snapshot = _TextSelectionSnapshot(
            None,
            _TextSelectionEndpoint(obj, focus_offset),
            3,
            7,
            _TextSelectionEndpoint(obj, anchor_offset),
        )

        assert (
            TextSelectionManager._get_selection_range_for_source_object(
                snapshot,
                selection_forward,
                10,
            )
            == expected_range
        )

    @pytest.mark.parametrize(
        "selection_forward,active_offset,active_selection,active_count,expected_range",
        [
            pytest.param(False, 12, ("", 0, 0), 20, (12, 20), id="backward_adds_tail"),
            pytest.param(
                False,
                81,
                ("whole first page", 0, 89),
                89,
                (0, 81),
                id="backward_shrinks_head",
            ),
            pytest.param(
                True,
                8,
                ("whole second page", 0, 20),
                20,
                (8, 20),
                id="forward_shrinks_tail",
            ),
        ],
    )
    def test_cross_object_fallback_updates_active_object(
        self,
        test_context: OrcaTestContext,
        selection_forward: bool,
        active_offset: int,
        active_selection: tuple[str, int, int],
        active_count: int,
        expected_range: tuple[int, int],
    ) -> None:
        """Test cross-object fallback adds or shrinks the active object's range."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXText, AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        source_obj = test_context.Mock(spec=Atspi.Accessible)
        active_obj = test_context.Mock(spec=Atspi.Accessible)
        empty_selection = ("", 0, 0)
        expected_selection = ("remaining", *expected_range)
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            side_effect=[
                empty_selection,
                active_selection,
                empty_selection,
                empty_selection,
                expected_selection,
            ],
        )
        test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=False,
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((None, -1), (None, -1)),
        )
        test_context.patch_object(AXUtilities, "has_selected_text", return_value=False)
        set_selected_text = test_context.patch_object(
            AXUtilities,
            "set_selected_text",
            return_value=True,
        )
        test_context.patch_object(AXText, "get_character_count", return_value=active_count)
        source_offset = 0 if not selection_forward else active_count
        snapshot = manager._take_snapshot(test_context.Mock(), source_obj, source_offset)

        assert manager._apply_selection(
            snapshot,
            active_obj,
            active_offset,
            active_obj,
            selection_forward=selection_forward,
            event=None,
            notify_user=True,
        )

        set_selected_text.assert_called_once_with(active_obj, *expected_range)

    @pytest.mark.parametrize(
        "operation_results,expected_calls",
        [
            pytest.param(
                [False, True],
                [("source", 2, 10), ("source", 2, 4)],
                id="source_failure",
            ),
            pytest.param(
                [True, False, True, True],
                [
                    ("source", 2, 10),
                    ("destination", 0, 5),
                    ("destination", 0, 0),
                    ("source", 2, 4),
                ],
                id="destination_failure",
            ),
        ],
    )
    def test_cross_object_failure_restores_previous_selection(
        self,
        test_context: OrcaTestContext,
        operation_results: list[bool],
        expected_calls: list[tuple[str, int, int]],
    ) -> None:
        """Test a partially applied cross-object selection is rolled back."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import (
            AXText,
            AXUtilities,
            TextSelectionManager,
            _TextSelectionEndpoint,
            _TextSelectionSnapshot,
        )

        manager = TextSelectionManager()
        source_obj = test_context.Mock(spec=Atspi.Accessible)
        destination_obj = test_context.Mock(spec=Atspi.Accessible)
        snapshot = _TextSelectionSnapshot(
            None,
            _TextSelectionEndpoint(source_obj, 4),
            2,
            4,
            _TextSelectionEndpoint(source_obj, 2),
        )
        set_selection = test_context.patch_object(
            manager,
            "_set_text_object_selection",
            side_effect=operation_results,
        )
        test_context.patch_object(AXUtilities, "get_selected_text", return_value=("", 0, 0))
        test_context.patch_object(AXText, "get_character_count", return_value=10)

        result = manager._apply_selection_across_text_objects(
            snapshot,
            _TextSelectionEndpoint(destination_obj, 5),
            destination_obj,
            True,
        )

        assert not result.succeeded
        names = {source_obj: "source", destination_obj: "destination"}
        calls = [(names[call.args[0]], *call.args[1:]) for call in set_selection.call_args_list]
        assert calls == expected_calls

    def test_same_object_fallback_maps_reported_cross_object_anchor(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test fallback retraction maps a reported cross-object anchor into the active object."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXText, AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        document = test_context.Mock(spec=Atspi.Accessible)
        page1 = test_context.Mock(spec=Atspi.Accessible)
        page2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("whole second page", 0, 52),
        )
        test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=False,
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((page1, 0), (page2, 50)),
        )
        test_context.patch_object(
            AXUtilities,
            "get_selection_anchor_offset",
            return_value=51,
        )
        test_context.patch_object(
            AXUtilities,
            "text_selection_positions_are_equivalent",
            side_effect=[False, True],
        )
        test_context.patch_object(AXText, "get_character_count", return_value=51)
        set_selected_text = test_context.patch_object(
            AXUtilities,
            "set_selected_text",
            return_value=True,
        )
        snapshot = manager._take_snapshot(document, page2, 51)

        assert manager._apply_selection(
            snapshot,
            page2,
            31,
            page2,
            selection_forward=False,
            event=None,
            notify_user=True,
        )

        set_selected_text.assert_called_once_with(page2, 0, 31)

    def test_clear_selection_for_navigation_clears_other_selected_objects(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test ordinary navigation clears every selected object under the root."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXObject, AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        root = test_context.Mock(spec=Atspi.Accessible)
        destination = test_context.Mock(spec=Atspi.Accessible)
        other_page = test_context.Mock(spec=Atspi.Accessible)
        manager._selection_boundaries = test_context.Mock()
        manager._selection_boundaries.get.return_value = ((other_page, 0), (other_page, 4))
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_container",
            return_value=other_page,
        )
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_elements",
            return_value=[other_page],
        )
        test_context.patch_object(
            AXUtilities,
            "has_selected_text",
            side_effect=lambda obj: obj is other_page,
        )
        clear_selected_text = test_context.patch_object(
            AXUtilities,
            "clear_all_selected_text",
        )
        update_cached_selected_text = test_context.patch_object(
            AXUtilities,
            "update_cached_selected_text",
        )
        get_text_descendants = test_context.patch_object(
            AXUtilities,
            "get_text_descendants",
        )

        affected = manager.clear_selection_for_navigation(root, destination)

        assert affected == [other_page]
        clear_selected_text.assert_called_once_with(other_page)
        update_cached_selected_text.assert_called_once_with(other_page)
        get_text_descendants.assert_not_called()

    def test_clear_selection_for_navigation_finds_preexisting_selection(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test ordinary navigation finds selection which Orca did not create."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXObject, AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        root = test_context.Mock(spec=Atspi.Accessible)
        selected_obj = test_context.Mock(spec=Atspi.Accessible)
        destination = selected_obj
        manager._selection_boundaries = None
        endpoint = selected_obj, 4
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=(endpoint, endpoint),
        )
        test_context.patch_object(
            AXUtilities,
            "has_selected_text",
            side_effect=lambda obj: obj is selected_obj,
        )
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_container",
            return_value=selected_obj,
        )
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_elements",
            return_value=[selected_obj],
        )
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        clear_selected_text = test_context.patch_object(
            AXUtilities,
            "clear_all_selected_text",
        )
        update_cached_selected_text = test_context.patch_object(
            AXUtilities,
            "update_cached_selected_text",
        )

        assert manager.clear_selection_for_navigation(root, destination) == [selected_obj]
        clear_selected_text.assert_called_once_with(selected_obj)
        update_cached_selected_text.assert_called_once_with(selected_obj)

    def test_clear_selection_for_navigation_skips_search_without_known_selection(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test ordinary navigation avoids a document walk when no selection is known."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        manager._selection_boundaries = None
        root = test_context.Mock(spec=Atspi.Accessible)
        destination = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "has_selected_text", return_value=False)
        get_endpoints = test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
        )
        clear_selected_text = test_context.patch_object(
            AXUtilities,
            "clear_all_selected_text",
        )

        assert manager.clear_selection_for_navigation(root, destination) == []
        get_endpoints.assert_not_called()
        clear_selected_text.assert_not_called()

    def test_current_selection_command_matches_objects_and_container(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test matching a current selection command by affected object or container."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        document = test_context.Mock(spec=Atspi.Accessible)
        descendant = test_context.Mock(spec=Atspi.Accessible)
        unrelated = test_context.Mock(spec=Atspi.Accessible)
        event = test_context.Mock()
        event.as_single_line_string.return_value = "Shift+Down"
        input_manager = test_context.Mock()
        input_manager.last_event_equals_or_is_release_for_event.return_value = True
        from orca.text_selection_manager import input_event_manager

        input_event_manager.get_manager.return_value = input_manager
        test_context.patch_object(
            AXUtilities,
            "is_ancestor",
            side_effect=lambda obj, ancestor, inclusive=False: (
                (obj is descendant and ancestor is document) or (inclusive and obj is ancestor)
            ),
        )

        assert manager.get_current_selection_command(document) is None

        manager._record_selection_command(
            event,
            (descendant,),
            True,
            selection_container=document,
            selection_anchor=None,
            selection_focus=None,
            pending_change=None,
        )

        command = manager.get_current_selection_command(document)
        assert command is not None
        assert manager.get_current_selection_command(descendant) == command
        assert manager.get_current_selection_command(unrelated) is None

    def test_get_current_selection_command(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test recognizing the input event used by the last selection command."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import TextSelectionManager, input_event_manager

        manager = TextSelectionManager()
        obj = test_context.Mock(spec=Atspi.Accessible)
        other_obj = test_context.Mock(spec=Atspi.Accessible)
        event = test_context.Mock()
        event.as_single_line_string.return_value = "Shift+Down"
        manager._record_selection_command(
            event,
            (obj, other_obj),
            False,
            selection_container=None,
            selection_anchor=None,
            selection_focus=None,
            pending_change=None,
        )
        input_manager = input_event_manager.get_manager.return_value
        input_manager.last_event_equals_or_is_release_for_event.return_value = True

        assert manager.get_current_selection_command(test_context.Mock()) is None
        command = manager.get_current_selection_command(obj)
        assert command is not None
        assert command.get_objects() == (obj, other_obj)
        assert command.should_notify_user() is False
        assert manager.get_current_selection_command(other_obj) == command
        assert manager.get_current_selection_command() == command
        input_manager.last_event_equals_or_is_release_for_event.assert_called_with(event)

        input_manager.last_event_equals_or_is_release_for_event.return_value = False
        assert manager.get_current_selection_command() is None

    def test_selection_change_from_native_selection_command(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test native selection input identifies its reported selection change."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import TextSelectionManager, input_event_manager

        manager = TextSelectionManager()
        input_manager = input_event_manager.get_manager.return_value
        input_manager.last_event_was_caret_selection.return_value = True

        assert manager.is_selection_change_from_selection_command(None)

    def test_selection_change_from_orca_selection_command(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test an Orca selection command identifies its reported selection change."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import TextSelectionManager, input_event_manager

        manager = TextSelectionManager()
        obj = test_context.Mock(spec=Atspi.Accessible)
        event = test_context.Mock()
        event.as_single_line_string.return_value = "Shift+Down"
        manager._record_selection_command(
            event,
            (obj,),
            True,
            selection_container=None,
            selection_anchor=None,
            selection_focus=None,
            pending_change=None,
        )
        input_manager = input_event_manager.get_manager.return_value
        input_manager.last_event_was_caret_selection.return_value = False
        input_manager.last_event_equals_or_is_release_for_event.return_value = True

        assert manager.is_selection_change_from_selection_command(obj)

    def test_deferred_page_change_is_tied_to_selection_command(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a page change is consumed by the selection command which caused it."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import TextSelectionManager, input_event_manager

        manager = TextSelectionManager()
        obj = test_context.Mock(spec=Atspi.Accessible)
        event = test_context.Mock()
        event.as_single_line_string.return_value = "Shift+Down"
        manager._record_selection_command(
            event,
            (obj,),
            True,
            selection_container=None,
            selection_anchor=None,
            selection_focus=None,
            pending_change=None,
        )
        input_manager = input_event_manager.get_manager.return_value
        input_manager.last_event_equals_or_is_release_for_event.return_value = True

        assert manager.defer_page_change_for_current_selection(2)
        assert manager.take_deferred_page_change_for_selection(obj) == 2
        assert manager.take_deferred_page_change_for_selection(obj) is None

    def test_new_selection_command_discards_deferred_page_change(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a page change is not retained after its selection command is replaced."""

        self._setup_dependencies(test_context)
        from orca.text_selection_manager import TextSelectionManager, input_event_manager

        manager = TextSelectionManager()
        obj = test_context.Mock(spec=Atspi.Accessible)
        first_event = test_context.Mock()
        first_event.as_single_line_string.return_value = "Shift+Down"
        second_event = test_context.Mock()
        second_event.as_single_line_string.return_value = "Shift+Up"
        input_manager = input_event_manager.get_manager.return_value
        input_manager.last_event_equals_or_is_release_for_event.return_value = True
        manager._record_selection_command(
            first_event,
            (obj,),
            True,
            selection_container=None,
            selection_anchor=None,
            selection_focus=None,
            pending_change=None,
        )
        assert manager.defer_page_change_for_current_selection(2)

        manager._record_selection_command(
            second_event,
            (obj,),
            True,
            selection_container=None,
            selection_anchor=None,
            selection_focus=None,
            pending_change=None,
        )

        assert manager.take_deferred_page_change_for_selection(obj) is None
