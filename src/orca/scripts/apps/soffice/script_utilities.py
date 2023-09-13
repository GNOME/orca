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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.debug as debug
import orca.keybindings as keybindings
import orca.messages as messages
import orca.orca_state as orca_state
import orca.script_utilities as script_utilities
from orca.ax_object import AXObject
from orca.ax_selection import AXSelection
from orca.ax_utilities import AXUtilities


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

        name = AXObject.get_name(obj)
        if name and AXUtilities.is_push_button(obj):
            return name

        if AXUtilities.is_table_cell(obj):
            strings = list(map(self.displayedText, [x for x in AXObject.iter_children(obj)]))
            text = "\n".join(strings)
            if text.strip():
                return text

        try:
            text = super().displayedText(obj)
        except Exception:
            return ""

        # TODO - JD: This is needed because the default behavior is to fall
        # back on the name, which is bogus. Once that has been fixed, this
        # hack can go.
        if AXUtilities.is_table_cell(obj) and text == name \
           and (self.isSpreadSheetCell(obj) or self.isTextDocumentCell(obj)):
            return ""

        # More bogusness from (at least) Calc combined with the aforementioned
        # fallback-to-name behavior....
        if self.isDocument(obj) and text == name and text.startswith("file:///"):
            return ""

        return text

    def isCellBeingEdited(self, obj):
        parent = AXObject.get_parent(obj)
        if AXUtilities.is_panel(parent) or AXUtilities.is_extended(parent):
            return self.spreadSheetCellName(parent)

        return False

    def spreadSheetCellName(self, cell):
        nameList = AXObject.get_name(cell).split()
        for name in nameList:
            name = name.replace('.', '')
            if not name.isalpha() and name.isalnum():
                return name

        return ''

    def getRowColumnAndTable(self, cell):
        """Returns the (row, column, table) tuple for cell."""

        if not AXUtilities.is_table_cell(cell):
            return -1, -1, None

        cellParent = AXObject.get_parent(cell)
        if AXUtilities.is_table_cell(cellParent):
            cell = cellParent
            cellParent = AXObject.get_parent(cell)

        table = cellParent
        if table is not None and not AXUtilities.is_table(table):
            table = AXObject.get_parent(table)

        try:
            iTable = table.queryTable()
        except Exception:
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

    def isSameObject(self, obj1, obj2, comparePaths=False, ignoreNames=False,
                     ignoreDescriptions=True):
        if obj1 == obj2:
            return True

        if not AXUtilities.have_same_role(obj1, obj2):
            return False

        if AXUtilities.is_paragraph(obj1):
            return False

        name = AXObject.get_name(obj1)
        if name == AXObject.get_name(obj2):
            if AXUtilities.is_frame(obj1):
                return True
            if AXUtilities.is_table_cell(obj1) and not name:
                if self.isZombie(obj1) and self.isZombie(obj2):
                    return False

        return super().isSameObject(obj1, obj2, comparePaths, ignoreNames)

    def isLayoutOnly(self, obj):
        """Returns True if the given object is a container which has
        no presentable information (label, name, displayed text, etc.)."""

        if AXUtilities.is_list(obj):
            if AXUtilities.is_combo_box(AXObject.get_parent(obj)):
                return True
            return super().isLayoutOnly(obj)

        name = AXObject.get_name(obj)
        if not name:
            return super().isLayoutOnly(obj)

        if AXUtilities.is_frame(obj):
            return name == AXObject.get_name(orca_state.activeWindow)

        if AXUtilities.is_panel(obj) and AXObject.get_child_count(obj):
            if AXObject.get_name(AXObject.get_child(obj, 0)) == name:
                return True

        return super().isLayoutOnly(obj)

    def isAnInputLine(self, obj):
        if not obj:
            return False
        if obj == self.locateInputLine(obj):
            return True

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_panel(parent) or AXUtilities.is_extended(parent):
            if self.spreadSheetCellName(parent):
                return False

        parent = AXObject.get_parent(parent)
        if AXUtilities.is_text(parent):
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

        if self._script.inputLineForCell is not None:
            topLevel = self.topLevelObject(self._script.inputLineForCell)
            if self.isSameObject(orca_state.activeWindow, topLevel):
                return self._script.inputLineForCell

        scrollPane = AXObject.find_ancestor(obj, AXUtilities.is_scroll_pane)
        if scrollPane is None:
            return None

        toolbar = None
        for child in AXObject.iter_children(AXObject.get_parent(scrollPane),
                                             AXUtilities.is_tool_bar):
            toolbar = child
            break

        if toolbar is None:
            msg = "ERROR: Calc inputline toolbar not found."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return None

        allParagraphs = self.findAllDescendants(toolbar, AXUtilities.is_paragraph)
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

        parent = AXObject.get_parent_checked(obj)
        while parent:
            if AXObject.get_role(parent) == Atspi.Role.FRAME:
                results[0] = parent
            if AXObject.get_role(parent) == Atspi.Role.TABLE:
                results[1] = parent
            parent = AXObject.get_parent_checked(parent)

        return results

    @staticmethod
    def _flowsFromOrToSelection(obj):
        relationSet = AXObject.get_relations(obj)
        flows = [Atspi.RelationType.FLOWS_FROM, Atspi.RelationType.FLOWS_TO]
        relations = filter(lambda r: r.getRelationType() in flows, relationSet)
        targets = [r.getTarget(0) for r in relations]
        for target in targets:
            try:
                nSelections = target.queryText().getNSelections()
            except Exception:
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

        return AXObject.find_descendant(self.topLevelObject(obj), self.isDrawingView)

    def isDrawingView(self, obj):
        """Returns True if obj is the Impress Drawing View."""

        if self.isDocument(obj):
            name = AXObject.get_name(obj)
            return ":" in name and "/" in name

        return False

    def isInImpress(self, obj=orca_state.locusOfFocus):
        """Returns True if obj is in OOo Impress."""

        # Having checked English, Spanish, and Arabic, it would seem
        # that the Frame name will end with "Impress", unlocalized.
        #
        if obj:
            try:
                topLevel = self.topLevelObject(obj)
            except Exception:
                tokens = ["ERROR: Exception getting top-level object for", obj]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return False
            if not topLevel:
                return False
            if AXObject.is_dead(topLevel):
                tokens = ["SOFFICE: Top level object", topLevel, "is dead."]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return False
            if AXObject.get_name(topLevel).endswith("Impress"):
                return True

        return False

    def slideAndTaskPanes(self, obj=orca_state.locusOfFocus):
        """Attempts to locate the Impress slide pane and task pane."""

        drawingView = self.drawingView(obj)
        if not drawingView:
            return None, None

        parent = AXObject.get_parent(drawingView)
        if parent:
            parent = AXObject.get_parent(parent)
        if not parent:
            return None, None

        panes = self.findAllDescendants(parent, AXUtilities.is_split_pane)
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

        dv = self.getDocumentForObject(obj)
        if not dv or not self.isDrawingView(dv):
            return "", 0, 0

        positionAndCount = AXObject.get_name(dv).split(":")[1]
        position, count = positionAndCount.split("/")
        title = ""
        for child in dv:
            childCount = AXObject.get_child_count(child)
            if not childCount:
                continue
            # We want an actual Title.
            #
            if AXObject.get_name(child).startswith("ImpressTitle"):
                title = self.displayedText(AXObject.get_child(child, 0))
                break
            # But we'll live with a Subtitle if we can't find a title.
            # Unlike Titles, a single subtitle can be made up of multiple
            # accessibles.
            #
            elif AXObject.get_name(child).startswith("ImpressSubtitle"):
                for i in range(childCount):
                    line = AXObject.get_child(child, i)
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

        if AXObject.get_role(event.source) != Atspi.Role.PARAGRAPH:
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
                except Exception:
                    charCount = 0
                return charCount > 0

        return False

    def containingComboBox(self, obj):
        if AXUtilities.is_combo_box(obj):
            comboBox = obj
        else:
            comboBox = AXObject.find_ancestor(obj, AXUtilities.is_combo_box)

        if not comboBox:
            return None

        if not self.isZombie(comboBox):
            return comboBox

        parent = AXObject.get_parent(comboBox)
        if not parent:
            return comboBox

        replicant = self.findReplicant(parent, comboBox)
        if replicant and not self.isZombie(replicant):
            comboBox = replicant

        return comboBox

    def isComboBoxSelectionChange(self, event):
        comboBox = self.containingComboBox(event.source)
        if not comboBox:
            return False

        lastKey, mods = self.lastKeyAndModifiers()
        if lastKey not in ["Down", "Up"]:
            return False

        return True

    def isComboBoxNoise(self, event):
        role = AXObject.get_role(event.source)
        if role == Atspi.Role.TEXT and event.type.startswith("object:text-"):
            return self.isComboBoxSelectionChange(event)

        return False

    def isPresentableTextChangedEventForLocusOfFocus(self, event):
        if self.isComboBoxNoise(event):
            msg = "SOFFICE: Event is believed to be combo box noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        return super().isPresentableTextChangedEventForLocusOfFocus(event)

    def isReadOnlyTextArea(self, obj):
        if not super().isReadOnlyTextArea(obj):
            return False

        return not self.inDocumentContent(obj)

    def isSelectedTextDeletionEvent(self, event):
        if event.type.startswith("object:state-changed:selected") and not event.detail1:
            return AXObject.is_dead(orca_state.locusOfFocus) and self.lastInputEventWasDelete()

        return super().isSelectedTextDeletionEvent(event)

    def lastInputEventWasRedo(self):
        if super().lastInputEventWasRedo():
            return True

        keyString, mods = self.lastKeyAndModifiers()
        if mods & keybindings.COMMAND_MODIFIER_MASK and keyString.lower() == 'y':
            return not (mods & keybindings.SHIFT_MODIFIER_MASK)

        return False

    def selectedChildren(self, obj):
        # TODO - JD: Are these overrides still needed? They appear to be
        # quite old.

        if obj is None:
            return []

        if not AXObject.supports_selection(obj) and AXUtilities.is_combo_box(obj):
            child = AXObject.find_descendant(obj, AXObject.supports_selection)
            if child:
                return super().selectedChildren(child)

        # Things only seem broken for certain tables, e.g. the Paths table.
        # TODO - JD: File the LibreOffice bugs and reference them here.
        if not AXUtilities.is_table(obj):
            return super().selectedChildren(obj)

        # We will need to special case this due to the possibility of there
        # being lots of children (which may also prove to be zombie objects).
        # This is why we can't have nice things.
        if self.isSpreadSheetTable(obj):
            return []

        return AXSelection.get_selected_children(obj)

    def getFirstCaretPosition(self, obj):
        try:
            obj.queryText()
        except Exception:
            if AXObject.get_child_count(obj):
                return self.getFirstCaretPosition(AXObject.get_child(obj, 0))

        return obj, 0

    def getWordAtOffsetAdjustedForNavigation(self, obj, offset=None):
        return self.getWordAtOffset(obj, offset)

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
        except Exception:
            tokens = ["SOFFICE: Exception querying Table interface of", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        try:
            cell = table.getAccessibleAt(row, col)
        except Exception:
            tokens = [f"SOFFICE: Exception getting cell ({row},{col}) of", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        name = self.spreadSheetCellName(cell)
        if includeContents:
            text = self.displayedText(cell)
            name = f"{text} {name}"

        return name.strip()

    def _getCoordinatesForSelectedRange(self, obj):
        if not (AXObject.supports_table(obj) and AXObject.supports_selection(obj)):
            tokens = ["SOFFICE:", obj, "does not implement both selection and table"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return (-1, -1), (-1, -1)

        first = AXSelection.get_selected_child(obj, 0)
        last = AXSelection.get_selected_child(obj, -1)
        firstCoords = self.coordinatesForCell(first)
        lastCoords = self.coordinatesForCell(last)
        return firstCoords, lastCoords

    def getSelectionContainer(self, obj):
        # Writer implements the selection interface on the document and all its
        # children. The former is interesting, but interferes with our presentation
        # of selected text. The latter is just weird.
        if AXUtilities.is_document_text(obj):
            return None
        if AXObject.find_ancestor(obj, AXUtilities.is_document_text):
            return None
        return super().getSelectionContainer(obj)

    def speakSelectedCellRange(self, obj):
        firstCoords, lastCoords = self._getCoordinatesForSelectedRange(obj)
        if firstCoords == (-1, -1) or lastCoords == (-1, -1):
            return False

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
        if not (AXObject.supports_table(obj) and AXObject.supports_selection(obj)):
            return True

        table = obj.queryTable()
        cols = set(table.getSelectedColumns())
        rows = set(table.getSelectedRows())

        selectedCols = sorted(cols.difference(set(self._calcSelectedColumns)))
        unselectedCols = sorted(set(self._calcSelectedColumns).difference(cols))

        def convertColumn(x):
            return self.columnConvert(x+1)

        def convertRow(x):
            return x + 1

        selectedCols = list(map(convertColumn, selectedCols))
        unselectedCols = list(map(convertColumn, unselectedCols))

        selectedRows = sorted(rows.difference(set(self._calcSelectedRows)))
        unselectedRows = sorted(set(self._calcSelectedRows).difference(rows))

        selectedRows = list(map(convertRow, selectedRows))
        unselectedRows = list(map(convertRow, unselectedRows))

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
            msgs.append(messages.TABLE_COLUMN_RANGE_UNSELECTED % \
                        (unselectedCols[0], unselectedCols[-1]))

        if len(unselectedRows) == 1:
            msgs.append(messages.TABLE_ROW_UNSELECTED % unselectedRows[0])
        elif len(unselectedRows) > 1:
            msgs.append(messages.TABLE_ROW_RANGE_UNSELECTED % \
                        (unselectedRows[0], unselectedRows[-1]))

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
