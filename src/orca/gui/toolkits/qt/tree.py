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

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QVariant, QModelIndex
from orca.gui.toolkits import tree

import tree_model

class Tree(tree.Tree):

    GRID_LINES_NONE       = None
    GRID_LINES_HORIZONTAL = None
    GRID_LINES_VERTICAL   = None
    GRID_LINES_BOTH       = None

    ORDER_DESCENDING      = Qt.DescendingOrder
    ORDER_ASCENDING       = Qt.AscendingOrder

    def __init__(self, *args):
        self._widget = QtGui.QTreeView()
        self._model = None
        super(Tree, self).__init__(*args)

        model = tree_model.TreeModel(*args)
        self.setModel(model)

    def getColumnTitle(self, column):
        # TODO: This seems wrong. Compare to Gtk2 and Gtk3.
        header = self._widget.header()
        model = header.model()
        return model.headerData(column, Qt.Horizontal)

    def setColumnTitle(self, column, title):
        # TODO: This seems wrong. Compare to Gtk2 and Gtk3.
        header = self._widget.header()
        model = header.model()
        model.setHeaderData(column, Qt.Horizontal, QVariant(title))

    def getColumnHidden(self, column):
        return self._widget.isColumnHidden(column)

    def setColumnHidden(self, column, hide):
        if hide:
            self._widget.hideColumn(column)
        else:
            self._widget.showColumn(column)

    def getColumnResizable(self, column):
        pass

    def setColumnResizable(self, column, resizable):
        pass

    def getHeadersHidden(self):
        return self._widget.isHeaderHidden()

    def setHeadersHidden(self, hide):
        self._widget.setHeaderHidden(hide)

    def collapseAll(self):
        self._widget.collapseAll()

    def expandAll(self):
        self._widget.expandAll()

    def getRowExpanded(self, row):
        pass

    def setRowExpanded(self, row, expanded):
        pass

    def getItemsExpandable(self):
        return self._widget.itemsExpandable()

    def setItemsExpandable(self, expandable):
        self._widget.setItemsExpandable(expandable)

    def setRootIsDecorated(self, setting):
        self._widget.setRootIsDecorated(setting)

    def sortByColumn(self, column, order):
        self._widget.setSortingEnabled(True)
        self._widget.sortByColumn(column, order)

    def setRulesHint(self, hint):
        self._widget.setAlternatingRowColors(hint)

    def getGridLines(self):
        pass

    def setGridLines(self, grid):
        pass

    def getModel(self):
        return self._model

    def setModel(self, model):
        self._widget.setModel(model._model)
        self._model = model
