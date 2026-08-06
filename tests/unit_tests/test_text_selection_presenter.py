# Unit tests for text_selection_presenter.py methods.
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

# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access
# pylint: disable=wrong-import-position

"""Unit tests for text_selection_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestTextSelectionPresenter:
    """Test TextSelectionPresenter methods."""

    @staticmethod
    def _setup_dependencies(test_context: OrcaTestContext) -> None:
        additional_modules = [
            "orca.document_presenter",
            "orca.input_event_manager",
            "orca.presentation_manager",
            "orca.speech_presenter",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    def test_newly_selected_text_is_cached_and_presented(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test extending a selection updates its cache and presents the new text."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXObject,
            AXText,
            AXUtilities,
            TextSelectionPresenter,
            input_event_manager,
            messages,
            presentation_manager,
            speech_presenter,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        obj = test_context.Mock()
        test_context.patch_object(AXUtilities, "is_web_element", return_value=False)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(
            AXUtilities,
            "get_cached_selected_text",
            side_effect=[("a", 0, 1), ("ab", 0, 2)],
        )
        update_cache = test_context.patch_object(AXUtilities, "update_cached_selected_text")
        test_context.patch_object(AXText, "get_substring", return_value="b")
        manager = input_event_manager.get_manager.return_value
        manager.last_event_was_cut.return_value = False
        manager.last_event_was_select_all.return_value = False
        manager.last_event_was_caret_selection.return_value = True
        speech_presenter.get_presenter.return_value.get_only_speak_displayed_text.return_value = (
            False
        )

        assert presenter.handle_text_selection_change(script, obj)
        update_cache.assert_called_once_with(obj)
        script.say_phrase.assert_called_once_with(obj, 1, 2)
        presentation_manager.get_manager.return_value.speak_message.assert_called_once_with(
            messages.TEXT_SELECTED
        )

    @pytest.mark.parametrize("destination_handles_change", [False, True])
    def test_preceding_child_change_has_exactly_one_selection_state(
        self,
        test_context: OrcaTestContext,
        destination_handles_change: bool,
    ) -> None:
        """Test a grouped child change gets a state when the destination does not provide one."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXText,
            AXUtilities,
            TextSelectionPresenter,
            messages,
            presentation_manager,
            speech_presenter,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        obj = test_context.Mock()
        child = test_context.Mock()
        test_context.patch_object(AXText, "get_substring", return_value="\ufffc")
        test_context.patch_object(AXUtilities, "find_child_at_offset", return_value=child)
        handle_child = test_context.patch_object(
            presenter,
            "_handle_basic_change",
            return_value=destination_handles_change,
        )
        speech_presenter.get_presenter.return_value.get_only_speak_displayed_text.return_value = (
            False
        )

        presenter._present_changes(
            script,
            obj,
            [[0, 1, messages.TEXT_SELECTED]],
            True,
            True,
        )

        handle_child.assert_called_once_with(script, child, True)
        manager = presentation_manager.get_manager.return_value
        if destination_handles_change:
            manager.speak_message.assert_not_called()
        else:
            manager.speak_message.assert_called_once_with(messages.TEXT_SELECTED)

    def test_removed_selection_is_cached_and_reported_as_unhandled(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test clearing a selection updates its cache while allowing caret presentation."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXObject,
            AXUtilities,
            TextSelectionPresenter,
            input_event_manager,
            messages,
            presentation_manager,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        obj = test_context.Mock()
        test_context.patch_object(AXUtilities, "is_web_element", return_value=False)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(
            AXUtilities,
            "get_cached_selected_text",
            side_effect=[("selected", 0, 8), ("", 0, 0)],
        )
        update_cache = test_context.patch_object(AXUtilities, "update_cached_selected_text")
        manager = input_event_manager.get_manager.return_value
        manager.last_event_was_cut.return_value = False
        manager.last_event_was_select_all.return_value = False
        manager.last_event_was_caret_selection.return_value = False

        assert not presenter.handle_text_selection_change(script, obj)
        update_cache.assert_called_once_with(obj)
        presentation_manager.get_manager.return_value.speak_message.assert_called_once_with(
            messages.SELECTION_REMOVED
        )
        script.say_phrase.assert_not_called()

    def test_document_selection_boundaries_resolve_embedded_children(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test document selection boundaries descend through embedded-object characters."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import AXObject, AXUtilities, TextSelectionPresenter

        presenter = TextSelectionPresenter()
        root = test_context.Mock()
        start = test_context.Mock()
        end = test_context.Mock()
        strings = {root: "\ufffc", start: "start", end: "end"}
        children = {(root, 0): start, (root, 1): end}
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            side_effect=lambda obj: (strings[obj], 0, len(strings[obj])),
        )
        test_context.patch_object(
            AXObject,
            "get_child_count",
            side_effect=lambda obj: 2 if obj == root else 0,
        )
        test_context.patch_object(
            AXObject,
            "get_child",
            side_effect=lambda obj, index: children.get((obj, index)),
        )

        assert presenter._get_document_selection_boundaries(root) == (start, end)

    def test_document_selection_updates_nested_cache_without_presenting_it(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test nested document elements are cached while selection boundaries are presented."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXObject,
            AXUtilities,
            TextSelectionPresenter,
            document_presenter,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        root = test_context.Mock()
        start = test_context.Mock()
        nested = test_context.Mock()
        end = test_context.Mock()
        test_context.patch_object(AXUtilities, "is_web_element", return_value=True)
        script.utilities.in_document_content.return_value = True
        document_presenter.get_presenter.return_value.in_focus_mode.return_value = False
        test_context.patch_object(
            presenter,
            "_get_document_selection_boundaries",
            return_value=(start, end),
        )
        test_context.patch_object(
            presenter,
            "_get_document_selection_elements",
            side_effect=[[], [start, nested, end]],
        )
        paths = {start: [0], nested: [1], end: [2]}
        test_context.patch_object(AXObject, "get_path", side_effect=paths.get)
        test_context.patch_object(
            AXUtilities,
            "path_comparison",
            side_effect=lambda path1, path2: (path1 > path2) - (path1 < path2),
        )
        test_context.patch_object(
            AXUtilities,
            "find_ancestor",
            side_effect=lambda obj, _predicate: start if obj == nested else None,
        )
        update_cache = test_context.patch_object(AXUtilities, "update_cached_selected_text")
        handle_basic = test_context.patch_object(
            presenter,
            "_handle_basic_change",
            return_value=True,
        )

        assert presenter.handle_text_selection_change(script, root)
        assert presenter._get_cached_document_selection_boundaries(script) == (start, end)
        assert [call.args for call in handle_basic.call_args_list] == [
            (script, start, True),
            (script, end, True),
        ]
        update_cache.assert_called_once_with(nested)

    def test_document_selection_elements_stop_after_end_boundary(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test document elements include nested boundaries without continuing past them."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import AXObject, AXUtilities, TextSelectionPresenter

        parent = test_context.Mock()
        start = test_context.Mock()
        start_child = test_context.Mock()
        end_container = test_context.Mock()
        end = test_context.Mock()
        following_end = test_context.Mock()
        following_container = test_context.Mock()
        children = {
            (parent, 0): start,
            (parent, 1): end_container,
            (parent, 2): following_container,
            (end_container, 1): following_end,
        }
        parents = {start: parent, end: end_container}
        indices = {start: 0, end: 0}
        descendants = {
            start: [start_child],
            end_container: [end, following_end],
        }
        test_context.patch_object(AXObject, "is_dead", return_value=False)
        test_context.patch_object(AXObject, "get_parent", side_effect=parents.get)
        test_context.patch_object(AXObject, "get_index_in_parent", side_effect=indices.get)
        test_context.patch_object(
            AXObject,
            "get_child_count",
            side_effect=lambda obj: 3 if obj == parent else 2,
        )
        test_context.patch_object(
            AXObject,
            "get_child",
            side_effect=lambda obj, index: children.get((obj, index)),
        )
        test_context.patch_object(AXUtilities, "is_web_element", return_value=True)
        test_context.patch_object(AXUtilities, "is_code", return_value=False)
        test_context.patch_object(
            AXUtilities,
            "find_all_descendants",
            side_effect=lambda obj, _include, _exclude: descendants.get(obj, []),
        )

        assert TextSelectionPresenter._get_document_selection_elements(start, end) == [
            start,
            start_child,
            end_container,
            end,
        ]
