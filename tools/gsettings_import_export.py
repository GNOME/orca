#!/usr/bin/python
# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
# pylint: disable=too-many-branches,too-many-statements,too-many-return-statements
# pylint: disable=too-many-lines
# gsettings_import_export.py
#
# Standalone tool for importing/exporting Orca settings between JSON and GSettings.
#
# Examples (run from the repo root):
#
# 1. Import your JSON settings into dconf. First preview what will be written:
#
#      python tools/gsettings_import_export.py import --dry-run $HOME/.local/share/orca
#
#    If the output looks correct, run the import for real. WARNING: This overwrites
#    any existing Orca settings in your dconf database. To clear imported settings
#    afterwards use "dconf reset -f /org/gnome/orca/" but note that this will not
#    restore whatever was there before the import.
#
#      python tools/gsettings_import_export.py import $HOME/.local/share/orca
#
#    View the result:
#
#      dconf dump /org/gnome/orca/
#
# 2. Export your dconf settings to JSON files that can be copied to another machine:
#
#      python tools/gsettings_import_export.py export /tmp/orca-export
#
#    This creates /tmp/orca-export/user-settings.conf and, if there are app-specific
#    overrides, /tmp/orca-export/app-settings/<AppName>.conf. To use the exported
#    files on another machine, copy them to $HOME/.local/share/orca/.
#
# 3. Roundtrip test (import → export → diff against original):
#
#      python tools/gsettings_import_export.py roundtrip \
#          $HOME/.local/share/orca /tmp/orca-roundtrip
#
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

"""Standalone tool for importing/exporting Orca settings between JSON and GSettings."""

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

from gi.repository import Gio

from generate_gsettings_schemas import _discover_schemas

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from orca.gsettings_migrator import (
    KEYBINDINGS_METADATA_KEYS,
    REVERSE_LEGACY_KEY_ALIASES,
    VOICE_FAMILY_FIELDS,
    VOICE_MIGRATION_MAP,
    VOICE_TYPES,
    SettingsMapping,
    add_legacy_aliases,
    apply_legacy_aliases,
    export_keybindings,
    export_pronunciations,
    export_synthesizer,
    export_voice,
    gsettings_to_json,
    hoist_keybindings_metadata,
    import_keybindings,
    import_pronunciations,
    import_synthesizer,
    import_voice,
    json_to_gsettings,
    resolve_enum_nick,
    sanitize_gsettings_path,
    stamp_version,
)

GSETTINGS_PATH_PREFIX = "/org/gnome/orca/"


# Enum settings where the legacy JSON format used string nicks rather than integers.
_JSON_STRING_ENUMS: frozenset[str] = frozenset({"capitalizationStyle"})


def _build_schemas_and_mappings() -> tuple[dict[str, str], dict[str, list[SettingsMapping]]]:
    """Build SCHEMAS and ALL_MAPPINGS from @gsetting decorators via AST parsing."""

    src_dir = Path(__file__).resolve().parent.parent / "src"
    schemas_raw, all_settings, all_enums = _discover_schemas(src_dir)

    schemas: dict[str, str] = dict(schemas_raw)
    mappings: dict[str, list[SettingsMapping]] = {}

    for setting in all_settings:
        migration_key = setting.get("migration_key")
        if migration_key is None:
            continue
        schema = setting["schema"]
        genum = setting.get("genum")
        enum_map: dict[int, str] | None = None
        string_enum = False
        if genum and genum in all_enums:
            enum_map = {v: k for k, v in all_enums[genum].items()}
            string_enum = migration_key in _JSON_STRING_ENUMS
        gtype = setting.get("gtype", "")
        mapping = SettingsMapping(
            migration_key, setting["key"], gtype, setting["default"], enum_map, string_enum
        )
        mappings.setdefault(schema, []).append(mapping)

    return schemas, mappings


SCHEMAS, ALL_MAPPINGS = _build_schemas_and_mappings()


class SchemaSource:
    """Loads GSettings schemas and creates Gio.Settings instances."""

    def __init__(self) -> None:
        self._source = Gio.SettingsSchemaSource.get_default()  # pylint: disable=no-value-for-parameter
        if self._source is None:
            print(
                "Error: No GSettings schema source found.\nXDG_DATA_DIRS may not be set correctly.",
                file=sys.stderr,
            )
            sys.exit(1)
        self._cache: dict[str, Gio.Settings] = {}

    def lookup(self, schema_id: str) -> "Gio.SettingsSchema | None":
        """Returns the schema for schema_id, or None if not installed."""
        return self._source.lookup(schema_id, True)

    def get_settings(self, schema_id: str, path: str) -> Gio.Settings:
        """Returns a Gio.Settings for the given schema and path, with caching."""
        cache_key = f"{schema_id}:{path}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        schema = self._source.lookup(schema_id, True)
        if schema is None:
            print(
                f"Error: {schema_id} not found in the default GSettings schema "
                "directories. \nIf you built Orca with a custom prefix "
                "(e.g. `meson setup -Dprefix=/my/prefix`), re-run with:"
                "\n\n  python tools/gsettings_import_export.py --prefix=/my/prefix ..."
                "\n\nNote: This is an experimental and currently unsupported tool.",
                file=sys.stderr,
            )
            sys.exit(1)
        gs = Gio.Settings.new_full(schema, None, path)
        self._cache[cache_key] = gs
        return gs


