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

from abstract_model import AbstractModel

class TreeModel(AbstractModel):

    def __init__(self, *args):
        super(TreeModel, self).__init__()

    def setValue(self, row, column, value):
        pass

    def remove(self, row):
        pass

    def insert(self, parent, position, rowItems):
        pass

    def prepend(self, parent, rowItems):
        pass

    def append(self, parent, rowItems):
        pass

    def isAncestor(self, row, descendant):
        pass

    def rowDepth(self, row):
        pass

    def clear(self):
        pass

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
