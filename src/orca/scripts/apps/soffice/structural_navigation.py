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

import orca.messages as messages
import orca.structural_navigation as structural_navigation
import orca.settings as settings
import orca.speech as speech

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
            speech.speak(messages.BLANK)

        if settings.speakCellCoordinates:
            [row, col] = self.getCellCoordinates(cell)
            self._script.presentMessage(messages.TABLE_CELL_COORDINATES \
                                       % {"row" : row + 1, "column" : col + 1})

        rowspan, colspan = self._script.utilities.rowAndColumnSpan(cell)
        spanString = messages.cellSpan(rowspan, colspan)
        if spanString and settings.speakCellSpan:
            self._script.presentMessage(spanString)

    def _getCaretPosition(self, obj):
        try:
            text = obj.queryText()
        except:
            if obj and obj.childCount:
                return self._getCaretPosition(obj[0])

        return obj, 0
