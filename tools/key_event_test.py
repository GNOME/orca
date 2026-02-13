#!/usr/bin/python
# key_event_test.py
#
# Command-line tool to print raw key event details for testing and debugging.
# This tool opens a small window to receive key events and prints the raw GDK
# event data for each press and release. Output goes to stdout.
#
# Usage: python3 key_event_test.py
# If Orca is running, enter bypass mode (Alt+Backspace) to release any grabs
# associated with Orca commands (other than Alt+Backspace, which will remain
# grabbed for the purpose of exiting bypass mode).
# Close the window to stop.
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

# pylint: disable=wrong-import-position

"""Command-line tool to print raw key event details for testing and debugging."""

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk  # pylint: disable=no-name-in-module


def on_key_event(_widget: Gtk.Window, event: Gdk.EventKey) -> bool:
    """Prints raw key event data."""

    event_type = "press" if event.type == Gdk.EventType.KEY_PRESS else "release"
    name = Gdk.keyval_name(event.keyval) or ""
    print(
        f"{event_type:8s}"
        f"  hw_code={event.hardware_keycode:<4d}"
        f"  keyval={event.keyval:<6d}"
        f"  state=0x{int(event.state):08x}"
        f"  name={name}"
    )
    return False


window = Gtk.Window(title="Key Event Test")
window.set_default_size(400, 200)
window.connect("destroy", Gtk.main_quit)
window.connect("key-press-event", on_key_event)
window.connect("key-release-event", on_key_event)
window.show_all()
print("Press keys to test. Close window to stop.\n")
Gtk.main()
