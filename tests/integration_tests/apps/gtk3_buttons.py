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

"""Buttons with an F12 reset for shared GTK widget integration tests."""

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

APP_TITLE = "OrcaButtons"


def main() -> int:
    """Shows push, toggle, check, and switch controls with repeatable initial state."""

    GLib.set_prgname(APP_TITLE)
    window = Gtk.Window()
    window.set_default_size(300, 240)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    save = Gtk.Button(label="Save")
    save.connect("clicked", lambda button: button.set_label("Saved"))
    bold = Gtk.ToggleButton(label="Bold")
    enabled = Gtk.CheckButton(label="Enabled")
    wifi = Gtk.Switch()
    wifi.set_halign(Gtk.Align.START)
    wifi.get_accessible().set_name("Wi-Fi")
    unavailable = Gtk.Button(label="Unavailable")
    unavailable.set_sensitive(False)
    done = Gtk.Button(label="Done")
    for widget in (save, bold, enabled, wifi, unavailable, done):
        box.pack_start(widget, False, False, 0)
    window.add(box)

    def reset() -> None:
        save.set_label("Save")
        bold.set_active(False)
        enabled.set_active(False)
        wifi.set_active(False)
        save.grab_focus()

    def key_pressed(_window: Gtk.Window, event: Gdk.EventKey) -> bool:
        if event.keyval == Gdk.KEY_F12:
            reset()
            return True
        return False

    window.connect("key-press-event", key_pressed)

    window.connect("map", lambda _window: reset())
    window.show_all()
    window.present()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
