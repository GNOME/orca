# Unit tests for extension.py methods.
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

"""Unit tests for extension.py methods."""

from __future__ import annotations

import struct
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from .orca_test_context import OrcaTestContext


def _write_mo(path: Path, messages: dict[str, str]) -> None:  # pylint: disable=too-many-locals
    """Write a small GNU MO catalog for tests."""

    encoded = sorted(
        (message.encode("utf-8"), translation.encode("utf-8"))
        for message, translation in messages.items()
    )
    count = len(encoded)
    originals_offset = 7 * 4
    translations_offset = originals_offset + count * 8
    strings_offset = translations_offset + count * 8

    original_data = b""
    original_entries = []
    for message, _translation in encoded:
        original_entries.append((len(message), strings_offset + len(original_data)))
        original_data += message + b"\0"

    translation_data_offset = strings_offset + len(original_data)
    translation_data = b""
    translation_entries = []
    for _message, translation in encoded:
        translation_entries.append(
            (len(translation), translation_data_offset + len(translation_data))
        )
        translation_data += translation + b"\0"

    data = struct.pack(
        "<7I",
        0x950412DE,
        0,
        count,
        originals_offset,
        translations_offset,
        0,
        0,
    )
    data += b"".join(struct.pack("<2I", *entry) for entry in original_entries)
    data += b"".join(struct.pack("<2I", *entry) for entry in translation_entries)
    data += original_data + translation_data
    path.parent.mkdir(parents=True)
    path.write_bytes(data)


