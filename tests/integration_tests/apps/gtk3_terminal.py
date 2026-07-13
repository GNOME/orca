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
# pylint: disable=no-name-in-module

"""A GTK3 window with a fixed-geometry VTE terminal running a real program."""

import os
import sys

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gdk, GLib, Gtk, Vte

APP_TITLE = "OrcaVteTerminal"

TERM = "xterm"

# A small, fixed grid: the pty inherits this winsize, so a pager paginates
# identically every run and braille assertions stay short.
_COLUMNS = 40
_ROWS = 8


def main() -> int:
    """Spawns argv[2:] in a fixed-geometry VTE terminal with argv[1] as its working dir."""

    working_directory = sys.argv[1]
    command = sys.argv[2:]

    GLib.set_prgname(APP_TITLE)
    font_css = b'vte-terminal { font-family: "DejaVu Sans Mono"; font-size: 12pt; }'

    provider = Gtk.CssProvider()
    provider.load_from_data(font_css)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

    window = Gtk.Window()
    window.set_resizable(False)
    window.set_decorated(False)
    window.connect("destroy", Gtk.main_quit)

    terminal = Vte.Terminal()
    terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.OFF)
    terminal.set_audible_bell(False)
    terminal.set_scrollback_lines(0)
    terminal.set_size(_COLUMNS, _ROWS)
    window.add(terminal)

    # A curated environment so the prompt, locale, and terminal type are fixed.
    envv = [
        f"TERM={TERM}",
        "LANG=en_US.UTF-8",
        "LC_ALL=en_US.UTF-8",
        "PS1=$ ",
        "PS2=> ",
        f"HOME={os.environ.get('HOME', '/tmp')}",
        f"PATH={os.environ.get('PATH', '/usr/bin')}",
    ]

    # Programs which cannot look up TERM fall back to crude output, such as erasing a
    # character by overwriting it with a space. Pass on where the database lives.
    envv.extend(
        f"{name}={value}"
        for name in ("TERMINFO", "TERMINFO_DIRS")
        if (value := os.environ.get(name))
    )

    def spawn(_widget: Gtk.Widget) -> None:
        terminal.grab_focus()
        terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            working_directory,
            command,
            envv,
            GLib.SpawnFlags.DEFAULT,
            None,
            None,
            -1,
            None,
            None,
        )

    window.connect("map", spawn)
    window.show_all()
    window.present()
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
