# Unit tests for verifying all Orca commands are properly registered.
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
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access
# pylint: disable=too-many-lines

"""Unit tests for verifying all Orca commands are properly registered."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


# Expected handler names for each module.
# These serve as the source of truth for what handlers should exist.

FLAT_REVIEW_PRESENTER_HANDLERS = frozenset(
    {
        "toggleFlatReviewModeHandler",
        "reviewHomeHandler",
        "reviewEndHandler",
        "reviewBottomLeftHandler",
        "reviewPreviousLineHandler",
        "reviewCurrentLineHandler",
        "reviewNextLineHandler",
        "reviewSpellCurrentLineHandler",
        "reviewPhoneticCurrentLineHandler",
        "reviewEndOfLineHandler",
        "reviewPreviousItemHandler",
        "reviewCurrentItemHandler",
        "reviewNextItemHandler",
        "reviewSpellCurrentItemHandler",
        "reviewPhoneticCurrentItemHandler",
        "reviewPreviousCharacterHandler",
        "reviewCurrentCharacterHandler",
        "reviewNextCharacterHandler",
        "reviewSpellCurrentCharacterHandler",
        "reviewUnicodeCurrentCharacterHandler",
        "reviewCurrentAccessibleHandler",
        "reviewAboveHandler",
        "reviewBelowHandler",
        "showContentsHandler",
        "flatReviewCopyHandler",
        "flatReviewAppendHandler",
        "flatReviewSayAllHandler",
        "flatReviewToggleRestrictHandler",
    }
)

FLAT_REVIEW_FINDER_HANDLERS = frozenset(
    {
        "findHandler",
        "findNextHandler",
        "findPreviousHandler",
    }
)

WHERE_AM_I_PRESENTER_HANDLERS = frozenset(
    {
        "whereAmIBasicHandler",
        "whereAmIDetailedHandler",
        "getTitleHandler",
        "getStatusBarHandler",
        "whereAmILinkHandler",
        "whereAmISelectionHandler",
        "readCharAttributesHandler",
        "presentSizeAndPositionHandler",
        "present_default_button",
        "present_cell_formula",
    }
)

LIVE_REGION_PRESENTER_HANDLERS = frozenset(
    {
        "toggle_live_region_support",
        "present_previous_live_region_message",
        "advance_live_politeness",
        "toggle_live_region_presentation",
        "present_next_live_region_message",
    }
)

NOTIFICATION_PRESENTER_HANDLERS = frozenset(
    {
        "present_last_notification",
        "present_next_notification",
        "present_previous_notification",
        "show_notification_list",
    }
)

CHAT_PRESENTER_HANDLERS = frozenset(
    {
        "chat_toggle_room_name_prefix",
        "chat_toggle_buddy_typing",
        "chat_toggle_message_histories",
        "chat_previous_message",
        "chat_next_message",
    }
)

SYSTEM_INFORMATION_PRESENTER_HANDLERS = frozenset(
    {
        "presentTimeHandler",
        "presentDateHandler",
        "present_battery_status",
        "present_cpu_and_memory_usage",
    }
)

LEARN_MODE_PRESENTER_HANDLERS = frozenset(
    {
        "enterLearnModeHandler",
    }
)

ACTION_PRESENTER_HANDLERS = frozenset(
    {
        "show_actions_list",
    }
)

MOUSE_REVIEW_HANDLERS = frozenset(
    {
        "toggleMouseReviewHandler",
    }
)

SLEEP_MODE_MANAGER_HANDLERS = frozenset(
    {
        "toggle_sleep_mode",
    }
)

BYPASS_MODE_MANAGER_HANDLERS = frozenset(
    {
        "bypass_mode_toggle",
    }
)

DEBUGGING_TOOLS_MANAGER_HANDLERS = frozenset(
    {
        "cycleDebugLevelHandler",
        "clear_atspi_app_cache",
        "capture_snapshot",
    }
)

CLIPBOARD_HANDLERS = frozenset(
    {
        "present_clipboard_contents",
    }
)

TYPING_ECHO_PRESENTER_HANDLERS = frozenset(
    {
        "cycleKeyEchoHandler",
    }
)

CARET_NAVIGATOR_HANDLERS = frozenset(
    {
        "end_of_file",
        "end_of_line",
        "next_character",
        "next_line",
        "next_word",
        "previous_character",
        "previous_line",
        "previous_word",
        "start_of_file",
        "start_of_line",
        "toggle_enabled",
    }
)

STRUCTURAL_NAVIGATOR_HANDLERS = frozenset(
    {
        "container_end",
        "container_start",
        "last_live_region",
        "list_blockquotes",
        "list_buttons",
        "list_checkboxes",
        "list_clickables",
        "list_comboboxes",
        "list_entries",
        "list_form_fields",
        "list_headings",
        "list_headings_level_1",
        "list_headings_level_2",
        "list_headings_level_3",
        "list_headings_level_4",
        "list_headings_level_5",
        "list_headings_level_6",
        "list_iframes",
        "list_images",
        "list_landmarks",
        "list_large_objects",
        "list_links",
        "list_list_items",
        "list_lists",
        "list_paragraphs",
        "list_radio_buttons",
        "list_tables",
        "list_unvisited_links",
        "list_visited_links",
        "next_blockquote",
        "next_button",
        "next_checkbox",
        "next_clickable",
        "next_combobox",
        "next_entry",
        "next_form_field",
        "next_heading",
        "next_heading_level_1",
        "next_heading_level_2",
        "next_heading_level_3",
        "next_heading_level_4",
        "next_heading_level_5",
        "next_heading_level_6",
        "next_iframe",
        "next_image",
        "next_landmark",
        "next_large_object",
        "next_link",
        "next_list",
        "next_list_item",
        "next_live_region",
        "next_paragraph",
        "next_radio_button",
        "next_separator",
        "next_table",
        "next_unvisited_link",
        "next_visited_link",
        "previous_blockquote",
        "previous_button",
        "previous_checkbox",
        "previous_clickable",
        "previous_combobox",
        "previous_entry",
        "previous_form_field",
        "previous_heading",
        "previous_heading_level_1",
        "previous_heading_level_2",
        "previous_heading_level_3",
        "previous_heading_level_4",
        "previous_heading_level_5",
        "previous_heading_level_6",
        "previous_iframe",
        "previous_image",
        "previous_landmark",
        "previous_large_object",
        "previous_link",
        "previous_list",
        "previous_list_item",
        "previous_live_region",
        "previous_paragraph",
        "previous_radio_button",
        "previous_separator",
        "previous_table",
        "previous_unvisited_link",
        "previous_visited_link",
        "structural_navigator_mode_cycle",
    }
)

TABLE_NAVIGATOR_HANDLERS = frozenset(
    {
        "clear_dynamic_column_headers_row",
        "clear_dynamic_row_headers_column",
        "set_dynamic_column_headers_row",
        "set_dynamic_row_headers_column",
        "table_cell_beginning_of_row",
        "table_cell_bottom_of_column",
        "table_cell_down",
        "table_cell_end_of_row",
        "table_cell_first",
        "table_cell_last",
        "table_cell_left",
        "table_cell_right",
        "table_cell_top_of_column",
        "table_cell_up",
        "table_navigator_toggle_enabled",
    }
)

OBJECT_NAVIGATOR_HANDLERS = frozenset(
    {
        "object_navigator_down",
        "object_navigator_next",
        "object_navigator_perform_action",
        "object_navigator_previous",
        "object_navigator_toggle_simplify",
        "object_navigator_up",
    }
)

SAY_ALL_PRESENTER_HANDLERS = frozenset(
    {
        "sayAllHandler",
    }
)

SPEECH_MANAGER_HANDLERS = frozenset(
    {
        "cycleCapitalizationStyleHandler",
        "cycleSpeakingPunctuationLevelHandler",
        "cycleSynthesizerHandler",
        "decreaseSpeechPitchHandler",
        "decreaseSpeechRateHandler",
        "decreaseSpeechVolumeHandler",
        "increaseSpeechPitchHandler",
        "increaseSpeechRateHandler",
        "increaseSpeechVolumeHandler",
        "toggleSilenceSpeechHandler",
    }
)

SPEECH_PRESENTER_HANDLERS = frozenset(
    {
        "changeNumberStyleHandler",
        "toggleSpeakingIndentationJustificationHandler",
        "toggleSpeechVerbosityHandler",
        "toggleTableCellReadModeHandler",
    }
)

# Script handlers - these will eventually move to presenter/manager modules
DEFAULT_SCRIPT_HANDLERS = frozenset(
    {
        "appPreferencesSettingsHandler",
        "contractedBrailleHandler",
        "cycleSettingsProfileHandler",
        "goBrailleHomeHandler",
        "leftClickReviewItemHandler",
        "panBrailleLeftHandler",
        "panBrailleRightHandler",
        "preferencesSettingsHandler",
        "processBrailleCutBeginHandler",
        "processBrailleCutLineHandler",
        "processRoutingKeyHandler",
        "rightClickReviewItemHandler",
        "routePointerToItemHandler",
        "shutdownHandler",
    }
)

DOCUMENT_PRESENTER_HANDLERS = frozenset(
    {
        "enable_sticky_browse_mode",
        "enable_sticky_focus_mode",
        "toggle_layout_mode",
        "toggle_presentation_mode",
    }
)

# Total expected command count for verification
EXPECTED_TOTAL_COMMANDS = (
    len(FLAT_REVIEW_PRESENTER_HANDLERS)
    + len(FLAT_REVIEW_FINDER_HANDLERS)
    + len(WHERE_AM_I_PRESENTER_HANDLERS)
    + len(LIVE_REGION_PRESENTER_HANDLERS)
    + len(NOTIFICATION_PRESENTER_HANDLERS)
    + len(CHAT_PRESENTER_HANDLERS)
    + len(SYSTEM_INFORMATION_PRESENTER_HANDLERS)
    + len(LEARN_MODE_PRESENTER_HANDLERS)
    + len(ACTION_PRESENTER_HANDLERS)
    + len(MOUSE_REVIEW_HANDLERS)
    + len(SLEEP_MODE_MANAGER_HANDLERS)
    + len(BYPASS_MODE_MANAGER_HANDLERS)
    + len(DEBUGGING_TOOLS_MANAGER_HANDLERS)
    + len(CLIPBOARD_HANDLERS)
    + len(TYPING_ECHO_PRESENTER_HANDLERS)
    + len(CARET_NAVIGATOR_HANDLERS)
    + len(STRUCTURAL_NAVIGATOR_HANDLERS)
    + len(TABLE_NAVIGATOR_HANDLERS)
    + len(OBJECT_NAVIGATOR_HANDLERS)
    + len(SAY_ALL_PRESENTER_HANDLERS)
    + len(SPEECH_MANAGER_HANDLERS)
    + len(SPEECH_PRESENTER_HANDLERS)
    + len(DEFAULT_SCRIPT_HANDLERS)
    + len(DOCUMENT_PRESENTER_HANDLERS)
)


class Fake:
    pass


@pytest.mark.unit
class TestCommandRegistry:
    """Tests for verifying all Orca commands are properly registered."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Sets up dependencies for command registry testing."""

        additional_modules = [
            "gi",
            "gi.repository",
            "gi.repository.Atspi",
            "gi.repository.Gtk",
            "gi.repository.GLib",
            "gi.repository.Gio",
            "gi.repository.Wnck",
            "dasbus",
            "dasbus.connection",
            "dasbus.error",
            "dasbus.client",
            "dasbus.client.proxy",
            "orca.dbus_service",
            "orca.flat_review",
            "orca.sound",
            "orca.speech",
            "orca.braille",
            "orca.braille_presenter",
            "orca.focus_manager",
            "orca.script_manager",
            "orca.ax_table",
            "orca.ax_text",
            "orca.ax_event_synthesizer",
            "orca.speech_manager",
            "orca.speech_presenter",
            "orca.orca_platform",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_mock = essential_modules["gi"]
        gi_mock.require_version = test_context.Mock()

        gi_repository_mock = essential_modules["gi.repository"]
        atspi_mock = essential_modules["gi.repository.Atspi"]
        atspi_mock.Role = Fake
        atspi_mock.Accessible = Fake
        atspi_mock.MatchRule = Fake
        atspi_mock.Relation = Fake
        gi_repository_mock.Atspi = atspi_mock

        gtk_mock = essential_modules["gi.repository.Gtk"]
        gtk_mock.Window = test_context.Mock()
        gtk_mock.VBox = test_context.Mock()
        gtk_mock.Label = test_context.Mock()
        gtk_mock.Button = test_context.Mock()
        gtk_mock.Entry = test_context.Mock()
        gtk_mock.CheckButton = test_context.Mock()
        gtk_mock.Dialog = test_context.Mock()
        gtk_mock.ResponseType = test_context.Mock()
        gtk_mock.ResponseType.OK = 1
        gtk_mock.ResponseType.CANCEL = 0

        glib_mock = essential_modules["gi.repository.GLib"]
        glib_error_mock = type("GError", (Exception,), {})
        glib_mock.GError = glib_error_mock

        gio_mock = essential_modules["gi.repository.Gio"]
        gi_repository_mock.Gio = gio_mock

        gio_wnck = essential_modules["gi.repository.Wnck"]

        class Screen:
            @staticmethod
            def get_windows_stacked():
                return []

            @staticmethod
            def get_active_workspace():
                return None

            @staticmethod
            def connect(fill1, fill2):
                return None

        gio_wnck.Screen.get_default = test_context.Mock(return_value=Screen)
        gi_repository_mock.Wnck = gio_wnck

        debug_mock = essential_modules["orca.debug"]
        debug_mock.debugFile = None

        flat_review_mock = essential_modules["orca.flat_review"]
        flat_review_mock.Context = Fake

        return essential_modules

    def _setup_structural_navigator_dependencies(
        self, test_context: OrcaTestContext
    ) -> dict[str, MagicMock]:
        """Sets up dependencies for structural navigator testing."""

        additional_modules = [
            "orca.cmdnames",
            "orca.dbus_service",
            "orca.debug",
            "orca.focus_manager",
            "orca.guilabels",
            "orca.input_event_manager",
            "orca.keybindings",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.script_manager",
            "orca.settings_manager",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        # Set up cmdnames with all required values
        cmdnames = essential_modules["orca.cmdnames"]
        cmdnames.STRUCTURAL_NAVIGATION_MODE_CYCLE = "cycle_mode"
        cmdnames.BLOCKQUOTE_PREV = "previous_blockquote"
        cmdnames.BLOCKQUOTE_NEXT = "next_blockquote"
        cmdnames.BLOCKQUOTE_LIST = "list_blockquotes"
        cmdnames.BUTTON_PREV = "previous_button"
        cmdnames.BUTTON_NEXT = "next_button"
        cmdnames.BUTTON_LIST = "list_buttons"
        cmdnames.CHECK_BOX_PREV = "previous_checkbox"
        cmdnames.CHECK_BOX_NEXT = "next_checkbox"
        cmdnames.CHECK_BOX_LIST = "list_checkboxes"
        cmdnames.COMBO_BOX_PREV = "previous_combobox"
        cmdnames.COMBO_BOX_NEXT = "next_combobox"
        cmdnames.COMBO_BOX_LIST = "list_comboboxes"
        cmdnames.ENTRY_PREV = "previous_entry"
        cmdnames.ENTRY_NEXT = "next_entry"
        cmdnames.ENTRY_LIST = "list_entries"
        cmdnames.FORM_FIELD_PREV = "previous_form_field"
        cmdnames.FORM_FIELD_NEXT = "next_form_field"
        cmdnames.FORM_FIELD_LIST = "list_form_fields"
        cmdnames.HEADING_PREV = "previous_heading"
        cmdnames.HEADING_NEXT = "next_heading"
        cmdnames.HEADING_LIST = "list_headings"
        cmdnames.HEADING_AT_LEVEL_PREV = "previous_heading_level_%d"
        cmdnames.HEADING_AT_LEVEL_NEXT = "next_heading_level_%d"
        cmdnames.HEADING_AT_LEVEL_LIST = "list_headings_level_%d"
        cmdnames.IFRAME_PREV = "previous_iframe"
        cmdnames.IFRAME_NEXT = "next_iframe"
        cmdnames.IFRAME_LIST = "list_iframes"
        cmdnames.IMAGE_PREV = "previous_image"
        cmdnames.IMAGE_NEXT = "next_image"
        cmdnames.IMAGE_LIST = "list_images"
        cmdnames.LANDMARK_PREV = "previous_landmark"
        cmdnames.LANDMARK_NEXT = "next_landmark"
        cmdnames.LANDMARK_LIST = "list_landmarks"
        cmdnames.LIST_PREV = "previous_list"
        cmdnames.LIST_NEXT = "next_list"
        cmdnames.LIST_LIST = "list_lists"
        cmdnames.LIST_ITEM_PREV = "previous_list_item"
        cmdnames.LIST_ITEM_NEXT = "next_list_item"
        cmdnames.LIST_ITEM_LIST = "list_list_items"
        cmdnames.LIVE_REGION_PREV = "previous_live_region"
        cmdnames.LIVE_REGION_NEXT = "next_live_region"
        cmdnames.LIVE_REGION_LAST = "last_live_region"
        cmdnames.PARAGRAPH_PREV = "previous_paragraph"
        cmdnames.PARAGRAPH_NEXT = "next_paragraph"
        cmdnames.PARAGRAPH_LIST = "list_paragraphs"
        cmdnames.RADIO_BUTTON_PREV = "previous_radio_button"
        cmdnames.RADIO_BUTTON_NEXT = "next_radio_button"
        cmdnames.RADIO_BUTTON_LIST = "list_radio_buttons"
        cmdnames.SEPARATOR_PREV = "previous_separator"
        cmdnames.SEPARATOR_NEXT = "next_separator"
        cmdnames.TABLE_PREV = "previous_table"
        cmdnames.TABLE_NEXT = "next_table"
        cmdnames.TABLE_LIST = "list_tables"
        cmdnames.UNVISITED_LINK_PREV = "previous_unvisited_link"
        cmdnames.UNVISITED_LINK_NEXT = "next_unvisited_link"
        cmdnames.UNVISITED_LINK_LIST = "list_unvisited_links"
        cmdnames.VISITED_LINK_PREV = "previous_visited_link"
        cmdnames.VISITED_LINK_NEXT = "next_visited_link"
        cmdnames.VISITED_LINK_LIST = "list_visited_links"
        cmdnames.LINK_PREV = "previous_link"
        cmdnames.LINK_NEXT = "next_link"
        cmdnames.LINK_LIST = "list_links"
        cmdnames.CLICKABLE_PREV = "previous_clickable"
        cmdnames.CLICKABLE_NEXT = "next_clickable"
        cmdnames.CLICKABLE_LIST = "list_clickables"
        cmdnames.LARGE_OBJECT_PREV = "previous_large_object"
        cmdnames.LARGE_OBJECT_NEXT = "next_large_object"
        cmdnames.LARGE_OBJECT_LIST = "list_large_objects"
        cmdnames.CONTAINER_START = "container_start"
        cmdnames.CONTAINER_END = "container_end"

        # Set up other required mocks
        settings_mock = essential_modules["orca.settings"]
        settings_mock.structuralNavigationEnabled = True
        settings_mock.structNavTriggersFocusMode = True
        settings_mock.wrappedStructuralNavigation = True
        settings_mock.largeObjectTextLength = 75

        essential_modules["orca.orca_i18n"]._ = lambda x: x
        essential_modules["orca.debug"].print_message = test_context.Mock()
        essential_modules["orca.debug"].LEVEL_INFO = 800

        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module.return_value = None
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = controller_mock

        focus_manager_instance = test_context.Mock()
        focus_manager_instance.get_locus_of_focus.return_value = None
        essential_modules["orca.focus_manager"].get_manager.return_value = focus_manager_instance

        essential_modules["orca.AXObject"].supports_collection.return_value = True
        essential_modules["orca.AXUtilities"].is_heading.return_value = False

        return essential_modules

    def _setup_speech_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Sets up dependencies for speech manager and presenter testing."""

        additional_modules = [
            "orca.mathsymbols",
            "orca.object_properties",
            "orca.pronunciation_dictionary_manager",
            "orca.speech",
            "orca.speechserver",
            "orca.acss",
            "orca.ax_hypertext",
            "orca.ax_table",
            "orca.ax_text",
            "orca.ax_utilities",
            "orca.colornames",
            "orca.ax_utilities_text",
            "orca.ax_document",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        settings_mock = essential_modules["orca.settings"]
        settings_mock.speechSystemOverride = "spiel"
        settings_mock.speechFactoryModules = ["spiel", "speechdispatcherfactory"]
        settings_mock.speechServerInfo = None
        settings_mock.voices = {}
        settings_mock.DEFAULT_VOICE = "default"
        settings_mock.enableSpeech = True
        settings_mock.CAPITALIZATION_STYLE_NONE = "none"
        settings_mock.CAPITALIZATION_STYLE_SPELL = "spell"
        settings_mock.CAPITALIZATION_STYLE_ICON = "icon"
        settings_mock.PUNCTUATION_STYLE_NONE = 3
        settings_mock.PUNCTUATION_STYLE_SOME = 2
        settings_mock.PUNCTUATION_STYLE_MOST = 1
        settings_mock.PUNCTUATION_STYLE_ALL = 0
        settings_mock.VERBOSITY_LEVEL_BRIEF = 0
        settings_mock.VERBOSITY_LEVEL_VERBOSE = 1

        essential_modules["orca.orca_i18n"]._ = lambda x: x
        essential_modules["orca.orca_i18n"].C_ = lambda c, x: x
        essential_modules["orca.orca_i18n"].ngettext = lambda s, p, n: s if n == 1 else p

        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module.return_value = None
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = controller_mock

        def passthrough_decorator(func):
            return func

        essential_modules["orca.dbus_service"].getter = passthrough_decorator
        essential_modules["orca.dbus_service"].setter = passthrough_decorator
        essential_modules["orca.dbus_service"].command = passthrough_decorator
        essential_modules["orca.dbus_service"].parameterized_command = passthrough_decorator

        essential_modules["orca.speech"].get_speech_server.return_value = test_context.Mock()

        acss_mock = essential_modules["orca.acss"]
        acss_mock.ACSS = test_context.Mock()
        acss_mock.ACSS.RATE = "rate"
        acss_mock.ACSS.AVERAGE_PITCH = "average-pitch"
        acss_mock.ACSS.GAIN = "gain"

        return essential_modules

    def test_flat_review_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all flat review presenter handlers are registered in CommandManager."""

        self._setup_dependencies(test_context)
        from orca.flat_review_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()

        cmd_manager = command_manager.get_manager()
        missing = frozenset(
            name
            for name in FLAT_REVIEW_PRESENTER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in flat_review_presenter: {missing}"

    def test_flat_review_finder_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all flat review finder handlers are registered in CommandManager."""

        self._setup_dependencies(test_context)
        from orca.flat_review_finder import get_finder
        from orca import command_manager

        finder = get_finder()
        finder.set_up_commands()

        cmd_manager = command_manager.get_manager()
        missing = frozenset(
            name
            for name in FLAT_REVIEW_FINDER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in flat_review_finder: {missing}"

    def test_where_am_i_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all where am I presenter handlers are registered."""

        self._setup_dependencies(test_context)
        from orca.where_am_i_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in WHERE_AM_I_PRESENTER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in where_am_i_presenter: {missing}"

    def test_notification_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all notification presenter commands are registered with CommandManager."""

        self._setup_dependencies(test_context)
        from orca.notification_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in NOTIFICATION_PRESENTER_HANDLERS
            if manager.get_keyboard_command(name) is None
        )

        assert not missing, f"Missing commands in notification_presenter: {missing}"

    def test_system_information_presenter_handlers_exist(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that all system information presenter commands are registered with CommandManager."""

        self._setup_dependencies(test_context)
        from orca.system_information_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in SYSTEM_INFORMATION_PRESENTER_HANDLERS
            if manager.get_keyboard_command(name) is None
        )

        assert not missing, f"Missing commands in system_information_presenter: {missing}"

    def test_sleep_mode_manager_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all sleep mode manager commands are registered with CommandManager."""

        self._setup_dependencies(test_context)
        from orca.sleep_mode_manager import get_manager
        from orca import command_manager

        manager = get_manager()
        manager.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in SLEEP_MODE_MANAGER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )

        assert not missing, f"Missing commands in sleep_mode_manager: {missing}"

    def test_live_region_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all live region presenter handlers are registered."""

        self._setup_dependencies(test_context)
        from orca.live_region_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in LIVE_REGION_PRESENTER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in live_region_presenter: {missing}"

    def test_chat_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all chat presenter handlers are registered."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in CHAT_PRESENTER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in chat_presenter: {missing}"

    def test_learn_mode_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all learn mode presenter commands are registered with CommandManager."""

        self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in LEARN_MODE_PRESENTER_HANDLERS
            if manager.get_keyboard_command(name) is None
        )

        assert not missing, f"Missing commands in learn_mode_presenter: {missing}"

    def test_action_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all action presenter handlers are registered."""

        self._setup_dependencies(test_context)
        from orca.action_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in ACTION_PRESENTER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in action_presenter: {missing}"

    def test_debugging_tools_manager_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all debugging tools manager handlers are registered."""

        self._setup_dependencies(test_context)
        from orca.debugging_tools_manager import get_manager
        from orca import command_manager

        manager = get_manager()
        manager.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in DEBUGGING_TOOLS_MANAGER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in debugging_tools_manager: {missing}"

    def test_bypass_mode_manager_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all bypass mode manager commands are registered with CommandManager."""

        self._setup_dependencies(test_context)
        from orca.bypass_mode_manager import get_manager
        from orca import command_manager

        manager = get_manager()
        manager.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in BYPASS_MODE_MANAGER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )

        assert not missing, f"Missing commands in bypass_mode_manager: {missing}"

    def test_mouse_review_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all mouse review handlers are registered."""

        self._setup_dependencies(test_context)
        from orca.mouse_review import get_reviewer
        from orca import command_manager

        reviewer = get_reviewer()
        reviewer.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name for name in MOUSE_REVIEW_HANDLERS if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in mouse_review: {missing}"

    def test_typing_echo_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all typing echo presenter handlers are registered."""

        self._setup_dependencies(test_context)
        from orca.typing_echo_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in TYPING_ECHO_PRESENTER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in typing_echo_presenter: {missing}"

    def test_clipboard_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all clipboard handlers are registered."""

        self._setup_dependencies(test_context)
        from orca.clipboard import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name for name in CLIPBOARD_HANDLERS if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in clipboard: {missing}"

    def test_caret_navigator_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all caret navigator commands are registered with CommandManager.

        Note: caret_navigator now registers Commands directly with CommandManager
        instead of returning handlers from get_handlers(). This test verifies the
        commands are properly registered.
        """

        self._setup_structural_navigator_dependencies(test_context)
        from orca.caret_navigator import get_navigator
        from orca import command_manager

        navigator = get_navigator()
        navigator.set_up_commands()
        manager = command_manager.get_manager()

        missing = frozenset(
            name for name in CARET_NAVIGATOR_HANDLERS if manager.get_keyboard_command(name) is None
        )

        assert not missing, f"Missing commands in caret_navigator: {missing}"

    def test_structural_navigator_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all structural navigator handlers are registered in CommandManager."""

        self._setup_structural_navigator_dependencies(test_context)
        from orca.structural_navigator import get_navigator
        from orca import command_manager

        navigator = get_navigator()
        navigator.set_up_commands()

        cmd_manager = command_manager.get_manager()
        missing = frozenset(
            name
            for name in STRUCTURAL_NAVIGATOR_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in structural_navigator: {missing}"

    def test_table_navigator_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all table navigator handlers are registered in CommandManager."""

        self._setup_dependencies(test_context)
        from orca.table_navigator import get_navigator
        from orca import command_manager

        navigator = get_navigator()
        navigator.set_up_commands()

        cmd_manager = command_manager.get_manager()
        missing = frozenset(
            name
            for name in TABLE_NAVIGATOR_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in table_navigator: {missing}"

    def test_object_navigator_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all object navigator handlers are registered in CommandManager."""

        self._setup_dependencies(test_context)
        from orca.object_navigator import get_navigator
        from orca import command_manager

        navigator = get_navigator()
        navigator.set_up_commands()

        cmd_manager = command_manager.get_manager()
        missing = frozenset(
            name
            for name in OBJECT_NAVIGATOR_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in object_navigator: {missing}"

    def test_say_all_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all say all presenter handlers are registered."""

        self._setup_structural_navigator_dependencies(test_context)
        from orca.say_all_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in SAY_ALL_PRESENTER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in say_all_presenter: {missing}"

    def test_speech_manager_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all speech manager handlers are registered in CommandManager."""

        self._setup_speech_dependencies(test_context)
        from orca.speech_manager import get_manager
        from orca import command_manager

        manager = get_manager()
        manager.set_up_commands()

        cmd_manager = command_manager.get_manager()
        missing = frozenset(
            name
            for name in SPEECH_MANAGER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in speech_manager: {missing}"

    def test_speech_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all speech presenter handlers are registered in CommandManager."""

        self._setup_speech_dependencies(test_context)
        from orca.speech_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()

        cmd_manager = command_manager.get_manager()
        missing = frozenset(
            name
            for name in SPEECH_PRESENTER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in speech_presenter: {missing}"

    def test_document_presenter_handlers_exist(self, test_context: OrcaTestContext) -> None:
        """Test that all document presenter handlers are registered."""

        self._setup_structural_navigator_dependencies(test_context)
        from orca.document_presenter import get_presenter
        from orca import command_manager

        presenter = get_presenter()
        presenter.set_up_commands()
        cmd_manager = command_manager.get_manager()

        missing = frozenset(
            name
            for name in DOCUMENT_PRESENTER_HANDLERS
            if cmd_manager.get_keyboard_command(name) is None
        )
        assert not missing, f"Missing commands in document_presenter: {missing}"

    def test_expected_total_command_count(self) -> None:
        """Test that the expected total command count is correct.

        This test verifies the sum of all module handler counts matches
        the expected total. If this fails, a module's handlers may have
        been added or removed without updating the frozensets.
        """

        # Calculate expected total from all frozensets
        calculated_total = (
            len(FLAT_REVIEW_PRESENTER_HANDLERS)
            + len(FLAT_REVIEW_FINDER_HANDLERS)
            + len(WHERE_AM_I_PRESENTER_HANDLERS)
            + len(LIVE_REGION_PRESENTER_HANDLERS)
            + len(NOTIFICATION_PRESENTER_HANDLERS)
            + len(CHAT_PRESENTER_HANDLERS)
            + len(SYSTEM_INFORMATION_PRESENTER_HANDLERS)
            + len(LEARN_MODE_PRESENTER_HANDLERS)
            + len(ACTION_PRESENTER_HANDLERS)
            + len(MOUSE_REVIEW_HANDLERS)
            + len(SLEEP_MODE_MANAGER_HANDLERS)
            + len(BYPASS_MODE_MANAGER_HANDLERS)
            + len(DEBUGGING_TOOLS_MANAGER_HANDLERS)
            + len(CLIPBOARD_HANDLERS)
            + len(TYPING_ECHO_PRESENTER_HANDLERS)
            + len(CARET_NAVIGATOR_HANDLERS)
            + len(STRUCTURAL_NAVIGATOR_HANDLERS)
            + len(TABLE_NAVIGATOR_HANDLERS)
            + len(OBJECT_NAVIGATOR_HANDLERS)
            + len(SAY_ALL_PRESENTER_HANDLERS)
            + len(SPEECH_MANAGER_HANDLERS)
            + len(SPEECH_PRESENTER_HANDLERS)
            + len(DEFAULT_SCRIPT_HANDLERS)
            + len(DOCUMENT_PRESENTER_HANDLERS)
        )

        assert calculated_total == EXPECTED_TOTAL_COMMANDS, (
            f"Total command count mismatch: calculated {calculated_total}, "
            f"expected {EXPECTED_TOTAL_COMMANDS}"
        )
