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

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


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
