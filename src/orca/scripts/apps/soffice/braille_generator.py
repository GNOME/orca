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

"""Custom script for StarOffice and OpenOffice."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.braille as braille
import orca.braille_generator as braille_generator
import orca.object_properties as object_properties
import orca.settings_manager as settings_manager

_settingsManager = settings_manager.getManager()

class BrailleGenerator(braille_generator.BrailleGenerator):

    # pylint: disable-msg=W0142

    def __init__(self, script):
        braille_generator.BrailleGenerator.__init__(self, script)

    def _generateRoleName(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role != pyatspi.ROLE_DOCUMENT_FRAME:
            result.extend(braille_generator.BrailleGenerator._generateRoleName(
                self, obj, **args))
        return result

    def _generateRowHeader(self, obj, **args):
        """Returns an array of strings that represent the row header for an
        object that is in a table, if it exists.  Otherwise, an empty
        array is returned. Overridden here so that we can get the
        dynamic row header(s).
        """

        newOnly = args.get('newOnly', False)
        rowHeader, columnHeader = \
            self._script.utilities.getDynamicHeadersForCell(obj, newOnly)
        if not rowHeader:
            return []

        text = self._script.utilities.displayedText(rowHeader)
        if text:
            return [text]

        return []

    def _generateColumnHeader(self, obj, **args):
        """Returns an array of strings that represent the column header for an
        object that is in a table, if it exists.  Otherwise, an empty
        array is returned. Overridden here so that we can get the
        dynamic column header(s).
        """

        newOnly = args.get('newOnly', False)
        rowHeader, columnHeader = \
            self._script.utilities.getDynamicHeadersForCell(obj, newOnly)
        if not columnHeader:
            return []

        text = self._script.utilities.displayedText(columnHeader)
        if text:
            return [text]

        return []

    def _generateSpreadSheetCell(self, obj, **args):
        try:
            objectText = self._script.utilities.substring(obj, 0, -1)
            cellName = self._script.utilities.spreadSheetCellName(obj)
        except:
            return []

        return [braille.Component(obj, " ".join((objectText, cellName)))]

    def _generateRealTableCell(self, obj, **args):
        """Get the speech for a table cell. If this isn't inside a
        spread sheet, just return the utterances returned by the default
        table cell speech handler.

        Arguments:
        - obj: the table cell

        Returns a list of utterances to be spoken for the object.
        """
        result = []
        if self._script.utilities.isSpreadSheetCell(obj):
            result.extend(self._generateSpreadSheetCell(obj, **args))
        else:
            # Check to see how many children this table cell has. If it's
            # just one (or none), then pass it on to the superclass to be
            # processed.
            #
            # If it's more than one, then get the speech for each child,
            # and call this method again.
            #
            if obj.childCount <= 1:
                result.extend(braille_generator.BrailleGenerator.\
                              _generateRealTableCell(self, obj, **args))
            else:
                for child in obj:
                    cellResult = self._generateRealTableCell(child, **args)
                    if cellResult and result and self._mode == 'braille':
                        result.append(braille.Region(
                            object_properties.TABLE_CELL_DELIMITER_BRAILLE))
                    result.extend(cellResult)
        return result

    def _generateTableCellRow(self, obj, **args):
        """Get the speech for a table cell row or a single table cell
        if settings.readTableCellRow is False. If this isn't inside a
        spread sheet, just return the utterances returned by the default
        table cell speech handler.

        Arguments:
        - obj: the table cell

        Returns a list of utterances to be spoken for the object.
        """
        result = []
        if self._script.utilities.isSpreadSheetCell(obj):
            # Adding in a check here to make sure that the parent is a
            # valid table. It's possible that the parent could be a
            # table cell too (see bug #351501).
            #
            parent = obj.parent
            parentTable = parent.queryTable()
            if _settingsManager.getSetting('readTableCellRow') and parentTable:
                index = self._script.utilities.cellIndex(obj)
                row = parentTable.getRowAtIndex(index)
                column = parentTable.getColumnAtIndex(index)
                # This is an indication of whether we should present all the
                # table cells (the user has moved focus up or down a row),
                # or just the current one (focus has moved left or right in
                # the same row).
                #
                presentAll = True
                if "lastRow" in self._script.pointOfReference and \
                    "lastColumn" in self._script.pointOfReference:
                    pointOfReference = self._script.pointOfReference
                    presentAll = \
                        (self._mode == 'braille') \
                        or ((pointOfReference["lastRow"] != row) \
                            or ((row == 0 or row == parentTable.nRows-1) \
                                and pointOfReference["lastColumn"] == column))
                if presentAll:
                    [startIndex, endIndex] = \
                        self._script.utilities.getTableRowRange(obj)
                    for i in range(startIndex, endIndex):
                        cell = parentTable.getAccessibleAt(row, i)
                        showing = cell.getState().contains( \
                                      pyatspi.STATE_SHOWING)
                        if showing:
                            cellResult = self._generateRealTableCell(cell,
                                                                     **args)
                            if cellResult and result \
                               and self._mode == 'braille':
                                result.append(braille.Region(
                                    object_properties.TABLE_CELL_DELIMITER_BRAILLE))
                            result.extend(cellResult)
                else:
                    result.extend(self._generateRealTableCell(obj, **args))
            else:
                result.extend(self._generateRealTableCell(obj, **args))
        else:
            result.extend(
                braille_generator.BrailleGenerator._generateTableCellRow(
                    self, obj, **args))
        return result

    def _generateChildTab(self, obj, **args):
        """If we are in the slide presentation scroll pane, also announce the
        current page tab. See bug #538056 for more details.
        """
        result = []
        rolesList = [pyatspi.ROLE_SCROLL_PANE, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_ROOT_PANE, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if self._script.utilities.hasMatchingHierarchy(obj, rolesList):
            for child in obj.parent:
                if child.getRole() == pyatspi.ROLE_PAGE_TAB_LIST:
                    for tab in child:
                        eventState = tab.getState()
                        if eventState.contains(pyatspi.STATE_SELECTED):
                            args['role'] = tab.getRole()
                            result.extend(self.generate(tab, **args))
        return result

    def generateBraille(self, obj, **args):
        result = []
        args['useDefaultFormatting'] = \
            ((obj.getRole() == pyatspi.ROLE_LIST) \
                and (not obj.getState().contains(pyatspi.STATE_FOCUSABLE)))
        result.extend(braille_generator.BrailleGenerator.\
                          generateBraille(self, obj, **args))
        del args['useDefaultFormatting']
        return result
