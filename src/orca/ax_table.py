# Utilities for obtaining information about accessible tables.
#
# Copyright 2023 Igalia, S.L.
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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-return-statements

"""Utilities for obtaining information about accessible tables."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L." \
                "Copyright (c) 2023 GNOME Foundation Inc."
__license__   = "LGPL"

import threading
import time
from typing import Generator

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from . import debug
from . import messages
from . import object_properties
from .ax_object import AXObject
from .ax_component import AXComponent
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState


class AXTable:
    """Utilities for obtaining information about accessible tables."""

    # Things we cache.
    CAPTIONS: dict[int, Atspi.Accessible] = {}
    PHYSICAL_COORDINATES_FROM_CELL: dict[int, tuple[int, int]] = {}
    PHYSICAL_COORDINATES_FROM_TABLE: dict[int, tuple[int, int]] = {}
    PHYSICAL_SPANS_FROM_CELL: dict[int, tuple[int, int]] = {}
    PHYSICAL_SPANS_FROM_TABLE: dict[int, tuple[int, int]] = {}
    PHYSICAL_COLUMN_COUNT: dict[int, int] = {}
    PHYSICAL_ROW_COUNT: dict[int, int] = {}
    PRESENTABLE_COORDINATES: dict[int, tuple[str | None, str | None]] = {}
    PRESENTABLE_COORDINATES_LABELS: dict[int, str] = {}
    PRESENTABLE_SPANS: dict[int, tuple[str | None, str | None]] = {}
    PRESENTABLE_COLUMN_COUNT: dict[int, int | None] = {}
    PRESENTABLE_ROW_COUNT: dict[int, int | None] = {}
    COLUMN_HEADERS_FOR_CELL: dict[int, list[Atspi.Accessible]] = {}
    ROW_HEADERS_FOR_CELL: dict[int, list[Atspi.Accessible]] = {}

    # Things which have to be explicitly cleared.
    DYNAMIC_COLUMN_HEADERS_ROW: dict[int, int] = {}
    DYNAMIC_ROW_HEADERS_COLUMN: dict[int, int] = {}

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
            AXTable.PRESENTABLE_COORDINATES_LABELS.clear()
            AXTable.PRESENTABLE_COLUMN_COUNT.clear()
            AXTable.PRESENTABLE_ROW_COUNT.clear()
            AXTable.COLUMN_HEADERS_FOR_CELL.clear()
            AXTable.ROW_HEADERS_FOR_CELL.clear()

    @staticmethod
    def clear_cache_now(reason: str = "") -> None:
        """Clears all cached information immediately."""

        AXTable._clear_all_dictionaries(reason)

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
        table: Atspi.Accessible, max_rows: int = 25, max_cols: int = 25
    ) -> bool:
        """Returns True if table has at least one cell with a span > 1."""

        for row in range(min(max_rows, AXTable.get_row_count(table, False))):
            for col in range(min(max_cols, AXTable.get_column_count(table, False))):
                try:
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
    def all_cells_are_selected(table: Atspi.Accessible) -> bool:
        """Returns True if all cells in table are selected."""

        if not AXObject.supports_table(table):
            return False

        rows = AXTable.get_row_count(table, prefer_attribute=False)
        if rows <= 0:
            return False

        if AXTable.get_selected_row_count(table) == rows:
            return True

        cols = AXTable.get_column_count(table, prefer_attribute=False)
        return AXTable.get_selected_column_count(table) == cols

    @staticmethod
    def get_cell_at(table: Atspi.Accessible, row: int, column: int) -> Atspi.Accessible | None:
        """Returns the cell at the 0-indexed row and column."""

        if not AXObject.supports_table(table):
            return None

        try:
            cell = Atspi.Table.get_accessible_at(table, row, column)
        except GLib.GError as error:
            tokens = [f"AXTable: Exception getting cell at row: {row} col: {column} in", table,
                      ":", error]
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
            row_span, col_span = AXTable._get_cell_spans_from_table(cell)

        if not prefer_attribute:
            return row_span, col_span

        rowspan_attr, colspan_attr = AXTable._get_cell_spans_from_attribute(cell)
        if rowspan_attr is not None:
            row_span = int(rowspan_attr)
        if colspan_attr is not None:
            col_span = int(colspan_attr)

        return row_span, col_span

    @staticmethod
    def _get_cell_spans_from_attribute(
        cell: Atspi.Accessible
    ) -> tuple[str | None, str | None]:
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
    def _get_cell_spans_from_table(cell: Atspi.Accessible) -> tuple[int, int]:
        """Returns the row and column spans of cell via the table interface."""

        if hash(cell) in AXTable.PHYSICAL_SPANS_FROM_TABLE:
            return AXTable.PHYSICAL_SPANS_FROM_TABLE.get(hash(cell), (-1, -1))

        index = AXTable._get_cell_index(cell)
        if index < 0:
            return -1, -1

        table = AXTable.get_table(cell)
        if table is None:
            return -1, -1

        if not AXObject.supports_table(table):
            return -1, -1

        # Cells in a tree are expected to not span multiple rows or columns.
        # Also this: https://bugreports.qt.io/browse/QTBUG-119167
        if AXUtilitiesRole.is_tree(table):
            return 1, 1

        try:
            result = Atspi.Table.get_row_column_extents_at_index(table, index)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_cell_spans_from_table: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1, -1

        if not result[0]:
            return -1, -1

        row_span = result.row_extents
        row_count = AXTable.get_row_count(table, False)
        if row_span > row_count:
            tokens = ["AXTable: Table iface row span for", cell,
                      f"{row_span} is greater than row count: {row_count}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            row_span = 1

        col_span = result.col_extents
        col_count = AXTable.get_column_count(table, False)
        if col_span > col_count:
            tokens = ["AXTable: Table iface col span for", cell,
                      f"{col_span} is greater than col count: {col_count}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            col_span = 1

        tokens = ["AXTable: Table iface spans for", cell,
                  f"are rowspan: {row_span}, colspan: {col_span}"]
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

        tokens = ["AXTable: TableCell iface spans for", cell,
                  f"are rowspan: {row_span}, colspan: {col_span}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PHYSICAL_SPANS_FROM_CELL[hash(cell)] = row_span, col_span
        return row_span, col_span

    @staticmethod
    def _get_column_headers_from_table(
        table: Atspi.Accessible, column: int
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
    def _get_column_headers_from_table_cell(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the column headers for cell via the table cell interface."""

        if not AXObject.supports_table_cell(cell):
            return []

        try:
            headers = Atspi.TableCell.get_column_header_cells(cell)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_column_headers_from_table_cell: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        tokens = ["AXTable: TableCell iface column headers for cell are:", headers]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return headers

    @staticmethod
    def _get_row_headers_from_table(table: Atspi.Accessible, row: int) -> list[Atspi.Accessible]:
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
    def _get_row_headers_from_table_cell(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the row headers for cell via the table cell interface."""

        if not AXObject.supports_table_cell(cell):
            return []

        try:
            headers = Atspi.TableCell.get_row_header_cells(cell)
        except GLib.GError as error:
            msg = f"AXTable: Exception in _get_row_headers_from_table_cell: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        tokens = ["AXTable: TableCell iface row headers for cell are:", headers]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return headers

    @staticmethod
    def get_new_row_headers(
        cell: Atspi.Accessible,
        old_cell: Atspi.Accessible | None
    ) -> list[Atspi.Accessible]:
        """Returns row headers of cell that are not also headers of old_cell. """

        if old_cell and not AXUtilitiesRole.is_table_cell_or_header(old_cell):
            old_cell = AXObject.find_ancestor(old_cell, AXUtilitiesRole.is_table_cell_or_header)

        headers = AXTable.get_row_headers(cell)
        if old_cell is None:
            return headers

        old_headers = AXTable.get_row_headers(old_cell)
        return list(set(headers).difference(set(old_headers)))

    @staticmethod
    def get_new_column_headers(
        cell: Atspi.Accessible,
        old_cell: Atspi.Accessible | None
    ) -> list[Atspi.Accessible]:
        """Returns column headers of cell that are not also headers of old_cell. """

        if old_cell and not AXUtilitiesRole.is_table_cell_or_header(old_cell):
            old_cell = AXObject.find_ancestor(old_cell, AXUtilitiesRole.is_table_cell_or_header)

        headers = AXTable.get_column_headers(cell)
        if old_cell is None:
            return headers

        old_headers = AXTable.get_column_headers(old_cell)
        return list(set(headers).difference(set(old_headers)))

    @staticmethod
    def get_row_headers(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the row headers for cell, doing extra work to ensure we have them all."""

        if not AXUtilitiesRole.is_table_cell(cell):
            return []

        dynamic_header = AXTable.get_dynamic_row_header(cell)
        if dynamic_header is not None:
            return [dynamic_header]

        # Firefox has the following implementation:
        #   1. Only gives us the innermost/closest header for a cell
        #   2. Supports returning the header of a header
        # Chromium has the following implementation:
        #   1. Gives us all the headers for a cell
        #   2. Does NOT support returning the header of a header
        # The Firefox implementation means we can get all the headers with some work.
        # The Chromium implementation means less work, but makes it hard to present
        # the changed outer header when navigating among nested row/column headers.
        # TODO - JD: Figure out what the rest do, and then try to get the implementations
        # aligned.

        result = AXTable.ROW_HEADERS_FOR_CELL.get(hash(cell))
        if result is not None:
            return result

        result = AXTable._get_row_headers(cell)
        # There either are no headers, or we got all of them.
        if len(result) != 1:
            AXTable.ROW_HEADERS_FOR_CELL[hash(cell)] = result
            return result

        others = AXTable._get_row_headers(result[0])
        while len(others) == 1 and others[0] not in result:
            result.insert(0, others[0])
            others = AXTable._get_row_headers(result[0])

        AXTable.ROW_HEADERS_FOR_CELL[hash(cell)] = result
        return result

    @staticmethod
    def _get_row_headers(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the row headers for cell."""

        if AXObject.supports_table_cell(cell):
            return AXTable._get_row_headers_from_table_cell(cell)

        row, column = AXTable._get_cell_coordinates_from_table(cell)
        if row < 0 or column < 0:
            return []

        table = AXTable.get_table(cell)
        if table is None:
            return []

        headers = []
        rowspan = AXTable._get_cell_spans_from_table(cell)[0]
        for index in range(row, row + rowspan):
            headers.extend(AXTable._get_row_headers_from_table(table, index))

        return headers

    @staticmethod
    def has_row_headers(table: Atspi.Accessible, stop_after: int = 10) -> bool:
        """Returns True if table has any headers for rows 0-stop_after."""

        if not AXObject.supports_table(table):
            return False

        stop_after = min(stop_after + 1, AXTable.get_row_count(table))
        for i in range(stop_after):
            if AXTable._get_row_headers_from_table(table, i):
                return True

        return False

    @staticmethod
    def get_column_headers(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the column headers for cell, doing extra work to ensure we have them all."""

        if not AXUtilitiesRole.is_table_cell(cell):
            return []

        dynamic_header = AXTable.get_dynamic_column_header(cell)
        if dynamic_header is not None:
            return [dynamic_header]

        # Firefox has the following implementation:
        #   1. Only gives us the innermost/closest header for a cell
        #   2. Supports returning the header of a header
        # Chromium has the following implementation:
        #   1. Gives us all the headers for a cell
        #   2. Does NOT support returning the header of a header
        # The Firefox implementation means we can get all the headers with some work.
        # The Chromium implementation means less work, but makes it hard to present
        # the changed outer header when navigating among nested row/column headers.
        # TODO - JD: Figure out what the rest do, and then try to get the implementations
        # aligned.

        result = AXTable.COLUMN_HEADERS_FOR_CELL.get(hash(cell))
        if result is not None:
            return result

        result = AXTable._get_column_headers(cell)
        # There either are no headers, or we got all of them.
        if len(result) != 1:
            AXTable.COLUMN_HEADERS_FOR_CELL[hash(cell)] = result
            return result

        others = AXTable._get_column_headers(result[0])
        while len(others) == 1 and others[0] not in result:
            result.insert(0, others[0])
            others = AXTable._get_column_headers(result[0])

        AXTable.COLUMN_HEADERS_FOR_CELL[hash(cell)] = result
        return result

    @staticmethod
    def _get_column_headers(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the column headers for cell."""

        if AXObject.supports_table_cell(cell):
            return AXTable._get_column_headers_from_table_cell(cell)

        row, column = AXTable._get_cell_coordinates_from_table(cell)
        if row < 0 or column < 0:
            return []

        table = AXTable.get_table(cell)
        if table is None:
            return []

        headers = []
        colspan = AXTable._get_cell_spans_from_table(cell)[1]
        for index in range(column, column + colspan):
            headers.extend(AXTable._get_column_headers_from_table(table, index))

        return headers

    @staticmethod
    def has_column_headers(table: Atspi.Accessible, stop_after: int = 10) -> bool:
        """Returns True if table has any headers for columns 0-stop_after."""

        if not AXObject.supports_table(table):
            return False

        stop_after = min(stop_after + 1, AXTable.get_column_count(table))
        for i in range(stop_after):
            if AXTable._get_column_headers_from_table(table, i):
                return True

        return False

    @staticmethod
    def get_cell_coordinates(
        cell: Atspi.Accessible,
        prefer_attribute: bool = True,
        find_cell: bool = False
    ) -> tuple[int, int]:
        """Returns the 0-based row and column indices."""

        if not AXUtilitiesRole.is_table_cell_or_header(cell) and find_cell:
            cell = AXObject.find_ancestor(cell, AXUtilitiesRole.is_table_cell_or_header)

        if not AXUtilitiesRole.is_table_cell_or_header(cell):
            return -1, -1

        if AXObject.supports_table_cell(cell):
            row, col = AXTable._get_cell_coordinates_from_table_cell(cell)
        else:
            row, col = AXTable._get_cell_coordinates_from_table(cell)

        if not prefer_attribute:
            return row, col

        row_index, col_index = AXTable._get_cell_coordinates_from_attribute(cell)
        if row_index is not None:
            row = int(row_index) - 1
        if col_index is not None:
            col = int(col_index) - 1

        return row, col

    @staticmethod
    def _get_cell_coordinates_from_table(cell: Atspi.Accessible) -> tuple[int, int]:
        """Returns the row and column indices of cell via the table interface."""

        if hash(cell) in AXTable.PHYSICAL_COORDINATES_FROM_TABLE:
            return AXTable.PHYSICAL_COORDINATES_FROM_TABLE.get(hash(cell), (-1, -1))

        index = AXTable._get_cell_index(cell)
        if index < 0:
            return -1, -1

        table = AXTable.get_table(cell)
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
        cell: Atspi.Accessible
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
    def get_presentable_sort_order_from_header(
        obj: Atspi.Accessible,
        include_name: bool = False
    ) -> str:
        """Returns the end-user-consumable row/column sort order from its header."""

        if not AXUtilitiesRole.is_table_header(obj):
            return ""

        sort_order = AXObject.get_attribute(obj, "sort", False)
        if not sort_order or sort_order == "none":
            return ""

        if sort_order == "ascending":
            result = object_properties.SORT_ORDER_ASCENDING
        elif sort_order == "descending":
            result = object_properties.SORT_ORDER_DESCENDING
        else:
            result = object_properties.SORT_ORDER_OTHER

        if include_name:
            name = AXObject.get_name(obj)
            if name:
                result = f"{name}. {result}"

        return result

    @staticmethod
    def get_table(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns obj if it is a table, otherwise returns the ancestor table of obj."""

        if obj is None:
            return None

        if AXObject.supports_table_cell(obj):
            try:
                table = Atspi.TableCell.get_table(obj)
            except GLib.GError as error:
                msg = f"AXTable: Exception in get_table: {error}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            else:
                if AXObject.supports_table(table):
                    return table

        def is_table(x):
            if AXUtilitiesRole.is_table(x) \
               or AXUtilitiesRole.is_tree_table(x) or AXUtilitiesRole.is_tree(x):
                return AXObject.supports_table(x)
            return False

        if is_table(obj):
            return obj

        return AXObject.find_ancestor(obj, is_table)

    @staticmethod
    def get_table_description_for_presentation(table: Atspi.Accessible) -> str:
        """Returns an end-user-consumable string which describes the table."""

        if not AXObject.supports_table(table):
            return ""

        result = messages.table_size(AXTable.get_row_count(table), AXTable.get_column_count(table))
        if AXTable.is_non_uniform_table(table):
            result = f"{messages.TABLE_NON_UNIFORM} {result}"
        return result

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
        return AXTable.get_cell_at(AXTable.get_table(cell), row, col)

    @staticmethod
    def get_cell_below(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell below cell in table."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        row += AXTable.get_cell_spans(cell, prefer_attribute=False)[0]
        return AXTable.get_cell_at(AXTable.get_table(cell), row, col)

    @staticmethod
    def get_cell_on_left(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell to the left."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        col -= 1
        return AXTable.get_cell_at(AXTable.get_table(cell), row, col)

    @staticmethod
    def get_cell_on_right(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell to the right."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        col += AXTable.get_cell_spans(cell, prefer_attribute=False)[1]
        return AXTable.get_cell_at(AXTable.get_table(cell), row, col)

    @staticmethod
    def get_start_of_row(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell at the start of cell's row."""

        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        return AXTable.get_cell_at(AXTable.get_table(cell), row, 0)

    @staticmethod
    def get_end_of_row(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell at the end of cell's row."""

        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        table = AXTable.get_table(cell)
        col = AXTable.get_column_count(table) - 1
        return AXTable.get_cell_at(AXTable.get_table(cell), row, col)

    @staticmethod
    def get_top_of_column(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell at the top of cell's column."""

        col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
        return AXTable.get_cell_at(AXTable.get_table(cell), 0, col)

    @staticmethod
    def get_bottom_of_column(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell at the bottom of cell's column."""

        col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
        table = AXTable.get_table(cell)
        row = AXTable.get_row_count(table) - 1
        return AXTable.get_cell_at(AXTable.get_table(cell), row, col)

    @staticmethod
    def get_cell_formula(cell: Atspi.Accessible) -> str | None:
        """Returns the formula associated with this cell."""

        attrs = AXObject.get_attributes_dict(cell, use_cache=False)
        return attrs.get("formula", attrs.get("Formula"))

    @staticmethod
    def is_first_cell(cell: Atspi.Accessible) -> bool:
        """Returns True if this is the first cell in its table."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        return row == 0 and col == 0

    @staticmethod
    def is_last_cell(cell: Atspi.Accessible) -> bool:
        """Returns True if this is the last cell in its table."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        if row < 0 or col < 0:
            return False

        table = AXTable.get_table(cell)
        if table is None:
            return False

        return row + 1 == AXTable.get_row_count(table, prefer_attribute=False) \
            and col + 1 == AXTable.get_column_count(table, prefer_attribute=False)

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

        table = AXTable.get_table(cell)
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

        table = AXTable.get_table(cell)
        if table is None:
            return False

        return row + 1 == AXTable.get_row_count(table, prefer_attribute=False)

    @staticmethod
    def is_layout_table(table: Atspi.Accessible) -> bool:
        """Returns True if this table should be treated as layout only."""

        result, reason = False, "Not enough information"
        attrs = AXObject.get_attributes_dict(table)
        if AXUtilitiesRole.is_table(table):
            if attrs.get("layout-guess") == "true":
                result, reason = True, "The layout-guess attribute is true."
            elif not AXObject.supports_table(table):
                result, reason = True, "Doesn't support table interface."
            elif attrs.get("xml-roles") == "table" or attrs.get("tag") == "table":
                result, reason = False, "Is a web table without layout-guess set to true."
            elif AXTable.has_column_headers(table) or AXTable.has_row_headers(table):
                result, reason = False, "Has headers"
            elif AXObject.get_name(table) or AXObject.get_description(table):
                result, reason = False, "Has name or description"
            elif AXTable.get_caption(table):
                result, reason = False, "Has caption"

        tokens = ["AXTable:", table, f"is layout only: {result} ({reason})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_label_for_cell_coordinates(cell: Atspi.Accessible) -> str:
        """Returns the text that should be used instead of the numeric indices."""

        if hash(cell) in AXTable.PRESENTABLE_COORDINATES_LABELS:
            return AXTable.PRESENTABLE_COORDINATES_LABELS.get(hash(cell), "")

        attrs = AXObject.get_attributes_dict(cell)
        result = ""

        # The attribute officially has the word "index" in it for clarity.
        # TODO - JD: Google Sheets needs to start using the correct attribute name.
        col_label = attrs.get("colindextext", attrs.get("coltext"))
        row_label = attrs.get("rowindextext", attrs.get("rowtext"))
        if col_label is not None and row_label is not None:
            result = f"{col_label}{row_label}"

        tokens = ["AXTable: Coordinates label for", cell, f": {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PRESENTABLE_COORDINATES_LABELS[hash(cell)] = result
        if result:
            return result

        row = AXObject.find_ancestor(cell, AXUtilitiesRole.is_table_row)
        if row is None:
            return result

        attrs = AXObject.get_attributes_dict(row)
        col_label = attrs.get("colindextext", attrs.get("coltext", col_label))
        row_label = attrs.get("rowindextext", attrs.get("rowtext", row_label))
        if col_label is not None and row_label is not None:
            result = f"{col_label}{row_label}"

        tokens = ["AXTable: Updated coordinates label based on", row, f": {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        AXTable.PRESENTABLE_COORDINATES_LABELS[hash(cell)] = result
        return result

    @staticmethod
    def get_dynamic_row_header(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the user-set row header for cell."""

        table = AXTable.get_table(cell)
        headers_column = AXTable.DYNAMIC_ROW_HEADERS_COLUMN.get(hash(table))
        if headers_column is None:
            return None

        cell_row, cell_column = AXTable.get_cell_coordinates(cell)
        if cell_column == headers_column:
            return None

        return AXTable.get_cell_at(table, cell_row, headers_column)

    @staticmethod
    def get_dynamic_column_header(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the user-set column header for cell."""

        table = AXTable.get_table(cell)
        headers_row = AXTable.DYNAMIC_COLUMN_HEADERS_ROW.get(hash(table))
        if headers_row is None:
            return None

        cell_row, cell_column = AXTable.get_cell_coordinates(cell)
        if cell_row == headers_row:
            return None

        return AXTable.get_cell_at(table, headers_row, cell_column)

    @staticmethod
    def set_dynamic_row_headers_column(table: Atspi.Accessible, column: int) -> None:
        """Sets the dynamic row headers column of table to column."""

        AXTable.DYNAMIC_ROW_HEADERS_COLUMN[hash(table)] = column

    @staticmethod
    def set_dynamic_column_headers_row(table: Atspi.Accessible, row: int) -> None:
        """Sets the dynamic column headers row of table to row."""

        AXTable.DYNAMIC_COLUMN_HEADERS_ROW[hash(table)] = row

    @staticmethod
    def clear_dynamic_row_headers_column(table: Atspi.Accessible) -> None:
        """Clears the dynamic row headers column of table."""

        if hash(table) not in AXTable.DYNAMIC_ROW_HEADERS_COLUMN:
            return

        AXTable.DYNAMIC_ROW_HEADERS_COLUMN.pop(hash(table))

    @staticmethod
    def clear_dynamic_column_headers_row(table: Atspi.Accessible) -> None:
        """Clears the dynamic column headers row of table."""

        if hash(table) not in AXTable.DYNAMIC_COLUMN_HEADERS_ROW:
            return

        AXTable.DYNAMIC_COLUMN_HEADERS_ROW.pop(hash(table))

    @staticmethod
    def _get_visible_cell_range(table: Atspi.Accessible) -> tuple[tuple[int, int], tuple[int, int]]:
        """Returns the (row, col) of the first and last visible cells in table."""

        if not AXObject.supports_table(table):
            return (-1, -1), (-1, -1)

        rect = AXComponent.get_rect(table)
        tokens = ["AXTable: Rect for", table, "is", rect]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        first_cell = AXComponent.get_descendant_at_point(table, rect.x + 1, rect.y + 1)
        tokens = ["AXTable: First visible cell for", table, "is", first_cell]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        start = AXTable.get_cell_coordinates(first_cell, prefer_attribute=False)
        tokens = ["AXTable: First visible cell is at row", start[0], "column", start[1]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        last_cell = AXComponent.get_descendant_at_point(
            table, rect.x + rect.width - 1, rect.y + rect.height - 1)
        tokens = ["AXTable: Last visible cell for", table, "is", last_cell]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        end = AXTable.get_cell_coordinates(last_cell, prefer_attribute=False)
        tokens = ["AXTable: Last visible cell is at row", end[0], "column", end[1]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if end == (-1, -1):
            last_cell = AXTable.get_last_cell(table)
            tokens = ["AXTable: Adjusted lasat visible cell for", table, "is", last_cell]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            end = AXTable.get_cell_coordinates(last_cell, prefer_attribute=False)
            tokens = ["AXTable: Adjusted last cell is at row", end[0], "column", end[1]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXUtilitiesRole.is_table_cell(last_cell) \
           and not AXUtilitiesRole.is_table_cell_or_header(first_cell):
            candidate = AXTable.get_cell_above(last_cell)
            while candidate and AXComponent.object_intersects_rect(candidate, rect):
                first_cell = candidate
                candidate = AXTable.get_cell_above(first_cell)

            candidate = AXTable.get_cell_on_left(first_cell)
            while candidate and AXComponent.object_intersects_rect(candidate, rect):
                first_cell = candidate
                candidate = AXTable.get_cell_on_left(first_cell)

            tokens = ["AXTable: Adjusted first visible cell for", table, "is", first_cell]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            start = AXTable.get_cell_coordinates(first_cell, prefer_attribute=False)
            tokens = ["AXTable: Adjusted first cell is at row", start[0], "column", start[1]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return start, end

    @staticmethod
    def iter_visible_cells(table: Atspi.Accessible) -> Generator[Atspi.Accessible, None, None]:
        """Yields the visible cells in table."""

        start, end = AXTable._get_visible_cell_range(table)
        if start[0] < 0 or start[1] < 0 or end[0] < 0 or end[1] < 0:
            return

        for row in range(start[0], end[0] + 1):
            for col in range(start[1], end[1] + 1):
                cell = AXTable.get_cell_at(table, row, col)
                if cell is None:
                    continue
                for child in AXObject.iter_children(cell, AXUtilitiesRole.is_table_cell):
                    if AXObject.get_name(child):
                        cell = child
                        break
                yield cell

    @staticmethod
    def get_showing_cells_in_same_row(
        cell: Atspi.Accessible,
        clip_to_window: bool = False
    ) -> list[Atspi.Accessible]:
        """Returns a list of all the cells in the same row as obj that are showing."""

        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        if row == -1:
            return []

        table = AXTable.get_table(cell)
        start_index, end_index = 0, AXTable.get_column_count(table, False)
        if clip_to_window:
            rect = AXComponent.get_rect(table)
            if (cell := AXComponent.get_descendant_at_point(table, rect.x + 1, rect.y)):
                start_index = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
            if (cell := AXComponent.get_descendant_at_point(
                    table, rect.x + rect.width - 1, rect.y)):
                end_index = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1] + 1

        if start_index == end_index:
            return []

        cells = []
        for i in range(start_index, end_index):
            cell = AXTable.get_cell_at(table, row, i)
            if AXUtilitiesState.is_showing(cell):
                cells.append(cell)

        if not cells:
            tokens = ["AXTable: No visible cells found in row with", cell]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        tokens = ["AXTable: First visible cell in row with", cell, "is", cells[0]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        tokens = ["AXTable: Last visible cell in row with", cell, "is", cells[-1]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return cells


AXTable.start_cache_clearing_thread()
