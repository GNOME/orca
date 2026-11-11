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

"""A note list that opens documents in separate windows."""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, GLib, Gtk

APP_TITLE = "OrcaNoteReader"


def main() -> int:
    """Shows the note list and runs the GTK main loop."""

    Gtk.init()
    GLib.set_prgname(APP_TITLE)
    loop = GLib.MainLoop()
    notes = (
        (
            "Garden note",
            "The garden gate is open.\nPlease water the roses.\nThe hose is beside the shed.",
        ),
        (
            "Kitchen note",
            "The bread is on the table.\nPlease wash the apples.\nThe bowls are in the cupboard.",
        ),
    )
    main = Gtk.Window(title="Notes", default_width=500, default_height=200)
    main.connect("close-request", lambda window: loop.quit())
    listing = Gtk.ListBox()
    main.set_child(listing)
    for title, _text in notes:
        listing.append(Gtk.Label(label=title, xalign=0))

    def open_note(_listing, row):
        title, text = notes[row.get_index()]
        window = Gtk.Window(title=title, default_width=500, default_height=200)
        window.set_transient_for(main)
        document = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, accessible_role=Gtk.AccessibleRole.DOCUMENT
        )
        view = Gtk.TextView(editable=False)
        buffer = view.get_buffer()
        buffer.set_text(text)
        buffer.place_cursor(buffer.get_start_iter())
        document.append(view)
        window.set_child(document)

        def close_note(window):
            window.destroy()
            main.present()
            row.grab_focus()
            return True

        def on_key(_controller, key, _code, _modifiers):
            if key == Gdk.KEY_Escape:
                return close_note(window)
            return False

        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", on_key)
        window.add_controller(keys)
        window.connect("close-request", close_note)
        window.present()
        view.grab_focus()

    listing.connect("row-activated", open_note)
    main.present()
    listing.get_row_at_index(0).grab_focus()
    loop.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
