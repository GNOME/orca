# Unit tests for ax_table.py table-related methods.
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
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=import-outside-toplevel
# pylint: disable=unused-argument
# pylint: disable=too-many-lines

"""Unit tests for ax_table.py table-related methods."""

from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache  # pylint: disable=import-error

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib



@pytest.mark.unit
class TestAXTable:
    """Test table-related methods."""

    @pytest.fixture
    def mock_table(self):
        """Create a mock Atspi.Accessible table object."""
        return Mock(spec=Atspi.Accessible)

    @pytest.fixture
    def mock_cell(self):
        """Create a mock Atspi.Accessible cell object."""
        return Mock(spec=Atspi.Accessible)

    def test_get_caption_with_table_support(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.get_caption with table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_caption = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_caption", lambda obj: mock_caption)

        result = AXTable.get_caption(mock_table)
        assert result == mock_caption
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_caption_without_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_caption without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.get_caption(mock_table)
        assert result is None

    def test_get_caption_with_glib_error(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.get_caption handles GLib.GError."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_caption", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXTable.get_caption(mock_table)
        assert result is None
        mock_orca_dependencies["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "prefer_attribute, attribute_count, physical_count, expected_result",
        [
            pytest.param(True, 5, 4, 5, id="prefer_attribute_available"),
            pytest.param(True, None, 4, 4, id="prefer_attribute_none_fallback"),
            pytest.param(False, 5, 4, 4, id="prefer_physical"),
        ],
    )
    def test_get_column_count(
        self,
        monkeypatch,
        mock_table,
        prefer_attribute,
        attribute_count,
        physical_count,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXTable.get_column_count."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(
            AXTable, "_get_column_count_from_attribute", lambda obj: attribute_count
        )
        monkeypatch.setattr(Atspi.Table, "get_n_columns", lambda obj: physical_count)

        result = AXTable.get_column_count(mock_table, prefer_attribute)
        assert result == expected_result
        if attribute_count is None or not prefer_attribute:
            mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_column_count_without_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_column_count without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.get_column_count(mock_table)
        assert result == -1

    def test_get_column_count_with_glib_error(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_column_count handles GLib.GError."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(AXTable, "_get_column_count_from_attribute", lambda obj: None)
        monkeypatch.setattr(Atspi.Table, "get_n_columns", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXTable.get_column_count(mock_table)
        assert result == -1
        mock_orca_dependencies["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "colcount_attr, expected_result",
        [
            pytest.param("3", 3, id="valid_colcount"),
            pytest.param(None, None, id="no_colcount"),
        ],
    )
    def test_get_column_count_from_attribute(
        self, monkeypatch, mock_table, colcount_attr, expected_result, mock_orca_dependencies
    ):
        """Test AXTable._get_column_count_from_attribute."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        attrs = {"colcount": colcount_attr} if colcount_attr else {}
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: attrs)

        result = AXTable._get_column_count_from_attribute(mock_table)
        assert result == expected_result
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "prefer_attribute, attribute_count, physical_count, expected_result",
        [
            pytest.param(True, 10, 8, 10, id="prefer_attribute_available"),
            pytest.param(True, None, 8, 8, id="prefer_attribute_none_fallback"),
            pytest.param(False, 10, 8, 8, id="prefer_physical"),
        ],
    )
    def test_get_row_count(
        self,
        monkeypatch,
        mock_table,
        prefer_attribute,
        attribute_count,
        physical_count,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXTable.get_row_count."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(AXTable, "_get_row_count_from_attribute", lambda obj: attribute_count)
        monkeypatch.setattr(Atspi.Table, "get_n_rows", lambda obj: physical_count)

        result = AXTable.get_row_count(mock_table, prefer_attribute)
        assert result == expected_result
        if attribute_count is None or not prefer_attribute:
            mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_row_count_without_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_row_count without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.get_row_count(mock_table)
        assert result == -1

    def test_get_row_count_with_glib_error(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.get_row_count handles GLib.GError."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(AXTable, "_get_row_count_from_attribute", lambda obj: None)
        monkeypatch.setattr(Atspi.Table, "get_n_rows", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXTable.get_row_count(mock_table)
        assert result == -1
        mock_orca_dependencies["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "rowcount_attr, expected_result",
        [
            pytest.param("7", 7, id="valid_rowcount"),
            pytest.param(None, None, id="no_rowcount"),
        ],
    )
    def test_get_row_count_from_attribute(
        self, monkeypatch, mock_table, rowcount_attr, expected_result, mock_orca_dependencies
    ):
        """Test AXTable._get_row_count_from_attribute."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        attrs = {"rowcount": rowcount_attr} if rowcount_attr else {}
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: attrs)

        result = AXTable._get_row_count_from_attribute(mock_table)
        assert result == expected_result
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "row_extents, col_extents, expected_result",
        [
            pytest.param([1, 1, 1, 1], [1, 1, 1, 1], False, id="uniform_table"),
            pytest.param([2, 1, 1, 1], [1, 1, 1, 1], True, id="row_span_greater_than_one"),
            pytest.param([1, 1, 1, 1], [1, 2, 1, 1], True, id="col_span_greater_than_one"),
        ],
    )
    def test_is_non_uniform_table(
        self,
        monkeypatch,
        mock_table,
        row_extents,
        col_extents,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXTable.is_non_uniform_table."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        call_count = 0
        def mock_get_extent(extent_type):
            nonlocal call_count
            if extent_type == "row":
                result = row_extents[call_count % len(row_extents)]
            else:
                result = col_extents[call_count % len(col_extents)]
            call_count += 1
            return result

        monkeypatch.setattr(AXTable, "get_row_count", lambda obj, prefer_attr: 2)
        monkeypatch.setattr(AXTable, "get_column_count", lambda obj, prefer_attr: 2)
        monkeypatch.setattr(
            Atspi.Table, "get_row_extent_at",
            lambda table, row, col: mock_get_extent("row")
        )
        monkeypatch.setattr(
            Atspi.Table, "get_column_extent_at",
            lambda table, row, col: mock_get_extent("col")
        )

        result = AXTable.is_non_uniform_table(mock_table)
        assert result == expected_result

    def test_is_non_uniform_table_with_glib_error(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.is_non_uniform_table handles GLib.GError."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca import debug

        def raise_glib_error(obj, row, col):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXTable, "get_row_count", lambda obj, prefer_attr: 1)
        monkeypatch.setattr(AXTable, "get_column_count", lambda obj, prefer_attr: 1)
        monkeypatch.setattr(Atspi.Table, "get_row_extent_at", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXTable.is_non_uniform_table(mock_table)
        assert result is False
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_selected_column_count_with_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_column_count with table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_n_selected_columns", lambda obj: 2)

        result = AXTable.get_selected_column_count(mock_table)
        assert result == 2
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_selected_column_count_without_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_column_count without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.get_selected_column_count(mock_table)
        assert result == 0

    def test_get_selected_column_count_with_glib_error(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_column_count handles GLib.GError."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_n_selected_columns", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXTable.get_selected_column_count(mock_table)
        assert result == 0
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_selected_columns_with_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_columns with table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        selected_columns = [0, 2, 4]

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_selected_columns", lambda obj: selected_columns)

        result = AXTable.get_selected_columns(mock_table)
        assert result == selected_columns
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_selected_columns_without_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_columns without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.get_selected_columns(mock_table)
        assert result == []

    def test_get_selected_columns_with_glib_error(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_columns handles GLib.GError."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_selected_columns", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXTable.get_selected_columns(mock_table)
        assert result == []
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_selected_row_count_with_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_row_count with table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_n_selected_rows", lambda obj: 3)

        result = AXTable.get_selected_row_count(mock_table)
        assert result == 3
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_selected_row_count_without_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_row_count without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.get_selected_row_count(mock_table)
        assert result == 0

    def test_get_selected_row_count_with_glib_error(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_row_count handles GLib.GError."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_n_selected_rows", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXTable.get_selected_row_count(mock_table)
        assert result == 0
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_selected_rows_with_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_rows with table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        selected_rows = [1, 3, 5]

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_selected_rows", lambda obj: selected_rows)

        result = AXTable.get_selected_rows(mock_table)
        assert result == selected_rows
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_selected_rows_without_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_rows without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.get_selected_rows(mock_table)
        assert result == []

    def test_get_selected_rows_with_glib_error(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_selected_rows handles GLib.GError."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_selected_rows", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXTable.get_selected_rows(mock_table)
        assert result == []
        mock_orca_dependencies["debug"].print_message.assert_called()

    @pytest.mark.parametrize(
        "row_count, selected_row_count, col_count, selected_col_count, expected_result",
        [
            pytest.param(5, 5, 3, 3, True, id="all_rows_selected"),
            pytest.param(5, 3, 3, 3, True, id="all_columns_selected"),
            pytest.param(5, 3, 3, 2, False, id="partial_selection"),
            pytest.param(0, 0, 0, 0, False, id="empty_table"),
        ],
    )
    def test_all_cells_are_selected(
        self, monkeypatch, mock_table, row_count, selected_row_count, col_count,
        selected_col_count, expected_result, mock_orca_dependencies
    ):
        """Test AXTable.all_cells_are_selected."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(AXTable, "get_row_count", lambda obj, prefer_attribute: row_count)
        monkeypatch.setattr(AXTable, "get_selected_row_count", lambda obj: selected_row_count)
        monkeypatch.setattr(AXTable, "get_column_count", lambda obj, prefer_attribute: col_count)
        monkeypatch.setattr(AXTable, "get_selected_column_count", lambda obj: selected_col_count)

        result = AXTable.all_cells_are_selected(mock_table)
        assert result == expected_result

    def test_all_cells_are_selected_without_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.all_cells_are_selected without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.all_cells_are_selected(mock_table)
        assert result is False

    def test_get_cell_at_with_table_support(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.get_cell_at with table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_accessible_at", lambda obj, row, col: mock_cell)

        result = AXTable.get_cell_at(mock_table, 1, 2)
        assert result == mock_cell
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_cell_at_without_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_cell_at without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.get_cell_at(mock_table, 1, 2)
        assert result is None

    def test_get_cell_at_with_glib_error(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.get_cell_at handles GLib.GError."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        def raise_glib_error(obj, row, col):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(Atspi.Table, "get_accessible_at", raise_glib_error)

        result = AXTable.get_cell_at(mock_table, 1, 2)
        assert result is None
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "cell_index_attr, parent_role, expected_index",
        [
            pytest.param("5", Atspi.Role.BUTTON, 5, id="cell_has_index_attribute"),
            pytest.param("", Atspi.Role.TABLE_CELL, 3, id="parent_is_table_cell"),
            pytest.param(None, Atspi.Role.BUTTON, 2, id="use_index_in_parent"),
        ],
    )
    def test_get_cell_index(
        self,
        monkeypatch,
        mock_cell,
        cell_index_attr,
        parent_role,
        expected_index,
        mock_orca_dependencies
    ):
        """Test AXTable._get_cell_index."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, attr: cell_index_attr)
        monkeypatch.setattr(AXObject, "get_parent", lambda obj: mock_parent)
        monkeypatch.setattr(AXObject, "get_role", lambda obj: parent_role)
        monkeypatch.setattr(AXObject, "get_index_in_parent", lambda obj: expected_index)

        result = AXTable._get_cell_index(mock_cell)
        if parent_role == Atspi.Role.TABLE_CELL:
            assert result == 3
        else:
            assert result == expected_index

    @pytest.mark.parametrize(
        "supports_table_cell, cell_role, prefer_attribute, rowspan_attr, "
        "colspan_attr, expected_spans",
        [
            pytest.param(
                True, Atspi.Role.TABLE_CELL, True, "2", "3", (2, 3),
                id="table_cell_with_attributes"
            ),
            pytest.param(
                False, Atspi.Role.TABLE_CELL, True, "2", "3", (2, 3),
                id="table_interface_with_attributes"
            ),
            pytest.param(
                True, Atspi.Role.TABLE_CELL, False, "2", "3", (2, 1),
                id="table_cell_no_attributes"
            ),
            pytest.param(
                True, Atspi.Role.TABLE_CELL, True, None, None, (2, 1),
                id="table_cell_no_attr_values"
            ),
            pytest.param(
                False, Atspi.Role.BUTTON, True, "2", "3", (-1, -1), id="not_table_cell"
            ),
        ],
    )
    def test_get_cell_spans(
        self, monkeypatch, mock_cell, supports_table_cell, cell_role,
        prefer_attribute, rowspan_attr, colspan_attr, expected_spans, mock_orca_dependencies
    ):
        """Test AXTable.get_cell_spans."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject

        monkeypatch.setattr(
            AXUtilitiesRole, "is_table_cell_or_header",
            lambda obj: cell_role == Atspi.Role.TABLE_CELL
        )
        monkeypatch.setattr(AXObject, "supports_table_cell", lambda obj: supports_table_cell)
        monkeypatch.setattr(AXTable, "_get_cell_spans_from_table_cell", lambda obj: (2, 1))
        monkeypatch.setattr(AXTable, "_get_cell_spans_from_table", lambda obj: (1, 2))
        monkeypatch.setattr(
            AXTable, "_get_cell_spans_from_attribute",
            lambda obj: (rowspan_attr, colspan_attr)
        )

        result = AXTable.get_cell_spans(mock_cell, prefer_attribute)
        assert result == expected_spans

    @pytest.mark.parametrize(
        "rowspan_attr, colspan_attr, expected_spans",
        [
            pytest.param("2", "3", ("2", "3"), id="both_attributes_present"),
            pytest.param(None, "3", (None, "3"), id="only_colspan"),
            pytest.param("2", None, ("2", None), id="only_rowspan"),
            pytest.param(None, None, (None, None), id="no_attributes"),
        ],
    )
    def test_get_cell_spans_from_attribute(
        self,
        monkeypatch,
        mock_cell,
        rowspan_attr,
        colspan_attr,
        expected_spans,
        mock_orca_dependencies
    ):
        """Test AXTable._get_cell_spans_from_attribute."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        attrs = {}
        if rowspan_attr:
            attrs["rowspan"] = rowspan_attr
        if colspan_attr:
            attrs["colspan"] = colspan_attr

        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: attrs)

        result = AXTable._get_cell_spans_from_attribute(mock_cell)
        assert result == expected_spans
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_cell_spans_from_table_cell_with_support(
        self, monkeypatch, mock_cell, mock_orca_dependencies
    ):
        """Test AXTable._get_cell_spans_from_table_cell with table cell support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table_cell", lambda obj: True)
        monkeypatch.setattr(Atspi.TableCell, "get_row_span", lambda obj: 2)
        monkeypatch.setattr(Atspi.TableCell, "get_column_span", lambda obj: 3)

        result = AXTable._get_cell_spans_from_table_cell(mock_cell)
        assert result == (2, 3)
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_cell_spans_from_table_cell_without_support(
        self, monkeypatch, mock_cell, mock_orca_dependencies
    ):
        """Test AXTable._get_cell_spans_from_table_cell without table cell support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table_cell", lambda obj: False)

        result = AXTable._get_cell_spans_from_table_cell(mock_cell)
        assert result == (-1, -1)

    def test_get_cell_spans_from_table_cell_with_glib_error(
        self, monkeypatch, mock_cell, mock_orca_dependencies
    ):
        """Test AXTable._get_cell_spans_from_table_cell handles GLib.GError."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_table_cell", lambda obj: True)
        monkeypatch.setattr(Atspi.TableCell, "get_row_span", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)

        result = AXTable._get_cell_spans_from_table_cell(mock_cell)
        assert result == (-1, -1)
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_table_from_table_cell(self, monkeypatch, mock_cell, mock_orca_dependencies):
        """Test AXTable.get_table with table cell object."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        mock_table = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "supports_table_cell", lambda obj: True)
        monkeypatch.setattr(Atspi.TableCell, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)

        result = AXTable.get_table(mock_cell)
        assert result == mock_table

    def test_get_table_from_table_cell_with_glib_error(
        self, monkeypatch, mock_cell, mock_orca_dependencies
    ):
        """Test AXTable.get_table handles GLib.GError in table cell interface."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        mock_table = Mock(spec=Atspi.Accessible)

        def is_table(obj):
            return obj == mock_table

        monkeypatch.setattr(AXObject, "supports_table_cell", lambda obj: True)
        monkeypatch.setattr(Atspi.TableCell, "get_table", raise_glib_error)
        monkeypatch.setattr(debug, "print_message", mock_orca_dependencies["debug"].print_message)
        monkeypatch.setattr(AXUtilitiesRole, "is_table", is_table)
        monkeypatch.setattr(AXUtilitiesRole, "is_tree_table", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_tree", lambda obj: False)
        monkeypatch.setattr(AXObject, "supports_table", is_table)
        monkeypatch.setattr(AXObject, "find_ancestor", lambda obj, func: mock_table)

        result = AXTable.get_table(mock_cell)
        assert result == mock_table
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_table_with_table_object(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.get_table with table object."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        monkeypatch.setattr(AXObject, "supports_table_cell", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_table", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_tree_table", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_tree", lambda obj: False)
        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)

        result = AXTable.get_table(mock_table)
        assert result == mock_table

    def test_get_table_with_none_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXTable.get_table with None object."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        result = AXTable.get_table(None)
        assert result is None

    def test_is_layout_table_with_layout_guess(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.is_layout_table with layout-guess attribute."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        attrs = {"layout-guess": "true"}

        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: attrs)
        monkeypatch.setattr(AXUtilitiesRole, "is_table", lambda obj: True)

        result = AXTable.is_layout_table(mock_table)
        assert result is True
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_is_layout_table_without_table_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.is_layout_table without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        attrs = {}

        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: attrs)
        monkeypatch.setattr(AXUtilitiesRole, "is_table", lambda obj: True)
        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.is_layout_table(mock_table)
        assert result is True
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_is_layout_table_with_headers(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.is_layout_table with headers present."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        attrs = {}

        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: attrs)
        monkeypatch.setattr(AXUtilitiesRole, "is_table", lambda obj: True)
        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(AXTable, "has_column_headers", lambda obj: True)
        monkeypatch.setattr(AXTable, "has_row_headers", lambda obj: False)

        result = AXTable.is_layout_table(mock_table)
        assert result is False
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_is_layout_table_with_name(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.is_layout_table with table name present."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        attrs = {}

        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: attrs)
        monkeypatch.setattr(AXUtilitiesRole, "is_table", lambda obj: True)
        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(AXTable, "has_column_headers", lambda obj: False)
        monkeypatch.setattr(AXTable, "has_row_headers", lambda obj: False)
        monkeypatch.setattr(AXObject, "get_name", lambda obj: "Table Name")
        monkeypatch.setattr(AXObject, "get_description", lambda obj: "")

        result = AXTable.is_layout_table(mock_table)
        assert result is False
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_is_layout_table_with_caption(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.is_layout_table with table caption present."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        attrs = {}
        mock_caption = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: attrs)
        monkeypatch.setattr(AXUtilitiesRole, "is_table", lambda obj: True)
        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(AXTable, "has_column_headers", lambda obj: False)
        monkeypatch.setattr(AXTable, "has_row_headers", lambda obj: False)
        monkeypatch.setattr(AXObject, "get_name", lambda obj: "")
        monkeypatch.setattr(AXObject, "get_description", lambda obj: "")
        monkeypatch.setattr(AXTable, "get_caption", lambda obj: mock_caption)

        result = AXTable.is_layout_table(mock_table)
        assert result is False
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_first_cell(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.get_first_cell."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXTable, "get_cell_at", lambda table, row, col: mock_cell)

        result = AXTable.get_first_cell(mock_table)
        assert result == mock_cell

    def test_get_last_cell(self, monkeypatch, mock_table, mock_orca_dependencies):
        """Test AXTable.get_last_cell."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXTable, "get_row_count", lambda table: 3)
        monkeypatch.setattr(AXTable, "get_column_count", lambda table: 4)
        monkeypatch.setattr(AXTable, "get_cell_at", lambda table, row, col: mock_cell)

        result = AXTable.get_last_cell(mock_table)
        assert result == mock_cell

    @pytest.mark.parametrize(
        "cell_row, cell_col, expected_row, expected_col",
        [
            pytest.param(2, 3, 1, 3, id="move_up_one_row"),
            pytest.param(0, 3, -1, 3, id="top_row"),
        ],
    )
    def test_get_cell_above(
        self,
        monkeypatch,
        mock_cell,
        cell_row,
        cell_col,
        expected_row,
        expected_col,
        mock_orca_dependencies
    ):
        """Test AXTable.get_cell_above."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible)
        mock_result_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            AXTable, "get_cell_coordinates",
            lambda obj, prefer_attribute: (cell_row, cell_col)
        )
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(AXTable, "get_cell_at", lambda table, row, col: mock_result_cell)

        result = AXTable.get_cell_above(mock_cell)
        assert result == mock_result_cell

    @pytest.mark.parametrize(
        "cell_row, cell_col, row_span, expected_row, expected_col",
        [
            pytest.param(2, 3, 1, 3, 3, id="single_row_span"),
            pytest.param(2, 3, 2, 4, 3, id="multi_row_span"),
        ],
    )
    def test_get_cell_below(
        self,
        monkeypatch,
        mock_cell,
        cell_row,
        cell_col,
        row_span,
        expected_row,
        expected_col,
        mock_orca_dependencies
    ):
        """Test AXTable.get_cell_below."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible)
        mock_result_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            AXTable, "get_cell_coordinates",
            lambda obj, prefer_attribute: (cell_row, cell_col)
        )
        monkeypatch.setattr(AXTable, "get_cell_spans", lambda obj, prefer_attribute: (row_span, 1))
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(AXTable, "get_cell_at", lambda table, row, col: mock_result_cell)

        result = AXTable.get_cell_below(mock_cell)
        assert result == mock_result_cell

    @pytest.mark.parametrize(
        "cell_row, cell_col, expected_row, expected_col",
        [
            pytest.param(2, 3, 2, 2, id="move_left_one_column"),
            pytest.param(2, 0, 2, -1, id="leftmost_column"),
        ],
    )
    def test_get_cell_on_left(
        self,
        monkeypatch,
        mock_cell,
        cell_row,
        cell_col,
        expected_row,
        expected_col,
        mock_orca_dependencies
    ):
        """Test AXTable.get_cell_on_left."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible)
        mock_result_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            AXTable, "get_cell_coordinates",
            lambda obj, prefer_attribute: (cell_row, cell_col)
        )
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(AXTable, "get_cell_at", lambda table, row, col: mock_result_cell)

        result = AXTable.get_cell_on_left(mock_cell)
        assert result == mock_result_cell

    @pytest.mark.parametrize(
        "cell_row, cell_col, col_span, expected_row, expected_col",
        [
            pytest.param(2, 3, 1, 2, 4, id="single_col_span"),
            pytest.param(2, 3, 2, 2, 5, id="multi_col_span"),
        ],
    )
    def test_get_cell_on_right(
        self,
        monkeypatch,
        mock_cell,
        cell_row,
        cell_col,
        col_span,
        expected_row,
        expected_col,
        mock_orca_dependencies
    ):
        """Test AXTable.get_cell_on_right."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible)
        mock_result_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            AXTable, "get_cell_coordinates",
            lambda obj, prefer_attribute: (cell_row, cell_col)
        )
        monkeypatch.setattr(AXTable, "get_cell_spans", lambda obj, prefer_attribute: (1, col_span))
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(AXTable, "get_cell_at", lambda table, row, col: mock_result_cell)

        result = AXTable.get_cell_on_right(mock_cell)
        assert result == mock_result_cell

    def test_get_start_of_row(self, monkeypatch, mock_cell, mock_orca_dependencies):
        """Test AXTable.get_start_of_row."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible)
        mock_result_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXTable, "get_cell_coordinates", lambda obj, prefer_attribute: (2, 3))
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(AXTable, "get_cell_at", lambda table, row, col: mock_result_cell)

        result = AXTable.get_start_of_row(mock_cell)
        assert result == mock_result_cell

    def test_get_end_of_row(self, monkeypatch, mock_cell, mock_orca_dependencies):
        """Test AXTable.get_end_of_row."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible)
        mock_result_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXTable, "get_cell_coordinates", lambda obj, prefer_attribute: (2, 3))
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(AXTable, "get_column_count", lambda table: 5)
        monkeypatch.setattr(AXTable, "get_cell_at", lambda table, row, col: mock_result_cell)

        result = AXTable.get_end_of_row(mock_cell)
        assert result == mock_result_cell

    def test_get_top_of_column(self, monkeypatch, mock_cell, mock_orca_dependencies):
        """Test AXTable.get_top_of_column."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible)
        mock_result_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXTable, "get_cell_coordinates", lambda obj, prefer_attribute: (2, 3))
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(AXTable, "get_cell_at", lambda table, row, col: mock_result_cell)

        result = AXTable.get_top_of_column(mock_cell)
        assert result == mock_result_cell

    def test_get_bottom_of_column(self, monkeypatch, mock_cell, mock_orca_dependencies):
        """Test AXTable.get_bottom_of_column."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible)
        mock_result_cell = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXTable, "get_cell_coordinates", lambda obj, prefer_attribute: (2, 3))
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(AXTable, "get_row_count", lambda table: 8)
        monkeypatch.setattr(AXTable, "get_cell_at", lambda table, row, col: mock_result_cell)

        result = AXTable.get_bottom_of_column(mock_cell)
        assert result == mock_result_cell

    @pytest.mark.parametrize(
        "formula_attr, formula_attr_alt, expected_result",
        [
            pytest.param("=SUM(A1:A5)", None, "=SUM(A1:A5)", id="formula_attribute"),
            pytest.param(None, "=A1+B1", "=A1+B1", id="formula_alt_attribute"),
            pytest.param(None, None, None, id="no_formula"),
        ],
    )
    def test_get_cell_formula(
        self,
        monkeypatch,
        mock_cell,
        formula_attr,
        formula_attr_alt,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXTable.get_cell_formula."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        attrs = {}
        if formula_attr:
            attrs["formula"] = formula_attr
        if formula_attr_alt:
            attrs["Formula"] = formula_attr_alt

        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj, use_cache: attrs)

        result = AXTable.get_cell_formula(mock_cell)
        assert result == expected_result

    @pytest.mark.parametrize(
        "cell_row, cell_col, expected_result",
        [
            pytest.param(0, 0, True, id="first_cell"),
            pytest.param(0, 1, False, id="not_first_cell"),
            pytest.param(1, 0, False, id="not_first_row"),
        ],
    )
    def test_is_first_cell(
        self,
        monkeypatch,
        mock_cell,
        cell_row,
        cell_col,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXTable.is_first_cell."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        monkeypatch.setattr(
            AXTable, "get_cell_coordinates",
            lambda obj, prefer_attribute: (cell_row, cell_col)
        )

        result = AXTable.is_first_cell(mock_cell)
        assert result == expected_result

    @pytest.mark.parametrize(
        "cell_row, cell_col, row_count, col_count, expected_result",
        [
            pytest.param(2, 3, 3, 4, True, id="last_cell"),
            pytest.param(1, 3, 3, 4, False, id="not_last_row"),
            pytest.param(2, 2, 3, 4, False, id="not_last_column"),
            pytest.param(-1, -1, 3, 4, False, id="invalid_coordinates"),
        ],
    )
    def test_is_last_cell(
        self, monkeypatch, mock_cell, cell_row, cell_col, row_count, col_count,
        expected_result, mock_orca_dependencies
    ):
        """Test AXTable.is_last_cell."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible) if cell_row >= 0 and cell_col >= 0 else None

        monkeypatch.setattr(
            AXTable, "get_cell_coordinates",
            lambda obj, prefer_attribute: (cell_row, cell_col)
        )
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(
            AXTable, "get_row_count", lambda table, prefer_attribute: row_count
        )
        monkeypatch.setattr(
            AXTable, "get_column_count", lambda table, prefer_attribute: col_count
        )

        result = AXTable.is_last_cell(mock_cell)
        assert result == expected_result

    @pytest.mark.parametrize(
        "cell_col, expected_result",
        [
            pytest.param(0, True, id="start_of_row"),
            pytest.param(1, False, id="not_start_of_row"),
        ],
    )
    def test_is_start_of_row(
        self,
        monkeypatch,
        mock_cell,
        cell_col,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXTable.is_start_of_row."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        monkeypatch.setattr(
            AXTable, "get_cell_coordinates", lambda obj, prefer_attribute: (2, cell_col)
        )

        result = AXTable.is_start_of_row(mock_cell)
        assert result == expected_result

    @pytest.mark.parametrize(
        "cell_col, col_count, expected_result",
        [
            pytest.param(3, 4, True, id="end_of_row"),
            pytest.param(2, 4, False, id="not_end_of_row"),
            pytest.param(-1, 4, False, id="invalid_column"),
        ],
    )
    def test_is_end_of_row(
        self,
        monkeypatch,
        mock_cell,
        cell_col,
        col_count,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXTable.is_end_of_row."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible) if cell_col >= 0 else None

        monkeypatch.setattr(
            AXTable, "get_cell_coordinates", lambda obj, prefer_attribute: (2, cell_col)
        )
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(
            AXTable, "get_column_count", lambda table, prefer_attribute: col_count
        )

        result = AXTable.is_end_of_row(mock_cell)
        assert result == expected_result

    @pytest.mark.parametrize(
        "cell_row, expected_result",
        [
            pytest.param(0, True, id="top_of_column"),
            pytest.param(1, False, id="not_top_of_column"),
        ],
    )
    def test_is_top_of_column(
        self,
        monkeypatch,
        mock_cell,
        cell_row,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXTable.is_top_of_column."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        monkeypatch.setattr(
            AXTable, "get_cell_coordinates", lambda obj, prefer_attribute: (cell_row, 3)
        )

        result = AXTable.is_top_of_column(mock_cell)
        assert result == expected_result

    @pytest.mark.parametrize(
        "cell_row, row_count, expected_result",
        [
            pytest.param(4, 5, True, id="bottom_of_column"),
            pytest.param(3, 5, False, id="not_bottom_of_column"),
            pytest.param(-1, 5, False, id="invalid_row"),
        ],
    )
    def test_is_bottom_of_column(
        self, monkeypatch, mock_cell, cell_row, row_count, expected_result, mock_orca_dependencies
    ):
        """Test AXTable.is_bottom_of_column."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable

        mock_table = Mock(spec=Atspi.Accessible) if cell_row >= 0 else None

        monkeypatch.setattr(
            AXTable, "get_cell_coordinates", lambda obj, prefer_attribute: (cell_row, 3)
        )
        monkeypatch.setattr(AXTable, "get_table", lambda obj: mock_table)
        monkeypatch.setattr(
            AXTable, "get_row_count", lambda table, prefer_attribute: row_count
        )

        result = AXTable.is_bottom_of_column(mock_cell)
        assert result == expected_result

    def test_get_table_description_for_presentation_with_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_table_description_for_presentation with table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import messages

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(AXTable, "get_row_count", lambda table: 5)
        monkeypatch.setattr(AXTable, "get_column_count", lambda table: 3)
        monkeypatch.setattr(AXTable, "is_non_uniform_table", lambda table: False)
        monkeypatch.setattr(messages, "table_size", lambda rows, cols: f"{rows} by {cols} table")

        result = AXTable.get_table_description_for_presentation(mock_table)
        assert result == "5 by 3 table"

    def test_get_table_description_for_presentation_non_uniform(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_table_description_for_presentation with non-uniform table."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject
        from orca import messages

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: True)
        monkeypatch.setattr(AXTable, "get_row_count", lambda table: 5)
        monkeypatch.setattr(AXTable, "get_column_count", lambda table: 3)
        monkeypatch.setattr(AXTable, "is_non_uniform_table", lambda table: True)
        monkeypatch.setattr(messages, "table_size", lambda rows, cols: f"{rows} by {cols} table")
        monkeypatch.setattr(messages, "TABLE_NON_UNIFORM", "non uniform")

        result = AXTable.get_table_description_for_presentation(mock_table)
        assert result == "non uniform 5 by 3 table"

    def test_get_table_description_for_presentation_without_support(
        self, monkeypatch, mock_table, mock_orca_dependencies
    ):
        """Test AXTable.get_table_description_for_presentation without table support."""

        clean_module_cache("orca.ax_table")
        from orca.ax_table import AXTable
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_table", lambda obj: False)

        result = AXTable.get_table_description_for_presentation(mock_table)
        assert result == ""
