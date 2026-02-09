# Unit tests for gsettings_registry.py
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

"""Unit tests for gsettings_registry.py."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestSanitizeGsettingsPath:
    """Tests for sanitize_gsettings_path."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    @pytest.mark.parametrize(
        "input_name,expected",
        [
            ("default", "default"),
            ("Default", "default"),
            ("MY_PROFILE", "my-profile"),
            ("Hello World", "hello-world"),
            ("based_on_italian,_or_is_it?", "based-on-italian-or-is-it"),
            ("--leading--", "leading"),
            ("trailing--", "trailing"),
            ("  spaces  ", "spaces"),
            ("a--b---c", "a-b-c"),
            ("simple", "simple"),
            ("CamelCase", "camelcase"),
            ("with.dots.here", "with-dots-here"),
            ("Firefox", "firefox"),
        ],
    )
    def test_sanitize_gsettings_path(
        self, test_context: OrcaTestContext, input_name: str, expected: str
    ) -> None:
        """Test sanitize_gsettings_path with various inputs."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        assert get_registry().sanitize_gsettings_path(input_name) == expected


@pytest.mark.unit
class TestActiveState:
    """Tests for set_active_app/get_active_app and set_active_profile/get_active_profile."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies and return essential modules."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        return test_context.setup_shared_dependencies(additional_modules)

    def test_default_profile_is_default(self, test_context: OrcaTestContext) -> None:
        """Test that the default active profile is 'default'."""

        self._setup(test_context)
        from orca import gsettings_registry

        assert gsettings_registry.get_registry().get_active_profile() == "default"

    def test_default_app_is_none(self, test_context: OrcaTestContext) -> None:
        """Test that the default active app is None."""

        self._setup(test_context)
        from orca import gsettings_registry

        assert gsettings_registry.get_registry().get_active_app() is None

    def test_set_active_profile(self, test_context: OrcaTestContext) -> None:
        """Test set_active_profile updates the stored profile."""

        self._setup(test_context)
        from orca import gsettings_registry

        gsettings_registry.get_registry().set_active_profile("spanish")
        assert gsettings_registry.get_registry().get_active_profile() == "spanish"
        gsettings_registry.get_registry().set_active_profile("default")

    def test_set_active_app(self, test_context: OrcaTestContext) -> None:
        """Test set_active_app updates the stored app name."""

        self._setup(test_context)
        from orca import gsettings_registry

        gsettings_registry.get_registry().set_active_app("Firefox")
        assert gsettings_registry.get_registry().get_active_app() == "Firefox"
        gsettings_registry.get_registry().set_active_app(None)

    def test_set_active_app_empty_string_becomes_none(self, test_context: OrcaTestContext) -> None:
        """Test set_active_app treats empty string as None."""

        self._setup(test_context)
        from orca import gsettings_registry

        gsettings_registry.get_registry().set_active_app("")
        assert gsettings_registry.get_registry().get_active_app() is None


@pytest.mark.unit
class TestGsettingDecorator:
    """Tests for the @gsetting decorator and registry."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    def test_decorator_registers_metadata(self, test_context: OrcaTestContext) -> None:
        """Test @gsetting decorator populates the registry."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()

        @registry.gsetting(
            key="test-key", schema="test-schema", gtype="b", default=True, summary="Test"
        )
        def some_getter():
            return True

        assert ("test-schema", "test-key") in registry._descriptors
        desc = registry._descriptors[("test-schema", "test-key")]
        assert desc.gsettings_key == "test-key"
        assert desc.schema == "test-schema"
        assert desc.gtype == "b"
        assert desc.default is True
        assert desc.settings_key is None

        # Clean up
        del registry._descriptors[("test-schema", "test-key")]

    def test_decorator_registers_settings_key(self, test_context: OrcaTestContext) -> None:
        """Test @gsetting decorator stores settings_key in the descriptor."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()

        @registry.gsetting(
            key="test-sk",
            schema="test",
            gtype="b",
            default=True,
            summary="Test",
            settings_key="enableTestSetting",
        )
        def some_getter():
            return True

        desc = registry._descriptors[("test", "test-sk")]
        assert desc.settings_key == "enableTestSetting"

        del registry._descriptors[("test", "test-sk")]

    def test_decorator_settings_key_defaults_to_none(self, test_context: OrcaTestContext) -> None:
        """Test @gsetting decorator defaults settings_key to None when omitted."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()

        @registry.gsetting(key="test-no-sk", schema="test", gtype="s", default="", summary="Test")
        def some_getter():
            return ""

        desc = registry._descriptors[("test", "test-no-sk")]
        assert desc.settings_key is None

        del registry._descriptors[("test", "test-no-sk")]

    def test_decorator_preserves_function(self, test_context: OrcaTestContext) -> None:
        """Test @gsetting decorator returns the function unchanged."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()

        @registry.gsetting(key="test-key2", schema="test", gtype="s", default="", summary="Test")
        def my_func():
            return "hello"

        assert my_func() == "hello"
        assert my_func.gsetting_key == "test-key2"  # type: ignore[attr-defined]

        del registry._descriptors[("test", "test-key2")]

    def test_decorator_with_voice_type(self, test_context: OrcaTestContext) -> None:
        """Test @gsetting decorator handles voice_type parameter."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()

        @registry.gsetting(
            key="test-voice-key",
            schema="voice",
            gtype="i",
            default=50,
            summary="Test",
            voice_type="default",
        )
        def voice_getter():
            return 50

        desc = registry._descriptors[("voice", "test-voice-key")]
        assert desc.voice_type == "default"

        del registry._descriptors[("voice", "test-voice-key")]