def _build_profile_path(profile: str, suffix: str) -> str:
    return f"{GSETTINGS_PATH_PREFIX}{sanitize_gsettings_path(profile)}/{suffix}/"


def _build_app_path(app_name: str, profile: str, suffix: str) -> str:
    profile = sanitize_gsettings_path(profile)
    app = sanitize_gsettings_path(app_name)
    return f"{GSETTINGS_PATH_PREFIX}{profile}/apps/{app}/{suffix}/"


def _import_mapped_settings(
    source: SchemaSource,
    schema_name: str,
    path: str,
    json_dict: dict,
    label: str,
    dry_run: bool,
    skip_defaults: bool = True,
) -> None:
    """Import mapped settings (speech or typing-echo) for a given path."""
    mappings = ALL_MAPPINGS.get(schema_name, [])
    if not mappings:
        return
    schema_id = SCHEMAS[schema_name]

    if dry_run:
        for m in mappings:
            if m.migration_key not in json_dict:
                continue
            value = json_dict[m.migration_key]
            if m.enum_map is not None:
                nick = resolve_enum_nick(value, m.enum_map)
                if nick is None:
                    continue
                if skip_defaults and nick == m.default:
                    continue
                print(f"  {path}{m.gs_key} = {nick!r}")
            elif not skip_defaults or value != m.default:
                print(f"  {path}{m.gs_key} = {value!r}")
        return

    gs = source.get_settings(schema_id, path)
    if json_to_gsettings(json_dict, gs, mappings, skip_defaults):
        stamp_version(gs)
        print(f"  Imported {schema_name} for {label}")


def _import_synthesizer_for_profile(
    source: SchemaSource,
    profile_prefs: dict,
    profile: str,
    label: str,
    dry_run: bool,
) -> None:
    """Import speechServerInfo as speech-server and synthesizer keys."""
    speech_server_info = profile_prefs.get("speechServerInfo")
    if speech_server_info is None or len(speech_server_info) < 2:
        return
    path = _build_profile_path(profile, "speech")

    if dry_run:
        print(f"  {path}speech-server = {speech_server_info[0]!r}")
        print(f"  {path}synthesizer = {speech_server_info[1]!r}")
        return

    gs = source.get_settings(SCHEMAS["speech"], path)
    if import_synthesizer(gs, profile_prefs):
        if gs.get_user_value("version") is None:
            stamp_version(gs)
        print(
            f"  Imported speech-server={speech_server_info[0]!r}, "
            f"synthesizer={speech_server_info[1]!r} for {label}"
        )


def _import_voice_for_path(
    source: SchemaSource,
    voice_data: dict,
    path: str,
    label: str,
    dry_run: bool,
    skip_defaults: bool = True,
) -> None:
    """Import ACSS voice data to GSettings."""
    if dry_run:
        for acss_key, (gs_key, gs_type, default) in VOICE_MIGRATION_MAP.items():
            if acss_key not in voice_data:
                continue
            value = voice_data[acss_key]
            if skip_defaults:
                if gs_type == "b" and bool(value) == default:
                    continue
                if gs_type == "i" and int(value) == default:
                    continue
                if gs_type == "d" and float(value) == default:
                    continue
            print(f"  {path}{gs_key} = {value!r}")
        family = voice_data.get("family", {})
        if isinstance(family, dict):
            for json_field, gs_key in VOICE_FAMILY_FIELDS.items():
                val = family.get(json_field)
                if val is not None and str(val):
                    print(f"  {path}{gs_key} = {str(val)!r}")
        return

    gs = source.get_settings(SCHEMAS["voice"], path)
    if import_voice(gs, voice_data, skip_defaults):
        stamp_version(gs)
        print(f"  Imported {label}")


def _import_pronunciations_for_path(
    source: SchemaSource,
    pronunciations_dict: dict,
    path: str,
    label: str,
    dry_run: bool,
) -> None:
    """Import pronunciation dictionary to GSettings."""
    if dry_run:
        converted: dict[str, str] = {}
        for key, value in pronunciations_dict.items():
            if isinstance(value, list) and len(value) >= 2:
                converted[key] = value[1]
            elif isinstance(value, list) and len(value) == 1:
                converted[key] = value[0]
            elif isinstance(value, str):
                converted[key] = value
        if converted:
            print(f"  {path}entries = {converted!r}")
        return

    gs = source.get_settings(SCHEMAS["pronunciations"], path)
    if import_pronunciations(gs, pronunciations_dict):
        stamp_version(gs)
        print(f"  Imported pronunciations for {label}")


