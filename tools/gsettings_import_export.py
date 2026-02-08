#!/usr/bin/python
# gsettings_import_export.py
#
# Standalone tool for importing/exporting Orca settings between JSON and GSettings.
#
# Examples (run from the repo root):
#
# 1. Compile and view the GSettings schemas that will be generated for Orca:
#
#      python tools/gsettings_import_export.py compile-schemas /tmp/orca-schemas
#      cat /tmp/orca-schemas/org.gnome.Orca.gschema.xml
#
# 2. Import your JSON settings into dconf. First preview what will be written:
#
#      python tools/gsettings_import_export.py import --dry-run \
#          --schema-dir /tmp/orca-schemas $HOME/.local/share/orca
#
#    If the output looks correct, run the import for real. WARNING: This overwrites
#    any existing Orca settings in your dconf database. To clear imported settings
#    afterwards use "dconf reset -f /org/gnome/orca/" but note that this will not
#    restore whatever was there before the import.
#
#      python tools/gsettings_import_export.py import \
#          --schema-dir /tmp/orca-schemas $HOME/.local/share/orca
#
#    View the result:
#
#      dconf dump /org/gnome/orca/
#
# 3. Export your dconf settings to JSON files that can be copied to another machine:
#
#      python tools/gsettings_import_export.py export \
#          --schema-dir /tmp/orca-schemas /tmp/orca-export
#
#    This creates /tmp/orca-export/user-settings.conf and, if there are app-specific
#    overrides, /tmp/orca-export/app-settings/<AppName>.conf. To use the exported
#    files on another machine, copy them to $HOME/.local/share/orca/.
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

"""Standalone tool for importing/exporting Orca settings between JSON and GSettings."""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

from gi.repository import Gio, GLib

GSETTINGS_PATH_PREFIX = "/org/gnome/orca/"

SCHEMAS = {
    "speech": "org.gnome.Orca.Speech",
    "voice": "org.gnome.Orca.Voice",
    "typing-echo": "org.gnome.Orca.TypingEcho",
    "caret-navigation": "org.gnome.Orca.CaretNavigation",
    "structural-navigation": "org.gnome.Orca.StructuralNavigation",
    "table-navigation": "org.gnome.Orca.TableNavigation",
    "document": "org.gnome.Orca.Document",
    "say-all": "org.gnome.Orca.SayAll",
    "flat-review": "org.gnome.Orca.FlatReview",
    "sound": "org.gnome.Orca.Sound",
    "chat": "org.gnome.Orca.Chat",
    "spellcheck": "org.gnome.Orca.Spellcheck",
    "mouse-review": "org.gnome.Orca.MouseReview",
    "live-regions": "org.gnome.Orca.LiveRegions",
    "system-information": "org.gnome.Orca.SystemInformation",
    "pronunciations": "org.gnome.Orca.Pronunciations",
    "keybindings": "org.gnome.Orca.Keybindings",
    "text-attributes": "org.gnome.Orca.TextAttributes",
}

VOICE_TYPES = ["default", "uppercase", "hyperlink", "system"]

# ACSS key → (GSettings key, gtype, default)
VOICE_MIGRATION_MAP = {
    "rate": ("rate", "i", 50),
    "average-pitch": ("pitch", "d", 5.0),
    "gain": ("volume", "d", 10.0),
}


def sanitize_gsettings_path(name: str) -> str:
    """Sanitize a name for use in a GSettings path."""
    sanitized = name.lower()
    sanitized = re.sub(r"[^a-z0-9-]", "-", sanitized)
    sanitized = re.sub(r"-+", "-", sanitized)
    return sanitized.strip("-")


@dataclass
class SettingsMapping:
    """Describes a mapping between a JSON settings key and a GSettings key."""

    json_key: str
    gs_key: str
    gtype: str  # "b", "s", "i", "d"
    default: Any
    enum_map: dict[int, str] | None = None