@pytest.mark.unit
class TestGSettingsSchemaHandle:
    """Tests for GSettingsSchemaHandle."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        return test_context.setup_shared_dependencies(additional_modules)

    def test_get_schema_returns_none_when_source_unavailable(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_schema returns None when GSettings schema source is unavailable."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")
        # Schema won't exist in test environment unless installed
        # Force it to return None by patching
        test_context.patch_object(handle, "get_schema", return_value=None)
        assert handle.get_schema() is None

    def test_has_key_returns_false_without_schema(self, test_context: OrcaTestContext) -> None:
        """Test has_key returns False when schema unavailable."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")
        test_context.patch_object(handle, "get_schema", return_value=None)
        assert handle.has_key("some-key") is False

    def test_has_key_delegates_to_schema(self, test_context: OrcaTestContext) -> None:
        """Test has_key delegates to schema.has_key."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")
        mock_schema = test_context.Mock()
        mock_schema.has_key.return_value = True
        test_context.patch_object(handle, "get_schema", return_value=mock_schema)
        assert handle.has_key("existing-key") is True
        mock_schema.has_key.assert_called_with("existing-key")

    def test_build_profile_path(self, test_context: OrcaTestContext) -> None:
        """Test _build_profile_path produces correct dconf path."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.TypingEcho", "typing-echo")
        assert handle._build_profile_path("default") == "/org/gnome/orca/default/typing-echo/"
        assert handle._build_profile_path("Spanish") == "/org/gnome/orca/spanish/typing-echo/"

    def test_build_profile_path_with_sub_path(self, test_context: OrcaTestContext) -> None:
        """Test _build_profile_path with sub_path override."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.Voice", "voices")
        path = handle._build_profile_path("default", sub_path="voices/uppercase")
        assert path == "/org/gnome/orca/default/voices/uppercase/"

    def test_build_app_path(self, test_context: OrcaTestContext) -> None:
        """Test _build_app_path produces correct dconf path."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.Speech", "speech")
        path = handle._build_app_path("Firefox", "default")
        assert path == "/org/gnome/orca/default/apps/firefox/speech/"

    def test_build_app_path_with_sub_path(self, test_context: OrcaTestContext) -> None:
        """Test _build_app_path with sub_path override."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.Voice", "voices")
        path = handle._build_app_path("Firefox", "spanish", sub_path="voices/default")
        assert path == "/org/gnome/orca/spanish/apps/firefox/voices/default/"

    def test_get_for_profile_returns_none_without_schema(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_for_profile returns None when schema unavailable."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")
        test_context.patch_object(handle, "get_schema", return_value=None)
        assert handle.get_for_profile("default") is None

    def test_get_boolean_returns_none_without_schema(self, test_context: OrcaTestContext) -> None:
        """Test get_boolean returns None when schema unavailable."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")
        test_context.patch_object(handle, "get_schema", return_value=None)
        assert handle.get_boolean("some-key") is None

    def test_set_boolean_returns_false_without_schema(self, test_context: OrcaTestContext) -> None:
        """Test set_boolean returns False when schema unavailable."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")
        test_context.patch_object(handle, "get_schema", return_value=None)
        assert handle.set_boolean("some-key", True) is False

    def test_layered_get_app_override_wins(self, test_context: OrcaTestContext) -> None:
        """Test layered getter returns app-specific value when set."""

        essential = self._setup(test_context)
        essential["orca.settings"].activeProfile = ["Default", "default"]

        from orca.gsettings_registry import GSettingsSchemaHandle
        from orca import gsettings_registry

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")

        mock_schema = test_context.Mock()
        mock_schema.has_key.return_value = True
        test_context.patch_object(handle, "get_schema", return_value=mock_schema)

        # Set context: app is "Firefox", profile is "default"
        gsettings_registry.get_registry().set_active_app("Firefox")
        gsettings_registry.get_registry().set_active_profile("default")

        # App GSettings has the value
        mock_app_gs = test_context.Mock()
        mock_app_variant = test_context.Mock()
        mock_app_gs.get_user_value.return_value = mock_app_variant
        mock_app_gs.get_boolean.return_value = False

        # Profile GSettings also has a value (should be ignored)
        mock_profile_gs = test_context.Mock()
        mock_profile_variant = test_context.Mock()
        mock_profile_gs.get_user_value.return_value = mock_profile_variant
        mock_profile_gs.get_boolean.return_value = True

        test_context.patch_object(handle, "get_for_app", return_value=mock_app_gs)
        test_context.patch_object(handle, "get_for_profile", return_value=mock_profile_gs)

        result = handle.get_boolean("some-key")
        assert result is False  # App value wins
        gsettings_registry.get_registry().set_active_app(None)

    def test_layered_get_profile_fallback(self, test_context: OrcaTestContext) -> None:
        """Test layered getter falls back to profile when app has no user value."""

        essential = self._setup(test_context)
        essential["orca.settings"].activeProfile = ["Default", "default"]

        from orca.gsettings_registry import GSettingsSchemaHandle
        from orca import gsettings_registry

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")

        mock_schema = test_context.Mock()
        mock_schema.has_key.return_value = True
        test_context.patch_object(handle, "get_schema", return_value=mock_schema)

        gsettings_registry.get_registry().set_active_app("Firefox")
        gsettings_registry.get_registry().set_active_profile("default")

        # App GSettings has no user value
        mock_app_gs = test_context.Mock()
        mock_app_gs.get_user_value.return_value = None

        # Profile GSettings has the value
        mock_profile_gs = test_context.Mock()
        mock_profile_variant = test_context.Mock()
        mock_profile_gs.get_user_value.return_value = mock_profile_variant
        mock_profile_gs.get_boolean.return_value = True

        test_context.patch_object(handle, "get_for_app", return_value=mock_app_gs)
        test_context.patch_object(handle, "get_for_profile", return_value=mock_profile_gs)

        result = handle.get_boolean("some-key")
        assert result is True
        gsettings_registry.get_registry().set_active_app(None)

    def test_layered_get_default_profile_fallback(self, test_context: OrcaTestContext) -> None:
        """Test layered getter falls back to default profile for non-default profiles."""

        essential = self._setup(test_context)
        essential["orca.settings"].activeProfile = ["Spanish", "spanish"]

        from orca.gsettings_registry import GSettingsSchemaHandle
        from orca import gsettings_registry

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")

        mock_schema = test_context.Mock()
        mock_schema.has_key.return_value = True
        test_context.patch_object(handle, "get_schema", return_value=mock_schema)

        gsettings_registry.get_registry().set_active_app(None)
        gsettings_registry.get_registry().set_active_profile("spanish")

        # Spanish profile has no user value
        mock_spanish_gs = test_context.Mock()
        mock_spanish_gs.get_user_value.return_value = None

        # Default profile has the value
        mock_default_gs = test_context.Mock()
        mock_default_variant = test_context.Mock()
        mock_default_gs.get_user_value.return_value = mock_default_variant
        mock_default_gs.get_boolean.return_value = True

        def get_for_profile_side_effect(profile, _sub_path=""):
            if profile == "spanish":
                return mock_spanish_gs
            return mock_default_gs

        test_context.patch_object(
            handle, "get_for_profile", side_effect=get_for_profile_side_effect
        )

        result = handle.get_boolean("some-key")
        assert result is True
        gsettings_registry.get_registry().set_active_profile("default")

    def test_layered_get_returns_none_when_nothing_set(self, test_context: OrcaTestContext) -> None:
        """Test layered getter returns None when no layer has a user value."""

        essential = self._setup(test_context)
        essential["orca.settings"].activeProfile = ["Default", "default"]

        from orca.gsettings_registry import GSettingsSchemaHandle
        from orca import gsettings_registry

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")

        mock_schema = test_context.Mock()
        mock_schema.has_key.return_value = True
        test_context.patch_object(handle, "get_schema", return_value=mock_schema)

        gsettings_registry.get_registry().set_active_app(None)
        gsettings_registry.get_registry().set_active_profile("default")

        mock_gs = test_context.Mock()
        mock_gs.get_user_value.return_value = None
        test_context.patch_object(handle, "get_for_profile", return_value=mock_gs)

        result = handle.get_boolean("some-key")
        assert result is None

    def test_set_boolean_stamps_version(self, test_context: OrcaTestContext) -> None:
        """Test set_boolean stamps version on first write."""

        essential = self._setup(test_context)
        essential["orca.settings"].activeProfile = ["Default", "default"]

        from orca.gsettings_registry import GSettingsSchemaHandle
        from orca import gsettings_registry

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test", version=2)

        mock_schema = test_context.Mock()
        mock_schema.has_key.return_value = True
        test_context.patch_object(handle, "get_schema", return_value=mock_schema)

        gsettings_registry.get_registry().set_active_app(None)
        gsettings_registry.get_registry().set_active_profile("default")

        mock_gs = test_context.Mock()
        mock_gs.get_user_value.return_value = None  # version not yet set
        test_context.patch_object(handle, "get_for_profile", return_value=mock_gs)

        result = handle.set_boolean("some-key", True)
        assert result is True
        mock_gs.set_boolean.assert_called_once_with("some-key", True)
        mock_gs.set_int.assert_not_called()

    def test_is_current_version(self, test_context: OrcaTestContext) -> None:
        """Test is_current_version checks version correctly."""

        self._setup(test_context)
        from orca.gsettings_registry import GSettingsSchemaHandle

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test", version=2)

        mock_schema = test_context.Mock()
        mock_schema.has_key.return_value = True
        test_context.patch_object(handle, "get_schema", return_value=mock_schema)

        mock_gs = test_context.Mock()
        mock_gs.get_int.return_value = 2
        test_context.patch_object(handle, "get_for_profile", return_value=mock_gs)

        assert handle.is_current_version("default") is True

        mock_gs.get_int.return_value = 1
        assert handle.is_current_version("default") is False

    def test_get_string_layered(self, test_context: OrcaTestContext) -> None:
        """Test get_string uses layered lookup."""

        essential = self._setup(test_context)
        essential["orca.settings"].activeProfile = ["Default", "default"]

        from orca.gsettings_registry import GSettingsSchemaHandle
        from orca import gsettings_registry

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")

        mock_schema = test_context.Mock()
        mock_schema.has_key.return_value = True
        test_context.patch_object(handle, "get_schema", return_value=mock_schema)

        gsettings_registry.get_registry().set_active_app(None)
        gsettings_registry.get_registry().set_active_profile("default")

        mock_gs = test_context.Mock()
        mock_variant = test_context.Mock()
        mock_gs.get_user_value.return_value = mock_variant
        mock_gs.get_string.return_value = "voxin"
        test_context.patch_object(handle, "get_for_profile", return_value=mock_gs)

        result = handle.get_string("synthesizer")
        assert result == "voxin"


@pytest.mark.unit
class TestSettingsMappings:
    """Tests for JSON ↔ GSettings conversion functions."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    def test_register_and_get_mappings(self, test_context: OrcaTestContext) -> None:
        """Test register_settings_mappings and _get_settings_mappings."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        mappings = [
            SettingsMapping("enableFoo", "foo-enabled", "b", True),
            SettingsMapping("barLevel", "bar-level", "s", "none"),
        ]
        registry.register_settings_mappings("test-schema", mappings)
        assert registry._get_settings_mappings("test-schema") == mappings
        assert not registry._get_settings_mappings("nonexistent")

        del registry._mappings["test-schema"]

    def test_json_to_gsettings_boolean(self, test_context: OrcaTestContext) -> None:
        """Test _json_to_gsettings writes boolean values."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-b",
            [
                SettingsMapping("enableFoo", "foo-enabled", "b", True),
            ],
        )

        mock_gs = test_context.Mock()
        # Value differs from default
        result = registry._json_to_gsettings({"enableFoo": False}, mock_gs, "test-b")
        assert result is True
        mock_gs.set_boolean.assert_called_once_with("foo-enabled", False)

        del registry._mappings["test-b"]

    def test_json_to_gsettings_skips_defaults(self, test_context: OrcaTestContext) -> None:
        """Test _json_to_gsettings skips values matching schema defaults."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-skip",
            [
                SettingsMapping("enableFoo", "foo-enabled", "b", True),
            ],
        )

        mock_gs = test_context.Mock()
        # Value matches default — should be skipped
        result = registry._json_to_gsettings({"enableFoo": True}, mock_gs, "test-skip")
        assert result is False
        mock_gs.set_boolean.assert_not_called()

        del registry._mappings["test-skip"]

    def test_json_to_gsettings_enum(self, test_context: OrcaTestContext) -> None:
        """Test _json_to_gsettings handles enum (int->string) conversions."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-enum",
            [
                SettingsMapping(
                    "verbLevel", "verbosity-level", "s", 1, enum_map={0: "brief", 1: "verbose"}
                ),
            ],
        )

        mock_gs = test_context.Mock()
        # Value 0 differs from default 1
        result = registry._json_to_gsettings({"verbLevel": 0}, mock_gs, "test-enum")
        assert result is True
        mock_gs.set_string.assert_called_once_with("verbosity-level", "brief")

        del registry._mappings["test-enum"]

    def test_json_to_gsettings_enum_skips_default(self, test_context: OrcaTestContext) -> None:
        """Test _json_to_gsettings enum skips value matching default int."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-enum-skip",
            [
                SettingsMapping(
                    "verbLevel", "verbosity-level", "s", 1, enum_map={0: "brief", 1: "verbose"}
                ),
            ],
        )

        mock_gs = test_context.Mock()
        result = registry._json_to_gsettings({"verbLevel": 1}, mock_gs, "test-enum-skip")
        assert result is False
        mock_gs.set_string.assert_not_called()

        del registry._mappings["test-enum-skip"]

    def test_gsettings_to_json_boolean(self, test_context: OrcaTestContext) -> None:
        """Test _gsettings_to_json reads boolean values."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-read",
            [
                SettingsMapping("enableFoo", "foo-enabled", "b", True),
                SettingsMapping("enableBar", "bar-enabled", "b", False),
            ],
        )

        mock_gs = test_context.Mock()

        mock_variant_foo = test_context.Mock()
        mock_variant_foo.get_boolean.return_value = False

        def get_user_value_side_effect(key):
            if key == "foo-enabled":
                return mock_variant_foo
            return None  # bar-enabled not set

        mock_gs.get_user_value.side_effect = get_user_value_side_effect

        result = registry._gsettings_to_json(mock_gs, "test-read")
        assert result == {"enableFoo": False}
        assert "enableBar" not in result

        del registry._mappings["test-read"]

    def test_gsettings_to_json_enum(self, test_context: OrcaTestContext) -> None:
        """Test _gsettings_to_json reverses enum mapping (string->int)."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-read-enum",
            [
                SettingsMapping(
                    "verbLevel", "verbosity-level", "s", 1, enum_map={0: "brief", 1: "verbose"}
                ),
            ],
        )

        mock_gs = test_context.Mock()
        mock_variant = test_context.Mock()
        mock_variant.get_string.return_value = "brief"
        mock_gs.get_user_value.return_value = mock_variant

        result = registry._gsettings_to_json(mock_gs, "test-read-enum")
        assert result == {"verbLevel": 0}

        del registry._mappings["test-read-enum"]

    def test_roundtrip(self, test_context: OrcaTestContext) -> None:
        """Test _json_to_gsettings followed by _gsettings_to_json preserves values."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-rt",
            [
                SettingsMapping("enableFoo", "foo-enabled", "b", True),
                SettingsMapping(
                    "punctStyle",
                    "punctuation-level",
                    "s",
                    1,
                    enum_map={0: "all", 1: "most", 2: "some", 3: "none"},
                ),
            ],
        )

        # Simulate a Gio.Settings object with in-memory storage
        store: dict[str, tuple] = {}

        mock_gs = test_context.Mock()

        def set_boolean(key, value):
            store[key] = ("b", value)

        def set_string(key, value):
            store[key] = ("s", value)

        mock_gs.set_boolean.side_effect = set_boolean
        mock_gs.set_string.side_effect = set_string

        def get_user_value(key):
            if key not in store:
                return None
            gtype, value = store[key]
            variant = test_context.Mock()
            if gtype == "b":
                variant.get_boolean.return_value = value
            elif gtype == "s":
                variant.get_string.return_value = value
            return variant

        mock_gs.get_user_value.side_effect = get_user_value

        original = {"enableFoo": False, "punctStyle": 2}
        registry._json_to_gsettings(original, mock_gs, "test-rt")

        recovered = registry._gsettings_to_json(mock_gs, "test-rt")
        assert recovered == original

        del registry._mappings["test-rt"]

    def test_json_to_gsettings_missing_keys(self, test_context: OrcaTestContext) -> None:
        """Test _json_to_gsettings ignores keys not present in json_dict."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-miss",
            [
                SettingsMapping("enableFoo", "foo-enabled", "b", True),
                SettingsMapping("enableBar", "bar-enabled", "b", False),
            ],
        )

        mock_gs = test_context.Mock()
        # Only enableBar in the dict, and it matches default
        result = registry._json_to_gsettings({"enableBar": False}, mock_gs, "test-miss")
        assert result is False
        mock_gs.set_boolean.assert_not_called()

        del registry._mappings["test-miss"]

    def test_json_to_gsettings_int_and_double(self, test_context: OrcaTestContext) -> None:
        """Test _json_to_gsettings handles int and double types."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-id",
            [
                SettingsMapping("rate", "rate", "i", 50),
                SettingsMapping("pitch", "pitch", "d", 5.0),
            ],
        )

        mock_gs = test_context.Mock()
        result = registry._json_to_gsettings({"rate": 75, "pitch": 7.5}, mock_gs, "test-id")
        assert result is True
        mock_gs.set_int.assert_called_once_with("rate", 75)
        mock_gs.set_double.assert_called_once_with("pitch", 7.5)

        del registry._mappings["test-id"]


