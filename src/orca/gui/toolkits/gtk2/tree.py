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

import gtk
from orca.gui.toolkits import tree

import tree_model

class Tree(tree.Tree):

    GRID_LINES_NONE       = gtk.TREE_VIEW_GRID_LINES_NONE
    GRID_LINES_HORIZONTAL = gtk.TREE_VIEW_GRID_LINES_HORIZONTAL
    GRID_LINES_VERTICAL   = gtk.TREE_VIEW_GRID_LINES_VERTICAL
    GRID_LINES_BOTH       = gtk.TREE_VIEW_GRID_LINES_BOTH

    ORDER_DESCENDING      = gtk.SORT_DESCENDING
    ORDER_ASCENDING       = gtk.SORT_ASCENDING

    def __init__(self, *args):
        self._widget = gtk.TreeView()
        self._model = None
        super(Tree, self).__init__(*args)

        model = tree_model.TreeModel(*args)
        self.setModel(model)
        cellRenderer = gtk.CellRendererText()
        for i, columnType in enumerate(args):
            column = gtk.TreeViewColumn(None, cellRenderer, text=i)
            self._widget.append_column(column)
            self.setColumnResizable(i, True)

    def getColumnTitle(self, column):
        treeColumn = self._widget.get_column(column)
        return treeColumn.get_title()

    def setColumnTitle(self, column, title):
        treeColumn = self._widget.get_column(column)
        return treeColumn.set_title(title)

    def getColumnHidden(self, column):
        treeColumn = self._widget.get_column(column)
        return not treeColumn.get_visible()

    def setColumnHidden(self, column, hide):
        treeColumn = self._widget.get_column(column)
        treeColumn.set_visible(not hide)

    def getColumnResizable(self, column):
        treeColumn = self._widget.get_column(column)
        return treeColumn.get_resizable()

    def setColumnResizable(self, column, resizable):
        treeColumn = self._widget.get_column(column)
        treeColumn.set_resizable(resizable)

    def getHeadersHidden(self):
        return not self._widget.get_headers_visible()

    def setHeadersHidden(self, hide):
        self._widget.set_headers_visible(not hide)

    def collapseAll(self):
        self._widget.collapse_all()

    def expandAll(self):
        self._widget.expand_all()

    def getRowExpanded(self, row):
        return self._widget.row_expanded(row)

    def setRowExpanded(self, row, expanded):
        if expanded:
            self._widget.expand_row(row, False)
        else:
            self._widget.collapse_row(row)

    def getItemsExpandable(self):
        pass

    def setItemsExpandable(self,expandable):
        pass

    def setRootIsDecorated(self, setting):
        pass

    def sortByColumn(self, column, order):
        self._model.setSortColumnId(column, order)
        treeColumn = self._widget.get_column(column)
        treeColumn.set_sort_column_id(column)
        treeColumn.set_sort_indicator(True)

    def setRulesHint(self, hint):
        self._widget.set_rules_hint(hint)

    def getGridLines(self):
        return self._widget.get_grid_lines()

    def setGridLines(self, gridLineType):
        self._widget.set_grid_lines(gridLineType)

    def getModel(self):
        return self._model

    def setModel(self, model):
        toolkitModel = model._model
        self._widget.set_model(toolkitModel)
        self._model = model
