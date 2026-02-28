# Orca
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

"""Utilities for accessible tables."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import debug, messages, object_properties
from .ax_component import AXComponent
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_utilities_component import AXUtilitiesComponent
from .ax_utilities_object import AXUtilitiesObject
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import ClassVar

    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class AXUtilitiesTable:
    """Utilities for accessible tables."""

    DYNAMIC_COLUMN_HEADERS_ROW: ClassVar[dict[int, int]] = {}
    DYNAMIC_ROW_HEADERS_COLUMN: ClassVar[dict[int, int]] = {}

    @staticmethod
    def _is_table_with_interface(obj: Atspi.Accessible) -> bool:
        """Returns True if obj has a table-like role and supports the table interface."""

        if (
            AXUtilitiesRole.is_table(obj)
            or AXUtilitiesRole.is_tree_table(obj)
            or AXUtilitiesRole.is_tree(obj)
        ):
            return AXObject.supports_table(obj)
        return False

    @staticmethod
    def get_table(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns obj if it is a table, otherwise returns the ancestor table of obj."""

        if obj is None:
            return None

        table = AXTable.get_table_from_table_cell(obj)
        if table is not None:
            return table

        return AXUtilitiesObject.find_ancestor_inclusive(
            obj, AXUtilitiesTable._is_table_with_interface
        )

    @staticmethod
    def get_new_row_headers(
        cell: Atspi.Accessible,
        old_cell: Atspi.Accessible | None,
    ) -> list[Atspi.Accessible]:
        """Returns row headers of cell that are not also headers of old_cell."""

        if old_cell and not AXUtilitiesRole.is_table_cell_or_header(old_cell):
            old_cell = AXUtilitiesObject.find_ancestor(
                old_cell, AXUtilitiesRole.is_table_cell_or_header
            )

        headers = AXUtilitiesTable.get_row_headers(cell)
        if old_cell is None:
            return headers

        old_headers = AXUtilitiesTable.get_row_headers(old_cell)
        return list(set(headers).difference(set(old_headers)))

    @staticmethod
    def get_new_column_headers(
        cell: Atspi.Accessible,
        old_cell: Atspi.Accessible | None,
    ) -> list[Atspi.Accessible]:
        """Returns column headers of cell that are not also headers of old_cell."""

        if old_cell and not AXUtilitiesRole.is_table_cell_or_header(old_cell):
            old_cell = AXUtilitiesObject.find_ancestor(
                old_cell, AXUtilitiesRole.is_table_cell_or_header
            )

        headers = AXUtilitiesTable.get_column_headers(cell)
        if old_cell is None:
            return headers

        old_headers = AXUtilitiesTable.get_column_headers(old_cell)
        return list(set(headers).difference(set(old_headers)))

    @staticmethod
    def get_row_headers(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the row headers for cell, doing extra work to ensure we have them all."""

        if not AXUtilitiesRole.is_table_cell(cell):
            return []

        dynamic_header = AXUtilitiesTable.get_dynamic_row_header(cell)
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

        result = AXUtilitiesTable._get_row_headers(cell)
        if len(result) != 1:
            return result

        others = AXUtilitiesTable._get_row_headers(result[0])
        while len(others) == 1 and others[0] not in result:
            result.insert(0, others[0])
            others = AXUtilitiesTable._get_row_headers(result[0])

        return result

    @staticmethod
    def _get_row_headers(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the row headers for cell."""

        if AXObject.supports_table_cell(cell):
            return AXTable.get_row_headers_from_table_cell(cell)

        row, column = AXTable.get_cell_coordinates_from_table(cell)
        if row < 0 or column < 0:
            return []

        table = AXUtilitiesTable.get_table(cell)
        if table is None:
            return []

        headers = []
        rowspan = AXTable.get_cell_spans_from_table(cell)[0]
        for index in range(row, row + rowspan):
            headers.extend(AXTable.get_row_headers_from_table(table, index))

        return headers

    @staticmethod
    def has_row_headers(table: Atspi.Accessible, stop_after: int = 10) -> bool:
        """Returns True if table has any headers for rows 0-stop_after."""

        if not AXObject.supports_table(table):
            return False

        stop_after = min(stop_after + 1, AXTable.get_row_count(table))
        return any(AXTable.get_row_headers_from_table(table, i) for i in range(stop_after))

    @staticmethod
    def get_column_headers(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the column headers for cell, doing extra work to ensure we have them all."""

        if not AXUtilitiesRole.is_table_cell(cell):
            return []

        dynamic_header = AXUtilitiesTable.get_dynamic_column_header(cell)
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

        result = AXUtilitiesTable._get_column_headers(cell)
        if len(result) != 1:
            return result

        others = AXUtilitiesTable._get_column_headers(result[0])
        while len(others) == 1 and others[0] not in result:
            result.insert(0, others[0])
            others = AXUtilitiesTable._get_column_headers(result[0])

        return result

    @staticmethod
    def _get_column_headers(cell: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the column headers for cell."""

        if AXObject.supports_table_cell(cell):
            return AXTable.get_column_headers_from_table_cell(cell)

        row, column = AXTable.get_cell_coordinates_from_table(cell)
        if row < 0 or column < 0:
            return []

        table = AXUtilitiesTable.get_table(cell)
        if table is None:
            return []

        headers = []
        colspan = AXTable.get_cell_spans_from_table(cell)[1]
        for index in range(column, column + colspan):
            headers.extend(AXTable.get_column_headers_from_table(table, index))

        return headers

    @staticmethod
    def has_column_headers(table: Atspi.Accessible, stop_after: int = 10) -> bool:
        """Returns True if table has any headers for columns 0-stop_after."""

        if not AXObject.supports_table(table):
            return False

        stop_after = min(stop_after + 1, AXTable.get_column_count(table))
        return any(AXTable.get_column_headers_from_table(table, i) for i in range(stop_after))

    @staticmethod
    def get_presentable_sort_order_from_header(
        obj: Atspi.Accessible,
        include_name: bool = False,
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
    def get_table_description_for_presentation(table: Atspi.Accessible) -> str:
        """Returns an end-user-consumable string which describes the table."""

        if not AXObject.supports_table(table):
            return ""

        result = messages.table_size(AXTable.get_row_count(table), AXTable.get_column_count(table))
        if AXTable.is_non_uniform_table(table):
            result = f"{messages.TABLE_NON_UNIFORM} {result}"
        return result

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
            elif AXUtilitiesTable.has_column_headers(table) or AXUtilitiesTable.has_row_headers(
                table,
            ):
                result, reason = False, "Has headers"
            elif AXObject.get_name(table) or AXObject.get_description(table):
                result, reason = False, "Has name or description"
            elif AXTable.get_caption(table):
                result, reason = False, "Has caption"

        tokens = ["AXUtilitiesTable:", table, f"is layout only: {result} ({reason})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def is_text_document_table(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a text document table (i.e. not a spreadsheet or GUI table)."""

        if not AXUtilitiesRole.is_table(obj):
            return False

        doc = AXUtilitiesObject.find_ancestor_inclusive(obj, AXUtilitiesRole.is_document)
        return doc is not None and not AXUtilitiesRole.is_document_spreadsheet(doc)

    @staticmethod
    def is_gui_table(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a GUI table."""

        return (
            AXUtilitiesRole.is_table(obj)
            and AXUtilitiesObject.find_ancestor_inclusive(obj, AXUtilitiesRole.is_document) is None
        )

    @staticmethod
    def is_spreadsheet_table(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a spreadsheet table."""

        if not (AXUtilitiesRole.is_table(obj) and AXObject.supports_table(obj)):
            return False

        doc = AXUtilitiesObject.find_ancestor_inclusive(obj, AXUtilitiesRole.is_document)
        if doc is None:
            return False
        if AXUtilitiesRole.is_document_spreadsheet(doc):
            return True

        return AXTable.get_row_count(obj) > 65536

    @staticmethod
    def is_text_document_cell(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a cell in a text document table."""

        if not AXUtilitiesRole.is_table_cell_or_header(obj):
            return False
        return (
            AXUtilitiesObject.find_ancestor(obj, AXUtilitiesTable.is_text_document_table)
            is not None
        )

    @staticmethod
    def is_gui_cell(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a cell in a GUI table."""

        if not AXUtilitiesRole.is_table_cell_or_header(obj):
            return False
        return AXUtilitiesObject.find_ancestor(obj, AXUtilitiesTable.is_gui_table) is not None

    @staticmethod
    def is_spreadsheet_cell(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a cell in a spreadsheet table."""

        if not AXUtilitiesRole.is_table_cell_or_header(obj):
            return False
        return (
            AXUtilitiesObject.find_ancestor(obj, AXUtilitiesTable.is_spreadsheet_table) is not None
        )

    @staticmethod
    def cell_column_changed(
        cell: Atspi.Accessible,
        prior_cell: Atspi.Accessible | None = None,
    ) -> bool:
        """Returns True if the column of cell has changed since prior_cell."""

        column = AXTable.get_cell_coordinates(cell)[1]
        if column == -1:
            return False

        if prior_cell is None:
            _last_row, last_column = AXTable.get_last_cell_coordinates()
        else:
            last_column = AXTable.get_cell_coordinates(prior_cell)[1]

        return column != last_column

    @staticmethod
    def cell_row_changed(
        cell: Atspi.Accessible,
        prior_cell: Atspi.Accessible | None = None,
    ) -> bool:
        """Returns True if the row of cell has changed since prior_cell."""

        row = AXTable.get_cell_coordinates(cell)[0]
        if row == -1:
            return False

        if prior_cell is None:
            last_row, _last_column = AXTable.get_last_cell_coordinates()
        else:
            last_row = AXTable.get_cell_coordinates(prior_cell)[0]
        return row != last_row

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

        table = AXUtilitiesTable.get_table(cell)
        if table is None:
            return False

        return row + 1 == AXTable.get_row_count(
            table,
            prefer_attribute=False,
        ) and col + 1 == AXTable.get_column_count(table, prefer_attribute=False)

    @staticmethod
    def get_label_for_cell_coordinates(cell: Atspi.Accessible) -> str:
        """Returns the text that should be used instead of the numeric indices."""

        attrs = AXObject.get_attributes_dict(cell)
        result = ""

        # The attribute officially has the word "index" in it for clarity.
        # TODO - JD: Google Sheets needs to start using the correct attribute name.
        col_label = attrs.get("colindextext", attrs.get("coltext"))
        row_label = attrs.get("rowindextext", attrs.get("rowtext"))
        if col_label is not None and row_label is not None:
            result = f"{col_label}{row_label}"

        tokens = ["AXUtilitiesTable: Coordinates label for", cell, f": {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if result:
            return result

        row = AXUtilitiesObject.find_ancestor(cell, AXUtilitiesRole.is_table_row)
        if row is None:
            return result

        attrs = AXObject.get_attributes_dict(row)
        col_label = attrs.get("colindextext", attrs.get("coltext", col_label))
        row_label = attrs.get("rowindextext", attrs.get("rowtext", row_label))
        if col_label is not None and row_label is not None:
            result = f"{col_label}{row_label}"

        tokens = ["AXUtilitiesTable: Updated coordinates label based on", row, f": {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_dynamic_row_header(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the user-set row header for cell."""

        table = AXUtilitiesTable.get_table(cell)
        headers_column = AXUtilitiesTable.DYNAMIC_ROW_HEADERS_COLUMN.get(hash(table))
        if headers_column is None:
            return None

        cell_row, cell_column = AXTable.get_cell_coordinates(cell)
        if cell_column == headers_column:
            return None

        return AXTable.get_cell_at(table, cell_row, headers_column)

    @staticmethod
    def get_dynamic_column_header(cell: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the user-set column header for cell."""

        table = AXUtilitiesTable.get_table(cell)
        headers_row = AXUtilitiesTable.DYNAMIC_COLUMN_HEADERS_ROW.get(hash(table))
        if headers_row is None:
            return None

        cell_row, cell_column = AXTable.get_cell_coordinates(cell)
        if cell_row == headers_row:
            return None

        return AXTable.get_cell_at(table, headers_row, cell_column)

    @staticmethod
    def set_dynamic_row_headers_column(table: Atspi.Accessible, column: int) -> None:
        """Sets the dynamic row headers column of table to column."""

        AXUtilitiesTable.DYNAMIC_ROW_HEADERS_COLUMN[hash(table)] = column

    @staticmethod
    def set_dynamic_column_headers_row(table: Atspi.Accessible, row: int) -> None:
        """Sets the dynamic column headers row of table to row."""

        AXUtilitiesTable.DYNAMIC_COLUMN_HEADERS_ROW[hash(table)] = row

    @staticmethod
    def clear_dynamic_row_headers_column(table: Atspi.Accessible) -> None:
        """Clears the dynamic row headers column of table."""

        if hash(table) not in AXUtilitiesTable.DYNAMIC_ROW_HEADERS_COLUMN:
            return

        AXUtilitiesTable.DYNAMIC_ROW_HEADERS_COLUMN.pop(hash(table))

    @staticmethod
    def clear_dynamic_column_headers_row(table: Atspi.Accessible) -> None:
        """Clears the dynamic column headers row of table."""

        if hash(table) not in AXUtilitiesTable.DYNAMIC_COLUMN_HEADERS_ROW:
            return

        AXUtilitiesTable.DYNAMIC_COLUMN_HEADERS_ROW.pop(hash(table))

    @staticmethod
    def _get_visible_cell_range(
        table: Atspi.Accessible,
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """Returns the (row, col) of the first and last visible cells in table."""

        if not AXObject.supports_table(table):
            return (-1, -1), (-1, -1)

        rect = AXComponent.get_rect(table)
        tokens = ["AXUtilitiesTable: Rect for", table, "is", rect]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        first_cell = AXUtilitiesComponent.get_descendant_at_point(table, rect.x + 1, rect.y + 1)
        tokens = ["AXUtilitiesTable: First visible cell for", table, "is", first_cell]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        start = AXTable.get_cell_coordinates(first_cell, prefer_attribute=False)
        tokens = ["AXUtilitiesTable: First visible cell is at row", start[0], "column", start[1]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        last_cell = AXUtilitiesComponent.get_descendant_at_point(
            table,
            rect.x + rect.width - 1,
            rect.y + rect.height - 1,
        )
        tokens = ["AXUtilitiesTable: Last visible cell for", table, "is", last_cell]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        end = AXTable.get_cell_coordinates(last_cell, prefer_attribute=False)
        tokens = ["AXUtilitiesTable: Last visible cell is at row", end[0], "column", end[1]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if end == (-1, -1):
            last_cell = AXTable.get_last_cell(table)
            tokens = ["AXUtilitiesTable: Adjusted last visible cell for", table, "is", last_cell]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            end = AXTable.get_cell_coordinates(last_cell, prefer_attribute=False)
            tokens = ["AXUtilitiesTable: Adjusted last cell is at row", end[0], "column", end[1]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXUtilitiesRole.is_table_cell(last_cell) and not AXUtilitiesRole.is_table_cell_or_header(
            first_cell,
        ):
            candidate = AXTable.get_cell_above(last_cell)
            while candidate and AXUtilitiesComponent.object_intersects_rect(candidate, rect):
                first_cell = candidate
                candidate = AXTable.get_cell_above(first_cell)

            candidate = AXTable.get_cell_on_left(first_cell)
            while candidate and AXUtilitiesComponent.object_intersects_rect(candidate, rect):
                first_cell = candidate
                candidate = AXTable.get_cell_on_left(first_cell)

            tokens = ["AXUtilitiesTable: Adjusted first visible cell for", table, "is", first_cell]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            start = AXTable.get_cell_coordinates(first_cell, prefer_attribute=False)
            tokens = [
                "AXUtilitiesTable: Adjusted first cell is at row",
                start[0],
                "column",
                start[1],
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return start, end

    @staticmethod
    def iter_visible_cells(
        table: Atspi.Accessible,
    ) -> Generator[Atspi.Accessible, None, None]:
        """Yields the visible cells in table."""

        start, end = AXUtilitiesTable._get_visible_cell_range(table)
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
        clip_to_window: bool = False,
    ) -> list[Atspi.Accessible]:
        """Returns a list of all the cells in the same row as obj that are showing."""

        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        if row == -1:
            return []

        table = AXUtilitiesTable.get_table(cell)
        start_index, end_index = 0, AXTable.get_column_count(table, False)
        if clip_to_window:
            rect = AXComponent.get_rect(table)
            if cell := AXUtilitiesComponent.get_descendant_at_point(table, rect.x + 1, rect.y):
                start_index = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
            if cell := AXUtilitiesComponent.get_descendant_at_point(
                table, rect.x + rect.width - 1, rect.y
            ):
                end_index = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1] + 1

        if start_index == end_index:
            return []

        cells = []
        for i in range(start_index, end_index):
            cell = AXTable.get_cell_at(table, row, i)
            if AXUtilitiesState.is_showing(cell):
                cells.append(cell)

        if not cells:
            tokens = ["AXUtilitiesTable: No visible cells found in row with", cell]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        tokens = ["AXUtilitiesTable: First visible cell in row with", cell, "is", cells[0]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        tokens = ["AXUtilitiesTable: Last visible cell in row with", cell, "is", cells[-1]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return cells
