# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Custom formatting for OpenOffice and StarOffice."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

# pylint: disable-msg=C0301

import copy

import pyatspi

import orca.formatting
import orca.settings

formatting = {
    'speech': {
        # Get rid of unselectedCell because we don't run into that in OOo
        # and we'd end up always speaking "not selected" for all table cells.
        #
        'suffix': {
            'focused': '[]',
            'unfocused': 'newNodeLevel + ' + orca.formatting.TUTORIAL,
            'basicWhereAmI': orca.formatting.TUTORIAL + ' + description',
            'detailedWhereAmI' : '[]'
            },
        pyatspi.ROLE_COMBO_BOX: {
            'focused': 'name + positionInList + availability',
            'unfocused': 'labelAndName + roleName + positionInList + availability'
            },
        pyatspi.ROLE_LABEL: {
            'focused': 'expandableState + availability',
            'unfocused': 'name + allTextSelection + expandableState + availability + positionInList',
            'basicWhereAmI': 'roleName + name + positionInList + expandableState + (nodeLevel or nestingLevel)'
            },
        pyatspi.ROLE_PUSH_BUTTON: {
            'unfocused': 'labelAndName + roleName + toggleState + availability',
            'focused': 'labelAndName + toggleState'
            },
        pyatspi.ROLE_TOGGLE_BUTTON: {
            'focused': 'labelAndName + toggleState'
            },
        pyatspi.ROLE_TABLE_CELL: {
            'focused': '(tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState + (expandableState and (expandableState + numberOfChildren))',
            'unfocused': 'endOfTableIndicator + tableCellRow',
            'basicWhereAmI': 'parentRoleName + columnHeader + rowHeader + roleName + cellCheckedState + (realActiveDescendantDisplayedText or imageDescription + image) + columnAndRow + expandableState + nodeLevel',
            'detailedWhereAmI': 'parentRoleName + columnHeader + rowHeader + roleName + cellCheckedState + (realActiveDescendantDisplayedText or imageDescription + image) + columnAndRow + tableCellRow + expandableState + nodeLevel'
            },
        'ROLE_SPREADSHEET_CELL': {
            # We treat spreadsheet cells differently from other table cells in
            # whereAmI.
            #
            'basicWhereAmI': 'roleName + column + columnHeader + row + rowHeader + (textContent or spreadSheetCell) + anyTextSelection'
            },
    },
    'braille': {
        pyatspi.ROLE_LIST: {
            'unfocused': '[Component(obj,\
                                     asString(labelOrName + roleName + required))]'
        },
        pyatspi.ROLE_SCROLL_PANE: {
            'unfocused': 'asPageTabOrScrollPane\
                          + (childTab\
                             and ([Region(" ")] + childTab) or [])'
        }
    }
}

if orca.settings.useExperimentalSpeechProsody:
    formatting['speech']['ROLE_SPREADSHEET_CELL']['basicWhereAmI'] = \
        'roleName + pause + column + pause + columnHeader + pause + row + pause + rowHeader + pause + (textContent or spreadSheetCell) + pause + anyTextSelection + pause'
    formatting['speech'][pyatspi.ROLE_TABLE_CELL]['focused'] = \
        '((tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState) + pause + (expandableState and (expandableState + pause + numberOfChildren + pause))'
    formatting['speech'][pyatspi.ROLE_TABLE_CELL]['unfocused'] = \
        'endOfTableIndicator + pause + tableCellRow + pause'
    formatting['speech'][pyatspi.ROLE_TABLE_CELL]['basicWhereAmI'] = \
        'parentRoleName + pause + columnHeader + pause + rowHeader + pause + roleName + pause + cellCheckedState + pause + (realActiveDescendantDisplayedText or imageDescription + image) + pause + columnAndRow + pause + expandableState + pause + nodeLevel + pause'
    formatting['speech'][pyatspi.ROLE_TABLE_CELL]['detailedWhereAmI'] = \
        'parentRoleName + pause + columnHeader + pause + rowHeader + pause + roleName + pause + cellCheckedState + pause + (realActiveDescendantDisplayedText or imageDescription + image) + pause + columnAndRow + pause + tableCellRow + pause + expandableState + pause + nodeLevel + pause'

class Formatting(orca.formatting.Formatting):
    def __init__(self, script):
        orca.formatting.Formatting.__init__(self, script)
        self.update(copy.deepcopy(formatting))
        self._defaultFormatting = orca.formatting.Formatting(script)

    def getFormat(self, **args):
        if args.get('useDefaultFormatting', False):
            return self._defaultFormatting.getFormat(**args)
        else:
            return orca.formatting.Formatting.getFormat(self, **args)
