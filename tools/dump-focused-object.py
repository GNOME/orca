#!/usr/bin/python
# dump-focused-object.py
#
# Command-line tool to dump the focused object, optionally with its ancestors.
# This tool listens for focus events and prints the focused object. Pass -a
# (or --ancestry) to also print the accessibility tree from the application
# down to the focused object.
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

"""Command-line tool to dump the focused object, optionally with its ancestors."""

import argparse
import signal

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib


def safe_call(func, default=""):
    """Calls func() and returns its result, or default if Atspi raises GError."""

    try:
        return func()
    except GLib.GError as error:
        return f"({error})" if default == "" else default


def as_string(obj):
    """Convert an accessible object to a string representation."""

    role = safe_call(lambda: Atspi.Accessible.get_role(obj).value_name)
    help_text = safe_call(lambda: Atspi.Accessible.get_help_text(obj))
    return (
        f"{role} "
        f"name:'{get_name(obj)}' "
        f"description:'{get_description(obj)}' "
        f"help text: '{help_text}'"
    )


def get_name(obj):
    """Get the name of an accessible object."""

    return _name_or_description_from(obj, Atspi.Accessible.get_name, Atspi.RelationType.LABELLED_BY)


def get_description(obj):
    """Get the description of an accessible object."""

    return _name_or_description_from(
        obj, Atspi.Accessible.get_description, Atspi.RelationType.DESCRIBED_BY
    )


def _name_or_description_from(obj, getter, relation_type):
    """Returns the result of getter(obj), falling back to relation targets' names."""

    value = safe_call(lambda: getter(obj))
    if value:
        return value

    relations = safe_call(lambda: Atspi.Accessible.get_relation_set(obj), default=[])
    for relation in relations:
        if relation.get_relation_type() != relation_type:
            continue
        targets = [relation.get_target(i) for i in range(relation.get_n_targets())]
        names = [safe_call(lambda t=t: Atspi.Accessible.get_name(t)) or "" for t in targets]
        return " ".join(names)

    return ""


def make_event_handler(dump_ancestry):
    """Returns a focus event handler that optionally dumps the ancestry."""

    def on_event(e):
        if not e.detail1:
            return

        print(f"\n{as_string(e.source)} is now focused")
        if dump_ancestry:
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

    return on_event


def main():
    """Starts the focus dumper and waits for events."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-a",
        "--ancestry",
        action="store_true",
        help="Also dump the ancestry of the focused object.",
    )
    args = parser.parse_args()

    listener = Atspi.EventListener.new(make_event_handler(args.ancestry))
    listener.register("object:state-changed:focused")

    def on_sigint():
        Atspi.event_quit()
        return GLib.SOURCE_REMOVE

    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, on_sigint)
    print("Listening for focus events. Press Ctrl+C or focus the terminal to exit.")
    Atspi.event_main()


if __name__ == "__main__":
    main()
