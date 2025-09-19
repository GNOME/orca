# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
# Copyright 2011 The Orca Team.
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

# pylint: disable=wrong-import-position

"""Provides a graphical braille display, mainly for development tasks."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2008 Sun Microsystems Inc." \
                "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

try:
    from brlapi import KEY_CMD_ROUTE
except ImportError:
    KEY_CMD_ROUTE = None

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import script_manager
from .input_event import BrailleEvent

# Attribute/Selection mask strings:
DOT_7 =   "\x40" # 01000000
DOT_8 =   "\x80" # 10000000
DOTS_78 = "\xc0" # 11000000

class BrlDot(Gtk.Alignment):
    """A single braille dot."""

    MARKUP_NORMAL  = "<tt><small>%s</small></tt>"
    SYMBOL_LOWERED = "\u25CB" # "○"
    SYMBOL_RAISED  = "\u25CF" # "●"

    def __init__(self, dot_number: int, is_raised: bool = False) -> None:
        """Create a new BrlDot.

        Arguments:
        - dot_number: an integer reflecting the location of the dot within
          an 8-dot braille cell, using traditional braille dot values.
        - is_raised: whether the dot should initially be raised.
        """

        super().__init__()
        if dot_number in [1, 2, 3, 7]:
            self.set(1.0, 0.5, 0.0, 0.0)
            self.set_padding(3, 0, 0, 3)
        else:
            self.set(0.0, 0.5, 0.0, 0.0)
            self.set_padding(3, 0, 3, 0)

        self.label = Gtk.Label()
        self.add(self.label)
        if is_raised:
            self.raise_dot()
        else:
            self.lower_dot()

    def raise_dot(self) -> None:
        """Raise the dot (make it visible/filled)."""
        self.set(0.5, 0.5, 0, 0)
        self.label.set_markup(self.MARKUP_NORMAL % self.SYMBOL_RAISED)

    def lower_dot(self) -> None:
        """Lower the dot (make it invisible/empty)."""
        self.set(0.5, 0.5, 0, 0)
        self.label.set_markup(self.MARKUP_NORMAL % self.SYMBOL_LOWERED)

class BrlCell(Gtk.Button):
    """A single graphical braille cell with cursor routing capability."""

    MARKUP_NORMAL      = "<tt><big>%s</big></tt>"
    MARKUP_CURSOR_CELL = "<b><u>%s</u></b>"

    def __init__(self, position: int) -> None:
        """Create a new BrlCell.

        Arguments:
        - position: The location of the cell with respect to the monitor.
        """

        super().__init__()
        self.set_size_request(30, 45)
        self._position = position
        self._displayed_char = Gtk.Label()
        self._dot7 = BrlDot(7)
        self._dot8 = BrlDot(8)

        grid = Gtk.Grid()
        grid.attach(self._displayed_char, 0, 0, 2, 3)
        grid.attach(self._dot7, 0, 3, 1, 1)
        grid.attach(self._dot8, 1, 3, 1, 1)
        self.add(grid)

        self.connect("clicked", self._on_cell_clicked)

    def _on_cell_clicked(self, _widget: Gtk.Button) -> None:
        """Callback for the 'clicked' signal on the push button."""

        if KEY_CMD_ROUTE is None:
            return

        script = script_manager.get_manager().get_active_script()
        if script is None:
            return

        fake_key_press = {}
        fake_key_press["command"] = KEY_CMD_ROUTE
        fake_key_press["argument"] = self._position
        event = BrailleEvent(fake_key_press)
        script.process_routing_key(event)

    def clear(self) -> None:
        """Clears the braille cell."""

        self._displayed_char.set_markup("")
        self._dot7.lower_dot()
        self._dot8.lower_dot()

    def display(self, char: str, mask: str | None = None, is_cursor_cell: bool = False) -> None:
        """Displays the specified character in the cell.

        Arguments:
        - char: The character to display in the cell.
        - mask: Optional mask for displaying attributes.
        - is_cursor_cell: If True, the cursor/caret is at this cell.
        """

        if char == "&":
            char = "&amp;"
        elif char == "<":
            char = "&lt;"
        elif char == "\t":
            char = "$t"

        markup = self.MARKUP_NORMAL
        if is_cursor_cell:
            markup = markup % self.MARKUP_CURSOR_CELL
        self._displayed_char.set_markup(markup % char)

        if mask in [DOT_7, DOTS_78]:
            self._dot7.raise_dot()
        if mask in [DOT_8, DOTS_78]:
            self._dot8.raise_dot()

class BrlMon(Gtk.Window):
    """Displays a GUI braille monitor that mirrors what would be displayed
    by Orca on a connected, configured, and enabled braille display."""

    def __init__(self, num_cells: int = 32) -> None:
        """Create a new BrlMon.

        Arguments:
        - num_cells: how many braille cells to make
        """

        super().__init__()
        self.set_title("Braille Monitor")

        grid = Gtk.Grid()
        self.add(grid)

        self.cells: list[BrlCell] = []
        for i in range(num_cells):
            cell = BrlCell(i)
            grid.attach(cell, i, 0, 1, 1)
            self.cells.append(cell)

        self.set_resizable(False)
        self.set_property("accept-focus", False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

    def clear(self) -> None:
        """Clears the braille monitor display."""

        for cell in self.cells:
            cell.clear()

    def write_text(self, cursor_cell: int, string: str, mask: str | None = None) -> None:
        """Display the given text and highlight the given cursor cell.

        Arguments:
        - cursor_cell: 1-based index of cell with cursor (0 means no cursor)
        - string: text to display (length must be <= num cells)
        - mask: optional attribute mask
        """

        self.clear()
        length = min(len(string), len(self.cells))
        for i in range(length):
            is_cursor_cell = i == cursor_cell - 1
            try:
                cell_mask = mask[i] if mask else None
            except (IndexError, TypeError):
                cell_mask = None
            self.cells[i].display(string[i], cell_mask, is_cursor_cell)
