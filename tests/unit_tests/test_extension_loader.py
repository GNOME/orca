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
import threading
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
        essential_modules[
            "orca.gsettings_registry"
        ].GSettingsRegistry.sanitize_gsettings_path.side_effect = lambda name: name.lower()
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
            assert result.settings._namespace == "dctest"
        finally:
            sys.modules.pop("orca_user_extension.dctest", None)

    def test_package_extension_loads(self, test_context: OrcaTestContext, tmp_path: Path) -> None:
        """Test a package extension loads from its __init__.py file."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        essential_modules[
            "orca.gsettings_registry"
        ].GSettingsRegistry.sanitize_gsettings_path.side_effect = lambda name: name.lower()
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        ext_dir = tmp_path / "pkgtest"
        ext_dir.mkdir()
        (ext_dir / "__init__.py").write_text(
            "from orca.extension import Extension\n"
            "class PackageExtension(Extension):\n"
            '    GROUP_LABEL = "Package"\n'
        )

        try:
            result = ExtensionLoader._load_from_file(str(ext_dir), "pkgtest")
            assert isinstance(result, Extension)
            assert result.GROUP_LABEL == "Package"
            assert result.settings._namespace == "pkgtest"
        finally:
            sys.modules.pop("orca_user_extension.pkgtest", None)

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

    def test_shutdown_user_extensions_notifies_loaded_extensions(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test loaded user extensions are notified of Orca shutdown."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        calls = []

        class FirstExtension(Extension):
            GROUP_LABEL = "First"

            def on_shutdown(self) -> None:
                calls.append("first")

        class SecondExtension(Extension):
            GROUP_LABEL = "Second"

            def on_shutdown(self) -> None:
                calls.append("second")

        loader = ExtensionLoader()
        loader._user_extensions = [FirstExtension(), SecondExtension()]

        loader.shutdown_user_extensions()

        assert sorted(calls) == ["first", "second"]

    def test_shutdown_user_extensions_logs_and_continues_after_exception(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test one extension shutdown failure does not block other extensions."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        debug_mock = essential_modules["orca.debug"]
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        calls = []

        class FirstExtension(Extension):
            GROUP_LABEL = "First"

            def on_shutdown(self) -> None:
                calls.append("first")

        class FailingExtension(Extension):
            GROUP_LABEL = "Failing"

            def on_shutdown(self) -> None:
                calls.append("failing")
                raise RuntimeError("Shutdown failed")

        loader = ExtensionLoader()
        loader._user_extensions = [FirstExtension(), FailingExtension()]

        loader.shutdown_user_extensions()

        assert sorted(calls) == ["failing", "first"]
        debug_mock.print_exception.assert_called_once_with(debug_mock.LEVEL_WARNING)

    def test_shutdown_user_extensions_stops_after_timeout(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test blocking shutdown hooks do not block Orca shutdown."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        debug_mock = essential_modules["orca.debug"]
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        calls = []
        block = threading.Event()

        class FirstExtension(Extension):
            GROUP_LABEL = "First"

            def on_shutdown(self) -> None:
                calls.append("first")

        class BlockingExtension(Extension):
            GROUP_LABEL = "Blocking"

            def on_shutdown(self) -> None:
                calls.append("blocking")
                block.wait()

        loader = ExtensionLoader()
        loader._SHUTDOWN_HOOK_TOTAL_TIMEOUT_SECONDS = 0.01
        loader._user_extensions = [FirstExtension(), BlockingExtension()]

        loader.shutdown_user_extensions()
        block.set()

        assert sorted(calls) == ["blocking", "first"]
        debug_mock.print_message.assert_any_call(
            debug_mock.LEVEL_WARNING,
            "EXTENSION LOADER: Shutdown hook timed out for: BlockingExtension",
            True,
        )

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
            '    DESCRIPTION = "Adds commands for testing approved extensions."\n'
            '    VERSION = "1.2"\n'
            '    AUTHOR = "Example Author"\n'
            '    ORGANIZATION = "Example, Inc."\n'
            '    COPYRIGHT = "2026 Example, Inc."\n'
            '    WEBSITE = "https://example.com/approved-extension"\n'
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
        assert infos["approved.py"].description == "Adds commands for testing approved extensions."
        assert infos["approved.py"].version == "1.2"
        assert infos["approved.py"].author == "Example Author"
        assert infos["approved.py"].organization == "Example, Inc."
        assert infos["approved.py"].copyright == "2026 Example, Inc."
        assert infos["approved.py"].website == "https://example.com/approved-extension"
        assert infos["approved.py"].status is UserExtensionStatus.DISABLED
        assert infos["modified.py"].group_label == "Modified"
        assert infos["unapproved.py"].group_label == "Unapproved"
        assert infos["modified.py"].status is UserExtensionStatus.MODIFIED
        assert infos["unapproved.py"].status is UserExtensionStatus.UNAPPROVED
        assert infos["invalid.py"].status is UserExtensionStatus.INVALID
        assert "orca_user_extension.approved" not in sys.modules

    def test_discover_user_extensions_reports_package_extensions(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test discovery includes package extensions without executing them."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension_loader import ExtensionLoader, UserExtensionStatus

        package_dir = tmp_path / "packaged"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text(
            "from orca.extension import Extension\n"
            "class PackageExtension(Extension):\n"
            '    GROUP_LABEL = "Packaged"\n'
        )
        (package_dir / "__pycache__").mkdir()
        (package_dir / "__pycache__" / "ignored.pyc").write_bytes(b"ignored")

        loader = ExtensionLoader()
        loader.get_approved_extensions = test_context.Mock(
            return_value={"packaged": loader._compute_hash(str(package_dir))}
        )
        loader.get_disabled_extensions = test_context.Mock(return_value=[])

        infos = {info.filename: info for info in loader.discover_user_extensions(str(tmp_path))}

        assert infos["packaged"].is_package is True
        assert infos["packaged"].filepath == str(package_dir)
        assert infos["packaged"].class_name == "PackageExtension"
        assert infos["packaged"].group_label == "Packaged"
        assert infos["packaged"].status is UserExtensionStatus.APPROVED
        assert "orca_user_extension.packaged" not in sys.modules

    def test_package_hash_ignores_bytecode_cache(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test package approval hash ignores bytecode cache files."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension_loader import ExtensionLoader

        package_dir = tmp_path / "packaged"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text("VALUE = 1\n")

        first_hash = ExtensionLoader._compute_hash(str(package_dir))
        (package_dir / "__pycache__").mkdir()
        (package_dir / "__pycache__" / "ignored.pyc").write_bytes(b"ignored")
        (package_dir / ".ignored").write_text("ignored")

        assert ExtensionLoader._compute_hash(str(package_dir)) == first_hash

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
