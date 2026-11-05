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

"""Use F5 to change Color and Shift+F5 to change City without moving focus."""

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

APP_TITLE = "OrcaComboBox"


def main() -> None:
    """Shows two combo boxes whose selections can change without moving focus."""

    GLib.set_prgname(APP_TITLE)
    window = Gtk.Window(title="Combo boxes")
    window.set_default_size(400, 240)
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    start = Gtk.Button(label="Start")
    color = Gtk.ComboBoxText()
    color.get_accessible().set_name("Color")
    city = Gtk.ComboBoxText.new_with_entry()
    city.get_accessible().set_name("City")
    for value in ("Red", "Green", "Blue"):
        color.append_text(value)
    for value in ("London", "Paris", "Rome"):
        city.append_text(value)
    color.set_active(0)
    city.set_active(0)
    for widget in (start, color, city, Gtk.Button(label="After")):
        box.pack_start(widget, False, False, 0)
    window.add(box)

    def on_key(_widget, event):
        if event.keyval == Gdk.KEY_F5:
            combo = city if event.state & Gdk.ModifierType.SHIFT_MASK else color
            combo.set_active((combo.get_active() + 1) % 3)
            return True
        return False

    window.connect("key-press-event", on_key)
    window.connect("map", lambda _widget: start.grab_focus())
    window.show_all()
    window.present()
    Gtk.main()


if __name__ == "__main__":
    main()
