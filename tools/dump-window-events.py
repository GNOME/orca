#!/usr/bin/python
# dump-window-events.py
#
# Command-line tool to dump window activation and deactivation events along with
# the window(s) which claim to be active.
#
# Copyright 2025 Igalia, S.L.
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

"""Command-line tool to dump window activation and deactivation events."""

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

def clear_atspi_cache(obj):
    """Clear the AT-SPI cache for a specific object."""

    try:
        Atspi.Accessible.clear_cache_single(obj)
    except GLib.GError:
        pass
    else:
        return

    try:
        Atspi.Accessible.clear_cache(obj)
    except GLib.GError:
        pass
    else:
        return

def get_all_applications():
    """Get all running accessible applications."""

    apps = []
    desktop = Atspi.get_desktop(0)
    for i in range(Atspi.Accessible.get_child_count(desktop)):
        try:
            child = Atspi.Accessible.get_child_at_index(desktop, i)
            # Children of mutter-x11-frames seem to mirror the actual apps, but are not what we
            # want. And Orca ignores them because we need to handle the real app; not some clone.
            if Atspi.Accessible.get_name(child) != "mutter-x11-frames":
                apps.append(child)
        except GLib.GError:
            continue

    return apps

def find_all_active_windows(apps=None):
    """Find all windows which claim to be active.."""

    active_windows = []
    if apps is None:
        apps = get_all_applications()

    for app in apps:
        try:
            for i in range(Atspi.Accessible.get_child_count(app)):
                child = Atspi.Accessible.get_child_at_index(app, i)
                # To ensure we're not basing the decision on stale data.
                clear_atspi_cache(child)
                state_set = Atspi.Accessible.get_state_set(child)
                if state_set.contains(Atspi.StateType.ACTIVE):
                    active_windows.append(child)
        except GLib.GError as error:
            print(f"(error finding active windows: {error})")

    return active_windows

def get_name_and_role(obj):
    """Get the name and role of an accessible object."""

    try:
        name = Atspi.Accessible.get_name(obj) or "<unnamed>"
        role = Atspi.Accessible.get_role(obj).value_nick
        return f"'{name}' {role}"
    except GLib.GError as error:
        return f"(error getting name and role: {error})"

def get_top_level_object(obj):
    """Get the highest level accessible object for a given object."""

    # In well-behaved applications, this should work.
    try:
        application = Atspi.Accessible.get_application(obj)
    except GLib.GError as error:
        print(f"(error getting application: {error})")
    else:
        if application is not None:
            return application

    # Walk up the tree as far as we can. We should be able to ascend all the way to the app.
    # But if we wound up here, we already have breakage and knowing how far we got may help
    # with debugging.
    desktop = Atspi.get_desktop(0)
    result = obj
    while result is not None:
        try:
            parent = Atspi.Accessible.get_parent(result)
        except GLib.GError:
            break
        if parent in (None, desktop):
            break
        result = parent

    return result

def get_object_info(obj):
    """Returns basic info about an accessible object."""

    name_and_role = get_name_and_role(obj)
    top_level_name_and_role = get_name_and_role(get_top_level_object(obj))
    return f"{name_and_role} from: {top_level_name_and_role}"

def on_window_event(e):
    """Handle window activation and deactivation events."""

    event_type = e.type.split(":")[-1].upper()
    print(f"\n{event_type}: {get_object_info(e.source)}")

    apps = get_all_applications()
    active_windows = find_all_active_windows(apps)
    if not active_windows:
        print("No windows have the active state. The following applications are known to AT-SPI2:")
        for i, app in enumerate(apps):
            try:
                print(f"{i+1:2}. {Atspi.Accessible.get_name(app)}")
            except GLib.GError as error:
                print(f"{i+1:2}. {error}")
        return

    if len(active_windows) == 1:
        print(f"The active window is: {get_object_info(active_windows[0])}")
        return

    print(f"{len(active_windows)} windows claim they are active:")
    for i, win in enumerate(active_windows):
        try:
            print(f"{i+1:2}. {get_object_info(win)}")
        except GLib.GError as error:
            print(f"{i+1:2}. {error}")

def on_focus_event(e):
    """Handle focus events for exit condition."""

    if not e.detail1:
        return

    try:
        if Atspi.Accessible.get_role(e.source) == Atspi.Role.TERMINAL:
            print("Exiting.")
            Atspi.event_quit()
    except GLib.GError:
        pass

def main():
    """Starts the window event dumper and waits for events."""

    window_listener = Atspi.EventListener.new(on_window_event)
    window_listener.register("window:activate")
    window_listener.register("window:deactivate")

    focus_listener = Atspi.EventListener.new(on_focus_event)
    focus_listener.register("object:state-changed:focused")

    print("Listening for window activation/deactivation events. Focus a terminal to exit.")
    Atspi.event_main()

if __name__ == "__main__":
    main()
