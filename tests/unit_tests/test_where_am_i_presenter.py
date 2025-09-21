# Unit tests for where_am_i_presenter.py methods.
#
# Copyright 2025 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines

"""Unit tests for where_am_i_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext

READ_CHAR_ATTRIBUTES_CMD = "readCharAttributesCommand"
PRESENT_SIZE_AND_POSITION_CMD = "presentSizeAndPositionCommand"
PRESENT_TITLE_CMD = "presentTitleCommand"
PRESENT_STATUS_BAR_CMD = "presentStatusBarCommand"
PRESENT_DEFAULT_BUTTON_CMD = "presentDefaultButtonCommand"
WHERE_AM_I_BASIC_CMD = "whereAmIBasicCommand"
WHERE_AM_I_DETAILED_CMD = "whereAmIDetailedCommand"
WHERE_AM_I_LINK_CMD = "whereAmILinkCommand"
WHERE_AM_I_SELECTION_CMD = "whereAmISelectionCommand"
LOCATION_NOT_FOUND_MSG = "Location not found"
DEFAULT_BUTTON_NOT_FOUND_MSG = "Default button not found"
STATUS_BAR_NOT_FOUND_FULL_MSG = "Status bar not found"
STATUS_BAR_NOT_FOUND_BRIEF_MSG = "No status bar"

@pytest.mark.unit
class TestWhereAmIPresenter:
    """Test WhereAmIPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Returns all dependencies needed for WhereAmIPresenter testing."""

        additional_modules = [
            "orca.speech_and_verbosity_manager",
            "orca.ax_component",
            "orca.ax_text",
            "orca.ax_utilities",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.READ_CHAR_ATTRIBUTES = READ_CHAR_ATTRIBUTES_CMD
        cmdnames_mock.PRESENT_SIZE_AND_POSITION = PRESENT_SIZE_AND_POSITION_CMD
        cmdnames_mock.PRESENT_TITLE = PRESENT_TITLE_CMD
        cmdnames_mock.PRESENT_STATUS_BAR = PRESENT_STATUS_BAR_CMD
        cmdnames_mock.PRESENT_DEFAULT_BUTTON = PRESENT_DEFAULT_BUTTON_CMD
        cmdnames_mock.WHERE_AM_I_BASIC = WHERE_AM_I_BASIC_CMD
        cmdnames_mock.WHERE_AM_I_DETAILED = WHERE_AM_I_DETAILED_CMD
        cmdnames_mock.WHERE_AM_I_LINK = WHERE_AM_I_LINK_CMD
        cmdnames_mock.WHERE_AM_I_SELECTION = WHERE_AM_I_SELECTION_CMD

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.ORCA_MODIFIER_MASK = 2
        keybindings_mock.NO_MODIFIER_MASK = 0

        messages_mock = essential_modules["orca.messages"]
        messages_mock.BOLD = "bold"
        messages_mock.MISSPELLED = "misspelled"
        messages_mock.LOCATION_NOT_FOUND_FULL = LOCATION_NOT_FOUND_MSG
        messages_mock.LOCATION_NOT_FOUND_BRIEF = LOCATION_NOT_FOUND_MSG
        messages_mock.SIZE_AND_POSITION_FULL = "Size: %d by %d pixels, at %d, %d"
        messages_mock.SIZE_AND_POSITION_BRIEF = "%dx%d at %d,%d"
        messages_mock.DIALOG_NOT_IN_A = "Not in a dialog"
        messages_mock.DEFAULT_BUTTON_NOT_FOUND = DEFAULT_BUTTON_NOT_FOUND_MSG
        messages_mock.DEFAULT_BUTTON_IS_GRAYED = "Default button %s is grayed"
        messages_mock.DEFAULT_BUTTON_IS = "Default button is %s"
        messages_mock.STATUS_BAR_NOT_FOUND_FULL = STATUS_BAR_NOT_FOUND_FULL_MSG
        messages_mock.STATUS_BAR_NOT_FOUND_BRIEF = STATUS_BAR_NOT_FOUND_BRIEF_MSG
        messages_mock.NOT_ON_A_LINK = "Not on a link"
        messages_mock.NO_SELECTED_TEXT = "No selected text"
        messages_mock.SELECTED_TEXT_IS = "Selected text is %s"
        messages_mock.selected_items_count = test_context.Mock(
            return_value="2 of 5 items selected"
        )


        handler_mock = test_context.Mock()
        essential_modules["orca.input_event"].InputEventHandler = test_context.Mock(
            return_value=handler_mock
        )
        essential_modules["orca.input_event"].InputEvent = test_context.Mock()

        settings_manager_instance = test_context.Mock()

        def get_setting_side_effect(setting_name):
            if setting_name == "textAttributesToSpeak":
                return ["weight", "style", "underline"]
            return []

        settings_manager_instance.get_setting = test_context.Mock(
            side_effect=get_setting_side_effect
        )
        essential_modules["orca.settings_manager"].get_manager = test_context.Mock(
            return_value=settings_manager_instance
        )

        essential_modules["orca.settings"].repeatCharacterLimit = 4

        speech_verbosity_instance = test_context.Mock()
        speech_verbosity_instance.get_indentation_description = test_context.Mock(
            return_value=""
        )
        speech_verbosity_instance.adjust_for_presentation = test_context.Mock(
            return_value="adjusted text"
        )
        speech_verbosity_instance.adjust_for_digits = test_context.Mock(
            return_value="adjusted text"
        )
        essential_modules[
            "orca.speech_and_verbosity_manager"
        ].get_manager = test_context.Mock(return_value=speech_verbosity_instance)

        ax_component_mock = essential_modules["orca.ax_component"]
        rect_mock = test_context.Mock()
        rect_mock.width = 100
        rect_mock.height = 50
        rect_mock.x = 200
        rect_mock.y = 150
        ax_component_mock.AXComponent = test_context.Mock()
        ax_component_mock.AXComponent.get_rect = test_context.Mock(return_value=rect_mock)
        ax_component_mock.AXComponent.is_empty_rect = test_context.Mock(return_value=False)

        ax_text_mock = essential_modules["orca.ax_text"]
        ax_text_mock.AXText = test_context.Mock()
        ax_text_mock.AXText.get_text_attributes_at_offset = test_context.Mock(
            return_value=({"weight": "bold"}, 0, 5)
        )
        ax_text_mock.AXText.get_selected_text = test_context.Mock(
            return_value=("selected text", 0, 5)
        )
        ax_text_mock.AXText.get_all_supported_text_attributes = test_context.Mock()

        ax_text_attribute_instance = test_context.Mock()
        ax_text_attribute_instance.get_localized_name = test_context.Mock(
            return_value="Weight"
        )
        ax_text_attribute_instance.get_localized_value = test_context.Mock(
            return_value="Bold"
        )
        ax_text_attribute_instance.value_is_default = test_context.Mock(return_value=False)
        ax_text_attribute_instance.get_attribute_name = test_context.Mock(
            return_value="weight"
        )
        ax_text_mock.AXTextAttribute = test_context.Mock()
        ax_text_mock.AXTextAttribute.from_string = test_context.Mock(
            return_value=ax_text_attribute_instance
        )

        ax_utilities_mock = essential_modules["orca.ax_utilities"]
        ax_utilities_mock.AXUtilities = test_context.Mock()
        ax_utilities_mock.AXUtilities.get_default_button = test_context.Mock()
        ax_utilities_mock.AXUtilities.is_sensitive = test_context.Mock(return_value=True)
        ax_utilities_mock.AXUtilities.get_status_bar = test_context.Mock()
        ax_utilities_mock.AXUtilities.get_info_bar = test_context.Mock()
        ax_utilities_mock.AXUtilities.is_showing = test_context.Mock(return_value=True)
        ax_utilities_mock.AXUtilities.is_visible = test_context.Mock(return_value=True)
        ax_utilities_mock.AXUtilities.is_focused = test_context.Mock(return_value=True)
        ax_utilities_mock.AXUtilities.is_table_cell = test_context.Mock(return_value=False)
        ax_utilities_mock.AXUtilities.is_table_cell_or_header = test_context.Mock(
            return_value=False
        )
        ax_utilities_mock.AXUtilities.save_object_info_for_events = test_context.Mock()
        ax_utilities_mock.AXUtilities.is_list_item = test_context.Mock(return_value=False)
        ax_utilities_mock.AXUtilities.is_layout_only = test_context.Mock(return_value=False)

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.__init__ using OrcaTestContext for simpler mocking."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        presenter = WhereAmIPresenter()

        assert presenter._handlers is not None
        assert isinstance(presenter._handlers, dict)
        assert presenter._desktop_bindings is not None
        assert presenter._laptop_bindings is not None

        dbus_mock = deps["orca.dbus_service"]
        assert dbus_mock.get_remote_controller.call_count >= 1
        controller = dbus_mock.get_remote_controller.return_value
        controller.register_decorated_module.assert_called_with("WhereAmIPresenter", presenter)

    @pytest.mark.parametrize(
        "refresh,is_desktop,mock_empty",
        [
            pytest.param(True, True, False, id="desktop_refresh"),
            pytest.param(True, False, False, id="laptop_refresh"),
            pytest.param(False, True, True, id="desktop_empty"),
            pytest.param(False, False, True, id="laptop_empty"),
        ],
    )
    def test_get_bindings(
        self,
        test_context: OrcaTestContext,
        refresh: bool,
        is_desktop: bool,
        mock_empty: bool,
    ) -> None:
        """Test WhereAmIPresenter.get_bindings with various refresh and desktop settings."""

        self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        presenter = WhereAmIPresenter()

        if mock_empty:
            bindings_attr = (
                presenter._desktop_bindings if is_desktop else presenter._laptop_bindings
            )
            test_context.patch_object(bindings_attr, "is_empty", return_value=True)

        bindings = presenter.get_bindings(refresh=refresh, is_desktop=is_desktop)
        assert bindings is not None
        expected_bindings = (
            presenter._desktop_bindings if is_desktop else presenter._laptop_bindings
        )
        assert bindings == expected_bindings

    @pytest.mark.parametrize(
        "refresh,check_instance",
        [
            pytest.param(True, True, id="with_refresh"),
            pytest.param(False, False, id="without_refresh"),
        ],
    )
    def test_get_handlers(
        self,
        test_context: OrcaTestContext,
        refresh: bool,
        check_instance: bool,
    ) -> None:
        """Test WhereAmIPresenter.get_handlers with and without refresh."""

        self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        presenter = WhereAmIPresenter()
        handlers = presenter.get_handlers(refresh=refresh)
        assert handlers is not None

        if check_instance:
            assert isinstance(handlers, dict)
        else:
            assert handlers == presenter._handlers

    def test_setup_handlers(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter._setup_handlers."""

        self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        presenter = WhereAmIPresenter()
        presenter._setup_handlers()

        expected_handlers = [
            "readCharAttributesHandler",
            "presentSizeAndPositionHandler",
            "getTitleHandler",
            "getStatusBarHandler",
            "present_default_button",
            "whereAmIBasicHandler",
            "whereAmIDetailedHandler",
            "whereAmILinkHandler",
            "whereAmISelectionHandler",
        ]
        for handler_name in expected_handlers:
            assert handler_name in presenter._handlers

    @pytest.mark.parametrize(
        "attribute, value, expected",
        [
            pytest.param("weight", None, "", id="none_value"),
            pytest.param("weight", "bold", "bold", id="bold_weight"),
            pytest.param("weight", "700", "bold", id="numeric_weight"),
            pytest.param("spelling", "spelling", "misspelled", id="spelling"),
            pytest.param("style", "italic", "Weight: Bold", id="general"),
        ],
    )
    def test_localize_text_attribute_scenarios(
        self, test_context: OrcaTestContext, attribute: str, value: str | None, expected: str
    ) -> None:
        """Test WhereAmIPresenter._localize_text_attribute with various attribute scenarios."""

        self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        presenter = WhereAmIPresenter()
        result = presenter._localize_text_attribute(attribute, value)
        assert result == expected

    def test_present_character_attributes(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_character_attributes."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        mock_focus = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = mock_focus

        deps["orca.ax_text"].AXText.get_text_attributes_at_offset.return_value = (
            {"weight": "bold", "style": "italic"},
            0,
            5,
        )

        deps["orca.settings_manager"].get_manager.return_value.get_setting = test_context.Mock(
            return_value=["weight", "style", "underline"]
        )

        mock_script = test_context.Mock()
        test_context.patch_object(mock_script, "speak_message")
        presenter = WhereAmIPresenter()
        result = presenter.present_character_attributes(mock_script)
        assert result is True
        mock_script.speak_message.assert_called()
        assert mock_script.speak_message.call_count >= 1
        call_args = mock_script.speak_message.call_args_list
        assert len(call_args) > 0, "Expected at least one call to speak_message for attributes"

    def test_present_character_attributes_no_custom_attributes(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test WhereAmIPresenter.present_character_attributes with no custom attributes."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        deps["orca.settings_manager"].get_manager.return_value.get_setting = test_context.Mock(
            return_value=[]
        )

        default_attr = test_context.Mock()
        default_attr.get_attribute_name.return_value = "weight"
        default_attr.value_is_default.return_value = False
        deps["orca.ax_text"].AXText.get_all_supported_text_attributes.return_value = [default_attr]
        mock_script = test_context.Mock()
        test_context.patch_object(mock_script, "speak_message")
        presenter = WhereAmIPresenter()
        result = presenter.present_character_attributes(mock_script)
        assert result is True
        mock_script.speak_message.assert_called()
        deps["orca.ax_text"].AXText.get_all_supported_text_attributes.assert_called_once()

    def test_present_size_and_position_flat_review(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_size_and_position in flat review mode."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        mock_script = test_context.Mock()
        flat_review_presenter = test_context.Mock()
        flat_review_presenter.is_active.return_value = True
        current_obj = test_context.Mock()
        flat_review_presenter.get_current_object.return_value = current_obj
        mock_script.get_flat_review_presenter.return_value = flat_review_presenter
        mock_script.present_message = test_context.Mock()

        rect = test_context.Mock()
        rect.width = 200
        rect.height = 100
        rect.x = 50
        rect.y = 75
        deps["orca.ax_component"].AXComponent.get_rect.return_value = rect
        deps["orca.ax_component"].AXComponent.is_empty_rect.return_value = False
        presenter = WhereAmIPresenter()
        result = presenter.present_size_and_position(mock_script)
        assert result is True
        mock_script.present_message.assert_called()

    def test_present_size_and_position_empty_rect(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_size_and_position with empty rectangle."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        mock_script = test_context.Mock()
        flat_review_presenter = test_context.Mock()
        flat_review_presenter.is_active.return_value = False
        mock_script.get_flat_review_presenter.return_value = flat_review_presenter
        mock_script.present_message = test_context.Mock()

        focus_obj = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = focus_obj

        deps["orca.ax_component"].AXComponent.is_empty_rect.return_value = True
        presenter = WhereAmIPresenter()
        result = presenter.present_size_and_position(mock_script)
        assert result is True
        mock_script.present_message.assert_called_with(
            LOCATION_NOT_FOUND_MSG, LOCATION_NOT_FOUND_MSG)

    def test_present_title_valid_focus(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_title with valid focus object."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = focus_obj

        deps["orca.ax_object"].AXObject.is_dead.return_value = False

        mock_script = test_context.Mock()
        mock_script.speech_generator = test_context.Mock()
        mock_script.speech_generator.generate_window_title.return_value = [("Test Window", None)]
        mock_script.present_message = test_context.Mock()
        presenter = WhereAmIPresenter()
        result = presenter.present_title(mock_script)
        assert result is True
        mock_script.present_message.assert_called_with("Test Window", voice=None)

    def test_present_title_dead_focus(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_title with dead focus object."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        dead_obj = test_context.Mock()
        active_window = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = dead_obj
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_active_window.return_value = active_window

        deps["orca.ax_object"].AXObject.is_dead.side_effect = [True, False]

        mock_script = test_context.Mock()
        mock_script.speech_generator = test_context.Mock()
        mock_script.speech_generator.generate_window_title.return_value = [("Active Window", None)]
        mock_script.present_message = test_context.Mock()
        presenter = WhereAmIPresenter()
        result = presenter.present_title(mock_script)
        assert result is True
        mock_script.present_message.assert_called_with("Active Window", voice=None)

    def test_present_title_no_valid_object(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_title with no valid object."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        deps["orca.focus_manager"].get_manager.return_value.get_locus_of_focus.return_value = None
        deps["orca.focus_manager"].get_manager.return_value.get_active_window.return_value = None

        deps["orca.ax_object"].AXObject.is_dead.return_value = True
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        presenter = WhereAmIPresenter()
        result = presenter.present_title(mock_script)
        assert result is True
        mock_script.present_message.assert_called_with(LOCATION_NOT_FOUND_MSG)

    @pytest.mark.parametrize(
        "has_dialog, has_button, is_sensitive, button_name, expected_message",
        [
            pytest.param(True, True, True, "OK", "Default button is OK", id="button_success"),
            pytest.param(
                True, True, False, "OK", "Default button OK is grayed", id="button_grayed"
            ),
            pytest.param(False, False, False, None, "Not in a dialog", id="no_dialog"),
            pytest.param(True, False, False, None, DEFAULT_BUTTON_NOT_FOUND_MSG, id="no_button"),
        ],
    )
    def test_present_default_button_scenarios(
        self,
        test_context: OrcaTestContext,
        has_dialog: bool,
        has_button: bool,
        is_sensitive: bool,
        button_name: str | None,
        expected_message: str,
    ) -> None:
        """Test WhereAmIPresenter.present_default_button for various scenarios."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = focus_obj

        mock_script = test_context.Mock()
        dialog = test_context.Mock() if has_dialog else None
        mock_script.utilities.frame_and_dialog.return_value = (None, dialog)
        mock_script.present_message = test_context.Mock()

        if has_button:
            button = test_context.Mock()
            deps["orca.ax_utilities"].AXUtilities.get_default_button.return_value = button
            deps["orca.ax_utilities"].AXUtilities.is_sensitive.return_value = is_sensitive
            deps["orca.ax_object"].AXObject.get_name.return_value = button_name
        else:
            deps["orca.ax_utilities"].AXUtilities.get_default_button.return_value = None

        presenter = WhereAmIPresenter()
        result = presenter.present_default_button(mock_script)
        assert result is True
        mock_script.present_message.assert_called_with(expected_message)

    def test_present_status_bar_with_info(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_status_bar with both status bar and info bar."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = focus_obj
        mock_script = test_context.Mock()
        frame = test_context.Mock()
        mock_script.utilities.frame_and_dialog.return_value = (frame, None)
        mock_script.present_object = test_context.Mock()

        statusbar = test_context.Mock()
        infobar = test_context.Mock()
        deps["orca.ax_utilities"].AXUtilities.get_status_bar.return_value = statusbar
        deps["orca.ax_utilities"].AXUtilities.get_info_bar.return_value = infobar
        deps["orca.ax_utilities"].AXUtilities.is_showing.return_value = True
        deps["orca.ax_utilities"].AXUtilities.is_visible.return_value = True
        presenter = WhereAmIPresenter()
        result = presenter.present_status_bar(mock_script)
        assert result is True
        assert mock_script.present_object.call_count == 2

    def test_present_status_bar_no_status_bar(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_status_bar with no status bar."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = focus_obj
        mock_script = test_context.Mock()
        frame = test_context.Mock()
        mock_script.utilities.frame_and_dialog.return_value = (frame, None)
        mock_script.present_object = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        deps["orca.ax_utilities"].AXUtilities.get_status_bar.return_value = None
        deps["orca.ax_utilities"].AXUtilities.get_info_bar.return_value = None
        presenter = WhereAmIPresenter()
        result = presenter.present_status_bar(mock_script)
        assert result is True
        mock_script.present_message.assert_called_with(
            STATUS_BAR_NOT_FOUND_FULL_MSG, STATUS_BAR_NOT_FOUND_BRIEF_MSG)

    def test_present_link_valid_link(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_link with valid link."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        link_obj = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = link_obj
        mock_script = test_context.Mock()
        mock_script.utilities.is_link.return_value = True
        presenter = WhereAmIPresenter()
        mock_do_where_am_i = test_context.patch_object(
            presenter, "_do_where_am_i", return_value=True
        )
        result = presenter.present_link(mock_script)
        assert result is True
        mock_do_where_am_i.assert_called_with(mock_script, True, link_obj)

    def test_present_link_not_link(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_link with non-link object."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        non_link_obj = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = non_link_obj
        mock_script = test_context.Mock()
        mock_script.utilities.is_link.return_value = False
        mock_script.present_message = test_context.Mock()
        presenter = WhereAmIPresenter()
        result = presenter.present_link(mock_script)
        assert result is True
        mock_script.present_message.assert_called_with("Not on a link")

    def test_get_all_selected_text_spreadsheet_cell(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter._get_all_selected_text with spreadsheet cell."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        cell_obj = test_context.Mock()
        mock_script = test_context.Mock()
        mock_script.utilities.is_spreadsheet_cell.return_value = True

        deps["orca.ax_text"].AXText.get_selected_text.return_value = ("cell text", 0, 9)
        presenter = WhereAmIPresenter()
        result = presenter._get_all_selected_text(mock_script, cell_obj)
        assert result == "cell text"

    def test_get_all_selected_text_with_adjacent(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter._get_all_selected_text with adjacent text objects."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        text_obj = test_context.Mock()
        prev_obj = test_context.Mock()
        next_obj = test_context.Mock()
        mock_script = test_context.Mock()
        mock_script.utilities.is_spreadsheet_cell.return_value = False
        mock_script.utilities.find_previous_object.side_effect = [prev_obj, None]
        mock_script.utilities.find_next_object.side_effect = [next_obj, None]

        deps["orca.ax_text"].AXText.get_selected_text.side_effect = [
            ("current text", 0, 12),  # current object
            ("prev text", 0, 9),  # previous object
            ("next text", 0, 9),  # next object
        ]
        presenter = WhereAmIPresenter()
        result = presenter._get_all_selected_text(mock_script, text_obj)
        assert result == "prev text current text next text"

    def test_present_selected_text_no_focus(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_selected_text with no focus."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        deps["orca.focus_manager"].get_manager.return_value.get_locus_of_focus.return_value = None
        mock_script = test_context.Mock()
        test_context.patch_object(mock_script, "speak_message")
        presenter = WhereAmIPresenter()
        result = presenter.present_selected_text(mock_script)
        assert result is True
        mock_script.speak_message.assert_called_with(LOCATION_NOT_FOUND_MSG)

    def test_present_selected_text_with_text(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_selected_text with selected text."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps["focus_manager_instance"].get_locus_of_focus.return_value = focus_obj
        mock_script = test_context.Mock()
        test_context.patch_object(mock_script, "speak_message")

        presenter = WhereAmIPresenter()
        test_context.patch_object(
            presenter, "_get_all_selected_text", return_value="selected text"
        )

        manager = deps["orca.speech_and_verbosity_manager"].get_manager.return_value
        manager.get_indentation_description.return_value = "indent: 2"

        def mock_adjust_for_presentation(_obj, text) -> str:
            return f"processed {text}"

        def mock_adjust_for_digits(_obj, text) -> str:
            text_str = str(text) if text is not None else ""
            return text_str

        manager.adjust_for_presentation = mock_adjust_for_presentation
        manager.adjust_for_digits = mock_adjust_for_digits
        result = presenter.present_selected_text(mock_script)
        assert result is True
        expected_msg = "Selected text is indent: 2 processed selected text"
        mock_script.speak_message.assert_called_with(expected_msg)

    def test_present_selection_spreadsheet_handling(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_selection with spreadsheet cell range."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = focus_obj

        spreadsheet = test_context.Mock()
        deps["orca.ax_object"].AXObject.find_ancestor.return_value = spreadsheet
        mock_script = test_context.Mock()
        mock_script.utilities.is_spreadsheet_table = test_context.Mock(return_value=True)
        mock_script.utilities.speak_selected_cell_range.return_value = True
        presenter = WhereAmIPresenter()
        result = presenter.present_selection(mock_script)
        assert result is True
        mock_script.utilities.speak_selected_cell_range.assert_called_with(spreadsheet)

    def test_present_selection_container_selection(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_selection with selection container."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps["focus_manager_instance"].get_locus_of_focus.return_value = focus_obj

        deps["orca.ax_object"].AXObject.find_ancestor.return_value = None
        deps["orca.ax_object"].AXObject.get_name.side_effect = ["Item 1", "Item 2"]

        container = test_context.Mock()
        selected_items = [test_context.Mock(), test_context.Mock()]
        mock_script = test_context.Mock()
        mock_script.utilities.is_spreadsheet_table = test_context.Mock(return_value=False)
        mock_script.utilities.get_selection_container.return_value = container
        mock_script.utilities.selected_child_count.return_value = 2
        mock_script.utilities.selectable_child_count.return_value = 5
        mock_script.utilities.selected_children.return_value = selected_items
        mock_script.present_message = test_context.Mock()
        test_context.patch_object(mock_script, "speak_message")
        presenter = WhereAmIPresenter()
        result = presenter.present_selection(mock_script)
        assert result is True
        mock_script.present_message.assert_called_with("2 of 5 items selected")
        mock_script.speak_message.assert_called_with("Item 1,Item 2")

    def test_present_selection_no_container(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.present_selection with no selection container."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps["focus_manager_instance"].get_locus_of_focus.return_value = focus_obj

        deps["orca.ax_object"].AXObject.find_ancestor.return_value = None
        mock_script = test_context.Mock()
        mock_script.utilities.is_spreadsheet_table = test_context.Mock(return_value=False)
        mock_script.utilities.get_selection_container.return_value = None
        presenter = WhereAmIPresenter()
        presenter.present_selected_text = test_context.Mock(return_value=True)
        result = presenter.present_selection(mock_script)
        assert result is True
        presenter.present_selected_text.assert_called_with(mock_script, None, focus_obj)

    def test_do_where_am_i_basic(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter._do_where_am_i with basic mode."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps["focus_manager_instance"].get_locus_of_focus.return_value = focus_obj

        deps["orca.ax_object"].AXObject.is_dead.return_value = False

        deps["orca.ax_utilities"].AXUtilities.is_focused.return_value = True
        deps["orca.ax_utilities"].AXUtilities.is_table_cell_or_header.return_value = False
        deps["orca.ax_utilities"].AXUtilities.is_list_item.return_value = False
        deps["orca.ax_utilities"].AXUtilities.is_layout_only.return_value = False
        mock_script = test_context.Mock()
        mock_script.spellcheck = None
        mock_script.present_object = test_context.Mock()
        presenter = WhereAmIPresenter()
        result = presenter._do_where_am_i(mock_script, basic_only=True)
        assert result is True
        mock_script.present_object.assert_called_once()

    def test_do_where_am_i_detailed(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter._do_where_am_i with detailed mode."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps["focus_manager_instance"].get_locus_of_focus.return_value = focus_obj

        deps["orca.ax_object"].AXObject.is_dead.return_value = False

        deps["orca.ax_utilities"].AXUtilities.is_focused.return_value = True
        mock_script = test_context.Mock()
        mock_script.spellcheck = None
        mock_script.present_object = test_context.Mock()
        presenter = WhereAmIPresenter()
        result = presenter._do_where_am_i(mock_script, basic_only=False)
        assert result is True
        call_args = mock_script.present_object.call_args
        assert call_args[1]["formatType"] == "detailedWhereAmI"

    def test_do_where_am_i_dead_object(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter._do_where_am_i with dead focus object."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        dead_obj = test_context.Mock()
        active_window = test_context.Mock()
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = dead_obj
        deps[
            "orca.focus_manager"
        ].get_manager.return_value.get_active_window.return_value = active_window

        deps["orca.ax_object"].AXObject.is_dead.side_effect = [True, False]

        deps["orca.ax_utilities"].AXUtilities.is_focused.return_value = True
        mock_script = test_context.Mock()
        mock_script.spellcheck = None
        mock_script.present_object = test_context.Mock()
        presenter = WhereAmIPresenter()
        result = presenter._do_where_am_i(mock_script)
        assert result is True

    def test_do_where_am_i_no_object(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter._do_where_am_i with no valid object."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        deps["orca.focus_manager"].get_manager.return_value.get_locus_of_focus.return_value = None
        deps["orca.focus_manager"].get_manager.return_value.get_active_window.return_value = None

        deps["orca.ax_object"].AXObject.is_dead.return_value = True
        mock_script = test_context.Mock()
        mock_script.spellcheck = None
        mock_script.present_message = test_context.Mock()
        presenter = WhereAmIPresenter()
        result = presenter._do_where_am_i(mock_script)
        assert result is True
        mock_script.present_message.assert_called_with(LOCATION_NOT_FOUND_MSG)

    def test_do_where_am_i_with_spellcheck(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter._do_where_am_i with active spellcheck."""

        deps = self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        focus_obj = test_context.Mock()
        deps["focus_manager_instance"].get_locus_of_focus.return_value = focus_obj

        deps["orca.ax_object"].AXObject.is_dead.return_value = False

        deps["orca.ax_utilities"].AXUtilities.is_focused.return_value = True

        spellcheck_mock = test_context.Mock()
        spellcheck_mock.is_active.return_value = True
        spellcheck_mock.present_error_details = test_context.Mock()
        mock_script = test_context.Mock()
        mock_script.spellcheck = spellcheck_mock
        mock_script.present_object = test_context.Mock()
        presenter = WhereAmIPresenter()
        result = presenter._do_where_am_i(mock_script, basic_only=False)
        assert result is True
        spellcheck_mock.present_error_details.assert_called_with(True)

    def test_where_am_i_basic(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.where_am_i_basic."""

        self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        mock_script = test_context.Mock()
        presenter = WhereAmIPresenter()
        mock_do_where_am_i = test_context.patch_object(
            presenter, "_do_where_am_i", return_value=True
        )
        result = presenter.where_am_i_basic(mock_script)
        assert result is True
        mock_do_where_am_i.assert_called_with(mock_script, notify_user=True)

    def test_where_am_i_detailed(self, test_context: OrcaTestContext) -> None:
        """Test WhereAmIPresenter.where_am_i_detailed."""

        self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import WhereAmIPresenter

        mock_script = test_context.Mock()
        mock_script.interrupt_presentation = test_context.Mock()
        presenter = WhereAmIPresenter()
        mock_do_where_am_i = test_context.patch_object(
            presenter, "_do_where_am_i", return_value=True
        )
        result = presenter.where_am_i_detailed(mock_script)
        assert result is True
        mock_script.interrupt_presentation.assert_called_once()
        mock_do_where_am_i.assert_called_with(mock_script, False, notify_user=True)

    def test_get_presenter(self, test_context: OrcaTestContext) -> None:
        """Test get_presenter function."""

        self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import get_presenter

        presenter = get_presenter()
        assert presenter is not None
        presenter2 = get_presenter()
        assert presenter is presenter2
