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

import imp
import importlib
import os
from gi.repository import Gio, GLib

from . import debug
from . import orca_i18n
from . import script_manager
from . import settings
from . import pronunciation_dict
from .acss import ACSS
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
except:
    _proxy = None

_scriptManager = script_manager.getManager()

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

        debug.println(debug.LEVEL_INFO, 'SETTINGS MANAGER: Initializing', True)

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

        debug.println(debug.LEVEL_INFO, 'SETTINGS MANAGER: Initialized', True)

    def activate(self, prefsDir=None, customSettings={}):
        debug.println(debug.LEVEL_INFO, 'SETTINGS MANAGER: Activating', True)

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

        debug.println(debug.LEVEL_INFO, 'SETTINGS MANAGER: Activated', True)

        # Set the active profile and load its stored settings
        if self.profile is None:
            self.profile = self.general.get('startingProfile')[1]
        self.setProfile(self.profile)

    def _loadBackend(self):
        """Load specific backend for manage user settings"""

        try:
            backend = '.backends.%s_backend' % self.backendName
            self.backendModule = importlib.import_module(backend, 'orca')
            return True
        except:
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
                except:
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
        try:
            msg = "SETTINGS MANAGER: Attempt to load orca-customizations "
            (fileHnd, moduleName, desc) = \
                imp.find_module("orca-customizations", pathList)
            msg += "from %s " % moduleName
            imp.load_module("orca-customizations", fileHnd, moduleName, desc)
        except ImportError:
            success = True
            msg += "failed due to ImportError. Giving up."
        except AttributeError:
            return False
        else:
            msg += "succeeded."
            fileHnd.close()
            success = True
        debug.println(debug.LEVEL_ALL, msg, True)
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
            lang = "%s_%s" % (lang, dialect.upper())
        return lang

    def _loadProfileSettings(self, profile=None):
        """Get from the active backend all the settings for the current
        profile and store them in the object's attributes.
        A profile can be passed as a parameter. This could be useful for
        change from one profile to another."""
        if profile is None:
            profile = self.profile
        self.profileGeneral = self.getGeneralSettings(profile) or {}
        self.profilePronunciations = self.getPronunciations(profile) or {}
        self.profileKeybindings = self.getKeybindings(profile) or {}

    def _mergeSettings(self):
        """Update the changed values on the profile settings
        over the current and active settings"""
        self.profileGeneral.update(self._appGeneral)
        self.profilePronunciations.update(self._appPronunciations)
        self.profileKeybindings.update(self._appKeybindings)

        self.general.update(self.profileGeneral)
        self.pronunciations.update(self.profilePronunciations)
        self.keybindings.update(self.profileKeybindings)

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
        if not _proxy:
            return False

        return _proxy.Get('(ss)', 'org.a11y.Status', 'IsEnabled')

    def setAccessibility(self, enable):
        if not _proxy:
            return False

        vEnable = GLib.Variant('b', enable)
        _proxy.Set('(ssv)', 'org.a11y.Status', 'IsEnabled', vEnable)            

    def isScreenReaderServiceEnabled(self):
        """Returns True if the screen reader service is enabled. Note that
        this does not necessarily mean that Orca (or any other screen reader)
        is running at the moment."""

        if not _proxy:
            return False

        return _proxy.Get('(ss)', 'org.a11y.Status', 'ScreenReaderEnabled')

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

    def removeProfile(self, profile):
        self._backend.removeProfile(profile)

    def _setSettingsRuntime(self, settingsDict):
        for key, value in settingsDict.items():
            setattr(settings, str(key), value)
        self._getCustomizedSettings()
        for key, value in self.customizedSettings.items():
            setattr(settings, str(key), value)

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

    def _setProfilePronunciations(self, pronunciations):
        """Set the changed pronunciations settings from the defaults' ones
        as the profile's."""
        self.profilePronunciations = self.defaultPronunciations.copy()
        self.profilePronunciations.update(pronunciations)

    def _setProfileKeybindings(self, keybindings):
        """Set the changed keybindings settings from the defaults' ones
        as the profile's."""
        self.profileKeybindings = self.defaultKeybindings.copy()
        self.profileKeybindings.update(keybindings)

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

        app = script.app
        if app:
            self._saveAppSettings(app.name, general, pronunciations, keybindings)
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

        self._backend.saveProfileSettings(self.profile,
                                          self.profileGeneral,
                                          self.profilePronunciations,
                                          self.profileKeybindings)
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
        """Set firstStart. This user-configurable settting is primarily
        intended to serve as an indication as to whether or not initial
        configuration is needed."""
        self._backend.setFirstStart(value)

    def availableProfiles(self):
        """Get available profiles from active backend"""

        return self._backend.availableProfiles()

    def getAppSetting(self, app, settingName, fallbackOnDefault=True):
        if not app:
            return None

        appPrefs = self._backend.getAppSettings(app.name)
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

        prefs = self._backend.getAppSettings(script.app.name)
        profiles = prefs.get('profiles', {})
        profilePrefs = profiles.get(self.profile, {})

        self._appGeneral = profilePrefs.get('general', {})
        self._appKeybindings = profilePrefs.get('keybindings', {})
        self._appPronunciations = profilePrefs.get('pronunciations', {})
        self._activeApp = script.app.name

        self._loadProfileSettings()
        self._mergeSettings()
        self._setSettingsRuntime(self.general)
        self._setPronunciationsRuntime(self.pronunciations)
        script.keyBindings = self.overrideKeyBindings(script, script.getKeyBindings())

_manager = SettingsManager()

def getManager():
    return _manager
