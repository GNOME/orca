# Unit tests for preferences documentation metadata.
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

"""Unit tests for preferences documentation metadata."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ORCA_SRC = _REPO_ROOT / "src" / "orca"
_PREFERENCES_GRID_FILES = tuple(sorted(_ORCA_SRC.glob("*preferences_grid.py")))
_GRID_BASES = {
    "AutoPreferencesGrid",
    "PreferencesGridBase",
    "preferences_grid_base.AutoPreferencesGrid",
    "preferences_grid_base.PreferencesGridBase",
}
_CONTROL_CLASSES = {
    "BooleanPreferenceControl",
    "ColorPreferenceControl",
    "EnumPreferenceControl",
    "FloatRangePreferenceControl",
    "IntRangePreferenceControl",
    "SelectionPreferenceControl",
    "preferences_grid_base.BooleanPreferenceControl",
    "preferences_grid_base.ColorPreferenceControl",
    "preferences_grid_base.EnumPreferenceControl",
    "preferences_grid_base.FloatRangePreferenceControl",
    "preferences_grid_base.IntRangePreferenceControl",
    "preferences_grid_base.SelectionPreferenceControl",
}
_DOC_CONTROL_CLASSES = {
    "PreferenceControlDoc",
    "preferences_grid_base.PreferenceControlDoc",
}


def _name(node: ast.AST) -> str:
    """Return a dotted name for node, or an empty string."""

    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _keyword(call: ast.Call, name: str) -> ast.AST | None:
    """Return keyword value from call."""

    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    return None


def _expression(node: ast.AST) -> str:
    """Return a stable expression string."""

    return ast.unparse(node)


def _is_dynamic_key(node: ast.AST) -> bool:
    """Return True if key expression cannot be checked statically."""

    expression = _expression(node)
    return expression in {"key", "pref.prefs_key", "prefs_key"} or expression.endswith(".prefs_key")


def _has_meaningful_documentation(class_node: ast.ClassDef) -> bool:
    """Return True if class overrides get_documentation with more than the base default."""

    for node in class_node.body:
        if not isinstance(node, ast.FunctionDef) or node.name != "get_documentation":
            continue
        for call in [item for item in ast.walk(node) if isinstance(item, ast.Call)]:
            if _name(call.func).endswith("PreferencePanelDoc"):
                title = _keyword(call, "title")
                controls = _keyword(call, "controls")
                description = _keyword(call, "description")
                summary = _keyword(call, "summary")
                return title is not None and (
                    controls is not None or description is not None or summary is not None
                )
    return False


def _preference_keys_in_ui(class_node: ast.ClassDef) -> set[str]:
    """Return explicit preference key expressions used by controls in the UI."""

    keys: set[str] = set()
    for call in [item for item in ast.walk(class_node) if isinstance(item, ast.Call)]:
        if _name(call.func) not in _CONTROL_CLASSES:
            continue
        key_node = _keyword(call, "prefs_key")
        if key_node is None or _is_dynamic_key(key_node):
            continue
        keys.add(_expression(key_node))
    return keys


def _preference_keys_in_metadata(class_node: ast.ClassDef) -> set[str]:
    """Return explicit preference key expressions documented in metadata."""

    keys: set[str] = set()
    for node in class_node.body:
        if not isinstance(node, ast.FunctionDef) or node.name != "get_documentation":
            continue
        for call in [item for item in ast.walk(node) if isinstance(item, ast.Call)]:
            if _name(call.func) not in _DOC_CONTROL_CLASSES:
                continue
            key_node = _keyword(call, "key")
            if key_node is None or _is_dynamic_key(key_node):
                continue
            keys.add(_expression(key_node))
    return keys


def _grid_classes(path: Path) -> list[ast.ClassDef]:
    """Return preferences grid classes from path."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    classes = []
    for node in [item for item in ast.walk(tree) if isinstance(item, ast.ClassDef)]:
        bases = {_name(base) for base in node.bases}
        if bases & _GRID_BASES:
            classes.append(node)
    return classes


@pytest.mark.unit
@pytest.mark.parametrize("path", _PREFERENCES_GRID_FILES, ids=lambda path: path.name)
def test_preferences_grids_have_documentation_metadata(path: Path) -> None:
    """Preferences grid classes should provide documentation metadata."""

    for class_node in _grid_classes(path):
        assert _has_meaningful_documentation(class_node), (
            f"{path.relative_to(_REPO_ROOT)}:{class_node.lineno}: "
            f"{class_node.name} needs get_documentation() metadata"
        )


@pytest.mark.unit
@pytest.mark.parametrize("path", _PREFERENCES_GRID_FILES, ids=lambda path: path.name)
def test_preferences_controls_have_documentation_metadata(path: Path) -> None:
    """Explicit preference controls should have matching documentation metadata."""

    for class_node in _grid_classes(path):
        ui_keys = _preference_keys_in_ui(class_node)
        metadata_keys = _preference_keys_in_metadata(class_node)
        missing = sorted(ui_keys - metadata_keys)
        assert not missing, (
            f"{path.relative_to(_REPO_ROOT)}:{class_node.lineno}: "
            f"{class_node.name} has undocumented preference keys: {missing}"
        )
