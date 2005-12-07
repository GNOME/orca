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
import orca.braille as braille
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
        #                        event,
        #                        event.source.toString())

        # When the focus is in the pane containing the lines of an 
        # actual mail message, then, for each of those lines, we 
        # don't want to speak "text", the role of the component that 
        # currently has focus.
        #
        # The situation is determine by checking the roles of the current
        # component, plus its parent, plus its parent. We are looking for
        # "text", "panel" and "unknown". If we find that, then (hopefully)
        # it's a line in the mail message and we get the utterances to
        # speak for that Text.

        if event.source.role == rolenames.ROLE_TEXT:
            parent = event.source.parent
            if parent and (parent.role == rolenames.ROLE_PANEL):
                parent = parent.parent
                if parent and (parent.role == rolenames.ROLE_UNKNOWN):
                    result = atspi.getTextLineAtCaret(event.source)
                    braille.displayMessage(result[0])
                    speech.speak(result[0])
                    orca.setLocusOfFocus(event, event.source, False)
                    return

        # When the focus is in the From:, To:, Subject: or Date: headers
        # of a message in the message area, then we should read the whole
        # row.
        #
        # The situation is determine by checking the roles of the current
        # component, plus its parent, plus its parent. We are looking for
        # "text", "panel" and "table cell". If we find that, then (hopefully)
        # it's a header line in the mail message.
        #
        # For each of the table cells in the current row in the table, we 
        # have to work our way back down the component hierarchy until we 
        # get a component with no children. We then use the role of that 
        # component to determine how to speak its contents.
        #
        # NOTE: the code assumes that there is only one child within each 
        # component and that the final component (with no children) is of 
        # role TEXT.

        if event.source.role == rolenames.ROLE_TEXT:
            parent = event.source.parent
            if parent and (parent.role == rolenames.ROLE_PANEL):
                parent = parent.parent
                if parent and (parent.role == rolenames.ROLE_TABLE_CELL):
                    obj = parent
                    parent = obj.parent
                    if parent.role == rolenames.ROLE_TABLE:
                        row = parent.table.getRowAtIndex(obj.index)
                        utterances = []
                        for i in range(0, parent.table.nColumns):
                            obj = parent.table.getAccessibleAt(row, i)
                            cell = atspi.Accessible.makeAccessible(obj)

                            while cell.childCount:
                                cell = cell.child(0)

                            if cell.role == rolenames.ROLE_TEXT:
                                result = atspi.getTextLineAtCaret(cell)
                                utterances.append(result[0])

                        line = ''.join([''.join(item) for item in utterances])
                        braille.displayMessage(line)
                        speech.speak(line)
                        orca.setLocusOfFocus(event, event.source, False)
                        return


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
                utterances = []
                for i in range(1, parent.table.nColumns):
                    obj = parent.table.getAccessibleAt(row, i)
                    cell = atspi.Accessible.makeAccessible(obj)
                    utterances.append(self.speechGenerator._getSpeechForTableCell(cell, False))

                line = ' '.join([''.join(item) for item in utterances])
                braille.displayMessage(line)
                speech.speak(line)
                orca.setLocusOfFocus(event, event.source, False)
