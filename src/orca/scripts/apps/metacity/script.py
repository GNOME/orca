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

"""Custom script for metacity."""

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
# The Metacity script class.                                           #
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
        """Presents information about the metacity status bar."""

        # We have to stop speech, as Metacity has a key grab and we're not
        # getting keys
        #
        speech.stop()

        # If the window was iconified, then obj.name will be surronded by
        # brackets. If this is the case, remove them before comparing the
        # name against the various window names. See bug #522797 for more
        # details.
        #
        objName = obj.name
        if objName and len(objName):
            if objName[0] == "[" and objName[-1] == "]":
                objName = objName[1:-1]

        try:
            text = obj.name
        except:
            text = objName

        self.displayBrailleMessage(text)
        speech.speak(text)

    def onNameChanged(self, event):
        """The status bar in metacity tells us what toplevel window
        will be activated when tab is released.  We will key off the
        text inserted event to determine when to say something, as it
        seems to be the more reliable event.

        Arguments:
        - event: the name changed Event
        """

        # Ignore changes on the status bar.  We handle them in onTextInserted.
        #
        if event.source.getRole() != pyatspi.ROLE_STATUS_BAR:
            default.Script.onNameChanged(self, event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        obj = event.source
        role = obj.getRole()

        # If the status bar is suddenly showing, we need to handle it here
        # because we typically do not get onTextInserted events at that time.
        if role == pyatspi.ROLE_STATUS_BAR and event.detail1:
            self.presentStatusBar(obj)
            return

        default.Script.onShowingChanged(self, event)

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

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        # Ignore changes on the status bar.  We handle them in onTextInserted.
        #
        if event.source.getRole() != pyatspi.ROLE_STATUS_BAR:
            default.Script.onCaretMoved(self, event)
