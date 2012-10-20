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
from . import script_manager
from . import settings
from . import pronunciation_dict
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

        debug.println(debug.LEVEL_FINEST, 'INFO: Initializing settings manager')

        self.backendModule = None
        self._backend = None
        self.profile = None
        self.backendName = backend
        self._prefsDir = None

        # Dictionaries for store the default values
        # The keys and values are defined at orca.settings
        #
        ## self.defaultGeneral contain some constants names as values
        self.defaultGeneral = {}
        ## self.defaultGeneralValues contain the actual values, no constants
        self.defaultGeneralValues = {}
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

        if not self._loadBackend():
            raise Exception('SettingsManager._loadBackend failed.')

        self.customizedSettings = {}
        self._customizationCompleted = False

        # For handling the currently-"classic" application settings
        self.settingsPackages = ["app-settings"]
        self._knownAppSettings = {}

        debug.println(debug.LEVEL_FINEST, 'INFO: Settings manager initialized')

    def activate(self, prefsDir=None, customSettings={}):
        debug.println(debug.LEVEL_FINEST, 'INFO: Activating settings manager')

        self.customizedSettings.update(customSettings)
        self._prefsDir = prefsDir \
            or os.path.join(GLib.get_user_data_dir(), "orca")

        # Load the backend and the default values
        self._backend = self.backendModule.Backend(self._prefsDir)
        self._setDefaultGeneral()
        self._setDefaultPronunciations()
        self._setDefaultKeybindings()
        self.defaultGeneralValues = getRealValues(self.defaultGeneral)
        self.general = self.defaultGeneralValues.copy()
        if not self.isFirstStart():
            self.general.update(self._backend.getGeneral())
        self.pronunciations = self.defaultPronunciations.copy()
        self.keybindings = self.defaultKeybindings.copy()

        # If this is the first time we launch Orca, there is no user settings
        # yet, so we need to create the user config directories and store the
        # initial default settings
        #
        self._createDefaults()

        debug.println(debug.LEVEL_FINEST, 'INFO: Settings manager activated')

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

        # Set up $XDG_DATA_HOME/orca/app-settings as a Python package.
        #
        orcaSettingsDir = os.path.join(orcaDir, "app-settings")
        _createDir(orcaSettingsDir)
        initFile = os.path.join(orcaSettingsDir, "__init__.py")
        if not os.path.exists(initFile):
            os.close(os.open(initFile, os.O_CREAT, 0o700))

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
            if value == None:
                try:
                    value = getattr(settings, key)
                except:
                    pass
            self.defaultGeneral[key] = value

    def _getCustomizedSettings(self):
        if self._customizationCompleted:
            return self.customizedSettings

        originalSettings = {}
        for key, value in list(settings.__dict__.items()):
            originalSettings[key] = value

        self._customizationCompleted = self._loadUserCustomizations()

        for key, value in list(originalSettings.items()):
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
            msg = "Attempt to load orca-customizations "
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
        debug.println(debug.LEVEL_ALL, msg)
        return success

    def getPrefsDir(self):
        return self._prefsDir

    def setSetting(self, settingName, settingValue):
        self._setSettingsRuntime({settingName:settingValue})

    def getSetting(self, settingName):
        return getattr(settings, settingName)

    def _getGeneral(self, profile=None):
        """Get from the active backend the general settings for
        the current profile"""
        if profile is None:
            profile = self.profile
        self.general = self._backend.getGeneral(profile)

    def _getPronunciations(self, profile=None):
        """Get from the active backend the pronunciations settings for
        the current profile"""
        if profile is None:
            profile = self.profile
        self.pronunciations = self._backend.getPronunciations(profile)

    def _getKeybindings(self, profile=None):
        """Get from the active backend the keybindings settings for
        the current profile"""
        if profile is None:
            profile = self.profile
        self.keybindings = self._backend.getKeybindings(profile)

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
        profileGeneral = getRealValues(self.profileGeneral) or {}
        self.general.update(profileGeneral)
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

    def setProfile(self, profile='default'):
        """Set a specific profile as the active one.
        Also the settings from that profile will be loading
        and updated the current settings with them."""
        self.profile = profile
        self._loadProfileSettings(profile)
        self._mergeSettings()
        self._setSettingsRuntime(self.general)

    def getPreferences(self, profile='default'):
        general = self.getGeneralSettings(profile)
        pronunciations = self.getPronunciations(profile)
        keybindings = self.getKeybindings(profile)
        return (general, pronunciations, keybindings)

    def _setSettingsRuntime(self, settingsDict):
        for key, value in list(settingsDict.items()):
            setattr(settings, str(key), value)
        self._getCustomizedSettings()
        for key, value in list(self.customizedSettings.items()):
            setattr(settings, str(key), value)
        self._setPronunciationsRuntime()

    def _setPronunciationsRuntime(self):
        pronunciation_dict.pronunciation_dict = {}
        for pron in self.pronunciations:
            key, value = self.pronunciations[pron]
            if key and value:
                pronunciation_dict.setPronunciation(key, value)

    def getGeneralSettings(self, profile='default'):
        """Return the current general settings.
        Those settings comes from updating the default settings
        with the profiles' ones"""
        generalDict = self._backend.getGeneral(profile)
        self._setSettingsRuntime(generalDict)
        return generalDict

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

        for key, value in list(general.items()):
            if isinstance(value, unicode):
                value = value.encode('UTF-8')
            if key in settings.excludeKeys:
                continue
            elif key == 'profile':
                self.profileGeneral[key] = value
            elif value != self.defaultGeneralValues.get(key):
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

    def saveSettings(self, general, pronunciations, keybindings):
        """Let the active backend to store the default settings and
        the profiles' ones."""
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
        keybindingsSettings = self.getKeybindings(self.profile)
        for handlerString, bindingTuples in list(keybindingsSettings.items()):
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

    def loadAppSettings(self, script):
        """Load the users application specific settings for an app.
        Note that currently the settings manager does not manage
        application settings in Orca; instead the old/"classic" files
        are used. This is scheduled to change.

        Arguments:
        - script: the current active script.
        """

        self._loadProfileSettings()
        script.voices = self.getSetting('voices')

        app = script.app
        moduleName = _scriptManager.getModuleName(app)
        if not moduleName:
            return

        module = None
        for package in self.settingsPackages:
            name = '.'.join((package, moduleName))
            debug.println(debug.LEVEL_FINEST, "Looking for %s.py" % name)
            try:
                module = importlib.import_module(name)
            except ImportError:
                debug.println(
                    debug.LEVEL_FINEST, "Could not import %s.py" % name)
                continue
            try:
                imp.reload(module)
            except:
                debug.println(debug.LEVEL_FINEST, "Could not load %s.py" % name)
                module = None
            else:
                debug.println(debug.LEVEL_FINEST, "Loaded %s.py" % name)
                break

        if not module:
            return

        self._knownAppSettings[name] = module
        imp.reload(self._knownAppSettings[name])

        appVoices = self.getSetting('voices')
        for voiceType, voiceDef in list(appVoices.items()):
            script.voices[voiceType].update(voiceDef)

        keybindings = getattr(module, 'overrideAppKeyBindings', None)
        if keybindings:
            script.overrideAppKeyBindings = keybindings
            script.keyBindings = keybindings(script, script.keyBindings)

        pronunciations = getattr(module, 'overridePronunciations', None)
        if pronunciations:
            script.overridePronunciations = pronunciations
            script.app_pronunciation_dict = \
                pronunciations(script, script.app_pronunciation_dict)

