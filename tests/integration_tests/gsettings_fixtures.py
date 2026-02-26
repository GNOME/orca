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

"""GSettings fixtures for integration tests."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import types
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable, Generator


def _inject_generated_module_stubs() -> None:
    """Injects minimal stubs for meson-generated modules into sys.modules."""

    i18n = types.ModuleType("orca.orca_i18n")
    i18n._ = lambda x: x  # type: ignore[attr-defined]
    i18n.C_ = lambda c, x: x  # type: ignore[attr-defined]
    i18n.ngettext = lambda s, p, n: s if n == 1 else p  # type: ignore[attr-defined]
    sys.modules["orca.orca_i18n"] = i18n

    platform = types.ModuleType("orca.orca_platform")
    platform.version = "0.0.0-test"  # type: ignore[attr-defined]
    platform.revision = ""  # type: ignore[attr-defined]
    platform.prefix = "/usr"  # type: ignore[attr-defined]
    platform.package = "orca"  # type: ignore[attr-defined]
    platform.datadir = "/usr/share"  # type: ignore[attr-defined]
    platform.tablesdir = ""  # type: ignore[attr-defined]
    sys.modules["orca.orca_platform"] = platform


def _build_schemas(source_root: str, output_dir: str) -> None:
    """Generates and compiles GSettings schemas into output_dir."""

    generator = os.path.join(source_root, "tools", "generate_gsettings_schemas.py")
    src_dir = os.path.join(source_root, "src")
    schema_xml = os.path.join(output_dir, "org.gnome.Orca.gschema.xml")

    subprocess.check_call([sys.executable, generator, src_dir, schema_xml])
    subprocess.check_call(["glib-compile-schemas", output_dir])


@pytest.fixture(scope="session", name="gsettings_registry")
def _gsettings_registry() -> Generator:
    """Session-scoped fixture providing a GSettingsRegistry backed by in-memory storage."""

    source_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
    schema_dir = tempfile.mkdtemp(prefix="orca-test-schemas-")

    try:
        _build_schemas(source_root, schema_dir)
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        shutil.rmtree(schema_dir, ignore_errors=True)
        pytest.skip(f"Schema generation failed: {error!s}")

    os.environ["GSETTINGS_BACKEND"] = "memory"
    os.environ["GSETTINGS_SCHEMA_DIR"] = schema_dir

    _inject_generated_module_stubs()

    from orca import (
        speech_presenter,  # noqa: F401  # pylint: disable=unused-import,import-outside-toplevel
    )
    from orca.gsettings_registry import get_registry  # pylint: disable=import-outside-toplevel

    yield get_registry()

    shutil.rmtree(schema_dir, ignore_errors=True)
    os.environ.pop("GSETTINGS_SCHEMA_DIR", None)


@pytest.fixture(name="gsettings_handle")
def _gsettings_handle(
    gsettings_registry,
) -> Callable:
    """Factory fixture returning a GSettingsSchemaHandle that resets user keys on teardown."""

    handles_used: list = []

    def _get_handle(schema_name: str):
        handle = gsettings_registry._get_handle(schema_name)
        if handle is None:
            pytest.fail(f"No handle found for schema {schema_name!r}")
        handles_used.append(handle)
        return handle

    yield _get_handle

    for handle in handles_used:
        for gs in handle._cache.values():
            for key in gs.props.settings_schema.list_keys():
                gs.reset(key)


@pytest.fixture(name="gsettings_profile")
def _gsettings_profile(gsettings_registry) -> Generator:
    """Ensures each test starts with the default profile and no active app."""

    gsettings_registry.set_active_profile("default")
    gsettings_registry.set_active_app(None)
    yield gsettings_registry
    gsettings_registry.set_active_profile("default")
    gsettings_registry.set_active_app(None)
