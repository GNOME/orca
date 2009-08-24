# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

import gtk
import pyatspi

import orca.debug as debug
import orca.default as default
import orca.input_event as input_event
import orca.braille as braille
import orca.orca as orca
import orca.orca_state as orca_state
import orca.speech as speech
import orca.settings as settings
import orca.keybindings as keybindings

from orca.orca_i18n import _ # for gettext support

from speech_generator import SpeechGenerator
from braille_generator import BrailleGenerator
from formatting import Formatting
from structural_navigation import StructuralNavigation
import script_settings

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

        # Set the number of retries after a COMM_FAILURE to 1. The default
        # of 5 was not allowing Orca to be responsive in the event of OOo
        # going into crash recovery mode (see bug #397787).
        #
        self.commFailureAttemptLimit = 1

        # Additional default set of text attributes to present to the
        # user. The only difference over the default set in
        # settings.py is to add in "left-margin:" and "right-margin:".
        #
        self.additionalBrailledTextAttributes = \
          " left-margin:0mm; right-margin:0mm;"
        self.additionalSpokenTextAttributes = \
          " left-margin:0mm; right-margin:0mm;"

    def activate(self):
        """Called when this script is activated."""
        self.savedreadTableCellRow = settings.readTableCellRow
        settings.readTableCellRow = False

        self.savedEnabledBrailledTextAttributes = \
            settings.enabledBrailledTextAttributes
        settings.enabledBrailledTextAttributes += \
            self.additionalBrailledTextAttributes

        self.savedEnabledSpokenTextAttributes = \
            settings.enabledSpokenTextAttributes
        settings.enabledSpokenTextAttributes += \
            self.additionalSpokenTextAttributes

        # Account for the differences in how OOo expresses indent and
        # strikethrough.
        #
        settings.enabledBrailledTextAttributes = \
            settings.enabledBrailledTextAttributes.replace(
            "strikethrough:false;",
            "strikethrough:none;")
        settings.enabledSpokenTextAttributes = \
            settings.enabledSpokenTextAttributes.replace(
            "strikethrough:false;",
            "strikethrough:none;")

        settings.enabledBrailledTextAttributes = \
            settings.enabledBrailledTextAttributes.replace(
            "indent:0;",
            "indent:0mm;")
        settings.enabledSpokenTextAttributes = \
            settings.enabledSpokenTextAttributes.replace(
            "indent:0;",
            "indent:0mm;")

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

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

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
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["speakInputLineHandler"]))

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
        self.speakSpreadsheetCoordinatesCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakSpreadsheetCoordinatesCheckButton)
        gtk.Box.pack_start(vbox, self.speakSpreadsheetCoordinatesCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(\
            self.speakSpreadsheetCoordinatesCheckButton,
            script_settings.speakSpreadsheetCoordinates)

        # Table Navigation frame.
        #
        tableFrame = gtk.Frame()
        gtk.Widget.show(tableFrame)
        gtk.Box.pack_start(vbox, tableFrame, False, False, 5)

        tableAlignment = gtk.Alignment(0.5, 0.5, 1, 1)
        gtk.Widget.show(tableAlignment)
        gtk.Container.add(tableFrame, tableAlignment)
        gtk.Alignment.set_padding(tableAlignment, 0, 0, 12, 0)

        tableVBox = gtk.VBox(False, 0)
        gtk.Widget.show(tableVBox)
        gtk.Container.add(tableAlignment, tableVBox)

        # Translators: this is an option to tell Orca whether or not it
        # should speak table cell coordinates in document content.
        #
        label = _("Speak _cell coordinates")
        self.speakCellCoordinatesCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakCellCoordinatesCheckButton)
        gtk.Box.pack_start(tableVBox, self.speakCellCoordinatesCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakCellCoordinatesCheckButton,
                                    settings.speakCellCoordinates)

        # Translators: this is an option to tell Orca whether or not it
        # should speak the span size of a table cell (e.g., how many
        # rows and columns a particular table cell spans in a table).
        #
        label = _("Speak _multiple cell spans")
        self.speakCellSpanCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakCellSpanCheckButton)
        gtk.Box.pack_start(tableVBox, self.speakCellSpanCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakCellSpanCheckButton,
                                    settings.speakCellSpan)

        # Translators: this is an option for whether or not to speak
        # the header of a table cell in document content.
        #
        label = _("Announce cell _header")
        self.speakCellHeadersCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakCellHeadersCheckButton)
        gtk.Box.pack_start(tableVBox, self.speakCellHeadersCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.speakCellHeadersCheckButton,
                                    settings.speakCellHeaders)

        # Translators: this is an option to allow users to skip over
        # empty/blank cells when navigating tables in document content.
        #
        label = _("Skip _blank cells")
        self.skipBlankCellsCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.skipBlankCellsCheckButton)
        gtk.Box.pack_start(tableVBox, self.skipBlankCellsCheckButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.skipBlankCellsCheckButton,
                                    settings.skipBlankCells)

        # Translators: this is the title of a panel containing options
        # for specifying how to navigate tables in document content.
        #
        tableLabel = gtk.Label("<b>%s</b>" % _("Table Navigation"))
        gtk.Widget.show(tableLabel)
        gtk.Frame.set_label_widget(tableFrame, tableLabel)
        gtk.Label.set_use_markup(tableLabel, True)

        return vbox

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        prefs.writelines("\n")
        prefix = "orca.scripts.apps.soffice.script_settings"

        script_settings.speakSpreadsheetCoordinates = \
                 self.speakSpreadsheetCoordinatesCheckButton.get_active()
        prefs.writelines("%s.speakSpreadsheetCoordinates = %s\n" % \
                         (prefix, script_settings.speakSpreadsheetCoordinates))

        settings.speakCellCoordinates = \
                 self.speakCellCoordinatesCheckButton.get_active()
        prefs.writelines("orca.settings.speakCellCoordinates = %s\n" % \
                         settings.speakCellCoordinates)

        settings.speakCellSpan = self.speakCellSpanCheckButton.get_active()
        prefs.writelines("orca.settings.speakCellSpan = %s\n" % \
                         settings.speakCellSpan)

        settings.speakCellHeaders = \
                self.speakCellHeadersCheckButton.get_active()
        prefs.writelines("orca.settings.speakCellHeaders = %s\n" % \
                         settings.speakCellHeaders)

        settings.skipBlankCells = self.skipBlankCellsCheckButton.get_active()
        prefs.writelines("orca.settings.skipBlankCells = %s\n" % \
                         settings.skipBlankCells)

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

    def isReadOnlyTextArea(self, obj):
        """Returns True if obj is a text entry area that is read only."""
        state = obj.getState()
        readOnly = obj.getRole() == pyatspi.ROLE_TEXT \
                   and state.contains(pyatspi.STATE_FOCUSABLE) \
                   and not state.contains(pyatspi.STATE_EDITABLE)
        debug.println(debug.LEVEL_ALL,
                      "soffice.script.py:isReadOnlyTextArea=%s for %s" \
                      % (readOnly, debug.getAccessibleDetails(obj)))
        return readOnly

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
            index = self.getCellIndex(obj)
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
            index = self.getCellIndex(obj)
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
                index = self.getCellIndex(leftCell)
                startIndex = table.getColumnAtIndex(index)

            rightX = extents.x + extents.width - 1
            rightCell = \
                parent.queryComponent().getAccessibleAtPoint(rightX, y, 0)
            if rightCell:
                table = rightCell.parent.queryTable()
                index = self.getCellIndex(rightCell)
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
                top = self.getTopLevel(cell)
                return (top and top.name.endswith(" Calc"))
            else:
                return False
        else:
            return table.nRows == 65536

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

            if not isinstance(role, list):
                role = [role]

            if isinstance(role[0], str):
                current_role = current.getRoleName()
            else:
                current_role = current.getRole()

            if not current_role in role:
                return False

            current = self._getParent(current)

        return True

    def findFrameAndDialog(self, obj):
        """Returns the frame and (possibly) the dialog containing
        the object. Overridden here for presentation of the title
        bar information: If the locusOfFocus is a spreadsheet cell,
        1) we are not in a dialog and 2) we need to present both the
        frame name and the sheet name. So we might as well return the
        sheet in place of the dialog so that the default code can do
        its thing.
        """

        if not self.isSpreadSheetCell(obj):
            return default.Script.findFrameAndDialog(self, obj)

        results = [None, None]

        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent.getRole() == pyatspi.ROLE_FRAME:
                results[0] = parent
            if parent.getRole() == pyatspi.ROLE_TABLE:
                results[1] = parent
            parent = parent.parent

        return results

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

        oldAncestor = self.getAncestor(oldFocus,
                                       [pyatspi.ROLE_TABLE,
                                        pyatspi.ROLE_UNKNOWN,
                                        pyatspi.ROLE_DOCUMENT_FRAME],
                                       [pyatspi.ROLE_FRAME])
        newAncestor = self.getAncestor(newFocus,
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

        if not self.isSameObject(oldAncestor, newAncestor):
            if oldTable:
                # We've left a table.  Announce this fact.
                #
                speech.speak(_("leaving table."))
            if newTable:
                # We've entered a table.  Announce the dimensions.
                #
                line = _("table with %(rows)d rows and %(columns)d columns.") \
                       % {"rows" : newTable.nRows,
                          "columns" : newTable.nColumns}
                speech.speak(line)

        if not newTable:
            self.lastCell = [None, -1]
            return True

        cell = self.getAncestor(newFocus,
                                [pyatspi.ROLE_TABLE_CELL],
                                [pyatspi.ROLE_TABLE])
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

        if not settings.readTableCellRow:
            self.speakCellName(cell.name)

        try:
            text = newFocus.queryText()
        except:
            offset = -1
        else:
            offset = text.caretOffset

        self.lastCell = [cell, offset]
        index = self.getCellIndex(cell)
        column = newTable.getColumnAtIndex(index)
        self.pointOfReference['lastColumn'] = column
        row = newTable.getRowAtIndex(index)
        self.pointOfReference['lastRow'] = row

        return True

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
                index = self.getCellIndex(cell)
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
                index = self.getCellIndex(cell)
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

        Returns True if this is the spell check dialog (whether we actually
        wind up reading the word or not).
        """

        paragraph = self.findByRole(pane, pyatspi.ROLE_PARAGRAPH)

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

        badWord = self.getText(paragraph[0], startOff, endOff - 1)

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

        voices = settings.voices

        for i in range(startOffset, endOffset):
            if self.getLinkIndex(obj, i) >= 0:
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
            rolesList = [pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_SCROLL_PANE,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_OPTION_PANE,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(event.source, rolesList):
                tmp = event.source.parent.parent
                if tmp.name.startswith(panelName):
                    isPanel = True

            if not isPanel:
                rolesList = [pyatspi.ROLE_SCROLL_PANE,
                             pyatspi.ROLE_PANEL,
                             pyatspi.ROLE_OPTION_PANE,
                             pyatspi.ROLE_DIALOG,
                             pyatspi.ROLE_APPLICATION]
                if self.isDesiredFocusedItem(event.source, rolesList):
                    if event.source.parent.name.startswith(panelName):
                        isPanel = True

            if not isPanel:
                rolesList = [pyatspi.ROLE_PANEL,
                             pyatspi.ROLE_OPTION_PANE,
                             pyatspi.ROLE_DIALOG,
                             pyatspi.ROLE_APPLICATION]
                if self.isDesiredFocusedItem(event.source, rolesList):
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
            if settings.enableSpeechIndentation:
                self.speakTextIndentation(event.source,
                                          textToSpeak.encode("UTF-8"))
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

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

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
            if self.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                   "StarOffice.locusOfFocusChanged - Writer: text paragraph.")

                result = self.getTextLineAtCaret(event.source)
                textToSpeak = result[0].decode("UTF-8")
                self._speakWriterText(event, textToSpeak)
                braille.displayRegions(\
                    brailleGen.generateBraille(event.source))
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
            if self.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "License Agreement screen: Scroll Down button.")
                self.handleSetupPanel(event.source.parent)
                speech.speak(_("Note that the Scroll Down button has " \
                               "to be pressed numerous times."))

            # Check for 2. License Agreement: Accept button.
            #
            rolesList = [pyatspi.ROLE_UNKNOWN,
                         pyatspi.ROLE_SCROLL_PANE,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_OPTION_PANE,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "License Agreement screen: accept button.")
                speech.speak( \
                    _("License Agreement Accept button now has focus."))

            # Check for 3. Personal Data: Transfer Personal Data check box.
            #
            rolesList = [pyatspi.ROLE_CHECK_BOX,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_OPTION_PANE,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(event.source, rolesList):
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
            rolesList = [pyatspi.ROLE_RADIO_BUTTON,
                         pyatspi.ROLE_PANEL,
                         pyatspi.ROLE_OPTION_PANE,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(event.source, rolesList):
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
        if self.isDesiredFocusedItem(event.source, rolesList):
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

        if self.isDesiredFocusedItem(event.source, rolesList) \
            and (not event.source.name or len(event.source.name) == 0):
            debug.println(self.debugLevel, "StarOffice.locusOfFocusChanged - " \
                          + "Calc: name box.")

            self.updateBraille(newLocusOfFocus)

            # Translators: this is our made up name for the nameless field
            # in StarOffice/OpenOffice calc that allows you to type in a
            # cell coordinate (e.g., A4) and then move to it.
            #
            speech.speak(_("Move to cell"))
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
                    index = self.getCellIndex(newLocusOfFocus)
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

        if self.isDesiredFocusedItem(event.source, rolesList):
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
        if self.isDesiredFocusedItem(event.source, rolesList):
            default.Script.locusOfFocusChanged(self, event,
                                    oldLocusOfFocus, newLocusOfFocus)
            for child in event.source:
                speech.speak(self.getText(child, 0, -1), None, False)
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
           and not self.isSameObject(newLocusOfFocus.parent,
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

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

        # self.printAncestry(event.source)

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

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

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
        if self.isDesiredFocusedItem(event.source, rolesList) \
           and self.isSameObject(event.source.parent, orca_state.activeWindow):
            self.readMisspeltWord(event, event.source)

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
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel, "StarOffice.onFocus - " \
                          + "Calc: Name combo box.")
            orca.setLocusOfFocus(event, event.source)
            return

        # OOo Writer gets rather enthusiastic with focus: events for lists.
        # See bug 546941.
        #
        if event.source.getRole() == pyatspi.ROLE_LIST \
           and orca_state.locusOfFocus \
           and self.isSameObject(orca_state.locusOfFocus.parent, event.source):
            return

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
            if self.isDesiredFocusedItem(event.source, rolesList) \
               and event.any_data:
                handleEvent = True

            # The style list in the Formatting toolbar also lacks state
            # focused.
            #
            elif event.any_data and self.getAncestor(event.source,
                                                     [pyatspi.ROLE_TOOL_BAR],
                                                     [pyatspi.ROLE_FRAME]):
                handleEvent = True

        elif self.isSameObject(orca_state.locusOfFocus, event.source.parent) \
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
           and self.isSameObject(orca_state.locusOfFocus, event.any_data):
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
                event, event.any_data, notifyPresentationManager=presentEvent)

            # We'll tuck away the activeDescendant information for future
            # reference since the AT-SPI gives us little help in finding
            # this.
            #
            self.pointOfReference['activeDescendantInfo'] = \
                [orca_state.locusOfFocus.parent,
                 orca_state.locusOfFocus.getIndexInParent()]
            return

        default.Script.onActiveDescendantChanged(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

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

            elif isinstance(orca_state.lastInputEvent, \
                            input_event.KeyboardEvent):
                keyString = orca_state.lastNonModifierKeyEvent.event_string
                navKeys = ["Up", "Down", "Page_Up", "Page_Down", "Home", "End"]
                wasCommand = orca_state.lastInputEvent.modifiers \
                             & settings.COMMAND_MODIFIER_MASK
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
            if self.isDesiredFocusedItem(event.source, rolesList):
                orca.setLocusOfFocus(
                    event, event.source, notifyPresentationManager=False)
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
                    None, event.source.parent, notifyPresentationManager=False)
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

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

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
        if self.isDesiredFocusedItem(event.source, rolesList):
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

        # If we've used structural navigation commands to get here, the
        # presentation will be handled by the StructuralNavigation class.
        # The subsequent event will result in redundant presentation.
        #
        if self.isStructuralNavigationCommand():
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
            if settings.enableEchoByWord and \
               (self.isDesiredFocusedItem(event.source, rolesList) or
                self.isDesiredFocusedItem(event.source, rolesList1)):
                if isinstance(orca_state.lastInputEvent,
                              input_event.KeyboardEvent):
                    keyString = orca_state.lastNonModifierKeyEvent.event_string
                    focusRole = orca_state.locusOfFocus.getRole()
                    if focusRole != pyatspi.ROLE_UNKNOWN and \
                       keyString == "Return":
                        result = self.getText(event.source, 0, -1)
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

        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent) \
           and orca_state.lastNonModifierKeyEvent:
            event_string = orca_state.lastNonModifierKeyEvent.event_string
            mods = orca_state.lastInputEvent.modifiers
        else:
            event_string = ''
            mods = 0
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

            result = self.getText(event.source, 0, -1)
            textToSpeak = result.decode("UTF-8")
            self._speakWriterText(event, textToSpeak)
            braille.displayRegions( \
                self.brailleGenerator.generateBraille(event.source))
        else:
            # The lists and combo boxes in the Formatting toolbar emit
            # object:active-descendant-changed events which cause us
            # to set the locusOfFocus to the list item. If the user then
            # arrows within the text portion, we will not present it due
            # to the event not being from the locusOfFocus.
            #
            if event.source.getRole() == pyatspi.ROLE_TEXT \
               and self.getAncestor(event.source,
                                    [pyatspi.ROLE_TOOL_BAR],
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
            if text.decode("UTF-8").isupper():
                speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(text)
        else:
            default.Script.onTextInserted(self, event)

    def getTextAttributes(self, acc, offset, get_defaults=False):
        """Get the text attributes run for a given offset in a given accessible

        Arguments:
        - acc: An accessible.
        - offset: Offset in the accessible's text for which to retrieve the
        attributes.
        - get_defaults: Get the default attributes as well as the unique ones.
        Default is True

        Returns a dictionary of attributes, a start offset where the attributes
        begin, and an end offset. Returns ({}, 0, 0) if the accessible does not
        supprt the text attribute.
        """
        rv, start, end = \
            default.Script.getTextAttributes(self, acc, offset, get_defaults)

        # If there are no text attributes associated with the text at a
        # given offset, we might get some seriously bogus offsets, in
        # particular, an extremely large start offset and an extremely
        # large, but negative end offset. As a result, any text attributes
        # which are present on the line after the specified offset will
        # not be indicated by braille.py's getAttributeMask. Therefore,
        # we'll set the start offset to the character being examined,
        # and the end offset to the next character.
        #
        start = min(start, offset)
        if end < 0:
            debug.println(debug.LEVEL_WARNING,
                "soffice.script.py:getTextAttributes: detected a bogus " +
                "end offset. Start offset: %s, end offset: %s" % (start, end))
            end = offset + 1
        else:
            end -= 1

        return rv, start, end

    def getDisplayedText(self, obj):
        """Returns the text being displayed for an object. Overridden here
        because OpenOffice uses symbols (e.g. ">>" for buttons but exposes
        more useful information via the accessible's name.

        Arguments:
        - obj: the object

        Returns the text being displayed for an object or None if there isn't
        any text being shown.
        """

        if obj.getRole() == pyatspi.ROLE_PUSH_BUTTON and obj.name:
            return obj.name
        else:
            return default.Script.getDisplayedText(self, obj)

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

        return default.Script.getTextLineAtCaret(self, obj, offset)

    def isFunctionalDialog(self, obj):
        """Returns true if the window is functioning as a dialog."""

        # The OOo Navigator window looks like a dialog, acts like a
        # dialog, and loses focus requiring the user to know that it's
        # there and needs Alt+F6ing into.  But officially it's a normal
        # window.

        # There doesn't seem to be (an efficient) top-down equivalent
        # of isDesiredFocusedItem(). But OOo documents have root panes;
        # this thing does not.
        #
        rolesList = [pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_TOOL_BAR,
                     pyatspi.ROLE_PUSH_BUTTON]

        if obj.getRole() != rolesList[0]:
            # We might be looking at the child.
            #
            rolesList.pop(0)

        while obj and obj.childCount and len(rolesList):
            if obj.getRole() != rolesList.pop(0):
                return False
            obj = obj[0]

        return True
