#!/usr/bin/python
# dump-tree.py
#
# Command-line tool to dump the tree of accessible objects for a given application.
# Usage: dump-tree.py <APP_NAME>
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

"""Command-line tool to dump the tree of accessible objects for a given application."""

from datetime import datetime
import sys

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

def as_string(obj: Atspi.Accessible, prefix: str) -> str:
    "Convert an accessible object to a string representation."

    timestamp = f"{datetime.now():%H:%M:%S}"
    indent = " " * (len(prefix) + len(timestamp) + 2)
    return (f"{timestamp} {prefix} "
            f"{get_role_as_string(obj)} ({hex(id(obj))}) "
            f"NAME: '{get_name(obj)}' "
            f"DESCRIPTION: '{get_description(obj)}'"
            f"\n{indent}PARENT: {get_parent_as_string(obj)} "
            f"INDEX IN PARENT: {get_index_in_parent(obj)}"
            f"\n{indent}ATTRIBUTES: {get_attributes_as_string(obj)}"
            f"\n{indent}RECT: {get_rect_as_string(obj)}"
            f"\n{indent}STATES: {get_states_as_string(obj)}"
            f"\n{indent}RELATIONS: {get_relations_as_string(obj)}"
            f"\n{indent}TEXT: {get_text(obj)}"
            )

def get_rect_as_string(obj: Atspi.Accessible) -> str:
    "Get the rectangle dimensions of an accessible object as a string."

    try:
        if Atspi.Accessible.get_role(obj) == Atspi.Role.APPLICATION:
            return ""
    except GLib.GError as error:
        print(f"Exception in get_role: {error}")
        return ""

    try:
        rect = Atspi.Component.get_extents(obj, Atspi.CoordType.WINDOW)
    except GLib.GError as error:
        print(f"Exception in get_extents: {error}")
        return ""
    return f"X:{rect.x}, Y:{rect.y}, WIDTH:{rect.width}, HEIGHT:{rect.height}"

def get_relations_as_string(obj: Atspi.Accessible) -> str:
    "Get the relations of an accessible object as a string."

    try:
        relations = Atspi.Accessible.get_relation_set(obj)
    except GLib.GError as error:
        print(f"Exception in get_relation_set: {error}")
        return ""

    result = []
    for relation in relations:
        if relation.get_n_targets() == 0:
            continue
        targets = [relation.get_target(i) for i in range(relation.get_n_targets())]
        target_addresses = ", ".join(
            [f"{get_role_as_string(target)} ({hex(id(target))})" for target in targets]
        )
        result.append(f"{relation.get_relation_type().value_nick}: {target_addresses}")

    return " ".join(result) or "(none)"

def get_states_as_string(obj: Atspi.Accessible) -> str:
    "Get the states of an accessible object as a string."

    try:
        state_set = Atspi.Accessible.get_state_set(obj)
    except GLib.GError as error:
        print(f"Exception in get_state_set: {error}")
        return ""
    return " ".join([s.value_nick for s in state_set.get_states()]) or "(none)"

def get_name(obj: Atspi.Accessible, fallback_on_labelled_by: bool = True) -> str:
    "Get the name of an accessible object."

    try:
        name = Atspi.Accessible.get_name(obj)
    except GLib.GError as error:
        print(f"Exception in get_name: {error}")
        return ""

    if name:
        return name

    result = "(none)"
    if not fallback_on_labelled_by:
        return result

    try:
        relations = Atspi.Accessible.get_relation_set(obj)
    except GLib.GError as error:
        print(f"Exception in get_relation_set: {error}")
        return ""

    for relation in relations:
        if relation.get_relation_type() != Atspi.RelationType.LABELLED_BY:
            continue
        targets = [relation.get_target(i) for i in range(relation.get_n_targets())]
        result = " ".join([get_name(target, False) for target in targets])
        if result:
            result += " (from labelled-by relation)"

    return result

def get_description(obj: Atspi.Accessible, fallback_on_described_by: bool = True) -> str:
    "Get the description of an accessible object."

    try:
        description = Atspi.Accessible.get_description(obj)
    except GLib.GError as error:
        print(f"Exception in get_description: {error}")
        return ""
    if description:
        return description

    result = "(none)"
    if not fallback_on_described_by:
        return result

    try:
        relations = Atspi.Accessible.get_relation_set(obj)
    except GLib.GError as error:
        print(f"Exception in get_relation_set: {error}")
        return ""

    for relation in relations:
        if relation.get_relation_type() != Atspi.RelationType.DESCRIBED_BY:
            continue
        targets = [relation.get_target(i) for i in range(relation.get_n_targets())]
        result = " ".join([get_name(target, False) for target in targets])
        if result:
            result += " (from described-by relation)"

    return result

