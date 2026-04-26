#!/usr/bin/python
# generate_dbus_documentation.py
#
# Generate markdown documentation for Orca's D-Bus remote controller.
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

"""Generate markdown documentation for Orca's D-Bus remote controller."""

import ast
import os
import sys
from pathlib import Path

SERVICE_NAME = "org.gnome.Orca.Service"
SERVICE_PATH = "/org/gnome/Orca/Service"
SERVICE_INTERFACE = "org.gnome.Orca.Service"
INTERFACE_PREFIX = "org.gnome.Orca"

DBUS_SERVICE_FILE = "dbus_service.py"
META_PROTOCOL_MARKER_CLASS = "OrcaModuleDBusInterface"

_DECORATOR_KINDS = ("command", "parameterized_command", "getter", "setter")
_RESERVED_PARAMS = frozenset({"self", "script", "event"})

_BUILTIN_DBUS_SIGNATURE = {
    "bool": "b",
    "int": "i",
    "float": "d",
    "str": "s",
}


def _decorator_kind(decorator):
    """Returns the @dbus_service.X kind of a decorator node, or None."""

    if isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Name):
        if decorator.value.id == "dbus_service" and decorator.attr in _DECORATOR_KINDS:
            return decorator.attr
    return None


def _classify_method(func_node):
    """Returns the kind for a function with a @dbus_service.X decorator, or None."""

    for dec in func_node.decorator_list:
        kind = _decorator_kind(dec)
        if kind is not None:
            return kind
    return None


def _camelize(snake):
    """Returns the CamelCase form of a snake_case name."""

    return "".join(word.capitalize() for word in snake.split("_"))


def _strip_property_prefix(name):
    """Drops a leading get_ or set_ used to derive a property name."""

    return name[4:] if name.startswith(("get_", "set_")) else name


def _annotation_str(node):
    """Renders an AST annotation node as Python source, or '' if absent."""

    return ast.unparse(node) if node is not None else ""


def _dbus_signature(annotation):
    """Converts a Python annotation string (e.g. ``list[str]``) to its D-Bus signature."""

    if not annotation:
        return ""
    try:
        tree = ast.parse(annotation, mode="eval")
    except SyntaxError:
        return ""
    return _signature_from_node(tree.body)


def _signature_from_node(node):
    """Walks an AST type expression and returns a D-Bus signature, or '' if unmappable."""

    if isinstance(node, ast.Name):
        return _BUILTIN_DBUS_SIGNATURE.get(node.id, "")
    if isinstance(node, ast.Constant) and node.value is None:
        return ""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        # Strip Optional / T | None — return whichever side resolves.
        return _signature_from_node(node.left) or _signature_from_node(node.right)
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        outer = node.value.id
        slice_node = node.slice
        if outer == "list":
            inner = _signature_from_node(slice_node)
            return f"a{inner}" if inner else ""
        if outer == "tuple":
            elts = slice_node.elts if isinstance(slice_node, ast.Tuple) else [slice_node]
            inner = "".join(_signature_from_node(elt) for elt in elts)
            return f"({inner})" if inner and all(inner) else ""
        if outer == "dict" and isinstance(slice_node, ast.Tuple) and len(slice_node.elts) == 2:
            key = _signature_from_node(slice_node.elts[0])
            value = _signature_from_node(slice_node.elts[1])
            return f"a{{{key}{value}}}" if key and value else ""
    return ""


def _user_facing_args(func_node):
    """Yields (name, annotation_str) for non-reserved positional args (notify_user kept)."""

    for arg in list(func_node.args.posonlyargs) + list(func_node.args.args):
        if arg.arg in _RESERVED_PARAMS:
            continue
        yield arg.arg, _annotation_str(arg.annotation)


def _value_annotation(setter_node):
    """Returns the annotation string of a setter's value parameter."""

    for arg in list(setter_node.args.posonlyargs) + list(setter_node.args.args):
        if arg.arg == "self":
            continue
        return _annotation_str(arg.annotation)
    return ""


def _module_members(class_node):
    """Returns (commands, parameterized, getters, setters) for one class."""

    commands = []
    parameterized = []
    getters = {}
    setters = {}

    for item in class_node.body:
        if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        kind = _classify_method(item)
        if kind is None:
            continue
        doc = ast.get_docstring(item) or ""

        if kind == "command":
            commands.append((_camelize(item.name), doc))
        elif kind == "parameterized_command":
            args = list(_user_facing_args(item))
            ret = _annotation_str(item.returns)
            parameterized.append((_camelize(item.name), doc, args, ret))
        elif kind == "getter":
            name = _camelize(_strip_property_prefix(item.name))
            getters[name] = (_annotation_str(item.returns), doc)
        elif kind == "setter":
            name = _camelize(_strip_property_prefix(item.name))
            setters[name] = (_value_annotation(item), doc)

    return commands, parameterized, getters, setters


