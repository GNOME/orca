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

"""Shared migration logic for converting between JSON settings and GSettings.

This module has no imports of debug, settings_manager, or anything that pulls
in Atspi, so it can be used by both the orca runtime and the standalone
gsettings_import_export tool.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from gi.repository import Gio, GLib

VOICE_TYPES: list[str] = ["default", "uppercase", "hyperlink", "system"]

# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
VOICE_MIGRATION_MAP: dict[str, tuple[str, str, Any]] = {
    "established": ("established", "b", False),
    "rate": ("rate", "i", 50),
    "average-pitch": ("pitch", "d", 5.0),
    "gain": ("volume", "d", 10.0),
}

# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
VOICE_FAMILY_FIELDS: dict[str, str] = {
    "name": "family-name",
    "lang": "family-lang",
    "dialect": "family-dialect",
    "gender": "family-gender",
    "variant": "family-variant",
}

# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
LEGACY_KEY_ALIASES: dict[str, str] = {
    "progressBarVerbosity": "progressBarSpeechVerbosity",
    "progressBarUpdateInterval": "progressBarSpeechInterval",
}

# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
REVERSE_LEGACY_KEY_ALIASES: dict[str, str] = {v: k for k, v in LEGACY_KEY_ALIASES.items()}

# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
KEYBINDINGS_METADATA_KEYS: frozenset[str] = frozenset({"keyboardLayout", "orcaModifierKeys"})


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
@dataclass
class SettingsMapping:
    """Describes a mapping between a preferences key and a GSettings key."""

    migration_key: str
    gs_key: str
    gtype: str  # "b", "s", "i", "d", "as"
    default: Any
    enum_map: dict[int, str] | None = None
    string_enum: bool = False


def sanitize_gsettings_path(name: str) -> str:
    """Sanitize a name for use in a GSettings path."""

    sanitized = name.lower()
    sanitized = re.sub(r"[^a-z0-9-]", "-", sanitized)
    sanitized = re.sub(r"-+", "-", sanitized)
    return sanitized.strip("-")


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def resolve_enum_nick(value: Any, enum_map: dict[int, str]) -> str | None:
    """Resolve a JSON enum value (string nick, int, or bool) to a GSettings enum nick."""

    if isinstance(value, str):
        return value if value in enum_map.values() else None
    return enum_map.get(value)


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
_NAVIGATION_ENABLED_KEYS = (
    "caretNavigationEnabled",
    "structuralNavigationEnabled",
    "tableNavigationEnabled",
)


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def force_navigation_enabled(json_dict: dict) -> None:
    """Force navigation-enabled keys to True during migration."""

    # In the old system these defaulted to False because per-script logic controlled
    # activation. In the new system they represent the user's preference and default
    # to True. Migrating the old False would disable navigation for all scripts.
    for key in _NAVIGATION_ENABLED_KEYS:
        if key in json_dict:
            json_dict[key] = True


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def apply_legacy_aliases(json_dict: dict) -> None:
    """Copy legacy key names to their modern equivalents if modern key is absent."""

    for legacy_key, modern_key in LEGACY_KEY_ALIASES.items():
        if legacy_key in json_dict and modern_key not in json_dict:
            json_dict[modern_key] = json_dict[legacy_key]


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def add_legacy_aliases(result: dict) -> None:
    """Add legacy key names to exported dict for backwards compatibility with stable."""

    for modern_key, legacy_key in REVERSE_LEGACY_KEY_ALIASES.items():
        if modern_key in result:
            result[legacy_key] = result[modern_key]


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def hoist_keybindings_metadata(profile_prefs: dict) -> None:
    """Move keyboardLayout and orcaModifierKeys from keybindings to profile level."""

    keybindings = profile_prefs.get("keybindings", {})
    for key in KEYBINDINGS_METADATA_KEYS:
        if key in keybindings and key not in profile_prefs:
            profile_prefs[key] = keybindings[key]


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def sink_keybindings_metadata(profile_data: dict, keybindings: dict) -> None:
    """Move keyboardLayout and orcaModifierKeys from profile level into keybindings."""

    for key in KEYBINDINGS_METADATA_KEYS:
        if key in profile_data:
            keybindings[key] = profile_data.pop(key)


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def _write_one_mapping(
    gs: Gio.Settings,
    m: SettingsMapping,
    value: Any,
    skip_defaults: bool,
) -> bool:
    """Write a single mapping value to GSettings. Returns True if written."""

    if m.enum_map is not None:
        nick = resolve_enum_nick(value, m.enum_map)
        if nick is None:
            return False
        if skip_defaults and m.default in (nick, value):
            return False
        gs.set_string(m.gs_key, nick)
        return True

    if skip_defaults and value == m.default:
        return False
    if m.gtype == "b":
        gs.set_boolean(m.gs_key, value)
    elif m.gtype == "s":
        gs.set_string(m.gs_key, value)
    elif m.gtype == "i":
        gs.set_int(m.gs_key, int(value))
    elif m.gtype == "d":
        gs.set_double(m.gs_key, float(value))
    elif m.gtype == "as":
        gs.set_strv(m.gs_key, value)
    else:
        return False
    return True


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def json_to_gsettings(
    json_dict: dict,
    gs: Gio.Settings,
    mappings: list[SettingsMapping],
    skip_defaults: bool = True,
) -> bool:
    """Writes JSON settings to a Gio.Settings object. Returns True if any value was written."""

    wrote_any = False
    for m in mappings:
        if m.migration_key not in json_dict:
            continue
        if _write_one_mapping(gs, m, json_dict[m.migration_key], skip_defaults):
            wrote_any = True
    return wrote_any


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def gsettings_to_json(gs: Gio.Settings, mappings: list[SettingsMapping]) -> dict:
    """Reads explicitly-set GSettings values into a JSON-compatible dict."""

    result: dict[str, Any] = {}
    for m in mappings:
        user_value = gs.get_user_value(m.gs_key)
        if user_value is None:
            continue
        if m.enum_map is not None:
            gs_str = user_value.get_string()
            if m.string_enum:
                result[m.migration_key] = gs_str
            else:
                reverse_map = {v: k for k, v in m.enum_map.items()}
                json_value = reverse_map.get(gs_str)
                if json_value is not None:
                    result[m.migration_key] = json_value
        elif m.gtype == "b":
            result[m.migration_key] = user_value.get_boolean()
        elif m.gtype == "s":
            result[m.migration_key] = user_value.get_string()
        elif m.gtype == "i":
            result[m.migration_key] = user_value.get_int32()
        elif m.gtype == "d":
            result[m.migration_key] = user_value.get_double()
        elif m.gtype == "as":
            result[m.migration_key] = list(user_value.unpack())
    return result


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def import_voice(gs: Gio.Settings, voice_data: dict, skip_defaults: bool = True) -> bool:
    """Import ACSS voice data to a Gio.Settings object. Returns True if any value was written."""

    migrated = False
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
        if gs_type == "b":
            gs.set_boolean(gs_key, bool(value))
        elif gs_type == "i":
            gs.set_int(gs_key, int(value))
        elif gs_type == "d":
            gs.set_double(gs_key, float(value))
        migrated = True

    family = voice_data.get("family", {})
    if isinstance(family, dict):
        for json_field, gs_key in VOICE_FAMILY_FIELDS.items():
            val = family.get(json_field)
            if val is not None and str(val):
                gs.set_string(gs_key, str(val))
                migrated = True

    return migrated


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def export_voice(gs: Gio.Settings) -> dict:
    """Export voice settings from a Gio.Settings to ACSS format."""

    voice_data: dict[str, Any] = {}
    for acss_key, (gs_key, gs_type, _default) in VOICE_MIGRATION_MAP.items():
        user_value = gs.get_user_value(gs_key)
        if user_value is None:
            continue
        if gs_type == "b":
            voice_data[acss_key] = user_value.get_boolean()
        elif gs_type == "i":
            voice_data[acss_key] = user_value.get_int32()
        elif gs_type == "d":
            voice_data[acss_key] = user_value.get_double()

    family_dict: dict[str, str] = {}
    for json_field, gs_key in VOICE_FAMILY_FIELDS.items():
        user_value = gs.get_user_value(gs_key)
        if user_value is not None:
            val = user_value.get_string()
            if val:
                family_dict[json_field] = val
    if family_dict:
        voice_data["family"] = family_dict

    return voice_data


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def import_synthesizer(gs: Gio.Settings, profile_prefs: dict) -> bool:
    """Import speechServerInfo to GSettings. Returns True if written."""

    speech_server_info = profile_prefs.get("speechServerInfo")
    if speech_server_info is None or len(speech_server_info) < 2:
        return False
    server_name = speech_server_info[0]
    synthesizer = speech_server_info[1]
    if server_name is None and synthesizer is None:
        return False
    gs.set_string("speech-server", server_name or "")
    gs.set_string("synthesizer", synthesizer or "")
    return True


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def export_synthesizer(gs: Gio.Settings) -> tuple[str, str] | None:
    """Export synthesizer from GSettings. Returns (display_name, module_id) or None."""

    synth_value = gs.get_user_value("synthesizer")
    if synth_value is None:
        return None
    synth = synth_value.get_string()
    server_value = gs.get_user_value("speech-server")
    server_name = server_value.get_string() if server_value is not None else ""
    if synth:
        return (server_name, synth)
    return ("", "")


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def import_pronunciations(gs: Gio.Settings, pronunciations_dict: dict) -> bool:
    """Import pronunciation dictionary to GSettings. Returns True if written.

    JSON format: {word: [word, replacement]} or {word: replacement}
    GSettings format: a{ss} {word: replacement}
    """

    converted: dict[str, str] = {}
    for key, value in pronunciations_dict.items():
        if isinstance(value, list) and len(value) >= 2:
            converted[key] = value[1]
        elif isinstance(value, list) and len(value) == 1:
            converted[key] = value[0]
        elif isinstance(value, str):
            converted[key] = value
    if not converted:
        return False

    gs.set_value("entries", GLib.Variant("a{ss}", converted))
    return True


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def export_pronunciations(gs: Gio.Settings) -> dict:
    """Export pronunciation dictionary from GSettings to JSON format.

    GSettings format: a{ss} {word: replacement}
    JSON format: {word: [word, replacement]}
    """

    user_value = gs.get_user_value("entries")
    if user_value is None:
        return {}
    entries = user_value.unpack()
    result: dict[str, list[str]] = {}
    for word, replacement in entries.items():
        result[word] = [word, replacement]
    return result


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def import_keybindings(gs: Gio.Settings, keybindings_dict: dict) -> bool:
    """Import keybinding overrides to GSettings. Returns True if written.

    JSON format: {command_name: [[keysym, mask, mods, clicks], ...]}
    GSettings format: a{saas} (same structure, all strings)
    """

    converted: dict[str, list[list[str]]] = {}
    for key, value in keybindings_dict.items():
        if key in KEYBINDINGS_METADATA_KEYS:
            continue
        if isinstance(value, list):
            bindings: list[list[str]] = [
                [str(v) for v in binding] for binding in value if isinstance(binding, list)
            ]
            converted[key] = bindings
    if not converted:
        return False

    gs.set_value("entries", GLib.Variant("a{saas}", converted))
    return True


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def export_keybindings(gs: Gio.Settings) -> dict:
    """Export keybinding overrides from GSettings to JSON format."""

    user_value = gs.get_user_value("entries")
    if user_value is None:
        return {}
    return user_value.unpack()


# TODO - JD: Delete this in v52 (remove -i/--import-dir support).
def stamp_version(gs: Gio.Settings, version: int = 1) -> None:
    """Stamps a version number on a Gio.Settings instance."""

    gs.set_int("version", version)
