#!/bin/bash

set -euxo pipefail

source ci/env.sh

echo "Container dependency versions"
for binary in Xvfb atril chromium firefox bash less nano vim seq gdbus dbus-run-session \
    dbus-update-activation-environment pgrep flock fusermount glib-compile-schemas notify-send; do
    printf '%s: ' "$binary"
    rpm -qf --queryformat '%{NAME} %{VERSION}-%{RELEASE}\n' "$(command -v "$binary")"
done
rpm -q --queryformat '%{NAME} %{VERSION}-%{RELEASE}\n' dejavu-fonts liblouis-data notification-daemon \
    terminfo-base typelib-1_0-Gtk-3_0 typelib-1_0-Gtk-4_0 typelib-1_0-Pango-1_0 \
    typelib-1_0-Vte-2_91 typelib-1_0-Vte-3_91
test -x /usr/libexec/notification-daemon
chromium --version
firefox --version
python3 --version
python3 -m pip show pytest pytest-mock python-xlib
pkg-config --modversion liblouis
louis_tables_dir=$(pkg-config --variable=tablesdir liblouis)
test -n "$louis_tables_dir"
test -r "$louis_tables_dir/en-us-g1.ctb"
test -r "$louis_tables_dir/en-us-g2.ctb"

python3 - "$louis_tables_dir" <<'PY'
import curses
import importlib
import os
import sys

import gi
import louis

gi.require_foreign("cairo")

for module in ("pytest", "pytest_mock", "dasbus", "psutil", "cairo", "babel", "Xlib.display"):
    importlib.import_module(module)

for namespace, version in (("Gtk", "3.0"), ("Gdk", "3.0"), ("GLib", "2.0"),
                           ("PangoCairo", "1.0"), ("Vte", "2.91")):
    gi.Repository.get_default().require(namespace, version, 0)

from gi.repository import PangoCairo

if not any(font.get_name() == "DejaVu Sans Mono"
           for font in PangoCairo.FontMap.get_default().list_families()):
    raise RuntimeError("DejaVu Sans Mono is missing")

with open(os.devnull, "w") as stream:
    curses.setupterm("xterm", stream.fileno())

for table in ("en-us-g1.ctb", "en-us-g2.ctb"):
    louis.translateString([os.path.join(sys.argv[1], table)], "container check")
print("liblouis:", louis.version())
print("Python imports, GI typelibs, font, terminfo, and braille tables: OK")
PY

# GTK4 and GTK3 cannot be loaded in the same process.
python3 - <<'PY_GTK4'
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "3.91")
from gi.repository import Gtk, Vte

print("GTK4:", Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())
print("VTE (GTK4):", Vte.get_major_version(), Vte.get_minor_version(), Vte.get_micro_version())
PY_GTK4
