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

# pylint: disable=import-outside-toplevel,protected-access

"""Integration tests for GSettings support.

These tests exercise Orca's GSettings infrastructure against real Gio.Settings
objects backed by the in-memory backend. Unlike the unit tests which mock the
GSettings layer, these verify that schemas compile correctly, the layered lookup
fallback chain works end-to-end, and save/load round-trips preserve data.
"""

from __future__ import annotations

import pytest
from gi.repository import Gio


@pytest.mark.gsettings
class TestSchemaRegistration:
    """Verifies @gsettings_schema decorators produce usable compiled schemas."""

    def test_all_expected_schemas_registered(self, gsettings_registry) -> None:
        """All decorated schemas should be present in the registry."""

        expected = {
            "braille",
            "caret-navigation",
            "chat",
            "document",
            "flat-review",
            "keybindings",
            "live-regions",
            "metadata",
            "mouse-review",
            "pronunciations",
            "say-all",
            "sound",
            "speech",
            "spellcheck",
            "structural-navigation",
            "system-information",
            "table-navigation",
            "text-attributes",
            "typing-echo",
            "voice",
        }
        registered = set(gsettings_registry.get_schema_names())
        assert expected == registered

    def test_each_schema_resolves_to_compiled_gio_schema(self, gsettings_registry) -> None:
        """Every registered schema ID should be findable in the compiled schema source."""

        source = Gio.SettingsSchemaSource.get_default()
        for name, schema_id in gsettings_registry._schemas.items():
            schema = source.lookup(schema_id, True)
            assert schema is not None, f"Schema {schema_id!r} ({name}) not compiled"


