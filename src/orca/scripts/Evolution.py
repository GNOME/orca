# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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
import orca.util as util

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

        # The default for Evolution is to read all table cells (such as in
        # the mail message header summary list).

        self.readTableCellRow = True

        # This will be used to cache a handle to the message area in the
        # Mail compose window.

        self.message_panel = None

        # The last row and column we were on in the mail message header list.

        self.lastMessageColumn = -1
        self.lastMessageRow = -1

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

    def readPageTab(self, tab):
        """Speak/Braille the given page tab. The speech verbosity is set
           to VERBOSITY_LEVEL_BRIEF for this operation and then restored
           to its previous value on completion.

        Arguments:
        - tab: the page tab to speak/braille.
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        savedSpeechVerbosityLevel = settings.speechVerbosityLevel
        settings.speechVerbosityLevel = settings.VERBOSITY_LEVEL_BRIEF
        utterances = speechGen.getSpeech(tab, False)
        speech.speakUtterances(utterances)
        settings.speechVerbosityLevel = savedSpeechVerbosityLevel

        braille.displayRegions(brailleGen.getBrailleRegions(tab))

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
            suffix = 'A.M.'
        else:
            totalMins -= 720
            suffix = 'P.M.'

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
    # 7) Mail view: insert attachment dialog: unlabelled arrow button.
    # 8) Mail compose window: message area
    # 9) Spell Checking Dialog
    # 10) Mail view: message area - attachments.

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

        # atspi.printAncestry(event.source)

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
        if util.isDesiredFocusedItem(event.source, rolesList):
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
        if self.readTableCellRow \
            and (util.isDesiredFocusedItem(event.source, rolesList)):
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

                braille.displayRegions([regions, regions[0]])
                speech.speakUtterances(utterances)
                orca.setLocusOfFocus(event, event.source, False)
                return

        # 3) Mail view: message header list
        #
        # Check if the focus is in the message header list. If this focus
        # event is for a different row that the last time we got a similar
        # focus event, we want to speak all of the tables cells (and the
        # header for the one that currently has focus) in the current
        # highlighted message. (The role is only spoken/brailled for the
        # table cell that currently has focus).
        #
        # If this focus event is just for a different table cell on the same
        # row as last time, then we just speak the current cell (and its
        # header).
        #
        # The braille cursor to set to point to the current cell.
        #
        # Note that the Evolution user can adjust which columns appear in
        # the message list and the order in which they appear, so that
        # Orca will just speak the ones that they are interested in.

        rolesList = [rolenames.ROLE_TABLE_CELL, \
                     rolenames.ROLE_TREE_TABLE]
        if self.readTableCellRow \
            and (util.isDesiredFocusedItem(event.source, rolesList)):
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - mail view: message header list.")

            parent = event.source.parent
            row = parent.table.getRowAtIndex(event.source.index)
            column = parent.table.getColumnAtIndex(event.source.index)

            # This is an indication of whether we should speak all the table
            # cells (the user has moved focus up or down the list), or just
            # the current one (focus has moved left or right in the same row).
            # If we at the start or the end of the message header list and
            # the row and column haven't changed, then speak all the table
            # cells.

            speakAll = (self.lastMessageRow != row) or \
                       ((row == 0 or row == parent.table.nRows-1) and \
                        self.lastMessageColumn == column)

            savedBrailleVerbosityLevel = settings.brailleVerbosityLevel
            savedSpeechVerbosityLevel = settings.speechVerbosityLevel

            brailleRegions = []
            cellWithFocus = None

            # If the current locus of focus is not a table cell, then we
            # are entering the mail message header list (rather than moving
            # around inside it), so speak/braille the number of mail messages
            # total.
            #
            # This code section handles one other bogusity. As Evolution is
            # initially being rendered on the screen, the focus at some point
            # is given to the highlighted row in the mail message header list.
            # Because of this, self.lastMessageRow and self.lastMessageColumn
            # will be set to that row number and column number, making the
            # setting of the speakAll variable above, incorrect. We fix that
            # up here.

            if orca.locusOfFocus.role != rolenames.ROLE_TABLE_CELL:
                speakAll = True
                message = "%d messages" % \
                    parent.table.nRows
                brailleRegions.append(braille.Region(message))
                speech.speak(message)

            for i in range(0, parent.table.nColumns):
                obj = parent.table.getAccessibleAt(row, i)
                if obj:
                    cell = atspi.Accessible.makeAccessible(obj)
                    verbose = (cell.index == event.source.index)

                    # Check if the current table cell is a check box. If it
                    # is, then to reduce verbosity, only speak and braille it,
                    # if it's checked or if we are moving the focus from to the
                    # left or right on the same row.

                    checkbox = False
                    toRead = True
                    action = cell.action
                    if action:
                        for j in range(0, action.nActions):
                            if action.getName(j) == "toggle":
                                checkbox = True
                                checked = cell.state.count( \
                                    atspi.Accessibility.STATE_CHECKED)
                                if not checked and speakAll == True:
                                    toRead = False
                                break

                    if toRead:
                        # Speak/braille the column header for this table cell
                        # if it has focus (unless it's a checkbox).
                        if not checkbox and verbose:
                            settings.brailleVerbosityLevel = \
                                settings.VERBOSITY_LEVEL_BRIEF
                            settings.speechVerbosityLevel = \
                                settings.VERBOSITY_LEVEL_BRIEF

                            obj = parent.table.getColumnHeader(i)
                            header = atspi.Accessible.makeAccessible(obj)
                            utterances = speechGen.getSpeech(header, False)
                            [headerRegions, focusedRegion] = \
                                         brailleGen.getBrailleRegions(header)
                            brailleRegions.extend(headerRegions)
                            brailleRegions.append(braille.Region(" "))

                            if column == i:
                                cellWithFocus = focusedRegion
                            if speakAll or (column == i):
                                speech.speakUtterances(utterances)

                        # Speak/braille the table cell.
                        #
                        if verbose:
                            settings.brailleVerbosityLevel = \
                                settings.VERBOSITY_LEVEL_VERBOSE
                        else:
                            settings.brailleVerbosityLevel = \
                                settings.VERBOSITY_LEVEL_BRIEF
                        settings.speechVerbosityLevel = \
                            savedSpeechVerbosityLevel
                        utterances = speechGen.getSpeech(cell, False)
                        [cellRegions, focusedRegion] = \
                                           brailleGen.getBrailleRegions(cell)
                        brailleRegions.extend(cellRegions)
                        brailleRegions.append(braille.Region(" "))

                        # If the current focus is on a checkbox then we won't
                        # have set braille line focus to its header above, so
                        # set it to the cell instead.
                        #
                        if column == i and cellWithFocus == None:
                            cellWithFocus = focusedRegion

                        if speakAll or (column == i):
                            speech.speakUtterances(utterances)

            if brailleRegions != []:
                braille.displayRegions([brailleRegions, cellWithFocus])

            orca.setLocusOfFocus(event, event.source, False)
            settings.brailleVerbosityLevel = savedBrailleVerbosityLevel
            settings.speechVerbosityLevel = savedSpeechVerbosityLevel
            self.lastMessageColumn = column
            self.lastMessageRow = row
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
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - calendar view: day view: " \
                      + "tabbing to day with appts.")

            parent = event.source.parent
            utterances = speechGen.getSpeech(parent, False)
            [brailleRegions, focusedRegion] = \
                    brailleGen.getBrailleRegions(parent)
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
                            braille.displayRegions([brailleRegions,
                                                    brailleRegions[0]])
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
        if util.isDesiredFocusedItem(event.source, rolesList):
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
                        braille.displayRegions([brailleRegions,
                                                brailleRegions[0]])
                        found = True

            if found == False:
                startTime = 'Start time ' + self.getTimeForCalRow(index, noRows)
                brailleRegions.append(braille.Region(startTime))
                speech.speak(startTime)

                utterance = _("No appointments")
                speech.speak(utterance)
                brailleRegions.append(braille.Region(utterance))
                braille.displayRegions([brailleRegions,
                                        brailleRegions[0]])

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
        if util.isDesiredFocusedItem(event.source, rolesList):
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
                        tabList = child
                        tab = tabList.child(index-1)
                        if (tab.role == rolenames.ROLE_PAGE_TAB):
                            self.readPageTab(tab)
                            return

        # 7) Mail view: insert attachment dialog: unlabelled arrow button.
        #
        # Check if the focus is on the unlabelled arrow button near the
        # top of the mail view Insert Attachment dialog. If it is, then
        # rather than just speak/braille "button", output something a
        # little more useful.

        rolesList = [rolenames.ROLE_PUSH_BUTTON, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_SPLIT_PANE, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_DIALOG]
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - mail insert attachment dialog: " \
                      + "unlabelled button.")

            brailleRegions = []
            utterance = _("Directories button")
            speech.speak(utterance)
            brailleRegions.append(braille.Region(utterance))
            braille.displayRegions([brailleRegions,
                                    brailleRegions[0]])
            return

        # 8) Mail compose window: message area
        #
        # This works in conjunction with code in section 9). Check to see if
        # focus is currently in the Mail compose window message area. If it
        # is, then, if this is the first time, save a pointer to the HTML
        # panel that will contain a variety of components that will, in turn,
        # contain the message text.
        #
        # Note that this drops through to then use the default event
        # processing in the parent class for this "focus:" event.

        rolesList = [rolenames.ROLE_TEXT, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_SCROLL_PANE]
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - mail compose window: " \
                      + "message area.")

            self.message_panel = event.source.parent.parent

        # 9) Spell Checking Dialog
        #
        # This works in conjunction with code in section 8). Check to see if
        # current focus is in the table of possible replacement words in the
        # spell checking dialog. If it is, then we use a cached handle to
        # the Mail compose window message area, to find out where the text
        # caret currently is, and use this to speak a selection of the
        # surrounding text, to give the user context for the current misspelt
        # word.

        rolesList = [rolenames.ROLE_TABLE, \
                    rolenames.ROLE_SCROLL_PANE, \
                    rolenames.ROLE_PANEL, \
                    rolenames.ROLE_PANEL, \
                    rolenames.ROLE_PANEL, \
                    rolenames.ROLE_FILLER, \
                    rolenames.ROLE_DIALOG]
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - spell checking dialog.")

            # Braille the default action for this component.
            #
            orca.setLocusOfFocus(event, event.source, False)
            self.updateBraille(orca.locusOfFocus)

            # Look for the "Suggestions for 'xxxxx' label in the spell
            # checker dialog panel. Extract out the xxxxx. This will be the
            # misspelt word.
            #
            panel = event.source.parent.parent
            allLabels = atspi.findByRole(panel, rolenames.ROLE_LABEL)
            found = False
            for i in range(0, len(allLabels)):
                if not found:
                    text = util.getDisplayedText(allLabels[i])
                    if text:
                        tokens = text.split()
                    else:
                        tokens = []
                    for j in range(0, len(tokens)):
                        if tokens[j].startswith("'"):
                            badWord = tokens[j]
                            badWord = badWord[1:len(badWord)-1]
                            found = True
                            break

            # If we have a handle to the HTML message panel, then extract out
            # all the text objects, and create a list of all the words found
            # in them.
            #
            if self.message_panel != None:
                allTokens = []
                panel = self.message_panel
                allText = atspi.findByRole(panel, rolenames.ROLE_TEXT)
                for i in range(0, len(allText)):
                    text = allText[i].text.getText(0, -1)
                    tokens = text.split()
                    allTokens += tokens

                util.speakMisspeltWord(allTokens, badWord)
                return

        # 10) Mail view: message area - attachments.
        #
        # Check if the focus is on the "go forward" button or the
        # "attachment button" for an attachment in the mail message
        # attachment area. (There will be a pair of these buttons
        # for each attachment in the mail message).
        #
        # If it is, then get the text which describes the current
        # attachment and speak it after doing the default action
        # for the button.
        #
        # NOTE: it is assumed that the last table cell in the table
        # contains this information.

        rolesList = [rolenames.ROLE_PUSH_BUTTON, \
                    rolenames.ROLE_FILLER, \
                    rolenames.ROLE_PANEL, \
                    rolenames.ROLE_PANEL, \
                    rolenames.ROLE_TABLE_CELL, \
                    rolenames.ROLE_TABLE, \
                    rolenames.ROLE_PANEL]
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "evolution.onFocus - mail message area attachments.")

            # Speak/braille the default action for this component.
            #
            default.Script.onFocus(self, event)

            table = event.source.parent.parent.parent.parent.parent
            cell = table.child(table.childCount-1)
            allText = atspi.findByRole(cell, rolenames.ROLE_TEXT)
            utterance = "for " + allText[0].text.getText(0, -1)
            speech.speak(utterance)
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
