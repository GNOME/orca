# Orca
#
# Copyright 2006-2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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

"""Custom formatting for Java Swing."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc., "  \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import copy

import pyatspi

import orca.formatting

# pylint: disable-msg=C0301

formatting = {
    'speech': {
        # In Java, tree objects are labels, so we need to look at their
        # states in order to tell whether they are expanded or collapsed.
        #
        pyatspi.ROLE_LABEL: {
            'unfocused': '(displayedText or roleName) + expandableState + numberOfChildren',
            'focused': 'expandableState + numberOfChildren',
            'basicWhereAmI': '(displayedText or roleName) + expandableState + numberOfChildren + nodeLevel',
            },
    },
    'braille': {
        pyatspi.ROLE_LABEL: {
            'unfocused': '[Component(obj, asString(displayedText + expandableState))]'
            },
    }
}

class Formatting(orca.formatting.Formatting):
    def __init__(self, script):
        orca.formatting.Formatting.__init__(self, script)
        self.update(copy.deepcopy(formatting))
