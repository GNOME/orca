# Unit tests for orca_modifier_manager.py OrcaModifierManager class methods.
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

"""Unit tests for orca_modifier_manager.py OrcaModifierManager class methods."""

from __future__ import annotations

import subprocess
import sys
from unittest.mock import Mock, patch, call

import gi
import pytest

gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Atspi, Gdk


@pytest.mark.unit
class TestOrcaModifierManager:
    """Test OrcaModifierManager class methods."""

    @pytest.fixture
    def mock_modifier_manager_deps(self, mock_orca_dependencies, monkeypatch):
        """Set up mocks for orca_modifier_manager dependencies."""

        mock_keybindings = Mock()
        mock_input_event_manager = Mock()
        mock_settings_manager = Mock()

        mock_input_manager_instance = Mock()
        mock_settings_manager_instance = Mock()
        mock_input_event_manager.get_manager.return_value = mock_input_manager_instance
        mock_settings_manager.get_manager.return_value = mock_settings_manager_instance

        mock_settings_manager_instance.get_setting.return_value = ["Insert", "KP_Insert"]

        mock_display = Mock(spec=Gdk.Display)
        mock_device_manager = Mock()
        mock_display.get_device_manager.return_value = mock_device_manager
        monkeypatch.setattr(Gdk.Display, "get_default", lambda: mock_display)

        monkeypatch.setitem(sys.modules, "orca.keybindings", mock_keybindings)
        monkeypatch.setitem(sys.modules, "orca.input_event_manager", mock_input_event_manager)
        monkeypatch.setitem(sys.modules, "orca.settings_manager", mock_settings_manager)

        return {
            "debug": mock_orca_dependencies.debug,
            "keybindings": mock_keybindings,
            "input_event_manager": mock_input_event_manager,
            "settings_manager": mock_settings_manager,
            "input_manager_instance": mock_input_manager_instance,
            "settings_manager_instance": mock_settings_manager_instance,
            "display": mock_display,
            "device_manager": mock_device_manager,
        }

    @pytest.fixture
    def mock_keyboard_event(self):
        """Create a mock KeyboardEvent."""
        mock_event = Mock()
        mock_event.keyval_name = "Insert"
        mock_event.hw_code = 110
        mock_event.modifiers = 0
        mock_event.is_pressed_key.return_value = False
        return mock_event

    @pytest.fixture
    def manager_instance(self, mock_modifier_manager_deps, monkeypatch):
        """Create OrcaModifierManager instance with mocked dependencies."""
        # Import the module
        from orca import orca_modifier_manager

        # Ensure the module uses the correct mocks
        debug_mock = mock_modifier_manager_deps["debug"]
        settings_manager_mock = mock_modifier_manager_deps["settings_manager"]
        input_event_manager_mock = mock_modifier_manager_deps["input_event_manager"]
        keybindings_mock = mock_modifier_manager_deps["keybindings"]

        monkeypatch.setattr(orca_modifier_manager, "debug", debug_mock)
        monkeypatch.setattr(orca_modifier_manager, "settings_manager", settings_manager_mock)
        monkeypatch.setattr(orca_modifier_manager, "input_event_manager", input_event_manager_mock)
        monkeypatch.setattr(orca_modifier_manager, "keybindings", keybindings_mock)

        # Create and return a fresh instance
        return orca_modifier_manager.OrcaModifierManager()

    def test_init(self, mock_modifier_manager_deps):
        """Test OrcaModifierManager.__init__."""
        # Clean module cache first
        if "orca.orca_modifier_manager" in sys.modules:
            del sys.modules["orca.orca_modifier_manager"]

        from orca import orca_modifier_manager

        manager = orca_modifier_manager.OrcaModifierManager()

        assert not manager._grabbed_modifiers
        assert manager._is_pressed is False
        assert manager._original_xmodmap == b""
        assert manager._caps_lock_cleared is False
        assert manager._need_to_restore_orca_modifier is False

        # Verify device manager connections
        mock_modifier_manager_deps["device_manager"].connect.assert_any_call(
            "device-added", manager._on_device_changed
        )
        mock_modifier_manager_deps["device_manager"].connect.assert_any_call(
            "device-removed", manager._on_device_changed
        )

    def test_init_no_display(self, mock_modifier_manager_deps, monkeypatch):
        """Test OrcaModifierManager.__init__ with no display available."""
        # Import the module to get the class
        from orca import orca_modifier_manager

        # Get debug mock and ensure module uses it
        debug_mock = mock_modifier_manager_deps["debug"]
        debug_mock.reset_mock()

        # Patch the module's debug reference to use our mock
        monkeypatch.setattr(orca_modifier_manager, "debug", debug_mock)

        # Patch the Gdk.Display to return None and create a new instance
        with patch.object(Gdk.Display, "get_default", return_value=None):
            manager = orca_modifier_manager.OrcaModifierManager()

            # Should print debug message about inability to listen for device changes
            debug_mock.print_message.assert_called_with(
                debug_mock.LEVEL_INFO,
                "ORCA MODIFIER MANAGER: Cannot listen for input device changes.",
                True,
            )

    @pytest.mark.parametrize(
        "device_source, should_refresh",
        [
            pytest.param(Gdk.InputSource.KEYBOARD, True, id="keyboard_device"),
            pytest.param(Gdk.InputSource.MOUSE, False, id="mouse_device"),
            pytest.param(Gdk.InputSource.TOUCHSCREEN, False, id="touchscreen_device"),
        ],
    )
    def test_on_device_changed(
        self, manager_instance, mock_modifier_manager_deps, device_source, should_refresh
    ):
        """Test OrcaModifierManager._on_device_changed."""
        mock_device = Mock(spec=Gdk.Device)
        mock_device.get_source.return_value = device_source

        with patch.object(manager_instance, "refresh_orca_modifiers") as mock_refresh:
            manager_instance._on_device_changed(None, mock_device)

            mock_modifier_manager_deps["debug"].print_tokens.assert_called_with(
                mock_modifier_manager_deps["debug"].LEVEL_INFO,
                ["ORCA MODIFIER MANAGER: Device changed", device_source],
                True,
            )

            if should_refresh:
                mock_refresh.assert_called_once_with("Keyboard change detected.")
            else:
                mock_refresh.assert_not_called()

    @pytest.mark.parametrize(
        "modifier, orca_modifier_keys, is_grabbed, expected_result",
        [
            pytest.param("Insert", ["Insert", "KP_Insert"], True, True, id="insert_grabbed"),
            pytest.param("Insert", ["Insert", "KP_Insert"], False, False, id="insert_not_grabbed"),
            pytest.param("KP_Insert", ["Insert", "KP_Insert"], True, True, id="kp_insert_grabbed"),
            pytest.param(
                "KP_Insert", ["Insert", "KP_Insert"], False, False, id="kp_insert_not_grabbed"
            ),
            pytest.param("Caps_Lock", ["Caps_Lock"], False, True, id="caps_lock_always_true"),
            pytest.param("Shift_Lock", ["Shift_Lock"], False, True, id="shift_lock_always_true"),
            pytest.param("Control_L", ["Insert"], False, False, id="not_orca_modifier"),
        ],
    )
    def test_is_orca_modifier(
        self,
        manager_instance,
        mock_modifier_manager_deps,
        modifier,
        orca_modifier_keys,
        is_grabbed,
        expected_result,
    ):
        """Test OrcaModifierManager.is_orca_modifier."""
        mock_modifier_manager_deps[
            "settings_manager_instance"
        ].get_setting.return_value = orca_modifier_keys
        manager_instance._grabbed_modifiers = {"Insert": 1, "KP_Insert": 2} if is_grabbed else {}

        result = manager_instance.is_orca_modifier(modifier)
        assert result == expected_result

    def test_get_pressed_state(self, manager_instance):
        """Test OrcaModifierManager.get_pressed_state."""
        # Initially False
        assert manager_instance.get_pressed_state() is False

        # Set to True
        manager_instance._is_pressed = True
        assert manager_instance.get_pressed_state() is True

    def test_set_pressed_state(self, manager_instance, mock_modifier_manager_deps):
        """Test OrcaModifierManager.set_pressed_state."""
        manager_instance.set_pressed_state(True)

        assert manager_instance._is_pressed is True
        mock_modifier_manager_deps["debug"].print_message.assert_called_with(
            mock_modifier_manager_deps["debug"].LEVEL_INFO,
            "ORCA MODIFIER MANAGER: Setting pressed state to True",
            True,
        )

        manager_instance.set_pressed_state(False)

        assert manager_instance._is_pressed is False
        mock_modifier_manager_deps["debug"].print_message.assert_called_with(
            mock_modifier_manager_deps["debug"].LEVEL_INFO,
            "ORCA MODIFIER MANAGER: Setting pressed state to False",
            True,
        )

    @pytest.mark.parametrize(
        "grabbed_modifiers, modifier, expected_result",
        [
            pytest.param({"Insert": 1, "KP_Insert": 2}, "Insert", True, id="modifier_grabbed"),
            pytest.param(
                {"Insert": 1, "KP_Insert": 2}, "KP_Insert", True, id="kp_modifier_grabbed"
            ),
            pytest.param({"Insert": 1}, "KP_Insert", False, id="modifier_not_grabbed"),
            pytest.param({}, "Insert", False, id="no_grabs"),
        ],
    )
    def test_is_modifier_grabbed(
        self, manager_instance, grabbed_modifiers, modifier, expected_result
    ):
        """Test OrcaModifierManager.is_modifier_grabbed."""
        manager_instance._grabbed_modifiers = grabbed_modifiers

        result = manager_instance.is_modifier_grabbed(modifier)
        assert result == expected_result

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
        self, manager_instance, mock_modifier_manager_deps, orca_modifier_keys, expected_calls
    ):
        """Test OrcaModifierManager.add_grabs_for_orca_modifiers."""
        mock_modifier_manager_deps[
            "settings_manager_instance"
        ].get_setting.return_value = orca_modifier_keys

        with patch.object(manager_instance, "add_modifier_grab") as mock_add_grab:
            manager_instance.add_grabs_for_orca_modifiers()

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
        self, manager_instance, mock_modifier_manager_deps, orca_modifier_keys, expected_calls
    ):
        """Test OrcaModifierManager.remove_grabs_for_orca_modifiers."""
        mock_modifier_manager_deps[
            "settings_manager_instance"
        ].get_setting.return_value = orca_modifier_keys

        with patch.object(manager_instance, "remove_modifier_grab") as mock_remove_grab:
            manager_instance.remove_grabs_for_orca_modifiers()

            calls = [call(modifier) for modifier in expected_calls]
            mock_remove_grab.assert_has_calls(calls, any_order=True)
            assert mock_remove_grab.call_count == len(expected_calls)

            # Should set pressed state to False
            assert manager_instance._is_pressed is False
            mock_modifier_manager_deps["debug"].print_message.assert_called_with(
                mock_modifier_manager_deps["debug"].LEVEL_INFO,
                "ORCA MODIFIER MANAGER: Setting pressed state to False for grab removal",
                True,
            )

    def test_add_modifier_grab_new(self, manager_instance, mock_modifier_manager_deps):
        """Test OrcaModifierManager.add_modifier_grab for new modifier."""
        mock_modifier_manager_deps["keybindings"].get_keycodes.return_value = (65379, 110)
        mock_modifier_manager_deps[
            "input_manager_instance"
        ].add_grab_for_modifier.return_value = 123

        manager_instance.add_modifier_grab("Insert")

        mock_modifier_manager_deps["keybindings"].get_keycodes.assert_called_once_with("Insert")
        mock_modifier_manager_deps[
            "input_manager_instance"
        ].add_grab_for_modifier.assert_called_once_with("Insert", 65379, 110)
        assert manager_instance._grabbed_modifiers["Insert"] == 123

    def test_add_modifier_grab_existing(self, manager_instance, mock_modifier_manager_deps):
        """Test OrcaModifierManager.add_modifier_grab for existing modifier."""
        manager_instance._grabbed_modifiers["Insert"] = 123

        manager_instance.add_modifier_grab("Insert")

        # Should not call keybindings or input manager
        mock_modifier_manager_deps["keybindings"].get_keycodes.assert_not_called()
        mock_modifier_manager_deps[
            "input_manager_instance"
        ].add_grab_for_modifier.assert_not_called()

    def test_add_modifier_grab_failed(self, manager_instance, mock_modifier_manager_deps):
        """Test OrcaModifierManager.add_modifier_grab when grab fails."""
        mock_modifier_manager_deps["keybindings"].get_keycodes.return_value = (65379, 110)
        mock_modifier_manager_deps["input_manager_instance"].add_grab_for_modifier.return_value = -1

        manager_instance.add_modifier_grab("Insert")

        # Should not add to grabbed_modifiers dict
        assert "Insert" not in manager_instance._grabbed_modifiers

    def test_remove_modifier_grab(self, manager_instance, mock_modifier_manager_deps):
        """Test OrcaModifierManager.remove_modifier_grab."""
        manager_instance._grabbed_modifiers["Insert"] = 123

        manager_instance.remove_modifier_grab("Insert")

        mock_modifier_manager_deps[
            "input_manager_instance"
        ].remove_grab_for_modifier.assert_called_once_with("Insert", 123)
        assert "Insert" not in manager_instance._grabbed_modifiers

    def test_remove_modifier_grab_not_grabbed(self, manager_instance, mock_modifier_manager_deps):
        """Test OrcaModifierManager.remove_modifier_grab for non-grabbed modifier."""
        manager_instance.remove_modifier_grab("Insert")

        # Should not call input manager
        mock_modifier_manager_deps[
            "input_manager_instance"
        ].remove_grab_for_modifier.assert_not_called()

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
        self, manager_instance, mock_keyboard_event, keyval_name, expected_method
    ):
        """Test OrcaModifierManager.toggle_modifier."""
        mock_keyboard_event.keyval_name = keyval_name

        with patch.object(manager_instance, expected_method) as mock_method:
            manager_instance.toggle_modifier(mock_keyboard_event)
            mock_method.assert_called_once_with(mock_keyboard_event)

    def test_toggle_modifier_grab_pressed_key(
        self, manager_instance, mock_keyboard_event, mock_modifier_manager_deps
    ):
        """Test OrcaModifierManager._toggle_modifier_grab with pressed key."""
        mock_keyboard_event.is_pressed_key.return_value = True

        with patch.object(manager_instance, "remove_modifier_grab") as mock_remove:
            manager_instance._toggle_modifier_grab(mock_keyboard_event)
            mock_remove.assert_not_called()

    @patch("orca.orca_modifier_manager.GLib.timeout_add")
    @patch("orca.orca_modifier_manager.Atspi.generate_keyboard_event")
    def test_toggle_modifier_grab_release(
        self,
        mock_generate,
        mock_timeout,
        manager_instance,
        mock_keyboard_event,
        mock_modifier_manager_deps,
    ):
        """Test OrcaModifierManager._toggle_modifier_grab with key release."""
        mock_keyboard_event.is_pressed_key.return_value = False
        mock_keyboard_event.keyval_name = "Insert"
        mock_keyboard_event.hw_code = 110

        with (
            patch.object(manager_instance, "remove_modifier_grab") as mock_remove,
            patch.object(manager_instance, "add_modifier_grab") as mock_add,
        ):
            manager_instance._toggle_modifier_grab(mock_keyboard_event)

            # Should remove grab before toggle
            mock_remove.assert_called_once_with("Insert")

            # Should schedule toggle and restore
            assert mock_timeout.call_count == 2
            timeout_calls = mock_timeout.call_args_list

            # First call: schedule toggle with 1ms delay
            assert timeout_calls[0][0][0] == 1
            assert timeout_calls[0][0][2] == 110  # hw_code

            # Second call: schedule restore grab with 500ms delay
            assert timeout_calls[1][0][0] == 500
            assert timeout_calls[1][0][2] == "Insert"  # modifier name

    @pytest.mark.parametrize(
        "keyval_name, is_pressed, expected_modifier",
        [
            pytest.param(
                "Caps_Lock", True, 1 << Atspi.ModifierType.SHIFTLOCK, id="caps_lock_pressed"
            ),
            pytest.param(
                "Shift_Lock", True, 1 << Atspi.ModifierType.SHIFT, id="shift_lock_pressed"
            ),
            pytest.param("Caps_Lock", False, None, id="caps_lock_released"),
            pytest.param("Other_Key", True, None, id="other_key"),
        ],
    )
    @patch("orca.orca_modifier_manager.GLib.timeout_add")
    def test_toggle_modifier_lock(
        self,
        mock_timeout,
        manager_instance,
        mock_keyboard_event,
        mock_modifier_manager_deps,
        keyval_name,
        is_pressed,
        expected_modifier,
    ):
        """Test OrcaModifierManager._toggle_modifier_lock."""
        mock_keyboard_event.keyval_name = keyval_name
        mock_keyboard_event.is_pressed_key.return_value = is_pressed
        mock_keyboard_event.modifiers = 0

        manager_instance._toggle_modifier_lock(mock_keyboard_event)

        if expected_modifier is not None:
            mock_timeout.assert_called_once()
            timeout_call = mock_timeout.call_args_list[0]
            assert timeout_call[0][0] == 1  # 1ms delay
            assert timeout_call[0][2] == 0  # modifiers
            assert timeout_call[0][3] == expected_modifier  # modifier value
        else:
            mock_timeout.assert_not_called()

    @patch("orca.orca_modifier_manager.subprocess.Popen")
    def test_refresh_orca_modifiers(
        self, mock_popen, manager_instance, mock_modifier_manager_deps, monkeypatch
    ):
        """Test OrcaModifierManager.refresh_orca_modifiers."""

        monkeypatch.setenv("DISPLAY", ":0")
        mock_process = Mock()
        mock_process.communicate.return_value = (b"xmodmap_content", b"")
        mock_popen.return_value.__enter__.return_value = mock_process

        with (
            patch.object(manager_instance, "unset_orca_modifiers") as mock_unset,
            patch.object(manager_instance, "_create_orca_xmodmap") as mock_create,
        ):
            manager_instance.refresh_orca_modifiers("test reason")

            mock_unset.assert_called_once_with("test reason")
            mock_popen.assert_called_once_with(
                ["xkbcomp", ":0", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            assert manager_instance._original_xmodmap == b"xmodmap_content"
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
        manager_instance,
        mock_modifier_manager_deps,
        caps_lock_orca,
        shift_lock_orca,
        caps_cleared,
        expected_calls,
    ):
        """Test OrcaModifierManager._create_orca_xmodmap."""
        manager_instance._caps_lock_cleared = caps_cleared

        def is_orca_modifier_side_effect(modifier):
            if modifier == "Caps_Lock":
                return caps_lock_orca
            if modifier == "Shift_Lock":
                return shift_lock_orca
            return False

        with (
            patch.object(
                manager_instance, "is_orca_modifier", side_effect=is_orca_modifier_side_effect
            ),
            patch.object(manager_instance, "set_caps_lock_as_orca_modifier") as mock_set_caps,
        ):
            manager_instance._create_orca_xmodmap()

            for call_type, enable in expected_calls:
                if call_type == "set_caps":
                    mock_set_caps.assert_called_with(enable)

            # Check _caps_lock_cleared state
            if caps_lock_orca or shift_lock_orca:
                assert manager_instance._caps_lock_cleared is True
            elif caps_cleared and not caps_lock_orca and not shift_lock_orca:
                assert manager_instance._caps_lock_cleared is False

    @patch("orca.orca_modifier_manager.subprocess.Popen")
    def test_unset_orca_modifiers(
        self, mock_popen, manager_instance, mock_modifier_manager_deps, monkeypatch
    ):
        """Test OrcaModifierManager.unset_orca_modifiers."""

        monkeypatch.setenv("DISPLAY", ":0")
        manager_instance._original_xmodmap = b"original_xmodmap_content"
        mock_process = Mock()
        mock_popen.return_value.__enter__.return_value = mock_process

        manager_instance.unset_orca_modifiers("test reason")

        mock_popen.assert_called_once_with(
            ["xkbcomp", "-w0", "-", ":0"], stdin=subprocess.PIPE, stdout=None, stderr=None
        )
        mock_process.communicate.assert_called_once_with(b"original_xmodmap_content")
        assert manager_instance._caps_lock_cleared is False

    def test_unset_orca_modifiers_no_xmodmap(self, manager_instance, mock_modifier_manager_deps):
        """Test OrcaModifierManager.unset_orca_modifiers with no stored xmodmap."""
        manager_instance._original_xmodmap = b""

        with patch("orca.orca_modifier_manager.subprocess.Popen") as mock_popen:
            manager_instance.unset_orca_modifiers()

            mock_popen.assert_not_called()
            mock_modifier_manager_deps["debug"].print_message.assert_called_with(
                mock_modifier_manager_deps["debug"].LEVEL_INFO,
                "ORCA MODIFIER MANAGER: No stored xmodmap found",
                True,
            )

    @patch("orca.orca_modifier_manager.subprocess.Popen")
    def test_set_caps_lock_as_orca_modifier_enable(
        self, mock_popen, manager_instance, mock_modifier_manager_deps, monkeypatch
    ):
        """Test OrcaModifierManager.set_caps_lock_as_orca_modifier enable."""

        monkeypatch.setenv("DISPLAY", ":0")
        original_xmodmap = """
            interpret Caps_Lock+AnyOfOrNone(all) {
                action= LockMods(modifiers=Lock);
            };
        """.encode("UTF-8")
        manager_instance._original_xmodmap = original_xmodmap
        mock_process = Mock()
        mock_popen.return_value.__enter__.return_value = mock_process

        manager_instance.set_caps_lock_as_orca_modifier(True)

        mock_popen.assert_called_once_with(
            ["xkbcomp", "-w0", "-", ":0"], stdin=subprocess.PIPE, stdout=None, stderr=None
        )

        # Check that the communicated data contains NoAction
        called_data = mock_process.communicate.call_args[0][0]
        assert b"NoAction()" in called_data

    @patch("orca.orca_modifier_manager.subprocess.Popen")
    def test_set_caps_lock_as_orca_modifier_disable(
        self, mock_popen, manager_instance, mock_modifier_manager_deps, monkeypatch
    ):
        """Test OrcaModifierManager.set_caps_lock_as_orca_modifier disable."""

        monkeypatch.setenv("DISPLAY", ":0")
        original_xmodmap = """
            interpret Caps_Lock+AnyOfOrNone(all) {
                action= NoAction();
            };
        """.encode("UTF-8")
        manager_instance._original_xmodmap = original_xmodmap
        mock_process = Mock()
        mock_popen.return_value.__enter__.return_value = mock_process

        manager_instance.set_caps_lock_as_orca_modifier(False)

        # Should call subprocess to apply modified xmodmap
        mock_popen.assert_called_once()

        # Check that the communicated data contains LockMods
        called_data = mock_process.communicate.call_args[0][0]
        assert b"LockMods(modifiers=Lock)" in called_data

    def test_set_caps_lock_as_orca_modifier_no_changes(
        self, manager_instance, mock_modifier_manager_deps
    ):
        """Test OrcaModifierManager.set_caps_lock_as_orca_modifier with no changes needed."""

        original_xmodmap = b"some other xmodmap content"
        manager_instance._original_xmodmap = original_xmodmap

        with patch("orca.orca_modifier_manager.subprocess.Popen") as mock_popen:
            manager_instance.set_caps_lock_as_orca_modifier(True)

            # Should not call subprocess since no modifications were made
            mock_popen.assert_not_called()
            mock_modifier_manager_deps["debug"].print_message.assert_called_with(
                mock_modifier_manager_deps["debug"].LEVEL_INFO,
                "ORCA MODIFIER MANAGER: Not updating xmodmap",
                True,
            )

    def test_get_manager(self, mock_modifier_manager_deps):
        """Test orca_modifier_manager.get_manager."""
        from orca import orca_modifier_manager

        # First call should return instance
        manager1 = orca_modifier_manager.get_manager()
        assert manager1 is not None
        assert isinstance(manager1, orca_modifier_manager.OrcaModifierManager)

        # Second call should return same instance
        manager2 = orca_modifier_manager.get_manager()
        assert manager2 is manager1
