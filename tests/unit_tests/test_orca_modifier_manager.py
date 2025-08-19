# Unit tests for orca_modifier_manager.py methods.
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
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals

"""Unit tests for orca_modifier_manager.py methods."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING
from unittest.mock import call

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestOrcaModifierManager:
    """Test OrcaModifierManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for orca_modifier_manager module testing."""

        additional_modules = ["orca.input_event_manager", "gi.repository"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.get_keycodes = test_context.Mock(return_value=(0, 0))

        input_event_manager_mock = essential_modules["orca.input_event_manager"]
        input_manager_instance = test_context.Mock()
        input_manager_instance.add_grab_for_modifier = test_context.Mock(return_value=123)
        input_manager_instance.remove_grab_for_modifier = test_context.Mock()
        input_event_manager_mock.get_manager = test_context.Mock(
            return_value=input_manager_instance
        )

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_instance.get_setting = test_context.Mock(
            return_value=["Insert", "KP_Insert"]
        )
        settings_manager_mock.get_manager = test_context.Mock(
            return_value=settings_manager_instance
        )

        gi_repository_mock = essential_modules["gi.repository"]

        gdk_mock = test_context.Mock()
        display_mock = test_context.Mock()
        device_manager_mock = test_context.Mock()
        display_mock.get_device_manager = test_context.Mock(return_value=device_manager_mock)
        gdk_mock.Display = test_context.Mock()
        gdk_mock.Display.get_default = test_context.Mock(return_value=display_mock)
        gdk_mock.InputSource = test_context.Mock()
        gdk_mock.InputSource.KEYBOARD = 4
        gi_repository_mock.Gdk = gdk_mock

        atspi_mock = test_context.Mock()
        atspi_mock.generate_keyboard_event = test_context.Mock()
        atspi_mock.ModifierType = test_context.Mock()
        atspi_mock.ModifierType.SHIFTLOCK = 1
        atspi_mock.ModifierType.SHIFT = 0
        gi_repository_mock.Atspi = atspi_mock

        glib_mock = test_context.Mock()
        glib_mock.timeout_add = test_context.Mock()
        gi_repository_mock.GLib = glib_mock

        essential_modules["input_manager_instance"] = input_manager_instance
        essential_modules["settings_manager_instance"] = settings_manager_instance
        essential_modules["gdk"] = gdk_mock
        essential_modules["atspi"] = atspi_mock
        essential_modules["glib"] = glib_mock

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModifierManager.__init__."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        mock_gdk = test_context.Mock()
        test_context.patch("orca.orca_modifier_manager.Gdk", new=mock_gdk)
        mock_display = test_context.Mock()
        mock_device_manager = test_context.Mock()
        mock_display.get_device_manager.return_value = mock_device_manager
        mock_gdk.Display.get_default.return_value = mock_display
        manager = orca_modifier_manager.OrcaModifierManager()
        assert not manager._grabbed_modifiers
        assert manager._is_pressed is False
        assert manager._original_xmodmap == b""
        assert manager._caps_lock_cleared is False
        assert manager._need_to_restore_orca_modifier is False

        assert manager is not None

    def test_init_no_display(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModifierManager.__init__ with no display available."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        mock_gdk = test_context.Mock()
        test_context.patch("orca.orca_modifier_manager.Gdk", new=mock_gdk)
        mock_gdk.Display.get_default.return_value = None
        essential_modules["orca.debug"].reset_mock()
        manager = orca_modifier_manager.OrcaModifierManager()

        assert not manager._grabbed_modifiers
        assert manager._is_pressed is False
        assert manager._original_xmodmap == b""
        assert manager._caps_lock_cleared is False
        assert manager._need_to_restore_orca_modifier is False

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "keyboard_device",
                "device_source": 4,
                "should_refresh": True,
            },  # Gdk.InputSource.KEYBOARD = 4
            {
                "id": "mouse_device",
                "device_source": 0,
                "should_refresh": False,
            },  # Gdk.InputSource.MOUSE = 0
            {
                "id": "touchscreen_device",
                "device_source": 5,
                "should_refresh": False,
            },  # Gdk.InputSource.TOUCHSCREEN = 5
        ],
        ids=lambda case: case["id"],
    )
    def test_on_device_changed(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test OrcaModifierManager._on_device_changed."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()

        mock_device = test_context.Mock()
        mock_device.get_source.return_value = case["device_source"]

        mock_refresh = test_context.Mock()
        test_context.patch_object(manager, "refresh_orca_modifiers", new=mock_refresh)
        test_context.patch("orca.orca_modifier_manager.Gdk.InputSource.KEYBOARD", new=4)
        manager._on_device_changed(None, mock_device)
        if case["should_refresh"]:
            mock_refresh.assert_called_once_with("Keyboard change detected.")
        else:
            mock_refresh.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "insert_grabbed",
                "modifier": "Insert",
                "orca_modifier_keys": ["Insert", "KP_Insert"],
                "is_grabbed": True,
                "expected_result": True,
            },
            {
                "id": "insert_not_grabbed",
                "modifier": "Insert",
                "orca_modifier_keys": ["Insert", "KP_Insert"],
                "is_grabbed": False,
                "expected_result": False,
            },
            {
                "id": "kp_insert_grabbed",
                "modifier": "KP_Insert",
                "orca_modifier_keys": ["Insert", "KP_Insert"],
                "is_grabbed": True,
                "expected_result": True,
            },
            {
                "id": "kp_insert_not_grabbed",
                "modifier": "KP_Insert",
                "orca_modifier_keys": ["Insert", "KP_Insert"],
                "is_grabbed": False,
                "expected_result": False,
            },
            {
                "id": "caps_lock_always_true",
                "modifier": "Caps_Lock",
                "orca_modifier_keys": ["Caps_Lock"],
                "is_grabbed": False,
                "expected_result": True,
            },
            {
                "id": "shift_lock_always_true",
                "modifier": "Shift_Lock",
                "orca_modifier_keys": ["Shift_Lock"],
                "is_grabbed": False,
                "expected_result": True,
            },
            {
                "id": "not_orca_modifier",
                "modifier": "Control_L",
                "orca_modifier_keys": ["Insert"],
                "is_grabbed": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_orca_modifier(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test OrcaModifierManager.is_orca_modifier."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()
        manager._grabbed_modifiers = {"Insert": 1, "KP_Insert": 2} if case["is_grabbed"] else {}

        mock_sm = test_context.Mock()
        test_context.patch(
            "orca.orca_modifier_manager.settings_manager.get_manager", new=mock_sm
        )
        mock_sm.return_value.get_setting.return_value = case["orca_modifier_keys"]
        result = manager.is_orca_modifier(case["modifier"])
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "get_initial_false",
                "test_type": "get",
                "initial_state": False,
                "new_state": None,
                "expected_get": False,
                "expected_set": None,
            },
            {
                "id": "get_set_true",
                "test_type": "get",
                "initial_state": True,
                "new_state": None,
                "expected_get": True,
                "expected_set": None,
            },
            {
                "id": "set_to_true",
                "test_type": "set",
                "initial_state": None,
                "new_state": True,
                "expected_get": None,
                "expected_set": True,
            },
            {
                "id": "set_to_false",
                "test_type": "set",
                "initial_state": None,
                "new_state": False,
                "expected_get": None,
                "expected_set": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_pressed_state_operations(self, test_context, case: dict) -> None:
        """Test OrcaModifierManager get_pressed_state and set_pressed_state."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()
        essential_modules["orca.debug"].reset_mock()

        if case["test_type"] == "get":
            if case["initial_state"] is not None:
                manager._is_pressed = case["initial_state"]
            result = manager.get_pressed_state()
            assert result == case["expected_get"]
        else:
            manager.set_pressed_state(case["new_state"])
            assert manager._is_pressed == case["expected_set"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "modifier_grabbed",
                "grabbed_modifiers": {"Insert": 1, "KP_Insert": 2},
                "modifier": "Insert",
                "expected_result": True,
            },
            {
                "id": "kp_modifier_grabbed",
                "grabbed_modifiers": {"Insert": 1, "KP_Insert": 2},
                "modifier": "KP_Insert",
                "expected_result": True,
            },
            {
                "id": "modifier_not_grabbed",
                "grabbed_modifiers": {"Insert": 1},
                "modifier": "KP_Insert",
                "expected_result": False,
            },
            {
                "id": "no_grabs",
                "grabbed_modifiers": {},
                "modifier": "Insert",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_modifier_grabbed(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test OrcaModifierManager.is_modifier_grabbed."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()
        manager._grabbed_modifiers = case["grabbed_modifiers"]
        result = manager.is_modifier_grabbed(case["modifier"])
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "orca_modifier_keys, expected_calls",
        [
            pytest.param(["Insert", "KP_Insert"], ["Insert", "KP_Insert"], id="insert_keys"),
            pytest.param(["Caps_Lock"], [], id="caps_lock_no_grab"),
            pytest.param(
                ["Insert", "Caps_Lock", "KP_Insert"], ["Insert", "KP_Insert"], id="mixed_keys"
            ),
            pytest.param([], [], id="no_keys"),
        ],
    )
    def test_add_grabs_for_orca_modifiers(
        self, test_context, orca_modifier_keys, expected_calls
    ) -> None:
        """Test OrcaModifierManager.add_grabs_for_orca_modifiers."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()

        mock_sm = test_context.Mock()
        test_context.patch(
            "orca.orca_modifier_manager.settings_manager.get_manager", new=mock_sm
        )
        mock_sm.return_value.get_setting.return_value = orca_modifier_keys
        mock_add_grab = test_context.Mock()
        test_context.patch_object(manager, "add_modifier_grab", new=mock_add_grab)
        manager.add_grabs_for_orca_modifiers()
        calls = [call(modifier) for modifier in expected_calls]
        mock_add_grab.assert_has_calls(calls, any_order=True)
        assert mock_add_grab.call_count == len(expected_calls)

    @pytest.mark.parametrize(
        "orca_modifier_keys, expected_calls",
        [
            pytest.param(["Insert", "KP_Insert"], ["Insert", "KP_Insert"], id="insert_keys"),
            pytest.param(["Caps_Lock"], [], id="caps_lock_no_ungrab"),
            pytest.param(
                ["Insert", "Caps_Lock", "KP_Insert"], ["Insert", "KP_Insert"], id="mixed_keys"
            ),
            pytest.param([], [], id="no_keys"),
        ],
    )
    def test_remove_grabs_for_orca_modifiers(
        self, test_context, orca_modifier_keys, expected_calls
    ) -> None:
        """Test OrcaModifierManager.remove_grabs_for_orca_modifiers."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()

        mock_sm = test_context.Mock()
        test_context.patch(
            "orca.orca_modifier_manager.settings_manager.get_manager", new=mock_sm
        )
        mock_sm.return_value.get_setting.return_value = orca_modifier_keys
        mock_remove_grab = test_context.Mock()
        test_context.patch_object(manager, "remove_modifier_grab", new=mock_remove_grab)
        manager.remove_grabs_for_orca_modifiers()
        calls = [call(modifier) for modifier in expected_calls]
        mock_remove_grab.assert_has_calls(calls, any_order=True)
        assert mock_remove_grab.call_count == len(expected_calls)
        assert manager._is_pressed is False

    @pytest.mark.parametrize(
        "scenario,has_existing,grab_result,expects_keycodes_call,expects_grab_call,expects_in_dict",
        [
            pytest.param("new", False, 123, True, True, True, id="new_modifier"),
            pytest.param("existing", True, None, False, False, True, id="existing_modifier"),
            pytest.param("failed", False, -1, True, True, False, id="failed_grab"),
        ],
    )
    def test_add_modifier_grab(
        self,
        test_context,
        scenario: str,
        has_existing: bool,
        grab_result: int | None,
        expects_keycodes_call: bool,
        expects_grab_call: bool,
        expects_in_dict: bool,
    ) -> None:
        """Test OrcaModifierManager.add_modifier_grab with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()

        if has_existing:
            manager._grabbed_modifiers["Insert"] = 123

        if scenario != "existing":
            mock_get_keycodes = test_context.Mock()
            test_context.patch(
                "orca.orca_modifier_manager.keybindings.get_keycodes", new=mock_get_keycodes
            )
            mock_iem = test_context.Mock()
            test_context.patch(
                "orca.orca_modifier_manager.input_event_manager.get_manager", new=mock_iem
            )
            mock_get_keycodes.return_value = (65379, 110)
            mock_input_manager = test_context.Mock()
            mock_input_manager.add_grab_for_modifier.return_value = grab_result
            mock_iem.return_value = mock_input_manager

        manager.add_modifier_grab("Insert")

        if expects_keycodes_call:
            mock_get_keycodes.assert_called_once_with("Insert")
        elif scenario == "existing":
            essential_modules["orca.keybindings"].get_keycodes.assert_not_called()

        if expects_grab_call:
            mock_input_manager.add_grab_for_modifier.assert_called_once_with("Insert", 65379, 110)
        elif scenario == "existing":
            essential_modules["input_manager_instance"].add_grab_for_modifier.assert_not_called()

        if expects_in_dict:
            if scenario == "new":
                assert manager._grabbed_modifiers["Insert"] == 123
            elif scenario == "existing":
                assert manager._grabbed_modifiers["Insert"] == 123
        else:
            assert "Insert" not in manager._grabbed_modifiers

    @pytest.mark.parametrize(
        "has_grabbed,expects_call",
        [
            pytest.param(True, True, id="grabbed_modifier"),
            pytest.param(False, False, id="not_grabbed_modifier"),
        ],
    )
    def test_remove_modifier_grab(
        self,
        test_context,
        has_grabbed: bool,
        expects_call: bool,
    ) -> None:
        """Test OrcaModifierManager.remove_modifier_grab with grabbed and non-grabbed modifiers."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()

        if has_grabbed:
            manager._grabbed_modifiers["Insert"] = 123
            mock_iem = test_context.Mock()
            test_context.patch(
                "orca.orca_modifier_manager.input_event_manager.get_manager", new=mock_iem
            )
            mock_input_manager = test_context.Mock()
            mock_iem.return_value = mock_input_manager

        manager.remove_modifier_grab("Insert")

        if expects_call:
            mock_input_manager.remove_grab_for_modifier.assert_called_once_with("Insert", 123)
            assert "Insert" not in manager._grabbed_modifiers
        else:
            essential_modules["input_manager_instance"].remove_grab_for_modifier.assert_not_called()

    @pytest.mark.parametrize(
        "keyval_name, expected_method",
        [
            pytest.param("Caps_Lock", "_toggle_modifier_lock", id="caps_lock"),
            pytest.param("Shift_Lock", "_toggle_modifier_lock", id="shift_lock"),
            pytest.param("Insert", "_toggle_modifier_grab", id="insert"),
            pytest.param("KP_Insert", "_toggle_modifier_grab", id="kp_insert"),
        ],
    )
    def test_toggle_modifier(
        self,
        test_context,
        keyval_name,
        expected_method,
    ) -> None:
        """Test OrcaModifierManager.toggle_modifier."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()
        mock_keyboard_event = test_context.Mock()
        mock_keyboard_event.keyval_name = keyval_name
        mock_keyboard_event.hw_code = 110
        mock_keyboard_event.modifiers = 0
        mock_keyboard_event.is_pressed_key.return_value = False
        mock_method = test_context.Mock()
        test_context.patch_object(manager, expected_method, new=mock_method)
        manager.toggle_modifier(mock_keyboard_event)
        mock_method.assert_called_once_with(mock_keyboard_event)

    @pytest.mark.parametrize(
        "is_pressed_key, expects_remove_call, expects_timeout_calls",
        [
            pytest.param(True, False, 0, id="pressed_key_no_action"),
            pytest.param(False, True, 2, id="released_key_full_action"),
        ],
    )
    def test_toggle_modifier_grab(
        self,
        test_context: OrcaTestContext,
        is_pressed_key,
        expects_remove_call,
        expects_timeout_calls,
    ) -> None:
        """Test OrcaModifierManager._toggle_modifier_grab with pressed and released keys."""
        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()
        mock_keyboard_event = test_context.Mock()
        mock_keyboard_event.keyval_name = "Insert"
        mock_keyboard_event.hw_code = 110
        mock_keyboard_event.modifiers = 0
        mock_keyboard_event.is_pressed_key.return_value = is_pressed_key
        mock_remove = test_context.Mock()
        test_context.patch_object(manager, "remove_modifier_grab", new=mock_remove)
        mock_add_grab = test_context.Mock()
        test_context.patch_object(manager, "add_modifier_grab", new=mock_add_grab)
        mock_timeout = test_context.Mock()
        test_context.patch(
            "orca.orca_modifier_manager.GLib.timeout_add", new=mock_timeout
        )
        test_context.patch(
            "orca.orca_modifier_manager.Atspi.generate_keyboard_event",
            side_effect=lambda *args, **kwargs: None
        )

        manager._toggle_modifier_grab(mock_keyboard_event)

        if expects_remove_call:
            mock_remove.assert_called_once_with("Insert")
            assert mock_timeout.call_count == expects_timeout_calls
            if expects_timeout_calls > 0:
                timeout_calls = mock_timeout.call_args_list
                assert timeout_calls[0][0][0] == 1
                assert timeout_calls[0][0][2] == 110  # hw_code
                if expects_timeout_calls > 1:
                    assert timeout_calls[1][0][0] == 500
                    assert timeout_calls[1][0][2] == "Insert"  # modifier name
        else:
            mock_remove.assert_not_called()
            assert mock_timeout.call_count == expects_timeout_calls

    @pytest.mark.parametrize(
        "keyval_name, is_pressed, expected_modifier",
        [
            pytest.param(
                "Caps_Lock",
                True,
                1 << 1,
                id="caps_lock_pressed",  # 1 << Atspi.ModifierType.SHIFTLOCK
            ),
            pytest.param(
                "Shift_Lock",
                True,
                1 << 0,
                id="shift_lock_pressed",  # 1 << Atspi.ModifierType.SHIFT
            ),
            pytest.param("Caps_Lock", False, None, id="caps_lock_released"),
            pytest.param("Other_Key", True, None, id="other_key"),
        ],
    )
    def test_toggle_modifier_lock(
        self,
        test_context,
        keyval_name,
        is_pressed,
        expected_modifier,
    ) -> None:
        """Test OrcaModifierManager._toggle_modifier_lock."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        test_context.patch(
            "orca.orca_modifier_manager.Atspi.ModifierType.SHIFTLOCK", new=1
        )
        test_context.patch("orca.orca_modifier_manager.Atspi.ModifierType.SHIFT", new=0)
        manager = orca_modifier_manager.OrcaModifierManager()
        mock_keyboard_event = test_context.Mock()
        mock_keyboard_event.keyval_name = keyval_name
        mock_keyboard_event.hw_code = 110
        mock_keyboard_event.modifiers = 0
        mock_keyboard_event.is_pressed_key.return_value = is_pressed
        mock_timeout = test_context.Mock()
        test_context.patch(
            "orca.orca_modifier_manager.GLib.timeout_add", new=mock_timeout
        )
        manager._toggle_modifier_lock(mock_keyboard_event)
        if expected_modifier is not None:
            mock_timeout.assert_called_once()
            timeout_call = mock_timeout.call_args_list[0]
            assert timeout_call[0][0] == 1  # 1ms delay
            assert timeout_call[0][2] == 0  # modifiers
            assert timeout_call[0][3] == expected_modifier  # modifier value
        else:
            mock_timeout.assert_not_called()

    def test_refresh_orca_modifiers(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModifierManager.refresh_orca_modifiers."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()
        test_context.patch("os.environ", new={"DISPLAY": ":0"})
        mock_popen = test_context.Mock()
        test_context.patch("orca.orca_modifier_manager.subprocess.Popen", new=mock_popen)
        mock_process = test_context.Mock()
        mock_process.communicate.return_value = (b"xmodmap_content", b"")
        mock_context_manager = test_context.Mock()
        mock_context_manager.__enter__ = test_context.Mock(return_value=mock_process)
        mock_context_manager.__exit__ = test_context.Mock(return_value=None)
        mock_popen.return_value = mock_context_manager
        mock_unset = test_context.Mock()
        test_context.patch_object(manager, "unset_orca_modifiers", new=mock_unset)
        mock_create = test_context.Mock()
        test_context.patch_object(manager, "_create_orca_xmodmap", new=mock_create)
        manager.refresh_orca_modifiers("test reason")
        mock_unset.assert_called_once_with("test reason")
        mock_popen.assert_called_once_with(
            ["xkbcomp", ":0", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        assert manager._original_xmodmap == b"xmodmap_content"
        mock_create.assert_called_once()

    @pytest.mark.parametrize(
        "caps_lock_orca, shift_lock_orca, caps_cleared, expected_calls",
        [
            pytest.param(True, False, False, [("set_caps", True)], id="caps_lock_enable"),
            pytest.param(False, True, False, [("set_caps", True)], id="shift_lock_enable"),
            pytest.param(True, True, False, [("set_caps", True)], id="both_enable"),
            pytest.param(
                False, False, True, [("set_caps", False)], id="disable_previously_cleared"
            ),
            pytest.param(False, False, False, [], id="no_changes"),
        ],
    )
    def test_create_orca_xmodmap(
        self,
        test_context,
        caps_lock_orca,
        shift_lock_orca,
        caps_cleared,
        expected_calls,
    ) -> None:
        """Test OrcaModifierManager._create_orca_xmodmap."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()
        manager._caps_lock_cleared = caps_cleared

        def is_orca_modifier_side_effect(modifier):
            if modifier == "Caps_Lock":
                return caps_lock_orca
            if modifier == "Shift_Lock":
                return shift_lock_orca
            return False

        mock_is_orca_modifier = test_context.Mock(side_effect=is_orca_modifier_side_effect)
        test_context.patch_object(manager, "is_orca_modifier", new=mock_is_orca_modifier)
        mock_set_caps = test_context.Mock()
        test_context.patch_object(manager, "set_caps_lock_as_orca_modifier", new=mock_set_caps)
        manager._create_orca_xmodmap()
        for call_type, enable in expected_calls:
            if call_type == "set_caps":
                mock_set_caps.assert_called_with(enable)

        if caps_lock_orca or shift_lock_orca:
            assert manager._caps_lock_cleared is True
        elif caps_cleared and not caps_lock_orca and not shift_lock_orca:
            assert manager._caps_lock_cleared is False

    @pytest.mark.parametrize(
        "has_xmodmap, expects_popen_call",
        [
            pytest.param(True, True, id="with_xmodmap"),
            pytest.param(False, False, id="no_xmodmap"),
        ],
    )
    def test_unset_orca_modifiers(
        self, test_context: OrcaTestContext, has_xmodmap, expects_popen_call
    ) -> None:
        """Test OrcaModifierManager.unset_orca_modifiers with and without xmodmap."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()
        if has_xmodmap:
            test_context.patch("os.environ", new={"DISPLAY": ":0"})
            manager._original_xmodmap = b"original_xmodmap_content"
        else:
            manager._original_xmodmap = b""

        essential_modules["orca.debug"].reset_mock()
        mock_popen = test_context.Mock()
        test_context.patch("orca.orca_modifier_manager.subprocess.Popen", new=mock_popen)

        if has_xmodmap:
            mock_process = test_context.Mock()
            mock_context_manager = test_context.Mock()
            mock_context_manager.__enter__ = test_context.Mock(return_value=mock_process)
            mock_context_manager.__exit__ = test_context.Mock(return_value=None)
            mock_popen.return_value = mock_context_manager

        manager.unset_orca_modifiers("test reason" if has_xmodmap else "")

        if expects_popen_call:
            mock_popen.assert_called_once_with(
                ["xkbcomp", "-w0", "-", ":0"], stdin=subprocess.PIPE, stdout=None, stderr=None
            )
            mock_process.communicate.assert_called_once_with(b"original_xmodmap_content")
            assert manager._caps_lock_cleared is False
        else:
            mock_popen.assert_not_called()

    @pytest.mark.parametrize(
        "enable, xmodmap_content, expects_popen_call, expected_content",
        [
            pytest.param(
                True,
                """interpret Caps_Lock+AnyOfOrNone(all) {
        action= LockMods(modifiers=Lock);
    };""",
                True,
                b"NoAction()",
                id="enable_caps_lock",
            ),
            pytest.param(
                False,
                """interpret Caps_Lock+AnyOfOrNone(all) {
        action= NoAction();
    };""",
                True,
                b"LockMods(modifiers=Lock)",
                id="disable_caps_lock",
            ),
            pytest.param(
                True,
                "some other xmodmap content",
                False,
                None,
                id="no_changes_needed",
            ),
        ],
    )
    def test_set_caps_lock_as_orca_modifier(
        self,
        test_context: OrcaTestContext,
        enable,
        xmodmap_content,
        expects_popen_call,
        expected_content,
    ) -> None:
        """Test OrcaModifierManager.set_caps_lock_as_orca_modifier with various scenarios."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()
        if expects_popen_call:
            test_context.patch("os.environ", new={"DISPLAY": ":0"})

        manager._original_xmodmap = xmodmap_content.encode("UTF-8")
        essential_modules["orca.debug"].reset_mock()
        mock_popen = test_context.Mock()
        test_context.patch("orca.orca_modifier_manager.subprocess.Popen", new=mock_popen)

        if expects_popen_call:
            mock_process = test_context.Mock()
            mock_context_manager = test_context.Mock()
            mock_context_manager.__enter__ = test_context.Mock(return_value=mock_process)
            mock_context_manager.__exit__ = test_context.Mock(return_value=None)
            mock_popen.return_value = mock_context_manager

        manager.set_caps_lock_as_orca_modifier(enable)

        if expects_popen_call:
            mock_popen.assert_called_once_with(
                ["xkbcomp", "-w0", "-", ":0"], stdin=subprocess.PIPE, stdout=None, stderr=None
            )
            called_data = mock_process.communicate.call_args[0][0]
            assert expected_content in called_data
        else:
            mock_popen.assert_not_called()

    def test_get_manager(
        self,
        test_context,
    ) -> None:
        """Test orca_modifier_manager.get_manager."""

        self._setup_dependencies(test_context)
        from orca import orca_modifier_manager

        manager1 = orca_modifier_manager.get_manager()
        assert manager1 is not None
        assert isinstance(manager1, orca_modifier_manager.OrcaModifierManager)

        manager2 = orca_modifier_manager.get_manager()
        assert manager2 is manager1