SPEECH_MAPPINGS = [
    SettingsMapping("enableSpeech", "enable", "b", True),
    SettingsMapping("onlySpeakDisplayedText", "only-speak-displayed-text", "b", False),
    SettingsMapping("messagesAreDetailed", "messages-are-detailed", "b", True),
    SettingsMapping("capitalizationStyle", "capitalization-style", "s", "none"),
    SettingsMapping(
        "verbalizePunctuationStyle",
        "punctuation-level",
        "s",
        1,
        enum_map={0: "all", 1: "most", 2: "some", 3: "none"},
    ),
    SettingsMapping(
        "speechVerbosityLevel",
        "verbosity-level",
        "s",
        1,
        enum_map={0: "brief", 1: "verbose"},
    ),
]

TYPING_ECHO_MAPPINGS = [
    SettingsMapping("enableKeyEcho", "key-echo", "b", True),
    SettingsMapping("enableEchoByCharacter", "character-echo", "b", False),
    SettingsMapping("enableEchoByWord", "word-echo", "b", False),
    SettingsMapping("enableEchoBySentence", "sentence-echo", "b", False),
    SettingsMapping("enableAlphabeticKeys", "alphabetic-keys", "b", True),
    SettingsMapping("enableNumericKeys", "numeric-keys", "b", True),
    SettingsMapping("enablePunctuationKeys", "punctuation-keys", "b", True),
    SettingsMapping("enableSpace", "space", "b", True),
    SettingsMapping("enableModifierKeys", "modifier-keys", "b", True),
    SettingsMapping("enableFunctionKeys", "function-keys", "b", True),
    SettingsMapping("enableActionKeys", "action-keys", "b", True),
    SettingsMapping("enableNavigationKeys", "navigation-keys", "b", False),
    SettingsMapping("enableDiacriticalKeys", "diacritical-keys", "b", False),
]

CARET_NAVIGATION_MAPPINGS = [
    SettingsMapping("caretNavigationEnabled", "enabled", "b", True),
    SettingsMapping("caretNavTriggersFocusMode", "triggers-focus-mode", "b", False),
]

STRUCTURAL_NAVIGATION_MAPPINGS = [
    SettingsMapping("structuralNavigationEnabled", "enabled", "b", True),
    SettingsMapping("wrappedStructuralNavigation", "wraps", "b", True),
    SettingsMapping("structNavTriggersFocusMode", "triggers-focus-mode", "b", False),
    SettingsMapping("largeObjectTextLength", "large-object-text-length", "i", 75),
]

TABLE_NAVIGATION_MAPPINGS = [
    SettingsMapping("tableNavigationEnabled", "enabled", "b", True),
    SettingsMapping("skipBlankCells", "skip-blank-cells", "b", False),
]

DOCUMENT_MAPPINGS = [
    SettingsMapping("nativeNavTriggersFocusMode", "native-nav-triggers-focus-mode", "b", True),
    SettingsMapping("autoStickyFocusModeForWebApps", "auto-sticky-focus-mode", "b", True),
    SettingsMapping("layoutMode", "layout-mode", "b", True),
    SettingsMapping("sayAllOnLoad", "say-all-on-load", "b", True),
    SettingsMapping("pageSummaryOnLoad", "page-summary-on-load", "b", True),
    SettingsMapping(
        "findResultsVerbosity",
        "find-results-verbosity",
        "s",
        2,
        enum_map={0: "none", 1: "if-line-changed", 2: "all"},
    ),
    SettingsMapping("findResultsMinimumLength", "find-results-minimum-length", "i", 4),
]

SAY_ALL_MAPPINGS = [
    SettingsMapping("sayAllContextBlockquote", "announce-blockquote", "b", True),
    SettingsMapping("sayAllContextNonLandmarkForm", "announce-form", "b", True),
    SettingsMapping("sayAllContextPanel", "announce-grouping", "b", True),
    SettingsMapping("sayAllContextLandmark", "announce-landmark", "b", True),
    SettingsMapping("sayAllContextList", "announce-list", "b", True),
    SettingsMapping("sayAllContextTable", "announce-table", "b", True),
    SettingsMapping(
        "sayAllStyle",
        "style",
        "s",
        1,
        enum_map={0: "line", 1: "sentence"},
    ),
    SettingsMapping("structNavInSayAll", "structural-navigation", "b", False),
    SettingsMapping("rewindAndFastForwardInSayAll", "rewind-and-fast-forward", "b", False),
]

