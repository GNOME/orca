# Orca
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

"""Check that user-facing strings are marked for translation."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

_ORCA_SRC = Path(__file__).resolve().parents[2] / "src/orca"
_TRANSLATION_ARGUMENTS = {"_": 1, "C_": 2, "ngettext": 2}
# These strings cannot be marked for translation during the v51 string freeze.
_UNLOCALIZED_UNTIL_52 = {
    "cmdnames": {
        repr("Select next character"),
        repr("Select previous character"),
        repr("Select next word"),
        repr("Select previous word"),
        repr("Select next line"),
        repr("Select previous line"),
        repr("Select to the top of the file"),
        repr("Select to the bottom of the file"),
        repr("Select to the beginning of the line"),
        repr("Select to the end of the line"),
    },
    "guilabels": {
        repr("Inline code"),
        repr("You can assign keybindings to any configured voice set in Commands."),
        repr("Text selection"),
        repr("Headers and footers"),
        repr("If 'Text selection' is enabled, Orca will also attempt to control text selection."),
    },
    "messages": {
        "f'{used:.1f} of {total:.1f} GB used.'",
        "f'{used:.1f} of {total:.1f} MB used.'",
    },
}


def _major_version() -> int:
    """Read the source version so a version bump takes effect without rebuilding Orca."""

    source = (_ORCA_SRC.parents[1] / "meson.build").read_text(encoding="utf-8")
    match = re.search(r"\bversion:\s*'([0-9]+)\.", source)
    assert match is not None, "Could not read Orca's major version from meson.build"
    return int(match.group(1))


def _unlocalized_strings(source: str) -> list[tuple[int, str]]:
    """Find untranslated text while excluding metadata and non-text formatting syntax."""

    tree = ast.parse(source)
    nodes = list(ast.walk(tree))
    excluded: set[ast.AST] = set()
    for node in nodes:
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.body and isinstance(node.body[0], ast.Expr):
                # Exclude docstrings.
                if isinstance(node.body[0].value, ast.Constant):
                    excluded.add(node.body[0].value)
        elif isinstance(node, ast.Dict):
            # Exclude dictionary keys which serve as internal identifiers.
            excluded.update(key for key in node.keys if isinstance(key, ast.Constant))
        elif isinstance(node, ast.FormattedValue) and node.format_spec is not None:
            # Exclude f-string format specifications, such as ".1f".
            excluded.update(ast.walk(node.format_spec))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            count = _TRANSLATION_ARGUMENTS.get(node.func.id, 0)
            # Exclude literal strings already marked for translation.
            excluded.update(arg for arg in node.args[:count] if isinstance(arg, ast.Constant))

    findings = []
    for node in nodes:
        if isinstance(node, ast.JoinedStr) and node not in excluded:
            parts = [part for part in node.values if isinstance(part, ast.Constant)]
            excluded.update(parts)
            if any(isinstance(part.value, str) and part.value.strip() for part in parts):
                findings.append((node.lineno, ast.unparse(node)))

    findings.extend(
        (node.lineno, repr(node.value))
        for node in nodes
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.strip()
        and node not in excluded
    )
    return sorted(findings)


@pytest.mark.parametrize("module", ["cmdnames", "guilabels", "messages"])
def test_user_facing_strings_are_localized(module: str) -> None:
    """Require translation markers on text constants and text returned by helper functions."""

    path = _ORCA_SRC / f"{module}.py"
    findings = _unlocalized_strings(path.read_text(encoding="utf-8"))
    if _major_version() < 52:
        exceptions = _UNLOCALIZED_UNTIL_52.get(module, set())
        findings = [(line, text) for line, text in findings if text not in exceptions]
    details = "\n".join(f"{path.name}:{line}: {text}" for line, text in findings)
    assert not findings, f"Strings missing translation markers:\n{details}"


def test_voice_set_commands_hint_restored_in_v52() -> None:
    """Require the temporarily hidden Voice Sets hint to return when string freeze ends."""

    # TODO - JD: Restore VOICE_SET_INFO_COMMANDS in the UI once marked for translation in v52.
    # In src/orca/speech_manager_preferences_grid.py, uncomment the original msg assignment
    # and delete the temporary assignment.
    if _major_version() < 52:
        return

    path = _ORCA_SRC / "speech_manager_preferences_grid.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assert any(
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "guilabels"
        and node.attr == "VOICE_SET_INFO_COMMANDS"
        for node in ast.walk(tree)
    ), (
        "Mark VOICE_SET_INFO_COMMANDS for translation in v52, then uncomment the original "
        "msg assignment and delete the temporary assignment in "
        "src/orca/speech_manager_preferences_grid.py"
    )


@pytest.mark.parametrize(
    "source",
    [
        'LABEL = _("Label")\nALIAS = LABEL',
        'LABEL = C_("Context", "Label")',
        'def count(n):\n    return ngettext("%d item", "%d items", n) % n',
        'LABEL = _("Hello %s") % name',
        'LABEL = _("Hello {name}").format(name=name)',
        'LABEL = {"internal-key": _("Label")}',
        (
            '"""Module documentation."""\ndef label():\n    """Function documentation."""\n'
            '    return " " + _("Label") + ""'
        ),
    ],
)
def test_translation_check_accepts_localized_text(source: str) -> None:
    """Recognize the translation, aliasing, formatting, and metadata patterns we support."""

    assert not _unlocalized_strings(source)


@pytest.mark.parametrize(
    "source",
    [
        'LABEL = "Untranslated"',
        'LABEL: str = "Untranslated"',
        'LABEL = ("Untranslated "\n "continued")',
        'def label():\n    return "Untranslated"',
        'LABEL = {"internal-key": "Untranslated"}',
        'LABEL = _("Translated") + " untranslated"',
        'LABEL = f"{used:.1f} of {total:.1f} GB used."',
        'LABEL = _(f"{used:.1f} of {total:.1f} GB used.")',
    ],
)
def test_translation_check_rejects_unlocalized_text(source: str) -> None:
    """Catch plain text and f-strings, including f-strings incorrectly passed to gettext."""

    findings = _unlocalized_strings(source)
    assert len(findings) == 1
