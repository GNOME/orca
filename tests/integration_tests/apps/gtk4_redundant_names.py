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

"""A GTK4 window with names that Orca may treat as redundant."""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

APP_TITLE = "OrcaRedundantNames"


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    Gtk.init()
    loop = GLib.MainLoop()
    GLib.set_prgname(APP_TITLE)

    window = Gtk.Window()
    window.set_default_size(400, 240)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("close-request", lambda _window: loop.quit())

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    same_name_frame = Gtk.Frame(label="Details")
    same_name_button = Gtk.Button(label="Details")
    same_name_group = Gtk.Box(accessible_role=Gtk.AccessibleRole.GROUP)
    same_name_group.append(same_name_button)
    same_name_frame.set_child(same_name_group)
    box.append(same_name_frame)

    different_name_frame = Gtk.Frame(label="Options")
    different_name_button = Gtk.Button(label="Save")
    different_name_group = Gtk.Box(accessible_role=Gtk.AccessibleRole.GROUP)
    different_name_group.append(different_name_button)
    different_name_frame.set_child(different_name_group)
    box.append(different_name_frame)

    same_name_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    same_name_panel.update_property([Gtk.AccessibleProperty.LABEL], ["Weather"])
    panel_button = Gtk.Button(label="Weather")
    same_name_panel.append(panel_button)
    box.append(same_name_panel)

    window.set_child(box)
    window.connect("map", lambda _widget: same_name_button.grab_focus())

    window.present()
    loop.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
