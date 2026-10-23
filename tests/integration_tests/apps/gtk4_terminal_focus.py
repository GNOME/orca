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

"""Two terminals with keyboard commands to move focus and remove a terminal."""

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "3.91")
from gi.repository import Gdk, GLib, Gtk, Vte

APP_TITLE = "OrcaTerminalFocus"


def main() -> int:
    """Shows two terminals; F5 resets them, F6 changes focus, and F7 also removes the old one."""

    Gtk.init()
    loop = GLib.MainLoop()
    GLib.set_prgname(APP_TITLE)
    window = Gtk.Window()
    window.set_decorated(False)
    window.connect("close-request", lambda _window: loop.quit())
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    window.set_child(box)
    terminals = []

    def reset() -> None:
        for terminal in terminals:
            box.remove(terminal)
        terminals.clear()
        for text in (
            "First terminal has a longer opening line.\r\nLast line.",
            "Second terminal.\r\nFinal line.",
        ):
            terminal = Vte.Terminal()
            terminal.set_size(50, 3)
            terminal.set_scrollback_lines(0)
            terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.OFF)
            terminal.feed((text + "\x1b[H").encode())
            box.append(terminal)
            terminals.append(terminal)
        terminals[0].grab_focus()

    def key_pressed(
        _controller: Gtk.EventControllerKey, keyval: int, _keycode: int, _state: Gdk.ModifierType
    ) -> bool:
        if keyval == Gdk.KEY_F5:
            reset()
            return True
        if keyval in (Gdk.KEY_F6, Gdk.KEY_F7):
            terminals[1].grab_focus()
            if keyval == Gdk.KEY_F7:
                box.remove(terminals.pop(0))
            return True
        return False

    controller = Gtk.EventControllerKey()
    controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
    controller.connect("key-pressed", key_pressed)
    window.add_controller(controller)
    reset()
    window.present()
    loop.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
