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

"""Shared GSettings infrastructure for Orca modules."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable

from gi.repository import Gio

from . import debug

GSETTINGS_PATH_PREFIX = "/org/gnome/orca/"


@dataclass
class SettingDescriptor:
    """Describes a setting for schema generation and runtime saving."""

    gsettings_key: str
    schema: str
    gtype: str  # "b", "s", "i", "d", or "" when genum is set
    default: Any
    getter: Callable[[], Any] | None = None
    voice_type: str | None = None
    genum: str | None = None


@dataclass
class SettingsMapping:
    """Describes a mapping between a JSON settings key and a GSettings key."""

    json_key: str
    gs_key: str
    gtype: str  # "b", "s", "i", "d"
    default: Any
    enum_map: dict[int, str] | None = None


class GSettingsRegistry:
    """Central registry for GSettings metadata, mappings, and active context."""

    def __init__(self) -> None:
        self._app_name: str | None = None
        self._profile: str = "default"
        self._descriptors: dict[str, SettingDescriptor] = {}
        self._mappings: dict[str, list[SettingsMapping]] = {}
        self._enums: dict[str, dict[str, int]] = {}
        self._schemas: dict[str, str] = {}

    @staticmethod
    def sanitize_gsettings_path(name: str) -> str:
        """Sanitize a name for use in a GSettings path."""

        sanitized = name.lower()
        sanitized = re.sub(r"[^a-z0-9-]", "-", sanitized)
        sanitized = re.sub(r"-+", "-", sanitized)
        return sanitized.strip("-")

    def set_active_app(self, app_name: str | None) -> None:
        """Sets the active app name for GSettings lookups."""

        self._app_name = app_name or None

    def set_active_profile(self, profile: str) -> None:
        """Sets the active profile for GSettings lookups."""

        self._profile = profile

    def get_active_app(self) -> str | None:
        """Returns the active app name for GSettings lookups."""

        return self._app_name

    def get_active_profile(self) -> str:
        """Returns the active profile for GSettings lookups."""

        return self._profile

    def gsetting(
        self,
        key: str,
        schema: str,
        default: Any,
        summary: str,  # pylint: disable=unused-argument
        gtype: str = "",
        genum: str | None = None,
        voice_type: str | None = None,
    ) -> Callable[[Callable], Callable]:
        """Decorator marking a method's associated GSettings key."""

        def decorator(func: Callable) -> Callable:
            self._descriptors[key] = SettingDescriptor(
                gsettings_key=key,
                schema=schema,
                gtype=gtype,
                default=default,
                getter=None,
                voice_type=voice_type,
                genum=genum,
            )
            func.gsetting_key = key  # type: ignore[attr-defined]
            return func

        return decorator

    def gsettings_schema(
        self,
        schema_id: str,
        name: str,
    ) -> Callable[[type], type]:
        """Class decorator declaring this class contributes to a GSettings schema."""

        self._schemas[name] = schema_id

        def decorator(cls: type) -> type:
            return cls

        return decorator

    def gsettings_enum(
        self,
        enum_id: str,
        values: dict[str, int],
    ) -> Callable[[type], type]:
        """Decorator marking an Enum class for GSettings schema generation."""

        self._enums[enum_id] = values

        def decorator(cls: type) -> type:
            return cls

        return decorator

    def register_settings_mappings(self, schema_name: str, mappings: list[SettingsMapping]) -> None:
        """Registers JSON-to-GSettings mappings for a schema."""

        self._mappings[schema_name] = mappings

    def _get_settings_mappings(self, schema_name: str) -> list[SettingsMapping]:
        """Returns the registered mappings for a schema name."""

        return self._mappings.get(schema_name, [])

    def _json_to_gsettings(
        self,
        json_dict: dict,
        gs: Gio.Settings,
        schema_name: str,
    ) -> bool:
        """Writes JSON settings to a Gio.Settings object. Returns True if any value was written."""

        mappings = self._get_settings_mappings(schema_name)
        if not mappings:
            return False

        wrote_any = False
        for m in mappings:
            if m.json_key not in json_dict:
                continue

            value = json_dict[m.json_key]

            if m.enum_map is not None:
                # int in JSON → string in GSettings
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

        return wrote_any

    def _gsettings_to_json(
        self,
        gs: Gio.Settings,
        schema_name: str,
    ) -> dict:
        """Reads explicitly-set GSettings values into a JSON-compatible dict."""

        mappings = self._get_settings_mappings(schema_name)
        if not mappings:
            return {}

        result: dict[str, Any] = {}
        for m in mappings:
            user_value = gs.get_user_value(m.gs_key)
            if user_value is None:
                continue

            if m.enum_map is not None:
                # string in GSettings → int in JSON
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

        return result

    @staticmethod
    def _get_settings_manager():
        """Returns the settings manager singleton. Lazy import to avoid circular imports.

        This is only needed for migration from JSON to GSettings."""

        from . import settings_manager  # pylint: disable=import-outside-toplevel

        return settings_manager.get_manager()

    # pylint: disable-next=too-many-locals
    def migrate_schema(
        self,
        handle: GSettingsSchemaHandle,
        schema_name: str,
        owner_name: str = "",
    ) -> bool:
        """Migrates JSON settings to GSettings for all profiles and apps.

        Args:
            handle:      The GSettingsSchemaHandle for the schema being migrated.
            schema_name: The name used with register_settings_mappings() for this schema.
            owner_name:  Module name for debug messages.
        """

        if handle.is_current_version():
            msg = f"{owner_name}: GSettings already current."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not handle.has_key("version"):
            msg = f"{owner_name}: Schema missing version key."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        mappings = self._get_settings_mappings(schema_name)
        if not mappings:
            msg = f"{owner_name}: No mappings registered for '{schema_name}'."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = f"{owner_name}: Migrating settings to GSettings."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        manager = self._get_settings_manager()
        migrated_any = False

        for _label, profile_name in manager.available_profiles():
            if self._migrate_profile(handle, schema_name, profile_name, owner_name):
                migrated_any = True

        if self._migrate_all_apps(handle, schema_name, owner_name):
            migrated_any = True

        msg = f"{owner_name}: Migration complete."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return migrated_any

    def _migrate_profile(
        self,
        handle: GSettingsSchemaHandle,
        schema_name: str,
        profile_name: str,
        owner_name: str,
    ) -> bool:
        """Migrates a single profile's settings from JSON to GSettings."""

        gs = handle.get_for_profile(profile_name)
        if gs is None:
            return False

        manager = self._get_settings_manager()
        settings_file = manager.get_settings_file_path()
        try:
            with open(settings_file, encoding="utf-8") as f:
                prefs = json.load(f)
            profile_prefs = prefs.get("profiles", {}).get(profile_name, {})
        except (OSError, json.JSONDecodeError):
            return False

        wrote = self._json_to_gsettings(profile_prefs, gs, schema_name)
        if wrote:
            handle.stamp_version(gs)
            msg = f"{owner_name}: Migrated profile:{profile_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return wrote

    def _migrate_all_apps(
        self,
        handle: GSettingsSchemaHandle,
        schema_name: str,
        owner_name: str,
    ) -> bool:
        """Migrates app-specific settings from JSON to GSettings."""

        manager = self._get_settings_manager()
        app_settings_dir = os.path.join(manager.get_prefs_dir(), "app-settings")
        if not os.path.isdir(app_settings_dir):
            return False

        migrated_any = False
        for filename in os.listdir(app_settings_dir):
            if not filename.endswith(".conf"):
                continue
            app_name = filename[:-5]
            if self._migrate_app(handle, schema_name, app_name, app_settings_dir, owner_name):
                migrated_any = True
        return migrated_any

    def _migrate_app(
        self,
        handle: GSettingsSchemaHandle,
        schema_name: str,
        app_name: str,
        app_settings_dir: str,
        owner_name: str,
    ) -> bool:
        """Migrates a single app's settings from JSON to GSettings for all profiles."""

        filepath = os.path.join(app_settings_dir, f"{app_name}.conf")
        try:
            with open(filepath, encoding="utf-8") as f:
                prefs = json.load(f)
        except (OSError, json.JSONDecodeError):
            return False

        migrated_any = False
        for profile_name, profile_data in prefs.get("profiles", {}).items():
            general = profile_data.get("general", {})
            if not general:
                continue
            gs = handle.get_for_app(app_name, profile_name)
            if gs is None:
                continue
            wrote = self._json_to_gsettings(general, gs, schema_name)
            if wrote:
                handle.stamp_version(gs)
                msg = f"{owner_name}: Migrated app:{app_name}/profile:{profile_name}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                migrated_any = True
        return migrated_any


