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

"""A GTK3 window whose containers share a name with the widget they contain."""

import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

APP_TITLE = "OrcaRedundantNames"


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    GLib.set_prgname(APP_TITLE)

    window = Gtk.Window()
    window.set_default_size(400, 240)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    same_name_frame = Gtk.Frame(label="Details")
    same_name_button = Gtk.Button(label="Details")
    same_name_frame.add(same_name_button)
    box.pack_start(same_name_frame, False, False, 0)

    different_name_frame = Gtk.Frame(label="Options")
    different_name_button = Gtk.Button(label="Save")
    different_name_frame.add(different_name_button)
    box.pack_start(different_name_frame, False, False, 0)

    same_name_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    same_name_panel.get_accessible().set_name("Weather")
    panel_button = Gtk.Button(label="Weather")
    same_name_panel.pack_start(panel_button, False, False, 0)
    box.pack_start(same_name_panel, False, False, 0)

    window.add(box)
    window.connect("map", lambda _widget: same_name_button.grab_focus())

    window.show_all()
    window.present()
    Gtk.main()

    return 0


if __name__ == "__main__":
    sys.exit(main())