def find_modules(orca_src_dir):
    """Yields (class_name, commands, parameterized, getters, setters) per D-Bus module."""

    for path in sorted(Path(orca_src_dir).glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            members = _module_members(node)
            if any(members):
                yield (node.name, *members)


def _is_service_interface_class(class_node):
    """Returns True if class_node is decorated with @dbus_interface('org.gnome.Orca.Service')."""

    for decorator in class_node.decorator_list:
        if not (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name)):
            continue
        if decorator.func.id != "dbus_interface" or not decorator.args:
            continue
        first_arg = decorator.args[0]
        if isinstance(first_arg, ast.Constant) and first_arg.value == SERVICE_INTERFACE:
            return True
    return False


def _uses_meta_protocol(orca_src_dir):
    """Returns True if the meta-protocol marker class is present in dbus_service.py."""

    path = Path(orca_src_dir) / DBUS_SERVICE_FILE
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return any(
        isinstance(node, ast.ClassDef) and node.name == META_PROTOCOL_MARKER_CLASS
        for node in ast.walk(tree)
    )


def find_service_methods(orca_src_dir):
    """Returns sorted (name, description, [(arg, ann), ...], ret) for the service interface."""

    path = Path(orca_src_dir) / DBUS_SERVICE_FILE
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and _is_service_interface_class(node)):
            continue
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # Service methods are CamelCase (Quit, GetVersion, ...); skip helpers.
            if not item.name[:1].isupper():
                continue
            doc = ast.get_docstring(item) or ""
            args = [(name, ann) for name, ann in _user_facing_args(item) if name != "notify_user"]
            ret = _annotation_str(item.returns)
            out.append((item.name, doc, args, ret))
    out.sort(key=lambda entry: entry[0])
    return out


def _generalize_doc_for_readwrite(doc):
    """Rewrites a getter-style or setter-style docstring to cover both read and write."""

    if doc.startswith("Returns "):
        return "Gets/Sets " + doc[len("Returns ") :]
    if doc.startswith("Sets "):
        return "Gets/Sets " + doc[len("Sets ") :]
    return doc


def _format_signature(args):
    """Renders an argument list as a markdown-formatted signature using D-Bus types."""

    parts = []
    for name, ann in args:
        sig = _dbus_signature(ann)
        parts.append(f"`{name}` ({sig})" if sig else f"`{name}`")
    return ", ".join(parts)


def _format_service_section(methods, *, meta_protocol):
    lines = [
        "## Service-Level Commands",
        "",
        f"These commands are available directly on the main service object at `{SERVICE_PATH}`.",
        "",
    ]
    for name, description, in_args, ret in methods:
        desc_part = f" {description}" if description else ""
        if meta_protocol:
            lines.append(f"- **`{name}`:**{desc_part}")
        else:
            sig = _format_signature(in_args)
            ret_sig = _dbus_signature(ret)
            ret_part = f" → `{ret_sig}`" if ret_sig else ""
            colon = ":" if description else ""
            lines.append(f"- **`{name}`**({sig}){ret_part}{colon}{desc_part}")
    lines.append("")
    return "\n".join(lines)


