# Orca
#
# Copyright 2005 Sun Microsystems Inc.
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

import orca.braille as braille
import orca.default as default
import orca.rolenames as rolenames
import orca.orca as orca
import orca.speech as speech

from orca.orca_i18n import _

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

        self.listeners["object:property-change:accessible-name"] = \
            self.onNameChanged 
        self.listeners["object:state-changed:visible"] = \
            self.onVisibilityChanged


    def onNameChanged(self, event):
        """The status bar in metacity tells us what toplevel window will be
        activated when tab is released.

        Arguments:
        - event: the name changed Event
        """

        # If it's not the statusbar's name changing, ignore it
        #
        if event.source.role != rolenames.ROLE_STATUSBAR:
            default.Script.onNameChanged(self, event)
            return

        # We have to stop speech, as Metacity has a key grab and we're not
        # getting keys
        #
        speech.stop()

        name = event.source.name

        # Do we know about this window?  Traverse through our list of apps
        # and go through the toplevel windows in each to see if we know
        # about this one.  If we do, it's accessible.  If we don't, it is
        # not.
        #
        found = False
        for app in orca.apps:
            i = 0
            while i < app.childCount:
                win = app.child(i)
                if win is None:
                    print "app error " + app.name
                elif win.name == name:
                    found = True
                i = i + 1

        text = name
        
        if not found:
            text += ". " + _("inaccessible")

        braille.displayMessage(text)
        speech.speak(text)
        

    def onVisibilityChanged(self, event):
        """The status bar in metacity tells us what toplevel window will be
        activated when tab is released.

        Arguments:
        - event: the object:state-changed:visible Event
        """

        # If it's not the statusbar's name changing, ignore it
        #
        if event.source.role != rolenames.ROLE_STATUSBAR:
            return

        orca.setLocusOfFocus(event, event.source)


    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """
        if event.source.role != rolenames.ROLE_STATUSBAR:
            default.Script.onTextInserted(self, event)

        
    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """
        if event.source.role != rolenames.ROLE_STATUSBAR:
            default.Script.onTextDeleted(self, event)


    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """
        if event.source.role != rolenames.ROLE_STATUSBAR:
            default.Script.onCaretMoved(self, event)
