# Orca
#
# Copyright 2005-2007 Sun Microsystems Inc.
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

"""Custom script for StarOffice and OpenOffice."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import gtk
import pyatspi

import orca.debug as debug
import orca.chnames as chnames
import orca.default as default
import orca.input_event as input_event
import orca.braille as braille
import orca.braillegenerator as braillegenerator
import orca.orca as orca
import orca.orca_state as orca_state
import orca.speech as speech
import orca.speechgenerator as speechgenerator
import orca.settings as settings
import orca.keybindings as keybindings
import orca.where_am_I as where_am_I

from orca.orca_i18n import _ # for gettext support
from orca.orca_i18n import Q_     # to provide qualified translatable strings

# Whether we speak spread sheet cell coordinates as the user moves around.
#
speakCellCoordinates = True

class WhereAmI(where_am_I.WhereAmI):

    def __init__(self, script):
        """Create a new WhereAmI that will be used to speak information
        about the current object of interest.
        """

        where_am_I.WhereAmI.__init__(self, script)

    def _speakTableCell(self, obj, basicOnly):
        """Given the nature of OpenOffice Calc, Orca should override the
        default whereAmI behavior when the item with focus is a cell
        within Calc. In this instance, the following information should
        be spoken/displayed:

        1. "Cell"
        2. the cell coordinates
        3. the cell contents:
            A. if the cell is empty, "blank"
            B. if the cell is being edited AND if some text within the cell
            is selected, the selected text followed by "selected"
            C. otherwise, the full contents of the cell
        """

        if not self._script.isSpreadSheetCell(obj):
            return where_am_I.WhereAmI._speakTableCell(self, obj, basicOnly)

        utterances = []
        utterances.append(_("cell"))

        table = obj.parent.queryTable()

        # Translators: this represents the column we're
        # on in a table.
        #
        text = _("column %d") % \
               (table.getColumnAtIndex(obj.getIndexInParent()) + 1)
        utterances.append(text)

        # Speak the dynamic column header (if any).
        #
        if self._script.dynamicColumnHeaders.has_key(table):
            row = self._script.dynamicColumnHeaders[table]
            header = self._script.getDynamicRowHeaderCell(obj, row)
            try:
                headerText = header.queryText()
            except:
                headerText = None

            if header.childCount > 0:
                for child in header:
                    text = self._script.getText(child, 0, -1)
                    if text:
                        utterances.append(text)
            elif headerText:
                text = self._script.getText(header, 0, -1)
                if text:
                    utterances.append(text)

        # Translators: this represents the row number of a table.
        #
        text = _("row %d") % (table.getRowAtIndex(obj.getIndexInParent()) + 1)
        utterances.append(text)

        # Speak the dynamic row header (if any).
        #
        if self._script.dynamicRowHeaders.has_key(table):
            column = self._script.dynamicRowHeaders[table]
            header = self._script.getDynamicColumnHeaderCell(obj, column)
            try:
                headerText = header.queryText()
            except:
                headerText = None

            if header.childCount > 0:
                for child in header:
                    text = self._script.getText(child, 0, -1)
                    if text:
                        utterances.append(text)
            elif headerText:
                text = self._script.getText(header, 0, -1)
                if text:
                    utterances.append(text)

        text = obj.queryText().getText(0, -1)
        utterances.append(text)

        debug.println(self._debugLevel, "calc table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakParagraph(self, obj, basicOnly):
        """OpenOffice Calc cells have the role "paragraph" when
        they are being edited.
        """

        top = self._script.getTopLevel(obj)
        if top and top.name.endswith(" Calc"):
            self._speakCalc(obj, basicOnly)
        elif top and top.name.endswith(" Writer"):
            self._speakText(obj, basicOnly)

    def _speakCalc(self, obj, basicOnly):
        """Speak a OpenOffice Calc cell.
        """

        utterances = []
        utterances.append(_("cell"))

        # No way to get cell coordinates?

        [textContents, startOffset, endOffset, selected] = \
            self._getTextContents(obj, basicOnly)
        text = textContents
        utterances.append(text)
        if selected:
            # Translators: when the user selects (highlights) text in
            # a document, Orca lets them know this.
            #
            # ONLY TRANSLATE THE PART AFTER THE PIPE CHARACTER |
            #
            text = Q_("text|selected")
            utterances.append(text)

        debug.println(self._debugLevel, "editable table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _getCalcFrameAndSheet(self, obj):
        """Returns the Calc frame and sheet
        """

        mylist = [None, None]

        parent = obj.parent
        while parent and (parent.parent != parent):
            # debug.println(self._debugLevel,
            #             "_getCalcFrameAndSheet: parent=%s, %s" % \
            #             (parent.getRole(), self._getObjLabelAndName(parent)))
            if parent.getRole() == pyatspi.ROLE_FRAME:
                mylist[0] = parent
            if parent.getRole() == pyatspi.ROLE_TABLE:
                mylist[1] = parent
            parent = parent.parent

        return mylist

    def _speakCalcStatusBar(self):
        """Speaks the OpenOffice Calc statusbar.
        """

        if not self._statusBar:
            return

        utterances = []
        for child in self._statusBar:
            text = self._getObjName(child)
            utterances.append(text)

        debug.println(self._debugLevel, "Calc statusbar utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def speakTitle(self, obj):
        """Speak the title bar.

        Calc-Specific Handling: 

        1. The contents of the title bar of the application main window
        2. The title of the current worksheet

        Note that if the application with focus is Calc, but a cell does not
        have focus, the default behavior should be used.
        """

        top = self._script.getTopLevel(obj)
        if top and not top.name.endswith(" Calc"):
            return where_am_I.WhereAmI.speakTitle(self, obj)

        utterances = []

        mylist = self._getCalcFrameAndSheet(obj)
        if mylist[0]:
            text = self.getObjLabelAndName(mylist[0])
            utterances.append(text)
        if mylist[1]:
            text = self.getObjLabelAndName(mylist[1])
            utterances.append(text)

        debug.println(self._debugLevel,
                      "Calc titlebar and sheet utterances=%s" % utterances)
        speech.speakUtterances(utterances)

    def speakStatusBar(self, obj):
        """Speak the status bar contents.

        Note that if the application with focus is Calc, but a cell does not
        have focus, the default behavior should be used.
        """

        top = self._script.getTopLevel(obj)
        if top and not top.name.endswith(" Calc"):
            return where_am_I.WhereAmI.speakStatusBar(self, obj)

        utterances = []

        mylist = self._getCalcFrameAndSheet(obj)
        if mylist[0]:
            self._statusBar = None
            self._getStatusBar(mylist[0])
            if self._statusBar:
                self._speakCalcStatusBar()

        debug.println(self._debugLevel,
                      "Calc status bar utterances=%s" % utterances)
        speech.speakUtterances(utterances)

class BrailleGenerator(braillegenerator.BrailleGenerator):
    """Overrides _getBrailleRegionsForTableCellRow so that , when we are
    in a spread sheet, we can braille the dynamic row and column headers
    (assuming they are set).
    Overrides _getBrailleRegionsForTableCell so that, when we are in
    a spread sheet, we can braille the location of the table cell as well
    as the contents.
    """

    def __init__(self, script):
        braillegenerator.BrailleGenerator.__init__(self, script)

    def _getBrailleRegionsForTableCellRow(self, obj):
        """Get the braille for a table cell row or a single table cell
        if settings.readTableCellRow is False.

        Arguments:
        - obj: the table cell

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        focusRegion = None
        regions = []

        # Check to see if this spread sheet cell has either a dynamic
        # column heading or row heading (or both) associated with it.
        # If it does, then braille those first before brailling the
        # cell contents.
        #
        table = self._script.getTable(obj)
        parent = obj.parent
        try:
            parentTable = parent.queryTable()
        except NotImplementedError:
            parentTable = None

        if self._script.pointOfReference.has_key("lastColumn") and \
              self._script.pointOfReference["lastColumn"] != \
              parentTable.getColumnAtIndex(obj.getIndexInParent()):
            if self._script.dynamicColumnHeaders.has_key(table):
                row = self._script.dynamicColumnHeaders[table]
                header = self._script.getDynamicRowHeaderCell(obj, row)
                try:
                    headerText = header.queryText()
                except:
                    headerText = None

                if header.childCount > 0:
                    for child in header:
                        text = self._script.getText(child, 0, -1)
                        if text:
                            regions.append(braille.Region(" " + text + " "))
                elif headerText:
                    text = self._script.getText(header, 0, -1)
                    if text:
                        regions.append(braille.Region(" " + text + " "))

        if self._script.pointOfReference.has_key("lastRow") and \
              self._script.pointOfReference['lastRow'] != \
              parentTable.getRowAtIndex(obj.getIndexInParent()):
            if self._script.dynamicRowHeaders.has_key(table):
                column = self._script.dynamicRowHeaders[table]
                header = self._script.getDynamicColumnHeaderCell(obj, column)
                try:
                    headerText = header.queryText()
                except:
                    headerText = None

                if header.childCount > 0:
                    for child in header:
                        text = self._script.getText(child, 0, -1)
                        if text:
                            regions.append(braille.Region(" " + text + " "))
                elif headerText:
                    text = self._script.getText(header, 0, -1)
                    if text:
                        regions.append(braille.Region(" " + text + " "))

        if self._script.isSpreadSheetCell(obj):

            # Adding in a check here to make sure that the parent is a
            # valid table. It's possible that the parent could be a
            # table cell too (see bug #351501).
            #
            if settings.readTableCellRow and parentTable:
                rowRegions = []
                savedBrailleVerbosityLevel = settings.brailleVerbosityLevel
                settings.brailleVerbosityLevel = \
                                             settings.VERBOSITY_LEVEL_BRIEF

                parent = obj.parent
                row = parentTable.getRowAtIndex(obj.getIndexInParent())
                column = parentTable.getColumnAtIndex(obj.getIndexInParent())

                # This is an indication of whether we should speak all the
                # table cells (the user has moved focus up or down a row),
                # or just the current one (focus has moved left or right in
                # the same row).
                #
                speakAll = True
                if self._script.pointOfReference.has_key("lastRow") and \
                    self._script.pointOfReference.has_key("lastColumn"):
                    pointOfReference = self._script.pointOfReference
                    speakAll = \
                        (pointOfReference["lastRow"] != row) or \
                           ((row == 0 or row == parentTable.nRows-1) and \
                            pointOfReference["lastColumn"] == column)

                if speakAll:
                    [startIndex, endIndex] = \
                        self._script.getSpreadSheetRowRange(obj)
                    for i in range(startIndex, endIndex+1):
                        cell = parentTable.getAccessibleAt(row, i)
                        showing = cell.getState().contains( \
                                        pyatspi.STATE_SHOWING)
                        if showing:
                            [cellRegions, focusRegion] = \
                                self._getBrailleRegionsForTableCell(cell)
                            if len(rowRegions):
                                rowRegions.append(braille.Region(" "))
                            rowRegions.append(cellRegions[0])
                    regions.extend(rowRegions)
                    settings.brailleVerbosityLevel = savedBrailleVerbosityLevel
                else:
                    [cellRegions, focusRegion] = \
                                self._getBrailleRegionsForTableCell(obj)
                    regions.extend(cellRegions)
            else:
                [cellRegions, focusRegion] = \
                                self._getBrailleRegionsForTableCell(obj)
                regions.extend(cellRegions)
            regions = [regions, focusRegion]
        else:
            [cellRegions, focusRegion] = \
                braillegenerator.BrailleGenerator.\
                    _getBrailleRegionsForTableCellRow(self, obj)
            regions.extend(cellRegions)
            regions = [regions, focusRegion]

        return regions

    def _getBrailleRegionsForTableCell(self, obj):
        """Get the braille for a table cell. If this isn't inside a
        spread sheet, just return the regions returned by the default
        table cell braille handler.

        Arguments:
        - obj: the table cell

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        if self._script.isSpreadSheetCell(obj):
            if self._script.inputLineForCell == None:
                self._script.inputLineForCell = \
                            self._script.locateInputLine(obj)

            regions = []
            text = self._script.getDisplayedText(obj)
            componentRegion = braille.Component(obj, text)
            regions.append(componentRegion)

            # If the spread sheet table cell has something in it, then we
            # want to append the name of the cell (which will be its location).
            # Note that if the cell was empty, then
            # self._script.getDisplayedText will have already done this for us.
            #
            try:
                if obj.queryText():
                    objectText = self._script.getText(obj, 0, -1)
                    if objectText and len(objectText) != 0:
                        regions.append(braille.Region(" " + obj.name))
            except NotImplementedError:
                pass

            return [regions, componentRegion]

        else:
            # Check to see how many children this table cell has. If it's
            # just one (or none), then pass it on to the superclass to be
            # processed.
            #
            # If it's more than one, then get the braille regions for each
            # child, and call this method again.
            #
            if obj.childCount <= 1:
                regions = braillegenerator.BrailleGenerator.\
                              _getBrailleRegionsForTableCell(self, obj)
            else:
                regions = []
                for child in obj:
                    [cellRegions, focusRegion] = \
                                self._getBrailleRegionsForTableCell(child)
                    regions.extend(cellRegions)
                return [regions, focusRegion]

        return regions

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForComboBox so that we can provide a name for
    the Calc Name combo box.
    Overrides _getSpeechForTableCellRow so that , when we are in a
    spread sheet, we can speak the dynamic row and column headers
    (assuming they are set).
    Overrides _getSpeechForTableCell so that, when we are in a spread
    sheet, we can speak the location of the table cell as well as the
    contents.
    Overrides _getSpeechForToggleButton so that, when the toggle buttons
    on the Formatting toolbar change state, we provide both the name and
    the state (as "on" or "off")
    Overrides _getSpeechForPushButton because sometimes the toggle buttons
    on the Formatting toolbar claim to be push buttons.
    """
    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForComboBox(self, obj, already_focused):
        """Get the speech for a combo box. If the combo box already has focus,
        then only the selection is spoken.
        Also provides a name for the OOo Calc Name combo box. This name is
        provided in clause 5) of locusOfFocusChanged() below.

        Arguments:
        - obj: the combo box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            if not label:
                label = [ obj.name ]
            utterances.extend(label)
        else:
            label = None

        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)

        if not already_focused:
            utterances.extend(self._getSpeechForObjectRole(obj))

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("_getSpeechForComboBox",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTable(self, obj, already_focused):
        """Get the speech for a table

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTable",
                             obj,
                             already_focused,
                             utterances)

        # If this is a table with no children, then let the user know.
        #
        if not obj.childCount:
            # Translators: this indicates that there are zero items in
            # a layered pane or table.
            #
            utterances.append(_("0 items"))

        return utterances

    def _getSpeechForTableCellRow(self, obj, already_focused):
        """Get the speech for a table cell row or a single table cell
        if settings.readTableCellRow is False. If this isn't inside a
        spread sheet, just return the utterances returned by the default
        table cell speech handler.

        Arguments:
        - obj: the table cell
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if not already_focused:

            # Check to see if this spread sheet cell has either a dynamic
            # column heading or row heading (or both) associated with it.
            # If it does, then speak those first before speaking the cell
            # contents.
            #
            table = self._script.getTable(obj)
            parent = obj.parent
            try:
                parentTable = parent.queryTable()
            except NotImplementedError:
                parentTable = None

            if self._script.pointOfReference.has_key("lastColumn") and \
               self._script.pointOfReference["lastColumn"] != \
               parentTable.getColumnAtIndex(obj.getIndexInParent()):
                if self._script.dynamicColumnHeaders.has_key(table):
                    row = self._script.dynamicColumnHeaders[table]
                    header = self._script.getDynamicRowHeaderCell(obj, row)
                    try:
                        headerText = header.queryText()
                    except:
                        headerText = None

                    if header.childCount > 0:
                        for child in header:
                            text = self._script.getText(child, 0, -1)
                            if text:
                                utterances.append(text)
                    elif headerText:
                        text = self._script.getText(header, 0, -1)
                        if text:
                            utterances.append(text)

            if self._script.pointOfReference.has_key("lastRow") and \
               self._script.pointOfReference["lastRow"] != \
               parentTable.getRowAtIndex(obj.getIndexInParent()):
                if self._script.dynamicRowHeaders.has_key(table):
                    column = self._script.dynamicRowHeaders[table]
                    header = self._script.getDynamicColumnHeaderCell(obj,
                                                                     column)
                    try:
                        headerText = header.queryText()
                    except:
                        headerText = None

                    if header.childCount > 0:
                        for child in header:
                            text = self._script.getText(child, 0, -1)
                            if text:
                                utterances.append(text)
                    elif headerText:
                        text = self._script.getText(header, 0, -1)
                        if text:
                            utterances.append(text)

        if self._script.isSpreadSheetCell(obj):
            if not already_focused:
                if settings.readTableCellRow:
                    parent = obj.parent
                    row = parentTable.getRowAtIndex(obj.getIndexInParent())
                    column = \
                        parentTable.getColumnAtIndex(obj.getIndexInParent())

                    # This is an indication of whether we should speak all the
                    # table cells (the user has moved focus up or down a row),
                    # or just the current one (focus has moved left or right in
                    # the same row).
                    #
                    speakAll = True
                    if self._script.pointOfReference.has_key("lastRow") and \
                        self._script.pointOfReference.has_key("lastColumn"):
                        pointOfReference = self._script.pointOfReference
                        speakAll = (pointOfReference["lastRow"] != row) or \
                               ((row == 0 or row == parentTable.nRows-1) and \
                                pointOfReference["lastColumn"] == column)

                    if speakAll:
                        [startIndex, endIndex] = \
                            self._script.getSpreadSheetRowRange(obj)
                        for i in range(startIndex, endIndex+1):
                            cell = parentTable.getAccessibleAt(row, i)
                            showing = cell.getState().contains( \
                                          pyatspi.STATE_SHOWING)
                            if showing:
                                utterances.extend(self._getSpeechForTableCell(\
                                                  cell, already_focused))
                    else:
                        utterances.extend(self._getSpeechForTableCell(obj,
                                                             already_focused))
                else:
                    utterances.extend(self._getSpeechForTableCell(obj,
                                                             already_focused))
        else:
            utterances.extend(speechgenerator.SpeechGenerator.\
                _getSpeechForTableCellRow(self, obj, already_focused))

        return utterances

    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech for a table cell. If this isn't inside a
        spread sheet, just return the utterances returned by the default
        table cell speech handler.

        Arguments:
        - obj: the table cell
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        if self._script.isSpreadSheetCell(obj):
            utterances = []

            if self._script.inputLineForCell == None:
                self._script.inputLineForCell = \
                            self._script.locateInputLine(obj)

            try:
                if obj.queryText():
                    objectText = self._script.getText(obj, 0, -1)
                    if not speakCellCoordinates and len(objectText) == 0:
                        # Translators: this indicates an empty (blank) spread
                        # sheet cell.
                        #
                        objectText = _("blank")

                    utterances.append(objectText)
            except NotImplementedError:
                pass

            if speakCellCoordinates:
                nameList = obj.name.split()
                utterances.append(nameList[1])
        else:
            # Check to see how many children this table cell has. If it's
            # just one (or none), then pass it on to the superclass to be
            # processed.
            #
            # If it's more than one, then get the speech for each child,
            # and call this method again.
            #
            if obj.childCount <= 1:
                utterances = speechgenerator.SpeechGenerator.\
                    _getSpeechForTableCell(self, obj, already_focused)
            else:
                utterances = []
                for child in obj:
                    utterances.extend(self._getSpeechForTableCell(child,
                                                        already_focused))

        return utterances

    def _getSpeechForToggleButton(self, obj, already_focused):
        """Get the speech for a toggle button.  We always want to speak the
        state if it's on a toolbar.

        Arguments:
        - obj: the toggle button
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        if obj.parent.getRole() == pyatspi.ROLE_TOOL_BAR:
            if obj.getState().contains(pyatspi.STATE_CHECKED):
                # Translators: this represents the state of a check box
                #
                checkedState = _("on")
            else:
                # Translators: this represents the state of a check box
                #
                checkedState = _("off")

            utterances.append(obj.name)
            utterances.append(checkedState)
        else:
            utterances.extend(speechgenerator.SpeechGenerator.\
                _getSpeechForToggleButton(self, obj, already_focused))

        return utterances

    def _getSpeechForPushButton(self, obj, already_focused):
        """Get the speech for a push button.  We always want to speak the
        state if it's on a toolbar.

        Arguments:
        - obj: the push button
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        if obj.parent.getRole() == pyatspi.ROLE_TOOL_BAR:
            if obj.getState().contains(pyatspi.STATE_CHECKED):
                # Translators: this represents the state of a check box
                #
                checkedState = _("on")
            else:
                # Translators: this represents the state of a check box
                #
                checkedState = _("off")

            utterances.append(obj.name)
            utterances.append(checkedState)
        else:
            utterances.extend(speechgenerator.SpeechGenerator.\
                _getSpeechForPushButton(self, obj, already_focused))

        return utterances

########################################################################
#                                                                      #
# The StarOffice script class.                                         #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

        # Initialize variable to None to make pylint happy.
        #
        self.savedEnabledBrailledTextAttributes = None
        self.savedEnabledSpokenTextAttributes = None
        self.speakCellCoordinatesCheckButton = None
        self.savedreadTableCellRow = None

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # A handle to the last spread sheet cell encountered.
        #
        self.lastCell = None

        # The spreadsheet input line.
        #
        self.inputLineForCell = None

        # Dictionaries for the calc dynamic row and column headers.
        #
        self.dynamicColumnHeaders = {}
        self.dynamicRowHeaders = {}

        # The following variables will be used to try to determine if we've
        # already handled this misspelt word (see readMisspeltWord() for
        # more details.

        self.lastTextLength = -1
        self.lastBadWord = ''
        self.lastStartOff = -1
        self.lastEndOff = -1

        # Used to determine whether the caret has moved to a new paragraph.
        #
        self.currentParagraph = None

        # Set the number of retries after a COMM_FAILURE to 1. The default
        # of 5 was not allowing Orca to be responsive in the event of OOo
        # going into crash recovery mode (see bug #397787).
        #
        self.commFailureAttemptLimit = 1

        # The default set of text attributes to speak to the user. The
        # only difference over the default set in settings.py is to add
        # in "left-margin:" and "right-margin:".

        self.enabledBrailledTextAttributes = \
          "size:; family-name:; weight:400; indent:0mm; left-margin:0mm; " \
          "right-margin:0mm; underline:none; strikethrough:none; " \
          "justification:left; style:normal;"
        self.enabledSpokenTextAttributes = \
          "size:; family-name:; weight:400; indent:0mm; left-margin:0mm; " \
          "right-margin:0mm; underline:none; strikethrough:none; " \
          "justification:left; style:normal;"

    def activate(self):
        """Called when this script is activated."""
        self.savedreadTableCellRow = settings.readTableCellRow
        settings.readTableCellRow = False

        self.savedEnabledBrailledTextAttributes = \
            settings.enabledBrailledTextAttributes
        settings.enabledBrailledTextAttributes = \
            self.enabledBrailledTextAttributes

        self.savedEnabledSpokenTextAttributes = \
            settings.enabledSpokenTextAttributes
        settings.enabledSpokenTextAttributes = self.enabledSpokenTextAttributes

    def deactivate(self):
        """Called when this script is deactivated."""
        settings.readTableCellRow = self.savedreadTableCellRow
        settings.enabledBrailledTextAttributes = \
            self.savedEnabledBrailledTextAttributes
        settings.enabledSpokenTextAttributes = \
            self.savedEnabledSpokenTextAttributes

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["object:state-changed:focused"]           = \
            self.onStateChanged
        listeners["object:state-changed:sensitive"]         = \
            self.onStateChanged
        listeners["object:state-changed:active"]            = \
            self.onStateChanged
        listeners["object:state-changed:checked"]           = \
            self.onStateChanged

        return listeners

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """

        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return SpeechGenerator(self)

    def getWhereAmI(self):
        """Returns the "where am I" class for this script.
        """

        return WhereAmI(self)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. In this particular case,
        we just want to be able to add a handler to return the contents of
        the input line.
        """

        default.Script.setupInputEventHandlers(self)

        self.inputEventHandlers["speakInputLineHandler"] = \
            input_event.InputEventHandler(
                Script.speakInputLine,
                # Translators: this is the input line of a spreadsheet
                # (i.e., the place where enter formulas)
                #
                _("Speaks the contents of the input line."))

        self.inputEventHandlers["setDynamicColumnHeadersHandler"] = \
            input_event.InputEventHandler(
                Script.setDynamicColumnHeaders,
                # Translators: Orca allows you to dynamically define which
                # row of a spreadsheet or table counts as column headers.
                #
                _("Set the row to use as dynamic column headers " \
                  "when speaking calc cells."))

        self.inputEventHandlers["clearDynamicColumnHeadersHandler"] = \
            input_event.InputEventHandler(
                Script.clearDynamicColumnHeaders,
                # Translators: Orca allows you to dynamically define which
                # row of a spreadsheet or table counts as column headers.
                #
                _("Clears the dynamic column headers."))

        self.inputEventHandlers["setDynamicRowHeadersHandler"] = \
            input_event.InputEventHandler(
                Script.setDynamicRowHeaders,
                # Translators: Orca allows you to dynamically define which
                # column of a spreadsheet or table counts as row headers.
                #
                _("Set the column to use as dynamic row headers " \
                  "to use when speaking calc cells."))

        self.inputEventHandlers["clearDynamicRowHeadersHandler"] = \
            input_event.InputEventHandler(
                Script.clearDynamicRowHeaders,
                # Translators: Orca allows you to dynamically define which
                # column of a spreadsheet or table counts as row headers.
                #
                _("Clears the dynamic row headers"))

    def getKeyBindings(self):
        """Defines the key bindings for this script. Setup the default
        key bindings, then add one in for reading the input line.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = default.Script.getKeyBindings(self)

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["speakInputLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "r",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["setDynamicColumnHeadersHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "r",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["clearDynamicColumnHeadersHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "c",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["setDynamicRowHeadersHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "c",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["clearDynamicRowHeadersHandler"],
                2))

        return keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkVBox contain the application unique configuration
        GUI items for the current application.
        """

        vbox = gtk.VBox(False, 0)
        vbox.set_border_width(12)
        gtk.Widget.show(vbox)

        # Checkbox for "Speak spread sheet cell coordinates".
        #
        # Translators: If checked, then Orca will speak the coordinates
        # of the current spread sheet cell. Coordinates are the row and
        # column position within the spread sheet (i.e. A1, B1, C2 ...)
        #
        label = _("Speak spread sheet cell coordinates")
        self.speakCellCoordinatesCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakCellCoordinatesCheckButton)
        gtk.Box.pack_start(vbox, self.speakCellCoordinatesCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakCellCoordinatesCheckButton,
                                    speakCellCoordinates)

        return vbox

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        global speakCellCoordinates

        prefs.writelines("\n")
        speakCellCoordinates = \
                 self.speakCellCoordinatesCheckButton.get_active()
        prefs.writelines( \
                 "orca.scripts.StarOffice.speakCellCoordinates = %s\n" % \
                 speakCellCoordinates)

    def getAppState(self):
        """Returns an object that can be passed to setAppState.  This
        object will be use by setAppState to restore any state information
        that was being maintained by the script."""
        return [default.Script.getAppState(self),
                self.dynamicColumnHeaders,
                self.dynamicRowHeaders]

    def setAppState(self, appState):
        """Sets the application state using the given appState object.

        Arguments:
        - appState: an object obtained from getAppState
        """
        try:
            [defaultAppState,
             self.dynamicColumnHeaders,
             self.dynamicRowHeaders] = appState
            default.Script.setAppState(self, defaultAppState)
        except:
            debug.printException(debug.LEVEL_WARNING)

    def adjustForWriterTable(self, obj):
        """Check to see if we are in Writer, where the object with focus
        is a paragraph, and the parent is the table cell. If it is, then,
        return the parent table cell otherwise return the current object.

        Arguments:
        - obj: the accessible object to check.

        Returns parent table cell (if in a Writer table ) or the current
        object.
        """

        if obj.getRole() == pyatspi.ROLE_PARAGRAPH and \
           obj.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            return obj.parent
        else:
            return obj

    def getTable(self, obj):
        """Get the table that this table cell is in.

        Arguments:
        - obj: the table cell.

        Return the table that this table cell is in, or None if this object
        isn't in a table.
        """

        obj = self.adjustForWriterTable(obj)
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL and obj.parent:
            try:
                table = obj.parent.queryTable()
            except NotImplementedError:
                table = None

        return table

    def getDynamicColumnHeaderCell(self, obj, column):
        """Given a table cell, return the dynamic column header cell
        associated with it.

        Arguments:
        - obj: the table cell.
        - column: the column that this dynamic header is on.

        Return the dynamic column header cell associated with the given
        table cell.
        """

        obj = self.adjustForWriterTable(obj)
        accCell = None
        parent = obj.parent
        try:
            parentTable = parent.queryTable()
        except NotImplementedError:
            parentTable = None

        if parent and parentTable:
            row = parentTable.getRowAtIndex(obj.getIndexInParent())
            accCell = parentTable.getAccessibleAt(row, column)

        return accCell

    def getDynamicRowHeaderCell(self, obj, row):
        """Given a table cell, return the dynamic row header cell
        associated with it.

        Arguments:
        - obj: the table cell.
        - row: the row that this dynamic header is on.

        Return the dynamic row header cell associated with the given
        table cell.
        """

        obj = self.adjustForWriterTable(obj)
        accCell = None
        parent = obj.parent
        try:
            parentTable = parent.queryTable()
        except NotImplementedError:
            parentTable = None

        if parent and parentTable:
            column = parentTable.getColumnAtIndex(obj.getIndexInParent())
            accCell = parentTable.getAccessibleAt(row, column)

        return accCell

    def locateInputLine(self, obj):
        """Return the spread sheet input line. This only needs to be found
        the very first time a spread sheet table cell gets focus. We use the
        table cell to work back up the component hierarchy until we have found
        the common panel that both it and the input line reside in. We then
        use that as the base component to search for a component which has a
        paragraph role. This will be the input line.

        Arguments:
        - obj: the spread sheet table cell that has just got focus.

        Returns the spread sheet input line component.
        """

        inputLine = None
        panel = obj.parent.parent.parent.parent
        if panel and panel.getRole() == pyatspi.ROLE_PANEL:
            allParagraphs = self.findByRole(panel, pyatspi.ROLE_PARAGRAPH)
            if len(allParagraphs) == 1:
                inputLine = allParagraphs[0]
            else:
                debug.println(debug.LEVEL_SEVERE,
                    "StarOffice: locateInputLine: incorrect paragraph count.")
        else:
            debug.println(debug.LEVEL_SEVERE,
                  "StarOffice: locateInputLine: couldn't find common panel.")

        return inputLine

    def getSpreadSheetRowRange(self, obj):
        """If this is spread sheet cell, return the start and end indices
        of the spread sheet cells for the table that obj is in. Otherwise
        return the complete range (0, parentTable.nColumns).

        Arguments:
        - obj: a spread sheet table cell.

        Returns the start and end table cell indices.
        """

        parent = obj.parent
        try:
            parentTable = parent.queryTable()
        except NotImplementedError:
            parentTable = None

        startIndex = 0
        endIndex = parentTable.nColumns

        if self.isSpreadSheetCell(obj):
            extents = parent.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
            y = extents.y
            leftX = extents.x + 1
            leftCell = \
                parent.queryComponent().getAccessibleAtPoint(leftX, y, 0)
            if leftCell:
                table = leftCell.parent.queryTable()
                startIndex = table.getColumnAtIndex(leftCell.getIndexInParent())

            rightX = extents.x + extents.width - 1
            rightCell = \
                parent.queryComponent().getAccessibleAtPoint(rightX, y, 0)
            if rightCell:
                table = rightCell.parent.queryTable()
                endIndex = table.getColumnAtIndex(rightCell.getIndexInParent())

        return [startIndex, endIndex]

    def isSpreadSheetCell(self, obj, startFromTable=False):
        """Return an indication of whether the given obj is a spread sheet
        table cell.

        Arguments:
        - obj: the object to check.
        - startFromTable: if True, then the component hierarchy check should
                          start from a table (as opposed to a table cell).

        Returns True if this is a table cell, False otherwise.
        """

        found = False
        rolesList = [pyatspi.ROLE_TABLE_CELL, \
                     pyatspi.ROLE_TABLE, \
                     pyatspi.ROLE_UNKNOWN, \
                     pyatspi.ROLE_SCROLL_PANE, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_ROOT_PANE, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if startFromTable:
            rolesList = rolesList[1:]
        if self.isDesiredFocusedItem(obj, rolesList):
            # We've found a table cell with the correct hierarchy. Now check
            # that we are in a spreadsheet as opposed to the writer application.
            # See bug #382408.
            #
            current = obj.parent
            while current.getRole() != pyatspi.ROLE_APPLICATION:
                # Translators: this represents a match on a window title.
                # We're looking for frame that ends in "Calc", representing
                # an OpenOffice or StarOffice spreadsheet window.  We
                # really try to avoid doing this kind of thing, but sometimes
                # it is necessary and we apologize.
                #
                if current.getRole() in [pyatspi.ROLE_FRAME,
                                         pyatspi.ROLE_ROOT_PANE] and \
                   (current.name and current.name.endswith(_("Calc"))):
                    found = True
                current = current.parent

        return found     

    def isDesiredFocusedItem(self, obj, rolesList):
        """Called to determine if the given object and it's hierarchy of
           parent objects, each have the desired roles.

           This is an override because of bugs in OOo's child/parent symmetry.
           See Script._getParent().

        Arguments:
        - obj: the accessible object to check.
        - rolesList: the list of desired roles for the components and the
          hierarchy of its parents.

        Returns True if all roles match.
        """
        current = obj
        for role in rolesList:
            if current is None:
                return False

            if isinstance(role, str):
                current_role = current.getRoleName()
            else:
                current_role = current.getRole()

            if current_role != role:
                return False
            
            current = self._getParent(current)

        return True   

    def printHierarchy(self, root, ooi, indent="",
                       onlyShowing=True, omitManaged=True):
        """Prints the accessible hierarchy of all children

        This is an override because of bugs in OOo's child/parent symmetry.
        See Script._getParent().

        Arguments:
        -indent:      Indentation string
        -root:        Accessible where to start
        -ooi:         Accessible object of interest
        -onlyShowing: If True, only show children painted on the screen
        -omitManaged: If True, omit children that are managed descendants
        """

        if not root:
            return

        if root == ooi:
            print indent + "(*)", debug.getAccessibleDetails(root)
        else:
            print indent + "+-", debug.getAccessibleDetails(root)

        rootManagesDescendants = root.getState().contains( \
                                      pyatspi.STATE_MANAGES_DESCENDANTS)

        for child in root:
            if child == root:
                print indent + "  " + "WARNING CHILD == PARENT!!!"
            elif not child:
                print indent + "  " + "WARNING CHILD IS NONE!!!"
            elif self._getParent(child) != root:
                print indent + "  " + "WARNING CHILD.PARENT != PARENT!!!"
            else:
                paint = (not onlyShowing) or (onlyShowing and \
                         child.getState().contains(pyatspi.STATE_SHOWING))
                paint = paint \
                        and ((not omitManaged) \
                             or (omitManaged and not rootManagesDescendants))

                if paint:
                    self.printHierarchy(child,
                                        ooi,
                                        indent + "  ",
                                        onlyShowing,
                                        omitManaged)

    def _getParent(self, obj):
        """This method gets a node's parent will be doubly linked.
        See bugs:
        http://www.openoffice.org/issues/show_bug.cgi?id=78117
        http://bugzilla.gnome.org/show_bug.cgi?id=489490
        """
        parent = obj.parent
        if parent and parent.getRole() in (pyatspi.ROLE_ROOT_PANE,
                                           pyatspi.ROLE_DIALOG):
            app = obj.getApplication()
            for frame in app:
                if frame.childCount < 1 or \
                      frame[0].getRole() not in (pyatspi.ROLE_ROOT_PANE,
                                                 pyatspi.ROLE_OPTION_PANE): 
                    continue
                root_pane = frame[0]
                if obj in root_pane:
                    return root_pane
        return parent


    def checkForTableBoundry(self, oldFocus, newFocus):
        """Check to see if we've entered or left a table.
        When entering a table, announce the table dimensions.
        When leaving a table, announce that the table has been exited.

        Arguments:
        - oldFocus: Accessible that is the old locus of focus
        - newFocus: Accessible that is the new locus of focus
        """

        if oldFocus == None or newFocus == None:
            return

        oldFocusIsTable = None
        while oldFocus.getRole() != pyatspi.ROLE_APPLICATION:
            if oldFocus.getRole() == pyatspi.ROLE_TABLE:
                oldFocusIsTable = oldFocus
                break
            oldFocus = oldFocus.parent

        newFocusIsTable = None
        while newFocus.getRole() != pyatspi.ROLE_APPLICATION:
            if newFocus.getRole() == pyatspi.ROLE_TABLE:
                newFocusIsTable = newFocus
                break
            newFocus = newFocus.parent

        if oldFocusIsTable == None and newFocusIsTable != None:
            rows = newFocusIsTable.queryTable().nRows
            columns = newFocusIsTable.queryTable().nColumns
            # We've entered a table.  Announce the dimensions.
            #
            line = _("table with %d rows and %d columns.") % (rows, columns)
            speech.speak(line)
        elif oldFocusIsTable != None and newFocusIsTable == None:
            # We've left a table.  Announce this fact.
            #
            speech.speak(_("leaving table."))

    def speakInputLine(self, inputEvent):
        """Speak the contents of the spread sheet input line (assuming we
        have a handle to it - generated when we first focus on a spread
        sheet table cell.

        This will be either the contents of the table cell that has focus
        or the formula associated with it.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "StarOffice.speakInputLine.")

        # Check to see if the current focus is a table cell.
        #
        if self.isSpreadSheetCell(orca_state.locusOfFocus):
            try:
                if self.inputLineForCell and self.inputLineForCell.queryText():
                    inputLine = self.getText(self.inputLineForCell, 0, -1)
                    if not inputLine:
                        # Translators: this is used to announce that the
                        # current input line in a spreadsheet is blank/empty.
                        #
                        inputLine = _("empty")
                    debug.println(self.debugLevel,
                        "StarOffice.speakInputLine: contents: %s" % inputLine)
                    speech.speak(inputLine)
            except NotImplementedError:
                pass

    def getTableRow(self, cell):
        """Get the row number in the table that this table cell is on.

        Arguments:
        - cell: the table cell to get the row number for.

        Return the row number that this table cell is on, or None if
        this isn't a table cell.
        """

        row = None
        cell = self.adjustForWriterTable(cell)
        if cell.getRole() == pyatspi.ROLE_TABLE_CELL:
            parent = cell.parent
            try:
                parentTable = parent.queryTable()
            except NotImplementedError:
                parentTable = None

            if parent and parentTable:
                row = parentTable.getRowAtIndex(cell.getIndexInParent())

        return row

    def getTableColumn(self, cell):
        """Get the column number in the table that this table cell is on.

        Arguments:
        - cell: the table cell to get the column number for.

        Return the column number that this table cell is on, or None if
        this isn't a table cell.
        """

        column = None
        cell = self.adjustForWriterTable(cell)
        if cell.getRole() == pyatspi.ROLE_TABLE_CELL:
            parent = cell.parent
            try:
                parentTable = parent.queryTable()
            except NotImplementedError:
                parentTable = None

            if parent and parentTable:
                column = parentTable.getColumnAtIndex(cell.getIndexInParent())

        return column

    def setDynamicColumnHeaders(self, inputEvent):
        """Set the row for the dynamic header columns to use when speaking
        calc cell entries. In order to set the row, the user should first set
        focus to the row that they wish to define and then press Insert-r.

        Once the user has defined the row, it will be used to first speak
        this header when moving between columns.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "StarOffice.setDynamicColumnHeaders.")

        table = self.getTable(orca_state.locusOfFocus)
        if table:
            row = self.getTableRow(orca_state.locusOfFocus)
            self.dynamicColumnHeaders[table] = row
            # Translators: Orca allows you to dynamically define which
            # row of a spreadsheet or table counts as column headers.
            #
            line = _("Dynamic column header set for row %d") % (row+1)
            speech.speak(line)
            braille.displayMessage(line)

        return True

    def clearDynamicColumnHeaders(self, inputEvent):
        """Clear the dynamic header column.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "StarOffice.clearDynamicColumnHeaders.")

        table = self.getTable(orca_state.locusOfFocus)
        if table:
            row = self.getTableRow(orca_state.locusOfFocus)
            try:
                del self.dynamicColumnHeaders[table]
                # Translators: Orca allows you to dynamically define which
                # row of a spreadsheet or table counts as column headers.
                #
                line = _("Dynamic column header cleared.")
                speech.stop()
                speech.speak(line)
                braille.displayMessage(line)
            except:
                pass

        return True

    def columnConvert(self, column):
        """ Convert a spreadsheet column into it's column label

        Arguments:
        - column: the column number to convert.

        Returns a string representing the spread sheet column.
        """

        base26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        if column <= len(base26):
            return base26[column-1]

        res = ""
        while column > 0:
            digit = column % len(base26)
            res = " " + base26[digit-1] + res
            column /= len(base26)

        return res

    def setDynamicRowHeaders(self, inputEvent):
        """Set the column for the dynamic header rows to use when speaking
        calc cell entries. In order to set the column, the user should first
        set focus to the column that they wish to define and then press
        Insert-c.

        Once the user has defined the column, it will be used to first speak
        this header when moving between rows.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "StarOffice.setDynamicRowHeaders.")

        table = self.getTable(orca_state.locusOfFocus)
        if table:
            column = self.getTableColumn(orca_state.locusOfFocus)
            self.dynamicRowHeaders[table] = column
            # Translators: Orca allows you to dynamically define which
            # column of a spreadsheet or table counts as row headers.
            #
            line = _("Dynamic row header set for column %s") \
                   % self.columnConvert(column+1)
            speech.speak(line)
            braille.displayMessage(line)

        return True

    def clearDynamicRowHeaders(self, inputEvent):
        """Clear the dynamic row headers.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "StarOffice.clearDynamicRowHeaders.")

        table = self.getTable(orca_state.locusOfFocus)
        if table:
            column = self.getTableColumn(orca_state.locusOfFocus)
            try:
                del self.dynamicRowHeaders[table]
                # Translators: Orca allows you to dynamically define which
                # column of a spreadsheet or table counts as row headers.
                #
                line = _("Dynamic row header cleared.")
                speech.stop()
                speech.speak(line)
                braille.displayMessage(line)
            except:
                pass

        return True

    def readMisspeltWord(self, event, pane):
        """Speak/braille the current misspelt word plus its context.
           The spell check dialog contains a "paragraph" which shows the
           context for the current spelling mistake. After speaking/brailling
           the default action for this component, that a selection of the
           surronding text from that paragraph with the misspelt word is also
           spoken.

        Arguments:
        - event: the event.
        - pane: the option pane in the spell check dialog.
        """

        paragraph = self.findByRole(pane, pyatspi.ROLE_PARAGRAPH)

        # Determine which word is the misspelt word. This word will have
        # non-default text attributes associated with it.

        textLength = paragraph[0].queryText().characterCount
        startFound = False
        startOff = 0
        endOff = textLength
        for i in range(0, textLength):
            attributes = paragraph[0].queryText().getAttributes(i)
            if len(attributes[0]) != 0:
                if not startFound:
                    startOff = i
                    startFound = True
            else:
                if startFound:
                    endOff = i
                    break

        badWord = self.getText(paragraph[0], startOff, endOff - 1)

        # Note that we often get two or more of these focus or property-change
        # events each time there is a new misspelt word. We extract the
        # length of the line of text, the misspelt word, the start and end
        # offsets for that word and compare them against the values saved
        # from the last time this routine was called. If they are the same
        # then we ignore it.

        debug.println(self.debugLevel, \
            "StarOffice.readMisspeltWord: type=%s  word=%s(%d,%d)  len=%d" % \
            (event.type, badWord, startOff, endOff, textLength))

        if (textLength == self.lastTextLength) and \
           (badWord == self.lastBadWord) and \
           (startOff == self.lastStartOff) and \
           (endOff == self.lastEndOff):
            return

        # Create a list of all the words found in the misspelt paragraph.
        #
        text = self.getText(paragraph[0], 0, -1)
        allTokens = text.split()

        self.speakMisspeltWord(allTokens, badWord)

        # Save misspelt word information for comparison purposes next
        # time around.
        #
        self.lastTextLength = textLength
        self.lastBadWord = badWord
        self.lastStartOff = startOff
        self.lastEndOff = endOff

    def endOfLink(self, obj, word, startOffset, endOffset):
        """Return an indication of whether the given word contains the
           end of a hypertext link.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        - word: the word to check
        - startOffset: the start offset for this word
        - endOffset: the end offset for this word

        Returns True if this word contains the end of a hypertext link.
        """

        nLinks = obj.queryHypertext().getNLinks()
        links = []
        for i in range(0, nLinks):
            links.append(obj.queryHypertext().getLink(i))

        for link in links:
            if link.endIndex > startOffset and \
               link.endIndex <= endOffset:
                return True

        return False

    def sayWriterWord(self, obj, word, startOffset, endOffset):
        """Speaks the given word in the appropriate voice. If this word is
        a hypertext link and it is also at the end offset for one of the
        links, then the word "link" is also spoken.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        - word: the word to speak
        - startOffset: the start offset for this word
        - endOffset: the end offset for this word
        """

        voices = settings.voices

        for i in range(startOffset, endOffset):
            if self.getLinkIndex(obj, i) >= 0:
                voice = voices[settings.HYPERLINK_VOICE]
                break
            elif word.isupper():
                voice = voices[settings.UPPERCASE_VOICE]
            else:
                voice = voices[settings.DEFAULT_VOICE]

        speech.speak(word, voice)
        if self.endOfLink(obj, word, startOffset, endOffset):
            speech.speak(_("link"))

    def isSetupDialog(self, obj):
        """ Check to see if this object is in the Setup dialog by walking
        back up the object hierarchy until we get to the dialog object and
        checking to see if it has a name that starts with "Welcome to
        StarOffice".

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface

        Returns an indication of whether this object is in the Setup dialog.
        """

        found = False
        while obj and obj.getRole() != pyatspi.ROLE_APPLICATION:
            # Translators: this is the title of the window that
            # you get when starting StarOffice.  The translated
            # form has to match what StarOffice/OpenOffice is
            # using.  We hate keying off stuff like this, but
            # we're forced to do so in this case.
            #
            if obj.getRole() == pyatspi.ROLE_DIALOG and \
                (obj.name and obj.name.startswith(_("Welcome to StarOffice"))):
                debug.println(self.debugLevel,
                              "StarOffice.isSetupDialog: True.")
                found = True

            obj = obj.parent

        return found

    def speakSetupLabel(self, label):
        """Speak this Setup dialog label.

        Arguments:
        - label: the Setup dialog Label.
        """

        text = self.getDisplayedText(label)
        if text:
            speech.speak(text)

    def handleSetupPanel(self, panel):
        """Find all the labels in this Setup panel and speak them.

        Arguments:
        - panel: the Setup panel.
        """

        allLabels = self.findByRole(panel, pyatspi.ROLE_LABEL)
        for label in allLabels:
            self.speakSetupLabel(label)

    def __isAvailableFieldsPanel(self, event):
        """If we are in the sbase Table Wizard, try to reduce the numerous
        utterances of "Available fields panel". See bug #465087 for more 
        details.

        Arguments:
        - event: the object state change event.
        """

        # Translators: this represents a match with the name of the
        # "Available fields" list in the Tables wizard dialog in the
        # the OOo oobase database application. We're looking for the
        # accessible object name starting with "Available fields".
        # We really try to avoid doing this kind of thing, but
        # sometimes it is necessary and we apologize.
        #
        panelName = _("Available fields")

        isPanel = False
        if event.type == "object:state-changed:focused":
            rolesList = [pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_SCROLL_PANE, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_OPTION_PANE, \
                         pyatspi.ROLE_DIALOG, \
                         pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(event.source, rolesList):
                tmp = event.source.parent.parent
                if tmp.name.startswith(panelName):
                    isPanel = True

            if not isPanel:
                rolesList = [pyatspi.ROLE_SCROLL_PANE, \
                             pyatspi.ROLE_PANEL, \
                             pyatspi.ROLE_OPTION_PANE, \
                             pyatspi.ROLE_DIALOG, \
                             pyatspi.ROLE_APPLICATION]
                if self.isDesiredFocusedItem(event.source, rolesList):
                    if event.source.parent.name.startswith(panelName):
                        isPanel = True

            if not isPanel:
                rolesList = [pyatspi.ROLE_PANEL, \
                             pyatspi.ROLE_OPTION_PANE, \
                             pyatspi.ROLE_DIALOG, \
                             pyatspi.ROLE_APPLICATION]
                if self.isDesiredFocusedItem(event.source, rolesList):
                    if event.source.name.startswith(panelName):
                        isPanel = True

        return isPanel

    # This method tries to detect and handle the following cases:
    # 0) Writer: find command.
    # 1) Writer: text paragraph.
    # 2) Writer: spell checking dialog.
    # 3) Welcome to StarOffice dialog.
    # 4) Calc: cell editor.
    # 5) Calc: name box.
    # 6) Calc: spreadsheet cell.

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        brailleGen = self.brailleGenerator

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

        # self.printAncestry(event.source)

        # 0) Writer: find command
        #
        # Check to see if this is this is for the find command. See
        # comment #18 of bug #354463.
        #
        if self.findCommandRun and \
           event.type.startswith("object:state-changed:focused"):
            self.findCommandRun = False
            self.find()
            return

        # 1) Writer: text paragraph.
        #
        # We need to handle two things here:
        #
        # If the old locus of focus was on the File->New->Text Document
        # menu item and we are currently have focus on an empty text
        # paragraph, then we've just created the first new text document
        # in Writer. Announce it by doing a "where am I".
        #
        # Also, when the focus is on a paragraph in the Document view of
        # the Writer, then just speak/braille the current line (rather than
        # speaking a bogus initial "paragraph" utterance as well).

        rolesList = [pyatspi.ROLE_PARAGRAPH, \
                     pyatspi.ROLE_UNKNOWN, \
                     pyatspi.ROLE_SCROLL_PANE, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_ROOT_PANE, \
                     pyatspi.ROLE_FRAME]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                  "StarOffice.locusOfFocusChanged - Writer: text paragraph.")

            result = self.getTextLineAtCaret(event.source)
            result[0] = result[0].decode("UTF-8")

            # Translators: this is the name of the menu item people
            # use in StarOffice to create a new text document.  It's
            # at File->New->Text Document.  The translated form has to
            # match what StarOffice/OpenOffice is using. We hate
            # keying off stuff like this, but we're forced to do so in
            # this case.
            #
            if oldLocusOfFocus and \
               oldLocusOfFocus.getRole() == pyatspi.ROLE_MENU_ITEM and \
               oldLocusOfFocus.name == _("Text Document") and \
               len(result[0]) == 0:
                self.whereAmI.whereAmI(None)

            # Check to see if there are any hypertext links in this paragraph.
            # If no, then just speak the whole line. Otherwise, split the
            # line into words and call sayWriterWord() to speak that token
            # in the appropriate voice.
            #
            try:
                hypertext = event.source.queryHypertext()
            except NotImplementedError:
                hypertext = None

            if not hypertext or (hypertext.getNLinks() == 0):
                if settings.enableSpeechIndentation:
                    self.speakTextIndentation(event.source,
                                              result[0].encode("UTF-8"))
                speech.speak(result[0].encode("UTF-8"), None, False)
            else:
                started = False
                startOffset = 0
                for i in range(0, len(result[0])):
                    if result[0][i] == ' ':
                        if started:
                            endOffset = i
                            self.sayWriterWord(event.source,
                                result[0][startOffset:endOffset+1].encode( \
                                                                    "UTF-8"),
                                startOffset, endOffset)
                            startOffset = i
                            started = False
                    else:
                        if not started:
                            startOffset = i
                            started = True

                if started:
                    endOffset = len(result[0])
                    self.sayWriterWord(event.source,
                        result[0][startOffset:endOffset].encode("UTF-8"),
                        startOffset, endOffset)

            braille.displayRegions(brailleGen.getBrailleRegions(event.source))

            return

        # 2) Writer: spell checking dialog.
        #
        # Check to see if the Spell Check dialog has just appeared and got
        # focus. If it has, then speak/braille the current misspelt word
        # plus its context.
        #
        # Note that in order to make sure that this focus event is for the
        # spell check dialog, a check is made of the localized name of the
        # option pane. Translators for other locales will need to ensure that
        # their translation of this string matches what StarOffice uses in
        # that locale.

        rolesList = [pyatspi.ROLE_PUSH_BUTTON, \
                     pyatspi.ROLE_OPTION_PANE, \
                     pyatspi.ROLE_DIALOG, \
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(event.source, rolesList):
            pane = event.source.parent
            # Translators: this is what the name of spell checking
            # window in StarOffice begins with.  The translated form
            # has to match what StarOffice/OpenOffice is using.  We
            # hate keying off stuff like this, but we're forced to do
            # so in this case.
            #
            if pane.name.startswith(_("Spellcheck:")):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - " \
                    + "Writer: spell check dialog.")

                self.readMisspeltWord(event, pane)

                # Fall-thru to process the event with the default handler.

        # 3) Welcome to StarOffice dialog.
        #
        # Check to see if the object that just got focus is in the Setup
        # dialog. If it is, then check for a variety of scenerios.

        if self.isSetupDialog(event.source):

            # Check for 2. License Agreement: Scroll Down button.
            #
            rolesList = [pyatspi.ROLE_PUSH_BUTTON, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_OPTION_PANE, \
                         pyatspi.ROLE_DIALOG, \
                         pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "License Agreement screen: Scroll Down button.")
                self.handleSetupPanel(event.source.parent)
                speech.speak(_("Note that the Scroll Down button has " \
                               "to be pressed numerous times."))

            # Check for 2. License Agreement: Accept button.
            #
            rolesList = [pyatspi.ROLE_UNKNOWN, \
                         pyatspi.ROLE_SCROLL_PANE, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_OPTION_PANE, \
                         pyatspi.ROLE_DIALOG, \
                         pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "License Agreement screen: accept button.")
                speech.speak( \
                    _("License Agreement Accept button now has focus."))

            # Check for 3. Personal Data: Transfer Personal Data check box.
            #
            rolesList = [pyatspi.ROLE_CHECK_BOX, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_OPTION_PANE, \
                         pyatspi.ROLE_DIALOG, \
                         pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "Personal Data: Transfer Personal Data check box.")
                self.handleSetupPanel(event.source.parent)

            # Check for 4. User name: First Name text field.
            #
            rolesList = [pyatspi.ROLE_TEXT, \
                        pyatspi.ROLE_PANEL, \
                        pyatspi.ROLE_OPTION_PANE, \
                        pyatspi.ROLE_DIALOG, \
                        pyatspi.ROLE_APPLICATION]
            # Translators: this is the name of the field in the StarOffice
            # setup dialog that is asking for the first name of the user.
            # The translated form has to match what StarOffice/OpenOffice
            # is using.  We hate keying off stuff like this, but we're
            # forced to in this case.
            #
            if self.isDesiredFocusedItem(event.source, rolesList) and \
               event.source.name == _("First name"):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "User name: First Name text field.")

                # Just speak the informative labels at the top of the panel
                # (and not the ones that have LABEL_FOR relationships).
                #
                panel = event.source.parent
                allLabels = self.findByRole(panel, pyatspi.ROLE_LABEL)
                for label in allLabels:
                    relations = label.getRelationSet()
                    hasLabelFor = False
                    for relation in relations:
                        if relation.getRelationType() \
                               == pyatspi.RELATION_LABEL_FOR:
                            hasLabelFor = True
                    if not hasLabelFor:
                        self.speakSetupLabel(label)

            # Check for 5. Registration: Register Now radio button.
            #
            rolesList = [pyatspi.ROLE_RADIO_BUTTON, \
                        pyatspi.ROLE_PANEL, \
                        pyatspi.ROLE_OPTION_PANE, \
                        pyatspi.ROLE_DIALOG, \
                        pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "Registration: Register Now radio button.")
                self.handleSetupPanel(event.source.parent)

        # 4) Calc: cell editor.
        #
        # Check to see if we are editing a spread sheet cell. If so, just
        # return to avoid uttering something like "Paragraph 0 paragraph".
        #
        rolesList = [pyatspi.ROLE_PARAGRAPH, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_UNKNOWN, \
                     pyatspi.ROLE_SCROLL_PANE, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_ROOT_PANE, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel, "StarOffice.locusOfFocusChanged - " \
                          + "Calc: cell editor.")
            return

        # 5) Calc: name box
        #
        # Check to see if the focus has just moved to the Name Box combo
        # box in Calc. If so, then replace the non-existent name with a
        # simple one before falling through and calling the default
        # locusOfFocusChanged method, which in turn will result in our
        # _getSpeechForComboBox() method being called.
        #
        rolesList = [pyatspi.ROLE_COMBO_BOX, \
                     pyatspi.ROLE_TOOL_BAR, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_ROOT_PANE, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]

        if self.isDesiredFocusedItem(event.source, rolesList) \
            and (not event.source.name or len(event.source.name) == 0):
            debug.println(self.debugLevel, "StarOffice.locusOfFocusChanged - " \
                          + "Calc: name box.")
            # Translators: this is our made up name for the nameless field
            # in StarOffice/OpenOffice calc that allows you to type in a
            # cell coordinate (e.g., A4) and then move to it.
            #
            event.source.name = _("Move to cell")

        # 6) Calc: spreadsheet cell.
        #
        # Check to see if this is a Calc: spread sheet cell. If it is then
        # we don't want to speak "not selected" after giving the cell
        # location and contents (which is what the default locusOfFocusChanged
        # method would now do).
        #
        if self.isSpreadSheetCell(event.source, True):
            if newLocusOfFocus:
                self.updateBraille(newLocusOfFocus)
                utterances = self.speechGenerator.getSpeech(newLocusOfFocus,
                                                            False)
                speech.speakUtterances(utterances)

                # Save the current row and column information in the table
                # cell's table, so that we can use it the next time.
                #
                try:
                    table = newLocusOfFocus.parent.queryTable()
                except:
                    pass
                else:
                    column = table.getColumnAtIndex( \
                                    newLocusOfFocus.getIndexInParent())
                    self.pointOfReference['lastColumn'] = column
                    row = table.getRowAtIndex( \
                                    newLocusOfFocus.getIndexInParent())
                    self.pointOfReference['lastRow'] = row
                return

        # Pass the event onto the parent class to be handled in the default way.

        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

    # This method tries to detect and handle the following cases:
    # 1) Setup dialog.

    def onWindowActivated(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

        # self.printAncestry(event.source)

        # 1) Setup dialog.
        #
        # Check to see if the Setup dialog window has just been activated.
        # If it has, then find the panel within it that has no name and
        # speak all the labels within that panel.
        #
        if self.isSetupDialog(event.source):
            debug.println(self.debugLevel,
                "StarOffice.onWindowActivated - Setup dialog: Welcome screen.")

            allPanels = self.findByRole(event.source.parent,
                                        pyatspi.ROLE_PANEL)
            for panel in allPanels:
                if not panel.name:
                    allLabels = self.findByRole(panel, pyatspi.ROLE_LABEL)
                    for label in allLabels:
                        self.speakSetupLabel(label)
        else:
            # Pass the event onto the parent class to be handled in the
            # default way.
            #
            default.Script.onWindowActivated(self, event)


    # This method tries to detect and handle the following cases:
    # 1) Writer: spell checking dialog.

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

        # self.printAncestry(event.source)

        # 1) Writer: spell checking dialog.
        #
        # Check to see if if we've had a property-change event for the
        # accessible name for the option pane in the spell check dialog.
        # This (hopefully) means that the user has just corrected a
        # spelling mistake, in which case, speak/braille the current
        # misspelt word plus its context.
        #
        # Note that in order to make sure that this focus event is for the
        # spell check dialog, a check is made of the localized name of the
        # option pane. Translators for other locales will need to ensure that
        # their translation of this string matches what StarOffice uses in
        # that locale.

        rolesList = [pyatspi.ROLE_OPTION_PANE, \
                     pyatspi.ROLE_DIALOG, \
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(event.source, rolesList):
            pane = event.source
            # Translators: this is what the name of spell checking
            # window in StarOffice begins with.  The translated form
            # has to match what StarOffice/OpenOffice is using.  We
            # hate keying off stuff like this, but we're forced to do
            # so in this case.
            #
            if pane.name.startswith(_("Spellcheck:")):
                debug.println(self.debugLevel,
                      "StarOffice.onNameChanged - Writer: spell check dialog.")

                self.readMisspeltWord(event, pane)

                # Fall-thru to process the event with the default handler.

        # Pass the event onto the parent class to be handled in the default way.

        default.Script.onNameChanged(self, event)


    def onFocus(self, event):
        """Called whenever an object gets focus. Overridden in this script
        so that we can adjust the "focus:" events for the Calc Name combo
        box to reduce its verbosity (see bug #364407).

        Arguments:
        - event: the Event
        """

        rolesList = [pyatspi.ROLE_LIST, \
                     pyatspi.ROLE_COMBO_BOX, \
                     pyatspi.ROLE_TOOL_BAR, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_ROOT_PANE, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel, "StarOffice.onFocus - " \
                          + "Calc: Name combo box.")
            orca.setLocusOfFocus(None, event.source.parent, False)
            return

        # If we are FOCUSED on a paragraph inside a table cell (in Writer),
        # then speak/braille that parent table cell (see bug #382415).
        #
        if event.source.getRole() == pyatspi.ROLE_PARAGRAPH and \
           event.source.parent.getRole() == pyatspi.ROLE_TABLE_CELL and \
           event.source.getState().contains(pyatspi.STATE_FOCUSED):
            if self.lastCell != event.source.parent:
                default.Script.locusOfFocusChanged(self, event,
                                                   None, event.source.parent)
                self.lastCell = event.source.parent
            return

        default.Script.onFocus(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # If this is state change "focused" event and event.source isn't a
        # focused object, then just return. See bug #517502 for more details.
        #
        if event.type.startswith("object:state-changed:focused") and \
           not event.source.getState().contains(pyatspi.STATE_FOCUSED):
            return

        # Check to see if we are in the Presentation startup wizard. If so,
        # then speak the object that currently has focus.
        #
        if event.type.startswith("object:state-changed:sensitive") and \
           event.source.getRole() == pyatspi.ROLE_PANEL and \
           event.source.getState().contains(pyatspi.STATE_SENSITIVE):
            current = event.source.parent
            while current.getRole() != pyatspi.ROLE_APPLICATION:
                # Translators: this is the title of the window that
                # you get when using StarOffice Presentation Wizard. The
                # translated form has to match what
                # StarOffice/OpenOffice is using.  We hate keying off
                # stuff like this, but we're forced to do so in this
                # case.
                #
                if current.getRole() == pyatspi.ROLE_DIALOG and \
                   (current.name and \
                    current.name.startswith(_("Presentation Wizard"))):
                    self.locusOfFocusChanged(event, None, 
                                             orca_state.locusOfFocus)
                    break
                current = current.parent

        # If this is a state change "focused" event that we care about, and
        # we are in Writer, check to see if we are entering or leaving a table.
        #
        if event.type.startswith("object:state-changed:focused") and \
           event.detail1 == 1:
            current = event.source.parent
            while current.getRole() != pyatspi.ROLE_APPLICATION:
                # Translators: this is the title of the window that
                # you get when using StarOffice Writer.  The
                # translated form has to match what
                # StarOffice/OpenOffice is using.  We hate keying off
                # stuff like this, but we're forced to do so in this
                # case.
                #
                if current.getRole() == pyatspi.ROLE_FRAME and \
                   (current.name and current.name.endswith(_("Writer"))):
                    self.checkForTableBoundry(orca_state.locusOfFocus,
                                              event.source)
                    break
                current = current.parent

        # Prevent  "object:state-changed:active" events from activating
        # the find operation. See comment #18 of bug #354463.
        #
        if event.type.startswith("object:state-changed:active"):
            if self.findCommandRun:
                return

        # Announce when the toolbar buttons are toggled if we just toggled
        # them; not if we navigated to some text.
        #
        if event.type.startswith("object:state-changed:checked") and \
           (event.source.getRole() == pyatspi.ROLE_TOGGLE_BUTTON or \
            event.source.getRole() == pyatspi.ROLE_PUSH_BUTTON):
            weToggledIt = False
            if isinstance(orca_state.lastInputEvent, \
                          input_event.MouseButtonEvent):
                x = orca_state.lastInputEvent.x
                y = orca_state.lastInputEvent.y
                weToggledIt = event.source.queryComponent().contains(x, y, 0)

            elif isinstance(orca_state.lastInputEvent, \
                            input_event.KeyboardEvent):
                keyString = orca_state.lastNonModifierKeyEvent.event_string
                navKeys = ["Up", "Down", "Page_Up", "Page_Down", "Home", "End"]
                wasCommand = orca_state.lastInputEvent.modifiers \
                             & (1 << pyatspi.MODIFIER_CONTROL \
                              | 1 << pyatspi.MODIFIER_ALT \
                              | 1 << pyatspi.MODIFIER_META \
                              | 1 << pyatspi.MODIFIER_META2 \
                              | 1 << pyatspi.MODIFIER_META3)
                weToggledIt = wasCommand and keyString not in navKeys

            if weToggledIt:
                speech.speakUtterances(self.speechGenerator.getSpeech( \
                                       event.source, False))

        # If we are FOCUSED on a paragraph inside a table cell (in Writer),
        # then speak/braille that parent table cell (see bug #382415).
        #
        if event.type.startswith("object:state-changed:focused") and \
           event.source.getRole() == pyatspi.ROLE_PARAGRAPH and \
           event.source.parent.getRole() == pyatspi.ROLE_TABLE_CELL and \
           event.detail1 == 0 and \
           event.source.getState().contains(pyatspi.STATE_FOCUSED):

            # Check to see if the last input event was "Up" or "Down".
            # If it was, and we are in the same table cell as last time,
            # and if that table cell has more than one child, then just
            # get the speech for that single child, otherwise speak/braille
            # the parent table cell.
            #
            event_string = None
            if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
                event_string = orca_state.lastNonModifierKeyEvent.event_string
            if (event_string == "Up" or event_string == "Down") and \
               event.source.parent == self.lastCell and \
               event.source.parent.childCount > 1:
                default.Script.locusOfFocusChanged(self, event,
                                                   None, event.source)
            else:
                default.Script.locusOfFocusChanged(self, event,
                                                   None, event.source.parent)
            self.lastCell = event.source.parent
            return

        # Two events are received when the caret moves
        # to a new paragraph. The first is a focus event
        # (in the form of object:state-changed:focused
        # instead of focus:). The second is a caret-moved
        # event. Just set the locusOfFocus for the first event.
        #
        if event.type.startswith("object:state-changed:focused") and \
           event.source.getRole() == pyatspi.ROLE_PARAGRAPH and \
           event.source != self.currentParagraph:
            self.currentParagraph = event.source
            orca.setLocusOfFocus(event, event.source, False)
            return

        # If we are in the sbase Table Wizard, try to reduce the numerous
        # utterances of "Available fields panel". See bug #465087 for
        # more details.
        #
        if self.__isAvailableFieldsPanel(event):
            return

        # If we get "object:state-changed:focused" events for children of
        # a combo-box, just set the focus to the combo box. This is needed
        # to help reduce the verbosity of focusing on the Calc Name combo
        # box (see bug #364407).
        #
        if event.source.parent and \
           event.source.parent.getRole() == pyatspi.ROLE_COMBO_BOX:
            orca.setLocusOfFocus(None, event.source.parent, False)
            return

        default.Script.onStateChanged(self, event)


    # This method tries to detect and handle the following cases:
    # 1) Calc: spread sheet Name Box line.

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

        # self.printAncestry(event.source)

        # 1) Calc: spread sheet input line.
        #
        # If this "object:selection-changed" is for the spread sheet Name
        # Box, then check to see if the current locus of focus is a spread
        # sheet cell. If it is, and the contents of the input line are
        # different from what is displayed in that cell, then speak "has
        # formula" and append it to the braille line.
        #
        rolesList = [pyatspi.ROLE_LIST, \
                     pyatspi.ROLE_COMBO_BOX, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_TOOL_BAR, \
                     pyatspi.ROLE_PANEL, \
                     pyatspi.ROLE_ROOT_PANE, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(event.source, rolesList):
            if orca_state.locusOfFocus.getRole() == pyatspi.ROLE_TABLE_CELL:
                cell = orca_state.locusOfFocus

                # We are getting two "object:selection-changed" events
                # for each spread sheet cell move, so in order to prevent
                # appending "has formula" twice, we only do it if the last
                # cell is different from this one.
                #
                if cell != self.lastCell:
                    self.lastCell = cell

                    try:
                        if cell.queryText():
                            cellText = self.getText(cell, 0, -1)
                            if cellText and len(cellText):
                                try:
                                    if self.inputLineForCell and \
                                       self.inputLineForCell.queryText():
                                        inputLine = self.getText( \
                                                 self.inputLineForCell, 0, -1)
                                        if inputLine and (len(inputLine) > 1) \
                                            and (inputLine[0] == "="):
                                            # Translators: this means a 
                                            # particular cell in a spreadsheet
                                            # has a formula
                                            # (e.g., "=sum(a1:d1)")
                                            #
                                            hf = " " + _("has formula")
                                            speech.speak(hf, None, False)

                                            line = braille.getShowingLine()
                                            line.addRegion(braille.Region(hf))
                                            braille.refresh()
                                            #
                                            # Fall-thru to process the event
                                            # with the default handler.
                                except NotImplementedError:
                                    pass
                    except NotImplementedError:
                        pass

        default.Script.onSelectionChanged(self, event)

    def getText(self, obj, startOffset, endOffset):
        """Returns the substring of the given object's text specialization.

        NOTE: This is here to handle the problematic implementation of
        getText by OpenOffice.  See the bug discussion at:

           http://bugzilla.gnome.org/show_bug.cgi?id=356425)

        Once the OpenOffice issue has been resolved, this method probably
        should be removed.

        Arguments:
        - obj: an accessible supporting the accessible text specialization
        - startOffset: the starting character position
        - endOffset: the ending character position
        """

        text = obj.queryText().getText(0, -1).decode("UTF-8")
        if startOffset >= len(text):
            startOffset = len(text) - 1
        if endOffset == -1:
            endOffset = len(text)
        elif startOffset >= endOffset:
            endOffset = startOffset + 1
        string = text[max(0, startOffset):min(len(text), endOffset)]
        string = string.encode("UTF-8")
        return string

    def speakCellName(self, name):
        """Speaks the given cell name.

        Arguments:
        - name: the name of the cell
        """

        # Translators: this is the name of a cell in a spreadsheet.
        #
        line = _("Cell %s") % name
        speech.speak(line)

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        if orca_state.lastNonModifierKeyEvent:
            event_string = orca_state.lastNonModifierKeyEvent.event_string
            isShiftKey = orca_state.lastNonModifierKeyEvent.modifiers \
                         & (1 << pyatspi.MODIFIER_SHIFT)
        else:
            event_string = ''
            isShiftKey = False

        # If we are FOCUSED on a paragraph inside a table cell (in Writer),
        # then just return (modulo the special cases below). Speaking and
        # brailling will have been done in the onStateChanged() routine
        # (see bug #382415).
        #
        if event.source.getRole() == pyatspi.ROLE_PARAGRAPH and \
           event.source.parent.getRole() == pyatspi.ROLE_TABLE_CELL and \
           event.source.getState().contains(pyatspi.STATE_FOCUSED):

            # If we are moving up and down, and we are speaking-by-cell
            # (as opposed to by-row), then speak the cell name. Otherwise
            # just return.
            #
            if (event_string == "Up" or event_string == "Down"):
                if not settings.readTableCellRow:
                    if event.detail1 != -1:
                        self.speakCellName(event.source.parent.name)
                return

            # If we are moving left or right and we are in a new cell, just
            # return.
            #
            if (event_string == "Left" or event_string == "Right") and \
               self.lastCell != event.source.parent:
                return

            caretOffset = event.source.queryText().caretOffset
            charLen = event.source.queryText().characterCount

            # If you are in a table cell and you arrow Right, the caret
            # will focus at the end of the current paragraph before moving
            # into the next cell. To be similar to the way that caret
            # navigation works in other paragraphs in OOo, just return.
            #
            if event_string == "Right" and caretOffset == charLen:
                return

            # If we have moved left and the caret position is at the end of
            # the paragraph or if we have moved right and the caret position
            # is at the start of the text string, or the last key input was
            # Tab or Shift-Tab, and if we are speaking-by-cell (as opposed
            # to by-row), then speak the cell name, otherwise just return
            # (see bug #382418).
            #
            if (event_string == "Left" and caretOffset == charLen) or \
               (event_string == "Right" and caretOffset == 0) or \
               (event_string == "Tab" or event_string == "ISO_Left_Tab"):
                if not settings.readTableCellRow:
                    if event.detail1 != -1:
                        self.speakCellName(event.source.parent.name)

                # Speak a blank line, if appropriate.
                if self.speakBlankLine(event.source):
                    # Translators: "blank" is a short word to mean the
                    # user has navigated to an empty line.
                    #
                    speech.speak(_("blank"), None, False)
                return

        # Remove possible extra utterances of the current paragraph by
        # stopping any pending speech. See bug #435201 for more details.
        #
        if (event_string == "Up" or event_string == "Down") and not isShiftKey:
            speech.stop()

        # Speak a newline, if appropriate.
        if self.speakNewLine(event.source):
            speech.speak(chnames.getCharacterName("\n"), None, False)

        # Speak a blank line, if appropriate.
        if self.speakBlankLine(event.source):
            # Translators: "blank" is a short word to mean the
            # user has navigated to an empty line.
            #
            speech.speak(_("blank"), None, False)

        default.Script.onCaretMoved(self, event)


    def speakNewLine(self, obj):
        """Returns True if a newline should be spoken.
           Otherwise, returns False.
        """

        # Get the the AccessibleText interface.
        try:
            text = obj.queryText()
        except NotImplementedError:
            return False

        # Was a left or right-arrow key pressed?
        if not (orca_state.lastInputEvent and \
                orca_state.lastInputEvent.__dict__.has_key("event_string")):
            return False

        lastKey = orca_state.lastNonModifierKeyEvent.event_string
        if lastKey != "Left" and lastKey != "Right":
            return False

        # Was a control key pressed?
        mods = orca_state.lastInputEvent.modifiers
        isControlKey = mods & (1 << pyatspi.MODIFIER_CONTROL)

        # Get the line containing the caret
        caretOffset = text.caretOffset
        line = text.getTextAtOffset(caretOffset, \
            pyatspi.TEXT_BOUNDARY_LINE_START)
        lineStart = line[1]
        lineEnd = line[2]

        if isControlKey:  # control-right-arrow or control-left-arrow

            # Get the word containing the caret.
            word = text.getTextAtOffset(caretOffset, \
                pyatspi.TEXT_BOUNDARY_WORD_START)
            wordStart = word[1]
            wordEnd = word[2]

            if lastKey == "Right":
                if wordStart == lineStart:
                    return True
            else:
                if wordEnd == lineEnd:
                    return True

        else:  # right arrow or left arrow

            if lastKey == "Right":
                if caretOffset == lineStart:
                    return True
            else:
                if caretOffset == lineEnd:
                    return True

        return False


    def speakBlankLine(self, obj):
        """Returns True if a blank line should be spoken.
        Otherwise, returns False.
        """

        # Get the the AccessibleText interface.
        try:
            text = obj.queryText()
        except NotImplementedError:
            return False

        # Get the line containing the caret
        caretOffset = text.caretOffset
        line = text.getTextAtOffset(caretOffset, \
            pyatspi.TEXT_BOUNDARY_LINE_START)

        # If this is a blank line, announce it if the user requested
        # that blank lines be spoken.
        if line[1] == 0 and line[2] == 0:
            return settings.speakBlankLines

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.  Overridden here
        to handle the case when the inserted text was pasted via middle mouse
        click.

        Arguments:
        - event: the Event
        """

        # Because event.source is the paragraph where the text was inserted
        # and locusOfFocus is the selected text, the default onTextInserted
        # will return without speaking the text that was pasted.
        #
        text = event.any_data
        if isinstance(orca_state.lastInputEvent,
                        input_event.MouseButtonEvent) and \
             orca_state.lastInputEvent.button == "2":
            if text.isupper():
                speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(text)
        else:
            default.Script.onTextInserted(self, event)
