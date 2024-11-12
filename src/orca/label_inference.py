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

# For the "AXUtilities has no ... member"
# pylint: disable=E1101

"""Heuristic means to infer the functional/displayed label of a widget."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (C) 2011-2013 Igalia, S.L."
__license__   = "LGPL"

from . import debug
from .ax_component import AXComponent
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities

class LabelInference:

    def __init__(self, script):
        """Creates an instance of the LabelInference class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        self._script = script
        self._lineCache = {}
        self._extentsCache = {}
        self._isWidgetCache = {}

    def infer(self, obj, focusedOnly=True):
        """Attempt to infer the functional/displayed label of obj.

        Arguments
        - obj: the unlabeled widget
        - focusedOnly: If True, only infer if the widget has focus.

        Returns the text which we think is the label, or None.
        """

        tokens = ["LABEL INFERENCE: Infer label for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not obj:
            return None, []

        if focusedOnly and not AXUtilities.is_focused(obj):
            tokens = ["LABEL INFERENCE:", obj, "is not focused"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None, []

        result, objects = None, []
        if not result:
            result, objects = self.inferFromTextLeft(obj)
            debug.print_message(debug.LEVEL_INFO, f"LABEL INFERENCE: Text Left: '{result}'", True)
        if not result or self._preferRight(obj):
            result, objects = self.inferFromTextRight(obj) or result
            debug.print_message(debug.LEVEL_INFO, f"LABEL INFERENCE: Text Right: '{result}'", True)
        if not result:
            result, objects = self.inferFromTable(obj)
            debug.print_message(debug.LEVEL_INFO, f"LABEL INFERENCE: Table: '{result}'", True)
        if not result:
            result, objects = self.inferFromTextAbove(obj)
            debug.print_message(debug.LEVEL_INFO, f"LABEL INFERENCE: Text Above: '{result}'", True)
        if not result:
            result, objects = self.inferFromTextBelow(obj)
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
            result, objects = self.inferFromTextLeft(obj, proximity=200)
            debug.print_message(
                debug.LEVEL_INFO,
                f"LABEL INFERENCE: Text Left with proximity of 200: '{result}'", True)

        self.clearCache()
        return result, objects

    def clearCache(self):
        """Dumps whatever we've stored for performance purposes."""

        self._lineCache = {}
        self._extentsCache = {}
        self._isWidgetCache = {}

    def _preferRight(self, obj):
        """Returns True if we should prefer text on the right, rather than the
        left, for the object obj."""

        return AXUtilities.is_check_box(obj) or AXUtilities.is_radio_button(obj)

    def _preventRight(self, obj):
        """Returns True if we should not permit inference based on text to
        the right for the object obj."""

        return AXUtilities.is_combo_box(obj) or AXUtilities.is_list_box(obj)

    def _preferTop(self, obj):
        """Returns True if we should prefer text above, rather than below for
        the object obj."""

        return AXUtilities.is_combo_box(obj) or AXUtilities.is_list_box(obj)

    def _preventBelow(self, obj):
        """Returns True if we should not permit inference based on text below
        the object obj."""

        return not AXUtilities.is_text_input(obj)

    def _isSimpleObject(self, obj):
        """Returns True if the given object has 'simple' contents, such as text
        without embedded objects or a single embedded object without text."""

        if obj is None:
            return False

        def isMatch(x):
            return AXUtilities.is_web_element(x) and not AXUtilities.is_link(x)

        children = [child for child in AXObject.iter_children(obj, isMatch)]
        if len(children) > 1:
            return False

        string = AXText.get_all_text(obj).strip()
        if string.count(self._script.EMBEDDED_OBJECT_CHARACTER) > 1:
            return False

        return True

    def _cannotLabel(self, obj):
        """Returns True if the given object should not be treated as a label."""

        if obj is None:
            return True

        if AXUtilities.is_heading(obj) or AXUtilities.is_list_item(obj):
            return True

        return self._isWidget(obj)

    def _isWidget(self, obj):
        """Returns True if the given object is a widget."""

        if obj is None:
            return False

        rv = self._isWidgetCache.get(hash(obj))
        if rv is not None:
            return rv

        isWidget = AXUtilities.is_widget(obj) or AXUtilities.is_menu_related(obj)
        if not isWidget and AXUtilities.is_editable(obj):
            isWidget = True

        self._isWidgetCache[hash(obj)] = isWidget
        return isWidget

    def _getExtents(self, obj, startOffset=0, endOffset=-1):
        """Returns (x, y, width, height) of the text at the given offsets
        if the object implements accessible text, or just the extents of
        the object if it doesn't implement accessible text."""

        if not obj:
            return 0, 0, 0, 0

        rv = self._extentsCache.get((hash(obj), startOffset, endOffset))
        if rv:
            return rv

        extents = 0, 0, 0, 0
        if AXObject.supports_text(obj):
            if not AXUtilities.is_text_input(obj):
                if endOffset == -1:
                    endOffset = AXText.get_character_count(obj)
                rect = AXText.get_range_rect(obj, startOffset, endOffset)
                extents = rect.x, rect.y, rect.width, rect.height

        if not (extents[2] and extents[3]):
            ext = AXComponent.get_rect(obj)
            extents = ext.x, ext.y, ext.width, ext.height

        self._extentsCache[(hash(obj), startOffset, endOffset)] = extents
        return extents

    def _createLabelFromContents(self, obj):
        """Gets the functional label text associated with the object obj."""

        if not self._isSimpleObject(obj):
            return None, []

        if self._cannotLabel(obj):
            return None, []

        contents = self._script.utilities.getObjectContentsAtOffset(obj, useCache=False)
        objects = [content[0] for content in contents]
        if list(filter(self._isWidget, objects)):
            return None, []

        strings = [content[3] for content in contents]
        return ''.join(strings), objects

    def _getLineContents(self, obj, start=0):
        """Get the (obj, startOffset, endOffset, string) tuples for the line
        containing the object, obj."""

        rv = self._lineCache.get(hash(obj))
        if rv:
            return rv

        key = hash(obj)
        if self._isWidget(obj):
            start = AXHypertext.get_link_start_offset(obj)
            obj = AXObject.get_parent(obj)

        rv = self._script.utilities.getLineContentsAtOffset(obj, start, True, False)
        self._lineCache[key] = rv

        return rv

    def inferFromTextLeft(self, obj, proximity=75):
        """Attempt to infer the functional/displayed label of obj by
        looking at the contents of the current line, which are to the
        left of this object

        Arguments
        - obj: the unlabeled widget
        - proximity: pixels expected for a match

        Returns the text which we think is the label, or None.
        """

        extents = self._getExtents(obj)
        contents = self._getLineContents(obj)
        content = [o for o in contents if o[0] == obj]
        try:
            index = contents.index(content[0])
        except IndexError:
            index = len(contents)

        onLeft = contents[0:index]
        start = 0
        for i in range(len(onLeft) - 1, -1, -1):
            lObj, lStart, lEnd, lString = onLeft[i]
            lExtents = self._getExtents(lObj)
            if lExtents[0] > extents[0] or self._cannotLabel(lObj):
                start = i + 1
                break

        onLeft = onLeft[start:]
        if not (onLeft and onLeft[0]):
            return None, []

        lObj, start, end, string = onLeft[-1]
        lExtents = self._getExtents(lObj, start, end)
        distance = extents[0] - (lExtents[0] + lExtents[2])
        if 0 <= distance <= proximity:
            strings = [content[3] for content in onLeft]
            result = ''.join(strings).strip()
            if result:
                return result, [content[0] for content in onLeft]

        return None, []

    def inferFromTextRight(self, obj, proximity=25):
        """Attempt to infer the functional/displayed label of obj by
        looking at the contents of the current line, which are to the
        right of this object

        Arguments
        - obj: the unlabeled widget
        - proximity: pixels expected for a match

        Returns the text which we think is the label, or None.
        """

        if self._preventRight(obj):
            return None, []

        extents = self._getExtents(obj)
        contents = self._getLineContents(obj)
        content = [o for o in contents if o[0] == obj]
        try:
            index = contents.index(content[0])
        except IndexError:
            index = len(contents)

        onRight = contents[min(len(contents), index+1):]
        end = len(onRight)
        for i, item in enumerate(onRight):
            if self._cannotLabel(item[0]):
                if not self._preferRight(obj):
                    return None, []
                end = i + 1
                break

        onRight = onRight[0:end]
        if not (onRight and onRight[0]):
            return None, []

        rObj, start, end, string = onRight[0]
        rExtents = self._getExtents(rObj, start, end)
        distance = rExtents[0] - (extents[0] + extents[2])
        if distance <= proximity or self._preferRight(obj):
            strings = [content[3] for content in onRight]
            result = ''.join(strings).strip()
            if result:
                return result, [content[0] for content in onRight]

        return None, []

    def inferFromTextAbove(self, obj, proximity=20):
        """Attempt to infer the functional/displayed label of obj by
        looking at the contents of the line above the line containing
        the object obj.

        Arguments
        - obj: the unlabeled widget
        - proximity: pixels expected for a match

        Returns the text which we think is the label, or None.
        """

        thisLine = self._getLineContents(obj)
        content = [o for o in thisLine if o[0] == obj]
        try:
            index = thisLine.index(content[0])
        except IndexError:
            return None, []
        if index > 0:
            return None, []

        prevObj, prevOffset = self._script.utilities.previousContext(
            thisLine[0][0], thisLine[0][1], True)
        prevLine = self._getLineContents(prevObj, prevOffset)
        if len(prevLine) != 1:
            return None, []

        prevObj, start, end, string = prevLine[0]
        if self._cannotLabel(prevObj):
            return None, []

        if string.strip():
            x, y, width, height = self._getExtents(prevObj, start, end)
            objX, objY, objWidth, objHeight = self._getExtents(obj)
            distance = objY - (y + height)
            if 0 <= distance <= proximity and x <= objX:
                return string.strip(), [prevObj]

        return None, []

    def inferFromTextBelow(self, obj, proximity=20):
        """Attempt to infer the functional/displayed label of obj by
        looking at the contents of the line above the line containing
        the object obj.

        Arguments
        - obj: the unlabeled widget
        - proximity: pixels expected for a match

        Returns the text which we think is the label, or None.
        """

        if self._preventBelow(obj):
            return None, []

        thisLine = self._getLineContents(obj)
        content = [o for o in thisLine if o[0] == obj]
        try:
            index = thisLine.index(content[0])
        except IndexError:
            return None, []
        if index > 0:
            return None, []

        nextObj, nextOffset = self._script.utilities.nextContext(
            thisLine[-1][0], thisLine[-1][2] - 1, True)
        nextLine = self._getLineContents(nextObj, nextOffset)
        if len(nextLine) != 1:
            return None, []

        nextObj, start, end, string = nextLine[0]
        if self._cannotLabel(nextObj):
            return None, []

        if string.strip():
            x, y, width, height = self._getExtents(nextObj, start, end)
            objX, objY, objWidth, objHeight = self._getExtents(obj)
            distance = y - (objY + objHeight)
            if 0 <= distance <= proximity:
                return string.strip(), [nextObj]

        return None, []

    def _isTable(self, obj):
        if AXUtilities.is_table(obj):
            return True

        return self._getTag(obj) == 'table'

    def _isRow(self, obj):
        if AXUtilities.is_table_row(obj):
            return True

        return self._getTag(obj) == 'tr'

    def _isCell(self, obj):
        if AXUtilities.is_table_cell(obj):
            return True

        return self._getTag(obj) in ['td', 'th']

    def _getCellFromRow(self, row, colindex):
        if 0 <= colindex < AXObject.get_child_count(row):
            return row[colindex]

        return None

    def _getTag(self, obj):
        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get('tag')

    def inferFromTable(self, obj, proximityForRight=50):
        """Attempt to infer the functional/displayed label of obj by looking
        at the contents of the surrounding table cells. Note that this approach
        assumes a simple table in which the widget is the sole occupant of its
        cell.

        Arguments
        - obj: the unlabeled widget

        Returns the text which we think is the label, or None.
        """

        cell = AXObject.find_ancestor(obj, self._isCell)
        if not self._isSimpleObject(cell):
            return None, []

        parent = AXObject.get_parent(obj)
        if cell not in [parent, AXObject.get_parent(parent)]:
            return None, []

        grid = AXObject.find_ancestor(cell, self._isTable)
        if not grid:
            return None, []

        cellLeft = cellRight = cellAbove = cellBelow = None
        gridrow = AXObject.find_ancestor(cell, self._isRow)
        rowindex, colindex = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        if colindex > -1:
            cellLeft = AXTable.get_cell_at(grid, rowindex, colindex - 1)
            cellRight = AXTable.get_cell_at(grid, rowindex, colindex + 1)
            cellAbove = AXTable.get_cell_at(grid, rowindex - 1, colindex)
            cellBelow = AXTable.get_cell_at(grid, rowindex + 1, colindex)
        elif gridrow and AXObject.get_parent(cell) == gridrow:
            cellindex = AXObject.get_index_in_parent(cell)
            cellLeft = self._getCellFromRow(gridrow, cellindex - 1)
            cellRight = self._getCellFromRow(gridrow, cellindex + 1)
            rowindex = AXObject.get_index_in_parent(gridrow)
            gridrowParent = AXObject.get_parent(gridrow)
            if rowindex > 0:
                rowAbove = AXObject.get_child(gridrowParent, rowindex - 1)
                cellAbove = self._getCellFromRow(rowAbove, cellindex)
            if rowindex + 1 < AXObject.get_child_count(grid):
                rowBelow = AXObject.get_child(gridrowParent, rowindex + 1)
                cellBelow = self._getCellFromRow(rowBelow, cellindex)

        if cellLeft and not self._preferRight(obj):
            label, sources = self._createLabelFromContents(cellLeft)
            if label:
                return label.strip(), sources

        objX, objY, objWidth, objHeight = self._getExtents(obj)

        if cellRight and not self._preventRight(obj):
            x, y, width, height = self._getExtents(cellRight)
            distance = x - (objX + objWidth)
            if distance <= proximityForRight or self._preferRight(obj):
                label, sources = self._createLabelFromContents(cellRight)
                if label:
                    return label.strip(), sources

        labelAbove = labelBelow = None
        if cellAbove:
            labelAbove, sourcesAbove = self._createLabelFromContents(cellAbove)
            if labelAbove and self._preferTop(obj):
                return labelAbove.strip(), sourcesAbove

        if cellBelow and not self._preventBelow(obj):
            labelBelow, sourcesBelow = self._createLabelFromContents(cellBelow)

        if labelAbove and labelBelow:
            aboveX, aboveY, aboveWidth, aboveHeight = self._getExtents(cellAbove)
            belowX, belowY, belowWidth, belowHeight = self._getExtents(cellBelow)
            dAbove = objY - (aboveY + aboveHeight)
            dBelow = belowY - (objY + objHeight)
            if dAbove <= dBelow:
                return labelAbove.strip(), sourcesAbove
            return labelBelow.strip(), sourcesBelow

        if labelAbove:
            return labelAbove.strip(), sourcesAbove
        if labelBelow:
            return labelBelow.strip(), sourcesBelow

        # None of the cells immediately surrounding this cell seem to be serving
        # as a functional label. Therefore, see if this table looks like a grid
        # of widgets with the functional labels in the first row.

        columns = AXTable.get_column_count(grid)
        firstRow = [AXTable.get_cell_at(grid, 0, i) for i in range(columns)]
        if not firstRow or list(filter(self._isWidget, firstRow)):
            return None, []

        if colindex < 0:
            return None, []

        def isMatch(x):
            if not AXObject.get_child_count(x):
                return False
            return not AXUtilities.have_same_role(AXObject.get_child(x, 0), obj)

        rows = AXTable.get_row_count(grid)
        cells = [AXTable.get_cell_at(grid, i, colindex) for i in range(1, rows)]
        if list(filter(isMatch, cells)):
            return None, []

        label, sources = self._createLabelFromContents(firstRow[colindex])
        if label:
            return label.strip(), sources

        return None, []