def _import_keybindings_for_path(
    source: SchemaSource,
    keybindings_dict: dict,
    path: str,
    label: str,
    dry_run: bool,
) -> None:
    """Import keybinding overrides to GSettings."""
    if dry_run:
        converted: dict[str, list[list[str]]] = {}
        for key, value in keybindings_dict.items():
            if key in KEYBINDINGS_METADATA_KEYS:
                continue
            if isinstance(value, list):
                bindings: list[list[str]] = []
                for binding in value:
                    if isinstance(binding, list):
                        bindings.append([str(v) for v in binding])
                converted[key] = bindings
        if not converted:
            return
        for cmd, cmd_bindings in sorted(converted.items()):
            if not cmd_bindings:
                print(f"  {path}entries[{cmd}] = [] (unbound)")
            else:
                for b in cmd_bindings:
                    print(f"  {path}entries[{cmd}] = {b}")
        return

    gs = source.get_settings(SCHEMAS["keybindings"], path)
    if import_keybindings(gs, keybindings_dict):
        stamp_version(gs)
        print(f"  Imported keybindings for {label}")


def _write_metadata(
    source: SchemaSource,
    path: str,
    display_name: str,
    internal_name: str,
    label: str,
    dry_run: bool,
) -> None:
    """Write display-name and internal-name to the metadata schema at the given path."""
    if dry_run:
        print(f"  {path}display-name = {display_name!r}")
        if internal_name:
            print(f"  {path}internal-name = {internal_name!r}")
        return
    gs = source.get_settings(SCHEMAS["metadata"], path)
    gs.set_string("display-name", display_name)
    if internal_name:
        gs.set_string("internal-name", internal_name)
    print(f"  Stored metadata for {label}")


def _import_profile(
    source: SchemaSource,
    profile_name: str,
    profile_prefs: dict,
    dry_run: bool,
) -> None:
    """Import all settings for a single profile."""
    apply_legacy_aliases(profile_prefs)
    hoist_keybindings_metadata(profile_prefs)
    profile = sanitize_gsettings_path(profile_name)

    for schema_name in ALL_MAPPINGS:
        path = _build_profile_path(profile, schema_name)
        _import_mapped_settings(
            source,
            schema_name,
            path,
            profile_prefs,
            f"profile:{profile_name}",
            dry_run,
            skip_defaults=True,
        )

    _import_synthesizer_for_profile(
        source, profile_prefs, profile, f"profile:{profile_name}", dry_run
    )

    voices = profile_prefs.get("voices", {})
    for voice_type in VOICE_TYPES:
        voice_data = voices.get(voice_type, {})
        if not voice_data:
            continue
        vt = sanitize_gsettings_path(voice_type)
        path = _build_profile_path(profile, f"voices/{vt}")
        _import_voice_for_path(
            source,
            voice_data,
            path,
            f"voice:{voice_type}/profile:{profile_name}",
            dry_run,
            skip_defaults=True,
        )

    pronunciations = profile_prefs.get("pronunciations", {})
    if pronunciations:
        path = _build_profile_path(profile, "pronunciations")
        _import_pronunciations_for_path(
            source, pronunciations, path, f"profile:{profile_name}", dry_run
        )

    keybindings_data = profile_prefs.get("keybindings", {})
    if keybindings_data:
        path = _build_profile_path(profile, "keybindings")
        _import_keybindings_for_path(
            source, keybindings_data, path, f"profile:{profile_name}", dry_run
        )

    profile_label = profile_prefs.get("profile", [profile_name])[0]
    metadata_path = _build_profile_path(profile, "metadata")
    _write_metadata(
        source, metadata_path, profile_label, profile_name, f"profile:{profile_name}", dry_run
    )


