# Orca
#
# Copyright 2010 Joanmarie Diggs.
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

# pylint: disable=too-many-branches

"""Custom script utilities for LibreOffice"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import debug
from orca import focus_manager
from orca import input_event_manager
from orca import messages
from orca import script_utilities
from orca.ax_object import AXObject
from orca.ax_selection import AXSelection
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Utilities(script_utilities.Utilities):
    """Custom script utilities for LibreOffice"""

    def __init__(self, script) -> None:
        super().__init__(script)
        self._calc_selected_cells: list[tuple[int, int]] = []
        self._calc_selected_rows: list[int] = []
        self._calc_selected_columns: list[int] = []

    def is_cell_being_edited(self, obj: Atspi.Accessible) -> str | bool:
        """Returns True if obj is a cell being edited."""

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_panel(parent) or AXUtilities.is_extended(parent):
            return self.spreadsheet_cell_name(parent)

        return False

    def spreadsheet_cell_name(self, cell: Atspi.Accessible) -> str:
        """Returns the accessible name of the cell."""

        # TODO - JD: Is this still needed? See also _get_cell_name_for_coordinates.
        name_list = AXObject.get_name(cell).split()
        for name in name_list:
            name = name.replace('.', '')
            if not name.isalpha() and name.isalnum():
                return name

        return ''

    def _get_cell_name_for_coordinates(
        self,
        obj: Atspi.Accessible,
        row: int,
        col: int,
        include_contents: bool = False
    ) -> str:
        # https://bugs.documentfoundation.org/show_bug.cgi?id=158030
        cell = AXTable.get_cell_at(obj, row, col)
        name = self.spreadsheet_cell_name(cell)
        if include_contents:
            text = AXText.get_all_text(cell)
            name = f"{text} {name}"

        return name.strip()

    def get_word_at_offset_adjusted_for_navigation(
        self,
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the word in obj at the specified or current offset."""

        if self._script.get_caret_navigator().last_input_event_was_navigation_command():
            return super().get_word_at_offset_adjusted_for_navigation(obj, offset)

        return AXText.get_word_at_offset(obj, offset)

    def should_read_full_row(
        self,
        obj: Atspi.Accessible,
        previous_object: Atspi.Accessible | None = None
    ) -> bool:
        """Returns True if the full row in obj should be read."""

        if self._script.get_table_navigator().last_input_event_was_navigation_command():
            return False

        if input_event_manager.get_manager().last_event_was_tab_navigation():
            return False

        return super().should_read_full_row(obj, previous_object)

    def _is_top_level_object(self, obj: Atspi.Accessible) -> bool:
        # https://bugs.documentfoundation.org/show_bug.cgi?id=160806
        if AXObject.get_parent(obj) is None and AXObject.get_role(obj) in self._top_level_roles():
            tokens = ["SOFFICE:", obj, "has no parent. Treating as top-level."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            return True

        return super()._is_top_level_object(obj)

    def convert_column_to_string(self, column: int):
        """Converts a column index to a string representation."""

        base26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        if column <= len(base26):
            return base26[column-1]

        res = ""
        while column > 0:
            digit = column % len(base26)
            res = " " + base26[digit-1] + res
            column = int(column / len(base26))

        return res

    def _get_coordinates_for_selected_range(
        self,
        obj: Atspi.Accessible
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        if not (AXObject.supports_table(obj) and AXObject.supports_selection(obj)):
            tokens = ["SOFFICE:", obj, "does not implement both selection and table"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return (-1, -1), (-1, -1)

        first = AXSelection.get_selected_child(obj, 0)
        last = AXSelection.get_selected_child(obj, -1)
        return AXTable.get_cell_coordinates(first), AXTable.get_cell_coordinates(last)

    def speak_selected_cell_range(self, obj: Atspi.Accessible) -> bool:
        """Speaks the selected cell range."""

        first_coords, last_coords = self._get_coordinates_for_selected_range(obj)
        if first_coords == (-1, -1) or last_coords == (-1, -1):
            return False

        self._script.interrupt_presentation()

        if first_coords == last_coords:
            cell = self._get_cell_name_for_coordinates(obj, *first_coords, True)
            self._script.speak_message(messages.CELL_SELECTED % cell)
            return True

        cell1 = self._get_cell_name_for_coordinates(obj, *first_coords, True)
        cell2 = self._get_cell_name_for_coordinates(obj, *last_coords, True)
        self._script.speak_message(messages.CELL_RANGE_SELECTED % (cell1, cell2))
        return True

    # pylint: disable-next=too-many-locals
    def handle_cell_selection_change(self, obj: Atspi.Accessible) -> bool:
        """Presents the selection change for obj."""

        first_coords, last_coords = self._get_coordinates_for_selected_range(obj)
        if first_coords == (-1, -1) or last_coords == (-1, -1):
            return True

        current_list: list[tuple[int, int]] = []
        for r in range(first_coords[0], last_coords[0]+1):
            current_list.extend((r, c) for c in range(first_coords[1], last_coords[1]+1))

        current = set(current_list)
        previous = set(self._calc_selected_cells)
        current.discard((-1, -1))
        previous.discard((-1, -1))

        unselected = sorted(previous.difference(current))
        selected = sorted(current.difference(previous))
        focus_coords = AXTable.get_cell_coordinates(
            focus_manager.get_manager().get_locus_of_focus())
        if focus_coords in selected:
            selected.remove(focus_coords)

        self._calc_selected_cells = sorted(current)

        msgs = []
        if len(unselected) == 1:
            cell = self._get_cell_name_for_coordinates(obj, *unselected[0], include_contents=True)
            msgs.append(messages.CELL_UNSELECTED % cell)
        elif len(unselected) > 1:
            cell1 = self._get_cell_name_for_coordinates(obj, *unselected[0], include_contents=True)
            cell2 = self._get_cell_name_for_coordinates(obj, *unselected[-1], include_contents=True)
            msgs.append(messages.CELL_RANGE_UNSELECTED % (cell1, cell2))

        if len(selected) == 1:
            cell = self._get_cell_name_for_coordinates(obj, *selected[0], include_contents=True)
            msgs.append(messages.CELL_SELECTED % cell)
        elif len(selected) > 1:
            cell1 = self._get_cell_name_for_coordinates(obj, *selected[0], include_contents=True)
            cell2 = self._get_cell_name_for_coordinates(obj, *selected[-1], include_contents=True)
            msgs.append(messages.CELL_RANGE_SELECTED % (cell1, cell2))

        if msgs:
            self._script.interrupt_presentation()

        for msg in msgs:
            self._script.speak_message(msg, interrupt=False)

        return bool(msgs)

    def handle_row_and_column_selection_change(
        self,
        obj: Atspi.Accessible
    ) -> bool:
        """Presents the selection change for obj."""

        if not (AXObject.supports_table(obj) and AXObject.supports_selection(obj)):
            return True

        cols = set(AXTable.get_selected_columns(obj))
        rows = set(AXTable.get_selected_rows(obj))

        selected_cols = sorted(cols.difference(set(self._calc_selected_columns)))
        unselected_cols = sorted(set(self._calc_selected_columns).difference(cols))

        def convert_column(x):
            return self.convert_column_to_string(x+1)

        def convert_row(x):
            return x + 1

        selected_cols = list(map(convert_column, selected_cols))
        unselected_cols = list(map(convert_column, unselected_cols))

        selected_rows = sorted(rows.difference(set(self._calc_selected_rows)))
        unselected_rows = sorted(set(self._calc_selected_rows).difference(rows))

        selected_rows = list(map(convert_row, selected_rows))
        unselected_rows = list(map(convert_row, unselected_rows))

        self._calc_selected_columns = list(cols)
        self._calc_selected_rows = list(rows)

        column_count = AXTable.get_column_count(obj)
        if len(cols) == column_count:
            self._script.speak_message(messages.DOCUMENT_SELECTED_ALL)
            return True

        if not cols and len(unselected_cols) == column_count:
            self._script.speak_message(messages.DOCUMENT_UNSELECTED_ALL)
            return True

        msgs = []
        if len(unselected_cols) == 1:
            msgs.append(messages.TABLE_COLUMN_UNSELECTED % unselected_cols[0])
        elif len(unselected_cols) > 1:
            msgs.append(messages.TABLE_COLUMN_RANGE_UNSELECTED % \
                        (unselected_cols[0], unselected_cols[-1]))

        if len(unselected_rows) == 1:
            msgs.append(messages.TABLE_ROW_UNSELECTED % unselected_rows[0])
        elif len(unselected_rows) > 1:
            msgs.append(messages.TABLE_ROW_RANGE_UNSELECTED % \
                        (unselected_rows[0], unselected_rows[-1]))

        if len(selected_cols) == 1:
            msgs.append(messages.TABLE_COLUMN_SELECTED % selected_cols[0])
        elif len(selected_cols) > 1:
            msgs.append(
                messages.TABLE_COLUMN_RANGE_SELECTED % (selected_cols[0], selected_cols[-1]))

        if len(selected_rows) == 1:
            msgs.append(messages.TABLE_ROW_SELECTED % selected_rows[0])
        elif len(selected_rows) > 1:
            msgs.append(messages.TABLE_ROW_RANGE_SELECTED % (selected_rows[0], selected_rows[-1]))

        if msgs:
            self._script.interrupt_presentation()

        for msg in msgs:
            self._script.speak_message(msg, interrupt=False)

        return bool(msgs)
