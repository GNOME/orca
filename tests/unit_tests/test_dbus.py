# Orca
#
# Copyright 2025 Valve Corporation
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

# pylint: disable=unused-argument
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Unit tests for D-Bus functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

@pytest.mark.unit
class TestDBusDecorators:
    """Test D-Bus decorators and related functionality."""

    def test_command_decorator(self, mock_dbus_service: ModuleType) -> None:
        """Test command decorator."""

        @mock_dbus_service.command
        def test_function(script=None, event=None, notify_user=False):
            """Test command function."""
            return True

        assert hasattr(test_function, "dbus_command_description")
        assert test_function.dbus_command_description == "Test command function."

    def test_command_decorator_without_docstring(self, mock_dbus_service: ModuleType) -> None:
        """Test command decorator without docstring."""

        @mock_dbus_service.command
        def test_function_no_doc(script=None, event=None, notify_user=False):
            return True

        assert hasattr(test_function_no_doc, "dbus_command_description")
        assert (test_function_no_doc.dbus_command_description ==
                "D-Bus command: test_function_no_doc")

    def test_parameterized_command_decorator(self, mock_dbus_service: ModuleType) -> None:
        """Test parameterized_command decorator."""

        @mock_dbus_service.parameterized_command
        def test_function(script=None, event=None, language="", variant="", notify_user=False):
            """Get voices for language."""
            return [("voice1", language, variant)]

        assert hasattr(test_function, "dbus_parameterized_command_description")
        assert test_function.dbus_parameterized_command_description == "Get voices for language."

    def test_getter_decorator(self, mock_dbus_service: ModuleType) -> None:
        """Test getter decorator."""

        @mock_dbus_service.getter
        def get_rate():
            """Returns the current speech rate."""
            return 50

        assert hasattr(get_rate, "dbus_getter_description")
        assert get_rate.dbus_getter_description == "Returns the current speech rate."

    def test_setter_decorator(self, mock_dbus_service: ModuleType) -> None:
        """Test setter decorator."""

        @mock_dbus_service.setter
        def set_rate(value):
            """Sets the current speech rate."""
            return True

        assert hasattr(set_rate, "dbus_setter_description")
        assert set_rate.dbus_setter_description == "Sets the current speech rate."

    def test_multiple_decorators_on_module(self, mock_dbus_service: ModuleType) -> None:
        """Test multiple decorators on module."""

        class MockModule:
            """Mock module for testing multiple decorators."""
            @mock_dbus_service.command
            def toggle_speech(self, notify_user=False):
                """Toggle speech on/off."""
                return True

            @mock_dbus_service.parameterized_command
            def get_voices_for_language(self, language="", variant="", notify_user=False):
                """Get voices for language."""
                return []

            @mock_dbus_service.getter
            def get_rate(self):
                """Get speech rate."""
                return 50

            @mock_dbus_service.setter
            def set_rate(self, value):
                """Set speech rate."""
                return True

        mock_module = MockModule()
        assert hasattr(mock_module.toggle_speech, "dbus_command_description")
        assert hasattr(mock_module.get_voices_for_language,
                       "dbus_parameterized_command_description")
        assert hasattr(mock_module.get_rate, "dbus_getter_description")
        assert hasattr(mock_module.set_rate, "dbus_setter_description")

    def test_decorated_functions_remain_callable(self, mock_dbus_service: ModuleType) -> None:
        """Test decorated functions remain callable."""

        @mock_dbus_service.parameterized_command
        def test_command(param1="default", notify_user=False):
            """Test parameterized command."""
            return f"param1={param1}, notify_user={notify_user}"

        assert hasattr(test_command, "dbus_parameterized_command_description")

        result = test_command(param1="test_value", notify_user=True)
        assert "param1=test_value" in result
        assert "notify_user=True" in result

