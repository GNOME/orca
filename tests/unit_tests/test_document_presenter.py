# Unit tests for document_presenter.py.
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

# pylint: disable=wrong-import-position
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-locals

# pylint: disable=too-many-lines
"""Unit tests for document_presenter.py."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestDocumentPresenter:
    """Test DocumentPresenter class."""

    def _setup_presenter(self, test_context: OrcaTestContext):
        """Set up mocks for document_presenter dependencies."""

        additional_modules = [
            "orca.ax_document",
            "orca.ax_object",
            "orca.ax_table",
            "orca.ax_text",
            "orca.ax_utilities",
            "orca.caret_navigator",
            "orca.focus_manager",
            "orca.guilabels",
            "orca.input_event_manager",
            "orca.live_region_presenter",
            "orca.preferences_grid_base",
            "orca.script_manager",
            "orca.structural_navigator",
            "orca.table_navigator",
            "orca.braille_presenter",
            "orca.presentation_manager",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        # Set up guilabels with required constants
        guilabels = essential_modules["orca.guilabels"]
        guilabels.DOCUMENTS = "Documents"
        guilabels.KB_GROUP_CARET_NAVIGATION = "Caret Navigation"
        guilabels.KB_GROUP_STRUCTURAL_NAVIGATION = "Structural Navigation"
        guilabels.KB_GROUP_TABLE_NAVIGATION = "Table Navigation"
        guilabels.NATIVE_NAVIGATION = "Native Navigation"
        guilabels.AUTOMATIC_FOCUS_MODE = "Automatic focus mode"
        guilabels.CONTENT_LAYOUT_MODE = "Layout mode"
        guilabels.TABLE_SKIP_BLANK_CELLS = "Skip blank cells"
        guilabels.FIND_SPEAK_RESULTS = "Speak find results"
        guilabels.FIND_ONLY_SPEAK_CHANGED_LINES = "Only speak changed lines"
        guilabels.FIND_MINIMUM_MATCH_LENGTH = "Minimum match length"
        guilabels.FIND_OPTIONS = "Find Options"
        guilabels.READ_PAGE_UPON_LOAD = "Read page upon load"
        guilabels.PAGE_SUMMARY_UPON_LOAD = "Page summary upon load"
        guilabels.PAGE_LOAD = "Page Load"
        guilabels.CARET_NAVIGATION_INFO = "Caret navigation info"
        guilabels.STRUCTURAL_NAVIGATION_INFO = "Structural navigation info"
        guilabels.NATIVE_NAVIGATION_INFO = "Native navigation info"
        guilabels.AUTOMATIC_FOCUS_MODE_INFO = "Auto focus mode info"

        from orca import gsettings_registry

        registry = gsettings_registry.get_registry()
        registry.clear_runtime_values()

        # Import and return the module
        from orca import document_presenter

        return document_presenter, essential_modules

    def test_get_presenter_returns_singleton(self, test_context: OrcaTestContext) -> None:
        """Test get_presenter returns the same instance."""

        module, _mocks = self._setup_presenter(test_context)
        presenter1 = module.get_presenter()
        presenter2 = module.get_presenter()

        assert presenter1 is presenter2

    def test_get_native_nav_triggers_focus_mode_default(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test get_native_nav_triggers_focus_mode returns default value."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.get_native_nav_triggers_focus_mode()

        assert result is True

    def test_set_native_nav_triggers_focus_mode(self, test_context: OrcaTestContext) -> None:
        """Test set_native_nav_triggers_focus_mode updates setting."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.set_native_nav_triggers_focus_mode(False)

        assert result is True
        assert presenter.get_native_nav_triggers_focus_mode() is False

    def test_set_native_nav_triggers_focus_mode_no_change(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test set_native_nav_triggers_focus_mode returns True when value unchanged."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.set_native_nav_triggers_focus_mode(True)

        assert result is True

    def test_get_say_all_on_load_default(self, test_context: OrcaTestContext) -> None:
        """Test get_say_all_on_load returns default value."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.get_say_all_on_load()

        assert result is True

    def test_set_say_all_on_load(self, test_context: OrcaTestContext) -> None:
        """Test set_say_all_on_load updates setting."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.set_say_all_on_load(False)

        assert result is True
        assert presenter.get_say_all_on_load() is False

    def test_set_say_all_on_load_no_change(self, test_context: OrcaTestContext) -> None:
        """Test set_say_all_on_load returns True when value unchanged."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.set_say_all_on_load(True)

        assert result is True

    def test_get_page_summary_on_load_default(self, test_context: OrcaTestContext) -> None:
        """Test get_page_summary_on_load returns default value."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.get_page_summary_on_load()

        assert result is True

    def test_set_page_summary_on_load(self, test_context: OrcaTestContext) -> None:
        """Test set_page_summary_on_load updates setting."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.set_page_summary_on_load(False)

        assert result is True
        assert presenter.get_page_summary_on_load() is False

    def test_set_page_summary_on_load_no_change(self, test_context: OrcaTestContext) -> None:
        """Test set_page_summary_on_load returns True when value unchanged."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.set_page_summary_on_load(True)

        assert result is True

    def test_get_speak_find_results_true(self, test_context: OrcaTestContext) -> None:
        """Test get_speak_find_results returns True when verbosity is not NONE."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.get_speak_find_results()

        assert result is True

    def test_get_speak_find_results_false(self, test_context: OrcaTestContext) -> None:
        """Test get_speak_find_results returns False when verbosity is NONE."""

        module, _mocks = self._setup_presenter(test_context)
        from orca import gsettings_registry  # pylint: disable=import-outside-toplevel

        presenter = module.get_presenter()
        gsettings_registry.get_registry().set_runtime_value(
            "document",
            "find-results-verbosity",
            "none",
        )
        result = presenter.get_speak_find_results()

        assert result is False

    def test_set_speak_find_results_enable(self, test_context: OrcaTestContext) -> None:
        """Test set_speak_find_results enables speech."""

        module, _mocks = self._setup_presenter(test_context)
        from orca import gsettings_registry  # pylint: disable=import-outside-toplevel

        presenter = module.get_presenter()
        gsettings_registry.get_registry().set_runtime_value(
            "document",
            "find-results-verbosity",
            "none",
        )
        result = presenter.set_speak_find_results(True)

        assert result is True
        assert presenter.get_speak_find_results() is True

    def test_set_speak_find_results_disable(self, test_context: OrcaTestContext) -> None:
        """Test set_speak_find_results disables speech."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.set_speak_find_results(False)

        assert result is True
        assert presenter.get_speak_find_results() is False

    def test_get_only_speak_changed_lines_true(self, test_context: OrcaTestContext) -> None:
        """Test get_only_speak_changed_lines returns True when set."""

        module, _mocks = self._setup_presenter(test_context)
        from orca import gsettings_registry  # pylint: disable=import-outside-toplevel

        presenter = module.get_presenter()
        gsettings_registry.get_registry().set_runtime_value(
            "document",
            "find-results-verbosity",
            "if-line-changed",
        )
        result = presenter.get_only_speak_changed_lines()

        assert result is True

    def test_get_only_speak_changed_lines_false(self, test_context: OrcaTestContext) -> None:
        """Test get_only_speak_changed_lines returns False when not set."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.get_only_speak_changed_lines()

        assert result is False

    def test_set_only_speak_changed_lines_enable(self, test_context: OrcaTestContext) -> None:
        """Test set_only_speak_changed_lines enables the option."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        result = presenter.set_only_speak_changed_lines(True)

        assert result is True
        assert presenter.get_only_speak_changed_lines() is True

    def test_set_only_speak_changed_lines_disable(self, test_context: OrcaTestContext) -> None:
        """Test set_only_speak_changed_lines disables the option."""

        module, _mocks = self._setup_presenter(test_context)
        from orca import gsettings_registry  # pylint: disable=import-outside-toplevel

        presenter = module.get_presenter()
        gsettings_registry.get_registry().set_runtime_value(
            "document",
            "find-results-verbosity",
            "if-line-changed",
        )
        result = presenter.set_only_speak_changed_lines(False)

        assert result is True
        assert presenter.get_only_speak_changed_lines() is False

    def test_get_find_results_minimum_length(self, test_context: OrcaTestContext) -> None:
        """Test get_find_results_minimum_length returns current value."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        presenter.set_find_results_minimum_length(5)
        result = presenter.get_find_results_minimum_length()

        assert result == 5

    def test_set_find_results_minimum_length(self, test_context: OrcaTestContext) -> None:
        """Test set_find_results_minimum_length updates setting."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        presenter.set_find_results_minimum_length(5)
        result = presenter.set_find_results_minimum_length(10)

        assert result is True
        assert presenter.get_find_results_minimum_length() == 10

    def test_set_find_results_minimum_length_no_change(self, test_context: OrcaTestContext) -> None:
        """Test set_find_results_minimum_length returns True when value unchanged."""

        module, _mocks = self._setup_presenter(test_context)

        presenter = module.get_presenter()
        presenter.set_find_results_minimum_length(5)
        result = presenter.set_find_results_minimum_length(5)

        assert result is True

    def test_reset_find_announcement_state(self, test_context: OrcaTestContext) -> None:
        """Test reset_find_announcement_state resets the internal state."""

        module, _mocks = self._setup_presenter(test_context)
        presenter = module.get_presenter()

        # Set the internal state to True
        presenter._made_find_announcement = True
        assert presenter._made_find_announcement is True

        # Reset and verify
        presenter.reset_find_announcement_state()
        assert presenter._made_find_announcement is False

    def test_present_find_results_no_active_script(self, test_context: OrcaTestContext) -> None:
        """Test present_find_results returns False when no active script."""

        module, mocks = self._setup_presenter(test_context)
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = None

        presenter = module.get_presenter()
        result = presenter.present_find_results(None, 0)

        assert result is False

    def test_present_find_results_no_document(self, test_context: OrcaTestContext) -> None:
        """Test present_find_results returns False when no document."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        # Set up mock script with utilities
        mock_script = MagicMock()
        mock_script.utilities.get_document_for_object.return_value = None
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        presenter = module.get_presenter()
        mock_obj = MagicMock()
        result = presenter.present_find_results(mock_obj, 0)

        assert result is False

    def test_present_find_results_selection_too_short(self, test_context: OrcaTestContext) -> None:
        """Test present_find_results returns False when selection is too short."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)
        from orca import gsettings_registry  # pylint: disable=import-outside-toplevel

        gsettings_registry.get_registry().set_runtime_value(
            "document",
            "find-results-minimum-length",
            5,
        )

        # Set up mock script
        mock_script = MagicMock()
        mock_script.utilities.get_document_for_object.return_value = MagicMock()
        mock_script.utilities.get_caret_context.return_value = (None, 0)
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        # Set up AXText mock to return short selection (length 3)
        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.get_selection_start_offset.return_value = 0
        ax_utilities.AXUtilities.get_selection_end_offset.return_value = 3

        presenter = module.get_presenter()
        mock_obj = MagicMock()
        result = presenter.present_find_results(mock_obj, 0)

        assert result is False

    def test_present_find_results_speak_disabled(self, test_context: OrcaTestContext) -> None:
        """Test present_find_results returns False when speak is disabled."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)
        from orca import gsettings_registry  # pylint: disable=import-outside-toplevel

        registry = gsettings_registry.get_registry()
        registry.set_runtime_value("document", "find-results-minimum-length", 3)
        registry.set_runtime_value("document", "find-results-verbosity", "none")

        # Set up mock script
        mock_script = MagicMock()
        mock_script.utilities.get_document_for_object.return_value = MagicMock()
        mock_script.utilities.get_caret_context.return_value = (None, 0)
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        # Set up AXText mock with valid selection length
        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.get_selection_start_offset.return_value = 0
        ax_utilities.AXUtilities.get_selection_end_offset.return_value = 10

        presenter = module.get_presenter()
        mock_obj = MagicMock()
        result = presenter.present_find_results(mock_obj, 0)

        assert result is False

    def test_present_find_results_success(self, test_context: OrcaTestContext) -> None:
        """Test present_find_results returns True and presents when conditions are met."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)
        from orca import gsettings_registry  # pylint: disable=import-outside-toplevel

        gsettings_registry.get_registry().set_runtime_value(
            "document",
            "find-results-minimum-length",
            3,
        )

        # Set up mock script
        mock_script = MagicMock()
        mock_script.utilities.get_document_for_object.return_value = MagicMock()
        mock_script.utilities.get_caret_context.return_value = (None, 0)
        mock_script.utilities.get_line_contents_at_offset.return_value = ["test content"]
        mock_script.utilities.get_find_results_count.return_value = "1 of 5"
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        # Set up AXText mock with valid selection length
        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.get_selection_start_offset.return_value = 0
        ax_utilities.AXUtilities.get_selection_end_offset.return_value = 10

        presenter = module.get_presenter()
        presenter._made_find_announcement = False
        pres_manager = mocks["orca.presentation_manager"].get_manager()
        pres_manager.speak_contents.reset_mock()
        pres_manager.present_message.reset_mock()
        mock_obj = MagicMock()
        result = presenter.present_find_results(mock_obj, 0)

        assert result is True
        assert presenter._made_find_announcement is True
        pres_manager.speak_contents.assert_called_once()
        mock_script.update_braille.assert_called_once()
        pres_manager.present_message.assert_called_once_with("1 of 5")

    def test_present_find_results_skips_same_line_when_only_changed(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test present_find_results skips when same line and only_speak_changed_lines."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)
        from orca import gsettings_registry  # pylint: disable=import-outside-toplevel

        registry = gsettings_registry.get_registry()
        registry.set_runtime_value("document", "find-results-minimum-length", 3)
        registry.set_runtime_value("document", "find-results-verbosity", "if-line-changed")

        # Set up mock script
        mock_script = MagicMock()
        mock_script.utilities.get_document_for_object.return_value = MagicMock()
        mock_script.utilities.get_caret_context.return_value = (MagicMock(), 5)
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        # Set up AXText mock with valid selection length
        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.get_selection_start_offset.return_value = 0
        ax_utilities.AXUtilities.get_selection_end_offset.return_value = 10
        ax_text = mocks["orca.ax_text"]
        ax_text.AXText.get_range_rect.return_value = MagicMock()

        ax_utilities.AXUtilities.rects_are_on_same_line = MagicMock(return_value=True)

        presenter = module.get_presenter()
        presenter._made_find_announcement = True  # Already announced
        pres_manager = mocks["orca.presentation_manager"].get_manager()
        pres_manager.speak_contents.reset_mock()
        mock_obj = MagicMock()
        result = presenter.present_find_results(mock_obj, 5)

        assert result is False
        pres_manager.speak_contents.assert_not_called()

    def test_use_focus_mode_no_active_script(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns False when no active script."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = None

        presenter = module.get_presenter()
        result = presenter.use_focus_mode(MagicMock())

        assert result is False

    def test_use_focus_mode_sticky_focus_mode(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns True when focus mode is sticky."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=True,
            focus_mode_is_sticky=True,
            browse_mode_is_sticky=False,
        )

        result = presenter.use_focus_mode(MagicMock())

        assert result is True

    def test_use_focus_mode_sticky_browse_mode(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns False when browse mode is sticky."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=True,
        )

        result = presenter.use_focus_mode(MagicMock())

        assert result is False

    def test_use_focus_mode_in_say_all(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns False when in say all."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        focus_manager = mocks["orca.focus_manager"]
        focus_manager.get_manager.return_value.in_say_all.return_value = True

        presenter = module.get_presenter()
        # No sticky state set (defaults to browse mode)
        result = presenter.use_focus_mode(MagicMock())

        assert result is False

    def test_use_focus_mode_struct_nav_prevents(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns False when struct nav prevents it."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        focus_manager = mocks["orca.focus_manager"]
        focus_manager.get_manager.return_value.in_say_all.return_value = False

        struct_nav = mocks["orca.structural_navigator"]
        struct_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = True

        presenter = module.get_presenter()
        result = presenter.use_focus_mode(MagicMock())

        assert result is False

    def test_use_focus_mode_table_nav_prevents(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns False when table nav was last command."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        focus_manager = mocks["orca.focus_manager"]
        focus_manager.get_manager.return_value.in_say_all.return_value = False

        struct_nav = mocks["orca.structural_navigator"]
        struct_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False

        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = True

        presenter = module.get_presenter()
        result = presenter.use_focus_mode(MagicMock())

        assert result is False

    def test_use_focus_mode_caret_nav_prevents(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns False when caret nav prevents it."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        focus_manager = mocks["orca.focus_manager"]
        focus_manager.get_manager.return_value.in_say_all.return_value = False

        struct_nav = mocks["orca.structural_navigator"]
        struct_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False

        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False

        caret_nav = mocks["orca.caret_navigator"]
        caret_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = True

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.is_dead.return_value = False

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.find_ancestor_inclusive.return_value = None

        presenter = module.get_presenter()
        result = presenter.use_focus_mode(MagicMock(), MagicMock())

        assert result is False

    def test_use_focus_mode_focus_mode_widget(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns True for focus mode widget."""

        from unittest.mock import MagicMock, patch

        module, mocks = self._setup_presenter(test_context)
        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        focus_manager = mocks["orca.focus_manager"]
        focus_manager.get_manager.return_value.in_say_all.return_value = False

        struct_nav = mocks["orca.structural_navigator"]
        struct_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False

        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False

        caret_nav = mocks["orca.caret_navigator"]
        caret_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False

        presenter = module.get_presenter()
        with patch.object(presenter, "is_focus_mode_widget", return_value=True):
            result = presenter.use_focus_mode(MagicMock())

        assert result is True

    def test_use_focus_mode_entering_web_app(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns True when entering a web application."""

        from unittest.mock import MagicMock, patch

        module, mocks = self._setup_presenter(test_context)
        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        focus_manager = mocks["orca.focus_manager"]
        focus_manager.get_manager.return_value.in_say_all.return_value = False

        struct_nav = mocks["orca.structural_navigator"]
        struct_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False

        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False

        caret_nav = mocks["orca.caret_navigator"]
        caret_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_link.return_value = False
        ax_utilities.AXUtilities.is_radio_button.return_value = False
        ax_utilities.AXUtilities.is_embedded = MagicMock()

        # prev_obj not in app, obj in app
        ax_utilities.AXUtilities.find_ancestor.side_effect = [None, MagicMock()]

        presenter = module.get_presenter()
        with patch.object(presenter, "is_focus_mode_widget", return_value=False):
            result = presenter.use_focus_mode(MagicMock(), MagicMock())

        assert result is True

    def test_use_focus_mode_default_false(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns False by default."""

        from unittest.mock import MagicMock, patch

        module, mocks = self._setup_presenter(test_context)
        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        focus_manager = mocks["orca.focus_manager"]
        focus_manager.get_manager.return_value.in_say_all.return_value = False

        struct_nav = mocks["orca.structural_navigator"]
        struct_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False

        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False

        caret_nav = mocks["orca.caret_navigator"]
        caret_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_link.return_value = False
        ax_utilities.AXUtilities.is_radio_button.return_value = False
        ax_utilities.AXUtilities.is_embedded = MagicMock()

        ax_utilities.AXUtilities.find_ancestor.return_value = None

        presenter = module.get_presenter()
        with patch.object(presenter, "is_focus_mode_widget", return_value=False):
            result = presenter.use_focus_mode(MagicMock())

        assert result is False

    def test_use_focus_mode_native_nav_no_trigger(self, test_context: OrcaTestContext) -> None:
        """Test use_focus_mode returns current mode when native nav doesn't trigger."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        focus_manager = mocks["orca.focus_manager"]
        focus_manager.get_manager.return_value.in_say_all.return_value = False

        struct_nav = mocks["orca.structural_navigator"]
        struct_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False
        nav_mock = struct_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False

        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False

        caret_nav = mocks["orca.caret_navigator"]
        caret_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False
        nav_mock = caret_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False

        presenter = module.get_presenter()
        presenter.set_native_nav_triggers_focus_mode(False)
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=True,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        result = presenter.use_focus_mode(MagicMock())

        assert result is True

    def test_in_focus_mode_default_false(self, test_context: OrcaTestContext) -> None:
        """Test in_focus_mode returns False when no state exists for app."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)
        presenter = module.get_presenter()
        mock_app = MagicMock()

        result = presenter.in_focus_mode(mock_app)

        assert result is False

    def test_in_focus_mode_returns_state(self, test_context: OrcaTestContext) -> None:
        """Test in_focus_mode returns stored state."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)
        presenter = module.get_presenter()
        mock_app = MagicMock()

        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=True,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        result = presenter.in_focus_mode(mock_app)

        assert result is True

    def test_focus_mode_is_sticky_default_false(self, test_context: OrcaTestContext) -> None:
        """Test focus_mode_is_sticky returns False by default."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)
        presenter = module.get_presenter()
        mock_app = MagicMock()

        result = presenter.focus_mode_is_sticky(mock_app)

        assert result is False

    def test_focus_mode_is_sticky_returns_state(self, test_context: OrcaTestContext) -> None:
        """Test focus_mode_is_sticky returns stored state."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)
        presenter = module.get_presenter()
        mock_app = MagicMock()

        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=True,
            focus_mode_is_sticky=True,
            browse_mode_is_sticky=False,
        )

        result = presenter.focus_mode_is_sticky(mock_app)

        assert result is True

    def test_browse_mode_is_sticky_default_false(self, test_context: OrcaTestContext) -> None:
        """Test browse_mode_is_sticky returns False by default."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)
        presenter = module.get_presenter()
        mock_app = MagicMock()

        result = presenter.browse_mode_is_sticky(mock_app)

        assert result is False

    def test_browse_mode_is_sticky_returns_state(self, test_context: OrcaTestContext) -> None:
        """Test browse_mode_is_sticky returns stored state."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)
        presenter = module.get_presenter()
        mock_app = MagicMock()

        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=True,
        )

        result = presenter.browse_mode_is_sticky(mock_app)

        assert result is True

    def test_get_state_for_app_sets_mode(self, test_context: OrcaTestContext) -> None:
        """Test _get_state_for_app can be used to set mode state."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)
        presenter = module.get_presenter()
        mock_app = MagicMock()

        state = presenter._get_state_for_app(mock_app)
        state.in_focus_mode = True

        assert presenter.in_focus_mode(mock_app) is True

        state = presenter._get_state_for_app(mock_app)
        state.in_focus_mode = False

        assert presenter.in_focus_mode(mock_app) is False

    def test_clear_state_for_app(self, test_context: OrcaTestContext) -> None:
        """Test clear_state_for_app removes app state."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)
        presenter = module.get_presenter()
        mock_app = MagicMock()

        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=True,
        )

        presenter.clear_state_for_app(mock_app)

        assert presenter.in_focus_mode(mock_app) is False
        assert presenter.focus_mode_is_sticky(mock_app) is False

    def test_per_app_state_isolation(self, test_context: OrcaTestContext) -> None:
        """Test that different apps have isolated mode state."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)
        presenter = module.get_presenter()

        app1 = MagicMock()
        app2 = MagicMock()

        presenter._app_states[hash(app1)] = module._AppModeState(
            in_focus_mode=True,
            focus_mode_is_sticky=True,
            browse_mode_is_sticky=False,
        )
        presenter._app_states[hash(app2)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=True,
        )

        assert presenter.in_focus_mode(app1) is True
        assert presenter.focus_mode_is_sticky(app1) is True
        assert presenter.browse_mode_is_sticky(app1) is False

        assert presenter.in_focus_mode(app2) is False
        assert presenter.focus_mode_is_sticky(app2) is False
        assert presenter.browse_mode_is_sticky(app2) is True

    def test_set_presentation_mode_not_in_document(self, test_context: OrcaTestContext) -> None:
        """Test set_presentation_mode returns False when not in document."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_script = MagicMock()
        mock_script.utilities.in_document_content.return_value = False

        mocks["orca.messages"] = MagicMock()
        mocks["orca.messages"].DOCUMENT_NOT_IN_A = "Not in document"

        presenter = module.get_presenter()
        pres_manager = mocks["orca.presentation_manager"].get_manager()
        pres_manager.present_message.reset_mock()
        result = presenter._set_presentation_mode(mock_script, True, obj=MagicMock())

        assert result is False
        pres_manager.present_message.assert_called_once()

    def test_set_presentation_mode_same_mode(self, test_context: OrcaTestContext) -> None:
        """Test set_presentation_mode returns False when already in requested mode."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_script.utilities.in_document_content.return_value = True

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=True,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        result = presenter._set_presentation_mode(mock_script, True, obj=MagicMock())

        assert result is False

    def test_set_presentation_mode_to_browse(self, test_context: OrcaTestContext) -> None:
        """Test set_presentation_mode switches to browse mode."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_script.utilities.in_document_content.return_value = True
        mock_script.utilities.get_caret_context.return_value = (MagicMock(), 0)

        struct_nav = mocks["orca.structural_navigator"]
        caret_nav = mocks["orca.caret_navigator"]

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=True,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        result = presenter._set_presentation_mode(mock_script, False, obj=MagicMock())

        assert result is True
        assert presenter.in_focus_mode(mock_app) is False
        struct_nav.get_navigator.return_value.set_mode.assert_called()
        caret_nav.get_navigator.return_value.set_enabled_for_script.assert_called()

    def test_set_presentation_mode_to_focus(self, test_context: OrcaTestContext) -> None:
        """Test set_presentation_mode switches to focus mode."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_script.utilities.in_document_content.return_value = True
        mock_script.utilities.get_caret_context.return_value = (MagicMock(), 0)

        caret_nav = mocks["orca.caret_navigator"]
        nav_mock = caret_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        struct_nav = mocks["orca.structural_navigator"]
        nav_mock = struct_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        result = presenter._set_presentation_mode(mock_script, True, obj=MagicMock())

        assert result is True
        assert presenter.in_focus_mode(mock_app) is True

    def test_set_presentation_mode_dead_obj_fallback(self, test_context: OrcaTestContext) -> None:
        """Test set_presentation_mode uses locus of focus when obj is dead."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_script.utilities.in_document_content.return_value = True
        mock_script.utilities.get_caret_context.return_value = (MagicMock(), 0)

        caret_nav = mocks["orca.caret_navigator"]
        nav_mock = caret_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        struct_nav = mocks["orca.structural_navigator"]
        nav_mock = struct_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.is_dead.return_value = True

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        dead_obj = MagicMock()
        result = presenter._set_presentation_mode(mock_script, True, obj=dead_obj)

        assert result is True
        mock_script.utilities.in_document_content.assert_called_with(None)

    def test_suspend_navigators(self, test_context: OrcaTestContext) -> None:
        """Test suspend_navigators suspends all navigators."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app

        caret_nav = mocks["orca.caret_navigator"]
        struct_nav = mocks["orca.structural_navigator"]

        presenter = module.get_presenter()
        result = presenter.suspend_navigators(mock_script, True, "test")

        assert result is True
        caret_nav.get_navigator.return_value.suspend_commands.assert_called_with(
            mock_script,
            True,
            "test",
        )
        struct_nav.get_navigator.return_value.suspend_commands.assert_called_with(
            mock_script,
            True,
            "test",
        )

    def test_enable_sticky_focus_mode(self, test_context: OrcaTestContext) -> None:
        """Test enable_sticky_focus_mode sets sticky focus mode."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app

        presenter = module.get_presenter()
        pres_manager = mocks["orca.presentation_manager"].get_manager()
        pres_manager.present_message.reset_mock()
        result = presenter.enable_sticky_focus_mode(mock_script)

        assert result is True
        assert presenter.in_focus_mode(mock_app) is True
        assert presenter.focus_mode_is_sticky(mock_app) is True
        assert presenter.browse_mode_is_sticky(mock_app) is False
        pres_manager.present_message.assert_called()

    def test_enable_sticky_browse_mode(self, test_context: OrcaTestContext) -> None:
        """Test enable_sticky_browse_mode sets sticky browse mode."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app

        presenter = module.get_presenter()
        pres_manager = mocks["orca.presentation_manager"].get_manager()
        pres_manager.present_message.reset_mock()
        result = presenter.enable_sticky_browse_mode(mock_script)

        assert result is True
        assert presenter.in_focus_mode(mock_app) is False
        assert presenter.focus_mode_is_sticky(mock_app) is False
        assert presenter.browse_mode_is_sticky(mock_app) is True
        pres_manager.present_message.assert_called()

    def test_toggle_presentation_mode_not_in_document(self, test_context: OrcaTestContext) -> None:
        """Test toggle_presentation_mode when not in document."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_script = MagicMock()
        mock_script.utilities.in_document_content.return_value = False

        presenter = module.get_presenter()
        pres_manager = mocks["orca.presentation_manager"].get_manager()
        pres_manager.present_message.reset_mock()
        result = presenter.toggle_presentation_mode(mock_script)

        assert result is True
        pres_manager.present_message.assert_called()

    def test_toggle_presentation_mode_to_focus(self, test_context: OrcaTestContext) -> None:
        """Test toggle_presentation_mode switches to focus mode."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_script.utilities.in_document_content.return_value = True
        mock_script.utilities.get_caret_context.return_value = (MagicMock(), 0)

        caret_nav = mocks["orca.caret_navigator"]
        nav_mock = caret_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        struct_nav = mocks["orca.structural_navigator"]
        nav_mock = struct_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        result = presenter.toggle_presentation_mode(mock_script)

        assert result is True
        assert presenter.in_focus_mode(mock_app) is True

    def test_restore_mode_for_script_no_app(self, test_context: OrcaTestContext) -> None:
        """Test restore_mode_for_script with no app does nothing."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)

        mock_script = MagicMock()
        mock_script.app = None

        presenter = module.get_presenter()
        presenter.restore_mode_for_script(mock_script)

    def test_restore_mode_for_script_no_state(self, test_context: OrcaTestContext) -> None:
        """Test restore_mode_for_script with no existing state does nothing."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)

        mock_script = MagicMock()
        mock_script.app = MagicMock()

        presenter = module.get_presenter()
        presenter.restore_mode_for_script(mock_script)

    def test_restore_mode_for_script_with_state(self, test_context: OrcaTestContext) -> None:
        """Test restore_mode_for_script restores navigator suspension state."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app

        caret_nav = mocks["orca.caret_navigator"]

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=True,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        presenter.restore_mode_for_script(mock_script)

        caret_nav.get_navigator.return_value.suspend_commands.assert_called()

    def test_restore_mode_for_script_browse_mode_enables_navigators(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test restore_mode_for_script re-enables navigators when restoring browse mode."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app

        struct_nav = mocks["orca.structural_navigator"]
        caret_nav = mocks["orca.caret_navigator"]

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        presenter.restore_mode_for_script(mock_script)

        struct_nav.get_navigator.return_value.set_mode.assert_called_once()
        caret_nav.get_navigator.return_value.set_enabled_for_script.assert_called_once_with(
            mock_script,
            True,
        )

    def test_update_mode_if_needed_not_in_doc(self, test_context: OrcaTestContext) -> None:
        """Test update_mode_if_needed when neither in document suspends navigators."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_script = MagicMock()
        mock_script.utilities.get_top_level_document_for_object.return_value = None

        caret_nav = mocks["orca.caret_navigator"]

        presenter = module.get_presenter()
        result = presenter.update_mode_if_needed(mock_script, MagicMock(), MagicMock())

        # When focus is not in a document, navigators should be suspended
        assert result is True
        caret_nav.get_navigator.return_value.suspend_commands.assert_called()

    def test_update_mode_if_needed_leaving_doc(self, test_context: OrcaTestContext) -> None:
        """Test update_mode_if_needed when leaving document."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_doc = MagicMock()
        mock_script.utilities.get_top_level_document_for_object.side_effect = [mock_doc, None]

        caret_nav = mocks["orca.caret_navigator"]

        presenter = module.get_presenter()
        old_focus = MagicMock()
        new_focus = MagicMock()
        result = presenter.update_mode_if_needed(mock_script, old_focus, new_focus)

        assert result is True
        caret_nav.get_navigator.return_value.suspend_commands.assert_called()

    def test_update_mode_if_needed_sticky_focus(self, test_context: OrcaTestContext) -> None:
        """Test update_mode_if_needed with sticky focus mode when entering document."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_doc = MagicMock()
        mock_script.utilities.get_top_level_document_for_object.side_effect = [None, mock_doc]

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=True,
            focus_mode_is_sticky=True,
            browse_mode_is_sticky=False,
        )

        pres_manager = mocks["orca.presentation_manager"].get_manager()
        pres_manager.present_message.reset_mock()
        result = presenter.update_mode_if_needed(mock_script, MagicMock(), MagicMock())

        assert result is True
        pres_manager.present_message.assert_called()

    def test_update_mode_if_needed_sticky_browse(self, test_context: OrcaTestContext) -> None:
        """Test update_mode_if_needed with sticky browse mode when entering document."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_doc = MagicMock()
        mock_script.utilities.get_top_level_document_for_object.side_effect = [None, mock_doc]

        struct_nav = mocks["orca.structural_navigator"]
        caret_nav = mocks["orca.caret_navigator"]

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=True,
        )

        pres_manager = mocks["orca.presentation_manager"].get_manager()
        pres_manager.present_message.reset_mock()
        result = presenter.update_mode_if_needed(mock_script, MagicMock(), MagicMock())

        assert result is True
        pres_manager.present_message.assert_called()
        struct_nav.get_navigator.return_value.set_mode.assert_called()
        caret_nav.get_navigator.return_value.set_enabled_for_script.assert_called()

    def test_handle_entering_document_refreshes_commands(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test entering document refreshes commands even when mode unchanged."""

        from unittest.mock import MagicMock, patch

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_doc = MagicMock()
        mock_script.utilities.get_top_level_document_for_object.side_effect = [None, mock_doc]

        caret_nav = mocks["orca.caret_navigator"]
        nav_mock = caret_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        caret_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False
        struct_nav = mocks["orca.structural_navigator"]
        nav_mock = struct_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        struct_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False
        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        focus_manager = mocks["orca.focus_manager"]
        focus_manager.get_manager.return_value.in_say_all.return_value = False

        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        presenter = module.get_presenter()
        # Already in browse mode - entering document should still refresh commands
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        with patch.object(presenter, "is_focus_mode_widget", return_value=False):
            result = presenter.update_mode_if_needed(mock_script, MagicMock(), MagicMock())

        assert result is True
        # Verify commands were refreshed (suspend_commands called with suspended=False for browse)
        caret_nav.get_navigator.return_value.suspend_commands.assert_called()
        struct_nav.get_navigator.return_value.suspend_commands.assert_called()

    def test_is_likely_electron_app_true(self, test_context: OrcaTestContext) -> None:
        """Test _is_likely_electron_app returns True for Chromium toolkit non-browser."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_toolkit_name.return_value = "Chromium"
        ax_object.AXObject.get_name.return_value = "code"

        mock_app = MagicMock()
        presenter = module.get_presenter()
        result = presenter._is_likely_electron_app(mock_app)

        assert result is True

    def test_is_likely_electron_app_false_for_browser(self, test_context: OrcaTestContext) -> None:
        """Test _is_likely_electron_app returns False for known browsers."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_toolkit_name.return_value = "Chromium"
        ax_object.AXObject.get_name.return_value = "google-chrome"

        mock_app = MagicMock()
        presenter = module.get_presenter()
        result = presenter._is_likely_electron_app(mock_app)

        assert result is False

    def test_is_likely_electron_app_false_for_non_chromium(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test _is_likely_electron_app returns False for non-Chromium toolkit."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_toolkit_name.return_value = "gtk"
        ax_object.AXObject.get_name.return_value = "gedit"

        mock_app = MagicMock()
        presenter = module.get_presenter()
        result = presenter._is_likely_electron_app(mock_app)

        assert result is False

    def test_update_mode_electron_app_sticky_focus(self, test_context: OrcaTestContext) -> None:
        """Test update_mode_if_needed enables sticky focus for Electron apps when entering."""

        from unittest.mock import MagicMock, patch

        module, _mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_doc = MagicMock()
        mock_script.utilities.get_top_level_document_for_object.side_effect = [None, mock_doc]
        mock_script.utilities.in_document_content.return_value = True

        presenter = module.get_presenter()

        with patch.object(presenter, "_is_likely_electron_app", return_value=True):
            result = presenter.update_mode_if_needed(mock_script, MagicMock(), MagicMock())

        assert result is True
        assert presenter.in_focus_mode(mock_app) is True
        assert presenter.focus_mode_is_sticky(mock_app) is True

    def test_is_top_level_web_app_true(self, test_context: OrcaTestContext) -> None:
        """Test _is_top_level_web_app returns True for embedded doc with http URI."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_doc = MagicMock()
        mock_script = MagicMock()
        mock_script.utilities.active_document.return_value = mock_doc

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_embedded.return_value = True

        ax_document = mocks["orca.ax_document"]
        ax_document.AXDocument.get_uri.return_value = "https://docs.google.com/document"

        presenter = module.get_presenter()

        result = presenter._is_top_level_web_app(mock_script, MagicMock())

        assert result is True

    def test_is_top_level_web_app_false_no_http(self, test_context: OrcaTestContext) -> None:
        """Test _is_top_level_web_app returns False for non-http URI."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_doc = MagicMock()
        mock_script = MagicMock()
        mock_script.utilities.active_document.return_value = mock_doc

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_embedded.return_value = True

        ax_document = mocks["orca.ax_document"]
        ax_document.AXDocument.get_uri.return_value = "file:///home/user/doc.html"

        presenter = module.get_presenter()

        result = presenter._is_top_level_web_app(mock_script, MagicMock())

        assert result is False

    def test_is_top_level_web_app_false_no_document(self, test_context: OrcaTestContext) -> None:
        """Test _is_top_level_web_app returns False when no active document."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)

        mock_script = MagicMock()
        mock_script.utilities.active_document.return_value = None

        presenter = module.get_presenter()

        result = presenter._is_top_level_web_app(mock_script, MagicMock())

        assert result is False

    def test_is_top_level_web_app_false_not_embedded(self, test_context: OrcaTestContext) -> None:
        """Test _is_top_level_web_app returns False when document is not embedded role."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        mock_doc = MagicMock()
        mock_script = MagicMock()
        mock_script.utilities.active_document.return_value = mock_doc

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_embedded.return_value = False

        presenter = module.get_presenter()

        result = presenter._is_top_level_web_app(mock_script, MagicMock())

        assert result is False

    def test_update_mode_top_level_web_app_sticky_focus(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test update_mode_if_needed enables sticky focus for top-level web apps when entering."""

        from unittest.mock import MagicMock, patch

        module, _mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_doc = MagicMock()
        mock_script.utilities.get_top_level_document_for_object.side_effect = [None, mock_doc]
        mock_script.utilities.in_document_content.return_value = True

        presenter = module.get_presenter()

        with (
            patch.object(presenter, "_is_likely_electron_app", return_value=False),
            patch.object(presenter, "_is_top_level_web_app", return_value=True),
        ):
            result = presenter.update_mode_if_needed(mock_script, MagicMock(), MagicMock())

        assert result is True
        assert presenter.in_focus_mode(mock_app) is True
        assert presenter.focus_mode_is_sticky(mock_app) is True

    def test_is_focus_mode_widget_editable(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns True for editable objects."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = True

        mock_script = MagicMock()
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_combo_box(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns True for combo boxes."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_combo_box.return_value = True

        mock_script = MagicMock()
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_expandable_focusable(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns True for expandable focusable non-links."""

        from unittest.mock import MagicMock

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = True
        ax_utilities.AXUtilities.is_focusable.return_value = True
        ax_utilities.AXUtilities.is_link.return_value = False

        mock_script = MagicMock()
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_expandable_link_false(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test is_focus_mode_widget returns False for expandable focusable links."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = True
        ax_utilities.AXUtilities.is_focusable.return_value = True
        ax_utilities.AXUtilities.is_link.return_value = True
        ax_utilities.AXUtilities.is_list_box_item.return_value = False
        ax_utilities.AXUtilities.is_button_with_popup.return_value = False
        ax_utilities.AXUtilities.is_grid = MagicMock()
        ax_utilities.AXUtilities.is_menu = MagicMock()
        ax_utilities.AXUtilities.is_tool_bar = MagicMock()

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.LINK
        ax_utilities.AXUtilities.find_ancestor.return_value = None

        mock_script = MagicMock()
        mock_script.utilities.is_content_editable_with_embedded_objects.return_value = False
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is False

    def test_is_focus_mode_widget_always_focus_role(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns True for always-focus-mode roles."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.SLIDER

        mock_script = MagicMock()
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_layout_table_false(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns False for layout tables."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.TABLE_CELL

        ax_utilities.AXUtilities.get_table.return_value = MagicMock()
        ax_utilities.AXUtilities.is_layout_table.return_value = True

        mock_script = MagicMock()
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is False

    def test_is_focus_mode_widget_list_box_item(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns True for list box items."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False
        ax_utilities.AXUtilities.is_list_box_item.return_value = True

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.LIST_ITEM

        ax_utilities.AXUtilities.is_layout_table.return_value = False

        mock_script = MagicMock()
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_button_with_popup(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns True for buttons with popup."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False
        ax_utilities.AXUtilities.is_list_box_item.return_value = False
        ax_utilities.AXUtilities.is_button_with_popup.return_value = True

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.BUTTON

        ax_utilities.AXUtilities.is_layout_table.return_value = False

        mock_script = MagicMock()
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_table_cell_not_layout(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test is_focus_mode_widget returns True for non-layout table cells."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False
        ax_utilities.AXUtilities.is_list_box_item.return_value = False
        ax_utilities.AXUtilities.is_button_with_popup.return_value = False

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.TABLE_CELL

        ax_utilities.AXUtilities.get_table.return_value = MagicMock()
        ax_utilities.AXUtilities.is_layout_table.return_value = False

        ax_document = mocks["orca.ax_document"]
        ax_document.AXDocument.is_pdf.return_value = False

        mock_script = MagicMock()
        mock_script.utilities.is_text_block_element.return_value = False
        mock_script.utilities.has_name_and_action_and_no_useful_children.return_value = False
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_grid_descendant(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns True for grid descendants."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False
        ax_utilities.AXUtilities.is_list_box_item.return_value = False
        ax_utilities.AXUtilities.is_button_with_popup.return_value = False
        ax_utilities.AXUtilities.is_grid = MagicMock()

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.PARAGRAPH
        ax_utilities.AXUtilities.find_ancestor.return_value = MagicMock()

        ax_utilities.AXUtilities.is_layout_table.return_value = False

        mock_script = MagicMock()
        mock_script.utilities.is_text_block_element.return_value = True
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_menu_descendant(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns True for menu descendants."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False
        ax_utilities.AXUtilities.is_list_box_item.return_value = False
        ax_utilities.AXUtilities.is_button_with_popup.return_value = False
        ax_utilities.AXUtilities.is_grid = MagicMock()
        ax_utilities.AXUtilities.is_menu = MagicMock()

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.PARAGRAPH
        ax_utilities.AXUtilities.find_ancestor.side_effect = [None, MagicMock()]

        ax_utilities.AXUtilities.is_layout_table.return_value = False

        mock_script = MagicMock()
        mock_script.utilities.is_text_block_element.return_value = True
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_toolbar_descendant(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns True for toolbar descendants."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False
        ax_utilities.AXUtilities.is_list_box_item.return_value = False
        ax_utilities.AXUtilities.is_button_with_popup.return_value = False
        ax_utilities.AXUtilities.is_grid = MagicMock()
        ax_utilities.AXUtilities.is_menu = MagicMock()
        ax_utilities.AXUtilities.is_tool_bar = MagicMock()

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.PARAGRAPH
        ax_utilities.AXUtilities.find_ancestor.side_effect = [None, None, MagicMock()]

        ax_utilities.AXUtilities.is_layout_table.return_value = False

        mock_script = MagicMock()
        mock_script.utilities.is_text_block_element.return_value = True
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_content_editable(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns True for content editable with embedded."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False
        ax_utilities.AXUtilities.is_list_box_item.return_value = False
        ax_utilities.AXUtilities.is_button_with_popup.return_value = False
        ax_utilities.AXUtilities.is_grid = MagicMock()
        ax_utilities.AXUtilities.is_menu = MagicMock()
        ax_utilities.AXUtilities.is_tool_bar = MagicMock()

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.PARAGRAPH
        ax_utilities.AXUtilities.find_ancestor.return_value = None

        ax_utilities.AXUtilities.is_layout_table.return_value = False

        mock_script = MagicMock()
        mock_script.utilities.is_text_block_element.return_value = True
        mock_script.utilities.is_content_editable_with_embedded_objects.return_value = True
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is True

    def test_is_focus_mode_widget_default_false(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns False by default."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False
        ax_utilities.AXUtilities.is_list_box_item.return_value = False
        ax_utilities.AXUtilities.is_button_with_popup.return_value = False
        ax_utilities.AXUtilities.is_grid = MagicMock()
        ax_utilities.AXUtilities.is_menu = MagicMock()
        ax_utilities.AXUtilities.is_tool_bar = MagicMock()

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.PARAGRAPH
        ax_utilities.AXUtilities.find_ancestor.return_value = None

        ax_utilities.AXUtilities.is_layout_table.return_value = False

        mock_script = MagicMock()
        mock_script.utilities.is_text_block_element.return_value = True
        mock_script.utilities.is_content_editable_with_embedded_objects.return_value = False
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is False

    def test_is_focus_mode_widget_pdf_table_false(self, test_context: OrcaTestContext) -> None:
        """Test is_focus_mode_widget returns False for table cells in PDFs."""

        from unittest.mock import MagicMock

        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi

        module, mocks = self._setup_presenter(test_context)

        ax_utilities = mocks["orca.ax_utilities"]
        ax_utilities.AXUtilities.is_editable.return_value = False
        ax_utilities.AXUtilities.is_expandable.return_value = False
        ax_utilities.AXUtilities.is_list_box_item.return_value = False
        ax_utilities.AXUtilities.is_button_with_popup.return_value = False
        ax_utilities.AXUtilities.is_grid = MagicMock()
        ax_utilities.AXUtilities.is_menu = MagicMock()
        ax_utilities.AXUtilities.is_tool_bar = MagicMock()

        ax_object = mocks["orca.ax_object"]
        ax_object.AXObject.get_role.return_value = Atspi.Role.TABLE_CELL
        ax_utilities.AXUtilities.find_ancestor.return_value = None

        ax_utilities.AXUtilities.get_table.return_value = MagicMock()
        ax_utilities.AXUtilities.is_layout_table.return_value = False

        ax_document = mocks["orca.ax_document"]
        ax_document.AXDocument.is_pdf.return_value = True

        mock_script = MagicMock()
        mock_script.utilities.is_text_block_element.return_value = False
        mock_script.utilities.has_name_and_action_and_no_useful_children.return_value = False
        mock_script.utilities.is_content_editable_with_embedded_objects.return_value = False
        mock_obj = MagicMock()

        presenter = module.get_presenter()
        result = presenter.is_focus_mode_widget(mock_script, mock_obj)

        assert result is False

    def test_get_in_focus_mode_no_script(self, test_context: OrcaTestContext) -> None:
        """Test get_in_focus_mode returns False when no active script."""

        module, mocks = self._setup_presenter(test_context)

        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = None

        presenter = module.get_presenter()
        result = presenter.get_in_focus_mode()

        assert result is False

    def test_get_focus_mode_is_sticky_no_script(self, test_context: OrcaTestContext) -> None:
        """Test get_focus_mode_is_sticky returns False when no active script."""

        module, mocks = self._setup_presenter(test_context)

        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = None

        presenter = module.get_presenter()
        result = presenter.get_focus_mode_is_sticky()

        assert result is False

    def test_get_browse_mode_is_sticky_no_script(self, test_context: OrcaTestContext) -> None:
        """Test get_browse_mode_is_sticky returns False when no active script."""

        module, mocks = self._setup_presenter(test_context)

        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = None

        presenter = module.get_presenter()
        result = presenter.get_browse_mode_is_sticky()

        assert result is False

    def test_has_state_for_app(self, test_context: OrcaTestContext) -> None:
        """Test has_state_for_app returns correct value."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        presenter = module.get_presenter()

        assert presenter.has_state_for_app(mock_app) is False

        presenter._app_states[hash(mock_app)] = module._AppModeState()

        assert presenter.has_state_for_app(mock_app) is True

    def test_update_mode_if_needed_within_doc(self, test_context: OrcaTestContext) -> None:
        """Test update_mode_if_needed when moving within document."""

        from unittest.mock import MagicMock, patch

        module, mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_doc = MagicMock()
        mock_script.utilities.get_top_level_document_for_object.return_value = mock_doc
        mock_script.utilities.in_document_content.return_value = True
        mock_script.utilities.get_caret_context.return_value = (MagicMock(), 0)

        caret_nav = mocks["orca.caret_navigator"]
        nav_mock = caret_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        caret_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False
        struct_nav = mocks["orca.structural_navigator"]
        nav_mock = struct_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        struct_nav.get_navigator.return_value.last_command_prevents_focus_mode.return_value = False
        table_nav = mocks["orca.table_navigator"]
        nav_mock = table_nav.get_navigator.return_value
        nav_mock.last_input_event_was_navigation_command.return_value = False
        focus_manager = mocks["orca.focus_manager"]
        focus_manager.get_manager.return_value.in_say_all.return_value = False

        script_manager = mocks["orca.script_manager"]
        script_manager.get_manager.return_value.get_active_script.return_value = mock_script

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=False,
            focus_mode_is_sticky=False,
            browse_mode_is_sticky=False,
        )

        with patch.object(presenter, "is_focus_mode_widget", return_value=False):
            result = presenter.update_mode_if_needed(mock_script, MagicMock(), MagicMock())

        assert result is True

    def test_update_mode_if_needed_sticky_within_doc(self, test_context: OrcaTestContext) -> None:
        """Test update_mode_if_needed within doc with sticky mode returns False."""

        from unittest.mock import MagicMock

        module, _mocks = self._setup_presenter(test_context)

        mock_app = MagicMock()
        mock_script = MagicMock()
        mock_script.app = mock_app
        mock_doc = MagicMock()
        mock_script.utilities.get_top_level_document_for_object.return_value = mock_doc

        presenter = module.get_presenter()
        presenter._app_states[hash(mock_app)] = module._AppModeState(
            in_focus_mode=True,
            focus_mode_is_sticky=True,
            browse_mode_is_sticky=False,
        )

        result = presenter.update_mode_if_needed(mock_script, MagicMock(), MagicMock())

        assert result is False
