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

import pyatspi

import orca.speechgenerator as speechgenerator
import orca.settings as settings

from orca.orca_i18n import _ # for gettext support

from constants import speakCellCoordinates

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
