# Unit tests for input_event_manager.py InputEventManager class methods.
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
# pylint: disable=too-many-locals
# pylint: disable=unused-variable
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-lines

"""Unit tests for input_event_manager.py InputEventManager class methods."""

from __future__ import annotations

import sys
from unittest.mock import Mock, call

import pytest


@pytest.mark.unit
class TestInputEventManager:
    """Test InputEventManager class methods."""

    @pytest.fixture
    def mock_input_event_manager_deps(self, mock_orca_dependencies, monkeypatch):
        """Mock dependencies for InputEventManager tests."""

        debug_mock = mock_orca_dependencies.debug

        focus_manager_mock = Mock()
        focus_manager_mock.get_manager = Mock()
        focus_manager_instance = Mock()
        focus_manager_mock.get_manager.return_value = focus_manager_instance

        script_manager_mock = Mock()
        script_manager_mock.get_manager = Mock()
        script_manager_instance = Mock()
        script_manager_mock.get_manager.return_value = script_manager_instance

        class MockKeyboardEvent:
            """Mock KeyboardEvent class for testing."""

            def __init__(self, pressed=True, keycode=65, keysym=97, modifiers=0, text="a"):
                self.process = Mock()
                self.set_window = Mock()
                self.set_object = Mock()
                self.set_script = Mock()
                self.set_click_count = Mock()
                self.is_modifier_key = Mock(return_value=False)
                self.is_pressed_key = Mock(return_value=True)
                self.get_window = Mock()
                self.get_object = Mock()
                self.get_script = Mock()
                self.get_click_count = Mock(return_value=1)
                self.is_printable_key = Mock(return_value=True)
                self.as_single_line_string = Mock(return_value="KeyboardEvent")
                # Store constructor parameters for comparison
                self.pressed = pressed
                self.keycode = keycode
                self.keysym = keysym
                self.modifiers = modifiers
                self.text = text
                # Add attributes that might be accessed directly
                self.id = 1
                self.hw_code = keycode
                self.keyval_name = text
                self.time = 1000
                self.button = None

            def __eq__(self, other):
                """Enable equality comparison for duplicate detection."""
                if not isinstance(other, MockKeyboardEvent):
                    return False
                return (
                    self.pressed == other.pressed
                    and self.keycode == other.keycode
                    and self.keysym == other.keysym
                    and self.modifiers == other.modifiers
                    and self.text == other.text
                )

        class MockBrailleEvent:
            """Mock BrailleEvent class for testing."""

            def __init__(self, *args, **kwargs):
                self.process = Mock(return_value=True)

        class MockMouseButtonEvent:
            """Mock MouseButtonEvent class for testing."""

            def __init__(self, *args, **kwargs):
                self.set_click_count = Mock()
                self.get_click_count = Mock(return_value=1)
                # Add attributes that might be accessed directly
                self.button = "1"
                self.pressed = True
                self.time = 1000

        input_event_mock = Mock()
        input_event_mock.KeyboardEvent = MockKeyboardEvent
        input_event_mock.BrailleEvent = MockBrailleEvent
        input_event_mock.MouseButtonEvent = MockMouseButtonEvent

        settings_mock = Mock()
        settings_mock.doubleClickTimeout = 500

        ax_object_module = Mock()
        ax_object_class = Mock()
        ax_object_class.get_action_key_binding = Mock(return_value="Alt+F")
        ax_object_module.AXObject = ax_object_class

        ax_utilities_mock = Mock()
        ax_utilities_mock.can_be_active_window = Mock(return_value=True)
        ax_utilities_mock.find_active_window = Mock(return_value=None)
        ax_utilities_mock.is_single_line = Mock(return_value=False)
        ax_utilities_mock.is_widget_controlled_by_line_navigation = Mock(return_value=False)
        ax_utilities_mock.is_table_header = Mock(return_value=False)
        ax_utilities_mock.is_terminal = Mock(return_value=False)

        atspi_mock = Mock()
        atspi_mock.get_version = Mock(return_value=(2, 56, 0))
        atspi_mock.Device = Mock()
        atspi_mock.Device.new_full = Mock()
        atspi_mock.Device.new = Mock()
        atspi_mock.Device.grab_keyboard = Mock()
        atspi_mock.Device.ungrab_keyboard = Mock()
        atspi_mock.KeyDefinition = Mock()
        atspi_mock.ModifierType = Mock()
        atspi_mock.ModifierType.CONTROL = 2
        atspi_mock.ModifierType.SHIFT = 0
        atspi_mock.ModifierType.ALT = 3

        gdk_mock = Mock()
        gdk_mock.Keymap = Mock()
        gdk_mock.Keymap.get_default = Mock()
        keymap_instance = Mock()
        gdk_mock.Keymap.get_default.return_value = keymap_instance
        keymap_instance.get_entries_for_keycode = Mock(return_value=(None, None, [120, 121]))
        gdk_mock.keyval_name = Mock(side_effect=lambda x: f"key_{x}")

        monkeypatch.setitem(sys.modules, "orca.focus_manager", focus_manager_mock)
        monkeypatch.setitem(sys.modules, "orca.script_manager", script_manager_mock)
        monkeypatch.setitem(sys.modules, "orca.input_event", input_event_mock)
        monkeypatch.setitem(sys.modules, "orca.settings", settings_mock)

        monkeypatch.setitem(sys.modules, "orca.ax_object", ax_object_module)

        ax_utilities_module = Mock()
        ax_utilities_module.AXUtilities = ax_utilities_mock
        monkeypatch.setitem(sys.modules, "orca.ax_utilities", ax_utilities_module)

        gi_repository_mock = Mock()
        gi_repository_mock.Atspi = atspi_mock
        gi_repository_mock.Gdk = gdk_mock
        monkeypatch.setitem(sys.modules, "gi.repository", gi_repository_mock)

        return {
            "debug": debug_mock,
            "focus_manager": focus_manager_mock,
            "focus_manager_instance": focus_manager_instance,
            "script_manager": script_manager_mock,
            "script_manager_instance": script_manager_instance,
            "input_event": input_event_mock,
            "settings": settings_mock,
            "ax_object": ax_object_class,
            "ax_utilities": ax_utilities_mock,
            "atspi": atspi_mock,
            "gdk": gdk_mock,
        }

    @pytest.fixture
    def input_event_manager(self, mock_input_event_manager_deps, monkeypatch):
        """Create InputEventManager instance with mocked dependencies."""

        monkeypatch.setattr(
            "orca.input_event_manager.debug", mock_input_event_manager_deps["debug"]
        )
        monkeypatch.setattr(
            "orca.input_event_manager.focus_manager", mock_input_event_manager_deps["focus_manager"]
        )
        monkeypatch.setattr(
            "orca.input_event_manager.script_manager",
            mock_input_event_manager_deps["script_manager"],
        )
        monkeypatch.setattr(
            "orca.input_event_manager.input_event", mock_input_event_manager_deps["input_event"]
        )
        monkeypatch.setattr(
            "orca.input_event_manager.settings", mock_input_event_manager_deps["settings"]
        )
        monkeypatch.setattr(
            "orca.input_event_manager.AXObject", mock_input_event_manager_deps["ax_object"]
        )
        monkeypatch.setattr(
            "orca.input_event_manager.AXUtilities", mock_input_event_manager_deps["ax_utilities"]
        )
        monkeypatch.setattr(
            "orca.input_event_manager.Atspi", mock_input_event_manager_deps["atspi"]
        )
        monkeypatch.setattr("orca.input_event_manager.Gdk", mock_input_event_manager_deps["gdk"])

        from orca.input_event_manager import InputEventManager

        return InputEventManager()

    def test_init(self, input_event_manager):
        """Test InputEventManager.__init__."""

        assert input_event_manager._last_input_event is None
        assert input_event_manager._last_non_modifier_key_event is None
        assert input_event_manager._device is None
        assert input_event_manager._mapped_keycodes == []
        assert input_event_manager._mapped_keysyms == []
        assert input_event_manager._grabbed_bindings == {}

    def test_start_key_watcher_with_new_atspi(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.start_key_watcher with Atspi version >= 2.55.90."""

        mock_device = Mock()
        mock_input_event_manager_deps["atspi"].Device.new_full.return_value = mock_device
        mock_input_event_manager_deps["atspi"].get_version.return_value = (2, 56, 0)

        input_event_manager.start_key_watcher()

        mock_input_event_manager_deps["atspi"].Device.new_full.assert_called_once_with(
            "org.gnome.Orca"
        )
        mock_device.add_key_watcher.assert_called_once_with(
            input_event_manager.process_keyboard_event
        )
        assert input_event_manager._device == mock_device

    def test_start_key_watcher_with_old_atspi(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.start_key_watcher with Atspi version < 2.55.90."""

        mock_device = Mock()
        mock_input_event_manager_deps["atspi"].Device.new.return_value = mock_device
        mock_input_event_manager_deps["atspi"].get_version.return_value = (2, 54, 0)

        input_event_manager.start_key_watcher()

        mock_input_event_manager_deps["atspi"].Device.new.assert_called_once()
        mock_device.add_key_watcher.assert_called_once_with(
            input_event_manager.process_keyboard_event
        )
        assert input_event_manager._device == mock_device

    def test_stop_key_watcher(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.stop_key_watcher."""

        input_event_manager._device = Mock()

        input_event_manager.stop_key_watcher()

        assert input_event_manager._device is None
        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_check_grabbed_bindings_empty(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.check_grabbed_bindings with no bindings."""

        input_event_manager.check_grabbed_bindings()

        calls = mock_input_event_manager_deps["debug"].print_message.call_args_list
        assert len(calls) == 1
        assert "0 grabbed key bindings" in calls[0][0][1]

    def test_check_grabbed_bindings_with_bindings(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.check_grabbed_bindings with bindings."""

        mock_binding = Mock()
        mock_binding.__str__ = Mock(return_value="test_binding")
        input_event_manager._grabbed_bindings = {123: mock_binding, 456: mock_binding}

        input_event_manager.check_grabbed_bindings()

        calls = mock_input_event_manager_deps["debug"].print_message.call_args_list
        assert len(calls) == 3  # One for count, two for individual bindings
        assert "2 grabbed key bindings" in calls[0][0][1]

    def test_add_grabs_for_keybinding_disabled(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.add_grabs_for_keybinding with disabled binding."""

        mock_binding = Mock()
        mock_binding.is_enabled.return_value = False
        mock_binding.is_bound.return_value = True

        result = input_event_manager.add_grabs_for_keybinding(mock_binding)

        assert result == []
        mock_binding.is_enabled.assert_called_once()

    def test_add_grabs_for_keybinding_unbound(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.add_grabs_for_keybinding with unbound binding."""

        mock_binding = Mock()
        mock_binding.is_enabled.return_value = True
        mock_binding.is_bound.return_value = False

        result = input_event_manager.add_grabs_for_keybinding(mock_binding)

        assert result == []
        mock_binding.is_enabled.assert_called_once()
        mock_binding.is_bound.assert_called_once()

    def test_add_grabs_for_keybinding_has_grabs(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.add_grabs_for_keybinding with binding that already has grabs."""

        mock_binding = Mock()
        mock_binding.is_enabled.return_value = True
        mock_binding.is_bound.return_value = True
        mock_binding.has_grabs.return_value = True

        result = input_event_manager.add_grabs_for_keybinding(mock_binding)

        assert result == []
        mock_input_event_manager_deps["debug"].print_tokens.assert_called()

    def test_add_grabs_for_keybinding_no_device(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.add_grabs_for_keybinding with no device."""

        mock_binding = Mock()
        mock_binding.is_enabled.return_value = True
        mock_binding.is_bound.return_value = True
        mock_binding.has_grabs.return_value = False

        result = input_event_manager.add_grabs_for_keybinding(mock_binding)

        assert result == []
        mock_input_event_manager_deps["debug"].print_tokens.assert_called()

    def test_add_grabs_for_keybinding_success(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.add_grabs_for_keybinding successfully adds grabs."""

        mock_device = Mock()
        mock_device.add_key_grab.side_effect = [111, 222]
        input_event_manager._device = mock_device

        mock_binding = Mock()
        mock_binding.is_enabled.return_value = True
        mock_binding.is_bound.return_value = True
        mock_binding.has_grabs.return_value = False
        mock_kd1 = Mock()
        mock_kd2 = Mock()
        mock_binding.key_definitions.return_value = [mock_kd1, mock_kd2]

        result = input_event_manager.add_grabs_for_keybinding(mock_binding)

        assert result == [111, 222]
        assert input_event_manager._grabbed_bindings[111] == mock_binding
        assert input_event_manager._grabbed_bindings[222] == mock_binding
        mock_device.add_key_grab.assert_has_calls([call(mock_kd1, None), call(mock_kd2, None)])

    def test_remove_grabs_for_keybinding_no_device(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.remove_grabs_for_keybinding with no device."""

        mock_binding = Mock()

        input_event_manager.remove_grabs_for_keybinding(mock_binding)

        mock_input_event_manager_deps["debug"].print_tokens.assert_called()

    def test_remove_grabs_for_keybinding_no_grabs(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.remove_grabs_for_keybinding with no grabs."""

        mock_device = Mock()
        input_event_manager._device = mock_device

        mock_binding = Mock()
        mock_binding.get_grab_ids.return_value = []

        input_event_manager.remove_grabs_for_keybinding(mock_binding)

        mock_input_event_manager_deps["debug"].print_tokens.assert_called()

    def test_remove_grabs_for_keybinding_success(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.remove_grabs_for_keybinding successfully removes grabs."""

        mock_device = Mock()
        input_event_manager._device = mock_device
        input_event_manager._grabbed_bindings = {111: Mock(), 222: Mock()}

        mock_binding = Mock()
        mock_binding.get_grab_ids.return_value = [111, 222]

        input_event_manager.remove_grabs_for_keybinding(mock_binding)

        mock_device.remove_key_grab.assert_has_calls([call(111), call(222)])
        assert 111 not in input_event_manager._grabbed_bindings
        assert 222 not in input_event_manager._grabbed_bindings

    def test_remove_grabs_for_keybinding_missing_grab(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.remove_grabs_for_keybinding with missing grab ID."""

        mock_device = Mock()
        input_event_manager._device = mock_device

        mock_binding = Mock()
        mock_binding.get_grab_ids.return_value = [999]

        input_event_manager.remove_grabs_for_keybinding(mock_binding)

        mock_device.remove_key_grab.assert_called_once_with(999)
        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_map_keycode_to_modifier_no_device(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.map_keycode_to_modifier with no device."""

        result = input_event_manager.map_keycode_to_modifier(42)

        assert result == 0
        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_map_keycode_to_modifier_success(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.map_keycode_to_modifier successfully maps keycode."""

        mock_device = Mock()
        mock_device.map_modifier.return_value = 8
        input_event_manager._device = mock_device

        result = input_event_manager.map_keycode_to_modifier(42)

        assert result == 8
        assert 42 in input_event_manager._mapped_keycodes
        mock_device.map_modifier.assert_called_once_with(42)

    def test_map_keysym_to_modifier_no_device(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.map_keysym_to_modifier with no device."""

        result = input_event_manager.map_keysym_to_modifier(0x61)

        assert result == 0
        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_map_keysym_to_modifier_success(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.map_keysym_to_modifier successfully maps keysym."""

        mock_device = Mock()
        mock_device.map_keysym_modifier.return_value = 16
        input_event_manager._device = mock_device

        result = input_event_manager.map_keysym_to_modifier(0x61)

        assert result == 16
        assert 0x61 in input_event_manager._mapped_keysyms
        mock_device.map_keysym_modifier.assert_called_once_with(0x61)

    def test_unmap_all_modifiers_no_device(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.unmap_all_modifiers with no device."""

        input_event_manager._mapped_keycodes = [42, 43]
        input_event_manager._mapped_keysyms = [0x61, 0x62]

        input_event_manager.unmap_all_modifiers()

        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_unmap_all_modifiers_success(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.unmap_all_modifiers successfully unmaps modifiers."""

        mock_device = Mock()
        input_event_manager._device = mock_device
        input_event_manager._mapped_keycodes = [42, 43]
        input_event_manager._mapped_keysyms = [0x61, 0x62]

        input_event_manager.unmap_all_modifiers()

        mock_device.unmap_modifier.assert_has_calls([call(42), call(43)])
        mock_device.unmap_keysym_modifier.assert_has_calls([call(0x61), call(0x62)])
        assert input_event_manager._mapped_keycodes == []
        assert input_event_manager._mapped_keysyms == []

    def test_add_grab_for_modifier_no_device(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.add_grab_for_modifier with no device."""

        result = input_event_manager.add_grab_for_modifier("Shift", 0xFFE1, 50)

        assert result == -1
        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_add_grab_for_modifier_success(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.add_grab_for_modifier successfully adds grab."""

        mock_device = Mock()
        mock_device.add_key_grab.return_value = 789
        input_event_manager._device = mock_device

        result = input_event_manager.add_grab_for_modifier("Shift", 0xFFE1, 50)

        assert result == 789
        mock_device.add_key_grab.assert_called_once()

    def test_remove_grab_for_modifier_no_device(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.remove_grab_for_modifier with no device."""

        input_event_manager.remove_grab_for_modifier("Shift", 789)

        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_remove_grab_for_modifier_success(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.remove_grab_for_modifier successfully removes grab."""

        mock_device = Mock()
        input_event_manager._device = mock_device

        input_event_manager.remove_grab_for_modifier("Shift", 789)

        mock_device.remove_key_grab.assert_called_once_with(789)
        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_grab_keyboard_without_reason(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.grab_keyboard without reason."""

        mock_device = Mock()
        input_event_manager._device = mock_device

        input_event_manager.grab_keyboard()

        mock_input_event_manager_deps["atspi"].Device.grab_keyboard.assert_called_once_with(
            mock_device
        )

    def test_grab_keyboard_with_reason(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.grab_keyboard with reason."""

        mock_device = Mock()
        input_event_manager._device = mock_device

        input_event_manager.grab_keyboard("learn mode")

        mock_input_event_manager_deps["atspi"].Device.grab_keyboard.assert_called_once_with(
            mock_device
        )
        debug_calls = mock_input_event_manager_deps["debug"].print_message.call_args_list
        assert any("learn mode" in str(call) for call in debug_calls)

    def test_ungrab_keyboard_without_reason(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.ungrab_keyboard without reason."""

        mock_device = Mock()
        input_event_manager._device = mock_device

        input_event_manager.ungrab_keyboard()

        mock_input_event_manager_deps["atspi"].Device.ungrab_keyboard.assert_called_once_with(
            mock_device
        )

    def test_ungrab_keyboard_with_reason(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.ungrab_keyboard with reason."""

        mock_device = Mock()
        input_event_manager._device = mock_device

        input_event_manager.ungrab_keyboard("exiting learn mode")

        mock_input_event_manager_deps["atspi"].Device.ungrab_keyboard.assert_called_once_with(
            mock_device
        )
        debug_calls = mock_input_event_manager_deps["debug"].print_message.call_args_list
        assert any("exiting learn mode" in str(call) for call in debug_calls)

    def test_process_braille_event(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.process_braille_event."""

        mock_event = Mock()

        result = input_event_manager.process_braille_event(mock_event)

        assert result is True
        assert isinstance(
            input_event_manager._last_input_event,
            mock_input_event_manager_deps["input_event"].BrailleEvent,
        )
        assert input_event_manager._last_non_modifier_key_event is None

    def test_process_mouse_button_event(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.process_mouse_button_event."""

        mock_event = Mock()
        input_event_manager._determine_mouse_event_click_count = Mock(return_value=2)
        input_event_manager.process_mouse_button_event(mock_event)

        assert isinstance(
            input_event_manager._last_input_event,
            mock_input_event_manager_deps["input_event"].MouseButtonEvent,
        )
        input_event_manager._last_input_event.set_click_count.assert_called_once_with(2)

    @pytest.mark.parametrize(
        "pressed, keycode, keysym, modifiers, text, window_can_be_active, new_window_found",
        [
            pytest.param(True, 65, 97, 0, "a", True, None, id="key_press_active_window"),
            pytest.param(
                True, 65, 97, 0, "a", False, Mock(), id="key_press_inactive_window_with_alternative"
            ),
            pytest.param(
                True, 65, 97, 0, "a", False, None, id="key_press_inactive_window_no_alternative"
            ),
            pytest.param(False, 65, 97, 0, "a", True, None, id="key_release"),
        ],
    )
    def test_process_keyboard_event(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        pressed,
        keycode,
        keysym,
        modifiers,
        text,
        window_can_be_active,
        new_window_found,
    ):
        """Test InputEventManager.process_keyboard_event."""

        mock_device = Mock()
        mock_window = Mock()
        mock_focus = Mock()
        mock_script = Mock()

        mock_focus_manager = mock_input_event_manager_deps["focus_manager_instance"]
        mock_focus_manager.get_active_window.return_value = mock_window
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus

        mock_script_manager = mock_input_event_manager_deps["script_manager_instance"]
        mock_script_manager.get_active_script.return_value = mock_script

        mock_input_event_manager_deps[
            "ax_utilities"
        ].can_be_active_window.return_value = window_can_be_active
        mock_input_event_manager_deps[
            "ax_utilities"
        ].find_active_window.return_value = new_window_found
        input_event_manager._determine_keyboard_event_click_count = Mock(return_value=1)

        result = input_event_manager.process_keyboard_event(
            mock_device, pressed, keycode, keysym, modifiers, text
        )

        assert result is True
        # Check that the last input event is the keyboard event instance created by the manager
        assert isinstance(
            input_event_manager._last_input_event,
            mock_input_event_manager_deps["input_event"].KeyboardEvent,
        )
        input_event_manager._last_input_event.process.assert_called_once()

    def test_process_keyboard_event_duplicate(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.process_keyboard_event with duplicate event."""

        mock_device = Mock()
        keyboard_event_instance = mock_input_event_manager_deps["input_event"].KeyboardEvent(
            True, 65, 97, 0, "a"
        )
        input_event_manager._last_input_event = keyboard_event_instance

        result = input_event_manager.process_keyboard_event(mock_device, True, 65, 97, 0, "a")
        assert result is False
        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_last_event_was_keyboard_true(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.last_event_was_keyboard returns True."""

        keyboard_event_class = mock_input_event_manager_deps["input_event"].KeyboardEvent
        mock_keyboard_event = keyboard_event_class()
        input_event_manager._last_input_event = mock_keyboard_event

        result = input_event_manager.last_event_was_keyboard()
        assert result is True

    def test_last_event_was_keyboard_false(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.last_event_was_keyboard returns False."""

        mock_mouse_event = Mock()
        input_event_manager._last_input_event = mock_mouse_event

        result = input_event_manager.last_event_was_keyboard()
        assert result is False

    def test_last_event_was_mouse_button_true(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.last_event_was_mouse_button returns True."""

        # Create an instance of the mock MouseButtonEvent class
        mouse_event_class = mock_input_event_manager_deps["input_event"].MouseButtonEvent
        mock_mouse_event = mouse_event_class()
        input_event_manager._last_input_event = mock_mouse_event

        result = input_event_manager.last_event_was_mouse_button()
        assert result is True

    def test_last_event_was_mouse_button_false(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.last_event_was_mouse_button returns False."""

        mock_keyboard_event = Mock()
        input_event_manager._last_input_event = mock_keyboard_event

        result = input_event_manager.last_event_was_mouse_button()
        assert result is False

    @pytest.mark.parametrize(
        "event1, event2, event1_pressed, event2_pressed, same_id, same_hw_code, same_keyval, "
        "event1_modifier, same_modifiers, expected_result",
        [
            pytest.param(
                None, Mock(), None, None, None, None, None, None, None, False, id="event1_none"
            ),
            pytest.param(
                Mock(), None, None, None, None, None, None, None, None, False, id="event2_none"
            ),
            pytest.param(
                Mock(),
                Mock(),
                False,
                True,
                True,
                True,
                True,
                False,
                True,
                True,
                id="release_for_press",
            ),
            pytest.param(
                Mock(), Mock(), True, True, True, True, True, False, True, False, id="both_pressed"
            ),
            pytest.param(
                Mock(),
                Mock(),
                False,
                False,
                True,
                True,
                True,
                False,
                True,
                False,
                id="both_released",
            ),
            pytest.param(
                Mock(),
                Mock(),
                False,
                True,
                False,
                True,
                True,
                False,
                True,
                False,
                id="different_id",
            ),
            pytest.param(
                Mock(),
                Mock(),
                False,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                id="modifier_key_ignore_modifiers",
            ),
        ],
    )
    def test_is_release_for(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        event1,
        event2,
        event1_pressed,
        event2_pressed,
        same_id,
        same_hw_code,
        same_keyval,
        event1_modifier,
        same_modifiers,
        expected_result,
    ):
        """Test InputEventManager.is_release_for."""

        if event1 is not None and event2 is not None:
            # Create proper instances using the mock class
            keyboard_event_class = mock_input_event_manager_deps["input_event"].KeyboardEvent
            event1 = keyboard_event_class()
            event2 = keyboard_event_class()

            event1.is_pressed_key.return_value = event1_pressed
            event2.is_pressed_key.return_value = event2_pressed
            event1.id = "test_id" if same_id else "other_id"
            event2.id = "test_id"
            event1.hw_code = 42 if same_hw_code else 43
            event2.hw_code = 42
            event1.keyval_name = "a" if same_keyval else "b"
            event2.keyval_name = "a"
            event1.is_modifier_key = event1_modifier
            event1.modifiers = 4 if same_modifiers else 8
            event2.modifiers = 4
            event1.as_single_line_string.return_value = "event1"
            event2.as_single_line_string.return_value = "event2"

            result = input_event_manager.is_release_for(event1, event2)
            assert result == expected_result

    def test_last_event_equals_or_is_release_for_event_no_last_event(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.last_event_equals_or_is_release_for_event with no last event."""

        mock_event = Mock()

        result = input_event_manager.last_event_equals_or_is_release_for_event(mock_event)
        assert result is False

    def test_last_event_equals_or_is_release_for_event_equal(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.last_event_equals_or_is_release_for_event with equal events."""

        keyboard_event_class = mock_input_event_manager_deps["input_event"].KeyboardEvent
        mock_event = keyboard_event_class()
        input_event_manager._last_non_modifier_key_event = mock_event
        input_event_manager._last_input_event = mock_event

        result = input_event_manager.last_event_equals_or_is_release_for_event(mock_event)
        assert result is True

    def test_last_event_equals_or_is_release_for_event_is_release(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.last_event_equals_or_is_release_for_event with release event."""

        keyboard_event_class = mock_input_event_manager_deps["input_event"].KeyboardEvent
        mock_event = keyboard_event_class(pressed=False)
        mock_last_event = keyboard_event_class(pressed=True)
        input_event_manager._last_non_modifier_key_event = mock_last_event
        input_event_manager._last_input_event = mock_last_event

        input_event_manager.is_release_for = Mock(return_value=True)

        result = input_event_manager.last_event_equals_or_is_release_for_event(mock_event)
        assert result is True
        input_event_manager.is_release_for.assert_called_once_with(mock_last_event, mock_event)

    @pytest.mark.parametrize(
        "has_last_non_modifier, last_event_keyboard, expected_key, expected_modifiers",
        [
            pytest.param(False, True, "", 0, id="no_last_non_modifier"),
            pytest.param(True, False, "", 0, id="last_not_keyboard"),
            pytest.param(True, True, "a", 4, id="has_both"),
        ],
    )
    def test_last_key_and_modifiers(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        has_last_non_modifier,
        last_event_keyboard,
        expected_key,
        expected_modifiers,
    ):
        """Test InputEventManager._last_key_and_modifiers."""

        if has_last_non_modifier:
            mock_last_non_modifier = Mock()
            mock_last_non_modifier.keyval_name = "a"
            input_event_manager._last_non_modifier_key_event = mock_last_non_modifier
        else:
            input_event_manager._last_non_modifier_key_event = None

        if last_event_keyboard:
            mock_last_event = Mock()
            mock_last_event.modifiers = 4
            input_event_manager._last_input_event = mock_last_event

        input_event_manager.last_event_was_keyboard = Mock(return_value=last_event_keyboard)
        result = input_event_manager._last_key_and_modifiers()
        assert result == (expected_key, expected_modifiers)

    @pytest.mark.parametrize(
        "has_last_non_modifier, last_event_keyboard, expected_keycode, expected_modifiers",
        [
            pytest.param(False, True, 0, 0, id="no_last_non_modifier"),
            pytest.param(True, False, 0, 0, id="last_not_keyboard"),
            pytest.param(True, True, 42, 4, id="has_both"),
        ],
    )
    def test_last_keycode_and_modifiers(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        has_last_non_modifier,
        last_event_keyboard,
        expected_keycode,
        expected_modifiers,
    ):
        """Test InputEventManager._last_keycode_and_modifiers."""

        if has_last_non_modifier:
            mock_last_non_modifier = Mock()
            mock_last_non_modifier.hw_code = 42
            input_event_manager._last_non_modifier_key_event = mock_last_non_modifier
        else:
            input_event_manager._last_non_modifier_key_event = None

        if last_event_keyboard:
            keyboard_event_class = mock_input_event_manager_deps["input_event"].KeyboardEvent
            mock_last_event = Mock(spec=keyboard_event_class())
            mock_last_event.__class__ = keyboard_event_class
            mock_last_event.modifiers = 4
            input_event_manager._last_input_event = mock_last_event

            result = input_event_manager._last_keycode_and_modifiers()

            assert result == (expected_keycode, expected_modifiers)
        else:
            result = input_event_manager._last_keycode_and_modifiers()
            assert result == (expected_keycode, expected_modifiers)

    def test_all_names_for_key_code(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager._all_names_for_key_code."""

        keycode = 42
        mock_keymap = mock_input_event_manager_deps["gdk"].Keymap.get_default.return_value
        mock_keymap.get_entries_for_keycode.return_value = (None, None, [120, 121])
        mock_input_event_manager_deps["gdk"].keyval_name.side_effect = lambda x: f"key_{x}"

        result = input_event_manager._all_names_for_key_code(keycode)
        assert result == ["key_120", "key_121"]
        mock_keymap.get_entries_for_keycode.assert_called_once_with(keycode)

    def test_last_event_was_command_true(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.last_event_was_command returns True."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=("a", 1 << 2))

        result = input_event_manager.last_event_was_command()
        assert result is True
        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_last_event_was_command_false(self, input_event_manager, mock_input_event_manager_deps):
        """Test InputEventManager.last_event_was_command returns False."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=("a", 0))

        result = input_event_manager.last_event_was_command()
        assert result is False

    @pytest.mark.parametrize(
        "key_string, action_key_bindings, expected_result",
        [
            pytest.param("", [], False, id="empty_key_string"),
            pytest.param("f", ["Alt+F"], True, id="matching_key_uppercase"),
            pytest.param("f", ["Alt+G"], False, id="non_matching_key"),
            pytest.param("f", ["Alt+F", "Ctrl+F"], True, id="multiple_bindings_match"),
        ],
    )
    def test_last_event_was_shortcut_for(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        action_key_bindings,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_shortcut_for."""

        mock_obj = Mock()
        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))
        mock_input_event_manager_deps["ax_object"].get_action_key_binding.return_value = ";".join(
            action_key_bindings
        )

        result = input_event_manager.last_event_was_shortcut_for(mock_obj)

        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_tokens.assert_called()

    def test_last_event_was_printable_key_true(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.last_event_was_printable_key returns True."""

        mock_last_event = Mock()
        mock_last_event.is_printable_key.return_value = True
        input_event_manager._last_input_event = mock_last_event
        input_event_manager.last_event_was_keyboard = Mock(return_value=True)

        result = input_event_manager.last_event_was_printable_key()
        assert result is True
        mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_last_event_was_printable_key_false_not_keyboard(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.last_event_was_printable_key returns False when not keyboard."""

        input_event_manager.last_event_was_keyboard = Mock(return_value=False)

        result = input_event_manager.last_event_was_printable_key()
        assert result is False

    def test_last_event_was_printable_key_false_not_printable(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.last_event_was_printable_key returns False when not printable."""

        mock_last_event = Mock()
        mock_last_event.is_printable_key.return_value = False
        input_event_manager._last_input_event = mock_last_event
        input_event_manager.last_event_was_keyboard = Mock(return_value=True)

        result = input_event_manager.last_event_was_printable_key()
        assert result is False

    def test_last_event_was_caret_navigation(
        self, input_event_manager, mock_input_event_manager_deps
    ):
        """Test InputEventManager.last_event_was_caret_navigation."""

        input_event_manager.last_event_was_character_navigation = Mock(return_value=False)
        input_event_manager.last_event_was_word_navigation = Mock(return_value=True)
        input_event_manager.last_event_was_line_navigation = Mock(return_value=False)
        input_event_manager.last_event_was_line_boundary_navigation = Mock(return_value=False)
        input_event_manager.last_event_was_file_boundary_navigation = Mock(return_value=False)
        input_event_manager.last_event_was_page_navigation = Mock(return_value=False)

        result = input_event_manager.last_event_was_caret_navigation()
        assert result is True

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Left", 1 << 0, True, id="left_with_shift"),
            pytest.param("Right", 1 << 0, True, id="right_with_shift"),
            pytest.param("Up", 1 << 0, True, id="up_with_shift"),
            pytest.param("Down", 1 << 0, True, id="down_with_shift"),
            pytest.param("Left", 0, False, id="left_without_shift"),
            pytest.param("a", 1 << 0, False, id="non_arrow_with_shift"),
        ],
    )
    def test_last_event_was_caret_selection(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_caret_selection."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_caret_selection()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Up", 0, True, id="up_without_shift"),
            pytest.param("Left", 0, True, id="left_without_shift"),
            pytest.param("Down", 0, False, id="down_without_shift"),
            pytest.param("Right", 0, False, id="right_without_shift"),
            pytest.param("Up", 1 << 0, False, id="up_with_shift"),
            pytest.param("a", 0, False, id="non_arrow"),
        ],
    )
    def test_last_event_was_backward_caret_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_backward_caret_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_backward_caret_navigation()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Down", 0, True, id="down_without_shift"),
            pytest.param("Right", 0, True, id="right_without_shift"),
            pytest.param("Up", 0, False, id="up_without_shift"),
            pytest.param("Left", 0, False, id="left_without_shift"),
            pytest.param("Down", 1 << 0, False, id="down_with_shift"),
            pytest.param("a", 0, False, id="non_arrow"),
        ],
    )
    def test_last_event_was_forward_caret_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_forward_caret_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_forward_caret_navigation()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Down", 1 << 0, True, id="down_with_shift"),
            pytest.param("Right", 1 << 0, True, id="right_with_shift"),
            pytest.param("Up", 1 << 0, False, id="up_with_shift"),
            pytest.param("Left", 1 << 0, False, id="left_with_shift"),
            pytest.param("Down", 0, False, id="down_without_shift"),
            pytest.param("a", 1 << 0, False, id="non_arrow"),
        ],
    )
    def test_last_event_was_forward_caret_selection(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_forward_caret_selection."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_forward_caret_selection()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Left", 0, True, id="left_no_modifiers"),
            pytest.param("Right", 0, True, id="right_no_modifiers"),
            pytest.param("Left", 1 << 2, False, id="left_with_ctrl"),
            pytest.param("Right", 1 << 3, False, id="right_with_alt"),
            pytest.param("Up", 0, False, id="non_horizontal_arrow"),
            pytest.param("a", 0, False, id="non_arrow"),
        ],
    )
    def test_last_event_was_character_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_character_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_character_navigation()

        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Left", 1 << 2, True, id="left_with_ctrl"),
            pytest.param("Right", 1 << 2, True, id="right_with_ctrl"),
            pytest.param("Left", 0, False, id="left_no_ctrl"),
            pytest.param("Right", 0, False, id="right_no_ctrl"),
            pytest.param("Up", 1 << 2, False, id="non_horizontal_arrow"),
            pytest.param("a", 1 << 2, False, id="non_arrow"),
        ],
    )
    def test_last_event_was_word_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_word_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_word_navigation()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Left", 1 << 2, True, id="left_with_ctrl"),
            pytest.param("Right", 1 << 2, False, id="right_with_ctrl"),
            pytest.param("Left", 0, False, id="left_no_ctrl"),
            pytest.param("a", 1 << 2, False, id="non_arrow"),
        ],
    )
    def test_last_event_was_previous_word_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_previous_word_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_previous_word_navigation()

        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Right", 1 << 2, True, id="right_with_ctrl"),
            pytest.param("Left", 1 << 2, False, id="left_with_ctrl"),
            pytest.param("Right", 0, False, id="right_no_ctrl"),
            pytest.param("a", 1 << 2, False, id="non_arrow"),
        ],
    )
    def test_last_event_was_next_word_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_next_word_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_next_word_navigation()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, is_single_line, is_widget_controlled, expected_result",
        [
            pytest.param("Up", 0, False, False, True, id="up_multiline_not_controlled"),
            pytest.param("Down", 0, False, False, True, id="down_multiline_not_controlled"),
            pytest.param("Up", 1 << 2, False, False, False, id="up_with_ctrl"),
            pytest.param("Up", 0, True, False, False, id="up_single_line"),
            pytest.param("Up", 0, False, True, False, id="up_widget_controlled"),
            pytest.param("Left", 0, False, False, False, id="non_vertical_arrow"),
        ],
    )
    def test_last_event_was_line_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        is_single_line,
        is_widget_controlled,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_line_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))
        mock_focus = Mock()
        mock_input_event_manager_deps[
            "focus_manager_instance"
        ].get_locus_of_focus.return_value = mock_focus
        mock_input_event_manager_deps["ax_utilities"].is_single_line.return_value = is_single_line
        mock_input_event_manager_deps[
            "ax_utilities"
        ].is_widget_controlled_by_line_navigation.return_value = is_widget_controlled

        result = input_event_manager.last_event_was_line_navigation()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Up", (1 << 2), True, id="up_with_ctrl_no_shift"),
            pytest.param("Down", (1 << 2), True, id="down_with_ctrl_no_shift"),
            pytest.param("Up", (1 << 2) | (1 << 0), False, id="up_with_ctrl_and_shift"),
            pytest.param("Up", 0, False, id="up_no_ctrl"),
            pytest.param("Left", 1 << 2, False, id="non_vertical_arrow"),
        ],
    )
    def test_last_event_was_paragraph_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_paragraph_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_paragraph_navigation()

        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Home", 0, True, id="home_no_ctrl"),
            pytest.param("End", 0, True, id="end_no_ctrl"),
            pytest.param("Home", 1 << 2, False, id="home_with_ctrl"),
            pytest.param("End", 1 << 2, False, id="end_with_ctrl"),
            pytest.param("Left", 0, False, id="non_boundary_key"),
        ],
    )
    def test_last_event_was_line_boundary_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_line_boundary_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_line_boundary_navigation()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Home", 1 << 2, True, id="home_with_ctrl"),
            pytest.param("End", 1 << 2, True, id="end_with_ctrl"),
            pytest.param("Home", 0, False, id="home_no_ctrl"),
            pytest.param("End", 0, False, id="end_no_ctrl"),
            pytest.param("Left", 1 << 2, False, id="non_boundary_key"),
        ],
    )
    def test_last_event_was_file_boundary_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_file_boundary_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_file_boundary_navigation()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, is_single_line, is_widget_controlled, expected_result",
        [
            pytest.param("Page_Up", 0, False, False, True, id="page_up_multiline_not_controlled"),
            pytest.param(
                "Page_Down", 0, False, False, True, id="page_down_multiline_not_controlled"
            ),
            pytest.param("Page_Up", 1 << 2, False, False, False, id="page_up_with_ctrl"),
            pytest.param("Page_Up", 0, True, False, False, id="page_up_single_line"),
            pytest.param("Page_Up", 0, False, True, False, id="page_up_widget_controlled"),
            pytest.param("Left", 0, False, False, False, id="non_page_key"),
        ],
    )
    def test_last_event_was_page_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        is_single_line,
        is_widget_controlled,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_page_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))
        mock_focus = Mock()
        mock_input_event_manager_deps[
            "focus_manager_instance"
        ].get_locus_of_focus.return_value = mock_focus
        mock_input_event_manager_deps["ax_utilities"].is_single_line.return_value = is_single_line
        mock_input_event_manager_deps[
            "ax_utilities"
        ].is_widget_controlled_by_line_navigation.return_value = is_widget_controlled

        result = input_event_manager.last_event_was_page_navigation()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("1", 1 << 3, True, id="numeric_with_alt"),
            pytest.param("2", 1 << 3, True, id="numeric_2_with_alt"),
            pytest.param("Page_Up", 1 << 2, True, id="page_up_with_ctrl"),
            pytest.param("Page_Down", 1 << 2, True, id="page_down_with_ctrl"),
            pytest.param("1", 0, False, id="numeric_no_alt"),
            pytest.param("Page_Up", 0, False, id="page_up_no_ctrl"),
            pytest.param("a", 1 << 3, False, id="non_numeric_non_page"),
        ],
    )
    def test_last_event_was_page_switch(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_page_switch."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_page_switch()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Tab", 0, True, id="tab_no_modifiers"),
            pytest.param("ISO_Left_Tab", 0, True, id="shift_tab_no_modifiers"),
            pytest.param("Tab", 1 << 2, False, id="tab_with_ctrl"),
            pytest.param("Tab", 1 << 3, False, id="tab_with_alt"),
            pytest.param("a", 0, False, id="non_tab_key"),
        ],
    )
    def test_last_event_was_tab_navigation(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_tab_navigation."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_tab_navigation()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "is_table_header, is_mouse_button, is_primary_click, "
        "is_keyboard, is_return_or_space, expected_result",
        [
            pytest.param(False, True, True, False, False, False, id="not_table_header"),
            pytest.param(
                True, True, True, False, False, True, id="table_header_mouse_primary_click"
            ),
            pytest.param(
                True, True, False, False, False, False, id="table_header_mouse_not_primary"
            ),
            pytest.param(
                True, False, False, True, True, True, id="table_header_keyboard_return_space"
            ),
            pytest.param(
                True, False, False, True, False, False, id="table_header_keyboard_not_return_space"
            ),
            pytest.param(
                True,
                False,
                False,
                False,
                False,
                False,
                id="table_header_neither_mouse_nor_keyboard",
            ),
        ],
    )
    def test_last_event_was_table_sort(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        is_table_header,
        is_mouse_button,
        is_primary_click,
        is_keyboard,
        is_return_or_space,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_table_sort."""

        mock_focus = Mock()
        mock_input_event_manager_deps[
            "focus_manager_instance"
        ].get_locus_of_focus.return_value = mock_focus
        mock_input_event_manager_deps["ax_utilities"].is_table_header.return_value = is_table_header

        input_event_manager.last_event_was_mouse_button = Mock(return_value=is_mouse_button)
        input_event_manager.last_event_was_primary_click = Mock(return_value=is_primary_click)
        input_event_manager.last_event_was_keyboard = Mock(return_value=is_keyboard)
        input_event_manager.last_event_was_return_or_space = Mock(return_value=is_return_or_space)

        result = input_event_manager.last_event_was_table_sort()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "key_string, modifiers, expected_result",
        [
            pytest.param("Left", 0, True, id="left_no_modifiers"),
            pytest.param("Right", 0, True, id="right_no_modifiers"),
            pytest.param("Up", 0, True, id="up_no_modifiers"),
            pytest.param("Down", 0, True, id="down_no_modifiers"),
            pytest.param("Left", 1 << 2, False, id="left_with_ctrl"),
            pytest.param("Left", 1 << 0, False, id="left_with_shift"),
            pytest.param("Left", 1 << 3, False, id="left_with_alt"),
            pytest.param("Left", 1 << 8, False, id="left_with_orca_modifier"),
            pytest.param("a", 0, False, id="non_arrow_key"),
        ],
    )
    def test_last_event_was_unmodified_arrow(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        key_string,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_unmodified_arrow."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, modifiers))

        result = input_event_manager.last_event_was_unmodified_arrow()
        assert result == expected_result

    @pytest.mark.parametrize(
        "modifiers, expected_result",
        [
            pytest.param(1 << 3, 8, id="has_alt_modifier"),  # Returns bitwise result, not boolean
            pytest.param(0, 0, id="no_alt_modifier"),
            pytest.param((1 << 3) | (1 << 2), 8, id="alt_and_ctrl_modifiers"),  # Alt bit is still 8
        ],
    )
    def test_last_event_was_alt_modified(
        self, input_event_manager, mock_input_event_manager_deps, modifiers, expected_result
    ):
        """Test InputEventManager.last_event_was_alt_modified."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=("a", modifiers))

        result = input_event_manager.last_event_was_alt_modified()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("BackSpace", True, id="backspace_key"),
            pytest.param("Delete", False, id="delete_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_backspace(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_backspace."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_backspace()

        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Down", True, id="down_key"),
            pytest.param("Up", False, id="up_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_down(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_down."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_down()

        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("F1", True, id="f1_key"),
            pytest.param("F2", False, id="f2_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_f1(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_f1."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_f1()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Left", True, id="left_key"),
            pytest.param("Right", False, id="right_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_left(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_left."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_left()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Left", True, id="left_key"),
            pytest.param("Right", True, id="right_key"),
            pytest.param("Up", False, id="up_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_left_or_right(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_left_or_right."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_left_or_right()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Page_Up", True, id="page_up_key"),
            pytest.param("Page_Down", True, id="page_down_key"),
            pytest.param("Up", False, id="up_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_page_up_or_page_down(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_page_up_or_page_down."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_page_up_or_page_down()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Right", True, id="right_key"),
            pytest.param("Left", False, id="left_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_right(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_right."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_right()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Return", True, id="return_key"),
            pytest.param("Enter", False, id="enter_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_return(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_return."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_return()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Return", True, id="return_key"),
            pytest.param("space", True, id="space_key"),
            pytest.param(" ", True, id="space_character"),
            pytest.param("Enter", False, id="enter_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_return_or_space(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_return_or_space."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_return_or_space()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Return", True, id="return_key"),
            pytest.param("Tab", True, id="tab_key"),
            pytest.param("space", True, id="space_key"),
            pytest.param(" ", True, id="space_character"),
            pytest.param("Enter", False, id="enter_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_return_tab_or_space(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_return_tab_or_space."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_return_tab_or_space()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param(" ", True, id="space_character"),
            pytest.param("space", True, id="space_key"),
            pytest.param("Return", False, id="return_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_space(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_space."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_space()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Tab", True, id="tab_key"),
            pytest.param("ISO_Left_Tab", False, id="shift_tab_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_tab(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_tab."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_tab()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Up", True, id="up_key"),
            pytest.param("Down", False, id="down_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_up(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_up."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_up()
        assert result == expected_result

    @pytest.mark.parametrize(
        "key_string, expected_result",
        [
            pytest.param("Up", True, id="up_key"),
            pytest.param("Down", True, id="down_key"),
            pytest.param("Left", False, id="left_key"),
            pytest.param("a", False, id="regular_key"),
        ],
    )
    def test_last_event_was_up_or_down(
        self, input_event_manager, mock_input_event_manager_deps, key_string, expected_result
    ):
        """Test InputEventManager.last_event_was_up_or_down."""

        input_event_manager._last_key_and_modifiers = Mock(return_value=(key_string, 0))

        result = input_event_manager.last_event_was_up_or_down()
        assert result == expected_result

    @pytest.mark.parametrize(
        "keynames, modifiers, expected_result",
        [
            pytest.param(["Delete"], 0, True, id="delete_key"),
            pytest.param(["KP_Delete"], 0, True, id="keypad_delete"),
            pytest.param(["d"], 1 << 2, True, id="ctrl_d"),
            pytest.param(["d"], 0, False, id="d_without_ctrl"),
            pytest.param(["a"], 1 << 2, False, id="ctrl_a"),
        ],
    )
    def test_last_event_was_delete(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        keynames,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_delete."""

        input_event_manager._last_keycode_and_modifiers = Mock(return_value=(42, modifiers))
        input_event_manager._all_names_for_key_code = Mock(return_value=keynames)

        result = input_event_manager.last_event_was_delete()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "keynames, modifiers, expected_result",
        [
            pytest.param(["x"], (1 << 2), True, id="ctrl_x"),
            pytest.param(["x"], (1 << 2) | (1 << 0), False, id="ctrl_shift_x"),
            pytest.param(["x"], 0, False, id="x_without_ctrl"),
            pytest.param(["y"], 1 << 2, False, id="ctrl_y"),
        ],
    )
    def test_last_event_was_cut(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        keynames,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_cut."""

        input_event_manager._last_keycode_and_modifiers = Mock(return_value=(42, modifiers))
        input_event_manager._all_names_for_key_code = Mock(return_value=keynames)

        result = input_event_manager.last_event_was_cut()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "keynames, modifiers, is_terminal, expected_result",
        [
            pytest.param(["c"], (1 << 2), False, True, id="ctrl_c_non_terminal"),
            pytest.param(["c"], (1 << 2) | (1 << 0), True, True, id="ctrl_shift_c_terminal"),
            pytest.param(["c"], (1 << 2) | (1 << 0), False, False, id="ctrl_shift_c_non_terminal"),
            pytest.param(["c"], (1 << 2), True, False, id="ctrl_c_terminal"),
            pytest.param(["c"], 0, False, False, id="c_without_ctrl"),
            pytest.param(["x"], 1 << 2, False, False, id="ctrl_x"),
        ],
    )
    def test_last_event_was_copy(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        keynames,
        modifiers,
        is_terminal,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_copy."""

        mock_object = Mock()
        mock_last_event = Mock()
        mock_last_event.get_object.return_value = mock_object
        input_event_manager._last_input_event = mock_last_event

        input_event_manager._last_keycode_and_modifiers = Mock(return_value=(42, modifiers))
        input_event_manager._all_names_for_key_code = Mock(return_value=keynames)
        mock_input_event_manager_deps["ax_utilities"].is_terminal.return_value = is_terminal

        result = input_event_manager.last_event_was_copy()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "keynames, modifiers, is_terminal, expected_result",
        [
            pytest.param(["v"], (1 << 2), False, True, id="ctrl_v_non_terminal"),
            pytest.param(["v"], (1 << 2) | (1 << 0), True, True, id="ctrl_shift_v_terminal"),
            pytest.param(["v"], (1 << 2) | (1 << 0), False, False, id="ctrl_shift_v_non_terminal"),
            pytest.param(["v"], (1 << 2), True, False, id="ctrl_v_terminal"),
            pytest.param(["v"], 0, False, False, id="v_without_ctrl"),
            pytest.param(["x"], 1 << 2, False, False, id="ctrl_x"),
        ],
    )
    def test_last_event_was_paste(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        keynames,
        modifiers,
        is_terminal,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_paste."""

        mock_object = Mock()
        mock_last_event = Mock()
        mock_last_event.get_object.return_value = mock_object
        input_event_manager._last_input_event = mock_last_event

        input_event_manager._last_keycode_and_modifiers = Mock(return_value=(42, modifiers))
        input_event_manager._all_names_for_key_code = Mock(return_value=keynames)
        mock_input_event_manager_deps["ax_utilities"].is_terminal.return_value = is_terminal

        result = input_event_manager.last_event_was_paste()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "keynames, modifiers, expected_result",
        [
            pytest.param(["z"], (1 << 2), True, id="ctrl_z"),
            pytest.param(["z"], (1 << 2) | (1 << 0), False, id="ctrl_shift_z"),
            pytest.param(["z"], 0, False, id="z_without_ctrl"),
            pytest.param(["y"], 1 << 2, False, id="ctrl_y"),
        ],
    )
    def test_last_event_was_undo(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        keynames,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_undo."""

        input_event_manager._last_keycode_and_modifiers = Mock(return_value=(42, modifiers))
        input_event_manager._all_names_for_key_code = Mock(return_value=keynames)

        result = input_event_manager.last_event_was_undo()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "keynames, modifiers, expected_result",
        [
            pytest.param(["z"], (1 << 2) | (1 << 0), True, id="ctrl_shift_z"),
            pytest.param(["y"], (1 << 2), True, id="ctrl_y_libreoffice"),
            pytest.param(["z"], (1 << 2), False, id="ctrl_z"),
            pytest.param(["y"], (1 << 2) | (1 << 0), False, id="ctrl_shift_y"),
            pytest.param(["z"], 0, False, id="z_without_ctrl"),
            pytest.param(["x"], 1 << 2, False, id="ctrl_x"),
        ],
    )
    def test_last_event_was_redo(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        keynames,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_redo."""

        input_event_manager._last_keycode_and_modifiers = Mock(return_value=(42, modifiers))
        input_event_manager._all_names_for_key_code = Mock(return_value=keynames)

        result = input_event_manager.last_event_was_redo()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "keynames, modifiers, expected_result",
        [
            pytest.param(["a"], (1 << 2), True, id="ctrl_a"),
            pytest.param(["a"], (1 << 2) | (1 << 0), False, id="ctrl_shift_a"),
            pytest.param(["a"], 0, False, id="a_without_ctrl"),
            pytest.param(["x"], 1 << 2, False, id="ctrl_x"),
        ],
    )
    def test_last_event_was_select_all(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        keynames,
        modifiers,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_select_all."""

        input_event_manager._last_keycode_and_modifiers = Mock(return_value=(42, modifiers))
        input_event_manager._all_names_for_key_code = Mock(return_value=keynames)

        result = input_event_manager.last_event_was_select_all()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "is_mouse_button, button, pressed, expected_result",
        [
            pytest.param(True, "1", True, True, id="primary_click"),
            pytest.param(True, "1", False, False, id="primary_release"),
            pytest.param(True, "2", True, False, id="middle_click"),
            pytest.param(False, "1", True, False, id="not_mouse_button"),
        ],
    )
    def test_last_event_was_primary_click(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        is_mouse_button,
        button,
        pressed,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_primary_click."""

        mock_last_event = Mock()
        mock_last_event.button = button
        mock_last_event.pressed = pressed
        input_event_manager._last_input_event = mock_last_event

        input_event_manager.last_event_was_mouse_button = Mock(return_value=is_mouse_button)

        result = input_event_manager.last_event_was_primary_click()

        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "is_mouse_button, button, pressed, expected_result",
        [
            pytest.param(True, "1", False, True, id="primary_release"),
            pytest.param(True, "1", True, False, id="primary_click"),
            pytest.param(True, "2", False, False, id="middle_release"),
            pytest.param(False, "1", False, False, id="not_mouse_button"),
        ],
    )
    def test_last_event_was_primary_release(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        is_mouse_button,
        button,
        pressed,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_primary_release."""

        mock_last_event = Mock()
        mock_last_event.button = button
        mock_last_event.pressed = pressed
        input_event_manager._last_input_event = mock_last_event

        input_event_manager.last_event_was_mouse_button = Mock(return_value=is_mouse_button)

        result = input_event_manager.last_event_was_primary_release()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "is_mouse_button, button, expected_result",
        [
            pytest.param(True, "1", True, id="primary_button"),
            pytest.param(True, "2", False, id="middle_button"),
            pytest.param(True, "3", False, id="secondary_button"),
            pytest.param(False, "1", False, id="not_mouse_button"),
        ],
    )
    def test_last_event_was_primary_click_or_release(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        is_mouse_button,
        button,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_primary_click_or_release."""

        mock_last_event = Mock()
        mock_last_event.button = button
        input_event_manager._last_input_event = mock_last_event

        input_event_manager.last_event_was_mouse_button = Mock(return_value=is_mouse_button)

        result = input_event_manager.last_event_was_primary_click_or_release()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "is_mouse_button, button, pressed, expected_result",
        [
            pytest.param(True, "2", True, True, id="middle_click"),
            pytest.param(True, "2", False, False, id="middle_release"),
            pytest.param(True, "1", True, False, id="primary_click"),
            pytest.param(False, "2", True, False, id="not_mouse_button"),
        ],
    )
    def test_last_event_was_middle_click(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        is_mouse_button,
        button,
        pressed,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_middle_click."""

        mock_last_event = Mock()
        mock_last_event.button = button
        mock_last_event.pressed = pressed
        input_event_manager._last_input_event = mock_last_event

        input_event_manager.last_event_was_mouse_button = Mock(return_value=is_mouse_button)

        result = input_event_manager.last_event_was_middle_click()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "is_mouse_button, button, pressed, expected_result",
        [
            pytest.param(True, "2", False, True, id="middle_release"),
            pytest.param(True, "2", True, False, id="middle_click"),
            pytest.param(True, "1", False, False, id="primary_release"),
            pytest.param(False, "2", False, False, id="not_mouse_button"),
        ],
    )
    def test_last_event_was_middle_release(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        is_mouse_button,
        button,
        pressed,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_middle_release."""

        mock_last_event = Mock()
        mock_last_event.button = button
        mock_last_event.pressed = pressed
        input_event_manager._last_input_event = mock_last_event

        input_event_manager.last_event_was_mouse_button = Mock(return_value=is_mouse_button)

        result = input_event_manager.last_event_was_middle_release()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "is_mouse_button, button, pressed, expected_result",
        [
            pytest.param(True, "3", True, True, id="secondary_click"),
            pytest.param(True, "3", False, False, id="secondary_release"),
            pytest.param(True, "1", True, False, id="primary_click"),
            pytest.param(False, "3", True, False, id="not_mouse_button"),
        ],
    )
    def test_last_event_was_secondary_click(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        is_mouse_button,
        button,
        pressed,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_secondary_click."""

        mock_last_event = Mock()
        mock_last_event.button = button
        mock_last_event.pressed = pressed
        input_event_manager._last_input_event = mock_last_event

        input_event_manager.last_event_was_mouse_button = Mock(return_value=is_mouse_button)

        result = input_event_manager.last_event_was_secondary_click()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "is_mouse_button, button, pressed, expected_result",
        [
            pytest.param(True, "3", False, True, id="secondary_release"),
            pytest.param(True, "3", True, False, id="secondary_click"),
            pytest.param(True, "1", False, False, id="primary_release"),
            pytest.param(False, "3", False, False, id="not_mouse_button"),
        ],
    )
    def test_last_event_was_secondary_release(
        self,
        input_event_manager,
        mock_input_event_manager_deps,
        is_mouse_button,
        button,
        pressed,
        expected_result,
    ):
        """Test InputEventManager.last_event_was_secondary_release."""

        mock_last_event = Mock()
        mock_last_event.button = button
        mock_last_event.pressed = pressed
        input_event_manager._last_input_event = mock_last_event

        input_event_manager.last_event_was_mouse_button = Mock(return_value=is_mouse_button)

        result = input_event_manager.last_event_was_secondary_release()
        assert result == expected_result
        if expected_result:
            mock_input_event_manager_deps["debug"].print_message.assert_called()

    def test_get_manager(self, mock_input_event_manager_deps):
        """Test get_manager function returns singleton."""

        from orca.input_event_manager import get_manager

        manager1 = get_manager()
        manager2 = get_manager()
        assert manager1 is manager2
