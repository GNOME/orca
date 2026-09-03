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
        dependencies = test_context.setup_shared_dependencies(additional_modules)
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.get_current_selection_command.return_value = None
        selection_manager.is_selection_change_from_selection_command.return_value = False
        selection_manager.take_deferred_page_change_for_selection.return_value = None
        return dependencies

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

    def test_present_selection_removed(self, test_context: OrcaTestContext) -> None:
        """Test presenting that the current text selection was removed."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            TextSelectionPresenter,
            messages,
            presentation_manager,
        )

        messages.SELECTION_REMOVED = "Text unselected"
        TextSelectionPresenter().present_selection_removed()

        presentation_manager.get_manager.return_value.speak_message.assert_called_once_with(
            "Text unselected"
        )

    def test_present_deferred_page_change(self, test_context: OrcaTestContext) -> None:
        """Test presenting a deferred page change for a selection command."""

        dependencies = self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            TextSelectionPresenter,
            messages,
            presentation_manager,
        )

        target = test_context.Mock()
        messages.PAGE_NUMBER = "Page %d"
        manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        manager.take_deferred_page_change_for_selection.return_value = 2

        assert TextSelectionPresenter()._present_pending_page_change(target)
        manager.take_deferred_page_change_for_selection.assert_called_once_with(target)
        presentation_manager.get_manager.return_value.present_message.assert_called_once_with(
            "Page 2"
        )

    def test_newly_selected_text_is_cached_and_presented(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test extending a selection updates its cache and presents the new text."""

        dependencies = self._setup_dependencies(test_context)
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
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.is_selection_change_from_selection_command.return_value = True
        speech_presenter.get_presenter.return_value.get_only_speak_displayed_text.return_value = (
            False
        )
        present_page_change = test_context.patch_object(
            presenter,
            "_present_pending_page_change",
        )

        assert presenter.present_text_selection_change(script, obj)
        update_cache.assert_called_once_with(obj)
        present_page_change.assert_called_once_with(obj)
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

    @pytest.mark.parametrize("speak_message", [False, True])
    def test_removed_selection_is_cached_and_reported_as_unhandled(
        self,
        test_context: OrcaTestContext,
        speak_message: bool,
    ) -> None:
        """Test clearing a selection updates its cache while allowing caret presentation."""

        dependencies = self._setup_dependencies(test_context)
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
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.is_selection_change_from_selection_command.return_value = False

        assert not presenter.present_text_selection_change(script, obj, speak_message)
        update_cache.assert_called_once_with(obj)
        speak = presentation_manager.get_manager.return_value.speak_message
        if speak_message:
            speak.assert_called_once_with(messages.SELECTION_REMOVED)
        else:
            speak.assert_not_called()
        script.say_phrase.assert_not_called()

    def test_document_text_change_is_presented_as_single_phrase(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a multi-object document change has one selection-state announcement."""

        dependencies = self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXUtilities,
            TextSelectionPresenter,
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
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.is_selection_change_from_selection_command.return_value = True
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
        present_page_change = test_context.patch_object(
            presenter,
            "_present_pending_page_change",
        )

        assert presenter._present_document_text_change(
            script,
            old_start,
            old_end,
            start,
            end,
            True,
        )

        present_page_change.assert_called_once_with(start_obj)
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
        """Test manager state is presented as one endpoint range."""

        dependencies = self._setup_dependencies(test_context)
        from orca.text_selection_manager import SelectionChangeState
        from orca.text_selection_presenter import AXUtilities, TextSelectionPresenter

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        event_source = test_context.Mock()
        start_obj = test_context.Mock()
        end_obj = test_context.Mock()
        start = (start_obj, 0)
        end = (end_obj, 8)
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.update_selection_state.return_value = (
            SelectionChangeState.NOT_ORCA,
            ((None, -1), (None, -1)),
            (start, end),
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

        assert presenter._handle_document_change(script, event_source, True)
        selection_manager.update_selection_state.assert_called_once_with(event_source)
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

        dependencies = self._setup_dependencies(test_context)
        from orca.text_selection_manager import SelectionChangeState
        from orca.text_selection_presenter import AXUtilities, TextSelectionPresenter

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        event_source = test_context.Mock()
        start_obj = test_context.Mock()
        nested_obj = test_context.Mock()
        end_obj = test_context.Mock()
        start = (start_obj, 0)
        end = (end_obj, 8)
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.update_selection_state.return_value = (
            SelectionChangeState.NOT_ORCA,
            ((None, -1), (None, -1)),
            (start, end),
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

        assert presenter._handle_document_change(script, event_source, True)
        assert [call.args for call in handle_basic.call_args_list] == [
            (script, start_obj, True),
            (script, end_obj, True),
        ]
        update_cache.assert_called_once_with(nested_obj)

    def test_document_selection_change_without_elements_uses_event_source(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test an empty document result falls back to the event source's text selection."""

        dependencies = self._setup_dependencies(test_context)
        from orca.text_selection_manager import SelectionChangeState
        from orca.text_selection_presenter import AXUtilities, TextSelectionPresenter

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        event_source = test_context.Mock()
        no_selection = ((None, -1), (None, -1))
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.update_selection_state.return_value = (
            SelectionChangeState.NOT_ORCA,
            no_selection,
            no_selection,
        )
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_elements",
            side_effect=[[], []],
        )
        handle_basic = test_context.patch_object(
            presenter,
            "_handle_basic_change",
            return_value=True,
        )
        present_document = test_context.patch_object(
            presenter,
            "_present_document_text_change",
        )

        assert presenter._handle_document_change(script, event_source, True)
        handle_basic.assert_called_once_with(script, event_source, True)
        present_document.assert_not_called()

    def test_unpresentable_document_selection_change_is_ignored(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test an unpresentable selection state is ignored."""

        dependencies = self._setup_dependencies(test_context)
        from orca.text_selection_manager import SelectionChangeState
        from orca.text_selection_presenter import TextSelectionPresenter

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        event_source = test_context.Mock()
        old_selection = ((test_context.Mock(), 0), (test_context.Mock(), 4))
        no_selection = ((None, -1), (None, -1))
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.update_selection_state.return_value = (
            SelectionChangeState.UNPRESENTABLE,
            old_selection,
            no_selection,
        )
        present_change = test_context.patch_object(
            presenter,
            "_present_document_text_change",
        )

        assert not presenter._handle_document_change(script, event_source, True)
        present_change.assert_not_called()

    def test_managed_non_web_selection_uses_document_presentation(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a managed non-web selection is presented as a document selection."""

        dependencies = self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXUtilities,
            TextSelectionPresenter,
            document_presenter,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        obj = test_context.Mock()
        document = test_context.Mock()
        command = test_context.Mock()
        selection_manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        selection_manager.get_current_selection_command.return_value = command
        script.utilities.active_document.return_value = document
        script.utilities.in_document_content.return_value = True
        test_context.patch_object(AXUtilities, "is_web_element", return_value=False)
        document_presenter.get_presenter.return_value.in_focus_mode.return_value = False
        handle_document_change = test_context.patch_object(
            presenter,
            "_handle_document_change",
            return_value=True,
        )

        assert presenter.present_text_selection_change(script, obj)
        selection_manager.get_current_selection_command.assert_any_call(document)
        handle_document_change.assert_called_once_with(script, obj, True)

    def test_document_image_selection_change_presents_image(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test an image endpoint is presented when its changed text range is empty."""

        dependencies = self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXUtilities,
            TextSelectionPresenter,
            messages,
            presentation_manager,
            speech_presenter,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        text_obj = test_context.Mock()
        image = test_context.Mock()
        old_start = (text_obj, 0)
        old_end = (text_obj, 10)
        start = old_start
        end = (image, 1)
        manager = dependencies["orca.text_selection_manager"].get_manager.return_value
        manager.is_selection_change_from_selection_command.return_value = True
        speech_presenter.get_presenter.return_value.get_only_speak_displayed_text.return_value = (
            False
        )
        test_context.patch_object(
            presenter,
            "_get_document_text_change",
            return_value=(old_end, end, True, False, messages.TEXT_SELECTED),
        )
        test_context.patch_object(AXUtilities, "expand_eocs_in_range", return_value="")
        test_context.patch_object(
            AXUtilities,
            "is_image_or_canvas",
            side_effect=lambda obj: obj == image,
        )

        assert presenter._present_document_text_change(
            script,
            old_start,
            old_end,
            start,
            end,
            True,
        )
        presentation_manager.get_manager.return_value.present_object.assert_called_once_with(
            script,
            image,
            generate_braille=False,
        )
        script.present_object.assert_not_called()
        presentation_manager.get_manager.return_value.speak_message.assert_called_once_with(
            messages.TEXT_SELECTED
        )

    def test_embedded_text_change_uses_basic_presentation(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test an embedded text object's selection change is presented directly."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXObject,
            AXText,
            AXUtilities,
            TextSelectionPresenter,
            messages,
            speech_presenter,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        parent = test_context.Mock()
        child = test_context.Mock()
        test_context.patch_object(AXText, "get_substring", return_value="\ufffc")
        test_context.patch_object(AXUtilities, "find_child_at_offset", return_value=child)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        speech_presenter.get_presenter.return_value.get_only_speak_displayed_text.return_value = (
            False
        )
        handle_basic_change = test_context.patch_object(presenter, "_handle_basic_change")

        presenter._present_changes(
            script,
            parent,
            [[11, 12, messages.TEXT_UNSELECTED]],
            True,
            False,
        )

        handle_basic_change.assert_called_once_with(script, child, True)

    def test_embedded_non_text_change_uses_presentation_manager(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a selected non-text child is presented without invoking navigation."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXObject,
            AXText,
            AXUtilities,
            TextSelectionPresenter,
            messages,
            presentation_manager,
            speech_presenter,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        parent = test_context.Mock()
        child = test_context.Mock()
        test_context.patch_object(AXText, "get_substring", return_value="\ufffc")
        test_context.patch_object(AXUtilities, "find_child_at_offset", return_value=child)
        test_context.patch_object(AXObject, "supports_text", return_value=False)
        speech_presenter.get_presenter.return_value.get_only_speak_displayed_text.return_value = (
            False
        )

        presenter._present_changes(
            script,
            parent,
            [[11, 12, messages.TEXT_SELECTED]],
            True,
            False,
        )

        presentation_manager.get_manager.return_value.present_object.assert_called_once_with(
            script,
            child,
            generate_braille=False,
        )
        script.present_object.assert_not_called()
        presentation_manager.get_manager.return_value.speak_message.assert_called_once_with(
            messages.TEXT_SELECTED
        )

    def test_whitespace_before_changed_child_is_not_presented_separately(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a changed child absorbs an adjacent whitespace-only announcement."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXObject,
            AXText,
            AXUtilities,
            TextSelectionPresenter,
            messages,
            speech_presenter,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        parent = test_context.Mock()
        child = test_context.Mock()
        test_context.patch_object(AXText, "get_substring", return_value=" \ufffc")
        test_context.patch_object(AXUtilities, "find_child_at_offset", return_value=child)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        speech_presenter.get_presenter.return_value.get_only_speak_displayed_text.return_value = (
            False
        )
        handle_basic_change = test_context.patch_object(
            presenter,
            "_handle_basic_change",
            return_value=True,
        )

        presenter._present_changes(
            script,
            parent,
            [[10, 12, messages.TEXT_SELECTED]],
            True,
            False,
        )

        handle_basic_change.assert_called_once_with(script, child, True)
        script.say_phrase.assert_not_called()

    def test_document_text_change_accepts_equivalent_anchor_position(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test an equivalent ancestor/descendant anchor is not treated as changed."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import AXUtilities, TextSelectionPresenter, messages

        presenter = TextSelectionPresenter()
        old_start = (test_context.Mock(), 0)
        old_end = (test_context.Mock(), 14)
        normalized_start = (test_context.Mock(), 0)
        new_end = (test_context.Mock(), 8)
        test_context.patch_object(
            AXUtilities,
            "compare_text_positions",
            side_effect=[0, 1, -1],
        )

        result = presenter._get_document_text_change(
            old_start,
            old_end,
            normalized_start,
            new_end,
        )

        assert result == (old_end, new_end, True, False, messages.TEXT_SELECTED)

    def test_document_selection_removed_outside_selection_command_is_concise(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test removing a document selection does not repeat its former text."""

        self._setup_dependencies(test_context)
        from orca.text_selection_presenter import (
            AXUtilities,
            TextSelectionPresenter,
            messages,
            presentation_manager,
        )

        presenter = TextSelectionPresenter()
        script = test_context.Mock()
        start_obj = test_context.Mock()
        end_obj = test_context.Mock()
        old_start = (start_obj, 0)
        old_end = (end_obj, 10)
        no_selection = (None, -1)
        expand = test_context.patch_object(
            AXUtilities,
            "expand_eocs_in_range",
        )

        assert presenter._present_document_text_change(
            script,
            old_start,
            old_end,
            no_selection,
            no_selection,
            True,
        )
        expand.assert_not_called()
        presentation_manager.get_manager.return_value.speak_message.assert_called_once_with(
            messages.SELECTION_REMOVED,
        )