class GSettingsSchemaHandle:
    """Encapsulates a GSettings schema and provides layered lookup."""

    def __init__(
        self,
        schema_id: str,
        path_suffix: str,
        owner_name: str = "",
        version: int = 1,
    ) -> None:
        """Initialize a GSettings schema handle.

        Args:
            schema_id:   Relocatable schema ID (e.g., "org.gnome.Orca.TypingEcho").
            path_suffix: Suffix after the profile segment (e.g., "typing-echo").
            owner_name:  Module name for debug messages.
            version:     Schema version number for version tracking.
        """
        self._schema_id = schema_id
        self._path_suffix = path_suffix
        self._owner_name = owner_name
        self._version = version
        self._schema: Gio.SettingsSchema | None = None
        self._cache: dict[str, Gio.Settings] = {}

    @property
    def schema_id(self) -> str:
        """The schema ID for this handle."""
        return self._schema_id

    def get_schema(self) -> Gio.SettingsSchema | None:
        """Returns the GSettings schema, or None if not installed."""

        if self._schema is not None:
            return self._schema

        source = Gio.SettingsSchemaSource.get_default()  # pylint: disable=no-value-for-parameter
        if source is None:
            msg = f"{self._owner_name}: GSettings schema source not available"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        self._schema = source.lookup(self._schema_id, True)
        if self._schema is None:
            msg = f"{self._owner_name}: Schema {self._schema_id} not found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            msg = f"{self._owner_name}: Schema {self._schema_id} loaded"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return self._schema

    def has_key(self, key: str) -> bool:
        """Returns True if the schema has the given key."""

        schema = self.get_schema()
        if schema is None:
            return False
        return schema.has_key(key)

    def _build_profile_path(self, profile: str, sub_path: str = "") -> str:
        """Returns the dconf path for a profile."""
        profile = GSettingsRegistry.sanitize_gsettings_path(profile)
        suffix = sub_path if sub_path else self._path_suffix
        return f"{GSETTINGS_PATH_PREFIX}{profile}/{suffix}/"

    def _build_app_path(self, app_name: str, profile: str, sub_path: str = "") -> str:
        """Returns the dconf path for an app override."""

        profile = GSettingsRegistry.sanitize_gsettings_path(profile)
        app_name = GSettingsRegistry.sanitize_gsettings_path(app_name)
        suffix = sub_path if sub_path else self._path_suffix
        return f"{GSETTINGS_PATH_PREFIX}{profile}/apps/{app_name}/{suffix}/"

    def _get_for_path(self, path: str) -> Gio.Settings | None:
        """Returns Gio.Settings for a specific dconf path, with caching."""

        if path in self._cache:
            return self._cache[path]

        if self.get_schema() is None:
            return None

        gs = Gio.Settings.new_with_path(self._schema_id, path)
        self._cache[path] = gs
        return gs

    def get_for_profile(self, profile: str, sub_path: str = "") -> Gio.Settings | None:
        """Returns Gio.Settings for a profile."""

        path = self._build_profile_path(profile, sub_path)
        return self._get_for_path(path)

    def get_for_app(
        self, app_name: str, profile: str = "default", sub_path: str = ""
    ) -> Gio.Settings | None:
        """Returns Gio.Settings for an app override within a profile."""

        path = self._build_app_path(app_name, profile, sub_path)
        return self._get_for_path(path)

    def _layered_get(
        self,
        key: str,
        extractor: Callable[[Gio.Settings, str], Any],
        sub_path: str = "",
    ) -> Any | None:
        """Returns the value from layered lookup (app -> profile -> default), or None."""

        if not self.has_key(key):
            return None

        registry = get_registry()
        app_name = registry.get_active_app()
        profile = registry.get_active_profile()

        # Layer 1: App-specific override
        if app_name:
            gs = self.get_for_app(app_name, profile, sub_path)
            if gs is not None and gs.get_user_value(key) is not None:
                return extractor(gs, key)

        # Layer 2: Current profile
        gs = self.get_for_profile(profile, sub_path)
        if gs is not None and gs.get_user_value(key) is not None:
            return extractor(gs, key)

        # Layer 3: Default profile (if current is not default)
        if profile != "default":
            gs = self.get_for_profile("default", sub_path)
            if gs is not None and gs.get_user_value(key) is not None:
                return extractor(gs, key)

        return None

    def get_boolean(self, key: str, sub_path: str = "") -> bool | None:
        """Returns a boolean via layered lookup, or None."""
        return self._layered_get(key, lambda gs, k: gs.get_boolean(k), sub_path)

    def get_string(self, key: str, sub_path: str = "") -> str | None:
        """Returns a string via layered lookup, or None."""
        return self._layered_get(key, lambda gs, k: gs.get_string(k), sub_path)

    def get_int(self, key: str, sub_path: str = "") -> int | None:
        """Returns an int via layered lookup, or None."""
        return self._layered_get(key, lambda gs, k: gs.get_int(k), sub_path)

    def get_double(self, key: str, sub_path: str = "") -> float | None:
        """Returns a double via layered lookup, or None."""
        return self._layered_get(key, lambda gs, k: gs.get_double(k), sub_path)

    def _set_value(
        self,
        key: str,
        writer: Callable[[Gio.Settings, str], None],
        sub_path: str = "",
    ) -> bool:
        """Sets a value in the current profile, stamping version on first write."""

        if not self.has_key(key):
            return False

        profile = get_registry().get_active_profile()
        gs = self.get_for_profile(profile, sub_path)
        if gs is None:
            return False

        writer(gs, key)
        if self.has_key("version") and gs.get_user_value("version") is None:
            gs.set_int("version", self._version)
        return True

    def set_boolean(self, key: str, value: bool, sub_path: str = "") -> bool:
        """Sets a boolean in the current profile."""
        return self._set_value(key, lambda gs, k: gs.set_boolean(k, value), sub_path)

    def set_string(self, key: str, value: str, sub_path: str = "") -> bool:
        """Sets a string in the current profile."""
        return self._set_value(key, lambda gs, k: gs.set_string(k, value), sub_path)

    def set_int(self, key: str, value: int, sub_path: str = "") -> bool:
        """Sets an int in the current profile."""
        return self._set_value(key, lambda gs, k: gs.set_int(k, value), sub_path)

    def set_double(self, key: str, value: float, sub_path: str = "") -> bool:
        """Sets a double in the current profile."""
        return self._set_value(key, lambda gs, k: gs.set_double(k, value), sub_path)

    def stamp_version(self, gs: Gio.Settings) -> None:
        """Stamps the current version on a Gio.Settings instance."""

        gs.set_int("version", self._version)

    def is_current_version(self, profile: str = "default") -> bool:
        """Returns True if GSettings is at the current version for a profile."""

        gs = self.get_for_profile(profile)
        if gs is None:
            return False
        if not self.has_key("version"):
            return False
        return gs.get_int("version") >= self._version

    def set_version(self, profile: str = "default") -> bool:
        """Sets the GSettings version for a profile."""

        gs = self.get_for_profile(profile)
        if gs is None:
            return False
        if not self.has_key("version"):
            return False
        gs.set_int("version", self._version)
        return True


_registry: GSettingsRegistry = GSettingsRegistry()


def get_registry() -> GSettingsRegistry:
    """Returns the GSettingsRegistry singleton."""

    return _registry
