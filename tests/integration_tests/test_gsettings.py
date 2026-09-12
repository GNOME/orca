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
            "extensions",
            "flat-review",
            "keybindings",
            "live-regions",
            "math-presentation",
            "metadata",
            "mouse-review",
            "pronunciations",
            "say-all",
            "sleep-mode",
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
        """voice_type='uppercase' should read from voice-sets/primary/uppercase."""

        from orca.gsettings_registry import GSettingsRegistry

        handle = gsettings_handle("voice")
        handle.get_for_profile(
            "default", sub_path=GSettingsRegistry.voice_set_sub_path("default")
        ).set_double("pitch", 1.0)
        handle.get_for_profile(
            "default", sub_path=GSettingsRegistry.voice_set_sub_path("uppercase")
        ).set_double("pitch", 9.0)

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

    def test_round_trip_strv(self, gsettings_registry, gsettings_handle, gsettings_profile) -> None:
        """String-array values should survive a save_schema round-trip."""

        gsettings_registry.save_schema(
            "keybindings",
            {"desktop-modifier-keys": ["Insert"], "laptop-modifier-keys": ["Caps_Lock"]},
            "default",
        )

        handle = gsettings_handle("keybindings")
        assert handle.get_strv("desktop-modifier-keys") == ["Insert"]
        assert handle.get_strv("laptop-modifier-keys") == ["Caps_Lock"]

    def test_round_trip_sleep_mode_apps(
        self, gsettings_registry, gsettings_handle, gsettings_profile
    ) -> None:
        """Sleep mode app list should survive a save_schema round-trip."""

        gsettings_registry.save_schema(
            "sleep-mode",
            {"apps": ["chromium-browser", "virt-manager"]},
            "default",
        )

        handle = gsettings_handle("sleep-mode")
        assert handle.get_strv("apps") == ["chromium-browser", "virt-manager"]

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
@pytest.mark.parametrize(
    "property_name, key, acss_key, primary_value, system_value, set_value, step",
    [
        ("rate", "rate", "rate", 65, 59, 50, 5),
        ("pitch", "pitch", "average-pitch", 6.0, 4.0, 5.0, 0.5),
        ("pitch_range", "pitch-range", "pitch-range", 6.0, 4.0, 5.0, 0.5),
        ("volume", "volume", "gain", 6.0, 4.0, 5.0, 0.5),
    ],
)
@pytest.mark.parametrize("configured", [False, True])
@pytest.mark.parametrize("system_voice", [False, True])
def test_voice_adjustment_targets_active_voice_set(
    gsettings_registry,
    gsettings_handle,
    gsettings_profile,
    monkeypatch,
    property_name,
    key,
    acss_key,
    primary_value,
    system_value,
    set_value,
    step,
    configured,
    system_voice,
) -> None:
    """Voice commands affect the selected set without changing primary voices or stored settings."""

    from orca import speech_manager, speechserver
    from orca.acss import ACSS

    registry = gsettings_registry
    handle = gsettings_handle("voice")
    setter = "set_int" if key == "rate" else "set_double"
    for voice_type, value in (("default", primary_value), ("system", system_value)):
        gs = handle.get_for_profile("default", registry.voice_set_sub_path(voice_type))
        gs.set_boolean("established", True)
        getattr(gs, setter)(key, value)

    selected = handle.get_for_profile("default", registry.voice_set_sub_path("default", "it"))
    selected.set_boolean("established", True)
    selected.set_string("family-lang", "it")
    if configured:
        getattr(selected, setter)(key, set_value)
    if system_voice:
        system = handle.get_for_profile("default", registry.voice_set_sub_path("system", "it"))
        system.set_boolean("established", True)
        getattr(system, setter)(key, system_value)

    manager = speech_manager.get_manager()
    monkeypatch.setattr(manager, "_active_voice_set", "primary")
    monkeypatch.setattr(manager, "_server", speechserver.SpeechServer())
    monkeypatch.setattr(manager, "get_voice_set_names", lambda: ["it"])
    get_value = getattr(manager, f"get_{property_name}")
    increase = getattr(manager, f"increase_{property_name}")
    decrease = getattr(manager, f"decrease_{property_name}")
    registry.clear_runtime_values()
    try:
        assert manager.set_active_voice_set("it")
        initial_value = set_value if configured else primary_value
        assert get_value() == initial_value
        assert increase(notify_user=False)
        assert get_value() == initial_value + step
        registry.set_active_app("another-app")
        voice = manager.apply_voice_set(ACSS({acss_key: primary_value}))
        assert voice[acss_key] == initial_value + step
        assert voice[ACSS.FAMILY]["lang"] == "it"
        voice = ACSS({acss_key: system_value})
        voice[ACSS.VOICE_TYPE] = "system"
        voice = manager.apply_voice_set(voice)
        assert voice[acss_key] == (initial_value + step if system_voice else system_value)

        assert manager.set_active_voice_set("primary")
        assert get_value() == primary_value
        assert manager.get_voice_properties("system")[acss_key] == system_value
        assert manager.set_active_voice_set("it")
        assert get_value() == initial_value + step
        assert decrease(notify_user=False)
        assert get_value() == initial_value
        voice = manager.apply_voice_set(ACSS({acss_key: primary_value}))
        assert voice[acss_key] == initial_value
        stored = selected.get_user_value(key)
        assert (stored.unpack() if stored is not None else None) == (
            set_value if configured else None
        )
        registry.clear_runtime_values()
        assert get_value() == initial_value
    finally:
        registry.clear_runtime_values()


@pytest.mark.gsettings
@pytest.mark.parametrize(
    "language, dialect, expected_navigation_dialect",
    [("ro", None, ""), ("ro", "RO", "RO"), ("en", None, "GB"), ("en", "US", "US")],
)
def test_voice_set_dialect_overlay(
    gsettings_registry,
    gsettings_handle,
    gsettings_profile,
    monkeypatch,
    language,
    dialect,
    expected_navigation_dialect,
) -> None:
    """A set inherits a dialect only from the same language and preserves explicit dialects."""

    from orca import speech_manager, speechserver
    from orca.acss import ACSS

    registry = gsettings_registry
    handle = gsettings_handle("voice")
    selected = handle.get_for_profile("default", registry.voice_set_sub_path("default", "test"))
    selected.set_boolean("established", True)
    selected.set_string("family-lang", language)
    selected.set_string("family-name", "Romanian+grandma")
    selected.set_string("family-variant", "grandma")
    if dialect is not None:
        selected.set_string("family-dialect", dialect)
    manager = speech_manager.get_manager()
    monkeypatch.setattr(manager, "_active_voice_set", "test")
    server = speechserver.SpeechServer()

    navigation = manager.apply_voice_set(ACSS({"family": {"lang": "en", "dialect": "GB"}}))
    say_all = manager.apply_voice_set(ACSS())
    assert server.get_language_and_dialect(navigation[ACSS.FAMILY]) == (
        language,
        expected_navigation_dialect,
    )
    assert server.get_language_and_dialect(say_all[ACSS.FAMILY]) == (language, dialect or "")
    for voice in (navigation, say_all):
        assert voice[ACSS.FAMILY]["name"] == "Romanian+grandma"
        assert voice[ACSS.FAMILY]["variant"] == "grandma"


@pytest.mark.gsettings
class TestDictSchemas:
    """Tests pronunciation and keybinding schemas (dict serialization)."""

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
