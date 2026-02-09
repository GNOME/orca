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

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines

"""Provides Orca-controlled navigation for tabular content."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


from typing import TYPE_CHECKING

from . import cmdnames
from . import command_manager
from . import dbus_service
from . import debug
from . import gsettings_registry
from . import focus_manager
from . import guilabels
from . import input_event
from . import input_event_manager
from . import keybindings
from . import messages
from . import presentation_manager
from . import settings
from . import speech_presenter
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .input_event import InputEvent
    from .scripts import default


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.TableNavigation",
    name="table-navigation",
)
class TableNavigator:
    """Provides Orca-controlled navigation for tabular content."""

    def __init__(self) -> None:
        self._previous_reported_row: int | None = None
        self._previous_reported_col: int | None = None
        self._last_input_event: InputEvent | None = None
        self._enabled: bool = True

        # To make it possible for focus mode to suspend this navigation without
        # changing the user's preferred setting.
        self._suspended: bool = False
        self._initialized: bool = False

        msg = "TABLE NAVIGATOR: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("TableNavigator", self)

    def is_enabled(self) -> bool:
        """Returns true if table-navigation support is enabled."""

        return self._enabled

    def last_input_event_was_navigation_command(self) -> bool:
        """Returns true if the last input event was a navigation command."""

        if self._last_input_event is None:
            return False

        manager = input_event_manager.get_manager()
        result = manager.last_event_equals_or_is_release_for_event(self._last_input_event)
        if self._last_input_event is not None:
            string = self._last_input_event.as_single_line_string()
        else:
            string = "None"

        msg = f"TABLE NAVIGATOR: Last navigation event ({string}) is last input event: {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_TABLE_NAVIGATION

        # Keybindings (same for desktop and laptop)
        kb_t = keybindings.KeyBinding("t", keybindings.ORCA_SHIFT_MODIFIER_MASK)
        kb_left = keybindings.KeyBinding("Left", keybindings.SHIFT_ALT_MODIFIER_MASK)
        kb_right = keybindings.KeyBinding("Right", keybindings.SHIFT_ALT_MODIFIER_MASK)
        kb_up = keybindings.KeyBinding("Up", keybindings.SHIFT_ALT_MODIFIER_MASK)
        kb_down = keybindings.KeyBinding("Down", keybindings.SHIFT_ALT_MODIFIER_MASK)
        kb_home = keybindings.KeyBinding("Home", keybindings.SHIFT_ALT_MODIFIER_MASK)
        kb_end = keybindings.KeyBinding("End", keybindings.SHIFT_ALT_MODIFIER_MASK)
        kb_left_orca = keybindings.KeyBinding("Left", keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK)
        kb_right_orca = keybindings.KeyBinding("Right", keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK)
        kb_up_orca = keybindings.KeyBinding("Up", keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK)
        kb_down_orca = keybindings.KeyBinding("Down", keybindings.ORCA_ALT_SHIFT_MODIFIER_MASK)
        kb_r = keybindings.KeyBinding("r", keybindings.ORCA_SHIFT_MODIFIER_MASK)
        kb_r_2 = keybindings.KeyBinding("r", keybindings.ORCA_SHIFT_MODIFIER_MASK, click_count=2)
        kb_c = keybindings.KeyBinding("c", keybindings.ORCA_SHIFT_MODIFIER_MASK)
        kb_c_2 = keybindings.KeyBinding("c", keybindings.ORCA_SHIFT_MODIFIER_MASK, click_count=2)

        manager.add_command(
            command_manager.KeyboardCommand(
                "table_navigator_toggle_enabled",
                self.toggle_enabled,
                group_label,
                cmdnames.TABLE_NAVIGATION_TOGGLE,
                desktop_keybinding=kb_t,
                laptop_keybinding=kb_t,
                is_group_toggle=True,
            )
        )

        # (name, function, description, keybinding)
        commands_data = [
            ("table_cell_left", self.move_left, cmdnames.TABLE_CELL_LEFT, kb_left),
            ("table_cell_right", self.move_right, cmdnames.TABLE_CELL_RIGHT, kb_right),
            ("table_cell_up", self.move_up, cmdnames.TABLE_CELL_UP, kb_up),
            ("table_cell_down", self.move_down, cmdnames.TABLE_CELL_DOWN, kb_down),
            ("table_cell_first", self.move_to_first_cell, cmdnames.TABLE_CELL_FIRST, kb_home),
            ("table_cell_last", self.move_to_last_cell, cmdnames.TABLE_CELL_LAST, kb_end),
            (
                "table_cell_beginning_of_row",
                self.move_to_beginning_of_row,
                cmdnames.TABLE_CELL_BEGINNING_OF_ROW,
                kb_left_orca,
            ),
            (
                "table_cell_end_of_row",
                self.move_to_end_of_row,
                cmdnames.TABLE_CELL_END_OF_ROW,
                kb_right_orca,
            ),
            (
                "table_cell_top_of_column",
                self.move_to_top_of_column,
                cmdnames.TABLE_CELL_TOP_OF_COLUMN,
                kb_up_orca,
            ),
            (
                "table_cell_bottom_of_column",
                self.move_to_bottom_of_column,
                cmdnames.TABLE_CELL_BOTTOM_OF_COLUMN,
                kb_down_orca,
            ),
            (
                "set_dynamic_column_headers_row",
                self.set_dynamic_column_headers_row,
                cmdnames.DYNAMIC_COLUMN_HEADER_SET,
                kb_r,
            ),
            (
                "clear_dynamic_column_headers_row",
                self.clear_dynamic_column_headers_row,
                cmdnames.DYNAMIC_COLUMN_HEADER_CLEAR,
                kb_r_2,
            ),
            (
                "set_dynamic_row_headers_column",
                self.set_dynamic_row_headers_column,
                cmdnames.DYNAMIC_ROW_HEADER_SET,
                kb_c,
            ),
            (
                "clear_dynamic_row_headers_column",
                self.clear_dynamic_row_headers_column,
                cmdnames.DYNAMIC_ROW_HEADER_CLEAR,
                kb_c_2,
            ),
        ]

        for name, function, description, kb in commands_data:
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=kb,
                    laptop_keybinding=kb,
                )
            )

        msg = f"TABLE NAVIGATOR: Commands set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    @dbus_service.command
    def toggle_enabled(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles table navigation."""

        self._enabled = not self._enabled

        tokens = [
            "TABLE NAVIGATOR: toggle_enabled. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if notify_user:
            if self._enabled:
                presentation_manager.get_manager().present_message(
                    messages.TABLE_NAVIGATION_ENABLED
                )
            else:
                presentation_manager.get_manager().present_message(
                    messages.TABLE_NAVIGATION_DISABLED
                )

        self._last_input_event = None
        command_manager.get_manager().set_group_enabled(
            guilabels.KB_GROUP_TABLE_NAVIGATION, self._enabled
        )
        return True

    def suspend_commands(self, script: default.Script, suspended: bool, reason: str = "") -> None:
        """Suspends table navigation independent of the enabled setting."""

        if suspended == self._suspended:
            return

        msg = f"TABLE NAVIGATOR: Suspended: {suspended}"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._suspended = suspended
        command_manager.get_manager().set_group_suspended(
            guilabels.KB_GROUP_TABLE_NAVIGATION, suspended
        )

    def _is_blank(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is empty or consists of only whitespace."""

        if AXUtilities.is_focusable(obj):
            tokens = ["TABLE NAVIGATOR:", obj, "is not blank: it is focusable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXObject.get_name(obj):
            tokens = ["TABLE NAVIGATOR:", obj, "is not blank: it has a name"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXObject.get_child_count(obj):
            for child in AXObject.iter_children(obj):
                if not self._is_blank(child):
                    tokens = ["TABLE NAVIGATOR:", obj, "is not blank:", child, "is not blank"]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    return False
            return True

        if not AXText.is_whitespace_or_empty(obj):
            tokens = ["TABLE NAVIGATOR:", obj, "is not blank: it has text"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["TABLE NAVIGATOR: Treating", obj, "as blank"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return True

    def _get_current_cell(self) -> Atspi.Accessible:
        """Returns the current cell."""

        cell = focus_manager.get_manager().get_locus_of_focus()

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
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return cell

    def _get_cell_coordinates(self, cell: Atspi.Accessible) -> tuple:
        """Returns the coordinates of cell, possibly adjusted for linear movement."""

        row, col = AXTable.get_cell_coordinates(cell, prefer_attribute=False)
        if self._previous_reported_row is None or self._previous_reported_col is None:
            return row, col

        # If we're in a cell that spans multiple rows and/or columns, the coordinates will refer to
        # the upper left cell in the spanned range(s). We're storing the last row and column that
        # we presented in order to facilitate more linear movement. Therefore, if the cell at the
        # stored coordinates is the same as cell, we prefer the stored coordinates.
        last_cell = AXTable.get_cell_at(
            AXTable.get_table(cell), self._previous_reported_row, self._previous_reported_col
        )
        if last_cell == cell:
            return self._previous_reported_row, self._previous_reported_col

        return row, col

    @dbus_service.command
    def move_left(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the cell on the left."""

        tokens = [
            "TABLE NAVIGATOR: move_left. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_start_of_row(current):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_ROW_BEGINNING)
            return True

        row, col = self._get_cell_coordinates(current)
        cell = AXTable.get_cell_on_left(current)

        if self.get_skip_blank_cells():
            while cell and self._is_blank(cell) and not AXTable.is_start_of_row(cell):
                cell = AXTable.get_cell_on_left(cell)

        self._present_cell(script, cell, row, col - 1, current, notify_user)
        return True

    @dbus_service.command
    def move_right(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the cell on the right."""

        tokens = [
            "TABLE NAVIGATOR: move_right. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_end_of_row(current):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_ROW_END)
            return True

        row, col = self._get_cell_coordinates(current)
        cell = AXTable.get_cell_on_right(current)

        if self.get_skip_blank_cells():
            while cell and self._is_blank(cell) and not AXTable.is_end_of_row(cell):
                cell = AXTable.get_cell_on_right(cell)

        self._present_cell(script, cell, row, col + 1, current, notify_user)
        return True

    @dbus_service.command
    def move_up(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the cell above."""

        tokens = [
            "TABLE NAVIGATOR: move_up. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_top_of_column(current):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_COLUMN_TOP)
            return True

        row, col = self._get_cell_coordinates(current)
        cell = AXTable.get_cell_above(current)

        if self.get_skip_blank_cells():
            while cell and self._is_blank(cell) and not AXTable.is_top_of_column(cell):
                cell = AXTable.get_cell_above(cell)

        self._present_cell(script, cell, row - 1, col, current, notify_user)
        return True

    @dbus_service.command
    def move_down(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the cell below."""

        tokens = [
            "TABLE NAVIGATOR: move_down. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_bottom_of_column(current):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_COLUMN_BOTTOM)
            return True

        row, col = self._get_cell_coordinates(current)
        cell = AXTable.get_cell_below(current)

        if self.get_skip_blank_cells():
            while cell and self._is_blank(cell) and not AXTable.is_bottom_of_column(cell):
                cell = AXTable.get_cell_below(cell)

        self._present_cell(script, cell, row + 1, col, current, notify_user)
        return True

    @dbus_service.command
    def move_to_first_cell(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the first cell."""

        tokens = [
            "TABLE NAVIGATOR: move_to_first_cell. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(current)
        cell = AXTable.get_first_cell(table)
        self._present_cell(script, cell, 0, 0, current, notify_user)
        return True

    @dbus_service.command
    def move_to_last_cell(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the last cell."""

        tokens = [
            "TABLE NAVIGATOR: move_to_last_cell. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(current)
        cell = AXTable.get_last_cell(table)
        self._present_cell(
            script,
            cell,
            AXTable.get_row_count(table),
            AXTable.get_column_count(table),
            current,
            notify_user,
        )
        return True

    @dbus_service.command
    def move_to_beginning_of_row(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the beginning of the row."""

        tokens = [
            "TABLE NAVIGATOR: move_to_beginning_of_row. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_start_of_row(current):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_ROW_BEGINNING)
            return True

        cell = AXTable.get_start_of_row(current)
        row, col = self._get_cell_coordinates(cell)
        self._present_cell(script, cell, row, col, current, notify_user)
        return True

    @dbus_service.command
    def move_to_end_of_row(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the end of the row."""

        tokens = [
            "TABLE NAVIGATOR: move_to_end_of_row. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_end_of_row(current):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_ROW_END)
            return True

        cell = AXTable.get_end_of_row(current)
        row, col = self._get_cell_coordinates(cell)
        self._present_cell(script, cell, row, col, current, notify_user)
        return True

    @dbus_service.command
    def move_to_top_of_column(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the top of the column."""

        tokens = [
            "TABLE NAVIGATOR: move_to_top_of_column. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_top_of_column(current):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_COLUMN_TOP)
            return True

        row = self._get_cell_coordinates(current)[0]
        cell = AXTable.get_top_of_column(current)
        col = self._get_cell_coordinates(cell)[1]
        self._present_cell(script, cell, row, col, current, notify_user)
        return True

    @dbus_service.command
    def move_to_bottom_of_column(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Moves to the bottom of the column."""

        tokens = [
            "TABLE NAVIGATOR: move_to_bottom_of_column. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        if AXTable.is_bottom_of_column(current):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_COLUMN_BOTTOM)
            return True

        row = self._get_cell_coordinates(current)[0]
        cell = AXTable.get_bottom_of_column(current)
        col = self._get_cell_coordinates(cell)[1]
        self._present_cell(script, cell, row, col, current, notify_user)
        return True

    @dbus_service.command
    def set_dynamic_column_headers_row(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Sets the row for the dynamic header columns to the current row."""

        tokens = [
            "TABLE NAVIGATOR: set_dynamic_column_headers_row. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(current)
        if table:
            row = AXTable.get_cell_coordinates(current)[0]
            AXTable.set_dynamic_column_headers_row(table, row)
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.DYNAMIC_COLUMN_HEADER_SET % (row + 1)
                )

        return True

    @dbus_service.command
    def clear_dynamic_column_headers_row(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Clears the row for the dynamic column headers."""

        tokens = [
            "TABLE NAVIGATOR: clear_dynamic_column_headers_row. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(focus_manager.get_manager().get_locus_of_focus())
        if table:
            AXTable.clear_dynamic_column_headers_row(table)
            if notify_user:
                presentation_manager.get_manager().interrupt_presentation()
                presentation_manager.get_manager().present_message(
                    messages.DYNAMIC_COLUMN_HEADER_CLEARED
                )

        return True

    @dbus_service.command
    def set_dynamic_row_headers_column(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Sets the column for the dynamic row headers to the current column."""

        tokens = [
            "TABLE NAVIGATOR: set_dynamic_row_headers_column. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(current)
        if table:
            column = AXTable.get_cell_coordinates(current)[1]
            AXTable.set_dynamic_row_headers_column(table, column)
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.DYNAMIC_ROW_HEADER_SET
                    % script.utilities.convert_column_to_string(column + 1)
                )

        return True

    @dbus_service.command
    def clear_dynamic_row_headers_column(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Clears the column for the dynamic row headers."""

        tokens = [
            "TABLE NAVIGATOR: clear_dynamic_row_headers_column. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        current = self._get_current_cell()
        if current is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        table = AXTable.get_table(focus_manager.get_manager().get_locus_of_focus())
        if table:
            AXTable.clear_dynamic_row_headers_column(table)
            if notify_user:
                presentation_manager.get_manager().interrupt_presentation()
                presentation_manager.get_manager().present_message(
                    messages.DYNAMIC_ROW_HEADER_CLEARED
                )

        return True

    def _present_cell(
        self,
        script: default.Script,
        cell: Atspi.Accessible,
        row: int,
        col: int,
        previous_cell: Atspi.Accessible,
        notify_user: bool = True,
    ) -> None:
        """Presents cell to the user."""

        if not AXUtilities.is_table_cell_or_header(cell):
            tokens = ["TABLE NAVIGATOR: ", cell, f"(row {row}, column {col}) is not cell or header"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        self._previous_reported_row = row
        self._previous_reported_col = col

        if script.utilities.grab_focus_when_setting_caret(cell):
            AXObject.grab_focus(cell)

        obj = AXObject.find_descendant(cell, AXObject.supports_text) or cell
        focus_mgr = focus_manager.get_manager()
        focus_mgr.set_locus_of_focus(None, obj, False)
        focus_mgr.emit_region_changed(obj, mode=focus_manager.TABLE_NAVIGATOR)

        if AXObject.supports_text(obj) and not script.utilities.is_gui_cell(cell):
            script.utilities.set_caret_position(obj, 0)

        if not notify_user:
            msg = "TABLE NAVIGATOR: _present_cell called with notify_user=False"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        script.present_object(cell, offset=0, priorObj=previous_cell, interrupt=True)

        manager = speech_presenter.get_presenter()
        # TODO - JD: This should be part of the normal table cell presentation.
        if manager.get_announce_cell_coordinates():
            presentation_manager.get_manager().present_message(
                messages.TABLE_CELL_COORDINATES % {"row": row + 1, "column": col + 1}
            )

        # TODO - JD: Ditto.
        if manager.get_announce_cell_span():
            rowspan, colspan = AXTable.get_cell_spans(cell)
            if rowspan > 1 or colspan > 1:
                presentation_manager.get_manager().present_message(
                    messages.cell_span(rowspan, colspan)
                )

    @gsettings_registry.get_registry().gsetting(
        key="enabled",
        schema="table-navigation",
        gtype="b",
        default=True,
        summary="Enable table navigation",
        settings_key="tableNavigationEnabled",
    )
    @dbus_service.getter
    def get_is_enabled(self) -> bool:
        """Returns whether table navigation is enabled."""

        return settings.tableNavigationEnabled

    @dbus_service.setter
    def set_is_enabled(self, value: bool) -> bool:
        """Sets whether table navigation is enabled."""

        if self.get_is_enabled() == value:
            msg = f"TABLE NAVIGATOR: Enabled already {value}. Refreshing command group."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            command_manager.get_manager().set_group_enabled(
                guilabels.KB_GROUP_TABLE_NAVIGATION, value
            )
            return True

        msg = f"TABLE NAVIGATOR: Setting enabled to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.tableNavigationEnabled = value

        self._last_input_event = None
        command_manager.get_manager().set_group_enabled(guilabels.KB_GROUP_TABLE_NAVIGATION, value)

        return True

    @gsettings_registry.get_registry().gsetting(
        key="skip-blank-cells",
        schema="table-navigation",
        gtype="b",
        default=False,
        summary="Skip blank cells during navigation",
        settings_key="skipBlankCells",
    )
    @dbus_service.getter
    def get_skip_blank_cells(self) -> bool:
        """Returns whether blank cells should be skipped during navigation."""

        return settings.skipBlankCells

    @dbus_service.setter
    def set_skip_blank_cells(self, value: bool) -> bool:
        """Sets whether blank cells should be skipped during navigation."""

        if self.get_skip_blank_cells() == value:
            return True

        msg = f"TABLE NAVIGATOR: Setting skip blank cells to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.skipBlankCells = value
        return True


_navigator: TableNavigator = TableNavigator()


def get_navigator() -> TableNavigator:
    """Returns the Table Navigator"""

    return _navigator
