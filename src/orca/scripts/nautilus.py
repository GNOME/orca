# Orca
#
# Copyright 2006-2007 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Custom script for nautilus"""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2006-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.atspi as atspi
import orca.braille as braille
import orca.debug as debug
import orca.default as default
import orca.rolenames as rolenames
import orca.speech as speech

from orca.orca_i18n import _         # for gettext support
from orca.orca_i18n import ngettext  # for ngettext support

########################################################################
#                                                                      #
# The nautilus script class.                                           #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # Path view panel child that is currently checked.
        #
        self.pathChild = None

        # Name of the last folder visited.
        #
        self.oldFolderName = None

    def getItemCount(self, frame):
        """Return a string containing the number of items in the current 
        folder.

        Arguments:
        - frame: the top-level frame for this Nautilus window.

        Return a string containing the number of items in the current 
        folder.
        """

        itemCount = -1
        itemCountString = " "
        allScrollPanes = self.findByRole(frame, rolenames.ROLE_SCROLL_PANE)
        rolesList = [rolenames.ROLE_SCROLL_PANE, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_SPLIT_PANE, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_FRAME, \
                     rolenames.ROLE_APPLICATION]

        # Look for the scroll pane containing the folder items. If this 
        # window is showing an icon view, then the child will be a layered
        # pane. If it's showing a list view, then the child will be a table.
        # Create a string of the number of items in the folder.
        #
        for pane in allScrollPanes:
            if self.isDesiredFocusedItem(pane, rolesList):
                for i in range(0, pane.childCount):
                    child = pane.child(i)
                    if child.role == rolenames.ROLE_LAYERED_PANE:
                        itemCount = child.childCount
                    elif child.role == rolenames.ROLE_TABLE:
                        itemCount = child.table.nRows
                    if itemCount != -1:
                        itemCountString = " " + ngettext("%d item",
                                                         "%d items",
                                                         itemCount) % itemCount
                    break

        return itemCountString

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        debug.printObjectEvent(self.debugLevel,
                               event,
                               event.source.toString())

        if event.source.role == rolenames.ROLE_FRAME:

            # If we've changed folders, announce the new folder name and
            # the number of items in it (see bug #350674).
            #
            # Unfortunately we get two of what appear to be idential events
            # when the accessible name of the frame changes. We only want to
            # speak/braille the new folder name if its different then last
            # time, so, if the Location bar is showing, look to see if the 
            # same toggle button (with the same name) in the "path view" is 
            # checked. If it isn't, then this is a new folder, so announce it.
            #
            # If the Location bar isn't showing, then just do a comparison of
            # the new folder name with the old folder name and if they are 
            # different, announce it. Note that this doesn't do the right 
            # thing when navigating directory hierarchies such as 
            # /path/to/same/same/same.
            #
            allTokens = event.source.name.split(" - ")
            newFolderName = allTokens[0] 

            allPanels = self.findByRole(event.source, rolenames.ROLE_PANEL)
            rolesList = [rolenames.ROLE_PANEL, \
                         rolenames.ROLE_FILLER, \
                         rolenames.ROLE_PANEL, \
                         rolenames.ROLE_TOOL_BAR, \
                         rolenames.ROLE_PANEL, \
                         rolenames.ROLE_FRAME, \
                         rolenames.ROLE_APPLICATION]
            locationBarFound = False
            for panel in allPanels:
                if self.isDesiredFocusedItem(panel, rolesList):
                    locationBarFound = True
                    break

            shouldAnnounce = False
            if locationBarFound:
                for i in range(0, panel.childCount):
                    child = panel.child(i)
                    if child.role == rolenames.ROLE_TOGGLE_BUTTON and \
                       child.state.count(atspi.Accessibility.STATE_CHECKED):
                        if not self.isSameObject(child, self.pathChild):
                            self.pathChild = child
                            shouldAnnounce = True
                            break

            else:
                if self.oldFolderName != newFolderName:
                    shouldAnnounce = True

            if shouldAnnounce:
                string = newFolderName
                string += self.getItemCount(event.source)
                debug.println(debug.LEVEL_INFO, string)
                speech.speak(string)
                braille.displayMessage(string)

            self.oldFolderName = newFolderName
            return

        # Pass the event onto the parent class to be handled in the default way.
        #
        default.Script.onNameChanged(self, event)