def _import_app(
    source: SchemaSource,
    app_name: str,
    app_filepath: str,
    dry_run: bool,
) -> None:
    """Import all settings for a single app override file."""
    try:
        with open(app_filepath, encoding="utf-8") as f:
            prefs = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"  Warning: Could not read {app_filepath}: {e}", file=sys.stderr)
        return

    for profile_name, profile_data in prefs.get("profiles", {}).items():
        general = profile_data.get("general", {})
        apply_legacy_aliases(general)
        pronunciations = profile_data.get("pronunciations", {})
        app_keybindings = profile_data.get("keybindings", {})
        if not general and not pronunciations and not app_keybindings:
            continue
        label = f"profile:{profile_name}/app:{app_name}"

        for schema_name in ALL_MAPPINGS:
            path = _build_app_path(app_name, profile_name, schema_name)
            _import_mapped_settings(
                source, schema_name, path, general, label, dry_run, skip_defaults=False
            )

        voices = general.get("voices", {})
        for voice_type in VOICE_TYPES:
            voice_data = voices.get(voice_type, {})
            if not voice_data:
                continue
            vt = sanitize_gsettings_path(voice_type)
            path = _build_app_path(app_name, profile_name, f"voices/{vt}")
            _import_voice_for_path(source, voice_data, path, f"voice:{voice_type}/{label}", dry_run)

        if pronunciations:
            path = _build_app_path(app_name, profile_name, "pronunciations")
            _import_pronunciations_for_path(source, pronunciations, path, label, dry_run)

        if app_keybindings:
            path = _build_app_path(app_name, profile_name, "keybindings")
            _import_keybindings_for_path(source, app_keybindings, path, label, dry_run)

        metadata_path = _build_app_path(app_name, profile_name, "metadata")
        _write_metadata(source, metadata_path, app_name, profile_name, label, dry_run)

        profile = sanitize_gsettings_path(profile_name)
        profile_metadata_path = _build_profile_path(profile, "metadata")
        if dry_run:
            print(f"  {profile_metadata_path}internal-name = {profile_name!r} (if not set)")
        else:
            gs = source.get_settings(SCHEMAS["metadata"], profile_metadata_path)
            if gs.get_user_value("internal-name") is None:
                gs.set_string("internal-name", profile_name)


def import_settings(settings_dir: str, source: SchemaSource, dry_run: bool = False) -> None:
    """Import JSON settings from a directory into GSettings/dconf."""
    settings_file = os.path.join(settings_dir, "user-settings.conf")
    if not os.path.isfile(settings_file):
        print(f"Error: {settings_file} not found", file=sys.stderr)
        sys.exit(1)

    with open(settings_file, encoding="utf-8") as f:
        prefs = json.load(f)

    profiles = prefs.get("profiles", {})
    if not profiles:
        print("No profiles found in settings file.", file=sys.stderr)
        return

    for profile_name, profile_data in profiles.items():
        print(f"Profile: {profile_name}")
        _import_profile(source, profile_name, profile_data, dry_run)

    app_dir = os.path.join(settings_dir, "app-settings")
    if os.path.isdir(app_dir):
        for filename in sorted(os.listdir(app_dir)):
            if not filename.endswith(".conf"):
                continue
            app_name = filename[:-5]
            print(f"App: {app_name}")
            _import_app(source, app_name, os.path.join(app_dir, filename), dry_run)


def _export_profile(source: SchemaSource, profile_name: str) -> dict:
    """Export all settings for a profile from dconf to a JSON-compatible dict."""
    profile_data: dict[str, Any] = {}
    profile = sanitize_gsettings_path(profile_name)

    # Mapped settings (speech, typing-echo, caret-navigation, etc.)
    for schema_name, mappings in ALL_MAPPINGS.items():
        try:
            path = _build_profile_path(profile, schema_name)
            gs = source.get_settings(SCHEMAS[schema_name], path)
            profile_data.update(gsettings_to_json(gs, mappings))
        except ValueError:
            pass

    try:
        path = _build_profile_path(profile, "speech")
        gs = source.get_settings(SCHEMAS["speech"], path)
        synth_result = export_synthesizer(gs)
        if synth_result is not None:
            profile_data["speechServerInfo"] = list(synth_result)
    except ValueError:
        pass

    # Voice settings
    voices: dict[str, Any] = {}
    for voice_type in VOICE_TYPES:
        try:
            vt = sanitize_gsettings_path(voice_type)
            path = _build_profile_path(profile, f"voices/{vt}")
            gs = source.get_settings(SCHEMAS["voice"], path)
            voice_data = export_voice(gs)
            if voice_data:
                voices[voice_type] = voice_data
        except ValueError:
            pass
    if voices:
        profile_data["voices"] = voices

    # Pronunciations
    try:
        path = _build_profile_path(profile, "pronunciations")
        gs = source.get_settings(SCHEMAS["pronunciations"], path)
        pronunciations = export_pronunciations(gs)
        if pronunciations:
            profile_data["pronunciations"] = pronunciations
    except ValueError:
        pass

    # Keybindings
    try:
        path = _build_profile_path(profile, "keybindings")
        gs = source.get_settings(SCHEMAS["keybindings"], path)
        kb = export_keybindings(gs)
        if kb:
            profile_data["keybindings"] = kb
    except ValueError:
        pass

    add_legacy_aliases(profile_data)
    return profile_data


