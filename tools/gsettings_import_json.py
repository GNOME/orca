#!/usr/bin/python
# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
# pylint: disable=too-many-branches,too-many-statements
# gsettings_import_json.py
#
# Standalone tool for importing Orca JSON settings into GSettings/dconf.
#
# Examples (run from the repo root):
#
# Import your JSON settings into dconf. First preview what will be written:
#
#      python tools/gsettings_import_json.py import --dry-run $HOME/.local/share/orca
#
#    If the output looks correct, run the import for real. WARNING: This overwrites
#    any existing Orca settings in your dconf database. To clear imported settings
#    afterwards use "dconf reset -f /org/gnome/orca/" but note that this will not
#    restore whatever was there before the import.
#
#      python tools/gsettings_import_json.py import $HOME/.local/share/orca
#
#    View the result:
#
#      dconf dump /org/gnome/orca/
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

"""Standalone tool for importing Orca JSON settings into GSettings/dconf."""

import argparse
import json
import os
import sys
from pathlib import Path

from gi.repository import Gio

from generate_gsettings_schemas import _discover_schemas

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from orca.gsettings_migrator import (
    KEYBINDINGS_METADATA_KEYS,
    VOICE_FAMILY_FIELDS,
    VOICE_MIGRATION_MAP,
    VOICE_TYPES,
    SettingsMapping,
    apply_legacy_aliases,
    fix_bool_enum_values,
    force_navigation_enabled,
    hoist_keybindings_metadata,
    import_keybindings,
    import_pronunciations,
    import_synthesizer,
    import_voice,
    json_to_gsettings,
    populate_per_layout_modifier_keys,
    resolve_enum_nick,
    sanitize_gsettings_path,
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
                "\n\n  python tools/gsettings_import_json.py --prefix=/my/prefix ..."
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
                bindings = [
                    [str(v) for v in binding] for binding in value if isinstance(binding, list)
                ]
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


def _import_per_layout_modifier_keys(
    source: SchemaSource,
    profile_prefs: dict,
    profile: str,
    label: str,
    dry_run: bool,
    skip_defaults: bool = True,
    app_name: str = "",
) -> None:
    """Import keyboard-layout and per-layout modifier keys from keybinding metadata."""
    if dry_run:
        layout = profile_prefs.get("keyboardLayout", 1)
        nick = "desktop" if layout == 1 else "laptop"
        modifier_keys = profile_prefs.get("orcaModifierKeys")
        if not skip_defaults or nick != "desktop":
            path = (
                _build_app_path(app_name, profile, "keybindings")
                if app_name
                else _build_profile_path(profile, "keybindings")
            )
            print(f"  {path}keyboard-layout = {nick!r}")
        if modifier_keys is not None:
            key = "desktop-modifier-keys" if layout == 1 else "laptop-modifier-keys"
            path = (
                _build_app_path(app_name, profile, "keybindings")
                if app_name
                else _build_profile_path(profile, "keybindings")
            )
            print(f"  {path}{key} = {modifier_keys!r}")
        return

    if app_name:
        path = _build_app_path(app_name, profile, "keybindings")
    else:
        path = _build_profile_path(profile, "keybindings")
    gs = source.get_settings(SCHEMAS["keybindings"], path)
    if populate_per_layout_modifier_keys(gs, profile_prefs, skip_defaults):
        print(f"  Imported per-layout modifier keys for {label}")


def _import_profile(
    source: SchemaSource,
    profile_name: str,
    profile_prefs: dict,
    dry_run: bool,
) -> None:
    """Import all settings for a single profile."""
    apply_legacy_aliases(profile_prefs)
    force_navigation_enabled(profile_prefs)
    fix_bool_enum_values(profile_prefs)
    hoist_keybindings_metadata(profile_prefs)
    profile = sanitize_gsettings_path(profile_name)
    skip_defaults = profile_name == "default"

    for schema_name in ALL_MAPPINGS:
        path = _build_profile_path(profile, schema_name)
        _import_mapped_settings(
            source,
            schema_name,
            path,
            profile_prefs,
            f"profile:{profile_name}",
            dry_run,
            skip_defaults=skip_defaults,
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
            skip_defaults=skip_defaults,
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

    _import_per_layout_modifier_keys(
        source, profile_prefs, profile, f"profile:{profile_name}", dry_run, skip_defaults
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
        force_navigation_enabled(general)
        fix_bool_enum_values(general)
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
            _import_voice_for_path(
                source,
                voice_data,
                path,
                f"voice:{voice_type}/{label}",
                dry_run,
                skip_defaults=False,
            )

        if pronunciations:
            path = _build_app_path(app_name, profile_name, "pronunciations")
            _import_pronunciations_for_path(source, pronunciations, path, label, dry_run)

        if app_keybindings:
            path = _build_app_path(app_name, profile_name, "keybindings")
            _import_keybindings_for_path(source, app_keybindings, path, label, dry_run)

        _import_per_layout_modifier_keys(
            source,
            general,
            sanitize_gsettings_path(profile_name),
            label,
            dry_run,
            skip_defaults=False,
            app_name=app_name,
        )

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


def _get_dict_entries(source: SchemaSource, schema_name: str, profile: str, app_name: str) -> dict:
    """Read dict entries (keybindings or pronunciations) from a single dconf layer."""

    if app_name:
        path = _build_app_path(app_name, profile, schema_name)
    else:
        path = _build_profile_path(profile, schema_name)
    gs = source.get_settings(SCHEMAS[schema_name], path)
    user_value = gs.get_user_value("entries")
    if user_value is None:
        return {}
    return user_value.unpack()


def _strip_inherited_dict_entries(
    source: SchemaSource,
    settings_dir: str,
    profile_names: list[str],
) -> None:
    """After import, strip dict entries that duplicate their parent layer."""

    for schema_name in ("keybindings", "pronunciations"):
        if schema_name not in SCHEMAS:
            continue

        default_entries = _get_dict_entries(source, schema_name, "default", "")

        for profile_name in profile_names:
            if profile_name == "default":
                continue
            profile = sanitize_gsettings_path(profile_name)
            entries = _get_dict_entries(source, schema_name, profile, "")
            if not entries:
                continue
            diff = {k: v for k, v in entries.items() if default_entries.get(k) != v}
            if len(diff) == len(entries):
                continue
            path = _build_profile_path(profile, schema_name)
            gs = source.get_settings(SCHEMAS[schema_name], path)
            if not diff:
                gs.reset("entries")
            elif schema_name == "keybindings":
                import_keybindings(gs, diff)
            else:
                import_pronunciations(gs, diff)
            print(f"  Stripped {schema_name} for {profile_name}: {len(entries)} -> {len(diff)}")

        app_dir = os.path.join(settings_dir, "app-settings")
        if not os.path.isdir(app_dir):
            continue
        for filename in sorted(os.listdir(app_dir)):
            if not filename.endswith(".conf"):
                continue
            app_name = filename[:-5]
            try:
                with open(os.path.join(app_dir, filename), encoding="utf-8") as f:
                    app_prefs = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            for profile_name in app_prefs.get("profiles", {}):
                profile = sanitize_gsettings_path(profile_name)
                parent = dict(default_entries)
                if profile_name != "default":
                    parent |= _get_dict_entries(source, schema_name, profile, "")
                entries = _get_dict_entries(source, schema_name, profile, app_name)
                if not entries:
                    continue
                diff = {k: v for k, v in entries.items() if parent.get(k) != v}
                if len(diff) == len(entries):
                    continue
                path = _build_app_path(app_name, profile, schema_name)
                gs = source.get_settings(SCHEMAS[schema_name], path)
                if not diff:
                    gs.reset("entries")
                elif schema_name == "keybindings":
                    import_keybindings(gs, diff)
                else:
                    import_pronunciations(gs, diff)
                target = f"{profile_name}/{app_name}"
                print(f"  Stripped {schema_name} for {target}: {len(entries)} -> {len(diff)}")


def import_settings(settings_dir: str, source: SchemaSource, dry_run: bool = False) -> None:
    """Import JSON settings into GSettings/dconf additively (overlay, no dconf reset first)."""
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

    if not dry_run:
        _strip_inherited_dict_entries(source, settings_dir, list(profiles.keys()))


def main() -> None:
    """CLI entry point for importing Orca JSON settings into GSettings/dconf."""
    parser = argparse.ArgumentParser(description="Orca GSettings tool: import JSON settings")
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


if __name__ == "__main__":
    main()
