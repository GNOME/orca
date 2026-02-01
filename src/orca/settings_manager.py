# Orca
#
# Copyright 2010 Consorcio Fernando de los Rios.
# Author: Javier Hernandez Antunez <jhernandez@emergya.es>
# Author: Alejandro Leiva <aleiva@emergya.es>
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

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches

"""Settings manager."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


import ast
import importlib
import importlib.util
import os
from json import load, dump
from types import ModuleType
from typing import TYPE_CHECKING

from gi.repository import GLib

from . import debug
from . import orca_i18n  # pylint: disable=no-name-in-module
from . import settings
from . import pronunciation_dictionary_manager
from .acss import ACSS
from .ax_object import AXObject

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .script import Script


class SettingsManager:
    """Settings manager"""

    # Settings managed elsewhere or internal implementation details.
    _EXCLUDED_SETTINGS: set[str] = {
        "speechFactoryModules",
        "speechSystemOverride",
        "silenceSpeech",
    }

    def __init__(self) -> None:
        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Initializing. Here's some extra test for a long line which CI will hopefully catch and fix", True)

        self._profile: str = "default"
        self._prefs_dir: str = ""
        self._settings_file: str = ""
        self._default_settings: dict = {}
        self._settings: dict = {}
        self._pronunciations: dict = {}
        self._keybindings: dict = {}
        self._customized_settings: dict | None = None
        self._configuring: bool = False

        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Initialized", True)

    def get_overridden_settings_for_debugging(self) -> dict:
        """Returns overridden settings for the purpose of debugging."""

        changed = {}
        for key, value in self._default_settings.items():
            if value != self._settings.get(key) and key not in (self._customized_settings or {}):
                changed[key] = self._settings.get(key)
        return changed

    def get_customized_settings_for_debugging(self) -> dict:
        """Returns customized settings for the purpose of debugging."""

        return (self._customized_settings or {}).copy()

    def get_settings(self) -> dict:
        """Returns a copy of the active settings."""

        return self._settings.copy()

    def snapshot_settings(self) -> dict:
        """Capture current runtime settings values for later restoration."""

        snapshot = {}
        for name in dir(settings):
            if name.startswith("_") or name[0].isupper():
                continue
            if name in self._EXCLUDED_SETTINGS:
                continue
            value = getattr(settings, name)
            if isinstance(value, (bool, int, float, str, list, dict, tuple, type(None))):
                snapshot[name] = value
        return snapshot

    def restore_settings(self, snapshot: dict) -> None:
        """Restore runtime settings from a previously captured snapshot."""

        restored = []
        for name, value in snapshot.items():
            current = getattr(settings, name, None)
            if current != value:
                restored.append(f"{name}: {current} -> {value}")
                setattr(settings, name, value)

        if restored:
            msg = f"SETTINGS MANAGER: Restored {len(restored)} runtime settings: {restored}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    # pylint: disable-next=too-many-locals
    def activate(self, prefs_dir: str | None = None, custom_settings: dict | None = None) -> None:
        """Activates this manager."""

        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Activating", True)

        self._prefs_dir = prefs_dir or os.path.join(GLib.get_user_data_dir(), "orca")  # pylint: disable=no-value-for-parameter
        self._settings_file = os.path.join(self._prefs_dir, "user-settings.conf")

        self._default_settings = {}
        for key in dir(settings):
            if key.startswith("_") or key[0].isupper() or key in self._EXCLUDED_SETTINGS:
                continue
            value = getattr(settings, key)
            if callable(value) or isinstance(value, ModuleType):
                continue
            self._default_settings[key] = value
        self._load_customizations()
        if custom_settings and self._customized_settings is not None:
            self._customized_settings.update(custom_settings)

        self._settings = self._default_settings.copy()
        if os.path.exists(self._settings_file):
            self._settings.update(self._get_general_from_file())

        def _create_dir(dir_name: str) -> None:
            if not os.path.isdir(dir_name):
                os.makedirs(dir_name)

        orca_dir = self._prefs_dir
        _create_dir(orca_dir)
        init_file = os.path.join(orca_dir, "__init__.py")
        if not os.path.exists(init_file):
            os.close(os.open(init_file, os.O_CREAT, 0o700))

        orca_script_dir = os.path.join(orca_dir, "orca-scripts")
        _create_dir(orca_script_dir)
        init_file = os.path.join(orca_script_dir, "__init__.py")
        if not os.path.exists(init_file):
            os.close(os.open(init_file, os.O_CREAT, 0o700))

        app_settings_dir = os.path.join(orca_dir, "app-settings")
        _create_dir(app_settings_dir)

        sounds_dir = os.path.join(orca_dir, "sounds")
        _create_dir(sounds_dir)

        customizations_file = os.path.join(orca_dir, "orca-customizations.py")
        if not os.path.exists(customizations_file):
            os.close(os.open(customizations_file, os.O_CREAT, 0o700))

        if not os.path.exists(self._settings_file):
            # Build legacy general dict with all default settings for backwards compatibility
            legacy_general = self._default_settings.copy()
            legacy_general["startingProfile"] = settings.profile
            prefs = {
                "startingProfile": settings.profile,
                "profiles": {
                    "default": {
                        "profile": settings.profile,
                    }
                },
                # Legacy keys for backwards compatibility with older Orca versions
                "general": legacy_general,
                "pronunciations": {},
                "keybindings": {},
            }
            with open(self._settings_file, "w", encoding="utf-8") as settings_file:
                dump(prefs, settings_file, indent=4)

        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Activated", True)

        starting_profile = self._settings.get("startingProfile", ["Default", "default"])

        # Handle corrupted data where list was saved as string representation
        if isinstance(starting_profile, str):
            msg = f"SETTINGS MANAGER: startingProfile is string '{starting_profile}', fixing."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            try:
                starting_profile = ast.literal_eval(starting_profile)
            except (ValueError, SyntaxError):
                starting_profile = ["Default", "default"]

        self._profile = starting_profile[1]
        tokens = ["SETTINGS MANAGER: Current profile is", self._profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.set_profile(self._profile)

    def _load_customizations(self) -> None:
        """Load user's orca-customizations.py and track any settings changes."""

        if self._customized_settings is not None:
            return

        self._customized_settings = {}
        original_settings = {}
        for key, value in settings.__dict__.items():
            if key.startswith("_") or key[0].isupper() or key in self._EXCLUDED_SETTINGS:
                continue
            if callable(value):
                continue
            original_settings[key] = value

        module_path = os.path.join(self._prefs_dir, "orca-customizations.py")
        tokens = ["SETTINGS MANAGER: Attempt to load orca-customizations"]

        try:
            spec = importlib.util.spec_from_file_location("orca-customizations", module_path)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                tokens.extend(["from", module_path, "succeeded."])
            else:
                tokens.extend(["from", module_path, "failed. Spec not found."])
        except FileNotFoundError:
            tokens.extend(["from", module_path, "failed. File not found."])
        except Exception as error:  # pylint: disable=broad-exception-caught
            tokens.extend(["failed due to:", str(error), ". Not loading customizations."])

        debug.print_tokens(debug.LEVEL_ALL, tokens, True)

        for key, value in original_settings.items():
            custom_value = settings.__dict__.get(key)
            if value != custom_value:
                self._customized_settings[key] = custom_value

    def _get_general_from_file(self, profile: str | None = None) -> dict:
        """Get settings from file, merging defaults with profile values."""

        with open(self._settings_file, encoding="utf-8") as settings_file:
            try:
                prefs = load(settings_file)
            except ValueError:
                return {}

        result = self._default_settings.copy()
        # Handle both new format (root level) and old format (inside "general")
        starting_profile = prefs.get("startingProfile")
        if starting_profile is None:
            starting_profile = prefs.get("general", {}).get(
                "startingProfile", ["Default", "default"]
            )

        # Handle corrupted data where list was saved as string representation
        if isinstance(starting_profile, str):
            msg = f"SETTINGS MANAGER: startingProfile is string '{starting_profile}', fixing."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            try:
                starting_profile = ast.literal_eval(starting_profile)
            except (ValueError, SyntaxError):
                starting_profile = ["Default", "default"]

        result["startingProfile"] = starting_profile
        default_profile = starting_profile
        if profile is None:
            profile = default_profile[1]

        # First apply the default profile's settings as a base, then overlay
        # the current profile's settings. This ensures that non-default profiles
        # inherit settings from the default profile that they don't override.
        profiles_to_apply = [default_profile[1]]
        if profile != default_profile[1]:
            profiles_to_apply.append(profile)

        for profile_name in profiles_to_apply:
            profile_settings = prefs["profiles"].get(profile_name, {}).copy()
            for key, value in profile_settings.items():
                if key == "voices":
                    for voice_type, voice_def in value.items():
                        value[voice_type] = ACSS(voice_def)
                if key not in ["startingProfile", "activeProfile"]:
                    result[key] = value

        if "voices" in result:
            for voice_type in (
                settings.DEFAULT_VOICE,
                settings.UPPERCASE_VOICE,
                settings.HYPERLINK_VOICE,
                settings.SYSTEM_VOICE,
            ):
                if voice_type not in result["voices"]:
                    result["voices"][voice_type] = ACSS({})

        try:
            result["activeProfile"] = profile_settings["profile"]
        except KeyError:
            result["activeProfile"] = default_profile

        # Ensure "profile" key is set for saving back to file
        if "profile" not in result and profile is not None:
            label = profile.replace("_", " ").title()
            result["profile"] = [label, profile]

        return result

    def _get_app_settings_from_file(self, app_name: str) -> dict:
        """Load app-specific settings from file."""

        file_name = os.path.join(self._prefs_dir, "app-settings", f"{app_name}.conf")
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as settings_file:
                try:
                    prefs = load(settings_file)
                except ValueError:
                    prefs = {}
        else:
            prefs = {}
        return prefs

    def get_prefs_dir(self) -> str:
        """Returns the preferences directory."""

        return self._prefs_dir

    def set_configuring(self, configuring: bool) -> None:
        """Set whether preferences are currently being configured."""

        self._configuring = configuring
        msg = f"SETTINGS MANAGER: Configuring mode set to {configuring}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def is_configuring(self) -> bool:
        """Return whether preferences are currently being configured."""

        return self._configuring

    def get_voice_locale(self, voice: str = "default") -> str:
        """Returns the locale for the specified voice."""

        voices = settings.voices
        v = ACSS(voices.get(voice, {}))
        lang = v.getLocale()
        dialect = v.getDialect()
        if dialect and len(str(dialect)) == 2:
            lang = f"{lang}_{dialect.upper()}"
        return lang

    def get_speech_server_factories(self) -> list[ModuleType]:
        """Imports all known SpeechServer factory modules."""

        factories: list[ModuleType] = []
        for module_name in settings.speechFactoryModules:
            try:
                module = importlib.import_module(f"orca.{module_name}")
                factories.append(module)
                tokens = ["SETTINGS MANAGER: Valid speech server factory:", module_name]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            except ImportError:
                tokens = ["SETTINGS MANAGER: Invalid speech server factory:", module_name]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return factories

    def _load_profile_settings(self, profile: str | None = None) -> tuple[dict, dict, dict]:
        """Load settings for profile from file. Returns (general, pronunciations, keybindings)."""

        if profile is None:
            profile = self._profile

        msg = f"SETTINGS MANAGER: Loading settings for '{profile}' profile"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        profile_general = self.get_general_settings(profile) or {}
        profile_pronunciations = self.get_pronunciations(profile) or {}
        profile_keybindings = self.get_keybindings(profile) or {}

        msg = f"SETTINGS MANAGER: Settings for '{profile}' profile loaded"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        return profile_general, profile_pronunciations, profile_keybindings

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def _apply_profile_and_app_settings(
        self,
        profile_general: dict,
        profile_pronunciations: dict,
        profile_keybindings: dict,
        app_general: dict | None = None,
        app_pronunciations: dict | None = None,
        app_keybindings: dict | None = None,
    ) -> None:
        """Merge profile and app settings into the active settings."""

        msg = "SETTINGS MANAGER: Merging settings."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._settings.update(profile_general)
        self._settings.update(app_general or {})

        self._pronunciations = profile_pronunciations.copy()
        self._pronunciations.update(app_pronunciations or {})

        # Clear keybindings first to ensure app-specific unbindings don't persist
        # when switching to an app without those overrides
        self._keybindings.clear()
        self._keybindings.update(profile_keybindings)
        self._keybindings.update(app_keybindings or {})

        msg = "SETTINGS MANAGER: Settings merged."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def set_starting_profile(self, profile: list[str] | None = None) -> None:
        """Set the profile that will be used on next start of Orca."""

        if profile is None:
            profile = settings.profile

        with open(self._settings_file, "r+", encoding="utf-8") as settings_file:
            try:
                prefs = load(settings_file)
            except ValueError:
                prefs = {}
            prefs.setdefault("profiles", {})
            prefs["startingProfile"] = profile
            # Update legacy general key for backwards compatibility with older Orca versions
            if "general" not in prefs or not isinstance(prefs["general"], dict):
                prefs["general"] = self._default_settings.copy()
            prefs["general"]["startingProfile"] = profile
            prefs.setdefault("pronunciations", {})
            prefs.setdefault("keybindings", {})
            settings_file.seek(0)
            settings_file.truncate()
            dump(prefs, settings_file, indent=4)

    def get_profile(self) -> str:
        """Returns the active profile."""

        return self._profile

    def get_settings_file_path(self) -> str:
        """Returns the path to the settings file."""

        return self._settings_file

    def set_profile(self, profile: str = "default", update_locale: bool = False) -> None:
        """Set a specific profile as the active one and update settings accordingly."""

        tokens = ["SETTINGS MANAGER: Setting profile to:", profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        old_voice_locale = self.get_voice_locale("default")
        self._profile = profile
        profile_settings = self._load_profile_settings(profile)
        self._apply_profile_and_app_settings(*profile_settings)
        self._set_settings_runtime(self._settings)

        if not update_locale:
            return

        new_voice_locale = self.get_voice_locale("default")
        if old_voice_locale != new_voice_locale:
            orca_i18n.setLocaleForNames(new_voice_locale)
            orca_i18n.setLocaleForMessages(new_voice_locale)
            orca_i18n.setLocaleForGUI(new_voice_locale)

        tokens = ["SETTINGS MANAGER: Profile set to:", profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def remove_profile(self, internal_name: str) -> None:
        """Remove an existing profile."""

        with open(self._settings_file, "r+", encoding="utf-8") as settings_file:
            try:
                prefs = load(settings_file)
            except ValueError:
                return
            if "profiles" not in prefs or internal_name not in prefs["profiles"]:
                return

            del prefs["profiles"][internal_name]
            if not prefs["profiles"]:
                prefs["profiles"]["default"] = {
                    "profile": settings.profile,
                }

            settings_file.seek(0)
            settings_file.truncate()
            dump(prefs, settings_file, indent=4)

    def rename_profile(self, old_internal_name: str, new_profile: list[str]) -> None:
        """Rename profile with old_internal_name to new_profile (label, internal_name)."""

        with open(self._settings_file, "r+", encoding="utf-8") as settings_file:
            try:
                prefs = load(settings_file)
            except ValueError:
                return
            if "profiles" not in prefs or old_internal_name not in prefs["profiles"]:
                return

            profile_data = prefs["profiles"][old_internal_name].copy()
            profile_data["profile"] = new_profile
            prefs["profiles"][new_profile[1]] = profile_data
            del prefs["profiles"][old_internal_name]

            settings_file.seek(0)
            settings_file.truncate()
            dump(prefs, settings_file, indent=4)

    def _set_settings_runtime(self, settings_dict: dict) -> None:
        """Apply settings to the runtime settings module."""

        msg = "SETTINGS MANAGER: Setting runtime settings."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        for key, value in settings_dict.items():
            setattr(settings, str(key), value)
        self._load_customizations()
        for key, value in (self._customized_settings or {}).items():
            setattr(settings, str(key), value)

        msg = "SETTINGS MANAGER: Runtime settings set."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def get_general_settings(self, profile: str = "default") -> dict:
        """Return the current general settings."""

        return self._get_general_from_file(profile)

    def get_pronunciations(self, profile: str = "default") -> dict:
        """Return the current pronunciations settings."""

        with open(self._settings_file, encoding="utf-8") as settings_file:
            try:
                prefs = load(settings_file)
            except ValueError:
                return {}

        profile_settings = prefs["profiles"].get(profile, {})
        return profile_settings.get("pronunciations", {})

    def get_keybindings(self, profile: str = "default") -> dict:
        """Return the keybindings from the profile settings file."""

        with open(self._settings_file, encoding="utf-8") as settings_file:
            try:
                prefs = load(settings_file)
            except ValueError:
                return {}

        profile_settings = prefs["profiles"].get(profile, {})
        return profile_settings.get("keybindings", {})

    def get_active_keybindings(self) -> dict:
        """Return the active keybindings (merged profile + app settings)."""

        return self._keybindings

    # pylint: disable-next=too-many-locals, too-many-branches
    def save_settings(
        self, script: Script, general: dict, pronunciations: dict, keybindings: dict
    ) -> None:
        """Save the settings provided for the script provided."""

        tokens = ["SETTINGS MANAGER: Saving settings for", script, "(app:", script.app, ")"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        app = script.app
        if app:
            app_name = AXObject.get_name(app)

            # Compare against current profile settings to find app-specific differences
            current_general = self.get_general_settings(self._profile)
            app_general = {}
            for key, value in general.items():
                if value != current_general.get(key):
                    app_general[key] = value

            current_pronunciations = self.get_pronunciations(self._profile)
            app_pronunciations = {}
            for key, value in pronunciations.items():
                if value != current_pronunciations.get(key):
                    app_pronunciations[key] = value

            current_keybindings = self.get_keybindings(self._profile)
            app_keybindings = {}
            for key, value in keybindings.items():
                if value != current_keybindings.get(key):
                    app_keybindings[key] = value

            prefs = self._get_app_settings_from_file(app_name)
            profiles = prefs.get("profiles", {})
            profiles[self._profile] = {
                "general": app_general,
                "pronunciations": app_pronunciations,
                "keybindings": app_keybindings,
            }
            prefs["profiles"] = profiles
            file_name = os.path.join(self._prefs_dir, "app-settings", f"{app_name}.conf")
            with open(file_name, "w", encoding="utf-8") as settings_file:
                dump(prefs, settings_file, indent=4)
            return

        _profile = general.get("profile", settings.profile)
        self._profile = _profile[1]

        # Build the profile settings to save (only non-default values)
        profile_general: dict = {}
        for key, value in general.items():
            if key in ["startingProfile", "activeProfile"]:
                continue
            if key == "profile":
                profile_general[key] = value
            elif value != self._default_settings.get(key):
                profile_general[key] = value
            elif self._settings.get(key) != value:
                profile_general[key] = value

        # Ensure profile key is always set
        if not profile_general.get("profile"):
            profile_general["profile"] = _profile

        if pronunciations:
            profile_general["pronunciations"] = dict(pronunciations)
        if keybindings:
            profile_general["keybindings"] = dict(keybindings)

        tokens = ["SETTINGS MANAGER: Saving for profile", self._profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        with open(self._settings_file, "r+", encoding="utf-8") as settings_file:
            try:
                prefs = load(settings_file)
            except ValueError:
                prefs = {}
            prefs.setdefault("profiles", {})
            prefs["profiles"][self._profile] = profile_general
            # Always use Default as the starting profile for backwards compatibility
            default_profile = ["Default", "default"]
            prefs["startingProfile"] = default_profile
            # Write legacy general with all settings for backwards compatibility
            # with older Orca versions
            legacy_general = self._default_settings.copy()
            legacy_general.update(general)
            legacy_general["startingProfile"] = default_profile
            legacy_general.pop("activeProfile", None)
            prefs["general"] = legacy_general
            prefs.setdefault("pronunciations", {})
            prefs.setdefault("keybindings", {})
            settings_file.seek(0)
            settings_file.truncate()
            dump(prefs, settings_file, indent=4)

        # Clear any cached app settings snapshots so they don't overwrite the
        # newly saved settings when focus returns to the original application.
        # Use late import to avoid circular dependency.
        from . import script_manager  # pylint: disable=import-outside-toplevel

        script_manager.get_manager().clear_app_settings_snapshots()

        tokens = ["SETTINGS MANAGER: Settings for", script, "(app:", script.app, ") saved"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def available_profiles(self) -> list:
        """Get available profiles."""

        with open(self._settings_file, encoding="utf-8") as settings_file:
            try:
                prefs = load(settings_file)
            except ValueError:
                return []

        if "profiles" not in prefs:
            return []

        profiles = []
        for profile_name, profile_data in prefs["profiles"].items():
            profile = profile_data.get("profile")
            if profile is None:
                label = profile_name.replace("_", " ").title()
                profile = [label, profile_name]
            profiles.append(profile)
        return profiles

    def get_app_setting(
        self, app: Atspi.Accessible | None, setting_name: str
    ) -> bool | str | int | float | list | dict | None:
        """Returns the specified setting for app, or None if not found."""

        if not app:
            return None

        app_prefs = self._get_app_settings_from_file(AXObject.get_name(app))
        profiles = app_prefs.get("profiles", {})
        profile_prefs = profiles.get(self._profile, {})
        general = profile_prefs.get("general", {})
        app_setting = general.get(setting_name)
        if app_setting is None:
            general = self._get_general_from_file(self._profile)
            app_setting = general.get(setting_name)

        return app_setting

    def load_app_settings(self, script: Script | None) -> None:
        """Load the users application specific settings for an app."""

        if not (script and script.app):
            return

        prefs = self._get_app_settings_from_file(AXObject.get_name(script.app))
        profiles = prefs.get("profiles", {})
        profile_prefs = profiles.get(self._profile, {})

        app_general = profile_prefs.get("general", {})
        app_keybindings = profile_prefs.get("keybindings", {})
        app_pronunciations = profile_prefs.get("pronunciations", {})

        profile_general, profile_pronunciations, profile_keybindings = self._load_profile_settings()
        self._apply_profile_and_app_settings(
            profile_general,
            profile_pronunciations,
            profile_keybindings,
            app_general,
            app_pronunciations,
            app_keybindings,
        )
        self._set_settings_runtime(self._settings)

        manager = pronunciation_dictionary_manager.get_manager()
        manager.set_dictionary({})
        for key, value in self._pronunciations.items():
            if key and value:
                if isinstance(value, list):
                    replacement = value[1] if len(value) > 1 else value[0]
                else:
                    replacement = value
                manager.set_pronunciation(key, replacement)


_manager: SettingsManager = SettingsManager()


def get_manager() -> SettingsManager:
    """Returns the Settings Manager singleton."""

    return _manager
