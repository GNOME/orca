# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

# [[[TODO: JD - Pylint is giving us a number of errors along these
# lines throughout this file:
#
# E1103:690:Script.presentTableInfo: Instance of 'list' has no
# 'queryTable' member (but some types could not be inferred)
#
# In each case, we're not querying the table interface (or asking
# for the name) of a list, but rather of an accessible. Pylint is
# correct about it's suggestion that it cannot infer types.]]]
#
# pylint: disable-msg=E1103

"""Custom script for StarOffice and OpenOffice."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

from gi.repository import Gtk
import pyatspi

import orca.debug as debug
import orca.scripts.default as default
import orca.keybindings as keybindings
import orca.input_event as input_event
import orca.orca as orca
import orca.orca_state as orca_state
import orca.speech as speech
import orca.settings as settings
import orca.settings_manager as settings_manager
from orca.orca_i18n import _
from orca.orca_i18n import ngettext

from .speech_generator import SpeechGenerator
from .braille_generator import BrailleGenerator
from .formatting import Formatting
from .structural_navigation import StructuralNavigation
from .script_utilities import Utilities
from . import script_settings

_settingsManager = settings_manager.getManager()

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
        self.speakSpreadsheetCoordinatesCheckButton = None
        self.savedreadTableCellRow = None
        self.skipBlankCellsCheckButton = None
        self.speakCellCoordinatesCheckButton = None
        self.speakCellHeadersCheckButton = None
        self.speakCellSpanCheckButton = None

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # A handle to the last Writer table or Calc spread sheet cell
        # encountered and its caret offset.
        #
        self.lastCell = [None, -1]

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

    def activate(self):
        """Called when this script is activated."""
        self.savedreadTableCellRow = \
            _settingsManager.getSetting('readTableCellRow')
        _settingsManager.setSetting('readTableCellRow', False)

        self.savedEnabledBrailledTextAttributes = \
            _settingsManager.getSetting('enabledBrailledTextAttributes')

        self.savedEnabledSpokenTextAttributes = \
            _settingsManager.getSetting('enabledSpokenTextAttributes')

        # Account for the differences in how OOo expresses indent, 
        # strikethrough, and margins.
        #
        attributes = _settingsManager.getSetting('allTextAttributes')
        attributes.replace("margin:;", "margin:0mm;")
        _settingsManager.setSetting('allTextAttributes', attributes)

        attributes = \
            _settingsManager.getSetting('enabledBrailledTextAttributes')
        attributes.replace("strikethrough:false;", "strikethrough:none;")
        attributes.replace("indent:0;", "indent:0mm;")
        _settingsManager.setSetting('enabledBrailledTextAttributes', attributes)

        attributes = _settingsManager.getSetting('enabledSpokenTextAttributes')
        attributes.replace("strikethrough:false;", "strikethrough:none;")
        attributes.replace("indent:0;", "indent:0mm;")
        _settingsManager.setSetting('enabledSpokenTextAttributes', attributes)

        default.Script.activate(self)

    def deactivate(self):
        """Called when this script is deactivated."""
        _settingsManager.setSetting('readTableCellRow',
                                    self.savedreadTableCellRow)
        _settingsManager.setSetting('enabledBrailledTextAttributes',
                                    self.savedEnabledBrailledTextAttributes)
        _settingsManager.setSetting('enabledSpokenTextAttributes',
                                    self.savedEnabledSpokenTextAttributes)

        default.Script.activate(self)

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
        listeners["object:children-changed"]                = \
            self.onChildrenChanged

        return listeners

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """
        return BrailleGenerator(self)

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
        self.inputEventHandlers.update(\
            self.structuralNavigation.inputEventHandlers)

        self.inputEventHandlers["presentInputLineHandler"] = \
            input_event.InputEventHandler(
                Script.presentInputLine,
                # Translators: this is the input line of a spreadsheet
                # (i.e., the place where enter formulas)
                #
                _("Presents the contents of the input line."))

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

        self.inputEventHandlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleLeft,
                # Translators: a refreshable braille display is an
                # external hardware device that presents braille
                # character to the user.  There are a limited number
                # of cells on the display (typically 40 cells).  Orca
                # provides the feature to build up a longer logical
                # line and allow the user to press buttons on the
                # braille display so they can pan left and right over
                # this line.
                #
                _("Pans the braille display to the left."),
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleRight,
                # Translators: a refreshable braille display is an
                # external hardware device that presents braille
                # character to the user.  There are a limited number
                # of cells on the display (typically 40 cells).  Orca
                # provides the feature to build up a longer logical
                # line and allow the user to press buttons on the
                # braille display so they can pan left and right over
                # this line.
                #
                _("Pans the braille display to the right."),
                False) # Do not enable learn mode for this action

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["presentInputLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "r",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["setDynamicColumnHeadersHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "r",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["clearDynamicColumnHeadersHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "c",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["setDynamicRowHeadersHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "c",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
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

        # Translators: If checked, then Orca will speak the coordinates
        # of the current spread sheet cell. Coordinates are the row and
        # column position within the spread sheet (i.e. A1, B1, C2 ...)
        #
        label = _("Speak spread sheet cell coordinates")
        value = script_settings.speakSpreadsheetCoordinates
        self.speakSpreadsheetCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakSpreadsheetCoordinatesCheckButton.set_active(value)
        grid.attach(self.speakSpreadsheetCoordinatesCheckButton, 0, 0, 1, 1)

        tableFrame = Gtk.Frame()
        grid.attach(tableFrame, 0, 1, 1, 1)

        # Translators: this is the title of a panel containing options
        # for specifying how to navigate tables in document content.
        #
        label = Gtk.Label(label="<b>%s</b>" % _("Table Navigation"))
        label.set_use_markup(True)
        tableFrame.set_label_widget(label)

        tableAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        tableAlignment.set_padding(0, 0, 12, 0)
        tableFrame.add(tableAlignment)
        tableGrid = Gtk.Grid()
        tableAlignment.add(tableGrid)

        # Translators: this is an option to tell Orca whether or not it
        # should speak table cell coordinates in document content.
        #
        label = _("Speak _cell coordinates")
        value = _settingsManager.getSetting('speakCellCoordinates')
        self.speakCellCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellCoordinatesCheckButton.set_active(value)
        tableGrid.attach(self.speakCellCoordinatesCheckButton, 0, 0, 1, 1)

        # Translators: this is an option to tell Orca whether or not it
        # should speak the span size of a table cell (e.g., how many
        # rows and columns a particular table cell spans in a table).
        #
        label = _("Speak _multiple cell spans")
        value = _settingsManager.getSetting('speakCellSpan')
        self.speakCellSpanCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellSpanCheckButton.set_active(value)
        tableGrid.attach(self.speakCellSpanCheckButton, 0, 1, 1, 1)

        # Translators: this is an option for whether or not to speak
        # the header of a table cell in document content.
        #
        label = _("Announce cell _header")
        value = _settingsManager.getSetting('speakCellHeaders')
        self.speakCellHeadersCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellHeadersCheckButton.set_active(value)
        tableGrid.attach(self.speakCellHeadersCheckButton, 0, 2, 1, 1)
           
        # Translators: this is an option to allow users to skip over
        # empty/blank cells when navigating tables in document content.
        #
        label = _("Skip _blank cells")
        value = _settingsManager.getSetting('skipBlankCells')
        self.skipBlankCellsCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.skipBlankCellsCheckButton.set_active(value)
        tableGrid.attach(self.skipBlankCellsCheckButton, 0, 3, 1, 1)

        grid.show_all()

        return grid

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        prefs.writelines("\n")
        prefix = "orca.scripts.apps.soffice.script_settings"
        prefs.writelines("import %s\n\n" % prefix)

        script_settings.speakSpreadsheetCoordinates = \
            self.speakSpreadsheetCoordinatesCheckButton.get_active()
        prefs.writelines("%s.speakSpreadsheetCoordinates = %s\n" % \
                        (prefix, script_settings.speakSpreadsheetCoordinates))

        value = self.speakCellCoordinatesCheckButton.get_active()
        _settingsManager.setSetting('speakCellCoordinates', value)            
        prefs.writelines("orca.settings.speakCellCoordinates = %s\n" % value)

        value = self.speakCellSpanCheckButton.get_active()
        _settingsManager.setSetting('speakCellSpan', value)
        prefs.writelines("orca.settings.speakCellSpan = %s\n" % value)

        value = self.speakCellHeadersCheckButton.get_active()
        _settingsManager.setSetting('speakCellHeaders', value)
        prefs.writelines("orca.settings.speakCellHeaders = %s\n" % value)

        value = self.skipBlankCellsCheckButton.get_active()
        _settingsManager.setSetting('skipBlankCells', value)
        prefs.writelines("orca.settings.skipBlankCells = %s\n" % value)

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

        table = None
        obj = self.adjustForWriterTable(obj)
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL and obj.parent:
            try:
                table = obj.parent.queryTable()
            except NotImplementedError:
                pass

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
            index = self.utilities.cellIndex(obj)
            row = parentTable.getRowAtIndex(index)
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
            index = self.utilities.cellIndex(obj)
            column = parentTable.getColumnAtIndex(index)
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
            allParagraphs = self.utilities.descendantsWithRole(
                panel, pyatspi.ROLE_PARAGRAPH)
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
                index = self.utilities.cellIndex(leftCell)
                startIndex = table.getColumnAtIndex(index)

            rightX = extents.x + extents.width - 1
            rightCell = \
                parent.queryComponent().getAccessibleAtPoint(rightX, y, 0)
            if rightCell:
                table = rightCell.parent.queryTable()
                index = self.utilities.cellIndex(rightCell)
                endIndex = table.getColumnAtIndex(index)

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

        cell = obj
        if not startFromTable:
            obj = obj.parent

        try:
            table = obj.queryTable()
        except:
            # There really doesn't seem to be a good way to identify
            # when the user is editing a cell because it has a role
            # of paragraph and no table in the ancestry. This hack is
            # a carry-over from the whereAmI code.
            #
            if cell.getRole() == pyatspi.ROLE_PARAGRAPH:
                top = self.utilities.topLevelObject(cell)
                return (top and top.name.endswith(" Calc"))
            else:
                return False
        else:
            return table.nRows in [65536, 1048576]

    def presentTableInfo(self, oldFocus, newFocus):
        """Presents information relevant to a table that was just entered
        (primarily) or exited.

        Arguments:
        - oldFocus: the first accessible to check (usually the previous
          locusOfFocus)
        - newFocus: the second accessible to check (usually the current
          locusOfFocus)

        Returns True if table info was presented.
        """

        oldAncestor = self.utilities.ancestorWithRole(
            oldFocus,
            [pyatspi.ROLE_TABLE,
             pyatspi.ROLE_UNKNOWN,
             pyatspi.ROLE_DOCUMENT_FRAME],
            [pyatspi.ROLE_FRAME])
        newAncestor = self.utilities.ancestorWithRole(
            newFocus,
            [pyatspi.ROLE_TABLE,
             pyatspi.ROLE_UNKNOWN,
             pyatspi.ROLE_DOCUMENT_FRAME],
            [pyatspi.ROLE_FRAME])

        if not (oldAncestor and newAncestor):
            # At least one of the objects not only is not in a table, but is
            # is not in a document either.
            #
            return False
        elif self.isSpreadSheetCell(oldAncestor, True) \
             or self.isSpreadSheetCell(newAncestor, True):
            # One or both objects is a table in a spreadsheet; we just want
            # to handle tables in documents (definitely Writer; maybe also
            # Impress).
            #
            return False

        try:
            oldTable = oldAncestor.queryTable()
        except:
            oldTable = None

        try:
            newTable = newAncestor.queryTable()
        except:
            newTable = None

        if oldTable == newTable == None:
            # We're in a document, but apparently have not entered or left
            # a table.
            #
            return False

        if not self.utilities.isSameObject(oldAncestor, newAncestor):
            if oldTable:
                # We've left a table.  Announce this fact.
                #
                self.presentMessage(_("leaving table."))
            if newTable:
                nRows = newTable.nRows
                nColumns = newTable.nColumns
                # Translators: this represents the number of rows in a table.
                #
                rowString = ngettext("table with %d row",
                                     "table with %d rows",
                                     nRows) % nRows
                # Translators: this represents the number of columns in a table.
                #
                colString = ngettext("%d column",
                                     "%d columns",
                                     nColumns) % nColumns

                line = rowString + " " + colString
                self.presentMessage(line)

        if not newTable:
            self.lastCell = [None, -1]
            return True

        cell = self.utilities.ancestorWithRole(
            newFocus, [pyatspi.ROLE_TABLE_CELL], [pyatspi.ROLE_TABLE])
        if not cell or self.lastCell[0] == cell:
            # If we haven't found a cell, who knows what's going on? If
            # the cell is the same as our last location, odds are that
            # there are multiple paragraphs in this cell and a focus:
            # and/or object:state-changed:focused event was emitted.
            # If we haven't changed cells, we'll just treat this as any
            # other paragraph and let the caret-moved events do their
            # thing.
            #
            return (cell != None)

        self.updateBraille(cell)
        speech.speak(self.speechGenerator.generateSpeech(cell))

        if not _settingsManager.getSetting('readTableCellRow'):
            self.speakCellName(cell.name)

        try:
            text = newFocus.queryText()
        except:
            offset = -1
        else:
            offset = text.caretOffset

        self.lastCell = [cell, offset]
        index = self.utilities.cellIndex(cell)
        column = newTable.getColumnAtIndex(index)
        self.pointOfReference['lastColumn'] = column
        row = newTable.getRowAtIndex(index)
        self.pointOfReference['lastRow'] = row

        return True

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """

        if self.flatReviewContext \
           or not self.isBrailleBeginningShowing() \
           or self.isSpreadSheetCell(orca_state.locusOfFocus):
            return default.Script.panBrailleLeft(self, inputEvent, panAmount)

        obj = self.utilities.findPreviousObject(orca_state.locusOfFocus)
        orca.setLocusOfFocus(None, obj, notifyScript=False)
        self.updateBraille(obj)

        # Hack: When panning to the left in a document, we want to start at
        # the right/bottom of each new object. For now, we'll pan there.
        # When time permits, we'll give our braille code some smarts.
        while self.panBrailleInDirection(panToLeft=False):
            pass
        self.refreshBraille(False)

        return True

    def panBrailleRight(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """

        if self.flatReviewContext \
           or not self.isBrailleEndShowing() \
           or self.isSpreadSheetCell(orca_state.locusOfFocus):
            return default.Script.panBrailleRight(self, inputEvent, panAmount)

        obj = self.utilities.findNextObject(orca_state.locusOfFocus)
        orca.setLocusOfFocus(None, obj, notifyScript=False)
        self.updateBraille(obj)

        # Hack: When panning to the right in a document, we want to start at
        # the left/top of each new object. For now, we'll pan there. When time
        # permits, we'll give our braille code some smarts.
        while self.panBrailleInDirection(panToLeft=True):
            pass
        self.refreshBraille(False)

        return True

    def presentInputLine(self, inputEvent):
        """Presents the contents of the spread sheet input line (assuming we
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
                    inputLine = \
                        self.utilities.substring(self.inputLineForCell, 0, -1)
                    if not inputLine:
                        # Translators: this is used to announce that the
                        # current input line in a spreadsheet is blank/empty.
                        #
                        inputLine = _("empty")
                    debug.println(self.debugLevel,
                        "StarOffice.speakInputLine: contents: %s" % inputLine)
                    self.displayBrailleMessage(inputLine, \
                      flashTime=_settingsManager.getSetting('brailleFlashTime'))
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
                index = self.utilities.cellIndex(cell)
                row = parentTable.getRowAtIndex(index)

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
                index = self.utilities.cellIndex(cell)
                column = parentTable.getColumnAtIndex(index)

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
            self.presentMessage(line)

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
                self.presentMessage(line)
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
            self.presentMessage(line)

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
                self.presentMessage(line)
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

        Returns True if this is the spell check dialog (whether we actually
        wind up reading the word or not).
        """

        paragraph = self.utilities.descendantsWithRole(
            pane, pyatspi.ROLE_PARAGRAPH)

        # If there is not exactly one paragraph, this isn't the spellcheck
        # dialog.
        #
        if len(paragraph) != 1:
            return False

        # If there's not any text displayed in the paragraph, this isn't
        # the spellcheck dialog.
        #
        try:
            text = paragraph[0].queryText()
        except:
            return False
        else:
            textLength = text.characterCount
            if not textLength:
                return False

        # If the text here is not editable, this isn't the spellcheck
        # dialog.
        #
        if not paragraph[0].getState().contains(pyatspi.STATE_EDITABLE):
            return False

        # Determine which word is the misspelt word. This word will have
        # non-default text attributes associated with it.
        #
        startFound = False
        startOff = 0
        endOff = textLength
        for i in range(0, textLength):
            attributes = text.getAttributes(i)
            if len(attributes[0]) != 0:
                if not startFound:
                    startOff = i
                    startFound = True
            else:
                if startFound:
                    endOff = i
                    break

        if not startFound:
            # If there are no text attributes in this paragraph, this isn't
            # the spellcheck dialog.
            #
            return False

        badWord = self.utilities.substring(paragraph[0], startOff, endOff - 1)

        # Note that we often get two or more of these focus or property-change
        # events each time there is a new misspelt word. We extract the
        # length of the line of text, the misspelt word, the start and end
        # offsets for that word and compare them against the values saved
        # from the last time this routine was called. If they are the same
        # then we ignore it.
        #
        debug.println(self.debugLevel, \
            "StarOffice.readMisspeltWord: type=%s  word=%s(%d,%d)  len=%d" % \
            (event.type, badWord, startOff, endOff, textLength))

        if (textLength == self.lastTextLength) and \
           (badWord == self.lastBadWord) and \
           (startOff == self.lastStartOff) and \
           (endOff == self.lastEndOff):
            return True

        # Create a list of all the words found in the misspelt paragraph.
        #
        text = self.utilities.substring(paragraph[0], 0, -1)
        allTokens = text.split()
        self.speakMisspeltWord(allTokens, badWord)

        # Save misspelt word information for comparison purposes next
        # time around.
        #
        self.lastTextLength = textLength
        self.lastBadWord = badWord
        self.lastStartOff = startOff
        self.lastEndOff = endOff

        return True

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

        voices = _settingsManager.getSetting('voices')

        for i in range(startOffset, endOffset):
            if self.utilities.linkIndex(obj, i) >= 0:
                voice = voices[settings.HYPERLINK_VOICE]
                break
            elif word.decode("UTF-8").isupper():
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

        text = self.utilities.displayedText(label)
        if text:
            speech.speak(text)

    def handleSetupPanel(self, panel):
        """Find all the labels in this Setup panel and speak them.

        Arguments:
        - panel: the Setup panel.
        """

        allLabels = self.utilities.descendantsWithRole(
            panel, pyatspi.ROLE_LABEL)
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
            rolesList = [pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_SCROLL_PANE,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_OPTION_PANE,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]
            if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                tmp = event.source.parent.parent
                if tmp.name.startswith(panelName):
                    isPanel = True

            if not isPanel:
                rolesList = [pyatspi.ROLE_SCROLL_PANE,
                             pyatspi.ROLE_PANEL,
                             pyatspi.ROLE_OPTION_PANE,
                             pyatspi.ROLE_DIALOG,
                             pyatspi.ROLE_APPLICATION]
                if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                    if event.source.parent.name.startswith(panelName):
                        isPanel = True

            if not isPanel:
                rolesList = [pyatspi.ROLE_PANEL,
                             pyatspi.ROLE_OPTION_PANE,
                             pyatspi.ROLE_DIALOG,
                             pyatspi.ROLE_APPLICATION]
                if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                    if event.source.name.startswith(panelName):
                        isPanel = True

        return isPanel

    def _speakWriterText(self, event, textToSpeak):
        """Called to speak the current line or paragraph of Writer text.

        Arguments:
        - event: the Event
        - textToSpeak: the text to speak
        """

        if not textToSpeak and event and self.speakBlankLine(event.source):
            # Translators: "blank" is a short word to mean the
            # user has navigated to an empty line.
            #
            speech.speak(_("blank"), None, False)

        # Check to see if there are any hypertext links in this paragraph.
        # If no, then just speak the whole line. Otherwise, split the text
        # to speak into words and call sayWriterWord() to speak that token
        # in the appropriate voice.
        #
        try:
            hypertext = event.source.queryHypertext()
        except NotImplementedError:
            hypertext = None

        if not hypertext or (hypertext.getNLinks() == 0):
            result = self.speechGenerator.generateTextIndentation( \
              event.source, line=textToSpeak.encode("UTF-8"))
            if result:
                speech.speak(result[0])

            speech.speak(textToSpeak.encode("UTF-8"), None, False)
        else:
            started = False
            startOffset = 0
            for i in range(0, len(textToSpeak)):
                if textToSpeak[i] == ' ':
                    if started:
                        endOffset = i
                        self.sayWriterWord(event.source,
                            textToSpeak[startOffset:endOffset+1].encode( \
                                                                "UTF-8"),
                            startOffset, endOffset)
                        startOffset = i
                        started = False
                else:
                    if not started:
                        startOffset = i
                        started = True

            if started:
                endOffset = len(textToSpeak)
                self.sayWriterWord(event.source,
                    textToSpeak[startOffset:endOffset].encode("UTF-8"),
                    startOffset, endOffset)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        brailleGen = self.brailleGenerator
        details = debug.getAccessibleDetails(self.debugLevel, event.source)
        debug.printObjectEvent(self.debugLevel, event, details)

        # self.printAncestry(event.source)

        # Check to see if this is this is for the find command. See
        # comment #18 of bug #354463.
        #
        if self.findCommandRun and \
           event.type.startswith("object:state-changed:focused"):
            self.findCommandRun = False
            self.find()
            return

        # We always automatically go back to focus tracking mode when
        # the focus changes.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        # If we are inside a paragraph inside a table cell (in Writer),
        # then speak/braille that parent table cell (see bug #382415).
        # Also announce that a table has been entered or left.
        #
        if event.source.getRole() == pyatspi.ROLE_PARAGRAPH:
            if self.presentTableInfo(oldLocusOfFocus, newLocusOfFocus):
                return

            rolesList = [pyatspi.ROLE_PARAGRAPH,
                         [pyatspi.ROLE_UNKNOWN, pyatspi.ROLE_DOCUMENT_FRAME],
                         pyatspi.ROLE_SCROLL_PANE,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_ROOT_PANE,
                         pyatspi.ROLE_FRAME]
            if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                debug.println(self.debugLevel,
                   "StarOffice.locusOfFocusChanged - Writer: text paragraph.")

                result = self.getTextLineAtCaret(event.source)
                textToSpeak = result[0].decode("UTF-8")
                self._speakWriterText(event, textToSpeak)
                self.displayBrailleForObject(event.source)
                return

        # Check to see if the object that just got focus is in the Setup
        # dialog. If it is, then check for a variety of scenerios.
        #
        if self.isSetupDialog(event.source):

            # Check for 1. License Agreement: Scroll Down button.
            #
            rolesList = [pyatspi.ROLE_PUSH_BUTTON,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_OPTION_PANE,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]
            if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "License Agreement screen: Scroll Down button.")
                self.handleSetupPanel(event.source.parent)
                self.presentMessage(_("Note that the Scroll Down button has " \
                                      "to be pressed numerous times."))

            # Check for 2. License Agreement: Accept button.
            #
            rolesList = [pyatspi.ROLE_UNKNOWN,
                         pyatspi.ROLE_SCROLL_PANE,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_OPTION_PANE,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]
            if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "License Agreement screen: accept button.")
                self.presentMessage(
                    _("License Agreement Accept button now has focus."))

            # Check for 3. Personal Data: Transfer Personal Data check box.
            #
            rolesList = [pyatspi.ROLE_CHECK_BOX,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_OPTION_PANE,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]
            if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "Personal Data: Transfer Personal Data check box.")
                self.handleSetupPanel(event.source.parent)

            # Check for 4. User name: First Name text field.
            #
            rolesList = [pyatspi.ROLE_TEXT,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_OPTION_PANE,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]
            # Translators: this is the name of the field in the StarOffice
            # setup dialog that is asking for the first name of the user.
            # The translated form has to match what StarOffice/OpenOffice
            # is using.  We hate keying off stuff like this, but we're
            # forced to in this case.
            #
            if self.utilities.hasMatchingHierarchy(event.source, rolesList) \
               and event.source.name == _("First name"):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "User name: First Name text field.")

                # Just speak the informative labels at the top of the panel
                # (and not the ones that have LABEL_FOR relationships).
                #
                panel = event.source.parent
                allLabels = self.utilities.descendantsWithRole(
                    panel, pyatspi.ROLE_LABEL)
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
            rolesList = [pyatspi.ROLE_RADIO_BUTTON,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_OPTION_PANE,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]
            if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "Registration: Register Now radio button.")
                self.handleSetupPanel(event.source.parent)

        # Check to see if we are editing a spread sheet cell. If so, just
        # return to avoid uttering something like "Paragraph 0 paragraph".
        #
        rolesList = [pyatspi.ROLE_PARAGRAPH,
                     [pyatspi.ROLE_PANEL, pyatspi.ROLE_EXTENDED],
                     [pyatspi.ROLE_UNKNOWN, pyatspi.ROLE_DOCUMENT_FRAME],
                     pyatspi.ROLE_SCROLL_PANE,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_ROOT_PANE,
                     pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_APPLICATION]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            debug.println(self.debugLevel, "StarOffice.locusOfFocusChanged - " \
                          + "Calc: cell editor.")
            return

        # Check to see if the focus has just moved to the Name Box combo
        # box in Calc. If so, then replace the non-existent name with a
        # simple one before falling through and calling the default
        # locusOfFocusChanged method, which in turn will result in our
        # _generateSpeechForComboBox() method being called.
        #
        rolesList = [pyatspi.ROLE_LIST,
                     pyatspi.ROLE_COMBO_BOX,
                     pyatspi.ROLE_TOOL_BAR,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_ROOT_PANE,
                     pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_APPLICATION]

        if self.utilities.hasMatchingHierarchy(event.source, rolesList) \
            and (not event.source.name or len(event.source.name) == 0):
            debug.println(self.debugLevel, "StarOffice.locusOfFocusChanged - " \
                          + "Calc: name box.")

            self.updateBraille(newLocusOfFocus)

            # Translators: this is our made up name for the nameless field
            # in StarOffice/OpenOffice calc that allows you to type in a
            # cell coordinate (e.g., A4) and then move to it.
            #
            self.presentMessage(_("Move to cell"))
            return

        # Check to see if this is a Calc: spread sheet cell. If it is then
        # we don't want to speak "not selected" after giving the cell
        # location and contents (which is what the default locusOfFocusChanged
        # method would now do).
        #
        if self.isSpreadSheetCell(event.source, True):
            if newLocusOfFocus:
                self.updateBraille(newLocusOfFocus)
                utterances = \
                    self.speechGenerator.generateSpeech(newLocusOfFocus)
                speech.speak(utterances)

                # Save the current row and column information in the table
                # cell's table, so that we can use it the next time.
                #
                try:
                    table = newLocusOfFocus.parent.queryTable()
                except:
                    pass
                else:
                    index = self.utilities.cellIndex(newLocusOfFocus)
                    column = table.getColumnAtIndex(index)
                    self.pointOfReference['lastColumn'] = column
                    row = table.getRowAtIndex(index)
                    self.pointOfReference['lastRow'] = row
                return

        # If we are in the slide presentation scroll pane, also announce
        # the current page tab. See bug #538056 for more details.
        #
        rolesList = [pyatspi.ROLE_SCROLL_PANE,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_ROOT_PANE,
                     pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_APPLICATION]

        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            debug.println(self.debugLevel, "soffice.locusOfFocusChanged - " \
                          + "Impress: scroll pane.")

            for child in event.source.parent:
                if child.getRole() == pyatspi.ROLE_PAGE_TAB_LIST:
                    for tab in child:
                        eventState = tab.getState()
                        if eventState.contains(pyatspi.STATE_SELECTED):
                            utterances = \
                                self.speechGenerator.generateSpeech(tab)
                            speech.speak(utterances)
            # Fall-thru to process the event with the default handler.

        # If we are focused on a place holder element in the slide
        # presentation scroll pane, first present the object, then
        # try to present each of its children. See bug #538064 for
        # more details.
        #
        rolesList = [[pyatspi.ROLE_UNKNOWN, pyatspi.ROLE_LIST_ITEM],
                     [pyatspi.ROLE_UNKNOWN, pyatspi.ROLE_DOCUMENT_FRAME],
                     pyatspi.ROLE_SCROLL_PANE,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_ROOT_PANE,
                     pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_APPLICATION]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            default.Script.locusOfFocusChanged(self, event,
                                    oldLocusOfFocus, newLocusOfFocus)
            for child in event.source:
                speech.speak(self.utilities.substring(child, 0, -1),
                             None, False)
            return

        # Combo boxes in OOo typically have two children: a text object
        # and a list. The combo box will often intially claim to have
        # focus, but not always. The list inside of it, however, will
        # claim focus quite regularly. In addition, the list will do
        # this even if the text object is editable and functionally has
        # focus, such as the File Name combo box in the Save As dialog.
        # We need to minimize chattiness and maximize useful information.
        #
        if newLocusOfFocus and oldLocusOfFocus \
           and newLocusOfFocus.getRole() == pyatspi.ROLE_LIST \
           and newLocusOfFocus.parent.getRole() == pyatspi.ROLE_COMBO_BOX \
           and not self.utilities.isSameObject(newLocusOfFocus.parent,
                                     oldLocusOfFocus.parent):

            # If the combo box contents cannot be edited, just present the
            # combo box. Otherwise, present the text object. The combo
            # box will be included as part of the speech context.
            #
            state = newLocusOfFocus.parent[0].getState()
            if not state.contains(pyatspi.STATE_EDITABLE):
                newLocusOfFocus = newLocusOfFocus.parent
            else:
                newLocusOfFocus = newLocusOfFocus.parent[0]

        # Pass the event onto the parent class to be handled in the default way.

        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

    def onWindowActivated(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        details = debug.getAccessibleDetails(self.debugLevel, event.source)
        debug.printObjectEvent(self.debugLevel, event, details)

        # self.printAncestry(event.source)

        # Check to see if the Setup dialog window has just been activated.
        # If it has, then find the panel within it that has no name and
        # speak all the labels within that panel.
        #
        if self.isSetupDialog(event.source):
            debug.println(self.debugLevel,
                "StarOffice.onWindowActivated - Setup dialog: Welcome screen.")

            allPanels = self.utilities.descendantsWithRole(
                event.source.parent, pyatspi.ROLE_PANEL)
            for panel in allPanels:
                if not panel.name:
                    allLabels = self.utilities.descendantsWithRole(
                        panel, pyatspi.ROLE_LABEL)
                    for label in allLabels:
                        self.speakSetupLabel(label)
        else:
            # Clear our stored misspelled word history.
            #
            self.lastTextLength = -1
            self.lastBadWord = ''
            self.lastStartOff = -1
            self.lastEndOff = -1

            # Let the default script do its thing.
            #
            default.Script.onWindowActivated(self, event)

            # Maybe it's the spellcheck dialog. Might as well try and see.
            # If it is, we want to speak the misspelled word and context
            # after we've spoken the window name.
            #
            if event.source.getRole() == pyatspi.ROLE_DIALOG \
               and event.source.childCount \
               and event.source[0].getRole() == pyatspi.ROLE_OPTION_PANE:
                self.readMisspeltWord(event, event.source)

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        details = debug.getAccessibleDetails(self.debugLevel, event.source)
        debug.printObjectEvent(self.debugLevel, event, details)

        # self.printAncestry(event.source)

        # Check to see if if we've had a property-change event for the
        # accessible name for the option pane in the spell check dialog.
        # This (hopefully) means that the user has just corrected a
        # spelling mistake, in which case, speak/braille the current
        # misspelt word plus its context.
        #
        rolesList = [pyatspi.ROLE_OPTION_PANE, \
                     pyatspi.ROLE_DIALOG, \
                     pyatspi.ROLE_APPLICATION]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList) \
           and self.utilities.isSameObject(
                event.source.parent, orca_state.activeWindow):
            self.readMisspeltWord(event, event.source)

        # Impress slide navigation.
        #
        if self.utilities.isInImpress(event.source) \
           and self.utilities.isDrawingView(event.source):
            title, position, count = \
                self.utilities.slideTitleAndPosition(event.source)
            if title:
                title += "."

            # Translators: this is an indication of the position of the
            # focused Impress slide and the total number of slides in the
            # presentation.
            #
            msg = _("slide %(position)d of %(count)d") % \
                    {"position" : position, "count" : count}
            msg = self.utilities.appendString(title, msg)
            self.presentMessage(msg)

        default.Script.onNameChanged(self, event)

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # If we've used structural navigation commands to get here, the
        # presentation will be handled by the StructuralNavigation class.
        # The subsequent event will result in redundant presentation.
        #
        if self.isStructuralNavigationCommand():
            return

        # If this is a "focus:" event for the Calc Name combo box, catch
        # it here to reduce verbosity (see bug #364407).
        #
        rolesList = [pyatspi.ROLE_LIST,
                     pyatspi.ROLE_COMBO_BOX,
                     pyatspi.ROLE_TOOL_BAR,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_ROOT_PANE,
                     pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_APPLICATION]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            debug.println(self.debugLevel, "StarOffice.onFocus - " \
                          + "Calc: Name combo box.")
            orca.setLocusOfFocus(event, event.source)
            return

        # OOo Writer gets rather enthusiastic with focus: events for lists.
        # See bug 546941.
        #
        if event.source.getRole() == pyatspi.ROLE_LIST \
           and orca_state.locusOfFocus \
           and self.utilities.isSameObject(
                orca_state.locusOfFocus.parent, event.source):
            return

        # Auto-inserted bullets and numbers are presented in braille, but not
        # spoken. So we'll speak them before sending this event off to the
        # default script.
        #
        if self.utilities.isAutoTextEvent(event):
            speech.speak(self.speechGenerator.generateSpeech(event.source))

        default.Script.onFocus(self, event)

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        handleEvent = False
        presentEvent = True
        if not event.source.getState().contains(pyatspi.STATE_FOCUSED):
            # Sometimes the items in the OOo Task Pane give up focus (e.g.
            # to a context menu) and never reclaim it. In this case, we
            # still get object:active-descendant-changed events, but the
            # event.source lacks STATE_FOCUSED. This causes the default
            # script to ignore the event. See bug #523416. [[[TODO - JD:
            # If the OOo guys fix this on their end, this hack should be
            # removed. The OOo issue can be found here:
            # http://www.openoffice.org/issues/show_bug.cgi?id=93083]]]
            #
            rolesList = [pyatspi.ROLE_LIST,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_LIST_ITEM]
            if self.utilities.hasMatchingHierarchy(event.source, rolesList) \
               and event.any_data:
                handleEvent = True

            # The style list in the Formatting toolbar also lacks state
            # focused.
            #
            elif event.any_data \
                 and self.utilities.ancestorWithRole(event.source,
                                                     [pyatspi.ROLE_TOOL_BAR],
                                                     [pyatspi.ROLE_FRAME]) \
                 and self.utilities.ancestorWithRole(orca_state.locusOfFocus,
                                                     [pyatspi.ROLE_TOOL_BAR],
                                                     [pyatspi.ROLE_FRAME]):
                handleEvent = True

        elif self.utilities.isSameObject(
                orca_state.locusOfFocus, event.source.parent) \
             and event.source.getRole() == pyatspi.ROLE_LIST \
             and orca_state.locusOfFocus.getRole() == pyatspi.ROLE_COMBO_BOX:
            # Combo boxes which have been explicitly given focus by the user
            # (as opposed to those which have been automatically given focus
            # in a dialog or alert) issue an object:state-changed:focused
            # event, then an object:active-descendant-changed event for the
            # list inside the combo box, and finally a focus: event for the
            # list itself. This leads to unnecessary chattiness. As these
            # objects look and act like combo boxes, we'll let the first of
            # the events cause the object to be presented. Quietly setting
            # the locusOfFocus to the activeDescendant here will prevent
            # this event's chattiness. The final focus: event for the list
            # is already being handled by onFocus as part of bug 546941.
            #
            handleEvent = True
            presentEvent = False

        if orca_state.locusOfFocus \
           and self.utilities.isSameObject(
            orca_state.locusOfFocus, event.any_data):
            # We're already on the new item. If we (or the default script)
            # presents it, the speech.stop() will cause us to interrupt the
            # presentation we're probably about to make due to an earlier
            # event.
            #
            handleEvent = True
            presentEvent = False

        if handleEvent:
            if presentEvent:
                speech.stop()
            orca.setLocusOfFocus(
                event, event.any_data, notifyScript=presentEvent)

            # We'll tuck away the activeDescendant information for future
            # reference since the AT-SPI gives us little help in finding
            # this.
            #
            self.pointOfReference['activeDescendantInfo'] = \
                [orca_state.locusOfFocus.parent,
                 orca_state.locusOfFocus.getIndexInParent()]
            return

        default.Script.onActiveDescendantChanged(self, event)

    def onChildrenChanged(self, event):
        """Called when a child node has changed.

        Arguments:
        - event: the Event
        """

        if not event.any_data or not orca_state.locusOfFocus:
            return

        if not event.type.startswith('object:children-changed:add'):
            return

        try:
            role = event.any_data.getRole()
        except:
            role = None
        if role == pyatspi.ROLE_TABLE:
            if self.isSpreadSheetCell(event.any_data, True):
                orca.setLocusOfFocus(event, event.any_data)
            return

        if role == pyatspi.ROLE_TABLE_CELL:
            activeRow = self.pointOfReference.get('lastRow', -1)
            activeCol = self.pointOfReference.get('lastColumn', -1)
            if activeRow < 0 or activeCol < 0:
                return

            try:
                itable = event.source.queryTable()
            except NotImplementedError:
                return

            index = self.utilities.cellIndex(event.any_data)
            eventRow = itable.getRowAtIndex(index)
            eventCol = itable.getColumnAtIndex(index)

            if eventRow == itable.nRows - 1 and eventCol == itable.nColumns - 1:
                fullMessage = briefMessage = ""
                voice = self.voices.get(settings.SYSTEM_VOICE)
                if activeRow == itable.nRows:
                    # Translators: This message is to inform the user that
                    # the last row of a table in a document was just deleted.
                    #
                    fullMessage = _("Last row deleted.")
                    # Translators: This message is to inform the user that
                    # a row in a table was just deleted.
                    #
                    briefMessage = _("Row deleted.")
                else:
                    # Translators: This message is to inform the user that a
                    # new table row was inserted at the end of the existing
                    # table. This typically happens when the user presses Tab
                    # from within the last cell of the table.
                    #
                    fullMessage = _("Row inserted at the end of the table.")
                    # Translators: This message is to inform the user that
                    # a row in a table was just inserted.
                    #
                    briefMessage = _("Row inserted.")
                if fullMessage:
                    self.presentMessage(fullMessage, briefMessage, voice)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        if event.source.getRole() == pyatspi.ROLE_EXTENDED:
            if event.source.getRoleName() == 'text frame':
                return

        parent = event.source.parent
        if parent and parent.getRole() == pyatspi.ROLE_EXTENDED:
            if parent.getRoleName() == 'text frame':
                return

        # If this is state change "focused" event and event.source isn't a
        # focused object, then just return. See bug #517502 for more details.
        #
        if event.type.startswith("object:state-changed:focused") \
           and (not event.source.getState().contains(pyatspi.STATE_FOCUSED) \
                or event.detail1 == 0):
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

            else:
                keyString, mods = self.utilities.lastKeyAndModifiers()
                navKeys = ["Up", "Down", "Left", "Right", "Page_Up",
                           "Page_Down", "Home", "End"]
                wasCommand = mods & settings.COMMAND_MODIFIER_MASK
                weToggledIt = wasCommand and keyString not in navKeys

            if weToggledIt:
                speech.speak(self.speechGenerator.generateSpeech(event.source))

        # When a new paragraph receives focus, we get a caret-moved event and
        # two focus events (the first being object:state-changed:focused).
        # The caret-moved event will cause us to present the text at the new
        # location, so it is safe to set the locusOfFocus silently here.
        # However, if we just created a new paragraph by pressing Return at
        # the end of the current paragraph, we will only get a caret-moved
        # event for the paragraph that just gave up focus (detail1 == -1).
        # In this case, we will keep displaying the previous line of text,
        # so we'll do an updateBraille() just in case.
        #
        if event.type.startswith("object:state-changed:focused"):
            rolesList = [pyatspi.ROLE_PARAGRAPH,
                         [pyatspi.ROLE_UNKNOWN, pyatspi.ROLE_DOCUMENT_FRAME],
                         pyatspi.ROLE_SCROLL_PANE,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_ROOT_PANE,
                         pyatspi.ROLE_FRAME]
            if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                orca.setLocusOfFocus(event, event.source, notifyScript=False)
                if event.source != self.currentParagraph:
                    self.updateBraille(event.source)
                return

            # If we get "object:state-changed:focused" events for children of
            # a combo-box, just set the focus to the combo box. This is needed
            # to help reduce the verbosity of focusing on the Calc Name combo
            # box (see bug #364407).
            #
            elif event.source.parent and \
                event.source.parent.getRole() == pyatspi.ROLE_COMBO_BOX:
                orca.setLocusOfFocus(
                    None, event.source.parent, notifyScript=False)
                return

        # If we are in the sbase Table Wizard, try to reduce the numerous
        # utterances of "Available fields panel". See bug #465087 for
        # more details.
        #
        if self.__isAvailableFieldsPanel(event):
            return

        default.Script.onStateChanged(self, event)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        details = debug.getAccessibleDetails(self.debugLevel, event.source)
        debug.printObjectEvent(self.debugLevel, event, details)

        # self.printAncestry(event.source)

        # If this "object:selection-changed" is for the spread sheet Name
        # Box, then check to see if the current locus of focus is a spread
        # sheet cell. If it is, and the contents of the input line are
        # different from what is displayed in that cell, then speak "has
        # formula" and append it to the braille line.
        #
        rolesList = [pyatspi.ROLE_LIST,
                     pyatspi.ROLE_COMBO_BOX,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_TOOL_BAR,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_ROOT_PANE,
                     pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_APPLICATION]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList) \
           and orca_state.locusOfFocus:
            if orca_state.locusOfFocus.getRole() == pyatspi.ROLE_TABLE_CELL:
                cell = orca_state.locusOfFocus

                # We are getting two "object:selection-changed" events
                # for each spread sheet cell move, so in order to prevent
                # appending "has formula" twice, we only do it if the last
                # cell is different from this one.
                #
                if cell != self.lastCell[0]:
                    self.lastCell[0] = cell

                    try:
                        if cell.queryText():
                            cellText = self.utilities.substring(cell, 0, -1)
                            if cellText and len(cellText):
                                try:
                                    if self.inputLineForCell and \
                                       self.inputLineForCell.queryText():
                                        inputLine = self.utilities.substring( \
                                                 self.inputLineForCell, 0, -1)
                                        if inputLine and (len(inputLine) > 1) \
                                            and (inputLine[0] == "="):
                                            # Translators: this means a
                                            # particular cell in a spreadsheet
                                            # has a formula
                                            # (e.g., "=sum(a1:d1)")
                                            #
                                            hf = _("has formula")
                                            speech.speak(" %s" % hf,
                                                         None, False)
                                            self.presentItemsInBraille([hf])
                                            #
                                            # Fall-thru to process the event
                                            # with the default handler.
                                except NotImplementedError:
                                    pass
                    except NotImplementedError:
                        pass

        default.Script.onSelectionChanged(self, event)

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

        # If we've used structural navigation commands to get here, the
        # presentation will be handled by the StructuralNavigation class.
        # The subsequent event will result in redundant presentation.
        #
        if self.isStructuralNavigationCommand():
            return

        if self.utilities.isDuplicateEvent(event):
            return

        # If we are losing focus and we in:
        # 1/ a paragraph in an ooimpress slide presentation
        # 2/ a paragraph in an oowriter text document
        # and the last thing the user typed was a Return, and echo by word
        # is enabled, and the last focused object was not of role "unknown",
        # then echo the previous word that the user typed.
        # See bug #538053 and bug #538835 for more details.
        #
        if event.detail1 == -1:
            # ooimpress paragraph in a slide presentation.
            rolesList = [pyatspi.ROLE_PARAGRAPH,
                         [pyatspi.ROLE_UNKNOWN, pyatspi.ROLE_LIST_ITEM],
                         [pyatspi.ROLE_UNKNOWN, pyatspi.ROLE_DOCUMENT_FRAME],
                         pyatspi.ROLE_SCROLL_PANE,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_ROOT_PANE,
                         pyatspi.ROLE_FRAME,
                         pyatspi.ROLE_APPLICATION]

            # oowriter paragraph in a text document.
            rolesList1 = [pyatspi.ROLE_PARAGRAPH,
                          [pyatspi.ROLE_UNKNOWN, pyatspi.ROLE_DOCUMENT_FRAME],
                          pyatspi.ROLE_SCROLL_PANE,
                          pyatspi.ROLE_PANEL,
                          pyatspi.ROLE_ROOT_PANE,
                          pyatspi.ROLE_FRAME,
                          pyatspi.ROLE_APPLICATION]
            if _settingsManager.getSetting('enableEchoByWord') and \
               (self.utilities.hasMatchingHierarchy(event.source, rolesList) or
                self.utilities.hasMatchingHierarchy(event.source, rolesList1)):
                keyString, mods = self.utilities.lastKeyAndModifiers()
                focusRole = orca_state.locusOfFocus.getRole()
                if focusRole != pyatspi.ROLE_UNKNOWN and keyString == "Return":
                    result = self.utilities.substring(event.source, 0, -1)
                    line = result.decode("UTF-8")
                    self.echoPreviousWord(event.source, len(line))
                    return

        # Otherwise, if the object is losing focus, then just ignore this event.
        #
        if event.detail1 == -1:
            return

        if self.lastCell[0] == event.source.parent:
            if self.lastCell[1] == event.detail1:
                # We took care of this in a focus event (our position has not
                # changed within the cell)
                #
                return
            else:
                # We're in the same cell, but at a different position. Update
                # our stored location and then let the normal caret-moved
                # processing take place.
                #
                self.lastCell[1] = event.detail1

        event_string, mods = self.utilities.lastKeyAndModifiers()
        isControlKey = mods & settings.CTRL_MODIFIER_MASK
        isShiftKey = mods & settings.SHIFT_MODIFIER_MASK

        # If the last input event was a keyboard event of Control-Up or
        # Control-Down, we want to speak the whole paragraph rather than
        # just the current line. In addition, we need to filter out some
        # creative uses of the caret-moved event on the part of the OOo
        # guys.
        #
        if event_string in ["Up", "Down"] and isControlKey and not isShiftKey:
            # If we moved to the next paragraph, the event.source index should
            # be larger than the current paragraph's index. If we moved to the
            # previous paragraph it should be smaller. Otherwise, it's bogus.
            #
            eventIndex = event.source.getIndexInParent()
            if self.currentParagraph:
                paraIndex = self.currentParagraph.getIndexInParent()
            else:
                paraIndex = eventIndex

            if (event_string == "Down" and (eventIndex - paraIndex <= 0)) \
               or (event_string == "Up" and (eventIndex - paraIndex >= 0)):
                return

            result = self.utilities.substring(event.source, 0, -1)
            textToSpeak = result.decode("UTF-8")
            self._speakWriterText(event, textToSpeak)
            self.displayBrailleForObject(event.source)
        else:
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
            default.Script.onCaretMoved(self, event)

        # If we're still here, we must be convinced that this paragraph
        # coincides with our actual location.
        #
        self.currentParagraph = event.source

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
            return _settingsManager.getSetting('speakBlankLines')

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
            if text.decode("UTF-8").isupper():
                speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(text)
        else:
            default.Script.onTextInserted(self, event)

    def getTextLineAtCaret(self, obj, offset=None):
        """Gets the line of text where the caret is. Overridden here to
        handle combo boxes who have a text object with a caret offset
        of -1 as a child.

        Argument:
        - obj: an Accessible object that implements the AccessibleText
          interface
        - offset: an optional caret offset to use. (Not used here at the
          moment, but needed in the Gecko script)

        Returns the [string, caretOffset, startOffset] for the line of text
        where the caret is.
        """

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
                content = lineString.decode("UTF-8")
                if content[-1:] == "\n":
                    content = content[:-1]

                return [content.encode("UTF-8"), 0, startOffset]

        textLine = default.Script.getTextLineAtCaret(self, obj, offset)
        if not obj.getState().contains(pyatspi.STATE_FOCUSED):
            textLine[0] = self.utilities.displayedText(obj)

        return textLine

