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

"""Provides an entry with completion suggestions."""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

APP_TITLE = "OrcaEntryCompletion"


def main() -> None:
    """Shows a city entry and its completion suggestions."""

    GLib.set_prgname(APP_TITLE)
    window = Gtk.Window(title="Entry completion")
    window.set_default_size(400, 240)
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    start = Gtk.Button(label="Start")
    entry = Gtk.Entry()
    label = Gtk.Label.new_with_mnemonic("_City")
    label.set_mnemonic_widget(entry)
    model = Gtk.ListStore(str)
    for city in ("London", "Los Angeles", "Lodz", "Paris"):
        model.append([city])
    completion = Gtk.EntryCompletion()
    completion.set_model(model)
    completion.set_text_column(0)
    completion.set_minimum_key_length(2)
    entry.set_completion(completion)
    for widget in (start, label, entry, Gtk.Button(label="After")):
        box.pack_start(widget, False, False, 0)
    window.add(box)
    window.connect("map", lambda _widget: start.grab_focus())
    window.show_all()
    window.present()
    Gtk.main()


if __name__ == "__main__":
    main()