@pytest.mark.unit
class TestBidirectionalConversionMultiKey:
    """Tests for JSON↔GSettings roundtrip with realistic multi-key mappings."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    def _make_mock_gs(self, test_context: OrcaTestContext):
        """Returns a mock Gio.Settings backed by an in-memory dict."""

        store: dict[str, tuple[str, object]] = {}
        mock_gs = test_context.Mock()

        def set_boolean(key, value):
            store[key] = ("b", value)

        def set_string(key, value):
            store[key] = ("s", value)

        def set_int(key, value):
            store[key] = ("i", value)

        def set_double(key, value):
            store[key] = ("d", value)

        mock_gs.set_boolean.side_effect = set_boolean
        mock_gs.set_string.side_effect = set_string
        mock_gs.set_int.side_effect = set_int
        mock_gs.set_double.side_effect = set_double

        def get_user_value(key):
            if key not in store:
                return None
            gtype, value = store[key]
            variant = test_context.Mock()
            if gtype == "b":
                variant.get_boolean.return_value = value
            elif gtype == "s":
                variant.get_string.return_value = value
            elif gtype == "i":
                variant.get_int32.return_value = value
            elif gtype == "d":
                variant.get_double.return_value = value
            return variant

        mock_gs.get_user_value.side_effect = get_user_value
        return mock_gs, store

    def test_roundtrip_with_mixed_types_and_enums(self, test_context: OrcaTestContext) -> None:
        """Test roundtrip with booleans, strings, ints, doubles, and enums together."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-multi",
            [
                SettingsMapping("enableSpeech", "enable", "b", True),
                SettingsMapping("capitalizationStyle", "capitalization-style", "s", "none"),
                SettingsMapping("rate", "rate", "i", 50),
                SettingsMapping("pitch", "pitch", "d", 5.0),
                SettingsMapping(
                    "verbalizePunctuationStyle",
                    "punctuation-level",
                    "s",
                    1,
                    enum_map={0: "all", 1: "most", 2: "some", 3: "none"},
                ),
            ],
        )
        try:
            json_dict = {
                "enableSpeech": False,
                "capitalizationStyle": "spell",
                "rate": 75,
                "pitch": 7.5,
                "verbalizePunctuationStyle": 2,
            }
            mock_gs, _ = self._make_mock_gs(test_context)
            wrote = registry._json_to_gsettings(json_dict, mock_gs, "test-multi")
            assert wrote is True

            recovered = registry._gsettings_to_json(mock_gs, "test-multi")
            assert recovered == json_dict
        finally:
            registry._mappings.pop("test-multi", None)

    def test_defaults_skipped_non_defaults_preserved(self, test_context: OrcaTestContext) -> None:
        """Test that default values are skipped and non-defaults roundtrip correctly."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-defaults",
            [
                SettingsMapping("enableKeyEcho", "key-echo", "b", True),
                SettingsMapping("enableEchoByCharacter", "character-echo", "b", False),
                SettingsMapping("enableNavigationKeys", "navigation-keys", "b", False),
                SettingsMapping(
                    "speechVerbosityLevel",
                    "verbosity-level",
                    "s",
                    1,
                    enum_map={0: "brief", 1: "verbose"},
                ),
            ],
        )
        try:
            json_dict = {
                "enableKeyEcho": False,  # non-default (default True)
                "enableEchoByCharacter": False,  # matches default — should be skipped
                "enableNavigationKeys": True,  # non-default (default False)
                "speechVerbosityLevel": 1,  # matches default — should be skipped
            }
            mock_gs, store = self._make_mock_gs(test_context)
            registry._json_to_gsettings(json_dict, mock_gs, "test-defaults")

            # Only non-defaults should have been written
            assert "key-echo" in store
            assert "navigation-keys" in store
            assert "character-echo" not in store
            assert "verbosity-level" not in store

            recovered = registry._gsettings_to_json(mock_gs, "test-defaults")
            assert recovered == {
                "enableKeyEcho": False,
                "enableNavigationKeys": True,
            }
        finally:
            registry._mappings.pop("test-defaults", None)

    def test_empty_dict_writes_nothing(self, test_context: OrcaTestContext) -> None:
        """Test that an empty JSON dict produces no writes and empty recovery."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-empty",
            [
                SettingsMapping("enableSpeech", "enable", "b", True),
                SettingsMapping("rate", "rate", "i", 50),
            ],
        )
        try:
            mock_gs, _ = self._make_mock_gs(test_context)
            wrote = registry._json_to_gsettings({}, mock_gs, "test-empty")
            assert wrote is False
            assert not registry._gsettings_to_json(mock_gs, "test-empty")
        finally:
            registry._mappings.pop("test-empty", None)

    def test_unrelated_keys_ignored(self, test_context: OrcaTestContext) -> None:
        """Test that JSON keys not in the mapping are ignored."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-ignore",
            [
                SettingsMapping("enableKeyEcho", "key-echo", "b", True),
            ],
        )
        try:
            json_dict = {
                "enableKeyEcho": False,
                "caretNavigationEnabled": True,
                "brailleFlashTime": 8000,
                "voices": {"default": {"rate": 56}},
            }
            mock_gs, store = self._make_mock_gs(test_context)
            registry._json_to_gsettings(json_dict, mock_gs, "test-ignore")

            assert len(store) == 1
            assert "key-echo" in store

            recovered = registry._gsettings_to_json(mock_gs, "test-ignore")
            assert recovered == {"enableKeyEcho": False}
        finally:
            registry._mappings.pop("test-ignore", None)

    def test_all_enum_values_roundtrip(self, test_context: OrcaTestContext) -> None:
        """Test that every enum value roundtrips correctly."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        enum_map = {0: "all", 1: "most", 2: "some", 3: "none"}
        registry.register_settings_mappings(
            "test-all-enums",
            [
                SettingsMapping("punctStyle", "punctuation-level", "s", 1, enum_map=enum_map),
            ],
        )
        try:
            for int_val, _str_val in enum_map.items():
                if int_val == 1:
                    continue  # skip default
                mock_gs, _ = self._make_mock_gs(test_context)
                registry._json_to_gsettings({"punctStyle": int_val}, mock_gs, "test-all-enums")
                recovered = registry._gsettings_to_json(mock_gs, "test-all-enums")
                assert recovered == {"punctStyle": int_val}
        finally:
            registry._mappings.pop("test-all-enums", None)


