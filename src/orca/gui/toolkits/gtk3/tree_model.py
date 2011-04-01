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

from gi.repository.Gtk import TreeStore as gtkTreeStore
from orca.gui.toolkits import tree_model

class TreeModel(tree_model.TreeModel):

    def __init__(self, *args):
        self._model = gtkTreeStore(*args)
        super(TreeModel, self).__init__(*args)

    def setValue(self, row, column, value):
        self._model.set_value(row, column, value)

    def remove(self, row):
        return self._model.remove(row)

    def insert(self, parent, position, rowItems):
        return self._model.insert(parent, position, rowItems)

    def prepend(self, parent, rowItems):
        return self._model.prepend(parent, rowItems)

    def append(self, parent, rowItems):
        return self._model.append(parent, rowItems)

    def isAncestor(self, row, descendant):
        return self._model.is_ancestor(row, descendant)

    def rowDepth(self, row):
        return self._model.iter_depth(row)

    def clear(self):
        self._model.clear()

    def reorder(self, parent, new_order):
        self._model.reorder(parent, new_order)

    def swap(self, a, b):
        self._model.swap(a, b)

    def moveAfter(self, row, position):
        self._model.move_after(row, position)

    def moveBefore(self, row, position):
        self._model.move_before(row, position)

    def setSortColumnId(self, column, order):
        self._model.set_sort_column_id(column, order)
