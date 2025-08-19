# Unit tests for dbus_service.py methods.
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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-public-methods
# pylint: disable=too-few-public-methods
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-lines

"""Unit tests for D-Bus functionality."""

from __future__ import annotations
from typing import TYPE_CHECKING
import re
import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

class _MockDBusError(Exception):
    def __init__(self, message="DBus error"):
        super().__init__(message)
        self.message = message

@pytest.mark.unit
class TestDBusService:
    """Test D-Bus service functionality."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for dbus_service dependencies."""

        external_modules = [
            "gi",
            "gi.repository",
            "dasbus",
            "dasbus.connection",
            "dasbus.error",
            "dasbus.loop",
            "dasbus.server.interface",
            "dasbus.server.publishable",
        ]

        internal_modules = [
            "orca.debug",
            "orca.input_event",
            "orca.input_event_manager",
            "orca.orca_platform",
            "orca.script_manager",
        ]

        all_modules = external_modules + internal_modules
        essential_modules = test_context._setup_essential_modules(all_modules)

        class MockGLibVariant:
            """Mock GLib.Variant for dasbus type handling."""

            def __init__(self, type_string: str, value):
                self._type_string = type_string
                self._value = value

            def get_type_string(self) -> str:
                """Return the GLib type string."""
                return self._type_string

            def unpack(self):
                """Unpack the variant value."""
                return self._value

        essential_modules["gi.repository"].GLib = test_context.Mock()
        essential_modules["gi.repository"].GLib.Variant = MockGLibVariant

        class MockPublishable:
            """Mock Publishable base class for inheritance."""

            def __init__(self, *args, **kwargs):
                pass

        essential_modules["dasbus.server.publishable"].Publishable = MockPublishable

        essential_modules["dasbus.error"].DBusError = _MockDBusError

        def mock_dbus_interface(_interface_name):
            def decorator(cls):
                return cls

            return decorator

        essential_modules["dasbus.server.interface"].dbus_interface = mock_dbus_interface

        essential_modules["orca.debug"].LEVEL_INFO = 800
        essential_modules["orca.debug"].println = test_context.Mock()

        essential_modules["orca.orca_platform"].version = "test-version"


        return essential_modules

    def _get_mock_dbus_error(self) -> type[Exception]:
        return _MockDBusError

    def test_command_decorator(self, test_context: OrcaTestContext) -> None:
        """Test command decorator."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.command
        def test_function(script=None, event=None, notify_user=False) -> bool:  # pylint: disable=unused-argument
            """Test command function."""

            return True

        assert hasattr(test_function, "dbus_command_description")
        assert test_function.dbus_command_description == "Test command function."

    def test_command_decorator_without_docstring(self, test_context: OrcaTestContext) -> None:
        """Test command decorator without docstring."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.command
        def test_function_no_doc(script=None, event=None, notify_user=False) -> bool:  # pylint: disable=unused-argument
            return True

        assert hasattr(test_function_no_doc, "dbus_command_description")
        assert (
            test_function_no_doc.dbus_command_description == "D-Bus command: test_function_no_doc"
        )

    def test_parameterized_command_decorator(self, test_context: OrcaTestContext) -> None:
        """Test parameterized_command decorator."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.parameterized_command
        def test_function(
            script=None,  # pylint: disable=unused-argument
            event=None,  # pylint: disable=unused-argument
            language="",  # pylint: disable=unused-argument
            variant="",  # pylint: disable=unused-argument
            notify_user=False,  # pylint: disable=unused-argument
        ) -> list[tuple[str, str, str]]:
            """Get voices for language."""

            return [("voice1", language, variant)]

        assert hasattr(test_function, "dbus_parameterized_command_description")
        assert test_function.dbus_parameterized_command_description == "Get voices for language."

    def test_getter_decorator(self, test_context: OrcaTestContext) -> None:
        """Test getter decorator."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.getter
        def get_rate() -> int:
            """Returns the current speech rate."""

            return 50

        assert hasattr(get_rate, "dbus_getter_description")
        assert get_rate.dbus_getter_description == "Returns the current speech rate."

    def test_setter_decorator(self, test_context: OrcaTestContext) -> None:
        """Test setter decorator."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.setter
        def set_rate(_value) -> bool:
            """Sets the current speech rate."""

            return True

        assert hasattr(set_rate, "dbus_setter_description")
        assert set_rate.dbus_setter_description == "Sets the current speech rate."

    def test_multiple_decorators_on_module(self, test_context: OrcaTestContext) -> None:
        """Test multiple decorators on module."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        class MockModule:
            """Mock module for testing multiple decorators."""

            @dbus_service.command
            def toggle_speech(self, notify_user=False) -> bool:  # pylint: disable=unused-argument
                """Toggle speech on/off."""

                return True

            @dbus_service.parameterized_command
            def get_voices_for_language(
                self,
                language="",  # pylint: disable=unused-argument
                variant="",  # pylint: disable=unused-argument
                notify_user=False,  # pylint: disable=unused-argument
            ) -> list:
                """Get voices for language."""

                return []

            @dbus_service.getter
            def get_rate(self) -> int:
                """Get speech rate."""

                return 50

            @dbus_service.setter
            def set_rate(self, _value) -> bool:
                """Set speech rate."""

                return True

        mock_module = MockModule()
        assert hasattr(mock_module.toggle_speech, "dbus_command_description")
        assert hasattr(
            mock_module.get_voices_for_language, "dbus_parameterized_command_description"
        )
        assert hasattr(mock_module.get_rate, "dbus_getter_description")
        assert hasattr(mock_module.set_rate, "dbus_setter_description")

    def test_decorated_functions_remain_callable(self, test_context: OrcaTestContext) -> None:
        """Test decorated functions remain callable."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.parameterized_command
        def test_command(param1="default", notify_user=False) -> str:
            """Test parameterized command."""

            return f"param1={param1}, notify_user={notify_user}"

        assert hasattr(test_command, "dbus_parameterized_command_description")
        result = test_command(param1="test_value", notify_user=True)
        assert "param1=test_value" in result
        assert "notify_user=True" in result

    def test_handler_info_creation(self, test_context: OrcaTestContext) -> None:
        """Test _HandlerInfo creation."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        def test_action() -> bool:
            return True

        info = dbus_service._HandlerInfo(
            python_function_name="test_function",
            description="Test function",
            action=test_action,
            handler_type=dbus_service.HandlerType.COMMAND,
        )
        assert info.python_function_name == "test_function"
        assert info.description == "Test function"
        assert info.action is test_action
        assert info.handler_type == dbus_service.HandlerType.COMMAND

    def test_handler_info_default_type(self, test_context: OrcaTestContext) -> None:
        """Test _HandlerInfo default type."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        def test_action() -> bool:
            return True

        info = dbus_service._HandlerInfo(
            python_function_name="test_function", description="Test function", action=test_action
        )
        assert info.handler_type == dbus_service.HandlerType.COMMAND

    def test_extract_function_parameters_basic(self, test_context: OrcaTestContext) -> None:
        """Test _extract_function_parameters basic types."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        def test_func(self, param1: str, param2: int, param3: bool) -> None:  # pylint: disable=unused-argument
            pass

        params = dbus_service._extract_function_parameters(test_func)
        expected = [("param1", "str"), ("param2", "int"), ("param3", "bool")]
        assert params == expected

    def test_extract_function_parameters_skips_standard_params(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _extract_function_parameters skips standard params."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        def test_func(self, script=None, event=None, param1: str = "test") -> None:  # pylint: disable=unused-argument
            pass

        params = dbus_service._extract_function_parameters(test_func)
        expected = [("param1", "str")]
        assert params == expected

    def test_extract_function_parameters_no_annotations(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _extract_function_parameters no annotations."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        def test_func(self, param1, param2) -> None:  # pylint: disable=unused-argument
            pass

        params = dbus_service._extract_function_parameters(test_func)
        expected = [("param1", "Any"), ("param2", "Any")]
        assert params == expected

    def test_extract_function_parameters_mixed_annotations(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _extract_function_parameters mixed annotations."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        def test_func(self, param1: str, param2, param3: bool) -> None:  # pylint: disable=unused-argument
            pass

        params = dbus_service._extract_function_parameters(test_func)
        expected = [("param1", "str"), ("param2", "Any"), ("param3", "bool")]
        assert params == expected

    def test_extract_function_parameters_complex_types(self, test_context: OrcaTestContext) -> None:
        """Test _extract_function_parameters complex types."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        def test_func(self, param1: list[str], param2: dict[str, int]) -> None:  # pylint: disable=unused-argument
            pass

        params = dbus_service._extract_function_parameters(test_func)
        assert len(params) == 2
        assert params[0][0] == "param1"
        assert params[1][0] == "param2"
        assert params[0][1] != "Any"
        assert params[1][1] != "Any"

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "command",
                "input_name": "toggle_speech",
                "handler_type": "COMMAND",
                "expected_result": "ToggleSpeech",
            },
            {
                "id": "getter_with_prefix",
                "input_name": "get_speech_rate",
                "handler_type": "GETTER",
                "expected_result": "SpeechRate",
            },
            {
                "id": "setter_with_prefix",
                "input_name": "set_speech_rate",
                "handler_type": "SETTER",
                "expected_result": "SpeechRate",
            },
            {
                "id": "getter_without_prefix",
                "input_name": "speech_rate",
                "handler_type": "GETTER",
                "expected_result": "SpeechRate",
            },
            {
                "id": "setter_without_prefix",
                "input_name": "speech_rate",
                "handler_type": "SETTER",
                "expected_result": "SpeechRate",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_normalize_handler_name(self, test_context, case: dict) -> None:
        """Test OrcaModuleDBusInterface._normalize_handler_name."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        handler_type_obj = getattr(dbus_service.HandlerType, case["handler_type"])
        result = dbus_service.OrcaModuleDBusInterface._normalize_handler_name(
            case["input_name"], handler_type_obj
        )
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "bool_true", "input_value": True, "expected_type": "b", "expected_output": True},
            {
                "id": "bool_false",
                "input_value": False,
                "expected_type": "b",
                "expected_output": False,
            },
            {"id": "integer", "input_value": 42, "expected_type": "i", "expected_output": 42},
            {"id": "float", "input_value": 3.14, "expected_type": "d", "expected_output": 3.14},
            {
                "id": "string",
                "input_value": "test",
                "expected_type": "s",
                "expected_output": "test",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_to_variant_basic_types(self, test_context, case: dict) -> None:
        """Test OrcaModuleDBusInterface._to_variant with basic types."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        variant = dbus_service.OrcaModuleDBusInterface._to_variant(case["input_value"])
        assert variant.get_type_string() == case["expected_type"]
        assert variant.unpack() == case["expected_output"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "list_strings", "input_list": ["hello", "world"], "expected_type": "as"},
            {"id": "list_ints", "input_list": [1, 2, 3], "expected_type": "ax"},
            {"id": "list_bools", "input_list": [True, False, True], "expected_type": "ab"},
            {"id": "list_ints_not_bools", "input_list": [2, 3, 4], "expected_type": "ax"},
            {"id": "empty_list", "input_list": [], "expected_type": "as"},
        ],
        ids=lambda case: case["id"],
    )
    def test_to_variant_lists(self, test_context, case: dict) -> None:
        """Test OrcaModuleDBusInterface._to_variant with various list types."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        variant = dbus_service.OrcaModuleDBusInterface._to_variant(case["input_list"])
        assert variant.get_type_string() == case["expected_type"]
        assert variant.unpack() == case["input_list"]

    def test_to_variant_list_tuples(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface._to_variant list tuples."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        test_list = [("voice1", "en", "US"), ("voice2", "es", "ES")]
        variant = dbus_service.OrcaModuleDBusInterface._to_variant(test_list)
        assert variant.get_type_string() == "a(sss)"
        expected = [("voice1", "en", "US"), ("voice2", "es", "ES")]
        assert variant.unpack() == expected

    def test_to_variant_dict(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface._to_variant dict."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        test_dict = {"key1": "value1", "key2": "value2"}
        variant = dbus_service.OrcaModuleDBusInterface._to_variant(test_dict)
        assert variant.get_type_string() == "a{sv}"
        unpacked = variant.unpack()
        assert "key1" in unpacked
        assert "key2" in unpacked

    def test_to_variant_none(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface._to_variant None."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        variant = dbus_service.OrcaModuleDBusInterface._to_variant(None)
        assert variant.get_type_string() == "v"
        inner = variant.unpack()
        assert inner.unpack() == ""

    def test_to_variant_unknown_type(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface._to_variant unknown type."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        class CustomObject:
            """Test class for unknown type conversion."""

            def __str__(self):
                return "custom_object"

        obj = CustomObject()
        variant = dbus_service.OrcaModuleDBusInterface._to_variant(obj)
        assert variant.get_type_string() == "s"
        assert variant.unpack() == "custom_object"

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "success",
                "handlers_config": {"has_handler": True, "action": lambda: 42},
                "getter_name": "Integer",
                "expected_type": "i",
                "expected_value": 42,
            },
            {
                "id": "unknown",
                "handlers_config": {"has_handler": False},
                "getter_name": "UnknownGetter",
                "expected_type": "v",
                "expected_value": "",
            },
            {
                "id": "string_type",
                "handlers_config": {"has_handler": True, "action": lambda: "hello"},
                "getter_name": "String",
                "expected_type": "s",
                "expected_value": "hello",
            },
            {
                "id": "bool_type",
                "handlers_config": {"has_handler": True, "action": lambda: True},
                "getter_name": "Bool",
                "expected_type": "b",
                "expected_value": True,
            },
            {
                "id": "list_type",
                "handlers_config": {"has_handler": True, "action": lambda: ["a", "b"]},
                "getter_name": "List",
                "expected_type": "as",
                "expected_value": ["a", "b"],
            },
            {
                "id": "none_type",
                "handlers_config": {"has_handler": True, "action": lambda: None},
                "getter_name": "None",
                "expected_type": "v",
                "expected_value": "",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_execute_runtime_getter_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test OrcaModuleDBusInterface.ExecuteRuntimeGetter with various scenarios."""
        self._setup_dependencies(test_context)
        from orca import dbus_service

        handlers_config = case["handlers_config"]
        getter_name = case["getter_name"]
        expected_type = case["expected_type"]
        expected_value = case["expected_value"]

        if handlers_config.get("has_handler", False):
            if "action" in handlers_config:
                action = handlers_config["action"]
            elif "return_value" in handlers_config:
                mock_action = test_context.Mock()
                mock_action.return_value = handlers_config["return_value"]
                action = mock_action
            else:
                action = test_context.Mock(return_value=True)

            mock_info = dbus_service._HandlerInfo(
                python_function_name=f"get_{getter_name.lower()}",
                description=f"Get {getter_name.lower()}",
                action=action,
                handler_type=dbus_service.HandlerType.GETTER,
            )
            handlers = [mock_info]
        else:
            handlers = []

        interface = dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        result = interface.ExecuteRuntimeGetter(getter_name)
        assert result.get_type_string() == expected_type

        if expected_type == "v":
            inner = result.unpack()
            assert inner.get_type_string() == "s"
            assert inner.unpack() == expected_value
        else:
            assert result.unpack() == expected_value

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "success",
                "has_handler": True,
                "action_returns": True,
                "variant_type": "i",
                "variant_value": 99,
                "setter_name": "TestValue",
                "expected_result": True,
                "expects_setter_called": True,
            },
            {
                "id": "unknown",
                "has_handler": False,
                "action_returns": None,
                "variant_type": "i",
                "variant_value": 99,
                "setter_name": "UnknownSetter",
                "expected_result": False,
                "expects_setter_called": False,
            },
            {
                "id": "failure",
                "has_handler": True,
                "action_returns": False,
                "variant_type": "s",
                "variant_value": "test",
                "setter_name": "TestValue",
                "expected_result": False,
                "expects_setter_called": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_execute_runtime_setter_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test OrcaModuleDBusInterface.ExecuteRuntimeSetter with various scenarios."""
        self._setup_dependencies(test_context)
        from orca import dbus_service

        test_state = {"setter_called": False, "setter_value": None}

        if case["has_handler"]:

            def mock_setter_action(value) -> bool:
                test_state["setter_called"] = True
                test_state["setter_value"] = value
                return case["action_returns"] if case["action_returns"] is not None else False

            mock_info = dbus_service._HandlerInfo(
                python_function_name="set_test_value",
                description="Set test value",
                action=mock_setter_action,
                handler_type=dbus_service.HandlerType.SETTER,
            )
            handlers = [mock_info]
        else:
            handlers = []

        interface = dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        mock_variant = dbus_service.GLib.Variant(case["variant_type"], case["variant_value"])
        result = interface.ExecuteRuntimeSetter(case["setter_name"], mock_variant)
        assert result is case["expected_result"]

        if case["expects_setter_called"]:
            assert test_state["setter_called"]
            assert test_state["setter_value"] == case["variant_value"]
        else:
            assert not test_state["setter_called"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "success",
                "command_name": "TestCommand",
                "notify_user": True,
                "mock_action_return": True,
                "handler_infos": "create_handler",
                "expected_result": True,
                "should_verify_call": True,
            },
            {
                "id": "unknown",
                "command_name": "UnknownCommand",
                "notify_user": False,
                "mock_action_return": None,
                "handler_infos": [],
                "expected_result": False,
                "should_verify_call": False,
            },
            {
                "id": "failure",
                "command_name": "FailingCommand",
                "notify_user": False,
                "mock_action_return": False,
                "handler_infos": "create_handler",
                "expected_result": False,
                "should_verify_call": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_execute_command_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test OrcaModuleDBusInterface.ExecuteCommand with various scenarios."""
        self._setup_dependencies(test_context)
        from orca import dbus_service

        command_name = case["command_name"]
        notify_user = case["notify_user"]
        mock_action_return = case["mock_action_return"]
        handler_infos = case["handler_infos"]
        expected_result = case["expected_result"]
        should_verify_call = case["should_verify_call"]

        test_state = {"command_called": False, "notify_value": None}

        if handler_infos == "create_handler":

            def mock_command_action(notify_user_param) -> bool:
                test_state["command_called"] = True
                test_state["notify_value"] = notify_user_param
                return mock_action_return

            mock_info = dbus_service._HandlerInfo(
                python_function_name="_".join(
                    word.lower() for word in re.findall(r"[A-Z][a-z]*", command_name)
                ),
                description="test command",
                action=mock_command_action,
                handler_type=dbus_service.HandlerType.COMMAND,
            )
            handler_infos = [mock_info]

        interface = dbus_service.OrcaModuleDBusInterface("TestModule", handler_infos)
        result = interface.ExecuteCommand(command_name, notify_user)

        assert result is expected_result
        if should_verify_call:
            assert test_state["command_called"]
            assert test_state["notify_value"] is notify_user

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "success",
                "has_handler": True,
                "command_name": "ParamCommand",
                "function_name": "param_command",
                "notify_user": True,
                "params": {"param1": ("s", "hello"), "param2": ("i", 42)},
                "expected_type": "as",
                "expected_value": ["result1", "result2"],
                "action_config": {
                    "returns": ["result1", "result2"],
                    "track_state": True,
                    "parameters": [("param1", "str"), ("param2", "int")],
                },
            },
            {
                "id": "unknown",
                "has_handler": False,
                "command_name": "UnknownCommand",
                "function_name": None,
                "notify_user": False,
                "params": {"param1": ("s", "test")},
                "expected_type": "b",
                "expected_value": False,
                "action_config": None,
            },
            {
                "id": "complex_result",
                "has_handler": True,
                "command_name": "GetVoices",
                "function_name": "get_voices",
                "notify_user": False,
                "params": {"language": ("s", "en")},
                "expected_type": "a(sss)",
                "expected_value": [("voice1", "en", "US"), ("voice2", "es", "ES")],
                "action_config": {
                    "returns": [("voice1", "en", "US"), ("voice2", "es", "ES")],
                    "track_state": False,
                },
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_execute_parameterized_command_scenarios(  # pylint: disable=too-many-locals
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test OrcaModuleDBusInterface.ExecuteParameterizedCommand with various scenarios."""
        self._setup_dependencies(test_context)
        from orca import dbus_service

        has_handler = case["has_handler"]
        command_name = case["command_name"]
        function_name = case["function_name"]
        notify_user = case["notify_user"]
        params = case["params"]
        expected_type = case["expected_type"]
        expected_value = case["expected_value"]
        action_config = case["action_config"]

        test_state: dict[str, str | int | float | bool | dict | None] = {
            "param_command_called": False,
            "received_params": None,
        }

        if has_handler:

            def mock_param_command(**kwargs) -> bool:
                if action_config and action_config.get("track_state", False):
                    test_state["param_command_called"] = True
                    test_state["received_params"] = kwargs
                return True

            parameters = action_config.get("parameters", []) if action_config else []
            mock_info = dbus_service._HandlerInfo(
                python_function_name=function_name or "default_function",
                description="test command",
                action=mock_param_command,
                handler_type=dbus_service.HandlerType.PARAMETERIZED_COMMAND,
                parameters=parameters,
            )
            handlers = [mock_info]
        else:
            handlers = []

        interface = dbus_service.OrcaModuleDBusInterface("TestModule", handlers)

        if has_handler and action_config:

            def wrapped_action(**kwargs):
                if action_config.get("track_state", False):
                    mock_param_command(**kwargs)
                return action_config["returns"]

            interface._parameterized_commands[command_name].action = wrapped_action

        # Convert params to GLib.Variant format
        variant_params = {}
        for key, (variant_type, value) in params.items():
            variant_params[key] = dbus_service.GLib.Variant(variant_type, value)

        result = interface.ExecuteParameterizedCommand(command_name, variant_params, notify_user)
        assert result.get_type_string() == expected_type
        assert result.unpack() == expected_value

        if action_config and action_config.get("track_state", False):
            assert test_state["param_command_called"]
            expected_params = {key: value for key, (_, value) in params.items()}
            expected_params["notify_user"] = notify_user
            assert test_state["received_params"] == expected_params

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "commands",
                "list_type": "commands",
                "handler_configs": [
                    {
                        "name": "command_one",
                        "desc": "First command",
                        "type": "COMMAND",
                        "action": lambda x: True,
                    },
                    {
                        "name": "command_two",
                        "desc": "Second command",
                        "type": "COMMAND",
                        "action": lambda x: True,
                    },
                    {
                        "name": "get_value",
                        "desc": "A getter",
                        "type": "GETTER",
                        "action": lambda: True,
                    },
                ],
                "method_name": "ListCommands",
                "expected_count": 2,
                "expected_items": [
                    ("CommandOne", "First command"),
                    ("CommandTwo", "Second command"),
                ],
            },
            {
                "id": "runtime_getters",
                "list_type": "runtime_getters",
                "handler_configs": [
                    {
                        "name": "get_rate",
                        "desc": "Get speech rate",
                        "type": "GETTER",
                        "action": lambda: True,
                    },
                    {
                        "name": "get_pitch",
                        "desc": "Get speech pitch",
                        "type": "GETTER",
                        "action": lambda: True,
                    },
                ],
                "method_name": "ListRuntimeGetters",
                "expected_count": 2,
                "expected_items": [("Rate", "Get speech rate"), ("Pitch", "Get speech pitch")],
            },
            {
                "id": "runtime_setters",
                "list_type": "runtime_setters",
                "handler_configs": [
                    {
                        "name": "set_rate",
                        "desc": "Set speech rate",
                        "type": "SETTER",
                        "action": lambda x: True,
                    },
                    {
                        "name": "set_pitch",
                        "desc": "Set speech pitch",
                        "type": "SETTER",
                        "action": lambda x: True,
                    },
                ],
                "method_name": "ListRuntimeSetters",
                "expected_count": 2,
                "expected_items": [("Rate", "Set speech rate"), ("Pitch", "Set speech pitch")],
            },
            {
                "id": "parameterized_commands",
                "list_type": "parameterized_commands",
                "handler_configs": [
                    {
                        "name": "get_voices_for_language",
                        "desc": "Get voices for language",
                        "type": "PARAMETERIZED_COMMAND",
                        "action": lambda **kwargs: True,
                        "parameters": [("language", "str"), ("variant", "str")],
                    },
                ],
                "method_name": "ListParameterizedCommands",
                "expected_count": 1,
                "expected_items": [
                    (
                        "GetVoicesForLanguage",
                        "Get voices for language",
                        [("language", "str"), ("variant", "str")],
                    )
                ],
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_list_methods_scenarios(  # pylint: disable=too-many-locals
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test OrcaModuleDBusInterface list methods with various handler types."""
        self._setup_dependencies(test_context)
        from orca import dbus_service

        list_type = case["list_type"]
        handler_configs = case["handler_configs"]
        method_name = case["method_name"]
        expected_count = case["expected_count"]
        expected_items = case["expected_items"]

        handlers = []
        for config in handler_configs:
            handler_type = getattr(dbus_service.HandlerType, config["type"])
            handler_info = dbus_service._HandlerInfo(
                python_function_name=config["name"],
                description=config["desc"],
                action=config["action"],
                handler_type=handler_type,
                parameters=config.get("parameters", []),
            )
            handlers.append(handler_info)

        interface = dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        list_method = getattr(interface, method_name)
        result = list_method()

        assert len(result) == expected_count

        if list_type == "parameterized_commands":
            # Parameterized commands return tuples with 3 elements
            for expected_item in expected_items:
                assert result[0][0] == expected_item[0]  # Name
                assert result[0][1] == expected_item[1]  # Description
                assert result[0][2] == expected_item[2]  # Parameters
        else:
            # Other types return simple tuples
            for expected_item in expected_items:
                assert expected_item in result

    def test_constructor_empty_handlers(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface constructor empty handlers."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        interface = dbus_service.OrcaModuleDBusInterface("TestModule", [])
        assert interface._module_name == "TestModule"
        assert len(interface._commands) == 0
        assert len(interface._parameterized_commands) == 0
        assert len(interface._getters) == 0
        assert len(interface._setters) == 0

    def test_constructor_mixed_handlers(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface constructor mixed handlers."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        handlers = [
            dbus_service._HandlerInfo(
                python_function_name="toggle_something",
                description="Toggle something",
                action=lambda x: True,
                handler_type=dbus_service.HandlerType.COMMAND,
            ),
            dbus_service._HandlerInfo(
                python_function_name="get_value",
                description="Get value",
                action=lambda: True,
                handler_type=dbus_service.HandlerType.GETTER,
            ),
            dbus_service._HandlerInfo(
                python_function_name="set_value",
                description="Set value",
                action=lambda x: True,
                handler_type=dbus_service.HandlerType.SETTER,
            ),
            dbus_service._HandlerInfo(
                python_function_name="do_something_complex",
                description="Do something complex",
                action=lambda **kwargs: True,
                handler_type=dbus_service.HandlerType.PARAMETERIZED_COMMAND,
                parameters=[("param", "str")],
            ),
        ]
        interface = dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        assert interface._module_name == "TestModule"
        assert "ToggleSomething" in interface._commands
        assert "Value" in interface._getters
        assert "Value" in interface._setters
        assert "DoSomethingComplex" in interface._parameterized_commands

    def test_constructor_handler_without_type(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface constructor handler without type."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        class MockHandlerInfo:
            """Mock handler info for testing."""

            def __init__(self):
                self.python_function_name = "test_command"
                self.description = "Test command"
                self.action = lambda x: True

        MockHandlerInfo()
        # Convert to proper _HandlerInfo for type compatibility
        real_handler = dbus_service._HandlerInfo(
            python_function_name="test_command",
            description="Test command",
            action=lambda x: True,
            handler_type=dbus_service.HandlerType.COMMAND,
        )
        interface = dbus_service.OrcaModuleDBusInterface("TestModule", [real_handler])
        assert "TestCommand" in interface._commands

    def test_constructor_duplicate_names(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface constructor duplicate names."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        handlers = [
            dbus_service._HandlerInfo(
                python_function_name="test_command",
                description="First command",
                action=lambda x: True,
                handler_type=dbus_service.HandlerType.COMMAND,
            ),
            dbus_service._HandlerInfo(
                python_function_name="test_command",
                description="Second command",
                action=lambda x: True,
                handler_type=dbus_service.HandlerType.COMMAND,
            ),
        ]
        interface = dbus_service.OrcaModuleDBusInterface("TestModule", handlers)
        assert len(interface._commands) == 1
        assert interface._commands["TestCommand"].action(False) is True

    def test_for_publication(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface.for_publication."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        interface = dbus_service.OrcaModuleDBusInterface("TestModule", [])
        interface.__dbus_xml__ = "<xml>test</xml>"
        result = interface.for_publication()
        assert result == "<xml>test</xml>"

    def test_orca_dbus_service_constructor(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface constructor."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        service = dbus_service.OrcaDBusServiceInterface()
        assert service._registered_modules == set()

    def test_orca_dbus_service_for_publication(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.for_publication."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        service = dbus_service.OrcaDBusServiceInterface()
        service.__dbus_xml__ = "<xml>service</xml>"
        result = service.for_publication()
        assert result == "<xml>service</xml>"

    def test_add_module_interface_new(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.add_module_interface new module."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_bus = test_context.Mock()
        service = dbus_service.OrcaDBusServiceInterface()
        handlers: list[dbus_service._HandlerInfo] = []
        mock_module_iface = test_context.Mock()
        test_context.patch_object(
            dbus_service,
            "OrcaModuleDBusInterface",
            side_effect=lambda module_name, handlers_info: mock_module_iface,
        )
        service.add_module_interface("TestModule", handlers, mock_bus, "/test/path")
        assert "TestModule" in service._registered_modules
        mock_bus.publish_object.assert_called_once_with("/test/path/TestModule", mock_module_iface)

    def test_add_module_interface_replace_existing(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.add_module_interface replace existing."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_bus = test_context.Mock()
        service = dbus_service.OrcaDBusServiceInterface()
        service._registered_modules.add("TestModule")
        handlers: list[dbus_service._HandlerInfo] = []
        mock_module_iface = test_context.Mock()
        test_context.patch_object(
            dbus_service,
            "OrcaModuleDBusInterface",
            side_effect=lambda module_name, handlers_info: mock_module_iface,
        )
        service.add_module_interface("TestModule", handlers, mock_bus, "/test/path")
        assert "TestModule" in service._registered_modules
        mock_bus.unpublish_object.assert_called_once_with("/test/path/TestModule")
        mock_bus.publish_object.assert_called_once_with("/test/path/TestModule", mock_module_iface)

    def test_add_module_interface_unpublish_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.add_module_interface unpublish error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        MockDBusError = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.unpublish_object.side_effect = MockDBusError("Unpublish failed")
        service = dbus_service.OrcaDBusServiceInterface()
        service._registered_modules.add("TestModule")
        handlers: list[dbus_service._HandlerInfo] = []
        mock_module_iface = test_context.Mock()
        test_context.patch_object(
            dbus_service,
            "OrcaModuleDBusInterface",
            side_effect=lambda module_name, handlers_info: mock_module_iface,
        )


        # The unpublish_object call should fail but be caught gracefully by the production code
        # The module should still be successfully registered despite the unpublish error
        service.add_module_interface("TestModule", handlers, mock_bus, "/test/path")
        assert "TestModule" in service._registered_modules
        mock_bus.unpublish_object.assert_called_once_with("/test/path/TestModule")
        mock_bus.publish_object.assert_called_once_with("/test/path/TestModule", mock_module_iface)

    def test_add_module_interface_publish_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.add_module_interface publish error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        MockDBusError = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.publish_object.side_effect = MockDBusError("Publish failed")
        service = dbus_service.OrcaDBusServiceInterface()
        handlers: list[dbus_service._HandlerInfo] = []
        mock_module_iface = test_context.Mock()
        test_context.patch_object(
            dbus_service,
            "OrcaModuleDBusInterface",
            side_effect=lambda module_name, handlers_info: mock_module_iface,
        )

        service.add_module_interface("TestModule", handlers, mock_bus, "/test/path")
        assert "TestModule" not in service._registered_modules

    def test_remove_module_interface_success(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.remove_module_interface success."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_bus = test_context.Mock()
        service = dbus_service.OrcaDBusServiceInterface()
        service._registered_modules.add("TestModule")
        result = service.remove_module_interface("TestModule", mock_bus, "/test/path")
        assert result is True
        assert "TestModule" not in service._registered_modules
        mock_bus.unpublish_object.assert_called_once_with("/test/path/TestModule")

    def test_remove_module_interface_not_registered(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.remove_module_interface not registered."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_bus = test_context.Mock()
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.remove_module_interface("TestModule", mock_bus, "/test/path")
        assert result is False
        mock_bus.unpublish_object.assert_not_called()

    def test_remove_module_interface_unpublish_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.remove_module_interface unpublish error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        MockDBusError = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.unpublish_object.side_effect = MockDBusError("Unpublish failed")
        service = dbus_service.OrcaDBusServiceInterface()
        service._registered_modules.add("TestModule")

        result = service.remove_module_interface("TestModule", mock_bus, "/test/path")
        assert result is False
        assert "TestModule" in service._registered_modules

    def test_list_modules(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.ListModules."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        service = dbus_service.OrcaDBusServiceInterface()
        service._registered_modules.update(["Module1", "Module2", "Module3"])
        modules = service.ListModules()
        assert set(modules) == {"Module1", "Module2", "Module3"}

    def test_orca_dbus_service_list_commands(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.ListCommands."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        service = dbus_service.OrcaDBusServiceInterface()
        commands = service.ListCommands()
        command_names = [cmd[0] for cmd in commands]
        assert "ShowPreferences" in command_names
        assert "PresentMessage" in command_names
        assert "GetVersion" in command_names

    def test_show_preferences_success(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.ShowPreferences success."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_script = test_context.Mock()
        mock_script.show_preferences_gui.return_value = None
        mock_manager = test_context.Mock()
        mock_manager.get_active_script.return_value = mock_script
        test_context.patch_object(
            dbus_service.script_manager, "get_manager", return_value=mock_manager
        )
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.ShowPreferences()
        assert result is True
        mock_script.show_preferences_gui.assert_called_once()

    def test_show_preferences_no_active_script(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.ShowPreferences no active script."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_script = test_context.Mock()
        mock_script.show_preferences_gui.return_value = None
        mock_manager = test_context.Mock()
        mock_manager.get_active_script.return_value = None
        mock_manager.get_default_script.return_value = mock_script
        test_context.patch_object(
            dbus_service.script_manager, "get_manager", return_value=mock_manager
        )
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.ShowPreferences()
        assert result is True
        mock_script.show_preferences_gui.assert_called_once()

    def test_show_preferences_no_script(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.ShowPreferences no script."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_manager = test_context.Mock()
        mock_manager.get_active_script.return_value = None
        mock_manager.get_default_script.return_value = None
        test_context.patch_object(
            dbus_service.script_manager, "get_manager", return_value=mock_manager
        )
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.ShowPreferences()
        assert result is False

    def test_present_message_success(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.PresentMessage success."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_script = test_context.Mock()
        mock_script.present_message.return_value = None
        mock_manager = test_context.Mock()
        mock_manager.get_active_script.return_value = mock_script
        test_context.patch_object(
            dbus_service.script_manager, "get_manager", return_value=mock_manager
        )
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.PresentMessage("Test message")
        assert result is True
        mock_script.present_message.assert_called_once_with("Test message")

    def test_present_message_no_script(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.PresentMessage no script."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_manager = test_context.Mock()
        mock_manager.get_active_script.return_value = None
        mock_manager.get_default_script.return_value = None
        test_context.patch_object(
            dbus_service.script_manager, "get_manager", return_value=mock_manager
        )
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.PresentMessage("Test message")
        assert result is False

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_revision",
                "version": "2.0.0",
                "revision": "abcd1234",
                "expected_result": "2.0.0 (rev abcd1234)",
            },
            {"id": "no_revision", "version": "2.0.0", "revision": "", "expected_result": "2.0.0"},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_version_scenarios(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test OrcaDBusServiceInterface.GetVersion with and without revision."""
        self._setup_dependencies(test_context)
        from orca import dbus_service

        version = case["version"]
        revision = case["revision"]
        expected_result = case["expected_result"]

        test_context.patch_object(dbus_service.orca_platform, "version", new=version)
        test_context.patch_object(dbus_service.orca_platform, "revision", new=revision)
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.GetVersion()
        assert result == expected_result

    def test_shutdown_service(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.shutdown_service."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_bus = test_context.Mock()
        service = dbus_service.OrcaDBusServiceInterface()
        service._registered_modules.update(["Module1", "Module2"])
        service.shutdown_service(mock_bus, "/test/path")
        assert len(service._registered_modules) == 0
        assert mock_bus.unpublish_object.call_count == 2
        mock_bus.unpublish_object.assert_any_call("/test/path/Module1")
        mock_bus.unpublish_object.assert_any_call("/test/path/Module2")

    def test_shutdown_service_unpublish_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.shutdown_service unpublish error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        MockDBusError = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.unpublish_object.side_effect = MockDBusError("Unpublish failed")
        service = dbus_service.OrcaDBusServiceInterface()
        service._registered_modules.update(["Module1"])

        service.shutdown_service(mock_bus, "/test/path")
        assert len(service._registered_modules) == 0

    def test_orca_remote_controller_constructor(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController constructor."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        assert controller._dbus_service_interface is None
        assert controller._is_running is False
        assert controller._bus is None
        assert controller._event_loop is None
        assert not controller._pending_registrations
        assert controller._total_commands == 0
        assert controller._total_getters == 0
        assert controller._total_setters == 0
        assert controller._total_modules == 0

    def test_is_running_false(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.is_running false."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        assert controller.is_running() is False

    def test_is_running_true(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.is_running true."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        assert controller.is_running() is True

    def test_start_already_running(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.start already running."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        result = controller.start()
        assert result is True

    def test_start_bus_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.start bus error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        MockDBusError = self._get_mock_dbus_error()
        def mock_session_bus() -> None:
            raise MockDBusError("Bus connection failed")

        test_context.patch_object(dbus_service, "SessionMessageBus", new=mock_session_bus)

        controller = dbus_service.OrcaRemoteController()
        result = controller.start()
        assert result is False
        assert controller._bus is None
        assert controller._is_running is False

    def test_start_publish_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.start publish error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        MockDBusError = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.connection.get_unique_name.return_value = "test_name"
        mock_bus.publish_object.side_effect = MockDBusError("Publish failed")
        test_context.patch_object(dbus_service, "SessionMessageBus", return_value=mock_bus)

        controller = dbus_service.OrcaRemoteController()
        result = controller.start()
        assert result is False
        assert controller._bus is None
        assert controller._dbus_service_interface is None
        assert controller._is_running is False

    def test_start_publish_error_with_cleanup(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.start publish error with cleanup."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        MockDBusError = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.connection.get_unique_name.return_value = "test_name"
        mock_bus.register_service.side_effect = MockDBusError("Register failed")
        test_context.patch_object(dbus_service, "SessionMessageBus", return_value=mock_bus)

        controller = dbus_service.OrcaRemoteController()
        result = controller.start()
        assert result is False
        mock_bus.unpublish_object.assert_called_once()

    def test_start_success(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.start success."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_bus = test_context.Mock()
        mock_bus.connection.get_unique_name.return_value = "test_name"
        test_context.patch_object(dbus_service, "SessionMessageBus", return_value=mock_bus)
        controller = dbus_service.OrcaRemoteController()
        mock_process = test_context.Mock()
        mock_print = test_context.Mock()
        test_context.patch_object(controller, "_process_pending_registrations", new=mock_process)
        test_context.patch_object(controller, "_print_registration_summary", new=mock_print)
        result = controller.start()
        assert result is True
        assert controller._is_running is True
        assert controller._bus is mock_bus
        assert controller._dbus_service_interface is not None
        mock_bus.publish_object.assert_called_once()
        mock_bus.register_service.assert_called_once()
        mock_process.assert_called_once()
        mock_print.assert_called_once()

    def test_shutdown_not_running(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.shutdown not running."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        controller.shutdown()

    def test_shutdown_success(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.shutdown success."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_bus = test_context.Mock()
        mock_service = test_context.Mock()
        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        controller._bus = mock_bus
        controller._dbus_service_interface = mock_service
        controller._total_commands = 5
        controller._total_getters = 3
        controller._total_setters = 2
        controller._total_modules = 1
        controller._pending_registrations = {"test": "module"}
        controller.shutdown()
        assert controller._is_running is False
        assert controller._bus is None
        assert controller._dbus_service_interface is None
        assert controller._total_commands == 0
        assert controller._total_getters == 0
        assert controller._total_setters == 0
        assert controller._total_modules == 0
        assert not controller._pending_registrations
        mock_service.shutdown_service.assert_called_once()
        mock_bus.unpublish_object.assert_called_once()
        mock_bus.unregister_service.assert_called_once()
        mock_bus.disconnect.assert_called_once()

    def test_shutdown_unpublish_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.shutdown unpublish error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        MockDBusError = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.unpublish_object.side_effect = MockDBusError("Unpublish failed")
        mock_service = test_context.Mock()
        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        controller._bus = mock_bus
        controller._dbus_service_interface = mock_service

        controller.shutdown()
        assert controller._is_running is False
        mock_bus.unregister_service.assert_called_once()
        mock_bus.disconnect.assert_called_once()

    def test_shutdown_unregister_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.shutdown unregister error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        MockDBusError = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.unregister_service.side_effect = MockDBusError("Unregister failed")
        mock_service = test_context.Mock()
        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        controller._bus = mock_bus
        controller._dbus_service_interface = mock_service

        controller.shutdown()
        assert controller._is_running is False
        mock_bus.disconnect.assert_called_once()

    def test_register_decorated_module_not_running(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.register_decorated_module not running."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        mock_module = test_context.Mock()
        controller.register_decorated_module("TestModule", mock_module)
        assert "TestModule" in controller._pending_registrations
        assert controller._pending_registrations["TestModule"] is mock_module

    def test_register_decorated_module_running(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.register_decorated_module running."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        controller._dbus_service_interface = test_context.Mock()
        controller._bus = test_context.Mock()
        mock_register = test_context.Mock()
        test_context.patch_object(
            controller, "_register_decorated_commands_internal", new=mock_register
        )
        mock_module = test_context.Mock()
        controller.register_decorated_module("TestModule", mock_module)
        mock_register.assert_called_once_with("TestModule", mock_module)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "pending",
                "is_running": False,
                "has_pending": True,
                "mock_service_returns": None,
                "expected_result": True,
                "expects_service_call": False,
            },
            {
                "id": "not_running",
                "is_running": False,
                "has_pending": False,
                "mock_service_returns": None,
                "expected_result": False,
                "expects_service_call": False,
            },
            {
                "id": "running",
                "is_running": True,
                "has_pending": False,
                "mock_service_returns": True,
                "expected_result": True,
                "expects_service_call": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_deregister_module_commands_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test OrcaRemoteController.deregister_module_commands with various scenarios."""
        self._setup_dependencies(test_context)
        from orca import dbus_service

        is_running = case["is_running"]
        has_pending = case["has_pending"]
        mock_service_returns = case["mock_service_returns"]
        expected_result = case["expected_result"]
        expects_service_call = case["expects_service_call"]

        controller = dbus_service.OrcaRemoteController()

        if has_pending:
            controller._pending_registrations["TestModule"] = test_context.Mock()

        if is_running:
            mock_service = test_context.Mock()
            mock_service.remove_module_interface.return_value = mock_service_returns
            controller._is_running = True
            controller._dbus_service_interface = mock_service
            controller._bus = test_context.Mock()

        result = controller.deregister_module_commands("TestModule")
        assert result is expected_result

        if has_pending:
            assert "TestModule" not in controller._pending_registrations

        if expects_service_call:
            mock_service.remove_module_interface.assert_called_once()

    def test_process_pending_registrations_empty(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController._process_pending_registrations empty."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        controller._process_pending_registrations()

    def test_process_pending_registrations_with_modules(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test OrcaRemoteController._process_pending_registrations with modules."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        mock_register = test_context.Mock()
        test_context.patch_object(
            controller, "_register_decorated_commands_internal", new=mock_register
        )
        mock_module1 = test_context.Mock()
        mock_module2 = test_context.Mock()
        controller._pending_registrations = {"Module1": mock_module1, "Module2": mock_module2}
        controller._process_pending_registrations()
        assert not controller._pending_registrations
        assert mock_register.call_count == 2
        mock_register.assert_any_call("Module1", mock_module1)
        mock_register.assert_any_call("Module2", mock_module2)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_interface",
                "has_interface": False,
                "expected_count_check": lambda count: count == 0,
            },
            {
                "id": "with_interface",
                "has_interface": True,
                "expected_count_check": lambda count: count >= 3,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_count_system_commands_scenarios(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test OrcaRemoteController._count_system_commands with and without interface."""
        self._setup_dependencies(test_context)
        from orca import dbus_service

        has_interface = case["has_interface"]
        expected_count_check = case["expected_count_check"]

        controller = dbus_service.OrcaRemoteController()
        if has_interface:
            controller._dbus_service_interface = dbus_service.OrcaDBusServiceInterface()

        count = controller._count_system_commands()
        assert expected_count_check(count)

    def test_print_registration_summary(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController._print_registration_summary."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        controller._total_commands = 5
        controller._total_getters = 3
        controller._total_setters = 2
        controller._total_modules = 2
        mock_count = test_context.Mock(return_value=4)
        test_context.patch_object(controller, "_count_system_commands", new=mock_count)
        controller._print_registration_summary()
        mock_count.assert_called_once()

    def test_get_remote_controller(self, test_context: OrcaTestContext) -> None:
        """Test get_remote_controller function."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.get_remote_controller()
        assert isinstance(controller, dbus_service.OrcaRemoteController)

    def test_extract_function_parameters_complex_annotation(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _extract_function_parameters complex annotation without __name__."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        def test_func(self, param1: list[str]) -> None:  # pylint: disable=unused-argument
            pass

        params = dbus_service._extract_function_parameters(test_func)
        assert len(params) == 1
        assert params[0][0] == "param1"
        # Complex types without __name__ get string representation
        assert "list" in params[0][1] or "List" in params[0][1]

    def test_to_variant_empty_list_tuples(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface._to_variant empty list tuples."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        empty_tuples: list[tuple[str, str]] = []
        variant = dbus_service.OrcaModuleDBusInterface._to_variant(empty_tuples)
        assert variant.get_type_string() == "as"  # Empty list defaults to string array
        assert variant.unpack() == []

    def test_to_variant_mixed_types_list(self, test_context: OrcaTestContext) -> None:
        """Test OrcaModuleDBusInterface._to_variant mixed types list."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mixed_list = ["string", 42, True]
        variant = dbus_service.OrcaModuleDBusInterface._to_variant(mixed_list)
        assert variant.get_type_string() == "av"
        unpacked = variant.unpack()
        assert len(unpacked) == 3

    def test_register_decorated_commands_internal_not_ready(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test OrcaRemoteController._register_decorated_commands_internal not ready."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        mock_module = test_context.Mock()

        # This should return early and not process anything
        controller._register_decorated_commands_internal("TestModule", mock_module)

        # Nothing should be changed since service is not ready
        assert controller._total_commands == 0
        assert controller._total_getters == 0
        assert controller._total_setters == 0
        assert controller._total_modules == 0

    def test_register_decorated_commands_internal_with_decorators(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test OrcaRemoteController._register_decorated_commands_internal with decorators."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        class MockModule:
            """Mock module with decorated methods."""

            def regular_method(self) -> str:
                """Regular method without decoration."""

                return "regular"

            def command_method(self) -> str:
                """Test command method."""

                return "command"

            def param_command_method(self) -> str:
                """Test parameterized command."""

                return "param_command"

            def getter_method(self) -> str:
                """Test getter method."""

                return "getter"

            def setter_method(self) -> str:
                """Test setter method."""

                return "setter"

        # Add decorations to methods
        setattr(MockModule.command_method, "dbus_command_description", "Test command method.")
        setattr(
            MockModule.param_command_method,
            "dbus_parameterized_command_description",
            "Test parameterized command.",
        )
        setattr(MockModule.getter_method, "dbus_getter_description", "Test getter method.")
        setattr(MockModule.setter_method, "dbus_setter_description", "Test setter method.")
        mock_module = MockModule()
        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        controller._dbus_service_interface = test_context.Mock()
        controller._bus = test_context.Mock()

        def mock_get_manager():
            return test_context.Mock()

        def mock_remote_controller_event():
            return test_context.Mock()

        test_context.patch_object(
            dbus_service.script_manager, "get_manager", new=mock_get_manager
        )
        test_context.patch_object(
            dbus_service.input_event, "RemoteControllerEvent", new=mock_remote_controller_event
        )
        controller._register_decorated_commands_internal("TestModule", mock_module)
        assert controller._total_commands == 2  # command + parameterized command
        assert controller._total_getters == 1
        assert controller._total_setters == 1
        assert controller._total_modules == 1

    def test_register_decorated_commands_internal_no_handlers(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test OrcaRemoteController._register_decorated_commands_internal no handlers."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        class MockModule:
            """Mock module without decorated methods."""

            def regular_method(self) -> str:
                """Regular method without decoration."""

                return "regular"

        mock_module = MockModule()
        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        controller._dbus_service_interface = test_context.Mock()
        controller._bus = test_context.Mock()

        # Properly patch the method we want to assert on
        mock_add_interface = test_context.Mock()
        test_context.patch_object(
            controller._dbus_service_interface, "add_module_interface", new=mock_add_interface
        )
        controller._register_decorated_commands_internal("TestModule", mock_module)
        assert controller._total_commands == 0
        assert controller._total_getters == 0
        assert controller._total_setters == 0
        assert controller._total_modules == 0
        mock_add_interface.assert_not_called()

    def test_start_unpublish_object_error_during_cleanup(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test OrcaRemoteController.start unpublish object error during cleanup."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        MockDBusError = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.connection.get_unique_name.return_value = "test_name"
        mock_bus.register_service.side_effect = MockDBusError("Register failed")
        mock_bus.unpublish_object.side_effect = MockDBusError("Unpublish failed")
        test_context.patch_object(dbus_service, "SessionMessageBus", return_value=mock_bus)

        controller = dbus_service.OrcaRemoteController()
        result = controller.start()
        assert result is False
        assert controller._bus is None
        assert controller._dbus_service_interface is None
