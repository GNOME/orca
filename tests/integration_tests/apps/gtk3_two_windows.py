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

"""Two top-level windows for cross-window flat review tests."""

import sys

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

APP_TITLE = "OrcaTwoWindows"

TEXT_VIEW_LINES = "First line.\nSecond line.\nThird line."


def main() -> int:
    """Shows the first window and runs the GTK main loop."""

    GLib.set_prgname(APP_TITLE)

    second_window = Gtk.Window()
    second_window.set_title("Second")
    second_window.set_default_size(300, 100)
    second_window.set_decorated(False)
    second_entry = Gtk.Entry()
    second_entry.set_text("Second window entry")
    second_window.add(second_entry)

    first_window = Gtk.Window()
    first_window.set_title("First")
    first_window.set_default_size(300, 100)
    first_window.set_decorated(False)
    text_view = Gtk.TextView()
    text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
    buffer = text_view.get_buffer()
    buffer.set_text(TEXT_VIEW_LINES)
    buffer.place_cursor(buffer.get_start_iter())
    first_window.add(text_view)

    def on_key(_widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        if event.keyval == Gdk.KEY_F2:
            second_window.show_all()
            second_window.present()
            second_entry.grab_focus()
            return True
        if event.keyval == Gdk.KEY_F3:
            first_window.show_all()
            first_window.present()
            text_view.grab_focus()
            return True
        return False

    first_window.connect("key-press-event", on_key)
    second_window.connect("key-press-event", on_key)
    first_window.connect("destroy", Gtk.main_quit)
    first_window.connect("map", lambda _widget: text_view.grab_focus())

    first_window.show_all()
    first_window.present()
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
