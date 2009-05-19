# Orca
#
# Copyright 2006-2009 Sun Microsystems Inc.
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

"""Custom formatting for Gecko."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.formatting

formatting = {
    'speech': {
        pyatspi.ROLE_ALERT: {
            'unfocused': 'expandedEOCs or (labelAndName + unrelatedLabels)'
            },
        pyatspi.ROLE_DOCUMENT_FRAME: {
            'unfocused': 'name + roleName'
            },
        pyatspi.ROLE_LIST: {
            'unfocused': 'labelOrName + multiselectableState + numberOfChildren'
            },
    }
}

class Formatting(orca.formatting.Formatting):

    # pylint: disable-msg=W0142

    def __init__(self, script):
        orca.formatting.Formatting.__init__(self, script)
        self.update(formatting)
        # This is a copy of the default formatting, which we will
        # use for ARIA widgets.
        #
        self._defaultFormatting = orca.formatting.Formatting(script)

    def getFormat(self, dictType, **args):
        # ARIA widgets get treated like regular default widgets.
        #
        if args.get('isAria', False):
            return self._defaultFormatting.getFormat(dictType, **args)
        else:
            return orca.formatting.Formatting.getFormat(self, dictType, **args)
