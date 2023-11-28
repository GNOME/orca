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

"""Settings manager module. This will load/save user settings from a 
defined settings backend."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import importlib
import os
from gi.repository import Gio, GLib

from . import debug
from . import orca_i18n
from . import settings
from . import pronunciation_dict
from .acss import ACSS
from .ax_object import AXObject
from .keybindings import KeyBinding

try:
    _proxy = Gio.DBusProxy.new_for_bus_sync(
        Gio.BusType.SESSION,
        Gio.DBusProxyFlags.NONE,
        None,
        'org.a11y.Bus',
        '/org/a11y/bus',
        'org.freedesktop.DBus.Properties',
        None)
except Exception:
    _proxy = None


class SettingsManager(object):
    """Settings backend manager. This class manages orca user's settings
    using different backends"""
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

        debug.printMessage(debug.LEVEL_INFO, 'SETTINGS MANAGER: Initializing', True)

        self.backendModule = None
        self._backend = None
        self.profile = None
        self.backendName = backend
        self._prefsDir = None

        # Dictionaries for store the default values
        # The keys and values are defined at orca.settings
        #
        self.defaultGeneral = {}
        self.defaultPronunciations = {}
        self.defaultKeybindings = {}

        # Dictionaries that store the key:value pairs which values are
        # different from the current profile and the default ones
        #
        self.profileGeneral = {}
        self.profilePronunciations = {}
        self.profileKeybindings = {}

        # Dictionaries that store the current settings.
        # They are result to overwrite the default values with
        # the ones from the current active profile
        self.general = {}
        self.pronunciations = {}
        self.keybindings = {}

        self._activeApp = ""
        self._appGeneral = {}
        self._appPronunciations = {}
        self._appKeybindings = {}

        if not self._loadBackend():
            raise Exception('SettingsManager._loadBackend failed.')

        self.customizedSettings = {}
        self._customizationCompleted = False

        # For handling the currently-"classic" application settings
        self.settingsPackages = ["app-settings"]

        debug.printMessage(debug.LEVEL_INFO, 'SETTINGS MANAGER: Initialized', True)

    def activate(self, prefsDir=None, customSettings={}):
        debug.printMessage(debug.LEVEL_INFO, 'SETTINGS MANAGER: Activating', True)

        self.customizedSettings.update(customSettings)
        self._prefsDir = prefsDir \
            or os.path.join(GLib.get_user_data_dir(), "orca")

        # Load the backend and the default values
        self._backend = self.backendModule.Backend(self._prefsDir)
        self._setDefaultGeneral()
        self._setDefaultPronunciations()
        self._setDefaultKeybindings()
        self.general = self.defaultGeneral.copy()
        if not self.isFirstStart():
            self.general.update(self._backend.getGeneral())
        self.pronunciations = self.defaultPronunciations.copy()
        self.keybindings = self.defaultKeybindings.copy()

        # If this is the first time we launch Orca, there is no user settings
        # yet, so we need to create the user config directories and store the
        # initial default settings
        #
        self._createDefaults()

        debug.printMessage(debug.LEVEL_INFO, 'SETTINGS MANAGER: Activated', True)

        # Set the active profile and load its stored settings
        tokens = ["SETTINGS MANAGER: Current profile is", self.profile]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if self.profile is None:
            self.profile = self.general.get('startingProfile')[1]
            tokens = ["SETTINGS MANAGER: Current profile is now", self.profile]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        self.setProfile(self.profile)

    def _loadBackend(self):
        """Load specific backend for manage user settings"""

        try:
            backend = f'.backends.{self.backendName}_backend'
            self.backendModule = importlib.import_module(backend, 'orca')
            return True
        except Exception:
            return False

    def _createDefaults(self):
        """Let the active backend to create the initial structure
        for storing the settings and save the default ones from
        orca.settings"""
        def _createDir(dirName):
            if not os.path.isdir(dirName):
                os.makedirs(dirName)

        # Set up the user's preferences directory
        # ($XDG_DATA_HOME/orca by default).
        #
        orcaDir = self._prefsDir
        _createDir(orcaDir)

        # Set up $XDG_DATA_HOME/orca/orca-scripts as a Python package
        #
        orcaScriptDir = os.path.join(orcaDir, "orca-scripts")
        _createDir(orcaScriptDir)
        initFile = os.path.join(orcaScriptDir, "__init__.py")
        if not os.path.exists(initFile):
            os.close(os.open(initFile, os.O_CREAT, 0o700))

        orcaSettingsDir = os.path.join(orcaDir, "app-settings")
        _createDir(orcaSettingsDir)

        orcaSoundsDir = os.path.join(orcaDir, "sounds")
        _createDir(orcaSoundsDir)

        # Set up $XDG_DATA_HOME/orca/orca-customizations.py empty file and
        # define orcaDir as a Python package.
        initFile = os.path.join(orcaDir, "__init__.py")
        if not os.path.exists(initFile):
            os.close(os.open(initFile, os.O_CREAT, 0o700))

        userCustomFile = os.path.join(orcaDir, "orca-customizations.py")
        if not os.path.exists(userCustomFile):
            os.close(os.open(userCustomFile, os.O_CREAT, 0o700))

        if self.isFirstStart():
            self._backend.saveDefaultSettings(self.defaultGeneral,
                                              self.defaultPronunciations,
                                              self.defaultKeybindings)

    def _setDefaultPronunciations(self):
        """Get the pronunciations by default from orca.settings"""
        self.defaultPronunciations = {}

    def _setDefaultKeybindings(self):
        """Get the keybindings by default from orca.settings"""
        self.defaultKeybindings = {}

    def _setDefaultGeneral(self):
        """Get the general settings by default from orca.settings"""
        self._getCustomizedSettings()
        self.defaultGeneral = {}
        for key in settings.userCustomizableSettings:
            value = self.customizedSettings.get(key)
            if value is None:
                try:
                    value = getattr(settings, key)
                except Exception:
                    pass
            self.defaultGeneral[key] = value

    def _getCustomizedSettings(self):
        if self._customizationCompleted:
            return self.customizedSettings

        originalSettings = {}
        for key, value in settings.__dict__.items():
            originalSettings[key] = value

        self._customizationCompleted = self._loadUserCustomizations()

        for key, value in originalSettings.items():
            customValue = settings.__dict__.get(key)
            if value != customValue:
                self.customizedSettings[key] = customValue

    def _loadUserCustomizations(self):
        """Attempt to load the user's orca-customizations. Returns a boolean
        indicating our success at doing so, where success is measured by the
        likelihood that the results won't be different if we keep trying."""

        success = False
        pathList = [self._prefsDir]
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

        debug.printTokens(debug.LEVEL_ALL, tokens, True)
        return success

    def getPrefsDir(self):
        return self._prefsDir

    def setSetting(self, settingName, settingValue):
        self._setSettingsRuntime({settingName:settingValue})

    def getSetting(self, settingName):
        return getattr(settings, settingName, None)

    def getVoiceLocale(self, voice='default'):
        voices = self.getSetting('voices')
        v = ACSS(voices.get(voice, {}))
        lang = v.getLocale()
        dialect = v.getDialect()
        if dialect and len(str(dialect)) == 2:
            lang = f"{lang}_{dialect.upper()}"
        return lang

    def getSpeechServerFactories(self):
        """Imports all known SpeechServer factory modules."""

        factories = []
        for moduleName in self.getSetting('speechFactoryModules'):
            try:
                module = importlib.import_module(f'orca.{moduleName}')
                factories.append(module)
                tokens = ["SETTINGS MANAGER: Valid speech server factory:", moduleName]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
            except Exception:
                tokens = ["SETTINGS MANAGER: Invalid speech server factory:", moduleName]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return factories

    def _loadProfileSettings(self, profile=None):
        """Get from the active backend all the settings for the current
        profile and store them in the object's attributes.
        A profile can be passed as a parameter. This could be useful for
        change from one profile to another."""

        tokens = ["SETTINGS MANAGER: Loading settings for", profile, "profile"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if profile is None:
            profile = self.profile
        self.profileGeneral = self.getGeneralSettings(profile) or {}
        self.profilePronunciations = self.getPronunciations(profile) or {}
        self.profileKeybindings = self.getKeybindings(profile) or {}

        tokens = ["SETTINGS MANAGER: Settings for", profile, "profile loaded"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

    def _mergeSettings(self):
        """Update the changed values on the profile settings
        over the current and active settings"""

        msg = 'SETTINGS MANAGER: Merging settings.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        self.profileGeneral.update(self._appGeneral)
        self.profilePronunciations.update(self._appPronunciations)
        self.profileKeybindings.update(self._appKeybindings)

        self.general.update(self.profileGeneral)
        self.pronunciations.update(self.profilePronunciations)
        self.keybindings.update(self.profileKeybindings)

        msg = 'SETTINGS MANAGER: Settings merged.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _enableAccessibility(self):
        """Enables the GNOME accessibility flag.  Users need to log out and
        then back in for this to take effect.

        Returns True if an action was taken (i.e., accessibility was not
        set prior to this call).
        """

        alreadyEnabled = self.isAccessibilityEnabled()
        if not alreadyEnabled:
            self.setAccessibility(True)

        return not alreadyEnabled

    def isAccessibilityEnabled(self):
        msg = 'SETTINGS MANAGER: Checking if accessibility is enabled.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        msg = 'SETTINGS MANAGER: Accessibility enabled: '
        if not _proxy:
            rv = False
            msg += 'Error (no proxy)'
        else:
            rv = _proxy.Get('(ss)', 'org.a11y.Status', 'IsEnabled')
            msg += str(rv)

        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return rv

    def setAccessibility(self, enable):
        msg = f'SETTINGS MANAGER: Attempting to set accessibility to {enable}.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        if not _proxy:
            msg = 'SETTINGS MANAGER: Error (no proxy)'
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        vEnable = GLib.Variant('b', enable)
        _proxy.Set('(ssv)', 'org.a11y.Status', 'IsEnabled', vEnable)

        msg = f'SETTINGS MANAGER: Finished setting accessibility to {enable}.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def isScreenReaderServiceEnabled(self):
        """Returns True if the screen reader service is enabled. Note that
        this does not necessarily mean that Orca (or any other screen reader)
        is running at the moment."""

        msg = 'SETTINGS MANAGER: Is screen reader service enabled? '

        if not _proxy:
            rv = False
            msg += 'Error (no proxy)'
        else:
            rv = _proxy.Get('(ss)', 'org.a11y.Status', 'ScreenReaderEnabled')
            msg += str(rv)

        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return rv

    def setStartingProfile(self, profile=None):
        if profile is None:
            profile = settings.profile
        self._backend._setProfileKey('startingProfile', profile)

    def getProfile(self):
        return self.profile

    def setProfile(self, profile='default', updateLocale=False):
        """Set a specific profile as the active one.
        Also the settings from that profile will be loading
        and updated the current settings with them."""

        tokens = ["SETTINGS MANAGER: Setting profile to:", profile]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        oldVoiceLocale = self.getVoiceLocale('default')
        self.profile = profile
        self._loadProfileSettings(profile)
        self._mergeSettings()
        self._setSettingsRuntime(self.general)

        if not updateLocale:
            return

        newVoiceLocale = self.getVoiceLocale('default')
        if oldVoiceLocale != newVoiceLocale:
            orca_i18n.setLocaleForNames(newVoiceLocale)
            orca_i18n.setLocaleForMessages(newVoiceLocale)
            orca_i18n.setLocaleForGUI(newVoiceLocale)

        tokens = ["SETTINGS MANAGER: Profile set to:", profile]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

    def removeProfile(self, profile):
        self._backend.removeProfile(profile)

    def _setSettingsRuntime(self, settingsDict):
        msg = 'SETTINGS MANAGER: Setting runtime settings.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        for key, value in settingsDict.items():
            setattr(settings, str(key), value)
        self._getCustomizedSettings()
        for key, value in self.customizedSettings.items():
            setattr(settings, str(key), value)

        msg = 'SETTINGS MANAGER: Runtime settings set.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setPronunciationsRuntime(self, pronunciationsDict):
        pronunciation_dict.pronunciation_dict = {}
        for key, value in pronunciationsDict.values():
            if key and value:
                pronunciation_dict.setPronunciation(key, value)

    def getGeneralSettings(self, profile='default'):
        """Return the current general settings.
        Those settings comes from updating the default settings
        with the profiles' ones"""
        return self._backend.getGeneral(profile)

    def getPronunciations(self, profile='default'):
        """Return the current pronunciations settings.
        Those settings comes from updating the default settings
        with the profiles' ones"""
        return self._backend.getPronunciations(profile)

    def getKeybindings(self, profile='default'):
        """Return the current keybindings settings.
        Those settings comes from updating the default settings
        with the profiles' ones"""
        return self._backend.getKeybindings(profile)

    def _setProfileGeneral(self, general):
        """Set the changed general settings from the defaults' ones
        as the profile's."""

        msg = 'SETTINGS MANAGER: Setting general settings for profile'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        self.profileGeneral = {}

        for key, value in general.items():
            if key in ['startingProfile', 'activeProfile']:
                continue
            elif key == 'profile':
                self.profileGeneral[key] = value
            elif value != self.defaultGeneral.get(key):
                self.profileGeneral[key] = value
            elif self.general.get(key) != value:
                self.profileGeneral[key] = value

        msg = 'SETTINGS MANAGER: General settings for profile set'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setProfilePronunciations(self, pronunciations):
        """Set the changed pronunciations settings from the defaults' ones
        as the profile's."""

        msg = 'SETTINGS MANAGER: Setting pronunciation settings for profile.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        self.profilePronunciations = self.defaultPronunciations.copy()
        self.profilePronunciations.update(pronunciations)

        msg = 'SETTINGS MANAGER: Pronunciation settings for profile set.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setProfileKeybindings(self, keybindings):
        """Set the changed keybindings settings from the defaults' ones
        as the profile's."""

        msg = 'SETTINGS MANAGER: Setting keybindings settings for profile.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        self.profileKeybindings = self.defaultKeybindings.copy()
        self.profileKeybindings.update(keybindings)

        msg = 'SETTINGS MANAGER: Keybindings settings for profile set.'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _saveAppSettings(self, appName, general, pronunciations, keybindings):
        appGeneral = {}
        profileGeneral = self.getGeneralSettings(self.profile)
        for key, value in general.items():
            if value != profileGeneral.get(key):
                appGeneral[key] = value

        appPronunciations = {}
        profilePronunciations = self.getPronunciations(self.profile)
        for key, value in pronunciations.items():
            if value != profilePronunciations.get(key):
                appPronunciations[key] = value

        appKeybindings = {}
        profileKeybindings = self.getKeybindings(self.profile)
        for key, value in keybindings.items():
            if value != profileKeybindings.get(key):
                appKeybindings[key] = value

        self._backend.saveAppSettings(appName,
                                      self.profile,
                                      appGeneral,
                                      appPronunciations,
                                      appKeybindings)

    def saveSettings(self, script, general, pronunciations, keybindings):
        """Save the settings provided for the script provided."""

        tokens = ["SETTINGS MANAGER: Saving settings for", script, "(app:", script.app, ")"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        app = script.app
        if app:
            self._saveAppSettings(AXObject.get_name(app), general, pronunciations, keybindings)
            return

        # Assign current profile
        _profile = general.get('profile', settings.profile)
        currentProfile = _profile[1]

        self.profile = currentProfile

        # Elements that need to stay updated in main configuration.
        self.defaultGeneral['startingProfile'] = general.get('startingProfile',
                                                              _profile)

        self._setProfileGeneral(general)
        self._setProfilePronunciations(pronunciations)
        self._setProfileKeybindings(keybindings)

        tokens = ["SETTINGS MANAGER: Saving for backend", self._backend]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        self._backend.saveProfileSettings(self.profile,
                                          self.profileGeneral,
                                          self.profilePronunciations,
                                          self.profileKeybindings)

        tokens = ["SETTINGS MANAGER: Settings for", script, "(app:", script.app, ") saved"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return self._enableAccessibility()

    def _adjustBindingTupleValues(self, bindingTuple):
        """Converts the values of bindingTuple into KeyBinding-ready values."""

        keysym, mask, mods, clicks = bindingTuple
        if not keysym:
            bindingTuple = ('', 0, 0, 0)
        else:
            bindingTuple = (keysym, int(mask), int(mods), int(clicks))

        return bindingTuple

    def overrideKeyBindings(self, script, scriptKeyBindings):
        keybindingsSettings = self.profileKeybindings
        for handlerString, bindingTuples in keybindingsSettings.items():
            handler = script.inputEventHandlers.get(handlerString)
            if not handler:
                continue

            scriptKeyBindings.removeByHandler(handler)
            for bindingTuple in bindingTuples:
                bindingTuple = self._adjustBindingTupleValues(bindingTuple)
                keysym, mask, mods, clicks = bindingTuple
                newBinding = KeyBinding(keysym, mask, mods, handler, clicks)
                scriptKeyBindings.add(newBinding)

        return scriptKeyBindings

    def isFirstStart(self):
        """Check if the firstStart key is True or false"""
        return self._backend.isFirstStart()

    def setFirstStart(self, value=False):
        """Set firstStart. This user-configurable setting is primarily
        intended to serve as an indication as to whether or not initial
        configuration is needed."""
        self._backend.setFirstStart(value)

    def availableProfiles(self):
        """Get available profiles from active backend"""

        return self._backend.availableProfiles()

    def getAppSetting(self, app, settingName, fallbackOnDefault=True):
        if not app:
            return None

        appPrefs = self._backend.getAppSettings(AXObject.get_name(app))
        profiles = appPrefs.get('profiles', {})
        profilePrefs = profiles.get(self.profile, {})
        general = profilePrefs.get('general', {})
        appSetting = general.get(settingName)
        if appSetting is None and fallbackOnDefault:
            general = self._backend.getGeneral(self.profile)
            appSetting = general.get(settingName)

        return appSetting

    def loadAppSettings(self, script):
        """Load the users application specific settings for an app.

        Arguments:
        - script: the current active script.
        """

        if not (script and script.app):
            return

        for key in self._appPronunciations.keys():
            self.pronunciations.pop(key)

        prefs = self._backend.getAppSettings(AXObject.get_name(script.app))
        profiles = prefs.get('profiles', {})
        profilePrefs = profiles.get(self.profile, {})

        self._appGeneral = profilePrefs.get('general', {})
        self._appKeybindings = profilePrefs.get('keybindings', {})
        self._appPronunciations = profilePrefs.get('pronunciations', {})
        self._activeApp = AXObject.get_name(script.app)

        self._loadProfileSettings()
        self._mergeSettings()
        self._setSettingsRuntime(self.general)
        self._setPronunciationsRuntime(self.pronunciations)
        script.keyBindings = self.overrideKeyBindings(script, script.getKeyBindings())

_manager = SettingsManager()

def getManager():
    return _manager
