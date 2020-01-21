# Orca
#
# Copyright 2010 Joanmarie Diggs.
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

"""Commonly-required utility methods needed by -- and potentially
   customized by -- application and toolkit scripts. They have
   been pulled out from the scripts because certain scripts had
   gotten way too large as a result of including these methods."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.keybindings as keybindings
import orca.messages as messages
import orca.orca_state as orca_state
import orca.script_utilities as script_utilities

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        script_utilities.Utilities.__init__(self, script)

        self._calcSelectedCells = []
        self._calcSelectedRows = []
        self._calcSelectedColumns = []

    #########################################################################
    #                                                                       #
    # Utilities for finding, identifying, and comparing accessibles         #
    #                                                                       #
    #########################################################################

    def displayedText(self, obj):
        """Returns the text being displayed for an object. Overridden here
        because OpenOffice uses symbols (e.g. ">>" for buttons but exposes
        more useful information via the accessible's name.

        Arguments:
        - obj: the object

        Returns the text being displayed for an object or None if there isn't
        any text being shown.
        """

        try:
            role = obj.getRole()
        except:
            return ""

        if role == pyatspi.ROLE_PUSH_BUTTON and obj.name:
            return obj.name

        if role == pyatspi.ROLE_TABLE_CELL:
            strings = list(map(self.displayedText, [child for child in obj]))
            text = "\n".join(strings)
            if text.strip():
                return text

        try:
            text = super().displayedText(obj)
        except:
            return ""

        # TODO - JD: This is needed because the default behavior is to fall
        # back on the name, which is bogus. Once that has been fixed, this
        # hack can go.
        if role == pyatspi.ROLE_TABLE_CELL and text == obj.name \
           and (self.isSpreadSheetCell(obj) or self.isTextDocumentCell(obj)):
            return ""

        # More bogusness from (at least) Calc combined with the aforementioned
        # fallback-to-name behavior....
        if self.isDocument(obj) and text == obj.name and obj.name.startswith("file:///"):
            return ""

        return text

    def isCellBeingEdited(self, obj):
        if not obj:
            return False

        parent = obj.parent
        try:
            role = parent.getRole()
        except:
            msg = "SOFFICE: Exception getting role of %s" % parent
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role in [pyatspi.ROLE_EXTENDED, pyatspi.ROLE_PANEL]:
            return self.spreadSheetCellName(parent)

        return False

    def spreadSheetCellName(self, cell):
        nameList = cell.name.split()
        for name in nameList:
            name = name.replace('.', '')
            if not name.isalpha() and name.isalnum():
                return name

        return ''

    def getRowColumnAndTable(self, cell):
        """Returns the (row, column, table) tuple for cell."""

        if not (cell and cell.getRole() == pyatspi.ROLE_TABLE_CELL):
            return -1, -1, None

        cellParent = cell.parent
        if cellParent and cellParent.getRole() == pyatspi.ROLE_TABLE_CELL:
            cell = cellParent
            cellParent = cell.parent

        table = cellParent
        if table and table.getRole() != pyatspi.ROLE_TABLE:
            table = table.parent

        try:
            iTable = table.queryTable()
        except:
            return -1, -1, None

        index = self.cellIndex(cell)
        row = iTable.getRowAtIndex(index)
        column = iTable.getColumnAtIndex(index)

        return row, column, table

    def rowHeadersForCell(self, obj):
        rowHeader, colHeader = self.getDynamicHeadersForCell(obj)
        if rowHeader:
            return [rowHeader]

        return super().rowHeadersForCell(obj)

    def columnHeadersForCell(self, obj):
        rowHeader, colHeader = self.getDynamicHeadersForCell(obj)
        if colHeader:
            return [colHeader]

        return super().columnHeadersForCell(obj)

    def getDynamicHeadersForCell(self, obj, onlyIfNew=False):
        if not (self._script.dynamicRowHeaders or self._script.dynamicColumnHeaders):
            return None, None

        objRow, objCol, table = self.getRowColumnAndTable(obj)
        if not table:
            return None, None

        headersRow = self._script.dynamicColumnHeaders.get(hash(table))
        headersCol = self._script.dynamicRowHeaders.get(hash(table))
        if headersRow == objRow or headersCol == objCol:
            return None, None

        getRowHeader = headersCol is not None
        getColHeader = headersRow is not None
        if onlyIfNew:
            getRowHeader = \
                getRowHeader and objRow != self._script.pointOfReference.get("lastRow")
            getColHeader = \
                getColHeader and objCol!= self._script.pointOfReference.get("lastColumn")

        parentTable = table.queryTable()
        rowHeader, colHeader = None, None
        if getColHeader:
            colHeader = parentTable.getAccessibleAt(headersRow, objCol)

        if getRowHeader:
            rowHeader = parentTable.getAccessibleAt(objRow, headersCol)

        return rowHeader, colHeader

    def isSameObject(self, obj1, obj2, comparePaths=False, ignoreNames=False):
        if obj1 == obj2:
            return True

        try:
            role1 = obj1.getRole()
            role2 = obj2.getRole()
        except:
            return False

        if role1 != role2 or role1 == pyatspi.ROLE_PARAGRAPH:
            return False

        try:
            name1 = obj1.name
            name2 = obj2.name
        except:
            return False

        if name1 == name2:
            if role1 == pyatspi.ROLE_FRAME:
                return True
            if role1 == pyatspi.ROLE_TABLE_CELL and not name1:
                if self.isZombie(obj1) and self.isZombie(obj2):
                    return False

        return super().isSameObject(obj1, obj2, comparePaths, ignoreNames)

    def isLayoutOnly(self, obj):
        """Returns True if the given object is a container which has
        no presentable information (label, name, displayed text, etc.)."""

        try:
            role = obj.getRole()
            childCount = obj.childCount
            name = obj.name
        except:
            msg = "SOFFICE: Exception getting properties of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if role == pyatspi.ROLE_PANEL and childCount == 1 and name:
            try:
                child = obj[0]
            except:
                msg = "SOFFICE: Exception getting child of %s" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                if child and child.name == name:
                    return True

        if role == pyatspi.ROLE_LIST:
            try:
                parentRole = obj.parent.getRole()
            except:
                msg = "SOFFICE: Exception getting parent role of %s" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                if parentRole == pyatspi.ROLE_COMBO_BOX:
                    return True

        if role == pyatspi.ROLE_FRAME and name:
            try:
                windowName = orca_state.activeWindow.name
            except:
                msg = "SOFFICE: Exception getting name of active window"
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                return name == windowName

        return super().isLayoutOnly(obj)

    def isAnInputLine(self, obj):
        if not obj:
            return False
        if obj == self.locateInputLine(obj):
            return True

        parent = obj.parent
        try:
            role = parent.getRole()
        except:
            msg = "SOFFICE: Exception getting role of %s" % parent
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role in [pyatspi.ROLE_EXTENDED, pyatspi.ROLE_PANEL]:
            if self.spreadSheetCellName(parent):
                return False

        parent = parent.parent
        try:
            role = parent.getRole()
        except:
            msg = "SOFFICE: Exception getting role of %s" % parent
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role == pyatspi.ROLE_TEXT:
            return True

        return False

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

        if self._script.inputLineForCell:
            try:
                topLevel = self.topLevelObject(self._script.inputLineForCell)
            except:
                msg = "ERROR: Exception getting topLevelObject for inputline"
                debug.println(debug.LEVEL_INFO, msg, True)
                self._script.inputLineForCell = None
            else:
                if self.isSameObject(orca_state.activeWindow, topLevel):
                    return self._script.inputLineForCell

        isScrollPane = lambda x: x and x.getRole() == pyatspi.ROLE_SCROLL_PANE
        scrollPane = pyatspi.findAncestor(obj, isScrollPane)
        if not scrollPane:
            return None

        toolbar = None
        for child in scrollPane.parent:
            if child and child.getRole() == pyatspi.ROLE_TOOL_BAR:
                toolbar = child
                break

        if not toolbar:
            msg = "ERROR: Calc inputline toolbar not found."
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        isParagraph = lambda x: x and x.getRole() == pyatspi.ROLE_PARAGRAPH
        allParagraphs = self.findAllDescendants(toolbar, isParagraph)
        if len(allParagraphs) == 1:
            self._script.inputLineForCell = allParagraphs[0]

        return self._script.inputLineForCell

    def frameAndDialog(self, obj):
        """Returns the frame and (possibly) the dialog containing
        the object. Overridden here for presentation of the title
        bar information: If the locusOfFocus is a spreadsheet cell,
        1) we are not in a dialog and 2) we need to present both the
        frame name and the sheet name. So we might as well return the
        sheet in place of the dialog so that the default code can do
        its thing.
        """

        if not self.isSpreadSheetCell(obj):
            return script_utilities.Utilities.frameAndDialog(self, obj)

        results = [None, None]

        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent.getRole() == pyatspi.ROLE_FRAME:
                results[0] = parent
            if parent.getRole() == pyatspi.ROLE_TABLE:
                results[1] = parent
            parent = parent.parent

        return results

    def validatedTopLevelObject(self, obj):
        # TODO - JD: We cannot just override topLevelObject() because that will
        # break flat review access to document content in LO using Gtk+ 3. That
        # bug seems to be fixed in LO v5.3.0. When that version is released, this
        # and hopefully other hacks can be removed.
        window = super().topLevelObject(obj)
        if not window or window.getIndexInParent() >= 0:
            return window

        msg = "SOFFICE: %s's window %s has -1 indexInParent" % (obj, window)
        debug.println(debug.LEVEL_INFO, msg, True)

        for child in self._script.app:
            if self.isSameObject(child, window):
                window = child
                break

        try:
            index = window.getIndexInParent()
        except:
            index = -1

        msg = "SOFFICE: Returning %s (index: %i)" % (window, index)
        debug.println(debug.LEVEL_INFO, msg, True)
        return window

    def commonAncestor(self, a, b):
        ancestor = super().commonAncestor(a, b)
        if ancestor or not (a and b):
            return ancestor

        windowA = self.validatedTopLevelObject(a)
        windowB = self.validatedTopLevelObject(b)
        if not self.isSameObject(windowA, windowB):
            return None

        msg = "SOFFICE: Adjusted ancestor %s and %s to %s" % (a, b, windowA)
        debug.println(debug.LEVEL_INFO, msg, True)
        return windowA

    def validParent(self, obj):
        """Returns the first valid parent/ancestor of obj. We need to do
        this in some applications and toolkits due to bogus hierarchies.

        See bugs:
        http://www.openoffice.org/issues/show_bug.cgi?id=78117
        http://bugzilla.gnome.org/show_bug.cgi?id=489490

        Arguments:
        - obj: the Accessible object
        """

        parent = obj.parent
        if parent and parent.getRole() in (pyatspi.ROLE_ROOT_PANE,
                                           pyatspi.ROLE_DIALOG):
            app = obj.getApplication()
            for frame in app:
                if frame.childCount < 1 \
                   or frame[0].getRole() not in (pyatspi.ROLE_ROOT_PANE,
                                                 pyatspi.ROLE_OPTION_PANE):
                    continue

                root_pane = frame[0]
                if obj in root_pane:
                    return root_pane

        return parent

    @staticmethod
    def _flowsFromOrToSelection(obj):
        try:
            relationSet = obj.getRelationSet()
        except:
            return False

        flows = [pyatspi.RELATION_FLOWS_FROM, pyatspi.RELATION_FLOWS_TO]
        relations = filter(lambda r: r.getRelationType() in flows, relationSet)
        targets = [r.getTarget(0) for r in relations]
        for target in targets:
            try:
                nSelections = target.queryText().getNSelections()
            except:
                return False
            if nSelections:
                return True

        return False

    def objectContentsAreInClipboard(self, obj=None):
        obj = obj or orca_state.locusOfFocus
        if not obj:
            return False

        if self.isSpreadSheetCell(obj):
            contents = self.getClipboardContents()
            string = self.displayedText(obj) or "\n"
            return string in contents

        return super().objectContentsAreInClipboard(obj)

    #########################################################################
    #                                                                       #
    # Impress-Specific Utilities                                            #
    #                                                                       #
    #########################################################################

    def drawingView(self, obj=orca_state.locusOfFocus):
        """Attempts to locate the Impress drawing view, which is the
        area in which slide editing occurs."""

        return pyatspi.findDescendant(self.topLevelObject(obj), self.isDrawingView)

    def isDrawingView(self, obj):
        """Returns True if obj is the Impress Drawing View."""

        if self.isDocument(obj):
            return (":" in obj.name and "/" in obj.name)

        return False

    def isInImpress(self, obj=orca_state.locusOfFocus):
        """Returns True if obj is in OOo Impress."""

        # Having checked English, Spanish, and Arabic, it would seem
        # that the Frame name will end with "Impress", unlocalized.
        #
        if obj:
            try:
                topLevel = self.topLevelObject(obj)
            except:
                msg = "ERROR: Exception getting top-level object for %s" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                return False
            if not topLevel:
                return False
            if self.isDead(topLevel):
                msg = "SOFFICE: Top level object %s is dead." % topLevel
                debug.println(debug.LEVEL_INFO, msg, True)
                return False
            if topLevel.name.endswith("Impress"):
                return True

        return False

    def slideAndTaskPanes(self, obj=orca_state.locusOfFocus):
        """Attempts to locate the Impress slide pane and task pane."""

        drawingView = self.drawingView(obj)
        if not drawingView:
            return None, None

        parent = drawingView.parent
        if parent:
            parent = parent.parent
        if not parent:
            return None, None

        hasRole = lambda x: x and x.getRole() == pyatspi.ROLE_SPLIT_PANE
        panes = self.findAllDescendants(parent, hasRole)
        if not panes:
            return None, None

        slidePane = taskPane = None
        if self.findAllDescendants(panes[0], self.isDocument):
            slidePane = panes[0]
            if len(panes) == 2:
                taskPane = panes[1]
        else:
            taskPane = panes[0]
            if len(panes) == 2:
                slidePane = panes[1]

        return slidePane, taskPane

    def slideTitleAndPosition(self, obj):
        """Attempts to obtain the title, position of the slide which contains
        or is represented by obj.

        Returns a (title, position, count) tuple.
        """

        if self.isDocument(obj):
            dv = obj
        else:
            dv = self.getContainingDocument(obj)

        if not dv or not self.isDrawingView(dv):
            return "", 0, 0

        positionAndCount = dv.name.split(":")[1]
        position, count = positionAndCount.split("/")
        title = ""
        for child in dv:
            if not child.childCount:
                continue
            # We want an actual Title.
            #
            if child.name.startswith("ImpressTitle"):
                title = self.displayedText(child[0])
                break
            # But we'll live with a Subtitle if we can't find a title.
            # Unlike Titles, a single subtitle can be made up of multiple
            # accessibles.
            #
            elif child.name.startswith("ImpressSubtitle"):
                for line in child:
                    title = self.appendString(title, self.displayedText(line))

        return title, int(position), int(count)

    #########################################################################
    #                                                                       #
    # Miscellaneous Utilities                                               #
    #                                                                       #
    #########################################################################

    def isAutoTextEvent(self, event):
        """Returns True if event is associated with text being autocompleted
        or autoinserted or autocorrected or autosomethingelsed.

        Arguments:
        - event: the accessible event being examined
        """

        if event.source.getRole() != pyatspi.ROLE_PARAGRAPH:
            return False

        lastKey, mods = self.lastKeyAndModifiers()
        if event.type.startswith("object:text-changed:insert"):
            if not event.any_data:
                return False

            if lastKey == "Tab" and event.any_data != "\t":
                return True

            if lastKey in ["BackSpace", "ISO_Left_Tab"]:
                return True

        if event.type.startswith("focus:"):
            if lastKey == "Return":
                try:
                    charCount = event.source.queryText().characterCount
                except:
                    charCount = 0
                return charCount > 0

        return False

    def containingComboBox(self, obj):
        isComboBox = lambda x: x and x.getRole() == pyatspi.ROLE_COMBO_BOX
        if isComboBox(obj):
            comboBox = obj
        else:
            comboBox = pyatspi.findAncestor(obj, isComboBox)

        if not comboBox:
            return None

        if not self.isZombie(comboBox):
            return comboBox

        try:
            parent = comboBox.parent
        except:
            pass
        else:
            replicant = self.findReplicant(parent, comboBox)
            if replicant and not self.isZombie(replicant):
                comboBox = replicant

        return comboBox

    def isComboBoxSelectionChange(self, event):
        comboBox = self.containingComboBox(event.source)
        if not comboBox:
            return False

        lastKey, mods = self.lastKeyAndModifiers()
        if not lastKey in ["Down", "Up"]:
            return False

        return True

    def isComboBoxNoise(self, event):
        role = event.source.getRole()
        if role == pyatspi.ROLE_TEXT and event.type.startswith("object:text-"):
            return self.isComboBoxSelectionChange(event)

        return False

    def isPresentableTextChangedEventForLocusOfFocus(self, event):
        if self.isComboBoxNoise(event):
            msg = "SOFFICE: Event is believed to be combo box noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return super().isPresentableTextChangedEventForLocusOfFocus(event)

    def isReadOnlyTextArea(self, obj):
        if not super().isReadOnlyTextArea(obj):
            return False

        return not self.inDocumentContent(obj)

    def isSelectedTextDeletionEvent(self, event):
        if event.type.startswith("object:state-changed:selected") and not event.detail1:
            return self.isDead(orca_state.locusOfFocus) and self.lastInputEventWasDelete()

        return super().isSelectedTextDeletionEvent(event)

    def lastInputEventWasRedo(self):
        if super().lastInputEventWasRedo():
            return True

        keyString, mods = self.lastKeyAndModifiers()
        if mods & keybindings.COMMAND_MODIFIER_MASK and keyString.lower() == 'y':
            return not (mods & keybindings.SHIFT_MODIFIER_MASK)

        return False

    def selectedChildren(self, obj):
        if not obj:
            return []

        role = obj.getRole()
        isSelection = lambda x: x and 'Selection' in pyatspi.listInterfaces(x)
        if not isSelection(obj) and role == pyatspi.ROLE_COMBO_BOX:
            child = pyatspi.findDescendant(obj, isSelection)
            if child:
                return super().selectedChildren(child)

        # Things only seem broken for certain tables, e.g. the Paths table.
        # TODO - JD: File the LibreOffice bugs and reference them here.
        if role != pyatspi.ROLE_TABLE:
            return super().selectedChildren(obj)

        # We will need to special case this due to the possibility of there
        # being lots of children (which may also prove to be zombie objects).
        # This is why we can't have nice things.
        if self.isSpreadSheetTable(obj):
            return []

        try:
            selection = obj.querySelection()
        except:
            return []

        children = []
        for i, child in enumerate(obj):
            if selection.isChildSelected(i):
                children.append(obj[i])

        return children

    def getFirstCaretPosition(self, obj):
        try:
            text = obj.queryText()
        except:
            if obj and obj.childCount:
                return self.getFirstCaretPosition(obj[0])

        return obj, 0

    def shouldReadFullRow(self, obj):
        if self._script._lastCommandWasStructNav:
            return False

        lastKey, mods = self.lastKeyAndModifiers()
        if lastKey in ["Tab", "ISO_Left_Tab"]:
            return False

        return super().shouldReadFullRow(obj)

    def presentEventFromNonShowingObject(self, event):
        return self.inDocumentContent(event.source)

    def columnConvert(self, column):
        """ Convert a spreadsheet column into it's column label."""

        base26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        if column <= len(base26):
            return base26[column-1]

        res = ""
        while column > 0:
            digit = column % len(base26)
            res = " " + base26[digit-1] + res
            column = int(column / len(base26))

        return res

    def _getCellNameForCoordinates(self, obj, row, col, includeContents=False):
        try:
            table = obj.queryTable()
        except:
            msg = "SOFFICE: Exception querying Table interface of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        try:
            cell = table.getAccessibleAt(row, col)
        except:
            msg = "SOFFICE: Exception getting cell (%i,%i) of %s" % (row, col, obj)
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        name = self.spreadSheetCellName(cell)
        if includeContents:
            text = self.displayedText(cell)
            name = "%s %s" % (text, name)

        return name.strip()

    def _getCoordinatesForSelectedRange(self, obj):
        interfaces = pyatspi.listInterfaces(obj)
        if not ("Table" in interfaces and "Selection" in interfaces):
            return (-1, -1), (-1, -1)

        first, last = self.firstAndLastSelectedChildren(obj)
        firstCoords = self.coordinatesForCell(first)
        lastCoords = self.coordinatesForCell(last)
        return firstCoords, lastCoords

    def speakSelectedCellRange(self, obj):
        firstCoords, lastCoords = self._getCoordinatesForSelectedRange(obj)
        if firstCoords == (-1, -1) or lastCoords == (-1, -1):
            return True

        self._script.presentationInterrupt()

        if firstCoords == lastCoords:
            cell = self._getCellNameForCoordinates(obj, *firstCoords, True)
            self._script.speakMessage(messages.CELL_SELECTED % cell)
            return True

        cell1 = self._getCellNameForCoordinates(obj, *firstCoords, True)
        cell2 = self._getCellNameForCoordinates(obj, *lastCoords, True)
        self._script.speakMessage(messages.CELL_RANGE_SELECTED % (cell1, cell2))
        return True

    def handleCellSelectionChange(self, obj):
        firstCoords, lastCoords = self._getCoordinatesForSelectedRange(obj)
        if firstCoords == (-1, -1) or lastCoords == (-1, -1):
            return True

        current = []
        for r in range(firstCoords[0], lastCoords[0]+1):
            current.extend((r, c) for c in range(firstCoords[1], lastCoords[1]+1))

        current = set(current)
        previous = set(self._calcSelectedCells)
        current.discard((-1, -1))
        previous.discard((-1, -1))

        unselected = sorted(previous.difference(current))
        selected = sorted(current.difference(previous))
        focusCoords = tuple(self.coordinatesForCell(orca_state.locusOfFocus))
        if focusCoords in selected:
            selected.remove(focusCoords)

        self._calcSelectedCells = sorted(current)

        msgs = []
        if len(unselected) == 1:
            cell = self._getCellNameForCoordinates(obj, *unselected[0], True)
            msgs.append(messages.CELL_UNSELECTED % cell)
        elif len(unselected) > 1:
            cell1 = self._getCellNameForCoordinates(obj, *unselected[0], True)
            cell2 = self._getCellNameForCoordinates(obj, *unselected[-1], True)
            msgs.append(messages.CELL_RANGE_UNSELECTED % (cell1, cell2))

        if len(selected) == 1:
            cell = self._getCellNameForCoordinates(obj, *selected[0], True)
            msgs.append(messages.CELL_SELECTED % cell)
        elif len(selected) > 1:
            cell1 = self._getCellNameForCoordinates(obj, *selected[0], True)
            cell2 = self._getCellNameForCoordinates(obj, *selected[-1], True)
            msgs.append(messages.CELL_RANGE_SELECTED % (cell1, cell2))

        if msgs:
            self._script.presentationInterrupt()

        for msg in msgs:
            self._script.speakMessage(msg, interrupt=False)

        return bool(len(msgs))

    def handleRowAndColumnSelectionChange(self, obj):
        interfaces = pyatspi.listInterfaces(obj)
        if not ("Table" in interfaces and "Selection" in interfaces):
            return True

        table = obj.queryTable()
        cols = set(table.getSelectedColumns())
        rows = set(table.getSelectedRows())

        selectedCols = sorted(cols.difference(set(self._calcSelectedColumns)))
        unselectedCols = sorted(set(self._calcSelectedColumns).difference(cols))
        convert = lambda x: self.columnConvert(x+1)
        selectedCols = list(map(convert, selectedCols))
        unselectedCols = list(map(convert, unselectedCols))

        selectedRows = sorted(rows.difference(set(self._calcSelectedRows)))
        unselectedRows = sorted(set(self._calcSelectedRows).difference(rows))
        convert = lambda x: x + 1
        selectedRows = list(map(convert, selectedRows))
        unselectedRows = list(map(convert, unselectedRows))

        self._calcSelectedColumns = list(cols)
        self._calcSelectedRows = list(rows)

        if len(cols) == table.nColumns:
            self._script.speakMessage(messages.DOCUMENT_SELECTED_ALL)
            return True

        if not len(cols) and len(unselectedCols) == table.nColumns:
            self._script.speakMessage(messages.DOCUMENT_UNSELECTED_ALL)
            return True

        msgs = []
        if len(unselectedCols) == 1:
            msgs.append(messages.TABLE_COLUMN_UNSELECTED % unselectedCols[0])
        elif len(unselectedCols) > 1:
            msgs.append(messages.TABLE_COLUMN_RANGE_UNSELECTED % (unselectedCols[0], unselectedCols[-1]))

        if len(unselectedRows) == 1:
            msgs.append(messages.TABLE_ROW_UNSELECTED % unselectedRows[0])
        elif len(unselectedRows) > 1:
            msgs.append(messages.TABLE_ROW_RANGE_UNSELECTED % (unselectedRows[0], unselectedRows[-1]))

        if len(selectedCols) == 1:
            msgs.append(messages.TABLE_COLUMN_SELECTED % selectedCols[0])
        elif len(selectedCols) > 1:
            msgs.append(messages.TABLE_COLUMN_RANGE_SELECTED % (selectedCols[0], selectedCols[-1]))

        if len(selectedRows) == 1:
            msgs.append(messages.TABLE_ROW_SELECTED % selectedRows[0])
        elif len(selectedRows) > 1:
            msgs.append(messages.TABLE_ROW_RANGE_SELECTED % (selectedRows[0], selectedRows[-1]))

        if msgs:
            self._script.presentationInterrupt()

        for msg in msgs:
            self._script.speakMessage(msg, interrupt=False)

        return bool(len(msgs))
