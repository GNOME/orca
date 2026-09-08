#!/bin/bash

set -euxo pipefail

source ci/env.sh

echo "Container dependency versions"
for binary in Xvfb chromium bash less nano vim seq gdbus dbus-run-session \
    dbus-update-activation-environment pgrep flock fusermount glib-compile-schemas; do
    printf '%s: ' "$binary"
    rpm -qf --queryformat '%{NAME} %{VERSION}-%{RELEASE}\n' "$(command -v "$binary")"
done
rpm -q --queryformat '%{NAME} %{VERSION}-%{RELEASE}\n' dejavu-fonts liblouis-data terminfo-base \
    typelib-1_0-Gtk-3_0 typelib-1_0-Pango-1_0 typelib-1_0-Vte-2_91
chromium --version
python3 --version
python3 -m pip show pytest pytest-mock
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

for module in ("pytest", "pytest_mock", "dasbus", "psutil", "cairo", "babel"):
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
