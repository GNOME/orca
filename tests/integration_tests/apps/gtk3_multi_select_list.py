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
from gi.repository import GLib, Gtk

APP_TITLE = "OrcaMultiSelectList"

ITEMS = ("Olives", "Peppers", "Mushrooms")


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

    window.add(tree_view)

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
