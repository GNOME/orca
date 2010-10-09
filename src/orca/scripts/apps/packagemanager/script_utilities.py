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

import orca.script_utilities as script_utilities

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        script_utilities.Utilities.__init__(self, script)

    #########################################################################
    #                                                                       #
    # Utilities for finding, identifying, and comparing accessibles         #
    #                                                                       #
    #########################################################################

    def isLink(self, obj):
        """Returns True if this is a text object serving as a link.

        Arguments:
        - obj: an accessible
        """

        if not obj:
            return False

        # Images seem to be exposed as ROLE_PANEL and implement very few of
        # the accessibility interfaces.
        #
        if obj.getRole() == pyatspi.ROLE_PANEL and not obj.childCount \
           and obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
           and self.ancestorWithRole(
                obj, [pyatspi.ROLE_HTML_CONTAINER], [pyatspi.ROLE_FRAME]):
            return True

        try:
            text = obj.queryText()
        except:
            return False
        else:
            return self.linkIndex(obj, text.caretOffset) >= 0

    def statusBar(self, obj):
        """Returns the status bar in the window which contains obj.
        Overridden here because Packagemanager seems to have multiple
        status bars which claim to be SHOWING and VISIBLE. The one we
        want should be displaying text, whereas the others are not.

        Arguments:
        - obj: the top-level object (e.g. window, frame, dialog) for
          which the status bar is sought.
        """

        # There are some objects which are not worth descending.
        #
        skipRoles = [pyatspi.ROLE_TREE,
                     pyatspi.ROLE_TREE_TABLE,
                     pyatspi.ROLE_TABLE]

        if obj.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
           or obj.getRole() in skipRoles:
            return

        statusBar = None
        for i in range(obj.childCount - 1, -1, -1):
            if obj[i].getRole() == pyatspi.ROLE_STATUS_BAR:
                statusBar = obj[i]
            elif not obj[i] in skipRoles:
                statusBar = self.statusBar(obj[i])

            if statusBar:
                try:
                    text = statusBar.queryText()
                except:
                    pass
                else:
                    if text.characterCount:
                        break

        return statusBar

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
