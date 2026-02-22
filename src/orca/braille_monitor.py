# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

from __future__ import annotations

import os
from typing import TYPE_CHECKING

try:
    from brlapi import KEY_CMD_ROUTE
except ImportError:
    KEY_CMD_ROUTE = None

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from . import guilabels, script_manager

if TYPE_CHECKING:
    from collections.abc import Callable

# Attribute/Selection mask strings:
DOT_7 = "\x40"  # 01000000
DOT_8 = "\x80"  # 10000000
DOTS_78 = "\xc0"  # 11000000


# pylint: disable-next=no-member
class BrailleDot(Gtk.Alignment):
    """A single braille dot."""

    MARKUP_NORMAL = "<tt><small>%s</small></tt>"
    SYMBOL_LOWERED = "\u25cb"  # "○"
    SYMBOL_RAISED = "\u25cf"  # "●"

    def __init__(self, dot_number: int, is_raised: bool = False) -> None:
        """Create a new BrailleDot.

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


class BrailleCell(Gtk.Button):
    """A single graphical braille cell with cursor routing capability."""

    MARKUP_NORMAL = "<tt><span size='x-large'><b>%s</b></span></tt>"
    MARKUP_BRAILLE = "<tt><span size='xx-large'><b>%s</b></span></tt>"
    MARKUP_CURSOR_CELL = "<u>%s</u>"

    def __init__(self, position: int) -> None:
        """Create a new BrailleCell.

        Arguments:
        - position: The location of the cell with respect to the monitor.
        """

        super().__init__()
        self.get_style_context().add_class("braille-cell")
        self.set_size_request(36, 52)
        self._position = position
        self._displayed_char = Gtk.Label()
        self._displayed_char.set_valign(Gtk.Align.END)
        self._dot7 = BrailleDot(7)
        self._dot8 = BrailleDot(8)

        grid = Gtk.Grid()
        grid.attach(self._displayed_char, 0, 0, 2, 3)
        grid.attach(self._dot7, 0, 3, 1, 1)
        grid.attach(self._dot8, 1, 3, 1, 1)
        self.add(grid)  # pylint: disable=no-member

        self.connect("clicked", self._on_cell_clicked)

    def _on_cell_clicked(self, _widget: Gtk.Button) -> None:
        """Callback for the 'clicked' signal on the push button."""

        if KEY_CMD_ROUTE is None:
            return

        script = script_manager.get_manager().get_active_script()
        if script is None:
            return

        # pylint: disable=import-outside-toplevel
        from . import input_event

        fake_key_press = {}
        fake_key_press["command"] = KEY_CMD_ROUTE
        fake_key_press["argument"] = self._position
        event = input_event.BrailleEvent(fake_key_press)
        script.process_routing_key(None, event)

    def clear(self) -> None:
        """Clears the braille cell."""

        self._displayed_char.set_markup(self.MARKUP_NORMAL % " ")
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

        is_braille = len(char) == 1 and 0x2800 <= ord(char) <= 0x28FF
        markup = self.MARKUP_BRAILLE if is_braille else self.MARKUP_NORMAL
        if is_cursor_cell:
            markup = markup % self.MARKUP_CURSOR_CELL
        self._displayed_char.set_markup(markup % char)

        if mask in [DOT_7, DOTS_78]:
            self._dot7.raise_dot()
        if mask in [DOT_8, DOTS_78]:
            self._dot8.raise_dot()


class BrailleMonitor(Gtk.Window):
    """Displays a GUI braille monitor that mirrors what would be displayed
    by Orca on a connected, configured, and enabled braille display."""

    _shared_css_provider: Gtk.CssProvider | None = None

    def __init__(
        self,
        num_cells: int = 32,
        on_close: Callable[[], None] | None = None,
        foreground: str = "#000000",
        background: str = "#ffffff",
    ) -> None:
        """Create a new BrailleMonitor."""

        # pylint: disable=no-member

        super().__init__()
        self._on_close = on_close
        self._foreground = foreground
        self._background = background
        self.set_title(guilabels.BRAILLE_MONITOR)
        self.set_icon_name("orca")

        titlebar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title_label = Gtk.Label(label=guilabels.BRAILLE_MONITOR)
        titlebar.set_center_widget(title_label)
        close_btn = Gtk.Button.new_from_icon_name(
            "window-close-symbolic",
            Gtk.IconSize.LARGE_TOOLBAR,
        )
        close_btn.set_relief(Gtk.ReliefStyle.NONE)
        close_btn.connect("clicked", self._on_close_clicked)
        titlebar.pack_end(close_btn, False, False, 0)
        self.set_titlebar(titlebar)

        self.get_style_context().add_class("braille-monitor")
        titlebar.get_style_context().add_class("braille-monitor-titlebar")
        title_label.get_style_context().add_class("braille-monitor-title")
        close_btn.get_style_context().add_class("braille-monitor-close")

        cell_box = Gtk.Grid()
        self.add(cell_box)
        if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
            cell_box.set_sensitive(False)

        self.cells: list[BrailleCell] = []
        for i in range(num_cells):
            cell = BrailleCell(i)
            cell_box.attach(cell, i, 0, 1, 1)
            self.cells.append(cell)

        if BrailleMonitor._shared_css_provider is None:
            BrailleMonitor._shared_css_provider = Gtk.CssProvider()
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                BrailleMonitor._shared_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
        self._apply_css()

        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_property("accept-focus", False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        self.connect("delete-event", self._on_delete_event)

    def reapply_css(
        self,
        foreground: str | None = None,
        background: str | None = None,
    ) -> None:
        """Reapplies CSS styling (e.g. after color changes)."""

        if foreground is not None:
            self._foreground = foreground
        if background is not None:
            self._background = background
        self._apply_css()

    def _apply_css(self) -> None:
        """Apply CSS styling for colors and minimal titlebar."""

        bg = self._background
        fg = self._foreground
        css = (
            f".braille-monitor {{ background-color: {bg}; }}\n"
            f".braille-monitor-titlebar {{ min-height: 0; padding: 0; margin: 0; "
            f"background-color: {bg}; border: none; box-shadow: none; }}\n"
            f".braille-monitor-title {{ color: {fg}; font-size: small; font-weight: bold; }}\n"
            f".braille-monitor-close {{ min-height: 16px; min-width: 16px; "
            f"padding: 2px; margin: 0; color: {fg}; }}\n"
            f".braille-monitor-close:hover {{ opacity: 0.7; }}\n"
            f".braille-monitor .braille-cell {{ "
            f"background: {bg}; color: {fg}; border-color: {fg}; }}\n"
            f".braille-monitor .braille-cell label {{ color: {fg}; }}"
        )
        if BrailleMonitor._shared_css_provider is not None:
            BrailleMonitor._shared_css_provider.load_from_data(css.encode())

    def _on_close_clicked(self, _button: Gtk.Button) -> None:
        """Handle the close button click."""

        if self._on_close is not None:
            self._on_close()

    def _on_delete_event(self, _window: Gtk.Window, _event: Gdk.Event) -> bool:
        """Intercept the close request to toggle the monitor off."""

        if self._on_close is not None:
            self._on_close()
        return True

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
