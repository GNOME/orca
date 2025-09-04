#!/usr/bin/python
# dump-focused-object.py
#
# Command-line tool to dump the focused object and its ancestors.
# This tool listens for focus events and displays the accessibility tree
# from the application down to the focused object.
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

"""Command-line tool to dump the focused object and its ancestors."""

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

def as_string(obj):
    """Convert an accessible object to a string representation."""

    try:
        help_text = Atspi.Accessible.get_help_text(obj)
    except GLib.GError as error:
        help_text = f"({error})"
    return (f"{Atspi.Accessible.get_role(obj).value_name} "
            f"name:'{get_name(obj)}' "
            f"description:'{get_description(obj)}' "
            f"help text: '{help_text}'")

def get_name(obj):
    """Get the name of an accessible object."""

    name = Atspi.Accessible.get_name(obj)
    if name:
        return name

    relations = Atspi.Accessible.get_relation_set(obj)
    for relation in relations:
        if relation.get_relation_type() != Atspi.RelationType.LABELLED_BY:
            continue
        targets = [relation.get_target(i) for i in range(relation.get_n_targets())]
        return " ".join([target.name for target in targets])

    return ""

def get_description(obj):
    """Get the description of an accessible object."""

    description = Atspi.Accessible.get_description(obj)
    if description:
        return description

    relations = Atspi.Accessible.get_relation_set(obj)
    for relation in relations:
        if relation.get_relation_type() != Atspi.RelationType.DESCRIBED_BY:
            continue
        targets = [relation.get_target(i) for i in range(relation.get_n_targets())]
        return " ".join([target.name for target in targets])

    return ""

def on_event(e):
    """Handle focus events."""

    if not e.detail1:
        return

    print(f"\n{as_string(e.source)} is now focused")
    ancestors = []
    parent = e.source
    while parent:
        grandparent = Atspi.Accessible.get_parent(parent)
        ancestors.append(as_string(parent))
        if Atspi.Accessible.get_role(parent) == Atspi.Role.APPLICATION:
            break
        parent = grandparent

    ancestors.reverse()
    indent = 0
    for ancestor in ancestors:
        print(f"{' ' * indent}--> {ancestor}")
        indent += 2

    if Atspi.Accessible.get_role(e.source) == Atspi.Role.TERMINAL:
        print("Exiting.")
        Atspi.event_quit()

def main():
    """Starts the focus dumper and waits for events."""

    listener = Atspi.EventListener.new(on_event)
    listener.register("object:state-changed:focused")
    print("Listening for focus events. Return focus to your terminal to exit.")
    Atspi.event_main()

if __name__ == "__main__":
    main()
