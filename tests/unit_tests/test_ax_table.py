# Unit tests for ax_table.py methods.
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
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Unit tests for ax_table.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestAXTable:
    """Test AXTable class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_table dependencies."""

        additional_modules = ["orca.ax_utilities_role", "orca.object_properties"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject = test_context.Mock()
        ax_object_mock.AXObject.supports_table = test_context.Mock(return_value=True)
        ax_object_mock.AXObject.supports_table_cell = test_context.Mock(return_value=True)
        ax_object_mock.AXObject.find_descendant = test_context.Mock()
        ax_object_mock.AXObject.get_name = test_context.Mock(return_value="")
        ax_object_mock.AXObject.get_role = test_context.Mock()
        ax_object_mock.AXObject.get_parent = test_context.Mock()
        ax_object_mock.AXObject.get_child_count = test_context.Mock(return_value=0)
        ax_object_mock.AXObject.get_child = test_context.Mock()
        ax_object_mock.AXObject.get_index_in_parent = test_context.Mock(return_value=0)

        ax_utilities_role_mock = essential_modules["orca.ax_utilities_role"]
        ax_utilities_role_mock.AXUtilitiesRole = test_context.Mock()
        ax_utilities_role_mock.AXUtilitiesRole.is_table = test_context.Mock(return_value=True)
        ax_utilities_role_mock.AXUtilitiesRole.is_table_cell = test_context.Mock(return_value=True)
        ax_utilities_role_mock.AXUtilitiesRole.is_table_header = test_context.Mock(
            return_value=False
        )
        ax_utilities_role_mock.AXUtilitiesRole.is_table_row = test_context.Mock(return_value=False)
        ax_utilities_role_mock.AXUtilitiesRole.is_table_column_header = test_context.Mock(
            return_value=False
        )
        ax_utilities_role_mock.AXUtilitiesRole.is_table_row_header = test_context.Mock(
            return_value=False
        )

        messages_mock = essential_modules["orca.messages"]
        messages_mock.TABLE_DYNAMIC_HEADERS_SET = "Dynamic headers set"
        messages_mock.TABLE_DYNAMIC_HEADERS_CLEARED = "Dynamic headers cleared"

        object_properties_mock = essential_modules["orca.object_properties"]
        object_properties_mock.OBJECT_PROPERTY_TABLE_DYNAMIC_COLUMN_HEADERS_ROW = 1
        object_properties_mock.OBJECT_PROPERTY_TABLE_DYNAMIC_ROW_HEADERS_COLUMN = 2

        return essential_modules

    def _setup_table_role_mocks(
        self, test_context: OrcaTestContext, is_table_func=None, is_tree_table=False, is_tree=False
    ) -> None:
        """Set up common table role checking mocks."""

        from orca.ax_utilities_role import AXUtilitiesRole

        default_is_table = is_table_func or (lambda _obj: True)
        test_context.patch_object(AXUtilitiesRole, "is_table", side_effect=default_is_table)
        test_context.patch_object(
            AXUtilitiesRole, "is_tree_table", side_effect=lambda obj: is_tree_table
        )
        test_context.patch_object(AXUtilitiesRole, "is_tree", side_effect=lambda obj: is_tree)

    def _setup_table_support_mocks(
        self, test_context: OrcaTestContext, supports_table_cell=True, supports_table=True
    ) -> None:
        """Set up common table support mocks."""

        from orca.ax_object import AXObject

        test_context.patch_object(
            AXObject, "supports_table_cell", side_effect=lambda obj: supports_table_cell
        )
        test_context.patch_object(
            AXObject, "supports_table", side_effect=lambda obj: supports_table
        )

    def _setup_debug_message_mock(
        self, test_context: OrcaTestContext, essential_modules: dict[str, MagicMock]
    ) -> None:
        """Set up debug message mocking for test verification."""

        from orca import debug

        test_context.patch_object(
            debug, "print_message", new=essential_modules["orca.debug"].print_message
        )

    def _setup_layout_table_mocks(
        self,
        test_context: OrcaTestContext,
        has_col_headers=False,
        has_row_headers=False,
        name="",
        description="",
        caption=None,
    ) -> None:
        """Set up common mocks for layout table testing."""

        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(
            AXTable, "has_column_headers", side_effect=lambda obj: has_col_headers
        )
        test_context.patch_object(
            AXTable, "has_row_headers", side_effect=lambda obj: has_row_headers
        )
        test_context.patch_object(AXObject, "get_name", side_effect=lambda obj: name)
        test_context.patch_object(AXObject, "get_description", side_effect=lambda obj: description)
        test_context.patch_object(AXTable, "get_caption", side_effect=lambda obj: caption)

    def _setup_cell_span_mocks(
        self, test_context: OrcaTestContext, cell_index=5, table_obj=None, result_func=None
    ) -> None:
        """Set up common mocks for cell span testing."""

        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        if table_obj is None:
            table_obj = test_context.Mock(spec=Atspi.Accessible)

        default_result = test_context.Mock()
        default_result.__getitem__ = lambda self, index: False

        test_context.patch_object(AXTable, "_get_cell_index", side_effect=lambda obj: cell_index)
        test_context.patch_object(AXTable, "get_table", side_effect=lambda obj: table_obj)
        test_context.patch_object(AXObject, "supports_table", side_effect=lambda _obj: True)
        test_context.patch_object(AXUtilitiesRole, "is_tree", side_effect=lambda obj: False)
        test_context.patch_object(
            Atspi.Table,
            "get_row_column_extents_at_index",
            side_effect=result_func or (lambda table, index: default_result),
        )

    def _setup_row_headers_mocks(
        self,
        test_context: OrcaTestContext,
        table_obj,
        coordinates=(2, 3),
        spans=(2, 1),
        headers=None,
    ) -> None:
        """Set up common mocks for row headers testing."""

        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        if headers is None:
            headers = [test_context.Mock(spec=Atspi.Accessible)]

        test_context.patch_object(
            AXObject, "supports_table_cell", side_effect=lambda obj: False
        )
        test_context.patch_object(
            AXTable, "_get_cell_coordinates_from_table", side_effect=lambda obj: coordinates
        )
        test_context.patch_object(AXTable, "get_table", side_effect=lambda obj: table_obj)
        test_context.patch_object(
            AXTable, "_get_cell_spans_from_table", side_effect=lambda obj: spans
        )
        test_context.patch_object(
            AXTable, "_get_row_headers_from_table", side_effect=lambda table, row: headers
        )

    def _setup_table_description_mocks(
        self,
        test_context: OrcaTestContext,
        row_count=5,
        col_count=3,
        is_non_uniform=False,
        table_size_msg=None,
    ) -> None:
        """Set up common mocks for table description testing."""

        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import messages

        test_context.patch_object(AXObject, "supports_table", side_effect=lambda _obj: True)
        test_context.patch_object(AXTable, "get_row_count", side_effect=lambda table: row_count)
        test_context.patch_object(AXTable, "get_column_count", side_effect=lambda table: col_count)
        test_context.patch_object(
            AXTable, "is_non_uniform_table", side_effect=lambda table: is_non_uniform
        )
        if table_size_msg:
            test_context.patch_object(messages, "table_size", new=table_size_msg)
        if is_non_uniform:
            test_context.patch_object(messages, "TABLE_NON_UNIFORM", new="non uniform")

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_table_support",
                "supports_table": True,
                "raises_error": False,
                "expected_result": "mock_caption",
                "should_log": True,
            },
            {
                "id": "without_table_support",
                "supports_table": False,
                "raises_error": False,
                "expected_result": None,
                "should_log": False,
            },
            {
                "id": "with_glib_error",
                "supports_table": True,
                "raises_error": True,
                "expected_result": None,
                "should_log": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_caption(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable.get_caption with various support and error conditions."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(
            AXObject, "supports_table", side_effect=lambda _obj: case["supports_table"]
        )

        if case["raises_error"]:

            def raise_glib_error(obj):
                raise GLib.GError("Test error")

            test_context.patch_object(Atspi.Table, "get_caption", side_effect=raise_glib_error)
            from orca import debug

            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )
        else:
            mock_caption = (
                test_context.Mock(spec=Atspi.Accessible) if case["expected_result"] else None
            )
            test_context.patch_object(
                Atspi.Table, "get_caption", side_effect=lambda obj: mock_caption
            )

        result = AXTable.get_caption(mock_table)

        if case["expected_result"] == "mock_caption":
            assert result is not None
        else:
            assert result == case["expected_result"]

        if case["should_log"]:
            if case["raises_error"]:
                essential_modules["orca.debug"].print_message.assert_called()
            else:
                essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "col_prefer_attribute_available",
                "count_type": "column",
                "prefer_attribute": True,
                "attribute_count": 5,
                "physical_count": 4,
                "expected_result": 5,
                "supports_table": True,
                "raises_error": False,
                "attr_name": "colcount",
                "attr_value": "3",
                "expected_attr_result": 3,
            },
            {
                "id": "col_prefer_attribute_none_fallback",
                "count_type": "column",
                "prefer_attribute": True,
                "attribute_count": None,
                "physical_count": 4,
                "expected_result": 4,
                "supports_table": True,
                "raises_error": False,
                "attr_name": "colcount",
                "attr_value": None,
                "expected_attr_result": None,
            },
            {
                "id": "col_prefer_physical",
                "count_type": "column",
                "prefer_attribute": False,
                "attribute_count": 5,
                "physical_count": 4,
                "expected_result": 4,
                "supports_table": True,
                "raises_error": False,
                "attr_name": "colcount",
                "attr_value": "3",
                "expected_attr_result": 3,
            },
            {
                "id": "col_without_table_support",
                "count_type": "column",
                "prefer_attribute": True,
                "attribute_count": None,
                "physical_count": -1,
                "expected_result": -1,
                "supports_table": False,
                "raises_error": False,
                "attr_name": "colcount",
                "attr_value": "3",
                "expected_attr_result": 3,
            },
            {
                "id": "col_with_glib_error",
                "count_type": "column",
                "prefer_attribute": True,
                "attribute_count": None,
                "physical_count": -1,
                "expected_result": -1,
                "supports_table": True,
                "raises_error": True,
                "attr_name": "colcount",
                "attr_value": "3",
                "expected_attr_result": 3,
            },
            {
                "id": "row_prefer_attribute_available",
                "count_type": "row",
                "prefer_attribute": True,
                "attribute_count": 10,
                "physical_count": 8,
                "expected_result": 10,
                "supports_table": True,
                "raises_error": False,
                "attr_name": "rowcount",
                "attr_value": "7",
                "expected_attr_result": 7,
            },
            {
                "id": "row_prefer_attribute_none_fallback",
                "count_type": "row",
                "prefer_attribute": True,
                "attribute_count": None,
                "physical_count": 8,
                "expected_result": 8,
                "supports_table": True,
                "raises_error": False,
                "attr_name": "rowcount",
                "attr_value": None,
                "expected_attr_result": None,
            },
            {
                "id": "row_prefer_physical",
                "count_type": "row",
                "prefer_attribute": False,
                "attribute_count": 10,
                "physical_count": 8,
                "expected_result": 8,
                "supports_table": True,
                "raises_error": False,
                "attr_name": "rowcount",
                "attr_value": "7",
                "expected_attr_result": 7,
            },
            {
                "id": "row_without_table_support",
                "count_type": "row",
                "prefer_attribute": True,
                "attribute_count": None,
                "physical_count": -1,
                "expected_result": -1,
                "supports_table": False,
                "raises_error": False,
                "attr_name": "rowcount",
                "attr_value": "7",
                "expected_attr_result": 7,
            },
            {
                "id": "row_with_glib_error",
                "count_type": "row",
                "prefer_attribute": True,
                "attribute_count": None,
                "physical_count": -1,
                "expected_result": -1,
                "supports_table": True,
                "raises_error": True,
                "attr_name": "rowcount",
                "attr_value": "7",
                "expected_attr_result": 7,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_count_methods_scenarios(  # pylint: disable=too-many-locals
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable.get_column_count, get_row_count and their attribute methods."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        test_context.patch_object(
            AXObject, "supports_table", side_effect=lambda _obj: case["supports_table"]
        )

        if case["count_type"] == "column":
            count_method = AXTable.get_column_count
            attr_method = AXTable._get_column_count_from_attribute
            atspi_method_name = "get_n_columns"
            attr_method_name = "_get_column_count_from_attribute"
        else:
            count_method = AXTable.get_row_count
            attr_method = AXTable._get_row_count_from_attribute
            atspi_method_name = "get_n_rows"
            attr_method_name = "_get_row_count_from_attribute"

        test_context.patch_object(
            AXTable, attr_method_name, side_effect=lambda obj: case["attribute_count"]
        )

        if case["raises_error"] and case["supports_table"]:

            def raise_glib_error(obj):
                raise GLib.GError("Test error")

            test_context.patch_object(Atspi.Table, atspi_method_name, side_effect=raise_glib_error)
            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )
        else:
            test_context.patch_object(
                Atspi.Table, atspi_method_name, side_effect=lambda obj: case["physical_count"]
            )

        if (
            case["supports_table"]
            and not case["raises_error"]
            and case["prefer_attribute"] is not None
        ):
            result = count_method(mock_table, case["prefer_attribute"])
        else:
            result = count_method(mock_table)
        assert result == case["expected_result"]

        if (
            (case["attribute_count"] is None or not case["prefer_attribute"])
            and case["supports_table"]
            and not case["raises_error"]
        ):
            essential_modules["orca.debug"].print_tokens.assert_called()
        if case["raises_error"] and case["supports_table"]:
            essential_modules["orca.debug"].print_message.assert_called()

        attrs = {case["attr_name"]: case["attr_value"]} if case["attr_value"] else {}
        test_context.patch_object(AXObject, "get_attributes_dict", side_effect=lambda obj: attrs)
        attr_result = attr_method(mock_table)
        assert attr_result == case["expected_attr_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "uniform_table",
                "row_extents": [1, 1, 1, 1],
                "col_extents": [1, 1, 1, 1],
                "expected_result": False,
            },
            {
                "id": "row_span_greater_than_one",
                "row_extents": [2, 1, 1, 1],
                "col_extents": [1, 1, 1, 1],
                "expected_result": True,
            },
            {
                "id": "col_span_greater_than_one",
                "row_extents": [1, 1, 1, 1],
                "col_extents": [1, 2, 1, 1],
                "expected_result": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_non_uniform_table(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable.is_non_uniform_table."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        call_count = 0

        def mock_get_extent(extent_type):
            nonlocal call_count
            if extent_type == "row":
                result = case["row_extents"][call_count % len(case["row_extents"])]
            else:
                result = case["col_extents"][call_count % len(case["col_extents"])]
            call_count += 1
            return result

        test_context.patch_object(AXTable, "get_row_count", side_effect=lambda obj, prefer_attr: 2)
        test_context.patch_object(
            AXTable, "get_column_count", side_effect=lambda obj, prefer_attr: 2
        )
        test_context.patch_object(
            Atspi.Table,
            "get_row_extent_at",
            side_effect=lambda table, row, col: mock_get_extent("row")
        )
        test_context.patch_object(
            Atspi.Table,
            "get_column_extent_at",
            side_effect=lambda table, row, col: mock_get_extent("col")
        )
        result = AXTable.is_non_uniform_table(mock_table)
        assert result == case["expected_result"]

    def test_is_non_uniform_table_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.is_non_uniform_table handles GLib.GError."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca import debug

        def raise_glib_error(obj, row, col):
            raise GLib.GError("Test error")

        test_context.patch_object(AXTable, "get_row_count", side_effect=lambda obj, prefer_attr: 1)
        test_context.patch_object(
            AXTable, "get_column_count", side_effect=lambda obj, prefer_attr: 1
        )
        test_context.patch_object(Atspi.Table, "get_row_extent_at", side_effect=raise_glib_error)
        test_context.patch_object(
            debug, "print_message", new=essential_modules["orca.debug"].print_message
        )
        result = AXTable.is_non_uniform_table(mock_table)
        assert result is False
        essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_table_support",
                "supports_table": True,
                "raises_error": False,
                "expected_result": 2,
            },
            {
                "id": "without_table_support",
                "supports_table": False,
                "raises_error": False,
                "expected_result": 0,
            },
            {
                "id": "with_glib_error",
                "supports_table": True,
                "raises_error": True,
                "expected_result": 0,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_selected_column_count(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable.get_selected_column_count in various scenarios."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        test_context.patch_object(
            AXObject, "supports_table", return_value=case["supports_table"]
        )

        if case["supports_table"] and not case["raises_error"]:
            test_context.patch_object(
                Atspi.Table, "get_n_selected_columns", side_effect=lambda obj: 2
            )
        elif case["supports_table"] and case["raises_error"]:

            def raise_glib_error(obj):
                raise GLib.GError("Test error")

            test_context.patch_object(
                Atspi.Table, "get_n_selected_columns", side_effect=raise_glib_error
            )
            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )

        result = AXTable.get_selected_column_count(mock_table)
        assert result == case["expected_result"]

        if case["supports_table"] and not case["raises_error"]:
            essential_modules["orca.debug"].print_tokens.assert_called()
        elif case["raises_error"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_table_support",
                "supports_table": True,
                "raises_error": False,
                "expected_result": [0, 2, 4],
            },
            {
                "id": "without_table_support",
                "supports_table": False,
                "raises_error": False,
                "expected_result": [],
            },
            {
                "id": "with_glib_error",
                "supports_table": True,
                "raises_error": True,
                "expected_result": [],
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_selected_columns(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable.get_selected_columns in various scenarios."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        test_context.patch_object(
            AXObject, "supports_table", return_value=case["supports_table"]
        )

        if case["supports_table"] and not case["raises_error"]:
            selected_columns = [0, 2, 4]
            test_context.patch_object(
                Atspi.Table, "get_selected_columns", return_value=selected_columns
            )
        elif case["supports_table"] and case["raises_error"]:

            def raise_glib_error(obj):
                raise GLib.GError("Test error")

            test_context.patch_object(
                Atspi.Table, "get_selected_columns", side_effect=raise_glib_error
            )
            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )

        result = AXTable.get_selected_columns(mock_table)
        assert result == case["expected_result"]

        if case["supports_table"] and not case["raises_error"]:
            essential_modules["orca.debug"].print_tokens.assert_called()
        elif case["raises_error"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_table_support",
                "supports_table": True,
                "raises_error": False,
                "expected_result": 3,
            },
            {
                "id": "without_table_support",
                "supports_table": False,
                "raises_error": False,
                "expected_result": 0,
            },
            {
                "id": "with_glib_error",
                "supports_table": True,
                "raises_error": True,
                "expected_result": 0,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_selected_row_count(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable.get_selected_row_count in various scenarios."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        test_context.patch_object(
            AXObject, "supports_table", return_value=case["supports_table"]
        )

        if case["supports_table"] and not case["raises_error"]:
            test_context.patch_object(Atspi.Table, "get_n_selected_rows", return_value=3)
        elif case["supports_table"] and case["raises_error"]:

            def raise_glib_error(obj):
                raise GLib.GError("Test error")

            test_context.patch_object(
                Atspi.Table, "get_n_selected_rows", side_effect=raise_glib_error
            )
            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )

        result = AXTable.get_selected_row_count(mock_table)
        assert result == case["expected_result"]

        if case["supports_table"] and not case["raises_error"]:
            essential_modules["orca.debug"].print_tokens.assert_called()
        elif case["raises_error"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_table_support",
                "supports_table": True,
                "raises_error": False,
                "expected_result": [1, 3, 5],
            },
            {
                "id": "without_table_support",
                "supports_table": False,
                "raises_error": False,
                "expected_result": [],
            },
            {
                "id": "with_glib_error",
                "supports_table": True,
                "raises_error": True,
                "expected_result": [],
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_selected_rows(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable.get_selected_rows in various scenarios."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        test_context.patch_object(
            AXObject, "supports_table", return_value=case["supports_table"]
        )

        if case["supports_table"] and not case["raises_error"]:
            selected_rows = [1, 3, 5]
            test_context.patch_object(
                Atspi.Table, "get_selected_rows", return_value=selected_rows
            )
        elif case["supports_table"] and case["raises_error"]:

            def raise_glib_error(obj):
                raise GLib.GError("Test error")

            test_context.patch_object(
                Atspi.Table, "get_selected_rows", side_effect=raise_glib_error
            )
            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )

        result = AXTable.get_selected_rows(mock_table)
        assert result == case["expected_result"]

        if case["supports_table"] and not case["raises_error"]:
            essential_modules["orca.debug"].print_tokens.assert_called()
        elif case["raises_error"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "all_rows_selected",
                "supports_table": True,
                "row_count": 5,
                "selected_row_count": 5,
                "col_count": 3,
                "selected_col_count": 3,
                "expected_result": True,
            },
            {
                "id": "all_columns_selected",
                "supports_table": True,
                "row_count": 5,
                "selected_row_count": 3,
                "col_count": 3,
                "selected_col_count": 3,
                "expected_result": True,
            },
            {
                "id": "partial_selection",
                "supports_table": True,
                "row_count": 5,
                "selected_row_count": 3,
                "col_count": 3,
                "selected_col_count": 2,
                "expected_result": False,
            },
            {
                "id": "empty_table",
                "supports_table": True,
                "row_count": 0,
                "selected_row_count": 0,
                "col_count": 0,
                "selected_col_count": 0,
                "expected_result": False,
            },
            {
                "id": "without_table_support",
                "supports_table": False,
                "row_count": 0,
                "selected_row_count": 0,
                "col_count": 0,
                "selected_col_count": 0,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_all_cells_are_selected_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable.all_cells_are_selected with various scenarios."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(
            AXObject, "supports_table", return_value=case["supports_table"]
        )

        if case["supports_table"]:
            test_context.patch_object(
                AXTable, "get_row_count", return_value=case["row_count"]
            )
            test_context.patch_object(
                AXTable, "get_selected_row_count", return_value=case["selected_row_count"]
            )
            test_context.patch_object(
                AXTable, "get_column_count", return_value=case["col_count"]
            )
            test_context.patch_object(
                AXTable, "get_selected_column_count", return_value=case["selected_col_count"]
            )

        result = AXTable.all_cells_are_selected(mock_table)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_table_support",
                "supports_table": True,
                "raises_error": False,
                "expected_result_type": "mock_cell",
            },
            {
                "id": "without_table_support",
                "supports_table": False,
                "raises_error": False,
                "expected_result_type": None,
            },
            {
                "id": "with_glib_error",
                "supports_table": True,
                "raises_error": True,
                "expected_result_type": None,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_at(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable.get_cell_at in various scenarios."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(
            AXObject, "supports_table", return_value=case["supports_table"]
        )

        if case["supports_table"] and not case["raises_error"]:
            test_context.patch_object(
                Atspi.Table, "get_accessible_at", side_effect=lambda obj, row, col: mock_cell
            )
        elif case["supports_table"] and case["raises_error"]:

            def raise_glib_error(obj, row, col):
                raise GLib.GError("Test error")

            test_context.patch_object(
                Atspi.Table, "get_accessible_at", side_effect=raise_glib_error
            )

        result = AXTable.get_cell_at(mock_table, 1, 2)

        if case["expected_result_type"] == "mock_cell":
            assert result == mock_cell
            essential_modules["orca.debug"].print_tokens.assert_called()
        else:
            assert result is None
            if case["raises_error"]:
                essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "cell_has_index_attribute",
                "cell_index_attr": "5",
                "parent_role": Atspi.Role.BUTTON,
                "expected_index": 5,
            },
            {
                "id": "parent_is_table_cell",
                "cell_index_attr": "",
                "parent_role": Atspi.Role.TABLE_CELL,
                "expected_index": 3,
            },
            {
                "id": "use_index_in_parent",
                "cell_index_attr": None,
                "parent_role": Atspi.Role.BUTTON,
                "expected_index": 2,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_index(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable._get_cell_index."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject, "get_attribute", side_effect=lambda obj, attr: case["cell_index_attr"]
        )
        test_context.patch_object(AXObject, "get_parent", return_value=mock_parent)
        test_context.patch_object(AXObject, "get_role", return_value=case["parent_role"])
        test_context.patch_object(
            AXObject, "get_index_in_parent", side_effect=lambda obj: case["expected_index"]
        )
        result = AXTable._get_cell_index(mock_cell)
        if case["parent_role"] == Atspi.Role.TABLE_CELL:
            assert result == 3
        else:
            assert result == case["expected_index"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "table_cell_with_attributes",
                "supports_table_cell": True,
                "cell_role": Atspi.Role.TABLE_CELL,
                "prefer_attribute": True,
                "rowspan_attr": "2",
                "colspan_attr": "3",
                "expected_spans": (2, 3),
            },
            {
                "id": "table_interface_with_attributes",
                "supports_table_cell": False,
                "cell_role": Atspi.Role.TABLE_CELL,
                "prefer_attribute": True,
                "rowspan_attr": "2",
                "colspan_attr": "3",
                "expected_spans": (2, 3),
            },
            {
                "id": "table_cell_no_attributes",
                "supports_table_cell": True,
                "cell_role": Atspi.Role.TABLE_CELL,
                "prefer_attribute": False,
                "rowspan_attr": "2",
                "colspan_attr": "3",
                "expected_spans": (2, 1),
            },
            {
                "id": "table_cell_no_attr_values",
                "supports_table_cell": True,
                "cell_role": Atspi.Role.TABLE_CELL,
                "prefer_attribute": True,
                "rowspan_attr": None,
                "colspan_attr": None,
                "expected_spans": (2, 1),
            },
            {
                "id": "not_table_cell",
                "supports_table_cell": False,
                "cell_role": Atspi.Role.BUTTON,
                "prefer_attribute": True,
                "rowspan_attr": "2",
                "colspan_attr": "3",
                "expected_spans": (-1, -1),
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_spans(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable.get_cell_spans."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject

        test_context.patch_object(
            AXUtilitiesRole,
            "is_table_cell_or_header",
            side_effect=lambda obj: case["cell_role"] == Atspi.Role.TABLE_CELL,
        )
        test_context.patch_object(
            AXObject, "supports_table_cell", side_effect=lambda obj: case["supports_table_cell"]
        )
        test_context.patch_object(
            AXTable, "_get_cell_spans_from_table_cell", return_value=(2, 1)
        )
        test_context.patch_object(AXTable, "_get_cell_spans_from_table", return_value=(1, 2))
        test_context.patch_object(
            AXTable,
            "_get_cell_spans_from_attribute",
            side_effect=lambda obj: (case["rowspan_attr"], case["colspan_attr"]),
        )
        result = AXTable.get_cell_spans(mock_cell, case["prefer_attribute"])
        assert result == case["expected_spans"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "both_attributes_present",
                "rowspan_attr": "2",
                "colspan_attr": "3",
                "expected_spans": ("2", "3"),
            },
            {
                "id": "only_colspan",
                "rowspan_attr": None,
                "colspan_attr": "3",
                "expected_spans": (None, "3"),
            },
            {
                "id": "only_rowspan",
                "rowspan_attr": "2",
                "colspan_attr": None,
                "expected_spans": ("2", None),
            },
            {
                "id": "no_attributes",
                "rowspan_attr": None,
                "colspan_attr": None,
                "expected_spans": (None, None),
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_spans_from_attribute(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable._get_cell_spans_from_attribute."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        attrs = {}
        if case["rowspan_attr"]:
            attrs["rowspan"] = case["rowspan_attr"]
        if case["colspan_attr"]:
            attrs["colspan"] = case["colspan_attr"]
        test_context.patch_object(AXObject, "get_attributes_dict", side_effect=lambda obj: attrs)
        result = AXTable._get_cell_spans_from_attribute(mock_cell)
        assert result == case["expected_spans"]
        essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_table_cell_support",
                "supports_table_cell": True,
                "raises_error": False,
                "expected_result": (2, 3),
            },
            {
                "id": "without_table_cell_support",
                "supports_table_cell": False,
                "raises_error": False,
                "expected_result": (-1, -1),
            },
            {
                "id": "with_glib_error",
                "supports_table_cell": True,
                "raises_error": True,
                "expected_result": (-1, -1),
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_spans_from_table_cell(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable._get_cell_spans_from_table_cell in various scenarios."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        test_context.patch_object(
            AXObject, "supports_table_cell", return_value=case["supports_table_cell"]
        )

        if case["supports_table_cell"] and not case["raises_error"]:
            test_context.patch_object(Atspi.TableCell, "get_row_span", return_value=2)
            test_context.patch_object(Atspi.TableCell, "get_column_span", return_value=3)
        elif case["supports_table_cell"] and case["raises_error"]:

            def raise_glib_error(obj):
                raise GLib.GError("Test error")

            test_context.patch_object(Atspi.TableCell, "get_row_span", side_effect=raise_glib_error)
            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )

        result = AXTable._get_cell_spans_from_table_cell(mock_cell)
        assert result == case["expected_result"]

        if case["supports_table_cell"] and not case["raises_error"]:
            essential_modules["orca.debug"].print_tokens.assert_called()
        elif case["raises_error"]:
            essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "table_cell_success",
                "scenario": "table_cell",
                "obj_type": "mock",
                "expected_result": "table",
                "expects_debug": False,
            },
            {
                "id": "table_cell_glib_error",
                "scenario": "table_cell_error",
                "obj_type": "mock",
                "expected_result": "table",
                "expects_debug": True,
            },
            {
                "id": "table_object",
                "scenario": "table_object",
                "obj_type": "mock",
                "expected_result": "table",
                "expects_debug": False,
            },
            {
                "id": "none_object",
                "scenario": "none_object",
                "obj_type": "none",
                "expected_result": None,
                "expects_debug": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_table(  # pylint: disable=too-many-locals
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable.get_table with various scenarios."""

        if case["scenario"] in ["table_cell_error", "table_object"]:
            essential_modules = self._setup_dependencies(test_context)
        else:
            essential_modules = self._setup_dependencies(test_context)

        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        if case["obj_type"] == "none":
            result = AXTable.get_table(None)
            assert result is None
            return

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        if case["scenario"] == "table_cell":
            test_context.patch_object(AXObject, "supports_table_cell", return_value=True)
            test_context.patch_object(
                Atspi.TableCell, "get_table", side_effect=lambda obj: mock_table
            )
            test_context.patch_object(AXObject, "supports_table", return_value=True)
        elif case["scenario"] == "table_cell_error":

            def raise_glib_error(obj):
                raise GLib.GError("Test error")

            def is_table(obj):
                return obj == mock_table

            self._setup_table_support_mocks(test_context, supports_table_cell=True)
            self._setup_table_role_mocks(test_context, is_table_func=is_table)
            self._setup_debug_message_mock(test_context, essential_modules)

            test_context.patch_object(Atspi.TableCell, "get_table", side_effect=raise_glib_error)
            test_context.patch_object(AXObject, "supports_table", side_effect=is_table)
            test_context.patch_object(
                AXObject, "find_ancestor", side_effect=lambda obj, func: mock_table
            )
        elif case["scenario"] == "table_object":
            self._setup_table_support_mocks(
                test_context, supports_table_cell=False, supports_table=True
            )
            self._setup_table_role_mocks(test_context, is_table_func=lambda _obj: True)
            mock_obj = mock_table

        result = AXTable.get_table(mock_obj)

        if case["expected_result"] == "table":
            assert result == mock_table
        else:
            assert result == case["expected_result"]

        if case["expects_debug"]:
            essential_modules["orca.debug"].print_message.assert_called()

    def test_is_layout_table_with_layout_guess(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.is_layout_table with layout-guess attribute."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        attrs = {"layout-guess": "true"}
        test_context.patch_object(AXObject, "get_attributes_dict", side_effect=lambda obj: attrs)
        test_context.patch_object(AXUtilitiesRole, "is_table", return_value=True)
        result = AXTable.is_layout_table(mock_table)
        assert result is True
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_is_layout_table_without_table_support(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.is_layout_table without table support."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        attrs: dict[str, str | int | float | bool] = {}
        test_context.patch_object(AXObject, "get_attributes_dict", side_effect=lambda obj: attrs)
        test_context.patch_object(AXUtilitiesRole, "is_table", return_value=True)
        test_context.patch_object(AXObject, "supports_table", return_value=False)
        result = AXTable.is_layout_table(mock_table)
        assert result is True
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_is_layout_table_with_headers(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.is_layout_table with headers present."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        attrs: dict[str, str | int | float | bool] = {}
        test_context.patch_object(AXObject, "get_attributes_dict", side_effect=lambda obj: attrs)
        test_context.patch_object(AXUtilitiesRole, "is_table", return_value=True)
        test_context.patch_object(AXObject, "supports_table", return_value=True)
        test_context.patch_object(AXTable, "has_column_headers", return_value=True)
        test_context.patch_object(AXTable, "has_row_headers", return_value=False)
        result = AXTable.is_layout_table(mock_table)
        assert result is False
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_is_layout_table_with_name(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.is_layout_table with table name present."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        attrs: dict[str, str | int | float | bool] = {}
        self._setup_table_role_mocks(test_context, is_table_func=lambda _obj: True)
        self._setup_table_support_mocks(test_context, supports_table=True)
        self._setup_layout_table_mocks(test_context, name="Table Name")
        test_context.patch_object(AXObject, "get_attributes_dict", side_effect=lambda obj: attrs)
        result = AXTable.is_layout_table(mock_table)
        assert result is False
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_is_layout_table_with_caption(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.is_layout_table with table caption present."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_caption = test_context.Mock(spec=Atspi.Accessible)
        attrs: dict[str, str | int | float | bool] = {}

        self._setup_table_role_mocks(test_context, is_table_func=lambda _obj: True)
        self._setup_table_support_mocks(test_context, supports_table=True)
        self._setup_layout_table_mocks(test_context, caption=mock_caption)

        test_context.patch_object(AXObject, "get_attributes_dict", side_effect=lambda obj: attrs)

        result = AXTable.is_layout_table(mock_table)
        assert result is False
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_get_first_cell(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_first_cell."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_cell
        )
        result = AXTable.get_first_cell(mock_table)
        assert result == mock_cell

    def test_get_last_cell(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_last_cell."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXTable, "get_row_count", return_value=3)
        test_context.patch_object(AXTable, "get_column_count", return_value=4)
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_cell
        )
        result = AXTable.get_last_cell(mock_table)
        assert result == mock_cell

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "move_up_one_row", "cell_row": 2, "cell_col": 3},
            {"id": "top_row", "cell_row": 0, "cell_col": 3},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_above(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable.get_cell_above."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_result_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXTable,
            "get_cell_coordinates",
            side_effect=lambda obj, prefer_attribute: (case["cell_row"], case["cell_col"]),
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_result_cell
        )
        result = AXTable.get_cell_above(mock_cell)
        assert result == mock_result_cell

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "single_row_span", "cell_row": 2, "cell_col": 3, "row_span": 1},
            {"id": "multi_row_span", "cell_row": 2, "cell_col": 3, "row_span": 2},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_below(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable.get_cell_below."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_result_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXTable,
            "get_cell_coordinates",
            side_effect=lambda obj, prefer_attribute: (case["cell_row"], case["cell_col"]),
        )
        test_context.patch_object(
            AXTable,
            "get_cell_spans",
            side_effect=lambda obj, prefer_attribute: (case["row_span"], 1)
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_result_cell
        )
        result = AXTable.get_cell_below(mock_cell)
        assert result == mock_result_cell

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "move_left_one_column", "cell_row": 2, "cell_col": 3},
            {"id": "leftmost_column", "cell_row": 2, "cell_col": 0},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_on_left(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable.get_cell_on_left."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_result_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXTable,
            "get_cell_coordinates",
            side_effect=lambda obj, prefer_attribute: (case["cell_row"], case["cell_col"]),
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_result_cell
        )
        result = AXTable.get_cell_on_left(mock_cell)
        assert result == mock_result_cell

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "single_col_span", "cell_row": 2, "cell_col": 3, "col_span": 1},
            {"id": "multi_col_span", "cell_row": 2, "cell_col": 3, "col_span": 2},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_on_right(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable.get_cell_on_right."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_result_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXTable,
            "get_cell_coordinates",
            side_effect=lambda obj, prefer_attribute: (case["cell_row"], case["cell_col"]),
        )
        test_context.patch_object(
            AXTable,
            "get_cell_spans",
            side_effect=lambda obj, prefer_attribute: (1, case["col_span"])
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_result_cell
        )
        result = AXTable.get_cell_on_right(mock_cell)
        assert result == mock_result_cell

    def test_get_start_of_row(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_start_of_row."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_result_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXTable, "get_cell_coordinates", return_value=(2, 3)
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_result_cell
        )
        result = AXTable.get_start_of_row(mock_cell)
        assert result == mock_result_cell

    def test_get_end_of_row(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_end_of_row."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_result_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXTable, "get_cell_coordinates", return_value=(2, 3)
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(AXTable, "get_column_count", return_value=5)
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_result_cell
        )
        result = AXTable.get_end_of_row(mock_cell)
        assert result == mock_result_cell

    def test_get_top_of_column(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_top_of_column."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_result_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXTable, "get_cell_coordinates", return_value=(2, 3)
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_result_cell
        )
        result = AXTable.get_top_of_column(mock_cell)
        assert result == mock_result_cell

    def test_get_bottom_of_column(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_bottom_of_column."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_result_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXTable, "get_cell_coordinates", return_value=(2, 3)
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(AXTable, "get_row_count", return_value=8)
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_result_cell
        )
        result = AXTable.get_bottom_of_column(mock_cell)
        assert result == mock_result_cell

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "formula_attribute",
                "formula_attr": "=SUM(A1:A5)",
                "formula_attr_alt": None,
                "expected_result": "=SUM(A1:A5)",
            },
            {
                "id": "formula_alt_attribute",
                "formula_attr": None,
                "formula_attr_alt": "=A1+B1",
                "expected_result": "=A1+B1",
            },
            {
                "id": "no_formula",
                "formula_attr": None,
                "formula_attr_alt": None,
                "expected_result": None,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_formula(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable.get_cell_formula."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        attrs = {}
        if case["formula_attr"]:
            attrs["formula"] = case["formula_attr"]
        if case["formula_attr_alt"]:
            attrs["Formula"] = case["formula_attr_alt"]
        test_context.patch_object(
            AXObject, "get_attributes_dict", side_effect=lambda obj, use_cache: attrs
        )
        result = AXTable.get_cell_formula(mock_cell)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "first_cell", "cell_row": 0, "cell_col": 0, "expected_result": True},
            {"id": "not_first_cell", "cell_row": 0, "cell_col": 1, "expected_result": False},
            {"id": "not_first_row", "cell_row": 1, "cell_col": 0, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_is_first_cell(self, test_context, case: dict) -> None:
        """Test AXTable.is_first_cell."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        test_context.patch_object(
            AXTable,
            "get_cell_coordinates",
            side_effect=lambda obj, prefer_attribute: (case["cell_row"], case["cell_col"]),
        )
        result = AXTable.is_first_cell(mock_cell)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "last_cell",
                "cell_row": 2,
                "cell_col": 3,
                "row_count": 3,
                "col_count": 4,
                "expected_result": True,
            },
            {
                "id": "not_last_row",
                "cell_row": 1,
                "cell_col": 3,
                "row_count": 3,
                "col_count": 4,
                "expected_result": False,
            },
            {
                "id": "not_last_column",
                "cell_row": 2,
                "cell_col": 2,
                "row_count": 3,
                "col_count": 4,
                "expected_result": False,
            },
            {
                "id": "invalid_coordinates",
                "cell_row": -1,
                "cell_col": -1,
                "row_count": 3,
                "col_count": 4,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_last_cell(
        self,
        test_context,
        case: dict,
    ) -> None:
        """Test AXTable.is_last_cell."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = (
            test_context.Mock(spec=Atspi.Accessible)
            if case["cell_row"] >= 0 and case["cell_col"] >= 0
            else None
        )
        test_context.patch_object(
            AXTable,
            "get_cell_coordinates",
            side_effect=lambda obj, prefer_attribute: (case["cell_row"], case["cell_col"]),
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(
            AXTable, "get_row_count", side_effect=lambda table, prefer_attribute: case["row_count"]
        )
        test_context.patch_object(
            AXTable,
            "get_column_count",
            side_effect=lambda table, prefer_attribute: case["col_count"]
        )
        result = AXTable.is_last_cell(mock_cell)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "start_of_row", "cell_col": 0, "expected_result": True},
            {"id": "not_start_of_row", "cell_col": 1, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_is_start_of_row(self, test_context, case: dict) -> None:
        """Test AXTable.is_start_of_row."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        test_context.patch_object(
            AXTable,
            "get_cell_coordinates",
            side_effect=lambda obj, prefer_attribute: (2, case["cell_col"])
        )
        result = AXTable.is_start_of_row(mock_cell)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "end_of_row", "cell_col": 3, "col_count": 4, "expected_result": True},
            {"id": "not_end_of_row", "cell_col": 2, "col_count": 4, "expected_result": False},
            {"id": "invalid_column", "cell_col": -1, "col_count": 4, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_is_end_of_row(self, test_context, case: dict) -> None:
        """Test AXTable.is_end_of_row."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible) if case["cell_col"] >= 0 else None
        test_context.patch_object(
            AXTable,
            "get_cell_coordinates",
            side_effect=lambda obj, prefer_attribute: (2, case["cell_col"])
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(
            AXTable,
            "get_column_count",
            side_effect=lambda table, prefer_attribute: case["col_count"]
        )
        result = AXTable.is_end_of_row(mock_cell)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "top_of_column", "cell_row": 0, "expected_result": True},
            {"id": "not_top_of_column", "cell_row": 1, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_is_top_of_column(self, test_context, case: dict) -> None:
        """Test AXTable.is_top_of_column."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        test_context.patch_object(
            AXTable,
            "get_cell_coordinates",
            side_effect=lambda obj, prefer_attribute: (case["cell_row"], 3)
        )
        result = AXTable.is_top_of_column(mock_cell)
        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "bottom_of_column", "cell_row": 4, "row_count": 5, "expected_result": True},
            {"id": "not_bottom_of_column", "cell_row": 3, "row_count": 5, "expected_result": False},
            {"id": "invalid_row", "cell_row": -1, "row_count": 5, "expected_result": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_is_bottom_of_column(self, test_context, case: dict) -> None:
        """Test AXTable.is_bottom_of_column."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible) if case["cell_row"] >= 0 else None
        test_context.patch_object(
            AXTable,
            "get_cell_coordinates",
            side_effect=lambda obj, prefer_attribute: (case["cell_row"], 3)
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(
            AXTable, "get_row_count", side_effect=lambda table, prefer_attribute: case["row_count"]
        )
        result = AXTable.is_bottom_of_column(mock_cell)
        assert result == case["expected_result"]

    def test_get_table_description_for_presentation_with_support(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable.get_table_description_for_presentation with table support."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import messages

        test_context.patch_object(AXObject, "supports_table", return_value=True)
        test_context.patch_object(AXTable, "get_row_count", return_value=5)
        test_context.patch_object(AXTable, "get_column_count", return_value=3)
        test_context.patch_object(AXTable, "is_non_uniform_table", return_value=False)
        test_context.patch_object(
            messages, "table_size", side_effect=lambda rows, cols: f"{rows} by {cols} table"
        )
        result = AXTable.get_table_description_for_presentation(mock_table)
        assert result == "5 by 3 table"

    def test_get_table_description_for_presentation_non_uniform(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable.get_table_description_for_presentation with non-uniform table."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        self._setup_table_description_mocks(
            test_context,
            row_count=5,
            col_count=3,
            is_non_uniform=True,
            table_size_msg=lambda rows, cols: f"{rows} by {cols} table",
        )
        result = AXTable.get_table_description_for_presentation(mock_table)
        assert result == "non uniform 5 by 3 table"

    def test_get_table_description_for_presentation_without_support(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable.get_table_description_for_presentation without table support."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table", return_value=False)
        result = AXTable.get_table_description_for_presentation(mock_table)
        assert result == ""

    def test_clear_cache_now(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.clear_cache_now."""

        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        clear_called = []

        def mock_clear(reason):
            clear_called.append(reason)

        test_context.patch(
            "orca.ax_table.AXTable._clear_all_dictionaries", new=mock_clear
        )
        AXTable.clear_cache_now("test reason")
        assert clear_called == ["test reason"]

    def test_clear_all_dictionaries(self, test_context: OrcaTestContext) -> None:
        """Test AXTable._clear_all_dictionaries."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca import debug

        AXTable.CAPTIONS[123] = test_context.Mock()
        AXTable.PHYSICAL_COORDINATES_FROM_CELL[456] = (1, 2)
        AXTable.COLUMN_HEADERS_FOR_CELL[789] = [test_context.Mock()]
        test_context.patch_object(
            debug, "print_message", new=essential_modules["orca.debug"].print_message
        )
        AXTable._clear_all_dictionaries("test clear")
        assert len(AXTable.CAPTIONS) == 0
        assert len(AXTable.PHYSICAL_COORDINATES_FROM_CELL) == 0
        assert len(AXTable.COLUMN_HEADERS_FOR_CELL) == 0
        essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_negative_index",
                "scenario": "negative_index",
                "expected_result": (-1, -1),
            },
            {"id": "with_glib_error", "scenario": "glib_error", "expected_result": (-1, -1)},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_cell_spans_from_table_error_scenarios(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXTable._get_cell_spans_from_table error handling scenarios."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)

        if case["scenario"] == "negative_index":
            self._setup_dependencies(test_context)
            from orca.ax_table import AXTable

            test_context.patch_object(AXTable, "_get_cell_index", return_value=-1)
            result = AXTable._get_cell_spans_from_table(mock_cell)
            assert result == case["expected_result"]
        else:  # glib_error
            mock_table = test_context.Mock(spec=Atspi.Accessible)
            essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
            from orca.ax_table import AXTable
            from orca.ax_object import AXObject
            from orca.ax_utilities_role import AXUtilitiesRole
            from orca import debug

            def raise_glib_error(obj, index):
                raise GLib.GError("Test error")

            test_context.patch_object(AXTable, "_get_cell_index", return_value=5)
            test_context.patch_object(AXTable, "get_table", return_value=mock_table)
            test_context.patch_object(AXObject, "supports_table", return_value=True)
            test_context.patch_object(AXUtilitiesRole, "is_tree", return_value=False)
            test_context.patch_object(
                Atspi.Table, "get_row_column_extents_at_index", side_effect=raise_glib_error
            )
            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )
            result = AXTable._get_cell_spans_from_table(mock_cell)
            assert result == case["expected_result"]
            essential_modules["orca.debug"].print_message.assert_called()

    def test_get_cell_spans_from_table_no_table(self, test_context: OrcaTestContext) -> None:
        """Test AXTable._get_cell_spans_from_table with no table found."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        test_context.patch_object(AXTable, "_get_cell_index", return_value=5)
        test_context.patch_object(AXTable, "get_table", return_value=None)
        result = AXTable._get_cell_spans_from_table(mock_cell)
        assert result == (-1, -1)

    def test_get_cell_spans_from_table_tree_table(self, test_context: OrcaTestContext) -> None:
        """Test AXTable._get_cell_spans_from_table with tree table."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXTable, "_get_cell_index", return_value=5)
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(AXObject, "supports_table", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_tree", return_value=True)
        result = AXTable._get_cell_spans_from_table(mock_cell)
        assert result == (1, 1)

    def test_get_cell_spans_from_table_failed_result(self, test_context: OrcaTestContext) -> None:
        """Test AXTable._get_cell_spans_from_table with failed result."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        self._setup_cell_span_mocks(test_context, cell_index=5, table_obj=mock_table)
        result = AXTable._get_cell_spans_from_table(mock_cell)
        assert result == (-1, -1)

    def test_get_cell_spans_from_table_span_validation(self, test_context: OrcaTestContext) -> None:
        """Test AXTable._get_cell_spans_from_table with span validation."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_result = test_context.Mock()
        mock_result.__getitem__ = lambda self, index: True
        mock_result.row_extents = 5
        mock_result.col_extents = 3
        test_context.patch_object(AXTable, "_get_cell_index", return_value=5)
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(AXObject, "supports_table", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_tree", return_value=False)
        test_context.patch_object(
            Atspi.Table,
            "get_row_column_extents_at_index",
            side_effect=lambda table, index: mock_result
        )
        test_context.patch_object(
            AXTable, "get_row_count", side_effect=lambda table, prefer_attr: 3
        )
        test_context.patch_object(
            AXTable, "get_column_count", side_effect=lambda table, prefer_attr: 2
        )
        result = AXTable._get_cell_spans_from_table(mock_cell)
        assert result == (1, 1)
        essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "with_table_support", "scenario": "table_support"},
            {"id": "with_glib_error", "scenario": "glib_error"},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_column_headers_from_table_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable._get_column_headers_from_table with different scenarios."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        if case["scenario"] == "table_support":
            mock_header = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(AXObject, "supports_table", return_value=True)
            test_context.patch_object(
                Atspi.Table, "get_column_header", side_effect=lambda table, col: mock_header
            )
            result = AXTable._get_column_headers_from_table(mock_table, 2)
            assert result == [mock_header]
            essential_modules["orca.debug"].print_tokens.assert_called()
        else:  # glib_error
            from orca import debug

            def raise_glib_error(obj, column):
                raise GLib.GError("Test error")

            test_context.patch_object(AXObject, "supports_table", return_value=True)
            test_context.patch_object(
                Atspi.Table, "get_column_header", side_effect=raise_glib_error
            )
            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )
            result = AXTable._get_column_headers_from_table(mock_table, 2)
            assert not result
            essential_modules["orca.debug"].print_message.assert_called()

    def test_get_column_headers_from_table_without_support(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_column_headers_from_table without table support."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_table", return_value=False)
        result = AXTable._get_column_headers_from_table(mock_table, 2)
        assert not result

    def test_get_column_headers_from_table_negative_column(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_column_headers_from_table with negative column."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_table", return_value=True)
        result = AXTable._get_column_headers_from_table(mock_table, -1)
        assert not result

    def test_get_column_headers_from_table_cell_with_support(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_column_headers_from_table_cell with table cell support."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_headers = [
            test_context.Mock(spec=Atspi.Accessible),
            test_context.Mock(spec=Atspi.Accessible),
        ]
        test_context.patch_object(AXObject, "supports_table_cell", return_value=True)
        test_context.patch_object(
            Atspi.TableCell, "get_column_header_cells", return_value=mock_headers
        )
        result = AXTable._get_column_headers_from_table_cell(mock_cell)
        assert result == mock_headers
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_get_column_headers_from_table_cell_without_support(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_column_headers_from_table_cell without table cell support."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table_cell", return_value=False)
        result = AXTable._get_column_headers_from_table_cell(mock_cell)
        assert result == []

    def test_get_column_headers_from_table_cell_with_glib_error(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_column_headers_from_table_cell handles GLib.GError."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        test_context.patch_object(AXObject, "supports_table_cell", return_value=True)
        test_context.patch_object(
            Atspi.TableCell, "get_column_header_cells", side_effect=raise_glib_error
        )
        test_context.patch_object(
            debug, "print_message", new=essential_modules["orca.debug"].print_message
        )
        result = AXTable._get_column_headers_from_table_cell(mock_cell)
        assert result == []
        essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "with_table_support", "scenario": "table_support"},
            {"id": "with_glib_error", "scenario": "glib_error"},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_row_headers_from_table_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable._get_row_headers_from_table with different scenarios."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        if case["scenario"] == "table_support":
            mock_header = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(AXObject, "supports_table", return_value=True)
            test_context.patch_object(
                Atspi.Table, "get_row_header", side_effect=lambda table, row: mock_header
            )
            result = AXTable._get_row_headers_from_table(mock_table, 1)
            assert result == [mock_header]
            essential_modules["orca.debug"].print_tokens.assert_called()
        else:  # glib_error
            from orca import debug

            def raise_glib_error(obj, row):
                raise GLib.GError("Test error")

            test_context.patch_object(AXObject, "supports_table", return_value=True)
            test_context.patch_object(Atspi.Table, "get_row_header", side_effect=raise_glib_error)
            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )
            result = AXTable._get_row_headers_from_table(mock_table, 1)
            assert not result
            essential_modules["orca.debug"].print_message.assert_called()

    def test_get_row_headers_from_table_without_support(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_row_headers_from_table without table support."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_table", return_value=False)
        result = AXTable._get_row_headers_from_table(mock_table, 1)
        assert not result

    def test_get_row_headers_from_table_negative_row(self, test_context: OrcaTestContext) -> None:
        """Test AXTable._get_row_headers_from_table with negative row."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_table", return_value=True)
        result = AXTable._get_row_headers_from_table(mock_table, -1)
        assert not result

    def test_get_row_headers_from_table_cell_with_support(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_row_headers_from_table_cell with table cell support."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_headers = [
            test_context.Mock(spec=Atspi.Accessible),
            test_context.Mock(spec=Atspi.Accessible),
        ]
        test_context.patch_object(AXObject, "supports_table_cell", return_value=True)
        test_context.patch_object(
            Atspi.TableCell, "get_row_header_cells", return_value=mock_headers
        )
        result = AXTable._get_row_headers_from_table_cell(mock_cell)
        assert result == mock_headers
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_get_row_headers_from_table_cell_without_support(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_row_headers_from_table_cell without table cell support."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table_cell", return_value=False)
        result = AXTable._get_row_headers_from_table_cell(mock_cell)
        assert result == []

    def test_get_row_headers_from_table_cell_with_glib_error(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_row_headers_from_table_cell handles GLib.GError."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        test_context.patch_object(AXObject, "supports_table_cell", return_value=True)
        test_context.patch_object(
            Atspi.TableCell, "get_row_header_cells", side_effect=raise_glib_error
        )
        test_context.patch_object(
            debug, "print_message", new=essential_modules["orca.debug"].print_message
        )
        result = AXTable._get_row_headers_from_table_cell(mock_cell)
        assert result == []
        essential_modules["orca.debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "old_cell_not_table_cell", "old_cell_type": "not_table_cell"},
            {"id": "no_old_cell", "old_cell_type": None},
            {"id": "different_headers", "old_cell_type": "table_cell"},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_new_row_headers_scenarios(  # pylint: disable=too-many-locals
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXTable.get_new_row_headers with various scenarios."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        if case["old_cell_type"] == "not_table_cell":
            from orca.ax_object import AXObject
            from orca.ax_utilities_role import AXUtilitiesRole

            mock_old_cell = test_context.Mock(spec=Atspi.Accessible)
            mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
            mock_headers = [test_context.Mock(spec=Atspi.Accessible)]
            test_context.patch_object(
                AXUtilitiesRole,
                "is_table_cell_or_header",
                side_effect=lambda obj: obj == mock_ancestor
            )
            test_context.patch_object(
                AXObject, "find_ancestor", side_effect=lambda obj, func: mock_ancestor
            )
            test_context.patch_object(
                AXTable,
                "get_row_headers",
                side_effect=lambda obj: mock_headers if obj == mock_cell else []
            )
            result = AXTable.get_new_row_headers(mock_cell, mock_old_cell)
            assert result == mock_headers
        elif case["old_cell_type"] is None:
            mock_headers = [test_context.Mock(spec=Atspi.Accessible)]
            test_context.patch_object(AXTable, "get_row_headers", return_value=mock_headers)
            result = AXTable.get_new_row_headers(mock_cell, None)
            assert result == mock_headers
        else:  # table_cell with different headers
            mock_old_cell = test_context.Mock(spec=Atspi.Accessible)
            mock_header1 = test_context.Mock(spec=Atspi.Accessible)
            mock_header2 = test_context.Mock(spec=Atspi.Accessible)
            mock_header3 = test_context.Mock(spec=Atspi.Accessible)

            def get_headers(obj):
                if obj == mock_cell:
                    return [mock_header1, mock_header2, mock_header3]
                return [mock_header1, mock_header2]

            test_context.patch_object(AXTable, "get_row_headers", side_effect=get_headers)
            result = AXTable.get_new_row_headers(mock_cell, mock_old_cell)
            assert result == [mock_header3]

    @pytest.mark.parametrize(
        "old_cell_type",
        [
            pytest.param("not_table_cell", id="old_cell_not_table_cell"),
            pytest.param(None, id="no_old_cell"),
            pytest.param("table_cell", id="different_headers"),
        ],
    )
    def test_get_new_column_headers_scenarios(  # pylint: disable=too-many-locals
        self,
        test_context: OrcaTestContext,
        old_cell_type: str | None,
    ) -> None:
        """Test AXTable.get_new_column_headers with various scenarios."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        if old_cell_type == "not_table_cell":
            from orca.ax_object import AXObject
            from orca.ax_utilities_role import AXUtilitiesRole

            mock_old_cell = test_context.Mock(spec=Atspi.Accessible)
            mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
            mock_headers = [test_context.Mock(spec=Atspi.Accessible)]
            test_context.patch_object(
                AXUtilitiesRole,
                "is_table_cell_or_header",
                side_effect=lambda obj: obj == mock_ancestor
            )
            test_context.patch_object(
                AXObject, "find_ancestor", side_effect=lambda obj, func: mock_ancestor
            )
            test_context.patch_object(
                AXTable,
                "get_column_headers",
                side_effect=lambda obj: mock_headers if obj == mock_cell else []
            )
            result = AXTable.get_new_column_headers(mock_cell, mock_old_cell)
            assert result == mock_headers
        elif old_cell_type is None:
            mock_headers = [test_context.Mock(spec=Atspi.Accessible)]
            test_context.patch_object(
                AXTable, "get_column_headers", return_value=mock_headers
            )
            result = AXTable.get_new_column_headers(mock_cell, None)
            assert result == mock_headers
        else:  # table_cell with different headers
            mock_old_cell = test_context.Mock(spec=Atspi.Accessible)
            mock_header1 = test_context.Mock(spec=Atspi.Accessible)
            mock_header2 = test_context.Mock(spec=Atspi.Accessible)
            mock_header3 = test_context.Mock(spec=Atspi.Accessible)

            def get_headers(obj):
                if obj == mock_cell:
                    return [mock_header1, mock_header2, mock_header3]
                return [mock_header1, mock_header2]

            test_context.patch_object(AXTable, "get_column_headers", side_effect=get_headers)
            result = AXTable.get_new_column_headers(mock_cell, mock_old_cell)
            assert result == [mock_header3]

    def test_get_row_headers_not_table_cell(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_row_headers with cell that is not a table cell."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_utilities_role import AXUtilitiesRole

        test_context.patch_object(AXUtilitiesRole, "is_table_cell", return_value=False)
        result = AXTable.get_row_headers(mock_cell)
        assert result == []

    @pytest.mark.parametrize(
        "header_scenario",
        [
            pytest.param("dynamic_header", id="with_dynamic_header"),
            pytest.param("multiple_headers", id="with_multiple_headers"),
            pytest.param("nested_headers", id="with_nested_headers"),
        ],
    )
    def test_get_row_headers_scenarios(
        self,
        test_context: OrcaTestContext,
        header_scenario: str,
    ) -> None:
        """Test AXTable.get_row_headers with different header scenarios."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_utilities_role import AXUtilitiesRole

        test_context.patch_object(AXUtilitiesRole, "is_table_cell", return_value=True)

        if header_scenario == "dynamic_header":
            mock_header = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(
                AXTable, "get_dynamic_row_header", return_value=mock_header
            )
            result = AXTable.get_row_headers(mock_cell)
            assert result == [mock_header]
        elif header_scenario == "multiple_headers":
            mock_headers = [
                test_context.Mock(spec=Atspi.Accessible),
                test_context.Mock(spec=Atspi.Accessible),
            ]
            test_context.patch_object(AXTable, "get_dynamic_row_header", return_value=None)
            test_context.patch_object(AXTable, "_get_row_headers", return_value=mock_headers)
            result = AXTable.get_row_headers(mock_cell)
            assert result == mock_headers
        else:  # nested_headers
            mock_header1 = test_context.Mock(spec=Atspi.Accessible)
            mock_header2 = test_context.Mock(spec=Atspi.Accessible)
            call_count = 0

            def mock_get_row_headers(_obj):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return [mock_header1]
                if call_count == 2:
                    return [mock_header2]
                return []

            test_context.patch_object(AXTable, "get_dynamic_row_header", return_value=None)
            test_context.patch_object(AXTable, "_get_row_headers", side_effect=mock_get_row_headers)
            result = AXTable.get_row_headers(mock_cell)
            assert result == [mock_header2, mock_header1]

    def test_get_row_headers_via_table_interface(self, test_context: OrcaTestContext) -> None:
        """Test AXTable._get_row_headers via table interface."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_headers = [test_context.Mock(spec=Atspi.Accessible)]
        self._setup_row_headers_mocks(
            test_context, mock_table, coordinates=(2, 3), spans=(2, 1), headers=mock_headers
        )
        result = AXTable._get_row_headers(mock_cell)
        assert result == mock_headers + mock_headers

    def test_get_row_headers_via_table_interface_invalid_coords(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_row_headers via table interface with invalid coordinates."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table_cell", return_value=False)
        test_context.patch_object(
            AXTable, "_get_cell_coordinates_from_table", return_value=(-1, -1)
        )
        result = AXTable._get_row_headers(mock_cell)
        assert result == []

    def test_get_row_headers_via_table_interface_no_table(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_row_headers via table interface with no table."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table_cell", return_value=False)
        test_context.patch_object(
            AXTable, "_get_cell_coordinates_from_table", return_value=(2, 3)
        )
        test_context.patch_object(AXTable, "get_table", return_value=None)
        result = AXTable._get_row_headers(mock_cell)
        assert result == []

    def test_has_row_headers_with_table_support(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.has_row_headers with table support."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_headers = [test_context.Mock(spec=Atspi.Accessible)]
        test_context.patch_object(AXObject, "supports_table", return_value=True)
        test_context.patch_object(AXTable, "get_row_count", return_value=5)
        test_context.patch_object(
            AXTable,
            "_get_row_headers_from_table",
            side_effect=lambda table, row: mock_headers if row == 2 else [],
        )
        result = AXTable.has_row_headers(mock_table, 3)
        assert result is True

    def test_has_row_headers_without_table_support(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.has_row_headers without table support."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table", return_value=False)
        result = AXTable.has_row_headers(mock_table)
        assert result is False

    def test_has_row_headers_no_headers_found(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.has_row_headers with no headers found."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table", return_value=True)
        test_context.patch_object(AXTable, "get_row_count", return_value=5)
        test_context.patch_object(
            AXTable, "_get_row_headers_from_table", side_effect=lambda table, row: []
        )
        result = AXTable.has_row_headers(mock_table, 3)
        assert result is False

    def test_get_column_headers_not_table_cell(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_column_headers with cell that is not a table cell."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_utilities_role import AXUtilitiesRole

        test_context.patch_object(AXUtilitiesRole, "is_table_cell", return_value=False)
        result = AXTable.get_column_headers(mock_cell)
        assert result == []

    @pytest.mark.parametrize(
        "header_scenario",
        [
            pytest.param("dynamic_header", id="with_dynamic_header"),
            pytest.param("multiple_headers", id="with_multiple_headers"),
            pytest.param("nested_headers", id="with_nested_headers"),
        ],
    )
    def test_get_column_headers_scenarios(
        self,
        test_context: OrcaTestContext,
        header_scenario: str,
    ) -> None:
        """Test AXTable.get_column_headers with different header scenarios."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_utilities_role import AXUtilitiesRole

        test_context.patch_object(AXUtilitiesRole, "is_table_cell", return_value=True)

        if header_scenario == "dynamic_header":
            mock_header = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(
                AXTable, "get_dynamic_column_header", return_value=mock_header
            )
            result = AXTable.get_column_headers(mock_cell)
            assert result == [mock_header]
        elif header_scenario == "multiple_headers":
            mock_headers = [
                test_context.Mock(spec=Atspi.Accessible),
                test_context.Mock(spec=Atspi.Accessible),
            ]
            test_context.patch_object(
                AXTable, "get_dynamic_column_header", return_value=None
            )
            test_context.patch_object(
                AXTable, "_get_column_headers", return_value=mock_headers
            )
            result = AXTable.get_column_headers(mock_cell)
            assert result == mock_headers
        else:  # nested_headers
            mock_header1 = test_context.Mock(spec=Atspi.Accessible)
            mock_header2 = test_context.Mock(spec=Atspi.Accessible)
            call_count = 0

            def mock_get_column_headers(_obj):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return [mock_header1]
                if call_count == 2:
                    return [mock_header2]
                return []

            test_context.patch_object(
                AXTable, "get_dynamic_column_header", return_value=None
            )
            test_context.patch_object(
                AXTable, "_get_column_headers", side_effect=mock_get_column_headers
            )
            result = AXTable.get_column_headers(mock_cell)
            assert result == [mock_header2, mock_header1]

    def test_get_column_headers_via_table_interface(self, test_context: OrcaTestContext) -> None:
        """Test AXTable._get_column_headers via table interface."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_headers = [test_context.Mock(spec=Atspi.Accessible)]
        test_context.patch_object(AXObject, "supports_table_cell", return_value=False)
        test_context.patch_object(
            AXTable, "_get_cell_coordinates_from_table", return_value=(2, 3)
        )
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(AXTable, "_get_cell_spans_from_table", return_value=(1, 2))
        test_context.patch_object(
            AXTable, "_get_column_headers_from_table", side_effect=lambda table, col: mock_headers
        )
        result = AXTable._get_column_headers(mock_cell)
        assert result == mock_headers + mock_headers

    def test_get_column_headers_via_table_interface_invalid_coords(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_column_headers via table interface with invalid coordinates."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table_cell", return_value=False)
        test_context.patch_object(
            AXTable, "_get_cell_coordinates_from_table", return_value=(-1, -1)
        )
        result = AXTable._get_column_headers(mock_cell)
        assert result == []

    def test_get_column_headers_via_table_interface_no_table(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_column_headers via table interface with no table."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table_cell", return_value=False)
        test_context.patch_object(
            AXTable, "_get_cell_coordinates_from_table", return_value=(2, 3)
        )
        test_context.patch_object(AXTable, "get_table", return_value=None)
        result = AXTable._get_column_headers(mock_cell)
        assert result == []

    def test_has_column_headers_with_table_support(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.has_column_headers with table support."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_headers = [test_context.Mock(spec=Atspi.Accessible)]
        test_context.patch_object(AXObject, "supports_table", return_value=True)
        test_context.patch_object(AXTable, "get_column_count", return_value=5)
        test_context.patch_object(
            AXTable,
            "_get_column_headers_from_table",
            side_effect=lambda table, col: mock_headers if col == 1 else [],
        )
        result = AXTable.has_column_headers(mock_table, 3)
        assert result is True

    def test_has_column_headers_without_table_support(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.has_column_headers without table support."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table", return_value=False)
        result = AXTable.has_column_headers(mock_table)
        assert result is False

    def test_has_column_headers_no_headers_found(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.has_column_headers with no headers found."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table", return_value=True)
        test_context.patch_object(AXTable, "get_column_count", return_value=5)
        test_context.patch_object(
            AXTable, "_get_column_headers_from_table", side_effect=lambda table, col: []
        )
        result = AXTable.has_column_headers(mock_table, 3)
        assert result is False

    def test_get_cell_coordinates_with_find_cell(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_cell_coordinates with find_cell=True."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesRole, "is_table_cell_or_header", side_effect=lambda obj: obj == mock_ancestor
        )
        test_context.patch_object(AXObject, "find_ancestor", return_value=mock_ancestor)
        test_context.patch_object(AXObject, "supports_table_cell", return_value=True)
        test_context.patch_object(
            AXTable, "_get_cell_coordinates_from_table_cell", return_value=(2, 3)
        )
        test_context.patch_object(
            AXTable, "_get_cell_coordinates_from_attribute", return_value=(None, None)
        )
        result = AXTable.get_cell_coordinates(mock_cell, find_cell=True)
        assert result == (2, 3)

    def test_get_cell_coordinates_not_table_cell_or_header(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable.get_cell_coordinates with object that is not a table cell or header."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_utilities_role import AXUtilitiesRole

        test_context.patch_object(
            AXUtilitiesRole, "is_table_cell_or_header", return_value=False
        )
        result = AXTable.get_cell_coordinates(mock_cell)
        assert result == (-1, -1)

    @pytest.mark.parametrize(
        "scenario, expected_result",
        [
            pytest.param("negative_index", (-1, -1), id="with_negative_index"),
            pytest.param("glib_error", (-1, -1), id="with_glib_error"),
        ],
    )
    def test_get_cell_coordinates_from_table_error_scenarios(
        self, test_context: OrcaTestContext, scenario: str, expected_result: tuple[int, int]
    ) -> None:
        """Test AXTable._get_cell_coordinates_from_table error handling scenarios."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)

        if scenario == "negative_index":
            self._setup_dependencies(test_context)
            from orca.ax_table import AXTable

            test_context.patch_object(AXTable, "_get_cell_index", return_value=-1)
            result = AXTable._get_cell_coordinates_from_table(mock_cell)
            assert result == expected_result
        else:  # glib_error
            mock_table = test_context.Mock(spec=Atspi.Accessible)
            essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
            from orca.ax_table import AXTable
            from orca import debug

            def raise_glib_error(obj, index):
                raise GLib.GError("Test error")

            test_context.patch_object(AXTable, "_get_cell_index", return_value=5)
            test_context.patch_object(AXTable, "get_table", return_value=mock_table)
            test_context.patch_object(Atspi.Table, "get_row_at_index", side_effect=raise_glib_error)
            test_context.patch_object(
                debug, "print_message", new=essential_modules["orca.debug"].print_message
            )
            result = AXTable._get_cell_coordinates_from_table(mock_cell)
            assert result == expected_result
            essential_modules["orca.debug"].print_message.assert_called()

    def test_get_cell_coordinates_from_table_no_table(self, test_context: OrcaTestContext) -> None:
        """Test AXTable._get_cell_coordinates_from_table with no table found."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        test_context.patch_object(AXTable, "_get_cell_index", return_value=5)
        test_context.patch_object(AXTable, "get_table", return_value=None)
        result = AXTable._get_cell_coordinates_from_table(mock_cell)
        assert result == (-1, -1)
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_get_cell_coordinates_from_table_cell_without_support(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_cell_coordinates_from_table_cell without table cell support."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table_cell", return_value=False)
        result = AXTable._get_cell_coordinates_from_table_cell(mock_cell)
        assert result == (-1, -1)

    def test_get_cell_coordinates_from_table_cell_with_glib_error(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_cell_coordinates_from_table_cell handles GLib.GError."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        test_context.patch_object(AXObject, "supports_table_cell", return_value=True)
        test_context.patch_object(Atspi.TableCell, "get_position", side_effect=raise_glib_error)
        test_context.patch_object(
            debug, "print_message", new=essential_modules["orca.debug"].print_message
        )
        result = AXTable._get_cell_coordinates_from_table_cell(mock_cell)
        assert result == (-1, -1)
        essential_modules["orca.debug"].print_message.assert_called()

    def test_get_cell_coordinates_from_table_cell_failed_result(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_cell_coordinates_from_table_cell with failed result."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        test_context.patch_object(AXObject, "supports_table_cell", return_value=True)
        test_context.patch_object(Atspi.TableCell, "get_position", return_value=(False, 2, 3))
        result = AXTable._get_cell_coordinates_from_table_cell(mock_cell)
        assert result == (-1, -1)

    def test_get_cell_coordinates_from_attribute_with_none_cell(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_cell_coordinates_from_attribute with None cell."""

        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        result = AXTable._get_cell_coordinates_from_attribute(None)
        assert result == (None, None)

    def test_get_cell_coordinates_from_attribute_from_row_ancestor(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable._get_cell_coordinates_from_attribute from row ancestor."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_row = test_context.Mock(spec=Atspi.Accessible)

        def get_attrs(obj):
            if obj == mock_cell:
                return {"rowindex": "2"}
            return {"rowindex": "2", "colindex": "5"}

        test_context.patch_object(AXObject, "get_attributes_dict", side_effect=get_attrs)
        test_context.patch_object(
            AXUtilitiesRole, "is_table_row", side_effect=lambda obj: obj == mock_row
        )
        test_context.patch_object(AXObject, "find_ancestor", return_value=mock_row)
        result = AXTable._get_cell_coordinates_from_attribute(mock_cell)
        assert result == ("2", "5")
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_get_presentable_sort_order_from_header_not_header(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable.get_presentable_sort_order_from_header with non-header object."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_utilities_role import AXUtilitiesRole

        test_context.patch_object(AXUtilitiesRole, "is_table_header", return_value=False)
        result = AXTable.get_presentable_sort_order_from_header(mock_cell)
        assert result == ""

    @pytest.mark.parametrize(
        "sort_order, include_name, expected_prefix",
        [
            pytest.param("ascending", False, "", id="ascending_no_name"),
            pytest.param("descending", True, "Header Name. ", id="descending_with_name"),
            pytest.param("other", False, "", id="other_sort"),
            pytest.param("none", False, "", id="none_sort"),
            pytest.param("", False, "", id="empty_sort"),
        ],
    )
    def test_get_presentable_sort_order_from_header(
        self,
        test_context,
        sort_order,
        include_name,
        expected_prefix,
    ) -> None:
        """Test AXTable.get_presentable_sort_order_from_header."""

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import object_properties

        test_context.patch_object(AXUtilitiesRole, "is_table_header", return_value=True)
        test_context.patch_object(
            AXObject, "get_attribute", side_effect=lambda obj, attr, default: sort_order
        )
        test_context.patch_object(
            AXObject, "get_name", side_effect=lambda obj: "Header Name" if include_name else ""
        )
        test_context.patch_object(
            object_properties, "SORT_ORDER_ASCENDING", new="ascending sort"
        )
        test_context.patch_object(
            object_properties, "SORT_ORDER_DESCENDING", new="descending sort"
        )
        test_context.patch_object(object_properties, "SORT_ORDER_OTHER", new="other sort")
        result = AXTable.get_presentable_sort_order_from_header(mock_cell, include_name)
        if sort_order == "ascending":
            assert result == expected_prefix + "ascending sort"
        elif sort_order == "descending":
            assert result == expected_prefix + "descending sort"
        elif sort_order == "other":
            assert result == expected_prefix + "other sort"
        else:
            assert result == ""

    def test_get_dynamic_row_header_no_headers_column(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_dynamic_row_header with no headers column set."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        result = AXTable.get_dynamic_row_header(mock_cell)
        assert result is None

    def test_get_dynamic_row_header_same_column(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_dynamic_row_header with cell in same column as headers."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        AXTable.DYNAMIC_ROW_HEADERS_COLUMN[hash(mock_table)] = 2
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(AXTable, "get_cell_coordinates", return_value=(1, 2))
        result = AXTable.get_dynamic_row_header(mock_cell)
        assert result is None

    def test_get_dynamic_row_header_different_column(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_dynamic_row_header with cell in different column."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_header_cell = test_context.Mock(spec=Atspi.Accessible)
        AXTable.DYNAMIC_ROW_HEADERS_COLUMN[hash(mock_table)] = 0
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(AXTable, "get_cell_coordinates", return_value=(1, 2))
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_header_cell
        )
        result = AXTable.get_dynamic_row_header(mock_cell)
        assert result == mock_header_cell

    def test_get_dynamic_column_header_no_headers_row(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_dynamic_column_header with no headers row set."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        result = AXTable.get_dynamic_column_header(mock_cell)
        assert result is None

    def test_get_dynamic_column_header_same_row(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_dynamic_column_header with cell in same row as headers."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        AXTable.DYNAMIC_COLUMN_HEADERS_ROW[hash(mock_table)] = 0
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(AXTable, "get_cell_coordinates", return_value=(0, 2))
        result = AXTable.get_dynamic_column_header(mock_cell)
        assert result is None

    def test_get_dynamic_column_header_different_row(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.get_dynamic_column_header with cell in different row."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_header_cell = test_context.Mock(spec=Atspi.Accessible)
        AXTable.DYNAMIC_COLUMN_HEADERS_ROW[hash(mock_table)] = 0
        test_context.patch_object(AXTable, "get_table", return_value=mock_table)
        test_context.patch_object(AXTable, "get_cell_coordinates", return_value=(1, 2))
        test_context.patch_object(
            AXTable, "get_cell_at", side_effect=lambda table, row, col: mock_header_cell
        )
        result = AXTable.get_dynamic_column_header(mock_cell)
        assert result == mock_header_cell

    def test_set_dynamic_row_headers_column(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.set_dynamic_row_headers_column."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        AXTable.set_dynamic_row_headers_column(mock_table, 3)
        assert AXTable.DYNAMIC_ROW_HEADERS_COLUMN[hash(mock_table)] == 3

    def test_set_dynamic_column_headers_row(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.set_dynamic_column_headers_row."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        AXTable.set_dynamic_column_headers_row(mock_table, 1)
        assert AXTable.DYNAMIC_COLUMN_HEADERS_ROW[hash(mock_table)] == 1

    def test_clear_dynamic_row_headers_column_exists(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.clear_dynamic_row_headers_column when entry exists."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        AXTable.DYNAMIC_ROW_HEADERS_COLUMN[hash(mock_table)] = 2
        AXTable.clear_dynamic_row_headers_column(mock_table)
        assert hash(mock_table) not in AXTable.DYNAMIC_ROW_HEADERS_COLUMN

    def test_clear_dynamic_row_headers_column_not_exists(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable.clear_dynamic_row_headers_column when entry does not exist."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        AXTable.clear_dynamic_row_headers_column(mock_table)

    def test_clear_dynamic_column_headers_row_exists(self, test_context: OrcaTestContext) -> None:
        """Test AXTable.clear_dynamic_column_headers_row when entry exists."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        AXTable.DYNAMIC_COLUMN_HEADERS_ROW[hash(mock_table)] = 1
        AXTable.clear_dynamic_column_headers_row(mock_table)
        assert hash(mock_table) not in AXTable.DYNAMIC_COLUMN_HEADERS_ROW

    def test_clear_dynamic_column_headers_row_not_exists(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test AXTable.clear_dynamic_column_headers_row when entry does not exist."""

        mock_table = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_table import AXTable

        AXTable.clear_dynamic_column_headers_row(mock_table)
