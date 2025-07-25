# Unit tests for ax_utilities.py main AXUtilities class methods.
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

"""Unit tests for ax_utilities.py main AXUtilities class methods."""

import threading
from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache  # pylint: disable=import-error

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi



@pytest.mark.unit
class TestAXUtilities:
    """Test AXUtilities class methods."""

    def setup_method(self):
        """Clear any existing state before each test."""

        try:
            from orca.ax_utilities import AXUtilities
            AXUtilities._clear_all_dictionaries("test setup")
        except ImportError:
            pass

    @pytest.mark.parametrize(
        "method_name, attribute_value, expected_result",
        [
            pytest.param("has_explicit_name", "true", True, id="explicit_name_true"),
            pytest.param("has_explicit_name", "false", False, id="explicit_name_false"),
        ],
    )
    def test_attribute_based_methods(
        self,
        monkeypatch,
        method_name,
        attribute_value,
        expected_result,
        mock_orca_dependencies,
    ):
        """Test AXUtilities attribute-based methods."""

        import sys

        # Configure AXObject module mock
        ax_object_module_mock = Mock()
        ax_object_class_mock = Mock()
        ax_object_class_mock.is_valid = Mock(return_value=True)
        ax_object_class_mock.get_attribute = Mock(return_value=attribute_value)
        ax_object_class_mock.get_index_in_parent = Mock(return_value=0)
        ax_object_class_mock.get_parent = Mock(return_value=None)
        ax_object_class_mock.get_child_count = Mock(return_value=0)
        ax_object_module_mock.AXObject = ax_object_class_mock

        # Configure AXUtilitiesRelation module mock
        relation_module_mock = Mock()
        relation_class_mock = Mock()
        relation_class_mock.get_flows_to = Mock(return_value=[])
        relation_class_mock.get_flows_from = Mock(return_value=[])
        relation_module_mock.AXUtilitiesRelation = relation_class_mock

        # Set up sys.modules mocks
        monkeypatch.setitem(sys.modules, "orca.ax_object", ax_object_module_mock)
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_relation", relation_module_mock)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        method = getattr(AXUtilities, method_name)
        result = method(mock_obj)
        assert result is expected_result

    @pytest.mark.parametrize(
        "method_name",
        [
            pytest.param("get_next_object", id="next_object"),
            pytest.param("get_previous_object", id="previous_object"),
        ],
    )
    def test_navigation_methods_with_invalid_object(
        self,
        monkeypatch,
        method_name,
        mock_orca_dependencies,
    ):
        """Test AXUtilities navigation methods with invalid objects."""

        import sys

        # Configure AXObject module mock
        ax_object_module_mock = Mock()
        ax_object_class_mock = Mock()
        ax_object_class_mock.is_valid = Mock(return_value=False)
        ax_object_class_mock.get_attribute = Mock(return_value="")
        ax_object_class_mock.get_index_in_parent = Mock(return_value=0)
        ax_object_class_mock.get_parent = Mock(return_value=None)
        ax_object_class_mock.get_child_count = Mock(return_value=0)
        ax_object_module_mock.AXObject = ax_object_class_mock

        # Configure AXUtilitiesRelation module mock
        relation_module_mock = Mock()
        relation_class_mock = Mock()
        relation_class_mock.get_flows_to = Mock(return_value=[])
        relation_class_mock.get_flows_from = Mock(return_value=[])
        relation_module_mock.AXUtilitiesRelation = relation_class_mock

        # Set up sys.modules mocks
        monkeypatch.setitem(sys.modules, "orca.ax_object", ax_object_module_mock)
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_relation", relation_module_mock)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        method = getattr(AXUtilities, method_name)
        result = method(mock_obj)
        assert result is None

    def test_get_on_screen_objects_leaf_node(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._get_on_screen_objects with leaf node."""

        import sys

        # Configure AXObject module mock
        ax_object_module_mock = Mock()
        ax_object_class_mock = Mock()
        ax_object_class_mock.is_valid = Mock(return_value=True)
        ax_object_class_mock.get_attribute = Mock(return_value="")
        ax_object_class_mock.get_index_in_parent = Mock(return_value=0)
        ax_object_class_mock.get_parent = Mock(return_value=None)
        ax_object_class_mock.get_child_count = Mock(return_value=0)
        ax_object_module_mock.AXObject = ax_object_class_mock

        # Configure AXUtilitiesRelation module mock
        relation_module_mock = Mock()
        relation_class_mock = Mock()
        relation_class_mock.get_flows_to = Mock(return_value=[])
        relation_class_mock.get_flows_from = Mock(return_value=[])
        relation_module_mock.AXUtilitiesRelation = relation_class_mock

        # Set up sys.modules mocks
        monkeypatch.setitem(sys.modules, "orca.ax_object", ax_object_module_mock)
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_relation", relation_module_mock)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        cancellation_event = threading.Event()
        monkeypatch.setattr(AXUtilities, "is_on_screen", lambda obj, bbox: True)
        monkeypatch.setattr(AXUtilities, "treat_as_leaf_node", lambda x: True)
        result = AXUtilities._get_on_screen_objects(mock_obj, cancellation_event)
        assert result == [mock_obj]
