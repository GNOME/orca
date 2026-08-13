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
    def _setup_dependencies(test_context: OrcaTestContext):
        additional_modules = [
            "orca.document_presenter",
            "orca.input_event_manager",
            "orca.presentation_manager",
            "orca.speech_presenter",
            "orca.text_selection_manager",
        ]
        return test_context.setup_shared_dependencies(additional_modules)

    def test_present_selected_text(self, test_context: OrcaTestContext) -> None:
        """Test presenting all text returned by the text-selection manager."""

        dependencies = self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            TextSelectionPresenter,
            messages,
            presentation_manager,
            speech_presenter,
        )

        script = test_context.Mock()
        obj = test_context.Mock()
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.get_all_selected_text.return_value = "selected text"
        speech_manager = speech_presenter.get_presenter.return_value
        speech_manager.get_indentation_description.return_value = "indent: 2"
        speech_manager.adjust_for_presentation.return_value = "processed selected text"
        messages.SELECTED_TEXT_IS = "Selected text is %s"

        assert TextSelectionPresenter().present_selected_text(script, obj)
        selection_manager.get_all_selected_text.assert_called_once_with(script, obj)
        speech_manager.get_indentation_description.assert_called_once_with(
            "selected text",
            only_if_changed=False,
        )
        speech_manager.adjust_for_presentation.assert_called_once_with(obj, "selected text")
        presentation_manager.get_manager.return_value.speak_message.assert_called_once_with(
            "Selected text is indent: 2 processed selected text"
        )

    def test_present_selected_text_when_nothing_is_selected(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test presenting selected text reports when no selection exists."""

        dependencies = self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            TextSelectionPresenter,
            messages,
            presentation_manager,
        )

        script = test_context.Mock()
        obj = test_context.Mock()
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.get_all_selected_text.return_value = ""
        messages.NO_SELECTED_TEXT = "No selected text"

        assert TextSelectionPresenter().present_selected_text(script, obj)
        presentation_manager.get_manager.return_value.speak_message.assert_called_once_with(
            "No selected text"
        )

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

    def test_document_text_change_is_presented_as_single_phrase(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a multi-object document change has one selection-state announcement."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXUtilities,
            TextSelectionPresenter,
            input_event_manager,
            messages,
            presentation_manager,
            speech_presenter,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        start_obj = test_context.Mock()
        end_obj = test_context.Mock()
        old_start = (start_obj, 10)
        old_end = (start_obj, 10)
        start = old_start
        end = (end_obj, 1)
        input_event_manager.get_manager.return_value.last_event_was_caret_selection.return_value = (
            True
        )
        speech_presenter.get_presenter.return_value.get_only_speak_displayed_text.return_value = (
            False
        )
        test_context.patch_object(
            presenter,
            "_get_document_text_change",
            return_value=(old_end, end, True, False, messages.TEXT_SELECTED),
        )
        expand = test_context.patch_object(
            AXUtilities,
            "expand_eocs_in_range",
            return_value=" next item,",
        )

        assert presenter._present_document_text_change(
            script,
            old_start,
            old_end,
            start,
            end,
            True,
        )

        expand.assert_called_once_with(
            start_obj,
            10,
            end_obj,
            1,
            include_start=True,
            include_end=False,
        )
        speech_presenter.get_presenter.return_value.speak_phrase.assert_called_once_with(
            script,
            start_obj,
            10,
            11,
            "next item,",
        )
        presentation_manager.get_manager.return_value.speak_message.assert_called_once_with(
            messages.TEXT_SELECTED
        )

    def test_document_text_change_identifies_changed_endpoint_range(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test extending and shrinking either endpoint identifies only the changed range."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import TextSelectionPresenter, messages

        presenter = TextSelectionPresenter()
        obj = test_context.Mock()
        no_selection = (None, -1)
        old_start = (obj, 2)
        old_end = (obj, 5)

        assert presenter._get_document_text_change(
            no_selection,
            no_selection,
            old_start,
            old_end,
        ) == (old_start, old_end, True, False, messages.TEXT_SELECTED)
        assert presenter._get_document_text_change(
            old_start,
            old_end,
            no_selection,
            no_selection,
        ) == (old_start, old_end, True, False, messages.TEXT_UNSELECTED)
        assert presenter._get_document_text_change(
            old_start,
            old_end,
            old_start,
            (obj, 8),
        ) == (old_end, (obj, 8), True, False, messages.TEXT_SELECTED)
        assert presenter._get_document_text_change(
            old_start,
            old_end,
            old_start,
            (obj, 3),
        ) == ((obj, 3), old_end, True, False, messages.TEXT_UNSELECTED)
        assert presenter._get_document_text_change(
            old_start,
            old_end,
            (obj, 0),
            old_end,
        ) == ((obj, 0), old_start, True, False, messages.TEXT_SELECTED)
        assert presenter._get_document_text_change(
            old_start,
            old_end,
            (obj, 4),
            old_end,
        ) == (old_start, (obj, 4), True, False, messages.TEXT_UNSELECTED)
        assert (
            presenter._get_document_text_change(
                old_start,
                old_end,
                (obj, 0),
                (obj, 8),
            )
            is None
        )

    def test_document_selection_change_uses_endpoint_range(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test one endpoint-range presentation replaces per-element presentation."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import AXUtilities, TextSelectionPresenter

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        document = test_context.Mock()
        event_source = test_context.Mock()
        start_obj = test_context.Mock()
        end_obj = test_context.Mock()
        start = (start_obj, 0)
        end = (end_obj, 8)
        get_container = test_context.patch_object(
            AXUtilities,
            "get_text_selection_container",
        )
        get_endpoints = test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=(start, end),
        )
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_elements",
            side_effect=[[], [start_obj, end_obj]],
        )
        present_change = test_context.patch_object(
            presenter,
            "_present_document_text_change",
            return_value=True,
        )
        update_cache = test_context.patch_object(AXUtilities, "update_cached_selected_text")
        handle_basic = test_context.patch_object(
            presenter,
            "_handle_basic_change",
            return_value=True,
        )

        assert presenter._handle_document_change(script, document, event_source, True)
        assert presenter._get_cached_document_selection_boundaries(script) == (start, end)
        get_endpoints.assert_called_once_with(
            document,
            document,
        )
        get_container.assert_not_called()
        present_change.assert_called_once_with(
            script,
            (None, -1),
            (None, -1),
            start,
            end,
            True,
        )
        assert [call.args for call in update_cache.call_args_list] == [
            (start_obj,),
            (end_obj,),
        ]
        handle_basic.assert_not_called()

    def test_document_selection_change_falls_back_to_basic_presentation(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test an unidentifiable document change retains per-element presentation."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import AXUtilities, TextSelectionPresenter

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        document = test_context.Mock()
        event_source = test_context.Mock()
        selection_root = test_context.Mock()
        start_obj = test_context.Mock()
        nested_obj = test_context.Mock()
        end_obj = test_context.Mock()
        start = (start_obj, 0)
        end = (end_obj, 8)
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_container",
            return_value=selection_root,
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=(start, end),
        )
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_elements",
            side_effect=[[], [start_obj, nested_obj, end_obj]],
        )
        test_context.patch_object(presenter, "_present_document_text_change", return_value=False)
        test_context.patch_object(
            AXUtilities,
            "find_ancestor",
            side_effect=lambda obj, _predicate: start_obj if obj == nested_obj else None,
        )
        update_cache = test_context.patch_object(AXUtilities, "update_cached_selected_text")
        handle_basic = test_context.patch_object(presenter, "_handle_basic_change")

        assert presenter._handle_document_change(script, document, event_source, True)
        assert [call.args for call in handle_basic.call_args_list] == [
            (script, start_obj, True),
            (script, end_obj, True),
        ]
        update_cache.assert_called_once_with(nested_obj)
