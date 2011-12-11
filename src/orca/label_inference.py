# Orca
#
# Copyright (C) 2011 Igalia, S.L.
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

"""Heuristic means to infer the functional/displayed label of a widget."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (C) 2011 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

class LabelInference:

    def __init__(self, script):
        """Creates an instance of the LabelInference class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        self._script = script
        self._lines = {}

    def infer(self, obj, focusedOnly=True):
        """Attempt to infer the functional/displayed label of obj.

        Arguments
        - obj: the unlabeled widget
        - focusedOnly: If True, only infer if the widget has focus.

        Returns the text which we think is the label, or None.
        """

        isFocused = obj.getState().contains(pyatspi.STATE_FOCUSED)
        if focusedOnly and not isFocused:
            return None

        result = None
        if not result:
            result = self.inferFromLine(obj)
        if not result:
            result = self.inferFromTable(obj)
        if not result:
            result = self.inferFromOtherLines(obj)
        if not result:
            result = obj.name
        if not result:
            result = obj.description
        if result:
            result = result.strip()
        self.clearCache()

        return result

    def clearCache(self):
        """Dumps whatever we've stored for performance purposes."""

        self._lines = {}

    def _preferRight(self, obj):
        """Returns True if we should prefer text on the right, rather than the
        left, for the object obj."""

        onRightRoles = [pyatspi.ROLE_CHECK_BOX, pyatspi.ROLE_RADIO_BUTTON]
        return obj.getRole() in onRightRoles

    def _isSimpleObject(self, obj):
        """Returns True if the given object has 'simple' contents, such as text
        without embedded objects or a single embedded object without text."""

        if not obj:
            return False

        children = [child for child in obj]
        children = filter(lambda x: x.getRole() != pyatspi.ROLE_LINK, children)
        if len(children) > 1:
            return False

        if self._isWidget(obj):
            return False

        try:
            text = obj.queryText()
        except NotImplementedError:
            return True

        string = text.getText(0, -1).decode('UTF-8')
        if string.find(self._script.EMBEDDED_OBJECT_CHARACTER) > -1:
            return len(string) == 1

        return True

    def _isWidget(self, obj):
        """Returns True if the given object is a widget."""

        if not obj:
            return False

        widgetRoles = [pyatspi.ROLE_CHECK_BOX,
                       pyatspi.ROLE_RADIO_BUTTON,
                       pyatspi.ROLE_COMBO_BOX,
                       pyatspi.ROLE_DOCUMENT_FRAME,
                       pyatspi.ROLE_LIST,
                       pyatspi.ROLE_ENTRY,
                       pyatspi.ROLE_PASSWORD_TEXT,
                       pyatspi.ROLE_PUSH_BUTTON]

        return obj.getRole() in widgetRoles

    def _getExtents(self, obj, startOffset=0, endOffset=-1):
        """Returns (x, y, width, height) of the text at the given offsets
        if the object implements accessible text, or just the extents of
        the object if it doesn't implement accessible text."""

        extents = 0, 0, 0, 0

        try:
            text = obj.queryText()
        except AttributeError:
            return extents
        except NotImplementedError:
            pass
        else:
            skipTextExtents = [pyatspi.ROLE_ENTRY, pyatspi.ROLE_PASSWORD_TEXT]
            if not obj.getRole() in skipTextExtents:
                extents = text.getRangeExtents(startOffset, endOffset, 0)

        if extents[2] and extents[3]:
            return extents

        ext = obj.queryComponent().getExtents(0)
        extents = ext.x, ext.y, ext.width, ext.height

        return extents

    def _createLabelFromContents(self, obj):
        """Gets the functional label text associated with the object obj."""

        if not self._isSimpleObject(obj):
            return ''

        contents = self._script.utilities.getObjectsFromEOCs(obj)
        objects = [content[0] for content in contents]
        if filter(self._isWidget, objects):
            return ''

        strings = [content[3] or content[0].name for content in contents]
        strings = map(lambda x: x.strip(), strings)
        return ' '.join(strings)

    def _getLineContents(self, obj):
        """Get the (obj, startOffset, endOffset, string) tuples for the line
        containing the object, obj."""

        rv = self._lines.get(hash(obj))
        if rv:
            return rv

        key = hash(obj)
        start = None
        if self._isWidget(obj):
            start, end = self._script.utilities.getHyperlinkRange(obj)
            obj = obj.parent

        boundary = pyatspi.TEXT_BOUNDARY_LINE_START
        rv = self._script.utilities.getObjectsFromEOCs(obj, boundary, start)
        self._lines[key] = rv

        return rv

    def inferFromLine(self, obj, proximity=75):
        """Attempt to infer the functional/displayed label of obj by
        looking at the contents of the current line.

        Arguments
        - obj: the unlabeled widget
        - proximity: pixels expected for a match

        Returns the text which we think is the label, or None.
        """

        extents = self._getExtents(obj)
        contents = self._getLineContents(obj)
        content = filter(lambda o: o[0] == obj, contents)
        try:
            index = contents.index(content[0])
        except IndexError:
            index = len(contents)

        onLeft = contents[max(0, index-1):index]
        onLeft = filter(lambda o: not self._isWidget(o[0]), onLeft)
        if onLeft:
            lObj, lStart, lEnd, lString = onLeft[0]
            lString = (lString or lObj.name).strip()
            if lString:
                lExtents = self._getExtents(lObj, lStart, lEnd)
                lDistance = extents[0] - (lExtents[0] + lExtents[2])
                if not self._preferRight(obj) and lDistance <= proximity:
                    return lString

        onRight = contents[min(len(contents), index+1):]
        onRight = filter(lambda o: not self._isWidget(o[0]), onRight)
        if onRight:
            rObj, rStart, rEnd, rString = onRight[0]
            rString = (rString or rObj.name).strip()
            if rString:
                rExtents = self._getExtents(rObj, rStart, rEnd)
                rDistance = rExtents[0] - (extents[0] + extents[2])
                if self._preferRight(obj) or rDistance <= proximity:
                    return rString

        return None

    def inferFromTable(self, obj):
        """Attempt to infer the functional/displayed label of obj by looking
        at the contents of the surrounding table cells. Note that this approach
        assumes a simple table in which the widget is the sole occupant of its
        cell.

        Arguments
        - obj: the unlabeled widget

        Returns the text which we think is the label, or None.
        """

        pred = lambda x: x.getRole() == pyatspi.ROLE_TABLE_CELL
        cell = pyatspi.utils.findAncestor(obj, pred)
        if not self._isSimpleObject(cell):
            return None

        pred = lambda x: x.getRole() == pyatspi.ROLE_TABLE
        grid = pyatspi.utils.findAncestor(cell, pred)
        if not grid:
            return None

        try:
            table = grid.queryTable()
        except NotImplementedError:
            return None

        index = self._script.utilities.cellIndex(cell)
        row = table.getRowAtIndex(index)
        col = table.getColumnAtIndex(index)

        if col > 0 and not self._preferRight(obj):
            candidate = table.getAccessibleAt(row, col - 1)
            label = self._createLabelFromContents(candidate)
            if label:
                return label

        if col < table.nColumns:
            candidate = table.getAccessibleAt(row, col + 1)
            label = self._createLabelFromContents(candidate)
            if label:
                return label

        if row > 0:
            candidate = table.getAccessibleAt(row - 1, col)
            label = self._createLabelFromContents(candidate)
            if label:
                return label

        if row < table.nRows:
            candidate = table.getAccessibleAt(row + 1, col)
            label = self._createLabelFromContents(candidate)
            if label:
                return label

        # None of the cells immediately surrounding this cell seem to be serving
        # as a functional label. Therefore, see if this table looks like a grid
        # of widgets with the functional labels in the first row.
        firstRow = [table.getAccessibleAt(0, i) for i in range(table.nColumns)]
        if not firstRow or filter(self._isWidget, firstRow):
            return None

        cells = [table.getAccessibleAt(i, col) for i in range(1, table.nRows)]
        if filter(lambda x: x[0] and x[0].getRole() != obj.getRole(), cells):
            return None

        label = self._createLabelFromContents(firstRow[col])
        if label:
            return label

        return None

    def inferFromOtherLines(self, obj):
        """Attempt to infer the functional/displayed label of obj by
        looking at the contents of the previous and/or next line.

        Arguments
        - obj: the unlabeled widget

        Returns the text which we think is the label, or None.
        """

        pass