@pytest.mark.unit
class TestHandlerInfo:
    """Test _HandlerInfo class functionality."""

    def test_handler_info_creation(self, mock_dbus_service: ModuleType) -> None:
        """Test _HandlerInfo creation."""

        def test_action():
            return True

        info = mock_dbus_service._HandlerInfo(
            python_function_name="test_function",
            description="Test function",
            action=test_action,
            handler_type=mock_dbus_service.HandlerType.COMMAND
        )

        assert info.python_function_name == "test_function"
        assert info.description == "Test function"
        assert info.action is test_action
        assert info.handler_type == mock_dbus_service.HandlerType.COMMAND

    def test_handler_info_default_type(self, mock_dbus_service: ModuleType) -> None:
        """Test _HandlerInfo default type."""

        def test_action():
            return True

        info = mock_dbus_service._HandlerInfo(
            python_function_name="test_function",
            description="Test function",
            action=test_action
        )

        assert info.handler_type == mock_dbus_service.HandlerType.COMMAND

@pytest.mark.unit
class TestHelperFunctions:
    """Test helper functions from dbus_service module."""

    def test_extract_function_parameters_basic(self, mock_dbus_service: ModuleType) -> None:
        """Test _extract_function_parameters basic types."""

        def test_func(self, param1: str, param2: int, param3: bool) -> None:
            pass

        params = mock_dbus_service._extract_function_parameters(test_func)
        expected = [("param1", "str"), ("param2", "int"), ("param3", "bool")]
        assert params == expected

    def test_extract_function_parameters_skips_standard_params(
        self, mock_dbus_service: ModuleType
    ) -> None:
        """Test _extract_function_parameters skips standard params."""

        def test_func(self, script=None, event=None, param1: str = "test") -> None:
            pass

        params = mock_dbus_service._extract_function_parameters(test_func)
        expected = [("param1", "str")]
        assert params == expected

    def test_extract_function_parameters_no_annotations(
        self, mock_dbus_service: ModuleType
    ) -> None:
        """Test _extract_function_parameters no annotations."""

        def test_func(self, param1, param2) -> None:
            pass

        params = mock_dbus_service._extract_function_parameters(test_func)
        expected = [("param1", "Any"), ("param2", "Any")]
        assert params == expected

    def test_extract_function_parameters_mixed_annotations(
        self, mock_dbus_service: ModuleType
    ) -> None:
        """Test _extract_function_parameters mixed annotations."""

        def test_func(self, param1: str, param2, param3: bool) -> None:
            pass

        params = mock_dbus_service._extract_function_parameters(test_func)
        expected = [("param1", "str"), ("param2", "Any"), ("param3", "bool")]
        assert params == expected

    def test_extract_function_parameters_complex_types(self, mock_dbus_service: ModuleType) -> None:
        """Test _extract_function_parameters complex types."""

        def test_func(self, param1: list[str], param2: dict[str, int]) -> None:
            pass

        params = mock_dbus_service._extract_function_parameters(test_func)
        # Complex types are converted to string representation
        assert len(params) == 2
        assert params[0][0] == "param1"
        assert params[1][0] == "param2"
        # Type strings will vary based on Python version, just ensure they're not "Any"
        assert params[0][1] != "Any"
        assert params[1][1] != "Any"

