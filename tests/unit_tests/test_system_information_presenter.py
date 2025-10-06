# Unit tests for system_information_presenter.py methods.
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

"""Unit tests for system_information_presenter.py methods."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestSystemInformationPresenter:
    """Test SystemInformationPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for system_information_presenter dependencies."""

        additional_modules = ["psutil"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.PRESENT_CURRENT_TIME = "presentCurrentTime"
        cmdnames_mock.PRESENT_CURRENT_DATE = "presentCurrentDate"
        cmdnames_mock.PRESENT_BATTERY_STATUS = "presentBatteryStatus"
        cmdnames_mock.PRESENT_CPU_AND_MEMORY_USAGE = "presentCpuAndMemoryUsage"

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        dbus_service_mock = essential_modules["orca.dbus_service"]
        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module = test_context.Mock()
        dbus_service_mock.get_remote_controller = test_context.Mock(return_value=controller_mock)
        dbus_service_mock.command = lambda func: func

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_class = test_context.Mock()
        input_event_handler_instance = test_context.Mock()
        input_event_handler_class.return_value = input_event_handler_instance
        input_event_mock.InputEventHandler = input_event_handler_class
        input_event_mock.InputEvent = test_context.Mock

        keybindings_mock = essential_modules["orca.keybindings"]
        key_bindings_instance = test_context.Mock()
        key_bindings_instance.is_empty = test_context.Mock(return_value=True)
        key_bindings_instance.remove_key_grabs = test_context.Mock()
        key_bindings_instance.add = test_context.Mock()
        keybindings_mock.KeyBindings = test_context.Mock(return_value=key_bindings_instance)
        keybinding_instance = test_context.Mock()
        keybindings_mock.KeyBinding = test_context.Mock(return_value=keybinding_instance)
        keybindings_mock.DEFAULT_MODIFIER_MASK = 1
        keybindings_mock.ORCA_MODIFIER_MASK = 2

        messages_mock = essential_modules["orca.messages"]
        messages_mock.BATTERY_STATUS_UNKNOWN = "Battery status unknown"
        messages_mock.BATTERY_LEVEL = "Battery: %d%%"
        messages_mock.BATTERY_PLUGGED_IN_TRUE = "plugged in"
        messages_mock.BATTERY_PLUGGED_IN_FALSE = "not plugged in"
        messages_mock.CPU_AND_MEMORY_USAGE_UNKNOWN = "CPU and memory usage unknown"
        messages_mock.CPU_AND_MEMORY_USAGE_LEVELS = "CPU: %d%%. Memory: %d%%"
        messages_mock.memory_usage_gb = test_context.Mock(return_value="5.2GB / 16GB")
        messages_mock.memory_usage_mb = test_context.Mock(return_value="512MB / 1024MB")

        messages_mock.DATE_FORMAT_LOCALE = "%x"
        messages_mock.DATE_FORMAT_NUMBERS_DM = "%d/%m"
        messages_mock.DATE_FORMAT_NUMBERS_MD = "%m/%d"
        messages_mock.DATE_FORMAT_NUMBERS_DMY = "%d/%m/%Y"
        messages_mock.DATE_FORMAT_NUMBERS_MDY = "%m/%d/%Y"
        messages_mock.DATE_FORMAT_NUMBERS_YMD = "%Y/%m/%d"
        messages_mock.DATE_FORMAT_FULL_DM = "%A, %-d %B"
        messages_mock.DATE_FORMAT_FULL_MD = "%A, %B %-d"
        messages_mock.DATE_FORMAT_FULL_DMY = "%A, %-d %B, %Y"
        messages_mock.DATE_FORMAT_FULL_MDY = "%A, %B %-d, %Y"
        messages_mock.DATE_FORMAT_FULL_YMD = "%Y. %B %-d, %A"
        messages_mock.DATE_FORMAT_ABBREVIATED_DM = "%a, %-d %b"
        messages_mock.DATE_FORMAT_ABBREVIATED_MD = "%a, %b %-d"
        messages_mock.DATE_FORMAT_ABBREVIATED_DMY = "%a, %-d %b, %Y"
        messages_mock.DATE_FORMAT_ABBREVIATED_MDY = "%a, %b %-d, %Y"
        messages_mock.DATE_FORMAT_ABBREVIATED_YMD = "%Y. %b %-d, %a"

        messages_mock.TIME_FORMAT_LOCALE = "%X"
        messages_mock.TIME_FORMAT_24_HMS = "%H:%M:%S"
        messages_mock.TIME_FORMAT_24_HM = "%H:%M"
        messages_mock.TIME_FORMAT_12_HM = "%I:%M %p"
        messages_mock.TIME_FORMAT_12_HMS = "%I:%M:%S %p"
        messages_mock.TIME_FORMAT_24_HMS_WITH_WORDS = "%H hours, %M minutes and %S seconds"
        messages_mock.TIME_FORMAT_24_HM_WITH_WORDS = "%H hours and %M minutes"

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_instance = test_context.Mock()
        settings_instance.get_setting = test_context.Mock(
            side_effect=lambda key: {
                "presentTimeFormat": "%I:%M %p",
                "presentDateFormat": "%A, %B %d, %Y",
            }.get(key, "%c")
        )
        settings_manager_mock.get_manager = test_context.Mock(return_value=settings_instance)

        psutil_mock = essential_modules["psutil"]
        battery_mock = test_context.Mock()
        battery_mock.percent = 85
        battery_mock.power_plugged = True
        psutil_mock.sensors_battery = test_context.Mock(return_value=battery_mock)
        psutil_mock.cpu_percent = test_context.Mock(return_value=45.7)

        memory_mock = test_context.Mock()
        memory_mock.percent = 67.3
        memory_mock.total = 16 * 1024**3
        memory_mock.used = 8 * 1024**3
        psutil_mock.virtual_memory = test_context.Mock(return_value=memory_mock)

        essential_modules["controller"] = controller_mock
        essential_modules["input_event_handler"] = input_event_handler_class
        essential_modules["settings_instance"] = settings_instance
        essential_modules["battery"] = battery_mock
        essential_modules["memory"] = memory_mock
        essential_modules["key_bindings_instance"] = key_bindings_instance

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test SystemInformationPresenter.__init__."""

        self._setup_dependencies(test_context)

        mock_controller = test_context.Mock()
        test_context.patch(
            "orca.system_information_presenter.dbus_service.get_remote_controller",
            return_value=mock_controller,
        )

        mock_bindings_instance = test_context.Mock()
        mock_keybindings_class = test_context.patch(
            "orca.system_information_presenter.keybindings.KeyBindings", 
            return_value=mock_bindings_instance
        )
        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()

        assert presenter._handlers is not None
        assert len(presenter._handlers) == 4
        assert "presentTimeHandler" in presenter._handlers
        assert "presentDateHandler" in presenter._handlers
        assert "present_battery_status" in presenter._handlers
        assert "present_cpu_and_memory_usage" in presenter._handlers

        assert presenter._bindings is not None
        mock_keybindings_class.assert_called()

        mock_controller.register_decorated_module.assert_called_with(
            "SystemInformationPresenter", presenter
        )

    @pytest.mark.parametrize(
        "is_empty",
        [
            pytest.param(True, id="empty_bindings"),
            pytest.param(False, id="existing_bindings"),
        ],
    )
    def test_get_bindings_no_refresh(self, test_context: OrcaTestContext, is_empty: bool) -> None:
        """Test SystemInformationPresenter.get_bindings with refresh=False."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        key_bindings_instance = essential_modules["key_bindings_instance"]
        is_empty_mock = key_bindings_instance.is_empty
        is_empty_mock.return_value = is_empty
        result = presenter.get_bindings(refresh=False, is_desktop=True)

        is_empty_mock.assert_called_once()
        assert result == presenter._bindings

    @pytest.mark.parametrize(
        "is_desktop",
        [
            pytest.param(True, id="desktop"),
            pytest.param(False, id="not_desktop"),
        ],
    )
    def test_get_bindings_refresh(self, test_context: OrcaTestContext, is_desktop: bool) -> None:
        """Test SystemInformationPresenter.get_bindings with refresh=True and desktop settings."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        result = presenter.get_bindings(refresh=True, is_desktop=is_desktop)

        assert result == presenter._bindings

        if is_desktop:
            key_bindings_instance = essential_modules["key_bindings_instance"]
            remove_key_grabs_mock = key_bindings_instance.remove_key_grabs
            remove_key_grabs_mock.assert_called_once()

        essential_modules["orca.debug"].print_message.assert_any_call(
            800,
            f"SYSTEM INFORMATION PRESENTER: Refreshing bindings. Is desktop: {is_desktop}",
            True,
        )

    @pytest.mark.parametrize(
        "refresh",
        [
            pytest.param(False, id="no_refresh"),
            pytest.param(True, id="refresh"),
        ],
    )
    def test_get_handlers(self, test_context: OrcaTestContext, refresh: bool) -> None:
        """Test SystemInformationPresenter.get_handlers with refresh parameter."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        original_handlers = presenter._handlers
        result = presenter.get_handlers(refresh=refresh)

        assert result == presenter._handlers

        if refresh:
            essential_modules["orca.debug"].print_message.assert_any_call(
                800, "SYSTEM INFORMATION PRESENTER: Refreshing handlers.", True
            )
        else:
            assert result == original_handlers
            assert len(result) == 4

    def test_setup_handlers(self, test_context: OrcaTestContext) -> None:
        """Test SystemInformationPresenter._setup_handlers."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()

        expected_handlers = [
            "presentTimeHandler",
            "presentDateHandler",
            "present_battery_status",
            "present_cpu_and_memory_usage",
        ]
        for handler_name in expected_handlers:
            assert handler_name in presenter._handlers

        assert essential_modules["input_event_handler"].call_count == 8

        essential_modules["orca.debug"].print_message.assert_any_call(
            800, "SYSTEM INFORMATION PRESENTER: Handlers set up.", True
        )

    def test_setup_bindings(self, test_context: OrcaTestContext) -> None:
        """Test SystemInformationPresenter._setup_bindings."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()

        keybindings_class_mock = essential_modules["orca.keybindings"].KeyBindings
        initial_call_count = keybindings_class_mock.call_count
        essential_modules["orca.debug"].print_message.reset_mock()

        presenter._setup_bindings()

        assert keybindings_class_mock.call_count == initial_call_count + 1

        key_bindings_instance = essential_modules["key_bindings_instance"]
        add_mock = key_bindings_instance.add
        assert add_mock.call_count == 4

        essential_modules["orca.debug"].print_message.assert_called_with(
            800, "SYSTEM INFORMATION PRESENTER: Bindings set up.", True
        )

    @pytest.mark.parametrize(
        "method_name,setting_key,format_string,expected_output",
        [
            ("present_time", "presentTimeFormat", "%I:%M %p", "2:30 PM"),
            ("present_date", "presentDateFormat", "%A, %B %d, %Y", "Monday, July 28, 2025"),
        ],
    )
    @pytest.mark.parametrize(
        "has_event,debugging_enabled",
        [
            pytest.param(True, True, id="with_event_debug"),
            pytest.param(False, False, id="no_event_no_debug"),
        ],
    )
    def test_present_time_and_date(
        self,
        test_context: OrcaTestContext,
        method_name: str,
        setting_key: str,
        format_string: str,
        expected_output: str,
        has_event: bool,
        debugging_enabled: bool,
    ) -> None:
        """Test SystemInformationPresenter time and date presentation methods."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.system_information_presenter import SystemInformationPresenter

        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        mock_time_tuple = time.struct_time((2025, 7, 28, 14, 30, 0, 0, 209, 0))
        test_context.patch("time.localtime", return_value=mock_time_tuple)
        mock_strftime = test_context.patch("time.strftime", return_value=expected_output)
        presenter = SystemInformationPresenter()

        mock_event = test_context.Mock() if has_event else None
        method = getattr(presenter, method_name)
        result = method(mock_script, mock_event, debugging_enabled)

        if has_event and debugging_enabled:
            essential_modules["settings_instance"].get_setting.assert_called_with(setting_key)
            essential_modules["orca.debug"].print_tokens.assert_called_once()

        mock_strftime.assert_called_once_with(format_string, mock_time_tuple)
        mock_script.present_message.assert_called_once_with(expected_output)
        assert result

    @pytest.mark.parametrize(
        "psutil_available,has_battery,power_plugged,expected_message",
        [
            (True, True, True, "Battery: 85% plugged in"),
            (True, True, False, "Battery: 85% not plugged in"),
            (True, False, None, "Battery status unknown"),
            (False, None, None, "Battery status unknown"),
        ],
    )
    def test_present_battery_status(
        self,
        test_context: OrcaTestContext,
        psutil_available: bool,
        has_battery: bool | None,
        power_plugged: bool | None,
        expected_message: str,
    ) -> None:
        """Test SystemInformationPresenter.present_battery_status with different scenarios."""
        if (
            not psutil_available
            and "orca.system_information_presenter" in __import__("sys").modules
        ):
            del __import__("sys").modules["orca.system_information_presenter"]

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()

        if psutil_available:
            test_context.patch(
                "orca.system_information_presenter._PSUTIL_AVAILABLE", new=True
            )
            if has_battery:
                if power_plugged is not None:
                    essential_modules["battery"].power_plugged = power_plugged
            else:
                essential_modules["psutil"].sensors_battery.return_value = None
        else:
            psutil_mock = essential_modules["psutil"]
            psutil_mock.sensors_battery.return_value = None

        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        mock_event = test_context.Mock()
        result = presenter.present_battery_status(mock_script, mock_event, True)

        mock_script.present_message.assert_called_once_with(expected_message)
        assert result

    @pytest.mark.parametrize(
        "psutil_available,memory_size,expected_message,check_debug",
        [
            (True, "gb", "CPU: 46%. Memory: 67%. 5.2GB / 16GB", False),
            (True, "mb", "CPU: 46%. Memory: 67%. 512MB / 1024MB", False),
            (False, None, "CPU and memory usage unknown", True),
        ],
    )
    def test_present_cpu_and_memory_usage(
        self,
        test_context: OrcaTestContext,
        psutil_available: bool,
        memory_size: str | None,
        expected_message: str,
        check_debug: bool,
    ) -> None:
        """Test SystemInformationPresenter.present_cpu_and_memory_usage with different scenarios."""
        if not psutil_available:
            if "orca.system_information_presenter" in __import__("sys").modules:
                del __import__("sys").modules["orca.system_information_presenter"]
            import sys

            if "psutil" in sys.modules:
                del sys.modules["psutil"]
            import builtins

            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == "psutil":
                    raise ModuleNotFoundError("No module named 'psutil'")
                return original_import(name, *args, **kwargs)

            test_context.patch("builtins.__import__", side_effect=mock_import)
            essential_modules = test_context.setup_shared_dependencies([])
            mock_script = test_context.Mock()
            mock_script.present_message = test_context.Mock()
            messages_mock = essential_modules["orca.messages"]
            messages_mock.CPU_AND_MEMORY_USAGE_UNKNOWN = "CPU and memory usage unknown"
        else:
            essential_modules = self._setup_dependencies(test_context)
            mock_script = test_context.Mock()
            mock_script.present_message = test_context.Mock()
            if memory_size == "mb":
                essential_modules["memory"].total = 512 * 1024**2
                essential_modules["memory"].used = 256 * 1024**2
            test_context.patch(
                "orca.system_information_presenter._PSUTIL_AVAILABLE", new=True
            )

        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        mock_event = test_context.Mock()
        result = presenter.present_cpu_and_memory_usage(mock_script, mock_event, True)

        if psutil_available:
            essential_modules["psutil"].cpu_percent.assert_called_once()
            essential_modules["psutil"].virtual_memory.assert_called_once()
            if memory_size == "gb":
                essential_modules["orca.messages"].memory_usage_gb.assert_called_once()
            elif memory_size == "mb":
                essential_modules["orca.messages"].memory_usage_mb.assert_called_once()

        mock_script.present_message.assert_called_once_with(expected_message)
        assert result

        if check_debug:
            essential_modules["orca.debug"].print_tokens.assert_called_once()

    def test_get_presenter_singleton(self, test_context: OrcaTestContext) -> None:
        """Test system_information_presenter.get_presenter singleton functionality."""

        self._setup_dependencies(test_context)
        test_context.patch(
            "orca.system_information_presenter._PSUTIL_AVAILABLE", new=True
        )
        from orca.system_information_presenter import get_presenter

        presenter1 = get_presenter()
        presenter2 = get_presenter()

        assert presenter1 is presenter2
        assert presenter1.__class__.__name__ == "SystemInformationPresenter"

    def test_module_level_psutil_detection(self, test_context: OrcaTestContext) -> None:
        """Test module-level psutil availability detection."""

        import sys

        if "orca.system_information_presenter" in sys.modules:
            del sys.modules["orca.system_information_presenter"]
        self._setup_dependencies(test_context)
        from orca.system_information_presenter import _PSUTIL_AVAILABLE

        assert _PSUTIL_AVAILABLE is True

        if "orca.system_information_presenter" in sys.modules:
            del sys.modules["orca.system_information_presenter"]

        if "psutil" in sys.modules:
            del sys.modules["psutil"]

        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "psutil":
                raise ModuleNotFoundError("No module named 'psutil'")
            return original_import(name, *args, **kwargs)

        test_context.patch("builtins.__import__", side_effect=mock_import)

        test_context.setup_shared_dependencies([])

        import orca.system_information_presenter as presenter_module

        assert presenter_module._PSUTIL_AVAILABLE is False

    @pytest.mark.parametrize(
        "format_value,expected_name",
        [
            ("%x", "locale"),
            ("%d/%m/%Y", "numbers_dmy"),
            ("%m/%d/%Y", "numbers_mdy"),
            ("%A, %-d %B", "full_dm"),
            ("%A, %B %-d", "full_md"),
            ("%a, %-d %b, %Y", "abbreviated_dmy"),
        ],
    )
    def test_get_date_format(
        self, test_context: OrcaTestContext, format_value: str, expected_name: str
    ) -> None:
        """Test SystemInformationPresenter.get_date_format returns correct enum name."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules["settings_instance"].get_setting = test_context.Mock(
            return_value=format_value
        )

        test_context.patch(
            "orca.system_information_presenter.dbus_service.getter",
            new=lambda func: func
        )

        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        result = presenter.get_date_format()

        assert result == expected_name
        essential_modules["settings_instance"].get_setting.assert_called_with("presentDateFormat")

    @pytest.mark.parametrize(
        "format_name,expected_success,expected_value",
        [
            ("locale", True, "%x"),
            ("LOCALE", True, "%x"),
            ("numbers_dmy", True, "%d/%m/%Y"),
            ("full_md", True, "%A, %B %-d"),
            ("abbreviated_ymd", True, "%Y. %b %-d, %a"),
            ("invalid_format", False, None),
        ],
    )
    def test_set_date_format(
        self,
        test_context: OrcaTestContext,
        format_name: str,
        expected_success: bool,
        expected_value: str | None,
    ) -> None:
        """Test SystemInformationPresenter.set_date_format validates and sets format."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules["settings_instance"].set_setting = test_context.Mock()

        test_context.patch(
            "orca.system_information_presenter.dbus_service.setter",
            new=lambda func: func
        )

        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        result = presenter.set_date_format(format_name)

        assert result == expected_success

        if expected_success:
            essential_modules["settings_instance"].set_setting.assert_called_once_with(
                "presentDateFormat", expected_value
            )
            essential_modules["orca.debug"].print_message.assert_any_call(
                800, f"SYSTEM INFORMATION PRESENTER: Setting date format to {format_name}.", True
            )
        else:
            essential_modules["settings_instance"].set_setting.assert_not_called()
            debug_mock = essential_modules["orca.debug"].print_message
            assert any(
                call[0][1] == f"SYSTEM INFORMATION PRESENTER: Invalid date format: {format_name}"
                for call in debug_mock.call_args_list
            )

    @pytest.mark.parametrize(
        "format_value,expected_name",
        [
            ("%X", "locale"),
            ("%I:%M %p", "twelve_hm"),
            ("%I:%M:%S %p", "twelve_hms"),
            ("%H:%M", "twentyfour_hm"),
            ("%H:%M:%S", "twentyfour_hms"),
        ],
    )
    def test_get_time_format(
        self, test_context: OrcaTestContext, format_value: str, expected_name: str
    ) -> None:
        """Test SystemInformationPresenter.get_time_format returns correct enum name."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules["settings_instance"].get_setting = test_context.Mock(
            return_value=format_value
        )

        test_context.patch(
            "orca.system_information_presenter.dbus_service.getter",
            new=lambda func: func
        )

        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        result = presenter.get_time_format()

        assert result == expected_name
        essential_modules["settings_instance"].get_setting.assert_called_with("presentTimeFormat")

    @pytest.mark.parametrize(
        "format_name,expected_success,expected_value",
        [
            ("locale", True, "%X"),
            ("LOCALE", True, "%X"),
            ("twelve_hm", True, "%I:%M %p"),
            ("twentyfour_hms", True, "%H:%M:%S"),
            ("twentyfour_hm_with_words", True, "%H hours and %M minutes"),
            ("invalid_format", False, None),
        ],
    )
    def test_set_time_format(
        self,
        test_context: OrcaTestContext,
        format_name: str,
        expected_success: bool,
        expected_value: str | None,
    ) -> None:
        """Test SystemInformationPresenter.set_time_format validates and sets format."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules["settings_instance"].set_setting = test_context.Mock()

        test_context.patch(
            "orca.system_information_presenter.dbus_service.setter",
            new=lambda func: func
        )

        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        result = presenter.set_time_format(format_name)

        assert result == expected_success

        if expected_success:
            essential_modules["settings_instance"].set_setting.assert_called_once_with(
                "presentTimeFormat", expected_value
            )
            essential_modules["orca.debug"].print_message.assert_any_call(
                800, f"SYSTEM INFORMATION PRESENTER: Setting time format to {format_name}.", True
            )
        else:
            essential_modules["settings_instance"].set_setting.assert_not_called()
            debug_mock = essential_modules["orca.debug"].print_message
            assert any(
                call[0][1] == f"SYSTEM INFORMATION PRESENTER: Invalid time format: {format_name}"
                for call in debug_mock.call_args_list
            )

    def test_get_available_date_formats(self, test_context: OrcaTestContext) -> None:
        """Test SystemInformationPresenter.get_available_date_formats returns all format names."""

        self._setup_dependencies(test_context)

        test_context.patch(
            "orca.system_information_presenter.dbus_service.getter",
            new=lambda func: func
        )

        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        result = presenter.get_available_date_formats()

        assert isinstance(result, list)
        assert len(result) == 16
        assert "locale" in result
        assert "numbers_dmy" in result
        assert "full_md" in result
        assert "abbreviated_ymd" in result

    def test_get_available_time_formats(self, test_context: OrcaTestContext) -> None:
        """Test SystemInformationPresenter.get_available_time_formats returns all format names."""

        self._setup_dependencies(test_context)

        test_context.patch(
            "orca.system_information_presenter.dbus_service.getter",
            new=lambda func: func
        )

        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        result = presenter.get_available_time_formats()

        assert isinstance(result, list)
        assert len(result) == 7
        assert "locale" in result
        assert "twelve_hm" in result
        assert "twentyfour_hms" in result
        assert "twentyfour_hm_with_words" in result

    def test_internal_get_date_format_string(self, test_context: OrcaTestContext) -> None:
        """Test SystemInformationPresenter._get_date_format_string returns raw format."""

        essential_modules = self._setup_dependencies(test_context)
        expected_format = "%A, %B %-d"
        essential_modules["settings_instance"].get_setting = test_context.Mock(
            return_value=expected_format
        )

        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        result = presenter._get_date_format_string()

        assert result == expected_format
        essential_modules["settings_instance"].get_setting.assert_called_with("presentDateFormat")

    def test_internal_get_time_format_string(self, test_context: OrcaTestContext) -> None:
        """Test SystemInformationPresenter._get_time_format_string returns raw format."""

        essential_modules = self._setup_dependencies(test_context)
        expected_format = "%I:%M %p"
        essential_modules["settings_instance"].get_setting = test_context.Mock(
            return_value=expected_format
        )

        from orca.system_information_presenter import SystemInformationPresenter

        presenter = SystemInformationPresenter()
        result = presenter._get_time_format_string()

        assert result == expected_format
        essential_modules["settings_instance"].get_setting.assert_called_with("presentTimeFormat")
