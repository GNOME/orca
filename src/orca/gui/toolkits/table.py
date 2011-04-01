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

class Table(AbstractWidget):

    def __init__(self, nRows, nColumns):
        super(Table, self).__init__()
        self.setSize(nRows, nColumns)

    def getSize(self):
        pass

    def setSize(self, nRows, nColumns):
        pass

    def add(self, obj, row, col, rowspan=1, colspan=1):
        pass

    def setPadding(self, xpadding, ypadding):
        pass

    def setOptions(self, child, xoptions, yoptions):
        pass

    def setContentsMargins(self, left, top, right, bottom):
        pass
