# Orca
#
# Copyright 2006-2009 Sun Microsystems Inc.
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

"""Custom script for nautilus"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import orca.debug as debug
import orca.messages as messages
import orca.scripts.default as default

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

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        try:
            role = event.source.getRole()
        except:
            return

        # We present the selection changes in the layered pane as a result
        # of the child announcing emitting an event for the state change.
        # And the default script will update the locusOfFocus to the layered
        # pane if nothing is selected.
        if role == pyatspi.ROLE_LAYERED_PANE:
            return

        default.Script.onSelectionChanged(self, event)
