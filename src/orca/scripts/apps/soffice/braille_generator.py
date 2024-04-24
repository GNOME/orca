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

from orca import braille
from orca import braille_generator
from orca.ax_object import AXObject
from orca.ax_table import AXTable


class BrailleGenerator(braille_generator.BrailleGenerator):

    def _generateRoleName(self, obj, **args):
        if self._script.utilities.isDocument(obj):
            return []

        if self._script.utilities.isFocusableLabel(obj):
            return []

        return super()._generateRoleName(obj, **args)

    def _generateRealTableCell(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateRealTableCell(obj, **args)

        if not AXObject.get_child_count(obj):
            result = super()._generateRealTableCell(obj, **args)
        else:
            result = []
            formatType = args.get('formatType')
            args['formatType'] = 'focused'
            for child in AXObject.iter_children(obj):
                result.extend(self.generate(child, **args))
            args['formatType'] = formatType

        if not self._script.utilities.isSpreadSheetCell(obj):
            return result

        try:
            objectText = self._script.utilities.substring(obj, 0, -1)
            cellName = AXTable.get_label_for_cell_coordinates(obj) \
                or self._script.utilities.spreadSheetCellName(obj)
        except Exception:
            return []

        return [braille.Component(obj, " ".join((objectText, cellName)))]

    def _generateAncestors(self, obj, **args):
        if self._script.get_table_navigator().last_input_event_was_navigation_command():
            return []

        return super()._generateAncestors(obj, **args)

    def _generateIncludeContext(self, obj, **args):
        if self._script.get_table_navigator().last_input_event_was_navigation_command():
            return False

        return super()._generateIncludeContext(obj, **args)

    def generateBraille(self, obj, **args):
        args['useDefaultFormatting'] = self._script.utilities.isNonFocusableList(obj)
        oldRole = self._overrideRole(self._getAlternativeRole(obj, **args), args)

        result = super().generateBraille(obj, **args)

        del args['useDefaultFormatting']
        self._restoreRole(oldRole, args)
        return result
