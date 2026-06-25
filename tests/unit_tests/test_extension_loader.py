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

    def test_iter_speech_output_handlers_returns_enabled_user_extensions_with_hook(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test speech output handlers are hook overrides not disabled by name."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        class NoHookExtension(Extension):
            GROUP_LABEL = "No Hook"

        class EnabledHookExtension(Extension):
            GROUP_LABEL = "Enabled"

            def on_speech_output(self, output):
                return None

        class DisabledHookExtension(Extension):
            GROUP_LABEL = "Disabled"

            def on_speech_output(self, output):
                return None

        loader = ExtensionLoader()
        no_hook = NoHookExtension()
        enabled = EnabledHookExtension()
        disabled = DisabledHookExtension()
        loader._user_extensions = [no_hook, enabled, disabled]
        loader._speech_output_handlers = [
            ext for ext in loader._user_extensions if loader._extension_handles_speech_output(ext)
        ]
        loader.get_disabled_extensions = test_context.Mock(return_value=["DisabledHookExtension"])

        assert loader.iter_speech_output_handlers() == [enabled]

    def test_iter_speech_output_handlers_short_circuits_without_hooks(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test no disabled-extension lookup is needed when no speech hooks exist."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension_loader import ExtensionLoader

        loader = ExtensionLoader()
        loader.get_disabled_extensions = test_context.Mock()

        assert loader.iter_speech_output_handlers() == []
        loader.get_disabled_extensions.assert_not_called()

    def test_discover_user_extensions_reports_status_without_loading(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test extension discovery reports status without executing extension files."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension_loader import ExtensionLoader, UserExtensionStatus

        approved_path = tmp_path / "approved.py"
        approved_path.write_text(
            "from orca.extension import Extension\n"
            "class ApprovedExtension(Extension):\n"
            '    GROUP_LABEL = "Approved"\n'
            '    GROUP_DESCRIPTION = "Approved description"\n'
        )
        modified_path = tmp_path / "modified.py"
        modified_path.write_text(
            "from orca.extension import Extension\n"
            "class ModifiedExtension(Extension):\n"
            '    GROUP_LABEL = "Modified"\n'
        )
        unapproved_path = tmp_path / "unapproved.py"
        unapproved_path.write_text(
            "from orca.extension import Extension\n"
            "class UnapprovedExtension(Extension):\n"
            '    GROUP_LABEL = "Unapproved"\n'
        )
        invalid_path = tmp_path / "invalid.py"
        invalid_path.write_text("print('not an extension')\n")

        loader = ExtensionLoader()
        loader.get_approved_extensions = test_context.Mock(
            return_value={
                "approved.py": loader._compute_hash(str(approved_path)),
                "modified.py": "old-hash",
            }
        )
        loader.get_disabled_extensions = test_context.Mock(return_value=["ApprovedExtension"])

        infos = {info.filename: info for info in loader.discover_user_extensions(str(tmp_path))}

        assert infos["approved.py"].class_name == "ApprovedExtension"
        assert infos["approved.py"].group_label == "Approved"
        assert infos["approved.py"].group_description == "Approved description"
        assert infos["approved.py"].status is UserExtensionStatus.DISABLED
        assert infos["modified.py"].group_label == "Modified"
        assert infos["unapproved.py"].group_label == "Unapproved"
        assert infos["modified.py"].status is UserExtensionStatus.MODIFIED
        assert infos["unapproved.py"].status is UserExtensionStatus.UNAPPROVED
        assert infos["invalid.py"].status is UserExtensionStatus.INVALID
        assert "orca_user_extension.approved" not in sys.modules

    def test_reload_user_extensions_unloads_old_extensions_and_sets_up_new_ones(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test reload clears stale user extensions and installs current ones."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        class OldExtension(Extension):
            GROUP_LABEL = "Old"

        ext_path = tmp_path / "new.py"
        ext_path.write_text(
            "from orca.extension import Extension\n"
            "class NewExtension(Extension):\n"
            '    GROUP_LABEL = "New"\n'
        )

        loader = ExtensionLoader()
        old = OldExtension()
        old.disable = test_context.Mock()
        loader._user_extensions = [old]
        loader._speech_output_handlers = [old]
        loader.get_approved_extensions = test_context.Mock(
            return_value={"new.py": loader._compute_hash(str(ext_path))}
        )
        loader.get_disabled_extensions = test_context.Mock(return_value=[])
        command_manager = essential_modules["orca.command_manager"].get_manager.return_value

        try:
            loader.reload_user_extensions(str(tmp_path))
        finally:
            sys.modules.pop("orca_user_extension.new", None)

        old.disable.assert_called_once()
        assert [extension.module_name for extension in loader._user_extensions] == ["NewExtension"]
        assert loader._speech_output_handlers == []
        command_manager.activate_commands.assert_called_once_with("reloaded user extensions")
