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

"""Custom script utilities for LibreOffice"""

from __future__ import annotations

from typing import TYPE_CHECKING

from orca import (
    caret_navigator,
    debug,
    focus_manager,
    messages,
    presentation_manager,
    script_utilities,
)
from orca.ax_object import AXObject
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
            return AXObject.get_name(parent)

        return False

    def get_word_at_offset_adjusted_for_navigation(
        self,
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> tuple[str, int, int]:
        """Returns the word in obj at the specified or current offset."""

        if caret_navigator.get_navigator().last_input_event_was_navigation_command():
            return super().get_word_at_offset_adjusted_for_navigation(obj, offset)

        return AXText.get_word_at_offset(obj, offset)

    def _is_top_level_object(self, obj: Atspi.Accessible) -> bool:
        # https://bugs.documentfoundation.org/show_bug.cgi?id=160806
        if AXObject.get_parent(obj) is None and AXObject.get_role(obj) in self._top_level_roles():
            tokens = ["SOFFICE:", obj, "has no parent. Treating as top-level."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            return True

        return super()._is_top_level_object(obj)

    def speak_selected_cell_range(self, obj: Atspi.Accessible) -> bool:
        """Speaks the selected cell range."""

        first_coords, last_coords = AXUtilities.get_selected_cell_coordinates_range(obj)
        if first_coords == (-1, -1) or last_coords == (-1, -1):
            return False

        presentation_manager.get_manager().interrupt_presentation()

        if first_coords == last_coords:
            cell = AXUtilities.get_cell_name_for_coordinates(obj, *first_coords, True)
            presentation_manager.get_manager().speak_message(messages.CELL_SELECTED % cell)
            return True

        cell1 = AXUtilities.get_cell_name_for_coordinates(obj, *first_coords, True)
        cell2 = AXUtilities.get_cell_name_for_coordinates(obj, *last_coords, True)
        presentation_manager.get_manager().speak_message(
            messages.CELL_RANGE_SELECTED % (cell1, cell2),
        )
        return True

    # pylint: disable-next=too-many-locals
    def handle_cell_selection_change(self, obj: Atspi.Accessible) -> bool:
        """Presents the selection change for obj."""

        first_coords, last_coords = AXUtilities.get_selected_cell_coordinates_range(obj)
        if first_coords == (-1, -1) or last_coords == (-1, -1):
            return True

        current_list: list[tuple[int, int]] = []
        for r in range(first_coords[0], last_coords[0] + 1):
            current_list.extend((r, c) for c in range(first_coords[1], last_coords[1] + 1))

        current = set(current_list)
        previous = set(self._calc_selected_cells)
        current.discard((-1, -1))
        previous.discard((-1, -1))

        unselected = sorted(previous.difference(current))
        selected = sorted(current.difference(previous))
        focus_coords = AXTable.get_cell_coordinates(
            focus_manager.get_manager().get_locus_of_focus(),
        )
        if focus_coords in selected:
            selected.remove(focus_coords)

        self._calc_selected_cells = sorted(current)

        msgs = []
        if len(unselected) == 1:
            cell = AXUtilities.get_cell_name_for_coordinates(
                obj, *unselected[0], include_contents=True
            )
            msgs.append(messages.CELL_UNSELECTED % cell)
        elif len(unselected) > 1:
            cell1 = AXUtilities.get_cell_name_for_coordinates(
                obj, *unselected[0], include_contents=True
            )
            cell2 = AXUtilities.get_cell_name_for_coordinates(
                obj, *unselected[-1], include_contents=True
            )
            msgs.append(messages.CELL_RANGE_UNSELECTED % (cell1, cell2))

        if len(selected) == 1:
            cell = AXUtilities.get_cell_name_for_coordinates(
                obj, *selected[0], include_contents=True
            )
            msgs.append(messages.CELL_SELECTED % cell)
        elif len(selected) > 1:
            cell1 = AXUtilities.get_cell_name_for_coordinates(
                obj, *selected[0], include_contents=True
            )
            cell2 = AXUtilities.get_cell_name_for_coordinates(
                obj, *selected[-1], include_contents=True
            )
            msgs.append(messages.CELL_RANGE_SELECTED % (cell1, cell2))

        if msgs:
            presentation_manager.get_manager().interrupt_presentation()

        for msg in msgs:
            presentation_manager.get_manager().speak_message(msg)

        return bool(msgs)

    @staticmethod
    def _build_selection_change_messages(
        selected: list,
        unselected: list,
        selected_msgs: tuple[str, str],
        unselected_msgs: tuple[str, str],
    ) -> list[str]:
        """Builds messages for a set of selected/unselected items."""

        result: list[str] = []
        if len(unselected) == 1:
            result.append(unselected_msgs[0] % unselected[0])
        elif len(unselected) > 1:
            result.append(unselected_msgs[1] % (unselected[0], unselected[-1]))
        if len(selected) == 1:
            result.append(selected_msgs[0] % selected[0])
        elif len(selected) > 1:
            result.append(selected_msgs[1] % (selected[0], selected[-1]))
        return result

    def handle_row_and_column_selection_change(self, obj: Atspi.Accessible) -> bool:
        """Presents the selection change for obj."""

        if not (AXObject.supports_table(obj) and AXObject.supports_selection(obj)):
            return True

        cols = set(AXTable.get_selected_columns(obj))
        rows = set(AXTable.get_selected_rows(obj))

        selected_col_labels = [
            AXUtilities.get_column_label(obj, c)
            for c in sorted(cols.difference(set(self._calc_selected_columns)))
        ]
        unselected_col_labels = [
            AXUtilities.get_column_label(obj, c)
            for c in sorted(set(self._calc_selected_columns).difference(cols))
        ]

        selected_row_labels = [
            AXUtilities.get_row_label(obj, r)
            for r in sorted(rows.difference(set(self._calc_selected_rows)))
        ]
        unselected_row_labels = [
            AXUtilities.get_row_label(obj, r)
            for r in sorted(set(self._calc_selected_rows).difference(rows))
        ]

        self._calc_selected_columns = list(cols)
        self._calc_selected_rows = list(rows)

        column_count = AXTable.get_column_count(obj)
        if len(cols) == column_count:
            presentation_manager.get_manager().speak_message(messages.DOCUMENT_SELECTED_ALL)
            return True

        if not cols and len(unselected_col_labels) == column_count:
            presentation_manager.get_manager().speak_message(messages.DOCUMENT_UNSELECTED_ALL)
            return True

        msgs = self._build_selection_change_messages(
            selected_col_labels,
            unselected_col_labels,
            (messages.TABLE_COLUMN_SELECTED, messages.TABLE_COLUMN_RANGE_SELECTED),
            (messages.TABLE_COLUMN_UNSELECTED, messages.TABLE_COLUMN_RANGE_UNSELECTED),
        )
        msgs.extend(
            self._build_selection_change_messages(
                selected_row_labels,
                unselected_row_labels,
                (messages.TABLE_ROW_SELECTED, messages.TABLE_ROW_RANGE_SELECTED),
                (messages.TABLE_ROW_UNSELECTED, messages.TABLE_ROW_RANGE_UNSELECTED),
            )
        )

        if msgs:
            presentation_manager.get_manager().interrupt_presentation()

        for msg in msgs:
            presentation_manager.get_manager().speak_message(msg)

        return bool(msgs)
