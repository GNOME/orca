# Orca
#
# Copyright 2023 Igalia, S.L.
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

"""Module for drawing highlights over an area of interest."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

from . import debug

try:
    import cairo
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    CAIRO_AVAILABLE = True
except Exception as error:
    msg = f"HIGHLIGHTER: GtkHighlighter unavailable: {error}"
    debug.println(debug.LEVEL_INFO, msg, True)
    CAIRO_AVAILABLE = False

class Highlighter:
    """Base class of all highlighters supported by Orca."""

    HIGHLIGHT = "highlight"
    RECTANGLE = "rectangle"
    UNDERLINE = "underline"

    RED = (1, 0, 0)
    BLUE = (0, 0, 1)
    GREEN = (0, 1, 0)
    YELLOW = (1, 1, 0)
    PURPLE = (0.5, 0, 0.5)
    ORANGE = (1, 0.5, 0)
    PINK = (1, 0.75, 0.8)
    CYAN = (0, 1, 1)
    MAGENTA = (1, 0, 1)
    LIME = (0.5, 1, 0)
    NAVY = (0, 0, 0.5)
    TEAL = (0, 0.5, 0.5)
    BLACK = (0, 0, 0)
    WHITE = (1, 1, 1)

    def __init__(self, highlight_type, color, alpha, thickness, padding, fill_color, fill_alpha):
        self._highlight_type = highlight_type
        self._color = color
        self._alpha = alpha
        self._thickness = thickness
        self._padding = padding
        self._fill_color = fill_color
        self._fill_alpha = fill_alpha
        self._gui = self._create_gui()

    def _create_gui(self):
        """Creates the gui for the overlay."""
        return None

    def _draw_highlight(self, painter):
        """Called by highlight to draw a highlight over the item."""
        pass

    def _draw_rectangle(self, painter):
        """Called by highlight to draw a rectangle around the item."""
        pass

    def _draw_underline(self, painter):
        """Called by highlight to draw an underline under the item."""
        pass

    def highlight(self, x, y, width, height):
        """Draws the desired indicator over the specified box."""
        pass

    def quit(self):
        """Quits the highlighter."""
        pass


class GtkHighlighter(Highlighter):
    """Highlighter that uses a GtkWindow to highlight items."""

    def __init__(self,
                 highlight_type=Highlighter.UNDERLINE,
                 color=Highlighter.GREEN,
                 alpha=1.0,
                 thickness=5,
                 padding=5,
                 fill_color=None,
                 fill_alpha=None):
        if not CAIRO_AVAILABLE:
            msg = "GTK HIGHLIGHTER: Unavailable. Is Cairo installed?"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        super().__init__(highlight_type, color, alpha, thickness, padding, fill_color, fill_alpha)
        self._drawing_area = None

    def _create_gui(self):
        """Creates the gui for the overlay."""

        gui = Gtk.Window()
        gui.set_decorated(False)
        gui.set_accept_focus(False)
        gui.set_app_paintable(True)
        gui.set_skip_taskbar_hint(True)
        gui.set_skip_pager_hint(True)

        screen = gui.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            gui.set_visual(visual)

        self._drawing_area = Gtk.DrawingArea()
        self._drawing_area.connect("draw", self._on_draw)
        gui.add(self._drawing_area)
        return gui

    def _on_draw(self, widget, painter):
        """Signal handler for the 'draw' event."""

        if self._highlight_type == self.HIGHLIGHT:
            self._draw_highlight(painter)
        elif self._highlight_type == self.RECTANGLE:
            self._draw_rectangle(painter)
        elif self._highlight_type == self.UNDERLINE:
            self._draw_underline(painter)

    def _draw_highlight(self, painter):
        """Called by highlight to draw a highlight over the item."""

        if self._fill_color is None:
            self._fill_color = self.YELLOW
        if self._fill_alpha is None:
            self._fill_alpha = 0.3

        fill = (*self._fill_color, self._fill_alpha)
        painter.set_source_rgba(*fill)
        painter.set_operator(cairo.OPERATOR_SOURCE)
        painter.paint()
        painter.set_operator(cairo.OPERATOR_OVER)

    def _draw_rectangle(self, painter):
        """Called by highlight to draw a rectangle around the item."""

        x = self._padding
        y = self._padding
        width = self._gui.get_allocated_width() - 2 * self._padding
        height = self._gui.get_allocated_height() - 2 * self._padding

        if self._fill_color is not None and self._fill_alpha is not None:
            fill = (*self._fill_color, self._fill_alpha * 255)
            painter.set_source_rgba(*fill)
            painter.rectangle(x, y, width, height)
            painter.fill()

        line = (*self._color, self._alpha)
        painter.set_source_rgba(*line)
        painter.set_line_width(self._thickness)
        painter.rectangle(x, y, width, height)
        painter.stroke()

    def _draw_underline(self, painter):
        """Called by highlight to draw an underline under the item."""

        line = (*self._color, self._alpha)
        painter.set_source_rgba(*line)
        painter.set_line_width(self._thickness)
        painter.move_to(0, self._gui.get_allocated_height() - 5)
        painter.line_to(self._gui.get_allocated_width(), self._gui.get_allocated_height() - 5)
        painter.stroke()

    def highlight(self, x, y, width, height):
        """Draws the desired indicator over the specified box."""

        msg = "GTK HIGHLIGHTER: x:%i, y:%i, width:%i, height:%i" % (x, y, width, height)
        debug.println(debug.LEVEL_INFO, msg, True)

        try:
            self._gui.move(x - self._padding, y - self._padding)
            self._gui.resize(width + 2 * self._padding, height + 2 * self._padding)
        except Exception as error:
            msg = f"GTK HIGHLIGHTER: Exception: {error}"
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            self._gui.show_all()

    def quit(self):
        """Quits the highlighter."""

        msg = "GTK HIGHLIGHTER: Quitting."
        debug.println(debug.LEVEL_INFO, msg, True)
        self._gui.destroy()
        self._drawing_area = None
        self._gui = None
