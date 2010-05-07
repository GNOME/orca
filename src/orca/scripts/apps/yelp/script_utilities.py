# Orca
#
# Copyright 2010 Joanmarie Diggs.
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

"""Commonly-required utility methods needed by -- and potentially
   customized by -- application and toolkit scripts. They have
   been pulled out from the scripts because certain scripts had
   gotten way too large as a result of including these methods."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import pyatspi

import orca.orca_state as orca_state

import orca.scripts.toolkits.Gecko as Gecko

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities(Gecko.Utilities):

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        Gecko.Utilities.__init__(self, script)

    #########################################################################
    #                                                                       #
    # Utilities for finding, identifying, and comparing accessibles         #
    #                                                                       #
    #########################################################################

    def documentFrame(self):
        """Returns the document frame that holds the content being shown."""

        obj = orca_state.locusOfFocus
        #print "documentFrame", obj

        if not obj:
            return None

        role = obj.getRole()
        if role == pyatspi.ROLE_DOCUMENT_FRAME:
            # We caught a lucky break.
            #
            return obj
        elif role == pyatspi.ROLE_FRAME:
            # The window was just activated. Do not look from the top down;
            # it will cause the yelp hierarchy to become crazy, resulting in
            # all future events having an empty name for the application.
            # See bug 356041 for more information.
            #
            return None
        else:
            if self.inFindToolbar():
                obj = self._script.lastFindContext[0]

            # We might be in some content. In this case, look up.
            #
            return self.ancestorWithRole(obj,
                                         [pyatspi.ROLE_DOCUMENT_FRAME,
                                          pyatspi.ROLE_EMBEDDED],
                                         [pyatspi.ROLE_FRAME])

    def inFindToolbar(self, obj=None):
        """Returns True if the given object is in the Find toolbar.

        Arguments:
        - obj: an accessible object
        """

        if not obj:
            obj = orca_state.locusOfFocus

        if obj and obj.getRole() == pyatspi.ROLE_TEXT \
           and obj.parent.getRole() == pyatspi.ROLE_FILLER:
            return True

        return False

    #########################################################################
    #                                                                       #
    # Utilities for working with the accessible text interface              #
    #                                                                       #
    #########################################################################

    #########################################################################
    #                                                                       #
    # Miscellaneous Utilities                                               #
    #                                                                       #
    #########################################################################
