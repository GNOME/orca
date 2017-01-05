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
        super().__init__(script)

    def _generateRoleName(self, obj, **args):
        if self._script.utilities.isDocument(obj):
            return []

        if self._script.utilities.isFocusableLabel(obj):
            return []

        return super()._generateRoleName(obj, **args)

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

    def _generateRealTableCell(self, obj, **args):
        if not obj.childCount:
            result = super()._generateRealTableCell(obj, **args)
        else:
            result = []
            formatType = args.get('formatType')
            args['formatType'] = 'focused'
            for child in obj:
                result.extend(self.generate(child, **args))
            args['formatType'] = formatType

        if not self._script.utilities.isSpreadSheetCell(obj):
            return result

        try:
            objectText = self._script.utilities.substring(obj, 0, -1)
            cellName = self._script.utilities.spreadSheetCellName(obj)
        except:
            return []

        return [braille.Component(obj, " ".join((objectText, cellName)))]

    def _generateTableCellDelimiter(self, obj, **args):
        return braille.Region(object_properties.TABLE_CELL_DELIMITER_BRAILLE)

    def _generateTableCellRow(self, obj, **args):
        if not self._script.utilities.shouldReadFullRow(obj):
            return self._generateRealTableCell(obj, **args)

        if not self._script.utilities.isSpreadSheetCell(obj):
            return super()._generateTableCellRow(obj, **args)

        cells = self._script.utilities.getShowingCellsInSameRow(obj)
        if not cells:
            return []

        result = []
        for cell in cells:
            cellResult = self._generateRealTableCell(cell, **args)
            if cellResult and result:
                result.append(self._generateTableCellDelimiter(obj, **args))
            result.extend(cellResult)

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

    def _generateAncestors(self, obj, **args):
        if self._script._lastCommandWasStructNav:
            return []

        return super()._generateAncestors(obj, **args)

    def _generateIncludeContext(self, obj, **args):
        if self._script._lastCommandWasStructNav:
            return False

        return super()._generateIncludeContext(obj, **args)

    def generateBraille(self, obj, **args):
        args['useDefaultFormatting'] = self._script.utilities.isNonFocusableList(obj)
        oldRole = self._overrideRole(self._getAlternativeRole(obj, **args), args)

        result = super().generateBraille(obj, **args)

        del args['useDefaultFormatting']
        self._restoreRole(oldRole, args)
        return result
