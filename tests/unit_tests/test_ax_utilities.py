# Unit tests for ax_utilities.py methods.
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

# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-statements

"""Unit tests for ax_utilities.py methods."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestAXUtilities:
    """Test AXUtilities class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities dependencies."""

        additional_modules = [
            "orca.ax_component",
            "orca.ax_selection",
            "orca.ax_table",
            "orca.ax_text",
            "orca.ax_utilities_application",
            "orca.ax_utilities_collection",
            "orca.ax_utilities_event",
            "orca.ax_utilities_relation",
            "orca.ax_utilities_role",
            "orca.ax_utilities_state",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.is_valid = test_context.Mock(return_value=True)
        ax_object_class_mock.get_attribute = test_context.Mock(return_value="")
        ax_object_class_mock.get_index_in_parent = test_context.Mock(return_value=0)
        ax_object_class_mock.get_parent = test_context.Mock(return_value=None)
        ax_object_class_mock.get_child_count = test_context.Mock(return_value=0)
        ax_object_class_mock.get_role = test_context.Mock(return_value=Atspi.Role.PANEL)
        ax_object_class_mock.get_name = test_context.Mock(return_value="")
        ax_object_class_mock.get_description = test_context.Mock(return_value="")
        ax_object_class_mock.get_child = test_context.Mock(return_value=None)
        ax_object_class_mock.find_ancestor = test_context.Mock(return_value=None)
        ax_object_class_mock.has_action = test_context.Mock(return_value=False)
        ax_object_class_mock.clear_cache = test_context.Mock()
        ax_object_class_mock.get_attributes_dict = test_context.Mock(return_value={})
        ax_object_class_mock.supports_collection = test_context.Mock(return_value=False)

        def mock_iter_children(parent, predicate=None):  # pylint: disable=unused-argument
            all_children = []
            if predicate:
                return [obj for obj in all_children if predicate(obj)]
            return all_children

        ax_object_class_mock.iter_children = mock_iter_children
        essential_modules["orca.ax_object"].AXObject = ax_object_class_mock

        role_class_mock = test_context.Mock()
        role_class_mock.get_layout_only_roles = test_context.Mock(return_value=[Atspi.Role.FILLER])
        role_class_mock.is_layered_pane = test_context.Mock(return_value=False)
        role_class_mock.is_desktop_frame = test_context.Mock(return_value=False)
        role_class_mock.is_menu = test_context.Mock(return_value=False)
        role_class_mock.is_list = test_context.Mock(return_value=False)
        role_class_mock.is_combo_box = test_context.Mock(return_value=False)
        role_class_mock.is_group = test_context.Mock(return_value=False)
        role_class_mock.is_panel = test_context.Mock(return_value=False)
        role_class_mock.is_grouping = test_context.Mock(return_value=False)
        role_class_mock.is_section = test_context.Mock(return_value=False)
        role_class_mock.is_document = test_context.Mock(return_value=False)
        role_class_mock.is_tool_bar = test_context.Mock(return_value=False)
        role_class_mock.is_page_tab_list = test_context.Mock(return_value=False)
        role_class_mock.is_table = test_context.Mock(return_value=False)
        role_class_mock.is_table_row = test_context.Mock(return_value=False)
        role_class_mock.is_table_cell = test_context.Mock(return_value=False)
        role_class_mock.is_label = test_context.Mock(return_value=False)
        role_class_mock.children_are_presentational = test_context.Mock(return_value=False)
        role_class_mock.is_page_tab = test_context.Mock(return_value=False)
        role_class_mock.has_role_from_aria = test_context.Mock(return_value=False)
        role_class_mock.is_link = test_context.Mock(return_value=False)
        role_class_mock.is_heading = test_context.Mock(return_value=False)
        role_class_mock.is_dialog_or_alert = test_context.Mock(return_value=False)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole = role_class_mock

        state_class_mock = test_context.Mock()
        state_class_mock.is_focusable = test_context.Mock(return_value=False)
        state_class_mock.is_selectable = test_context.Mock(return_value=False)
        state_class_mock.is_expandable = test_context.Mock(return_value=False)
        state_class_mock.is_showing = test_context.Mock(return_value=True)
        state_class_mock.is_visible = test_context.Mock(return_value=True)
        state_class_mock.is_hidden = test_context.Mock(return_value=False)
        state_class_mock.is_expanded = test_context.Mock(return_value=False)
        state_class_mock.is_focused = test_context.Mock(return_value=False)
        state_class_mock.is_editable = test_context.Mock(return_value=False)
        state_class_mock.is_active = test_context.Mock(return_value=False)
        state_class_mock.is_iconified = test_context.Mock(return_value=False)
        essential_modules["orca.ax_utilities_state"].AXUtilitiesState = state_class_mock

        relation_class_mock = test_context.Mock()
        relation_class_mock.get_flows_to = test_context.Mock(return_value=[])
        relation_class_mock.get_flows_from = test_context.Mock(return_value=[])
        relation_class_mock.get_is_labelled_by = test_context.Mock(return_value=[])
        relation_class_mock.get_is_described_by = test_context.Mock(return_value=[])
        essential_modules["orca.ax_utilities_relation"].AXUtilitiesRelation = relation_class_mock

        app_class_mock = test_context.Mock()
        app_class_mock.get_application = test_context.Mock(return_value=test_context.Mock())
        app_class_mock.is_application_in_desktop = test_context.Mock(return_value=True)
        essential_modules["orca.ax_utilities_application"].AXUtilitiesApplication = app_class_mock

        table_class_mock = test_context.Mock()
        table_class_mock.is_layout_table = test_context.Mock(return_value=False)
        table_class_mock.get_table = test_context.Mock(return_value=None)
        table_class_mock.get_cell_coordinates = test_context.Mock(return_value=(0, 0))
        table_class_mock.get_row_count = test_context.Mock(return_value=0)
        essential_modules["orca.ax_table"].AXTable = table_class_mock

        collection_class_mock = test_context.Mock()
        collection_class_mock.find_all_descendants = test_context.Mock(return_value=[])
        collection_class_mock.find_descendant = test_context.Mock(return_value=None)
        collection_class_mock.has_scroll_pane = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection = collection_class_mock

        text_class_mock = test_context.Mock()
        text_class_mock.get_all_text = test_context.Mock(return_value="")
        essential_modules["orca.ax_text"].AXText = text_class_mock

        return essential_modules

    def test_has_explicit_name_true(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.has_explicit_name with explicit name attribute."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value="true"
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.has_explicit_name(mock_obj)
        assert result is True

    def test_has_explicit_name_false(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.has_explicit_name without explicit name attribute."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value="false"
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.has_explicit_name(mock_obj)
        assert result is False

    def test_is_redundant_object_same_objects(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.is_redundant_object with same objects."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_redundant_object(mock_obj, mock_obj)
        assert result is False

    def test_is_redundant_object_different_names(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.is_redundant_object with different names."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        def mock_get_name(obj):
            if obj == "obj1":
                return "Name1"
            return "Name2"

        essential_modules["orca.ax_object"].AXObject.get_name = mock_get_name
        essential_modules["orca.ax_object"].AXObject.get_role = test_context.Mock(
            return_value=Atspi.Role.BUTTON
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.is_redundant_object("obj1", "obj2")
        assert result is False

    def test_is_redundant_object_same_name_and_role(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.is_redundant_object with same name and role."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_name = test_context.Mock(
            return_value="Button"
        )
        essential_modules["orca.ax_object"].AXObject.get_role = test_context.Mock(
            return_value=Atspi.Role.BUTTON
        )
        from orca.ax_utilities import AXUtilities

        mock_obj1 = test_context.Mock(spec=Atspi.Accessible)
        mock_obj2 = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_redundant_object(mock_obj1, mock_obj2)
        assert result is True

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "layout_only_role",
                "mocks_config": {"ax_object.get_role": Atspi.Role.FILLER},
                "expected": True,
            },
            {
                "id": "group_without_explicit_name",
                "mocks_config": {
                    "ax_utilities_role.is_group": True,
                    "has_explicit_name": False,
                },
                "expected": True,
            },
            {
                "id": "group_with_explicit_name",
                "mocks_config": {"ax_utilities_role.is_group": True, "has_explicit_name": True},
                "expected": False,
            },
            {
                "id": "layered_pane_in_desktop",
                "mocks_config": {
                    "ax_utilities_role.is_layered_pane": True,
                    "ax_utilities_role.is_desktop_frame": True,
                    "ax_object.find_ancestor": "desktop",
                },
                "expected": True,
            },
            {
                "id": "layered_pane_not_in_desktop",
                "mocks_config": {
                    "ax_utilities_role.is_layered_pane": True,
                    "ax_utilities_role.is_desktop_frame": False,
                    "ax_object.find_ancestor": None,
                },
                "expected": False,
            },
            {
                "id": "menu_in_combo_box",
                "mocks_config": {
                    "ax_utilities_role.is_menu": True,
                    "ax_utilities_role.is_combo_box": True,
                    "ax_object.find_ancestor": "combo_box",
                },
                "expected": True,
            },
            {
                "id": "list_not_in_combo_box",
                "mocks_config": {
                    "ax_utilities_role.is_list": True,
                    "ax_utilities_role.is_combo_box": False,
                    "ax_object.find_ancestor": None,
                },
                "expected": False,
            },
            {
                "id": "section_focusable",
                "mocks_config": {
                    "ax_utilities_role.is_section": True,
                    "ax_utilities_state.is_focusable": True,
                },
                "expected": False,
            },
            {
                "id": "section_not_focusable",
                "mocks_config": {
                    "ax_utilities_role.is_section": True,
                    "ax_utilities_state.is_focusable": False,
                },
                "expected": True,
            },
            {
                "id": "document_with_click_action",
                "mocks_config": {
                    "ax_utilities_role.is_document": True,
                    "ax_object.has_action": True,
                },
                "expected": False,
            },
            {
                "id": "table_layout_table",
                "mocks_config": {
                    "ax_utilities_role.is_table": True,
                    "ax_table.is_layout_table": True,
                },
                "expected": True,
            },
            {
                "id": "table_data_table",
                "mocks_config": {
                    "ax_utilities_role.is_table": True,
                    "ax_table.is_layout_table": False,
                },
                "expected": False,
            },
            {
                "id": "table_row_focusable",
                "mocks_config": {
                    "ax_utilities_role.is_table_row": True,
                    "ax_utilities_state.is_focusable": True,
                },
                "expected": False,
            },
            {
                "id": "table_row_selectable",
                "mocks_config": {
                    "ax_utilities_role.is_table_row": True,
                    "ax_utilities_state.is_focusable": False,
                    "ax_utilities_state.is_selectable": True,
                },
                "expected": False,
            },
            {
                "id": "table_row_expandable",
                "mocks_config": {
                    "ax_utilities_role.is_table_row": True,
                    "ax_utilities_state.is_focusable": False,
                    "ax_utilities_state.is_selectable": False,
                    "ax_utilities_state.is_expandable": True,
                },
                "expected": False,
            },
            {
                "id": "table_row_has_explicit_name",
                "mocks_config": {
                    "ax_utilities_role.is_table_row": True,
                    "ax_utilities_state.is_focusable": False,
                    "ax_utilities_state.is_selectable": False,
                    "ax_utilities_state.is_expandable": False,
                    "has_explicit_name": True,
                },
                "expected": False,
            },
            {
                "id": "table_row_layout_only",
                "mocks_config": {
                    "ax_utilities_role.is_table_row": True,
                    "ax_utilities_state.is_focusable": False,
                    "ax_utilities_state.is_selectable": False,
                    "ax_utilities_state.is_expandable": False,
                    "has_explicit_name": False,
                },
                "expected": True,
            },
            {
                "id": "other_role_returns_false",
                "mocks_config": {"ax_object.get_role": Atspi.Role.BUTTON},
                "expected": False,
            },
            {
                "id": "wrapper_method",
                "mocks_config": {"_is_layout_only": (True, "wrapper test")},
                "expected": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_layout_only_scenarios(  # pylint: disable=too-many-branches,too-many-statements
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXUtilities.is_layout_only with various scenarios."""
        mocks_config = case["mocks_config"]
        expected = case["expected"]
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        for mock_path, mock_value in mocks_config.items():
            if mock_path == "has_explicit_name":
                test_context.patch(
                    "orca.ax_utilities.AXUtilities.has_explicit_name",
                    return_value=mock_value
                )
            elif mock_path == "_is_layout_only":
                test_context.patch(
                    "orca.ax_utilities.AXUtilities._is_layout_only",
                    return_value=mock_value
                )
            elif mock_path.startswith("ax_object.find_ancestor"):
                if mock_value == "desktop":
                    mock_desktop = test_context.Mock(spec=Atspi.Accessible)
                    essential_modules["orca.ax_object"].AXObject.find_ancestor = test_context.Mock(
                        return_value=mock_desktop
                    )
                elif mock_value == "combo_box":
                    mock_combo = test_context.Mock(spec=Atspi.Accessible)
                    essential_modules["orca.ax_object"].AXObject.find_ancestor = test_context.Mock(
                        return_value=mock_combo
                    )
                else:
                    essential_modules["orca.ax_object"].AXObject.find_ancestor = test_context.Mock(
                        return_value=None
                    )
            elif mock_path.startswith("ax_object.has_action"):
                essential_modules["orca.ax_object"].AXObject.has_action = test_context.Mock(
                    return_value=mock_value
                )
            elif mock_path.startswith("ax_object.get_role"):
                essential_modules["orca.ax_object"].AXObject.get_role = test_context.Mock(
                    return_value=mock_value
                )
            elif mock_path.startswith("ax_utilities_role."):
                method_name = mock_path.split(".", 1)[1]
                setattr(
                    essential_modules["orca.ax_utilities_role"].AXUtilitiesRole,
                    method_name,
                    test_context.Mock(return_value=mock_value),
                )
            elif mock_path.startswith("ax_utilities_state."):
                method_name = mock_path.split(".", 1)[1]
                setattr(
                    essential_modules["orca.ax_utilities_state"].AXUtilitiesState,
                    method_name,
                    test_context.Mock(return_value=mock_value),
                )
            elif mock_path.startswith("ax_table."):
                method_name = mock_path.split(".", 1)[1]
                setattr(
                    essential_modules["orca.ax_table"].AXTable,
                    method_name,
                    test_context.Mock(return_value=mock_value),
                )

        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_layout_only(mock_obj)
        assert result is expected

    def test_get_next_object_with_invalid_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_next_object with invalid object."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(
            return_value=False
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_next_object(mock_obj)
        assert result is None

    def test_get_previous_object_with_invalid_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_previous_object with invalid object."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(
            return_value=False
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_previous_object(mock_obj)
        assert result is None

    def test_get_on_screen_objects_leaf_node(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities._get_on_screen_objects with leaf node."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "is_on_screen", side_effect=lambda obj, bbox: True)
        test_context.patch_object(AXUtilities, "treat_as_leaf_node", return_value=True)
        result = AXUtilities.get_on_screen_objects(mock_obj)
        assert result == [mock_obj]

    def test_sort_by_child_index_needs_sorting(self, test_context: OrcaTestContext) -> None:
        """Test sorting behavior through public methods that use _sort_by_child_index."""

        mock_obj1, mock_obj2, mock_obj3 = [
            test_context.Mock(spec=Atspi.Accessible) for _ in range(3)
        ]

        def mock_get_index(obj):
            if obj == mock_obj1:
                return 2
            if obj == mock_obj2:
                return 0
            if obj == mock_obj3:
                return 1
            return 0

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_index_in_parent = mock_get_index
        from orca.ax_utilities import AXUtilities

        mock_sort = test_context.Mock()
        test_context.patch_object(AXUtilities, "_sort_by_child_index", new=mock_sort)
        input_list = [mock_obj1, mock_obj2, mock_obj3]
        expected_result = [mock_obj2, mock_obj3, mock_obj1]  # sorted by index: 0, 1, 2
        mock_sort.return_value = expected_result

        result = mock_sort(input_list)
        assert result == expected_result
        mock_sort.assert_called_once_with(input_list)

    def test_get_set_size_with_valid_size(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_set_size with valid set size."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value="5"
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_set_size(mock_obj)
        assert result == 5

    def test_get_set_size_is_unknown_true(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_set_size_is_unknown returns True for unknown size."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(
            AXUtilities, "get_set_size", return_value=-1
        )
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_set_size_is_unknown(mock_obj)
        assert result is True

    def test_treat_as_leaf_node_with_child_count(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.treat_as_leaf_node with objects having children."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=3
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is False

    def test_treat_as_leaf_node_without_children(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.treat_as_leaf_node with objects having presentational children."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.children_are_presentational = test_context.Mock(return_value=True)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_page_tab = test_context.Mock(
            return_value=False
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is True

    def test_has_visible_caption_without_label(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.has_visible_caption without visible label."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_label = test_context.Mock(
            return_value=False
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.has_visible_caption(mock_obj)
        assert result is False

    def test_get_displayed_label_with_name(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_displayed_label with labelling objects."""

        mock_label1 = test_context.Mock(spec=Atspi.Accessible)
        mock_label2 = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_labelled_by = test_context.Mock(
            return_value=[mock_label1, mock_label2]
        )

        def mock_get_name(obj):
            if obj == mock_label1:
                return "Button"
            if obj == mock_label2:
                return "Label"
            return ""

        essential_modules["orca.ax_object"].AXObject.get_name = mock_get_name
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_displayed_label(mock_obj)
        assert result == "Button Label"

    def test_get_displayed_description_with_description(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_displayed_description with describing objects."""

        mock_desc1 = test_context.Mock(spec=Atspi.Accessible)
        mock_desc2 = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_described_by = test_context.Mock(
            return_value=[mock_desc1, mock_desc2]
        )

        def mock_get_name(obj):
            if obj == mock_desc1:
                return "Button"
            if obj == mock_desc2:
                return "description"
            return ""

        essential_modules["orca.ax_object"].AXObject.get_name = mock_get_name
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_displayed_description(mock_obj)
        assert result == "Button description"

    def test_get_heading_level_with_level(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_heading_level with heading level."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_heading = test_context.Mock(
            return_value=True
        )
        essential_modules["orca.ax_object"].AXObject.get_attributes_dict = test_context.Mock(
            return_value={"level": "2"}
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_heading_level(mock_obj)
        assert result == 2

    def test_get_heading_level_invalid(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_heading_level with invalid level."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_heading = test_context.Mock(
            return_value=True
        )
        essential_modules["orca.ax_object"].AXObject.get_attributes_dict = test_context.Mock(
            return_value={"level": "invalid"}
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_heading_level(mock_obj)
        assert result == 0

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "alert_dialog",
                "is_dialog": True,
                "supports_collection": False,
                "get_all_widgets": [],
                "collection_checks": {},
                "expected": True,
            },
            {
                "id": "regular_dialog",
                "is_dialog": True,
                "supports_collection": True,
                "get_all_widgets": [],
                "collection_checks": {
                    "has_scroll_pane": False,
                    "has_split_pane": False,
                    "has_tree_or_tree_table": False,
                    "has_combo_box_or_list_box": False,
                    "has_editable_object": False,
                },
                "expected": True,
            },
            {
                "id": "non_dialog",
                "is_dialog": False,
                "supports_collection": None,
                "get_all_widgets": [],
                "collection_checks": {},
                "expected": False,
            },
            {
                "id": "no_collection_support_with_widgets",
                "is_dialog": True,
                "supports_collection": False,
                "get_all_widgets": ["widget1"],
                "collection_checks": {},
                "expected": False,
            },
            {
                "id": "no_collection_support_no_widgets",
                "is_dialog": True,
                "supports_collection": False,
                "get_all_widgets": [],
                "collection_checks": {},
                "expected": True,
            },
            {
                "id": "has_scroll_pane",
                "is_dialog": True,
                "supports_collection": True,
                "get_all_widgets": [],
                "collection_checks": {"has_scroll_pane": True},
                "expected": False,
            },
            {
                "id": "has_split_pane",
                "is_dialog": True,
                "supports_collection": True,
                "get_all_widgets": [],
                "collection_checks": {"has_scroll_pane": False, "has_split_pane": True},
                "expected": False,
            },
            {
                "id": "has_tree_or_tree_table",
                "is_dialog": True,
                "supports_collection": True,
                "get_all_widgets": [],
                "collection_checks": {
                    "has_scroll_pane": False,
                    "has_split_pane": False,
                    "has_tree_or_tree_table": True,
                },
                "expected": False,
            },
            {
                "id": "has_combo_box_or_list_box",
                "is_dialog": True,
                "supports_collection": True,
                "get_all_widgets": [],
                "collection_checks": {
                    "has_scroll_pane": False,
                    "has_split_pane": False,
                    "has_tree_or_tree_table": False,
                    "has_combo_box_or_list_box": True,
                },
                "expected": False,
            },
            {
                "id": "has_editable_object",
                "is_dialog": True,
                "supports_collection": True,
                "get_all_widgets": [],
                "collection_checks": {
                    "has_scroll_pane": False,
                    "has_split_pane": False,
                    "has_tree_or_tree_table": False,
                    "has_combo_box_or_list_box": False,
                    "has_editable_object": True,
                },
                "expected": False,
            },
            {
                "id": "true_case",
                "is_dialog": True,
                "supports_collection": True,
                "get_all_widgets": [],
                "collection_checks": {
                    "has_scroll_pane": False,
                    "has_split_pane": False,
                    "has_tree_or_tree_table": False,
                    "has_combo_box_or_list_box": False,
                    "has_editable_object": False,
                },
                "expected": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_message_dialog_scenarios(  # pylint: disable=too-many-branches,too-many-positional-arguments
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXUtilities.is_message_dialog with various scenarios."""
        is_dialog = case["is_dialog"]
        supports_collection = case["supports_collection"]
        get_all_widgets = case["get_all_widgets"]
        collection_checks = case["collection_checks"]
        expected = case["expected"]
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_dialog_or_alert = test_context.Mock(return_value=is_dialog)

        if supports_collection is not None:
            essential_modules["orca.ax_object"].AXObject.supports_collection = test_context.Mock(
                return_value=supports_collection
            )

        if not supports_collection and get_all_widgets is not None:
            test_context.patch(
                "orca.ax_utilities.AXUtilities.get_all_widgets",
                return_value=get_all_widgets
            )

        for check_name, check_value in collection_checks.items():
            if check_name in ["has_scroll_pane", "has_split_pane"]:
                setattr(
                    essential_modules["orca.ax_utilities_collection"].AXUtilitiesCollection,
                    check_name,
                    test_context.Mock(return_value=check_value),
                )
            else:
                setattr(
                    sys.modules["orca.ax_utilities_collection"].AXUtilitiesCollection,
                    check_name,
                    test_context.Mock(return_value=check_value),
                )

        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_message_dialog(mock_obj)
        assert result is expected

    def test_can_be_active_window_with_dialog(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.can_be_active_window with dialog window."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_utilities_state"].AXUtilitiesState.is_active = test_context.Mock(
            return_value=True
        )
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_showing = test_context.Mock(return_value=True)
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_iconified = test_context.Mock(return_value=False)
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.can_be_active_window(mock_obj)
        assert result is True

    def test_can_be_active_window_with_hidden_window(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.can_be_active_window with hidden window."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_role = test_context.Mock(
            return_value=Atspi.Role.FRAME
        )
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_showing = test_context.Mock(return_value=False)
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.can_be_active_window(mock_obj)
        assert result is False

    def test_can_be_active_window_with_none(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.can_be_active_window with None object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.can_be_active_window(None)
        assert result is False

    def test_is_unfocused_alert_or_dialog_with_alert(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.is_unfocused_alert_or_dialog with alert."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_dialog_or_alert = test_context.Mock(return_value=True)
        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=1
        )
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_showing = test_context.Mock(return_value=True)
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(
            AXUtilities, "can_be_active_window", return_value=False
        )
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_unfocused_alert_or_dialog(mock_obj)
        assert result is True

    def test_is_unfocused_alert_or_dialog_with_focused_dialog(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.is_unfocused_alert_or_dialog with focused dialog."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_role = test_context.Mock(
            return_value=Atspi.Role.DIALOG
        )
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_focused = test_context.Mock(return_value=True)
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_unfocused_alert_or_dialog(mock_obj)
        assert result is False

    def test_is_unfocused_alert_or_dialog_with_no_children(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.is_unfocused_alert_or_dialog with alert having no children."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_dialog_or_alert = test_context.Mock(return_value=True)
        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=0
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_unfocused_alert_or_dialog(mock_obj)
        assert result is False

    def test_is_unfocused_alert_or_dialog_not_showing(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.is_unfocused_alert_or_dialog with alert not showing."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_dialog_or_alert = test_context.Mock(return_value=True)
        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=3
        )
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_showing = test_context.Mock(return_value=False)
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.is_unfocused_alert_or_dialog(mock_obj)
        assert result is False

    def test_get_unfocused_alerts_and_dialogs_with_alerts(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_unfocused_alerts_and_dialogs with alert objects."""

        mock_alert1 = test_context.Mock(spec=Atspi.Accessible)
        mock_alert2 = test_context.Mock(spec=Atspi.Accessible)
        mock_normal = test_context.Mock(spec=Atspi.Accessible)
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_application"
        ].AXUtilitiesApplication.get_application = test_context.Mock(return_value=mock_app)
        essential_modules["orca.ax_object"].AXObject.find_ancestor = test_context.Mock(
            return_value=None
        )

        def mock_iter_children(parent, predicate=None):
            if parent == mock_app:
                all_children = [mock_alert1, mock_alert2, mock_normal]
                if predicate:
                    return [obj for obj in all_children if predicate(obj)]
                return all_children
            return []

        essential_modules["orca.ax_object"].AXObject.iter_children = mock_iter_children
        from orca.ax_utilities import AXUtilities

        def mock_is_unfocused(obj):
            return obj in [mock_alert1, mock_alert2]

        test_context.patch_object(
            AXUtilities, "is_unfocused_alert_or_dialog", new=mock_is_unfocused
        )
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_unfocused_alerts_and_dialogs(mock_obj)
        assert result == [mock_alert1, mock_alert2]

    def test_get_all_widgets_with_button_predicate(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_all_widgets returns widget objects."""

        mock_button1 = test_context.Mock(spec=Atspi.Accessible)
        mock_button2 = test_context.Mock(spec=Atspi.Accessible)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.supports_collection = test_context.Mock(
            return_value=True
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.get_widget_roles = test_context.Mock(
            return_value=[Atspi.Role.PUSH_BUTTON, Atspi.Role.CHECK_BOX]
        )
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.find_all_with_role_and_all_states = test_context.Mock(
            return_value=[mock_button1, mock_button2]
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_all_widgets(mock_obj, must_be_showing_and_visible=True)
        assert result == [mock_button1, mock_button2]

    def test_get_all_widgets_exclude_push_button(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_all_widgets with exclude_push_button=True."""

        mock_checkbox = test_context.Mock(spec=Atspi.Accessible)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.supports_collection = test_context.Mock(
            return_value=True
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.get_widget_roles = test_context.Mock(
            return_value=[Atspi.Role.PUSH_BUTTON, Atspi.Role.CHECK_BOX]
        )
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.find_all_with_role_and_all_states = test_context.Mock(
            return_value=[mock_checkbox]
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_all_widgets(mock_obj, exclude_push_button=True)
        # Should call with CHECK_BOX only (PUSH_BUTTON removed)
        collection_module = sys.modules["orca.ax_utilities_collection"]
        find_all_method = collection_module.AXUtilitiesCollection.find_all_with_role_and_all_states
        find_all_method.assert_called_with(
            mock_obj, [Atspi.Role.CHECK_BOX], [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE]
        )
        assert result == [mock_checkbox]

    def test_get_default_button_with_default_button(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_default_button with default button."""

        mock_default_button = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.supports_collection = test_context.Mock(
            return_value=True
        )
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.find_default_button = test_context.Mock(
            return_value=mock_default_button
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_default_button(mock_obj)
        assert result == mock_default_button

    def test_get_focused_object_with_focused_descendant(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_focused_object with focused descendant."""

        mock_focused = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.supports_collection = test_context.Mock(
            return_value=True
        )
        sys.modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.find_focused_object = test_context.Mock(return_value=mock_focused)
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_focused_object(mock_obj)
        assert result == mock_focused

    def test_get_info_bar_with_info_bar(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_info_bar with info bar descendant."""

        mock_info_bar = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.supports_collection = test_context.Mock(
            return_value=True
        )
        essential_modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.find_info_bar = test_context.Mock(return_value=mock_info_bar)
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_info_bar(mock_obj)
        assert result == mock_info_bar

    def test_get_status_bar_with_status_bar(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_status_bar with status bar descendant."""

        mock_status_bar = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.supports_collection = test_context.Mock(
            return_value=True
        )
        essential_modules[
            "orca.ax_utilities_collection"
        ].AXUtilitiesCollection.find_status_bar = test_context.Mock(return_value=mock_status_bar)
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_status_bar(mock_obj)
        assert result == mock_status_bar

    def test_clear_all_cache_now_with_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.clear_all_cache_now with specific object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        AXUtilities.clear_all_cache_now(mock_obj, "test reason")

    def test_clear_all_cache_now_without_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.clear_all_cache_now without specific object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        AXUtilities.clear_all_cache_now(None, "test reason")

    def test_get_set_members_with_basic_set(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_set_members with basic set."""

        mock_member1 = test_context.Mock(spec=Atspi.Accessible)
        mock_member2 = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(
            AXUtilities,
            "_get_set_members",
            return_value=[mock_member1, mock_member2]
        )
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_set_members(mock_obj)
        assert result == [mock_member1, mock_member2]

    def test_get_set_members_with_empty_set(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_set_members with empty set."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(
            AXUtilities, "_get_set_members", return_value=[]
        )
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_set_members(mock_obj)
        assert result == []

    def test_find_active_window_with_active_window(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.find_active_window with active window."""

        mock_active_window = test_context.Mock(spec=Atspi.Accessible)
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        sys.modules[
            "orca.ax_utilities_application"
        ].AXUtilitiesApplication.get_all_applications = test_context.Mock(return_value=[mock_app])
        essential_modules["orca.ax_object"].AXObject.iter_children = test_context.Mock(
            return_value=[mock_active_window]
        )
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(
            AXUtilities, "can_be_active_window", side_effect=lambda x: x == mock_active_window
        )
        result = AXUtilities.find_active_window()
        assert result == mock_active_window

    def test_find_active_window_with_no_active_window(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.find_active_window with no active window."""

        self._setup_dependencies(test_context)
        sys.modules[
            "orca.ax_utilities_application"
        ].AXUtilitiesApplication.get_all_applications = test_context.Mock(return_value=[])
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.find_active_window()
        assert result is None

    def test_start_cache_clearing_thread(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.start_cache_clearing_thread."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        mock_start_thread = test_context.Mock()
        test_context.patch_object(
            AXUtilities, "start_cache_clearing_thread", new=mock_start_thread
        )
        mock_start_thread()
        mock_start_thread.assert_called_once()

    def test_get_on_screen_objects_with_invalid_root(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_on_screen_objects with invalid root."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(
            return_value=False
        )
        essential_modules["orca.ax_table"].AXTable.iter_visible_cells = test_context.Mock(
            return_value=[]
        )
        from orca.ax_utilities import AXUtilities

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = AXUtilities.get_on_screen_objects(mock_obj)
        assert result == []

    def test_clear_all_dictionaries_with_reason(self, test_context: OrcaTestContext) -> None:
        """Test cache clearing functionality with reason."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(AXUtilities, "SET_MEMBERS", new={"test": "data"})
        test_context.patch_object(AXUtilities, "IS_LAYOUT_ONLY", new={"test": "data"})
        mock_clear = test_context.Mock()
        test_context.patch_object(AXUtilities, "_clear_all_dictionaries", new=mock_clear)

        AXUtilities.clear_all_cache_now(reason="test reason")

        mock_clear.assert_called()

    def test_clear_all_dictionaries_without_reason(self, test_context: OrcaTestContext) -> None:
        """Test cache clearing functionality without reason."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(AXUtilities, "SET_MEMBERS", new={"test": "data"})
        test_context.patch_object(AXUtilities, "IS_LAYOUT_ONLY", new={"test": "data"})
        mock_clear = test_context.Mock()
        test_context.patch_object(AXUtilities, "_clear_all_dictionaries", new=mock_clear)

        AXUtilities.clear_all_cache_now()

        mock_clear.assert_called()

    def test_get_nesting_level_list_item(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_nesting_level with list item."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor1 = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor2 = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_list_item = test_context.Mock(return_value=True)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_list = test_context.Mock(
            return_value=True
        )
        find_calls = []

        def mock_find_ancestor(obj, _pred):
            find_calls.append(obj)
            if obj == mock_obj:
                return mock_ancestor1
            if obj == mock_ancestor1:
                return mock_ancestor2
            return None

        essential_modules["orca.ax_object"].AXObject.find_ancestor = mock_find_ancestor
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=mock_obj
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_nesting_level(mock_obj)
        assert result == 2

    def test_get_nesting_level_regular_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_nesting_level with regular object."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor1 = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_list_item = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.have_same_role = test_context.Mock(return_value=True)
        find_calls = []

        def mock_find_ancestor(obj, _pred):
            find_calls.append(obj)
            if obj == mock_obj:
                return mock_ancestor1
            return None

        essential_modules["orca.ax_object"].AXObject.find_ancestor = mock_find_ancestor
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_nesting_level(mock_obj)
        assert result == 1

    def test_get_position_in_set_with_posinset_attribute(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_position_in_set with posinset attribute."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value="3"
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == 2

    def test_get_position_in_set_table_row_with_rowindex(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_position_in_set with table row and rowindex."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_row = test_context.Mock(return_value=True)
        get_attribute_calls = []

        def mock_get_attribute(obj, attr, use_cache):
            get_attribute_calls.append((obj, attr, use_cache))
            if attr == "posinset":
                return None
            if attr == "rowindex":
                return "5"
            return None

        essential_modules["orca.ax_object"].AXObject.get_attribute = mock_get_attribute
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == 4

    def test_get_position_in_set_fallback_to_set_members(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_position_in_set fallback to set members."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_member1 = test_context.Mock(spec=Atspi.Accessible)
        mock_member2 = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_row = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_cell_or_header = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=False)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value=None
        )
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=mock_parent
        )
        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=100
        )
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(
            AXUtilities,
            "get_set_members",
            side_effect=lambda x: [mock_member1, mock_obj, mock_member2]
        )
        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == 1

    def test_get_set_members_internal_with_none_container(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_set_members with None container."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        essential_modules["orca.ax_object"].AXObject.get_parent_checked = test_context.Mock(
            return_value=None
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_members(mock_obj)
        assert result == []

    def test_get_set_members_internal_with_member_of_relation(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities._get_set_members with member-of relation."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_member1 = test_context.Mock(spec=Atspi.Accessible)
        mock_member2 = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_member_of = test_context.Mock(
            return_value=[mock_member1, mock_member2]
        )
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(AXUtilities, "_sort_by_child_index", side_effect=lambda x: x)
        result = AXUtilities.get_set_members(mock_obj)
        assert result == [mock_member1, mock_member2]

    def test_get_set_members_internal_with_node_parent_relation(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities._get_set_members with node-parent-of relation."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_child1 = test_context.Mock(spec=Atspi.Accessible)
        mock_child2 = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_member_of = test_context.Mock(return_value=[])
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_node_parent_of = test_context.Mock(
            return_value=[mock_child1, mock_child2]
        )
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(AXUtilities, "_sort_by_child_index", side_effect=lambda x: x)
        result = AXUtilities.get_set_members(mock_obj)
        assert result == [mock_child1, mock_child2]

    def test_get_set_members_internal_with_description_values(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities._get_set_members with description values."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_prev = test_context.Mock(spec=Atspi.Accessible)
        mock_next = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_member_of = test_context.Mock(return_value=[])
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_node_parent_of = test_context.Mock(return_value=[])
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_description_value = test_context.Mock(return_value=True)

        def mock_get_previous_sibling(obj):
            if obj == mock_obj:
                return mock_prev
            return None

        def mock_get_next_sibling(obj):
            if obj == mock_obj:
                return mock_next
            return None

        essential_modules[
            "orca.ax_object"
        ].AXObject.get_previous_sibling = mock_get_previous_sibling
        essential_modules["orca.ax_object"].AXObject.get_next_sibling = mock_get_next_sibling
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_members(mock_obj)
        assert len(result) == 3
        assert mock_obj in result
        assert mock_prev in result
        assert mock_next in result

    def test_get_set_members_internal_with_menu_related(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities._get_set_members with menu-related objects."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_menu1 = test_context.Mock(spec=Atspi.Accessible)
        mock_menu2 = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_member_of = test_context.Mock(return_value=[])
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_node_parent_of = test_context.Mock(return_value=[])
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_description_value = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_menu_related = test_context.Mock(return_value=True)
        essential_modules["orca.ax_object"].AXObject.iter_children = test_context.Mock(
            return_value=[mock_menu1, mock_menu2]
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_members(mock_obj)
        assert result == [mock_menu1, mock_menu2]

    def test_get_set_members_internal_fallback_to_role(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities._get_set_members fallback to role-based matching."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_same_role1 = test_context.Mock(spec=Atspi.Accessible)
        mock_same_role2 = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_member_of = test_context.Mock(return_value=[])
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_node_parent_of = test_context.Mock(return_value=[])
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_description_value = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_menu_related = test_context.Mock(return_value=False)
        essential_modules["orca.ax_object"].AXObject.get_role = test_context.Mock(
            return_value=Atspi.Role.PUSH_BUTTON
        )
        essential_modules["orca.ax_object"].AXObject.iter_children = test_context.Mock(
            return_value=[mock_same_role1, mock_same_role2]
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_members(mock_obj)
        assert result == [mock_same_role1, mock_same_role2]

    def test_get_next_object_with_flows_to_relation(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_next_object with flows-to relation."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_target = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(return_value=True)
        essential_modules["orca.ax_object"].AXObject.is_dead = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_flows_to = test_context.Mock(return_value=[mock_target])
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_next_object(mock_obj)
        assert result == mock_target

    def test_get_next_object_with_dead_flows_to_targets(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_next_object filters out dead objects from flows-to targets."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_target = test_context.Mock(spec=Atspi.Accessible)
        mock_live_target = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(
            return_value=True
        )
        essential_modules["orca.ax_object"].AXObject.is_dead = test_context.Mock(
            side_effect=lambda obj: obj == mock_dead_target
        )
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_flows_to = test_context.Mock(
            return_value=[mock_dead_target, mock_live_target]
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_next_object(mock_obj)
        assert result == mock_live_target

    def test_get_next_object_with_all_dead_flows_to_targets(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_next_object falls back to traversal when all flows-to are dead."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_target1 = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_target2 = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_next = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(
            return_value=True
        )
        essential_modules["orca.ax_object"].AXObject.is_dead = test_context.Mock(
            return_value=True
        )
        essential_modules["orca.ax_object"].AXObject.get_index_in_parent = (
            test_context.Mock(return_value=0)
        )
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=mock_parent
        )
        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=2
        )
        essential_modules["orca.ax_object"].AXObject.get_child = test_context.Mock(
            return_value=mock_next
        )
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_flows_to = test_context.Mock(
            return_value=[mock_dead_target1, mock_dead_target2]
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_next_object(mock_obj)
        assert result == mock_next

    def test_get_next_object_normal_traversal(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_next_object with normal parent-child traversal."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_next = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(return_value=True)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_flows_to = test_context.Mock(return_value=[])
        essential_modules["orca.ax_object"].AXObject.get_index_in_parent = test_context.Mock(
            return_value=0
        )
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=mock_parent
        )
        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=3
        )
        essential_modules["orca.ax_object"].AXObject.get_child = test_context.Mock(
            return_value=mock_next
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_next_object(mock_obj)
        assert result == mock_next

    def test_get_previous_object_with_flows_from_relation(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_previous_object with flows-from relation."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_source = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(return_value=True)
        essential_modules["orca.ax_object"].AXObject.is_dead = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_flows_from = test_context.Mock(return_value=[mock_source])
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_previous_object(mock_obj)
        assert result == mock_source

    def test_get_previous_object_with_dead_flows_from_targets(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_previous_object filters out dead objects from flows-from targets."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_source = test_context.Mock(spec=Atspi.Accessible)
        mock_live_source = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(
            return_value=True
        )
        essential_modules["orca.ax_object"].AXObject.is_dead = test_context.Mock(
            side_effect=lambda obj: obj == mock_dead_source
        )
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_flows_from = test_context.Mock(
            return_value=[mock_dead_source, mock_live_source]
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_previous_object(mock_obj)
        assert result == mock_live_source

    def test_get_previous_object_with_all_dead_flows_from_targets(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_previous_object falls back when all flows-from are dead."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_source1 = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_source2 = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_previous = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(
            return_value=True
        )
        essential_modules["orca.ax_object"].AXObject.is_dead = test_context.Mock(
            return_value=True
        )
        essential_modules["orca.ax_object"].AXObject.get_index_in_parent = (
            test_context.Mock(return_value=1)
        )
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=mock_parent
        )
        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=2
        )
        essential_modules["orca.ax_object"].AXObject.get_child = test_context.Mock(
            return_value=mock_previous
        )
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_flows_from = test_context.Mock(
            return_value=[mock_dead_source1, mock_dead_source2]
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_previous_object(mock_obj)
        assert result == mock_previous

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "showing_visible_on_screen",
                "is_showing": True,
                "is_visible": True,
                "is_hidden": False,
                "has_no_size_invalid_rect": False,
                "object_is_off_screen": False,
                "object_intersects_rect": True,
                "bbox_provided": False,
                "expected_result": True,
            },
            {
                "id": "hidden_object",
                "is_showing": False,
                "is_visible": False,
                "is_hidden": True,
                "has_no_size_invalid_rect": False,
                "object_is_off_screen": False,
                "object_intersects_rect": True,
                "bbox_provided": False,
                "expected_result": False,
            },
            {
                "id": "not_showing_but_visible",
                "is_showing": False,
                "is_visible": True,
                "is_hidden": False,
                "has_no_size_invalid_rect": False,
                "object_is_off_screen": False,
                "object_intersects_rect": True,
                "bbox_provided": False,
                "expected_result": False,
            },
            {
                "id": "showing_visible_but_hidden",
                "is_showing": True,
                "is_visible": True,
                "is_hidden": True,
                "has_no_size_invalid_rect": False,
                "object_is_off_screen": False,
                "object_intersects_rect": True,
                "bbox_provided": False,
                "expected_result": False,
            },
            {
                "id": "no_size_or_invalid_rect",
                "is_showing": True,
                "is_visible": True,
                "is_hidden": False,
                "has_no_size_invalid_rect": True,
                "object_is_off_screen": False,
                "object_intersects_rect": True,
                "bbox_provided": False,
                "expected_result": True,
            },
            {
                "id": "object_off_screen",
                "is_showing": True,
                "is_visible": True,
                "is_hidden": False,
                "has_no_size_invalid_rect": False,
                "object_is_off_screen": True,
                "object_intersects_rect": True,
                "bbox_provided": False,
                "expected_result": False,
            },
            {
                "id": "bbox_no_intersection",
                "is_showing": True,
                "is_visible": True,
                "is_hidden": False,
                "has_no_size_invalid_rect": False,
                "object_is_off_screen": False,
                "object_intersects_rect": False,
                "bbox_provided": True,
                "expected_result": False,
            },
            {
                "id": "fully_on_screen",
                "is_showing": True,
                "is_visible": True,
                "is_hidden": False,
                "has_no_size_invalid_rect": False,
                "object_is_off_screen": False,
                "object_intersects_rect": True,
                "bbox_provided": False,
                "expected_result": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_on_screen_scenarios(  # pylint: disable=too-many-positional-arguments,too-many-locals
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXUtilities.is_on_screen with various state combinations."""
        is_showing = case["is_showing"]
        is_visible = case["is_visible"]
        is_hidden = case["is_hidden"]
        has_no_size_invalid_rect = case["has_no_size_invalid_rect"]
        object_is_off_screen = case["object_is_off_screen"]
        object_intersects_rect = case["object_intersects_rect"]
        bbox_provided = case["bbox_provided"]
        expected_result = case["expected_result"]
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_bbox = test_context.Mock(spec=Atspi.Rect) if bbox_provided else None
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_showing = test_context.Mock(return_value=is_showing)
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_visible = test_context.Mock(return_value=is_visible)
        essential_modules["orca.ax_utilities_state"].AXUtilitiesState.is_hidden = test_context.Mock(
            return_value=is_hidden
        )

        essential_modules[
            "orca.ax_component"
        ].AXComponent.has_no_size_or_invalid_rect = test_context.Mock(
            return_value=has_no_size_invalid_rect
        )
        essential_modules["orca.ax_component"].AXComponent.object_is_off_screen = test_context.Mock(
            return_value=object_is_off_screen
        )
        essential_modules[
            "orca.ax_component"
        ].AXComponent.object_intersects_rect = test_context.Mock(
            return_value=object_intersects_rect
        )

        from orca.ax_utilities import AXUtilities

        result = (
            AXUtilities.is_on_screen(mock_obj, mock_bbox)
            if bbox_provided
            else AXUtilities.is_on_screen(mock_obj)
        )
        assert result is expected_result

    def test_has_visible_caption_with_visible_caption(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.has_visible_caption with visible caption."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_caption = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_figure = test_context.Mock(
            return_value=True
        )
        essential_modules["orca.ax_object"].AXObject.supports_table = test_context.Mock(
            return_value=False
        )
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_labelled_by = test_context.Mock(return_value=[mock_caption])
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_caption = test_context.Mock(
            return_value=True
        )
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_showing = test_context.Mock(return_value=True)
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_visible = test_context.Mock(return_value=True)
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.has_visible_caption(mock_obj)
        assert result is True

    def test_has_visible_caption_not_figure_or_table(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.has_visible_caption with object that's not figure or table."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_figure = test_context.Mock(
            return_value=False
        )
        essential_modules["orca.ax_object"].AXObject.supports_table = test_context.Mock(
            return_value=False
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.has_visible_caption(mock_obj)
        assert result is False

    def test_get_displayed_description_from_relations(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_displayed_description returns description from relations."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_desc = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_is_described_by = test_context.Mock(return_value=[mock_desc])
        essential_modules["orca.ax_object"].AXObject.get_name = test_context.Mock(
            return_value="Test description"
        )
        essential_modules["orca.ax_text"].AXText.get_all_text = test_context.Mock(return_value="")
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_displayed_description(mock_obj)
        assert result == "Test description"

    def test_get_displayed_description_empty(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_displayed_description with empty description."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_description = test_context.Mock(
            return_value=""
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_displayed_description(mock_obj)
        assert result == ""

    def test_get_position_in_set_with_large_child_count(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_position_in_set with large child count uses index_in_parent."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_row = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_cell_or_header = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=False)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value=None
        )
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=mock_parent
        )
        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=1000
        )
        essential_modules["orca.ax_object"].AXObject.get_index_in_parent = test_context.Mock(
            return_value=42
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == 42

    def test_get_position_in_set_object_not_in_members(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_position_in_set when object not in set members."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_other = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_row = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_cell_or_header = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=False)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value=None
        )
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=mock_parent
        )
        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=10
        )
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(
            AXUtilities, "get_set_members", side_effect=lambda x: [mock_other])
        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == -1

    def test_treat_as_leaf_node_presentational_page_tab(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.treat_as_leaf_node with presentational page tab."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.children_are_presentational = test_context.Mock(return_value=True)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_page_tab = test_context.Mock(
            return_value=True
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is False

    def test_treat_as_leaf_node_presentational_non_page_tab(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.treat_as_leaf_node with presentational non-page-tab."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.children_are_presentational = test_context.Mock(return_value=True)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_page_tab = test_context.Mock(
            return_value=False
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is True

    def test_treat_as_leaf_node_combo_box_expanded(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.treat_as_leaf_node with expanded combo box."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.children_are_presentational = test_context.Mock(return_value=False)
        essential_modules["orca.ax_object"].AXObject.get_role = test_context.Mock(
            return_value=Atspi.Role.COMBO_BOX
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=True)
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_expanded = test_context.Mock(return_value=True)
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is False

    def test_treat_as_leaf_node_menu_non_aria_expanded(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.treat_as_leaf_node with expanded non-ARIA menu."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.children_are_presentational = test_context.Mock(return_value=False)
        essential_modules["orca.ax_object"].AXObject.get_role = test_context.Mock(
            return_value=Atspi.Role.MENU
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=False)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_menu = test_context.Mock(
            return_value=True
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.has_role_from_aria = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_expanded = test_context.Mock(return_value=True)
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.treat_as_leaf_node(mock_obj)
        assert result is False

    def test_get_set_size_combo_box_with_selection(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_set_size with combo box having selection."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_selected = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value=None
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_row = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_cell_or_header = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=True)
        essential_modules[
            "orca.ax_selection"
        ].AXSelection.get_selected_children = test_context.Mock(return_value=[mock_selected])
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(
            AXUtilities,
            "get_set_members",
            side_effect=lambda x: [test_context.Mock(), test_context.Mock(), test_context.Mock()]
        )
        result = AXUtilities.get_set_size(mock_obj)
        assert result == 3

    def test_get_set_size_table_cell_not_in_row(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_set_size with table cell not in table row."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value=None
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_row = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_cell_or_header = test_context.Mock(return_value=True)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=False)
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=mock_parent
        )
        essential_modules["orca.ax_table"].AXTable.get_table = test_context.Mock(
            return_value=mock_table
        )
        essential_modules["orca.ax_table"].AXTable.get_row_count = test_context.Mock(
            return_value=15
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_size(mock_obj)
        assert result == 15

    def test_get_set_size_table_row_with_table(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_set_size with table row."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value=None
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_row = test_context.Mock(return_value=True)
        essential_modules["orca.ax_table"].AXTable.get_table = test_context.Mock(
            return_value=mock_table
        )
        essential_modules["orca.ax_table"].AXTable.get_row_count = test_context.Mock(
            return_value=20
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_size(mock_obj)
        assert result == 20

    def test_get_set_size_fallback_to_set_members(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_set_size fallback to set members count."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value=None
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_row = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_cell_or_header = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=False)
        from orca.ax_utilities import AXUtilities

        test_context.patch_object(
            AXUtilities,
            "get_set_members",
            side_effect=lambda x: [
                test_context.Mock(),
                test_context.Mock(),
                test_context.Mock(),
                test_context.Mock(),
            ]
        )
        result = AXUtilities.get_set_size(mock_obj)
        assert result == 4

    def test_get_set_size_is_unknown_with_indeterminate_state(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_set_size_is_unknown with indeterminate state."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_indeterminate = test_context.Mock(return_value=True)
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_size_is_unknown(mock_obj)
        assert result is True

    def test_get_set_size_is_unknown_table_with_negative_counts(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_set_size_is_unknown with table having negative counts."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_state"
        ].AXUtilitiesState.is_indeterminate = test_context.Mock(return_value=False)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table = test_context.Mock(
            return_value=True
        )
        essential_modules["orca.ax_object"].AXObject.get_attributes_dict = test_context.Mock(
            return_value={"rowcount": "-1", "colcount": "5"}
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_set_size_is_unknown(mock_obj)
        assert result is True

    def test_has_explicit_name_true_case(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.has_explicit_name returns True when explicit-name attribute is true."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value="true"
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.has_explicit_name(mock_obj)
        assert result is True

    def test_get_next_object_no_parent(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_next_object when no parent is found."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(return_value=True)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_flows_to = test_context.Mock(return_value=[])
        essential_modules["orca.ax_object"].AXObject.get_index_in_parent = test_context.Mock(
            return_value=2
        )
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=None
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_next_object(mock_obj)
        assert result is None

    def test_get_previous_object_no_parent(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.get_previous_object when no parent is found."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.ax_object"].AXObject.is_valid = test_context.Mock(return_value=True)
        essential_modules[
            "orca.ax_utilities_relation"
        ].AXUtilitiesRelation.get_flows_from = test_context.Mock(return_value=[])
        essential_modules["orca.ax_object"].AXObject.get_index_in_parent = test_context.Mock(
            return_value=0
        )
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=None
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_previous_object(mock_obj)
        assert result is None

    def test_get_position_in_set_table_cell_with_coordinates(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXUtilities.get_position_in_set with table cell using coordinates."""

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_row = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_cell_or_header = test_context.Mock(return_value=True)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=False)
        essential_modules["orca.ax_object"].AXObject.get_attribute = test_context.Mock(
            return_value=None
        )
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=mock_parent
        )
        essential_modules["orca.ax_table"].AXTable.get_cell_coordinates = test_context.Mock(
            return_value=(3, 2)
        )
        from orca.ax_utilities import AXUtilities

        result = AXUtilities.get_position_in_set(mock_obj)
        assert result == 3
