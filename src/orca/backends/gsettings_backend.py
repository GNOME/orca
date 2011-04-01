# Orca
#
# Copyright 2011 Consorcio Fernando de los Rios.
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

"""GSettings backend for Orca settings"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import os
import re
from orca import settings

from gi.repository.Gio import Settings as GSettings

# Orca Application Schemas
#
BASE_SCHEMA           = 'org.gnome.Orca'
SETTINGS_SCHEMA       = 'org.gnome.Orca.Settings'
VOICES_SCHEMA         = 'org.gnome.Orca.Settings.Voices'
FAMILY_SCHEMA         = 'org.gnome.Orca.Settings.Voices.Family'
KEYBINDINGS_SCHEMA    = 'org.gnome.Orca.Settings.Keybindings'
PRONUNCIATIONS_SCHEMA = 'org.gnome.Orca.Settings.Pronunciations'

# Orca Application paths
#
BASE_PATH     = '/apps/gnome/Orca/'
PROFILES_PATH = '/apps/gnome/Orca/Profiles/'

class Backend:

    def __init__(self):
        """ Initialize the GSettings Backend.
        """ 
        self.general = {}
        self.pronunciations = {}
        self.keybindings = {}
        self.profiles = {}

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

        baseDict = {}
        for key in ['activeProfile', 'startingProfile', \
                    'availableProfiles', 'firstStart']:
            if general.has_key(key): 
                value = general.pop(key)
                baseDict[key] = value

        voicesDict = general['voices']

        self._setSchemaToPath(BASE_SCHEMA, None, baseDict)
        self._setSchemaToPath(SETTINGS_SCHEMA, BASE_PATH, general)
        self._setVoices(BASE_PATH, voicesDict)

        self._setProfilesDict(defaultProfiles)
        self._setPronunciationsDict(BASE_PATH, pronunciations)
        self._setKeybindingsDict(BASE_PATH, keybindings)

    def saveProfileSettings(self, profile, general,
                                  pronunciations, keybindings):
        """ Save minimal subset defined in the profile against current 
            defaults. """
        if profile is None:
            profile = 'default'

        general['pronunciations'] = pronunciations
        general['keybindings'] = keybindings

        profiles = self._getProfilesDict()
        profiles[profile] = general

        self._setProfilesDict(profiles)

    def _getSettings(self):
        """ Load from GSettings all settings """
        settingsDict = self._getSchemaFromPath(BASE_SCHEMA)
        settingsDict.update(self._getSchemaFromPath(SETTINGS_SCHEMA, BASE_PATH))
        #settingsDict['voices'] = self._getSchemaFromPath(VOICES_SCHEMA, BASE_PATH)

        for key in ['availableProfiles', 'availableKeybindings', 'availablePronunciations']:
            settingsDict.pop(key)

        self.general = settingsDict.copy()

        self.pronunciations = self._getPronunciationsDict(BASE_PATH)
        self.keybindings = self._getKeybindingsDict(BASE_PATH)

        profilesDict = self._getProfilesDict()
        self.profiles = profilesDict.copy()

    def getGeneral(self, profile='default'):
        """ Get general settings from default settings and
            override with profile values. """
        self._getSettings()
        generalSettings = self.general.copy()
        profileSettings = self.profiles[profile].copy()
        for key, value in profileSettings.items():
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

    def isFirstStart(self):
        """ Check if we're in first start. """
 
