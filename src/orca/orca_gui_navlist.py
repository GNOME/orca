# Orca
#
# Copyright 2012 Igalia, S.L.
#
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

# pylint: disable=wrong-import-position
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals

"""Displays a GUI for Orca navigation list dialogs"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2012 Igalia, S.L."
__license__   = "LGPL"

import time
from typing import TYPE_CHECKING, Any

import gi
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk

from . import debug
from . import guilabels
from . import script_manager
from .ax_event_synthesizer import AXEventSynthesizer
from .ax_object import AXObject

if TYPE_CHECKING:
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class OrcaNavListGUI:
    """A GUI for displaying navigation lists in Orca."""

    def __init__(
        self,
        title: str,
        column_headers: list[str],
        rows: list[tuple[Any, ...]],
        selected_row: int
    ) -> None:
        """Initialize the navigation list GUI."""
        self._tree: Gtk.TreeView | None = None
        self._activate_button: Gtk.Button | None = None
        self._jump_to_button: Gtk.Button | None = None
        self._gui: Gtk.Dialog = self._create_nav_list_dialog(column_headers, rows, selected_row)
        self._gui.set_title(title)
        self._gui.set_modal(True)
        self._gui.set_keep_above(True) # pylint: disable=no-member
        self._gui.set_focus_on_map(True) # pylint: disable=no-member
        self._gui.set_accept_focus(True) # pylint: disable=no-member
        self._script: default.Script | None = script_manager.get_manager().get_active_script()
        self._document: Atspi.Accessible | None = None

    def _create_nav_list_dialog(
        self,
        column_headers: list[str],
        rows: list[tuple[Any, ...]],
        selected_row: int
    ) -> Gtk.Dialog:
        """Create the navigation list dialog."""
        dialog = Gtk.Dialog()
        dialog.set_default_size(500, 400)

        grid = Gtk.Grid()
        content_area = dialog.get_content_area()
        content_area.add(grid)

        scrolled_window = Gtk.ScrolledWindow()
        grid.add(scrolled_window) # pylint: disable=no-member

        self._tree = Gtk.TreeView()
        self._tree.set_hexpand(True)
        self._tree.set_vexpand(True)
        scrolled_window.add(self._tree) # pylint: disable=no-member

        cols: list[type] = [GObject.TYPE_OBJECT, GObject.TYPE_INT]
        cols.extend(len(column_headers) * [GObject.TYPE_STRING])
        model = Gtk.ListStore(*cols)

        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Accessible", cell, text=0)
        column.set_visible(False)
        self._tree.append_column(column)

        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("offset", cell, text=1)
        column.set_visible(False)
        self._tree.append_column(column)

        for i, header in enumerate(column_headers):
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(header, cell, text=i + 2)
            column.set_sort_column_id(i + 2)
            self._tree.append_column(column)

        for row in rows:
            row_iter = model.append(None)
            for i, cell_value in enumerate(row):
                model.set_value(row_iter, i, cell_value)

        self._tree.set_model(model)
        selection = self._tree.get_selection()
        selection.select_path(selected_row)

        btn = dialog.add_button(guilabels.BTN_CANCEL, Gtk.ResponseType.CANCEL)
        btn.connect("clicked", self._on_cancel_clicked)

        self._jump_to_button = dialog.add_button(guilabels.BTN_JUMP_TO, Gtk.ResponseType.APPLY)
        self._jump_to_button.connect("clicked", self._on_jump_to_clicked)

        self._activate_button = dialog.add_button(guilabels.ACTIVATE, Gtk.ResponseType.OK)
        self._activate_button.connect("clicked", self._on_activate_clicked)
        self._activate_button.grab_default()

        self._tree.connect("key-release-event", self._on_key_release)
        self._tree.connect("cursor-changed", self._on_cursor_changed)
        self._tree.set_search_column(2)

        return dialog

    def show_gui(self) -> None:
        """Show the navigation list GUI."""
        self._gui.show_all() # pylint: disable=no-member
        self._gui.present_with_time(time.time())

    def _on_cursor_changed(self, _widget: Gtk.Widget) -> None:
        """Handle cursor change events in the tree view."""
        obj, _offset = self._get_selected_accessible_and_offset()
        n_actions = AXObject.get_n_actions(obj)
        if self._activate_button is not None:
            self._activate_button.set_sensitive(n_actions > 0)
            if n_actions > 0:
                self._activate_button.grab_default()
            elif self._jump_to_button is not None:
                self._jump_to_button.grab_default()

    def _on_key_release(self, _widget: Gtk.Widget, event: Gdk.EventKey) -> None:
        """Handle key release events in the tree view."""
        keycode = event.hardware_keycode
        keymap = Gdk.Keymap.get_default()
        entries_for_keycode = keymap.get_entries_for_keycode(keycode)
        entries = entries_for_keycode[-1]
        event_string = Gdk.keyval_name(entries[0])
        if event_string == "Return":
            self._gui.activate_default()

    def _on_cancel_clicked(self, _widget: Gtk.Widget) -> None:
        """Handle cancel button click."""
        self._gui.destroy()

    def _on_jump_to_clicked(self, _widget: Gtk.Widget) -> None:
        """Handle jump to button click."""
        obj, offset = self._get_selected_accessible_and_offset()
        self._gui.destroy()
        if self._script is not None:
            self._script.utilities.set_caret_position(obj, offset, self._document)

    def _on_activate_clicked(self, _widget: Gtk.Widget) -> None:
        """Handle activate button click."""
        obj, offset = self._get_selected_accessible_and_offset()
        self._gui.destroy()
        if not obj:
            return

        if self._script is not None:
            self._script.utilities.set_caret_position(obj, offset)
        if not AXEventSynthesizer.try_all_clickable_actions(obj):
            tokens = ["INFO: Attempting a synthesized click on", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            AXEventSynthesizer.click_object(obj)

    def _get_selected_accessible_and_offset(self) -> tuple[Atspi.Accessible | None, int]:
        """Get the selected accessible object and offset."""
        if not self._tree:
            msg = "ERROR: Could not get navlist tree"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None, -1

        selection = self._tree.get_selection()
        if not selection:
            msg = "ERROR: Could not get selection for navlist tree"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None, -1

        model, paths = selection.get_selected_rows()
        if not paths:
            msg = "ERROR: Could not get paths for navlist tree"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None, -1

        obj = model.get_value(model.get_iter(paths[0]), 0)
        offset = model.get_value(model.get_iter(paths[0]), 1)
        return obj, max(0, offset)


def show_ui(
    title: str = "",
    column_headers: list[str] | None = None,
    rows: list[tuple[Any, ...]] | None = None,
    selected_row: int = 0,
) -> None:
    """Show the navigation list UI."""
    if column_headers is None:
        column_headers = []
    if rows is None:
        rows = [()]

    gui = OrcaNavListGUI(title, column_headers, rows, selected_row)
    gui.show_gui()
