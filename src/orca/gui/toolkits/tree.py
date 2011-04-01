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

from abstract_widget import AbstractWidget

class Tree(AbstractWidget):

    GRID_LINES_NONE       = None
    GRID_LINES_HORIZONTAL = None
    GRID_LINES_VERTICAL   = None
    GRID_LINES_BOTH       = None

    ORDER_DESCENDING      = None
    ORDER_ASCENDING       = None

    def __init__(self, *args):
        super(Tree, self).__init__()

    def getColumnTitle(self):
        pass

    def setColumnTitle(self, header):
        pass

    def getColumnHidden(self, column):
        pass

    def setColumnHidden(self, column, hide):
        pass

    def getColumnResizable(self, column):
        pass

    def setColumnResizable(self, column, resizable):
        pass

    def getHeadersHidden(self):
        pass

    def setHeadersHidden(self, hide):
        pass

    def collapseAll(self):
        pass

    def expandAll(self):
        pass

    def getRowExpanded(self, row):
        pass

    def setRowExpanded(self, row, expanded):
        pass

    def getItemsExpandable(self):
        pass

    def setItemsExpandable(self,expandable):
        pass

    def setRootIsDecorated(self, setting):
        pass

    def sortByColumn(self, column, order):
        pass

    def setRulesHint(self, hint):
        pass

    def getGridLines(self):
        pass

    def setGridLines(self, grid):
        pass

    def getModel(self):
        pass

    def setModel(self, model):
        pass
