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

import sys

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib


def as_string(
    obj: Atspi.Accessible, prefix: str, expected_parent: Atspi.Accessible | None = None
) -> str:
    "Convert an accessible object to a string representation."

    indent = " " * (len(prefix) + 1)
    result = (
        f"{prefix} "
        f"{get_role_as_string(obj)} "
        f"NAME: '{get_name(obj)}' "
        f"DESCRIPTION: '{get_description(obj)}' "
        f"ACCESSIBLE ID: '{get_accessible_id(obj)}'"
    )

    parent_info = get_parent_info(obj, expected_parent)
    if parent_info:
        result += f"\n{indent}{parent_info}"

    result += (
        f"\n{indent}INTERFACES: {get_interfaces_as_string(obj)}"
        f"\n{indent}STATES: {get_states_as_string(obj)}"
        f"\n{indent}ATTRIBUTES: {get_attributes_as_string(obj)}"
        f"\n{indent}LOCALE: '{get_locale(obj)}'"
        f"\n{indent}RECT: {get_rect_as_string(obj)}"
    )

    relations = get_relations_as_string(obj)
    if relations:
        result += f"\n{indent}RELATIONS: {relations}"

    selection_info = get_selection_info(obj, indent)
    if selection_info:
        result += f"\n{indent}{selection_info}"

    if supports_interface(obj, Atspi.Accessible.get_text_iface):
        result += f"\n{indent}TEXT: {get_text(obj)}"
        text_attrs = get_text_attributes(obj, indent)
        if text_attrs:
            result += f"\n{indent}{text_attrs}"

    table_info = get_table_info(obj, indent)
    if table_info:
        result += f"\n{indent}{table_info}"

    table_cell_info = get_table_cell_info(obj, indent)
    if table_cell_info:
        result += f"\n{indent}{table_cell_info}"

    return result


def supports_interface(obj: Atspi.Accessible, getter) -> bool:
    "Check if an accessible object supports a specific interface."

    try:
        iface = getter(obj)
    except GLib.GError:
        return False
    return iface is not None


INTERFACE_CHECKS = [
    (Atspi.Accessible.get_action_iface, "Action"),
    (Atspi.Accessible.get_collection_iface, "Collection"),
    (Atspi.Accessible.get_component_iface, "Component"),
    (Atspi.Accessible.get_document_iface, "Document"),
    (Atspi.Accessible.get_editable_text_iface, "EditableText"),
    (Atspi.Accessible.get_hyperlink, "Hyperlink"),
    (Atspi.Accessible.get_hypertext_iface, "Hypertext"),
    (Atspi.Accessible.get_image_iface, "Image"),
    (Atspi.Accessible.get_selection_iface, "Selection"),
    (Atspi.Accessible.get_table_iface, "Table"),
    (Atspi.Accessible.get_table_cell, "TableCell"),
    (Atspi.Accessible.get_text_iface, "Text"),
    (Atspi.Accessible.get_value_iface, "Value"),
]


def get_interfaces_as_string(obj: Atspi.Accessible) -> str:
    "Get the supported interfaces of an accessible object as a string."

    ifaces = [name for getter, name in INTERFACE_CHECKS if supports_interface(obj, getter)]
    return ", ".join(ifaces) or "(none)"


def get_selection_info(obj: Atspi.Accessible, indent: str) -> str:
    "Get selection interface details if the selection interface is supported."

    if not supports_interface(obj, Atspi.Accessible.get_selection_iface):
        return ""

    try:
        count = Atspi.Selection.get_n_selected_children(obj)
    except GLib.GError as error:
        return f"SELECTION: Exception in get_n_selected_children: {error}"

    result = f"SELECTION: SELECTED CHILD COUNT: {count}"

    def format_selected_child(index: int) -> str:
        try:
            child = Atspi.Selection.get_selected_child(obj, index)
        except GLib.GError as error:
            return f"SELECTED CHILD [{index}]: Exception: {error}"
        if child is None:
            return f"SELECTED CHILD [{index}]: (null)"
        return f"SELECTED CHILD [{index}]: {get_role_as_string(child)} NAME: '{get_name(child)}'"

    if count <= 10:
        indices = range(count)
    else:
        indices = list(range(5)) + list(range(count - 5, count))

    for i in indices:
        if i == count - 5 and count > 10:
            result += f"\n{indent}  ... ({count - 10} selected children omitted) ..."
        result += f"\n{indent}  {format_selected_child(i)}"

    return result


def get_table_info(obj: Atspi.Accessible, _indent: str) -> str:
    "Get table interface details if the table interface is supported."

    if not supports_interface(obj, Atspi.Accessible.get_table_iface):
        return ""

    try:
        n_rows = Atspi.Table.get_n_rows(obj)
    except GLib.GError as error:
        return f"TABLE: Exception in get_n_rows: {error}"

    try:
        n_cols = Atspi.Table.get_n_columns(obj)
    except GLib.GError as error:
        return f"TABLE: ROWS: {n_rows}, Exception in get_n_columns: {error}"

    return f"TABLE: ROWS: {n_rows}, COLUMNS: {n_cols}"


