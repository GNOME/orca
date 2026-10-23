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

"""A terminal which writes a line and then clears a status line during navigation."""

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "3.91")
from gi.repository import Gdk, GLib, Gtk, Vte

APP_TITLE = "OrcaTerminalTrailingDeletion"


def main() -> int:
    """Uses Up and Down to replace a line without moving the final caret position."""

    Gtk.init()
    loop = GLib.MainLoop()
    GLib.set_prgname(APP_TITLE)
    window = Gtk.Window()
    window.set_decorated(False)
    window.connect("close-request", lambda _window: loop.quit())
    terminal = Vte.Terminal()
    terminal.set_size(40, 4)
    terminal.set_scrollback_lines(0)
    terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.OFF)
    terminal.feed(b"old line\r\nstatus\x1b[1;1H")
    window.set_child(terminal)

    def erase_status() -> bool:
        terminal.feed(b"\x1b[2;1H\x1b[K\x1b[1;1H")
        return GLib.SOURCE_REMOVE

    def replace_line(line: str) -> bool:
        terminal.feed(f"\x1b[1;1H{line}\x1b[K\x1b[2;1Hstatus\x1b[K\x1b[1;1H".encode())
        GLib.timeout_add(100, erase_status)
        return GLib.SOURCE_REMOVE

    def key_pressed(
        _controller: Gtk.EventControllerKey, keyval: int, _keycode: int, _state: Gdk.ModifierType
    ) -> bool:
        if keyval not in (Gdk.KEY_Up, Gdk.KEY_Down):
            return False
        line = "new line" if keyval == Gdk.KEY_Up else "old line"
        GLib.timeout_add(150, replace_line, line)
        return True

    controller = Gtk.EventControllerKey()
    controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
    controller.connect("key-pressed", key_pressed)
    window.add_controller(controller)
    terminal.grab_focus()
    window.present()
    loop.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
