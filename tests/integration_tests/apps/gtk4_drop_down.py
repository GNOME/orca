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

"""A GTK4 drop-down with a mnemonic label and a following button."""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

APP_TITLE = "OrcaDropDown"


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    Gtk.init()
    GLib.set_prgname(APP_TITLE)
    loop = GLib.MainLoop()
    window = Gtk.Window()
    window.set_default_size(300, 160)
    window.set_decorated(False)
    window.connect("close-request", lambda _window: loop.quit())

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    label = Gtk.Label.new_with_mnemonic("_Color")
    drop_down = Gtk.DropDown.new_from_strings(["Red", "Green", "Blue"])
    label.set_mnemonic_widget(drop_down)
    box.append(label)
    box.append(drop_down)
    box.append(Gtk.Button(label="Done"))
    window.set_child(box)
    window.connect("map", lambda _widget: drop_down.grab_focus())
    window.present()
    loop.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
