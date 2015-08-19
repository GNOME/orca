# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010-2013 The Orca Team.
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

"""Custom script for LibreOffice."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2013 The Orca Team."
__license__   = "LGPL"

from gi.repository import Gtk
import pyatspi

import orca.cmdnames as cmdnames
import orca.debug as debug
import orca.scripts.default as default
import orca.guilabels as guilabels
import orca.keybindings as keybindings
import orca.input_event as input_event
import orca.messages as messages
import orca.orca as orca
import orca.orca_state as orca_state
import orca.speech as speech
import orca.settings as settings
import orca.settings_manager as settings_manager

from .braille_generator import BrailleGenerator
from .formatting import Formatting
from .script_utilities import Utilities
from .spellcheck import SpellCheck
from .speech_generator import SpeechGenerator
from .structural_navigation import StructuralNavigation

_settingsManager = settings_manager.getManager()

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

        self.speakSpreadsheetCoordinatesCheckButton = None
        self.skipBlankCellsCheckButton = None
        self.speakCellCoordinatesCheckButton = None
        self.speakCellHeadersCheckButton = None
        self.speakCellSpanCheckButton = None

        # The spreadsheet input line.
        #
        self.inputLineForCell = None

        # Dictionaries for the calc and writer dynamic row and column headers.
        #
        self.dynamicColumnHeaders = {}
        self.dynamicRowHeaders = {}

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """
        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def getSpellCheck(self):
        """Returns the spellcheck for this script."""

        return SpellCheck(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def getStructuralNavigation(self):
        """Returns the 'structural navigation' class for this script.
        """
        types = self.getEnabledStructuralNavigationTypes()
        return StructuralNavigation(self, types, enabled=False)

    def getEnabledStructuralNavigationTypes(self):
        """Returns a list of the structural navigation object types
        enabled in this script.
        """

        enabledTypes = [StructuralNavigation.TABLE_CELL]

        return enabledTypes

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. In this particular case,
        we just want to be able to add a handler to return the contents of
        the input line.
        """

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers.update(
            self.structuralNavigation.inputEventHandlers)

        self.inputEventHandlers["presentInputLineHandler"] = \
            input_event.InputEventHandler(
                Script.presentInputLine,
                cmdnames.PRESENT_INPUT_LINE)

        self.inputEventHandlers["setDynamicColumnHeadersHandler"] = \
            input_event.InputEventHandler(
                Script.setDynamicColumnHeaders,
                cmdnames.DYNAMIC_COLUMN_HEADER_SET)

        self.inputEventHandlers["clearDynamicColumnHeadersHandler"] = \
            input_event.InputEventHandler(
                Script.clearDynamicColumnHeaders,
                cmdnames.DYNAMIC_COLUMN_HEADER_CLEAR)

        self.inputEventHandlers["setDynamicRowHeadersHandler"] = \
            input_event.InputEventHandler(
                Script.setDynamicRowHeaders,
                cmdnames.DYNAMIC_ROW_HEADER_SET)

        self.inputEventHandlers["clearDynamicRowHeadersHandler"] = \
            input_event.InputEventHandler(
                Script.clearDynamicRowHeaders,
                cmdnames.DYNAMIC_ROW_HEADER_CLEAR)

        self.inputEventHandlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleLeft,
                cmdnames.PAN_BRAILLE_LEFT,
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleRight,
                cmdnames.PAN_BRAILLE_RIGHT,
                False) # Do not enable learn mode for this action

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["presentInputLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "r",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["setDynamicColumnHeadersHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "r",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["clearDynamicColumnHeadersHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "c",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["setDynamicRowHeadersHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "c",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["clearDynamicRowHeadersHandler"],
                2))

        bindings = self.structuralNavigation.keyBindings
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        return keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = Gtk.Grid()
        grid.set_border_width(12)

        label = guilabels.SPREADSHEET_SPEAK_CELL_COORDINATES
        value = _settingsManager.getSetting('speakSpreadsheetCoordinates')
        self.speakSpreadsheetCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakSpreadsheetCoordinatesCheckButton.set_active(value)
        grid.attach(self.speakSpreadsheetCoordinatesCheckButton, 0, 0, 1, 1)

        tableFrame = Gtk.Frame()
        grid.attach(tableFrame, 0, 1, 1, 1)

        label = Gtk.Label(label="<b>%s</b>" % guilabels.TABLE_NAVIGATION)
        label.set_use_markup(True)
        tableFrame.set_label_widget(label)

        tableAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        tableAlignment.set_padding(0, 0, 12, 0)
        tableFrame.add(tableAlignment)
        tableGrid = Gtk.Grid()
        tableAlignment.add(tableGrid)

        label = guilabels.TABLE_SPEAK_CELL_COORDINATES
        value = _settingsManager.getSetting('speakCellCoordinates')
        self.speakCellCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellCoordinatesCheckButton.set_active(value)
        tableGrid.attach(self.speakCellCoordinatesCheckButton, 0, 0, 1, 1)

        label = guilabels.TABLE_SPEAK_CELL_SPANS
        value = _settingsManager.getSetting('speakCellSpan')
        self.speakCellSpanCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellSpanCheckButton.set_active(value)
        tableGrid.attach(self.speakCellSpanCheckButton, 0, 1, 1, 1)

        label = guilabels.TABLE_ANNOUNCE_CELL_HEADER
        value = _settingsManager.getSetting('speakCellHeaders')
        self.speakCellHeadersCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellHeadersCheckButton.set_active(value)
        tableGrid.attach(self.speakCellHeadersCheckButton, 0, 2, 1, 1)

        label = guilabels.TABLE_SKIP_BLANK_CELLS
        value = _settingsManager.getSetting('skipBlankCells')
        self.skipBlankCellsCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.skipBlankCellsCheckButton.set_active(value)
        tableGrid.attach(self.skipBlankCellsCheckButton, 0, 3, 1, 1)

        spellcheck = self.spellcheck.getAppPreferencesGUI()
        grid.attach(spellcheck, 0, len(grid.get_children()), 1, 1)
        grid.show_all()

        return grid

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        prefs = {
            'speakCellSpan': self.speakCellSpanCheckButton.get_active(),
            'speakCellHeaders': self.speakCellHeadersCheckButton.get_active(),
            'skipBlankCells': self.skipBlankCellsCheckButton.get_active(),
            'speakCellCoordinates': self.speakCellCoordinatesCheckButton.get_active(),
            'speakSpreadsheetCoordinates': self.speakSpreadsheetCoordinatesCheckButton.get_active(),
        }

        prefs.update(self.spellcheck.getPreferencesFromGUI())
        return prefs

    def isStructuralNavigationCommand(self, inputEvent=None):
        """Checks to see if the inputEvent was a structural navigation
        command. This is necessary to prevent double-presentation of
        items. [[[TODO - JD: Perhaps this should be moved to default.py]]]

        Arguments:
        - inputEvent: The input event to examine. If none is provided,
          orca_state.lastInputEvent will be used.

        Returns True if inputEvent is a structural navigation command
        enabled in this script.
        """

        inputEvent = inputEvent or orca_state.lastInputEvent
        if isinstance(inputEvent, input_event.KeyboardEvent):
            if self.structuralNavigation.keyBindings.\
                    getInputHandler(inputEvent):
                return True

        return False

    def doWhereAmI(self, inputEvent, basicOnly):
        """Performs the whereAmI operation."""

        if self.spellcheck.isActive():
            self.spellcheck.presentErrorDetails(not basicOnly)

        super().doWhereAmI(inputEvent, basicOnly)

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """

        if self.flatReviewContext \
           or not self.isBrailleBeginningShowing() \
           or self.utilities.isSpreadSheetCell(orca_state.locusOfFocus) \
           or not self.utilities.isTextArea(orca_state.locusOfFocus):
            return default.Script.panBrailleLeft(self, inputEvent, panAmount)

        text = orca_state.locusOfFocus.queryText()
        string, startOffset, endOffset = text.getTextAtOffset(
            text.caretOffset, pyatspi.TEXT_BOUNDARY_LINE_START)
        if 0 < startOffset:
            text.setCaretOffset(startOffset-1)
            return True

        obj = self.utilities.findPreviousObject(orca_state.locusOfFocus)
        try:
            text = obj.queryText()
        except:
            pass
        else:
            orca.setLocusOfFocus(None, obj, notifyScript=False)
            text.setCaretOffset(text.characterCount)
            return True

        return default.Script.panBrailleLeft(self, inputEvent, panAmount)

    def panBrailleRight(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """

        if self.flatReviewContext \
           or not self.isBrailleEndShowing() \
           or self.utilities.isSpreadSheetCell(orca_state.locusOfFocus) \
           or not self.utilities.isTextArea(orca_state.locusOfFocus):
            return default.Script.panBrailleRight(self, inputEvent, panAmount)

        text = orca_state.locusOfFocus.queryText()
        string, startOffset, endOffset = text.getTextAtOffset(
            text.caretOffset, pyatspi.TEXT_BOUNDARY_LINE_START)
        if endOffset < text.characterCount:
            text.setCaretOffset(endOffset)
            return True

        obj = self.utilities.findNextObject(orca_state.locusOfFocus)
        try:
            text = obj.queryText()
        except:
            pass
        else:
            orca.setLocusOfFocus(None, obj, notifyScript=False)
            text.setCaretOffset(0)
            return True

        return default.Script.panBrailleRight(self, inputEvent, panAmount)

    def presentInputLine(self, inputEvent):
        """Presents the contents of the spread sheet input line (assuming we
        have a handle to it - generated when we first focus on a spread
        sheet table cell.

        This will be either the contents of the table cell that has focus
        or the formula associated with it.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        if not self.utilities.isSpreadSheetCell(orca_state.locusOfFocus):
            return

        inputLine = self.utilities.locateInputLine(orca_state.locusOfFocus)
        if not inputLine:
            return

        text = self.utilities.displayedText(inputLine)
        if not text:
            text = messages.EMPTY

        self.presentMessage(text)

    def setDynamicColumnHeaders(self, inputEvent):
        """Set the row for the dynamic header columns to use when speaking
        calc cell entries. In order to set the row, the user should first set
        focus to the row that they wish to define and then press Insert-r.

        Once the user has defined the row, it will be used to first speak
        this header when moving between columns.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        cell = orca_state.locusOfFocus
        if cell and cell.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            cell = cell.parent

        row, column, table = self.utilities.getRowColumnAndTable(cell)
        if table:
            self.dynamicColumnHeaders[hash(table)] = row
            self.presentMessage(messages.DYNAMIC_COLUMN_HEADER_SET % (row+1))

        return True

    def clearDynamicColumnHeaders(self, inputEvent):
        """Clear the dynamic header column.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        cell = orca_state.locusOfFocus
        if cell and cell.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            cell = cell.parent

        row, column, table = self.utilities.getRowColumnAndTable(cell)
        try:
            del self.dynamicColumnHeaders[hash(table)]
            speech.stop()
            self.presentMessage(messages.DYNAMIC_COLUMN_HEADER_CLEARED)
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

        cell = orca_state.locusOfFocus
        if cell and cell.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            cell = cell.parent

        row, column, table = self.utilities.getRowColumnAndTable(cell)
        if table:
            self.dynamicRowHeaders[hash(table)] = column
            self.presentMessage(
                messages.DYNAMIC_ROW_HEADER_SET % self.columnConvert(column+1))

        return True

    def clearDynamicRowHeaders(self, inputEvent):
        """Clear the dynamic row headers.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        cell = orca_state.locusOfFocus
        if cell and cell.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            cell = cell.parent

        row, column, table = self.utilities.getRowColumnAndTable(cell)
        try:
            del self.dynamicRowHeaders[hash(table)]
            speech.stop()
            self.presentMessage(messages.DYNAMIC_ROW_HEADER_CLEARED)
        except:
            pass

        return True

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        # Check to see if this is this is for the find command. See
        # comment #18 of bug #354463.
        #
        if self.findCommandRun and \
           event.type.startswith("object:state-changed:focused"):
            self.findCommandRun = False
            self.find()
            return

        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        if self.spellcheck.isSuggestionsItem(newLocusOfFocus) \
           and not self.spellcheck.isSuggestionsItem(oldLocusOfFocus):
            self.updateBraille(newLocusOfFocus)
            self.spellcheck.presentSuggestionListItem(includeLabel=True)
            return

        # TODO - JD: Sad hack that wouldn't be needed if LO were fixed.
        # If we are in the slide presentation scroll pane, also announce
        # the current page tab. See bug #538056 for more details.
        #
        rolesList = [pyatspi.ROLE_SCROLL_PANE,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_ROOT_PANE,
                     pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_APPLICATION]
        if self.utilities.hasMatchingHierarchy(newLocusOfFocus, rolesList):
            for child in newLocusOfFocus.parent:
                if child.getRole() == pyatspi.ROLE_PAGE_TAB_LIST:
                    for tab in child:
                        eventState = tab.getState()
                        if eventState.contains(pyatspi.STATE_SELECTED):
                            utterances = \
                                self.speechGenerator.generateSpeech(tab)
                            speech.speak(utterances)

        # TODO - JD: This is a hack that needs to be done better. For now it
        # fixes the broken echo previous word on Return.
        elif newLocusOfFocus and oldLocusOfFocus \
           and newLocusOfFocus.getRole() == pyatspi.ROLE_PARAGRAPH \
           and oldLocusOfFocus.getRole() == pyatspi.ROLE_PARAGRAPH \
           and newLocusOfFocus != oldLocusOfFocus:
            lastKey, mods = self.utilities.lastKeyAndModifiers()
            if lastKey == "Return" and _settingsManager.getSetting('enableEchoByWord'):
                self.echoPreviousWord(oldLocusOfFocus)
                return

            # TODO - JD: And this hack is another one that needs to be done better.
            # But this will get us to speak the entire paragraph when navigation by
            # paragraph has occurred.
            event_string, mods = self.utilities.lastKeyAndModifiers()
            isControlKey = mods & keybindings.CTRL_MODIFIER_MASK
            isShiftKey = mods & keybindings.SHIFT_MODIFIER_MASK
            if event_string in ["Up", "Down"] and isControlKey and not isShiftKey:
                if self.utilities.displayedText(newLocusOfFocus):
                    speech.speak(self.utilities.displayedText(newLocusOfFocus))
                    self.updateBraille(newLocusOfFocus)
                    try:
                        text = newLocusOfFocus.queryText()
                    except:
                        pass
                    else:
                        self._saveLastCursorPosition(newLocusOfFocus, text.caretOffset)
                    return

        # Pass the event onto the parent class to be handled in the default way.
        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

        if self.utilities.isDocumentCell(newLocusOfFocus):
            row, column, table = \
                self.utilities.getRowColumnAndTable(newLocusOfFocus.parent)
            self.pointOfReference['lastRow'] = row
            self.pointOfReference['lastColumn'] = column

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        if self.spellcheck.isCheckWindow(event.source):
            return

        # Impress slide navigation.
        #
        if self.utilities.isInImpress(event.source) \
           and self.utilities.isDrawingView(event.source):
            title, position, count = \
                self.utilities.slideTitleAndPosition(event.source)
            if title:
                title += "."

            msg = messages.PRESENTATION_SLIDE_POSITION % \
                    {"position" : position, "count" : count}
            msg = self.utilities.appendString(title, msg)
            self.presentMessage(msg)

        default.Script.onNameChanged(self, event)

    def onActiveChanged(self, event):
        """Callback for object:state-changed:active accessibility events."""

        # Prevent this events from activating the find operation.
        # See comment #18 of bug #354463.
        if self.findCommandRun:
            return
 
        default.Script.onActiveChanged(self, event)

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        if self.utilities.isSameObject(event.any_data, orca_state.locusOfFocus):
            return

        if event.source == self.spellcheck.getSuggestionsList():
            if event.source.getState().contains(pyatspi.STATE_FOCUSED):
                orca.setLocusOfFocus(event, event.any_data, False)
                self.updateBraille(orca_state.locusOfFocus)
                self.spellcheck.presentSuggestionListItem()
            else:
                self.spellcheck.presentErrorDetails()
            return

        default.Script.onActiveDescendantChanged(self, event)

    def onChildrenChanged(self, event):
        """Called when a child node has changed.

        Arguments:
        - event: the Event
        """

        try:
            anyDataRole = event.any_data.getRole()
        except:
            return

        if anyDataRole == pyatspi.ROLE_TABLE:
            if self.utilities.isSpreadSheetCell(event.any_data, True):
                orca.setLocusOfFocus(event, event.any_data)
            return

        if anyDataRole == pyatspi.ROLE_TABLE_CELL:
            activeRow = self.pointOfReference.get('lastRow', -1)
            activeCol = self.pointOfReference.get('lastColumn', -1)
            if activeRow < 0 or activeCol < 0:
                return

            eventRow, eventCol, table = \
                self.utilities.getRowColumnAndTable(event.any_data)
            try:
                itable = table.queryTable()
            except NotImplementedError:
                return

            if eventRow == itable.nRows - 1 and eventCol == itable.nColumns - 1:
                fullMessage = briefMessage = ""
                voice = self.voices.get(settings.SYSTEM_VOICE)
                if activeRow == itable.nRows:
                    fullMessage = messages.TABLE_ROW_DELETED_FROM_END
                    briefMessage = messages.TABLE_ROW_DELETED
                else:
                    fullMessage =  messages.TABLE_ROW_INSERTED_AT_END
                    briefMessage = messages.TABLE_ROW_INSERTED
                if fullMessage:
                    self.presentMessage(fullMessage, briefMessage, voice)
                return

        default.Script.onChildrenChanged(self, event)

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # NOTE: This event type is deprecated and Orca should no longer use it.
        # This callback remains just to handle bugs in applications and toolkits
        # during the remainder of the unstable (3.11) development cycle.

        if self.utilities.isSameObject(orca_state.locusOfFocus, event.source):
            return

        role = event.source.getRole()

        # This seems to be something we inherit from Gtk+
        if role in [pyatspi.ROLE_TEXT, pyatspi.ROLE_PASSWORD_TEXT]:
            orca.setLocusOfFocus(event, event.source)
            return

        # Ditto.
        if role == pyatspi.ROLE_PUSH_BUTTON:
            orca.setLocusOfFocus(event, event.source)
            return

        # Ditto.
        if role == pyatspi.ROLE_COMBO_BOX:
            orca.setLocusOfFocus(event, event.source)
            return

        # Ditto.
        if role == pyatspi.ROLE_PANEL and event.source.name:
            orca.setLocusOfFocus(event, event.source)
            return

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if self._inSayAll:
            return

        if self.isStructuralNavigationCommand():
            return

        if not event.detail1:
            return

        if event.source.getRoleName() == 'text frame':
            return

        parent = event.source.parent
        if parent and parent.getRoleName() == 'text frame':
            return

        if parent and parent.getRole() == pyatspi.ROLE_TOOL_BAR:
            default.Script.onFocusedChanged(self, event)
            return

        role = event.source.getRole()
        ignoreRoles = [pyatspi.ROLE_FILLER, pyatspi.ROLE_PANEL]
        if role in ignoreRoles:
            return

        # We will present this when the selection changes.
        if role == pyatspi.ROLE_MENU:
            return

        if self.utilities._flowsFromOrToSelection(event.source):
            return

        if role == pyatspi.ROLE_PARAGRAPH:
            obj, offset = self.pointOfReference.get("lastCursorPosition", (None, -1))
            textSelections = self.pointOfReference.get('textSelections', {})
            start, end = textSelections.get(hash(obj), (0, 0))
            if start != end:
                return

            keyString, mods = self.utilities.lastKeyAndModifiers()
            if keyString in ["Left", "Right"]:
                orca.setLocusOfFocus(event, event.source, False)
                return

        # We should present this in response to active-descendant-changed events
        if event.source.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS):
            if role != pyatspi.ROLE_LIST:
                return

        default.Script.onFocusedChanged(self, event)

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        if self.isStructuralNavigationCommand():
            return

        if event.detail1 == -1:
            return

        if self.utilities.isCellBeingEdited(event.source):
            orca.setLocusOfFocus(event, event.source.parent, False)

        if not orca_state.locusOfFocus \
           or self.utilities.isZombie(orca_state.locusOfFocus):
            orca.setLocusOfFocus(event, event.source)
            default.Script.onCaretMoved(self, event)
            return

        if orca_state.locusOfFocus.getRole() == pyatspi.ROLE_TABLE_CELL:
            default.Script.onCaretMoved(self, event)
            return

        # The lists and combo boxes in the Formatting toolbar emit
        # object:active-descendant-changed events which cause us
        # to set the locusOfFocus to the list item. If the user then
        # arrows within the text portion, we will not present it due
        # to the event not being from the locusOfFocus. A similar
        # issue is present in the Target entry of the Hyperlink dialog
        # for OOo 3.2.
        #
        if event.source.getRole() == pyatspi.ROLE_TEXT \
           and self.utilities.ancestorWithRole(
               event.source,
               [pyatspi.ROLE_TOOL_BAR, pyatspi.ROLE_DIALOG],
               [pyatspi.ROLE_FRAME]):
            orca.setLocusOfFocus(event, event.source, False)

        if self.utilities._flowsFromOrToSelection(event.source):
            return

        default.Script.onCaretMoved(self, event)

    def onCheckedChanged(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        obj = event.source
        role = obj.getRole()
        parentRole = obj.parent.getRole()
        if not role in [pyatspi.ROLE_TOGGLE_BUTTON, pyatspi.ROLE_PUSH_BUTTON] \
           or not parentRole == pyatspi.ROLE_TOOL_BAR:
            default.Script.onCheckedChanged(self, event)
            return
 
        # Announce when the toolbar buttons are toggled if we just toggled
        # them; not if we navigated to some text.
        weToggledIt = False
        if isinstance(orca_state.lastInputEvent, input_event.MouseButtonEvent):
            x = orca_state.lastInputEvent.x
            y = orca_state.lastInputEvent.y
            weToggledIt = obj.queryComponent().contains(x, y, 0)
        elif obj.getState().contains(pyatspi.STATE_FOCUSED):
            weToggledIt = True
        else:
            keyString, mods = self.utilities.lastKeyAndModifiers()
            navKeys = ["Up", "Down", "Left", "Right", "Page_Up", "Page_Down",
                       "Home", "End", "N"]
            wasCommand = mods & keybindings.COMMAND_MODIFIER_MASK
            weToggledIt = wasCommand and keyString not in navKeys
        if weToggledIt:
            speech.speak(self.speechGenerator.generateSpeech(obj))

    def onRowReordered(self, event):
        """Callback for object:row-reordered accessibility events."""

        # We're seeing a crazy ton of these emitted bogusly.
        pass

    def getTextLineAtCaret(self, obj, offset=None, startOffset=None, endOffset=None):
        """To-be-removed. Returns the string, caretOffset, startOffset."""

        if obj.parent.getRole() == pyatspi.ROLE_COMBO_BOX:
            try:
                text = obj.queryText()
            except NotImplementedError:
                return ["", 0, 0]

            if text.caretOffset < 0:
                [lineString, startOffset, endOffset] = text.getTextAtOffset(
                    0, pyatspi.TEXT_BOUNDARY_LINE_START)

                # Sometimes we get the trailing line-feed -- remove it
                #
                if lineString[-1:] == "\n":
                    lineString = lineString[:-1]

                return [lineString, 0, startOffset]

        textLine = super().getTextLineAtCaret(obj, offset, startOffset, endOffset)
        if not obj.getState().contains(pyatspi.STATE_FOCUSED):
            textLine[0] = self.utilities.displayedText(obj)

        return textLine

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        super().onWindowActivated(event)
        if not self.spellcheck.isCheckWindow(event.source):
            return

        if event.source[0].getRole() == pyatspi.ROLE_DIALOG:
            orca.setLocusOfFocus(event, event.source[0], False)

        self.spellcheck.presentErrorDetails()

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        super().onWindowDeactivated(event)
        self.spellcheck.deactivate()
