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

import braille
import rolenames
import orca
import speech

from orca_i18n import _

from default import Default

########################################################################
#                                                                      #
# The factory method for this module.  All Scripts are expected to     #
# have this method, and it is the sole way that instances of scripts   #
# should be created.                                                   #
#                                                                      #
########################################################################

def getScript(app):
    """Factory method to create a new Default script for the given
    application.  This method should be used for creating all
    instances of this script class.

    Arguments:
    - app: the application to create a script for (should be metacity)
    """
    
    return Metacity(app)


########################################################################
#                                                                      #
# The Metacity script class.                                           #
#                                                                      #
########################################################################

class Metacity(Default):

    def __init__(self, app):
        """Creates a new script for the given application.  Callers
        should use the getScript factory method instead of calling
        this constructor directly.
        
        Arguments:
        - app: the application to create a script for.
        """

        Default.__init__(self, app)

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
            Default.onNameChanged(self, event)
            return

        # We have to stop speech, as Metacity has a key grab and we're not
        # getting keys
        #
        speech.stop("default")

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
        
        if found == False:
            text += ". " + _("inaccessible")

        braille.displayMessage(text)
        speech.say("status", text)
        

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
            Default.onTextInserted(self, event)

        
    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """
        if event.source.role != rolenames.ROLE_STATUSBAR:
            Default.onTextDeleted(self, event)


    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """
        if event.source.role != rolenames.ROLE_STATUSBAR:
            Default.onCaretMoved(self, event)
