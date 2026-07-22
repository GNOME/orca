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
from types import ModuleType, SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import call

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from .orca_test_context import OrcaTestContext


def _load_preferences_grid_module(test_context: OrcaTestContext):
    """Loads the user-extension preferences grid with lightweight dependencies."""

    essential_modules = test_context.setup_shared_dependencies(
        [
            "orca.command_manager",
            "orca.extension_preferences",
            "orca.extension_preferences_dialog",
            "orca.gsettings_registry",
            "orca.orca_gui_helpers",
            "orca.presentation_manager",
        ]
    )
    registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
    registry.gsettings_schema.return_value = lambda cls: cls
    registry.gsetting.return_value = lambda func: func

    preferences_grid_base = ModuleType("orca.preferences_grid_base")
    preferences_grid_base.PreferencesGridBase = object
    test_context.patch_module("orca.preferences_grid_base", preferences_grid_base)

    from orca import extension_loader, extension_loader_preferences_grid

    return extension_loader, extension_loader_preferences_grid


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

    def test_iter_braille_output_handlers_returns_enabled_user_extensions_with_hook(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test braille output handlers are hook overrides not disabled by name."""

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

            def on_braille_output(self, output):
                return None

        class DisabledHookExtension(Extension):
            GROUP_LABEL = "Disabled"

            def on_braille_output(self, output):
                return None

        loader = ExtensionLoader()
        no_hook = NoHookExtension()
        enabled = EnabledHookExtension()
        disabled = DisabledHookExtension()
        loader._user_extensions = [no_hook, enabled, disabled]
        loader._braille_output_handlers = [
            ext for ext in loader._user_extensions if loader._extension_handles_braille_output(ext)
        ]
        loader.get_disabled_extensions = test_context.Mock(return_value=["DisabledHookExtension"])

        assert loader.iter_braille_output_handlers() == [enabled]

    def test_iter_braille_output_handlers_short_circuits_without_hooks(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test no disabled-extension lookup is needed when no braille hooks exist."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension_loader import ExtensionLoader

        loader = ExtensionLoader()
        loader.get_disabled_extensions = test_context.Mock()

        assert loader.iter_braille_output_handlers() == []
        loader.get_disabled_extensions.assert_not_called()

    def test_notify_user_extensions_ready_runs_all_hooks(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test loaded user extensions are notified when Orca is ready."""

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

            def on_ready(self) -> None:
                calls.append("first ready")

        class SecondExtension(Extension):
            GROUP_LABEL = "Second"

            def on_ready(self) -> None:
                calls.append("second ready")

        loader = ExtensionLoader()
        loader._user_extensions = [FirstExtension(), SecondExtension()]

        loader.notify_user_extensions_ready()
        loader.notify_user_extensions_ready()

        assert calls == ["first ready", "second ready"]
        assert loader._orca_is_ready is True

    def test_notify_user_extensions_ready_logs_and_continues_after_exception(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test one failing ready hook does not block other extensions."""

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

        class FailingExtension(Extension):
            GROUP_LABEL = "Failing"

            def on_ready(self) -> None:
                calls.append("failing")
                raise RuntimeError("Ready failed")

        class WorkingExtension(Extension):
            GROUP_LABEL = "Working"

            def on_ready(self) -> None:
                calls.append("working")

        loader = ExtensionLoader()
        loader._user_extensions = [FailingExtension(), WorkingExtension()]

        loader.notify_user_extensions_ready()

        assert calls == ["failing", "working"]
        debug_mock.print_exception.assert_called_once_with(debug_mock.LEVEL_WARNING)

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

    def test_discover_and_load_does_not_execute_disabled_extension(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test an approved but disabled extension is not imported or instantiated."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension_loader import ExtensionLoader

        marker = tmp_path / "executed"
        extension_path = tmp_path / "disabled.py"
        extension_path.write_text(
            "from pathlib import Path\n"
            "from orca.extension import Extension\n"
            f"Path({str(marker)!r}).write_text('executed')\n"
            "class DisabledExtension(Extension):\n"
            '    GROUP_LABEL = "Disabled"\n'
        )

        loader = ExtensionLoader()
        loader.get_approved_extensions = test_context.Mock(
            return_value={"disabled.py": loader._compute_hash(str(extension_path))}
        )
        loader.get_disabled_extensions = test_context.Mock(return_value=["DisabledExtension"])

        loader.discover_and_load(str(tmp_path))

        assert not marker.exists()
        assert loader._user_extensions == []
        assert loader._user_extensions_by_source == {}
        assert "orca_user_extension.disabled" not in sys.modules

    def test_get_metadata_localizes_marked_package_strings_without_loading(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test marked metadata is safely parsed and localized without execution."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca import extension_loader

        translation = test_context.Mock()
        translation.gettext.side_effect = lambda message: {
            "Localized Extension": "Estensione localizzata",
        }.get(message, message)
        translation.pgettext.side_effect = lambda context, message: {
            ("extension description", "Demonstrates localization."): (
                "Dimostra la localizzazione."
            ),
        }.get((context, message), message)
        test_context.patch_object(
            extension_loader,
            "get_translation",
            return_value=translation,
        )
        package_dir = tmp_path / "localized"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text(
            "raise RuntimeError('must not execute')\n"
            "from orca.extension import Extension\n"
            "class LocalizedExtension(Extension):\n"
            '    GROUP_LABEL = _("Localized Extension")\n'
            "    DESCRIPTION = pgettext(\n"
            '        "extension description", "Demonstrates localization."\n'
            "    )\n"
            '    VERSION = "1.0"\n'
        )

        metadata = extension_loader.ExtensionLoader.get_metadata(str(package_dir))

        assert metadata.class_name == "LocalizedExtension"
        assert metadata.group_label == "Estensione localizzata"
        assert metadata.description == "Dimostra la localizzazione."
        assert metadata.version == "1.0"
        extension_loader.get_translation.assert_called_once_with(str(package_dir / "__init__.py"))  # pylint: disable=no-member

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

    def test_reload_user_extension_replaces_only_target_source(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test targeted reload preserves unrelated instances and their lifecycle state."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        calls = []

        class OldTarget(Extension):
            GROUP_LABEL = "Old Target"

            def on_disabled(self) -> None:
                calls.append("old target disabled")

            def on_speech_output(self, _output):
                return None

        class NewTarget(Extension):
            GROUP_LABEL = "New Target"

            def on_enabled(self) -> None:
                calls.append("new target enabled")

            def on_braille_output(self, _output):
                return None

        class UnrelatedExtension(Extension):
            GROUP_LABEL = "Unrelated"

            def on_enabled(self) -> None:
                calls.append("unrelated enabled")

            def on_disabled(self) -> None:
                calls.append("unrelated disabled")

            def on_speech_output(self, _output):
                return None

        old_target = OldTarget()
        new_target = NewTarget()
        unrelated = UnrelatedExtension()
        old_target.disable = test_context.Mock()
        new_target.set_up_commands = test_context.Mock()
        unrelated.reset_commands = test_context.Mock()
        unrelated.set_up_commands = test_context.Mock()

        loader = ExtensionLoader()
        loader._orca_is_ready = True
        loader._user_extensions_by_source = {
            "a.py": old_target,
            "b.py": unrelated,
        }
        loader.get_disabled_extensions = test_context.Mock(return_value=[])
        loader._sync_user_extension_lists()
        loader._load_user_extension_source = test_context.Mock(return_value=new_target)
        target_module = ModuleType("orca_user_extension.a")
        target_submodule = ModuleType("orca_user_extension.a.helper")
        unrelated_module = ModuleType("orca_user_extension.b")
        test_context.patch_modules(
            {
                "orca_user_extension.a": target_module,
                "orca_user_extension.a.helper": target_submodule,
                "orca_user_extension.b": unrelated_module,
            }
        )
        command_manager = essential_modules["orca.command_manager"].get_manager.return_value

        loader.reload_user_extension("/extensions", "a.py")

        assert calls == ["old target disabled", "new target enabled"]
        assert loader._user_extensions_by_source == {
            "a.py": new_target,
            "b.py": unrelated,
        }
        assert loader._user_extensions == [new_target, unrelated]
        assert loader._speech_output_handlers == [unrelated]
        assert loader._braille_output_handlers == [new_target]
        assert "orca_user_extension.a" not in sys.modules
        assert "orca_user_extension.a.helper" not in sys.modules
        assert sys.modules["orca_user_extension.b"] is unrelated_module
        old_target.disable.assert_called_once()
        unrelated.reset_commands.assert_called_once()
        unrelated.set_up_commands.assert_called_once()
        new_target.set_up_commands.assert_called_once()
        command_manager.activate_commands.assert_called_once_with("reloaded user extension")

    def test_reload_user_extension_loads_updated_file_only(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test an actual targeted reload imports new code and preserves its peer."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension_loader import ExtensionLoader

        target_path = tmp_path / "target.py"
        peer_path = tmp_path / "peer.py"
        target_path.write_text(
            "from orca.extension import Extension\n"
            "class OldTarget(Extension):\n"
            '    GROUP_LABEL = "Old target"\n'
        )
        peer_path.write_text(
            "from orca.extension import Extension\n"
            "class PeerExtension(Extension):\n"
            '    GROUP_LABEL = "Peer"\n'
        )
        loader = ExtensionLoader()
        approved = {
            "peer.py": loader._compute_hash(str(peer_path)),
            "target.py": loader._compute_hash(str(target_path)),
        }
        loader.get_approved_extensions = test_context.Mock(return_value=approved)
        loader.get_disabled_extensions = test_context.Mock(return_value=[])

        try:
            loader.discover_and_load(str(tmp_path))
            peer = loader._user_extensions_by_source["peer.py"]
            old_target = loader._user_extensions_by_source["target.py"]
            target_path.write_text(
                "from orca.extension import Extension\n"
                "class NewTargetExtension(Extension):\n"
                '    GROUP_LABEL = "New target extension"\n'
            )
            approved["target.py"] = loader._compute_hash(str(target_path))

            loader.reload_user_extension(str(tmp_path), "target.py")

            assert loader._user_extensions_by_source["peer.py"] is peer
            assert loader._user_extensions_by_source["target.py"] is not old_target
            assert loader._user_extensions_by_source["target.py"].module_name == (
                "NewTargetExtension"
            )
        finally:
            sys.modules.pop("orca_user_extension.peer", None)
            sys.modules.pop("orca_user_extension.target", None)

    def test_reload_missing_inactive_source_preserves_everything(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a target with no old or new instance causes no unrelated churn."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        class UnrelatedExtension(Extension):
            GROUP_LABEL = "Unrelated"

        unrelated = UnrelatedExtension()
        unrelated.reset_commands = test_context.Mock()
        loader = ExtensionLoader()
        loader._user_extensions_by_source = {"unrelated.py": unrelated}
        loader._sync_user_extension_lists()
        loader._load_user_extension_source = test_context.Mock(return_value=None)
        command_manager = essential_modules["orca.command_manager"].get_manager.return_value

        loader.reload_user_extension("/extensions", "disabled.py")

        assert loader._user_extensions == [unrelated]
        unrelated.reset_commands.assert_not_called()
        command_manager.activate_commands.assert_not_called()

    @pytest.mark.parametrize(
        ("old_target_present", "new_target_present", "expected_calls"),
        [
            (True, False, ["target disabled"]),
            (False, True, ["target enabled"]),
        ],
    )
    def test_reload_user_extension_handles_activation_boundaries(
        self,
        test_context: OrcaTestContext,
        old_target_present: bool,
        new_target_present: bool,
        expected_calls: list[str],
    ) -> None:
        """Test targeted enable and disable notify only the target instance."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.command_manager", "orca.gsettings_registry"]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        calls = []

        class TargetExtension(Extension):
            GROUP_LABEL = "Target"

            def on_enabled(self) -> None:
                calls.append("target enabled")

            def on_disabled(self) -> None:
                calls.append("target disabled")

        class UnrelatedExtension(Extension):
            GROUP_LABEL = "Unrelated"

            def on_enabled(self) -> None:
                calls.append("unrelated enabled")

            def on_disabled(self) -> None:
                calls.append("unrelated disabled")

        old_target = TargetExtension() if old_target_present else None
        new_target = TargetExtension() if new_target_present else None
        unrelated = UnrelatedExtension()
        unrelated.reset_commands = test_context.Mock()
        unrelated.set_up_commands = test_context.Mock()
        if old_target is not None:
            old_target.disable = test_context.Mock()
        if new_target is not None:
            new_target.set_up_commands = test_context.Mock()

        loader = ExtensionLoader()
        loader._orca_is_ready = True
        loader._user_extensions_by_source = {"unrelated.py": unrelated}
        if old_target is not None:
            loader._user_extensions_by_source["target.py"] = old_target
        loader.get_disabled_extensions = test_context.Mock(return_value=[])
        loader._sync_user_extension_lists()
        loader._load_user_extension_source = test_context.Mock(return_value=new_target)

        loader.reload_user_extension("/extensions", "target.py")

        assert calls == expected_calls
        assert loader._user_extensions_by_source.get("unrelated.py") is unrelated
        assert loader._user_extensions_by_source.get("target.py") is new_target
        unrelated.reset_commands.assert_called_once()
        unrelated.set_up_commands.assert_called_once()

    def test_targeted_reload_reconciles_keybinding_conflicts_in_source_order(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test targeted changes restore and recreate conflicts without replacing peers."""

        essential_modules = test_context.setup_shared_dependencies(
            [
                "orca.ax_device_manager",
                "orca.gsettings_registry",
                "orca.orca_modifier_manager",
                "orca.presentation_manager",
            ]
        )
        registry = essential_modules["orca.gsettings_registry"].get_registry.return_value
        registry.gsettings_schema.return_value = lambda cls: cls
        registry.gsetting.return_value = lambda func: func
        registry.layered_lookup.return_value = {}
        modifier_manager = essential_modules["orca.orca_modifier_manager"].get_manager.return_value
        modifier_manager.get_orca_modifier_keys.return_value = []
        from orca import command_manager
        from orca.extension import Extension
        from orca.extension_loader import ExtensionLoader

        def create_binding():
            binding = test_context.Mock()
            binding.keysymstring = "F9"
            binding.modifiers = 256
            binding.click_count = 1
            binding.keyval = 65
            binding.keycode = 38
            binding.has_grabs.return_value = False
            binding.get_grab_ids.return_value = []
            binding.as_string.return_value = "Orca+F9"
            return binding

        class FirstExtension(Extension):
            GROUP_LABEL = "First"

            def _get_commands(self):
                return [
                    command_manager.KeyboardCommand(
                        "first_command",
                        lambda: None,
                        self.GROUP_LABEL,
                        desktop_keybinding=create_binding(),
                    )
                ]

        class SecondExtension(Extension):
            GROUP_LABEL = "Second"

            def _get_commands(self):
                return [
                    command_manager.KeyboardCommand(
                        "second_command",
                        lambda: None,
                        self.GROUP_LABEL,
                        desktop_keybinding=create_binding(),
                    )
                ]

        first = FirstExtension()
        second = SecondExtension()
        first.mark_as_user_extension("first")
        second.mark_as_user_extension("second")
        loader = ExtensionLoader()
        loader._user_extensions_by_source = {
            "a-first.py": first,
            "b-second.py": second,
        }
        loader.get_disabled_extensions = test_context.Mock(return_value=[])
        loader._sync_user_extension_lists()
        loader.set_up_user_commands()
        manager = command_manager.get_manager()

        assert manager.get_keyboard_command("first_command").get_keybinding() is not None
        assert manager.get_keyboard_command("second_command").get_keybinding() is None
        assert manager.has_user_extension_keybinding_conflicts("SecondExtension")

        loader._load_user_extension_source = test_context.Mock(return_value=None)
        loader.reload_user_extension("/extensions", "a-first.py")

        assert loader._user_extensions == [second]
        assert manager.get_keyboard_command("first_command") is None
        assert manager.get_keyboard_command("second_command").get_keybinding() is not None
        assert not manager.has_user_extension_keybinding_conflicts("SecondExtension")

        replacement = FirstExtension()
        replacement.mark_as_user_extension("first")
        loader._load_user_extension_source = test_context.Mock(return_value=replacement)
        loader.reload_user_extension("/extensions", "a-first.py")

        assert loader._user_extensions == [replacement, second]
        assert manager.get_keyboard_command("first_command").get_keybinding() is not None
        assert manager.get_keyboard_command("second_command").get_keybinding() is None
        assert manager.has_user_extension_keybinding_conflicts("SecondExtension")


@pytest.mark.unit
class TestExtensionLoaderPreferencesLifecycle:
    """Tests preferences actions delegate lifecycle transitions to reloads."""

    @pytest.mark.parametrize(
        ("enabled", "disabled", "expected_disabled"),
        [
            (False, [], ["ExampleExtension"]),
            (True, ["ExampleExtension", "OtherExtension"], ["OtherExtension"]),
        ],
    )
    def test_toggling_reloads_only_selected_extension(
        self,
        test_context: OrcaTestContext,
        enabled: bool,
        disabled: list[str],
        expected_disabled: list[str],
    ) -> None:
        """Test toggling updates state and targets the selected source for reload."""

        _extension_loader, grid_module = _load_preferences_grid_module(test_context)
        info = SimpleNamespace(class_name="ExampleExtension")
        loader = test_context.Mock()
        loader.get_disabled_extensions.return_value = disabled
        switch = test_context.Mock()
        switch.get_active.return_value = enabled
        grid = SimpleNamespace(
            _extensions_dir="/extensions",
            _get_info=test_context.Mock(return_value=info),
            _loader=loader,
            _sync_row=test_context.Mock(),
            _syncing_filenames=set(),
        )

        grid_module.ExtensionLoaderPreferencesGrid._on_switch_toggled(
            grid,
            switch,
            None,
            "example.py",
        )

        assert loader.method_calls == [
            call.get_disabled_extensions(),
            call.set_disabled_extensions(expected_disabled),
            call.reload_user_extension("/extensions", "example.py"),
        ]

    def test_revoking_approval_reloads_extensions(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test revoking approval relies on reload to run lifecycle hooks."""

        extension_loader, grid_module = _load_preferences_grid_module(test_context)
        info = SimpleNamespace(
            class_name="ExampleExtension",
            filepath="/extensions/example.py",
            status=extension_loader.UserExtensionStatus.APPROVED,
        )
        loader = test_context.Mock()
        grid = SimpleNamespace(
            _extensions_dir="/extensions",
            _get_info=test_context.Mock(return_value=info),
            _loader=loader,
            _sync_row=test_context.Mock(),
        )

        grid_module.ExtensionLoaderPreferencesGrid._on_approval_clicked(grid, "example.py")

        assert loader.method_calls == [
            call.revoke_extension("example.py"),
            call.reload_user_extension("/extensions", "example.py"),
        ]

    def test_reapproving_reloads_extensions(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test reapproval relies on reload to run lifecycle hooks."""

        extension_loader, grid_module = _load_preferences_grid_module(test_context)
        info = SimpleNamespace(
            class_name="ExampleExtension",
            filepath="/extensions/example.py",
            status=extension_loader.UserExtensionStatus.MODIFIED,
        )
        loader = test_context.Mock()
        grid = SimpleNamespace(
            _extensions_dir="/extensions",
            _get_info=test_context.Mock(return_value=info),
            _loader=loader,
            _sync_row=test_context.Mock(),
        )

        grid_module.ExtensionLoaderPreferencesGrid._on_approval_clicked(grid, "example.py")

        assert loader.method_calls == [
            call.approve_extension_file("/extensions/example.py"),
            call.reload_user_extension("/extensions", "example.py"),
        ]

    def test_deleting_reloads_extensions(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test deletion relies on reload to run lifecycle hooks."""

        _extension_loader, grid_module = _load_preferences_grid_module(test_context)
        filepath = str(tmp_path / "example.py")
        info = SimpleNamespace(class_name="ExampleExtension", filepath=filepath)
        loader = test_context.Mock()
        loader.get_disabled_extensions.return_value = ["ExampleExtension"]
        grid = SimpleNamespace(
            _confirm_delete=test_context.Mock(return_value=True),
            _extensions_dir=str(tmp_path),
            _get_info=test_context.Mock(return_value=info),
            _is_deletable_extension_path=test_context.Mock(return_value=True),
            _loader=loader,
            _present_delete_error=test_context.Mock(),
            _staged_settings_by_class_name={"ExampleExtension": ([], {})},
            refresh=test_context.Mock(),
        )
        test_context.patch_object(grid_module.os, "remove")

        grid_module.ExtensionLoaderPreferencesGrid._on_delete_clicked(grid, "example.py")

        assert loader.method_calls == [
            call.revoke_extension("example.py"),
            call.get_disabled_extensions(),
            call.set_disabled_extensions([]),
            call.reload_user_extension(str(tmp_path), "example.py"),
        ]
