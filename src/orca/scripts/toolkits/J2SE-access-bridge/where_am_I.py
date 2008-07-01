# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

__id__        = "$Id: J2SE-access-bridge.py 3882 2008-05-07 18:22:10Z richb $"
__version__   = "$Revision: 3882 $"
__date__      = "$Date: 2008-05-07 14:22:10 -0400 (Wed, 07 May 2008) $"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.where_am_I as where_am_I

########################################################################
#                                                                      #
# Custom WhereAmI                                                      #
#                                                                      #
########################################################################

class WhereAmI(where_am_I.WhereAmI):
    def __init__(self, script):
        where_am_I.WhereAmI.__init__(self, script)

    def whereAmI(self, obj, basicOnly):
        """Calls the base class method for basic information and Java
        specific presentation methods for detailed/custom information.
        """

        # If we're in the text area of a spin button, then we'll do the
        # where am I for the spin button.
        #
        if obj and obj.getRole() == pyatspi.ROLE_TEXT:
            spinbox = self._script.getAncestor(obj,
                                               [pyatspi.ROLE_SPIN_BUTTON],
                                               None)
            if spinbox:
                obj = spinbox

        where_am_I.WhereAmI.whereAmI(self, obj, basicOnly)
