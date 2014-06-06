# Orca
#
# Copyright 2013 Igalia, S.L.
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

"""Displays a GUI to present Orca commands."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013 Igalia, S.L."
__license__   = "LGPL"

from gi.repository import GObject, Gdk, Gtk
from . import guilabels
from . import orca_state

class OrcaCommandListGUI:

    def __init__(self, title, columnHeaders, rows, canPerformCommands):
        self._tree = None
        self._okButton = None
        self._gui = self._createCommandListDialog(columnHeaders, rows)
        self._gui.set_title(title)
        self._gui.set_modal(True)
        if not canPerformCommands:
            self._okButton.destroy()
        self.showGUI()

    def _createCommandListDialog(self, columnHeaders, rows):
        dialog = Gtk.Dialog()
        dialog.set_default_size(600, 400)

        grid = Gtk.Grid()
        contentArea = dialog.get_content_area()
        contentArea.add(grid)

        scrolledWindow = Gtk.ScrolledWindow()
        grid.add(scrolledWindow)

        self._tree = Gtk.TreeView()
        self._tree.set_hexpand(True)
        self._tree.set_vexpand(True)
        scrolledWindow.add(self._tree)

        cols = len(columnHeaders) * [GObject.TYPE_STRING]
        for i, header in enumerate(columnHeaders):
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(header, cell, text=i)
            self._tree.append_column(column)
            if header:
                column.set_sort_column_id(i)

        model = Gtk.ListStore(*cols)
        for row in rows:
            rowIter = model.append(None)
            for i, cell in enumerate(row):
                model.set_value(rowIter, i, str(cell))

        column = self._tree.get_column(0)
        column.set_visible(False)

        btn = dialog.add_button(guilabels.BTN_CANCEL, Gtk.ResponseType.CANCEL)
        btn.connect('clicked', self._onCancelClicked)

        self._okButton = dialog.add_button(guilabels.BTN_OK, Gtk.ResponseType.OK)
        self._okButton.grab_default()
        self._okButton.connect('clicked', self._onOKClicked)

        self._tree.set_model(model)
        self._tree.connect('key-release-event', self._onKeyRelease)
        return dialog

    def showGUI(self):
        self._gui.show_all()

        ts = orca_state.lastInputEvent.timestamp
        if ts == 0:
            ts = Gtk.get_current_event_time()
        self._gui.present_with_time(ts)

    def _onKeyRelease(self, widget, event):
        keycode = event.hardware_keycode
        keymap = Gdk.Keymap.get_default()
        entries_for_keycode = keymap.get_entries_for_keycode(keycode)
        entries = entries_for_keycode[-1]
        eventString = Gdk.keyval_name(entries[0])
        if eventString == 'Return':
            self._gui.activate_default()

    def _onCancelClicked(self, widget):
        self._gui.destroy()

    def _onOKClicked(self, widget):
        handler = self._getSelectedHandler()
        self._gui.destroy()

    def _getSelectedHandler(self):
        if not self._tree:
            return None

        selection = self._tree.get_selection()
        if not selection:
            return None

        model, paths = selection.get_selected_rows()
        if not paths:
            return None

        return model.get_value(model.get_iter(paths[0]), 0)

def showUI(title='', columnHeaders=[], rows=[()], canPerformCommands=True):
    gui = OrcaCommandListGUI(title, columnHeaders, rows, canPerformCommands)
    gui.showGUI()