def _dconf_list(path: str) -> list[str]:
    """List dconf entries under a path. Returns empty list on failure."""
    try:
        output = subprocess.check_output(["dconf", "list", path], text=True)
        return [e.strip("/") for e in output.strip().split("\n") if e.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def _export_apps(
    source: SchemaSource,
    profile_name: str,
    output_dir: str,
    original_profile_name: str = "",
) -> None:
    """Export app-specific settings for a profile."""
    profile = sanitize_gsettings_path(profile_name)
    original_profile_name = original_profile_name or profile_name
    apps_prefix = f"{GSETTINGS_PATH_PREFIX}{profile}/apps/"
    app_entries = _dconf_list(apps_prefix)
    if not app_entries:
        return

    app_settings_dir = os.path.join(output_dir, "app-settings")
    os.makedirs(app_settings_dir, exist_ok=True)

    for sanitized_app in app_entries:
        metadata_path = _build_app_path(sanitized_app, profile, "metadata")
        app_display_name, _ = _read_metadata(source, metadata_path)
        original_app_name = app_display_name or sanitized_app

        app_data: dict[str, Any] = {}

        for schema_name, mappings in ALL_MAPPINGS.items():
            try:
                path = _build_app_path(sanitized_app, profile, schema_name)
                gs = source.get_settings(SCHEMAS[schema_name], path)
                app_data.update(gsettings_to_json(gs, mappings))
            except ValueError:
                pass

        try:
            path = _build_app_path(sanitized_app, profile, "speech")
            gs = source.get_settings(SCHEMAS["speech"], path)
            synth_result = export_synthesizer(gs)
            if synth_result is not None:
                app_data["speechServerInfo"] = list(synth_result)
        except ValueError:
            pass

        voices: dict[str, Any] = {}
        for voice_type in VOICE_TYPES:
            try:
                vt = sanitize_gsettings_path(voice_type)
                path = _build_app_path(sanitized_app, profile, f"voices/{vt}")
                gs = source.get_settings(SCHEMAS["voice"], path)
                voice_data = export_voice(gs)
                if voice_data:
                    voices[voice_type] = voice_data
            except ValueError:
                pass
        if voices:
            app_data["voices"] = voices

        app_pronunciations: dict[str, list[str]] = {}
        try:
            path = _build_app_path(sanitized_app, profile, "pronunciations")
            gs = source.get_settings(SCHEMAS["pronunciations"], path)
            app_pronunciations = export_pronunciations(gs)
        except ValueError:
            pass

        app_kb: dict = {}
        try:
            path = _build_app_path(sanitized_app, profile, "keybindings")
            gs = source.get_settings(SCHEMAS["keybindings"], path)
            app_kb = export_keybindings(gs)
        except ValueError:
            pass

        if not app_data and not app_pronunciations and not app_kb:
            continue

        filepath = os.path.join(app_settings_dir, f"{original_app_name}.conf")
        if os.path.isfile(filepath):
            with open(filepath, encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = {"profiles": {}}
        add_legacy_aliases(app_data)
        profile_entry: dict[str, Any] = {"general": app_data}
        if app_pronunciations:
            profile_entry["pronunciations"] = app_pronunciations
        if app_kb:
            profile_entry["keybindings"] = app_kb
        existing.setdefault("profiles", {})[original_profile_name] = profile_entry
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4)
        print(f"  Exported app:{original_app_name}/profile:{profile_name}")


def _read_metadata(source: SchemaSource, path: str) -> tuple[str, str]:
    """Read display-name and internal-name from metadata. Returns ("", "") if not set."""
    display_name = ""
    internal_name = ""
    try:
        gs = source.get_settings(SCHEMAS["metadata"], path)
        user_value = gs.get_user_value("display-name")
        if user_value is not None:
            display_name = user_value.get_string()
        user_value = gs.get_user_value("internal-name")
        if user_value is not None:
            internal_name = user_value.get_string()
    except ValueError:
        pass
    return display_name, internal_name


def export_settings(source: SchemaSource, output_dir: str) -> None:
    """Export GSettings/dconf settings to JSON format."""
    entries = _dconf_list(GSETTINGS_PATH_PREFIX)
    if not entries:
        print("No Orca settings found in dconf.", file=sys.stderr)
        return

    result: dict[str, Any] = {"profiles": {}}
    profile_name_map: dict[str, str] = {}

    for sanitized_name in entries:
        metadata_path = _build_profile_path(sanitized_name, "metadata")
        display_name, internal_name = _read_metadata(source, metadata_path)
        profile_key = internal_name or sanitized_name
        profile_name_map[sanitized_name] = profile_key

        profile_data = _export_profile(source, sanitized_name)
        if profile_data:
            profile_label = display_name or profile_key.replace("-", " ").title()
            profile_data["profile"] = [profile_label, profile_key]
            result["profiles"][profile_key] = profile_data
            print(f"  Exported profile:{profile_key}")

    output_file = os.path.join(output_dir, "user-settings.conf")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    print(f"Wrote {output_file}")

    for sanitized_name in entries:
        original_name = profile_name_map.get(sanitized_name, sanitized_name)
        _export_apps(source, sanitized_name, output_dir, original_name)


_LEGACY_ROOT_KEYS = {"general", "keybindings", "pronunciations"}

_KNOWN_UNMIGRATED_KEYS: set[str] = set()

_LEGACY_CONSTANT_KEYS: set[str] = set()

_LEGACY_ALIAS_KEYS = {"progressBarVerbosity", "progressBarUpdateInterval"}


def _build_default_info() -> dict[str, tuple[Any, dict[int, str] | None]]:
    """Build a map of migration_key → (default_value, enum_map) from all known mappings."""
    defaults: dict[str, tuple[Any, dict[int, str] | None]] = {}
    for mappings in ALL_MAPPINGS.values():
        for m in mappings:
            defaults[m.migration_key] = (m.default, m.enum_map)
    return defaults


_DEFAULT_INFO: dict[str, tuple[Any, dict[int, str] | None]] = {}


def _get_default_info() -> dict[str, tuple[Any, dict[int, str] | None]]:
    """Lazily build and cache the defaults map."""
    if not _DEFAULT_INFO:
        _DEFAULT_INFO.update(_build_default_info())
    return _DEFAULT_INFO


def _diff_dicts(
    original: Any,
    exported: Any,
    path: str = "",
    diffs: list[tuple[str, str, Any]] | None = None,
) -> list[tuple[str, str, Any]]:
    """Recursively compare two dicts/values. Returns list of (kind, path, original_value)."""
    if diffs is None:
        diffs = []
    if isinstance(original, dict) and isinstance(exported, dict):
        all_keys = sorted(set(original) | set(exported))
        for key in all_keys:
            child_path = f"{path}.{key}" if path else key
            if key not in exported:
                diffs.append(("removed", child_path, original[key]))
            elif key not in original:
                diffs.append(("added", child_path, exported[key]))
            else:
                _diff_dicts(original[key], exported[key], child_path, diffs)
    elif original != exported:
        diffs.append(("changed", path, (original, exported)))
    return diffs


def _is_default_voice_entry(value: Any) -> bool:
    """Return True if value is a voice dict containing only default values."""
    if not isinstance(value, dict):
        return False
    for key, val in value.items():
        if key == "established" and val is False:
            continue
        return False
    return True


_VOICE_FAMILY_FIELD_NAMES = frozenset(VOICE_FAMILY_FIELDS.keys())


def _classify_diff(kind: str, path: str, value: Any) -> str:
    """Classify a diff item into a known category, or return empty string for unexpected."""
    parts = path.split(".")
    if parts[0] in _LEGACY_ROOT_KEYS:
        return "legacy_root"
    if parts[-1] in _KNOWN_UNMIGRATED_KEYS:
        return "unmigrated"
    if parts[-1] in _LEGACY_CONSTANT_KEYS:
        return "legacy_constant"
    if parts[-1] in _LEGACY_ALIAS_KEYS:
        return "legacy_alias"
    if parts[-1] in REVERSE_LEGACY_KEY_ALIASES:
        return "legacy_alias"
    if (
        kind == "removed"
        and ".voices." in path
        and parts[-1] in _VOICE_FAMILY_FIELD_NAMES
        and (value is None or value == "")
    ):
        return "null_voice_field"
    if kind == "removed" and ".voices." in path and _is_default_voice_entry(value):
        return "default_voice"
    if kind == "removed":
        leaf = parts[-1]
        if leaf in ("pronunciations", "keybindings") and isinstance(value, dict) and not value:
            return "empty_dict"
        info = _get_default_info()
        if leaf in info:
            default, enum_map = info[leaf]
            if _values_match_default(value, default, enum_map):
                return "default_value"
        if leaf in KEYBINDINGS_METADATA_KEYS and _is_hoisted_keybinding_metadata(parts):
            return "legacy_alias"
        if _is_empty_synthesizer(leaf, value):
            return "default_value"
    return ""


def _is_hoisted_keybinding_metadata(parts: list[str]) -> bool:
    """Return True if this is a keyboardLayout/orcaModifierKeys inside a keybindings dict."""
    return len(parts) >= 3 and parts[-2] == "keybindings"


def _is_empty_synthesizer(key: str, value: Any) -> bool:
    """Return True if this is an empty speechServerInfo."""
    return key == "speechServerInfo" and isinstance(value, list) and all(v == "" for v in value)


def _values_match_default(value: Any, default: Any, enum_map: dict[int, str] | None = None) -> bool:
    """Check if a JSON value matches a schema default, handling type coercion and enums."""
    if value == default:
        return True
    if enum_map is not None:
        nick = resolve_enum_nick(value, enum_map)
        return nick == default
    if isinstance(default, bool):
        return bool(value) == default
    if isinstance(default, int):
        try:
            return int(value) == default
        except (TypeError, ValueError):
            return False
    return False


def _diff_json_files(
    original_path: str, exported_path: str, label: str, verbose: bool = False
) -> None:
    """Load two JSON files and print a categorized diff (ignoring key order)."""
    with open(original_path, encoding="utf-8") as f:
        original = json.load(f)
    with open(exported_path, encoding="utf-8") as f:
        exported = json.load(f)
    diffs = _diff_dicts(original, exported)
    if not diffs:
        if verbose:
            print(f"* {label}: (no differences)")
        return

    category_labels = {
        "legacy_root": "Legacy root-level keys (not part of profiles)",
        "unmigrated": "Settings not yet migrated to GSettings",
        "legacy_constant": "Legacy constants (data migrated under a different key)",
        "legacy_alias": "Legacy key aliases at default value",
        "null_voice_field": "Null/empty voice family fields (no GSettings representation)",
        "default_voice": "Voice entries with only default values",
        "default_value": "Settings at their schema default (normalized away)",
        "empty_dict": "Empty dicts",
    }

    categories: dict[str, list[tuple[str, str, Any]]] = {}
    unexpected: list[tuple[str, str, Any]] = []
    for kind, path, value in diffs:
        cat = _classify_diff(kind, path, value)
        if cat:
            categories.setdefault(cat, []).append((kind, path, value))
        else:
            unexpected.append((kind, path, value))

    if not unexpected and not verbose:
        return

    print(f"* {label}")

    if verbose and categories:
        print("  Expected/known losses:")
        for cat, items in categories.items():
            desc = category_labels.get(cat, cat)
            print(f"    {desc} ({len(items)}):")
            for kind, path, value in items:
                if kind == "changed":
                    orig, exp = value
                    print(
                        f"      {path}: {_truncate(json.dumps(orig, default=str))} → "
                        f"{_truncate(json.dumps(exp, default=str))}"
                    )
                elif cat == "default_value":
                    print(f"      {path}: {_format_diff_value(path, value)}")
                else:
                    print(f"      {path}: {_truncate(json.dumps(value, default=str))}")

    if unexpected:
        not_in_dconf = [(p, v) for k, p, v in unexpected if k == "removed"]
        not_in_json = [(p, v) for k, p, v in unexpected if k == "added"]
        differs = [(p, v) for k, p, v in unexpected if k == "changed"]
        if not_in_dconf:
            print(f"  Not in dconf ({len(not_in_dconf)}):")
            for path, val in not_in_dconf:
                print(f"    {path}: {_truncate(json.dumps(val, default=str))}")
        if not_in_json:
            print(f"  Not in JSON ({len(not_in_json)}):")
            for path, val in not_in_json:
                print(f"    {path}: {_truncate(json.dumps(val, default=str))}")
        if differs:
            print(f"  Differs ({len(differs)}):")
            for path, val in differs:
                orig, exp = val
                print(
                    f"    {path}: {_truncate(json.dumps(orig, default=str))} (JSON) → "
                    f"{_truncate(json.dumps(exp, default=str))} (dconf)"
                )
    elif verbose and not categories:
        print("  (no differences)")


def _format_diff_value(path: str, value: Any) -> str:
    """Format a diff value, resolving enum nicks when possible."""
    raw = _truncate(json.dumps(value, default=str))
    leaf = path.split(".")[-1]
    info = _get_default_info()
    if leaf not in info:
        return raw
    default, enum_map = info[leaf]
    if enum_map is None:
        return raw
    nick = resolve_enum_nick(value, enum_map)
    if nick is None:
        return raw
    return f"{raw} (= {nick!r}, schema default {default!r})"


def _print_file_summary(filepath: str) -> None:
    """Print a summary of a JSON file's contents."""
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        print(f"  Contents: {json.dumps(data, indent=2)}")
    except (OSError, json.JSONDecodeError) as err:
        print(f"  (could not read: {err})")


def _truncate(text: str, max_length: int = 120) -> str:
    """Truncate a string with ellipsis if it exceeds max_length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def diff_settings(original_dir: str, exported_dir: str, verbose: bool = False) -> None:
    """Diff two settings directories (original JSON vs exported JSON)."""

    original_conf = os.path.join(original_dir, "user-settings.conf")
    exported_conf = os.path.join(exported_dir, "user-settings.conf")
    if os.path.isfile(original_conf) and os.path.isfile(exported_conf):
        _diff_json_files(original_conf, exported_conf, "user-settings.conf", verbose)

    original_app_dir = os.path.join(original_dir, "app-settings")
    exported_app_dir = os.path.join(exported_dir, "app-settings")
    if os.path.isdir(original_app_dir):
        original_apps = {f for f in os.listdir(original_app_dir) if f.endswith(".conf")}
        exported_apps = set()
        if os.path.isdir(exported_app_dir):
            exported_apps = {f for f in os.listdir(exported_app_dir) if f.endswith(".conf")}

        for app in sorted(original_apps | exported_apps):
            orig = os.path.join(original_app_dir, app)
            exp = os.path.join(exported_app_dir, app)
            if not os.path.isfile(orig):
                print(f"* app-settings/{app}: only in dconf")
                _print_file_summary(exp)
            elif not os.path.isfile(exp):
                print(f"* app-settings/{app}: only in JSON")
                _print_file_summary(orig)
            else:
                _diff_json_files(orig, exp, f"app-settings/{app}", verbose)


def roundtrip(settings_dir: str, output_dir: str, verbose: bool = False) -> None:
    """Import JSON → dconf, export dconf → JSON, diff original vs exported."""

    source = SchemaSource()
    subprocess.run(["dconf", "reset", "-f", "/org/gnome/orca/"], check=True)
    with redirect_stdout(io.StringIO()):
        import_settings(settings_dir, source)
        Gio.Settings.sync()  # pylint: disable=no-value-for-parameter

        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        export_settings(source, output_dir)

    diff_settings(settings_dir, output_dir, verbose)


def main() -> None:
    """CLI entry point for import, export, roundtrip, and diff commands."""
    parser = argparse.ArgumentParser(description="Orca GSettings tool: import/export settings")
    parser.add_argument(
        "--prefix",
        help="Orca install prefix (e.g. /usr/local). Adds <prefix>/share to XDG_DATA_DIRS.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    imp = subparsers.add_parser("import", help="Import JSON settings into GSettings/dconf")
    imp.add_argument(
        "settings_dir",
        help="Directory containing user-settings.conf (and optionally app-settings/)",
    )
    imp.add_argument(
        "--dry-run", action="store_true", help="Show what would be written without changes"
    )

    exp = subparsers.add_parser("export", help="Export GSettings/dconf settings to JSON")
    exp.add_argument("output_dir", help="Directory to write exported settings")

    rt = subparsers.add_parser("roundtrip", help="Import JSON → dconf → export JSON, then diff")
    rt.add_argument(
        "settings_dir",
        help="Directory containing user-settings.conf (e.g. ~/.local/share/orca)",
    )
    rt.add_argument("output_dir", help="Directory for exported JSON (e.g. /tmp/orca-roundtrip)")
    rt.add_argument("-v", "--verbose", action="store_true", help="Show expected/known losses too")

    di = subparsers.add_parser("diff", help="Export dconf → JSON, then diff against original JSON")
    di.add_argument(
        "settings_dir",
        help="Directory containing original user-settings.conf (e.g. ~/.local/share/orca)",
    )
    di.add_argument("output_dir", help="Directory for exported JSON (e.g. /tmp/orca-diff)")
    di.add_argument("-v", "--verbose", action="store_true", help="Show expected/known losses too")

    args = parser.parse_args()

    if args.prefix:
        share_dir = os.path.join(args.prefix, "share")
        if os.path.isdir(share_dir):
            xdg = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share")
            if share_dir not in xdg.split(":"):
                os.environ["XDG_DATA_DIRS"] = f"{share_dir}:{xdg}"

    if args.command == "import":
        source = SchemaSource()
        print(f"Importing from {args.settings_dir}...")
        import_settings(args.settings_dir, source, dry_run=args.dry_run)
        if args.dry_run:
            print("(dry run - no changes made)")
        else:
            Gio.Settings.sync()  # pylint: disable=no-value-for-parameter
            print("Import complete.")

    elif args.command == "export":
        source = SchemaSource()
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"Exporting to {args.output_dir}...")
        export_settings(source, args.output_dir)

    elif args.command == "roundtrip":
        roundtrip(args.settings_dir, args.output_dir, args.verbose)

    elif args.command == "diff":
        source = SchemaSource()
        if os.path.isdir(args.output_dir):
            shutil.rmtree(args.output_dir)
        os.makedirs(args.output_dir, exist_ok=True)
        if args.verbose:
            print(f"Exporting current dconf to {args.output_dir}...")
            export_settings(source, args.output_dir)
        else:
            with redirect_stdout(io.StringIO()):
                export_settings(source, args.output_dir)
        diff_settings(args.settings_dir, args.output_dir, args.verbose)


if __name__ == "__main__":
    main()