@pytest.mark.gsettings
class TestLayeredLookupFallback:
    """Verifies the 3-tier fallback: app override -> active profile -> default profile."""

    def test_returns_none_when_no_user_values_exist(
        self, gsettings_handle, gsettings_profile
    ) -> None:
        """With nothing set at any layer, layered lookup returns None."""

        handle = gsettings_handle("speech")
        assert handle.get_boolean("enable") is None

    def test_finds_value_in_default_profile(self, gsettings_handle, gsettings_profile) -> None:
        """A value set in the default profile should be returned."""

        handle = gsettings_handle("speech")
        handle.get_for_profile("default").set_boolean("enable", False)
        assert handle.get_boolean("enable") is False

    def test_active_profile_overrides_default(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """When both profiles have values, the active profile wins."""

        handle = gsettings_handle("speech")
        handle.get_for_profile("default").set_boolean("enable", False)
        handle.get_for_profile("spanish").set_boolean("enable", True)

        gsettings_registry.set_active_profile("spanish")
        assert handle.get_boolean("enable") is True

    def test_active_profile_falls_back_to_default(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """When the active profile has no value, the default profile's value is used."""

        handle = gsettings_handle("speech")
        handle.get_for_profile("default").set_boolean("enable", False)

        gsettings_registry.set_active_profile("spanish")
        assert handle.get_boolean("enable") is False

    def test_app_override_takes_precedence(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """An app-specific value should win over both profile layers."""

        handle = gsettings_handle("speech")
        handle.get_for_profile("default").set_boolean("enable", False)
        handle.get_for_app("firefox").set_boolean("enable", True)

        gsettings_registry.set_active_app("Firefox")
        assert handle.get_boolean("enable") is True

    def test_no_app_override_falls_through_to_profile(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """When an app is active but has no override, the profile value is used."""

        handle = gsettings_handle("speech")
        handle.get_for_profile("default").set_boolean("enable", False)

        gsettings_registry.set_active_app("Firefox")
        assert handle.get_boolean("enable") is False


@pytest.mark.gsettings
class TestRegistryLookup:
    """Tests registry-level lookup: runtime overrides, defaults, voice routing, enums."""

    def test_default_parameter_used_when_no_value_exists(
        self, gsettings_registry, gsettings_profile
    ) -> None:
        """The default= parameter should be returned when nothing is set in dconf."""

        result = gsettings_registry.layered_lookup("speech", "enable", "b", default=True)
        assert result is True

    def test_runtime_override_takes_precedence_over_dconf(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """A runtime override should win over a value stored in dconf."""

        handle = gsettings_handle("speech")
        handle.get_for_profile("default").set_boolean("enable", True)

        gsettings_registry.set_runtime_value("speech", "enable", False)
        try:
            assert gsettings_registry.layered_lookup("speech", "enable", "b") is False
        finally:
            gsettings_registry.remove_runtime_value("speech", "enable")

    def test_voice_type_routes_to_correct_sub_path(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """voice_type='uppercase' should read from voices/uppercase, not voices/default."""

        handle = gsettings_handle("voice")
        handle.get_for_profile("default", sub_path="voices/default").set_double("pitch", 1.0)
        handle.get_for_profile("default", sub_path="voices/uppercase").set_double("pitch", 9.0)

        default_pitch = gsettings_registry.layered_lookup(
            "voice", "pitch", "d", voice_type="default"
        )
        uppercase_pitch = gsettings_registry.layered_lookup(
            "voice", "pitch", "d", voice_type="uppercase"
        )
        assert default_pitch == 1.0
        assert uppercase_pitch == 9.0

    def test_enum_lookup_returns_string_nick(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """Enum settings should be returned as their string nick, not an int."""

        handle = gsettings_handle("speech")
        handle.get_for_profile("default").set_string("verbosity-level", "brief")

        result = gsettings_registry.layered_lookup(
            "speech",
            "verbosity-level",
            "",
            genum="org.gnome.Orca.VerbosityLevel",
        )
        assert result == "brief"


@pytest.mark.gsettings
class TestSaveSchema:
    """Tests save_schema, the preferences UI path for writing settings to dconf."""

    def test_round_trip_multiple_types(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """Boolean, string, and int values should survive a save_schema round-trip."""

        gsettings_registry.save_schema(
            "speech",
            {"enable": False, "synthesizer": "espeak-ng", "repeated-character-limit": 8},
            "default",
        )

        handle = gsettings_handle("speech")
        assert handle.get_boolean("enable") is False
        assert handle.get_string("synthesizer") == "espeak-ng"
        assert handle.get_int("repeated-character-limit") == 8

    def test_app_override_isolation(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """Settings saved with an app_name should not be visible without that app active."""

        gsettings_registry.save_schema("speech", {"enable": False}, "default", app_name="firefox")

        handle = gsettings_handle("speech")
        assert handle.get_boolean("enable") is None

        gsettings_registry.set_active_app("firefox")
        assert handle.get_boolean("enable") is False

    def test_skip_defaults_resets_default_valued_key(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """skip_defaults should reset a key whose value matches the descriptor default."""

        handle = gsettings_handle("speech")
        handle.get_for_profile("default").set_boolean("enable", False)
        assert handle.get_boolean("enable") is False

        gsettings_registry.save_schema("speech", {"enable": True}, "default", skip_defaults=True)
        assert handle.get_boolean("enable") is None

    def test_enum_saved_by_nick(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """Enum values passed as string nicks should be written correctly."""

        gsettings_registry.save_schema("speech", {"verbosity-level": "brief"}, "default")

        handle = gsettings_handle("speech")
        assert handle.get_string("verbosity-level") == "brief"

    def test_enum_saved_by_int(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """Enum values passed as ints should be resolved to their nick before writing."""

        gsettings_registry.save_schema(
            "speech",
            {"progress-bar-speech-verbosity": 2},
            "default",
        )

        handle = gsettings_handle("speech")
        assert handle.get_string("progress-bar-speech-verbosity") == "window"


@pytest.mark.gsettings
class TestProfileOperations:
    """Tests profile reset, rename, and copy operations across all schemas."""

    def test_reset_profile_clears_all_user_keys(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """reset_profile should remove all user-set values for that profile."""

        handle = gsettings_handle("speech")
        gs = handle.get_for_profile("doomed")
        gs.set_boolean("enable", False)
        gs.set_string("synthesizer", "espeak-ng")

        gsettings_registry.reset_profile("doomed")

        gs_after = Gio.Settings.new_with_path(
            handle.get_schema_id(), "/org/gnome/orca/doomed/speech/"
        )
        assert gs_after.get_user_value("enable") is None
        assert gs_after.get_user_value("synthesizer") is None

    def test_rename_profile_moves_keys(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """rename_profile should copy keys to the new path and clear the old."""

        handle = gsettings_handle("speech")
        handle.get_for_profile("old-name").set_boolean("enable", False)

        gsettings_registry.rename_profile("old-name", "New Label", "new-name")

        gs_new = Gio.Settings.new_with_path(
            handle.get_schema_id(), "/org/gnome/orca/new-name/speech/"
        )
        assert gs_new.get_boolean("enable") is False

        gs_old = Gio.Settings.new_with_path(
            handle.get_schema_id(), "/org/gnome/orca/old-name/speech/"
        )
        assert gs_old.get_user_value("enable") is None

    def test_rename_profile_updates_metadata(self, gsettings_registry, gsettings_profile) -> None:
        """rename_profile should set display-name and internal-name on the new path."""

        gs_old = gsettings_registry.get_settings("metadata", "src-profile")
        gs_old.set_string("display-name", "Old Label")

        gsettings_registry.rename_profile("src-profile", "Shiny New", "dest-profile")

        gs_new = gsettings_registry.get_settings("metadata", "dest-profile")
        assert gs_new.get_string("display-name") == "Shiny New"
        assert gs_new.get_string("internal-name") == "dest-profile"

    def test_copy_user_keys(self, gsettings_registry, gsettings_handle, gsettings_profile) -> None:
        """copy_user_keys should duplicate user-set values without affecting the source."""

        handle = gsettings_handle("speech")
        gs_src = handle.get_for_profile("default")
        gs_src.set_boolean("enable", False)
        gs_src.set_string("synthesizer", "espeak-ng")

        gs_dest = handle.get_for_profile("cloned")
        gsettings_registry.copy_user_keys(gs_src, gs_dest)

        assert gs_dest.get_boolean("enable") is False
        assert gs_dest.get_string("synthesizer") == "espeak-ng"
        assert gs_src.get_user_value("enable") is not None


@pytest.mark.gsettings
class TestDictSchemas:
    """Tests pronunciation and keybinding schemas (dict serialization)."""

    def test_pronunciation_round_trip(self, gsettings_registry, gsettings_profile) -> None:
        """Pronunciations should survive import -> get_pronunciations."""

        from orca import gsettings_migrator

        gs = gsettings_registry.get_settings("pronunciations", "default", "pronunciations")
        gsettings_migrator.import_pronunciations(
            gs, {"orca": ["orca", "or-kah"], "GNOME": ["GNOME", "guh-nome"]}
        )

        result = gsettings_registry.get_pronunciations("default")
        assert result == {"orca": "or-kah", "GNOME": "guh-nome"}

    def test_keybinding_round_trip(self, gsettings_registry, gsettings_profile) -> None:
        """Keybindings should survive import -> get_keybindings."""

        from orca import gsettings_migrator

        gs = gsettings_registry.get_settings("keybindings", "default", "keybindings")
        gsettings_migrator.import_keybindings(gs, {"doAction": [["65", "0", "1", "1"]]})

        result = gsettings_registry.get_keybindings("default")
        assert result["doAction"] == [["65", "0", "1", "1"]]

    def test_pronunciations_empty_for_unset_profile(
        self, gsettings_registry, gsettings_profile
    ) -> None:
        """get_pronunciations should return {} for a profile with no data."""

        assert gsettings_registry.get_pronunciations("nonexistent") == {}

    def test_keybindings_empty_for_unset_profile(
        self, gsettings_registry, gsettings_profile
    ) -> None:
        """get_keybindings should return {} for a profile with no data."""

        assert gsettings_registry.get_keybindings("nonexistent") == {}


@pytest.mark.gsettings
class TestMigrationRoundTrip:
    """Tests JSON-to-dconf migration via _write_profile_settings."""

    def test_legacy_keys_land_in_correct_schemas(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """Legacy prefs should be mapped to their correct GSettings schema and key."""

        general = {
            "enableSpeech": False,
            "enableBraille": False,
        }
        gsettings_registry._write_profile_settings("migrated", general, {}, {})

        gsettings_registry.set_active_profile("migrated")
        speech = gsettings_handle("speech")
        braille = gsettings_handle("braille")

        assert speech.get_boolean("enable") is False
        assert braille.get_boolean("enabled") is False

    def test_migration_includes_pronunciations(self, gsettings_registry, gsettings_profile) -> None:
        """_write_profile_settings should also persist pronunciations."""

        gsettings_registry._write_profile_settings(
            "with-pron", {"enableSpeech": True}, {"orca": ["orca", "or-kah"]}, {}
        )
        assert gsettings_registry.get_pronunciations("with-pron") == {"orca": "or-kah"}

    def test_migration_includes_keybindings(self, gsettings_registry, gsettings_profile) -> None:
        """_write_profile_settings should also persist keybindings."""

        gsettings_registry._write_profile_settings(
            "with-kb", {"enableSpeech": True}, {}, {"doAction": [["65", "0", "1", "1"]]}
        )
        result = gsettings_registry.get_keybindings("with-kb")
        assert "doAction" in result

    def test_migration_sets_profile_metadata(self, gsettings_registry, gsettings_profile) -> None:
        """_write_profile_settings should write display-name and internal-name."""

        general = {"enableSpeech": True, "profile": ["My Profile", "my-profile"]}
        gsettings_registry._write_profile_settings("my-profile", general, {}, {})

        gs = gsettings_registry.get_settings("metadata", "my-profile")
        assert gs.get_string("display-name") == "My Profile"
        assert gs.get_string("internal-name") == "my-profile"
