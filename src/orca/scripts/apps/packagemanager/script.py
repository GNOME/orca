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

"""Custom script for Packagemanager."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.default as default
import orca.orca_state as orca_state
import orca.speech as speech

from orca.orca_i18n import _

from tutorialgenerator import TutorialGenerator

########################################################################
#                                                                      #
# The Packagemanager script class.                                     #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)
        self._isBusy = False

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script."""

        listeners = default.Script.getListeners(self)
        listeners["object:state-changed:busy"] = self.onStateChanged

        return listeners

    def getTutorialGenerator(self):
        """Returns the tutorial generator for this script."""

        return TutorialGenerator(self)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # TODO - JD: This might be a good candidate for a braille "flash
        # message."
        #
        if event.source.getRole() == pyatspi.ROLE_FRAME \
           and event.type.startswith("object:state-changed:busy"):
            # The busy cursor gets set/unset frequently. It's only worth
            # presenting if we're in the Search entry (handles both search
            # and catalog refreshes).
            #
            if not self.isSearchEntry(orca_state.locusOfFocus):
                return

            if event.detail1 == 1 and not self._isBusy:
                # Translators: this is in reference to loading a web page
                # or some other content.
                #
                speech.speak(_("Loading.  Please wait."))
                self._isBusy = True
            elif event.detail1 == 0 and self._isBusy:
                # Translators: this is in reference to loading a web page
                # or some other content.
                #
                speech.speak(_("Finished loading."))
                self._isBusy = False
            return

        default.Script.onStateChanged(self, event)

    def findStatusBar(self, obj):
        """Returns the status bar in the window which contains obj.
        Overridden here because Packagemanager seems to have multiple
        status bars which claim to be SHOWING and VISIBLE. The one we
        want should be displaying text, whereas the others are not.
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
                statusBar = self.findStatusBar(obj[i])

            if statusBar:
                try:
                    text = statusBar.queryText()
                except:
                    pass
                else:
                    if text.characterCount:
                        break

        return statusBar

    def isSearchEntry(self, obj):
        """Attempts to distinguish the Search entry from other accessibles.

        Arguments:
        -obj: the accessible being examined

        Returns True if we think obj is the Search entry.
        """

        # The Search entry is the only entry inside a toolbar. If that
        # should change, we'll need to make our criteria more specific.
        #
        if obj and obj.getRole() == pyatspi.ROLE_TEXT \
           and self.getAncestor( \
            obj, [pyatspi.ROLE_TOOL_BAR], [pyatspi.ROLE_FRAME]):
            return True

        return False
