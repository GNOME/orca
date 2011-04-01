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
from orca.gui.toolkits import table

class Table(table.Table):
    def __init__(self, nRows, nColumns):
        self._widget = QtGui.QGridLayout()
        super(Table, self).__init__(nRows, nColumns)

    def getSize(self):
        rows = self._widget.rowCount()
        columns = self._widget.columnCount()
        return rows, columns

    def setSize(self, nRows, nColumns):
        # Can you really not specify this?
        pass

    def add(self, obj, row, col, rowspan=1, colspan=1):
        child = obj._widget
        if isinstance(child, QtGui.QLayout):
            self._widget.addLayout(child, row, col, rowspan, colspan)
        elif isinstance(child, QtGui.QWidget):
            self._widget.addWidget(child, row, col, rowspan, colspan)
        else:
            self._widget.addItem(child, row, col, rowspan, colspan)

    def setPadding(self, child, xpadding, ypadding):
        pass

    def setOptions(self, child, xoptions, yoptions):
        pass

    def setContentsMargins(self, left, top, right, bottom):
        self._widget.setContentsMargins(left, top, right, bottom)
