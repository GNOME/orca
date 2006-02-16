# Orca
#
# Copyright 2006 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import gtk

class BrlMon(gtk.Window):
    """Displays a GUI braille monitor that mirrors what is being
    shown on the braille display.  This currently needs a lot of
    work, but it is a start.  TODO's include removing decorations,
    preventing this from getting focus, docking it at the top of
    the display, doing better highlighting of the cursor cell,
    allowing the font to be set, and perhaps allowing clicks to 
    simulate cursor routing keys."""

    def __init__(self, numCells=32, cellWidth=25, cellHeight=50):
	"""Create a new BrlMon.

	Arguments:
	- numCells: how many braille cells to make
	- cellWidth: width of each cell in pixels
 	- cellHeight: height of each cell in pixels
        """

	gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
	self.set_title("Braille Monitor")
	self.set_default_size(cellWidth * numCells, cellHeight)
	hbox = gtk.HBox(True)
	self.add(hbox)
	self.cellFrames = []
	self.cellLabels = []
	for i in range(0, numCells):
	    frame = gtk.Frame()
	    frame.set_shadow_type(gtk.SHADOW_OUT)
	    label = gtk.Label(" ")
	    frame.add(label)
	    hbox.add(frame)
	    self.cellFrames.append(frame)
	    self.cellLabels.append(label)

    def writeText(self, cursorCell, string):
        """Display the given text and highlight the given
        cursor cell.  A cursorCell of 0 means no cell has
	the cursor.

	Arguments:
	- cursorCell: 1-based index of cell with cursor
	- string: len must be <= num cells.
	"""

	# Fill out the cells from the string.
	#
	for i in range(0, len(string)):
	    self.cellLabels[i].set_text(string[i])
 	    self.cellFrames[i].set_shadow_type(
		gtk.SHADOW_OUT)

	# Pad the rest
	#
	for i in range(len(string), len(self.cellFrames)):
	    self.cellLabels[i].set_text(" ")
 	    self.cellFrames[i].set_shadow_type(
		gtk.SHADOW_OUT)

	# Highlight the cursor cell.
	#
	if cursorCell:
 	    self.cellFrames[cursorCell - 1].set_shadow_type(
		gtk.SHADOW_IN)
