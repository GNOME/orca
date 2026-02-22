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

# pylint: disable=too-many-arguments

"""Module for drawing highlights over an area of interest."""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from . import debug

try:
    import cairo
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    CAIRO_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as error:
    tokens = ["HIGHLIGHTER: GtkHighlighter unavailable:", error]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
    CAIRO_AVAILABLE = False

if TYPE_CHECKING:
    from typing import Any

    if CAIRO_AVAILABLE:
        from gi.repository import Gtk as GtkType
    else:
        GtkType = Any


class HighlightColor(NamedTuple):
    """An RGBA color for use with highlighters."""

    red: float
    green: float
    blue: float
    alpha: float = 1.0


class Highlighter:
    """Base class of all highlighters supported by Orca."""

    HIGHLIGHT = "highlight"
    RECTANGLE = "rectangle"
    UNDERLINE = "underline"

    RED = HighlightColor(1, 0, 0)
    BLUE = HighlightColor(0, 0, 1)
    GREEN = HighlightColor(0, 1, 0)
    YELLOW = HighlightColor(1, 1, 0)
    PURPLE = HighlightColor(0.5, 0, 0.5)
    ORANGE = HighlightColor(1, 0.5, 0)
    PINK = HighlightColor(1, 0.75, 0.8)
    CYAN = HighlightColor(0, 1, 1)
    MAGENTA = HighlightColor(1, 0, 1)
    LIME = HighlightColor(0.5, 1, 0)
    NAVY = HighlightColor(0, 0, 0.5)
    TEAL = HighlightColor(0, 0.5, 0.5)
    BLACK = HighlightColor(0, 0, 0)
    WHITE = HighlightColor(1, 1, 1)

    def __init__(
        self,
        highlight_type: str,
        color: HighlightColor,
        thickness: int,
        padding: int,
        *,
        fill_color: HighlightColor | None = None,
    ) -> None:
        self._highlight_type = highlight_type
        self._color = color
        self._thickness = thickness
        self._padding = padding
        self._fill_color = fill_color
        self._gui = self._create_gui()  # pylint: disable=assignment-from-none

    def _create_gui(self) -> Any:
        """Creates the gui for the overlay."""

        return None

    def _draw_highlight(self, painter: Any) -> None:
        """Called by highlight to draw a highlight over the item."""

    def _draw_rectangle(self, painter: Any) -> None:
        """Called by highlight to draw a rectangle around the item."""

    def _draw_underline(self, painter: Any) -> None:
        """Called by highlight to draw an underline under the item."""

    def highlight(self, x: int, y: int, width: int, height: int) -> None:
        """Draws the desired indicator over the specified box."""

    def quit(self) -> None:
        """Quits the highlighter."""


class GtkHighlighter(Highlighter):
    """Highlighter that uses a GtkWindow to highlight items."""

    def __init__(
        self,
        highlight_type: str = Highlighter.UNDERLINE,
        color: HighlightColor = Highlighter.GREEN,
        thickness: int = 5,
        padding: int = 5,
        *,
        fill_color: HighlightColor | None = None,
    ) -> None:
        if not CAIRO_AVAILABLE:
            msg = "GTK HIGHLIGHTER: Unavailable. Is Cairo installed?"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        super().__init__(highlight_type, color, thickness, padding, fill_color=fill_color)
        self._drawing_area: Any = None

    def _create_gui(self) -> Any:
        """Creates the gui for the overlay."""

        # pylint: disable=no-member
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

    def _on_draw(self, _widget: Any, painter: Any) -> None:
        """Signal handler for the 'draw' event."""

        if self._highlight_type == self.HIGHLIGHT:
            self._draw_highlight(painter)
        elif self._highlight_type == self.RECTANGLE:
            self._draw_rectangle(painter)
        elif self._highlight_type == self.UNDERLINE:
            self._draw_underline(painter)

    def _draw_highlight(self, painter: Any) -> None:
        """Called by highlight to draw a highlight over the item."""

        fill = self._fill_color or HighlightColor(1, 1, 0, 0.3)
        painter.set_source_rgba(*fill)
        painter.set_operator(cairo.OPERATOR_SOURCE)  # pylint: disable=no-member
        painter.paint()
        painter.set_operator(cairo.OPERATOR_OVER)  # pylint: disable=no-member

    def _draw_rectangle(self, painter: Any) -> None:
        """Called by highlight to draw a rectangle around the item."""

        x = self._padding
        y = self._padding
        width = self._gui.get_allocated_width() - 2 * self._padding
        height = self._gui.get_allocated_height() - 2 * self._padding

        if self._fill_color is not None:
            painter.set_source_rgba(*self._fill_color)
            painter.rectangle(x, y, width, height)
            painter.fill()

        painter.set_source_rgba(*self._color)
        painter.set_line_width(self._thickness)
        painter.rectangle(x, y, width, height)
        painter.stroke()

    def _draw_underline(self, painter: Any) -> None:
        """Called by highlight to draw an underline under the item."""

        painter.set_source_rgba(*self._color)
        painter.set_line_width(self._thickness)
        painter.move_to(0, self._gui.get_allocated_height() - 5)
        painter.line_to(self._gui.get_allocated_width(), self._gui.get_allocated_height() - 5)
        painter.stroke()

    def highlight(self, x: int, y: int, width: int, height: int) -> None:
        """Draws the desired indicator over the specified box."""

        msg = f"GTK HIGHLIGHTER: x:{x}, y:{y}, width:{width}, height:{height}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        try:
            self._gui.move(x - self._padding, y - self._padding)
            self._gui.resize(width + 2 * self._padding, height + 2 * self._padding)
        except (ValueError, TypeError, AttributeError, RuntimeError) as exc:
            error_tokens = ["GTK HIGHLIGHTER: Exception:", exc]
            debug.print_tokens(debug.LEVEL_INFO, error_tokens, True)
        else:
            self._gui.show_all()

    def quit(self) -> None:
        """Quits the highlighter."""

        msg = "GTK HIGHLIGHTER: Quitting."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._gui.destroy()
        self._drawing_area = None
        self._gui = None
