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
import orca.settings as settings

from orca.orca_i18n import _ # for gettext support

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

        # Evolution defines new custom roles. We need to make them known
        # to Orca for Speech and Braille output.

        rolenames.ROLE_CALENDAR_VIEW = "Calendar View"
        rolenames.rolenames[rolenames.ROLE_CALENDAR_VIEW] = \
            rolenames.Rolename(rolenames.ROLE_CALENDAR_VIEW,
                               _("calv"),
                               _("CalendarView"),
                               _("calendar view"))

        rolenames.ROLE_CALENDAR_EVENT = "Calendar Event"
        rolenames.rolenames[rolenames.ROLE_CALENDAR_EVENT] = \
            rolenames.Rolename(rolenames.ROLE_CALENDAR_EVENT,
                               _("cale"),
                               _("CalendarEvent"),
                               _("calendar event"))


    def walkComponentHierarchy(self, obj):
        """Debug routine to print out the hierarchy of components for the
           given object.

        Arguments:
        - obj: the component to start from
        """

        print "<<<<---- Component Hierachy ---->>>>"
        print "START: Obj:", obj.name, obj.role
        parent = obj
        while parent:
            if parent != obj:
                if not parent.parent:
                    print "TOP: Parent:", parent.name, parent.role
                else:
                    print "Parent:", parent.name, parent.role
            parent = parent.parent
        print "<<<<============================>>>>"


    def isDesiredFocusedItem(self, obj, rolesList):
        """Called to determine if the given object and it's hierarchy of
           parent objects, each have the desired roles.

        Arguments:
        - rolesList: the list of desired roles for the components and the
          hierarchy of its parents.

        Returns True if all roles match.
        """

        current = obj
        for i in range(0, len(rolesList)):
            if (current == None) or (current.role != rolesList[i]):
                return False
            current = current.parent

        return True


    # This method tries to detect and handle the following cases:
    # 1) Mail view: current message pane: individual lines of text.
    # 2) Mail view: current message pane: "standard" mail header lines.
    # 3) Mail view: message header list
    # 4) Calendar view: day view: tabbing to day with no appts.
    # 5) Calendar view: day view: tabbing to day with appts.
    # 6) Calendar view: day view: moving with arrow keys.
    # 7) Calendar view: month calendar

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # debug.printObjectEvent(debug.LEVEL_OFF,
        #                        event,
        #                        event.source.toString())

        # self.walkComponentHierarchy(event.source)

        # 1) Mail view: current message pane: individual lines of text.
        #
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

        rolesList = [rolenames.ROLE_TEXT, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_UNKNOWN]
        if self.isDesiredFocusedItem(event.source, rolesList):
            result = atspi.getTextLineAtCaret(event.source)
            braille.displayMessage(result[0])
            speech.speak(result[0])
            orca.setLocusOfFocus(event, event.source, False)
            return


        # 2) Mail view: current message pane: "standard" mail header lines.
        #
        # Check if the focus is in the From:, To:, Subject: or Date: headers
        # of a message in the message area, and that we want to speak all of 
        # the tables cells for that current row.
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

        rolesList = [rolenames.ROLE_TEXT, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_TABLE_CELL]
        if (self.readTableCellRow == True) \
            and (self.isDesiredFocusedItem(event.source, rolesList)):
            obj = event.source.parent.parent
            parent = obj.parent
            if parent.role == rolenames.ROLE_TABLE:
                row = parent.table.getRowAtIndex(obj.index)
                utterances = []
                regions = []
                for i in range(0, parent.table.nColumns):
                    obj = parent.table.getAccessibleAt(row, i)
                    cell = atspi.Accessible.makeAccessible(obj)

                    while cell.childCount:
                        cell = cell.child(0)

                    if cell.role == rolenames.ROLE_TEXT:
                        regions.append(braille.Text(cell))
                        result = atspi.getTextLineAtCaret(cell)
                        utterances.append(result[0])

                braille.displayRegions(regions)
                speech.speakUtterances(utterances)
                orca.setLocusOfFocus(event, event.source, False)
                return


        # 3) Mail view: message header list
        #
        # Check if the focus is in the message header list, and we want to 
        # speak all of the tables cells in the current highlighted message.
        # The role is only brailled for the table cell that currently has
        # focus.
        #
        # Note that the Evolution user can adjust which colums appear in 
        # the message list and the order in which they appear, so that 
        # Orca will just speak the ones that they are interested in.

        rolesList = [rolenames.ROLE_TABLE_CELL, rolenames.ROLE_TREE_TABLE]
        if (self.readTableCellRow == True) \
            and (self.isDesiredFocusedItem(event.source, rolesList)):
            parent = event.source.parent
            row = parent.table.getRowAtIndex(event.source.index)
            savedBrailleVerbosityLevel = \
                settings.getSetting(settings.BRAILLE_VERBOSITY_LEVEL)
            brailleRegions = []
            for i in range(0, parent.table.nColumns):
                obj = parent.table.getAccessibleAt(row, i)
                cell = atspi.Accessible.makeAccessible(obj)
                utterances = self.speechGenerator.getSpeech(cell, False)
                if cell.index == event.source.index:
                    settings.brailleVerbosityLevel = \
                        settings.VERBOSITY_LEVEL_VERBOSE
                else:
                    settings.brailleVerbosityLevel = \
                        settings.VERBOSITY_LEVEL_BRIEF
                [cellRegions, focusedRegion] = \
                    self.brailleGenerator.getBrailleRegions(cell)
                brailleRegions.extend(cellRegions)
                speech.speakUtterances(utterances)

            braille.displayRegions(brailleRegions)
            orca.setLocusOfFocus(event, event.source, False)
            settings.brailleVerbosityLevel = savedBrailleVerbosityLevel
            return

        # 4) Calendar view: day view: tabbing to day with no appts.
        #

        rolesList = [rolenames.ROLE_TABLE, \
                     rolenames.ROLE_CALENDAR_VIEW, \
                     rolenames.ROLE_FILLER]
        if self.isDesiredFocusedItem(event.source, rolesList):
            print ">>>> Calendar view: day view: tabbing to day with no appts <<<<"

        # 5) Calendar view: day view: tabbing to day with appts.
        #

        rolesList = [rolenames.ROLE_CALENDAR_EVENT, \
                     rolenames.ROLE_CALENDAR_VIEW]
        if self.isDesiredFocusedItem(event.source, rolesList):
            print ">>>> Calendar view: day view: tabbing to day with appts <<<<"


        # 6) Calendar view: day view: moving with arrow keys.
        #

        rolesList = [rolenames.ROLE_UNKNOWN, \
                     rolenames.ROLE_TABLE, \
                     rolenames.ROLE_CALENDAR_VIEW]
        if self.isDesiredFocusedItem(event.source, rolesList):
            print ">>>> Calendar view: day view: moving with arrow keys <<<<"


        # 7) Calendar view: month calendar
        #

        rolesList = [rolenames.ROLE_TABLE_CELL, \
                     rolenames.ROLE_CALENDAR, \
                     rolenames.ROLE_PANEL]
        if self.isDesiredFocusedItem(event.source, rolesList):
            print ">>>> Calendar view: month calendar <<<<"


        # For everything else, pass the focus event onto the parent class 
        # to be handled in the default way.
        #
        # Note that this includes table cells if we only want to read the
        # current cell.

        default.Script.onFocus(self, event)