@pytest.mark.unit
class TestBuildMappingsFromDescriptors:
    """Tests for auto-generating SettingsMapping from @gsetting descriptors."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    def test_builds_mappings_from_descriptors(self, test_context: OrcaTestContext) -> None:
        """Test _build_mappings_from_descriptors creates SettingsMapping from descriptors."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingDescriptor, get_registry

        registry = get_registry()

        registry._descriptors[("my-schema", "foo-enabled")] = SettingDescriptor(
            gsettings_key="foo-enabled",
            schema="my-schema",
            gtype="b",
            default=True,
            settings_key="enableFoo",
        )
        registry._descriptors[("my-schema", "bar-level")] = SettingDescriptor(
            gsettings_key="bar-level",
            schema="my-schema",
            gtype="i",
            default=50,
            settings_key="barLevel",
        )
        try:
            mappings = registry._build_mappings_from_descriptors("my-schema")
            assert len(mappings) == 2

            by_gs_key = {m.gs_key: m for m in mappings}
            assert "foo-enabled" in by_gs_key
            assert by_gs_key["foo-enabled"].json_key == "enableFoo"
            assert by_gs_key["foo-enabled"].gtype == "b"
            assert by_gs_key["foo-enabled"].default is True
            assert by_gs_key["foo-enabled"].enum_map is None

            assert "bar-level" in by_gs_key
            assert by_gs_key["bar-level"].json_key == "barLevel"
            assert by_gs_key["bar-level"].gtype == "i"
            assert by_gs_key["bar-level"].default == 50
        finally:
            registry._descriptors.pop(("my-schema", "foo-enabled"), None)
            registry._descriptors.pop(("my-schema", "bar-level"), None)

    def test_skips_descriptors_without_settings_key(self, test_context: OrcaTestContext) -> None:
        """Test _build_mappings_from_descriptors skips descriptors with settings_key=None."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingDescriptor, get_registry

        registry = get_registry()

        registry._descriptors[("my-schema", "has-key")] = SettingDescriptor(
            gsettings_key="has-key",
            schema="my-schema",
            gtype="b",
            default=True,
            settings_key="enableHasKey",
        )
        registry._descriptors[("my-schema", "no-key")] = SettingDescriptor(
            gsettings_key="no-key",
            schema="my-schema",
            gtype="b",
            default=False,
            settings_key=None,
        )
        try:
            mappings = registry._build_mappings_from_descriptors("my-schema")
            assert len(mappings) == 1
            assert mappings[0].json_key == "enableHasKey"
        finally:
            registry._descriptors.pop(("my-schema", "has-key"), None)
            registry._descriptors.pop(("my-schema", "no-key"), None)

    def test_skips_descriptors_from_other_schemas(self, test_context: OrcaTestContext) -> None:
        """Test _build_mappings_from_descriptors only includes matching schema."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingDescriptor, get_registry

        registry = get_registry()

        registry._descriptors[("schema-a", "enabled")] = SettingDescriptor(
            gsettings_key="enabled",
            schema="schema-a",
            gtype="b",
            default=True,
            settings_key="enableA",
        )
        registry._descriptors[("schema-b", "enabled")] = SettingDescriptor(
            gsettings_key="enabled",
            schema="schema-b",
            gtype="b",
            default=False,
            settings_key="enableB",
        )
        try:
            mappings_a = registry._build_mappings_from_descriptors("schema-a")
            assert len(mappings_a) == 1
            assert mappings_a[0].json_key == "enableA"

            mappings_b = registry._build_mappings_from_descriptors("schema-b")
            assert len(mappings_b) == 1
            assert mappings_b[0].json_key == "enableB"
        finally:
            registry._descriptors.pop(("schema-a", "enabled"), None)
            registry._descriptors.pop(("schema-b", "enabled"), None)

    def test_builds_enum_map_from_registered_enum(self, test_context: OrcaTestContext) -> None:
        """Test _build_mappings_from_descriptors builds enum_map from registered enums."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingDescriptor, get_registry

        registry = get_registry()

        registry._enums["org.gnome.Orca.Verbosity"] = {"brief": 0, "verbose": 1}
        registry._descriptors[("my-schema", "verbosity")] = SettingDescriptor(
            gsettings_key="verbosity",
            schema="my-schema",
            gtype="",
            default=1,
            settings_key="verbosityLevel",
            genum="org.gnome.Orca.Verbosity",
        )
        try:
            mappings = registry._build_mappings_from_descriptors("my-schema")
            assert len(mappings) == 1
            assert mappings[0].enum_map == {0: "brief", 1: "verbose"}
        finally:
            registry._descriptors.pop(("my-schema", "verbosity"), None)
            registry._enums.pop("org.gnome.Orca.Verbosity", None)

    def test_returns_empty_list_for_unknown_schema(self, test_context: OrcaTestContext) -> None:
        """Test _build_mappings_from_descriptors returns [] for unknown schema."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()
        mappings = registry._build_mappings_from_descriptors("nonexistent-schema")
        assert not mappings


