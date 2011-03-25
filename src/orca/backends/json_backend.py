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

    def __init__(self):
        """ Initialize the JSON Backend.
        """ 
        self.general = {}
        self.pronunciations = {}
        self.keybindings = {}
        self.profiles = {}
        self.plugins = {}
        self.settingsFile = os.path.join(settings.userPrefsDir,
                                         "user-settings.conf")

# nacho's
#        self.plugins_conf = self.getPlugins() \
#            if self.getPlugins() is not None \
#            else {}

    def saveDefaultSettings(self, general, pronunciations, keybindings, plugins):
        """ Save default settings for all the properties from
            orca.settings. """
        defaultProfiles = {'default': { 'profile':  settings.profile,
                                                    'pronunciations': {},
                                                    'keybindings': {},
                                                    'plugins': plugins
                                      }
                          }
        prefs = {'general': general,
                 'profiles': defaultProfiles,
                 'pronunciations': pronunciations,
                 'keybindings': keybindings, 
                 'plugins': plugins}

        self.general = general
        self.profiles = defaultProfiles
        self.pronunciations = pronunciations
        self.keybindings = keybindings
        self.plugins = plugins

        settingsFile = open(self.settingsFile, 'w')
        dump(prefs, settingsFile, indent=4)
        settingsFile.close()

    def saveProfileSettings(self, profile, general, pronunciations, \
                            keybindings, plugins):
        """ Save minimal subset defined in the profile against current 
            defaults. """
        if profile is None:
            profile = 'default'

        general['pronunciations'] = pronunciations
        general['keybindings'] = keybindings
        general['plugins'] = plugins

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
        self.plugins = prefs['plugins']
        self.profiles = prefs['profiles'].copy()

    def getGeneral(self, profile='default'):
        """ Get general settings from default settings and
            override with profile values. """
        self._getSettings()
        generalSettings = self.general.copy()
        profileSettings = self.profiles[profile].copy()
        for key, value in profileSettings.items():
            if key == 'voices':
                for voiceType, voiceDef in value.items():
                    value[voiceType] = acss.ACSS(voiceDef)
            if key not in settings.excludeKeys:
                generalSettings[key] = value
        generalSettings['activeProfile'] = profileSettings['profile']
        return generalSettings

    def getPronunciations(self, profile='default'):
        """ Get pronunciation settings from default settings and
            override with profile values. """
        self._getSettings()
        pronunciations = self.pronunciations.copy()
        profileSettings = self.profiles[profile].copy()
        if profileSettings.has_key('pronunciations'):
            pronunciations = profileSettings['pronunciations']
        return pronunciations

    def getKeybindings(self, profile='default'):
        """ Get keybindings settings from default settings and
            override with profile values. """
        self._getSettings()
        keybindings = self.keybindings.copy()
        profileSettings = self.profiles[profile].copy()
        if profileSettings.has_key('keybindings'):
            keybindings = profileSettings['keybindings']
        return keybindings

    def getPlugins(self, profile='default'):
        """ Get plugins settings from default settings and
            override with profile values. """
        self._getSettings()
        plugins = self.plugins.copy()
        profileSettings = self.profiles[profile].copy()
        if profileSettings.has_key('plugins'):
            plugins = profileSettings['plugins']
        return plugins

    def isFirstStart(self):
        """ Check if we're in first start. """
 
        if not os.path.exists(self.settingsFile):
            return True

        self._getSettings()
        return self.general.get('firstStart', True)

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

        for profileName in self.profiles.keys():
            profileDict = self.profiles[profileName].copy()
            profiles.append(profileDict.get('profile'))

        return profiles

# nacho's
#    def addPlugin(self, plugin_data):
#        # receives a dict in the following way
#        # 'chat': { 'name': 'Chat plugin',
#        #           'active': True,
#        #           'registered': False
#        #           'type': 'Commander'
#        #           'path': /bar/foo }
#        try:
#            if self.plugins_conf == {}:
#                self.plugins_conf.update({'plugins': plugin_data})
#            else:
#                self.plugins_conf['plugins'].update(plugin_data)
#        except LookupError, e:
#            print "Error adding dictionary. Key "+str(e)+" exists"
#
#        self.saveConf(self.plugins_conf)
#
#    def getPlugins(self):
#        settingsFile = open(self.settingsFile)
#        try:
#            plugs = load(settingsFile)
#            if plugs.has_key('plugins'):
#                if not plugs['plugins']:
#                    return {}
#                else:
#                    return plugs.copy()
#            else:
#                return None
#        except ValueError:
#            return
#
#    def saveConf(self, plugins_to_save):
#        self.plugins_conf = plugins_to_save
#
#        with open(self.settingsFile, 'r+') as settingsFile:
#            prefs = load(settingsFile)
#            prefs.update(plugins_to_save)
#            settingsFile.seek(0)
#            settingsFile.truncate()
#            dump(prefs, settingsFile, indent=4)
#
#    def updatePlugin(self, plugin_to_update):
#        self.addPlugin(plugin_to_update)
#
#    def getPluginByName(self, plugin_name):
#        return self.plugins_conf['plugins'][plugin_name]
