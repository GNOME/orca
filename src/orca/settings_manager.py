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

# pylint: disable=too-few-public-methods

"""Settings manager."""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from types import ModuleType
from typing import TYPE_CHECKING

from gi.repository import GLib

from . import debug
from . import gsettings_registry
from . import orca_i18n  # pylint: disable=no-name-in-module
from . import pronunciation_dictionary_manager
from . import speech_manager
from .ax_object import AXObject

if TYPE_CHECKING:
    from .script import Script


DEFAULT_PROFILE: list[str] = ["Default", "default"]


# TODO - JD: Remove _DeprecatedSettingsStub in Orca v51.
class _DeprecatedSettingsStub(ModuleType):
    """Stub for the removed orca.settings module."""

    _has_warned: bool = False

    def __setattr__(self, name: str, value: object) -> None:
        if not name.startswith("_") and not _DeprecatedSettingsStub._has_warned:
            _DeprecatedSettingsStub._has_warned = True
            msg = (
                "WARNING: orca.settings has been removed. "
                "Please update your orca-customizations.py to remove references to it."
            )
            debug.print_message(debug.LEVEL_SEVERE, msg, True)
        super().__setattr__(name, value)


class SettingsManager:
    """Settings manager"""

    def __init__(self) -> None:
        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Initializing", True)

        self._profile: str = "default"
        self._prefs_dir: str = ""
        self._pronunciations: dict = {}
        self._keybindings: dict = {}
        self._customized_settings: dict | None = None
        self._configuring: bool = False

        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Initialized", True)

    def activate(self) -> None:
        """Activates this manager."""

        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Activating", True)

        self._prefs_dir = os.path.join(GLib.get_user_data_dir(), "orca")  # pylint: disable=no-value-for-parameter

        self._load_customizations()

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

        sounds_dir = os.path.join(orca_dir, "sounds")
        _create_dir(sounds_dir)

        customizations_file = os.path.join(orca_dir, "orca-customizations.py")
        if not os.path.exists(customizations_file):
            os.close(os.open(customizations_file, os.O_CREAT, 0o700))

        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Activated", True)

        self._profile = "default"
        tokens = ["SETTINGS MANAGER: Current profile is", self._profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.set_profile(self._profile)

    def _load_customizations(self) -> None:
        """Load user's orca-customizations.py."""

        if self._customized_settings is not None:
            return

        self._customized_settings = {}
        module_path = os.path.join(self._prefs_dir, "orca-customizations.py")
        tokens = ["SETTINGS MANAGER: Attempt to load orca-customizations"]

        try:
            spec = importlib.util.spec_from_file_location("orca-customizations", module_path)
            if spec is not None and spec.loader is not None:
                if "orca.settings" not in sys.modules:
                    settings_stub = _DeprecatedSettingsStub("orca.settings")
                    sys.modules["orca.settings"] = settings_stub
                    sys.modules["orca"].settings = settings_stub  # type: ignore[attr-defined]
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

        lookup = gsettings_registry.get_registry().layered_lookup
        lang = lookup("voice", "family-lang", "s", voice_type=voice) or ""
        dialect = lookup("voice", "family-dialect", "s", voice_type=voice) or ""
        if dialect and len(dialect) == 2:
            lang = f"{lang}_{dialect.upper()}"
        return lang

    def get_speech_server_factories(self) -> list[ModuleType]:
        """Imports all known SpeechServer factory modules."""

        factories: list[ModuleType] = []
        for module_name in speech_manager.SPEECH_FACTORY_MODULES:
            try:
                module = importlib.import_module(f"orca.{module_name}")
                factories.append(module)
                tokens = ["SETTINGS MANAGER: Valid speech server factory:", module_name]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            except ImportError:
                tokens = ["SETTINGS MANAGER: Invalid speech server factory:", module_name]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return factories

    def _load_profile_settings(self, profile: str | None = None) -> tuple[dict, dict]:
        """Load settings for profile. Returns (pronunciations, keybindings)."""

        if profile is None:
            profile = self._profile

        msg = f"SETTINGS MANAGER: Loading settings for '{profile}' profile"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        profile_pronunciations = self.get_pronunciations(profile) or {}
        profile_keybindings = self.get_keybindings(profile) or {}

        msg = f"SETTINGS MANAGER: Settings for '{profile}' profile loaded"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        return profile_pronunciations, profile_keybindings

    def _apply_profile_and_app_settings(
        self,
        profile_pronunciations: dict,
        profile_keybindings: dict,
        app_pronunciations: dict | None = None,
        app_keybindings: dict | None = None,
    ) -> None:
        """Merge profile and app settings into the active settings."""

        msg = "SETTINGS MANAGER: Merging settings."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._pronunciations = profile_pronunciations.copy()
        self._pronunciations.update(app_pronunciations or {})

        # Clear keybindings first to ensure app-specific unbindings don't persist
        # when switching to an app without those overrides
        self._keybindings.clear()
        self._keybindings.update(profile_keybindings)
        self._keybindings.update(app_keybindings or {})

        msg = "SETTINGS MANAGER: Settings merged."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def get_profile(self) -> str:
        """Returns the active profile."""

        return self._profile

    def set_profile(self, profile: str = "default", update_locale: bool = False) -> None:
        """Set a specific profile as the active one and update settings accordingly."""

        tokens = ["SETTINGS MANAGER: Setting profile to:", profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        old_voice_locale = self.get_voice_locale("default")
        self._profile = profile
        pronunciations, keybindings = self._load_profile_settings(profile)
        self._apply_profile_and_app_settings(pronunciations, keybindings)

        if not update_locale:
            return

        new_voice_locale = self.get_voice_locale("default")
        if old_voice_locale != new_voice_locale:
            orca_i18n.setLocaleForNames(new_voice_locale)
            orca_i18n.setLocaleForMessages(new_voice_locale)
            orca_i18n.setLocaleForGUI(new_voice_locale)

        tokens = ["SETTINGS MANAGER: Profile set to:", profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def get_pronunciations(self, profile: str = "default") -> dict:
        """Return the current pronunciations settings."""

        return gsettings_registry.get_registry().get_pronunciations(profile)

    def get_keybindings(self, profile: str = "default") -> dict:
        """Return the keybindings from the profile settings file."""

        return gsettings_registry.get_registry().get_keybindings(profile)

    def get_active_keybindings(self) -> dict:
        """Return the active keybindings (merged profile + app settings)."""

        return self._keybindings

    def load_app_settings(self, script: Script | None) -> None:
        """Load the users application specific settings for an app."""

        if not (script and script.app):
            return

        app_name = AXObject.get_name(script.app)
        registry = gsettings_registry.get_registry()
        app_pronunciations = registry.get_pronunciations(self._profile, app_name)
        app_keybindings = registry.get_keybindings(self._profile, app_name)

        profile_pronunciations, profile_keybindings = self._load_profile_settings()
        self._apply_profile_and_app_settings(
            profile_pronunciations,
            profile_keybindings,
            app_pronunciations,
            app_keybindings,
        )

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
