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


    def readPageTab(self, tab):
        """Speak/Braille the given page tab. The speech verbosity is set
           to VERBOSITY_LEVEL_BRIEF for this operation and then restored
           to its previous value on completion.

        Arguments:
        - tab: the page tab to speak/braille.
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        savedSpeechVerbosityLevel = \
            settings.getSetting(settings.SPEECH_VERBOSITY_LEVEL)
        settings.speechVerbosityLevel = settings.VERBOSITY_LEVEL_BRIEF
        utterances = speechGen.getSpeech(tab, False)
        speech.speakUtterances(utterances)
        settings.speechVerbosityLevel = savedSpeechVerbosityLevel

        brailleRegions = []
        [cellRegions, focusedRegion] = brailleGen.getBrailleRegions(tab)
        brailleRegions.extend(cellRegions)
        braille.displayRegions(brailleRegions)


    def getTimeForCalRow(self, row, noIncs):
        """Return a string equivalent to the time of the given row in
           the calendar day view. Each calendar row is equivalent to
           a certain time interval (from 5 minutes upto 1 hour), with 
           time (row 0) starting at 12 am (midnight).

        Arguments:
        - row: the row number.
        - noIncs: the number of equal increments that the 24 hour period 
                  is divided into.

        Returns the time as a string.
        """

        totalMins = timeIncrements[noIncs] * row

        if totalMins < 720:
            suffix = 'ay em'
        else:
            totalMins -= 720
            suffix = 'pee em'

        hrs = hours[totalMins / 60]
        mins = minutes[totalMins % 60]

        return hrs + ' ' + mins + ' ' + suffix


    # This method tries to detect and handle the following cases:
    # 1) Mail view: current message pane: individual lines of text.
    # 2) Mail view: current message pane: "standard" mail header lines.
    # 3) Mail view: message header list
    # 4) Calendar view: day view: tabbing to day with appts.
    # 5) Calendar view: day view: moving with arrow keys.
    # 6) Preferences Dialog: options list.

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        debug.printObjectEvent(debug.LEVEL_FINEST,
                               event,
                               event.source.toString())

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
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - mail view: current message pane: " \
                      + "individual lines of text.")

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
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - mail view: current message pane: " \
                      + "standard mail header lines.")

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
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - mail view: message header list.")

            parent = event.source.parent
            row = parent.table.getRowAtIndex(event.source.index)
            savedBrailleVerbosityLevel = \
                settings.getSetting(settings.BRAILLE_VERBOSITY_LEVEL)
            brailleRegions = []
            for i in range(0, parent.table.nColumns):
                obj = parent.table.getAccessibleAt(row, i)
                cell = atspi.Accessible.makeAccessible(obj)
                utterances = speechGen.getSpeech(cell, False)
                if cell.index == event.source.index:
                    settings.brailleVerbosityLevel = \
                        settings.VERBOSITY_LEVEL_VERBOSE
                else:
                    settings.brailleVerbosityLevel = \
                        settings.VERBOSITY_LEVEL_BRIEF
                [cellRegions, focusedRegion] = \
                    brailleGen.getBrailleRegions(cell)
                brailleRegions.extend(cellRegions)
                speech.speakUtterances(utterances)

            braille.displayRegions(brailleRegions)
            orca.setLocusOfFocus(event, event.source, False)
            settings.brailleVerbosityLevel = savedBrailleVerbosityLevel
            return


        # 4) Calendar view: day view: tabbing to day with appts.
        #
        # If the focus is in the Calendar Day View on an appointment, then
        # provide the user with useful feedback. First we get the current
        # date and appointment summary from the parent. This is then followed
        # by getting the information on the current appointment.
        #
        # The start time for the appointment is determined by detecting the 
        # equivalent child in the parent Calendar View's table has the same 
        # y position on the screen.
        #
        # The end time for the appointment is determined by using the height
        # of the current appointment component divided by the height of a 
        # single child in the parent Calendar View's table
        #
        # Both of these time values depend upon the value of a time increment
        # which is determined by the number of children in the parent Calendar
        # View's table.

        rolesList = [rolenames.ROLE_CALENDAR_EVENT, \
                     rolenames.ROLE_CALENDAR_VIEW]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - calendar view: day view: " \
                      + "tabbing to day with appts.")

            brailleRegions = []
            parent = event.source.parent
            utterances = speechGen.getSpeech(parent, False)
            [cellRegions, focusedRegion] = \
                    brailleGen.getBrailleRegions(parent)
            brailleRegions.extend(cellRegions)
            speech.speakUtterances(utterances)

            apptExtents = event.source.component.getExtents(0)

            for i in range(0, parent.childCount):
                child = parent.child(i)
                if (child.role == rolenames.ROLE_TABLE):
                    noRows = child.table.nRows
                    for j in range(0, noRows):
                        row = child.table.getRowAtIndex(j)
                        obj = child.table.getAccessibleAt(row, 0)
                        appt = atspi.Accessible.makeAccessible(obj)
                        extents = appt.component.getExtents(0)
                        if extents.y == apptExtents.y:
                            utterances = speechGen.getSpeech(event.source, \
                                                             False)
                            [apptRegions, focusedRegion] = \
                                brailleGen.getBrailleRegions(event.source)
                            brailleRegions.extend(apptRegions)
                            speech.speakUtterances(utterances)

                            startTime = 'Start time ' + \
                                self.getTimeForCalRow(j, noRows)
                            brailleRegions.append(braille.Region(startTime))
                            speech.speak(startTime)

                            apptLen = apptExtents.height / extents.height
                            endTime = 'End time ' + \
                                self.getTimeForCalRow(j + apptLen, noRows)
                            brailleRegions.append(braille.Region(endTime))
                            speech.speak(endTime)
                            braille.displayRegions(brailleRegions)
                            return


        # 5) Calendar view: day view: moving with arrow keys.
        #
        # If the focus is in the Calendar Day View, check to see if there
        # are any appointments starting at the current time. If there are, 
        # then provide the user with useful feedback for that appointment,
        # otherwise output the current time and state that there are no
        # appointments.
        #
        # First get the y position of the current table entry. Then compare
        # this will any Calendar Events in the parent Calendar View. If their
        # y position is the same, then speak that information.
        #
        # The end time for the appointment is determined by using the height
        # of the current appointment component divided by the height of a
        # single child in the parent Calendar View's table
        #
        # Both of these time values depend upon the value of a time increment
        # which is determined by the number of children in the parent Calendar
        # View's table.

        rolesList = [rolenames.ROLE_UNKNOWN, \
                     rolenames.ROLE_TABLE, \
                     rolenames.ROLE_CALENDAR_VIEW]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - calendar view: day view: " \
                      + "moving with arrow keys.")

            brailleRegions = []
            index = event.source.index
            parent = event.source.parent
            calendarView = event.source.parent.parent
            extents = event.source.component.getExtents(0)
            noRows = parent.table.nRows
            found = False

            for i in range(0, calendarView.childCount):
                child = calendarView.child(i)
                if (child.role == rolenames.ROLE_CALENDAR_EVENT):
                    apptExtents = child.component.getExtents(0)

                    if extents.y == apptExtents.y:
                        utterances = speechGen.getSpeech(child, False)
                        [apptRegions, focusedRegion] = \
                            brailleGen.getBrailleRegions(child)
                        brailleRegions.extend(apptRegions)
                        speech.speakUtterances(utterances)

                        startTime = 'Start time ' + \
                            self.getTimeForCalRow(index, noRows)
                        brailleRegions.append(braille.Region(startTime))
                        speech.speak(startTime)

                        apptLen = apptExtents.height / extents.height
                        endTime = 'End time ' + \
                            self.getTimeForCalRow(index + apptLen, noRows)
                        brailleRegions.append(braille.Region(endTime))
                        speech.speak(endTime)
                        braille.displayRegions(brailleRegions)
                        found = True

            if found == False:
                startTime = 'Start time ' + self.getTimeForCalRow(index, noRows)
                brailleRegions.append(braille.Region(startTime))
                speech.speak(startTime)

                utterance = "No appointments."
                speech.speak(utterance)
                brailleRegions.append(braille.Region(utterance))
                braille.displayRegions(brailleRegions)

            return

        # 6) Preferences Dialog: options list.
        #
        # Check if the focus is in one of the various options on the left
        # side of the Preferences dialog. If it is, then we just want to
        # speak the name of the page we are currently on.
        #
        # Even though it looks like the focus is on one of the page tabs
        # in this dialog, it's possible that it's actually on a table cell,
        # within a table which is contained within a scroll pane. We check
        # for this my looking for a component hierarchy of "table cell",
        # "table", "unknown" and "scroll pane".
        #
        # If this is the case, then we get the parent of the scroll pane
        # and look to see if one of its other children is a "page tab list".
        # If that's true, then we get the Nth child, when N is the index of
        # the initial table cell minus 1. We double check that this is a
        # "page tab", then if so, speak and braille that component.
        #
        # NOTE: assumes there is only one "page tab list" in the "filler"
        # component.

        rolesList = [rolenames.ROLE_TABLE_CELL, \
                     rolenames.ROLE_TABLE, \
                     rolenames.ROLE_UNKNOWN, \
                     rolenames.ROLE_SCROLL_PANE]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - preferences dialog: " \
                      + "table cell in options list.")

            index = event.source.index
            obj = event.source.parent.parent.parent
            parent = obj.parent
            if parent.role == rolenames.ROLE_FILLER:
                for i in range(0, parent.childCount):
                    child = parent.child(i)
                    if (child.role == rolenames.ROLE_PAGE_TAB_LIST):
                        list = child
                        tab = list.child(index-1)
                        if (tab.role == rolenames.ROLE_PAGE_TAB):
                            self.readPageTab(tab)
                            return


        # For everything else, pass the focus event onto the parent class 
        # to be handled in the default way.
        #
        # Note that this includes table cells if we only want to read the
        # current cell.

        default.Script.onFocus(self, event)


# Values used to construct a time string for calendar appointments.
#
timeIncrements = {}
timeIncrements[288] = 5
timeIncrements[144] = 10
timeIncrements[96] = 15
timeIncrements[48] = 30
timeIncrements[24] = 60

minutes = {}
minutes[0] = ''
minutes[5] = '5'
minutes[10] = '10'
minutes[15] = '15'
minutes[20] = '20'
minutes[25] = '25'
minutes[30] = '30'
minutes[35] = '35'
minutes[40] = '40'
minutes[45] = '45'
minutes[50] = '50'
minutes[55] = '55'

hours = ['12', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
