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

"""Custom script for nautilus"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import orca.braille as braille
import orca.debug as debug
import orca.default as default
import orca.speech as speech

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

    def isActivatableEvent(self, event):
        """Returns True if the given event is one that should cause this
        script to become the active script.  This is only a hint to
        the focus tracking manager and it is not guaranteed this
        request will be honored.  Note that by the time the focus
        tracking manager calls this method, it thinks the script
        should become active.  This is an opportunity for the script
        to say it shouldn't.
        """

        # Let's make sure we have an active window if focus on an icon
        # changes. Focus can change when we don't have an an active
        # window when someone deletes a file from a shell and nautilus
        # happens to be showing the directory where that file exists.
        # See bug #568696.  We'll be specific here so as to avoid
        # looking at the child states for every single event from
        # nautilus, which happens to be an event-happy application.
        #
        if event and event.type == "focus:" \
           and event.source.getRole() == pyatspi.ROLE_ICON:
            shouldActivate = False
            for child in self.app:
                if child.getState().contains(pyatspi.STATE_ACTIVE):
                    shouldActivate = True
                    break
        else:
            shouldActivate = True

        if not shouldActivate:
            debug.println(debug.LEVEL_FINE,
                          "%s does not want to become active" % self.name)

        return shouldActivate

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
        allScrollPanes = self.findByRole(frame, pyatspi.ROLE_SCROLL_PANE)
        rolesList = [pyatspi.ROLE_SCROLL_PANE, \
                     pyatspi.ROLE_FILLER, \
                     pyatspi.ROLE_FILLER, \
                     pyatspi.ROLE_SPLIT_PANE, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]

        # Look for the scroll pane containing the folder items. If this
        # window is showing an icon view, then the child will be a layered
        # pane. If it's showing a list view, then the child will be a table.
        # Create a string of the number of items in the folder.
        #
        for pane in allScrollPanes:
            if self.isDesiredFocusedItem(pane, rolesList):
                for i in range(0, pane.childCount):
                    child = pane.getChildAtIndex(i)
                    if child.getRole() == pyatspi.ROLE_LAYERED_PANE:
                        itemCount = child.childCount
                    elif child.getRole() == pyatspi.ROLE_TABLE:
                        try:
                            itemCount = child.queryTable().nRows
                        except NotImplementedError:
                            itemCount = -1
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
                               debug.getAccessibleDetails(event.source))

        if event.source.getRole() == pyatspi.ROLE_FRAME:

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

            allPanels = self.findByRole(event.source, pyatspi.ROLE_PANEL)
            rolesList = [pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_FILLER, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_TOOL_BAR, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_FRAME, \
                         pyatspi.ROLE_APPLICATION]
            locationBarFound = False
            for panel in allPanels:
                if self.isDesiredFocusedItem(panel, rolesList):
                    locationBarFound = True
                    desiredPanel = panel
                    break

            shouldAnnounce = False
            if locationBarFound:
                for i in range(0, desiredPanel.childCount):
                    child = desiredPanel.getChildAtIndex(i)
                    if child.getRole() == pyatspi.ROLE_TOGGLE_BUTTON and \
                       child.getState().contains(pyatspi.STATE_CHECKED):
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

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # If we've received an "object:state-changed:showing" event for the
        # poorly named gtk-edit toggle button, then just return. We will have
        # spoken the information for this component with the previously
        # received "object:state-changed:focused" event. For all other events,
        # just let the parent class handle it. See bug #371637 for more
        # details.
        #
        if event.type.startswith("object:state-changed:showing"):
            rolesList = [pyatspi.ROLE_LABEL, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_FILLER, \
                         pyatspi.ROLE_FILLER, \
                         pyatspi.ROLE_FILLER, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_TOOL_BAR, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_FRAME, \
                         pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel, "nautilus.onStateChanged - " \
                              + "Location: label.")
                return

        default.Script.onStateChanged(self, event)
