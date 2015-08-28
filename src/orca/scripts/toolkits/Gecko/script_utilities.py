# Orca
#
# Copyright 2010 Joanmarie Diggs.
# Copyright 2014-2015 Igalia, S.L.
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

"""Commonly-required utility methods needed by -- and potentially
   customized by -- application and toolkit scripts. They have
   been pulled out from the scripts because certain scripts had
   gotten way too large as a result of including these methods."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs." \
                "Copyright (c) 2014-2015 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

from orca import debug
from orca import orca_state
from orca.scripts import web


class Utilities(web.Utilities):

    def __init__(self, script):
        super().__init__(script)

    def _attemptBrokenTextRecovery(self):
        return True

    def nodeLevel(self, obj):
        """Determines the level of at which this object is at by using
        the object attribute 'level'.  To be consistent with the default
        nodeLevel() this value is 0-based (Gecko return is 1-based) """

        if obj is None or obj.getRole() == pyatspi.ROLE_HEADING \
           or (obj.parent and obj.parent.getRole() == pyatspi.ROLE_MENU):
            return -1

        try:
            attrs = obj.getAttributes()
        except:
            msg = "GECKO: Exception getting attributes for %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            return -1
        for attr in attrs:
            if attr.startswith("level:"):
                return int(attr[6:]) - 1
        return -1

    def showingDescendants(self, parent):
        """Given an accessible object, returns a list of accessible children
        that are actually showing/visible/pursable for flat review. We're
        overriding the default method here primarily to handle enormous
        tree tables (such as the Thunderbird message list) which do not
        manage their descendants.

        Arguments:
        - parent: The accessible which manages its descendants

        Returns a list of Accessible descendants which are showing.
        """

        if not parent:
            return []

        # If this object is not a tree table, if it manages its descendants,
        # or if it doesn't have very many children, let the default script
        # handle it.
        #
        if parent.getRole() != pyatspi.ROLE_TREE_TABLE \
           or parent.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
           or parent.childCount <= 50:
            return super().showingDescendants(parent)

        try:
            table = parent.queryTable()
        except NotImplementedError:
            return []

        descendants = []

        # First figure out what columns are visible as there's no point
        # in examining cells which we know won't be visible.
        # 
        visibleColumns = []
        for i in range(table.nColumns):
            header = table.getColumnHeader(i)
            if self.pursueForFlatReview(header):
                visibleColumns.append(i)
                descendants.append(header)

        if not len(visibleColumns):
            return []

        # Now that we know in which columns we can expect to find visible
        # cells, try to quickly locate a visible row.
        #
        startingRow = 0

        # If we have one or more selected items, odds are fairly good
        # (although not guaranteed) that one of those items happens to
        # be showing. Failing that, calculate how many rows can fit in
        # the exposed portion of the tree table and scroll down.
        #
        selectedRows = table.getSelectedRows()
        for row in selectedRows:
            acc = table.getAccessibleAt(row, visibleColumns[0])
            if self.pursueForFlatReview(acc):
                startingRow = row
                break
        else:
            try:
                tableExtents = parent.queryComponent().getExtents(0)
                acc = table.getAccessibleAt(0, visibleColumns[0])
                cellExtents = acc.queryComponent().getExtents(0)
            except:
                pass
            else:
                rowIncrement = max(1, tableExtents.height / cellExtents.height)
                for row in range(0, table.nRows, rowIncrement):
                    acc = table.getAccessibleAt(row, visibleColumns[0])
                    if acc and self.pursueForFlatReview(acc):
                        startingRow = row
                        break

        # Get everything after this point which is visible.
        #
        for row in range(startingRow, table.nRows):
            acc = table.getAccessibleAt(row, visibleColumns[0])
            if self.pursueForFlatReview(acc):
                descendants.append(acc)
                for col in visibleColumns[1:len(visibleColumns)]:
                    descendants.append(table.getAccessibleAt(row, col))
            else:
                break

        # Get everything before this point which is visible.
        #
        for row in range(startingRow - 1, -1, -1):
            acc = table.getAccessibleAt(row, visibleColumns[0])
            if self.pursueForFlatReview(acc):
                thisRow = [acc]
                for col in visibleColumns[1:len(visibleColumns)]:
                    thisRow.append(table.getAccessibleAt(row, col))
                descendants[0:0] = thisRow
            else:
                break

        return descendants
