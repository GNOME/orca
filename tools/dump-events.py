#!/usr/bin/python
# dump-events.py
#
# Command-line tool to listen for and display accessibility events for a named
# application.
#
# Usage: dump-events.py <APP_NAME> [EVENT_TYPE]
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

# pylint: disable=invalid-name
# pylint: disable=wrong-import-position

"""Command-line tool to listen for and display accessibility events for a named application."""

import signal
import sys
from types import SimpleNamespace

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

_state = SimpleNamespace(
    app_name="",
    desktop_app_names=set(),
    extra_app_names=set(),
    all_app_names=set(),
    event_count=0,
    event_filter="",
)


def get_name_and_role(obj):
    """Get the name and role of an accessible object, falling back on labelled-by."""

    try:
        name = Atspi.Accessible.get_name(obj) or ""
        role = Atspi.Accessible.get_role(obj).value_nick
    except GLib.GError:
        return "", "(error)"

    if not name:
        label = _get_name_from_labelled_by(obj)
        if label:
            name = f"{label} (from labelled-by)"

    return name, role


def _get_name_from_labelled_by(obj):
    """Returns the name derived from the labelled-by relation, or empty string."""

    try:
        relations = Atspi.Accessible.get_relation_set(obj)
    except GLib.GError:
        return ""

    for relation in relations:
        if relation.get_relation_type() != Atspi.RelationType.LABELLED_BY:
            continue
        targets = [relation.get_target(i) for i in range(relation.get_n_targets())]
        names = []
        for target in targets:
            try:
                target_name = Atspi.Accessible.get_name(target) or ""
            except GLib.GError:
                target_name = ""
            if target_name:
                names.append(target_name)
        if names:
            return " ".join(names)

    return ""


def matches_app(obj):
    """Returns True if obj belongs to the target application."""

    try:
        app = Atspi.Accessible.get_application(obj)
        app_name = Atspi.Accessible.get_name(app) or "" if app is not None else ""
    except GLib.GError:
        app_name = ""
    if app_name in _state.all_app_names:
        return True
    if _state.app_name.lower() in app_name.lower():
        _state.all_app_names.add(app_name)
        if app_name not in _state.desktop_app_names:
            _state.extra_app_names.add(app_name)
        return True
    return False


def on_event(event):
    """Callback for all accessibility events."""

    if not matches_app(event.source):
        return

    if _state.event_filter and not event.type.startswith(_state.event_filter):
        return

    _state.event_count += 1

    name, role = get_name_and_role(event.source)
    source = f"'{name}' ({role})" if name else f"<unnamed> ({role})"

    detail1 = bool(event.detail1) if "state-changed" in event.type else event.detail1

    print(
        f"{event.type} src={source}"
        f" detail1={detail1} detail2={event.detail2}"
        f" any_data={event.any_data}"
    )


def get_desktop_apps():
    """Get all accessible applications from the desktop as (name, object) pairs."""

    apps = []
    desktop = Atspi.get_desktop(0)
    for i in range(Atspi.Accessible.get_child_count(desktop)):
        try:
            child = Atspi.Accessible.get_child_at_index(desktop, i)
            name = Atspi.Accessible.get_name(child)
            if name != "mutter-x11-frames":
                apps.append((name, child))
        except GLib.GError:
            continue
    return apps


def main():
    """Starts listening for events from the specified application."""

    if len(sys.argv) < 2:
        print("Usage: dump-events.py <APP_NAME> [EVENT_TYPE]")
        print()
        print("EVENT_TYPE is an optional prefix filter, e.g.:")
        print("  object:state-changed:focused")
        print("  object:text-changed")
        print("  window:")
        print()
        apps = get_desktop_apps()
        print(f"Desktop has {len(apps)} accessible application(s):")
        for i, (name, _obj) in enumerate(apps):
            print(f"  {i + 1}. {name}")
        sys.exit(1)

    _state.app_name = sys.argv[1]
    _state.event_filter = sys.argv[2] if len(sys.argv) > 2 else ""

    apps = get_desktop_apps()
    matches = [(n, o) for n, o in apps if _state.app_name.lower() in n.lower()]
    if not matches:
        print(f"No application matching '{_state.app_name}' found.")
        print(f"Desktop has {len(apps)} accessible application(s):")
        for i, (name, _obj) in enumerate(apps):
            print(f"  {i + 1}. {name}")
        sys.exit(1)

    match_names = [n for n, _o in matches]
    _state.desktop_app_names = set(match_names)
    _state.all_app_names = set(match_names)
    if len(matches) > 1:
        print(f"Matching applications: {', '.join(match_names)}")

    event_types = [
        "object:state-changed:",
        "object:children-changed:",
        "object:property-change:",
        "object:text-caret-moved",
        "object:text-changed:",
        "window:",
    ]

    listeners = []
    for event_type in event_types:
        listener = Atspi.EventListener.new(on_event)
        listener.register(event_type)
        listeners.append(listener)

    filter_msg = f" (filter: {_state.event_filter})" if _state.event_filter else ""
    print(f"Listening for events from '{_state.app_name}'{filter_msg}. Press Ctrl+C to stop.\n")

    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGINT, _on_sigint)
    Atspi.event_main()  # pylint: disable=no-value-for-parameter


def _on_sigint():
    """Handle Ctrl+C by quitting the event loop."""

    print(f"\nStopped. {_state.event_count} event(s) received.")
    Atspi.event_quit()  # pylint: disable=no-value-for-parameter
    return GLib.SOURCE_REMOVE


if __name__ == "__main__":
    main()