#        if not os.path.exists(self.settingsFile):
#            return True

        self._getSettings()

        return self.general.get('firstStart', True)

    def _setProfileKey(self, key, value):
        self.general[key] = value

        self.__setKeyValue(BASE_SCHEMA, BASE_PATH, \
                           self.__camelToDash(key), value)

    def setFirstStart(self, value=False):
        """Set firstStart. This user-configurable settting is primarily
        intended to serve as an indication as to whether or not initial
        configuration is needed."""
        self.general['firstStart'] = value
        self.__setKeyValue(BASE_SCHEMA, None, 'first-start', value)

    def availableProfiles(self):
        """ List available profiles. """

        profileDict = self._getProfilesDict()
        profiles = []

        for profileName in profileDict.keys(): 
            profiles.append(profileDict[profileName].get('profile'))

        return profiles

    # GSettings-related methods
    #
    def _getSchemaFromPath(self, schema, path=None):
        """ Get a dictionary object from a given schema.
        This method returns a dictionary from a given schema and from an
        optionally path. We assume that we only call this method
        without a path when we want to get org.gnome.Orca schema. """

        out_dict = {}

        g_settings = GSettings(schema=schema, path=path)

        for key in g_settings.list_keys():
            value = self.__getKeyValue(schema, path, key)
            out_dict[self.__dashToCamel(key)] = value

        return out_dict

    def _setSchemaToPath(self, schema, path=None, dict_in=None):
        g_settings = GSettings(schema=schema, path=path)

        for key in g_settings.list_keys():
            if self.__dashToCamel(key) not in dict_in.keys(): continue
            self.__setKeyValue(schema, path, \
                    key, \
                    dict_in[self.__dashToCamel(key)])


    def __getKeyValue(self, schema, path, key):
        """ Get a key value from a given"""

        g_settings = GSettings(schema = schema, \
                                  path = path)

        g_value_get = { \
            's' : g_settings.get_string, \
            'i' : g_settings.get_int, \
            'd' : g_settings.get_double, \
            'b' : g_settings.get_boolean, \
            'as': g_settings.get_strv, \
        }

        g_value = g_settings.get_value(key)
        value_type = g_value.get_type_string()
        value = g_value_get[value_type](key)

        return value

    def __setKeyValue(self, schema, path, key, value):
        """ Get a key value from a given"""

        g_settings = GSettings(schema = schema, path = path)

        if isinstance(value, dict) or isinstance(value, type(None)): return

        g_value_set = { \
            str   : g_settings.set_string, \
            int   : g_settings.set_int, \
            bool  : g_settings.set_boolean, \
            list  : g_settings.set_strv, \
            tuple : g_settings.set_strv, \
            float : g_settings.set_double, \
        }

        g_value_set[type(value)](key, value)

    def _getProfilesDict(self):
        g_settings = GSettings(schema=BASE_SCHEMA)

        out_dict = {}

        for profile in g_settings.get_strv('available-profiles'):
            path = '%s%s/' % (PROFILES_PATH, profile)

            value = self._getSchemaFromPath(SETTINGS_SCHEMA, path)
            for key in ['availableKeybindings', 'availablePronunciations']:
                value.pop(key)
            out_dict[profile] = value

            value = self._getVoices(path)
            out_dict[profile]['voices'] = value

            value = self._getPronunciationsDict(path)
            out_dict[profile]['pronunciations'] = value

            value = self._getKeybindingsDict(path)
            out_dict[profile]['keybindings'] = value

        return out_dict

    def _setProfilesDict(self, dict_in):
        g_settings = GSettings(schema=BASE_SCHEMA)

        for profile in dict_in.keys():
            availableProfiles = g_settings.get_strv('available-profiles')
            if not profile in availableProfiles:
                availableProfiles.append(profile)
                g_settings.set_strv('available-profiles', availableProfiles)

            path = '%s%s/' % (PROFILES_PATH, profile)

            self._setSchemaToPath(SETTINGS_SCHEMA, path, dict_in[profile])

            if dict_in[profile].has_key('voices'):
                self._setVoices(path, dict_in[profile]['voices'])

            self._setPronunciationsDict(path, dict_in[profile]['pronunciations'])

            self._setKeybindingsDict(path, dict_in[profile]['keybindings'])


    def _getVoices(self, path=None):
        out_dict = {}

        for voice in ['default', 'hyperlink', 'system', 'uppercase']:
            voice_path = '%sVoices/%s/' % (path, voice)
            value = self._getSchemaFromPath(VOICES_SCHEMA, voice_path)
            out_dict[voice] = value

            family_path = '%sfamily/' % voice_path
            family = self._getSchemaFromPath(FAMILY_SCHEMA, family_path)
            out_dict[voice]['family'] = family

        return out_dict

    def _setVoices(self, path, dict_in):
        root_path = path

        voices_dict = self._getVoices(path)
        voices_dict.update(dict_in)

        for voice in ['default', 'hyperlink', 'system', 'uppercase']:
            path = '%sVoices/%s/' % (root_path, voice)
            self._setSchemaToPath(VOICES_SCHEMA, path, dict_in[voice])

            if 'family' in dict_in[voice]:
                path = '%sfamily/' % path
                self._setSchemaToPath(FAMILY_SCHEMA, path, dict_in[voice]['family'])

    def _getPronunciationsDict(self, path):
        g_settings = GSettings(schema=SETTINGS_SCHEMA, path=path)
        schema = PRONUNCIATIONS_SCHEMA
        root_path = path

        out_dict = {}

        for pronunciation in g_settings.get_strv('available-pronunciations'):
            path = '%sPronunciations/%s/' % (root_path, pronunciation)
            value = self._getSchemaFromPath(schema, path)
            out_dict[pronunciation] = [value['word'], value['pronunciation']]

        return out_dict

    def _setPronunciationsDict(self, path, dict_in):
        g_settings = GSettings(schema=SETTINGS_SCHEMA, path=path)
        schema = PRONUNCIATIONS_SCHEMA
        root_path = path

        for pronunciation in dict_in.keys():
            path = '%sPronunciations/%s/' % (root_path, pronunciation)
            pron_dict = {'word': dict_in[pronunciation][0],
                    'pronunciation': dict_in[pronunciation][1]}
            self._setSchemaToPath(schema, path, pron_dict)

        pronunciations = dict_in.keys()
        g_settings.set_strv('available-pronunciations', pronunciations)

    def _getKeybindingsDict(self, path=None):
        g_settings = GSettings(schema=SETTINGS_SCHEMA, path=path)
        schema = KEYBINDINGS_SCHEMA
        root_path = path

        out_dict = {}

        for keybinding in g_settings.get_strv('available-keybindings'):
            path = '%sKeybindings/%s/' % (root_path, keybinding)
            value = self._getSchemaFromPath(schema, path)
            out_dict[keybinding] = [(value['modifierMask'], \
                                    value['defaultModifierMask'], \
                                    value['handler'], \
                                    value['click']), \
                                    (value['modifierMaskAlt'], \
                                    value['defaultModifierMaskAlt'], \
                                    value['handlerAlt'], \
                                    value['clickAlt'])]

        return out_dict

    def _setKeybindingsDict(self, path, dict_in):
        g_settings = GSettings(schema=SETTINGS_SCHEMA, path=path)

        schema = KEYBINDINGS_SCHEMA
        root_path = path
        keybindings = []

        for keybinding in dict_in.keys():
            # go to the next iteration if is empty
            if dict_in[keybinding][0] == '' and \
               dict_in[keybinding][1] == '': continue
            path = '%sKeybindings/%s/' % (root_path, keybinding)
            keybs_dict = {'modifierMask' : dict_in[keybinding][0][0], \
                          'defaultModifierMask': dict_in[keybinding][0][1], \
                          'handler': dict_in[keybinding][0][2], \
                          'click': dict_in[keybinding][0][3], \
                          'modifierMaskAlt' : dict_in[keybinding][1][0], \
                          'defaultModifierMaskAlt': dict_in[keybinding][1][1], \
                          'handlerAlt': dict_in[keybinding][1][2], \
                          'clickAlt': dict_in[keybinding][1][3]}

            self._setSchemaToPath(schema, path, keybs_dict)
            keybindings.append(keybinding)

        g_settings.set_strv('available-keybindings', keybindings)


    # Key names conversion methods
    # At this moment, Orca's code style is camelCase, but GSettings
    # force us to store them in a dasherized way, so we are converting
    # key our settings names on the fly.
    #
    # We're using this methods only in direct calls to load or store related
    # code.
    #
    def __camelToDash(self, stringAsCamelCase):
        if stringAsCamelCase is None:
            return None
 
        pattern = re.compile('([A-Z][A-Z][a-z])|([a-z][A-Z])')
        return pattern.sub( \
            lambda m: m.group()[:1].lower() + "-" + m.group()[1:].lower(), \
            stringAsCamelCase)

    def __dashToCamel(self, stringAsDasherized):
        if stringAsDasherized is None:
            return None

        myList = stringAsDasherized.split('-')
        outString = myList.pop(0)

        for word in myList:
            outString += word.capitalize()

        return outString

