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

# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, overload

from gi.repository import Gio, GLib

from . import debug

if TYPE_CHECKING:
    from collections.abc import Callable

GSETTINGS_PATH_PREFIX = "/org/gnome/orca/"
PRIMARY_VOICE_SET = "primary"
VOICE_TYPES: list[str] = ["default", "uppercase", "hyperlink", "system"]


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
    migration_key: str | None = None


@dataclass
class SettingsMapping:
    """Describes a mapping between a preferences key and a GSettings key."""

    migration_key: str
    gs_key: str
    gtype: str  # "b", "s", "i", "d", "as"
    default: Any
    enum_map: dict[int, str] | None = None
    string_enum: bool = False


_NOT_SET = object()


class GSettingsRegistry:
    """Central registry for GSettings metadata, mappings, and active context."""

    def __init__(self) -> None:
        self._app_name: str | None = None
        self._profile: str = "default"
        self._descriptors: dict[tuple[str, str], SettingDescriptor] = {}
        self._mappings: dict[str, list[SettingsMapping]] = {}
        self._enums: dict[str, dict[str, int]] = {}
        self._schemas: dict[str, str] = {}
        self._handles: dict[str, GSettingsSchemaHandle] = {}
        self._runtime_values: dict[tuple[str, str, str | None], Any] = {}
        self._ignore_runtime: bool = False

    def set_ignore_runtime(self, ignore: bool) -> None:
        """Sets whether layered_lookup should skip runtime overrides."""

        self._ignore_runtime = ignore

    def _get_handle(self, schema_name: str) -> GSettingsSchemaHandle | None:
        """Returns a cached GSettingsSchemaHandle for a schema name."""

        if schema_name in self._handles:
            return self._handles[schema_name]
        schema_id = self._schemas.get(schema_name)
        if schema_id is None:
            return None
        handle = GSettingsSchemaHandle(schema_id, schema_name)
        self._handles[schema_name] = handle
        return handle

    @overload
    def layered_lookup(
        self,
        schema: str,
        key: str,
        gtype: str,
        genum: str | None = None,
        voice_type: str | None = None,
        app_name: str | None = None,
        *,
        default: Any,
    ) -> Any: ...

    @overload
    def layered_lookup(
        self,
        schema: str,
        key: str,
        gtype: str,
        genum: str | None = None,
        voice_type: str | None = None,
        app_name: str | None = None,
    ) -> Any | None: ...

    def layered_lookup(
        self,
        schema: str,
        key: str,
        gtype: str,
        genum: str | None = None,
        voice_type: str | None = None,
        app_name: str | None = None,
        default: Any = _NOT_SET,
    ) -> Any | None:
        """Returns a setting value via layered GSettings lookup, default, or None."""

        handle = self._get_handle(schema)

        sub_path = ""
        if handle is not None and schema == "voice":
            sub_path = self.voice_set_sub_path(voice_type or "default")

        # For explicit app lookups, check app dconf before runtime overrides.
        if app_name and handle is not None:
            gs = handle.get_for_app(app_name, self.get_active_profile(), sub_path)
            if gs is not None and gs.get_user_value(key) is not None:
                extractors: dict[str, Callable[..., Any]] = {
                    "b": gs.get_boolean,
                    "s": gs.get_string,
                    "i": gs.get_int,
                    "d": gs.get_double,
                    "as": gs.get_strv,
                }
                extractor = extractors.get("s" if genum else gtype)
                if extractor is not None:
                    return extractor(key)

        if not self._ignore_runtime:
            runtime = self._runtime_values.get((schema, key, voice_type))
            if runtime is not None:
                msg = f"GSETTINGS REGISTRY: {schema}/{key} runtime override = {runtime!r}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return runtime

        if handle is None:
            return self._use_default(schema, key, default)

        accessors: dict[str, Callable[..., Any | None]] = {
            "b": handle.get_boolean,
            "s": handle.get_string,
            "i": handle.get_int,
            "d": handle.get_double,
            "as": handle.get_strv,
            "a{ss}": handle.get_dict,
            "a{saas}": handle.get_dict,
        }
        accessor = accessors.get("s" if genum else gtype)
        # For explicit app lookups, skip the app layer (already checked above).
        effective_app = "" if app_name else None
        result = accessor(key, sub_path, effective_app) if accessor is not None else None
        if result is not None:
            return result
        return self._use_default(schema, key, default)

    @staticmethod
    def _use_default(schema: str, key: str, default: Any) -> Any | None:
        """Returns default value, or None if no default was provided."""

        if default is _NOT_SET:
            return None
        msg = f"GSETTINGS REGISTRY: {schema}/{key} using default value = {default!r}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default

    @staticmethod
    def sanitize_gsettings_path(name: str) -> str:
        """Sanitize a name for use in a GSettings path."""

        sanitized = name.lower()
        sanitized = re.sub(r"[^a-z0-9-]", "-", sanitized)
        sanitized = re.sub(r"-+", "-", sanitized)
        return sanitized.strip("-")

    @staticmethod
    def voice_set_sub_path(voice_type: str, voice_set: str = PRIMARY_VOICE_SET) -> str:
        """Returns the dconf sub-path for a voice type within a voice set."""

        sanitized = GSettingsRegistry.sanitize_gsettings_path(voice_type)
        return f"voice-sets/{voice_set}/{sanitized}"

    def get_settings(
        self,
        schema_name: str,
        profile: str,
        sub_path: str = "",
        app_name: str = "",
    ) -> Gio.Settings | None:
        """Creates Gio.Settings for a sub-schema at the correct dconf path."""

        schema_id = self._schemas.get(schema_name)
        if schema_id is None:
            return None
        source = Gio.SettingsSchemaSource.get_default()  # pylint: disable=no-value-for-parameter
        if source is None:
            return None
        if source.lookup(schema_id, True) is None:
            return None
        profile = GSettingsRegistry.sanitize_gsettings_path(profile)
        suffix = sub_path or schema_name
        if app_name:
            app = GSettingsRegistry.sanitize_gsettings_path(app_name)
            path = f"{GSETTINGS_PATH_PREFIX}{profile}/apps/{app}/{suffix}/"
        else:
            path = f"{GSETTINGS_PATH_PREFIX}{profile}/{suffix}/"
        return Gio.Settings.new_with_path(schema_id, path)

    def set_runtime_value(
        self,
        schema: str,
        key: str,
        value: Any,
        voice_type: str | None = None,
    ) -> None:
        """Stores a runtime value override."""

        self._runtime_values[(schema, key, voice_type)] = value

    def get_runtime_value(
        self,
        schema: str,
        key: str,
        voice_type: str | None = None,
    ) -> tuple[bool, Any]:
        """Returns (found, value) for a runtime override."""

        rt_key = (schema, key, voice_type)
        if rt_key in self._runtime_values:
            return True, self._runtime_values[rt_key]
        return False, None

    def remove_runtime_value(self, schema: str, key: str, voice_type: str | None = None) -> None:
        """Removes a single runtime value override."""

        self._runtime_values.pop((schema, key, voice_type), None)

    def clear_runtime_values(self) -> None:
        """Clears all runtime value overrides."""

        self._runtime_values.clear()

    def set_dict(self, schema: str, key: str, gtype: str, value: dict) -> bool:
        """Sets a dict value in dconf for the current profile."""

        gs = self.get_settings(schema, self._profile)
        if gs is None:
            return False
        gs.set_value(key, GLib.Variant(gtype, value))
        return True

    def set_strv(self, schema: str, key: str, value: list[str]) -> bool:
        """Sets a string list in dconf for the current profile."""

        gs = self.get_settings(schema, self._profile)
        if gs is None:
            return False
        gs.set_strv(key, value)
        return True

    def get_pronunciations(self, profile: str = "", app_name: str = "") -> dict:
        """Returns the pronunciation dictionary from dconf for a single profile/app layer."""

        if not profile:
            profile = self._profile
        gs = self.get_settings("pronunciations", profile, "pronunciations", app_name)
        if gs is None:
            return {}
        user_value = gs.get_user_value("entries")
        if user_value is None:
            return {}
        return user_value.unpack()

    def get_keybindings(self, profile: str = "", app_name: str = "") -> dict:
        """Returns the keybinding overrides from dconf for a single profile/app layer."""

        if not profile:
            profile = self._profile
        gs = self.get_settings("keybindings", profile, "keybindings", app_name)
        if gs is None:
            return {}
        user_value = gs.get_user_value("entries")
        if user_value is None:
            return {}
        return user_value.unpack()

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
        migration_key: str | None = None,
    ) -> Callable[[Callable], Callable]:
        """Decorator marking a method's associated GSettings key."""

        def decorator(func: Callable) -> Callable:
            self._descriptors[(schema, key)] = SettingDescriptor(
                gsettings_key=key,
                schema=schema,
                gtype=gtype,
                default=default,
                getter=None,
                voice_type=voice_type,
                genum=genum,
                migration_key=migration_key,
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

    def get_enum_values(self, enum_id: str) -> dict[str, int] | None:
        """Returns the nick-to-int mapping for a registered GSettings enum."""

        return self._enums.get(enum_id)

    def register_settings_mappings(self, schema_name: str, mappings: list[SettingsMapping]) -> None:
        """Registers prefs-to-GSettings mappings for a schema."""

        self._mappings[schema_name] = mappings

    def _build_mappings_from_descriptors(self, schema_name: str) -> list[SettingsMapping]:
        """Builds SettingsMapping list from @gsetting descriptors for a schema."""

        mappings: list[SettingsMapping] = []
        for (schema, _key), desc in self._descriptors.items():
            if schema != schema_name or desc.migration_key is None:
                continue
            enum_map: dict[int, str] | None = None
            if desc.genum and desc.genum in self._enums:
                enum_map = {v: k for k, v in self._enums[desc.genum].items()}
            mappings.append(
                SettingsMapping(
                    desc.migration_key,
                    desc.gsettings_key,
                    desc.gtype,
                    desc.default,
                    enum_map,
                ),
            )
        return mappings

    def _get_settings_mappings(self, schema_name: str) -> list[SettingsMapping]:
        """Returns the registered mappings for a schema name."""

        if schema_name in self._mappings:
            return self._mappings[schema_name]
        return self._build_mappings_from_descriptors(schema_name)

    @staticmethod
    def dconf_list(path: str) -> list[str]:
        """Returns directory entries under a dconf path, stripped of trailing slashes."""

        try:
            result = subprocess.run(  # noqa: S603
                ["dconf", "list", path],  # noqa: S607
                capture_output=True,
                text=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []
        return [e.strip("/") for e in result.stdout.strip().splitlines() if e.strip("/")]

    def get_schema_names(self) -> list[str]:
        """Returns the list of registered schema names."""

        return list(self._schemas.keys())

    def save_schema(
        self,
        schema_name: str,
        settings: dict,
        profile: str,
        app_name: str = "",
        skip_defaults: bool = False,
    ) -> None:
        """Writes settings keyed by GSettings keys directly to dconf."""

        gs = self.get_settings(schema_name, profile, app_name=app_name)
        if gs is None:
            return

        global_gs = None
        if app_name:
            global_gs = self.get_settings(schema_name, profile, app_name="")

        writers: dict[str, Callable[..., None]] = {
            "b": gs.set_boolean,
            "s": gs.set_string,
            "i": gs.set_int,
            "d": gs.set_double,
            "as": gs.set_strv,
        }
        readers: dict[str, Callable[..., Any]] = {
            "b": gs.get_boolean,
            "s": gs.get_string,
            "i": gs.get_int,
            "d": gs.get_double,
            "as": gs.get_strv,
        }
        global_readers: dict[str, Callable[..., Any]] = {}
        if global_gs is not None:
            global_readers = {
                "b": global_gs.get_boolean,
                "s": global_gs.get_string,
                "i": global_gs.get_int,
                "d": global_gs.get_double,
                "as": global_gs.get_strv,
            }

        for key, value in settings.items():
            setting = self._descriptors.get((schema_name, key))
            if setting is None:
                continue

            if setting.genum:
                nick: str
                if isinstance(value, str):
                    nick = value
                else:
                    enum_data = self._enums.get(setting.genum, {})
                    reverse = {v: k for k, v in enum_data.items()}
                    resolved = reverse.get(int(value))
                    if resolved is None:
                        continue
                    nick = resolved
                is_redundant = skip_defaults and nick == setting.default
                if not is_redundant and global_gs is not None:
                    is_redundant = nick == global_gs.get_string(key)
                if is_redundant:
                    if gs.get_user_value(key) is not None:
                        gs.reset(key)
                    continue
                if not app_name or gs.get_user_value(key) is None or gs.get_string(key) != nick:
                    gs.set_string(key, nick)
                continue

            is_redundant = skip_defaults and value == setting.default
            if not is_redundant and global_gs is not None:
                global_reader = global_readers.get(setting.gtype)
                if global_reader is not None:
                    is_redundant = value == global_reader(key)
            if is_redundant:
                if gs.get_user_value(key) is not None:
                    gs.reset(key)
                continue
            reader = readers.get(setting.gtype)
            if reader is not None and reader(key) == value:
                if not app_name or gs.get_user_value(key) is not None:
                    continue
            if value is None:
                msg = f"GSETTINGS: Skipping None value for {schema_name}/{key}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)
                continue
            writer = writers.get(setting.gtype)
            if writer is not None:
                writer(key, value)

    def rename_profile(self, old_name: str, new_label: str, new_internal_name: str) -> None:
        """Renames a profile by copying all keys to the new path and resetting the old."""

        old_profile = GSettingsRegistry.sanitize_gsettings_path(old_name)
        new_profile = GSettingsRegistry.sanitize_gsettings_path(new_internal_name)

        for schema_name in self._schemas:
            if schema_name == "voice":
                for voice_type in VOICE_TYPES:
                    vt = GSettingsRegistry.sanitize_gsettings_path(voice_type)
                    old_gs = self.get_settings("voice", old_profile, self.voice_set_sub_path(vt))
                    new_gs = self.get_settings("voice", new_profile, self.voice_set_sub_path(vt))
                    self.copy_user_keys(old_gs, new_gs)
                continue
            old_gs = self.get_settings(schema_name, old_profile)
            new_gs = self.get_settings(schema_name, new_profile)
            self.copy_user_keys(old_gs, new_gs)

        metadata_gs = self.get_settings("metadata", new_profile)
        if metadata_gs is not None:
            metadata_gs.set_string("display-name", new_label)
            metadata_gs.set_string("internal-name", new_internal_name)

        self.reset_profile(old_name)

    def reset_profile(self, profile_name: str) -> None:
        """Resets all dconf keys for a profile."""

        profile = GSettingsRegistry.sanitize_gsettings_path(profile_name)
        for schema_name in self._schemas:
            if schema_name == "voice":
                for voice_type in VOICE_TYPES:
                    vt = GSettingsRegistry.sanitize_gsettings_path(voice_type)
                    gs = self.get_settings("voice", profile, self.voice_set_sub_path(vt))
                    if gs is not None:
                        self._reset_all_keys(gs)
                continue
            gs = self.get_settings(schema_name, profile)
            if gs is not None:
                self._reset_all_keys(gs)
        Gio.Settings.sync()  # pylint: disable=no-value-for-parameter

    @staticmethod
    def copy_user_keys(source: Gio.Settings | None, dest: Gio.Settings | None) -> None:
        """Copies all user-set keys from source to dest."""

        if source is None or dest is None:
            return
        for key in source.list_keys():
            value = source.get_user_value(key)
            if value is not None:
                dest.set_value(key, value)

    @staticmethod
    def _reset_all_keys(gs: Gio.Settings) -> None:
        """Resets all user-set keys on a Gio.Settings instance."""

        for key in gs.list_keys():
            if gs.get_user_value(key) is not None:
                gs.reset(key)


class GSettingsSchemaHandle:
    """Encapsulates a GSettings schema and provides layered lookup."""

    def __init__(
        self,
        schema_id: str,
        path_suffix: str,
    ) -> None:
        self._schema_id = schema_id
        self._path_suffix = path_suffix
        self._schema: Gio.SettingsSchema | None = None
        self._cache: dict[str, Gio.Settings] = {}

    def get_schema_id(self) -> str:
        """Returns the schema ID for this handle."""
        return self._schema_id

    def get_schema(self) -> Gio.SettingsSchema | None:
        """Returns the GSettings schema, or None if not installed."""

        if self._schema is not None:
            return self._schema

        source = Gio.SettingsSchemaSource.get_default()  # pylint: disable=no-value-for-parameter
        if source is None:
            msg = f"GSETTINGS REGISTRY: Schema source not available for {self._schema_id}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        self._schema = source.lookup(self._schema_id, True)
        if self._schema is None:
            msg = f"GSETTINGS REGISTRY: Schema {self._schema_id} not found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            msg = f"GSETTINGS REGISTRY: Schema {self._schema_id} loaded"
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
        suffix = sub_path or self._path_suffix
        return f"{GSETTINGS_PATH_PREFIX}{profile}/{suffix}/"

    def _build_app_path(self, app_name: str, profile: str, sub_path: str = "") -> str:
        """Returns the dconf path for an app override."""

        profile = GSettingsRegistry.sanitize_gsettings_path(profile)
        app_name = GSettingsRegistry.sanitize_gsettings_path(app_name)
        suffix = sub_path or self._path_suffix
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
        self,
        app_name: str,
        profile: str = "default",
        sub_path: str = "",
    ) -> Gio.Settings | None:
        """Returns Gio.Settings for an app override within a profile."""

        path = self._build_app_path(app_name, profile, sub_path)
        return self._get_for_path(path)

    def _layered_get(
        self,
        key: str,
        extractor: Callable[[Gio.Settings, str], Any],
        sub_path: str = "",
        app_name: str | None = None,
    ) -> Any | None:
        """Returns the value from layered lookup (app -> profile -> default), or None."""

        if not self.has_key(key):
            return None

        registry = get_registry()
        if app_name is None:
            app_name = registry.get_active_app()
        profile = registry.get_active_profile()

        suffix = self._path_suffix
        checked: list[str] = []

        # Layer 1: App-specific override
        if app_name:
            gs = self.get_for_app(app_name, profile, sub_path)
            if gs is not None and gs.get_user_value(key) is not None:
                value = extractor(gs, key)
                msg = (
                    f"GSETTINGS SCHEMA HANDLE: {suffix}/{key}"
                    f" = {value!r} (app:{app_name} profile:{profile})"
                )
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return value
            checked.append(f"app:{app_name}")

        # Layer 2: Current profile
        gs = self.get_for_profile(profile, sub_path)
        if gs is not None and gs.get_user_value(key) is not None:
            value = extractor(gs, key)
            skipped = f" [{', '.join(checked)} not set]" if checked else ""
            msg = (
                f"GSETTINGS SCHEMA HANDLE: {suffix}/{key} = {value!r} (profile:{profile}){skipped}"
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return value
        checked.append(f"profile:{profile}")

        # Layer 3: Default profile (if current is not default)
        if profile != "default":
            gs = self.get_for_profile("default", sub_path)
            if gs is not None and gs.get_user_value(key) is not None:
                value = extractor(gs, key)
                skipped = f" [{', '.join(checked)} not set]"
                msg = (
                    f"GSETTINGS SCHEMA HANDLE: {suffix}/{key}"
                    f" = {value!r} (profile:default fallback){skipped}"
                )
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return value
            checked.append("profile:default")

        msg = f"GSETTINGS SCHEMA HANDLE: {suffix}/{key} not set [{', '.join(checked)}]"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return None

    def get_boolean(self, key: str, sub_path: str = "", app_name: str | None = None) -> bool | None:
        """Returns a boolean via layered lookup, or None."""
        return self._layered_get(key, lambda gs, k: gs.get_boolean(k), sub_path, app_name)

    def get_string(self, key: str, sub_path: str = "", app_name: str | None = None) -> str | None:
        """Returns a string via layered lookup, or None."""
        return self._layered_get(key, lambda gs, k: gs.get_string(k), sub_path, app_name)

    def get_int(self, key: str, sub_path: str = "", app_name: str | None = None) -> int | None:
        """Returns an int via layered lookup, or None."""
        return self._layered_get(key, lambda gs, k: gs.get_int(k), sub_path, app_name)

    def get_double(self, key: str, sub_path: str = "", app_name: str | None = None) -> float | None:
        """Returns a double via layered lookup, or None."""
        return self._layered_get(key, lambda gs, k: gs.get_double(k), sub_path, app_name)

    def get_strv(
        self,
        key: str,
        sub_path: str = "",
        app_name: str | None = None,
    ) -> list[str] | None:
        """Returns a string array via layered lookup, or None."""
        return self._layered_get(key, lambda gs, k: gs.get_strv(k), sub_path, app_name)

    def _layered_get_dict(
        self,
        key: str,
        sub_path: str = "",
        app_name: str | None = None,
    ) -> dict | None:
        """Returns a merged dict from default-profile, profile, and app layers.

        Later layers override earlier ones via dict merge, so profile entries
        shadow inherited default-profile entries (e.g. [] unbinds a keybinding).
        """

        if not self.has_key(key):
            return None

        registry = get_registry()
        if app_name is None:
            app_name = registry.get_active_app()
        profile = registry.get_active_profile()

        suffix = self._path_suffix
        result: dict = {}
        found_any = False

        if profile != "default":
            gs = self.get_for_profile("default", sub_path)
            if gs is not None:
                variant = gs.get_user_value(key)
                if variant is not None:
                    result |= variant.unpack()
                    found_any = True

        gs = self.get_for_profile(profile, sub_path)
        if gs is not None:
            variant = gs.get_user_value(key)
            if variant is not None:
                result |= variant.unpack()
                found_any = True

        if app_name:
            gs = self.get_for_app(app_name, profile, sub_path)
            if gs is not None:
                variant = gs.get_user_value(key)
                if variant is not None:
                    result |= variant.unpack()
                    found_any = True

        if not found_any:
            msg = f"GSETTINGS SCHEMA HANDLE: {suffix}/{key} no dict values set"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        msg = f"GSETTINGS SCHEMA HANDLE: {suffix}/{key} merged dict ({len(result)} entries)"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def get_dict(self, key: str, sub_path: str = "", app_name: str | None = None) -> dict | None:
        """Returns a merged dict via layered lookup, or None."""

        return self._layered_get_dict(key, sub_path, app_name)

    def _set_value(
        self,
        key: str,
        writer: Callable[[Gio.Settings, str], None],
        sub_path: str = "",
    ) -> bool:
        """Sets a value in the current profile."""

        if not self.has_key(key):
            return False

        profile = get_registry().get_active_profile()
        gs = self.get_for_profile(profile, sub_path)
        if gs is None:
            return False

        writer(gs, key)
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


_registry: GSettingsRegistry = GSettingsRegistry()


def get_registry() -> GSettingsRegistry:
    """Returns the GSettingsRegistry singleton."""

    return _registry
