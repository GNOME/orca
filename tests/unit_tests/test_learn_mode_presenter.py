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
            "orca.input_event_manager",
            "time",
            "orca.speech",
            "orca.speech_generator",
            "orca.generator",
            "orca.ax_hypertext"
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        gi_repository_mock = essential_modules["gi.repository"]
        gdk_mock = test_context.Mock()
        gdk_mock.Screen = test_context.Mock()
        gdk_mock.Screen.get_default = test_context.Mock(
            return_value=test_context.Mock()
        )

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
        input_event_manager_mock.get_manager = test_context.Mock(
            return_value=manager_instance
        )
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
            return_value=[test_context.Mock()])

        for method_name in [
            "get_learn_mode_presenter",
            "get_where_am_i_presenter",
            "get_speech_and_verbosity_manager",
            "get_sleep_mode_manager",
            "get_flat_review_presenter",
            "get_flat_review_finder",
            "get_object_navigator",
            "get_structural_navigator",
            "get_table_navigator",
            "get_system_information_presenter",
            "get_notification_presenter",
            "get_clipboard_presenter",
            "get_bookmarks",
            "get_mouse_reviewer",
            "get_action_presenter",
            "get_debugging_tools_manager",
        ]:
            presenter_mock = test_context.Mock()
            presenter_mock.get_bindings = test_context.Mock(
                return_value=key_bindings_instance
            )
            getattr(script_instance, method_name).return_value = presenter_mock

        script_instance.get_app_key_bindings = test_context.Mock(
            return_value=key_bindings_instance
        )

        script_manager_mock.get_manager = test_context.Mock(
            return_value=test_context.Mock()
        )
        script_manager_mock.get_manager.return_value.get_active_script = test_context.Mock(
            return_value=script_instance
        )

        settings_mock = essential_modules["orca.settings"]
        settings_mock.GENERAL_KEYBOARD_LAYOUT_DESKTOP = 1

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_instance.get_setting = test_context.Mock(return_value=1)
        settings_manager_mock.get_manager = test_context.Mock(
            return_value=settings_manager_instance
        )

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
        assert presenter._handlers is not None
        assert presenter._bindings is not None

    def test_get_bindings_and_handlers(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.get_bindings and get_handlers."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()

        bindings = presenter.get_bindings()
        assert bindings is not None
        essential_modules["orca.keybindings"].KeyBindings.assert_called()

        bindings = presenter.get_bindings(refresh=True, is_desktop=True)
        assert bindings is not None
        essential_modules["orca.debug"].print_message.assert_called()

        handlers = presenter.get_handlers()
        assert handlers is not None
        assert "enterLearnModeHandler" in handlers

    def test_setup_handlers(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter._setup_handlers."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        presenter._setup_handlers()
        assert "enterLearnModeHandler" in presenter._handlers
        essential_modules["orca.input_event"].InputEventHandler.assert_called()
        essential_modules["orca.debug"].print_message.assert_called()

    def test_setup_bindings(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter._setup_bindings."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        presenter._setup_bindings()
        essential_modules["orca.keybindings"].KeyBindings.assert_called()
        essential_modules["orca.keybindings"].KeyBinding.assert_called()
        essential_modules["orca.debug"].print_message.assert_called()

    def test_start_when_inactive(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.start when learn mode is inactive."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        result = presenter.start()
        assert result is True
        assert presenter._is_active is True

        script_manager = essential_modules["orca.script_manager"]
        script = script_manager.get_manager.return_value.get_active_script.return_value
        messages = essential_modules["orca.messages"]
        script.present_message.assert_called_with(messages.VERSION)
        script.speak_message.assert_called_with(messages.LEARN_MODE_START_SPEECH)
        script.display_message.assert_called_with(messages.LEARN_MODE_START_BRAILLE)
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
        result = presenter.start(script=script)
        assert result is True
        assert presenter._is_active is True
        if expected_debug_called:
            essential_modules["orca.debug"].print_message.assert_called()
        if script_provided and script is not None:
            script.present_message.assert_called_with(essential_modules["orca.messages"].VERSION)

    def test_quit_when_active(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.quit when learn mode is active."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        presenter._is_active = True
        result = presenter.quit()
        assert result is True
        assert presenter._is_active is False
        script_manager = essential_modules["orca.script_manager"]
        script = script_manager.get_manager.return_value.get_active_script.return_value
        messages = essential_modules["orca.messages"]
        script.present_message.assert_called_with(messages.LEARN_MODE_STOP)
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
        result = presenter.quit(script=script)
        assert result is True
        expected_final_state = False if is_active else False
        assert presenter._is_active == expected_final_state
        if expected_debug_called:
            essential_modules["orca.debug"].print_message.assert_called()
        if script_provided and script is not None:
            script.present_message.assert_called_with(
                essential_modules["orca.messages"].LEARN_MODE_STOP
            )

    def test_handle_event_when_inactive(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event when learn mode is inactive."""

        self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        event = test_context.Mock()
        result = presenter.handle_event(event)
        assert result is False

    def test_handle_event_non_keyboard_event(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event with non-keyboard event."""

        self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        presenter._is_active = True
        event = test_context.Mock()
        result = presenter.handle_event(event)
        assert result is False

    def test_handle_event_no_script(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event when no active script."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = None
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        presenter._is_active = True
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        result = presenter.handle_event(event)
        assert result is False

    def test_handle_event_basic_key(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event with basic key event."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        presenter._is_active = True
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        event.keyval_name = "a"
        event.modifiers = 0
        result = presenter.handle_event(event)
        assert result is True
        speech_mock = essential_modules["orca.speech"]
        speech_mock.speak_key_event.assert_called()

    def test_handle_event_printable_double_click(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event with printable key double-click."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        presenter._is_active = True
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        event.keyval_name = "a"
        event.is_printable_key.return_value = True
        event.get_click_count.return_value = 2
        event.get_handler.return_value = None
        event.get_key_name.return_value = "a"
        result = presenter.handle_event(event)
        assert result is True
        script_manager = essential_modules["orca.script_manager"]
        script = script_manager.get_manager.return_value.get_active_script.return_value
        script.spell_phonetically.assert_called_with("a")

    @pytest.mark.parametrize(
        "key_name,method_name,has_modifiers",
        [
            ("Escape", "quit", False),
            ("F1", "show_help", True),
            ("F2", "list_orca_shortcuts", True),
            ("F3", "list_orca_shortcuts", True),
        ],
    )
    def test_handle_event_special_keys(
        self, test_context: OrcaTestContext, key_name: str, method_name: str, has_modifiers: bool
    ) -> None:
        """Test LearnModePresenter.handle_event with special function keys."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        presenter._is_active = True
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        event.keyval_name = key_name
        if has_modifiers:
            event.modifiers = 0
        script_manager = essential_modules["orca.script_manager"]
        script_instance = script_manager.get_manager.return_value.get_active_script.return_value
        mock_method = test_context.patch_object(presenter, method_name, return_value=True)
        result = presenter.handle_event(event)
        assert result is True
        mock_method.assert_called_with(script_instance, event)

    def test_handle_event_with_present_command(self, test_context: OrcaTestContext) -> None:
        """Test LearnModePresenter.handle_event calls present_command."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        presenter._is_active = True
        keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
        event = keyboard_event_cls()
        event.keyval_name = "a"
        mock_present = test_context.patch_object(presenter, "present_command", return_value=True)
        result = presenter.handle_event(event)
        assert result is True
        mock_present.assert_called_with(event)

    @pytest.mark.parametrize(
        "is_keyboard_event,has_handler,handler_enabled,has_description,has_script,"
        "should_present_message",
        [
            (False, False, False, False, True, False),  # Non-keyboard event
            (True, False, False, False, True, False),  # No handler
            (True, True, True, False, True, False),  # Handler with no description
            (True, True, False, True, True, False),  # Disabled handler
            (True, True, True, True, True, True),  # Enabled handler with description
            (True, True, True, True, False, False),  # No active script
        ],
    )
    def test_present_command_scenarios(
        self,
        test_context: OrcaTestContext,
        is_keyboard_event: bool,
        has_handler: bool,
        handler_enabled: bool,
        has_description: bool,
        has_script: bool,
        should_present_message: bool,
    ) -> None:
        """Test LearnModePresenter.present_command under different scenarios."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        if not has_script:
            essential_modules[
                "orca.script_manager"
            ].get_manager.return_value.get_active_script.return_value = None
        from orca.learn_mode_presenter import LearnModePresenter

        presenter = LearnModePresenter()
        if is_keyboard_event:
            keyboard_event_cls = essential_modules["orca.input_event"].KeyboardEvent
            event = keyboard_event_cls()
            if has_handler:
                handler = test_context.Mock()
                handler.learn_mode_enabled = handler_enabled
                handler.description = "Test command" if has_description else None
                event.get_handler.return_value = handler
            else:
                event.get_handler.return_value = None
        else:
            event = test_context.Mock()
        result = presenter.present_command(event)
        assert result is True
        if should_present_message:
            script_manager = essential_modules["orca.script_manager"]
            script = script_manager.get_manager.return_value.get_active_script.return_value
            script.present_message.assert_called_with("Test command")

    @pytest.mark.parametrize(
        "key_name,is_f3_event",
        [
            ("F2", False),
            ("F3", True),
        ],
    )
    def test_list_orca_shortcuts_events(
        self, test_context: OrcaTestContext, key_name: str, is_f3_event: bool
    ) -> None:
        """Test LearnModePresenter.list_orca_shortcuts with F2/F3 events."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.learn_mode_presenter import LearnModePresenter

        script_manager = essential_modules["orca.script_manager"]
        script = script_manager.get_manager.return_value.get_active_script.return_value
        if not is_f3_event:
            default_kb = test_context.Mock()
            default_kb.get_bound_bindings.return_value = []
            script.get_default_keybindings_deprecated.return_value = default_kb
            learn_presenter = test_context.Mock()
            learn_kb = test_context.Mock()
            learn_kb.get_bound_bindings.return_value = []
            learn_presenter.get_bindings.return_value = learn_kb
            script.get_learn_mode_presenter.return_value = learn_presenter
            where_presenter = test_context.Mock()
            where_kb = test_context.Mock()
            where_kb.get_bound_bindings.return_value = []
            where_presenter.get_bindings.return_value = where_kb
            script.get_where_am_i_presenter.return_value = where_presenter
            speech_manager = test_context.Mock()
            speech_kb = test_context.Mock()
            speech_kb.get_bound_bindings.return_value = []
            speech_manager.get_bindings.return_value = speech_kb
            script.get_speech_and_verbosity_manager.return_value = speech_manager
            sleep_manager = test_context.Mock()
            sleep_kb = test_context.Mock()
            sleep_kb.get_bound_bindings.return_value = []
            sleep_manager.get_bindings.return_value = sleep_kb
            script.get_sleep_mode_manager.return_value = sleep_manager
            flat_review_presenter = test_context.Mock()
            flat_review_kb = test_context.Mock()
            flat_review_kb.get_bound_bindings.return_value = []
            flat_review_presenter.get_bindings.return_value = flat_review_kb
            script.get_flat_review_presenter.return_value = flat_review_presenter
            flat_review_finder = test_context.Mock()
            flat_review_finder_kb = test_context.Mock()
            flat_review_finder_kb.get_bound_bindings.return_value = []
            flat_review_finder.get_bindings.return_value = flat_review_finder_kb
            script.get_flat_review_finder.return_value = flat_review_finder
            object_navigator = test_context.Mock()
            object_navigator_kb = test_context.Mock()
            object_navigator_kb.get_bound_bindings.return_value = []
            object_navigator.get_bindings.return_value = object_navigator_kb
            script.get_object_navigator.return_value = object_navigator
            caret_navigator = test_context.Mock()
            caret_navigator_kb = test_context.Mock()
            caret_navigator_kb.get_bound_bindings.return_value = []
            caret_navigator.get_bindings.return_value = caret_navigator_kb
            script.get_caret_navigator.return_value = caret_navigator
        else:
            key_binding_mock = test_context.Mock()
            key_binding_mock.handler = test_context.Mock()
            key_binding_mock.handler.description = TEST_COMMAND_DESCRIPTION
            key_binding_mock.as_string = test_context.Mock(return_value="Ctrl+t")
            app_bindings_mock = test_context.Mock()
            app_bindings_mock.get_bound_bindings = test_context.Mock(
                return_value=[key_binding_mock]
            )
            script.get_app_key_bindings.return_value = app_bindings_mock
        presenter = LearnModePresenter()
        event = test_context.Mock()
        event.keyval_name = key_name
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
