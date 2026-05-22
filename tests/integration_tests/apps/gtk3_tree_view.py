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

"""A GTK3 window with a column-headed tree view, used as an accessible table."""

import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

APP_TITLE = "OrcaTreeView"

COLUMNS = ("Name", "Role", "Office")
ROWS = (
    ("Ada", "Engineer", "London"),
    ("Grace", "Admiral", "Boston"),
    ("Alan", "Analyst", "Manchester"),
)


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    GLib.set_prgname(APP_TITLE)

    window = Gtk.Window()
    window.set_default_size(400, 200)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)

    store = Gtk.ListStore(str, str, str)
    for row in ROWS:
        store.append(list(row))

    tree_view = Gtk.TreeView(model=store)
    tree_view.set_headers_visible(True)
    for index, title in enumerate(COLUMNS):
        tree_view.append_column(Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=index))

    window.add(tree_view)

    def on_map(_widget: Gtk.Widget) -> None:
        tree_view.grab_focus()
        tree_view.set_cursor(Gtk.TreePath.new_first(), tree_view.get_column(0), False)

    window.connect("map", on_map)
    window.show_all()
    window.present()
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