def get_attributes_as_string(obj: Atspi.Accessible) -> str:
    "Get the attributes of an accessible object as a string."

    try:
        attributes = Atspi.Accessible.get_attributes(obj)
    except GLib.GError as error:
        print(f"Exception in get_attributes: {error}")
        return ""

    if not attributes:
        return "(none)"

    result = []
    for key, value in attributes.items():
        if value is None:
            value = "(null)"
        result.append(f"{key}={value}")

    return ", ".join(result)

def get_role_as_string(obj: Atspi.Accessible) -> str:
    "Get the role of an accessible object."

    try:
        return Atspi.Accessible.get_role(obj).value_name
    except GLib.GError as error:
        print(f"Exception in get_role: {error}")
        return "(unknown role)"

def get_text(obj: Atspi.Accessible) -> str:
    "Get the text of an accessible object."

    try:
        length = Atspi.Text.get_character_count(obj)
        result = Atspi.Text.get_text(obj, 0, length)
    except GLib.GError:
        return "(not implemented)"

    result = result.replace("\n", "\\n")
    if len(result) > 80:
        result = result[:80] + "[...]"
    return f"'{result}'"

def get_parent(obj: Atspi.Accessible) -> Atspi.Accessible:
    "Get the parent of an accessible object."

    try:
        if Atspi.Accessible.get_role(obj) == Atspi.Role.APPLICATION:
            return None
    except GLib.GError as error:
        print(f"Exception in get_role: {error}")
        return None

    try:
        return Atspi.Accessible.get_parent(obj)
    except GLib.GError as error:
        print(f"Exception in get_parent: {error}")
        return None

def get_parent_as_string(obj: Atspi.Accessible) -> str:
    "Get the parent of an accessible object."

    parent = get_parent(obj)
    if parent:
        return f"{get_role_as_string(parent)} ({hex(id(parent))})"
    return ""

def get_index_in_parent(obj: Atspi.Accessible) -> int:
    "Get the index of an accessible object in its parent's children."

    parent = get_parent(obj)
    if not parent:
        return -1

    try:
        index = Atspi.Accessible.get_index_in_parent(obj)
    except GLib.GError as error:
        print(f"Exception in get_index_in_parent: {error}")
        return -1

    if index < 0:
        print(f"WARNING: Object {hex(id(obj))} has invalid index in parent {hex(id(parent))}")
        return -1

    child = Atspi.Accessible.get_child_at_index(parent, index)
    if child != obj:
        print(f"WARNING: Object {hex(id(obj))} at index {index} in parent {hex(id(parent))} "
              f"is not the expected child {hex(id(child))}")

    return index

def get_children(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
    "Get the children of an accessible object."

    children = []
    try:
        count = Atspi.Accessible.get_child_count(obj)
    except GLib.GError as error:
        print(f"Exception in get_child_count: {error}")
        return []

    for i in range(count):
        try:
            children.append(Atspi.Accessible.get_child_at_index(obj, i))
        except GLib.GError as error:
            print(f"Exception in get_child_at_index: {error}")
            return children

    return children

def clear_cache_single(obj: Atspi.Accessible) -> None:
    "Clear the cache for a single accessible object."

    try:
        Atspi.Accessible.clear_cache_single(obj)
    except GLib.GError as error:
        print(f"Exception in clear_cache_single: {error}")

def print_tree(root: Atspi.Accessible, indent: int = 0) -> None:
    "Print the tree structure of accessible objects."

    clear_cache_single(root)
    prefix = f"{'  ' * indent}-->"
    print(f"{as_string(root, prefix)}")
    for child in get_children(root):
        print_tree(child, indent + 1)

def find_application_with_name(app_name: str) -> Atspi.Accessible:
    "Find the accessible application with the specified name."

    try:
        desktop = Atspi.get_desktop(0)
    except GLib.GError as error:
        print(f"Exception getting desktop from Atspi: {error}")
        return None

    apps = []
    for child in get_children(desktop):
        if get_name(child, False) == app_name:
            return child
        apps.append(child)

    apps_as_string = "\n".join([f"{i + 1}. {get_name(app, False)}" for i, app in enumerate(apps)])
    print(
        f"Application '{app_name}' not found.\nDesktop has {len(apps)} accessible applications:\n"
        f"{apps_as_string}"
    )
    return None

def main():
    """Starts the tree dumper and waits for events."""

    if len(sys.argv) != 2:
        print("Usage: dump-tree.py <APP_NAME>")
        sys.exit(1)

    app = find_application_with_name(sys.argv[1])
    if not app:
        sys.exit(1)

    print_tree(app)
    print("Tree dump complete.")

if __name__ == "__main__":
    main()