FLAT_REVIEW_MAPPINGS = [
    SettingsMapping("flatReviewIsRestricted", "restricted", "b", False),
]

SOUND_MAPPINGS = [
    SettingsMapping("enableSound", "enabled", "b", True),
    SettingsMapping("soundVolume", "volume", "d", 0.5),
    SettingsMapping("beepProgressBarUpdates", "beep-progress-bar-updates", "b", False),
    SettingsMapping("progressBarBeepInterval", "progress-bar-beep-interval", "i", 0),
    SettingsMapping(
        "progressBarBeepVerbosity",
        "progress-bar-beep-verbosity",
        "s",
        1,
        enum_map={0: "all", 1: "application", 2: "window"},
    ),
]

CHAT_MAPPINGS = [
    SettingsMapping(
        "chatMessageVerbosity",
        "message-verbosity",
        "s",
        0,
        enum_map={0: "all", 1: "all-if-focused", 2: "focused-channel"},
    ),
    SettingsMapping("chatSpeakRoomName", "speak-room-name", "b", False),
    SettingsMapping("chatAnnounceBuddyTyping", "announce-buddy-typing", "b", False),
    SettingsMapping("chatRoomHistories", "room-histories", "b", False),
    SettingsMapping("presentChatRoomLast", "speak-room-name-last", "b", False),
]

SPELLCHECK_MAPPINGS = [
    SettingsMapping("spellcheckSpellError", "spell-error", "b", True),
    SettingsMapping("spellcheckSpellSuggestion", "spell-suggestion", "b", True),
    SettingsMapping("spellcheckPresentContext", "present-context", "b", True),
]

MOUSE_REVIEW_MAPPINGS = [
    SettingsMapping("enableMouseReview", "enabled", "b", False),
    SettingsMapping("presentToolTips", "present-tooltips", "b", False),
]

LIVE_REGIONS_MAPPINGS = [
    SettingsMapping("enableLiveRegions", "enabled", "b", True),
    SettingsMapping("presentLiveRegionFromInactiveTab", "present-from-inactive-tab", "b", False),
]

SYSTEM_INFORMATION_MAPPINGS = [
    SettingsMapping("presentDateFormat", "date-format", "s", "%x"),
    SettingsMapping("presentTimeFormat", "time-format", "s", "%X"),
]

TEXT_ATTRIBUTES_MAPPINGS = [
    SettingsMapping("textAttributesToSpeak", "attributes-to-speak", "as", []),
    SettingsMapping("textAttributesToBraille", "attributes-to-braille", "as", []),
]

ALL_MAPPINGS = {
    "speech": SPEECH_MAPPINGS,
    "typing-echo": TYPING_ECHO_MAPPINGS,
    "caret-navigation": CARET_NAVIGATION_MAPPINGS,
    "structural-navigation": STRUCTURAL_NAVIGATION_MAPPINGS,
    "table-navigation": TABLE_NAVIGATION_MAPPINGS,
    "document": DOCUMENT_MAPPINGS,
    "say-all": SAY_ALL_MAPPINGS,
    "flat-review": FLAT_REVIEW_MAPPINGS,
    "sound": SOUND_MAPPINGS,
    "chat": CHAT_MAPPINGS,
    "spellcheck": SPELLCHECK_MAPPINGS,
    "mouse-review": MOUSE_REVIEW_MAPPINGS,
    "live-regions": LIVE_REGIONS_MAPPINGS,
    "system-information": SYSTEM_INFORMATION_MAPPINGS,
    "text-attributes": TEXT_ATTRIBUTES_MAPPINGS,
}


