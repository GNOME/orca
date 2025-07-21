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

"""Settings backend manager."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import importlib
import os
from gi.repository import Gio, GLib

from . import debug
from . import orca_i18n # pylint: disable=no-name-in-module
from . import settings
from . import pronunciation_dict
from .acss import ACSS
from .ax_object import AXObject
from .keybindings import KeyBinding

try:
    _PROXY = Gio.DBusProxy.new_for_bus_sync(
        Gio.BusType.SESSION,
        Gio.DBusProxyFlags.NONE,
        None,
        'org.a11y.Bus',
        '/org/a11y/bus',
        'org.freedesktop.DBus.Properties',
        None)
except Exception:
    _PROXY = None


class SettingsManager:
    """Settings backend manager"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if '__instance' not in vars(cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self, backend='json'):
        """Initialize a SettingsManager Object.
        If backend isn't defined then uses default backend, in this
        case json-backend.
        backend parameter can use the follow values:
        backend='json'
        """

        debug.print_message(debug.LEVEL_INFO, 'SETTINGS MANAGER: Initializing', True)

        self.backend_module = None
        self._backend = None
        self.profile = None
        self.backend_name = backend
        self._prefs_dir = None

        # Dictionaries for store the default values
        # The keys and values are defined at orca.settings
        #
        self.default_general = {}
        self.default_pronunciations = {}
        self.default_keybindings = {}

        # Dictionaries that store the key:value pairs which values are
        # different from the current profile and the default ones
        #
        self.profile_general = {}
        self.profile_pronunciations = {}
        self.profile_keybindings = {}

        # Dictionaries that store the current settings.
        # They are result to overwrite the default values with
        # the ones from the current active profile
        self.general = {}
        self.pronunciations = {}
        self.keybindings = {}

        self._runtime_settings = {}

        self._active_app = ""
        self._app_general = {}
        self._appPronunciations = {}
        self._appKeybindings = {}

        if not self._load_backend():
            raise Exception('SettingsManager._load_backend failed.')

        self.customized_settings = {}
        self._customization_completed = False

        # For handling the currently-"classic" application settings
        self.settingsPackages = ["app-settings"]

        debug.print_message(debug.LEVEL_INFO, 'SETTINGS MANAGER: Initialized', True)

    def get_overridden_settings_for_debugging(self):
        """Returns overridden settings for the purpose of debugging."""

        changed = {}
        for key, value in self.default_general.items():
            if value != self.general.get(key) and key not in self.customized_settings:
                changed[key] = self.general.get(key)
        for key, value in self._app_general.items():
            if value != self.general.get(key):
                changed[key] = self.general.get(key)
        return changed

    def activate(self, prefsDir=None, customSettings={}):
        """Activates this manager."""

        debug.print_message(debug.LEVEL_INFO, 'SETTINGS MANAGER: Activating', True)

        self.customized_settings.update(customSettings)
        self._prefs_dir = prefsDir \
            or os.path.join(GLib.get_user_data_dir(), "orca")

        # Load the backend and the default values
        self._backend = self.backend_module.Backend(self._prefs_dir)
        self._set_default_general()
        self._set_default_pronunciations()
        self._set_default_keybindings()
        self.general = self.default_general.copy()
        if not self.is_first_start():
            self.general.update(self._backend.getGeneral())
        self.pronunciations = self.default_pronunciations.copy()
        self.keybindings = self.default_keybindings.copy()

        # If this is the first time we launch Orca, there is no user settings
        # yet, so we need to create the user config directories and store the
        # initial default settings
        #
        self._create_defaults()

        debug.print_message(debug.LEVEL_INFO, 'SETTINGS MANAGER: Activated', True)

        # Set the active profile and load its stored settings
        tokens = ["SETTINGS MANAGER: Current profile is", self.profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self.profile is None:
            self.profile = self.general.get('startingProfile')[1]
            tokens = ["SETTINGS MANAGER: Current profile is now", self.profile]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.set_profile(self.profile)

    def _load_backend(self):
        """Loads backend for managing user settings"""

        try:
            backend = f'.backends.{self.backend_name}_backend'
            self.backend_module = importlib.import_module(backend, 'orca')
            return True
        except Exception:
            return False

    def _create_defaults(self):
        """Creates the initial structure for storing the default settings."""

        def _create_dir(dirName):
            if not os.path.isdir(dirName):
                os.makedirs(dirName)

        # Set up the user's preferences directory
        # ($XDG_DATA_HOME/orca by default).
        #
        orca_dir = self._prefs_dir
        _create_dir(orca_dir)

        # Set up $XDG_DATA_HOME/orca/orca-scripts as a Python package
        #
        orca_script_dir = os.path.join(orca_dir, "orca-scripts")
        _create_dir(orca_script_dir)
        initFile = os.path.join(orca_script_dir, "__init__.py")
        if not os.path.exists(initFile):
            os.close(os.open(initFile, os.O_CREAT, 0o700))

        orcaSettingsDir = os.path.join(orca_dir, "app-settings")
        _create_dir(orcaSettingsDir)

        orcaSoundsDir = os.path.join(orca_dir, "sounds")
        _create_dir(orcaSoundsDir)

        # Set up $XDG_DATA_HOME/orca/orca-customizations.py empty file and
        # define orca_dir as a Python package.
        initFile = os.path.join(orca_dir, "__init__.py")
        if not os.path.exists(initFile):
            os.close(os.open(initFile, os.O_CREAT, 0o700))

        userCustomFile = os.path.join(orca_dir, "orca-customizations.py")
        if not os.path.exists(userCustomFile):
            os.close(os.open(userCustomFile, os.O_CREAT, 0o700))

        if self.is_first_start():
            self._backend.saveDefaultSettings(self.default_general,
                                              self.default_pronunciations,
                                              self.default_keybindings)

    def _set_default_pronunciations(self):
        """Get the pronunciations by default from orca.settings"""
        self.default_pronunciations = {}

    def _set_default_keybindings(self):
        """Get the keybindings by default from orca.settings"""
        self.default_keybindings = {}

    def _set_default_general(self):
        """Get the general settings by default from orca.settings"""
        self._get_customized_settings()
        self.default_general = {}
        for key in settings.userCustomizableSettings:
            value = self.customized_settings.get(key)
            if value is None:
                try:
                    value = getattr(settings, key)
                except Exception:
                    pass
            self.default_general[key] = value

    def _get_customized_settings(self):
        if self._customization_completed:
            return self.customized_settings

        originalSettings = {}
        for key, value in settings.__dict__.items():
            originalSettings[key] = value

        self._customization_completed = self._load_user_customizations()

        for key, value in originalSettings.items():
            customValue = settings.__dict__.get(key)
            if value != customValue:
                self.customized_settings[key] = customValue

    def _load_user_customizations(self):
        """Attempt to load the user's orca-customizations. Returns a boolean
        indicating our success at doing so, where success is measured by the
        likelihood that the results won't be different if we keep trying."""

        success = False
        pathList = [self._prefs_dir]
        tokens = ["SETTINGS MANAGER: Attempt to load orca-customizations"]
        module_path = pathList[0] + "/orca-customizations.py"

        try:
            spec = importlib.util.spec_from_file_location("orca-customizations", module_path)
            if spec is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                tokens.extend(["from", module_path, "succeeded."])
                success = True
            else:
                tokens.extend(["from", module_path, "failed. Spec not found."])
        except FileNotFoundError:
            tokens.extend(["from", module_path, "failed. File not found."])
        except Exception as error:
            # Treat this failure as a "success" so that we don't stomp on the existing file.
            success = True
            tokens.extend(["failed due to:", error, ". Not loading customizations."])

        debug.print_tokens(debug.LEVEL_ALL, tokens, True)
        return success

    def get_prefs_dir(self):
        return self._prefs_dir

    def set_setting(self, name, value):
        """Updates the named setting to value."""

        self._runtime_settings[name] = value
        self._set_settings_runtime({name:value})

    def get_setting(self, settingName):
        return getattr(settings, settingName, None)

    def get_voice_locale(self, voice='default'):
        voices = self.get_setting('voices')
        v = ACSS(voices.get(voice, {}))
        lang = v.getLocale()
        dialect = v.getDialect()
        if dialect and len(str(dialect)) == 2:
            lang = f"{lang}_{dialect.upper()}"
        return lang

    def get_speech_server_factories(self):
        """Imports all known SpeechServer factory modules."""

        factories = []
        for module_name in self.get_setting('speechFactoryModules'):
            try:
                module = importlib.import_module(f'orca.{module_name}')
                factories.append(module)
                tokens = ["SETTINGS MANAGER: Valid speech server factory:", module_name]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            except Exception:
                tokens = ["SETTINGS MANAGER: Invalid speech server factory:", module_name]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return factories

    def _load_profile_settings(self, profile=None):
        """Get from the active backend all the settings for the current
        profile and store them in the object's attributes.
        A profile can be passed as a parameter. This could be useful for
        change from one profile to another."""

        tokens = ["SETTINGS MANAGER: Loading settings for", profile, "profile"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if profile is None:
            profile = self.profile
        self.profile_general = self.get_general_settings(profile) or {}
        self.profile_pronunciations = self.get_pronunciations(profile) or {}
        self.profile_keybindings = self.get_keybindings(profile) or {}

        tokens = ["SETTINGS MANAGER: Settings for", profile, "profile loaded"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def _merge_settings(self):
        """Update the changed values on the profile settings
        over the current and active settings"""

        msg = 'SETTINGS MANAGER: Merging settings.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.profile_general.update(self._app_general)
        self.profile_pronunciations.update(self._appPronunciations)
        self.profile_keybindings.update(self._appKeybindings)

        self.general.update(self.profile_general)
        self.pronunciations.update(self.profile_pronunciations)
        self.keybindings.update(self.profile_keybindings)

        msg = 'SETTINGS MANAGER: Settings merged.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _enable_accessibility(self):
        """Enables the GNOME accessibility flag.  Users need to log out and
        then back in for this to take effect.

        Returns True if an action was taken (i.e., accessibility was not
        set prior to this call).
        """

        alreadyEnabled = self.is_accessibility_enabled()
        if not alreadyEnabled:
            self.set_accessibility(True)

        return not alreadyEnabled

    def is_accessibility_enabled(self):
        msg = 'SETTINGS MANAGER: Checking if accessibility is enabled.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

        msg = 'SETTINGS MANAGER: Accessibility enabled: '
        if not _PROXY:
            rv = False
            msg += 'Error (no proxy)'
        else:
            rv = _PROXY.Get('(ss)', 'org.a11y.Status', 'IsEnabled')
            msg += str(rv)

        debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def set_accessibility(self, enable):
        msg = f'SETTINGS MANAGER: Attempting to set accessibility to {enable}.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if not _PROXY:
            msg = 'SETTINGS MANAGER: Error (no proxy)'
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        vEnable = GLib.Variant('b', enable)
        _PROXY.Set('(ssv)', 'org.a11y.Status', 'IsEnabled', vEnable)

        msg = f'SETTINGS MANAGER: Finished setting accessibility to {enable}.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def is_screen_reader_service_enabled(self):
        """Returns True if the screen reader service is enabled. Note that
        this does not necessarily mean that Orca (or any other screen reader)
        is running at the moment."""

        msg = 'SETTINGS MANAGER: Is screen reader service enabled? '

        if not _PROXY:
            rv = False
            msg += 'Error (no proxy)'
        else:
            rv = _PROXY.Get('(ss)', 'org.a11y.Status', 'ScreenReaderEnabled')
            msg += str(rv)

        debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def set_starting_profile(self, profile=None):
        if profile is None:
            profile = settings.profile
        self._backend._setProfileKey('startingProfile', profile)

    def get_profile(self):
        return self.profile

    def set_profile(self, profile='default', updateLocale=False):
        """Set a specific profile as the active one.
        Also the settings from that profile will be loading
        and updated the current settings with them."""

        tokens = ["SETTINGS MANAGER: Setting profile to:", profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        oldVoiceLocale = self.get_voice_locale('default')
        self.profile = profile
        self._load_profile_settings(profile)
        self._merge_settings()
        self._set_settings_runtime(self.general)

        if not updateLocale:
            return

        newVoiceLocale = self.get_voice_locale('default')
        if oldVoiceLocale != newVoiceLocale:
            orca_i18n.setLocaleForNames(newVoiceLocale)
            orca_i18n.setLocaleForMessages(newVoiceLocale)
            orca_i18n.setLocaleForGUI(newVoiceLocale)

        tokens = ["SETTINGS MANAGER: Profile set to:", profile]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def remove_profile(self, profile):
        self._backend.remove_profile(profile)

    def _set_settings_runtime(self, settingsDict):
        msg = 'SETTINGS MANAGER: Setting runtime settings.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

        for key, value in settingsDict.items():
            setattr(settings, str(key), value)
        self._get_customized_settings()
        for key, value in self.customized_settings.items():
            setattr(settings, str(key), value)

        msg = 'SETTINGS MANAGER: Runtime settings set.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _set_pronunciations_runtime(self, pronunciationsDict):
        pronunciation_dict.pronunciation_dict = {}
        for key, value in pronunciationsDict.values():
            if key and value:
                pronunciation_dict.set_pronunciation(key, value)

    def get_general_settings(self, profile='default'):
        """Return the current general settings.
        Those settings comes from updating the default settings
        with the profiles' ones"""
        return self._backend.getGeneral(profile)

    def get_pronunciations(self, profile='default'):
        """Return the current pronunciations settings.
        Those settings comes from updating the default settings
        with the profiles' ones"""
        return self._backend.get_pronunciations(profile)

    def get_keybindings(self, profile='default'):
        """Return the current keybindings settings.
        Those settings comes from updating the default settings
        with the profiles' ones"""
        return self._backend.get_keybindings(profile)

    def _set_profile_general(self, general):
        """Set the changed general settings from the defaults' ones
        as the profile's."""

        msg = 'SETTINGS MANAGER: Setting general settings for profile'
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.profile_general = {}

        for key, value in general.items():
            if key in ['startingProfile', 'activeProfile']:
                continue
            elif key == 'profile':
                self.profile_general[key] = value
            elif value != self.default_general.get(key):
                self.profile_general[key] = value
            elif self.general.get(key) != value:
                self.profile_general[key] = value

        msg = 'SETTINGS MANAGER: General settings for profile set'
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _set_profile_pronunciations(self, pronunciations):
        """Set the changed pronunciations settings from the defaults' ones
        as the profile's."""

        msg = 'SETTINGS MANAGER: Setting pronunciation settings for profile.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.profile_pronunciations = self.default_pronunciations.copy()
        self.profile_pronunciations.update(pronunciations)

        msg = 'SETTINGS MANAGER: Pronunciation settings for profile set.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _set_profile_keybindings(self, keybindings):
        """Set the changed keybindings settings from the defaults' ones
        as the profile's."""

        msg = 'SETTINGS MANAGER: Setting keybindings settings for profile.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.profile_keybindings = self.default_keybindings.copy()
        self.profile_keybindings.update(keybindings)

        msg = 'SETTINGS MANAGER: Keybindings settings for profile set.'
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _save_app_settings(self, appName, general, pronunciations, keybindings):
        appGeneral = {}
        profile_general = self.get_general_settings(self.profile)
        for key, value in general.items():
            if value != profile_general.get(key):
                appGeneral[key] = value

        appPronunciations = {}
        profile_pronunciations = self.get_pronunciations(self.profile)
        for key, value in pronunciations.items():
            if value != profile_pronunciations.get(key):
                appPronunciations[key] = value

        appKeybindings = {}
        profile_keybindings = self.get_keybindings(self.profile)
        for key, value in keybindings.items():
            if value != profile_keybindings.get(key):
                appKeybindings[key] = value

        self._backend.saveAppSettings(appName,
                                      self.profile,
                                      appGeneral,
                                      appPronunciations,
                                      appKeybindings)

    def get_runtime_settings(self):
        """Returns a dictionary with settings toggled at runtime."""

        return self._runtime_settings

    def save_settings(self, script, general, pronunciations, keybindings):
        """Save the settings provided for the script provided."""

        tokens = ["SETTINGS MANAGER: Saving settings for", script, "(app:", script.app, ")"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        app = script.app
        if app:
            self._save_app_settings(AXObject.get_name(app), general, pronunciations, keybindings)
            return

        # Assign current profile
        _profile = general.get('profile', settings.profile)
        currentProfile = _profile[1]

        self.profile = currentProfile

        # Elements that need to stay updated in main configuration.
        self.default_general['startingProfile'] = general.get('startingProfile',
                                                              _profile)

        self._set_profile_general(general)
        self._set_profile_pronunciations(pronunciations)
        self._set_profile_keybindings(keybindings)

        tokens = ["SETTINGS MANAGER: Saving for backend", self._backend]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._backend.saveProfileSettings(self.profile,
                                          self.profile_general,
                                          self.profile_pronunciations,
                                          self.profile_keybindings)

        tokens = ["SETTINGS MANAGER: Settings for", script, "(app:", script.app, ") saved"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._enable_accessibility()

    def _adjust_binding_tuple_values(self, bindingTuple):
        """Converts the values of bindingTuple into KeyBinding-ready values."""

        keysym, mask, mods, clicks = bindingTuple
        if not keysym:
            bindingTuple = ('', 0, 0, 0)
        else:
            bindingTuple = (keysym, int(mask), int(mods), int(clicks))

        return bindingTuple

    def override_key_bindings(self, handlers, bindings, enabled_only=True):
        # TODO - JD: See about moving this logic, along with any callers, into KeyBindings.
        # Establishing and maintaining grabs should JustWork(tm) as part of the overall
        # keybinding/command process.
        keybindingsSettings = self.profile_keybindings
        for handlerString, bindingTuples in keybindingsSettings.items():
            handler = handlers.get(handlerString)
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

            oldBindings = bindings.get_bindings_for_handler(handler)
            wasEnabled = None
            for b in oldBindings:
                tokens = ["SETTINGS MANAGER: Removing old binding for", b]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

                if wasEnabled is not None and b.is_enabled() != wasEnabled:
                    msg = "SETTINGS MANAGER: Warning, different enabled values found for binding"
                    debug.print_message(debug.LEVEL_INFO, msg, True)

                wasEnabled = b.is_enabled()
                bindings.remove(b, True)

            for bindingTuple in bindingTuples:
                bindingTuple = self._adjust_binding_tuple_values(bindingTuple)
                keysym, mask, mods, clicks = bindingTuple
                newBinding = KeyBinding(keysym, mask, mods, handler, clicks, enabled=wasEnabled)
                bindings.add(newBinding)
                tokens = ["SETTINGS MANAGER:", handler, f"is rebound to {bindingTuple}"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return bindings

    def is_first_start(self):
        """Check if the firstStart key is True or false"""
        return self._backend.is_first_start()

    def available_profiles(self):
        """Get available profiles from active backend"""

        return self._backend.available_profiles()

    def get_app_setting(self, app, settingName, fallbackOnDefault=True):
        """Returns the specified setting for app."""

        if not app:
            return None

        appPrefs = self._backend.get_app_settings(AXObject.get_name(app))
        profiles = appPrefs.get('profiles', {})
        profilePrefs = profiles.get(self.profile, {})
        general = profilePrefs.get('general', {})
        appSetting = general.get(settingName)
        if appSetting is None and fallbackOnDefault:
            general = self._backend.getGeneral(self.profile)
            appSetting = general.get(settingName)

        return appSetting

    def load_app_settings(self, script):
        """Load the users application specific settings for an app."""

        if not (script and script.app):
            return

        self._runtime_settings = {}

        for key in self._appPronunciations.keys():
            self.pronunciations.pop(key)

        prefs = self._backend.get_app_settings(AXObject.get_name(script.app))
        profiles = prefs.get('profiles', {})
        profilePrefs = profiles.get(self.profile, {})

        self._app_general = profilePrefs.get('general', {})
        self._appKeybindings = profilePrefs.get('keybindings', {})
        self._appPronunciations = profilePrefs.get('pronunciations', {})
        self._active_app = AXObject.get_name(script.app)

        self._load_profile_settings()
        self._merge_settings()
        self._set_settings_runtime(self.general)
        self._set_pronunciations_runtime(self.pronunciations)

_manager = SettingsManager()

def get_manager():
    """Returns the Settings Manager singleton."""
    return _manager
