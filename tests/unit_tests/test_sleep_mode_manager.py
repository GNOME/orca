# Unit tests for sleep_mode_manager.py SleepModeManager class methods.
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

# pylint: disable=too-many-public-methods
# pylint: disable=wrong-import-position
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=unused-argument
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-statements
# pylint: disable=unused-variable

"""Unit tests for sleep_mode_manager.py SleepModeManager class methods."""

from __future__ import annotations

import sys
from unittest.mock import Mock

import pytest

from .conftest import clean_module_cache


@pytest.fixture(name="mock_sleep_dependencies")
def _mock_sleep_dependencies(monkeypatch, mock_orca_dependencies):
    """Create mocks for sleep_mode_manager dependencies."""

    # Create additional mocks not in the standard fixture
    braille_mock = Mock()
    braille_mock.clear = Mock()

    cmdnames_mock = Mock()
    cmdnames_mock.TOGGLE_SLEEP_MODE = "Toggle sleep mode for the current application"

    dbus_service_mock = Mock()
    controller_mock = Mock()
    controller_mock.register_decorated_module = Mock()
    dbus_service_mock.get_remote_controller = Mock(return_value=controller_mock)
    dbus_service_mock.command = lambda func: func  # Mock decorator

    input_event_mock = Mock()
    input_event_handler_mock = Mock()
    input_event_mock.InputEventHandler = Mock(return_value=input_event_handler_mock)

    keybindings_mock = Mock()
    key_bindings_instance = Mock()
    key_bindings_instance.is_empty = Mock(return_value=False)
    key_bindings_instance.remove_key_grabs = Mock()
    key_bindings_instance.add = Mock()
    keybindings_mock.KeyBindings = Mock(return_value=key_bindings_instance)
    keybindings_mock.KeyBinding = Mock()
    keybindings_mock.DEFAULT_MODIFIER_MASK = 1
    keybindings_mock.SHIFT_ALT_CTRL_MODIFIER_MASK = 15

    messages_mock = Mock()
    messages_mock.SLEEP_MODE_ENABLED_FOR = "Sleep mode enabled for %s."
    messages_mock.SLEEP_MODE_DISABLED_FOR = "Sleep mode disabled for %s."

    script_manager_mock = Mock()
    script_manager_instance = Mock()
    script_manager_mock.get_manager = Mock(return_value=script_manager_instance)

    # Mock AXObject.get_name globally to return a string
    ax_object_mock = Mock()
    ax_object_mock.get_name = Mock(return_value="TestApp")

    # Configure debug mock from mock_orca_dependencies to prevent debugFile issues
    mock_orca_dependencies.debug.debugFile = None

    # Use monkeypatch's setitem which properly cleans up after each test
    monkeypatch.setitem(sys.modules, "orca.ax_object", ax_object_mock)
    monkeypatch.setitem(sys.modules, "orca.braille", braille_mock)
    monkeypatch.setitem(sys.modules, "orca.cmdnames", cmdnames_mock)
    monkeypatch.setitem(sys.modules, "orca.dbus_service", dbus_service_mock)
    monkeypatch.setitem(sys.modules, "orca.input_event", input_event_mock)
    monkeypatch.setitem(sys.modules, "orca.keybindings", keybindings_mock)
    monkeypatch.setitem(sys.modules, "orca.messages", messages_mock)
    monkeypatch.setitem(sys.modules, "orca.script_manager", script_manager_mock)

    return {
        "ax_object": ax_object_mock,
        "braille": braille_mock,
        "cmdnames": cmdnames_mock,
        "controller": controller_mock,
        "dbus_service": dbus_service_mock,
        "input_event": input_event_mock,
        "input_event_handler": input_event_handler_mock,
        "keybindings": keybindings_mock,
        "key_bindings_instance": key_bindings_instance,
        "messages": messages_mock,
        "script_manager": script_manager_mock,
        "script_manager_instance": script_manager_instance,
    }


