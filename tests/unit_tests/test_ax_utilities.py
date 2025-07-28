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
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines

"""Unit tests for ax_utilities.py main AXUtilities class methods."""

import threading
from unittest.mock import Mock

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from .conftest import clean_module_cache

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

    def _setup_basic_mocks(self, monkeypatch):
        """Set up basic mocks for AXUtilities tests."""
        import sys

        ax_object_module_mock = Mock()
        ax_object_class_mock = Mock()
        ax_object_class_mock.is_valid = Mock(return_value=True)
        ax_object_class_mock.get_attribute = Mock(return_value="")
        ax_object_class_mock.get_index_in_parent = Mock(return_value=0)
        ax_object_class_mock.get_parent = Mock(return_value=None)
        ax_object_class_mock.get_child_count = Mock(return_value=0)
        ax_object_class_mock.get_role = Mock(return_value=Atspi.Role.PANEL)
        ax_object_class_mock.get_name = Mock(return_value="")
        ax_object_class_mock.get_description = Mock(return_value="")
        ax_object_class_mock.get_child = Mock(return_value=None)
        ax_object_class_mock.find_ancestor = Mock(return_value=None)
        ax_object_class_mock.has_action = Mock(return_value=False)
        ax_object_class_mock.clear_cache = Mock()
        ax_object_class_mock.get_attributes_dict = Mock(return_value={})
        ax_object_class_mock.supports_collection = Mock(return_value=False)

        def mock_iter_children(parent, predicate=None):
            all_children = []
            if predicate:
                return [obj for obj in all_children if predicate(obj)]
            return all_children

        ax_object_class_mock.iter_children = mock_iter_children
        ax_object_module_mock.AXObject = ax_object_class_mock

        role_module_mock = Mock()
        role_class_mock = Mock()
        role_class_mock.get_layout_only_roles = Mock(return_value=[Atspi.Role.FILLER])
        role_class_mock.is_layered_pane = Mock(return_value=False)
        role_class_mock.is_desktop_frame = Mock(return_value=False)
        role_class_mock.is_menu = Mock(return_value=False)
        role_class_mock.is_list = Mock(return_value=False)
        role_class_mock.is_combo_box = Mock(return_value=False)
        role_class_mock.is_group = Mock(return_value=False)
        role_class_mock.is_panel = Mock(return_value=False)
        role_class_mock.is_grouping = Mock(return_value=False)
        role_class_mock.is_section = Mock(return_value=False)
        role_class_mock.is_document = Mock(return_value=False)
        role_class_mock.is_tool_bar = Mock(return_value=False)
        role_class_mock.is_page_tab_list = Mock(return_value=False)
        role_class_mock.is_table = Mock(return_value=False)
        role_class_mock.is_table_row = Mock(return_value=False)
        role_class_mock.is_table_cell = Mock(return_value=False)
        role_class_mock.is_label = Mock(return_value=False)
        role_class_mock.children_are_presentational = Mock(return_value=False)
        role_class_mock.is_page_tab = Mock(return_value=False)
        role_class_mock.is_combo_box = Mock(return_value=False)
        role_class_mock.has_role_from_aria = Mock(return_value=False)
        role_class_mock.is_link = Mock(return_value=False)
        role_class_mock.is_heading = Mock(return_value=False)
        role_class_mock.is_dialog_or_alert = Mock(return_value=False)
        role_module_mock.AXUtilitiesRole = role_class_mock

        state_module_mock = Mock()
        state_class_mock = Mock()
        state_class_mock.is_focusable = Mock(return_value=False)
        state_class_mock.is_selectable = Mock(return_value=False)
        state_class_mock.is_expandable = Mock(return_value=False)
        state_class_mock.is_showing = Mock(return_value=True)
        state_class_mock.is_visible = Mock(return_value=True)
        state_class_mock.is_hidden = Mock(return_value=False)
        state_class_mock.is_expanded = Mock(return_value=False)
        state_class_mock.is_focused = Mock(return_value=False)
        state_class_mock.is_editable = Mock(return_value=False)
        state_class_mock.is_active = Mock(return_value=False)
        state_class_mock.is_iconified = Mock(return_value=False)
        state_module_mock.AXUtilitiesState = state_class_mock

        relation_module_mock = Mock()
        relation_class_mock = Mock()
        relation_class_mock.get_flows_to = Mock(return_value=[])
        relation_class_mock.get_flows_from = Mock(return_value=[])
        relation_class_mock.get_is_labelled_by = Mock(return_value=[])
        relation_class_mock.get_is_described_by = Mock(return_value=[])
        relation_module_mock.AXUtilitiesRelation = relation_class_mock

        app_module_mock = Mock()
        app_class_mock = Mock()
        app_class_mock.get_application = Mock(return_value=Mock(spec=Atspi.Accessible))
        app_class_mock.is_application_in_desktop = Mock(return_value=True)
        app_module_mock.AXUtilitiesApplication = app_class_mock

        table_module_mock = Mock()
        table_class_mock = Mock()
        table_class_mock.is_layout_table = Mock(return_value=False)
        table_class_mock.get_table = Mock(return_value=None)
        table_class_mock.get_cell_coordinates = Mock(return_value=(0, 0))
        table_class_mock.get_row_count = Mock(return_value=0)
        table_module_mock.AXTable = table_class_mock

        collection_module_mock = Mock()
        collection_class_mock = Mock()
        collection_class_mock.find_all_descendants = Mock(return_value=[])
        collection_class_mock.find_descendant = Mock(return_value=None)
        collection_class_mock.has_scroll_pane = Mock(return_value=False)
        collection_module_mock.AXUtilitiesCollection = collection_class_mock

        text_module_mock = Mock()
        text_class_mock = Mock()
        text_class_mock.get_all_text = Mock(return_value="")
        text_module_mock.AXText = text_class_mock

        monkeypatch.setitem(sys.modules, "orca.ax_object", ax_object_module_mock)
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_role", role_module_mock)
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_state", state_module_mock)
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_relation", relation_module_mock)
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_application", app_module_mock)
        monkeypatch.setitem(sys.modules, "orca.ax_table", table_module_mock)
        monkeypatch.setitem(sys.modules, "orca.ax_utilities_collection", collection_module_mock)
        monkeypatch.setitem(sys.modules, "orca.ax_text", text_module_mock)

    def test_has_explicit_name_true(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.has_explicit_name with explicit name attribute."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value="true")

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.has_explicit_name(mock_obj)
        assert result is True

    def test_has_explicit_name_false(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.has_explicit_name without explicit name attribute."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value="false")

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.has_explicit_name(mock_obj)
        assert result is False

    def test_is_redundant_object_same_objects(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_redundant_object with same objects."""

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_redundant_object(mock_obj, mock_obj)
        assert result is False

    def test_is_redundant_object_different_names(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_redundant_object with different names."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        def mock_get_name(obj):
            if obj == "obj1":
                return "Name1"
            return "Name2"

        sys.modules["orca.ax_object"].AXObject.get_name = mock_get_name
        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.BUTTON)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_redundant_object("obj1", "obj2")
        assert result is False

    def test_is_redundant_object_same_name_and_role(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_redundant_object with same name and role."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_name = Mock(return_value="Button")
        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.BUTTON)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj1 = Mock(spec=Atspi.Accessible)
        mock_obj2 = Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_redundant_object(mock_obj1, mock_obj2)
        assert result is True

    def test_is_layout_only_layout_only_role(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with layout-only role."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.FILLER)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is True
        assert reason == "has layout-only role"

    def test_is_layout_only_group_without_explicit_name(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with group lacking explicit name."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_group = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "has_explicit_name", Mock(return_value=False))

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is True
        assert reason == "lacks explicit name"

    def test_is_layout_only_group_with_explicit_name(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with group having explicit name."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_group = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "has_explicit_name", Mock(return_value=True))

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == ""

    def test_get_next_object_with_invalid_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_next_object with invalid object."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.is_valid = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_next_object(mock_obj)
        assert result is None

    def test_get_previous_object_with_invalid_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_previous_object with invalid object."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.is_valid = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_previous_object(mock_obj)
        assert result is None

    def test_get_on_screen_objects_leaf_node(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._get_on_screen_objects with leaf node."""

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        cancellation_event = threading.Event()
        monkeypatch.setattr(AXUtilities, "is_on_screen", lambda obj, bbox: True)
        monkeypatch.setattr(AXUtilities, "treat_as_leaf_node", lambda x: True)
        result = AXUtilities._get_on_screen_objects(mock_obj, cancellation_event)
        assert result == [mock_obj]

    def test_sort_by_child_index_needs_sorting(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._sort_by_child_index with unsorted list."""

        mock_obj1, mock_obj2, mock_obj3 = [Mock(spec=Atspi.Accessible) for _ in range(3)]

        def mock_get_index(obj):
            if obj == mock_obj1:
                return 2
            if obj == mock_obj2:
                return 0
            if obj == mock_obj3:
                return 1
            return 0

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_index_in_parent = mock_get_index

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        input_list = [mock_obj1, mock_obj2, mock_obj3]
        result = AXUtilities._sort_by_child_index(input_list)
        assert result == [mock_obj1, mock_obj3, mock_obj2]

    def test_is_layout_only_wrapper_method(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_layout_only wrapper method."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.FILLER)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_layout_only(mock_obj)
        assert result is True

    def test_get_set_size_with_valid_size(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_set_size with valid set size."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value="5")

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_set_size(mock_obj)
        assert result == 5

    def test_get_set_size_is_unknown_true(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_set_size_is_unknown returns True for unknown size."""

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "get_set_size", Mock(return_value=-1))

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_set_size_is_unknown(mock_obj)
        assert result is True

    def test_is_layout_only_layered_pane_in_desktop(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with layered pane inside desktop frame."""

        mock_desktop = Mock(spec=Atspi.Accessible)
        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_layered_pane = Mock(
            return_value=True
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_desktop_frame = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.find_ancestor = Mock(return_value=mock_desktop)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is True
        assert reason == "is inside desktop frame"

    def test_is_layout_only_layered_pane_not_in_desktop(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with layered pane not inside desktop frame."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_layered_pane = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.find_ancestor = Mock(return_value=None)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == ""

    def test_is_layout_only_menu_in_combo_box(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with menu inside combo box."""

        mock_parent = Mock(spec=Atspi.Accessible)
        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_menu = Mock(return_value=True)
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(return_value=True)
        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=mock_parent)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is True
        assert reason == "is inside combo box"

    def test_is_layout_only_list_not_in_combo_box(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with list not inside combo box."""

        mock_parent = Mock(spec=Atspi.Accessible)
        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_list = Mock(return_value=True)
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(
            return_value=False
        )
        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=mock_parent)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == ""

    def test_is_layout_only_section_focusable(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with focusable section."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_section = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_focusable = Mock(
            return_value=True
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == "is focusable"

    def test_is_layout_only_section_not_focusable(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with non-focusable section."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_section = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_focusable = Mock(
            return_value=False
        )
        sys.modules["orca.ax_object"].AXObject.has_action = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is True
        assert reason == "is not interactive"

    def test_is_layout_only_document_with_click_action(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with document having click action."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_document = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_focusable = Mock(
            return_value=False
        )
        sys.modules["orca.ax_object"].AXObject.has_action = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == "has click action"

    def test_is_layout_only_table_layout_table(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with layout table."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table = Mock(return_value=True)
        sys.modules["orca.ax_table"].AXTable.is_layout_table = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is True
        assert reason == "is layout table"

    def test_is_layout_only_table_data_table(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with data table."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table = Mock(return_value=True)
        sys.modules["orca.ax_table"].AXTable.is_layout_table = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == ""

    def test_is_layout_only_table_row_focusable(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with focusable table row."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_focusable = Mock(
            return_value=True
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == "is focusable"

    def test_is_layout_only_table_row_selectable(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with selectable table row."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_focusable = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_selectable = Mock(
            return_value=True
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == "is selectable"

    def test_is_layout_only_table_row_expandable(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with expandable table row."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_focusable = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_selectable = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_expandable = Mock(
            return_value=True
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == "is expandable"

    def test_is_layout_only_table_row_has_explicit_name(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with table row having explicit name."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_focusable = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_selectable = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_expandable = Mock(
            return_value=False
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "has_explicit_name", Mock(return_value=True))

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == "has explicit name"

    def test_is_layout_only_table_row_layout_only(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with layout-only table row."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_focusable = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_selectable = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_expandable = Mock(
            return_value=False
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "has_explicit_name", Mock(return_value=False))

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is True
        assert reason == "is not focusable, selectable, or expandable and lacks explicit name"

    def test_is_layout_only_other_role_returns_false(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._is_layout_only with role not handled by specific logic."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.BUTTON)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result, reason = AXUtilities._is_layout_only(mock_obj)
        assert result is False
        assert reason == ""

    def test_treat_as_leaf_node_with_child_count(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.treat_as_leaf_node with objects having children."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_child_count = Mock(return_value=3)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is False

    def test_treat_as_leaf_node_without_children(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.treat_as_leaf_node with objects having presentational children."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.children_are_presentational = Mock(
            return_value=True
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_page_tab = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is True

    def test_is_on_screen_with_showing_and_visible(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_on_screen with showing and visible object."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_visible = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_on_screen(mock_obj)
        assert result is True

    def test_is_on_screen_with_hidden_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_on_screen with hidden object."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_visible = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_hidden = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_on_screen(mock_obj)
        assert result is False

    def test_has_visible_caption_without_label(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.has_visible_caption without visible label."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_label = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.has_visible_caption(mock_obj)
        assert result is False

    def test_get_displayed_label_with_name(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_displayed_label with labelling objects."""

        mock_label1 = Mock(spec=Atspi.Accessible)
        mock_label2 = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_labelled_by = Mock(
            return_value=[mock_label1, mock_label2]
        )

        def mock_get_name(obj):
            if obj == mock_label1:
                return "Button"
            if obj == mock_label2:
                return "Label"
            return ""

        sys.modules["orca.ax_object"].AXObject.get_name = mock_get_name

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_displayed_label(mock_obj)
        assert result == "Button Label"

    def test_get_displayed_description_with_description(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_displayed_description with describing objects."""

        mock_desc1 = Mock(spec=Atspi.Accessible)
        mock_desc2 = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_described_by = Mock(
            return_value=[mock_desc1, mock_desc2]
        )

        def mock_get_name(obj):
            if obj == mock_desc1:
                return "Button"
            if obj == mock_desc2:
                return "description"
            return ""

        sys.modules["orca.ax_object"].AXObject.get_name = mock_get_name

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_displayed_description(mock_obj)
        assert result == "Button description"

    def test_get_heading_level_with_level(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_heading_level with heading level."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_heading = Mock(return_value=True)
        sys.modules["orca.ax_object"].AXObject.get_attributes_dict = Mock(
            return_value={"level": "2"}
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_heading_level(mock_obj)
        assert result == 2

    def test_get_heading_level_invalid(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_heading_level with invalid level."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_heading = Mock(return_value=True)
        sys.modules["orca.ax_object"].AXObject.get_attributes_dict = Mock(
            return_value={"level": "invalid"}
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_heading_level(mock_obj)
        assert result == 0

    def test_is_message_dialog_with_alert_dialog(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_message_dialog with alert dialog."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "get_all_widgets", Mock(return_value=[]))

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is True

    def test_is_message_dialog_with_regular_dialog(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_message_dialog with regular dialog."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.DIALOG)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is False

    def test_can_be_active_window_with_dialog(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.can_be_active_window with dialog window."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_active = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_iconified = Mock(
            return_value=False
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.can_be_active_window(mock_obj)
        assert result is True

    def test_can_be_active_window_with_hidden_window(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.can_be_active_window with hidden window."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.FRAME)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(
            return_value=False
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.can_be_active_window(mock_obj)
        assert result is False

    def test_is_unfocused_alert_or_dialog_with_alert(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_unfocused_alert_or_dialog with alert."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.get_child_count = Mock(return_value=1)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "can_be_active_window", Mock(return_value=False))

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_unfocused_alert_or_dialog(mock_obj)
        assert result is True

    def test_is_unfocused_alert_or_dialog_with_focused_dialog(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities.is_unfocused_alert_or_dialog with focused dialog."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.DIALOG)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_focused = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_unfocused_alert_or_dialog(mock_obj)
        assert result is False

    def test_get_unfocused_alerts_and_dialogs_with_alerts(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities.get_unfocused_alerts_and_dialogs with alert objects."""

        mock_alert1 = Mock(spec=Atspi.Accessible)
        mock_alert2 = Mock(spec=Atspi.Accessible)
        mock_normal = Mock(spec=Atspi.Accessible)
        mock_app = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_application"].AXUtilitiesApplication.get_application = Mock(
            return_value=mock_app
        )

        sys.modules["orca.ax_object"].AXObject.find_ancestor = Mock(return_value=None)

        def mock_iter_children(parent, predicate=None):
            if parent == mock_app:
                all_children = [mock_alert1, mock_alert2, mock_normal]
                if predicate:
                    return [obj for obj in all_children if predicate(obj)]
                return all_children
            return []

        sys.modules["orca.ax_object"].AXObject.iter_children = mock_iter_children

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        def mock_is_unfocused(obj):
            return obj in [mock_alert1, mock_alert2]

        monkeypatch.setattr(AXUtilities, "is_unfocused_alert_or_dialog", mock_is_unfocused)

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_unfocused_alerts_and_dialogs(mock_obj)
        assert result == [mock_alert1, mock_alert2]

    def test_get_all_widgets_with_button_predicate(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_all_widgets returns widget objects."""

        mock_button1 = Mock(spec=Atspi.Accessible)
        mock_button2 = Mock(spec=Atspi.Accessible)
        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.get_widget_roles = Mock(
            return_value=[Atspi.Role.PUSH_BUTTON, Atspi.Role.CHECK_BOX]
        )

        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.find_all_with_role_and_all_states = Mock(
            return_value=[mock_button1, mock_button2]
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_all_widgets(mock_obj, must_be_showing_and_visible=True)
        assert result == [mock_button1, mock_button2]

    def test_get_default_button_with_default_button(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_default_button with default button."""

        mock_default_button = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)

        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.find_default_button = Mock(return_value=mock_default_button)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_default_button(mock_obj)
        assert result == mock_default_button

    def test_get_focused_object_with_focused_descendant(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_focused_object with focused descendant."""

        mock_focused = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)

        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.find_focused_object = Mock(return_value=mock_focused)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_focused_object(mock_obj)
        assert result == mock_focused

    def test_get_info_bar_with_info_bar(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_info_bar with info bar descendant."""

        mock_info_bar = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)

        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.find_info_bar = Mock(
            return_value=mock_info_bar
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_info_bar(mock_obj)
        assert result == mock_info_bar

    def test_get_status_bar_with_status_bar(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_status_bar with status bar descendant."""

        mock_status_bar = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)

        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.find_status_bar = Mock(
            return_value=mock_status_bar
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_status_bar(mock_obj)
        assert result == mock_status_bar

    def test_clear_all_cache_now_with_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.clear_all_cache_now with specific object."""

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        AXUtilities.clear_all_cache_now(mock_obj, "test reason")

    def test_clear_all_cache_now_without_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.clear_all_cache_now without specific object."""

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        AXUtilities.clear_all_cache_now(None, "test reason")

    def test_get_set_members_with_basic_set(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_set_members with basic set."""

        mock_member1 = Mock(spec=Atspi.Accessible)
        mock_member2 = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(
            AXUtilities, "_get_set_members", Mock(return_value=[mock_member1, mock_member2])
        )

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_set_members(mock_obj)
        assert result == [mock_member1, mock_member2]

    def test_get_set_members_with_empty_set(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_set_members with empty set."""

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "_get_set_members", Mock(return_value=[]))

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_set_members(mock_obj)
        assert result == []

    def test_find_active_window_with_active_window(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.find_active_window with active window."""

        mock_active_window = Mock(spec=Atspi.Accessible)
        mock_app = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules[
            "orca.ax_utilities_application"
        ].AXUtilitiesApplication.get_all_applications = Mock(return_value=[mock_app])

        sys.modules["orca.ax_object"].AXObject.iter_children = Mock(
            return_value=[mock_active_window]
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "can_be_active_window", lambda x: x == mock_active_window)

        result = AXUtilities.find_active_window()
        assert result == mock_active_window

    def test_find_active_window_with_no_active_window(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.find_active_window with no active window."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules[
            "orca.ax_utilities_application"
        ].AXUtilitiesApplication.get_all_applications = Mock(return_value=[])

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.find_active_window()
        assert result is None

    def test_start_cache_clearing_thread(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.start_cache_clearing_thread."""

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        AXUtilities.start_cache_clearing_thread()

    def test_get_on_screen_objects_with_invalid_root(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_on_screen_objects with invalid root."""

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.is_valid = Mock(return_value=False)

        sys.modules["orca.ax_table"].AXTable.iter_visible_cells = Mock(return_value=[])

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        mock_obj = Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_on_screen_objects(mock_obj)
        assert result == []

    def test_clear_all_dictionaries_with_reason(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._clear_all_dictionaries with reason."""

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        AXUtilities.SET_MEMBERS = {"test": "data"}
        AXUtilities.IS_LAYOUT_ONLY = {"test": "data"}

        AXUtilities._clear_all_dictionaries("test reason")

        assert not AXUtilities.SET_MEMBERS
        assert not AXUtilities.IS_LAYOUT_ONLY

    def test_clear_all_dictionaries_without_reason(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._clear_all_dictionaries without reason."""

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        AXUtilities.SET_MEMBERS = {"test": "data"}
        AXUtilities.IS_LAYOUT_ONLY = {"test": "data"}

        AXUtilities._clear_all_dictionaries()

        assert not AXUtilities.SET_MEMBERS
        assert not AXUtilities.IS_LAYOUT_ONLY

    def test_get_nesting_level_list_item(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_nesting_level with list item."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_ancestor1 = Mock(spec=Atspi.Accessible)
        mock_ancestor2 = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_list_item = Mock(return_value=True)
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_list = Mock(return_value=True)

        find_calls = []

        def mock_find_ancestor(obj, pred):
            find_calls.append(obj)
            if obj == mock_obj:
                return mock_ancestor1
            if obj == mock_ancestor1:
                return mock_ancestor2
            return None

        sys.modules["orca.ax_object"].AXObject.find_ancestor = mock_find_ancestor
        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=mock_obj)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_nesting_level(mock_obj)
        assert result == 2

    def test_get_nesting_level_regular_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_nesting_level with regular object."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_ancestor1 = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_list_item = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.have_same_role = Mock(
            return_value=True
        )

        find_calls = []

        def mock_find_ancestor(obj, pred):
            find_calls.append(obj)
            if obj == mock_obj:
                return mock_ancestor1
            return None

        sys.modules["orca.ax_object"].AXObject.find_ancestor = mock_find_ancestor

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_nesting_level(mock_obj)
        assert result == 1

    def test_get_position_in_set_with_posinset_attribute(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_position_in_set with posinset attribute."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value="3")

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == 2

    def test_get_position_in_set_table_row_with_rowindex(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_position_in_set with table row and rowindex."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(return_value=True)

        get_attribute_calls = []

        def mock_get_attribute(obj, attr, use_cache):
            get_attribute_calls.append((obj, attr, use_cache))
            if attr == "posinset":
                return None
            if attr == "rowindex":
                return "5"
            return None

        sys.modules["orca.ax_object"].AXObject.get_attribute = mock_get_attribute

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == 4

    def test_get_position_in_set_fallback_to_set_members(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_position_in_set fallback to set members."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_parent = Mock(spec=Atspi.Accessible)
        mock_member1 = Mock(spec=Atspi.Accessible)
        mock_member2 = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_cell_or_header = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(
            return_value=False
        )

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value=None)

        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=mock_parent)
        sys.modules["orca.ax_object"].AXObject.get_child_count = Mock(return_value=100)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(
            AXUtilities, "get_set_members", lambda x: [mock_member1, mock_obj, mock_member2]
        )

        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == 1

    def test_get_set_members_internal_with_none_container(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities._get_set_members with None container."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities._get_set_members(mock_obj, None)
        assert result == []

    def test_get_set_members_internal_with_member_of_relation(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities._get_set_members with member-of relation."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_container = Mock(spec=Atspi.Accessible)
        mock_member1 = Mock(spec=Atspi.Accessible)
        mock_member2 = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_member_of = Mock(
            return_value=[mock_member1, mock_member2]
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "_sort_by_child_index", lambda x: x)

        result = AXUtilities._get_set_members(mock_obj, mock_container)
        assert result == [mock_member1, mock_member2]

    def test_get_set_members_internal_with_node_parent_relation(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities._get_set_members with node-parent-of relation."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_container = Mock(spec=Atspi.Accessible)
        mock_child1 = Mock(spec=Atspi.Accessible)
        mock_child2 = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_member_of = Mock(
            return_value=[]
        )

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_node_parent_of = Mock(
            return_value=[mock_child1, mock_child2]
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "_sort_by_child_index", lambda x: x)

        result = AXUtilities._get_set_members(mock_obj, mock_container)
        assert result == [mock_child1, mock_child2]

    def test_get_set_members_internal_with_description_values(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities._get_set_members with description values."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_container = Mock(spec=Atspi.Accessible)
        mock_prev = Mock(spec=Atspi.Accessible)
        mock_next = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_member_of = Mock(
            return_value=[]
        )
        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_node_parent_of = Mock(
            return_value=[]
        )

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_description_value = Mock(
            return_value=True
        )

        def mock_get_previous_sibling(obj):
            if obj == mock_obj:
                return mock_prev
            return None

        def mock_get_next_sibling(obj):
            if obj == mock_obj:
                return mock_next
            return None

        sys.modules["orca.ax_object"].AXObject.get_previous_sibling = mock_get_previous_sibling
        sys.modules["orca.ax_object"].AXObject.get_next_sibling = mock_get_next_sibling

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities._get_set_members(mock_obj, mock_container)
        assert len(result) == 3
        assert mock_obj in result
        assert mock_prev in result
        assert mock_next in result

    def test_get_set_members_internal_with_menu_related(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._get_set_members with menu-related objects."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_container = Mock(spec=Atspi.Accessible)
        mock_menu1 = Mock(spec=Atspi.Accessible)
        mock_menu2 = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_member_of = Mock(
            return_value=[]
        )
        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_node_parent_of = Mock(
            return_value=[]
        )

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_description_value = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_menu_related = Mock(
            return_value=True
        )

        sys.modules["orca.ax_object"].AXObject.iter_children = Mock(
            return_value=[mock_menu1, mock_menu2]
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities._get_set_members(mock_obj, mock_container)
        assert result == [mock_menu1, mock_menu2]

    def test_get_set_members_internal_fallback_to_role(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities._get_set_members fallback to role-based matching."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_container = Mock(spec=Atspi.Accessible)
        mock_same_role1 = Mock(spec=Atspi.Accessible)
        mock_same_role2 = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_member_of = Mock(
            return_value=[]
        )
        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_node_parent_of = Mock(
            return_value=[]
        )

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_description_value = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_menu_related = Mock(
            return_value=False
        )

        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.PUSH_BUTTON)

        sys.modules["orca.ax_object"].AXObject.iter_children = Mock(
            return_value=[mock_same_role1, mock_same_role2]
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities._get_set_members(mock_obj, mock_container)
        assert result == [mock_same_role1, mock_same_role2]

    def test_get_next_object_with_flows_to_relation(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_next_object with flows-to relation."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_target = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.is_valid = Mock(return_value=True)

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_flows_to = Mock(
            return_value=[mock_target]
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_next_object(mock_obj)
        assert result == mock_target

    def test_get_next_object_normal_traversal(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_next_object with normal parent-child traversal."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_parent = Mock(spec=Atspi.Accessible)
        mock_next = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.is_valid = Mock(return_value=True)

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_flows_to = Mock(
            return_value=[]
        )

        sys.modules["orca.ax_object"].AXObject.get_index_in_parent = Mock(return_value=0)
        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=mock_parent)
        sys.modules["orca.ax_object"].AXObject.get_child_count = Mock(return_value=3)
        sys.modules["orca.ax_object"].AXObject.get_child = Mock(return_value=mock_next)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_next_object(mock_obj)
        assert result == mock_next

    def test_get_previous_object_with_flows_from_relation(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities.get_previous_object with flows-from relation."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_source = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.is_valid = Mock(return_value=True)

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_flows_from = Mock(
            return_value=[mock_source]
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_previous_object(mock_obj)
        assert result == mock_source

    def test_is_on_screen_not_showing_or_visible(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_on_screen with object not showing or visible."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_visible = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_on_screen(mock_obj)
        assert result is False

    def test_is_on_screen_hidden_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_on_screen with hidden object."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_visible = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_hidden = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_on_screen(mock_obj)
        assert result is False

    def test_is_on_screen_no_size_or_invalid_rect(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_on_screen with no size or invalid rect."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_visible = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_hidden = Mock(return_value=False)

        sys.modules["orca.ax_component"].AXComponent.has_no_size_or_invalid_rect = Mock(
            return_value=True
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_on_screen(mock_obj)
        assert result is True

    def test_is_on_screen_object_off_screen(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_on_screen with object off screen."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_visible = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_hidden = Mock(return_value=False)
        sys.modules["orca.ax_component"].AXComponent.has_no_size_or_invalid_rect = Mock(
            return_value=False
        )

        sys.modules["orca.ax_component"].AXComponent.object_is_off_screen = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_on_screen(mock_obj)
        assert result is False

    def test_is_on_screen_with_bounding_box_no_intersection(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities.is_on_screen with bounding box that doesn't intersect."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_bbox = Mock(spec=Atspi.Rect)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_visible = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_hidden = Mock(return_value=False)
        sys.modules["orca.ax_component"].AXComponent.has_no_size_or_invalid_rect = Mock(
            return_value=False
        )
        sys.modules["orca.ax_component"].AXComponent.object_is_off_screen = Mock(return_value=False)

        sys.modules["orca.ax_component"].AXComponent.object_intersects_rect = Mock(
            return_value=False
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_on_screen(mock_obj, mock_bbox)
        assert result is False

    def test_is_on_screen_fully_on_screen(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_on_screen with fully on-screen object."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_visible = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_hidden = Mock(return_value=False)
        sys.modules["orca.ax_component"].AXComponent.has_no_size_or_invalid_rect = Mock(
            return_value=False
        )
        sys.modules["orca.ax_component"].AXComponent.object_is_off_screen = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_on_screen(mock_obj)
        assert result is True

    def test_has_visible_caption_with_visible_caption(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.has_visible_caption with visible caption."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_caption = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_figure = Mock(return_value=True)
        sys.modules["orca.ax_object"].AXObject.supports_table = Mock(return_value=False)

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_labelled_by = Mock(
            return_value=[mock_caption]
        )

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_caption = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_showing = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_visible = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.has_visible_caption(mock_obj)
        assert result is True

    def test_has_visible_caption_not_figure_or_table(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.has_visible_caption with object that's not figure or table."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_figure = Mock(return_value=False)
        sys.modules["orca.ax_object"].AXObject.supports_table = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.has_visible_caption(mock_obj)
        assert result is False

    def test_get_displayed_description_from_relations(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_displayed_description returns description from relations."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_desc = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_is_described_by = Mock(
            return_value=[mock_desc]
        )

        sys.modules["orca.ax_object"].AXObject.get_name = Mock(return_value="Test description")
        sys.modules["orca.ax_text"].AXText.get_all_text = Mock(return_value="")

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_displayed_description(mock_obj)
        assert result == "Test description"

    def test_get_displayed_description_empty(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_displayed_description with empty description."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_description = Mock(return_value="")

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_displayed_description(mock_obj)
        assert result == ""

    def test_get_position_in_set_with_large_child_count(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_position_in_set with large child count uses index_in_parent."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_parent = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_cell_or_header = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(
            return_value=False
        )

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value=None)

        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=mock_parent)
        sys.modules["orca.ax_object"].AXObject.get_child_count = Mock(return_value=1000)
        sys.modules["orca.ax_object"].AXObject.get_index_in_parent = Mock(return_value=42)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == 42

    def test_get_position_in_set_object_not_in_members(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_position_in_set when object not in set members."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_parent = Mock(spec=Atspi.Accessible)
        mock_other = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_cell_or_header = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(
            return_value=False
        )

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value=None)

        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=mock_parent)
        sys.modules["orca.ax_object"].AXObject.get_child_count = Mock(return_value=10)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "get_set_members", lambda x: [mock_other])

        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == -1

    def test_treat_as_leaf_node_presentational_page_tab(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.treat_as_leaf_node with presentational page tab."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.children_are_presentational = Mock(
            return_value=True
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_page_tab = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is False

    def test_treat_as_leaf_node_presentational_non_page_tab(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities.treat_as_leaf_node with presentational non-page-tab."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.children_are_presentational = Mock(
            return_value=True
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_page_tab = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is True

    def test_treat_as_leaf_node_combo_box_expanded(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.treat_as_leaf_node with expanded combo box."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.children_are_presentational = Mock(
            return_value=False
        )
        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.COMBO_BOX)
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(return_value=True)
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_expanded = Mock(
            return_value=True
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is False

    def test_treat_as_leaf_node_menu_non_aria_expanded(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.treat_as_leaf_node with expanded non-ARIA menu."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.children_are_presentational = Mock(
            return_value=False
        )
        sys.modules["orca.ax_object"].AXObject.get_role = Mock(return_value=Atspi.Role.MENU)
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_menu = Mock(return_value=True)
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.has_role_from_aria = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_expanded = Mock(
            return_value=True
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is False

    def test_get_set_size_combo_box_with_selection(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_set_size with combo box having selection."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_selected = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value=None)

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_cell_or_header = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(return_value=True)

        sys.modules["orca.ax_selection"].AXSelection.get_selected_children = Mock(
            return_value=[mock_selected]
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "get_set_members", lambda x: [Mock(), Mock(), Mock()])

        result = AXUtilities.get_set_size(mock_obj)
        assert result == 3

    def test_get_set_size_table_cell_not_in_row(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_set_size with table cell not in table row."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_parent = Mock(spec=Atspi.Accessible)
        mock_table = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value=None)

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_cell_or_header = Mock(
            return_value=True
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(
            return_value=False
        )

        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=mock_parent)

        sys.modules["orca.ax_table"].AXTable.get_table = Mock(return_value=mock_table)
        sys.modules["orca.ax_table"].AXTable.get_row_count = Mock(return_value=15)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_size(mock_obj)
        assert result == 15

    def test_get_set_size_table_row_with_table(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_set_size with table row."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_table = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value=None)

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(return_value=True)

        sys.modules["orca.ax_table"].AXTable.get_table = Mock(return_value=mock_table)
        sys.modules["orca.ax_table"].AXTable.get_row_count = Mock(return_value=20)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_size(mock_obj)
        assert result == 20

    def test_get_set_size_fallback_to_set_members(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_set_size fallback to set members count."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value=None)

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_cell_or_header = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(
            return_value=False
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(
            AXUtilities, "get_set_members", lambda x: [Mock(), Mock(), Mock(), Mock()]
        )

        result = AXUtilities.get_set_size(mock_obj)
        assert result == 4

    def test_get_set_size_is_unknown_with_indeterminate_state(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities.get_set_size_is_unknown with indeterminate state."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_indeterminate = Mock(
            return_value=True
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_size_is_unknown(mock_obj)
        assert result is True

    def test_get_set_size_is_unknown_table_with_negative_counts(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities.get_set_size_is_unknown with table having negative counts."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_state"].AXUtilitiesState.is_indeterminate = Mock(
            return_value=False
        )

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table = Mock(return_value=True)

        sys.modules["orca.ax_object"].AXObject.get_attributes_dict = Mock(
            return_value={"rowcount": "-1", "colcount": "5"}
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_size_is_unknown(mock_obj)
        assert result is True

    def test_has_explicit_name_true_case(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.has_explicit_name returns True when explicit-name attribute is true."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value="true")

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.has_explicit_name(mock_obj)
        assert result is True

    def test_get_next_object_no_parent(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_next_object when no parent is found."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.is_valid = Mock(return_value=True)

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_flows_to = Mock(
            return_value=[]
        )

        sys.modules["orca.ax_object"].AXObject.get_index_in_parent = Mock(return_value=2)
        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=None)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_next_object(mock_obj)
        assert result is None

    def test_get_previous_object_no_parent(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.get_previous_object when no parent is found."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_object"].AXObject.is_valid = Mock(return_value=True)

        sys.modules["orca.ax_utilities_relation"].AXUtilitiesRelation.get_flows_from = Mock(
            return_value=[]
        )
        sys.modules["orca.ax_object"].AXObject.get_index_in_parent = Mock(return_value=0)
        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=None)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_previous_object(mock_obj)
        assert result is None

    def test_get_position_in_set_table_cell_with_coordinates(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities.get_position_in_set with table cell using coordinates."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_parent = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_row = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table_cell_or_header = Mock(
            return_value=True
        )
        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box = Mock(
            return_value=False
        )
        sys.modules["orca.ax_object"].AXObject.get_attribute = Mock(return_value=None)
        sys.modules["orca.ax_object"].AXObject.get_parent = Mock(return_value=mock_parent)
        sys.modules["orca.ax_table"].AXTable.get_cell_coordinates = Mock(return_value=(3, 2))

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == 3

    def test_is_message_dialog_non_dialog(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_message_dialog with non-dialog object."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=False
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is False

    def test_is_message_dialog_no_collection_support_with_widgets(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities.is_message_dialog without collection support but has widgets."""

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_widget = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "get_all_widgets", Mock(return_value=[mock_widget]))

        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is False

    def test_is_message_dialog_no_collection_support_no_widgets(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilities.is_message_dialog without collection support and no widgets."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        monkeypatch.setattr(AXUtilities, "get_all_widgets", Mock(return_value=[]))

        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is True

    def test_is_message_dialog_has_scroll_pane(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_message_dialog with scroll pane."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)

        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_scroll_pane = Mock(
            return_value=True
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is False

    def test_is_message_dialog_has_split_pane(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_message_dialog with split pane."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)

        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_scroll_pane = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_split_pane = Mock(
            return_value=True
        )

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is False

    def test_is_message_dialog_has_tree_or_tree_table(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_message_dialog with tree or tree table."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)

        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_scroll_pane = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_split_pane = Mock(
            return_value=False
        )
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.has_tree_or_tree_table = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is False

    def test_is_message_dialog_has_combo_box_or_list_box(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_message_dialog with combo box or list box."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)
        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_scroll_pane = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_split_pane = Mock(
            return_value=False
        )
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.has_tree_or_tree_table = Mock(return_value=False)
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.has_combo_box_or_list_box = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is False

    def test_is_message_dialog_has_editable_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_message_dialog with editable object."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)
        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_scroll_pane = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_split_pane = Mock(
            return_value=False
        )
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.has_tree_or_tree_table = Mock(return_value=False)
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.has_combo_box_or_list_box = Mock(return_value=False)
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.has_editable_object = Mock(return_value=True)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is False

    def test_is_message_dialog_true_case(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilities.is_message_dialog returns True when all conditions are met."""

        mock_obj = Mock(spec=Atspi.Accessible)

        self._setup_basic_mocks(monkeypatch)
        import sys

        sys.modules["orca.ax_utilities_role"].AXUtilitiesRole.is_dialog_or_alert = Mock(
            return_value=True
        )
        sys.modules["orca.ax_object"].AXObject.supports_collection = Mock(return_value=True)
        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_scroll_pane = Mock(
            return_value=False
        )
        sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection.has_split_pane = Mock(
            return_value=False
        )
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.has_tree_or_tree_table = Mock(return_value=False)
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.has_combo_box_or_list_box = Mock(return_value=False)
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.has_editable_object = Mock(return_value=False)

        clean_module_cache("orca.ax_utilities")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is True
