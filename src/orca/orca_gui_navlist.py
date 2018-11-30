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

"""Displays a GUI for Orca navigation list dialogs"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2012 Igalia, S.L."
__license__   = "LGPL"

from gi.repository import GObject, Gdk, Gtk

from . import debug
from . import guilabels
from . import orca_state

class OrcaNavListGUI:

    def __init__(self, title, columnHeaders, rows, selectedRow):
        self._tree = None
        self._activateButton = None
        self._gui = self._createNavListDialog(columnHeaders, rows, selectedRow)
        self._gui.set_title(title)
        self._gui.set_modal(True)
        self._gui.set_keep_above(True)
        self._gui.set_focus_on_map(True)
        self._gui.set_accept_focus(True)
        self._script = orca_state.activeScript
        self._document = None

    def _createNavListDialog(self, columnHeaders, rows, selectedRow):
        dialog = Gtk.Dialog()
        dialog.set_default_size(500, 400)

        grid = Gtk.Grid()
        contentArea = dialog.get_content_area()
        contentArea.add(grid)

        scrolledWindow = Gtk.ScrolledWindow()
        grid.add(scrolledWindow)

        self._tree = Gtk.TreeView()
        self._tree.set_hexpand(True)
        self._tree.set_vexpand(True)
        scrolledWindow.add(self._tree)

        cols = [GObject.TYPE_OBJECT, GObject.TYPE_INT]
        cols.extend(len(columnHeaders) * [GObject.TYPE_STRING])
        model = Gtk.ListStore(*cols)

        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Accessible", cell, text=0)
        column.set_visible(False)
        self._tree.append_column(column)

        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("offset", cell, text=1)
        column.set_visible(False)
        self._tree.append_column(column)

        for i, header in enumerate(columnHeaders):
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(header, cell, text=i+2)
            column.set_sort_column_id(i+2)
            self._tree.append_column(column)

        for row in rows:
            rowIter = model.append(None)
            for i, cell in enumerate(row):
                model.set_value(rowIter, i, cell)

        self._tree.set_model(model)
        selection = self._tree.get_selection()
        selection.select_path(selectedRow)

        btn = dialog.add_button(guilabels.BTN_CANCEL, Gtk.ResponseType.CANCEL)
        btn.connect('clicked', self._onCancelClicked)

        btn = dialog.add_button(guilabels.BTN_JUMP_TO, Gtk.ResponseType.APPLY)
        btn.grab_default()
        btn.connect('clicked', self._onJumpToClicked)

        self._activateButton = dialog.add_button(
            guilabels.ACTIVATE, Gtk.ResponseType.OK)
        self._activateButton.connect('clicked', self._onActivateClicked)

        self._tree.connect('key-release-event', self._onKeyRelease)
        self._tree.connect('cursor-changed', self._onCursorChanged)
        self._tree.set_search_column(2)

        return dialog

    def showGUI(self):
        self._document = self._script.utilities.documentFrame()
        x, y, width, height = self._script.utilities.getBoundingBox(self._document)
        if (width and height):
            self._gui.move(x + 100, y + 100)

        self._gui.show_all()
        ts = orca_state.lastInputEvent.timestamp
        if ts == 0:
            ts = Gtk.get_current_event_time()
        self._gui.present_with_time(ts)

    def _onCursorChanged(self, widget):
        obj, offset = self._getSelectedAccessibleAndOffset()
        try:
            action = obj.queryAction()
        except:
            self._activateButton.set_sensitive(False)
        else:
            self._activateButton.set_sensitive(action.get_nActions() > 0)

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

    def _onJumpToClicked(self, widget):
        obj, offset = self._getSelectedAccessibleAndOffset()
        self._gui.destroy()
        self._script.utilities.setCaretPosition(obj, offset, self._document)

    def _onActivateClicked(self, widget):
        obj, offset = self._getSelectedAccessibleAndOffset()
        self._gui.destroy()
        if not obj:
            return

        self._script.utilities.setCaretPosition(obj, offset)
        try:
            action = obj.queryAction()
        except NotImplementedError:
            msg = "ERROR: Action interface not implemented for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
        except:
            msg = "ERROR: Exception getting action interface for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            action.doAction(0)

    def _getSelectedAccessibleAndOffset(self):
        if not self._tree:
            msg = "ERROR: Could not get navlist tree"
            debug.println(debug.LEVEL_INFO, msg, True)
            return None, -1

        selection = self._tree.get_selection()
        if not selection:
            msg = "ERROR: Could not get selection for navlist tree"
            debug.println(debug.LEVEL_INFO, msg, True)
            return None, -1

        model, paths = selection.get_selected_rows()
        if not paths:
            msg = "ERROR: Could not get paths for navlist tree"
            debug.println(debug.LEVEL_INFO, msg, True)
            return None, -1

        obj = model.get_value(model.get_iter(paths[0]), 0)
        offset = model.get_value(model.get_iter(paths[0]), 1)
        return obj, max(0, offset)

def showUI(title='', columnHeaders=[], rows=[()], selectedRow=0):
    gui = OrcaNavListGUI(title, columnHeaders, rows, selectedRow)
    gui.showGUI()
