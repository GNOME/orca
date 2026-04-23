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

"""A GTK3 window with a fixed-size wrapping text view."""

import sys
from pathlib import Path

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

APP_TITLE = "OrcaTextView"


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    window_width = 600
    window_height = 300
    font_css = b"""
    textview, textview text {
        font-family: "DejaVu Sans Mono";
        font-size: 12pt;
    }
    """

    content = Path(sys.argv[1]).read_text(encoding="utf-8") if len(sys.argv) > 1 else ""

    GLib.set_prgname(APP_TITLE)

    provider = Gtk.CssProvider()
    provider.load_from_data(font_css)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

    window = Gtk.Window()
    window.set_default_size(window_width, window_height)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)

    text_view = Gtk.TextView()
    text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
    text_view.set_size_request(window_width, window_height)

    buffer = text_view.get_buffer()
    buffer.set_text(content)
    buffer.place_cursor(buffer.get_start_iter())

    window.add(text_view)
    window.connect("map", lambda _widget: text_view.grab_focus())

    window.show_all()
    window.present()
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
