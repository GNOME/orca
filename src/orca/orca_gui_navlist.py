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
from . import orca_state
from .orca_i18n import _

class OrcaNavListGUI:

    def __init__(self, title, columnHeaders, rows):
        self._tree = None
        self._activateButton = None
        self._gui = self._createNavListDialog(columnHeaders, rows)
        self._gui.set_title(title)
        self._gui.set_modal(True)
        self.showGUI()

    def _createNavListDialog(self, columnHeaders, rows):
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

        cols = [GObject.TYPE_OBJECT]
        cols.extend(len(columnHeaders) * [GObject.TYPE_STRING])
        model = Gtk.ListStore(*cols)

        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Accessible", cell, text=0)
        column.set_visible(False)
        self._tree.append_column(column)

        for i, header in enumerate(columnHeaders):
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(header, cell, text=i+1)
            column.set_sort_column_id(i+1)
            self._tree.append_column(column)

        for row in rows:
            rowIter = model.append(None)
            for i, cell in enumerate(row):
                model.set_value(rowIter, i, cell)

        self._tree.set_model(model)

        btn = dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        btn.connect('clicked', self._onCancelClicked)

        btn = dialog.add_button(Gtk.STOCK_JUMP_TO, Gtk.ResponseType.APPLY)
        btn.grab_default()
        btn.connect('clicked', self._onJumpToClicked)

        # Translators: This string appears on a button in a dialog. "Activating"
        # the selected item will perform the action that one would expect to
        # occur if the object were clicked on with the mouse. Thus if the object
        # is a link, activating it will bring you to a new page. If the object
        # is a button, activating it will press the button. If the object is a
        # combobox, activating it will expand it to show all of its contents.
        self._activateButton = dialog.add_button(_('_Activate'), Gtk.ResponseType.OK)
        self._activateButton.connect('clicked', self._onActivateClicked)

        self._tree.connect('key-release-event', self._onKeyRelease)
        self._tree.connect('cursor-changed', self._onCursorChanged)

        return dialog

    def showGUI(self):
        self._gui.show_all()
        ts = orca_state.lastInputEventTimestamp
        if ts == 0:
            ts = Gtk.get_current_event_time()
        self._gui.present_with_time(ts)

    def _onCursorChanged(self, widget):
        obj = self._getSelectedAccessible()
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
        obj = self._getSelectedAccessible()
        self._gui.destroy()
        try:
            obj.queryComponent().grabFocus()
        except:
            debug.println(debug.LEVEL_FINE, 'Could not grab focus on %s' % obj)
        try:
            text = obj.queryText()
            text.setCaretOffset(0)
        except NotImplementedError:
            pass

    def _onActivateClicked(self, widget):
        obj = self._getSelectedAccessible()
        self._gui.destroy()
        try:
            action = obj.queryAction()
        except:
            debug.println(
                debug.LEVEL_FINE, 'Could not perform action on %s' % obj)
        else:
            action.doAction(0)

    def _getSelectedAccessible(self):
        if not self._tree:
            return None

        selection = self._tree.get_selection()
        if not selection:
            return None

        model, paths = selection.get_selected_rows()
        if not paths:
            return None

        return model.get_value(model.get_iter(paths[0]), 0)

def showUI(title='', columnHeaders=[], rows=[()]):
    gui = OrcaNavListGUI(title, columnHeaders, rows)
    gui.showGUI()