@pytest.mark.unit
class TestGetSettingsMappingsFallback:
    """Tests for _get_settings_mappings fallback to descriptors."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    def test_prefers_explicit_mappings(self, test_context: OrcaTestContext) -> None:
        """Test _get_settings_mappings prefers explicitly registered mappings."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingDescriptor, SettingsMapping, get_registry

        registry = get_registry()

        explicit = [SettingsMapping("enableFoo", "foo-enabled", "b", True)]
        registry.register_settings_mappings("test-pref", explicit)

        registry._descriptors[("test-pref", "foo-enabled")] = SettingDescriptor(
            gsettings_key="foo-enabled",
            schema="test-pref",
            gtype="b",
            default=False,
            settings_key="enableFoo",
        )
        try:
            result = registry._get_settings_mappings("test-pref")
            assert result is explicit
        finally:
            registry._mappings.pop("test-pref", None)
            registry._descriptors.pop(("test-pref", "foo-enabled"), None)

    def test_falls_back_to_descriptors(self, test_context: OrcaTestContext) -> None:
        """Test _get_settings_mappings falls back to descriptors when no explicit mappings."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingDescriptor, get_registry

        registry = get_registry()

        registry._descriptors[("test-fb", "bar")] = SettingDescriptor(
            gsettings_key="bar",
            schema="test-fb",
            gtype="s",
            default="",
            settings_key="barSetting",
        )
        try:
            result = registry._get_settings_mappings("test-fb")
            assert len(result) == 1
            assert result[0].json_key == "barSetting"
            assert result[0].gs_key == "bar"
        finally:
            registry._descriptors.pop(("test-fb", "bar"), None)


@pytest.mark.unit
class TestSaveToGsettings:
    """Tests for save_to_gsettings."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    def test_save_writes_to_profile(self, test_context: OrcaTestContext) -> None:
        """Test save_to_gsettings writes values to GSettings for the active profile."""

        self._setup(test_context)
        from orca.gsettings_registry import (
            GSettingsSchemaHandle,
            SettingsMapping,
            get_registry,
        )

        registry = get_registry()
        registry.set_active_profile("default")

        registry.register_settings_mappings(
            "test-save",
            [SettingsMapping("enableFoo", "foo-enabled", "b", True)],
        )

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")
        mock_gs = test_context.Mock()
        mock_get = test_context.patch_object(handle, "get_for_profile", return_value=mock_gs)

        try:
            registry.save_to_gsettings(handle, "test-save", {"enableFoo": False})
            mock_get.assert_called_once_with("default")
            mock_gs.set_boolean.assert_called_once_with("foo-enabled", False)
        finally:
            registry._mappings.pop("test-save", None)

    def test_save_skips_when_no_gs(self, test_context: OrcaTestContext) -> None:
        """Test save_to_gsettings does nothing when get_for_profile returns None."""

        self._setup(test_context)
        from orca.gsettings_registry import (
            GSettingsSchemaHandle,
            SettingsMapping,
            get_registry,
        )

        registry = get_registry()
        registry.set_active_profile("default")

        registry.register_settings_mappings(
            "test-save-none",
            [SettingsMapping("enableFoo", "foo-enabled", "b", True)],
        )

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")
        mock_get = test_context.patch_object(handle, "get_for_profile", return_value=None)

        try:
            registry.save_to_gsettings(handle, "test-save-none", {"enableFoo": False})
            mock_get.assert_called_once_with("default")
        finally:
            registry._mappings.pop("test-save-none", None)

    def test_save_uses_descriptor_mappings(self, test_context: OrcaTestContext) -> None:
        """Test save_to_gsettings works with auto-generated mappings from descriptors."""

        self._setup(test_context)
        from orca.gsettings_registry import (
            GSettingsSchemaHandle,
            SettingDescriptor,
            get_registry,
        )

        registry = get_registry()
        registry.set_active_profile("default")

        registry._descriptors[("test-desc-save", "bar-enabled")] = SettingDescriptor(
            gsettings_key="bar-enabled",
            schema="test-desc-save",
            gtype="b",
            default=True,
            settings_key="enableBar",
        )

        handle = GSettingsSchemaHandle("org.gnome.Orca.Test", "test")
        mock_gs = test_context.Mock()
        test_context.patch_object(handle, "get_for_profile", return_value=mock_gs)

        try:
            registry.save_to_gsettings(handle, "test-desc-save", {"enableBar": False})
            mock_gs.set_boolean.assert_called_once_with("bar-enabled", False)
        finally:
            registry._descriptors.pop(("test-desc-save", "bar-enabled"), None)


