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

"""Settings manager."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import importlib
import importlib.util
import os
from json import load, dump
from types import ModuleType
from typing import TYPE_CHECKING

from gi.repository import GLib

from . import debug
from . import orca_i18n # pylint: disable=no-name-in-module
from . import settings
from . import pronunciation_dict
from .acss import ACSS
from .ax_object import AXObject
from .keybindings import KeyBinding, KeyBindings

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .input_event import InputEventHandler
    from .script import Script


class SettingsManager:
    """Settings manager"""

    # Settings managed elsewhere or internal implementation details.
    _EXCLUDED_SETTINGS: set[str] = {
        "keyBindingsMap",
        "brailleBindingsMap",
        "speechFactoryModules",
        "speechSystemOverride",
    }

    def __init__(self) -> None:
        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Initializing", True)

        self._profile: str = "default"
        self._prefs_dir: str = ""
        self._settings_file: str = ""
        self._default_settings: dict = {}
        self._settings: dict = {}
        self._pronunciations: dict = {}
        self._keybindings: dict = {}
        self._customized_settings: dict | None = None

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
            if callable(value):
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
            prefs = {
                "startingProfile": settings.profile,
                "profiles": {
                    "default": {
                        "profile": settings.profile,
                    }
                },
                # Legacy keys for backwards compatibility with older Orca versions
                "general": {"startingProfile": settings.profile},
                "pronunciations": {},
                "keybindings": {},
            }
            with open(self._settings_file, "w", encoding="utf-8") as settings_file:
                dump(prefs, settings_file, indent=4)

        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Activated", True)

        starting_profile = self._settings.get("startingProfile", ["Default", "default"])
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
            starting_profile = prefs.get("general", {}).get("startingProfile", ["Default", "default"])
        result["startingProfile"] = starting_profile
        default_profile = starting_profile
        if profile is None:
            profile = default_profile[1]

        profile_settings = prefs["profiles"].get(profile, {}).copy()
        for key, value in profile_settings.items():
            if key == "voices":
                for voice_type, voice_def in value.items():
                    value[voice_type] = ACSS(voice_def)
            if key not in ["startingProfile", "activeProfile"]:
                result[key] = value

        try:
            result["activeProfile"] = profile_settings["profile"]
        except KeyError:
            result["activeProfile"] = default_profile

        return result

    def _get_app_settings_from_file(self, app_name: str) -> dict:
        """Load app-specific settings from file."""

        file_name = os.path.join(self._prefs_dir, "app-settings", f"{app_name}.conf")
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as settings_file:
                prefs = load(settings_file)
        else:
            prefs = {}
        return prefs

    def get_prefs_dir(self) -> str:
        """Returns the preferences directory."""

        return self._prefs_dir

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

        tokens = ["SETTINGS MANAGER: Loading settings for", profile, "profile"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        profile_general = self.get_general_settings(profile) or {}
        profile_pronunciations = self.get_pronunciations(profile) or {}
        profile_keybindings = self.get_keybindings(profile) or {}

        tokens = ["SETTINGS MANAGER: Settings for", profile, "profile loaded"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return profile_general, profile_pronunciations, profile_keybindings

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def _apply_profile_and_app_settings(
        self,
        profile_general: dict,
        profile_pronunciations: dict,
        profile_keybindings: dict,
        app_general: dict | None = None,
        app_pronunciations: dict | None = None,
        app_keybindings: dict | None = None
    ) -> None:
        """Merge profile and app settings into the active settings."""

        msg = "SETTINGS MANAGER: Merging settings."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._settings.update(profile_general)
        self._settings.update(app_general or {})

        self._pronunciations = profile_pronunciations.copy()
        self._pronunciations.update(app_pronunciations or {})

        self._keybindings.update(profile_keybindings)
        self._keybindings.update(app_keybindings or {})

        msg = "SETTINGS MANAGER: Settings merged."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def set_starting_profile(self, profile: list[str] | None = None) -> None:
        """Set the profile that will be used on next start of Orca."""

        if profile is None:
            profile = settings.profile

        with open(self._settings_file, "r+", encoding="utf-8") as settings_file:
            prefs = load(settings_file)
            prefs["startingProfile"] = profile
            # Write legacy keys for backwards compatibility with older Orca versions
            prefs["general"] = {"startingProfile": profile}
            prefs.setdefault("pronunciations", {})
            prefs.setdefault("keybindings", {})
            settings_file.seek(0)
            settings_file.truncate()
            dump(prefs, settings_file, indent=4)

    def get_profile(self) -> str:
        """Returns the active profile."""

        return self._profile

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

    def remove_profile(self, profile: str) -> None:
        """Remove an existing profile."""

        with open(self._settings_file, "r+", encoding="utf-8") as settings_file:
            prefs = load(settings_file)
            if profile not in prefs["profiles"]:
                return

            del prefs["profiles"][profile]
            if not prefs["profiles"]:
                prefs["profiles"]["default"] = {
                    "profile": settings.profile,
                }

            settings_file.seek(0)
            settings_file.truncate()
            dump(prefs, settings_file, indent=4)

    def _set_settings_runtime(self, settings_dict: dict) -> None:
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
        """Return the current keybindings settings."""

        with open(self._settings_file, encoding="utf-8") as settings_file:
            try:
                prefs = load(settings_file)
            except ValueError:
                return {}

        profile_settings = prefs["profiles"].get(profile, {})
        return profile_settings.get("keybindings", {})

    # pylint: disable-next=too-many-locals
    def save_settings(
        self,
        script: Script,
        general: dict,
        pronunciations: dict,
        keybindings: dict
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
                "keybindings": app_keybindings
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

        if pronunciations:
            profile_general["pronunciations"] = dict(pronunciations)
        if keybindings:
            profile_general["keybindings"] = dict(keybindings)

        tokens = ["SETTINGS MANAGER: Saving for profile", self._profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        with open(self._settings_file, "r+", encoding="utf-8") as settings_file:
            prefs = load(settings_file)
            prefs["profiles"][self._profile] = profile_general
            starting_profile = general.get("startingProfile", _profile)
            prefs["startingProfile"] = starting_profile
            # Write legacy keys for backwards compatibility with older Orca versions
            prefs["general"] = {"startingProfile": starting_profile}
            prefs.setdefault("pronunciations", {})
            prefs.setdefault("keybindings", {})
            settings_file.seek(0)
            settings_file.truncate()
            dump(prefs, settings_file, indent=4)

        tokens = ["SETTINGS MANAGER: Settings for", script, "(app:", script.app, ") saved"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    # pylint: disable-next=too-many-locals
    def override_key_bindings(
        self,
        handlers: dict[str, InputEventHandler],
        bindings: KeyBindings,
        enabled_only: bool = True
    ) -> KeyBindings:
        """Override key bindings based on profile settings."""

        # TODO - JD: See about moving this logic, along with any callers, into KeyBindings.
        # Establishing and maintaining grabs should JustWork(tm) as part of the overall
        # keybinding/command process.
        keybindings_settings = self._keybindings
        for handler_string, binding_tuples in keybindings_settings.items():
            handler = handlers.get(handler_string)
            if not handler:
                continue

            if enabled_only:
                if not bindings.has_handler(handler):
                    tokens = ["SETTINGS MANAGER:", handler, "is not in the bindings provided."]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    continue

                if not bindings.has_enabled_handler(handler):
                    tokens = ["SETTINGS MANAGER:", handler.function,
                              "is not enabled. Not overriding."]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    continue

            old_bindings = bindings.get_bindings_for_handler(handler)
            was_enabled: bool = True
            for b in old_bindings:
                tokens = ["SETTINGS MANAGER: Removing old binding for", b]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

                if b.is_enabled() != was_enabled:
                    msg = "SETTINGS MANAGER: Warning, different enabled values found for binding"
                    debug.print_message(debug.LEVEL_INFO, msg, True)

                was_enabled = b.is_enabled()
                bindings.remove(b, True)

            for binding_tuple in binding_tuples:
                keysym, mask, mods, clicks = binding_tuple
                if not keysym:
                    keysym, mask, mods, clicks = "", 0, 0, 0
                else:
                    mask, mods, clicks = int(mask), int(mods), int(clicks)
                new_binding = KeyBinding(keysym, mask, mods, handler, clicks, enabled=was_enabled)
                bindings.add(new_binding)
                tokens = ["SETTINGS MANAGER:", handler, f"is rebound to {binding_tuple}"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return bindings

    def available_profiles(self) -> list:
        """Get available profiles."""

        with open(self._settings_file, encoding="utf-8") as settings_file:
            try:
                prefs = load(settings_file)
            except ValueError:
                return []

        profiles = []
        for _profile_name, profile_data in prefs["profiles"].items():
            profiles.append(profile_data.get("profile"))
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
            profile_general, profile_pronunciations, profile_keybindings,
            app_general, app_pronunciations, app_keybindings
        )
        self._set_settings_runtime(self._settings)

        pronunciation_dict.pronunciation_dict = {}
        for key, value in self._pronunciations.values():
            if key and value:
                pronunciation_dict.set_pronunciation(key, value)

_manager: SettingsManager = SettingsManager()

def get_manager() -> SettingsManager:
    """Returns the Settings Manager singleton."""

    return _manager
