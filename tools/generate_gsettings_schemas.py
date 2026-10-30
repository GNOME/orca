#!/usr/bin/python
# generate_gsettings_schemas.py
#
# Generate GSettings schema XML files by parsing @gsetting decorators.
# Invoked by data/meson.build as a build-time custom target.
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

# pylint: disable=too-many-branches
# pylint: disable=too-many-nested-blocks

"""Generate GSettings schema XML files by parsing @gsetting decorators."""

import argparse
import ast
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

REQUIRED_SETTING_FIELDS = {"key", "schema", "default"}


def _extract_gsettings_schemas(tree: ast.Module) -> list[tuple[str, str]]:
    """Extract @gsettings_schema class decorator arguments from a parsed AST."""

    schemas: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if isinstance(func, ast.Attribute):
                if func.attr != "gsettings_schema":
                    continue
            elif isinstance(func, ast.Name):
                if func.id != "gsettings_schema":
                    continue
            else:
                continue

            schema_id = None
            schema_name = None

            if decorator.args and isinstance(decorator.args[0], ast.Constant):
                schema_id = str(decorator.args[0].value)

            for keyword in decorator.keywords:
                if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                    schema_name = str(keyword.value.value)

            if schema_id and schema_name:
                schemas.append((schema_id, schema_name))

    return schemas


def _collect_class_constants(tree: ast.Module) -> dict[str, Any]:
    """Collect class-level NAME = CONSTANT assignments for resolving references."""

    constants: dict[str, Any] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
                continue
            target = stmt.targets[0]
            if isinstance(target, ast.Name) and isinstance(stmt.value, ast.Constant):
                constants[target.id] = stmt.value.value
    return constants


