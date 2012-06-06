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

"""Custom script for Evolution."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.scripts.default as default
import orca.keybindings as keybindings
import orca.input_event as input_event
import orca.braille as braille
import orca.orca as orca
import orca.orca_state as orca_state
import orca.speech as speech
import orca.speechserver as speechserver
import orca.settings as settings
import orca.settings_manager as settings_manager
from orca.orca_i18n import _

from .formatting import Formatting
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities

_settingsManager = settings_manager.getManager()

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

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        default.Script.__init__(self, app)

        # This will be used to cache a handle to the message area in the
        # Mail compose window.

        self.message_panel = None

        # A handle to the Spellcheck dialog.
        #
        self.spellCheckDialog = None

        # Last Setup Assistant panel spoken.
        #
        self.lastSetupPanel = None

        # The last row and column we were on in the mail message header list.

        self.lastMessageColumn = -1
        self.lastMessageRow = -1

        # The last locusOfFocusChanged roles hierarchy.
        #
        self.rolesList = []

        # By default, don't present if Evolution is not the active application.
        #
        self.presentIfInactive = False

        # Evolution defines new custom roles. We need to make them known
        # to Orca for Speech and Braille output.

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return SpeechGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. In this particular case,
        we just want to be able to define our own sayAll() method.
        """

        default.Script.setupInputEventHandlers(self)

        self.inputEventHandlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.sayAll,
                _("Speaks entire document."))

        self.inputEventHandlers["toggleReadMailHandler"] = \
            input_event.InputEventHandler(
                Script.toggleReadMail,
                # Translators: this tells Orca to act like 'biff', or let
                # the user know when new mail has arrived, even if Evolution
                # doesn't have focus.
                #
                _("Toggle whether we present new mail " \
                  "if we are not the active script."))

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "n",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["toggleReadMailHandler"]))

        return keyBindings

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["object:state-changed:showing"]           = \
            self.onStateChanged

        return listeners

    def isActivatableEvent(self, event):
        """Returns True if the given event is one that should cause this
        script to become the active script.  This is only a hint to
        the focus tracking manager and it is not guaranteed this
        request will be honored.  Note that by the time the focus
        tracking manager calls this method, it thinks the script
        should become active.  This is an opportunity for the script
        to say it shouldn't.
        """

        # If the Evolution window is not focused, ignore this event.
        #
        window = self.utilities.topLevelObject(event.source)
        if window and not window.getState().contains(pyatspi.STATE_ACTIVE):
            return False

        return True

    def toggleReadMail(self, inputEvent):
        """ Toggle whether we present new mail if we not not the active script.+
        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "Evolution.toggleReadMail.")

        # Translators: this tells Orca to act like 'biff', or let
        # the user know when new mail has arrived, even if Evolution
        # doesn't have focus.
        #
        line = _("present new mail if this script is not active.")
        self.presentIfInactive = not self.presentIfInactive
        if not self.presentIfInactive:
            # Translators: this tells Orca to act like 'biff', or let
            # the user know when new mail has arrived, even if Evolution
            # doesn't have focus.
            #
            line = _("do not present new mail if this script is not active.")

        self.presentMessage(line)

        return True

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

    # [[[TODO - JD: This method is way, way too huge]]]
    #
    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        details = debug.getAccessibleDetails(self.debugLevel, event.source)
        debug.printObjectEvent(self.debugLevel, event, details)

        # We always automatically go back to focus tracking mode when
        # the focus changes.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        # self.printAncestry(event.source)

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
        if self.utilities.isMessageBody(event.source) \
           and not event.source.getState().contains(pyatspi.STATE_EDITABLE):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail view: " \
                          + "current message pane: " \
                          + "individual lines of text.")

            self.presentMessageLine(event.source, newLocusOfFocus)
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

        self.rolesList = [pyatspi.ROLE_TEXT, \
                          pyatspi.ROLE_PANEL, \
                          pyatspi.ROLE_TABLE_CELL]
        if _settingsManager.getSetting('readTableCellRow') \
            and (self.utilities.hasMatchingHierarchy(
                    event.source, self.rolesList)):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail view: " \
                          + "current message pane: " \
                          + "standard mail header lines.")

            obj = event.source.parent.parent
            parent = obj.parent
            if parent.getRole() == pyatspi.ROLE_TABLE:
                parentTable = parent.queryTable()
                index = self.utilities.cellIndex(obj)
                row = parentTable.getRowAtIndex(index)
                utterances = []
                regions = []
                for i in range(0, parentTable.nColumns):
                    cell = parentTable.getAccessibleAt(row, i)

                    while cell.childCount:
                        cell = cell[0]

                    if cell.getRole() == pyatspi.ROLE_TEXT:
                        regions.append(self.getNewBrailleText(cell))
                        [string, caretOffset, startOffset] = \
                            self.getTextLineAtCaret(cell)
                        utterances.append(string)

                self.displayBrailleRegions([regions, regions[0]])
                speech.speak(utterances)
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

        self.rolesList = [pyatspi.ROLE_TABLE_CELL, \
                          pyatspi.ROLE_TREE_TABLE]
        if _settingsManager.getSetting('readTableCellRow') \
                and self.utilities.hasMatchingHierarchy(event.source,
                                                        self.rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail view: " \
                          + "message header list.")

            # Unfortunately the default read table cell row handling won't
            # just work with Evolution (see bogusity comment below). We
            # quickly solve this by setting readTableCellRow to False
            # for the duration of this code section, then resetting it to
            # True at the end.
            #
            _settingsManager.setSetting('readTableCellRow', False)

            parent = event.source.parent
            parentTable = parent.queryTable()
            index = self.utilities.cellIndex(event.source)
            row = parentTable.getRowAtIndex(index)
            column = parentTable.getColumnAtIndex(index)

            # If we are on the same row, then just speak/braille the table
            # cell as if settings.readTableCellRow was False.
            # See bug #503874 for more details.
            #
            if self.lastMessageRow == row:
                default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)
                _settingsManager.setSetting('readTableCellRow', True)
                return

            # This is an indication of whether we should speak all the table
            # cells (the user has moved focus up or down the list, or just
            # deleted a message), or just the current one (focus has moved
            # left or right in the same row). If we at the start or the end
            # of the message header list and the row and column haven't
            # changed, then speak all the table cells.
            #
            justDeleted = False
            string, mods = self.utilities.lastKeyAndModifiers()
            if string == "Delete":
                justDeleted = True

            speakAll = (self.lastMessageRow != row) or \
                       ((row == 0 or row == parentTable.nRows-1) and \
                        self.lastMessageColumn == column) or \
                       justDeleted

            savedBrailleVerbosityLevel = \
                _settingsManager.getSetting('brailleVerbosityLevel')
            savedSpeechVerbosityLevel = \
                _settingsManager.getSetting('speechVerbosityLevel')

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

            if orca_state.locusOfFocus.getRole() != pyatspi.ROLE_TABLE_CELL:
                speakAll = True
                message = "%d messages" % parentTable.nRows
                brailleRegions.append(self.brailleRegionsFromStrings(message))
                speech.speak(message)

            for i in range(0, parentTable.nColumns):
                cell = parentTable.getAccessibleAt(row, i)
                if cell:
                    verbose = (cell.getIndexInParent() == \
                               event.source.getIndexInParent())

                    # Check if the current table cell is a check box. If it
                    # is, then to reduce verbosity, only speak and braille it,
                    # if it's checked or if we are moving the focus from to the
                    # left or right on the same row.
                    #
                    # The one exception to the above is if this is for the
                    # Status checkbox, in which case we speake/braille it if
                    # the message is unread (not checked).
                    #
                    header = parentTable.getColumnHeader(i)

                    checkbox = False
                    toRead = True
                    # Whether or not we want to replace the cell's column
                    # header with a more user-friendly alternative name.
                    # Currently we only do this with the "status" column,
                    # which we replace with "unread" if it is not checked.
                    #
                    useAlternativeName = False
                    try:
                        action = cell.queryAction()
                    except NotImplementedError:
                        action = None

                    if action:
                        for j in range(0, action.nActions):
                            # Translators: this is the action name for
                            # the 'toggle' action. It must be the same
                            # string used in the *.po file for gail.
                            #
                            if action.getName(j) in ["toggle", _("toggle")]:
                                checkbox = True
                                checked = cell.getState().contains( \
                                    pyatspi.STATE_CHECKED)
                                if speakAll:
                                    # Translators: this is the name of the
                                    # status column header in the message
                                    # list in Evolution.  The name needs to
                                    # match what Evolution is using.
                                    #
                                    if header.name == _("Status"):
                                        toRead = not checked
                                        useAlternativeName = True
                                        break
                                    # Translators: this is the name of the
                                    # flagged column header in the message
                                    # list in Evolution.  The name needs to
                                    # match what Evolution is using.
                                    #
                                    elif header.name == _("Flagged"):
                                        toRead = checked
                                        break
                                    if not checked:
                                        toRead = False
                                break

                    if toRead:
                        # Speak/braille the column header for this table cell
                        # if it has focus (unless it's a checkbox).
                        #
                        if (verbose or (checkbox and column == i)) \
                           and not useAlternativeName:
                            _settingsManager.setSetting(
                                'brailleVerbosityLevel',
                                settings.VERBOSITY_LEVEL_BRIEF)
                            _settingsManager.setSetting(
                                'speechVerbosityLevel',
                                settings.VERBOSITY_LEVEL_BRIEF)

                            utterances = speechGen.generateSpeech(
                                header,
                                includeContext=False,
                                priorObj=oldLocusOfFocus)
                            [headerRegions, focusedRegion] = \
                                         brailleGen.generateBraille(header)
                            brailleRegions.extend(headerRegions)
                            brailleRegions.append(braille.Region(" "))

                            if column == i:
                                cellWithFocus = focusedRegion
                            if speakAll or (column == i):
                                speech.speak(utterances)

                        # Speak/braille the table cell.
                        #
                        # If this cell has a column header of "Status",
                        # then speak/braille "read".
                        # If this cell has a column header of "Attachment",
                        # then speak/braille "attachment".
                        #
                        if verbose:
                            level = settings.VERBOSITY_LEVEL_VERBOSE
                        else:
                            level = settings.VERBOSITY_LEVEL_BRIEF
                        _settingsManager.setSetting(
                            'brailleVerbosityLevel', level)
                        _settingsManager.setSetting(
                            'speechVerbosityLevel',
                            savedSpeechVerbosityLevel)
                        utterances = speechGen.generateSpeech(
                            cell,
                            includeContext=False,
                            priorObj=oldLocusOfFocus)
                        [cellRegions, focusedRegion] = \
                                           brailleGen.generateBraille(cell)

                        # Translators: this is the name of the
                        # status column header in the message
                        # list in Evolution.  The name needs to
                        # match what Evolution is using.
                        #
                        if header.name == _("Status"):
                            # Translators: we present this to the user to
                            # indicate that an email message has not been
                            # marked as having been read.
                            #
                            text = _("unread")
                            utterances = [ text ]
                            brailleRegions.append(braille.Region(text))
                            brailleRegions.append(braille.Region(" "))
                        # Translators: this is the name of the
                        # attachment column header in the message
                        # list in Evolution.  The name needs to
                        # match what Evolution is using.
                        #
                        elif header.name == _("Attachment"):
                            text = header.name
                            utterances = [ text ]
                            if column != i:
                                brailleRegions.append(braille.Region(text))
                                brailleRegions.append(braille.Region(" "))
                        # Translators: this is the name of the
                        # flagged column header in the message
                        # list in Evolution.  The name needs to
                        # match what Evolution is using.
                        #
                        elif header.name == _("Flagged"):
                            text = header.name
                            utterances = [ text ]
                            if column != i:
                                brailleRegions.append(braille.Region(text))
                                brailleRegions.append(braille.Region(" "))
                        else:
                            brailleRegions.extend(cellRegions)
                            brailleRegions.append(braille.Region(" "))

                        # If the current focus is on a checkbox then we won't
                        # have set braille line focus to its header above, so
                        # set it to the cell instead.
                        #
                        if column == i and cellWithFocus == None:
                            cellWithFocus = focusedRegion

                        if speakAll or (column == i):
                            speech.speak(utterances)

            if brailleRegions != []:
                self.displayBrailleRegions([brailleRegions, cellWithFocus])

            _settingsManager.setSetting(
                'brailleVerbosityLevel', savedBrailleVerbosityLevel)
            _settingsManager.setSetting(
                'speechVerbosityLevel', savedSpeechVerbosityLevel)
            self.lastMessageColumn = column
            self.lastMessageRow = row
            _settingsManager.setSetting('readTableCellRow', True)
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

        self.rolesList = ['Calendar Event', 'Calendar View']
        if self.utilities.hasMatchingHierarchy(event.source, self.rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - calendar view: " \
                          + "day view: tabbing to day with appts.")

            parent = event.source.parent
            utterances = speechGen.generateSpeech(parent,
                                                  includeContext=False,
                                                  priorObj=oldLocusOfFocus)
            [brailleRegions, focusedRegion] = \
                    brailleGen.generateBraille(parent)
            speech.speak(utterances)

            apptExtents = event.source.queryComponent().getExtents(0)

            for child in parent:
                if (child.getRole() == pyatspi.ROLE_TABLE):
                    childTable = child.queryTable()
                    noRows = childTable.nRows
                    for j in range(0, noRows):
                        row = childTable.getRowAtIndex(j)
                        appt = childTable.getAccessibleAt(row, 0)
                        extents = appt.queryComponent().getExtents(0)
                        if extents.y == apptExtents.y:
                            utterances = speechGen.generateSpeech(
                                event.source,
                                includeContext=False,
                                priorObj=oldLocusOfFocus)
                            [apptRegions, focusedRegion] = \
                                brailleGen.generateBraille(event.source)
                            brailleRegions.extend(apptRegions)
                            speech.speak(utterances)

                            startTime = 'Start time ' + \
                                self.utilities.timeForCalRow(j, noRows)
                            brailleRegions.append(braille.Region(startTime))
                            speech.speak(startTime)

                            apptLen = apptExtents.height / extents.height
                            endTime = 'End time ' + \
                                self.utilities.timeForCalRow(j + apptLen,
                                                             noRows)
                            brailleRegions.append(braille.Region(endTime))
                            speech.speak(endTime)
                            self.displayBrailleRegions([brailleRegions,
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

        self.rolesList = [pyatspi.ROLE_UNKNOWN, \
                          pyatspi.ROLE_TABLE, \
                          'Calendar View']
        if self.utilities.hasMatchingHierarchy(event.source, self.rolesList):
            debug.println(self.debugLevel,
                      "evolution.locusOfFocusChanged - calendar view: " \
                      + "day view: moving with arrow keys.")

            brailleRegions = []
            index = event.source.getIndexInParent()
            parent = event.source.parent
            calendarView = event.source.parent.parent
            extents = event.source.queryComponent().getExtents(0)
            noRows = parent.queryTable().nRows
            found = False

            for child in calendarView:
                if child.getRoleName() == 'Calendar Event':
                    apptExtents = child.queryComponent().getExtents(0)

                    if extents.y == apptExtents.y:
                        utterances = speechGen.generateSpeech(
                            child,
                            includeContext=False,
                            priorObj=oldLocusOfFocus)
                        [apptRegions, focusedRegion] = \
                            brailleGen.generateBraille(child)
                        brailleRegions.extend(apptRegions)
                        speech.speak(utterances)

                        startTime = 'Start time ' + \
                            self.utilities.timeForCalRow(index, noRows)
                        brailleRegions.append(braille.Region(startTime))
                        speech.speak(startTime)

                        apptLen = apptExtents.height / extents.height
                        endTime = 'End time ' + \
                            self.utilities.timeForCalRow(index + apptLen,
                                                         noRows)
                        brailleRegions.append(braille.Region(endTime))
                        speech.speak(endTime)
                        self.displayBrailleRegions([brailleRegions,
                                                brailleRegions[0]])
                        found = True

            if not found:
                startTime = 'Start time ' + \
                    self.utilities.timeForCalRow(index, noRows)
                brailleRegions.append(braille.Region(startTime))
                speech.speak(startTime)

                # Translators: this means there are no scheduled entries
                # in the calendar.
                #
                utterance = _("No appointments")
                speech.speak(utterance)
                brailleRegions.append(braille.Region(utterance))
                self.displayBrailleRegions([brailleRegions,
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

        self.rolesList = [pyatspi.ROLE_TABLE_CELL, \
                          pyatspi.ROLE_TABLE, \
                          pyatspi.ROLE_UNKNOWN, \
                          pyatspi.ROLE_SCROLL_PANE]
        if self.utilities.hasMatchingHierarchy(event.source, self.rolesList):
            debug.println(self.debugLevel,
                      "evolution.locusOfFocusChanged - preferences dialog: " \
                      + "table cell in options list.")

            index = event.source.getIndexInParent()
            obj = event.source.parent.parent.parent
            parent = obj.parent
            if parent.getRole() == pyatspi.ROLE_FILLER:
                for child in parent:
                    if (child.getRole() == pyatspi.ROLE_PAGE_TAB_LIST):
                        tabList = child
                        tab = tabList[index-1]
                        if (tab.getRole() == pyatspi.ROLE_PAGE_TAB):
                            self.readPageTab(tab)
                            return

        # 7) Mail view: insert attachment dialog: unlabelled arrow button.
        #
        # Check if the focus is on the unlabelled arrow button near the
        # top of the mail view Insert Attachment dialog. If it is, then
        # rather than just speak/braille "button", output something a
        # little more useful.

        self.rolesList = [pyatspi.ROLE_PUSH_BUTTON, \
                          pyatspi.ROLE_PANEL, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_SPLIT_PANE, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_FILLER, \
                          pyatspi.ROLE_DIALOG]
        if self.utilities.hasMatchingHierarchy(event.source, self.rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail insert " \
                          + "attachment dialog: unlabelled button.")

            brailleRegions = []
            # Translators: this is the unlabelled arrow button near the
            # top of the mail view Insert Attachment dialog in Evolution.
            # We give it a name.
            #
            utterance = _("Directories button")
            speech.speak(utterance)
            brailleRegions.append(braille.Region(utterance))
            self.displayBrailleRegions([brailleRegions,
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
        if self.utilities.isMessageBody(event.source) \
           and event.source.getState().contains(pyatspi.STATE_EDITABLE):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - mail " \
                          + "compose window: message area.")

            # We are getting extra (bogus?) "focus:" events from Evolution
            # when we type the first character at the beginning of a line.
            # If the last input event was a keyboard event and the parent
            # of the locusOfFocus and the event.source are the same, and
            # the last roles hierarchy is the same as this one and
            # the last key pressed wasn't a navigation key, then just
            # ignore it. See bug #490317 for more details.
            #
            if self.utilities.isSameObject(event.source.parent,
                                           orca_state.locusOfFocus.parent):
                lastKey, mods = self.utilities.lastKeyAndModifiers()
                if self.utilities.isMessageBody(orca_state.locusOfFocus) \
                   and lastKey not in ["Left", "Right", "Up", "Down",
                                       "Home", "End", "Return", "Tab"]:
                    return

                # If the last keyboard event was a "same line"
                # navigation key, then pass this event onto the
                # onCaretMoved() method in the parent class for
                # speaking. See bug #516565 for more details.
                #
                if lastKey in ["Left", "Right", "Home", "End"]:
                    default.Script.onCaretMoved(self, event)
                    return

            self.message_panel = event.source.parent.parent
            self.presentMessageLine(event.source, newLocusOfFocus)
            return

        # 9) Spell Checking Dialog
        #
        # This works in conjunction with code in section 8). Check to see if
        # current focus is in the table of possible replacement words in the
        # spell checking dialog. If it is, then we use a cached handle to
        # the Mail compose window message area, to find out where the text
        # caret currently is, and use this to speak a selection of the
        # surrounding text, to give the user context for the current misspelt
        # word.
        if self.utilities.isSpellingSuggestionsList(event.source) \
           or self.utilities.isSpellingSuggestionsList(newLocusOfFocus):
            debug.println(self.debugLevel,
                      "evolution.locusOfFocusChanged - spell checking dialog.")

            # Braille the default action for this component.
            #
            self.updateBraille(orca_state.locusOfFocus)

            if not self.pointOfReference.get('activeDescendantInfo'):
                [badWord, allTokens] = \
                    self.utilities.misspelledWordAndBody(event.source,
                                                         self.message_panel)
                self.speakMisspeltWord(allTokens, badWord)

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

        self.rolesList = [pyatspi.ROLE_PUSH_BUTTON, \
                         pyatspi.ROLE_FILLER, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_TABLE_CELL, \
                         pyatspi.ROLE_TABLE, \
                         pyatspi.ROLE_PANEL]
        if self.utilities.hasMatchingHierarchy(event.source, self.rolesList):
            debug.println(self.debugLevel,
                          "evolution.locusOfFocusChanged - " \
                          + "mail message area attachments.")

            # Speak/braille the default action for this component.
            #
            default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

            tmp = event.source.parent.parent
            table = tmp.parent.parent.parent
            cell = table[table.childCount-1]
            allText = self.utilities.descendantsWithRole(
                cell, pyatspi.ROLE_TEXT)
            utterance = "for " + self.utilities.substring(allText[0], 0, -1)
            speech.speak(utterance)
            return

        # For everything else, pass the focus event onto the parent class
        # to be handled in the default way.
        #
        # Note that this includes table cells if we only want to read the
        # current cell.

        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in onActiveDescendantChanged.

        Arguments:
        - event: the Event

        Returns True if speech should be stopped; False otherwise.
        """

        return False

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        # The default script's onActiveDescendantChanged method is cutting
        # off speech with a speech.stop. If we're in the spellcheck dialog,
        # this interrupts the presentation of the context.
        #
        if self.utilities.isSpellingSuggestionsList(event.source):
            orca.setLocusOfFocus(event, event.any_data)

            # We'll tuck away the activeDescendant information for future
            # reference since the AT-SPI gives us little help in finding
            # this.
            #
            if orca_state.locusOfFocus \
               and (orca_state.locusOfFocus != event.source):
                self.pointOfReference['activeDescendantInfo'] = \
                    [orca_state.locusOfFocus.parent,
                     orca_state.locusOfFocus.getIndexInParent()]
            return

        default.Script.onActiveDescendantChanged(self, event)

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # When a message is deleted from within the table of messages, we get
        # two focus events:  One for the index of the new message prior to
        # deletion and one for the index of the new message after deletion.
        # This causes us to speak the message after the one that gets focus
        # prior to speaking the actual message that gets focus.
        # See bug #347964.
        #
        string, mods = self.utilities.lastKeyAndModifiers()
        if string == "Delete":
            roles = [pyatspi.ROLE_TABLE_CELL,
                     pyatspi.ROLE_TREE_TABLE,
                     pyatspi.ROLE_UNKNOWN,
                     pyatspi.ROLE_SCROLL_PANE]
            oldLocusOfFocus = orca_state.locusOfFocus
            if self.utilities.hasMatchingHierarchy(event.source, roles) \
               and self.utilities.hasMatchingHierarchy(oldLocusOfFocus, roles):
                parent = event.source.parent
                parentTable = parent.queryTable()
                newIndex = self.utilities.cellIndex(event.source)
                newRow = parentTable.getRowAtIndex(newIndex)
                oldIndex = self.utilities.cellIndex(oldLocusOfFocus)
                oldRow = parentTable.getRowAtIndex(oldIndex)
                nRows = parentTable.nRows
                if (newRow != oldRow) and (oldRow != nRows):
                    return

        # For everything else, pass the event onto the parent class
        # to be handled in the default way.
        #
        default.Script.onFocus(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.  We are only
        interested in "object:state-changed:showing" events for any
        object in the Setup Assistant.

        Arguments:
        - event: the Event
        """

        if self.utilities.isWizardNewInfoEvent(event):
            if event.source.getRole() == pyatspi.ROLE_PANEL:
                self.lastSetupPanel = event.source
            self.presentWizardNewInfo(
                self.utilities.topLevelObject(event.source))
            return

        # For everything else, pass the event onto the parent class
        # to be handled in the default way.
        #
        default.Script.onStateChanged(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        # When the active descendant in the list of misspelled words
        # changes, we typically get an object:active-descendant-changed
        # event. Unfortunately, we don't seem to get this event (or a
        # focus: event) when the user presses a button without moving
        # focus there explicitly. (e.g. pressing Alt+R) The label which
        # is associated with the spelling list gets new text. So we'll
        # try to look for that instead.
        #
        if event.source.getRole() == pyatspi.ROLE_LABEL:
            relations = event.source.getRelationSet()
            for relation in relations:
                if relation.getRelationType() == pyatspi.RELATION_LABEL_FOR:
                    target = relation.getTarget(0)
                    if self.utilities.isSpellingSuggestionsList(target):
                        [badWord, allTokens] = \
                            self.utilities.misspelledWordAndBody(
                                target, self.message_panel)
                        self.speakMisspeltWord(allTokens, badWord)

                        try:
                            selection = target.querySelection()
                        except NotImplementedError:
                            selection = None
                        if selection and selection.nSelectedChildren > 0:
                            newFocus = selection.getSelectedChild(0)
                            orca.setLocusOfFocus(event, newFocus)
                            self.pointOfReference['activeDescendantInfo'] = \
                                [target, newFocus.getIndexInParent()]

                        return

        default.Script.onTextInserted(self, event)

    ########################################################################
    #                                                                      #
    # Methods for presenting content                                       #
    #                                                                      #
    ########################################################################

    def presentMessageLine(self, obj, newLocusOfFocus):
        """Speak/braille the line at the current text caret offset.
        """

        [string, caretOffset, startOffset] = self.getTextLineAtCaret(obj)
        self.updateBraille(newLocusOfFocus)
        result = self.speechGenerator.generateTextIndentation(obj, line=string)
        if result:
            speech.speak(result[0])
        line = self.utilities.adjustForRepeats(string)

        if self.utilities.speakBlankLine(obj):
            # Translators: "blank" is a short word to mean the
            # user has navigated to an empty line.
            #
            speech.speak(_("blank"), None, False)
        else:
            speech.speak(line, None, False)

    def presentWizardNewInfo(self, obj):
        """Causes the new information displayed in a wizard to be presented
        to the user.

        Arguments:
        - obj: the Accessible object
        """

        if not obj:
            return

        # TODO - JD: Presenting the Setup Assistant (or any Wizard) as a
        # dialog means that we will repeat the dialog's name for each new
        # "screen". We should consider a 'ROLE_WIZARD' or some other means
        # for presenting these objects.
        #
        utterances = \
            self.speechGenerator.generateSpeech(obj, role=pyatspi.ROLE_DIALOG)

        # The following falls under the heading of "suck it and see." The
        # worst case scenario is that we present the push button and then
        # process a focus:/object:state-changed:focused event and present
        # it.
        #
        if orca_state.locusOfFocus \
           and orca_state.locusOfFocus.getRole() == pyatspi.ROLE_PUSH_BUTTON \
           and orca_state.locusOfFocus.getState().\
               contains(pyatspi.STATE_FOCUSED):
            utterances.append(
                self.speechGenerator.generateSpeech(orca_state.locusOfFocus))

        speech.speak(utterances)

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
        _settingsManager.setSetting(
            'speechVerbosityLevel', settings.VERBOSITY_LEVEL_BRIEF)
        utterances = speechGen.generateSpeech(tab)
        speech.speak(utterances)
        _settingsManager.setSetting(
            'speechVerbosityLevel', savedSpeechVerbosityLevel)

        self.displayBrailleRegions(brailleGen.generateBraille(tab))

    def textLines(self, obj):
        """Creates a generator that can be used to iterate over each line
        of a text object, starting at the caret offset.

        We have to subclass this because Evolution lays out its messages
        such that each paragraph is in its own panel, each of which is
        in a higher level panel.  So, we just traverse through the
        children.

        Arguments:
        - obj: an Accessible that has a text specialization

        Returns an iterator that produces elements of the form:
        [SayAllContext, acss], where SayAllContext has the text to be
        spoken and acss is an ACSS instance for speaking the text.
        """

        if not obj:
            return

        try:
            text = obj.queryText()
        except NotImplementedError:
            return

        panel = obj.parent
        htmlPanel = panel.parent
        startIndex = panel.getIndexInParent()
        i = startIndex
        total = htmlPanel.childCount
        textObjs = []
        startOffset = text.caretOffset
        offset = text.caretOffset
        string = ""
        done = False

        # Determine the correct "say all by" mode to use.
        #
        sayAllStyle = _settingsManager.getSetting('sayAllStyle')
        if sayAllStyle == settings.SAYALL_STYLE_SENTENCE:
            mode = pyatspi.TEXT_BOUNDARY_SENTENCE_END
        elif sayAllStyle == settings.SAYALL_STYLE_LINE:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START
        else:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START
        voices = _settingsManager.getSetting('voices')

        while not done:
            panel = htmlPanel.getChildAtIndex(i)
            if panel != None:
                textObj = panel.getChildAtIndex(0)
                try:
                    text = textObj.queryText()
                except NotImplementedError:
                    return
                textObjs.append(textObj)
                length = text.characterCount

                while offset <= length:
                    [mystr, start, end] = text.getTextAtOffset(offset, mode)
                    endOffset = end

                    if len(mystr) != 0:
                        string += " " + mystr

                    if mode == pyatspi.TEXT_BOUNDARY_LINE_START or \
                       len(mystr) == 0 or mystr[len(mystr)-1] in '.?!':
                        string = self.utilities.adjustForRepeats(string)
                        if string.decode("UTF-8").isupper():
                            voice = voices[settings.UPPERCASE_VOICE]
                        else:
                            voice = voices[settings.DEFAULT_VOICE]

                        if not textObjs:
                            textObjs.append(textObj)
                        if len(string) != 0:
                            yield [speechserver.SayAllContext(textObjs, string,
                                                      startOffset, endOffset),
                               voice]
                        textObjs = []
                        string = ""
                        startOffset = endOffset

                    if len(mystr) == 0 or end == length:
                        break
                    else:
                        offset = end

            offset = 0
            i += 1
            if i == total:
                done = True

        # If there is anything left unspoken, speak it now.
        #
        if len(string) != 0:
            string = self.utilities.adjustForRepeats(string)
            if string.decode("UTF-8").isupper():
                voice = voices[settings.UPPERCASE_VOICE]
            else:
                voice = voices[settings.DEFAULT_VOICE]

            yield [speechserver.SayAllContext(textObjs, string,
                                              startOffset, endOffset),
                   voice]

    def __sayAllProgressCallback(self, context, callbackType):
        """Provide feedback during the sayAll operation.
        """

        if callbackType == speechserver.SayAllContext.PROGRESS:
            #print "PROGRESS", context.utterance, context.currentOffset
            return
        elif callbackType == speechserver.SayAllContext.INTERRUPTED:
            #print "INTERRUPTED", context.utterance, context.currentOffset
            offset = context.currentOffset
            for i in range(0, len(context.obj)):
                obj = context.obj[i]
                charCount = obj.queryText().characterCount
                if offset > charCount:
                    offset -= charCount
                else:
                    obj.queryText().setCaretOffset(offset)
                    break
        elif callbackType == speechserver.SayAllContext.COMPLETED:
            #print "COMPLETED", context.utterance, context.currentOffset
            obj = context.obj[len(context.obj)-1]
            obj.queryText().setCaretOffset(context.currentOffset)
            orca.setLocusOfFocus(None, obj, notifyScript=False)

        # If there is a selection, clear it. See bug #489504 for more details.
        # This is not straight forward with Evolution. all the text is in
        # an HTML panel which contains multiple panels, each containing a
        # single text object.
        #
        panel = obj.parent
        htmlPanel = panel.parent
        for i in range(0, htmlPanel.childCount):
            panel = htmlPanel.getChildAtIndex(i)
            if panel != None:
                textObj = panel.getChildAtIndex(0)
                try:
                    text = textObj.queryText()
                except:
                    pass
                else:
                    if text.getNSelections():
                        text.removeSelection(0)

    def sayAll(self, inputEvent):
        """Speak all the text associated with the text object that has
           focus. We have to define our own method here because Evolution
           does not implement the FLOWS_TO relationship and all the text
           are in an HTML panel which contains multiple panels, each
           containing a single text object.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "evolution.sayAll.")
        try:
            if orca_state.locusOfFocus and orca_state.locusOfFocus.queryText():
                speech.sayAll(self.textLines(orca_state.locusOfFocus),
                              self.__sayAllProgressCallback)
        except:
            default.Script.sayAll(self, inputEvent)

        return True