def _format_module_section(name, commands, parameterized, getters, setters, *, meta_protocol):
    object_path = f"{SERVICE_PATH}/{name}"
    lines = [
        f"### {name}",
        "",
        f"**Object Path:** `{object_path}`",
        "",
    ]
    if not meta_protocol:
        lines += [f"**Interface:** `{INTERFACE_PREFIX}.{name}`", ""]

    if commands:
        lines.append("#### Commands")
        lines.append("")
        if meta_protocol:
            lines += [
                "**Method:** `org.gnome.Orca.Module.ExecuteCommand`",
                "",
                "**Parameters:** `CommandName` (string), "
                "[`NotifyUser`](remote-controller.md#user-notification-applicability) (boolean)",
                "",
            ]
        for cname, description in sorted(commands):
            if description:
                lines.append(f"- **`{cname}`:** {description}")
            else:
                lines.append(f"- **`{cname}`**")
        lines.append("")

    if parameterized:
        lines.append("#### Parameterized Commands")
        lines.append("")
        if meta_protocol:
            lines += [
                "**Method:** `org.gnome.Orca.Module.ExecuteParameterizedCommand`",
                "",
            ]
        for cname, description, args, ret in sorted(parameterized):
            if meta_protocol:
                # Match the live-bus tool's old output: include notify_user, render
                # Python annotation strings, no trailing period.
                py_parts = [f"`{name}` ({ann})" if ann else f"`{name}`" for name, ann in args]
                py_params = ", ".join(py_parts)
                desc_part = f" {description}" if description else ""
                suffix = f" Parameters: {py_params}" if py_params else ""
                lines.append(f"- **`{cname}`:**{desc_part}{suffix}")
            else:
                native_args = [(name, ann) for name, ann in args if name != "notify_user"]
                params = _format_signature(native_args)
                suffix = f" Parameters: {params}." if params else ""
                ret_sig = _dbus_signature(ret)
                ret_part = f" → `{ret_sig}`" if ret_sig else ""
                colon = ":" if description else ""
                desc_part = f" {description}" if description else ""
                lines.append(f"- **`{cname}`**{ret_part}{colon}{desc_part}{suffix}")
        lines.append("")

    if getters or setters:
        if meta_protocol:
            lines += [
                "#### Settings",
                "",
                "**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / "
                "`org.gnome.Orca.Module.ExecuteRuntimeSetter`",
                "",
                "**Parameters:** `PropertyName` (string), `Value` (variant, setter only)",
                "",
            ]
        else:
            lines += ["#### Properties", ""]

        for prop in sorted(set(getters) | set(setters)):
            has_get = prop in getters
            has_set = prop in setters
            # Setter docs typically include range/default info; prefer them when present.
            doc = setters[prop][1] if has_set else getters[prop][1]
            ann = getters[prop][0] if has_get else setters[prop][0]
            sig = _dbus_signature(ann)
            if meta_protocol:
                if has_get and has_set:
                    doc = _generalize_doc_for_readwrite(doc)
                    annotation = ""
                elif has_get:
                    annotation = " (getter only)"
                else:
                    annotation = " (setter only)"
                desc_part = f" {doc}" if doc else ""
                lines.append(f"- **`{prop}`:**{desc_part}{annotation}")
            else:
                for prefix in ("Returns ", "Gets ", "Sets "):
                    if doc.startswith(prefix):
                        rest = doc[len(prefix) :]
                        doc = rest[:1].upper() + rest[1:]
                        break
                access = (
                    "read/write"
                    if has_get and has_set
                    else "read-only"
                    if has_get
                    else "write-only"
                )
                type_part = f"`{sig}`, " if sig else ""
                desc_part = f": {doc}" if doc else ""
                lines.append(f"- **`{prop}`** ({type_part}{access}){desc_part}")
        lines.append("")

    return "\n".join(lines)


def generate_documentation(orca_src_dir):
    """Walks the source tree and renders the service interface plus each registered module."""

    meta_protocol = _uses_meta_protocol(orca_src_dir)

    header = [
        "# Orca D-Bus Service Commands Reference",
        "",
        "The service can be accessed at:",
        "",
        f"- **Service Name:** `{SERVICE_NAME}`",
        f"- **Main Object Path:** `{SERVICE_PATH}`",
        f"- **Module Object Paths:** `{SERVICE_PATH}/ModuleName`",
    ]
    if not meta_protocol:
        header.append(f"- **Module Interface Names:** `{INTERFACE_PREFIX}.<ModuleName>`")
    header += [
        "",
        "Additional information about using the remote controller can be found in "
        "[remote-controller.md](remote-controller.md).",
        "",
        "---",
        "",
    ]
    sections = list(header)

    sections.append(
        _format_service_section(find_service_methods(orca_src_dir), meta_protocol=meta_protocol)
    )
    sections.append("---")
    sections.append("")

    sections.append("## Modules")
    sections.append("")
    if meta_protocol:
        sections.append(
            "Each module exposes commands, getters, and setters on its object "
            f"at `{SERVICE_PATH}/ModuleName`."
        )
        sections.append("")
    for entry in sorted(find_modules(orca_src_dir), key=lambda e: e[0]):
        sections.append(_format_module_section(*entry, meta_protocol=meta_protocol))
        sections.append("---")
        sections.append("")

    return "\n".join(sections)


def main():
    """Main entry point."""

    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    src_dir = os.path.join(parent_dir, "src", "orca")
    output_file = os.path.join(parent_dir, "docs", "remote-controller-commands.md")

    print("Generating D-Bus documentation...", file=sys.stderr)
    try:
        documentation = generate_documentation(src_dir)
    except OSError as error:
        print(f"Error reading source files: {error}", file=sys.stderr)
        return 1

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(documentation)
        print(f"Documentation written to {output_file}", file=sys.stderr)
        return 0
    except OSError as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
