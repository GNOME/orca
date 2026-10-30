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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA 02110-1301 USA.

"""Tests for how the GSettings schema generator resolves setting keys."""

from __future__ import annotations

import re
import runpy
from pathlib import Path
from typing import Any

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "generate_gsettings_schemas.py"

_OWNER = """
from .{settings_module} import Settings


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Test", name="test")
class Owner:
    @gsettings_registry.get_registry().gsetting(
        key=Settings.KEY_EXAMPLE, schema="test", gtype="b", default=False, summary="Example"
    )
    def get_example(self):
        return False
"""


@pytest.fixture(scope="module", name="generator")
def generator_fixture() -> dict[str, Any]:
    """Loads the standalone schema generator."""

    return runpy.run_path(str(_SCRIPT))


def _write_sources(src_dir: Path, files: dict[str, str]) -> None:
    """Writes each named file into src_dir/orca."""

    orca_dir = src_dir / "orca"
    orca_dir.mkdir(parents=True)
    for name, text in files.items():
        (orca_dir / name).write_text(text, encoding="utf-8")


@pytest.mark.unit
def test_key_comes_from_the_imported_settings_class(
    generator: dict[str, Any], tmp_path: Path
) -> None:
    """A key named as Settings.KEY_X is read from the module Settings was imported from."""

    _write_sources(
        tmp_path,
        {
            "a_settings.py": 'class Settings:\n    KEY_EXAMPLE = "example-key"\n',
            "b_settings.py": 'class Settings:\n    KEY_EXAMPLE = "wrong"\n',
            "owner.py": _OWNER.format(settings_module="a_settings"),
        },
    )

    _schemas, settings, _enums = generator["_discover_schemas"](tmp_path)
    assert [setting["key"] for setting in settings] == ["example-key"]


@pytest.mark.unit
def test_key_from_a_class_that_is_not_imported_is_rejected(
    generator: dict[str, Any], tmp_path: Path
) -> None:
    """A key named as Settings.KEY_X fails generation when Settings is not imported."""

    owner = _OWNER.format(settings_module="b_settings").replace(
        "from .b_settings import Settings\n", ""
    )
    _write_sources(
        tmp_path,
        {
            "b_settings.py": 'class Settings:\n    KEY_EXAMPLE = "example-key"\n',
            "owner.py": owner,
        },
    )

    with pytest.raises(ValueError, match=re.escape("Cannot resolve Settings.KEY_EXAMPLE")):
        generator["_discover_schemas"](tmp_path)


@pytest.mark.unit
def test_key_assigned_more_than_once_is_rejected(generator: dict[str, Any], tmp_path: Path) -> None:
    """A key assigned twice in the settings class fails generation instead of using the first."""

    _write_sources(
        tmp_path,
        {
            "a_settings.py": (
                'class Settings:\n    KEY_EXAMPLE = "old"\n    KEY_EXAMPLE = "example-key"\n'
            ),
            "owner.py": _OWNER.format(settings_module="a_settings"),
        },
    )

    with pytest.raises(ValueError, match=re.escape("KEY_EXAMPLE is bound 2 times in Settings")):
        generator["_discover_schemas"](tmp_path)
