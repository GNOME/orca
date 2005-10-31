# Orca
#
# Copyright 2004 Sun Microsystems Inc.
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

import orca.core as core
import orca.a11y as a11y
import orca.braille as braille
import orca.input_event as input_event
import orca.kbd as kbd
import orca.rolenames as rolenames
import orca.speech as speech
import orca.orca as orca

from orca.default import Default

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
    - app: the application to create a script for (should be gcalctool)
    """

    return StarOffice(app)


########################################################################
#                                                                      #
# The StarOffice script class.                                         #
#                                                                      #
########################################################################

class StarOffice(Default):

    def __init__(self, app):
        """Creates a new script for the given application.  Callers
        should use the getScript factory method instead of calling
        this constructor directly.
        
        Arguments:
        - app: the application to create a script for.
        """
        
        Default.__init__(self, app)

        self._display = None
        self._display_txt = None


    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        print "StarOffice: onFocus: called."

        # If this is a focus event for a menu or one of the various
        # types of menu item, then just ignore it. Otherwise pass the
        # event onto the parent class to be processed.

        role = event.source.role
        print "StarOffice: onFocus: role %s" % role

        if (role == rolenames.ROLE_MENU) \
           or (role == rolenames.ROLE_MENU_ITEM) \
           or (role == rolenames.ROLE_CHECK_MENU_ITEM) \
           or (role == rolenames.ROLE_RADIO_MENU_ITEM):
            print "StarOffice: onFocus: just returning."
            return
        else:
            print "StarOffice: onFocus: passing to parent."
            Default.onFocus(self, event)


    def onStateChanged(self, event):
        """Called whenever an object's state changes.  Currently, the
        state changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        print "StarOffice: onStateChanged called."

        # If this is an "armed" object-state-changed event for a menu 
        # or one of the various types of menu item, and this object has 
        # the focus, then set the locus of focus. Otherwise pass the
        # event onto the parent class to be processed.

        print "StarOffice: onStateChanged: event.type %s" % event.type

        if event.type.endswith("armed"):
            role = event.source.role
            print "StarOffice: onFocus: role %s" % role

            if event.source.state.count(core.Accessibility.STATE_FOCUSED) \
               and ((role == rolenames.ROLE_MENU) or \
                    (role == rolenames.ROLE_MENU_ITEM) or \
                    (role == rolenames.ROLE_CHECK_MENU_ITEM) or \
                    (role == rolenames.ROLE_RADIO_MENU_ITEM)):
                print "StatOffice: onStateChanged: setting locus of focus."
                orca.setLocusOfFocus(event, event.source)
                return

        print "StarOffice: onStateChanged: passing to parent."
        Default.onStateChanged(self, event)
