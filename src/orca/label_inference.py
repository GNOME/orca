# Orca
#
# Copyright (C) 2011-2013 Igalia, S.L.
#
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

# pylint: disable=too-many-locals
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-statements

"""Heuristic means to infer the functional/displayed label of a widget."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (C) 2011-2013 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from . import debug
from .ax_component import AXComponent
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi
    from .scripts import default

class LabelInference:
    """Heuristic means to infer the functional/displayed label of a widget."""

    def __init__(self, script: default.Script) -> None:
        self._script = script
        self._line_cache: dict[int, list[tuple[Atspi.Accessible, int, int, str]]] = {}
        self._extents_cache: dict[tuple[int, int, int], tuple[int, int, int, int]] = {}
        self._is_widget_cache: dict[int, bool] = {}

    def infer(
        self,
        obj: Atspi.Accessible,
        focused_only: bool = True
    ) -> tuple[str | None, list[Atspi.Accessible]]:
        """Attempt to infer the functional/displayed label of obj."""

        tokens = ["LABEL INFERENCE: Infer label for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not obj:
            return None, []

        if focused_only and not AXUtilities.is_focused(obj):
            tokens = ["LABEL INFERENCE:", obj, "is not focused"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None, []

        result: str | None = None
        objects: list[Atspi.Accessible] = []
        if not result:
            result, objects = self._infer_from_text_left(obj)
            debug.print_message(debug.LEVEL_INFO, f"LABEL INFERENCE: Text Left: '{result}'", True)
        if not result or self._prefer_right(obj):
            temp_result = self._infer_from_text_right(obj)
            if temp_result[0] is not None:
                result, objects = temp_result
            debug.print_message(debug.LEVEL_INFO, f"LABEL INFERENCE: Text Right: '{result}'", True)
        if not result:
            result, objects = self._infer_from_table(obj)
            debug.print_message(debug.LEVEL_INFO, f"LABEL INFERENCE: Table: '{result}'", True)
        if not result:
            result, objects = self._infer_from_text_above(obj)
            debug.print_message(debug.LEVEL_INFO, f"LABEL INFERENCE: Text Above: '{result}'", True)
        if not result:
            result, objects = self._infer_from_text_below(obj)
            debug.print_message(debug.LEVEL_INFO, f"LABEL INFERENCE: Text Below: '{result}'", True)

        # TODO - We probably do not wish to "infer" from these. Instead, we
        # should ensure that this content gets presented as part of the widget.
        # (i.e. the label is something on screen. Widget name and description
        # are each something other than a label.)
        if not result:
            result, objects = AXObject.get_name(obj), []
            debug.print_message(debug.LEVEL_INFO, f"LABEL INFERENCE: Name: '{result}'", True)

        if result:
            result = result.strip()
            result = result.replace("\n", " ")

        # Desperate times call for desperate measures....
        if not result:
            result, objects = self._infer_from_text_left(obj, proximity=200)
            debug.print_message(
                debug.LEVEL_INFO,
                f"LABEL INFERENCE: Text Left with proximity of 200: '{result}'", True)

        self._clear_cache()
        return result, objects

    def _clear_cache(self) -> None:
        """Dumps whatever we've stored for performance purposes."""

        self._line_cache = {}
        self._extents_cache = {}
        self._is_widget_cache = {}

    def _prefer_right(self, obj: Atspi.Accessible) -> bool:
        """Returns True if we should prefer text on the right."""

        return AXUtilities.is_check_box(obj) or AXUtilities.is_radio_button(obj)

    def _prevent_right(self, obj: Atspi.Accessible) -> bool:
        """Returns True if we should not permit inference based on text to the right of obj."""

        return AXUtilities.is_combo_box(obj) or AXUtilities.is_list_box(obj)

    def _prefer_top(self, obj: Atspi.Accessible) -> bool:
        """Returns True if we should prefer text above, rather than below for obj."""

        return AXUtilities.is_combo_box(obj) or AXUtilities.is_list_box(obj)

    def _prevent_below(self, obj: Atspi.Accessible) -> bool:
        """Returns True if we should not permit inference based on text below obj."""

        return not AXUtilities.is_text_input(obj)

    def _is_simple_object(self, obj: Atspi.Accessible | None) -> bool:
        """Returns True if the given object has 'simple' contents."""

        if obj is None:
            return False

        def is_match(x: Atspi.Accessible) -> bool:
            return AXUtilities.is_web_element(x) and not AXUtilities.is_link(x)

        children = list(AXObject.iter_children(obj, is_match))
        if len(children) > 1:
            return False

        string = AXText.get_all_text(obj).strip()
        if string.count("\ufffc") > 1:
            return False

        return True

    def _cannot_label(self, obj: Atspi.Accessible | None) -> bool:
        """Returns True if the given object should not be treated as a label."""

        if obj is None:
            return True

        if AXUtilities.is_heading(obj) or AXUtilities.is_list_item(obj):
            return True

        return self._is_widget(obj)

    def _is_widget(self, obj: Atspi.Accessible | None) -> bool:
        """Returns True if the given object is a widget."""

        if obj is None:
            return False

        rv = self._is_widget_cache.get(hash(obj))
        if rv is not None:
            return rv

        is_widget = AXUtilities.is_widget(obj) or AXUtilities.is_menu_related(obj)
        if not is_widget and AXUtilities.is_editable(obj):
            is_widget = True

        self._is_widget_cache[hash(obj)] = is_widget
        return is_widget

    def _get_extents(
        self,
        obj: Atspi.Accessible | None,
        start_offset: int = 0,
        end_offset: int = -1
    ) -> tuple[int, int, int, int]:
        """Returns (x, y, width, height) of the text at the given offsets."""

        if obj is None:
            return 0, 0, 0, 0

        rv = self._extents_cache.get((hash(obj), start_offset, end_offset))
        if rv:
            return rv

        extents = 0, 0, 0, 0
        if AXObject.supports_text(obj):
            if not AXUtilities.is_text_input(obj):
                if end_offset == -1:
                    end_offset = AXText.get_character_count(obj)
                rect = AXText.get_range_rect(obj, start_offset, end_offset)
                extents = rect.x, rect.y, rect.width, rect.height

        if not (extents[2] and extents[3]):
            ext = AXComponent.get_rect(obj)
            extents = ext.x, ext.y, ext.width, ext.height

        self._extents_cache[(hash(obj), start_offset, end_offset)] = extents
        return extents

    def _create_label_from_contents(
        self,
        obj: Atspi.Accessible
    ) -> tuple[str | None, list[Atspi.Accessible]]:
        """Gets the functional label text associated with the object obj."""

        if not self._is_simple_object(obj):
            return None, []

        if self._cannot_label(obj):
            return None, []

        contents = self._script.utilities.get_object_contents_at_offset(obj, use_cache=False)
        objects = [content[0] for content in contents]
        if list(filter(self._is_widget, objects)):
            return None, []

        strings = [content[3] for content in contents]
        return ''.join(strings), objects

    def _get_line_contents(
        self,
        obj: Atspi.Accessible,
        start: int = 0
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Get the (obj, start_offset, end_offset, string) tuples for the line containing obj."""

        rv = self._line_cache.get(hash(obj))
        if rv:
            return rv

        key = hash(obj)
        if self._is_widget(obj):
            start = AXHypertext.get_link_start_offset(obj)
            obj = AXObject.get_parent(obj)

        rv = self._script.utilities.get_line_contents_at_offset(obj, start, True, False)
        if rv is None:
            rv = []
        self._line_cache[key] = rv

        return rv

    def _infer_from_text_left(
        self,
        obj: Atspi.Accessible,
        proximity: int = 75
    ) -> tuple[str | None, list[Atspi.Accessible]]:
        """Attempt to infer the functional/displayed label of obj from contents on its left."""

        extents = self._get_extents(obj)
        contents = self._get_line_contents(obj)
        content = [o for o in contents if o[0] == obj]
        try:
            index = contents.index(content[0])
        except IndexError:
            index = len(contents)

        on_left = contents[0:index]
        start = 0
        for i in range(len(on_left) - 1, -1, -1):
            left_obj, _left_start, _left_end, _left_string = on_left[i]
            left_extents = self._get_extents(left_obj)
            if left_extents[0] > extents[0] or self._cannot_label(left_obj):
                start = i + 1
                break

        on_left = on_left[start:]
        if not (on_left and on_left[0]):
            return None, []

        left_obj, start, end, _string = on_left[-1]
        left_extents = self._get_extents(left_obj, start, end)
        distance = extents[0] - (left_extents[0] + left_extents[2])
        if 0 <= distance <= proximity:
            strings = [content[3] for content in on_left]
            result = ''.join(strings).strip()
            if result:
                return result, [content[0] for content in on_left]

        return None, []

    def _infer_from_text_right(
        self,
        obj: Atspi.Accessible,
        proximity: int = 25
    ) -> tuple[str | None, list[Atspi.Accessible]]:
        """Attempt to infer the functional/displayed label of obj from contents on its right."""

        if self._prevent_right(obj):
            return None, []

        extents = self._get_extents(obj)
        contents = self._get_line_contents(obj)
        content = [o for o in contents if o[0] == obj]
        try:
            index = contents.index(content[0])
        except IndexError:
            index = len(contents)

        on_right = contents[min(len(contents), index+1):]
        end = len(on_right)
        for i, item in enumerate(on_right):
            if self._cannot_label(item[0]):
                if not self._prefer_right(obj):
                    return None, []
                end = i + 1
                break

        on_right = on_right[0:end]
        if not (on_right and on_right[0]):
            return None, []

        right_obj, start, end,_string = on_right[0]
        right_extents = self._get_extents(right_obj, start, end)
        distance = right_extents[0] - (extents[0] + extents[2])
        if distance <= proximity or self._prefer_right(obj):
            strings = [content[3] for content in on_right]
            result = ''.join(strings).strip()
            if result:
                return result, [content[0] for content in on_right]

        return None, []

    def _infer_from_text_above(
        self,
        obj: Atspi.Accessible,
        proximity: int = 20
    ) -> tuple[str | None, list[Atspi.Accessible]]:
        """Attempt to infer the functional/displayed label of obj from contents above it."""

        this_line = self._get_line_contents(obj)
        content = [o for o in this_line if o[0] == obj]
        try:
            index = this_line.index(content[0])
        except IndexError:
            return None, []
        if index > 0:
            return None, []

        prev_obj, prev_offset = self._script.utilities.previous_context(
            this_line[0][0], this_line[0][1], True)
        prev_line = self._get_line_contents(prev_obj, prev_offset)
        if len(prev_line) != 1:
            return None, []

        prev_obj, start, end, string = prev_line[0]
        if self._cannot_label(prev_obj):
            return None, []

        if string.endswith("\n"):
            string = string[:-1]
            end -= 1

        if string.strip():
            x, y, _width, height = self._get_extents(prev_obj, start, end)
            obj_x, obj_y, _obj_width, _obj_height = self._get_extents(obj)
            distance = obj_y - (y + height)
            if 0 <= distance <= proximity and x <= obj_x:
                return string.strip(), [prev_obj]

        return None, []

    def _infer_from_text_below(
        self,
        obj: Atspi.Accessible,
        proximity: int = 20
    ) -> tuple[str | None, list[Atspi.Accessible]]:
        """Attempt to infer the functional/displayed label of obj from contents below it."""

        if self._prevent_below(obj):
            return None, []

        this_line = self._get_line_contents(obj)
        content = [o for o in this_line if o[0] == obj]
        try:
            index = this_line.index(content[0])
        except IndexError:
            return None, []
        if index > 0:
            return None, []

        next_obj, next_offset = self._script.utilities.next_context(
            this_line[-1][0], this_line[-1][2] - 1, True)
        next_line = self._get_line_contents(next_obj, next_offset)
        if len(next_line) != 1:
            return None, []

        next_obj, start, end, string = next_line[0]
        if self._cannot_label(next_obj):
            return None, []

        if string.strip():
            _x, y, _width, _height = self._get_extents(next_obj, start, end)
            _obj_x, obj_y, _obj_width, obj_height = self._get_extents(obj)
            distance = y - (obj_y + obj_height)
            if 0 <= distance <= proximity:
                return string.strip(), [next_obj]

        return None, []

    def _infer_from_table(
        self,
        obj: Atspi.Accessible,
        proximity_for_right: int = 50
    ) -> tuple[str | None, list[Atspi.Accessible]]:
        """Attempt to infer the functional/displayed label of obj from neighboring cells."""

        cell = AXObject.find_ancestor(obj, AXUtilities.is_table_cell)
        if not self._is_simple_object(cell):
            return None, []

        parent = AXObject.get_parent(obj)
        if cell not in [parent, AXObject.get_parent(parent)]:
            return None, []

        grid = AXObject.find_ancestor(cell, AXUtilities.is_table)
        if not grid:
            return None, []

        cell_left = cell_right = cell_above = cell_below = None
        gridrow = AXObject.find_ancestor(cell, AXUtilities.is_table_row)
        rowindex, colindex = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        if colindex > -1:
            cell_left = AXTable.get_cell_at(grid, rowindex, colindex - 1)
            cell_right = AXTable.get_cell_at(grid, rowindex, colindex + 1)
            cell_above = AXTable.get_cell_at(grid, rowindex - 1, colindex)
            cell_below = AXTable.get_cell_at(grid, rowindex + 1, colindex)
        elif gridrow and AXObject.get_parent(cell) == gridrow:
            cellindex = AXObject.get_index_in_parent(cell)
            cell_left = AXObject.get_child(gridrow, cellindex - 1)
            cell_right = AXObject.get_child(gridrow, cellindex + 1)
            rowindex = AXObject.get_index_in_parent(gridrow)
            gridrow_parent = AXObject.get_parent(gridrow)
            if rowindex > 0:
                row_above = AXObject.get_child(gridrow_parent, rowindex - 1)
                cell_above = AXObject.get_child(row_above, cellindex)
            if rowindex + 1 < AXObject.get_child_count(grid):
                row_below = AXObject.get_child(gridrow_parent, rowindex + 1)
                cell_below = AXObject.get_child(row_below, cellindex)

        if cell_left and not self._prefer_right(obj):
            label, sources = self._create_label_from_contents(cell_left)
            if label:
                return label.strip(), sources

        obj_x, obj_y, obj_width, obj_height = self._get_extents(obj)
        if cell_right and not self._prevent_right(obj):
            x, _y, _width, _height = self._get_extents(cell_right)
            distance = x - (obj_x + obj_width)
            if distance <= proximity_for_right or self._prefer_right(obj):
                label, sources = self._create_label_from_contents(cell_right)
                if label:
                    return label.strip(), sources

        label_above: str | None = None
        sources_above: list[Atspi.Accessible] = []
        if cell_above:
            label_above, sources_above = self._create_label_from_contents(cell_above)
            if label_above and self._prefer_top(obj):
                return label_above.strip(), sources_above

        label_below: str | None = None
        sources_below: list[Atspi.Accessible] = []
        if cell_below and not self._prevent_below(obj):
            label_below, sources_below = self._create_label_from_contents(cell_below)

        if label_above and label_below:
            _above_x, above_y, _above_width, above_height = self._get_extents(cell_above)
            _below_x, below_y, _below_width, _below_height = self._get_extents(cell_below)
            delta_above = obj_y - (above_y + above_height)
            delta_below = below_y - (obj_y + obj_height)
            if delta_above <= delta_below:
                return label_above.strip(), sources_above
            return label_below.strip(), sources_below

        if label_above:
            return label_above.strip(), sources_above
        if label_below:
            return label_below.strip(), sources_below

        # None of the cells immediately surrounding this cell seem to be serving
        # as a functional label. Therefore, see if this table looks like a grid
        # of widgets with the functional labels in the first row.
        columns = AXTable.get_column_count(grid)
        first_row = [AXTable.get_cell_at(grid, 0, i) for i in range(columns)]
        if not first_row or list(filter(self._is_widget, first_row)):
            return None, []

        if colindex < 0:
            return None, []

        def is_match(x: Atspi.Accessible) -> bool:
            if not AXObject.get_child_count(x):
                return False
            return not AXUtilities.have_same_role(AXObject.get_child(x, 0), obj)

        rows = AXTable.get_row_count(grid)
        cells = [AXTable.get_cell_at(grid, i, colindex) for i in range(1, rows)]
        if list(filter(is_match, cells)):
            return None, []

        label, sources = self._create_label_from_contents(first_row[colindex])
        if label:
            return label.strip(), sources

        return None, []
