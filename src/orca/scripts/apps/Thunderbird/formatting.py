# Orca
#
# Copyright 2010 Joanmarie Diggs.
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

"""Custom formatting for Thunderbird."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

# pylint: disable-msg=C0301

import copy
import pyatspi

import orca.formatting
import orca.scripts.toolkits.Gecko.formatting as GeckoFormatting

formatting = {
    'speech': {
        pyatspi.ROLE_DOCUMENT_FRAME: {
            'basicWhereAmI': 'label + readOnly + textRole + textContent + anyTextSelection + ' + orca.formatting.MNEMONIC,
            'detailedWhereAmI': 'label + readOnly + textRole + textContentWithAttributes + anyTextSelection + ' + orca.formatting.MNEMONIC + ' + ' + orca.formatting.TUTORIAL
            },
        }
    }

class Formatting(GeckoFormatting.Formatting):
    def __init__(self, script):
        GeckoFormatting.Formatting.__init__(self, script)
        self.update(copy.deepcopy(formatting))
        self._defaultFormatting = orca.formatting.Formatting(script)

    def getFormat(self, **args):
        if args.get('useDefaultFormatting', False):
            return self._defaultFormatting.getFormat(**args)
        else:
            return GeckoFormatting.Formatting.getFormat(self, **args)
