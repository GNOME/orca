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

# pylint: disable=too-many-arguments,too-many-positional-arguments
# pylint: disable=too-many-locals,too-many-instance-attributes,too-many-lines
# pylint: disable=too-many-public-methods,too-many-branches

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, overload

from gi.repository import Gio

from . import debug, gsettings_migrator

if TYPE_CHECKING:
    from collections.abc import Callable

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
    migration_key: str | None = None


SettingsMapping = gsettings_migrator.SettingsMapping


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
        self._extras_migrated: set[str] = set()
        self._handles: dict[str, GSettingsSchemaHandle] = {}
        self._runtime_values: dict[tuple[str, str, str | None], Any] = {}

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

        runtime = self._runtime_values.get((schema, key, voice_type))
        if runtime is not None:
            msg = f"GSETTINGS REGISTRY: {schema}/{key} runtime override = {runtime!r}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return runtime

        handle = self._get_handle(schema)
        if handle is None:
            return self._use_default(schema, key, default)

        sub_path = ""
        if schema == "voice":
            vt = voice_type or "default"
            sub_path = f"voices/{gsettings_migrator.sanitize_gsettings_path(vt)}"

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
        result = accessor(key, sub_path, app_name) if accessor is not None else None
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

        return gsettings_migrator.sanitize_gsettings_path(name)

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
        profile = gsettings_migrator.sanitize_gsettings_path(profile)
        suffix = sub_path or schema_name
        if app_name:
            app = gsettings_migrator.sanitize_gsettings_path(app_name)
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

    def _write_mapped_settings(
        self,
        prefs_dict: dict,
        gs: Gio.Settings,
        schema_name: str,
        skip_defaults: bool = True,
    ) -> bool:
        """Writes mapped settings to a Gio.Settings object."""

        mappings = self._get_settings_mappings(schema_name)
        if not mappings:
            return False
        return gsettings_migrator.json_to_gsettings(prefs_dict, gs, mappings, skip_defaults)

    def _is_migration_done(self) -> bool:
        """Returns True if JSON-to-GSettings migration has already been completed."""

        for name, schema_id in self._schemas.items():
            handle = GSettingsSchemaHandle(schema_id, name)
            if handle.is_current_version():
                msg = f"GSETTINGS REGISTRY: Migration already done (found version on '{name}')."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        count = len(self._schemas)
        msg = f"GSETTINGS REGISTRY: No migration version found. {count} schema(s) to migrate."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    def _stamp_migration_done(self) -> None:
        """Stamps version on all schemas to mark migration as complete."""

        stamped = 0
        for name, schema_id in self._schemas.items():
            handle = GSettingsSchemaHandle(schema_id, name)
            if handle.set_version():
                stamped += 1

        msg = f"GSETTINGS REGISTRY: Stamped migration version on {stamped} schema(s)."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def migrate_all(self, prefs_dir: str) -> bool:
        """Migrates all registered schemas from JSON to GSettings."""

        profiles = self._read_profiles_from_json(prefs_dir)
        migrated_any = False

        if not self._is_migration_done():
            for name, schema_id in self._schemas.items():
                handle = GSettingsSchemaHandle(schema_id, name)
                if self.migrate_schema(handle, name, prefs_dir, profiles):
                    migrated_any = True

            self._migrate_display_names(prefs_dir, profiles)
            self._sync_missing_profiles(prefs_dir, profiles)
            self._stamp_migration_done()
        Gio.Settings.sync()  # pylint: disable=no-value-for-parameter
        return migrated_any

    def import_from_dir(self, import_dir: str) -> None:
        """Imports settings from a directory by resetting dconf and re-migrating."""

        import subprocess  # pylint: disable=import-outside-toplevel

        msg = f"GSETTINGS REGISTRY: Importing settings from '{import_dir}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        try:
            subprocess.run(
                ["dconf", "reset", "-f", GSETTINGS_PATH_PREFIX],
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            msg = f"GSETTINGS REGISTRY: Failed to reset dconf: {e}"
            debug.print_message(debug.LEVEL_SEVERE, msg, True)
            return

        self._extras_migrated.clear()
        self._handles.clear()
        self.migrate_all(import_dir)

    @staticmethod
    def _read_profiles_from_json(prefs_dir: str) -> list:
        """Reads profile list from user-settings.conf for migration."""

        settings_file = os.path.join(prefs_dir, "user-settings.conf")
        if not os.path.exists(settings_file):
            return [["Default", "default"]]

        try:
            with open(settings_file, encoding="utf-8") as f:
                prefs = json.load(f)
        except (OSError, json.JSONDecodeError):
            return [["Default", "default"]]

        profiles = []
        for profile_name, profile_data in prefs.get("profiles", {}).items():
            profile = profile_data.get("profile")
            if profile is None:
                label = profile_name.replace("_", " ").title()
                profile = [label, profile_name]
            profiles.append(profile)
        return profiles or [["Default", "default"]]

    def _migrate_display_names(self, prefs_dir: str, profiles: list) -> None:
        """Writes display-name and internal-name metadata for all profiles and apps."""

        metadata_id = self._schemas.get("metadata")
        if metadata_id is None:
            return

        metadata_handle = GSettingsSchemaHandle(metadata_id, "metadata")

        stamped_profiles: set[str] = set()
        for label, profile_name in profiles:
            gs = metadata_handle.get_for_profile(profile_name)
            if gs is not None:
                gs.set_string("display-name", label)
                gs.set_string("internal-name", profile_name)
                stamped_profiles.add(profile_name)

        app_dir = os.path.join(prefs_dir, "app-settings")
        if not os.path.isdir(app_dir):
            return

        for filename in os.listdir(app_dir):
            if not filename.endswith(".conf"):
                continue
            app_name = filename[:-5]
            filepath = os.path.join(app_dir, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    app_prefs = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue

            for profile_name in app_prefs.get("profiles", {}):
                if profile_name not in stamped_profiles:
                    gs = metadata_handle.get_for_profile(profile_name)
                    if gs is not None:
                        gs.set_string("display-name", profile_name)
                        gs.set_string("internal-name", profile_name)
                        stamped_profiles.add(profile_name)

                gs = metadata_handle.get_for_app(app_name, profile_name)
                if gs is not None:
                    gs.set_string("display-name", app_name)
                    gs.set_string("internal-name", profile_name)

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

        for (schema, _key), desc in self._descriptors.items():
            if schema == schema_name and _key in settings:
                if gs.get_user_value(desc.gsettings_key) is not None:
                    gs.reset(desc.gsettings_key)

        writers: dict[str, Callable[..., None]] = {
            "b": gs.set_boolean,
            "s": gs.set_string,
            "i": gs.set_int,
            "d": gs.set_double,
            "as": gs.set_strv,
        }

        for key, value in settings.items():
            setting = self._descriptors.get((schema_name, key))
            if setting is None:
                continue
            if skip_defaults and value == setting.default:
                continue
            if setting.genum:
                if not isinstance(value, str):
                    enum_data = self._enums.get(setting.genum, {})
                    reverse = {v: k for k, v in enum_data.items()}
                    enum_name = reverse.get(int(value))
                    if enum_name is None:
                        continue
                    gs.set_string(key, enum_name)
                else:
                    gs.set_string(key, value)
                continue
            writer = writers.get(setting.gtype)
            if writer is not None:
                writer(key, value)

    # TODO - JD: Delete this when we remove JSON support.
    def save_schema_to_gsettings(
        self,
        schema_name: str,
        prefs_dict: dict,
        profile: str,
        app_name: str = "",
        skip_defaults: bool = False,
    ) -> None:
        """Writes one schema's mapped settings to dconf. Migration-only."""

        gs = self.get_settings(schema_name, profile, app_name=app_name)
        if gs is None:
            return
        mappings = self._get_settings_mappings(schema_name)
        self._reset_mapped_keys(gs, mappings)
        self._write_mapped_settings(prefs_dict, gs, schema_name, skip_defaults)

    # TODO - JD: Delete this when we remove JSON support.
    def _write_profile_settings(
        self,
        profile_name: str,
        general: dict,
        pronunciations: dict,
        keybindings: dict,
        app_name: str = "",
    ) -> None:
        """Writes all settings for a profile to dconf. Internal admin/migration utility."""

        general = dict(general)
        gsettings_migrator.apply_legacy_aliases(general)

        profile = gsettings_migrator.sanitize_gsettings_path(profile_name)
        skip_defaults = not app_name and profile_name == "default"

        for schema_name in self._schemas:
            if schema_name in ("voice", "pronunciations", "metadata"):
                continue
            self.save_schema_to_gsettings(schema_name, general, profile, app_name, skip_defaults)

        if "voice" in self._schemas:
            voices = general.get("voices", {})
            for voice_type in gsettings_migrator.VOICE_TYPES:
                voice_data = voices.get(voice_type, {})
                if not voice_data:
                    continue
                vt = gsettings_migrator.sanitize_gsettings_path(voice_type)
                voice_gs = self.get_settings("voice", profile, f"voices/{vt}", app_name)
                if voice_gs is not None:
                    gsettings_migrator.import_voice(voice_gs, voice_data, skip_defaults)

        if "speech" in self._schemas:
            speech_gs = self.get_settings("speech", profile, "speech", app_name)
            if speech_gs is not None:
                gsettings_migrator.import_synthesizer(speech_gs, general)

        if pronunciations:
            prefs = {"pronunciations": dict(pronunciations)}
            self._migrate_dict_schema(
                "pronunciations",
                prefs,
                profile,
                gsettings_migrator.import_pronunciations,
                app_name,
            )
        if keybindings:
            prefs = {"keybindings": dict(keybindings)}
            self._migrate_dict_schema(
                "keybindings",
                prefs,
                profile,
                gsettings_migrator.import_keybindings,
                app_name,
            )

        metadata_gs = self.get_settings("metadata", profile, app_name=app_name)
        if metadata_gs is not None:
            if app_name:
                metadata_gs.set_string("display-name", app_name)
                metadata_gs.set_string("internal-name", profile)
            else:
                profile_tuple = general.get("profile")
                if isinstance(profile_tuple, list) and len(profile_tuple) >= 2:
                    metadata_gs.set_string("display-name", profile_tuple[0])
                    metadata_gs.set_string("internal-name", profile_tuple[1])

        Gio.Settings.sync()  # pylint: disable=no-value-for-parameter

    def _sync_missing_profiles(self, prefs_dir: str, profiles: list) -> None:
        """Syncs profiles that exist in JSON but have no dconf entries."""

        settings_file = os.path.join(prefs_dir, "user-settings.conf")
        try:
            with open(settings_file, encoding="utf-8") as f:
                prefs = json.load(f)
        except (OSError, json.JSONDecodeError):
            return

        for _label, profile_name in profiles:
            profile = gsettings_migrator.sanitize_gsettings_path(profile_name)
            metadata_gs = self.get_settings("metadata", profile)
            if metadata_gs is None:
                continue
            if metadata_gs.get_user_value("display-name") is not None:
                continue

            profile_data = prefs.get("profiles", {}).get(profile_name, {})
            if not profile_data:
                continue

            msg = f"GSETTINGS REGISTRY: Syncing missing profile '{profile_name}' to dconf."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            pronunciations = profile_data.get("pronunciations", {})
            keybindings = profile_data.get("keybindings", {})
            self._write_profile_settings(profile_name, profile_data, pronunciations, keybindings)

    def rename_profile(self, old_name: str, new_label: str, new_internal_name: str) -> None:
        """Renames a profile by copying all keys to the new path and resetting the old."""

        old_profile = gsettings_migrator.sanitize_gsettings_path(old_name)
        new_profile = gsettings_migrator.sanitize_gsettings_path(new_internal_name)

        for schema_name in self._schemas:
            if schema_name == "voice":
                for voice_type in gsettings_migrator.VOICE_TYPES:
                    vt = gsettings_migrator.sanitize_gsettings_path(voice_type)
                    old_gs = self.get_settings("voice", old_profile, f"voices/{vt}")
                    new_gs = self.get_settings("voice", new_profile, f"voices/{vt}")
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

        profile = gsettings_migrator.sanitize_gsettings_path(profile_name)
        for schema_name in self._schemas:
            if schema_name == "voice":
                for voice_type in gsettings_migrator.VOICE_TYPES:
                    vt = gsettings_migrator.sanitize_gsettings_path(voice_type)
                    gs = self.get_settings("voice", profile, f"voices/{vt}")
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

    @staticmethod
    def _reset_mapped_keys(gs: Gio.Settings, mappings: list[SettingsMapping]) -> None:
        """Resets all user-set mapped keys so _write_mapped_settings writes a clean slate."""

        for m in mappings:
            if gs.get_user_value(m.gs_key) is not None:
                gs.reset(m.gs_key)

    def migrate_schema(
        self,
        handle: GSettingsSchemaHandle,
        schema_name: str,
        prefs_dir: str,
        profiles: list,
    ) -> bool:
        """Migrates JSON settings to GSettings for all profiles and apps."""

        mappings = self._get_settings_mappings(schema_name)
        if not mappings:
            return False

        msg = f"GSETTINGS REGISTRY: Migrating '{schema_name}' settings to GSettings."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        migrated_any = False

        for _label, profile_name in profiles:
            if self._migrate_profile(handle, schema_name, profile_name, prefs_dir):
                migrated_any = True

        if self._migrate_all_apps(handle, schema_name, prefs_dir):
            migrated_any = True

        return migrated_any

    def _migrate_profile(
        self,
        handle: GSettingsSchemaHandle,
        schema_name: str,
        profile_name: str,
        prefs_dir: str,
    ) -> bool:
        """Migrates a single profile's settings from JSON to GSettings."""

        gs = handle.get_for_profile(profile_name)
        if gs is None:
            return False

        settings_file = os.path.join(prefs_dir, "user-settings.conf")
        try:
            with open(settings_file, encoding="utf-8") as f:
                prefs = json.load(f)
            profile_prefs = prefs.get("profiles", {}).get(profile_name, {})
        except (OSError, json.JSONDecodeError):
            return False

        gsettings_migrator.apply_legacy_aliases(profile_prefs)
        gsettings_migrator.force_navigation_enabled(profile_prefs)
        gsettings_migrator.hoist_keybindings_metadata(profile_prefs)

        skip_defaults = profile_name == "default"

        wrote = self._write_mapped_settings(profile_prefs, gs, schema_name, skip_defaults)
        if wrote:
            msg = f"GSETTINGS REGISTRY: Migrated {schema_name} profile:{profile_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        wrote_extra = self._migrate_profile_extras(profile_name, profile_prefs, skip_defaults)

        return wrote or wrote_extra

    # TODO - JD: Delete this when we remove JSON support.
    def _migrate_profile_extras(
        self,
        profile_name: str,
        profile_prefs: dict,
        skip_defaults: bool,
    ) -> bool:
        """Migrates voices, synthesizer, pronunciations, and keybindings for a profile."""

        key = f"profile:{profile_name}"
        if key in self._extras_migrated:
            return False
        self._extras_migrated.add(key)

        profile = gsettings_migrator.sanitize_gsettings_path(profile_name)
        wrote_any = False

        if "voice" in self._schemas:
            voices = profile_prefs.get("voices", {})
            for voice_type in gsettings_migrator.VOICE_TYPES:
                voice_data = voices.get(voice_type, {})
                if not voice_data:
                    continue
                vt = gsettings_migrator.sanitize_gsettings_path(voice_type)
                voice_gs = self.get_settings("voice", profile, f"voices/{vt}")
                if voice_gs is not None:
                    if gsettings_migrator.import_voice(voice_gs, voice_data, skip_defaults):
                        wrote_any = True

        if "speech" in self._schemas:
            speech_gs = self.get_settings("speech", profile, "speech")
            if speech_gs is not None:
                if gsettings_migrator.import_synthesizer(speech_gs, profile_prefs):
                    wrote_any = True

        if self._migrate_dict_schema(
            "pronunciations",
            profile_prefs,
            profile,
            gsettings_migrator.import_pronunciations,
        ):
            wrote_any = True
        if self._migrate_dict_schema(
            "keybindings",
            profile_prefs,
            profile,
            gsettings_migrator.import_keybindings,
        ):
            wrote_any = True
        return wrote_any

    def _migrate_dict_schema(
        self,
        schema_name: str,
        prefs: dict,
        profile: str,
        importer: Callable[[Gio.Settings, dict], bool],
        app_name: str = "",
    ) -> bool:
        """Migrates a dict-based schema (pronunciations or keybindings)."""

        data = prefs.get(schema_name, {})
        if not data or schema_name not in self._schemas:
            return False
        gs = self.get_settings(schema_name, profile, schema_name, app_name)
        if gs is None:
            return False
        return importer(gs, data)

    def _migrate_all_apps(
        self,
        handle: GSettingsSchemaHandle,
        schema_name: str,
        prefs_dir: str,
    ) -> bool:
        """Migrates app-specific settings from JSON to GSettings."""

        app_settings_dir = os.path.join(prefs_dir, "app-settings")
        if not os.path.isdir(app_settings_dir):
            return False

        migrated_any = False
        for filename in os.listdir(app_settings_dir):
            if not filename.endswith(".conf"):
                continue
            app_name = filename[:-5]
            if self._migrate_app(handle, schema_name, app_name, app_settings_dir):
                migrated_any = True
        return migrated_any

    def _migrate_app(
        self,
        handle: GSettingsSchemaHandle,
        schema_name: str,
        app_name: str,
        app_settings_dir: str,
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
            gsettings_migrator.apply_legacy_aliases(general)
            gsettings_migrator.force_navigation_enabled(general)
            pronunciations = profile_data.get("pronunciations", {})
            app_keybindings = profile_data.get("keybindings", {})
            if not general and not pronunciations and not app_keybindings:
                continue

            gs = handle.get_for_app(app_name, profile_name)
            if gs is None:
                continue
            wrote = self._write_mapped_settings(general, gs, schema_name, skip_defaults=False)
            if wrote:
                msg = (
                    f"GSETTINGS REGISTRY: Migrated {schema_name}"
                    f" app:{app_name}/profile:{profile_name}"
                )
                debug.print_message(debug.LEVEL_INFO, msg, True)
                migrated_any = True

            if self._migrate_app_extras(
                app_name,
                profile_name,
                general,
                pronunciations,
                app_keybindings,
            ):
                migrated_any = True

        return migrated_any

    # TODO - JD: Delete this when we remove JSON support.
    def _migrate_app_extras(
        self,
        app_name: str,
        profile_name: str,
        general: dict,
        pronunciations: dict,
        keybindings_data: dict,
    ) -> bool:
        """Migrates voices, pronunciations, and keybindings for an app override."""

        key = f"app:{app_name}:{profile_name}"
        if key in self._extras_migrated:
            return False
        self._extras_migrated.add(key)

        app_prefs = dict(general)
        app_prefs["pronunciations"] = pronunciations
        app_prefs["keybindings"] = keybindings_data

        wrote_any = False

        if "voice" in self._schemas:
            voices = general.get("voices", {})
            for voice_type in gsettings_migrator.VOICE_TYPES:
                voice_data = voices.get(voice_type, {})
                if not voice_data:
                    continue
                vt = gsettings_migrator.sanitize_gsettings_path(voice_type)
                voice_gs = self.get_settings("voice", profile_name, f"voices/{vt}", app_name)
                if voice_gs is not None:
                    if gsettings_migrator.import_voice(voice_gs, voice_data, False):
                        wrote_any = True

        if "speech" in self._schemas:
            speech_gs = self.get_settings("speech", profile_name, "speech", app_name)
            if speech_gs is not None:
                if gsettings_migrator.import_synthesizer(speech_gs, general):
                    wrote_any = True

        if self._migrate_dict_schema(
            "pronunciations",
            app_prefs,
            profile_name,
            gsettings_migrator.import_pronunciations,
            app_name,
        ):
            wrote_any = True
        if self._migrate_dict_schema(
            "keybindings",
            app_prefs,
            profile_name,
            gsettings_migrator.import_keybindings,
            app_name,
        ):
            wrote_any = True
        return wrote_any


class GSettingsSchemaHandle:
    """Encapsulates a GSettings schema and provides layered lookup."""

    def __init__(
        self,
        schema_id: str,
        path_suffix: str,
        version: int = 1,
    ) -> None:
        self._schema_id = schema_id
        self._path_suffix = path_suffix
        self._version = version
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
        """Returns a merged dict from profile and app layers, or None if neither has a value."""

        # Unlike scalar lookups, dicts do NOT inherit from the default profile.
        # Profile creation copies the default's dict entries into new profiles,
        # so at runtime each profile already has everything it needs. Merging
        # with default would make it impossible to delete inherited entries.

        if not self.has_key(key):
            return None

        registry = get_registry()
        if app_name is None:
            app_name = registry.get_active_app()
        profile = registry.get_active_profile()

        suffix = self._path_suffix
        result: dict = {}
        found_any = False

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
