#
# Copyright 2008 Sun Microsystems Inc.
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

"""Provides a simple utility to draw outlines on the screen.
[[[TODO: WDW - The Wedge support is experimental and not perfect.]]]"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Sun Microsystems Inc."
__license__   = "LGPL"

import cairo

try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    import gtk
    display = gtk.gdk.display_get_default()
    screen = display.get_default_screen()
    screen_width = screen.get_width()
    screen_height = screen.get_height()
except:
    pass

import orca_state
import settings

def _adjustToScreen(x, y, width, height):
    if x < 0:
        width = width + x
        x = 0
    elif x >= screen_width:
        width -= (x - screen_width)
        x = screen_width
    if y < 0:
        height = height + y
        y = 0
    elif y >= screen_height:
        height -= (y - screen_height)
        y = screen_height
    if (x + width) >= screen_width:
        width = screen_width - x
    if (y + height) >= screen_height:
        height = max(1, screen_height - y)
    width = max(1, width)
    height = max(1, height)
    return [x, y, width, height]

# Our known windows that we've put on the screen.
#
_outlineWindows = []

class Line(gtk.Window):
    """Draws a simple filled box on the display using
    settings.outlineColor for the color.

    Arguments:
    - x, y, width, height: the dimensions of the box
    """
    def __init__(self, x, y, width, height):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.modify_bg(gtk.STATE_NORMAL,
                       gtk.gdk.Color(settings.outlineColor[0],
                                     settings.outlineColor[1],
                                     settings.outlineColor[2]))

        self.set_property("accept-focus", False)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)

        self.move(x, y)
        self.set_default_size(width, height)
        self.resize(width, height)
        self.realize()

class Wedge(Line):
    """Draws a filled isosceles triangle on the display
    using settings.outlineColor for the color.

    Arguments:
    - x, y, width, height - the bounding box of the triangle
    - top - if true, the triangle is flat on the bottom,
            if false, the triangle is pointy on the bottom
    """
    def __init__(self, x, y, width, height, top):
        self.top = top
        Line.__init__(self, x, y, width, height)
        self.connect('size-allocate', self._on_size_allocate)

    def _on_size_allocate(self, win, allocation):
        """Sets the shape of the window to a triangle."""
        # Create a bitmap to draw into.  This will be the mask
        # for the shape of the window.
        #
        width, height = allocation.width, allocation.height
        bitmap = gtk.gdk.Pixmap(None, width, height, 1)
        cr = bitmap.cairo_create()

        # Clear the bitmap
        #
        cr.set_source_rgb(0, 0, 0)
        cr.set_operator(cairo.OPERATOR_DEST_OUT)
        cr.paint()

        # Draw our shape into the bitmap using cairo
        #
        cr.set_operator(cairo.OPERATOR_OVER)
        if self.top:
            # In this case, height is the same as thickness
            #
            cr.move_to(width/2.0, 0.0)
            cr.line_to(width/2.0 + height/2.0, height)
            cr.line_to(width/2.0 - height/2.0, height)
        else:
            cr.move_to(width/2.0, height)
            cr.line_to(width/2.0 + height/2.0, 0.0)
            cr.line_to(width/2.0 - height/2.0, 0.0)
        cr.close_path()
        cr.fill()

        # Set the window shape
        #
        win.shape_combine_mask(bitmap, 0, 0)

class Box(Line):
    """Draws the outline of a rectangle on the display
    using settings.outlineColor for the color.

    Arguments:
    - x, y, width, height - the bounding box of the rectangle
    - thickness - the thickness of the border
    """
    def __init__(self, x, y, width, height, thickness):
        self.thickness = thickness
        Line.__init__(self, x, y, width, height)
        self.connect('size-allocate', self._on_size_allocate)

    def _on_size_allocate(self, win, allocation):
        """Sets the shape of the window to a hollow rectangle."""
        # Create a bitmap to draw into.  This will be the mask
        # for the shape of the window.
        #
        width, height = allocation.width, allocation.height
        bitmap = gtk.gdk.Pixmap(None, width, height, 1)
        cr = bitmap.cairo_create()

        # Clear the bitmap
        #
        cr.set_source_rgb(0, 0, 0)
        cr.set_operator(cairo.OPERATOR_DEST_OUT)
        cr.paint()

        # Draw our shape into the bitmap using cairo
        #
        cr.set_line_width(self.thickness)
        cr.set_operator(cairo.OPERATOR_OVER)
        offset = self.thickness / 2.0
        cr.rectangle(0.0 + offset, 0.0 + offset,
                     width - self.thickness, height - self.thickness)
        cr.stroke()

        # Set the window shape
        #
        win.shape_combine_mask(bitmap, 0, 0)

def reset():
    """Destroys all windows we have put on the screen."""
    global _outlineWindows
    for window in _outlineWindows:
        window.destroy()
    _outlineWindows = []
   
def erase():
    """Erases all windows we have put on the screen."""
    for window in _outlineWindows:
        window.hide()

def draw(x, y, width, height):
    """Draws an outline for the given rectangle.  This might
    be composed of multiple windows depending upon the
    settings.outlineStyle."""

    if settings.outlineStyle == settings.OUTLINE_NONE:
        pass
    elif settings.outlineStyle == settings.OUTLINE_LINE:
        y = y + height + settings.outlineMargin
        height = settings.outlineThickness
        [x, y, width, height] = _adjustToScreen(x, y, width, height)
        if not _outlineWindows:
            line = \
                Line(x, y, width, height)
            _outlineWindows.append(line)
        else:
            _outlineWindows[0].resize(width, height)
            _outlineWindows[0].move(x, y)
    elif settings.outlineStyle == settings.OUTLINE_BOX:
        extra = settings.outlineThickness + settings.outlineMargin
        x = x - extra
        y = y - extra
        width = width + (2 * extra)
        height = height + (2 * extra)
        [x, y, width, height] = _adjustToScreen(x, y, width, height)
        if not _outlineWindows:
            box = \
                Box(x, y, width, height,
                    settings.outlineThickness)
            _outlineWindows.append(box)
        else:
            _outlineWindows[0].resize(width, height)
            _outlineWindows[0].move(x, y)
    elif settings.outlineStyle == settings.OUTLINE_WEDGES:
        wedgeSize = 4 * settings.outlineThickness
        if width < wedgeSize:
            diff = wedgeSize - width
            width = wedgeSize
            x -= (diff/2)
        topy = y - (4 * settings.outlineThickness)
        bottomy = y + height + settings.outlineMargin
        [topx, topy, topwidth, topheight] = \
           _adjustToScreen(x, topy, width, wedgeSize)
        [bottomx, bottomy, bottomwidth, bottomheight] = \
           _adjustToScreen(x, bottomy, width, wedgeSize)
        if not _outlineWindows:
            top = \
                Wedge(topx, topy, topwidth, topheight, True)
            _outlineWindows.append(top)
            bottom = \
                Wedge(bottomx, bottomy, bottomwidth, bottomheight, False)
            _outlineWindows.append(bottom)
        else:
            _outlineWindows[0].resize(topwidth, topheight)
            _outlineWindows[0].move(topx, topy)
            _outlineWindows[1].resize(bottomwidth, bottomheight)
            _outlineWindows[1].move(bottomx, bottomy)

    for window in _outlineWindows:
        window.present()
        # Make sure the windows stay on top.
        #
        try:
            window.window.set_user_time(orca_state.lastInputEventTimestamp)
        except:
            pass
