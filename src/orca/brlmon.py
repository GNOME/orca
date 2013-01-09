# -*- coding: utf-8 -*-
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

"""Provides a graphical braille display, mainly for development tasks."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

import brlapi
from gi.repository import Gtk

from . import orca_state
from .input_event import BrailleEvent

# Attribute/Selection mask strings:
#
DOT_7 =   '\x40' # 01000000
DOT_8 =   '\x80' # 10000000
DOTS_78 = '\xc0' # 11000000

class BrlDot(Gtk.Alignment):
    """A single braille dot."""

    MARKUP_NORMAL  = '<tt><small>%s</small></tt>'
    SYMBOL_LOWERED = '\u25CB' # '○'
    SYMBOL_RAISED  = '\u25CF' # '●'

    def __init__(self, dotNumber, isRaised=False):
        """Create a new BrlDot.

        Arguments:
        - dotNumber: an integer reflecting the location of the dot within
          an 8-dot braille cell, using traditional braille dot values.
        """

        Gtk.Alignment.__init__(self)
        if dotNumber in [1, 2, 3, 7]:
            self.set(1.0, 0.5, 0.0, 0.0)
            self.set_padding(0, 0, 3, 0)
        else:
            self.set(0.0, 0.5, 0.0, 0.0)
            self.set_padding(0, 0, 0, 3)

        self.label = Gtk.Label()
        self.add(self.label)
        if isRaised:
            self.raiseDot()
        else:
            self.lowerDot()

    def raiseDot(self):
        self.set(0.5, 0.5, 0, 0)
        self.label.set_markup(self.MARKUP_NORMAL % self.SYMBOL_RAISED)

    def lowerDot(self):
        self.set(0.5, 0.5, 0, 0)
        self.label.set_markup(self.MARKUP_NORMAL % self.SYMBOL_LOWERED)

class BrlCell(Gtk.Grid):
    """A single graphical braille cell with cursor routing capability."""

    MARKUP_NORMAL      = '<tt><big>%s</big></tt>'
    MARKUP_CURSOR_CELL = '<b><u>%s</u></b>'

    def __init__(self, position):
        """Create a new BrlCell.

        Arguments:
        - position: The location of the cell with respect to the monitor.
        """

        Gtk.Grid.__init__(self)
        self._position = position

        # For now, we display the char in print, like we always have. Use
        # (merge) dots 1-6 for this purpose. Also make the button a means
        # by which developers can work on cursor routing.
        self._displayedChar = Gtk.Button()
        self._displayedChar.set_size_request(30, 40)
        self._displayedChar.add(Gtk.Label())
        self.attach(self._displayedChar, 0, 0, 2, 3)
        self._displayedChar.connect("clicked", self._onCellClicked)

        # Create a more braille-like representation for dots 7-8 so that we
        # do not have to remember/guess what pango underline type goes with
        # what dot(s).
        self.dot7 = BrlDot(7)
        self.dot8 = BrlDot(8)
        self.attach(self.dot7, 0, 3, 1, 1)
        self.attach(self.dot8, 1, 3, 1, 1)

    def _onCellClicked(self, widget):
        """Callback for the 'clicked' signal on the push button. Synthesizes
        a fake brlapi command to route the cursor to the current cell, similar
        to what occurs when a user presses the cursor routing key on his/her
        hardware braille display."""

        if not orca_state.activeScript:
            return

        fakeKeyPress = {}
        fakeKeyPress['command'] = brlapi.KEY_CMD_ROUTE
        fakeKeyPress['argument'] = self._position
        event = BrailleEvent(fakeKeyPress)
        orca_state.activeScript.processRoutingKey(event)

    def clear(self):
        """Clears the braille cell."""

        try:
            label, = self._displayedChar.get_children()
        except ValueError:
            return

        label.set_markup("")
        self.dot7.lowerDot()
        self.dot8.lowerDot()

    def display(self, char, mask=None, isCursorCell=False):
        """Displays the specified character in the cell.

        Arguments:
        - char: The character to display in the cell.
        - isCursorCell: If True, the cursor/caret is at this cell and this
          should be indicated visually.
        """

        if char == '&':
            char = '&amp;'
        elif char == '<':
            char = '&lt;'
        elif char == '\t':
            char = '$t'

        markup = self.MARKUP_NORMAL
        if isCursorCell:
            markup = markup % self.MARKUP_CURSOR_CELL
        label, = self._displayedChar.get_children()
        label.set_markup(markup % char)

        if mask in [DOT_7, DOTS_78]:
            self.dot7.raiseDot()
        if mask in [DOT_8, DOTS_78]:
            self.dot8.raiseDot()

class BrlMon(Gtk.Window):
    """Displays a GUI braille monitor that mirrors what would be displayed
    by Orca on a connected, configured, and enabled braille display. Cursor
    routing functionality is emulated by each cell being a push button.
    Panning and other functionality found on hardware braille displays will
    be added."""

    def __init__(self, numCells=32):
        """Create a new BrlMon.

        Arguments:
        - numCells: how many braille cells to make
        """

        Gtk.Window.__init__(self)
        self.set_title("Braille Monitor")

        grid = Gtk.Grid()
        self.add(grid)

        self.cells = []
        for i in range(numCells):
            cell = BrlCell(i)
            grid.attach(cell, i, 0, 1, 1)
            self.cells.append(cell)

        self.set_resizable(False)
        self.set_property("accept-focus", False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

    def clear(self):
        """Clears the braille monitor display."""

        for cell in self.cells:
            cell.clear()

    def writeText(self, cursorCell, string, mask=None):
        """Display the given text and highlight the given
        cursor cell.  A cursorCell of 0 means no cell has
        the cursor.

        Arguments:
        - cursorCell: 1-based index of cell with cursor
        - string: len must be <= num cells.
        """

        self.clear()
        length = min(len(string), len(self.cells))
        for i in range(length):
            isCursorCell = i == cursorCell - 1
            try:
                cellMask = mask[i]
            except (IndexError, TypeError):
                cellMask = None
            self.cells[i].display(string[i], cellMask, isCursorCell)
