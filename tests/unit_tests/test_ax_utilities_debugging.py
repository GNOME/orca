# Unit tests for ax_utilities_debugging.py methods.
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
# pylint: disable=too-many-public-methods
# pylint: disable=import-outside-toplevel

"""Unit tests for ax_utilities_debugging.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext

@pytest.mark.unit
class TestAXUtilitiesDebugging:
    """Test debugging utility methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Returns dependencies for ax_utilities_debugging module testing."""

        additional_modules = ["orca.ax_utilities_application", "orca.ax_utilities_relation"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.is_valid = test_context.Mock(return_value=True)
        ax_object_class_mock.is_dead = test_context.Mock(return_value=False)
        ax_object_class_mock.get_name = test_context.Mock(return_value="test-object")
        ax_object_class_mock.get_role_name = test_context.Mock(return_value="unknown")
        ax_object_class_mock.get_description = test_context.Mock(return_value="")
        ax_object_class_mock.get_help_text = test_context.Mock(return_value="")
        ax_object_class_mock.get_accessible_id = test_context.Mock(return_value="")
        ax_object_class_mock.get_path = test_context.Mock(return_value=[])
        ax_object_class_mock.get_n_actions = test_context.Mock(return_value=0)
        ax_object_class_mock.get_action_name = test_context.Mock(return_value="")
        ax_object_class_mock.get_action_key_binding = test_context.Mock(return_value="")
        ax_object_class_mock.get_attributes_dict = test_context.Mock(return_value={})
        ax_object_class_mock.get_state_set = test_context.Mock(
            return_value=test_context.Mock()
        )
        ax_object_class_mock.supports_text = test_context.Mock(return_value=False)
        essential_modules["orca.ax_object"].AXObject = ax_object_class_mock

        app_class_mock = test_context.Mock()
        app_class_mock.application_as_string = test_context.Mock(return_value="TestApp")
        essential_modules["orca.ax_utilities_application"].AXUtilitiesApplication = app_class_mock

        relation_class_mock = test_context.Mock()
        relation_class_mock.get_relations = test_context.Mock(return_value=[])
        relation_class_mock.get_relation_targets_for_debugging = test_context.Mock(
            return_value=[]
        )
        essential_modules["orca.ax_utilities_relation"].AXUtilitiesRelation = relation_class_mock

        return essential_modules

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
    def test_format_string(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, input_string, expected_result, test_context
    ) -> None:
        """Test AXUtilitiesDebugging._format_string."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        result = AXUtilitiesDebugging._format_string(input_string)  # pylint: disable=protected-access
        assert result == expected_result

    def test_as_string_accessible_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.as_string with Atspi.Accessible objects."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_role_name", return_value="button"
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_name", return_value="OK"
        )
        result = AXUtilitiesDebugging.as_string(mock_obj)
        assert "button: 'OK'" in result
        assert hex(id(mock_obj)) in result

    def test_as_string_accessible_dead_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.as_string handles dead accessible objects."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_role_name", return_value=""
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_name", return_value=""
        )
        result = AXUtilitiesDebugging.as_string(mock_obj)
        assert "[DEAD" in result

    def test_as_string_event_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.as_string with Atspi.Event objects."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "focus:in"
        mock_event.source = test_context.Mock(spec=Atspi.Accessible)
        mock_event.detail1 = 0
        mock_event.detail2 = 0
        mock_event.any_data = None

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_role_name", return_value="button"
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_name", return_value="OK"
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXUtilitiesApplication.application_as_string",
            return_value="TestApp"
        )
        result = AXUtilitiesDebugging.as_string(mock_event)
        assert "focus:in for" in result
        assert "TestApp" in result

    def test_actions_as_string(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.actions_as_string."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_n_actions", return_value=2
        )

        def mock_get_action_name(unused_obj, index):
            return ["click", "focus"][index]

        def mock_get_action_key_binding(unused_obj, index):
            return ["Return", ""][index]

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_action_name", new=mock_get_action_name
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_action_key_binding",
            new=mock_get_action_key_binding
        )
        result = AXUtilitiesDebugging.actions_as_string(mock_obj)
        assert "click (Return)" in result
        assert "focus" in result
        assert ";" in result

    def test_attributes_as_string(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.attributes_as_string."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        attributes_dict = {"level": "2", "placeholder-text": "Enter name"}
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_attributes_dict", return_value=attributes_dict
        )
        result = AXUtilitiesDebugging.attributes_as_string(mock_obj)
        assert "level:2" in result
        assert "placeholder-text:Enter name" in result
        assert ", " in result

    def test_interfaces_as_string(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.interfaces_as_string."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.is_valid", return_value=False
        )
        result = AXUtilitiesDebugging.interfaces_as_string(mock_obj)
        assert result == ""

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
            test_context.patch(
                f"orca.ax_utilities_debugging.AXObject.{method_name}", return_value=return_value
            )
        result = AXUtilitiesDebugging.interfaces_as_string(mock_obj)
        assert "Action" in result
        assert "Component" in result
        assert "Text" in result
        assert ", " in result

    def test_state_set_as_string(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.state_set_as_string."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.is_valid", return_value=False
        )
        result = AXUtilitiesDebugging.state_set_as_string(mock_obj)
        assert result == ""

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.is_valid", return_value=True
        )

        mock_state_set = test_context.Mock()
        mock_state1 = test_context.Mock()
        mock_state1.value_name = "ATSPI_STATE_FOCUSED"
        mock_state2 = test_context.Mock()
        mock_state2.value_name = "ATSPI_STATE_VISIBLE"
        mock_state_set.get_states.return_value = [mock_state1, mock_state2]
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_state_set", return_value=mock_state_set
        )
        result = AXUtilitiesDebugging.state_set_as_string(mock_obj)
        assert "focused" in result
        assert "visible" in result
        assert ", " in result

    @pytest.mark.parametrize(
        "supports_text, should_raise_error, expected_result",
        [
            pytest.param(False, False, "", id="no_text_support"),
            pytest.param(True, False, "Sample text content", id="success_case"),
            pytest.param(True, True, "", id="glib_error"),
        ],
    )
    def test_text_for_debugging(
        self,
        test_context: OrcaTestContext,
        supports_text: bool,
        should_raise_error: bool,
        expected_result: str,
    ) -> None:
        """Test AXUtilitiesDebugging.text_for_debugging with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.supports_text", return_value=supports_text
        )

        if supports_text:
            if should_raise_error:

                def mock_get_text_with_error(unused_obj, unused_start, unused_end):
                    raise GLib.GError("Access error")

                test_context.patch_object(Atspi.Text, "get_text", new=mock_get_text_with_error)
            else:

                def mock_get_text(unused_obj, unused_start, unused_end):
                    return "Sample text content"

                test_context.patch_object(Atspi.Text, "get_text", new=mock_get_text)

            character_count = 10 if should_raise_error else 20
            test_context.patch_object(
                Atspi.Text, "get_character_count", return_value=character_count
            )

        result = AXUtilitiesDebugging.text_for_debugging(mock_obj)
        assert result == expected_result

    def test_as_string_role_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.as_string with role object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_role = test_context.Mock(spec=Atspi.Role)
        mock_role.value_nick = "button"
        result = AXUtilitiesDebugging.as_string(mock_role)
        assert "button" in result

    def test_as_string_rect_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.as_string with rect object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_rect = test_context.Mock(spec=Atspi.Rect)
        mock_rect.x = 10
        mock_rect.y = 20
        mock_rect.width = 100
        mock_rect.height = 200
        result = AXUtilitiesDebugging.as_string(mock_rect)
        assert "(x:10, y:20, width:100, height:200)" in result

    def test_as_string_collection_objects(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.as_string with collection objects."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging

        test_list = ["item1", "item2"]
        result = AXUtilitiesDebugging.as_string(test_list)
        assert "[item1, item2]" in result

        test_dict = {"key1": "value1", "key2": "value2"}
        result = AXUtilitiesDebugging.as_string(test_dict)
        assert "{'key1': 'value1'" in result

    def test_object_details_as_string_basic(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.object_details_as_string basic functionality."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging

        non_accessible = "not an accessible"
        result = AXUtilitiesDebugging.object_details_as_string(non_accessible)
        assert result == ""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.is_dead", return_value=True
        )
        result = AXUtilitiesDebugging.object_details_as_string(mock_obj)
        assert result == "(exception fetching data)"

    def test_object_event_details_as_string(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.object_event_details_as_string."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "mouse:button"
        result = AXUtilitiesDebugging.object_event_details_as_string(mock_event)
        assert result == ""

        mock_event.type = "object:state-changed:focused"
        mock_event.source = test_context.Mock(spec=Atspi.Accessible)
        mock_event.any_data = test_context.Mock(spec=Atspi.Accessible)

        def mock_object_details(obj, indent="", unused_include_app=True):
            if obj == mock_event.source:
                return f"{indent}SOURCE DETAILS"
            if obj == mock_event.any_data:
                return f"{indent}ANY_DATA DETAILS"
            return ""

        test_context.patch_object(
            AXUtilitiesDebugging, "object_details_as_string", new=mock_object_details
        )
        result = AXUtilitiesDebugging.object_event_details_as_string(mock_event)
        assert "EVENT SOURCE:" in result
        assert "SOURCE DETAILS" in result
        assert "EVENT ANY DATA:" in result
        assert "ANY_DATA DETAILS" in result

        mock_event.any_data = None

        def mock_object_details_no_any_data(obj, indent="", unused_include_app=True):
            if obj == mock_event.source:
                return f"{indent}SOURCE DETAILS"
            return ""

        test_context.patch_object(
            AXUtilitiesDebugging, "object_details_as_string", new=mock_object_details_no_any_data
        )
        result = AXUtilitiesDebugging.object_event_details_as_string(mock_event)
        assert "EVENT SOURCE:" in result
        assert "SOURCE DETAILS" in result
        assert "EVENT ANY DATA:" not in result

    def test_relations_as_string(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.relations_as_string."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.is_valid", return_value=False
        )
        result = AXUtilitiesDebugging.relations_as_string(mock_obj)
        assert result == ""

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.is_valid", return_value=True
        )

        mock_relation = test_context.Mock()
        mock_relation_type = test_context.Mock()
        mock_relation_type.value_name = "ATSPI_RELATION_LABELLED_BY"
        mock_relation.get_relation_type.return_value = mock_relation_type

        mock_target = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.ax_utilities_debugging.AXUtilitiesRelation.get_relations",
            return_value=[mock_relation]
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXUtilitiesRelation.get_relation_targets_for_debugging",
            side_effect=lambda obj, rel_type: [mock_target]
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_role_name", return_value="label"
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_name", return_value="Username"
        )
        result = AXUtilitiesDebugging.relations_as_string(mock_obj)
        assert "labelled-by" in result
        assert "label: 'Username'" in result

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_role_name", return_value=""
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_name", return_value=""
        )
        result = AXUtilitiesDebugging.relations_as_string(mock_obj)
        assert "labelled-by" in result
        assert "DEAD" in result

    def test_object_details_as_string_complete(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesDebugging.object_details_as_string complete functionality."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_debugging import AXUtilitiesDebugging
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.is_dead", return_value=False
        )

        test_context.patch(
            "orca.ax_utilities_debugging.AXUtilitiesApplication.application_as_string",
            return_value="TestApp"
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_name", return_value="button name"
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_role_name", return_value="button"
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_description", return_value="button desc"
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_help_text", return_value="button help"
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_accessible_id", return_value="btn1"
        )
        test_context.patch(
            "orca.ax_utilities_debugging.AXObject.get_path", return_value=[0, 1, 2]
        )

        test_context.patch_object(
            AXUtilitiesDebugging, "state_set_as_string", return_value="focused, visible"
        )
        test_context.patch_object(
            AXUtilitiesDebugging, "relations_as_string", return_value="labelled-by: [label]"
        )
        test_context.patch_object(
            AXUtilitiesDebugging, "actions_as_string", return_value="click, focus"
        )
        test_context.patch_object(
            AXUtilitiesDebugging, "interfaces_as_string", return_value="Action, Component"
        )
        test_context.patch_object(
            AXUtilitiesDebugging, "attributes_as_string", return_value="level:1"
        )
        test_context.patch_object(
            AXUtilitiesDebugging, "text_for_debugging", return_value="button text"
        )

        result = AXUtilitiesDebugging.object_details_as_string(mock_obj)
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

        result = AXUtilitiesDebugging.object_details_as_string(mock_obj, include_app=False)
        assert "app='TestApp'" not in result
        assert "name='button name'" in result
        assert "role='button'" in result

        result = AXUtilitiesDebugging.object_details_as_string(mock_obj, indent="  ")
        assert "  app='TestApp' name='button name'" in result