def _imported_classes(tree: ast.Module, source_path: Path) -> dict[str, tuple[Path, str]]:
    """Map each name bound by a top-level 'from .module import Name' to its file and name."""

    imported: dict[str, tuple[Path, str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or node.level != 1 or not node.module:
            continue
        module_path = source_path.parent / f"{node.module}.py"
        for alias in node.names:
            imported[alias.asname or alias.name] = (module_path, alias.name)
    return imported


def _names_bound_by(stmt: ast.stmt) -> list[str]:
    """Return the names a statement directly in a class body binds."""

    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [stmt.name]
    if isinstance(stmt, ast.Assign):
        targets = stmt.targets
    elif isinstance(stmt, (ast.AnnAssign, ast.AugAssign)):
        targets = [stmt.target]
    else:
        return []
    return [
        name.id for target in targets for name in ast.walk(target) if isinstance(name, ast.Name)
    ]


def _resolve_imported_constant(
    node: ast.Attribute,
    imported: dict[str, tuple[Path, str]],
    parsed: dict[Path, ast.Module],
    source_path: Path,
) -> Any:
    """Return the value of ClassName.CONSTANT, with ClassName imported from a sibling module."""

    def unsupported(reason: str) -> ValueError:
        return ValueError(
            f"Cannot resolve {ast.unparse(node)} in {source_path}: {reason}. Only "
            f"ClassName.CONSTANT, with ClassName imported by 'from .module import ClassName' "
            f"and CONSTANT assigned once to a literal in that class, is supported"
        )

    if not isinstance(node.value, ast.Name) or node.value.id not in imported:
        raise unsupported("the class is not imported")

    module_path, class_name = imported[node.value.id]
    if not module_path.is_file():
        raise unsupported(f"{module_path.name} is not a sibling file")
    if module_path not in parsed:
        parsed[module_path] = ast.parse(module_path.read_text(encoding="utf-8"))

    classes = [
        stmt
        for stmt in parsed[module_path].body
        if isinstance(stmt, ast.ClassDef) and stmt.name == class_name
    ]
    if len(classes) != 1:
        raise unsupported(f"{class_name} is defined {len(classes)} times in {module_path.name}")

    bindings = [stmt for stmt in classes[0].body if node.attr in _names_bound_by(stmt)]
    if len(bindings) != 1:
        raise unsupported(f"{node.attr} is bound {len(bindings)} times in {class_name}")

    binding = bindings[0]
    if (
        not isinstance(binding, ast.Assign)
        or len(binding.targets) != 1
        or not isinstance(binding.targets[0], ast.Name)
        or not isinstance(binding.value, ast.Constant)
    ):
        raise unsupported(f"{node.attr} is not assigned a literal")
    return binding.value.value


def _extract_gsetting_decorators(
    tree: ast.Module, source_path: Path, parsed: dict[Path, ast.Module]
) -> list[dict]:
    """Extract @gsetting decorator arguments from a parsed AST."""

    class_constants = _collect_class_constants(tree)
    imported = _imported_classes(tree, source_path)
    settings: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if isinstance(func, ast.Name):
                if func.id != "gsetting":
                    continue
            elif isinstance(func, ast.Attribute):
                if func.attr != "gsetting":
                    continue
            else:
                continue

            setting: dict = {}
            for keyword in decorator.keywords:
                if isinstance(keyword.value, ast.Constant):
                    setting[keyword.arg] = keyword.value.value
                elif isinstance(keyword.value, ast.Name) and keyword.value.id in class_constants:
                    setting[keyword.arg] = class_constants[keyword.value.id]
                elif isinstance(keyword.value, ast.Attribute):
                    setting[keyword.arg] = _resolve_imported_constant(
                        keyword.value, imported, parsed, source_path
                    )
                elif isinstance(keyword.value, ast.Dict):
                    d = {}
                    for k, v in zip(keyword.value.keys, keyword.value.values, strict=True):
                        if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                            d[k.value] = v.value
                    setting[keyword.arg] = d
                elif isinstance(keyword.value, ast.List):
                    items = [
                        elt.value for elt in keyword.value.elts if isinstance(elt, ast.Constant)
                    ]
                    setting[keyword.arg] = items

            missing = REQUIRED_SETTING_FIELDS - set(setting)
            if missing:
                raise ValueError(
                    f"@gsetting on {node.name} in {source_path} missing required fields: {missing}"
                )
            settings.append(setting)

    return settings


def _extract_gsettings_enums(tree: ast.Module) -> dict[str, dict[str, int]]:
    """Extract @gsettings_enum decorator arguments from a parsed AST."""

    enums: dict[str, dict[str, int]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if isinstance(func, ast.Name):
                if func.id != "gsettings_enum":
                    continue
            elif isinstance(func, ast.Attribute):
                if func.attr != "gsettings_enum":
                    continue
            else:
                continue

            enum_id = None
            values: dict[str, int] = {}

            if decorator.args and isinstance(decorator.args[0], ast.Constant):
                enum_id = str(decorator.args[0].value)

            for keyword in decorator.keywords:
                if keyword.arg == "enum_id" and isinstance(keyword.value, ast.Constant):
                    enum_id = str(keyword.value.value)
                elif keyword.arg == "values" and isinstance(keyword.value, ast.Dict):
                    for k, v in zip(keyword.value.keys, keyword.value.values, strict=True):
                        if (
                            isinstance(k, ast.Constant)
                            and isinstance(v, ast.Constant)
                            and isinstance(v.value, int)
                        ):
                            values[str(k.value)] = v.value

            if enum_id and values:
                enums[enum_id] = values

    return enums


def _discover_schemas(
    src_dir: Path,
) -> tuple[dict[str, str], list[dict], dict[str, dict[str, int]]]:
    """Scan source files for @gsettings_schema, @gsetting, and @gsettings_enum decorators."""

    schemas: dict[str, str] = {}
    all_settings: list[dict] = []
    all_enums: dict[str, dict[str, int]] = {}

    orca_dir = src_dir / "orca"
    parsed: dict[Path, ast.Module] = {}
    for source_file in sorted(orca_dir.glob("*.py")):
        text = source_file.read_text(encoding="utf-8")
        if "gsetting" not in text:
            continue

        tree = ast.parse(text)

        for schema_id, schema_name in _extract_gsettings_schemas(tree):
            if schema_name in schemas and schemas[schema_name] != schema_id:
                raise ValueError(
                    f"Schema name '{schema_name}' declared with conflicting IDs: "
                    f"'{schemas[schema_name]}' vs '{schema_id}' in {source_file}"
                )
            schemas[schema_name] = schema_id

        all_settings.extend(_extract_gsetting_decorators(tree, source_file, parsed))

        for enum_id, values in _extract_gsettings_enums(tree).items():
            if enum_id in all_enums and all_enums[enum_id] != values:
                raise ValueError(
                    f"Enum '{enum_id}' declared with conflicting values: "
                    f"{all_enums[enum_id]} vs {values} in {source_file}"
                )
            all_enums[enum_id] = values

    setting_schemas = {s.get("schema") for s in all_settings}
    unknown = setting_schemas - set(schemas)
    if unknown:
        raise ValueError(f"@gsetting decorators reference undeclared schemas: {unknown}")

    return schemas, all_settings, all_enums


def _format_default(gtype: str, default: Any, key_name: str) -> str:  # pylint: disable=too-many-return-statements
    """Format a default value for GSettings schema XML."""

    if gtype == "b":
        return "true" if default else "false"
    if gtype == "d":
        if default is None:
            raise ValueError(f"Missing default for double setting '{key_name}'")
        return str(float(default))
    if gtype == "s":
        if default is None:
            raise ValueError(f"Missing default for string setting '{key_name}'")
        return f"'{default}'"
    if gtype == "i":
        if default is None:
            raise ValueError(f"Missing default for integer setting '{key_name}'")
        return str(int(default))
    if gtype == "a{ss}":
        return "@a{ss} {}"
    if gtype == "a{saas}":
        return "@a{saas} {}"
    if gtype == "a{sv}":
        return "@a{sv} {}"
    if gtype == "as":
        if not default:
            return "@as []"
        items = ", ".join(f"'{v}'" for v in default)
        return f"[{items}]"
    raise ValueError(f"Unsupported gtype '{gtype}' for setting '{key_name}'")


# pylint: disable-next=too-many-locals
def build_schema_tree(src_dir: Path) -> ET.Element:
    """Build schema XML element tree from @gsetting decorators in source files."""

    return build_schema_tree_with_names(src_dir)[0]


def build_schema_tree_with_names(src_dir: Path) -> tuple[ET.Element, dict[str, str]]:
    """Builds schema XML and returns its logical-name to schema-id mapping."""

    schemas, all_settings, all_enums = _discover_schemas(src_dir)

    schemalist = ET.Element("schemalist")

    for enum_id in sorted(all_enums):
        enum_el = ET.SubElement(schemalist, "enum", id=enum_id)
        for nick, int_value in all_enums[enum_id].items():
            ET.SubElement(enum_el, "value", nick=nick, value=str(int_value))

    for schema_name in sorted(schemas):
        schema_id = schemas[schema_name]
        settings = [s for s in all_settings if s.get("schema") == schema_name]

        schema = ET.SubElement(schemalist, "schema", id=schema_id)

        for setting in settings:
            genum = setting.get("genum")
            key_name = setting["key"]
            default = setting.get("default")

            if genum:
                default_str = f"'{default}'"
                key = ET.SubElement(schema, "key", name=key_name, enum=genum)
            else:
                gtype = setting.get("gtype", "s")
                default_str = _format_default(gtype, default, key_name)
                key = ET.SubElement(schema, "key", name=key_name, type=gtype)

            ET.SubElement(key, "default").text = default_str
            ET.SubElement(key, "summary").text = setting.get("summary", "")

    return schemalist, schemas


def generate_schema_xml(src_dir: Path, output_path: str) -> None:
    """Generate schema XML file from @gsetting decorators in source files."""

    schemalist = build_schema_tree(src_dir)
    ET.indent(schemalist, space="  ")
    tree = ET.ElementTree(schemalist)
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)
    with open(output_path, "a", encoding="utf-8") as f:
        f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Orca GSettings schemas")
    parser.add_argument("src_dir", help="Path to src directory")
    parser.add_argument("output", help="Output XML file path")
    args = parser.parse_args()

    generate_schema_xml(Path(args.src_dir), args.output)
