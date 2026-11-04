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

"""Launches Nautilus for integration tests."""

import os
import sys

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio


def main() -> None:
    """Configures the requested view and launches Nautilus."""

    os.environ["GSETTINGS_BACKEND"] = "keyfile"
    os.environ["XDG_SESSION_TYPE"] = "x11"
    binary, folder, view = sys.argv[1:]
    settings = Gio.Settings.new("org.gnome.nautilus.preferences")
    settings.set_string("default-folder-viewer", view + "-view")
    settings.set_string("default-sort-order", "name")
    settings.set_boolean("default-sort-in-reverse-order", False)
    settings.set_string("show-image-thumbnails", "never")
    Gio.Settings.new("org.gtk.Settings.FileChooser").set_boolean("sort-directories-first", True)
    Gio.Settings.new("org.gtk.Settings.FileChooser").set_boolean("show-hidden", False)
    icons = Gio.Settings.new("org.gnome.nautilus.icon-view")
    icons.set_string("default-zoom-level", "medium")
    icons.set_strv("captions", ["none", "none", "none"])
    listing = Gio.Settings.new("org.gnome.nautilus.list-view")
    listing.set_string("default-zoom-level", "medium")
    listing.set_strv("default-visible-columns", ["name"])
    listing.set_strv("default-column-order", ["name"])
    Gio.Settings.sync()  # pylint: disable=no-value-for-parameter
    os.execv(binary, [binary, "--new-window", folder])  # noqa: S606


if __name__ == "__main__":
    main()
