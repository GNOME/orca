# Orca
#
# Copyright 2026 Igalia, S.L.
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

# pylint: disable=no-member
# pylint: disable=no-value-for-parameter

"""A GTK3 window with a list whose items can be selected and unselected."""

import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Atk", "1.0")
from gi.repository import Atk, Gdk, GLib, Gtk

APP_TITLE = "OrcaMultiSelectList"

ITEMS = ("Olives", "Peppers", "Mushrooms")


class ItemAccessible(Gtk.LabelAccessible):
    """Exposes selection without claiming keyboard focus."""

    def do_ref_state_set(self):
        states = Gtk.LabelAccessible.do_ref_state_set(self)
        states.add_state(Atk.StateType.SELECTABLE)
        if self.get_widget().get_parent().selected:
            states.add_state(Atk.StateType.SELECTED)
        return states


class Item(Gtk.Label):
    """Shows the selectable item."""

    def __init__(self):
        super().__init__(label="Read report")
        self.set_accessible_type(ItemAccessible)
        self.get_accessible().set_role(Atk.Role.LIST_ITEM)


class ListAccessible(Gtk.ContainerAccessible, Atk.Selection):
    """Exposes a list which manages its descendants."""

    def do_ref_state_set(self):
        states = Gtk.ContainerAccessible.do_ref_state_set(self)
        states.add_state(Atk.StateType.MANAGES_DESCENDANTS)
        return states

    def do_get_selection_count(self):
        return int(self.get_widget().selected)

    def do_ref_selection(self, index):
        if index == 0 and self.get_widget().selected:
            return self.ref_accessible_child(0)
        return None

    def do_is_child_selected(self, index):
        return index == 0 and self.get_widget().selected


class SelectableList(Gtk.Box):
    """Selects an item with Space and announces it as the active descendant."""

    def __init__(self, selection_first):
        super().__init__()
        self.selected = False
        self.selection_first = selection_first
        self.set_can_focus(True)
        self.set_accessible_type(ListAccessible)
        self.add(Item())
        accessible = self.get_accessible()
        accessible.set_role(Atk.Role.LIST_BOX)
        accessible.set_name("Selection first" if selection_first else "Active descendant first")
        self.connect("key-press-event", self.on_key_press)

    def on_key_press(self, _widget, event):
        if event.keyval != Gdk.KEY_space:
            return False

        self.selected = True
        item = self.get_children()[0]
        item.set_state_flags(Gtk.StateFlags.SELECTED, False)
        item.get_accessible().notify_state_change(Atk.StateType.SELECTED, True)
        accessible = self.get_accessible()

        def selection_changed():
            accessible.emit("selection-changed")

        def active_descendant_changed():
            child = accessible.ref_accessible_child(0)
            accessible.emit("active-descendant-changed", child.__gpointer__)

        first, second = selection_changed, active_descendant_changed
        if not self.selection_first:
            first, second = second, first
        first()
        # Separate the events so queue priority cannot determine their processing order.
        GLib.timeout_add(750, second)
        return True


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    GLib.set_prgname(APP_TITLE)

    window = Gtk.Window()
    window.set_default_size(400, 200)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)

    store = Gtk.ListStore(str)
    for item in ITEMS:
        store.append([item])

    tree_view = Gtk.TreeView(model=store)
    tree_view.set_headers_visible(False)
    tree_view.append_column(Gtk.TreeViewColumn("Topping", Gtk.CellRendererText(), text=0))
    tree_view.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.pack_start(tree_view, True, True, 0)
    box.add(SelectableList(True))
    box.add(SelectableList(False))
    window.add(box)

    def on_map(_widget: Gtk.Widget) -> None:
        tree_view.grab_focus()
        tree_view.set_cursor(Gtk.TreePath.new_first(), tree_view.get_column(0), False)
        tree_view.get_selection().unselect_all()

    window.connect("map", on_map)
    window.show_all()
    window.present()
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
