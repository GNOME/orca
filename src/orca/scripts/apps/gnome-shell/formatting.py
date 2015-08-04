# Orca
#
# Copyright 2013 Igalia, S.L.
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

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013 Igalia, S.L."
__license__   = "LGPL"

import copy
import pyatspi

import orca.formatting
import orca.settings

formatting = {
    'speech': {
        pyatspi.ROLE_MENU_ITEM: {
            'focused': 'expandableState',
            'unfocused': 'labelAndName + pause + unrelatedLabels + pause + menuItemCheckedState + expandableState + availability + ' + orca.formatting.MNEMONIC + ' + accelerator + pause + positionInList',
            'basicWhereAmI': 'ancestors + pause + labelAndName + pause + unrelatedLabels + pause + accelerator + pause + positionInList + ' + orca.formatting.MNEMONIC
            },
    },
    'braille': {
        pyatspi.ROLE_MENU_ITEM: {
            'unfocused': '[Component(obj,\
                                     asString(label + (displayedText or unrelatedLabels) + expandableState + availability) + asString(accelerator),\
                                     indicator=asString(menuItemCheckedState))]'
            },
    }
}

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
