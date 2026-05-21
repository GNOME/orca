# Unit tests for extension_loader.py methods.
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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

"""Unit tests for extension_loader.py methods."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestExtensionLoaderDataclass:
    """Tests loading user extensions that use class decorators introspecting sys.modules."""

    def test_dataclass_extension_loads(self, test_context: OrcaTestContext, tmp_path: Path) -> None:
        """A user extension using @dataclass with string annotations must load."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        # ExtensionLoader is decorated with gsettings_registry's schema/gsetting decorators
        # at class-definition time; make them pass-through so the real class is imported.
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        # @dataclass with "from __future__ import annotations" makes the stdlib look the
        # module up via sys.modules[__name__] during class creation; the loader must have
        # registered the module by then or class creation raises and the load silently fails.
        ext_path = tmp_path / "dctest.py"
        ext_path.write_text(
            "from __future__ import annotations\n"
            "from dataclasses import dataclass\n"
            "from orca.extension import Extension\n"
            "\n"
            "@dataclass(frozen=True)\n"
            "class Point:\n"
            "    x: int\n"
            "    y: int\n"
            "\n"
            "class DCTestExtension(Extension):\n"
            '    GROUP_LABEL = "DCTest"\n'
            "    def _get_commands(self):\n"
            "        return []\n"
        )

        try:
            result = ExtensionLoader._load_from_file(str(ext_path), "dctest.py")
            assert isinstance(result, Extension)
            assert result.GROUP_LABEL == "DCTest"
        finally:
            sys.modules.pop("orca_user_extension.dctest", None)
