# Orca
#
# Copyright 2011 The Orca Team.
# Author: Joanmarie Diggs <joanmarie.diggs@gmail.com>
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

from PyQt4.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant
from orca.gui.toolkits import tree_model

class Row(list):
    def __init__(self, parent, columnTypes):
        super(Row, self).__init__()
        self.parent = parent
        self._columnTypes = columnTypes
        self.extend([None] * len(columnTypes))

    def getCellValue(self, column):
        return self[column]

    def setCellValue(self, column, value):
        # TODO: Add validation based on type
        self[column] = value

    def populate(self, values):
        if len(values) != len(self):
            return False

        for i, value in enumerate(values):
            self.setCellValue(i, value)

        return True

# NOTE: This isn't done or fully working. Qt implementation is merely
# a proof-of-concept at this stage. (Having said that, the tree in the
# test works.)

class QtTreeModel(QAbstractItemModel):

    def __init__(self, *args):
        super(QtTreeModel, self).__init__()
        self._columnTypes = args
        self._columnHeaders = [None] * len(args)
        self.rows = []

    def rowCount(self, parent):
        return len(self.rows)

    def columnCount(self, parent):
        return len(self._columnTypes)

    def index(self, row, column, parent):
        if not parent.isValid():
            return self.createIndex(row, column, parent)

        # TODO: Finish this.
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        # TODO: Finish this.
        return QModelIndex()

    def data(self, index, role):
        # TODO: Finish this, including using the pointer to get the
        # parent row. (Some error somewhere was resulting in frequent
        # segfaults.)
        if not index.isValid():
            return QVariant()

        if not role == Qt.DisplayRole:
            return QVariant()

        row = self.rows[index.row()]
        cell = row[index.column()]

        return QVariant(cell)

    def setData(self, index, value, role):
        # TODO: Implement this.
        pass

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._columnHeaders[section]

        return QVariant()

    def setHeaderData(self, section, orientation, value, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            self._columnHeaders[section] = value

    def insertRows(self, row, count, parent):
        if parent == None:
            parent = QModelIndex()

        lastRow = row + count - 1
        self.beginInsertRows(parent, row, lastRow)
        parentItem = parent.internalPointer()
        emptyRow = Row(parentItem, self._columnTypes)
        emptyRows = [emptyRow for i in xrange(count)]
        self.rows[row:lastRow] = emptyRows
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent):
        if parent == None:
            parent = QModelIndex()

        self.beginRemoveRows(parent, row, row + count - 1)
        for i in xrange(row, row + count - 1):
            self.rows.pop(i)
        self.endRemoveRows()
        return True

class TreeModel(tree_model.TreeModel):

    def __init__(self, *args):
        self._model = QtTreeModel(*args)
        super(TreeModel, self).__init__(*args)

    def setValue(self, row, column, value):
        index = self.index(row, column, parent)
        self._model.setData(index, value)

    def remove(self, row):
        self._model.removeRows(row, 1, parent)

    def insert(self, parent, position, rowItems):
        self._model.insertRows(position, 1, parent)
        emptyRow = self._model.rows[position]
        emptyRow.populate(rowItems)

    def prepend(self, parent, rowItems):
        self._model.insertRows(0, 1, parent)
        emptyRow = self._model.rows[end]
        emptyRow.populate(rowItems)

    def append(self, parent, rowItems):
        end = self._model.rowCount(parent)
        self._model.insertRows(end, 1, parent)
        emptyRow = self._model.rows[end]
        emptyRow.populate(rowItems)

    def isAncestor(self, row, descendant):
        pass

    def rowDepth(self, row):
        pass

    def clear(self):
        self._model.reset()

    def reorder(self, parent, new_order):
        pass

    def swap(self, a, b):
        pass

    def moveAfter(self, row, position):
        pass

    def moveBefore(self, row, position):
        pass

    def setSortColumnId(self, column, order):
        pass