class SchemaSource:
    """Loads GSettings schemas and creates Gio.Settings instances."""

    def __init__(self, schema_dir: str | None = None) -> None:
        if schema_dir:
            parent = Gio.SettingsSchemaSource.get_default()  # pylint: disable=no-value-for-parameter
            self._source = Gio.SettingsSchemaSource.new_from_directory(schema_dir, parent, True)
        else:
            self._source = Gio.SettingsSchemaSource.get_default()  # pylint: disable=no-value-for-parameter
        self._cache: dict[str, Gio.Settings] = {}

    def lookup(self, schema_id: str) -> "Gio.SettingsSchema | None":
        return self._source.lookup(schema_id, True)

    def get_settings(self, schema_id: str, path: str) -> Gio.Settings:
        """Returns a Gio.Settings for the given schema and path, with caching."""
        cache_key = f"{schema_id}:{path}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        schema = self._source.lookup(schema_id, True)
        if schema is None:
            raise ValueError(f"Schema {schema_id} not found in schema source")
        gs = Gio.Settings.new_full(schema, None, path)
        self._cache[cache_key] = gs
        return gs


def json_to_gsettings(json_dict: dict, gs: Gio.Settings, mappings: list[SettingsMapping]) -> bool:
    """Writes JSON settings to a Gio.Settings object. Returns True if any value was written."""
    wrote_any = False
    for m in mappings:
        if m.json_key not in json_dict:
            continue
        value = json_dict[m.json_key]
        if m.enum_map is not None:
            if value == m.default:
                continue
            gs_value = m.enum_map.get(value)
            if gs_value is not None:
                gs.set_string(m.gs_key, gs_value)
                wrote_any = True
        elif m.gtype == "b":
            if value == m.default:
                continue
            gs.set_boolean(m.gs_key, value)
            wrote_any = True
        elif m.gtype == "s":
            if value == m.default:
                continue
            gs.set_string(m.gs_key, value)
            wrote_any = True
        elif m.gtype == "i":
            if int(value) == m.default:
                continue
            gs.set_int(m.gs_key, int(value))
            wrote_any = True
        elif m.gtype == "d":
            if float(value) == m.default:
                continue
            gs.set_double(m.gs_key, float(value))
            wrote_any = True
        elif m.gtype == "as":
            if value == m.default:
                continue
            gs.set_strv(m.gs_key, value)
            wrote_any = True
    return wrote_any


def gsettings_to_json(gs: Gio.Settings, mappings: list[SettingsMapping]) -> dict:
    """Reads explicitly-set GSettings values into a JSON-compatible dict."""
    result: dict[str, Any] = {}
    for m in mappings:
        user_value = gs.get_user_value(m.gs_key)
        if user_value is None:
            continue
        if m.enum_map is not None:
            gs_str = user_value.get_string()
            reverse_map = {v: k for k, v in m.enum_map.items()}
            json_value = reverse_map.get(gs_str)
            if json_value is not None:
                result[m.json_key] = json_value
        elif m.gtype == "b":
            result[m.json_key] = user_value.get_boolean()
        elif m.gtype == "s":
            result[m.json_key] = user_value.get_string()
        elif m.gtype == "i":
            result[m.json_key] = user_value.get_int32()
        elif m.gtype == "d":
            result[m.json_key] = user_value.get_double()
        elif m.gtype == "as":
            result[m.json_key] = list(user_value.unpack())
    return result


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
) -> None:
    """Import mapped settings (speech or typing-echo) for a given path."""
    mappings = ALL_MAPPINGS.get(schema_name, [])
    if not mappings:
        return
    schema_id = SCHEMAS[schema_name]

    if dry_run:
        for m in mappings:
            if m.json_key not in json_dict:
                continue
            value = json_dict[m.json_key]
            if m.enum_map is not None:
                if value == m.default:
                    continue
                gs_value = m.enum_map.get(value)
                if gs_value is not None:
                    print(f"  {path}{m.gs_key} = {gs_value!r}")
            elif value != m.default:
                print(f"  {path}{m.gs_key} = {value!r}")
        return

    gs = source.get_settings(schema_id, path)
    if json_to_gsettings(json_dict, gs, mappings):
        gs.set_int("version", 1)
        print(f"  Imported {schema_name} for {label}")