def get_table_cell_info(obj: Atspi.Accessible, _indent: str) -> str:
    "Get table cell interface details if the table cell interface is supported."

    if not supports_interface(obj, Atspi.Accessible.get_table_cell):
        return ""

    try:
        success, row, column = Atspi.TableCell.get_position(obj)
    except GLib.GError as error:
        return f"TABLE CELL: Exception in get_position: {error}"

    if not success:
        return "TABLE CELL: ROW: (unknown), COLUMN: (unknown)"

    result = f"TABLE CELL: ROW: {row}, COLUMN: {column}"

    try:
        row_span = Atspi.TableCell.get_row_span(obj)
        col_span = Atspi.TableCell.get_column_span(obj)
    except GLib.GError as error:
        return f"{result}, Exception in get_span: {error}"

    if row_span != 1 or col_span != 1:
        result += f", ROW SPAN: {row_span}, COLUMN SPAN: {col_span}"

    return result


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
            [f"{get_role_as_string(target)} NAME: '{get_name(target)}'" for target in targets]
        )
        result.append(f"{relation.get_relation_type().value_nick}: {target_addresses}")

    return " ".join(result)


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


def get_accessible_id(obj: Atspi.Accessible) -> str:
    """Get the accessible id of obj"""

    try:
        result = Atspi.Accessible.get_accessible_id(obj)
    except GLib.GError as error:
        print(f"Exception in get_accessible_id: {error}")
        return ""

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
        result.append(f"{key}={value if value is not None else '(null)'}")

    return ", ".join(result)


def get_role_as_string(obj: Atspi.Accessible) -> str:
    "Get the role of an accessible object."

    try:
        return Atspi.Accessible.get_role(obj).value_name
    except GLib.GError as error:
        print(f"Exception in get_role: {error}")
        return "(unknown role)"


def get_locale(obj: Atspi.Accessible) -> str:
    """Returns the locale of obj"""

    try:
        locale = Atspi.Accessible.get_object_locale(obj)
    except GLib.GError as error:
        print(f"Exception in get_object_locale: {error}")
        return ""

    return locale


def get_text(obj: Atspi.Accessible) -> str:
    "Get the text of an accessible object."

    length = Atspi.Text.get_character_count(obj)
    result = Atspi.Text.get_text(obj, 0, length)
    result = result.replace("\ufffc", "[OBJ]")
    result = result.replace("\n", "\\n")
    if len(result) > 80:
        result = result[:80] + "[...]"
    return f"'{result}'"


def get_text_attributes(obj: Atspi.Accessible, indent: str) -> str:
    "Get the text attribute runs for an accessible object."

    try:
        length = Atspi.Text.get_character_count(obj)
    except GLib.GError:
        return ""

    if length <= 0:
        return ""

    runs = []
    offset = 0
    while offset < length:
        try:
            attrs, start, end = Atspi.Text.get_attribute_run(obj, offset, True)
        except GLib.GError as error:
            runs.append(f"Exception at offset {offset}: {error}")
            break

        if end <= offset:
            break

        if attrs:
            formatted = ", ".join(f"{k}={v}" for k, v in attrs.items())
            runs.append(f"[{start}-{end}] {formatted}")

        offset = end

    if not runs:
        return ""

    result = f"TEXT ATTRIBUTES: {len(runs)} run(s)"
    for run in runs:
        result += f"\n{indent}  {run}"
    return result


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


def get_parent_info(obj: Atspi.Accessible, expected_parent: Atspi.Accessible | None) -> str:
    "Get parent info, only if the parent is unexpected or missing."

    parent = get_parent(obj)
    if parent is None and expected_parent is None:
        return ""

    if parent is None:
        return "**NO PARENT** (expected one)"

    if expected_parent is None:
        return f"PARENT: {get_role_as_string(parent)} (unexpected; object has no expected parent)"

    if parent == expected_parent:
        return ""

    return f"**UNEXPECTED PARENT**: {get_role_as_string(parent)} NAME: '{get_name(parent)}'"


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


def print_tree(
    root: Atspi.Accessible,
    indent: int = 0,
    expected_parent: Atspi.Accessible | None = None,
) -> None:
    "Print the tree structure of accessible objects."

    clear_cache_single(root)
    prefix = f"{'  ' * indent}-->"
    print(f"{as_string(root, prefix, expected_parent)}")
    for child in get_children(root):
        print_tree(child, indent + 1, root)


def get_desktop_apps() -> list[Atspi.Accessible]:
    "Get all accessible applications from the desktop."

    try:
        desktop = Atspi.get_desktop(0)
    except GLib.GError as error:
        print(f"Exception getting desktop from Atspi: {error}")
        return []

    return get_children(desktop)


def print_available_apps(apps: list[Atspi.Accessible]) -> None:
    "Print the list of available accessible applications."

    print(f"Desktop has {len(apps)} accessible application(s):")
    for i, app in enumerate(apps):
        print(f"  {i + 1}. {get_name(app, False)}")


def find_application_with_name(app_name: str) -> Atspi.Accessible:
    "Find the accessible application with the specified name."

    apps = get_desktop_apps()
    for app in apps:
        if get_name(app, False) == app_name:
            return app

    print(f"Application '{app_name}' not found.")
    print_available_apps(apps)
    return None


def main():
    """Starts the tree dumper and waits for events."""

    if len(sys.argv) != 2:
        print("Usage: dump-tree.py <APP_NAME>")
        print()
        print_available_apps(get_desktop_apps())
        sys.exit(1)

    app = find_application_with_name(sys.argv[1])
    if not app:
        sys.exit(1)

    print_tree(app)
    print("Tree dump complete.")


if __name__ == "__main__":
    main()
