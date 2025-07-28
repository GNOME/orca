# Unit tests for bypass_mode_manager.py BypassModeManager class methods.
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

"""Unit tests for bypass_mode_manager.py BypassModeManager class methods."""

from __future__ import annotations

import sys
from unittest.mock import Mock

import pytest

from .conftest import clean_module_cache


@pytest.fixture(name="mock_bypass_dependencies")
def _mock_bypass_dependencies(monkeypatch, mock_orca_dependencies):
    """Create mocks for bypass_mode_manager dependencies."""

    # Create additional mocks not in the standard fixture
    cmdnames_mock = Mock()
    cmdnames_mock.BYPASS_MODE_TOGGLE = "Toggle all Orca command keys"

    input_event_mock = Mock()
    input_event_handler_mock = Mock()
    input_event_mock.InputEventHandler = Mock(return_value=input_event_handler_mock)

    keybindings_mock = Mock()
    key_bindings_instance = Mock()
    key_bindings_instance.is_empty = Mock(return_value=False)
    key_bindings_instance.key_bindings = []
    key_bindings_instance.add = Mock()
    keybindings_mock.KeyBindings = Mock(return_value=key_bindings_instance)
    keybindings_mock.KeyBinding = Mock()
    keybindings_mock.DEFAULT_MODIFIER_MASK = 1
    keybindings_mock.ALT_MODIFIER_MASK = 2

    messages_mock = Mock()
    messages_mock.BYPASS_MODE_ENABLED = "Orca command keys off."
    messages_mock.BYPASS_MODE_DISABLED = "Orca command keys on."

    orca_modifier_manager_mock = Mock()
    modifier_manager_instance = Mock()
    modifier_manager_get_manager = Mock(return_value=modifier_manager_instance)
    orca_modifier_manager_mock.get_manager = modifier_manager_get_manager

    settings_manager_mock = Mock()
    settings_manager_instance = Mock()
    override_method = Mock(return_value=key_bindings_instance)
    settings_manager_instance.override_key_bindings = override_method
    settings_manager_mock.get_manager = Mock(return_value=settings_manager_instance)

    monkeypatch.setitem(sys.modules, "orca.cmdnames", cmdnames_mock)
    monkeypatch.setitem(sys.modules, "orca.input_event", input_event_mock)
    monkeypatch.setitem(sys.modules, "orca.keybindings", keybindings_mock)
    monkeypatch.setitem(sys.modules, "orca.messages", messages_mock)
    monkeypatch.setitem(sys.modules, "orca.orca_modifier_manager", orca_modifier_manager_mock)
    monkeypatch.setitem(sys.modules, "orca.settings_manager", settings_manager_mock)

    return {
        "cmdnames": cmdnames_mock,
        "input_event": input_event_mock,
        "input_event_handler": input_event_handler_mock,
        "keybindings": keybindings_mock,
        "key_bindings_instance": key_bindings_instance,
        "messages": messages_mock,
        "orca_modifier_manager": orca_modifier_manager_mock,
        "modifier_manager_instance": modifier_manager_instance,
        "settings_manager": settings_manager_mock,
        "settings_manager_instance": settings_manager_instance,
    }


