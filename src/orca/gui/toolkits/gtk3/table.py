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

from gi.repository.Gtk import Table as gtkTable
from orca.gui.toolkits import table

class Table(table.Table):
    def __init__(self, nRows, nColumns):
        self._widget = gtkTable()
        super(Table, self).__init__(nRows, nColumns)

    def getSize(self):
        rows = self._widget.get_property('n-rows')
        columns = self._widget.get_property('n-columns')
        return rows, columns

    def setSize(self, nRows, nColumns):
        self._widget.resize(nRows, nColumns)

    def add(self, obj, row, col, rowspan=1, colspan=1):
        self._widget.attach(obj._widget, col, col+colspan, row, row+rowspan)

    def setPadding(self, child, xpadding, ypadding):
        obj = child._widget
        self._widget.child_set_property(obj, 'x-padding', xpadding)
        self._widget.child_set_property(obj, 'y-padding', ypadding)

    def setOptions(self, child, xoptions, yoptions):
        obj = child._widget
        self._widget.child_set_property(obj, 'x-options', xoptions)
        self._widget.child_set_property(obj, 'y-options', yoptions)

    def setContentsMargins(self, left, top, right, bottom):
        pass