@pytest.mark.unit
class TestOrcaModuleDBusInterface:
    """Test OrcaModuleDBusInterface methods."""

    @pytest.mark.parametrize(
        "input_name, handler_type, expected_result",
        [
            pytest.param("toggle_speech", "COMMAND", "ToggleSpeech", id="command"),
            pytest.param("get_speech_rate", "GETTER", "SpeechRate", id="getter_with_prefix"),
            pytest.param("set_speech_rate", "SETTER", "SpeechRate", id="setter_with_prefix"),
            pytest.param("speech_rate", "GETTER", "SpeechRate", id="getter_without_prefix"),
            pytest.param("speech_rate", "SETTER", "SpeechRate", id="setter_without_prefix"),
        ],
    )
    def test_normalize_handler_name(
        self, mock_dbus_service: ModuleType, input_name, handler_type, expected_result
    ) -> None:
        """Test OrcaModuleDBusInterface._normalize_handler_name."""

        handler_type_obj = getattr(mock_dbus_service.HandlerType, handler_type)
        result = mock_dbus_service.OrcaModuleDBusInterface._normalize_handler_name(
            input_name, handler_type_obj
        )
        assert result == expected_result

    @pytest.mark.parametrize(
        "input_value, expected_type, expected_output",
        [
            pytest.param(True, "b", True, id="bool_true"),
            pytest.param(False, "b", False, id="bool_false"),
            pytest.param(42, "i", 42, id="integer"),
            pytest.param(3.14, "d", 3.14, id="float"),
            pytest.param("test", "s", "test", id="string"),
        ],
    )
    def test_to_variant_basic_types(
        self, mock_dbus_service: ModuleType, input_value, expected_type, expected_output
    ) -> None:
        """Test OrcaModuleDBusInterface._to_variant with basic types."""

        variant = mock_dbus_service.OrcaModuleDBusInterface._to_variant(input_value)
        assert variant.get_type_string() == expected_type
        assert variant.unpack() == expected_output

    @pytest.mark.parametrize(
        "input_list, expected_type",
        [
            pytest.param(["hello", "world"], "as", id="list_strings"),
            pytest.param([1, 2, 3], "ax", id="list_ints"),
            pytest.param([True, False, True], "ab", id="list_bools"),
            pytest.param([2, 3, 4], "ax", id="list_ints_not_bools"),
            pytest.param([], "as", id="empty_list"),
        ],
    )
    def test_to_variant_lists(
        self, mock_dbus_service: ModuleType, input_list, expected_type
    ) -> None:
        """Test OrcaModuleDBusInterface._to_variant with various list types."""

        variant = mock_dbus_service.OrcaModuleDBusInterface._to_variant(input_list)
        assert variant.get_type_string() == expected_type
        assert variant.unpack() == input_list

    def test_to_variant_list_tuples(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface._to_variant list tuples."""

        test_list = [("voice1", "en", "US"), ("voice2", "es", "ES")]
        variant = mock_dbus_service.OrcaModuleDBusInterface._to_variant(test_list)
        assert variant.get_type_string() == "a(sss)"
        expected = [("voice1", "en", "US"), ("voice2", "es", "ES")]
        assert variant.unpack() == expected


    def test_to_variant_dict(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface._to_variant dict."""

        test_dict = {"key1": "value1", "key2": "value2"}
        variant = mock_dbus_service.OrcaModuleDBusInterface._to_variant(test_dict)
        assert variant.get_type_string() == "a{sv}"
        unpacked = variant.unpack()
        assert "key1" in unpacked
        assert "key2" in unpacked

    def test_to_variant_none(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface._to_variant None."""

        variant = mock_dbus_service.OrcaModuleDBusInterface._to_variant(None)
        assert variant.get_type_string() == "v"
        inner = variant.unpack()
        assert inner.unpack() == ""

    def test_to_variant_unknown_type(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface._to_variant unknown type."""

        class CustomObject:
            """Test class for unknown type conversion."""
            def __str__(self):
                return "custom_object"

        obj = CustomObject()
        variant = mock_dbus_service.OrcaModuleDBusInterface._to_variant(obj)
        assert variant.get_type_string() == "s"
        assert variant.unpack() == "custom_object"


@pytest.mark.unit
class TestOrcaModuleDBusInterfaceExecution:
    """Test OrcaModuleDBusInterface execution methods."""

    def test_execute_runtime_getter_success(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ExecuteRuntimeGetter success."""

        def mock_getter_action():
            return 42

        mock_info = mock_dbus_service._HandlerInfo(
            python_function_name="get_test_value",
            description="Get test value",
            action=mock_getter_action,
            handler_type=mock_dbus_service.HandlerType.GETTER
        )

        handlers = [mock_info]
        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        result = interface.ExecuteRuntimeGetter("TestValue")
        assert result.get_type_string() == "i"
        assert result.unpack() == 42

    def test_execute_runtime_getter_unknown(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ExecuteRuntimeGetter unknown."""

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [])
        result = interface.ExecuteRuntimeGetter("UnknownGetter")
        assert result.get_type_string() == "v"
        inner = result.unpack()
        assert inner.get_type_string() == "s"
        assert inner.unpack() == ""

    @pytest.mark.parametrize(
        "func_name, action, expected_type, expected_value",
        [
            pytest.param("get_string", lambda: "hello", "s", "hello", id="string_type"),
            pytest.param("get_bool", lambda: True, "b", True, id="bool_type"),
            pytest.param("get_list", lambda: ["a", "b"], "as", ["a", "b"], id="list_type"),
            pytest.param("get_none", lambda: None, "v", "", id="none_type"),
        ],
    )
    def test_execute_runtime_getter_various_types(
        self, mock_dbus_service: ModuleType, func_name, action, expected_type, expected_value
    ) -> None:
        """Test OrcaModuleDBusInterface.ExecuteRuntimeGetter various types."""

        mock_info = mock_dbus_service._HandlerInfo(
            python_function_name=func_name,
            description=f"Test {func_name}",
            action=action,
            handler_type=mock_dbus_service.HandlerType.GETTER
        )

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [mock_info])
        normalized_name = func_name[4:].replace("_", " ").title().replace(" ", "")
        result = interface.ExecuteRuntimeGetter(normalized_name)
        assert result.get_type_string() == expected_type

        if expected_type == "v":
            inner = result.unpack()
            assert inner.unpack() == expected_value
        else:
            assert result.unpack() == expected_value

    def test_execute_runtime_setter_success(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ExecuteRuntimeSetter success."""

        test_state = {"setter_called": False, "setter_value": None}

        def mock_setter_action(value):
            test_state["setter_called"] = True
            test_state["setter_value"] = value
            return True

        mock_info = mock_dbus_service._HandlerInfo(
            python_function_name="set_test_value",
            description="Set test value",
            action=mock_setter_action,
            handler_type=mock_dbus_service.HandlerType.SETTER
        )

        handlers = [mock_info]
        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        mock_variant = mock_dbus_service.GLib.Variant("i", 99)
        result = interface.ExecuteRuntimeSetter("TestValue", mock_variant)
        assert result is True
        assert test_state["setter_called"]
        assert test_state["setter_value"] == 99

    def test_execute_runtime_setter_unknown(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ExecuteRuntimeSetter unknown."""

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [])
        mock_variant = mock_dbus_service.GLib.Variant("i", 99)
        result = interface.ExecuteRuntimeSetter("UnknownSetter", mock_variant)
        assert result is False

    def test_execute_runtime_setter_failure(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ExecuteRuntimeSetter failure."""

        def mock_setter_action(value):
            return False

        mock_info = mock_dbus_service._HandlerInfo(
            python_function_name="set_test_value",
            description="Set test value",
            action=mock_setter_action,
            handler_type=mock_dbus_service.HandlerType.SETTER
        )

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [mock_info])
        mock_variant = mock_dbus_service.GLib.Variant("s", "test")
        result = interface.ExecuteRuntimeSetter("TestValue", mock_variant)
        assert result is False

    def test_execute_command_success(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ExecuteCommand success."""

        test_state = {"command_called": False, "notify_value": None}

        def mock_command_action(notify_user):
            test_state["command_called"] = True
            test_state["notify_value"] = notify_user
            return True

        mock_info = mock_dbus_service._HandlerInfo(
            python_function_name="test_command",
            description="Test command",
            action=mock_command_action,
            handler_type=mock_dbus_service.HandlerType.COMMAND
        )

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [mock_info])
        result = interface.ExecuteCommand("TestCommand", True)
        assert result is True
        assert test_state["command_called"]
        assert test_state["notify_value"] is True

    def test_execute_command_unknown(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ExecuteCommand unknown."""

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [])
        result = interface.ExecuteCommand("UnknownCommand", False)
        assert result is False

    def test_execute_command_failure(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ExecuteCommand failure."""

        def mock_command_action(notify_user):
            return False

        mock_info = mock_dbus_service._HandlerInfo(
            python_function_name="failing_command",
            description="Failing command",
            action=mock_command_action,
            handler_type=mock_dbus_service.HandlerType.COMMAND
        )

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [mock_info])
        result = interface.ExecuteCommand("FailingCommand", False)
        assert result is False

    def test_execute_parameterized_command_success(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ExecuteParameterizedCommand success."""

        test_state = {"param_command_called": False, "received_params": None}

        def mock_param_command(**kwargs):
            test_state["param_command_called"] = True
            test_state["received_params"] = kwargs
            return ["result1", "result2"]

        mock_info = mock_dbus_service._HandlerInfo(
            python_function_name="param_command",
            description="Parameterized command",
            action=mock_param_command,
            handler_type=mock_dbus_service.HandlerType.PARAMETERIZED_COMMAND,
            parameters=[("param1", "str"), ("param2", "int")]
        )

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [mock_info])
        params = {
            "param1": mock_dbus_service.GLib.Variant("s", "hello"),
            "param2": mock_dbus_service.GLib.Variant("i", 42)
        }
        result = interface.ExecuteParameterizedCommand("ParamCommand", params, True)
        assert test_state["param_command_called"]
        expected_params = {"param1": "hello", "param2": 42, "notify_user": True}
        assert test_state["received_params"] == expected_params
        assert result.get_type_string() == "as"
        assert result.unpack() == ["result1", "result2"]

    def test_execute_parameterized_command_unknown(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ExecuteParameterizedCommand unknown."""

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [])
        params = {"param1": mock_dbus_service.GLib.Variant("s", "test")}
        result = interface.ExecuteParameterizedCommand("UnknownCommand", params, False)
        assert result.get_type_string() == "b"
        assert result.unpack() is False

    def test_execute_parameterized_command_complex_result(
        self, mock_dbus_service: ModuleType
    ) -> None:
        """Test OrcaModuleDBusInterface.ExecuteParameterizedCommand complex result."""

        def mock_command(**kwargs):
            return [("voice1", "en", "US"), ("voice2", "es", "ES")]

        mock_info = mock_dbus_service._HandlerInfo(
            python_function_name="get_voices",
            description="Get voices",
            action=mock_command,
            handler_type=mock_dbus_service.HandlerType.PARAMETERIZED_COMMAND
        )

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [mock_info])
        params = {"language": mock_dbus_service.GLib.Variant("s", "en")}
        result = interface.ExecuteParameterizedCommand("GetVoices", params, False)
        assert result.get_type_string() == "a(sss)"
        assert result.unpack() == [("voice1", "en", "US"), ("voice2", "es", "ES")]

    def test_list_commands(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ListCommands."""

        handlers = [
            mock_dbus_service._HandlerInfo(
                python_function_name="command_one",
                description="First command",
                action=lambda x: True,
                handler_type=mock_dbus_service.HandlerType.COMMAND
            ),
            mock_dbus_service._HandlerInfo(
                python_function_name="command_two",
                description="Second command",
                action=lambda x: True,
                handler_type=mock_dbus_service.HandlerType.COMMAND
            ),
            mock_dbus_service._HandlerInfo(
                python_function_name="get_value",
                description="A getter",
                action=lambda: 42,
                handler_type=mock_dbus_service.HandlerType.GETTER
            ),
        ]

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        commands = interface.ListCommands()
        assert len(commands) == 2
        assert ("CommandOne", "First command") in commands
        assert ("CommandTwo", "Second command") in commands

    def test_list_runtime_getters(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ListRuntimeGetters."""

        handlers = [
            mock_dbus_service._HandlerInfo(
                python_function_name="get_rate",
                description="Get speech rate",
                action=lambda: 50,
                handler_type=mock_dbus_service.HandlerType.GETTER
            ),
            mock_dbus_service._HandlerInfo(
                python_function_name="get_pitch",
                description="Get speech pitch",
                action=lambda: 5,
                handler_type=mock_dbus_service.HandlerType.GETTER
            ),
        ]

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        getters = interface.ListRuntimeGetters()
        assert len(getters) == 2
        assert ("Rate", "Get speech rate") in getters
        assert ("Pitch", "Get speech pitch") in getters

    def test_list_runtime_setters(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ListRuntimeSetters."""

        handlers = [
            mock_dbus_service._HandlerInfo(
                python_function_name="set_rate",
                description="Set speech rate",
                action=lambda x: True,
                handler_type=mock_dbus_service.HandlerType.SETTER
            ),
            mock_dbus_service._HandlerInfo(
                python_function_name="set_pitch",
                description="Set speech pitch",
                action=lambda x: True,
                handler_type=mock_dbus_service.HandlerType.SETTER
            ),
        ]

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        setters = interface.ListRuntimeSetters()
        assert len(setters) == 2
        assert ("Rate", "Set speech rate") in setters
        assert ("Pitch", "Set speech pitch") in setters

    def test_list_parameterized_commands(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.ListParameterizedCommands."""

        handlers = [
            mock_dbus_service._HandlerInfo(
                python_function_name="get_voices_for_language",
                description="Get voices for language",
                action=lambda **kwargs: [],
                handler_type=mock_dbus_service.HandlerType.PARAMETERIZED_COMMAND,
                parameters=[("language", "str"), ("variant", "str")]
            ),
        ]

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        commands = interface.ListParameterizedCommands()
        assert len(commands) == 1
        assert commands[0][0] == "GetVoicesForLanguage"
        assert commands[0][1] == "Get voices for language"
        assert commands[0][2] == [("language", "str"), ("variant", "str")]


@pytest.mark.unit
class TestOrcaModuleDBusInterfaceConstructor:
    """Test OrcaModuleDBusInterface constructor and initialization."""

    def test_constructor_empty_handlers(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface constructor empty handlers."""

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [])
        assert interface._module_name == "TestModule"
        assert len(interface._commands) == 0
        assert len(interface._parameterized_commands) == 0
        assert len(interface._getters) == 0
        assert len(interface._setters) == 0

    def test_constructor_mixed_handlers(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface constructor mixed handlers."""

        handlers = [
            mock_dbus_service._HandlerInfo(
                python_function_name="toggle_something",
                description="Toggle something",
                action=lambda x: True,
                handler_type=mock_dbus_service.HandlerType.COMMAND
            ),
            mock_dbus_service._HandlerInfo(
                python_function_name="get_value",
                description="Get value",
                action=lambda: 42,
                handler_type=mock_dbus_service.HandlerType.GETTER
            ),
            mock_dbus_service._HandlerInfo(
                python_function_name="set_value",
                description="Set value",
                action=lambda x: True,
                handler_type=mock_dbus_service.HandlerType.SETTER
            ),
            mock_dbus_service._HandlerInfo(
                python_function_name="do_something_complex",
                description="Do something complex",
                action=lambda **kwargs: [],
                handler_type=mock_dbus_service.HandlerType.PARAMETERIZED_COMMAND,
                parameters=[("param", "str")]
            ),
        ]

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        assert interface._module_name == "TestModule"
        assert "ToggleSomething" in interface._commands
        assert "Value" in interface._getters
        assert "Value" in interface._setters
        assert "DoSomethingComplex" in interface._parameterized_commands

    def test_constructor_handler_without_type(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface constructor handler without type."""

        class MockHandlerInfo:
            """Mock handler info for testing."""
            def __init__(self):
                self.python_function_name = "test_command"
                self.description = "Test command"
                self.action = lambda x: True

        handler = MockHandlerInfo()
        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [handler])
        assert "TestCommand" in interface._commands

    def test_constructor_duplicate_names(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface constructor duplicate names."""

        handlers = [
            mock_dbus_service._HandlerInfo(
                python_function_name="test_command",
                description="First command",
                action=lambda x: "first",
                handler_type=mock_dbus_service.HandlerType.COMMAND
            ),
            mock_dbus_service._HandlerInfo(
                python_function_name="test_command",
                description="Second command",
                action=lambda x: "second",
                handler_type=mock_dbus_service.HandlerType.COMMAND
            ),
        ]

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        assert len(interface._commands) == 1
        assert interface._commands["TestCommand"].action(False) == "second"

    def test_for_publication(self, mock_dbus_service: ModuleType) -> None:
        """Test OrcaModuleDBusInterface.for_publication."""

        interface = mock_dbus_service.OrcaModuleDBusInterface("TestModule", [])
        interface.__dbus_xml__ = "<xml>test</xml>"
        result = interface.for_publication()
        assert result == "<xml>test</xml>"
