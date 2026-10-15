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

# pylint: disable=import-outside-toplevel

"""Launches Atril with settings confined to the integration-test sandbox."""

from __future__ import annotations

import os
import sys

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio


def prepare_window(pid: int) -> None:
    """Sizes and focuses the owned Atril window on Xvfb, without a window manager."""

    from Xlib import X, display  # type: ignore[import-untyped]

    connection = display.Display()
    try:
        pid_atom = connection.intern_atom("_NET_WM_PID")
        for window in connection.screen().root.query_tree().children:
            owner = window.get_full_property(pid_atom, X.AnyPropertyType)
            if owner is None or owner.value[0] != pid:
                continue
            attributes = window.get_attributes()
            if attributes.map_state != X.IsViewable or attributes.win_class != X.InputOutput:
                continue
            window.configure(x=0, y=0, width=1023, height=767)
            window.set_input_focus(X.RevertToParent, X.CurrentTime)
            connection.sync()
            return
        raise RuntimeError(f"No mapped Atril window found for pid {pid}")
    finally:
        connection.close()


def main() -> None:
    """Writes private settings which survive exec, then replaces this process with Atril."""

    os.environ["GSETTINGS_BACKEND"] = "keyfile"
    settings = Gio.Settings.new("org.mate.Atril")
    settings.set_boolean("show-caret-navigation-message", False)
    defaults = settings.get_child("default")
    defaults.set_boolean("show-sidebar", False)
    defaults.set_string("sizing-mode", "fit-page")
    Gio.Settings.sync()  # pylint: disable=no-value-for-parameter
    binary, document = sys.argv[1:]
    os.execv(binary, [binary, document])  # noqa: S606 - replaces the owned launcher process


if __name__ == "__main__":
    main()
