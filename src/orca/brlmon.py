# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""Provides a graphical braille display at the top of the screen.
This is mainly for debugging and for demonstrations."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import gtk

# Attribute/Selection mask strings:
#
DOT_7 =   '\x40' # 01000000
DOT_8 =   '\x80' # 10000000
DOTS_78 = '\xc0' # 11000000
    
# Markup strings:
#
NORMAL = " size='xx-large'"

CURSOR_CELL_EMPTY =   " background='black'" \
                    + " weight='ultrabold'" \
                    + " style='italic'"

CURSOR_CELL =   " background='white'" \
              + " weight='ultrabold'" \
              + " style='italic'" \

ATTRIBUTE_7 = " underline='low'"

ATTRIBUTE_8 = " underline='error'"

ATTRIBUTE_78 = " underline='double'"

class BrlMon(gtk.Window):

    """Displays a GUI braille monitor that mirrors what is being
    shown on the braille display.  This currently needs a lot of
    work, but it is a start.  TODO's include doing a better job of
    docking it at the top of the display (e.g., make all other
    windows move out from underneath it), doing better highlighting of
    the cursor cell, allowing the font to be set, and perhaps allowing
    clicks to simulate cursor routing keys."""

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
        i = 0
        while (i < numCells):
            frame = gtk.Frame()
            frame.set_shadow_type(gtk.SHADOW_OUT)
            label = gtk.Label(" ")
            label.set_use_markup(True)
            frame.add(label)
            hbox.add(frame)
            self.cellFrames.append(frame)
            self.cellLabels.append(label)
            i += 1

        # This prevents it from getting focus.
        #
        self.set_property("accept-focus", False)
        self.connect_after("check-resize", self.onResize)

    def onResize(self, obj):
        """Tell the window to be a dock and set its struts, which I
        thinks means to attempt to glue it somewhere on the display.
        """

        # We know what we are doing here, so tell pylint not to flag
        # the self.window method calls as errors (e.g., Class 'window' 
        # has no 'get_size' member).  The disable-msg is localized to
        # just this method.
        #
        # pylint: disable-msg=E1101

        screen_width = gtk.gdk.screen_width()
        [window_width, window_height] = self.window.get_size()
        if window_width < screen_width:
            x = (screen_width - window_width) / 2
        else:
            x = 0

        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
        self.window.property_change(
                gtk.gdk.atom_intern("_NET_WM_STRUT_PARTIAL", False),
                gtk.gdk.atom_intern("CARDINAL", False), 32,
                gtk.gdk.PROP_MODE_REPLACE,
                [0,                     # LEFT
                 0,                     # RIGHT
                 window_height,         # TOP
                 0,                     # BOTTOM
                 0,                     # LEFT_START
                 0,                     # LEFT_END
                 0,                     # RIGHT_START
                 0,                     # RIGHT_END
                 0,                     # TOP_START
                 screen_width - 1,      # TOP_END
                 0,                     # BOTTOM_START
                 0])                    # BOTTOM_END

        self.move(x, 0)

    def writeText(self, cursorCell, string, mask=None):
        """Display the given text and highlight the given
        cursor cell.  A cursorCell of 0 means no cell has
        the cursor.

        Arguments:
        - cursorCell: 1-based index of cell with cursor
        - string: len must be <= num cells.
        """

        # Fill out the cells from the string.
        #
        try:
            string = string.decode("UTF-8")
        except:
            string = ""

        for i in range(0, len(string)):

            # Handle special chars so they are not interpreted by pango.
            #
            if string[i] == "<":
                char = "&lt;"
            elif string[i] == "&":
                char = "&amp;"
            elif string[i] == "\t":
                char = "$t"
            else:
                char = string[i]

            markup = NORMAL
            if i == (cursorCell - 1):
                if string[i] == " ":
                    markup += CURSOR_CELL_EMPTY
                else:
                    markup += CURSOR_CELL
                self.cellFrames[i].set_shadow_type(
                    gtk.SHADOW_IN)
            else:
                self.cellFrames[i].set_shadow_type(
                    gtk.SHADOW_OUT)

            try:
                if mask:
                    if (mask[i] == DOTS_78):
                        markup += ATTRIBUTE_78
                    elif (mask[i] == DOT_7):
                        markup += ATTRIBUTE_7
                    elif (mask[i] == DOT_8):
                        markup += ATTRIBUTE_8
            except:
                pass

            self.cellLabels[i].set_markup(
                "<span" + markup + ">%s</span>" % char)

        # Pad the rest
        #
        for i in range(len(string), len(self.cellFrames)):
            self.cellLabels[i].set_text(" ")
            self.cellFrames[i].set_shadow_type(
                gtk.SHADOW_OUT)
