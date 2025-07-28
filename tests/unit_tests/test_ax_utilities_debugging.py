# Unit tests for ax_utilities_debugging.py debugging utility methods.
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

"""Unit tests for ax_utilities_debugging.py debugging utility methods."""

from __future__ import annotations

import importlib
import inspect
import types
from unittest.mock import Mock

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib
import pytest

from conftest import clean_module_cache # pylint: disable=import-error


def load_debugging_module():
    """Load the debugging module."""

    clean_module_cache("orca.ax_utilities_debugging")
    # Dynamic import to avoid circular dependencies and allow module cache cleanup
    module = importlib.import_module("orca.ax_utilities_debugging")
    return module.AXUtilitiesDebugging


@pytest.mark.unit
class TestAXUtilitiesDebuggingCore:
    """Test core debugging utility methods."""

    @pytest.mark.parametrize(
        "input_string, expected_result",
        [
            pytest.param("", "", id="empty_string"),
            pytest.param("short text", "short text", id="short_text"),
            pytest.param("text with\nnewline", "text with\\nnewline", id="newline_replacement"),
            pytest.param("text with\ufffcobject", "text with[OBJ]object", id="object_replacement"),
            pytest.param(
                "this is a very long text with many words that should be truncated",
                "this is a very long text with many words that should be truncated",
                id="under_100_chars_no_truncation",
            ),
            pytest.param(
                "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 "
                "word11 word12 word13 word14 word15 word16 word17 word18 word19 word20",
                "word1 word2 word3 word4 word5 ... word16 word17 word18 word19 word20 (130 chars.)",
                id="over_100_chars_truncation",
            ),
        ],
    )
    def test_format_string(self, input_string, expected_result, mock_orca_dependencies):
        """Test AXUtilitiesDebugging._format_string."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        result = axutils_debug._format_string(input_string)  # pylint: disable=protected-access
        assert result == expected_result

    def test_as_string_accessible_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.as_string with Atspi.Accessible objects."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Mock AXObject methods by patching the imported module
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_role_name", lambda obj: "button"
        )
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.get_name", lambda obj: "OK")

        result = axutils_debug.as_string(mock_obj)
        assert "button: 'OK'" in result
        assert hex(id(mock_obj)) in result

    def test_as_string_accessible_dead_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.as_string handles dead accessible objects."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Mock AXObject methods to return empty values (dead object behavior)
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.get_role_name", lambda obj: "")
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.get_name", lambda obj: "")

        result = axutils_debug.as_string(mock_obj)
        assert "[DEAD" in result

    def test_as_string_event_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.as_string with Atspi.Event objects."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "focus:in"
        mock_event.source = Mock(spec=Atspi.Accessible)
        mock_event.detail1 = 0
        mock_event.detail2 = 0
        mock_event.any_data = None

        # Mock AXObject methods for the source
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_role_name", lambda obj: "button"
        )
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.get_name", lambda obj: "OK")

        # Mock application string formatting
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXUtilitiesApplication.application_as_string",
            lambda obj: "TestApp",
        )

        result = axutils_debug.as_string(mock_event)
        assert "focus:in for" in result
        assert "TestApp" in result

    def test_actions_as_string(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.actions_as_string."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object with actions
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.get_n_actions", lambda obj: 2)

        def mock_get_action_name(unused_obj, index):
            return ["click", "focus"][index]

        def mock_get_action_key_binding(unused_obj, index):
            return ["Return", ""][index]

        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_action_name", mock_get_action_name
        )
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_action_key_binding",
            mock_get_action_key_binding,
        )

        result = axutils_debug.actions_as_string(mock_obj)
        assert "click (Return)" in result
        assert "focus" in result
        assert ";" in result

    def test_attributes_as_string(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.attributes_as_string."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object with attributes
        attributes_dict = {"level": "2", "placeholder-text": "Enter name"}
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_attributes_dict", lambda obj: attributes_dict
        )

        result = axutils_debug.attributes_as_string(mock_obj)
        assert "level:2" in result
        assert "placeholder-text:Enter name" in result
        assert ", " in result

    def test_interfaces_as_string(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.interfaces_as_string."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Invalid object
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.is_valid", lambda obj: False)
        result = axutils_debug.interfaces_as_string(mock_obj)
        assert result == ""

        # Scenario: Valid object with multiple interfaces
        interface_support = {
            "is_valid": True,
            "supports_action": True,
            "supports_component": True,
            "supports_text": True,
            "supports_collection": False,
            "supports_document": False,
            "supports_editable_text": False,
            "supports_hyperlink": False,
            "supports_hypertext": False,
            "supports_image": False,
            "supports_selection": False,
            "supports_table": False,
            "supports_table_cell": False,
            "supports_value": False,
        }

        for method_name, return_value in interface_support.items():
            monkeypatch.setattr(
                f"orca.ax_utilities_debugging.AXObject.{method_name}",
                lambda obj, rv=return_value: rv
            )

        result = axutils_debug.interfaces_as_string(mock_obj)
        assert "Action" in result
        assert "Component" in result
        assert "Text" in result
        assert ", " in result

    def test_state_set_as_string(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.state_set_as_string."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Invalid object
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.is_valid", lambda obj: False)
        result = axutils_debug.state_set_as_string(mock_obj)
        assert result == ""

        # Scenario: Valid object with states
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.is_valid", lambda obj: True)

        # Mock state set
        mock_state_set = Mock()
        mock_state1 = Mock()
        mock_state1.value_name = "ATSPI_STATE_FOCUSED"
        mock_state2 = Mock()
        mock_state2.value_name = "ATSPI_STATE_VISIBLE"
        mock_state_set.get_states.return_value = [mock_state1, mock_state2]

        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_state_set", lambda obj: mock_state_set
        )

        result = axutils_debug.state_set_as_string(mock_obj)
        assert "focused" in result
        assert "visible" in result
        assert ", " in result

    def test_text_for_debugging(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.text_for_debugging."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object does not support text
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.supports_text", lambda obj: False)
        result = axutils_debug.text_for_debugging(mock_obj)
        assert result == ""

        # Scenario: Object supports text and returns content
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.supports_text", lambda obj: True)

        def mock_get_text(unused_obj, unused_start, unused_end):
            return "Sample text content"

        def mock_get_character_count(unused_obj):
            return 20

        monkeypatch.setattr(Atspi.Text, "get_text", mock_get_text)
        monkeypatch.setattr(Atspi.Text, "get_character_count", mock_get_character_count)

        result = axutils_debug.text_for_debugging(mock_obj)
        assert result == "Sample text content"


@pytest.mark.unit
class TestAXUtilitiesDebuggingExtended:
    """Test extended debugging utility methods."""

    @pytest.mark.parametrize(
        "obj_type, expected_pattern",
        [
            pytest.param("role", "role-nick", id="role_enum"),
            pytest.param("state", "state-nick", id="state_enum"),
            pytest.param("rect", "(x:10, y:20, width:100, height:200)", id="rect_object"),
            pytest.param("list", "[item1, item2]", id="list_object"),
            pytest.param("set", "item1", id="set_object"),
            pytest.param("dict", "{'key1': 'value1'", id="dict_object"),
            pytest.param("function", "test_module.test_function", id="function_object"),
            pytest.param("method", "TestClass.test_method", id="method_object"),
            pytest.param("frame", "test_module.test_function", id="frame_object"),
            pytest.param("frameinfo", "test_module.test_function:42", id="frameinfo_object"),
            pytest.param("string", "test string", id="string_object"),
        ],
    )
    def test_as_string_various_objects(self, obj_type, expected_pattern, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.as_string with various object types."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()

        # Create test objects based on type
        test_obj = self._create_test_object(obj_type)
        result = axutils_debug.as_string(test_obj)

        # Verify the result contains expected patterns
        assert expected_pattern in result

    def _create_test_object(self, obj_type):
        """Create test objects for various types."""
        creators = {
            "role": self._create_role_object,
            "state": self._create_state_object,
            "rect": self._create_rect_object,
            "list": self._create_list_object,
            "set": self._create_set_object,
            "dict": self._create_dict_object,
            "function": self._create_function_object,
            "method": self._create_method_object,
            "frame": self._create_frame_object,
            "frameinfo": self._create_frameinfo_object,
            "string": self._create_string_object,
        }
        creator = creators.get(obj_type)
        return creator() if creator else None

    def _create_role_object(self):
        """Create mock role object."""
        mock_role = Mock(spec=Atspi.Role)
        mock_role.value_nick = "role-nick"
        return mock_role

    def _create_state_object(self):
        """Create mock state object."""
        mock_state = Mock(spec=Atspi.StateType)
        mock_state.value_nick = "state-nick"
        return mock_state

    def _create_rect_object(self):
        """Create mock rect object."""
        mock_rect = Mock(spec=Atspi.Rect)
        mock_rect.x = 10
        mock_rect.y = 20
        mock_rect.width = 100
        mock_rect.height = 200
        return mock_rect

    def _create_list_object(self):
        """Create list object."""
        return ["item1", "item2"]

    def _create_set_object(self):
        """Create set object."""
        return {"item1", "item2"}

    def _create_dict_object(self):
        """Create dict object."""
        return {"key1": "value1", "key2": "value2"}

    def _create_function_object(self):
        """Create function object."""
        def test_function():
            pass
        test_function.__module__ = "test_module"
        test_function.__name__ = "test_function"
        return test_function

    def _create_method_object(self):
        """Create method object."""
        # Create a real method object
        class TestClass:
            """Test class for method creation."""
            def test_method(self):
                """Test method for testing."""
            def another_method(self):
                """Another method to satisfy pylint requirements."""
        return TestClass().test_method

    def _create_frame_object(self):
        """Create frame object."""
        mock_frame = Mock(spec=types.FrameType)
        mock_frame.f_code.co_filename = "/path/to/test_module.py"
        mock_frame.f_code.co_name = "test_function"
        return mock_frame

    def _create_frameinfo_object(self):
        """Create frameinfo object."""
        mock_frameinfo = Mock(spec=inspect.FrameInfo)
        mock_frameinfo.filename = "/path/to/test_module.py"
        mock_frameinfo.function = "test_function"
        mock_frameinfo.lineno = 42
        return mock_frameinfo

    def _create_string_object(self):
        """Create string object."""
        return "test string"

    def test_object_details_as_string_basic(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.object_details_as_string basic functionality."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()

        # Scenario: Non-Atspi.Accessible object
        non_accessible = "not an accessible"
        result = axutils_debug.object_details_as_string(non_accessible)
        assert result == ""

        # Scenario: Dead object
        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.is_dead", lambda obj: True)
        result = axutils_debug.object_details_as_string(mock_obj)
        assert result == "(exception fetching data)"

    def test_object_event_details_as_string(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.object_event_details_as_string."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()

        # Scenario: Mouse event (should return empty string)
        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "mouse:button"

        result = axutils_debug.object_event_details_as_string(mock_event)
        assert result == ""

        # Scenario: Non-mouse event with source and any_data
        mock_event.type = "focus:in"
        mock_event.source = Mock(spec=Atspi.Accessible)
        mock_event.any_data = Mock(spec=Atspi.Accessible)

        def mock_object_details(obj, indent="", unused_include_app=True):
            if obj == mock_event.source:
                return f"{indent}SOURCE DETAILS"
            if obj == mock_event.any_data:
                return f"{indent}ANY_DATA DETAILS"
            return ""

        monkeypatch.setattr(axutils_debug, "object_details_as_string", mock_object_details)

        result = axutils_debug.object_event_details_as_string(mock_event)
        assert "EVENT SOURCE:" in result
        assert "SOURCE DETAILS" in result
        assert "EVENT ANY DATA:" in result
        assert "ANY_DATA DETAILS" in result

        # Scenario: Non-mouse event with source but no any_data
        mock_event.any_data = None

        def mock_object_details_no_any_data(obj, indent="", unused_include_app=True):
            if obj == mock_event.source:
                return f"{indent}SOURCE DETAILS"
            return ""

        monkeypatch.setattr(
            axutils_debug, "object_details_as_string", mock_object_details_no_any_data
        )

        result = axutils_debug.object_event_details_as_string(mock_event)
        assert "EVENT SOURCE:" in result
        assert "SOURCE DETAILS" in result
        assert "EVENT ANY DATA:" not in result

    def test_as_string_collection_match_type(self, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.as_string with CollectionMatchType."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_match_type = Mock(spec=Atspi.CollectionMatchType)
        mock_match_type.value_nick = "all"

        result = axutils_debug.as_string(mock_match_type)
        assert result == "all"

    def test_as_string_text_granularity(self, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.as_string with TextGranularity."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_granularity = Mock(spec=Atspi.TextGranularity)
        mock_granularity.value_nick = "char"

        result = axutils_debug.as_string(mock_granularity)
        assert result == "char"

    def test_as_string_scroll_type(self, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.as_string with ScrollType."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_scroll_type = Mock(spec=Atspi.ScrollType)
        mock_scroll_type.value_nick = "top-left"

        result = axutils_debug.as_string(mock_scroll_type)
        assert result == "top-left"

    def test_as_string_function_with_self(self, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.as_string with function that has __self__."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()

        def test_function():
            pass

        # Mock function with __self__ attribute
        test_function.__module__ = "test_module"
        test_function.__name__ = "test_function"
        test_function.__self__ = Mock()
        test_function.__self__.__class__.__name__ = "TestClass"

        result = axutils_debug.as_string(test_function)
        assert "test_module.TestClass.test_function" in result

    def test_as_string_method_without_self(self, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.as_string with method without __self__."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()

        # Create a method mock without __self__
        mock_method = Mock(spec=types.MethodType)
        mock_method.__name__ = "test_method"

        # Remove __self__ attribute
        if hasattr(mock_method, "__self__"):
            delattr(mock_method, "__self__")

        result = axutils_debug.as_string(mock_method)
        assert result == "test_method"

    def test_as_string_frameinfo_unknown_module(self, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.as_string with FrameInfo unknown module."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_frameinfo = Mock(spec=inspect.FrameInfo)
        mock_frameinfo.filename = "/unknown/path/file.py"
        mock_frameinfo.function = "test_function"
        mock_frameinfo.lineno = 42

        result = axutils_debug.as_string(mock_frameinfo)
        assert "file.test_function:42" in result

    def test_relations_as_string(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.relations_as_string."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Invalid object
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.is_valid", lambda obj: False)
        result = axutils_debug.relations_as_string(mock_obj)
        assert result == ""

        # Scenario: Valid object with relations
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.is_valid", lambda obj: True)

        # Mock relation
        mock_relation = Mock()
        mock_relation_type = Mock()
        mock_relation_type.value_name = "ATSPI_RELATION_LABELLED_BY"
        mock_relation.get_relation_type.return_value = mock_relation_type

        # Mock relation targets
        mock_target = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXUtilitiesRelation.get_relations",
            lambda obj: [mock_relation]
        )
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXUtilitiesRelation.get_relation_targets_for_debugging",
            lambda obj, rel_type: [mock_target]
        )
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_role_name", lambda obj: "label"
        )
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.get_name", lambda obj: "Username")

        result = axutils_debug.relations_as_string(mock_obj)
        assert "labelled-by" in result
        assert "label: 'Username'" in result

        # Scenario: Dead target object
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.get_role_name", lambda obj: "")
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.get_name", lambda obj: "")

        result = axutils_debug.relations_as_string(mock_obj)
        assert "labelled-by" in result
        assert "DEAD" in result

    def test_text_for_debugging_glib_error(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.text_for_debugging with GLib.GError."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Object supports text but raises GLib.GError
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.supports_text", lambda obj: True)

        def mock_get_text_with_error(unused_obj, unused_start, unused_end):
            raise GLib.GError("Access error")

        monkeypatch.setattr(Atspi.Text, "get_text", mock_get_text_with_error)
        monkeypatch.setattr(Atspi.Text, "get_character_count", lambda obj: 10)

        result = axutils_debug.text_for_debugging(mock_obj)
        assert result == ""

    def test_object_details_as_string_complete(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesDebugging.object_details_as_string complete functionality."""
        _ = mock_orca_dependencies  # unused but required
        axutils_debug = load_debugging_module()
        mock_obj = Mock(spec=Atspi.Accessible)

        # Scenario: Valid object with all details
        monkeypatch.setattr("orca.ax_utilities_debugging.AXObject.is_dead", lambda obj: False)

        # Mock all the AXObject methods used in object_details_as_string
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXUtilitiesApplication.application_as_string",
            lambda obj: "TestApp"
        )
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_name", lambda obj: "button name"
        )
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_role_name", lambda obj: "button"
        )
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_description", lambda obj: "button desc"
        )
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_help_text", lambda obj: "button help"
        )
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_accessible_id", lambda obj: "btn1"
        )
        monkeypatch.setattr(
            "orca.ax_utilities_debugging.AXObject.get_path", lambda obj: [0, 1, 2]
        )

        # Mock the debugging methods
        monkeypatch.setattr(
            axutils_debug, "state_set_as_string", lambda obj: "focused, visible"
        )
        monkeypatch.setattr(
            axutils_debug, "relations_as_string", lambda obj: "labelled-by: [label]"
        )
        monkeypatch.setattr(axutils_debug, "actions_as_string", lambda obj: "click, focus")
        monkeypatch.setattr(axutils_debug, "interfaces_as_string", lambda obj: "Action, Component")
        monkeypatch.setattr(axutils_debug, "attributes_as_string", lambda obj: "level:1")
        monkeypatch.setattr(axutils_debug, "text_for_debugging", lambda obj: "button text")

        # Test with include_app=True (default)
        result = axutils_debug.object_details_as_string(mock_obj)
        assert "app='TestApp'" in result
        assert "name='button name'" in result
        assert "role='button'" in result
        assert "axid='btn1'" in result
        assert "description='button desc'" in result
        assert "help='button help'" in result
        assert "states='focused, visible'" in result
        assert "relations='labelled-by: [label]'" in result
        assert "actions='click, focus'" in result
        assert "interfaces='Action, Component'" in result
        assert "attributes='level:1'" in result
        assert "text='button text'" in result
        assert "path=[0, 1, 2]" in result

        # Test with include_app=False
        result = axutils_debug.object_details_as_string(mock_obj, include_app=False)
        assert "app='TestApp'" not in result
        assert "name='button name'" in result
        assert "role='button'" in result

        # Test with custom indent
        result = axutils_debug.object_details_as_string(mock_obj, indent="  ")
        assert "  app='TestApp' name='button name'" in result
