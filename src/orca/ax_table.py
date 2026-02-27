# Utilities for obtaining information about accessible tables.
#
# Copyright 2023-2026 Igalia, S.L.
# Copyright 2023 GNOME Foundation Inc.
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

"""Utilities for obtaining information about accessible tables."""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from . import debug
from .ax_object import AXObject
from .ax_utilities_role import AXUtilitiesRole

if TYPE_CHECKING:
    from typing import ClassVar


class AXTable:
    """Utilities for obtaining information about accessible tables."""

    CAPTIONS: ClassVar[dict[int, Atspi.Accessible]] = {}
    PHYSICAL_COORDINATES_FROM_CELL: ClassVar[dict[int, tuple[int, int]]] = {}
    PHYSICAL_COORDINATES_FROM_TABLE: ClassVar[dict[int, tuple[int, int]]] = {}
    PHYSICAL_SPANS_FROM_CELL: ClassVar[dict[int, tuple[int, int]]] = {}
    PHYSICAL_SPANS_FROM_TABLE: ClassVar[dict[int, tuple[int, int]]] = {}
    PHYSICAL_COLUMN_COUNT: ClassVar[dict[int, int]] = {}
    PHYSICAL_ROW_COUNT: ClassVar[dict[int, int]] = {}
    PRESENTABLE_COORDINATES: ClassVar[dict[int, tuple[str | None, str | None]]] = {}
    PRESENTABLE_SPANS: ClassVar[dict[int, tuple[str | None, str | None]]] = {}
    PRESENTABLE_COLUMN_COUNT: ClassVar[dict[int, int | None]] = {}
    PRESENTABLE_ROW_COUNT: ClassVar[dict[int, int | None]] = {}

    _last_cell_row: ClassVar[int] = -1
    _last_cell_column: ClassVar[int] = -1

    _lock = threading.Lock()

    @staticmethod
    def start_cache_clearing_thread() -> None:
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=AXTable._clear_stored_data)
        thread.daemon = True
        thread.start()

    @staticmethod
    def _clear_stored_data() -> None:
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(60)
            AXTable._clear_all_dictionaries()

    @staticmethod
    def _clear_all_dictionaries(reason: str = "") -> None:
        msg = "AXTable: Clearing cache."
        if reason:
            msg += f" Reason: {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        with AXTable._lock:
            AXTable.CAPTIONS.clear()
            AXTable.PHYSICAL_COORDINATES_FROM_CELL.clear()
            AXTable.PHYSICAL_COORDINATES_FROM_TABLE.clear()
            AXTable.PHYSICAL_SPANS_FROM_CELL.clear()
            AXTable.PHYSICAL_SPANS_FROM_TABLE.clear()
            AXTable.PHYSICAL_COLUMN_COUNT.clear()
            AXTable.PHYSICAL_ROW_COUNT.clear()
            AXTable.PRESENTABLE_COORDINATES.clear()
            AXTable.PRESENTABLE_COLUMN_COUNT.clear()
            AXTable.PRESENTABLE_ROW_COUNT.clear()

    @staticmethod
    def clear_cache_now(reason: str = "") -> None:
        """Clears all cached information immediately."""

        AXTable._clear_all_dictionaries(reason)

    @staticmethod
    def get_last_cell_coordinates() -> tuple[int, int]:
        """Returns the last known cell coordinates as a tuple of (row, column)."""

        row, column = AXTable._last_cell_row, AXTable._last_cell_column
        msg = f"AXTable: Last known cell coordinates: row={row}, column={column}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return row, column

    @staticmethod
    def save_last_cell_coordinates(obj: Atspi.Accessible) -> None:
        """Saves the cell coordinates for obj for future reference."""

        row, column = AXTable.get_cell_coordinates(obj, find_cell=True)
        msg = f"AXTable: Setting last cell coordinates to row={row}, column={column}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        AXTable._last_cell_row = row
        AXTable._last_cell_column = column

    @staticmethod
    def get_caption(table: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the accessible object containing the caption of table."""

        if not AXObject.supports_table(table):
            return None

        if hash(table) in AXTable.CAPTIONS:
            return AXTable.CAPTIONS.get(hash(table))

        try:
            caption = Atspi.Table.get_caption(table)
        except GLib.GError as error:
            msg = f"AXTable: Exception in get_caption: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        tokens = ["AXTable: Caption for", table, "is", caption]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.CAPTIONS[hash(table)] = caption
        return caption

    @staticmethod
    def get_column_count(table: Atspi.Accessible, prefer_attribute: bool = True) -> int:
        """Returns the column count of table."""

        if not AXObject.supports_table(table):
            return -1

        if prefer_attribute:
            count = AXTable._get_column_count_from_attribute(table)
            if count is not None:
                return count

        count = AXTable.PHYSICAL_COLUMN_COUNT.get(hash(table))
        if count is not None:
            return count

        try:
            count = Atspi.Table.get_n_columns(table)
        except GLib.GError as error:
            msg = f"AXTable: Exception in get_column_count: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1

        tokens = ["AXTable: Column count for", table, "is", count]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PHYSICAL_COLUMN_COUNT[hash(table)] = count
        return count

    @staticmethod
    def _get_column_count_from_attribute(table: Atspi.Accessible) -> int | None:
        """Returns the value of the 'colcount' object attribute or None if not found."""

        if hash(table) in AXTable.PRESENTABLE_COLUMN_COUNT:
            return AXTable.PRESENTABLE_COLUMN_COUNT.get(hash(table))

        attrs = AXObject.get_attributes_dict(table)
        attr = attrs.get("colcount")
        count = None
        if attr is not None:
            count = int(attr)

        tokens = ["AXTable: Column count attribute for", table, "is", count]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PRESENTABLE_COLUMN_COUNT[hash(table)] = count
        return count

    @staticmethod
    def get_row_count(table: Atspi.Accessible, prefer_attribute: bool = True) -> int:
        """Returns the row count of table."""

        if not AXObject.supports_table(table):
            return -1

        if prefer_attribute:
            count = AXTable._get_row_count_from_attribute(table)
            if count is not None:
                return count

        count = AXTable.PHYSICAL_ROW_COUNT.get(hash(table))
        if count is not None:
            return count

        try:
            count = Atspi.Table.get_n_rows(table)
        except GLib.GError as error:
            msg = f"AXTable: Exception in get_row_count: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1

        tokens = ["AXTable: Row count for", table, "is", count]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PHYSICAL_ROW_COUNT[hash(table)] = count
        return count

    @staticmethod
    def _get_row_count_from_attribute(table: Atspi.Accessible) -> int | None:
        """Returns the value of the 'rowcount' object attribute or None if not found."""

        if hash(table) in AXTable.PRESENTABLE_ROW_COUNT:
            return AXTable.PRESENTABLE_ROW_COUNT.get(hash(table))

        attrs = AXObject.get_attributes_dict(table)
        attr = attrs.get("rowcount")
        count = None
        if attr is not None:
            count = int(attr)

        tokens = ["AXTable: Row count attribute for", table, "is", count]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PRESENTABLE_ROW_COUNT[hash(table)] = count
        return count

    @staticmethod
    def is_non_uniform_table(
        table: Atspi.Accessible,
        max_rows: int = 25,
        max_cols: int = 25,
    ) -> bool:
        """Returns True if table has at least one cell with a span > 1."""

        try:
            for row in range(min(max_rows, AXTable.get_row_count(table, False))):
                for col in range(min(max_cols, AXTable.get_column_count(table, False))):
                    if Atspi.Table.get_row_extent_at(table, row, col) > 1:
                        return True
                    if Atspi.Table.get_column_extent_at(table, row, col) > 1:
                        return True
        except GLib.GError as error:
            msg = f"AXTable: Exception in is_non_uniform_table: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return False

    @staticmethod
    def get_selected_column_count(table: Atspi.Accessible) -> int:
        """Returns the number of selected columns in table."""

        if not AXObject.supports_table(table):
            return 0

        try:
            count = Atspi.Table.get_n_selected_columns(table)
        except GLib.GError as error:
            msg = f"AXTable: Exception in get_selected_column_count {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXTable: Selected column count for", table, "is", count]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return count

    @staticmethod
    def get_selected_columns(table: Atspi.Accessible) -> list[int]:
        """Returns a list of column indices for the selected columns in table."""

        if not AXObject.supports_table(table):
            return []

        try:
            columns = Atspi.Table.get_selected_columns(table)
        except GLib.GError as error:
            msg = f"AXTable: Exception in get_selected_columns: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        tokens = ["AXTable: Selected columns for", table, "are", columns]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return columns

    @staticmethod
    def get_selected_row_count(table: Atspi.Accessible) -> int:
        """Returns the number of selected rows in table."""

        if not AXObject.supports_table(table):
            return 0

        try:
            count = Atspi.Table.get_n_selected_rows(table)
        except GLib.GError as error:
            msg = f"AXTable: Exception in get_selected_row_count {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXTable: Selected row count for", table, "is", count]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return count

    @staticmethod
    def get_selected_rows(table: Atspi.Accessible) -> list[int]:
        """Returns a list of row indices for the selected rows in table."""

        if not AXObject.supports_table(table):
            return []

        try:
            rows = Atspi.Table.get_selected_rows(table)
        except GLib.GError as error:
            msg = f"AXTable: Exception in get_selected_rows: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        tokens = ["AXTable: Selected rows for", table, "are", rows]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return rows

    @staticmethod
    def get_cell_at(table: Atspi.Accessible, row: int, column: int) -> Atspi.Accessible | None:
        """Returns the cell at the 0-indexed row and column."""

        if not AXObject.supports_table(table):
            return None

        try:
            cell = Atspi.Table.get_accessible_at(table, row, column)
        except GLib.GError as error:
            tokens = [
                f"AXTable: Exception getting cell at row: {row} col: {column} in",
                table,
                ":",
                error,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        tokens = [f"AXTable: Cell at row: {row} col: {column} in", table, "is", cell]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return cell

    @staticmethod
    def _get_cell_index(cell: Atspi.Accessible) -> int:
        """Returns the index of cell to be used with the table interface."""

        index = AXObject.get_attribute(cell, "table-cell-index")
        if index is not None and index != "":
            return int(index)

        # We might have nested cells. So far this has only been seen in Gtk,
        # where the parent of a table cell is also a table cell. We need the
        # index of the parent for use with the table interface.
        parent = AXObject.get_parent(cell)
        if AXObject.get_role(parent) == Atspi.Role.TABLE_CELL:
            cell = parent

        return AXObject.get_index_in_parent(cell)

    @staticmethod
    def get_cell_spans(cell: Atspi.Accessible, prefer_attribute: bool = True) -> tuple[int, int]:
        """Returns the row and column spans."""

        if not AXUtilitiesRole.is_table_cell_or_header(cell):
            return -1, -1

        if AXObject.supports_table_cell(cell):
            row_span, col_span = AXTable._get_cell_spans_from_table_cell(cell)
        else:
            row_span, col_span = AXTable.get_cell_spans_from_table(cell)

        if not prefer_attribute:
            return row_span, col_span

        rowspan_attr, colspan_attr = AXTable._get_cell_spans_from_attribute(cell)
        if rowspan_attr is not None:
            row_span = int(rowspan_attr)
        if colspan_attr is not None:
            col_span = int(colspan_attr)

        return row_span, col_span

    @staticmethod
    def _get_cell_spans_from_attribute(cell: Atspi.Accessible) -> tuple[str | None, str | None]:
        """Returns the row and column spans exposed via object attribute, or None, None."""

        if hash(cell) in AXTable.PRESENTABLE_SPANS:
            return AXTable.PRESENTABLE_SPANS.get(hash(cell), (None, None))

        attrs = AXObject.get_attributes_dict(cell)
        row_span = attrs.get("rowspan", None)
        col_span = attrs.get("colspan", None)

        tokens = ["AXTable: Row and col span attributes for", cell, ":", row_span, ",", col_span]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PRESENTABLE_SPANS[hash(cell)] = row_span, col_span
        return row_span, col_span

    @staticmethod
    def _get_row_column_extents(
        cell: Atspi.Accessible,
        table: Atspi.Accessible,
        index: int,
    ) -> tuple[int, int]:
        """Returns the validated row and column extents for cell, or (-1, -1) on failure."""

        try:
            result = Atspi.Table.get_row_column_extents_at_index(table, index)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_cell_spans_from_table: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1, -1

        if result is None:
            tokens = [
                "AXTable: get_row_column_extents_at_index failed for",
                cell,
                f"at index {index} in",
                table,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return -1, -1

        if not result[0]:
            return -1, -1

        row_span = result.row_extents
        row_count = AXTable.get_row_count(table, False)
        if row_span > row_count:
            tokens = [
                "AXTable: Table iface row span for",
                cell,
                f"{row_span} is greater than row count: {row_count}",
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            row_span = 1

        col_span = result.col_extents
        col_count = AXTable.get_column_count(table, False)
        if col_span > col_count:
            tokens = [
                "AXTable: Table iface col span for",
                cell,
                f"{col_span} is greater than col count: {col_count}",
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            col_span = 1

        return row_span, col_span

    @staticmethod
    def get_cell_spans_from_table(cell: Atspi.Accessible) -> tuple[int, int]:
        """Returns the row and column spans of cell via the table interface."""

        if hash(cell) in AXTable.PHYSICAL_SPANS_FROM_TABLE:
            return AXTable.PHYSICAL_SPANS_FROM_TABLE.get(hash(cell), (-1, -1))

        index = AXTable._get_cell_index(cell)
        if index < 0:
            return -1, -1

        table = AXTable._find_ancestor_table(cell)
        if table is None or not AXObject.supports_table(table):
            return -1, -1

        # Cells in a tree are expected to not span multiple rows or columns.
        # Also this: https://bugreports.qt.io/browse/QTBUG-119167
        if AXUtilitiesRole.is_tree(table):
            return 1, 1

        row_span, col_span = AXTable._get_row_column_extents(cell, table, index)
        tokens = [
            "AXTable: Table iface spans for",
            cell,
            f"are rowspan: {row_span}, colspan: {col_span}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PHYSICAL_SPANS_FROM_TABLE[hash(cell)] = row_span, col_span
        return row_span, col_span

    @staticmethod
    def _get_cell_spans_from_table_cell(cell: Atspi.Accessible) -> tuple[int, int]:
        """Returns the row and column spans of cell via the table cell interface."""

        if hash(cell) in AXTable.PHYSICAL_SPANS_FROM_CELL:
            return AXTable.PHYSICAL_SPANS_FROM_CELL.get(hash(cell), (-1, -1))

        if not AXObject.supports_table_cell(cell):
            return -1, -1

        try:
            # TODO - JD: We get the spans individually due to
            # https://bugzilla.mozilla.org/show_bug.cgi?id=1862437
            row_span = Atspi.TableCell.get_row_span(cell)
            col_span = Atspi.TableCell.get_column_span(cell)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_cell_spans_from_table_cell: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1, -1

        tokens = [
            "AXTable: TableCell iface spans for",
            cell,
            f"are rowspan: {row_span}, colspan: {col_span}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PHYSICAL_SPANS_FROM_CELL[hash(cell)] = row_span, col_span
        return row_span, col_span

    @staticmethod
    def get_column_headers_from_table(
        table: Atspi.Accessible,
        column: int,
    ) -> list[Atspi.Accessible]:
        """Returns the column headers of the indexed column via the table interface."""

        if not AXObject.supports_table(table):
            return []

        if column < 0:
            return []

        try:
            header = Atspi.Table.get_column_header(table, column)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_column_headers_from_table: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        tokens = [f"AXTable: Table iface header for column {column} of", table, "is", header]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if header is not None:
            return [header]

        return []

    @staticmethod
    def get_column_headers_from_table_cell(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the column headers for cell via the table cell interface."""

        if not AXObject.supports_table_cell(cell):
            return []

        try:
            headers = Atspi.TableCell.get_column_header_cells(cell)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_column_headers_from_table_cell: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        if headers is None:
            tokens = ["AXTable: get_column_header_cells failed for", cell]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        tokens = ["AXTable: TableCell iface column headers for cell are:", headers]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return headers

    @staticmethod
    def get_row_headers_from_table(table: Atspi.Accessible, row: int) -> list[Atspi.Accessible]:
        """Returns the row headers of the indexed row via the table interface."""

        if not AXObject.supports_table(table):
            return []

        if row < 0:
            return []

        try:
            header = Atspi.Table.get_row_header(table, row)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_row_headers_from_table: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        tokens = [f"AXTable: Table iface header for row {row} of", table, "is", header]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if header is not None:
            return [header]

        return []

    @staticmethod
    def get_row_headers_from_table_cell(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the row headers for cell via the table cell interface."""

        if not AXObject.supports_table_cell(cell):
            return []

        try:
            headers = Atspi.TableCell.get_row_header_cells(cell)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_row_headers_from_table_cell: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        if headers is None:
            tokens = ["AXTable: get_row_header_cells failed for", cell]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        tokens = ["AXTable: TableCell iface row headers for cell are:", headers]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return headers

    @staticmethod
    def get_cell_coordinates(
        cell: Atspi.Accessible,
        prefer_attribute: bool = True,
        find_cell: bool = False,
    ) -> tuple[int, int]:
        """Returns the 0-based row and column indices."""

        if not AXUtilitiesRole.is_table_cell_or_header(cell) and find_cell:
            cell = AXObject.find_ancestor(cell, AXUtilitiesRole.is_table_cell_or_header)

        if not AXUtilitiesRole.is_table_cell_or_header(cell):
            return -1, -1

        if AXObject.supports_table_cell(cell):
            row, col = AXTable._get_cell_coordinates_from_table_cell(cell)
        else:
            row, col = AXTable.get_cell_coordinates_from_table(cell)

        if not prefer_attribute:
            return row, col

        row_index, col_index = AXTable._get_cell_coordinates_from_attribute(cell)
        if row_index is not None:
            row = int(row_index) - 1
        if col_index is not None:
            col = int(col_index) - 1

        return row, col

    @staticmethod
    def get_cell_coordinates_from_table(cell: Atspi.Accessible) -> tuple[int, int]:
        """Returns the row and column indices of cell via the table interface."""

        if hash(cell) in AXTable.PHYSICAL_COORDINATES_FROM_TABLE:
            return AXTable.PHYSICAL_COORDINATES_FROM_TABLE.get(hash(cell), (-1, -1))

        index = AXTable._get_cell_index(cell)
        if index < 0:
            return -1, -1

        table = AXTable._find_ancestor_table(cell)
        if table is None:
            tokens = ["AXTable: Couldn't find table-implementing ancestor for", cell]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return -1, -1

        try:
            row = Atspi.Table.get_row_at_index(table, index)
            column = Atspi.Table.get_column_at_index(table, index)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_cell_coordinates_from_table: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1, -1

        tokens = ["AXTable: Table iface coords for", cell, f"are row: {row}, col: {column}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PHYSICAL_COORDINATES_FROM_TABLE[hash(cell)] = row, column
        return row, column

    @staticmethod
    def _get_cell_coordinates_from_table_cell(cell: Atspi.Accessible) -> tuple[int, int]:
        """Returns the row and column indices of cell via the table cell interface."""

        if hash(cell) in AXTable.PHYSICAL_COORDINATES_FROM_CELL:
            return AXTable.PHYSICAL_COORDINATES_FROM_CELL.get(hash(cell), (-1, -1))

        if not AXObject.supports_table_cell(cell):
            return -1, -1

        try:
            success, row, column = Atspi.TableCell.get_position(cell)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_cell_coordinates_from_table_cell: {error}"

            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1, -1

        if not success:
            return -1, -1

        tokens = ["AXTable: TableCell iface coords for", cell, f"are row: {row}, col: {column}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PHYSICAL_COORDINATES_FROM_CELL[hash(cell)] = row, column
        return row, column

    @staticmethod
    def _get_cell_coordinates_from_attribute(
        cell: Atspi.Accessible,
    ) -> tuple[str | None, str | None]:
        """Returns the 1-based indices for cell exposed via object attribute, or None, None."""

        if cell is None:
            return None, None

        if hash(cell) in AXTable.PRESENTABLE_COORDINATES:
            return AXTable.PRESENTABLE_COORDINATES.get(hash(cell), (None, None))

        attrs = AXObject.get_attributes_dict(cell)
        row_index = attrs.get("rowindex")
        col_index = attrs.get("colindex")

        tokens = ["AXTable: Row and col index attributes for", cell, ":", row_index, ",", col_index]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PRESENTABLE_COORDINATES[hash(cell)] = row_index, col_index
        if row_index is not None and col_index is not None:
            return row_index, col_index

        row = AXObject.find_ancestor(cell, AXUtilitiesRole.is_table_row)
        if row is None:
            return row_index, col_index

        attrs = AXObject.get_attributes_dict(row)
        row_index = attrs.get("rowindex", row_index)
        col_index = attrs.get("colindex", col_index)

        tokens = ["AXTable: Updated attributes based on", row, ":", row_index, col_index]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PRESENTABLE_COORDINATES[hash(cell)] = row_index, col_index
        return row_index, col_index

    @staticmethod
    def get_table_from_table_cell(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the table for obj via the table cell interface."""

        if not AXObject.supports_table_cell(obj):
            return None

        try:
            table = Atspi.TableCell.get_table(obj)
        except GLib.GError as error:
            msg = f"AXTable: Exception in get_table_from_table_cell: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        if AXObject.supports_table(table):
            return table

        return None

    @staticmethod
    def _find_ancestor_table(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns obj if it is a table, or the closest ancestor table of obj."""

        if obj is None:
            return None

        def is_table(x: Atspi.Accessible) -> bool:
            if (
                AXUtilitiesRole.is_table(x)
                or AXUtilitiesRole.is_tree_table(x)
                or AXUtilitiesRole.is_tree(x)
            ):
                return AXObject.supports_table(x)
            return False

        if is_table(obj):
            return obj

        return AXObject.find_ancestor(obj, is_table)

    @staticmethod
    def _get_table(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns obj if it is a table, or the closest ancestor table of obj."""

        if obj is None:
            return None

        table = AXTable.get_table_from_table_cell(obj)
        if table is not None:
            return table

        return AXTable._find_ancestor_table(obj)

    @staticmethod
    def get_first_cell(table: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the first cell in table."""

        row, col = 0, 0
        return AXTable.get_cell_at(table, row, col)

    @staticmethod
    def get_last_cell(table: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the last cell in table."""

        row, col = AXTable.get_row_count(table) - 1, AXTable.get_column_count(table) - 1
        return AXTable.get_cell_at(table, row, col)

    @staticmethod
    def get_cell_above(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell above cell in table."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        row -= 1
        return AXTable.get_cell_at(AXTable._get_table(cell), row, col)

    @staticmethod
    def get_cell_below(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell below cell in table."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        row += AXTable.get_cell_spans(cell, prefer_attribute=False)[0]
        return AXTable.get_cell_at(AXTable._get_table(cell), row, col)

    @staticmethod
    def get_cell_on_left(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell to the left."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        col -= 1
        return AXTable.get_cell_at(AXTable._get_table(cell), row, col)

    @staticmethod
    def get_cell_on_right(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell to the right."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        col += AXTable.get_cell_spans(cell, prefer_attribute=False)[1]
        return AXTable.get_cell_at(AXTable._get_table(cell), row, col)

    @staticmethod
    def get_start_of_row(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell at the start of cell's row."""

        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        return AXTable.get_cell_at(AXTable._get_table(cell), row, 0)

    @staticmethod
    def get_end_of_row(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell at the end of cell's row."""

        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        table = AXTable._get_table(cell)
        col = AXTable.get_column_count(table) - 1
        return AXTable.get_cell_at(AXTable._get_table(cell), row, col)

    @staticmethod
    def get_top_of_column(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell at the top of cell's column."""

        col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
        return AXTable.get_cell_at(AXTable._get_table(cell), 0, col)

    @staticmethod
    def get_bottom_of_column(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell at the bottom of cell's column."""

        col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
        table = AXTable._get_table(cell)
        row = AXTable.get_row_count(table) - 1
        return AXTable.get_cell_at(AXTable._get_table(cell), row, col)

    @staticmethod
    def is_start_of_row(cell: Atspi.Accessible) -> bool:
        """Returns True if this is the first cell in its row."""

        col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
        return col == 0

    @staticmethod
    def is_end_of_row(cell: Atspi.Accessible) -> bool:
        """Returns True if this is the last cell in its row."""

        col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
        if col < 0:
            return False

        table = AXTable._get_table(cell)
        if table is None:
            return False

        return col + 1 == AXTable.get_column_count(table, prefer_attribute=False)

    @staticmethod
    def is_top_of_column(cell: Atspi.Accessible) -> bool:
        """Returns True if this is the first cell in its column."""

        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        return row == 0

    @staticmethod
    def is_bottom_of_column(cell: Atspi.Accessible) -> bool:
        """Returns True if this is the last cell in its column."""

        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        if row < 0:
            return False

        table = AXTable._get_table(cell)
        if table is None:
            return False

        return row + 1 == AXTable.get_row_count(table, prefer_attribute=False)


AXTable.start_cache_clearing_thread()
