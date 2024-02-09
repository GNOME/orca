# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2011-2023 Igalia, S.L.
# Copyright 2023 GNOME Foundation Inc.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

"""Provides Orca-controlled navigation for tabular content."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2011-2023 Igalia, S.L." \
                "Copyright (c) 2023 GNOME Foundation Inc."
__license__   = "LGPL"

from . import cmdnames
from . import debug
from . import focus_manager
from . import input_event
from . import keybindings
from . import messages
from . import orca_state
from . import settings_manager
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_utilities import AXUtilities


class TableNavigator:
    """Provides Orca-controlled navigation for tabular content."""

    def __init__(self):
        self._previous_reported_row = None
        self._previous_reported_col = None
        self._last_input_event = None
        self._enabled = True

        # To make it possible for focus mode to suspend this navigation without
        # changing the user's preferred setting.
        self._suspended = False

        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the table-navigator keybindings."""

        if refresh:
            msg = "TABLE NAVIGATOR: Refreshing bindings."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif self._bindings.isEmpty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the table-navigator handlers."""

        if refresh:
            msg = "TABLE NAVIGATOR: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def is_enabled(self):
        """Returns true if table-navigation support is enabled."""

        return self._enabled

    def last_input_event_was_navigation_command(self):
        """Returns true if the last input event was a navigation command."""

        result = self._last_input_event is not None \
            and (self._last_input_event == orca_state.lastNonModifierKeyEvent \
                or orca_state.lastNonModifierKeyEvent.isReleaseFor(self._last_input_event))

        if self._last_input_event is not None:
            string = self._last_input_event.asSingleLineString()
        else:
            string = "None"

        msg = f"TABLE NAVIGATOR: Last navigation event ({string}) was last key event: {result}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return result

    def _setup_bindings(self):
        """Sets up the table-navigation key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.defaultModifierMask,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers.get("table_navigator_toggle_enabled"),
                1,
                not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "Left",
                keybindings.defaultModifierMask,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers.get("table_cell_left"),
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "Right",
                keybindings.defaultModifierMask,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers.get("table_cell_right"),
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "Up",
                keybindings.defaultModifierMask,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers.get("table_cell_up"),
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "Down",
                keybindings.defaultModifierMask,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers.get("table_cell_down"),
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "Home",
                keybindings.defaultModifierMask,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers.get("table_cell_first"),
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "End",
                keybindings.defaultModifierMask,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers.get("table_cell_last"),
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "Left",
                keybindings.defaultModifierMask,
                keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK,
                self._handlers.get("table_cell_beginning_of_row"),
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "Right",
                keybindings.defaultModifierMask,
                keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK,
                self._handlers.get("table_cell_end_of_row"),
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "Up",
                keybindings.defaultModifierMask,
                keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK,
                self._handlers.get("table_cell_top_of_column"),
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "Down",
                keybindings.defaultModifierMask,
                keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK,
                self._handlers.get("table_cell_bottom_of_column"),
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "r",
                keybindings.defaultModifierMask,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers["set_dynamic_column_headers_row"],
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "r",
                keybindings.defaultModifierMask,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers["clear_dynamic_column_headers_row"],
                2,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "c",
                keybindings.defaultModifierMask,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers["set_dynamic_row_headers_column"],
                1,
                self._enabled and not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "c",
                keybindings.defaultModifierMask,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers["clear_dynamic_row_headers_column"],
                2,
                self._enabled and not self._suspended))

        # This pulls in the user's overrides to alternative keys.
        self._bindings = settings_manager.getManager().overrideKeyBindings(
            self._handlers, self._bindings, False)

        msg = f"TABLE NAVIGATOR: Bindings set up. Suspended: {self._suspended}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        tokens = [self._bindings]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

    def _setup_handlers(self):
        """Sets up the table-navigator input event handlers."""

        self._handlers = {}

        self._handlers["table_navigator_toggle_enabled"] = \
            input_event.InputEventHandler(
                self._toggle_enabled,
                cmdnames.TABLE_NAVIGATION_TOGGLE,
                enabled = not self._suspended)

        self._handlers["table_cell_left"] = \
            input_event.InputEventHandler(
                self._table_cell_left,
                cmdnames.TABLE_CELL_LEFT,
                enabled = self._enabled and not self._suspended)

        self._handlers["table_cell_right"] = \
            input_event.InputEventHandler(
                self._table_cell_right,
                cmdnames.TABLE_CELL_RIGHT,
                enabled = self._enabled and not self._suspended)

        self._handlers["table_cell_up"] = \
            input_event.InputEventHandler(
                self._table_cell_up,
                cmdnames.TABLE_CELL_UP,
                enabled = self._enabled and not self._suspended)

        self._handlers["table_cell_down"] = \
            input_event.InputEventHandler(
                self._table_cell_down,
                cmdnames.TABLE_CELL_DOWN,
                enabled = self._enabled and not self._suspended)

        self._handlers["table_cell_first"] = \
            input_event.InputEventHandler(
                self._table_cell_first,
                cmdnames.TABLE_CELL_FIRST,
                enabled = self._enabled and not self._suspended)

        self._handlers["table_cell_last"] = \
            input_event.InputEventHandler(
                self._table_cell_last,
                cmdnames.TABLE_CELL_LAST,
                enabled = self._enabled and not self._suspended)

        self._handlers["table_cell_beginning_of_row"] = \
            input_event.InputEventHandler(
                self._table_cell_beginning_of_row,
                cmdnames.TABLE_CELL_BEGINNING_OF_ROW,
                enabled = self._enabled and not self._suspended)

        self._handlers["table_cell_end_of_row"] = \
            input_event.InputEventHandler(
                self._table_cell_end_of_row,
                cmdnames.TABLE_CELL_END_OF_ROW,
                enabled = self._enabled and not self._suspended)

        self._handlers["table_cell_top_of_column"] = \
            input_event.InputEventHandler(
                self._table_cell_top_of_column,
                cmdnames.TABLE_CELL_TOP_OF_COLUMN,
                enabled = self._enabled and not self._suspended)

        self._handlers["table_cell_bottom_of_column"] = \
            input_event.InputEventHandler(
                self._table_cell_bottom_of_column,
                cmdnames.TABLE_CELL_BOTTOM_OF_COLUMN,
                enabled = self._enabled and not self._suspended)

        self._handlers["set_dynamic_column_headers_row"] = \
            input_event.InputEventHandler(
                self._set_dynamic_column_headers_row,
                cmdnames.DYNAMIC_COLUMN_HEADER_SET,
                enabled = self._enabled and not self._suspended)

        self._handlers["clear_dynamic_column_headers_row"] = \
            input_event.InputEventHandler(
                self._clear_dynamic_column_headers_row,
                cmdnames.DYNAMIC_COLUMN_HEADER_CLEAR,
                enabled = self._enabled and not self._suspended)

        self._handlers["set_dynamic_row_headers_column"] = \
            input_event.InputEventHandler(
                self._set_dynamic_row_headers_column,
                cmdnames.DYNAMIC_ROW_HEADER_SET,
                enabled = self._enabled and not self._suspended)

        self._handlers["clear_dynamic_row_headers_column"] = \
            input_event.InputEventHandler(
                self._clear_dynamic_row_headers_column,
                cmdnames.DYNAMIC_ROW_HEADER_CLEAR,
                enabled = self._enabled and not self._suspended)

        msg = f"TABLE NAVIGATOR: Handlers set up. Suspended: {self._suspended}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def refresh_bindings_and_grabs(self, script, reason=""):
        """Refreshes table navigation bindings and grabs for script."""

        msg = "TABLE NAVIGATOR: Refreshing bindings and grabs"
        if reason:
            msg += f": {reason}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        for binding in self._bindings.keyBindings:
            script.keyBindings.remove(binding, includeGrabs=True)

        self._handlers = self.get_handlers(True)
        self._bindings = self.get_bindings(True)

        for binding in self._bindings.keyBindings:
            script.keyBindings.add(binding, includeGrabs=not self._suspended)

    def _toggle_enabled(self, script, event=None):
        """Toggles table navigation."""

        self._enabled = not self._enabled

        if self._enabled:
            script.presentMessage(messages.TABLE_NAVIGATION_ENABLED)
        else:
            script.presentMessage(messages.TABLE_NAVIGATION_DISABLED)

        self._last_input_event = None
        self.refresh_bindings_and_grabs(script, "toggling table navigation")
        return True

    def suspend_commands(self, script, suspended, reason=""):
        """Suspends table navigation independent of the enabled setting."""

        if suspended == self._suspended:
            return

        msg = f"TABLE NAVIGATOR: Suspended: {suspended}"
        if reason:
            msg += f": {reason}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._suspended = suspended
        self.refresh_bindings_and_grabs(script, f"Suspended changed to {suspended}")

    def _is_blank(self, obj):
        """Returns True if obj is empty or consists of only whitespace."""

        if AXUtilities.is_focusable(obj):
            tokens = ["TABLE NAVIGATOR:", obj, "is not blank: it is focusable"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXObject.get_name(obj):
            tokens = ["TABLE NAVIGATOR:", obj, "is not blank: it has a name"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXObject.get_child_count(obj):
            for child in AXObject.iter_children(obj):
                if not self._is_blank(child):
                    tokens = ["TABLE NAVIGATOR:", obj, "is not blank:", child, "is not blank"]
                    debug.printTokens(debug.LEVEL_INFO, tokens, True)
                    return False
            return True

        if AXObject.supports_text(obj) and obj.queryText().getText(0, -1).strip():
            tokens = ["TABLE NAVIGATOR:", obj, "is not blank: it has text"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["TABLE NAVIGATOR: Treating", obj, "as blank"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return True

    def _get_current_cell(self):
        """Returns the current cell."""

        cell = focus_manager.getManager().get_locus_of_focus()

        # We might have nested cells. So far this has only been seen in Gtk, where the
        # parent of a table cell is also a table cell. From the user's perspective, we
        # are on the parent. This check also covers Writer documents in which the caret
        # is likely in a paragraph child of the cell.
        parent = AXObject.get_parent(cell)
        if AXUtilities.is_table_cell_or_header(parent):
            cell = parent

        # And we might instead be in some deeply-nested elements which display text in
        # a web table, so we do one more check.
        if not AXUtilities.is_table_cell_or_header(cell):
            cell = AXObject.find_ancestor(cell, AXUtilities.is_table_cell_or_header)

        tokens = ["TABLE NAVIGATOR: Current cell is", cell]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return cell

    def _get_cell_coordinates(self, cell):
        """Returns the coordinates of cell, possibly adjusted for linear movement."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        if self._previous_reported_row is None or self._previous_reported_row is None:
            return row, col

        # If we're in a cell that spans multiple rows and/or columns, the coordinates will refer to
        # the upper left cell in the spanned range(s). We're storing the last row and column that
        # we presented in order to facilitate more linear movement. Therefore, if the cell at the
        # stored coordinates is the same as cell, we prefer the stored coordinates.
        last_cell = AXTable.get_cell_at(
            AXTable.get_table(cell), self._previous_reported_row, self._previous_reported_col)
        if last_cell == cell:
            return self._previous_reported_row, self._previous_reported_col

        return row, col

    def _table_cell_left(self, script, event=None):
        """Moves to the cell on the left."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_start_of_row(current):
            script.presentMessage(messages.TABLE_ROW_BEGINNING)
            return True

        row, col = self._get_cell_coordinates(current)
        cell = AXTable.get_cell_on_left(current)

        if settings_manager.getManager().getSetting("skipBlankCells"):
            while cell and self._is_blank(cell) and not AXTable.is_start_of_row(cell):
                cell = AXTable.get_cell_on_left(cell)

        self._present_cell(script, cell, row, col - 1, current)
        return True

    def _table_cell_right(self, script, event=None):
        """Moves to the cell on the right."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_end_of_row(current):
            script.presentMessage(messages.TABLE_ROW_END)
            return True

        row, col = self._get_cell_coordinates(current)
        cell = AXTable.get_cell_on_right(current)

        if settings_manager.getManager().getSetting("skipBlankCells"):
            while cell and self._is_blank(cell) and not AXTable.is_end_of_row(cell):
                cell = AXTable.get_cell_on_right(cell)

        self._present_cell(script, cell, row, col + 1, current)
        return True

    def _table_cell_up(self, script, event=None):
        """Moves to the cell above."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_top_of_column(current):
            script.presentMessage(messages.TABLE_COLUMN_TOP)
            return True

        row, col = self._get_cell_coordinates(current)
        cell = AXTable.get_cell_above(current)

        if settings_manager.getManager().getSetting("skipBlankCells"):
            while cell and self._is_blank(cell) and not AXTable.is_top_of_column(cell):
                cell = AXTable.get_cell_above(cell)

        self._present_cell(script, cell, row - 1, col, current)
        return True

    def _table_cell_down(self, script, event=None):
        """Moves to the cell below."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_bottom_of_column(current):
            script.presentMessage(messages.TABLE_COLUMN_BOTTOM)
            return True

        row, col = self._get_cell_coordinates(current)
        cell = AXTable.get_cell_below(current)

        if settings_manager.getManager().getSetting("skipBlankCells"):
            while cell and self._is_blank(cell) and not AXTable.is_bottom_of_column(cell):
                cell = AXTable.get_cell_below(cell)

        self._present_cell(script, cell, row + 1, col, current)
        return True

    def _table_cell_first(self, script, event=None):
        """Moves to the first cell."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(current)
        cell = AXTable.get_first_cell(table)
        self._present_cell(script, cell, 0, 0, current)
        return True

    def _table_cell_last(self, script, event=None):
        """Moves to the last cell."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(current)
        cell = AXTable.get_last_cell(table)
        self._present_cell(
            script, cell, AXTable.get_row_count(table), AXTable.get_column_count(table), current)
        return True

    def _table_cell_beginning_of_row(self, script, event=None):
        """Moves to the beginning of the row."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_start_of_row(current):
            script.presentMessage(messages.TABLE_ROW_BEGINNING)
            return True

        cell = AXTable.get_start_of_row(current)
        row, col = self._get_cell_coordinates(cell)
        self._present_cell(script, cell, row, col, current)
        return True

    def _table_cell_end_of_row(self, script, event=None):
        """Moves to the end of the row."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_end_of_row(current):
            script.presentMessage(messages.TABLE_ROW_END)
            return True

        cell = AXTable.get_end_of_row(current)
        row, col = self._get_cell_coordinates(cell)
        self._present_cell(script, cell, row, col, current)
        return True

    def _table_cell_top_of_column(self, script, event=None):
        """Moves to the top of the column."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_top_of_column(current):
            script.presentMessage(messages.TABLE_COLUMN_TOP)
            return True

        row = self._get_cell_coordinates(current)[0]
        cell = AXTable.get_top_of_column(current)
        col = self._get_cell_coordinates(cell)[1]
        self._present_cell(script, cell, row, col, current)
        return True

    def _table_cell_bottom_of_column(self, script, event=None):
        """Moves to the bottom of the column."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_bottom_of_column(current):
            script.presentMessage(messages.TABLE_COLUMN_BOTTOM)
            return True

        row = self._get_cell_coordinates(current)[0]
        cell = AXTable.get_bottom_of_column(current)
        col = self._get_cell_coordinates(cell)[1]
        self._present_cell(script, cell, row, col, current)
        return True

    def _set_dynamic_column_headers_row(self, script, event=None):
        """Sets the row for the dynamic header columns."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(current)
        if table:
            row = AXTable.get_cell_coordinates(current)[0]
            AXTable.set_dynamic_column_headers_row(table, row)
            script.presentMessage(messages.DYNAMIC_COLUMN_HEADER_SET % (row + 1))

        return True

    def _clear_dynamic_column_headers_row(self, script, event=None):
        """Clears the row for the dynamic column headers."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(focus_manager.getManager().get_locus_of_focus())
        if table:
            script.presentationInterrupt()
            AXTable.clear_dynamic_column_headers_row(table)
            script.presentMessage(messages.DYNAMIC_COLUMN_HEADER_CLEARED)

        return True

    def _set_dynamic_row_headers_column(self, script, event=None):
        """Sets the column for the dynamic row headers."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(current)
        if table:
            column = AXTable.get_cell_coordinates(current)[1]
            AXTable.set_dynamic_row_headers_column(table, column)
            script.presentMessage(
                messages.DYNAMIC_ROW_HEADER_SET % script.utilities.columnConvert(column + 1))

        return True

    def _clear_dynamic_row_headers_column(self, script, event=None):
        """Clears the column for the dynamic row headers."""

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(focus_manager.getManager().get_locus_of_focus())
        if table:
            script.presentationInterrupt()
            AXTable.clear_dynamic_row_headers_column(table)
            script.presentMessage(messages.DYNAMIC_ROW_HEADER_CLEARED)

        return True

    def _present_cell(self, script, cell, row, col, previous_cell):
        """Presents cell to the user."""

        if not AXUtilities.is_table_cell_or_header(cell):
            tokens = ["TABLE NAVIGATOR: ", cell, f"(row {row}, column {col}) is not cell or header"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        self._previous_reported_row = row
        self._previous_reported_col = col

        if script.utilities.grabFocusWhenSettingCaret(cell):
            AXObject.grab_focus(cell)

        obj, offset = script.utilities.getFirstCaretPosition(cell)
        focus_manager.getManager().set_locus_of_focus(None, obj, False)
        if AXObject.supports_text(obj) and not script.utilities.isGUICell(cell):
            script.utilities.setCaretPosition(obj, offset)

        script.presentObject(cell, offset=offset, priorObj=previous_cell, interrupt=True)

        # TODO - JD: This should be part of the normal table cell presentation.
        if settings_manager.getManager().getSetting("speakCellCoordinates"):
            script.presentMessage(
                messages.TABLE_CELL_COORDINATES % {"row" : row + 1, "column" : col + 1})

        # TODO - JD: Ditto.
        if settings_manager.getManager().getSetting("speakCellSpan"):
            rowspan, colspan = AXTable.get_cell_spans(cell)
            if rowspan > 1 or colspan > 1:
                script.presentMessage(messages.cellSpan(rowspan, colspan))

_navigator = TableNavigator()
def getNavigator():
    """Returns the Table Navigator"""

    return _navigator