@pytest.mark.unit
class TestDescriptorKeyCollision:
    """Tests verifying (schema, key) tuple prevents collisions."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    def test_same_key_different_schemas_coexist(self, test_context: OrcaTestContext) -> None:
        """Test that the same gsettings key in different schemas does not collide."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()

        @registry.gsetting(
            key="enabled",
            schema="braille",
            gtype="b",
            default=True,
            summary="Test",
            settings_key="enableBraille",
        )
        def get_braille_enabled():
            return True

        @registry.gsetting(
            key="enabled",
            schema="sound",
            gtype="b",
            default=True,
            summary="Test",
            settings_key="enableSound",
        )
        def get_sound_enabled():
            return True

        try:
            assert ("braille", "enabled") in registry._descriptors
            assert ("sound", "enabled") in registry._descriptors
            assert registry._descriptors[("braille", "enabled")].settings_key == "enableBraille"
            assert registry._descriptors[("sound", "enabled")].settings_key == "enableSound"
        finally:
            registry._descriptors.pop(("braille", "enabled"), None)
            registry._descriptors.pop(("sound", "enabled"), None)


@pytest.mark.unit
class TestMigrateAll:
    """Tests for migrate_all."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    def test_migrate_all_calls_migrate_schema_for_each(self, test_context: OrcaTestContext) -> None:
        """Test migrate_all iterates through all registered schemas."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()

        registry._schemas["test-alpha"] = "org.gnome.Orca.TestAlpha"
        registry._schemas["test-beta"] = "org.gnome.Orca.TestBeta"

        migrated_schemas: list[str] = []

        def tracking_migrate(_handle, schema_name, _prefs_dir, _profiles):
            migrated_schemas.append(schema_name)
            return False

        try:
            test_context.patch_object(registry, "_is_migration_done", return_value=False)
            test_context.patch_object(registry, "_stamp_migration_done")
            test_context.patch_object(registry, "migrate_schema", side_effect=tracking_migrate)
            registry.migrate_all("/tmp/test", [])
            assert "test-alpha" in migrated_schemas
            assert "test-beta" in migrated_schemas
        finally:
            registry._schemas.pop("test-alpha", None)
            registry._schemas.pop("test-beta", None)

    def test_migrate_all_returns_true_when_any_migrated(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test migrate_all returns True when at least one schema was migrated."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()

        registry._schemas["test-m1"] = "org.gnome.Orca.TestM1"
        registry._schemas["test-m2"] = "org.gnome.Orca.TestM2"

        def selective_migrate(_handle, schema_name, _prefs_dir, _profiles):
            return schema_name == "test-m2"

        try:
            test_context.patch_object(registry, "_is_migration_done", return_value=False)
            test_context.patch_object(registry, "_stamp_migration_done")
            test_context.patch_object(registry, "migrate_schema", side_effect=selective_migrate)
            assert registry.migrate_all("/tmp/test", []) is True
        finally:
            registry._schemas.pop("test-m1", None)
            registry._schemas.pop("test-m2", None)

    def test_migrate_all_returns_false_when_none_migrated(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test migrate_all returns False when no schemas were migrated."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()

        registry._schemas["test-n1"] = "org.gnome.Orca.TestN1"

        try:
            test_context.patch_object(registry, "_is_migration_done", return_value=False)
            test_context.patch_object(registry, "_stamp_migration_done")
            test_context.patch_object(registry, "migrate_schema", return_value=False)
            assert registry.migrate_all("/tmp/test", []) is False
        finally:
            registry._schemas.pop("test-n1", None)

    def test_migrate_all_creates_handle_with_correct_ids(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test migrate_all creates GSettingsSchemaHandle with correct schema_id and path."""

        self._setup(test_context)
        from orca.gsettings_registry import get_registry

        registry = get_registry()

        registry._schemas["typing-echo"] = "org.gnome.Orca.TypingEcho"

        captured_handles: list = []

        def capture_migrate(handle, schema_name, _prefs_dir, _profiles):
            captured_handles.append((handle.get_schema_id(), schema_name))
            return False

        try:
            test_context.patch_object(registry, "_is_migration_done", return_value=False)
            test_context.patch_object(registry, "_stamp_migration_done")
            test_context.patch_object(registry, "migrate_schema", side_effect=capture_migrate)
            registry.migrate_all("/tmp/test", [])
            assert len(captured_handles) >= 1
            found = [h for h in captured_handles if h[1] == "typing-echo"]
            assert len(found) == 1
            assert found[0][0] == "org.gnome.Orca.TypingEcho"
        finally:
            registry._schemas.pop("typing-echo", None)

    def test_migrate_all_skips_schemas_without_mappings(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test migrate_all gracefully handles schemas with no mappable descriptors."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingDescriptor, get_registry

        registry = get_registry()

        registry._schemas["test-nomaps"] = "org.gnome.Orca.TestNoMaps"
        registry._descriptors[("test-nomaps", "entries")] = SettingDescriptor(
            gsettings_key="entries",
            schema="test-nomaps",
            gtype="a{ss}",
            default={},
            settings_key=None,
        )

        try:
            mappings = registry._build_mappings_from_descriptors("test-nomaps")
            assert not mappings
        finally:
            registry._schemas.pop("test-nomaps", None)
            registry._descriptors.pop(("test-nomaps", "entries"), None)


@pytest.mark.unit
class TestStringArraySupport:
    """Tests for string array (as) type support in JSON↔GSettings conversion."""

    def _setup(self, test_context: OrcaTestContext):
        """Set up dependencies."""

        additional_modules = [
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        test_context.setup_shared_dependencies(additional_modules)

    def test_json_to_gsettings_string_array(self, test_context: OrcaTestContext) -> None:
        """Test _json_to_gsettings writes string array values."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-as",
            [SettingsMapping("textAttributesToSpeak", "attributes-to-speak", "as", [])],
        )

        mock_gs = test_context.Mock()
        attrs = ["size", "weight", "style"]
        try:
            result = registry._json_to_gsettings(
                {"textAttributesToSpeak": attrs}, mock_gs, "test-as"
            )
            assert result is True
            mock_gs.set_strv.assert_called_once_with("attributes-to-speak", attrs)
        finally:
            registry._mappings.pop("test-as", None)

    def test_json_to_gsettings_string_array_skips_default(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _json_to_gsettings skips string array when it matches default."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        default_attrs = ["size", "weight"]
        registry.register_settings_mappings(
            "test-as-skip",
            [SettingsMapping("textAttributesToSpeak", "attributes-to-speak", "as", default_attrs)],
        )

        mock_gs = test_context.Mock()
        try:
            result = registry._json_to_gsettings(
                {"textAttributesToSpeak": ["size", "weight"]}, mock_gs, "test-as-skip"
            )
            assert result is False
            mock_gs.set_strv.assert_not_called()
        finally:
            registry._mappings.pop("test-as-skip", None)

    def test_gsettings_to_json_string_array(self, test_context: OrcaTestContext) -> None:
        """Test _gsettings_to_json reads string array values."""

        self._setup(test_context)
        from orca.gsettings_registry import SettingsMapping, get_registry

        registry = get_registry()

        registry.register_settings_mappings(
            "test-as-read",
            [SettingsMapping("textAttributesToSpeak", "attributes-to-speak", "as", [])],
        )

        mock_gs = test_context.Mock()
        mock_variant = test_context.Mock()
        mock_variant.unpack.return_value = ["size", "weight", "style"]
        mock_gs.get_user_value.return_value = mock_variant

        try:
            result = registry._gsettings_to_json(mock_gs, "test-as-read")
            assert result == {"textAttributesToSpeak": ["size", "weight", "style"]}
        finally:
            registry._mappings.pop("test-as-read", None)
