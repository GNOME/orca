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

from orca import debug
from orca import focus_manager
from orca import input_event_manager
from orca import messages
from orca import script_utilities
from orca.ax_object import AXObject
from orca.ax_selection import AXSelection
from orca.ax_table import AXTable
from orca.ax_text import AXText
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

    def isCellBeingEdited(self, obj):
        parent = AXObject.get_parent(obj)
        if AXUtilities.is_panel(parent) or AXUtilities.is_extended(parent):
            return self.spreadSheetCellName(parent)

        return False

    def spreadSheetCellName(self, cell):
        name_list = AXObject.get_name(cell).split()
        for name in name_list:
            name = name.replace('.', '')
            if not name.isalpha() and name.isalnum():
                return name

        return ''

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
            return name == AXObject.get_name(focus_manager.get_manager().get_active_window())

        if AXUtilities.is_panel(obj) and AXObject.get_child_count(obj):
            if AXObject.get_name(AXObject.get_child(obj, 0)) == name:
                return True

        return super().isLayoutOnly(obj)

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
            if AXUtilities.is_frame(parent):
                results[0] = parent
            elif AXUtilities.is_table(parent):
                results[1] = parent
            parent = AXObject.get_parent_checked(parent)

        return results

    @staticmethod
    def _flowsFromOrToSelection(obj):
        targets = AXUtilities.get_flows_from(obj)
        targets.extend(AXUtilities.get_flows_to(obj))
        for target in targets:
            if AXText.has_selected_text(target):
                return True

        return False

    def objectContentsAreInClipboard(self, obj=None):
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if not obj:
            return False

        if self.isSpreadSheetCell(obj):
            contents = self.getClipboardContents()
            string = AXText.get_all_text(obj) or "\n"
            return string in contents

        return super().objectContentsAreInClipboard(obj)

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
        # default logic for editable comboboxes works for LibreOffice >= 24.8
        if self.isEditableDescendantOfComboBox(event.source):
            return super().isAutoTextEvent(event)

        if not AXUtilities.is_paragraph(event.source):
            return False

        manager = input_event_manager.get_manager()
        if event.type.startswith("object:text-changed:insert"):
            if not event.any_data:
                return False

            if manager.last_event_was_tab() and event.any_data != "\t":
                return True

            if manager.last_event_was_backspace():
                return True

        return False

    def isReadOnlyTextArea(self, obj):
        if not super().isReadOnlyTextArea(obj):
            return False

        return not self.inDocumentContent(obj)

    def isSelectedTextDeletionEvent(self, event):
        if event.type.startswith("object:state-changed:selected") and not event.detail1:
            return input_event_manager.get_manager().last_event_was_delete() \
                and focus_manager.get_manager().focus_is_dead()

        return super().isSelectedTextDeletionEvent(event)

    def getWordAtOffsetAdjustedForNavigation(self, obj, offset=None):
        return AXText.get_word_at_offset(obj, offset)

    def shouldReadFullRow(self, obj, prevObj=None):
        if self._script.get_table_navigator().last_input_event_was_navigation_command():
            return False

        if input_event_manager.get_manager().last_event_was_tab_navigation():
            return False

        return super().shouldReadFullRow(obj, prevObj)

    def presentEventFromNonShowingObject(self, event):
        return self.inDocumentContent(event.source)

    def _isTopLevelObject(self, obj):
        # https://bugs.documentfoundation.org/show_bug.cgi?id=160806
        if AXObject.get_parent(obj) is None and AXObject.get_role(obj) in self._topLevelRoles():
            tokens = ["SOFFICE:", obj, "has no parent. Treating as top-level."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True, True)
            return True

        return super()._isTopLevelObject(obj)

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
        # https://bugs.documentfoundation.org/show_bug.cgi?id=158030
        cell = AXTable.get_cell_at(obj, row, col)
        name = self.spreadSheetCellName(cell)
        if includeContents:
            text = AXText.get_all_text(cell)
            name = f"{text} {name}"

        return name.strip()

    def _getCoordinatesForSelectedRange(self, obj):
        if not (AXObject.supports_table(obj) and AXObject.supports_selection(obj)):
            tokens = ["SOFFICE:", obj, "does not implement both selection and table"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return (-1, -1), (-1, -1)

        first = AXSelection.get_selected_child(obj, 0)
        last = AXSelection.get_selected_child(obj, -1)
        return AXTable.get_cell_coordinates(first), AXTable.get_cell_coordinates(last)

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
        focusCoords = AXTable.get_cell_coordinates(focus_manager.get_manager().get_locus_of_focus())
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

        cols = set(AXTable.get_selected_columns(obj))
        rows = set(AXTable.get_selected_rows(obj))

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

        columnCount = AXTable.get_column_count(obj)
        if len(cols) == columnCount:
            self._script.speakMessage(messages.DOCUMENT_SELECTED_ALL)
            return True

        if not cols and len(unselectedCols) == columnCount:
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
