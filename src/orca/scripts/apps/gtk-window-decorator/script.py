# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

"""Custom script for gtk-window-decorator."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.messages as messages
import orca.scripts.default as default
import orca.speech as speech
import pyatspi

########################################################################
#                                                                      #
# The gtk-window-decorator script class.                               #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

    def presentStatusBar(self, obj):
        """Presents information about the gtk-window-decorator status
        bar.

        Arguments:
        - obj: the accessible status bar.
        """

        objName = obj.name
        if not (objName and len(objName)):
            return

        # gtk-window-decorator sometimes abbreviates the names, placing
        # '...' at the end.  Strip the ending off so that we can compare
        # the beginning of the window names with the objName.
        #
        index = objName.rfind('...')
        if index >= 0:
            objName = objName[0:index]

        # Do we know about this window?  Traverse through our list of apps
        # and go through the toplevel windows in each to see if we know
        # about this one.  If we do, it's accessible.  If we don't, it is
        # not.
        #
        found = False
        for app in self.utilities.knownApplications():
            for child in app:
                if child.name.startswith(objName):
                    found = True
                    break

        text = obj.name
        if not found:
            text += ". " + messages.INACCESSIBLE

        self.displayBrailleMessage(text)
        speech.stop()
        speech.speak(text)

    def onNameChanged(self, event):
        """The status bar in gtk-window-decorator tells us what toplevel
        window will be activated when Alt is released.  We will key off
        the text inserted event to determine when to say something, as it
        seems to be the more reliable event.

        Arguments:
        - event: the name changed Event
        """

        # Ignore changes on the status bar.  We handle them in onTextInserted.
        #
        if event.source.getRole() != pyatspi.ROLE_STATUS_BAR:
            default.Script.onNameChanged(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.  This seems to
        be the most reliable event to let us know something is changing.

        Arguments:
        - event: the Event
        """

        if event.source.getRole() != pyatspi.ROLE_STATUS_BAR:
            default.Script.onTextInserted(self, event)

        self.presentStatusBar(event.source)

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

        # Ignore changes on the status bar.  We handle them in onTextInserted.
        #
        if event.source.getRole() != pyatspi.ROLE_STATUS_BAR:
            default.Script.onTextDeleted(self, event)