@pytest.mark.unit
class TestBypassModeManager:
    """Test BypassModeManager class methods."""

    def test_init(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test BypassModeManager initialization."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        assert manager._is_active is False
        assert manager._handlers is not None
        assert manager._bindings is not None
        mock_bypass_dependencies["keybindings"].KeyBindings.assert_called()

    def test_get_bindings_refresh_true(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test get_bindings with refresh=True."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        # Reset debug mock to track calls after initialization
        mock_orca_dependencies.debug.print_message.reset_mock()

        bindings = manager.get_bindings(refresh=True, is_desktop=True)

        assert bindings is not None
        mock_orca_dependencies.debug.print_message.assert_called_with(
            mock_orca_dependencies.debug.LEVEL_INFO,
            "BYPASS MODE MANAGER: Refreshing bindings. Is desktop: True",
            True,
        )

    def test_get_bindings_refresh_desktop_false(
        self, mock_bypass_dependencies, mock_orca_dependencies
    ):
        """Test get_bindings with refresh=True and is_desktop=False."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        # Reset debug mock to track calls after initialization
        mock_orca_dependencies.debug.print_message.reset_mock()

        bindings = manager.get_bindings(refresh=True, is_desktop=False)

        assert bindings is not None
        mock_orca_dependencies.debug.print_message.assert_called_with(
            mock_orca_dependencies.debug.LEVEL_INFO,
            "BYPASS MODE MANAGER: Refreshing bindings. Is desktop: False",
            True,
        )

    def test_get_bindings_empty_bindings(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test get_bindings when bindings are empty."""

        # Configure empty bindings
        key_bindings_instance = mock_bypass_dependencies["key_bindings_instance"]
        key_bindings_instance.is_empty.return_value = True

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        bindings = manager.get_bindings(refresh=False)

        assert bindings is not None
        key_bindings_instance.is_empty.assert_called()

    def test_get_bindings_not_empty(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test get_bindings when bindings are not empty."""

        # Configure non-empty bindings
        key_bindings_instance = mock_bypass_dependencies["key_bindings_instance"]
        key_bindings_instance.is_empty.return_value = False

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        bindings = manager.get_bindings(refresh=False)

        assert bindings == key_bindings_instance
        key_bindings_instance.is_empty.assert_called()

    def test_get_handlers_refresh_true(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test get_handlers with refresh=True."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        # Reset debug mock to track calls after initialization
        mock_orca_dependencies.debug.print_message.reset_mock()

        handlers = manager.get_handlers(refresh=True)

        assert handlers is not None
        mock_orca_dependencies.debug.print_message.assert_called_with(
            mock_orca_dependencies.debug.LEVEL_INFO,
            "BYPASS MODE MANAGER: Refreshing handlers.",
            True,
        )

    def test_get_handlers_refresh_false(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test get_handlers with refresh=False."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        initial_handlers = manager._handlers

        handlers = manager.get_handlers(refresh=False)

        assert handlers == initial_handlers

    def test_setup_handlers(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test _setup_handlers method."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        manager._setup_handlers()

        assert "bypass_mode_toggle" in manager._handlers
        expected_handler = mock_bypass_dependencies["input_event_handler"]
        assert manager._handlers["bypass_mode_toggle"] == expected_handler
        input_event = mock_bypass_dependencies["input_event"]
        input_event.InputEventHandler.assert_called_with(
            manager.toggle_enabled, "Toggle all Orca command keys"
        )

    def test_setup_bindings(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test _setup_bindings method."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        manager._setup_bindings()

        # Check that KeyBinding was created with correct parameters
        mock_bypass_dependencies["keybindings"].KeyBinding.assert_called_with(
            "BackSpace",
            1,
            2,
            manager._handlers["bypass_mode_toggle"],
            1,
            True,
        )

        # Check that binding was added and overrides were applied
        key_bindings_instance = mock_bypass_dependencies["key_bindings_instance"]
        key_bindings_instance.add.assert_called()
        settings_manager_instance = mock_bypass_dependencies["settings_manager_instance"]
        settings_manager_instance.override_key_bindings.assert_called_with(
            manager._handlers, key_bindings_instance, False
        )

    def test_is_active_initially_false(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test is_active returns False initially."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        assert manager.is_active() is False

    def test_is_active_after_toggle(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test is_active returns True after setting active state."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        manager._is_active = True

        assert manager.is_active() is True

    def test_toggle_enabled_activate_with_event(
        self, mock_bypass_dependencies, mock_orca_dependencies
    ):
        """Test toggle_enabled activating bypass mode with event."""

        # Configure bindings with some mock key bindings
        mock_binding1 = Mock()
        mock_binding2 = Mock()
        key_bindings = [mock_binding1, mock_binding2]
        key_bindings_instance = mock_bypass_dependencies["key_bindings_instance"]
        key_bindings_instance.key_bindings = key_bindings

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        mock_script = Mock()
        mock_event = Mock()

        result = manager.toggle_enabled(mock_script, mock_event)

        assert result is True
        assert manager._is_active is True
        mock_script.present_message.assert_called_with("Orca command keys off.")
        mock_script.remove_key_grabs.assert_called_with("bypass mode enabled")
        modifier_manager = mock_bypass_dependencies["modifier_manager_instance"]
        modifier_manager.unset_orca_modifiers.assert_called_with("bypass mode enabled")

        # Check that bindings were added to script
        # pylint: disable=no-member
        mock_script.key_bindings.add.assert_any_call(mock_binding1, include_grabs=True)
        mock_script.key_bindings.add.assert_any_call(mock_binding2, include_grabs=True)

    def test_toggle_enabled_activate_without_event(
        self, mock_bypass_dependencies, mock_orca_dependencies
    ):
        """Test toggle_enabled activating bypass mode without event."""

        key_bindings_instance = mock_bypass_dependencies["key_bindings_instance"]
        key_bindings_instance.key_bindings = []

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        mock_script = Mock()

        result = manager.toggle_enabled(mock_script, None)

        assert result is True
        assert manager._is_active is True
        mock_script.present_message.assert_not_called()
        mock_script.remove_key_grabs.assert_called_with("bypass mode enabled")
        modifier_manager = mock_bypass_dependencies["modifier_manager_instance"]
        modifier_manager.unset_orca_modifiers.assert_called_with("bypass mode enabled")

    def test_toggle_enabled_deactivate_with_event(
        self, mock_bypass_dependencies, mock_orca_dependencies
    ):
        """Test toggle_enabled deactivating bypass mode with event."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        manager._is_active = True

        mock_script = Mock()
        mock_event = Mock()

        result = manager.toggle_enabled(mock_script, mock_event)

        assert result is True
        assert manager._is_active is False
        mock_script.present_message.assert_called_with("Orca command keys on.")
        mock_script.add_key_grabs.assert_called_with("bypass mode disabled")
        modifier_manager = mock_bypass_dependencies["modifier_manager_instance"]
        modifier_manager.refresh_orca_modifiers.assert_called_with("bypass mode disabled")

    def test_toggle_enabled_deactivate_without_event(
        self, mock_bypass_dependencies, mock_orca_dependencies
    ):
        """Test toggle_enabled deactivating bypass mode without event."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        manager._is_active = True  # Start in active state

        mock_script = Mock()

        result = manager.toggle_enabled(mock_script, None)

        assert result is True
        assert manager._is_active is False
        mock_script.present_message.assert_not_called()
        mock_script.add_key_grabs.assert_called_with("bypass mode disabled")
        modifier_manager = mock_bypass_dependencies["modifier_manager_instance"]
        modifier_manager.refresh_orca_modifiers.assert_called_with("bypass mode disabled")

    def test_get_manager_returns_singleton(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test get_manager returns the singleton instance."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import get_manager

        manager1 = get_manager()
        manager2 = get_manager()

        assert manager1 is manager2
        assert hasattr(manager1, "toggle_enabled")
        assert hasattr(manager1, "is_active")

    def test_toggle_enabled_multiple_times(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test toggle_enabled works correctly when called multiple times."""

        # Configure bindings with empty key bindings
        key_bindings_instance = mock_bypass_dependencies["key_bindings_instance"]
        key_bindings_instance.key_bindings = []

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        mock_script = Mock()

        # Initially inactive
        assert manager.is_active() is False

        # First toggle - should activate
        result1 = manager.toggle_enabled(mock_script, None)
        assert result1 is True
        assert manager.is_active() is True

        # Second toggle - should deactivate
        result2 = manager.toggle_enabled(mock_script, None)
        assert result2 is True
        assert manager.is_active() is False

        # Third toggle - should activate again
        result3 = manager.toggle_enabled(mock_script, None)
        assert result3 is True
        assert manager.is_active() is True

    def test_handlers_structure_and_content(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test that handlers are properly structured and contain expected content."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        handlers = manager.get_handlers()

        assert isinstance(handlers, dict)
        assert "bypass_mode_toggle" in handlers
        assert len(handlers) == 1
        expected_handler = mock_bypass_dependencies["input_event_handler"]
        assert handlers["bypass_mode_toggle"] == expected_handler

    def test_bindings_with_key_override(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test that bindings are properly configured with key overrides."""

        # Configure override behavior
        mock_overridden_bindings = Mock()
        settings_manager_instance = mock_bypass_dependencies["settings_manager_instance"]
        settings_manager_instance.override_key_bindings.return_value = mock_overridden_bindings

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        bindings = manager.get_bindings(refresh=True)

        # Verify that the overridden bindings are returned
        assert bindings == mock_overridden_bindings

        # Verify override_key_bindings was called with correct parameters
        key_bindings_instance = mock_bypass_dependencies["key_bindings_instance"]
        settings_manager_instance.override_key_bindings.assert_called_with(
            manager._handlers, key_bindings_instance, False
        )

    def test_setup_bindings_key_creation(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test that _setup_bindings creates correct key binding configuration."""

        # Set up specific modifier mask values
        keybindings_mock = mock_bypass_dependencies["keybindings"]
        keybindings_mock.DEFAULT_MODIFIER_MASK = 8
        keybindings_mock.ALT_MODIFIER_MASK = 16

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        # Reset mocks to track specific setup calls
        keybindings_mock.KeyBinding.reset_mock()

        manager._setup_bindings()

        # Verify KeyBinding was called with the updated mask values
        keybindings_mock.KeyBinding.assert_called_with(
            "BackSpace",
            8,  # DEFAULT_MODIFIER_MASK
            16,  # ALT_MODIFIER_MASK
            manager._handlers["bypass_mode_toggle"],
            1,
            True,
        )

    def test_handlers_refresh_behavior(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test that get_handlers properly refreshes handlers when requested."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()

        _initial_handlers = manager.get_handlers(refresh=False)

        # Reset the input event handler mock to track new calls
        input_event_mock = mock_bypass_dependencies["input_event"]
        input_event_mock.InputEventHandler.reset_mock()

        # Refresh handlers
        refreshed_handlers = manager.get_handlers(refresh=True)

        # Verify handlers were refreshed (new InputEventHandler created)
        input_event_mock.InputEventHandler.assert_called()
        assert refreshed_handlers is not None

    def test_toggle_state_persistence(self, mock_bypass_dependencies, mock_orca_dependencies):
        """Test that bypass mode state persists across multiple operations."""

        clean_module_cache("orca.bypass_mode_manager")
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        mock_script = Mock()

        # Verify initial state
        assert manager.is_active() is False

        # Activate bypass mode
        manager.toggle_enabled(mock_script, None)
        assert manager.is_active() is True

        # Check that state persists across other method calls
        manager.get_bindings()
        manager.get_handlers()
        assert manager.is_active() is True

        # Deactivate bypass mode
        manager.toggle_enabled(mock_script, None)
        assert manager.is_active() is False

        # Verify state remains false
        manager.get_bindings()
        manager.get_handlers()
        assert manager.is_active() is False