@pytest.mark.unit
class TestSleepModeManager:
    """Test SleepModeManager class methods."""

    def test_init(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test SleepModeManager initialization."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        assert manager._handlers is not None
        assert manager._bindings is not None
        assert not manager._apps
        mock_sleep_dependencies["keybindings"].KeyBindings.assert_called()

        # Check that D-Bus service is available (may not be called in all test contexts)
        assert mock_sleep_dependencies["dbus_service"] is not None
        assert mock_sleep_dependencies["controller"] is not None

    def test_get_bindings_refresh_true_desktop_true(
        self, mock_sleep_dependencies, mock_orca_dependencies
    ):
        """Test get_bindings with refresh=True and is_desktop=True."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        bindings = manager.get_bindings(refresh=True, is_desktop=True)

        assert bindings is not None
        mock_orca_dependencies.debug.print_message.assert_any_call(
            mock_orca_dependencies.debug.LEVEL_INFO,
            "SLEEP MODE MANAGER: Refreshing bindings. Is desktop: True",
            True,
        )

    def test_get_bindings_refresh_true_desktop_false(
        self, mock_sleep_dependencies, mock_orca_dependencies
    ):
        """Test get_bindings with refresh=True and is_desktop=False."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        bindings = manager.get_bindings(refresh=True, is_desktop=False)

        assert bindings is not None
        mock_orca_dependencies.debug.print_message.assert_any_call(
            mock_orca_dependencies.debug.LEVEL_INFO,
            "SLEEP MODE MANAGER: Refreshing bindings. Is desktop: False",
            True,
        )

    def test_get_bindings_empty_bindings(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test get_bindings when bindings are empty."""

        # Configure empty bindings
        key_bindings_instance = mock_sleep_dependencies["key_bindings_instance"]
        key_bindings_instance.is_empty.return_value = True

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        bindings = manager.get_bindings(refresh=False)

        assert bindings is not None
        key_bindings_instance.is_empty.assert_called()

    def test_get_bindings_not_empty(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test get_bindings when bindings are not empty."""

        # Configure non-empty bindings
        key_bindings_instance = mock_sleep_dependencies["key_bindings_instance"]
        key_bindings_instance.is_empty.return_value = False

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        bindings = manager.get_bindings(refresh=False)

        assert bindings == key_bindings_instance
        key_bindings_instance.is_empty.assert_called()

    def test_get_handlers_refresh_true(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test get_handlers with refresh=True."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        handlers = manager.get_handlers(refresh=True)

        assert handlers is not None
        mock_orca_dependencies.debug.print_message.assert_any_call(
            mock_orca_dependencies.debug.LEVEL_INFO,
            "SLEEP MODE MANAGER: Refreshing handlers.",
            True,
        )

    def test_get_handlers_refresh_false(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test get_handlers with refresh=False."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        initial_handlers = manager._handlers

        handlers = manager.get_handlers(refresh=False)

        assert handlers == initial_handlers

    def test_is_active_for_app_with_active_app(
        self, mock_sleep_dependencies, mock_orca_dependencies
    ):
        """Test is_active_for_app returns True for active app."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        mock_app = Mock()
        app_hash = hash(mock_app)
        manager._apps.append(app_hash)

        # Reset debug mock to track calls after initialization
        mock_orca_dependencies.debug.print_tokens.reset_mock()

        result = manager.is_active_for_app(mock_app)

        assert result is True
        mock_orca_dependencies.debug.print_tokens.assert_called_with(
            mock_orca_dependencies.debug.LEVEL_INFO,
            ["SLEEP MODE MANAGER: Is active for", mock_app],
            True,
        )

    def test_is_active_for_app_with_inactive_app(
        self, mock_sleep_dependencies, mock_orca_dependencies
    ):
        """Test is_active_for_app returns False for inactive app."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        mock_app = Mock()

        result = manager.is_active_for_app(mock_app)

        assert result is False
        mock_orca_dependencies.debug.print_tokens.assert_not_called()

    def test_is_active_for_app_with_none_app(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test is_active_for_app returns False for None app."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        result = manager.is_active_for_app(None)

        assert result is False

    def test_setup_handlers(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test _setup_handlers method."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        manager._setup_handlers()

        assert "toggle_sleep_mode" in manager._handlers
        expected_handler = mock_sleep_dependencies["input_event_handler"]
        assert manager._handlers["toggle_sleep_mode"] == expected_handler
        input_event = mock_sleep_dependencies["input_event"]
        input_event.InputEventHandler.assert_called_with(
            manager.toggle_sleep_mode, "Toggle sleep mode for the current application"
        )

    def test_setup_bindings(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test _setup_bindings method."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        manager._setup_bindings()

        # Check that KeyBinding was created with correct parameters
        mock_sleep_dependencies["keybindings"].KeyBinding.assert_called_with(
            "q",
            1,  # DEFAULT_MODIFIER_MASK
            15,  # SHIFT_ALT_CTRL_MODIFIER_MASK
            manager._handlers["toggle_sleep_mode"],
        )

        # Check that binding was added
        key_bindings_instance = mock_sleep_dependencies["key_bindings_instance"]
        key_bindings_instance.add.assert_called()

    def test_toggle_sleep_mode_no_script(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test toggle_sleep_mode with no script."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        result = manager.toggle_sleep_mode(None)

        assert result is True

    def test_toggle_sleep_mode_script_no_app(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test toggle_sleep_mode with script but no app."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()

        mock_script = Mock()
        mock_script.app = None

        result = manager.toggle_sleep_mode(mock_script)

        assert result is True

    def test_toggle_sleep_mode_enable_with_event_and_notification(
        self, mock_sleep_dependencies, mock_orca_dependencies
    ):
        """Test toggle_sleep_mode enabling sleep mode with event and notification."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager
        from unittest.mock import patch

        manager = SleepModeManager()

        mock_script = Mock()
        mock_app = Mock()
        mock_script.app = mock_app
        mock_event = Mock()

        # Mock script_manager methods with patch to ensure test isolation
        script_manager_instance = mock_sleep_dependencies["script_manager_instance"]
        sleep_script = Mock()

        script_manager_instance.get_or_create_sleep_mode_script = Mock(return_value=sleep_script)
        with patch(
            "orca.sleep_mode_manager.script_manager.get_manager",
            return_value=script_manager_instance,
        ):
            result = manager.toggle_sleep_mode(mock_script, mock_event, notify_user=True)

            assert result is True
            assert hash(mock_app) in manager._apps

            # Check braille was cleared
            mock_sleep_dependencies["braille"].clear.assert_called()

            # Check user notification was called
            mock_script.present_message.assert_called_once()
            # Check that the call contains the expected message pattern
            call_args = mock_script.present_message.call_args[0][0]
            assert "Sleep mode enabled for" in call_args

            # Check script manager calls
            script_manager_instance.get_or_create_sleep_mode_script.assert_called_with(mock_app)
            script_manager_instance.set_active_script.assert_called_with(
                sleep_script, "Sleep mode toggled on"
            )

    def test_toggle_sleep_mode_enable_without_notification(
        self, mock_sleep_dependencies, mock_orca_dependencies
    ):
        """Test toggle_sleep_mode enabling sleep mode without notification."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager
        from unittest.mock import patch

        manager = SleepModeManager()

        mock_script = Mock()
        mock_app = Mock()
        mock_script.app = mock_app
        mock_event = Mock()

        # Mock script_manager methods with patch to ensure test isolation
        script_manager_instance = mock_sleep_dependencies["script_manager_instance"]
        sleep_script = Mock()

        script_manager_instance.get_or_create_sleep_mode_script = Mock(return_value=sleep_script)
        with patch(
            "orca.sleep_mode_manager.script_manager.get_manager",
            return_value=script_manager_instance,
        ):
            result = manager.toggle_sleep_mode(mock_script, mock_event, notify_user=False)

            assert result is True
            assert hash(mock_app) in manager._apps

            # Check braille was cleared
            mock_sleep_dependencies["braille"].clear.assert_called()

            # Check user notification was not called
            mock_script.present_message.assert_not_called()

            # Check script manager calls
            script_manager_instance.get_or_create_sleep_mode_script.assert_called_with(mock_app)
            script_manager_instance.set_active_script.assert_called_with(
                sleep_script, "Sleep mode toggled on"
            )

    def test_toggle_sleep_mode_disable_with_notification(
        self, mock_sleep_dependencies, mock_orca_dependencies
    ):
        """Test toggle_sleep_mode disabling sleep mode with notification."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager
        from unittest.mock import patch

        manager = SleepModeManager()

        mock_script = Mock()
        mock_app = Mock()
        mock_script.app = mock_app
        mock_event = Mock()

        # Pre-configure app as active in sleep mode
        app_hash = hash(mock_app)
        manager._apps.append(app_hash)

        # Mock script_manager methods with patch to ensure test isolation
        script_manager_instance = mock_sleep_dependencies["script_manager_instance"]
        new_script = Mock()

        script_manager_instance.get_script = Mock(return_value=new_script)
        with patch(
            "orca.sleep_mode_manager.script_manager.get_manager",
            return_value=script_manager_instance,
        ):
            result = manager.toggle_sleep_mode(mock_script, mock_event, notify_user=True)

            assert result is True
            assert app_hash not in manager._apps

            # Check script manager calls
            script_manager_instance.get_script.assert_called_with(mock_app)
            script_manager_instance.set_active_script.assert_called_with(
                new_script, "Sleep mode toggled off"
            )

            # Check user notification was called
            new_script.present_message.assert_called_once()
            # Check that the call contains the expected message pattern
            call_args = new_script.present_message.call_args[0][0]
            assert "Sleep mode disabled for" in call_args

    def test_toggle_sleep_mode_disable_without_notification(
        self, mock_sleep_dependencies, mock_orca_dependencies
    ):
        """Test toggle_sleep_mode disabling sleep mode without notification."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import SleepModeManager
        from unittest.mock import patch

        manager = SleepModeManager()

        mock_script = Mock()
        mock_app = Mock()
        mock_script.app = mock_app
        mock_event = Mock()

        # Pre-configure app as active in sleep mode
        app_hash = hash(mock_app)
        manager._apps.append(app_hash)

        # Mock script_manager methods with patch to ensure test isolation
        script_manager_instance = mock_sleep_dependencies["script_manager_instance"]
        new_script = Mock()

        script_manager_instance.get_script = Mock(return_value=new_script)
        with patch(
            "orca.sleep_mode_manager.script_manager.get_manager",
            return_value=script_manager_instance,
        ):
            result = manager.toggle_sleep_mode(mock_script, mock_event, notify_user=False)

            assert result is True
            assert app_hash not in manager._apps

            # Check script manager calls
            script_manager_instance.get_script.assert_called_with(mock_app)
            script_manager_instance.set_active_script.assert_called_with(
                new_script, "Sleep mode toggled off"
            )

            # Check user notification was not called
            new_script.present_message.assert_not_called()

    def test_get_manager_returns_singleton(self, mock_sleep_dependencies, mock_orca_dependencies):
        """Test get_manager returns the singleton instance."""

        clean_module_cache("orca.sleep_mode_manager")
        from orca.sleep_mode_manager import get_manager

        manager1 = get_manager()
        manager2 = get_manager()

        assert manager1 is manager2
        assert manager1 is not None
