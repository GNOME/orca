# Unit tests for learn_mode_presenter.py methods.
#
# Copyright 2025 Igalia, S.L.
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
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements
# pylint: disable=too-few-public-methods
# pylint: disable=protected-access
# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Unit tests for learn_mode_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

GTK_STOCK_CLOSE = "gtk-close"
TEST_COMMAND_DESCRIPTION = "Test Command"


@pytest.mark.unit
class TestLearnModePresenter:
    """Test LearnModePresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns all dependencies needed for LearnModePresenter testing."""

        additional_modules = [
            "gi.repository",
            "orca.command_manager",
            "orca.input_event_manager",
            "time",
            "orca.speech",
            "orca.speech_generator",
            "orca.generator",
            "orca.ax_hypertext",
            "orca.command_manager",
            "orca.braille_presenter",
            "orca.presentation_manager",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_repository_mock = essential_modules["gi.repository"]
        gdk_mock = test_context.Mock()
        gdk_mock.Screen = test_context.Mock()
        gdk_mock.Screen.get_default = test_context.Mock(return_value=test_context.Mock())

        gtk_mock = test_context.Mock()
        gtk_mock.show_uri = test_context.Mock()
        gtk_mock.Dialog = test_context.Mock()
        gtk_mock.DialogFlags = test_context.Mock()
        gtk_mock.DialogFlags.MODAL = 1
        gtk_mock.ResponseType = test_context.Mock()
        gtk_mock.ResponseType.CLOSE = -7
        gtk_mock.STOCK_CLOSE = GTK_STOCK_CLOSE
        gtk_mock.Grid = test_context.Mock()
        gtk_mock.ScrolledWindow = test_context.Mock()
        gtk_mock.TreeView = test_context.Mock()
        gtk_mock.CellRendererText = test_context.Mock()
        gtk_mock.TreeViewColumn = test_context.Mock()
        gtk_mock.TreeStore = test_context.Mock()

        gobject_mock = test_context.Mock()
        gobject_mock.TYPE_STRING = str

        atspi_mock = test_context.Mock()
        atspi_hyperlink_mock = test_context.Mock()
        atspi_hyperlink_mock.__or__ = test_context.Mock(return_value=type("UnionType", (), {}))
        atspi_mock.Hyperlink = atspi_hyperlink_mock
        atspi_mock.Accessible = test_context.Mock()
        atspi_mock.Hypertext = test_context.Mock()
        glib_mock = test_context.Mock()
        glib_mock.GError = Exception

        gi_repository_mock.Gdk = gdk_mock
        gi_repository_mock.Gtk = gtk_mock
        gi_repository_mock.GObject = gobject_mock
        gi_repository_mock.Atspi = atspi_mock
        gi_repository_mock.GLib = glib_mock

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.ENTER_LEARN_MODE = "enterLearnMode"

        guilabels_mock = essential_modules["orca.guilabels"]
        guilabels_mock.KB_GROUP_DEFAULT = "Default Commands"
        guilabels_mock.KB_GROUP_LEARN_MODE = "Learn Mode Commands"
        guilabels_mock.KB_GROUP_WHERE_AM_I = "Where Am I Commands"
        guilabels_mock.KB_GROUP_SPEECH_VERBOSITY = "Speech and Verbosity Commands"
        guilabels_mock.KB_GROUP_SLEEP_MODE = "Sleep Mode Commands"
        guilabels_mock.KB_GROUP_FLAT_REVIEW = "Flat Review Commands"
        guilabels_mock.KB_GROUP_FIND = "Find Commands"
        guilabels_mock.KB_GROUP_OBJECT_NAVIGATION = "Object Navigation Commands"
        guilabels_mock.KB_GROUP_STRUCTURAL_NAVIGATION = "Structural Navigation Commands"
        guilabels_mock.KB_GROUP_TABLE_NAVIGATION = "Table Navigation Commands"
        guilabels_mock.KB_GROUP_SYSTEM_INFORMATION = "System Information Commands"
        guilabels_mock.KB_GROUP_NOTIFICATIONS = "Notification Commands"
        guilabels_mock.KB_GROUP_CLIPBOARD = "Clipboard Commands"
        guilabels_mock.KB_GROUP_BOOKMARKS = "Bookmark Commands"
        guilabels_mock.KB_GROUP_MOUSE_REVIEW = "Mouse Review Commands"
        guilabels_mock.KB_GROUP_ACTIONS = "Action Commands"
        guilabels_mock.KB_GROUP_DEBUGGING_TOOLS = "Debugging Tool Commands"
        guilabels_mock.KB_HEADER_FUNCTION = "Function"
        guilabels_mock.KB_HEADER_KEY_BINDING = "Key Binding"

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_mock = test_context.Mock()

        class MockKeyboardEvent:
            """Mock keyboard event class for testing."""

            def __init__(self):
                self.is_printable_key = test_context.Mock(return_value=False)
                self.get_click_count = test_context.Mock(return_value=1)
                self.get_handler = test_context.Mock(return_value=None)
                self.get_command = test_context.Mock(return_value=None)
                self.get_command_name = test_context.Mock(return_value="")
                self.get_key_name = test_context.Mock(return_value="a")
                self.keyval_name = "a"
                self.modifiers = 0

        input_event_mock.InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )
        input_event_mock.KeyboardEvent = MockKeyboardEvent

        input_event_manager_mock = essential_modules["orca.input_event_manager"]
        manager_instance = test_context.Mock()
        mock_device = test_context.Mock()
        manager_instance._device = mock_device
        manager_instance.grab_keyboard = test_context.Mock()
        manager_instance.ungrab_keyboard = test_context.Mock()
        input_event_manager_mock.get_manager = test_context.Mock(return_value=manager_instance)
        input_event_manager_mock.InputEventManager = test_context.Mock(
            return_value=manager_instance
        )

        keybindings_mock = essential_modules["orca.keybindings"]
        key_bindings_instance = test_context.Mock()
        key_bindings_instance.is_empty = test_context.Mock(return_value=True)
        key_bindings_instance.remove_key_grabs = test_context.Mock(return_value=None)
        key_bindings_instance.add = test_context.Mock(return_value=None)
        key_bindings_instance.get_bound_bindings = test_context.Mock(return_value=[])

        key_binding_mock = test_context.Mock()
        key_binding_mock.handler = test_context.Mock()
        key_binding_mock.handler.description = TEST_COMMAND_DESCRIPTION
        key_binding_mock.as_string = test_context.Mock(return_value="Ctrl+t")

        keybindings_mock.KeyBindings = test_context.Mock(return_value=key_bindings_instance)
        keybindings_mock.KeyBinding = test_context.Mock(return_value=key_binding_mock)
        keybindings_mock.DEFAULT_MODIFIER_MASK = 0
        keybindings_mock.ORCA_MODIFIER_MASK = 1 << 26

        messages_mock = essential_modules["orca.messages"]
        messages_mock.VERSION = "Orca Version Information"
        messages_mock.LEARN_MODE_START_SPEECH = "Entering learn mode"
        messages_mock.LEARN_MODE_START_BRAILLE = "Learn mode"
        messages_mock.LEARN_MODE_STOP = "Exiting learn mode"
        messages_mock.APPLICATION_NO_NAME = "application with no name"
        messages_mock.shortcuts_found_orca = test_context.Mock(
            return_value="Found 25 Orca shortcuts"
        )
        messages_mock.shortcuts_found_app = test_context.Mock(
            return_value="Found 5 application shortcuts"
        )

        script_manager_mock = essential_modules["orca.script_manager"]
        script_instance = test_context.Mock()
        script_instance.present_message = test_context.Mock()
        script_instance.speak_message = test_context.Mock()
        script_instance.display_message = test_context.Mock()
        script_instance.speak_key_event = test_context.Mock()
        script_instance.phoneticSpellCurrentItem = test_context.Mock()
        script_instance.spell_phonetically = test_context.Mock()
        script_instance.app = test_context.Mock()
        script_instance.getDefaultKeyBindings = test_context.Mock(
            return_value=key_bindings_instance
        )
        script_instance.speech_generator = test_context.Mock()
        script_instance.speech_generator.voice = test_context.Mock(
            return_value=[test_context.Mock()]
        )

        for method_name in [
            "get_learn_mode_presenter",
            "get_where_am_i_presenter",
            "get_speech_and_verbosity_manager",
            "get_sleep_mode_manager",
            "get_flat_review_presenter",
            "get_flat_review_finder",
            "get_object_navigator",
            "get_caret_navigator",
            "get_structural_navigator",
            "get_table_navigator",
            "get_live_region_presenter",
            "get_system_information_presenter",
            "get_notification_presenter",
            "get_clipboard_presenter",
            "get_mouse_reviewer",
            "get_action_presenter",
            "get_debugging_tools_manager",
        ]:
            presenter_mock = test_context.Mock()
            presenter_mock.get_bindings = test_context.Mock(return_value=key_bindings_instance)
            getattr(script_instance, method_name).return_value = presenter_mock

        script_instance.get_app_key_bindings = test_context.Mock(return_value=key_bindings_instance)

        script_manager_mock.get_manager = test_context.Mock(return_value=test_context.Mock())
        script_manager_mock.get_manager.return_value.get_active_script = test_context.Mock(
            return_value=script_instance
        )

        settings_mock = essential_modules["orca.settings"]
        settings_mock.GENERAL_KEYBOARD_LAYOUT_DESKTOP = 1

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_mock.get_manager = test_context.Mock(
            return_value=settings_manager_instance
        )
        # Set keyboard layout setting
        settings_mock.keyboardLayout = 1

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.get_name = test_context.Mock(return_value="Test Application")

        time_mock = essential_modules["time"]
        time_mock.time = test_context.Mock(return_value=1234567890.0)

        speech_mock = essential_modules["orca.speech"]
        speech_mock.speak_key_event = test_context.Mock()

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.__init__."""

        self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        assert presenter._is_active is False
        assert presenter._gui is None

    def test_setup_commands(self, test_context: OrcaTestContext) -> None:
        """Test that commands are registered with CommandManager during setup."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter
        from orca import command_manager

        presenter = LearnModePresenter()
        presenter.set_up_commands()
        cmd_manager = command_manager.get_manager()
        cmd = cmd_manager.get_keyboard_command("enterLearnModeHandler")
        assert cmd is not None
        essential_modules["orca.debug"].print_message.assert_called()

    def test_start_when_inactive(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.start when learn mode is inactive."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        result = presenter.start()
        assert result is True
        assert presenter._is_active is True

        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        messages = essential_modules["orca.messages"]
        pres_manager.present_message.assert_called_with(messages.VERSION)
        pres_manager.speak_message.assert_called_with(messages.LEARN_MODE_START_SPEECH)
        pres_manager.display_message.assert_called_with(messages.LEARN_MODE_START_BRAILLE)
        input_manager = essential_modules["orca.input_event_manager"].get_manager.return_value
        input_manager.grab_keyboard.assert_called_with("Entering learn mode")

    @pytest.mark.parametrize(
        "is_active,script_provided,script_manager_returns_none,expected_debug_called",
        [
            (True, False, False, True),  # Already active
            (False, True, False, False),  # With specific script
            (False, False, True, False),  # No script from manager
        ],
    )
    def test_start_scenarios(
        self,
        test_context: OrcaTestContext,
        is_active: bool,
        script_provided: bool,
        script_manager_returns_none: bool,
        expected_debug_called: bool,
    ) -> None:
        """Test LearnModePresenter.start under different scenarios."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        if script_manager_returns_none:
            essential_modules[
                "orca.script_manager"
            ].get_manager.return_value.get_active_script.return_value = None
        presenter = LearnModePresenter()
        presenter._is_active = is_active
        script = test_context.Mock() if script_provided else None
        if script_provided and script is not None:
            script.present_message = test_context.Mock()
            script.speak_message = test_context.Mock()
            script.display_message = test_context.Mock()
        result = presenter.start(_script=script)
        assert result is True
        assert presenter._is_active is True
        if expected_debug_called:
            essential_modules["orca.debug"].print_message.assert_called()
        if script_provided and script is not None:
            pres_manager = essential_modules["orca.presentation_manager"].get_manager()
            pres_manager.present_message.assert_called_with(
                essential_modules["orca.messages"].VERSION
            )

    def test_quit_when_active(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.quit when learn mode is active."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        presenter._is_active = True
        result = presenter.quit()
        assert result is True
        assert presenter._is_active is False
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        messages = essential_modules["orca.messages"]
        pres_manager.present_message.assert_called_with(messages.LEARN_MODE_STOP)
        input_manager = essential_modules["orca.input_event_manager"].get_manager.return_value
        input_manager.ungrab_keyboard.assert_called_with("Exiting learn mode")

    @pytest.mark.parametrize(
        "is_active,script_provided,script_manager_returns_none,expected_debug_called",
        [
            (False, False, False, True),  # Already inactive
            (True, True, False, False),  # With specific script
            (True, False, True, False),  # No script from manager
        ],
    )
    def test_quit_scenarios(
        self,
        test_context: OrcaTestContext,
        is_active: bool,
        script_provided: bool,
        script_manager_returns_none: bool,
        expected_debug_called: bool,
    ) -> None:
        """Test LearnModePresenter.quit under different scenarios."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        if script_manager_returns_none:
            essential_modules[
                "orca.script_manager"
            ].get_manager.return_value.get_active_script.return_value = None
        presenter = LearnModePresenter()
        presenter._is_active = is_active
        script = test_context.Mock() if script_provided else None
        if script_provided and script is not None:
            script.present_message = test_context.Mock()
        result = presenter.quit(_script=script)
        assert result is True
        expected_final_state = False if is_active else False
        assert presenter._is_active == expected_final_state
        if expected_debug_called:
            essential_modules["orca.debug"].print_message.assert_called()
        if script_provided and script is not None:
            pres_manager = essential_modules["orca.presentation_manager"].get_manager()
            pres_manager.present_message.assert_called_with(
                essential_modules["orca.messages"].LEARN_MODE_STOP
            )

    def test_handle_event_no_script(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event when no active script."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = None
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        result = presenter.handle_event(event, None)
        assert result is False

    def test_handle_event_basic_key(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event with basic key event."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        event.keyval_name = "a"
        event.modifiers = 0
        result = presenter.handle_event(event, None)
        assert result is True
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.present_key_event.assert_called()

    def test_handle_event_printable_double_click(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event with printable key double-click."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        event.keyval_name = "a"
        event.is_printable_key.return_value = True
        event.get_click_count.return_value = 2
        event.get_key_name.return_value = "a"
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.spell_phonetically.reset_mock()
        result = presenter.handle_event(event, None)
        assert result is True
        pres_manager.spell_phonetically.assert_called_with("a")

    @pytest.mark.parametrize(
        "key_name,method_name,has_modifiers",
        [
            ("Escape", "quit", False),
            ("F1", "show_help", True),
            ("F2", "list_orca_shortcuts", True),
        ],
    )
    def test_handle_event_special_keys(
        self, test_context: OrcaTestContext, key_name: str, method_name: str, has_modifiers: bool
    ) -> None:
        """Test LearnModePresenter.handle_event with special function keys."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        event.keyval_name = key_name
        if has_modifiers:
            event.modifiers = 0
        script_manager = essential_modules["orca.script_manager"]
        script_instance = script_manager.get_manager.return_value.get_active_script.return_value
        mock_method = test_context.patch_object(presenter, method_name, return_value=True)
        result = presenter.handle_event(event, None)
        assert result is True
        mock_method.assert_called_with(script_instance, event)

    def test_handle_event_with_command(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event presents command description."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        event.keyval_name = "a"
        command = test_context.Mock()
        command.get_description.return_value = "Test command"
        result = presenter.handle_event(event, command)
        assert result is True
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.present_message.assert_called_with("Test command")

    def test_handle_event_command_no_description(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event with command without description."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        event.keyval_name = "a"
        command = test_context.Mock()
        command.get_description.return_value = ""
        result = presenter.handle_event(event, command)
        assert result is True
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.present_message.assert_not_called()

    def test_list_orca_shortcuts_events(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.list_orca_shortcuts with F2 event."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        mock_keybinding = test_context.Mock()
        mock_keybinding.handler = test_context.Mock()
        mock_keybinding.handler.description = "Test command"

        mock_command = test_context.Mock()
        mock_command.get_keybinding.return_value = mock_keybinding
        mock_command.get_group_label.return_value = "Test Group"

        command_manager_mock = essential_modules["orca.command_manager"]
        command_manager_mock.get_manager.return_value.get_all_keyboard_commands.return_value = (
            mock_command,
        )

        script_manager = essential_modules["orca.script_manager"]
        script = script_manager.get_manager.return_value.get_active_script.return_value

        presenter = LearnModePresenter()
        event = test_context.Mock()
        event.keyval_name = "F2"
        mock_quit = test_context.patch_object(presenter, "quit")
        mock_gui = test_context.patch("orca.learn_mode_presenter.CommandListGUI")
        result = presenter.list_orca_shortcuts(script, event)
        assert result is True
        mock_quit.assert_called_with(script, event)
        mock_gui.assert_called()

    def test_show_help_default_page(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.show_help with default page."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        script_manager = essential_modules["orca.script_manager"]
        script = script_manager.get_manager.return_value.get_active_script.return_value
        event = test_context.Mock()
        mock_quit = test_context.patch_object(presenter, "quit")
        result = presenter.show_help(script, event)
        assert result is True
        mock_quit.assert_called_with(script, event)
        gi_repository = essential_modules["gi.repository"]
        gi_repository.Gtk.show_uri.assert_called()

    def test_handle_braille_event_no_command(self, test_context: OrcaTestContext) -> None:
        """Test handle_braille_event with no command returns True (don't execute)."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        script_manager = essential_modules["orca.script_manager"]
        script = script_manager.get_manager.return_value.get_active_script.return_value
        event = test_context.Mock()
        result = presenter.handle_braille_event(script, event, None)
        assert result is True

    def test_handle_braille_event_with_command(self, test_context: OrcaTestContext) -> None:
        """Test handle_braille_event speaks description and checks executes_in_learn_mode."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        script_manager = essential_modules["orca.script_manager"]
        script = script_manager.get_manager.return_value.get_active_script.return_value
        event = test_context.Mock()
        command = test_context.Mock()
        command.get_description.return_value = "Pan braille left"
        command.executes_in_learn_mode.return_value = False
        result = presenter.handle_braille_event(script, event, command)
        assert result is True  # Don't execute
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.speak_message.assert_called_with("Pan braille left")

    def test_handle_braille_event_pan_command(self, test_context: OrcaTestContext) -> None:
        """Test handle_braille_event returns False for pan commands (should execute)."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        script_manager = essential_modules["orca.script_manager"]
        script = script_manager.get_manager.return_value.get_active_script.return_value
        event = test_context.Mock()
        command = test_context.Mock()
        command.get_description.return_value = "Pan braille left"
        command.executes_in_learn_mode.return_value = True
        result = presenter.handle_braille_event(script, event, command)
        assert result is False  # Should execute
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.speak_message.assert_called_with("Pan braille left")
