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

"""A terminal whose second line changes repeatedly after F5."""

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gdk, GLib, Gtk, Vte

APP_TITLE = "OrcaTerminalUpdates"


def main() -> int:
    """Shows a terminal; F5 starts 100 updates after a short pause."""

    GLib.set_prgname(APP_TITLE)
    window = Gtk.Window()
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)
    terminal = Vte.Terminal()
    terminal.set_size(40, 4)
    terminal.set_scrollback_lines(0)
    terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.OFF)
    terminal.feed(b"anchor\r\nvalue 000\r\nbottom\x1b[2;1H")
    window.add(terminal)
    value = 0

    def update() -> bool:
        nonlocal value
        value += 1
        terminal.feed(f"\x1b[2;1Hvalue {value:03d}\x1b[K\x1b[2;1H".encode())
        return value < 100

    def start() -> bool:
        GLib.timeout_add(20, update)
        return GLib.SOURCE_REMOVE

    def key_pressed(_widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        if event.keyval != Gdk.KEY_F5:
            return False
        GLib.timeout_add(600, start)
        return True

    window.connect("key-press-event", key_pressed)
    window.show_all()
    terminal.grab_focus()
    window.present()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
