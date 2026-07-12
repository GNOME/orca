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

"""A GTK3 window with two single-line entries holding distinct text."""

import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

APP_TITLE = "OrcaTwoEntries"

FIRST_ENTRY_TEXT = "Apple pie recipe"
SECOND_ENTRY_TEXT = "Banana bread recipe"


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    GLib.set_prgname(APP_TITLE)

    window = Gtk.Window()
    window.set_default_size(400, 120)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    first_entry = Gtk.Entry()
    first_entry.set_text(FIRST_ENTRY_TEXT)
    second_entry = Gtk.Entry()
    second_entry.set_text(SECOND_ENTRY_TEXT)
    button = Gtk.Button(label="Apply")

    box.pack_start(first_entry, False, False, 0)
    box.pack_start(second_entry, False, False, 0)
    box.pack_start(button, False, False, 0)
    window.add(box)

    def focus_first_entry(_widget: Gtk.Widget) -> None:
        # grab_focus() selects the text. Move the cursor to the end to eliminate test flakiness.
        first_entry.grab_focus()
        first_entry.set_position(-1)

    window.connect("map", focus_first_entry)

    window.show_all()
    window.present()
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
