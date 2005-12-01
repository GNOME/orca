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

import orca.debug as debug
import orca.default as default
import orca.atspi as atspi
import orca.rolenames as rolenames
import orca.orca as orca
import orca.speech as speech

########################################################################
#                                                                      #
# The Evolution script class.                                          #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # debug.printObjectEvent(debug.LEVEL_OFF,
        #                       event,
        #                       event.source.toString())

        # Pass the focus event onto the parent class to be handled in the
        # default way.

        default.Script.onFocus(self, event)

        # If the focus is in the message header list, then we want to speak
        # the remainder of the tables cells in the current highlighted 
        # message (the default.py onFocus() method will have handled the
        # first one above).
        #
        # Note that the Evolution user can adjust which colums appear in 
        # the message list and the order in which they appear, so that 
        # Orca will just speak the ones that they are interested in.

        if event.source.role == rolenames.ROLE_TABLE_CELL:
            parent = event.source.parent
            if parent.role == rolenames.ROLE_TREE_TABLE:
                row = parent.table.getRowAtIndex(event.source.index)
                for i in range(1, parent.table.nColumns):
                    obj = parent.table.getAccessibleAt(row, i)
                    cell = atspi.Accessible.makeAccessible(obj)
                    utterances = self.speechGenerator._getSpeechForTableCell(cell, False)
                    speech.speakUtterances(utterances)
                    orca.setLocusOfFocus(event, event.source, False)
