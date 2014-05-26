# Orca
#
# Copyright 2010-2011 Consorcio Fernando de los Rios.
# Author: Juanje Ojeda Croissier <jojeda@emergya.es>
# Author: Javier Hernandez Antunez <jhernandez@emergya.es>
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

"""JSON backend for Orca settings"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010-2011 Consorcio Fernando de los Rios."
__license__   = "LGPL"

from json import load, dump
import os
from orca import settings, acss

class Backend:

    def __init__(self, prefsDir):
        """ Initialize the JSON Backend.
        """ 
        self.general = {}
        self.pronunciations = {}
        self.keybindings = {}
        self.profiles = {}
        self.settingsFile = os.path.join(prefsDir, "user-settings.conf")
        self.appPrefsDir = os.path.join(prefsDir, "app-settings")

    def saveDefaultSettings(self, general, pronunciations, keybindings):
        """ Save default settings for all the properties from
            orca.settings. """
        defaultProfiles = {'default': { 'profile':  settings.profile,
                                                    'pronunciations': {},
                                                    'keybindings': {}
                                      }
                          }
        prefs = {'general': general,
                 'profiles': defaultProfiles,
                 'pronunciations': pronunciations,
                 'keybindings': keybindings}

        self.general = general
        self.profiles = defaultProfiles
        self.pronunciations = pronunciations
        self.keybindings = keybindings

        settingsFile = open(self.settingsFile, 'w')
        dump(prefs, settingsFile, indent=4)
        settingsFile.close()

    def getAppSettings(self, appName):
        fileName = os.path.join(self.appPrefsDir, "%s.conf" % appName)
        if os.path.exists(fileName):
            settingsFile = open(fileName, 'r')
            prefs = load(settingsFile)
            settingsFile.close()
        else:
            prefs = {}

        return prefs

    def saveAppSettings(self, appName, profile, general, pronunciations, keybindings):
        prefs = self.getAppSettings(appName)
        profiles = prefs.get('profiles', {})
        profiles[profile] = {'general': general,
                             'pronunciations': pronunciations,
                             'keybindings': keybindings}
        prefs['profiles'] = profiles

        fileName = os.path.join(self.appPrefsDir, "%s.conf" % appName)
        settingsFile = open(fileName, 'w')
        dump(prefs, settingsFile, indent=4)
        settingsFile.close()

    def saveProfileSettings(self, profile, general,
                                  pronunciations, keybindings):
        """ Save minimal subset defined in the profile against current 
            defaults. """
        if profile is None:
            profile = 'default'

        general['pronunciations'] = pronunciations
        general['keybindings'] = keybindings

        with open(self.settingsFile, 'r+') as settingsFile:
            prefs = load(settingsFile)
            prefs['profiles'][profile] = general
            settingsFile.seek(0)
            settingsFile.truncate()
            dump(prefs, settingsFile, indent=4)

    def _getSettings(self):
        """ Load from config file all settings """
        settingsFile = open(self.settingsFile)
        try:
            prefs = load(settingsFile)
        except ValueError:
            return
        self.general = prefs['general'].copy()
        self.pronunciations = prefs['pronunciations']
        self.keybindings = prefs['keybindings']
        self.profiles = prefs['profiles'].copy()

    def getGeneral(self, profile='default'):
        """ Get general settings from default settings and
            override with profile values. """
        self._getSettings()
        generalSettings = self.general.copy()
        profileSettings = self.profiles[profile].copy()
        for key, value in list(profileSettings.items()):
            if key == 'voices':
                for voiceType, voiceDef in list(value.items()):
                    value[voiceType] = acss.ACSS(voiceDef)
            if key not in ['startingProfile', 'activeProfile']:
                generalSettings[key] = value
        try:
            generalSettings['activeProfile'] = profileSettings['profile']
        except KeyError:
            generalSettings['activeProfile'] = ["Default", "default"] 
        return generalSettings

    def getPronunciations(self, profile='default'):
        """ Get pronunciation settings from default settings and
            override with profile values. """
        self._getSettings()
        pronunciations = self.pronunciations.copy()
        profileSettings = self.profiles[profile].copy()
        if 'pronunciations' in profileSettings:
            pronunciations = profileSettings['pronunciations']
        return pronunciations

    def getKeybindings(self, profile='default'):
        """ Get keybindings settings from default settings and
            override with profile values. """
        self._getSettings()
        keybindings = self.keybindings.copy()
        profileSettings = self.profiles[profile].copy()
        if 'keybindings' in profileSettings:
            keybindings = profileSettings['keybindings']
        return keybindings

    def isFirstStart(self):
        """ Check if we're in first start. """
 
        return not os.path.exists(self.settingsFile)

    def _setProfileKey(self, key, value):
        self.general[key] = value

        with open(self.settingsFile, 'r+') as settingsFile:
            prefs = load(settingsFile)
            prefs['general'][key] = value
            settingsFile.seek(0)
            settingsFile.truncate()
            dump(prefs, settingsFile, indent=4)

    def setFirstStart(self, value=False):
        """Set firstStart. This user-configurable settting is primarily
        intended to serve as an indication as to whether or not initial
        configuration is needed."""
        self.general['firstStart'] = value
        self._setProfileKey('firstStart', value)

    def availableProfiles(self):
        """ List available profiles. """
        self._getSettings()
        profiles = []

        for profileName in list(self.profiles.keys()):
            profileDict = self.profiles[profileName].copy()
            profiles.append(profileDict.get('profile'))

        return profiles
