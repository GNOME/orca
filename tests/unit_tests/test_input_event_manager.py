# Unit tests for input_event_manager.py methods.
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
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines
# pylint: disable=too-many-instance-attributes

"""Unit tests for input_event_manager.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import call
import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestInputEventManager:
    """Test InputEventManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for input_event_manager module testing."""

        additional_modules = ["orca.ax_utilities", "gi.repository"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_WARNING = 2
        debug_mock.LEVEL_SEVERE = 3
        debug_mock.debugLevel = 0

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_mgr_instance = test_context.Mock()
        focus_mgr_instance.get_locus_of_focus = test_context.Mock()
        focus_mgr_instance.get_active_window = test_context.Mock()
        focus_mgr_instance.focus_and_window_are_unknown = test_context.Mock(
            return_value=False
        )
        focus_mgr_instance.clear_state = test_context.Mock()
        focus_manager_mock.get_manager = test_context.Mock(return_value=focus_mgr_instance)

        script_manager_mock = essential_modules["orca.script_manager"]
        script_mgr_instance = test_context.Mock()
        script_instance = test_context.Mock()
        script_instance.app = test_context.Mock()
        script_instance.event_cache = {}
        script_instance.listeners = {}
        script_instance.is_activatable_event = test_context.Mock(return_value=True)
        script_instance.force_script_activation = test_context.Mock(return_value=False)
        script_instance.present_if_inactive = False
        script_mgr_instance.get_active_script = test_context.Mock(
            return_value=script_instance
        )
        script_mgr_instance.get_script = test_context.Mock(return_value=script_instance)
        script_mgr_instance.set_active_script = test_context.Mock()
        script_mgr_instance.get_default_script = test_context.Mock(
            return_value=script_instance
        )
        script_mgr_instance.reclaim_scripts = test_context.Mock()
        script_manager_mock.get_manager = test_context.Mock(return_value=script_mgr_instance)

        input_event_mock = essential_modules["orca.input_event"]

        class MockKeyboardEvent:
            """Mock KeyboardEvent class for testing."""

            def __init__(self, pressed=True, keycode=65, keysym=97, modifiers=0, text="a"):
                self.process = test_context.Mock()
                self.set_window = test_context.Mock()
                self.set_object = test_context.Mock()
                self.set_script = test_context.Mock()
                self.set_click_count = test_context.Mock()
                self.is_modifier_key = test_context.Mock(return_value=False)
                self.is_pressed_key = test_context.Mock(return_value=True)
                self.get_window = test_context.Mock()
                self.get_object = test_context.Mock()
                self.get_script = test_context.Mock()
                self.get_click_count = test_context.Mock(return_value=1)
                self.is_printable_key = test_context.Mock(return_value=True)
                self.as_single_line_string = test_context.Mock(return_value="KeyboardEvent")
                self.pressed = pressed
                self.keycode = keycode
                self.keysym = keysym
                self.modifiers = modifiers
                self.text = text
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

            def __init__(self, *_args, **_kwargs):
                self.process = test_context.Mock(return_value=True)

        class MockMouseButtonEvent:
            """Mock MouseButtonEvent class for testing."""

            def __init__(self, *_args, **_kwargs):
                self.set_click_count = test_context.Mock()
                self.get_click_count = test_context.Mock(return_value=1)
                self.button = "1"
                self.pressed = True
                self.time = 1000

        input_event_mock.KeyboardEvent = MockKeyboardEvent
        input_event_mock.BrailleEvent = MockBrailleEvent
        input_event_mock.MouseButtonEvent = MockMouseButtonEvent

        settings_mock = essential_modules["orca.settings"]
        settings_mock.doubleClickTimeout = 500

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_class = test_context.Mock()
        ax_object_class.get_action_key_binding = test_context.Mock(return_value="Alt+F")
        ax_object_mock.AXObject = ax_object_class

        ax_utilities_mock = essential_modules["orca.ax_utilities"]
        ax_utilities_class = test_context.Mock()
        ax_utilities_class.can_be_active_window = test_context.Mock(return_value=True)
        ax_utilities_class.find_active_window = test_context.Mock(return_value=None)
        ax_utilities_class.is_single_line = test_context.Mock(return_value=False)
        ax_utilities_class.is_widget_controlled_by_line_navigation = test_context.Mock(
            return_value=False
        )
        ax_utilities_class.is_table_header = test_context.Mock(return_value=False)
        ax_utilities_class.is_terminal = test_context.Mock(return_value=False)
        ax_utilities_mock.AXUtilities = ax_utilities_class

        gi_repo_mock = essential_modules["gi.repository"]

        atspi_mock = test_context.Mock()
        atspi_mock.get_version = test_context.Mock(return_value=(2, 56, 0))
        atspi_mock.Device = test_context.Mock()
        atspi_mock.Device.new_full = test_context.Mock()
        atspi_mock.Device.new = test_context.Mock()
        atspi_mock.Device.grab_keyboard = test_context.Mock()
        atspi_mock.Device.ungrab_keyboard = test_context.Mock()
        atspi_mock.KeyDefinition = test_context.Mock()
        atspi_mock.ModifierType = test_context.Mock()
        atspi_mock.ModifierType.CONTROL = 2
        atspi_mock.ModifierType.SHIFT = 0
        atspi_mock.ModifierType.ALT = 3
        gi_repo_mock.Atspi = atspi_mock

        essential_modules["focus_manager_instance"] = focus_mgr_instance
        essential_modules["script_manager_instance"] = script_mgr_instance
        essential_modules["script_instance"] = script_instance
        essential_modules["ax_object_class"] = ax_object_class
        essential_modules["ax_utilities_class"] = ax_utilities_class
        essential_modules["atspi"] = atspi_mock
        return essential_modules

    def _setup_input_event_manager(self, test_context) -> tuple:
        """Helper method to set up InputEventManager with dependencies."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        test_context.patch(
            "orca.input_event_manager.debug", new=essential_modules["orca.debug"]
        )
        test_context.patch(
            "orca.input_event_manager.focus_manager", new=essential_modules["orca.focus_manager"]
        )
        test_context.patch(
            "orca.input_event_manager.script_manager", new=essential_modules["orca.script_manager"]
        )
        test_context.patch(
            "orca.input_event_manager.input_event", new=essential_modules["orca.input_event"]
        )
        test_context.patch(
            "orca.input_event_manager.settings", new=essential_modules["orca.settings"]
        )
        test_context.patch(
            "orca.input_event_manager.AXObject", new=essential_modules["ax_object_class"]
        )
        test_context.patch(
            "orca.input_event_manager.AXUtilities", new=essential_modules["ax_utilities_class"]
        )
        test_context.patch(
            "orca.input_event_manager.Atspi", new=essential_modules["atspi"]
        )

        from orca.input_event_manager import InputEventManager

        return InputEventManager(), essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test InputEventManager.__init__."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        assert input_event_manager._last_input_event is None
        assert input_event_manager._last_non_modifier_key_event is None
        assert input_event_manager._device is None
        assert not input_event_manager._mapped_keycodes
        assert not input_event_manager._mapped_keysyms
        assert not input_event_manager._grabbed_bindings

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "new_atspi",
                "atspi_version": (2, 56, 0),
                "device_factory_method": "new_full",
            },
            {
                "id": "old_atspi",
                "atspi_version": (2, 54, 0),
                "device_factory_method": "new",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_start_key_watcher_scenarios(self, test_context, case: dict) -> None:
        """Test InputEventManager.start_key_watcher with different Atspi versions."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_device = test_context.Mock()
        device_factory = getattr(essential_modules["atspi"].Device, case["device_factory_method"])
        device_factory.return_value = mock_device
        essential_modules["atspi"].get_version.return_value = case["atspi_version"]

        input_event_manager.start_key_watcher()

        if case["device_factory_method"] == "new_full":
            device_factory.assert_called_once_with("org.gnome.Orca")
        else:
            device_factory.assert_called_once()

        mock_device.add_key_watcher.assert_called_once_with(
            input_event_manager.process_keyboard_event
        )
        assert input_event_manager._device == mock_device

    def test_stop_key_watcher(self, test_context: OrcaTestContext) -> None:
        """Test InputEventManager.stop_key_watcher."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._device = test_context.Mock()
        input_event_manager.stop_key_watcher()
        assert input_event_manager._device is None
        essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "empty",
                "binding_count": 0,
                "expected_call_count": 1,
                "expected_message_pattern": "0 grabbed key bindings",
            },
            {
                "id": "with_bindings",
                "binding_count": 2,
                "expected_call_count": 3,
                "expected_message_pattern": "2 grabbed key bindings",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_check_grabbed_bindings_scenarios(self, test_context, case: dict) -> None:
        """Test InputEventManager.check_grabbed_bindings scenarios."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)

        if case["binding_count"] > 0:
            mock_binding = test_context.Mock()
            test_context.patch_object(
                mock_binding, "__str__", new=test_context.Mock(return_value="test_binding")
            )
            input_event_manager._grabbed_bindings = {123: mock_binding, 456: mock_binding}

        input_event_manager.check_grabbed_bindings()
        calls = essential_modules["orca.debug"].print_message.call_args_list
        assert len(calls) == case["expected_call_count"]
        assert case["expected_message_pattern"] in calls[0][0][1]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "disabled",
                "scenario": "disabled",
                "is_enabled": False,
                "is_bound": True,
                "has_grabs": False,
                "has_device": False,
                "expected_result": [],
                "expects_debug_call": False,
            },
            {
                "id": "unbound",
                "scenario": "unbound",
                "is_enabled": True,
                "is_bound": False,
                "has_grabs": False,
                "has_device": False,
                "expected_result": [],
                "expects_debug_call": False,
            },
            {
                "id": "has_grabs",
                "scenario": "has_grabs",
                "is_enabled": True,
                "is_bound": True,
                "has_grabs": True,
                "has_device": False,
                "expected_result": [],
                "expects_debug_call": True,
            },
            {
                "id": "no_device",
                "scenario": "no_device",
                "is_enabled": True,
                "is_bound": True,
                "has_grabs": False,
                "has_device": False,
                "expected_result": [],
                "expects_debug_call": True,
            },
            {
                "id": "success",
                "scenario": "success",
                "is_enabled": True,
                "is_bound": True,
                "has_grabs": False,
                "has_device": True,
                "expected_result": [111, 222],
                "expects_debug_call": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_add_grabs_for_keybinding_scenarios(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test InputEventManager.add_grabs_for_keybinding with various scenarios."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)

        mock_binding = test_context.Mock()
        mock_binding.is_enabled.return_value = case["is_enabled"]
        mock_binding.is_bound.return_value = case["is_bound"]
        mock_binding.has_grabs.return_value = case["has_grabs"]

        if case["has_device"]:
            mock_device = test_context.Mock()
            mock_device.add_key_grab.side_effect = [111, 222]
            input_event_manager._device = mock_device
            mock_kd1 = test_context.Mock()
            mock_kd2 = test_context.Mock()
            mock_binding.key_definitions.return_value = [mock_kd1, mock_kd2]

        result = input_event_manager.add_grabs_for_keybinding(mock_binding)

        if case["scenario"] == "success":
            assert result == case["expected_result"]
            assert input_event_manager._grabbed_bindings[111] == mock_binding
            assert input_event_manager._grabbed_bindings[222] == mock_binding
            mock_device.add_key_grab.assert_has_calls([call(mock_kd1, None), call(mock_kd2, None)])
        else:
            assert result == case["expected_result"]

        if case["expects_debug_call"]:
            essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_device",
                "scenario": "no_device",
                "has_device": False,
                "grab_ids": [],
                "has_grabbed_bindings": False,
                "expects_debug_tokens": True,
                "expects_debug_message": False,
                "expects_device_calls": False,
            },
            {
                "id": "no_grabs",
                "scenario": "no_grabs",
                "has_device": True,
                "grab_ids": [],
                "has_grabbed_bindings": False,
                "expects_debug_tokens": True,
                "expects_debug_message": False,
                "expects_device_calls": False,
            },
            {
                "id": "success",
                "scenario": "success",
                "has_device": True,
                "grab_ids": [111, 222],
                "has_grabbed_bindings": True,
                "expects_debug_tokens": False,
                "expects_debug_message": False,
                "expects_device_calls": True,
            },
            {
                "id": "missing_grab",
                "scenario": "missing_grab",
                "has_device": True,
                "grab_ids": [999],
                "has_grabbed_bindings": False,
                "expects_debug_tokens": False,
                "expects_debug_message": True,
                "expects_device_calls": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_remove_grabs_for_keybinding_scenarios(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test InputEventManager.remove_grabs_for_keybinding with various scenarios."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)

        if case["has_device"]:
            mock_device = test_context.Mock()
            input_event_manager._device = mock_device

        if case["has_grabbed_bindings"]:
            input_event_manager._grabbed_bindings = {
                111: test_context.Mock(),
                222: test_context.Mock(),
            }

        mock_binding = test_context.Mock()
        mock_binding.get_grab_ids.return_value = case["grab_ids"]

        input_event_manager.remove_grabs_for_keybinding(mock_binding)

        if case["expects_debug_tokens"]:
            essential_modules["orca.debug"].print_tokens.assert_called()

        if case["expects_debug_message"]:
            essential_modules["orca.debug"].print_message.assert_called()

        if case["expects_device_calls"]:
            if case["scenario"] == "success":
                mock_device.remove_key_grab.assert_has_calls([call(111), call(222)])
                assert 111 not in input_event_manager._grabbed_bindings
                assert 222 not in input_event_manager._grabbed_bindings
            elif case["scenario"] == "missing_grab":
                mock_device.remove_key_grab.assert_called_once_with(999)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "keycode_no_device",
                "method_type": "keycode",
                "has_device": False,
                "input_value": 42,
                "expected_result": 0,
                "device_method": None,
                "device_return_value": None,
                "mapped_collection": None,
            },
            {
                "id": "keycode_success",
                "method_type": "keycode",
                "has_device": True,
                "input_value": 42,
                "expected_result": 8,
                "device_method": "map_modifier",
                "device_return_value": 8,
                "mapped_collection": "_mapped_keycodes",
            },
            {
                "id": "keysym_no_device",
                "method_type": "keysym",
                "has_device": False,
                "input_value": 0x61,
                "expected_result": 0,
                "device_method": None,
                "device_return_value": None,
                "mapped_collection": None,
            },
            {
                "id": "keysym_success",
                "method_type": "keysym",
                "has_device": True,
                "input_value": 0x61,
                "expected_result": 16,
                "device_method": "map_keysym_modifier",
                "device_return_value": 16,
                "mapped_collection": "_mapped_keysyms",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_map_modifier_scenarios(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test InputEventManager modifier mapping methods with various scenarios."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        if case["has_device"]:
            mock_device = test_context.Mock()
            if case["device_method"]:
                getattr(mock_device, case["device_method"]).return_value = case[
                    "device_return_value"
                ]
            input_event_manager._device = mock_device

        if case["method_type"] == "keycode":
            result = input_event_manager.map_keycode_to_modifier(case["input_value"])
        else:
            result = input_event_manager.map_keysym_to_modifier(case["input_value"])

        assert result == case["expected_result"]

        if case["has_device"] and case["device_method"] and case["mapped_collection"]:
            getattr(mock_device, case["device_method"]).assert_called_once_with(case["input_value"])
            collection = getattr(input_event_manager, case["mapped_collection"])
            assert case["input_value"] in collection
        elif not case["has_device"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_device",
                "has_device": False,
                "expects_debug_call": True,
                "expects_unmap_calls": False,
            },
            {
                "id": "success",
                "has_device": True,
                "expects_debug_call": False,
                "expects_unmap_calls": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_unmap_all_modifiers_scenarios(self, test_context, case: dict) -> None:
        """Test InputEventManager.unmap_all_modifiers scenarios."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._mapped_keycodes = [42, 43]
        input_event_manager._mapped_keysyms = [0x61, 0x62]

        if case["has_device"]:
            mock_device = test_context.Mock()
            input_event_manager._device = mock_device

        input_event_manager.unmap_all_modifiers()

        if case["expects_debug_call"]:
            essential_modules["orca.debug"].print_message.assert_called()

        if case["expects_unmap_calls"]:
            mock_device.unmap_modifier.assert_has_calls([call(42), call(43)])
            mock_device.unmap_keysym_modifier.assert_has_calls([call(0x61), call(0x62)])
            assert not input_event_manager._mapped_keycodes
            assert not input_event_manager._mapped_keysyms

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "add_no_device",
                "operation": "add",
                "scenario": "no_device",
                "has_device": False,
                "grab_id": None,
                "expected_result": -1,
                "expects_debug_call": True,
            },
            {
                "id": "add_success",
                "operation": "add",
                "scenario": "success",
                "has_device": True,
                "grab_id": 789,
                "expected_result": 789,
                "expects_debug_call": False,
            },
            {
                "id": "remove_no_device",
                "operation": "remove",
                "scenario": "no_device",
                "has_device": False,
                "grab_id": 789,
                "expected_result": None,
                "expects_debug_call": True,
            },
            {
                "id": "remove_success",
                "operation": "remove",
                "scenario": "success",
                "has_device": True,
                "grab_id": 789,
                "expected_result": None,
                "expects_debug_call": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_grab_for_modifier_scenarios(self, test_context, case: dict) -> None:
        """Test InputEventManager add/remove_grab_for_modifier scenarios."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)

        if case["has_device"]:
            mock_device = test_context.Mock()
            if case["operation"] == "add":
                mock_device.add_key_grab.return_value = case["grab_id"]
            input_event_manager._device = mock_device

        if case["operation"] == "add":
            result = input_event_manager.add_grab_for_modifier("Shift", 0xFFE1, 50)
            if case["expected_result"] is not None:
                assert result == case["expected_result"]
            if case["has_device"] and case["scenario"] == "success":
                mock_device.add_key_grab.assert_called_once()
        else:
            input_event_manager.remove_grab_for_modifier("Shift", case["grab_id"])
            if case["has_device"] and case["scenario"] == "success":
                mock_device.remove_key_grab.assert_called_once_with(case["grab_id"])

        if case["expects_debug_call"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "grab_without_reason",
                "operation": "grab",
                "reason": None,
                "expected_reason_text": None,
            },
            {
                "id": "grab_with_reason",
                "operation": "grab",
                "reason": "learn mode",
                "expected_reason_text": "learn mode",
            },
            {
                "id": "ungrab_without_reason",
                "operation": "ungrab",
                "reason": None,
                "expected_reason_text": None,
            },
            {
                "id": "ungrab_with_reason",
                "operation": "ungrab",
                "reason": "exiting learn mode",
                "expected_reason_text": "exiting learn mode",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_keyboard_grab_scenarios(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test InputEventManager keyboard grab/ungrab operations with and without reasons."""
        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_device = test_context.Mock()
        input_event_manager._device = mock_device

        if case["operation"] == "grab":
            if case["reason"]:
                input_event_manager.grab_keyboard(case["reason"])
            else:
                input_event_manager.grab_keyboard()
            essential_modules["atspi"].Device.grab_keyboard.assert_called_once_with(mock_device)
        else:
            if case["reason"]:
                input_event_manager.ungrab_keyboard(case["reason"])
            else:
                input_event_manager.ungrab_keyboard()
            essential_modules["atspi"].Device.ungrab_keyboard.assert_called_once_with(mock_device)

        if case["expected_reason_text"]:
            debug_calls = essential_modules["orca.debug"].print_message.call_args_list
            assert any(case["expected_reason_text"] in str(call) for call in debug_calls)

    def test_process_braille_event(self, test_context: OrcaTestContext) -> None:
        """Test InputEventManager.process_braille_event."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_event = test_context.Mock()
        result = input_event_manager.process_braille_event(mock_event)
        assert result is True
        assert isinstance(
            input_event_manager._last_input_event,
            essential_modules["orca.input_event"].BrailleEvent,
        )
        assert input_event_manager._last_non_modifier_key_event is None

    def test_process_mouse_button_event(self, test_context: OrcaTestContext) -> None:
        """Test InputEventManager.process_mouse_button_event."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_event = test_context.Mock()
        input_event_manager._determine_mouse_event_click_count = test_context.Mock(return_value=2)
        input_event_manager.process_mouse_button_event(mock_event)
        assert isinstance(
            input_event_manager._last_input_event,
            essential_modules["orca.input_event"].MouseButtonEvent,
        )
        input_event_manager._last_input_event.set_click_count.assert_called_once_with(2)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "key_press_active_window",
                "pressed": True,
                "keycode": 65,
                "keysym": 97,
                "modifiers": 0,
                "text": "a",
                "window_can_be_active": True,
                "new_window_found": None,
            },
            {
                "id": "key_press_inactive_window_with_alternative",
                "pressed": True,
                "keycode": 65,
                "keysym": 97,
                "modifiers": 0,
                "text": "a",
                "window_can_be_active": False,
                "new_window_found": "mock_window",
            },
            {
                "id": "key_press_inactive_window_no_alternative",
                "pressed": True,
                "keycode": 65,
                "keysym": 97,
                "modifiers": 0,
                "text": "a",
                "window_can_be_active": False,
                "new_window_found": None,
            },
            {
                "id": "key_release",
                "pressed": False,
                "keycode": 65,
                "keysym": 97,
                "modifiers": 0,
                "text": "a",
                "window_can_be_active": True,
                "new_window_found": None,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_process_keyboard_event(self, test_context, case: dict) -> None:
        """Test InputEventManager.process_keyboard_event."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        new_window_found = case["new_window_found"]
        if new_window_found == "mock_window":
            new_window_found = test_context.Mock()
        mock_device = test_context.Mock()
        mock_window = test_context.Mock()
        mock_focus = test_context.Mock()
        mock_script = test_context.Mock()
        mock_focus_manager = essential_modules["orca.focus_manager"]
        mock_focus_manager.get_active_window.return_value = mock_window
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        mock_script_manager = essential_modules["orca.script_manager"]
        mock_script_manager.get_active_script.return_value = mock_script
        essential_modules["ax_utilities_class"].can_be_active_window.return_value = case[
            "window_can_be_active"
        ]
        essential_modules["ax_utilities_class"].find_active_window.return_value = new_window_found
        input_event_manager._determine_keyboard_event_click_count = test_context.Mock(
            return_value=1
        )
        result = input_event_manager.process_keyboard_event(
            mock_device,
            case["pressed"],
            case["keycode"],
            case["keysym"],
            case["modifiers"],
            case["text"],
        )
        assert result is True
        assert isinstance(
            input_event_manager._last_input_event,
            essential_modules["orca.input_event"].KeyboardEvent,
        )
        input_event_manager._last_input_event.process.assert_called_once()

    def test_process_keyboard_event_duplicate(self, test_context: OrcaTestContext) -> None:
        """Test InputEventManager.process_keyboard_event with duplicate event."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_device = test_context.Mock()
        keyboard_event_instance = essential_modules["orca.input_event"].KeyboardEvent(
            True, 65, 97, 0, "a"
        )
        input_event_manager._last_input_event = keyboard_event_instance
        result = input_event_manager.process_keyboard_event(mock_device, True, 65, 97, 0, "a")
        assert result is False
        essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "keyboard_true",
                "method_name": "last_event_was_keyboard",
                "event_class_name": "KeyboardEvent",
                "expected_result": True,
            },
            {
                "id": "keyboard_false",
                "method_name": "last_event_was_keyboard",
                "event_class_name": "MouseButtonEvent",
                "expected_result": False,
            },
            {
                "id": "mouse_button_true",
                "method_name": "last_event_was_mouse_button",
                "event_class_name": "MouseButtonEvent",
                "expected_result": True,
            },
            {
                "id": "mouse_button_false",
                "method_name": "last_event_was_mouse_button",
                "event_class_name": "KeyboardEvent",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_basic_event_types(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test InputEventManager basic event type detection methods."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)

        if case["event_class_name"] == "KeyboardEvent":
            event_class = essential_modules["orca.input_event"].KeyboardEvent
            mock_event = event_class()
        elif case["event_class_name"] == "MouseButtonEvent":
            event_class = essential_modules["orca.input_event"].MouseButtonEvent
            mock_event = event_class()
        else:
            mock_event = test_context.Mock()

        input_event_manager._last_input_event = mock_event
        method = getattr(input_event_manager, case["method_name"])
        result = method()
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "event1_none",
                "event1": None,
                "event2": "mock_event",
                "event1_pressed": None,
                "event2_pressed": None,
                "same_id": None,
                "same_hw_code": None,
                "same_keyval": None,
                "event1_modifier": None,
                "same_modifiers": None,
                "expected_result": False,
            },
            {
                "id": "event2_none",
                "event1": "mock_event",
                "event2": None,
                "event1_pressed": None,
                "event2_pressed": None,
                "same_id": None,
                "same_hw_code": None,
                "same_keyval": None,
                "event1_modifier": None,
                "same_modifiers": None,
                "expected_result": False,
            },
            {
                "id": "release_for_press",
                "event1": "mock_event1",
                "event2": "mock_event2",
                "event1_pressed": False,
                "event2_pressed": True,
                "same_id": True,
                "same_hw_code": True,
                "same_keyval": True,
                "event1_modifier": False,
                "same_modifiers": True,
                "expected_result": True,
            },
            {
                "id": "both_pressed",
                "event1": "mock_event1",
                "event2": "mock_event2",
                "event1_pressed": True,
                "event2_pressed": True,
                "same_id": True,
                "same_hw_code": True,
                "same_keyval": True,
                "event1_modifier": False,
                "same_modifiers": True,
                "expected_result": False,
            },
            {
                "id": "both_released",
                "event1": "mock_event1",
                "event2": "mock_event2",
                "event1_pressed": False,
                "event2_pressed": False,
                "same_id": True,
                "same_hw_code": True,
                "same_keyval": True,
                "event1_modifier": False,
                "same_modifiers": True,
                "expected_result": False,
            },
            {
                "id": "different_id",
                "event1": "mock_event1",
                "event2": "mock_event2",
                "event1_pressed": False,
                "event2_pressed": True,
                "same_id": False,
                "same_hw_code": True,
                "same_keyval": True,
                "event1_modifier": False,
                "same_modifiers": True,
                "expected_result": False,
            },
            {
                "id": "modifier_key_ignore_modifiers",
                "event1": "mock_event1",
                "event2": "mock_event2",
                "event1_pressed": False,
                "event2_pressed": True,
                "same_id": True,
                "same_hw_code": True,
                "same_keyval": True,
                "event1_modifier": True,
                "same_modifiers": True,
                "expected_result": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_release_for(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.is_release_for."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        event1 = case["event1"]
        event2 = case["event2"]
        if event1 in ("mock_event", "mock_event1"):
            event1 = test_context.Mock()
        if event2 in ("mock_event", "mock_event2"):
            event2 = test_context.Mock()
        if event1 is not None and event2 is not None:
            keyboard_event_class = essential_modules["orca.input_event"].KeyboardEvent
            event1 = keyboard_event_class()
            event2 = keyboard_event_class()
            event1.is_pressed_key.return_value = case["event1_pressed"]
            event2.is_pressed_key.return_value = case["event2_pressed"]
            event1.id = "test_id" if case["same_id"] else "other_id"
            event2.id = "test_id"
            event1.hw_code = 42 if case["same_hw_code"] else 43
            event2.hw_code = 42
            event1.keyval_name = "a" if case["same_keyval"] else "b"
            event2.keyval_name = "a"
            event1.is_modifier_key = case["event1_modifier"]
            event1.modifiers = 4 if case["same_modifiers"] else 8
            event2.modifiers = 4
            event1.as_single_line_string.return_value = "event1"
            event2.as_single_line_string.return_value = "event2"
            result = input_event_manager.is_release_for(event1, event2)
            assert result == case["expected_result"]

    def test_last_event_equals_or_is_release_for_event_no_last_event(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test InputEventManager.last_event_equals_or_is_release_for_event with no last event."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        mock_event = test_context.Mock()
        result = input_event_manager.last_event_equals_or_is_release_for_event(mock_event)
        assert result is False

    def test_last_event_equals_or_is_release_for_event_equal(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test InputEventManager.last_event_equals_or_is_release_for_event with equal events."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        mock_event = test_context.Mock()
        input_event_manager._last_non_modifier_key_event = mock_event
        input_event_manager.last_event_was_keyboard = test_context.Mock(return_value=True)
        result = input_event_manager.last_event_equals_or_is_release_for_event(mock_event)
        assert result is True

    def test_last_event_equals_or_is_release_for_event_is_release(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test InputEventManager.last_event_equals_or_is_release_for_event with release event."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        mock_event = test_context.Mock()
        mock_last_event = test_context.Mock()
        input_event_manager._last_non_modifier_key_event = mock_last_event
        input_event_manager.last_event_was_keyboard = test_context.Mock(return_value=True)

        input_event_manager.is_release_for = test_context.Mock(return_value=True)
        result = input_event_manager.last_event_equals_or_is_release_for_event(mock_event)
        assert result is True
        input_event_manager.is_release_for.assert_called_once_with(mock_last_event, mock_event)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_last_non_modifier",
                "has_last_non_modifier": False,
                "last_event_keyboard": True,
                "expected_key": "",
                "expected_modifiers": 0,
            },
            {
                "id": "last_not_keyboard",
                "has_last_non_modifier": True,
                "last_event_keyboard": False,
                "expected_key": "",
                "expected_modifiers": 0,
            },
            {
                "id": "has_both",
                "has_last_non_modifier": True,
                "last_event_keyboard": True,
                "expected_key": "a",
                "expected_modifiers": 4,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_key_and_modifiers(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager._last_key_and_modifiers."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        if case["has_last_non_modifier"]:
            mock_last_non_modifier = test_context.Mock()
            mock_last_non_modifier.keyval_name = "a"
            input_event_manager._last_non_modifier_key_event = mock_last_non_modifier
        else:
            input_event_manager._last_non_modifier_key_event = None
        if case["last_event_keyboard"]:
            mock_last_event = test_context.Mock()
            mock_last_event.modifiers = 4
            input_event_manager._last_input_event = mock_last_event
        input_event_manager.last_event_was_keyboard = test_context.Mock(
            return_value=case["last_event_keyboard"]
        )
        result = input_event_manager._last_key_and_modifiers()
        assert result == (case["expected_key"], case["expected_modifiers"])


    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "command_true",
                "method_name": "last_event_was_command",
                "key_modifiers": ("a", 1 << 2),
                "expected_result": True,
                "expects_debug": True,
            },
            {
                "id": "command_false",
                "method_name": "last_event_was_command",
                "key_modifiers": ("a", 0),
                "expected_result": False,
                "expects_debug": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_command(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test InputEventManager command detection methods."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=case["key_modifiers"]
        )
        method = getattr(input_event_manager, case["method_name"])
        result = method()
        assert result is case["expected_result"]

        if case["expects_debug"]:
            essential_modules["orca.debug"].print_message.assert_called()
        else:
            essential_modules["orca.debug"].print_message.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "empty_key_string",
                "key_string": "",
                "action_key_bindings": [],
                "expected_result": False,
            },
            {
                "id": "matching_key_uppercase",
                "key_string": "f",
                "action_key_bindings": ["Alt+F"],
                "expected_result": True,
            },
            {
                "id": "non_matching_key",
                "key_string": "f",
                "action_key_bindings": ["Alt+G"],
                "expected_result": False,
            },
            {
                "id": "multiple_bindings_match",
                "key_string": "f",
                "action_key_bindings": ["Alt+F", "Ctrl+F"],
                "expected_result": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_shortcut_for(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_shortcut_for."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_obj = test_context.Mock()
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], 0)
        )
        essential_modules["ax_object_class"].get_action_key_binding.return_value = ";".join(
            case["action_key_bindings"]
        )
        result = input_event_manager.last_event_was_shortcut_for(mock_obj)
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "printable_key_true",
                "is_keyboard": True,
                "is_printable": True,
                "expected_result": True,
                "expects_debug": True,
            },
            {
                "id": "not_keyboard",
                "is_keyboard": False,
                "is_printable": None,
                "expected_result": False,
                "expects_debug": False,
            },
            {
                "id": "not_printable",
                "is_keyboard": True,
                "is_printable": False,
                "expected_result": False,
                "expects_debug": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_printable_key(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_printable_key with various scenarios."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager.last_event_was_keyboard = test_context.Mock(
            return_value=case["is_keyboard"]
        )

        if case["is_keyboard"] and case["is_printable"] is not None:
            mock_last_event = test_context.Mock()
            mock_last_event.is_printable_key.return_value = case["is_printable"]
            input_event_manager._last_input_event = mock_last_event

        result = input_event_manager.last_event_was_printable_key()
        assert result is case["expected_result"]

        if case["expects_debug"]:
            essential_modules["orca.debug"].print_message.assert_called()
        else:
            essential_modules["orca.debug"].print_message.assert_not_called()

    def test_last_event_was_caret_navigation(self, test_context: OrcaTestContext) -> None:
        """Test InputEventManager.last_event_was_caret_navigation."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager.last_event_was_character_navigation = test_context.Mock(
            return_value=False
        )
        input_event_manager.last_event_was_word_navigation = test_context.Mock(return_value=True)
        input_event_manager.last_event_was_line_navigation = test_context.Mock(return_value=False)
        input_event_manager.last_event_was_line_boundary_navigation = test_context.Mock(
            return_value=False
        )
        input_event_manager.last_event_was_file_boundary_navigation = test_context.Mock(
            return_value=False
        )
        input_event_manager.last_event_was_page_navigation = test_context.Mock(return_value=False)
        result = input_event_manager.last_event_was_caret_navigation()
        assert result is True

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "left_with_shift",
                "key_string": "Left",
                "modifiers": 1 << 0,
                "expected_result": True,
            },
            {
                "id": "right_with_shift",
                "key_string": "Right",
                "modifiers": 1 << 0,
                "expected_result": True,
            },
            {
                "id": "up_with_shift",
                "key_string": "Up",
                "modifiers": 1 << 0,
                "expected_result": True,
            },
            {
                "id": "down_with_shift",
                "key_string": "Down",
                "modifiers": 1 << 0,
                "expected_result": True,
            },
            {
                "id": "left_without_shift",
                "key_string": "Left",
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "non_arrow_with_shift",
                "key_string": "a",
                "modifiers": 1 << 0,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_caret_selection(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_caret_selection."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_caret_selection()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "up_without_shift", "key_string": "Up", "modifiers": 0, "expected_result": True},
            {
                "id": "left_without_shift",
                "key_string": "Left",
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "down_without_shift",
                "key_string": "Down",
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "right_without_shift",
                "key_string": "Right",
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "up_with_shift",
                "key_string": "Up",
                "modifiers": 1 << 0,
                "expected_result": False,
            },
            {"id": "non_arrow", "key_string": "a", "modifiers": 0, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_backward_caret_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_backward_caret_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_backward_caret_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "down_without_shift",
                "key_string": "Down",
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "right_without_shift",
                "key_string": "Right",
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "up_without_shift",
                "key_string": "Up",
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "left_without_shift",
                "key_string": "Left",
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "down_with_shift",
                "key_string": "Down",
                "modifiers": 1 << 0,
                "expected_result": False,
            },
            {"id": "non_arrow", "key_string": "a", "modifiers": 0, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_forward_caret_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_forward_caret_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_forward_caret_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "down_with_shift",
                "key_string": "Down",
                "modifiers": 1 << 0,
                "expected_result": True,
            },
            {
                "id": "right_with_shift",
                "key_string": "Right",
                "modifiers": 1 << 0,
                "expected_result": True,
            },
            {
                "id": "up_with_shift",
                "key_string": "Up",
                "modifiers": 1 << 0,
                "expected_result": False,
            },
            {
                "id": "left_with_shift",
                "key_string": "Left",
                "modifiers": 1 << 0,
                "expected_result": False,
            },
            {
                "id": "down_without_shift",
                "key_string": "Down",
                "modifiers": 0,
                "expected_result": False,
            },
            {"id": "non_arrow", "key_string": "a", "modifiers": 1 << 0, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_forward_caret_selection(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_forward_caret_selection."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_forward_caret_selection()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "left_no_modifiers",
                "key_string": "Left",
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "right_no_modifiers",
                "key_string": "Right",
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "left_with_ctrl",
                "key_string": "Left",
                "modifiers": 1 << 2,
                "expected_result": False,
            },
            {
                "id": "right_with_alt",
                "key_string": "Right",
                "modifiers": 1 << 3,
                "expected_result": False,
            },
            {
                "id": "non_horizontal_arrow",
                "key_string": "Up",
                "modifiers": 0,
                "expected_result": False,
            },
            {"id": "non_arrow", "key_string": "a", "modifiers": 0, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_character_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_character_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_character_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "left_with_ctrl",
                "key_string": "Left",
                "modifiers": 1 << 2,
                "expected_result": True,
            },
            {
                "id": "right_with_ctrl",
                "key_string": "Right",
                "modifiers": 1 << 2,
                "expected_result": True,
            },
            {"id": "left_no_ctrl", "key_string": "Left", "modifiers": 0, "expected_result": False},
            {
                "id": "right_no_ctrl",
                "key_string": "Right",
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "non_horizontal_arrow",
                "key_string": "Up",
                "modifiers": 1 << 2,
                "expected_result": False,
            },
            {"id": "non_arrow", "key_string": "a", "modifiers": 1 << 2, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_word_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_word_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_word_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "left_with_ctrl",
                "key_string": "Left",
                "modifiers": 1 << 2,
                "expected_result": True,
            },
            {
                "id": "right_with_ctrl",
                "key_string": "Right",
                "modifiers": 1 << 2,
                "expected_result": False,
            },
            {"id": "left_no_ctrl", "key_string": "Left", "modifiers": 0, "expected_result": False},
            {"id": "non_arrow", "key_string": "a", "modifiers": 1 << 2, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_previous_word_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_previous_word_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_previous_word_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "right_with_ctrl",
                "key_string": "Right",
                "modifiers": 1 << 2,
                "expected_result": True,
            },
            {
                "id": "left_with_ctrl",
                "key_string": "Left",
                "modifiers": 1 << 2,
                "expected_result": False,
            },
            {
                "id": "right_no_ctrl",
                "key_string": "Right",
                "modifiers": 0,
                "expected_result": False,
            },
            {"id": "non_arrow", "key_string": "a", "modifiers": 1 << 2, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_next_word_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_next_word_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_next_word_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "up_multiline_not_controlled",
                "key_string": "Up",
                "modifiers": 0,
                "is_single_line": False,
                "is_widget_controlled": False,
                "expected_result": True,
            },
            {
                "id": "down_multiline_not_controlled",
                "key_string": "Down",
                "modifiers": 0,
                "is_single_line": False,
                "is_widget_controlled": False,
                "expected_result": True,
            },
            {
                "id": "up_with_ctrl",
                "key_string": "Up",
                "modifiers": 1 << 2,
                "is_single_line": False,
                "is_widget_controlled": False,
                "expected_result": False,
            },
            {
                "id": "up_single_line",
                "key_string": "Up",
                "modifiers": 0,
                "is_single_line": True,
                "is_widget_controlled": False,
                "expected_result": False,
            },
            {
                "id": "up_widget_controlled",
                "key_string": "Up",
                "modifiers": 0,
                "is_single_line": False,
                "is_widget_controlled": True,
                "expected_result": False,
            },
            {
                "id": "non_vertical_arrow",
                "key_string": "Left",
                "modifiers": 0,
                "is_single_line": False,
                "is_widget_controlled": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_line_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_line_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        mock_focus = test_context.Mock()
        essential_modules["orca.focus_manager"].get_locus_of_focus.return_value = mock_focus
        essential_modules["ax_utilities_class"].is_single_line.return_value = case["is_single_line"]
        essential_modules[
            "ax_utilities_class"
        ].is_widget_controlled_by_line_navigation.return_value = case["is_widget_controlled"]
        result = input_event_manager.last_event_was_line_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "up_with_ctrl_no_shift",
                "key_string": "Up",
                "modifiers": (1 << 2),
                "expected_result": True,
            },
            {
                "id": "down_with_ctrl_no_shift",
                "key_string": "Down",
                "modifiers": (1 << 2),
                "expected_result": True,
            },
            {
                "id": "up_with_ctrl_and_shift",
                "key_string": "Up",
                "modifiers": (1 << 2) | (1 << 0),
                "expected_result": False,
            },
            {"id": "up_no_ctrl", "key_string": "Up", "modifiers": 0, "expected_result": False},
            {
                "id": "non_vertical_arrow",
                "key_string": "Left",
                "modifiers": 1 << 2,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_paragraph_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_paragraph_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_paragraph_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "home_no_ctrl", "key_string": "Home", "modifiers": 0, "expected_result": True},
            {"id": "end_no_ctrl", "key_string": "End", "modifiers": 0, "expected_result": True},
            {
                "id": "home_with_ctrl",
                "key_string": "Home",
                "modifiers": 1 << 2,
                "expected_result": False,
            },
            {
                "id": "end_with_ctrl",
                "key_string": "End",
                "modifiers": 1 << 2,
                "expected_result": False,
            },
            {
                "id": "non_boundary_key",
                "key_string": "Left",
                "modifiers": 0,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_line_boundary_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_line_boundary_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_line_boundary_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "home_with_ctrl",
                "key_string": "Home",
                "modifiers": 1 << 2,
                "expected_result": True,
            },
            {
                "id": "end_with_ctrl",
                "key_string": "End",
                "modifiers": 1 << 2,
                "expected_result": True,
            },
            {"id": "home_no_ctrl", "key_string": "Home", "modifiers": 0, "expected_result": False},
            {"id": "end_no_ctrl", "key_string": "End", "modifiers": 0, "expected_result": False},
            {
                "id": "non_boundary_key",
                "key_string": "Left",
                "modifiers": 1 << 2,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_file_boundary_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_file_boundary_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_file_boundary_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "page_up_multiline_not_controlled",
                "key_string": "Page_Up",
                "modifiers": 0,
                "is_single_line": False,
                "is_widget_controlled": False,
                "expected_result": True,
            },
            {
                "id": "page_down_multiline_not_controlled",
                "key_string": "Page_Down",
                "modifiers": 0,
                "is_single_line": False,
                "is_widget_controlled": False,
                "expected_result": True,
            },
            {
                "id": "page_up_with_ctrl",
                "key_string": "Page_Up",
                "modifiers": 1 << 2,
                "is_single_line": False,
                "is_widget_controlled": False,
                "expected_result": False,
            },
            {
                "id": "page_up_single_line",
                "key_string": "Page_Up",
                "modifiers": 0,
                "is_single_line": True,
                "is_widget_controlled": False,
                "expected_result": False,
            },
            {
                "id": "page_up_widget_controlled",
                "key_string": "Page_Up",
                "modifiers": 0,
                "is_single_line": False,
                "is_widget_controlled": True,
                "expected_result": False,
            },
            {
                "id": "non_page_key",
                "key_string": "Left",
                "modifiers": 0,
                "is_single_line": False,
                "is_widget_controlled": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_page_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_page_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        mock_focus = test_context.Mock()
        essential_modules["orca.focus_manager"].get_locus_of_focus.return_value = mock_focus
        essential_modules["ax_utilities_class"].is_single_line.return_value = case["is_single_line"]
        essential_modules[
            "ax_utilities_class"
        ].is_widget_controlled_by_line_navigation.return_value = case["is_widget_controlled"]
        result = input_event_manager.last_event_was_page_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "numeric_with_alt",
                "key_string": "1",
                "modifiers": 1 << 3,
                "expected_result": True,
            },
            {
                "id": "numeric_2_with_alt",
                "key_string": "2",
                "modifiers": 1 << 3,
                "expected_result": True,
            },
            {
                "id": "page_up_with_ctrl",
                "key_string": "Page_Up",
                "modifiers": 1 << 2,
                "expected_result": True,
            },
            {
                "id": "page_down_with_ctrl",
                "key_string": "Page_Down",
                "modifiers": 1 << 2,
                "expected_result": True,
            },
            {"id": "numeric_no_alt", "key_string": "1", "modifiers": 0, "expected_result": False},
            {
                "id": "page_up_no_ctrl",
                "key_string": "Page_Up",
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "non_numeric_non_page",
                "key_string": "a",
                "modifiers": 1 << 3,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_page_switch(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_page_switch."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_page_switch()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "tab_no_modifiers",
                "key_string": "Tab",
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "shift_tab_no_modifiers",
                "key_string": "ISO_Left_Tab",
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "tab_with_ctrl",
                "key_string": "Tab",
                "modifiers": 1 << 2,
                "expected_result": False,
            },
            {
                "id": "tab_with_alt",
                "key_string": "Tab",
                "modifiers": 1 << 3,
                "expected_result": False,
            },
            {"id": "non_tab_key", "key_string": "a", "modifiers": 0, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_tab_navigation(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_tab_navigation."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_tab_navigation()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "not_table_header",
                "is_table_header": False,
                "is_mouse_button": True,
                "is_primary_click": True,
                "is_keyboard": False,
                "is_return_or_space": False,
                "expected_result": False,
            },
            {
                "id": "table_header_mouse_primary_click",
                "is_table_header": True,
                "is_mouse_button": True,
                "is_primary_click": True,
                "is_keyboard": False,
                "is_return_or_space": False,
                "expected_result": True,
            },
            {
                "id": "table_header_mouse_not_primary",
                "is_table_header": True,
                "is_mouse_button": True,
                "is_primary_click": False,
                "is_keyboard": False,
                "is_return_or_space": False,
                "expected_result": False,
            },
            {
                "id": "table_header_keyboard_return_space",
                "is_table_header": True,
                "is_mouse_button": False,
                "is_primary_click": False,
                "is_keyboard": True,
                "is_return_or_space": True,
                "expected_result": True,
            },
            {
                "id": "table_header_keyboard_not_return_space",
                "is_table_header": True,
                "is_mouse_button": False,
                "is_primary_click": False,
                "is_keyboard": True,
                "is_return_or_space": False,
                "expected_result": False,
            },
            {
                "id": "table_header_neither_mouse_nor_keyboard",
                "is_table_header": True,
                "is_mouse_button": False,
                "is_primary_click": False,
                "is_keyboard": False,
                "is_return_or_space": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_table_sort(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_table_sort."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_focus = test_context.Mock()
        essential_modules["orca.focus_manager"].get_locus_of_focus.return_value = mock_focus
        essential_modules["ax_utilities_class"].is_table_header.return_value = case[
            "is_table_header"
        ]
        input_event_manager.last_event_was_mouse_button = test_context.Mock(
            return_value=case["is_mouse_button"]
        )
        input_event_manager.last_event_was_primary_click = test_context.Mock(
            return_value=case["is_primary_click"]
        )
        input_event_manager.last_event_was_keyboard = test_context.Mock(
            return_value=case["is_keyboard"]
        )
        input_event_manager.last_event_was_return_or_space = test_context.Mock(
            return_value=case["is_return_or_space"]
        )
        result = input_event_manager.last_event_was_table_sort()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "left_no_modifiers",
                "key_string": "Left",
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "right_no_modifiers",
                "key_string": "Right",
                "modifiers": 0,
                "expected_result": True,
            },
            {"id": "up_no_modifiers", "key_string": "Up", "modifiers": 0, "expected_result": True},
            {
                "id": "down_no_modifiers",
                "key_string": "Down",
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "left_with_ctrl",
                "key_string": "Left",
                "modifiers": 1 << 2,
                "expected_result": False,
            },
            {
                "id": "left_with_shift",
                "key_string": "Left",
                "modifiers": 1 << 0,
                "expected_result": False,
            },
            {
                "id": "left_with_alt",
                "key_string": "Left",
                "modifiers": 1 << 3,
                "expected_result": False,
            },
            {
                "id": "left_with_orca_modifier",
                "key_string": "Left",
                "modifiers": 1 << 8,
                "expected_result": False,
            },
            {"id": "non_arrow_key", "key_string": "a", "modifiers": 0, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_unmodified_arrow(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_unmodified_arrow."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], case["modifiers"])
        )
        result = input_event_manager.last_event_was_unmodified_arrow()
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "has_alt_modifier",
                "modifiers": 1 << 3,
                "expected_result": 8,
            },  # Returns bitwise result, not boolean
            {"id": "no_alt_modifier", "modifiers": 0, "expected_result": 0},
            {
                "id": "alt_and_ctrl_modifiers",
                "modifiers": (1 << 3) | (1 << 2),
                "expected_result": 8,
            },  # Alt bit is still 8
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_alt_modified(self, test_context, case: dict) -> None:
        """Test InputEventManager.last_event_was_alt_modified."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=("a", case["modifiers"])
        )
        result = input_event_manager.last_event_was_alt_modified()
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "backspace_key", "key_string": "BackSpace", "expected_result": True},
            {"id": "delete_key", "key_string": "Delete", "expected_result": False},
            {"id": "regular_key", "key_string": "a", "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_backspace(self, test_context, case: dict) -> None:
        """Test InputEventManager.last_event_was_backspace."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], 0)
        )
        result = input_event_manager.last_event_was_backspace()
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "down_key", "key_string": "Down", "expected_result": True},
            {"id": "up_key", "key_string": "Up", "expected_result": False},
            {"id": "regular_key", "key_string": "a", "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_down(self, test_context, case: dict) -> None:
        """Test InputEventManager.last_event_was_down."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], 0)
        )
        result = input_event_manager.last_event_was_down()
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "f1_key", "key_string": "F1", "expected_result": True},
            {"id": "f2_key", "key_string": "F2", "expected_result": False},
            {"id": "regular_key", "key_string": "a", "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_f1(self, test_context, case: dict) -> None:
        """Test InputEventManager.last_event_was_f1."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], 0)
        )
        result = input_event_manager.last_event_was_f1()
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "left_key", "key_string": "Left", "expected_result": True},
            {"id": "right_key", "key_string": "Right", "expected_result": False},
            {"id": "regular_key", "key_string": "a", "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_left(self, test_context, case: dict) -> None:
        """Test InputEventManager.last_event_was_left."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], 0)
        )
        result = input_event_manager.last_event_was_left()
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "left_or_right_left_key",
                "method_name": "last_event_was_left_or_right",
                "key_string": "Left",
                "expected_result": True,
            },
            {
                "id": "left_or_right_right_key",
                "method_name": "last_event_was_left_or_right",
                "key_string": "Right",
                "expected_result": True,
            },
            {
                "id": "left_or_right_up_key",
                "method_name": "last_event_was_left_or_right",
                "key_string": "Up",
                "expected_result": False,
            },
            {
                "id": "page_up_or_down_page_up",
                "method_name": "last_event_was_page_up_or_page_down",
                "key_string": "Page_Up",
                "expected_result": True,
            },
            {
                "id": "page_up_or_down_page_down",
                "method_name": "last_event_was_page_up_or_page_down",
                "key_string": "Page_Down",
                "expected_result": True,
            },
            {
                "id": "page_up_or_down_up_key",
                "method_name": "last_event_was_page_up_or_page_down",
                "key_string": "Up",
                "expected_result": False,
            },
            {
                "id": "right_right_key",
                "method_name": "last_event_was_right",
                "key_string": "Right",
                "expected_result": True,
            },
            {
                "id": "right_left_key",
                "method_name": "last_event_was_right",
                "key_string": "Left",
                "expected_result": False,
            },
            {
                "id": "return_return_key",
                "method_name": "last_event_was_return",
                "key_string": "Return",
                "expected_result": True,
            },
            {
                "id": "return_enter_key",
                "method_name": "last_event_was_return",
                "key_string": "Enter",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_single_key_detection(self, test_context, case: dict) -> None:
        """Test InputEventManager single key detection methods."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], 0)
        )
        method = getattr(input_event_manager, case["method_name"])
        result = method()
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "return_or_space_return",
                "method_name": "last_event_was_return_or_space",
                "key_string": "Return",
                "expected_result": True,
            },
            {
                "id": "return_or_space_space_key",
                "method_name": "last_event_was_return_or_space",
                "key_string": "space",
                "expected_result": True,
            },
            {
                "id": "return_or_space_space_char",
                "method_name": "last_event_was_return_or_space",
                "key_string": " ",
                "expected_result": True,
            },
            {
                "id": "return_or_space_enter",
                "method_name": "last_event_was_return_or_space",
                "key_string": "Enter",
                "expected_result": False,
            },
            {
                "id": "return_tab_space_return",
                "method_name": "last_event_was_return_tab_or_space",
                "key_string": "Return",
                "expected_result": True,
            },
            {
                "id": "return_tab_space_tab",
                "method_name": "last_event_was_return_tab_or_space",
                "key_string": "Tab",
                "expected_result": True,
            },
            {
                "id": "return_tab_space_space_key",
                "method_name": "last_event_was_return_tab_or_space",
                "key_string": "space",
                "expected_result": True,
            },
            {
                "id": "return_tab_space_space_char",
                "method_name": "last_event_was_return_tab_or_space",
                "key_string": " ",
                "expected_result": True,
            },
            {
                "id": "return_tab_space_enter",
                "method_name": "last_event_was_return_tab_or_space",
                "key_string": "Enter",
                "expected_result": False,
            },
            {
                "id": "space_space_character",
                "method_name": "last_event_was_space",
                "key_string": " ",
                "expected_result": True,
            },
            {
                "id": "space_space_key",
                "method_name": "last_event_was_space",
                "key_string": "space",
                "expected_result": True,
            },
            {
                "id": "space_return_key",
                "method_name": "last_event_was_space",
                "key_string": "Return",
                "expected_result": False,
            },
            {
                "id": "tab_tab_key",
                "method_name": "last_event_was_tab",
                "key_string": "Tab",
                "expected_result": True,
            },
            {
                "id": "tab_shift_tab_key",
                "method_name": "last_event_was_tab",
                "key_string": "ISO_Left_Tab",
                "expected_result": False,
            },
            {
                "id": "up_up_key",
                "method_name": "last_event_was_up",
                "key_string": "Up",
                "expected_result": True,
            },
            {
                "id": "up_down_key",
                "method_name": "last_event_was_up",
                "key_string": "Down",
                "expected_result": False,
            },
            {
                "id": "up_or_down_up_key",
                "method_name": "last_event_was_up_or_down",
                "key_string": "Up",
                "expected_result": True,
            },
            {
                "id": "up_or_down_down_key",
                "method_name": "last_event_was_up_or_down",
                "key_string": "Down",
                "expected_result": True,
            },
            {
                "id": "up_or_down_left_key",
                "method_name": "last_event_was_up_or_down",
                "key_string": "Left",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_composite_key_detection(self, test_context, case: dict) -> None:
        """Test InputEventManager composite key detection methods."""

        input_event_manager, _essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["key_string"], 0)
        )
        method = getattr(input_event_manager, case["method_name"])
        result = method()
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "delete_delete_key",
                "method_name": "last_event_was_delete",
                "keynames": ["Delete"],
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "delete_keypad_delete",
                "method_name": "last_event_was_delete",
                "keynames": ["KP_Delete"],
                "modifiers": 0,
                "expected_result": True,
            },
            {
                "id": "delete_ctrl_d",
                "method_name": "last_event_was_delete",
                "keynames": ["d"],
                "modifiers": 1 << 2,
                "expected_result": True,
            },
            {
                "id": "delete_d_without_ctrl",
                "method_name": "last_event_was_delete",
                "keynames": ["d"],
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "delete_unknown_key",
                "method_name": "last_event_was_delete",
                "keynames": ["x"],
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "cut_ctrl_x",
                "method_name": "last_event_was_cut",
                "keynames": ["x"],
                "modifiers": (1 << 2),
                "expected_result": True,
            },
            {
                "id": "cut_ctrl_shift_x",
                "method_name": "last_event_was_cut",
                "keynames": ["x"],
                "modifiers": (1 << 2) | (1 << 0),
                "expected_result": False,
            },
            {
                "id": "cut_x_without_ctrl",
                "method_name": "last_event_was_cut",
                "keynames": ["x"],
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "cut_ctrl_y",
                "method_name": "last_event_was_cut",
                "keynames": ["y"],
                "modifiers": 1 << 2,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_simple_editing_actions(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager simple editing action methods."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["keynames"][0] if case["keynames"] else "", case["modifiers"])
        )
        method = getattr(input_event_manager, case["method_name"])
        result = method()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "copy_ctrl_c_non_terminal",
                "method_name": "last_event_was_copy",
                "keynames": ["c"],
                "modifiers": (1 << 2),
                "is_terminal": False,
                "expected_result": True,
            },
            {
                "id": "copy_ctrl_shift_c_terminal",
                "method_name": "last_event_was_copy",
                "keynames": ["c"],
                "modifiers": (1 << 2) | (1 << 0),
                "is_terminal": True,
                "expected_result": True,
            },
            {
                "id": "copy_ctrl_shift_c_non_terminal",
                "method_name": "last_event_was_copy",
                "keynames": ["c"],
                "modifiers": (1 << 2) | (1 << 0),
                "is_terminal": False,
                "expected_result": False,
            },
            {
                "id": "copy_ctrl_c_terminal",
                "method_name": "last_event_was_copy",
                "keynames": ["c"],
                "modifiers": (1 << 2),
                "is_terminal": True,
                "expected_result": False,
            },
            {
                "id": "copy_c_without_ctrl",
                "method_name": "last_event_was_copy",
                "keynames": ["c"],
                "modifiers": 0,
                "is_terminal": False,
                "expected_result": False,
            },
            {
                "id": "paste_ctrl_v_non_terminal",
                "method_name": "last_event_was_paste",
                "keynames": ["v"],
                "modifiers": (1 << 2),
                "is_terminal": False,
                "expected_result": True,
            },
            {
                "id": "paste_ctrl_shift_v_terminal",
                "method_name": "last_event_was_paste",
                "keynames": ["v"],
                "modifiers": (1 << 2) | (1 << 0),
                "is_terminal": True,
                "expected_result": True,
            },
            {
                "id": "paste_ctrl_shift_v_non_terminal",
                "method_name": "last_event_was_paste",
                "keynames": ["v"],
                "modifiers": (1 << 2) | (1 << 0),
                "is_terminal": False,
                "expected_result": False,
            },
            {
                "id": "paste_ctrl_v_terminal",
                "method_name": "last_event_was_paste",
                "keynames": ["v"],
                "modifiers": (1 << 2),
                "is_terminal": True,
                "expected_result": False,
            },
            {
                "id": "paste_v_without_ctrl",
                "method_name": "last_event_was_paste",
                "keynames": ["v"],
                "modifiers": 0,
                "is_terminal": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_terminal_aware_editing_actions(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager terminal-aware editing action methods."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_object = test_context.Mock()
        mock_last_event = test_context.Mock()
        mock_last_event.get_object.return_value = mock_object
        input_event_manager._last_input_event = mock_last_event
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["keynames"][0] if case["keynames"] else "", case["modifiers"])
        )
        essential_modules["ax_utilities_class"].is_terminal.return_value = case["is_terminal"]
        method = getattr(input_event_manager, case["method_name"])
        result = method()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "undo_ctrl_z",
                "method_name": "last_event_was_undo",
                "keynames": ["z"],
                "modifiers": (1 << 2),
                "expected_result": True,
            },
            {
                "id": "undo_ctrl_shift_z",
                "method_name": "last_event_was_undo",
                "keynames": ["z"],
                "modifiers": (1 << 2) | (1 << 0),
                "expected_result": False,
            },
            {
                "id": "undo_z_without_ctrl",
                "method_name": "last_event_was_undo",
                "keynames": ["z"],
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "undo_ctrl_y",
                "method_name": "last_event_was_undo",
                "keynames": ["y"],
                "modifiers": 1 << 2,
                "expected_result": False,
            },
            {
                "id": "redo_ctrl_shift_z",
                "method_name": "last_event_was_redo",
                "keynames": ["z"],
                "modifiers": (1 << 2) | (1 << 0),
                "expected_result": True,
            },
            {
                "id": "redo_ctrl_y_libreoffice",
                "method_name": "last_event_was_redo",
                "keynames": ["y"],
                "modifiers": (1 << 2),
                "expected_result": True,
            },
            {
                "id": "redo_ctrl_z",
                "method_name": "last_event_was_redo",
                "keynames": ["z"],
                "modifiers": (1 << 2),
                "expected_result": False,
            },
            {
                "id": "redo_ctrl_shift_y",
                "method_name": "last_event_was_redo",
                "keynames": ["y"],
                "modifiers": (1 << 2) | (1 << 0),
                "expected_result": False,
            },
            {
                "id": "redo_z_without_ctrl",
                "method_name": "last_event_was_redo",
                "keynames": ["z"],
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "redo_unknown_key",
                "method_name": "last_event_was_redo",
                "keynames": ["x"],
                "modifiers": 1 << 2,
                "expected_result": False,
            },
            {
                "id": "select_all_ctrl_a",
                "method_name": "last_event_was_select_all",
                "keynames": ["a"],
                "modifiers": (1 << 2),
                "expected_result": True,
            },
            {
                "id": "select_all_ctrl_shift_a",
                "method_name": "last_event_was_select_all",
                "keynames": ["a"],
                "modifiers": (1 << 2) | (1 << 0),
                "expected_result": False,
            },
            {
                "id": "select_all_a_without_ctrl",
                "method_name": "last_event_was_select_all",
                "keynames": ["a"],
                "modifiers": 0,
                "expected_result": False,
            },
            {
                "id": "select_all_unknown_key",
                "method_name": "last_event_was_select_all",
                "keynames": ["x"],
                "modifiers": 1 << 2,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_undo_redo_select_editing_actions(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager undo/redo/select editing action methods."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        input_event_manager._last_key_and_modifiers = test_context.Mock(
            return_value=(case["keynames"][0] if case["keynames"] else "", case["modifiers"])
        )
        method = getattr(input_event_manager, case["method_name"])
        result = method()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "primary_click_primary_click",
                "method_name": "last_event_was_primary_click",
                "is_mouse_button": True,
                "button": "1",
                "pressed": True,
                "expected_result": True,
            },
            {
                "id": "primary_click_primary_release",
                "method_name": "last_event_was_primary_click",
                "is_mouse_button": True,
                "button": "1",
                "pressed": False,
                "expected_result": False,
            },
            {
                "id": "primary_click_middle_click",
                "method_name": "last_event_was_primary_click",
                "is_mouse_button": True,
                "button": "2",
                "pressed": True,
                "expected_result": False,
            },
            {
                "id": "primary_click_not_mouse_button",
                "method_name": "last_event_was_primary_click",
                "is_mouse_button": False,
                "button": "1",
                "pressed": True,
                "expected_result": False,
            },
            {
                "id": "primary_release_primary_release",
                "method_name": "last_event_was_primary_release",
                "is_mouse_button": True,
                "button": "1",
                "pressed": False,
                "expected_result": True,
            },
            {
                "id": "primary_release_primary_click",
                "method_name": "last_event_was_primary_release",
                "is_mouse_button": True,
                "button": "1",
                "pressed": True,
                "expected_result": False,
            },
            {
                "id": "primary_release_middle_release",
                "method_name": "last_event_was_primary_release",
                "is_mouse_button": True,
                "button": "2",
                "pressed": False,
                "expected_result": False,
            },
            {
                "id": "primary_release_not_mouse_button",
                "method_name": "last_event_was_primary_release",
                "is_mouse_button": False,
                "button": "1",
                "pressed": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_primary_mouse_button_actions(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager primary mouse button action methods."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_last_event = test_context.Mock()
        mock_last_event.button = case["button"]
        mock_last_event.pressed = case["pressed"]
        input_event_manager._last_input_event = mock_last_event
        input_event_manager.last_event_was_mouse_button = test_context.Mock(
            return_value=case["is_mouse_button"]
        )
        method = getattr(input_event_manager, case["method_name"])
        result = method()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "primary_button",
                "is_mouse_button": True,
                "button": "1",
                "expected_result": True,
            },
            {
                "id": "middle_button",
                "is_mouse_button": True,
                "button": "2",
                "expected_result": False,
            },
            {
                "id": "secondary_button",
                "is_mouse_button": True,
                "button": "3",
                "expected_result": False,
            },
            {
                "id": "not_mouse_button",
                "is_mouse_button": False,
                "button": "1",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_last_event_was_primary_click_or_release(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager.last_event_was_primary_click_or_release."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_last_event = test_context.Mock()
        mock_last_event.button = case["button"]
        input_event_manager._last_input_event = mock_last_event
        input_event_manager.last_event_was_mouse_button = test_context.Mock(
            return_value=case["is_mouse_button"]
        )
        result = input_event_manager.last_event_was_primary_click_or_release()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "middle_click_middle_click",
                "method_name": "last_event_was_middle_click",
                "is_mouse_button": True,
                "button": "2",
                "pressed": True,
                "expected_result": True,
            },
            {
                "id": "middle_click_middle_release",
                "method_name": "last_event_was_middle_click",
                "is_mouse_button": True,
                "button": "2",
                "pressed": False,
                "expected_result": False,
            },
            {
                "id": "middle_click_primary_click",
                "method_name": "last_event_was_middle_click",
                "is_mouse_button": True,
                "button": "1",
                "pressed": True,
                "expected_result": False,
            },
            {
                "id": "middle_click_not_mouse_button",
                "method_name": "last_event_was_middle_click",
                "is_mouse_button": False,
                "button": "2",
                "pressed": True,
                "expected_result": False,
            },
            {
                "id": "middle_release_middle_release",
                "method_name": "last_event_was_middle_release",
                "is_mouse_button": True,
                "button": "2",
                "pressed": False,
                "expected_result": True,
            },
            {
                "id": "middle_release_middle_click",
                "method_name": "last_event_was_middle_release",
                "is_mouse_button": True,
                "button": "2",
                "pressed": True,
                "expected_result": False,
            },
            {
                "id": "middle_release_primary_release",
                "method_name": "last_event_was_middle_release",
                "is_mouse_button": True,
                "button": "1",
                "pressed": False,
                "expected_result": False,
            },
            {
                "id": "middle_release_not_mouse_button",
                "method_name": "last_event_was_middle_release",
                "is_mouse_button": False,
                "button": "2",
                "pressed": False,
                "expected_result": False,
            },
            {
                "id": "secondary_click_secondary_click",
                "method_name": "last_event_was_secondary_click",
                "is_mouse_button": True,
                "button": "3",
                "pressed": True,
                "expected_result": True,
            },
            {
                "id": "secondary_click_secondary_release",
                "method_name": "last_event_was_secondary_click",
                "is_mouse_button": True,
                "button": "3",
                "pressed": False,
                "expected_result": False,
            },
            {
                "id": "secondary_click_primary_click",
                "method_name": "last_event_was_secondary_click",
                "is_mouse_button": True,
                "button": "1",
                "pressed": True,
                "expected_result": False,
            },
            {
                "id": "secondary_click_not_mouse_button",
                "method_name": "last_event_was_secondary_click",
                "is_mouse_button": False,
                "button": "3",
                "pressed": True,
                "expected_result": False,
            },
            {
                "id": "secondary_release_secondary_release",
                "method_name": "last_event_was_secondary_release",
                "is_mouse_button": True,
                "button": "3",
                "pressed": False,
                "expected_result": True,
            },
            {
                "id": "secondary_release_secondary_click",
                "method_name": "last_event_was_secondary_release",
                "is_mouse_button": True,
                "button": "3",
                "pressed": True,
                "expected_result": False,
            },
            {
                "id": "secondary_release_primary_release",
                "method_name": "last_event_was_secondary_release",
                "is_mouse_button": True,
                "button": "1",
                "pressed": False,
                "expected_result": False,
            },
            {
                "id": "secondary_release_not_mouse_button",
                "method_name": "last_event_was_secondary_release",
                "is_mouse_button": False,
                "button": "3",
                "pressed": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_middle_secondary_mouse_button_actions(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test InputEventManager middle and secondary mouse button action methods."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_last_event = test_context.Mock()
        mock_last_event.button = case["button"]
        mock_last_event.pressed = case["pressed"]
        input_event_manager._last_input_event = mock_last_event
        input_event_manager.last_event_was_mouse_button = test_context.Mock(
            return_value=case["is_mouse_button"]
        )
        method = getattr(input_event_manager, case["method_name"])
        result = method()
        assert result == case["expected_result"]
        if case["expected_result"]:
            essential_modules["orca.debug"].print_message.assert_called()

    def test_get_manager(self, test_context: OrcaTestContext) -> None:
        """Test get_manager function returns singleton."""

        self._setup_input_event_manager(test_context)
        from orca.input_event_manager import get_manager

        manager1 = get_manager()
        manager2 = get_manager()
        assert manager1 is manager2

    def test_pause_key_watcher_with_debug_message(self, test_context: OrcaTestContext) -> None:
        """Test InputEventManager.pause_key_watcher logs debug message."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)

        input_event_manager.pause_key_watcher(True, "Testing pause functionality")

        essential_modules["orca.debug"].print_message.assert_called()
        assert input_event_manager._paused is True

        input_event_manager.pause_key_watcher(False, "Testing unpause functionality")

        assert input_event_manager._paused is False

    def test_check_grabbed_bindings_debug_output(self, test_context: OrcaTestContext) -> None:
        """Test InputEventManager.check_grabbed_bindings logs debug information."""

        input_event_manager, essential_modules = self._setup_input_event_manager(test_context)
        mock_binding1 = test_context.Mock()
        mock_binding2 = test_context.Mock()
        input_event_manager._grabbed_bindings = {"grab1": mock_binding1, "grab2": mock_binding2}
        input_event_manager.check_grabbed_bindings()
        assert essential_modules["orca.debug"].print_message.call_count >= 3  # Summary + 2 bindings
