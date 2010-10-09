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
        """Returns the document frame that holds the content being shown.
        Overridden here because multiple open messages are not arranged
        in tabs like they are in Firefox."""

        if self.inFindToolbar():
            return Gecko.Utilities.documentFrame(self)

        obj = orca_state.locusOfFocus
        while obj:
            role = obj.getRole()
            if role in [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_EMBEDDED]:
                return obj
            else:
                obj = obj.parent

        return None

    def isEntry(self, obj):
        """Returns True if we should treat this object as an entry."""

        return obj and obj.getRole() == pyatspi.ROLE_ENTRY

    def isPasswordText(self, obj):
        """Returns True if we should treat this object as password text."""

        return obj and obj.getRole() == pyatspi.ROLE_PASSWORD_TEXT

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