@pytest.mark.unit
class TestExtensionTranslation:
    """Tests for package-scoped extension translations."""

    @staticmethod
    def _setup(test_context: OrcaTestContext):
        test_context.setup_shared_dependencies(["orca.command_manager"])
        from orca import extension

        return extension

    def test_get_translation_loads_package_catalog(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test gettext, plurals, and contexts use the package's domain."""

        extension = self._setup(test_context)
        package_dir = tmp_path / "localized_test"
        source_file = package_dir / "__init__.py"
        source_file.parent.mkdir()
        source_file.write_text("")
        catalog = package_dir / "locale" / "it" / "LC_MESSAGES" / "localized_test.mo"
        _write_mo(
            catalog,
            {
                "": (
                    "Content-Type: text/plain; charset=UTF-8\n"
                    "Language: it\n"
                    "Plural-Forms: nplurals=2; plural=(n != 1);\n"
                ),
                "Hello": "Ciao",
                "One item\0Many items": "Un elemento\0Molti elementi",
                "menu\x04Open": "Apri",
            },
        )
        test_context.patch_env({"LANGUAGE": "it"})

        translation = extension.get_translation(str(source_file))

        assert translation.gettext("Hello") == "Ciao"
        assert translation.ngettext("One item", "Many items", 1) == "Un elemento"
        assert translation.ngettext("One item", "Many items", 2) == "Molti elementi"
        assert translation.pgettext("menu", "Open") == "Apri"
        assert translation.gettext("Missing") == "Missing"

    def test_get_translation_keeps_package_domains_isolated(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test packages can translate the same source string differently."""

        extension = self._setup(test_context)
        test_context.patch_env({"LANGUAGE": "it"})
        translations = {}
        for domain, value in (("first", "Primo"), ("second", "Secondo")):
            source_file = tmp_path / domain / "__init__.py"
            source_file.parent.mkdir()
            source_file.write_text("")
            catalog = source_file.parent / "locale" / "it" / "LC_MESSAGES" / f"{domain}.mo"
            _write_mo(
                catalog,
                {
                    "": "Content-Type: text/plain; charset=UTF-8\nLanguage: it\n",
                    "Value": value,
                },
            )
            translations[domain] = extension.get_translation(str(source_file))

        assert translations["first"].gettext("Value") == "Primo"
        assert translations["second"].gettext("Value") == "Secondo"

    def test_get_translation_uses_source_strings_for_single_file_extension(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test single-file extensions do not load unhashed sidecar catalogs."""

        extension = self._setup(test_context)
        source_file = tmp_path / "single.py"
        source_file.write_text("")

        translation = extension.get_translation(str(source_file))

        assert translation.gettext("Hello") == "Hello"

    def test_get_translation_ignores_broken_catalog(
        self,
        test_context: OrcaTestContext,
        tmp_path: Path,
    ) -> None:
        """Test a malformed package catalog falls back to source strings."""

        extension = self._setup(test_context)
        source_file = tmp_path / "broken" / "__init__.py"
        source_file.parent.mkdir()
        source_file.write_text("")
        catalog = source_file.parent / "locale" / "it" / "LC_MESSAGES" / "broken.mo"
        catalog.parent.mkdir(parents=True)
        catalog.write_bytes(b"not a message catalog")
        test_context.patch_env({"LANGUAGE": "it"})

        translation = extension.get_translation(str(source_file))

        assert translation.gettext("Hello") == "Hello"
        extension.debug.print_message.assert_called_once()  # pylint: disable=no-member


@pytest.mark.unit
class TestExtensionCommands:
    """Tests command setup for user extensions."""

    def test_cached_command_function_is_wrapped_only_once(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test setting up a cached command twice keeps its original wrapper."""

        test_context.setup_shared_dependencies(["orca.command_manager", "orca.dbus_service"])
        from orca.extension import Extension

        calls = []

        def callback() -> bool:
            calls.append("called")
            return True

        class CachedCommand:
            def __init__(self) -> None:
                self.function = callback

            def get_function(self):
                return self.function

            def set_function(self, function) -> None:
                self.function = function

            @staticmethod
            def get_name() -> str:
                return "cached_command"

        command = CachedCommand()

        class CachedCommandExtension(Extension):
            GROUP_LABEL = "Cached command"

            def _get_commands(self):
                return [command]

        extension = CachedCommandExtension()
        extension.mark_as_user_extension()
        extension.set_up_commands()
        first_wrapper = command.get_function()

        extension.reset_commands()
        extension.set_up_commands()
        second_wrapper = command.get_function()

        assert second_wrapper is first_wrapper
        assert second_wrapper(None, None) is True
        assert calls == ["called"]


class _VariantLike:
    """Simple object that mimics GLib.Variant.unpack()."""

    def __init__(self, value):
        self._value = value

    def unpack(self):
        """Return the stored value."""

        return self._value


class _SettingsLike:
    """Simple object that mimics the Gio.Settings calls used by ExtensionSettings."""

    def __init__(self, registry):
        self._registry = registry

    def get_user_value(self, key):
        """Return a variant-like local value."""

        local_values = self._registry.local_values.get(self._registry.current_sub_path, {})
        if key not in local_values:
            return None
        return _VariantLike(local_values[key])


class _RegistryLike:
    """Simple registry used to test ExtensionSettings."""

    def __init__(self):
        self.local_values = {}
        self.layered_values = {}
        self.writes = []
        self.current_sub_path = ""

    def get_active_profile(self):
        """Return the active profile."""

        return "default"

    def get_settings(self, _schema, _profile, sub_path=""):
        """Return a settings-like object."""

        self.current_sub_path = sub_path
        return _SettingsLike(self)

    def layered_lookup(self, _schema, key, _gtype, sub_path="", default=None):
        """Return layered settings."""

        return self.layered_values.get(sub_path, {}).get(key, default)

    def set_dict(self, schema, key, gtype, value, sub_path=""):
        """Store a settings dict."""

        if gtype == "a{sv}":
            from orca.gsettings_registry import GSettingsRegistry

            GSettingsRegistry._variant_dict(value)
        self.writes.append((schema, key, gtype, value, sub_path))
        self.local_values.setdefault(sub_path, {})[key] = value
        self.layered_values.setdefault(sub_path, {})[key] = value
        return True


@pytest.mark.unit
class TestExtensionSettings:
    """Tests for extension-scoped settings."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies and return the imported module."""

        test_context.setup_shared_dependencies(["orca.command_manager"])
        from orca import extension

        return extension

    def _patch_registry(self, test_context: OrcaTestContext, extension, registry) -> None:
        """Patch the extension module to use a test registry."""

        test_context.patch_object(
            extension.gsettings_registry,
            "get_registry",
            return_value=registry,
        )

    def test_get_uses_extension_path(self, test_context: OrcaTestContext) -> None:
        """Test get returns the value from the extension's settings path."""

        extension = self._setup(test_context)
        registry = _RegistryLike()
        registry.layered_values["extensions/hello-world"] = {"settings": {"reverse": True}}
        registry.layered_values["extensions/other"] = {"settings": {"reverse": False}}
        self._patch_registry(test_context, extension, registry)

        settings = extension.ExtensionSettings("hello_world")

        assert settings.get("reverse", default=False) is True

    def test_get_returns_default_when_key_is_missing(self, test_context: OrcaTestContext) -> None:
        """Test get returns the caller-provided default for missing values."""

        extension = self._setup(test_context)
        registry = _RegistryLike()
        registry.layered_values["extensions/hello-world"] = {"settings": {}}
        self._patch_registry(test_context, extension, registry)

        settings = extension.ExtensionSettings("hello_world")

        assert settings.get("reverse", default=True) is True

    def test_get_unpacks_nested_variant_values(self, test_context: OrcaTestContext) -> None:
        """Test get returns plain Python values from a nested variant dictionary."""

        extension = self._setup(test_context)
        registry = _RegistryLike()
        variant = extension.gsettings_registry.GLib.Variant
        registry.layered_values["extensions/hello-world"] = {
            "settings": {
                "word-replacements": variant(
                    "a{sv}",
                    {
                        "screen": variant("s", "display"),
                    },
                )
            }
        }
        self._patch_registry(test_context, extension, registry)

        settings = extension.ExtensionSettings("hello_world")

        assert settings.get("word-replacements", default={}) == {"screen": "display"}

    def test_set_writes_to_active_profile(self, test_context: OrcaTestContext) -> None:
        """Test set stores the value in the extension's settings path."""

        extension = self._setup(test_context)
        registry = _RegistryLike()
        self._patch_registry(test_context, extension, registry)

        settings = extension.ExtensionSettings("hello_world")

        assert settings.set("reverse", True) is True
        assert registry.writes == [
            (
                "extensions",
                "settings",
                "a{sv}",
                {"reverse": True},
                "extensions/hello-world",
            )
        ]

    def test_set_accepts_simple_dict_values(self, test_context: OrcaTestContext) -> None:
        """Test set accepts dictionaries with string keys and simple values."""

        extension = self._setup(test_context)
        registry = _RegistryLike()
        self._patch_registry(test_context, extension, registry)

        settings = extension.ExtensionSettings("hello_world")

        assert settings.set(
            "provider",
            {
                "enabled": True,
                "count": 3,
                "scale": 1.5,
                "name": "demo",
            },
        )
        assert registry.writes[-1] == (
            "extensions",
            "settings",
            "a{sv}",
            {
                "provider": {
                    "enabled": True,
                    "count": 3,
                    "scale": 1.5,
                    "name": "demo",
                }
            },
            "extensions/hello-world",
        )

    def test_reset_removes_local_value(self, test_context: OrcaTestContext) -> None:
        """Test reset removes the value from the extension's settings path."""

        extension = self._setup(test_context)
        registry = _RegistryLike()
        registry.local_values["extensions/hello-world"] = {
            "settings": {"reverse": True, "other": False}
        }
        self._patch_registry(test_context, extension, registry)

        settings = extension.ExtensionSettings("hello_world")

        assert settings.reset("reverse") is True
        assert registry.writes[-1] == (
            "extensions",
            "settings",
            "a{sv}",
            {"other": False},
            "extensions/hello-world",
        )

    def test_rejects_invalid_key(self, test_context: OrcaTestContext) -> None:
        """Test setting keys are restricted to simple names."""

        extension = self._setup(test_context)
        settings = extension.ExtensionSettings("hello_world")

        with pytest.raises(ValueError):
            settings.get("../bad")

    def test_rejects_unsupported_value(self, test_context: OrcaTestContext) -> None:
        """Test set rejects values that cannot be represented in V1."""

        extension = self._setup(test_context)
        registry = _RegistryLike()
        self._patch_registry(test_context, extension, registry)
        settings = extension.ExtensionSettings("hello_world")

        with pytest.raises(TypeError):
            settings.set("bad", {"not": ["simple"]})

        with pytest.raises(TypeError):
            settings.set("bad", {"nested": {"dict": True}})

        with pytest.raises(TypeError):
            settings.set("bad", {1: "one"})
