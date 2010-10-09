# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Custom structural navigation for the StarOffice/OpenOffice."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.structural_navigation as structural_navigation
import orca.settings as settings
import orca.speech as speech

from orca.orca_i18n import _

########################################################################
#                                                                      #
# Custom Structural Navigation                                         #
#                                                                      #
########################################################################

class StructuralNavigation(structural_navigation.StructuralNavigation):

    def __init__(self, script, enabledTypes, enabled):
        """StarOffice/OpenOffice specific Structural Navigation."""
        structural_navigation.StructuralNavigation.__init__(self,
                                                            script,
                                                            enabledTypes,
                                                            enabled)

    def _isHeader(self, obj):
        """Returns True if the table cell is a header.

        Arguments:
        - obj: the accessible table cell to examine.
        """

        if not obj:
            return False

        if obj.getRole() in [pyatspi.ROLE_TABLE_COLUMN_HEADER,
                             pyatspi.ROLE_TABLE_ROW_HEADER]:
            return True

        # Check for dynamic row and column headers.
        #
        try:
            table = obj.parent.queryTable()
        except:
            return False

        # Make sure we're in the correct table first.
        #
        if not (table in self._script.dynamicRowHeaders or
                table in self._script.dynamicColumnHeaders):
            return False

        [row, col] = self.getCellCoordinates(obj)
        return (row == self._script.dynamicColumnHeaders.get(table) \
                or col == self._script.dynamicRowHeaders.get(table))

    def _tableCellPresentation(self, cell, arg):
        """Presents the table cell or indicates that one was not found.
        Overridden here to avoid the double-speaking of the dynamic
        headers.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        # TODO - JD: This really should be dealt with via a formatting
        # string, once we work out how to implement formatting strings
        # throughout the Gecko code. In the meantime, this method will
        # result in a consistent user experience between applications.
        #
        if not cell:
            return

        if settings.speakCellHeaders:
            self._presentCellHeaders(cell, arg)

        [obj, characterOffset] = self._getCaretPosition(cell)
        self._setCaretPosition(obj, characterOffset)
        self._script.updateBraille(obj)

        blank = self._isBlankCell(cell)
        if not blank:
            for child in cell:
                speech.speak(self._script.utilities.displayedText(child))
        else:
            # Translators: "blank" is a short word to mean the
            # user has navigated to an empty line.
            #
            speech.speak(_("blank"))

        if settings.speakCellCoordinates:
            [row, col] = self.getCellCoordinates(cell)
            # Translators: this represents the (row, col) position of
            # a cell in a table.
            #
            self._script.presentMessage(_("Row %(row)d, column %(column)d.") \
                                       % {"row" : row + 1, "column" : col + 1})

        spanString = self._getCellSpanInfo(cell)
        if spanString and settings.speakCellSpan:
            self._script.presentMessage(spanString)
