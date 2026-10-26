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

"""A GTK4 window with check buttons whose state cycles through unchecked, mixed, and checked."""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

APP_TITLE = "OrcaTriStateCheckbox"


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    Gtk.init()
    loop = GLib.MainLoop()
    GLib.set_prgname(APP_TITLE)

    window = Gtk.Window()
    window.set_default_size(400, 200)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("close-request", lambda _window: loop.quit())

    forward = Gtk.CheckButton(label="Forward")
    backward = Gtk.CheckButton(label="Backward")
    backward.set_active(True)
    states = {forward: 0, backward: 2}

    def on_activate(button: Gtk.CheckButton, step: int) -> None:
        states[button] = (states[button] + step) % 3
        button.set_inconsistent(states[button] == 1)
        button.set_active(states[button] == 2)

    forward.connect_after("activate", on_activate, 1)
    backward.connect_after("activate", on_activate, 2)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.append(forward)
    box.append(backward)
    window.set_child(box)

    def on_map(_widget: Gtk.Widget) -> None:
        forward.grab_focus()

    window.connect("map", on_map)
    window.present()
    loop.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
