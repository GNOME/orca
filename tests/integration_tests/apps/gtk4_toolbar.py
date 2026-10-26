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

"""A GTK4 window with a toolbar of tool buttons."""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

APP_TITLE = "OrcaToolbar"


def main() -> int:
    """Shows the window and runs the GTK main loop."""

    Gtk.init()
    loop = GLib.MainLoop()
    GLib.set_prgname(APP_TITLE)

    window = Gtk.Window()
    window.set_default_size(400, 120)
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("close-request", lambda _window: loop.quit())

    toolbar = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL, accessible_role=Gtk.AccessibleRole.TOOLBAR
    )
    buttons = []
    for label in ("Cut", "Copy", "Paste"):
        button = Gtk.Button(label=label)
        toolbar.append(button)
        buttons.append(button)

    window.set_child(toolbar)
    window.connect("map", lambda _widget: buttons[0].grab_focus())

    window.present()
    loop.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