def _import_synthesizer(
    source: SchemaSource,
    profile_prefs: dict,
    profile: str,
    label: str,
    dry_run: bool,
) -> None:
    """Import speechServerInfo[1] as the synthesizer key."""
    speech_server_info = profile_prefs.get("speechServerInfo", [])
    if len(speech_server_info) < 2 or not speech_server_info[1]:
        return
    synthesizer = speech_server_info[1]
    path = _build_profile_path(profile, "speech")

    if dry_run:
        print(f"  {path}synthesizer = {synthesizer!r}")
        return

    gs = source.get_settings(SCHEMAS["speech"], path)
    gs.set_string("synthesizer", synthesizer)
    if gs.get_user_value("version") is None:
        gs.set_int("version", 1)
    print(f"  Imported synthesizer={synthesizer!r} for {label}")


def _import_voice(
    source: SchemaSource,
    voice_data: dict,
    path: str,
    label: str,
    dry_run: bool,
) -> None:
    """Import ACSS voice data to GSettings."""
    if dry_run:
        for acss_key, (gs_key, gs_type, default) in VOICE_MIGRATION_MAP.items():
            if acss_key not in voice_data:
                continue
            value = voice_data[acss_key]
            if gs_type == "i" and int(value) == default:
                continue
            if gs_type == "d" and float(value) == default:
                continue
            print(f"  {path}{gs_key} = {value!r}")
        family = voice_data.get("family", {})
        if isinstance(family, dict) and family.get("name"):
            print(f"  {path}family-name = {family['name']!r}")
        return

    gs = source.get_settings(SCHEMAS["voice"], path)
    migrated = False

    for acss_key, (gs_key, gs_type, default) in VOICE_MIGRATION_MAP.items():
        if acss_key not in voice_data:
            continue
        value = voice_data[acss_key]
        if gs_type == "i" and int(value) == default:
            continue
        if gs_type == "d" and float(value) == default:
            continue
        if gs_type == "i":
            gs.set_int(gs_key, int(value))
        elif gs_type == "d":
            gs.set_double(gs_key, float(value))
        migrated = True

    family = voice_data.get("family", {})
    if isinstance(family, dict):
        name = family.get("name")
        if name:
            gs.set_string("family-name", name)
            migrated = True

    if migrated:
        gs.set_int("version", 1)
        print(f"  Imported {label}")