def getVoiceKey(voice):
    voicesKeys = getattr(settings, 'voicesKeys')
    for key in list(voicesKeys.keys()):
        if voicesKeys[key] == voice:
            return key
    return ""

def getValueForKey(prefsDict, key):
    need2repr = ['brailleEOLIndicator', 'brailleContractionTable',
                 'brailleRequiredStateString', 'enabledBrailledTextAttributes',
                 'enabledSpokenTextAttributes', 'speechRequiredStateString',
                 'speechServerFactory', 'presentDateFormat',
                 'presentTimeFormat']

    value = None
    if key in prefsDict:
        if isinstance(prefsDict[key], str):
            if key in need2repr:
                value = "\'%s\'" % prefsDict[key]
            elif key  == 'voices':
                key = getVoiceKey(key)
                value = prefsDict[key]
            else:
                try:
                    value = getattr(settings, prefsDict[key])
                except:
                    debug.println(debug.LEVEL_SEVERE,
                                  "Something went wront with key: " % key)
                    debug.printStack(debug.LEVEL_FINEST)
        else:
            value = prefsDict[key]
    return value

def getRealValues(prefs):
    """Get the actual values for any constant stored on a
    general settings dictionary.
    prefs is a dictionary with the userCustomizableSettings keys
    and values."""
    #for key in prefs.keys():
    #    prefs[key] = getValueForKey(prefs, key)
    return prefs

_manager = SettingsManager()

def getManager():
    return _manager