def _import_pronunciations(
    source: SchemaSource,
    pronunciations_dict: dict,
    path: str,
    label: str,
    dry_run: bool,
) -> None:
    """Import pronunciation dictionary to GSettings.

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
        return

    if dry_run:
        print(f"  {path}entries = {converted!r}")
        return

    gs = source.get_settings(SCHEMAS["pronunciations"], path)
    gs.set_value("entries", GLib.Variant("a{ss}", converted))
    gs.set_int("version", 1)
    print(f"  Imported pronunciations for {label}")


# Keys in the JSON keybindings dict that are metadata, not actual keybinding commands.
_KEYBINDINGS_METADATA_KEYS = {"keyboardLayout", "orcaModifierKeys"}


def _import_keybindings(
    source: SchemaSource,
    keybindings_dict: dict,
    path: str,
    label: str,
    dry_run: bool,
) -> None:
    """Import keybinding overrides to GSettings.

    JSON format: {command_name: [[keysym, mask, mods, clicks], ...]}
    GSettings format: a{saas} (same structure, all strings)
    """
    converted: dict[str, list[list[str]]] = {}
    for key, value in keybindings_dict.items():
        if key in _KEYBINDINGS_METADATA_KEYS:
            continue
        if isinstance(value, list):
            bindings: list[list[str]] = []
            for binding in value:
                if isinstance(binding, list):
                    bindings.append([str(v) for v in binding])
            converted[key] = bindings
    if not converted:
        return

    if dry_run:
        for cmd, bindings in sorted(converted.items()):
            if not bindings:
                print(f"  {path}entries[{cmd}] = [] (unbound)")
            else:
                for b in bindings:
                    print(f"  {path}entries[{cmd}] = {b}")
        return

    gs = source.get_settings(SCHEMAS["keybindings"], path)
    gs.set_value("entries", GLib.Variant("a{saas}", converted))
    gs.set_int("version", 1)
    print(f"  Imported keybindings for {label}")


def _import_profile(
    source: SchemaSource,
    profile_name: str,
    profile_prefs: dict,
    dry_run: bool,
) -> None:
    """Import all settings for a single profile."""
    profile = sanitize_gsettings_path(profile_name)

    for schema_name in ALL_MAPPINGS:
        path = _build_profile_path(profile, schema_name)
        _import_mapped_settings(
            source, schema_name, path, profile_prefs, f"profile:{profile_name}", dry_run
        )

    _import_synthesizer(source, profile_prefs, profile, f"profile:{profile_name}", dry_run)

    voices = profile_prefs.get("voices", {})
    for voice_type in VOICE_TYPES:
        voice_data = voices.get(voice_type, {})
        if not voice_data:
            continue
        vt = sanitize_gsettings_path(voice_type)
        path = _build_profile_path(profile, f"voices/{vt}")
        _import_voice(
            source, voice_data, path, f"voice:{voice_type}/profile:{profile_name}", dry_run
        )

    pronunciations = profile_prefs.get("pronunciations", {})
    if pronunciations:
        path = _build_profile_path(profile, "pronunciations")
        _import_pronunciations(source, pronunciations, path, f"profile:{profile_name}", dry_run)

    keybindings_data = profile_prefs.get("keybindings", {})
    if keybindings_data:
        path = _build_profile_path(profile, "keybindings")
        _import_keybindings(source, keybindings_data, path, f"profile:{profile_name}", dry_run)


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
        pronunciations = profile_data.get("pronunciations", {})
        app_keybindings = profile_data.get("keybindings", {})
        if not general and not pronunciations and not app_keybindings:
            continue
        label = f"profile:{profile_name}/app:{app_name}"

        for schema_name in ALL_MAPPINGS:
            path = _build_app_path(app_name, profile_name, schema_name)
            _import_mapped_settings(source, schema_name, path, general, label, dry_run)

        voices = general.get("voices", {})
        for voice_type in VOICE_TYPES:
            voice_data = voices.get(voice_type, {})
            if not voice_data:
                continue
            vt = sanitize_gsettings_path(voice_type)
            path = _build_app_path(app_name, profile_name, f"voices/{vt}")
            _import_voice(source, voice_data, path, f"voice:{voice_type}/{label}", dry_run)

        if pronunciations:
            path = _build_app_path(app_name, profile_name, "pronunciations")
            _import_pronunciations(source, pronunciations, path, label, dry_run)

        if app_keybindings:
            path = _build_app_path(app_name, profile_name, "keybindings")
            _import_keybindings(source, app_keybindings, path, label, dry_run)


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


def _export_voice(gs: Gio.Settings) -> dict:
    """Export voice settings from a Gio.Settings to ACSS format."""
    voice_data: dict[str, Any] = {}

    for acss_key, (gs_key, gs_type, _default) in VOICE_MIGRATION_MAP.items():
        user_value = gs.get_user_value(gs_key)
        if user_value is None:
            continue
        if gs_type == "i":
            voice_data[acss_key] = user_value.get_int32()
        elif gs_type == "d":
            voice_data[acss_key] = user_value.get_double()

    family_value = gs.get_user_value("family-name")
    if family_value is not None:
        name = family_value.get_string()
        if name:
            voice_data["family"] = {"name": name}

    return voice_data


def _export_pronunciations(gs: Gio.Settings) -> dict:
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


def _export_keybindings(gs: Gio.Settings) -> dict:
    """Export keybinding overrides from GSettings to JSON format.

    GSettings format: a{saas} {command: [[keysym, mask, mods, clicks], ...]}
    JSON format: same structure
    """
    user_value = gs.get_user_value("entries")
    if user_value is None:
        return {}
    return user_value.unpack()


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

    # Synthesizer (special case: not in a mapping table)
    try:
        path = _build_profile_path(profile, "speech")
        gs = source.get_settings(SCHEMAS["speech"], path)
        synth_value = gs.get_user_value("synthesizer")
        if synth_value is not None:
            profile_data["speechServerInfo"] = ["Speech Dispatcher", synth_value.get_string()]
    except ValueError:
        pass

    # Voice settings
    voices: dict[str, Any] = {}
    for voice_type in VOICE_TYPES:
        try:
            vt = sanitize_gsettings_path(voice_type)
            path = _build_profile_path(profile, f"voices/{vt}")
            gs = source.get_settings(SCHEMAS["voice"], path)
            voice_data = _export_voice(gs)
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
        pronunciations = _export_pronunciations(gs)
        if pronunciations:
            profile_data["pronunciations"] = pronunciations
    except ValueError:
        pass

    # Keybindings
    try:
        path = _build_profile_path(profile, "keybindings")
        gs = source.get_settings(SCHEMAS["keybindings"], path)
        kb = _export_keybindings(gs)
        if kb:
            profile_data["keybindings"] = kb
    except ValueError:
        pass

    return profile_data


def _dconf_list(path: str) -> list[str]:
    """List dconf entries under a path. Returns empty list on failure."""
    try:
        output = subprocess.check_output(["dconf", "list", path], text=True)
        return [e.strip("/") for e in output.strip().split("\n") if e.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def _export_apps(source: SchemaSource, profile_name: str, output_dir: str) -> None:
    """Export app-specific settings for a profile."""
    profile = sanitize_gsettings_path(profile_name)
    apps_prefix = f"{GSETTINGS_PATH_PREFIX}{profile}/apps/"
    app_entries = _dconf_list(apps_prefix)
    if not app_entries:
        return

    app_settings_dir = os.path.join(output_dir, "app-settings")
    os.makedirs(app_settings_dir, exist_ok=True)

    for app_name in app_entries:
        app_data: dict[str, Any] = {}

        # Mapped settings (speech, typing-echo, caret-navigation, etc.)
        for schema_name, mappings in ALL_MAPPINGS.items():
            try:
                path = _build_app_path(app_name, profile, schema_name)
                gs = source.get_settings(SCHEMAS[schema_name], path)
                app_data.update(gsettings_to_json(gs, mappings))
            except ValueError:
                pass

        # Voices
        voices: dict[str, Any] = {}
        for voice_type in VOICE_TYPES:
            try:
                vt = sanitize_gsettings_path(voice_type)
                path = _build_app_path(app_name, profile, f"voices/{vt}")
                gs = source.get_settings(SCHEMAS["voice"], path)
                voice_data = _export_voice(gs)
                if voice_data:
                    voices[voice_type] = voice_data
            except ValueError:
                pass
        if voices:
            app_data["voices"] = voices

        # Pronunciations (stored outside "general" in app settings JSON)
        app_pronunciations: dict[str, list[str]] = {}
        try:
            path = _build_app_path(app_name, profile, "pronunciations")
            gs = source.get_settings(SCHEMAS["pronunciations"], path)
            app_pronunciations = _export_pronunciations(gs)
        except ValueError:
            pass

        # Keybindings (stored outside "general" in app settings JSON)
        app_kb: dict = {}
        try:
            path = _build_app_path(app_name, profile, "keybindings")
            gs = source.get_settings(SCHEMAS["keybindings"], path)
            app_kb = _export_keybindings(gs)
        except ValueError:
            pass

        if not app_data and not app_pronunciations and not app_kb:
            continue

        filepath = os.path.join(app_settings_dir, f"{app_name}.conf")
        if os.path.isfile(filepath):
            with open(filepath, encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = {"profiles": {}}
        profile_entry: dict[str, Any] = {"general": app_data}
        if app_pronunciations:
            profile_entry["pronunciations"] = app_pronunciations
        if app_kb:
            profile_entry["keybindings"] = app_kb
        existing.setdefault("profiles", {})[profile_name] = profile_entry
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4)
        print(f"  Exported app:{app_name}/profile:{profile_name}")


def export_settings(source: SchemaSource, output_dir: str) -> None:
    """Export GSettings/dconf settings to JSON format."""
    entries = _dconf_list(GSETTINGS_PATH_PREFIX)
    if not entries:
        print("No Orca settings found in dconf.", file=sys.stderr)
        return

    result: dict[str, Any] = {"profiles": {}}

    for profile_name in entries:
        profile_data = _export_profile(source, profile_name)
        if profile_data:
            profile_data["profile"] = [
                profile_name.replace("-", " ").title(),
                profile_name,
            ]
            result["profiles"][profile_name] = profile_data
            print(f"  Exported profile:{profile_name}")

    output_file = os.path.join(output_dir, "user-settings.conf")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    print(f"Wrote {output_file}")

    for profile_name in entries:
        _export_apps(source, profile_name, output_dir)


def compile_schemas(src_dir: str, output_dir: str) -> str:
    """Generate and compile GSettings schemas. Returns the schema directory."""
    os.makedirs(output_dir, exist_ok=True)

    generator = os.path.join(os.path.dirname(__file__), "generate_gsettings_schemas.py")
    if not os.path.isfile(generator):
        print(f"Error: Schema generator not found: {generator}", file=sys.stderr)
        sys.exit(1)

    output_xml = os.path.join(output_dir, "org.gnome.Orca.gschema.xml")
    subprocess.check_call([sys.executable, generator, src_dir, output_xml])
    print(f"Generated schema: {output_xml}")

    subprocess.check_call(["glib-compile-schemas", output_dir])
    print(f"Compiled schemas in: {output_dir}")

    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Orca GSettings tool: compile schemas, import/export settings"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    cs = subparsers.add_parser("compile-schemas", help="Generate and compile GSettings schemas")
    cs.add_argument("output_dir", help="Output directory for compiled schemas")
    cs.add_argument("--src-dir", default="src", help="Path to src directory (default: src)")

    imp = subparsers.add_parser("import", help="Import JSON settings into GSettings/dconf")
    imp.add_argument(
        "settings_dir",
        help="Directory containing user-settings.conf (and optionally app-settings/)",
    )
    imp.add_argument(
        "--schema-dir",
        default=None,
        help="Directory with compiled schemas (default: system-installed)",
    )
    imp.add_argument(
        "--dry-run", action="store_true", help="Show what would be written without changes"
    )

    exp = subparsers.add_parser("export", help="Export GSettings/dconf settings to JSON")
    exp.add_argument("output_dir", help="Directory to write exported settings")
    exp.add_argument(
        "--schema-dir",
        default=None,
        help="Directory with compiled schemas (default: system-installed)",
    )

    args = parser.parse_args()

    if args.command == "compile-schemas":
        compile_schemas(args.src_dir, args.output_dir)

    elif args.command == "import":
        source = SchemaSource(args.schema_dir)
        print(f"Importing from {args.settings_dir}...")
        import_settings(args.settings_dir, source, dry_run=args.dry_run)
        if args.dry_run:
            print("(dry run - no changes made)")
        else:
            Gio.Settings.sync()
            print("Import complete.")

    elif args.command == "export":
        source = SchemaSource(args.schema_dir)
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"Exporting to {args.output_dir}...")
        export_settings(source, args.output_dir)


if __name__ == "__main__":
    main()
