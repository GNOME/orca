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

        base_dict = {}
        for key in ['activeProfile', 'startingProfile', \
                    'availableProfiles', 'firstStart']:
            if general.has_key(key): 
                value = general.pop(key)
                base_dict[key] = value

        voices_dict = general['voices']

        self._set_schema_to_path(BASE_SCHEMA, None, base_dict)
        self._set_schema_to_path(SETTINGS_SCHEMA, BASE_PATH, general)
        self._set_voices(BASE_PATH, voices_dict)


        self._set_profiles_dict(defaultProfiles)
        self._set_pronunciations_dict(BASE_PATH, pronunciations)
        self._set_keybindings_dict(BASE_PATH, keybindings)


    def saveProfileSettings(self, profile, general,
                                  pronunciations, keybindings):
        """ Save minimal subset defined in the profile against current 
            defaults. """
        if profile is None:
            profile = 'default'

        general['pronunciations'] = pronunciations
        general['keybindings'] = keybindings

        profiles = self._get_profiles_dict()
        profiles[profile] = general

        self._set_profiles_dict(profiles)

    def _getSettings(self):
        """ Load from GSettings all settings """
        settings_dict = self._get_dict_path(BASE_SCHEMA)
        settings_dict.update(self._get_dict_path(SETTINGS_SCHEMA, BASE_PATH))
        #settings_dict['voices'] = self._get_dict_path(VOICES_SCHEMA, BASE_PATH)

        for key in ['availableProfiles', 'availableKeybindings', 'availablePronunciations']:
            settings_dict.pop(key)

        self.general = settings_dict.copy()
        

        self.pronunciations = self._get_pronunciations_dict(BASE_PATH)
        self.keybindings = self._get_keybindings_dict(BASE_PATH)

        profiles_dict = self._get_profiles_dict()
        self.profiles = profiles_dict.copy()

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

        self.__set_key_value(BASE_SCHEMA, BASE_PATH, key, value)

    def setFirstStart(self, value=False):
        """Set firstStart. This user-configurable settting is primarily
        intended to serve as an indication as to whether or not initial
        configuration is needed."""
        self.general['firstStart'] = value
        self.__set_key_value(BASE_SCHEMA, None, 'firstStart', value)

    def availableProfiles(self):
        """ List available profiles. """

        profileDict = self._get_profiles_dict()
        profiles = []

        for profileName in profileDict.keys(): 
            profiles.append(profileDict[profileName].get('profile'))

        return profiles

# GSettings-related methods


    def _get_dict_path(self, schema, path=None):
        """ Get a dictionary object from a given schema.
        This method returns a dictionary from a given schema and from an
        optionally path. We assume that we only call this method
        without a path when we want to get org.gnome.Orca schema. """

        out_dict = {}

        g_settings = GSettings(schema=schema, path=path)

        for key in g_settings.list_keys():
            value = self.__get_key_value(schema, path, key)
            out_dict[key] = value

        return out_dict

    def _set_schema_to_path(self, schema, path=None, dict_in=None):
        g_settings = GSettings(schema=schema, path=path)

        for key in g_settings.list_keys():
            if key not in dict_in.keys(): continue
            self.__set_key_value(schema, path, \
                    key, dict_in[key])


    def __get_key_value(self, schema, path, key):
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

    def __set_key_value(self, schema, path, key, value):
        """ Get a key value from a given"""

        g_settings = GSettings(schema = schema, \
                                  path = path)

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

    def _get_profiles_dict(self):
        g_settings = GSettings(schema=BASE_SCHEMA)

        out_dict = {}

        for profile in g_settings.get_strv('availableProfiles'):
            path = '%s%s/' % (PROFILES_PATH, profile)

            value = self._get_dict_path(SETTINGS_SCHEMA, path)
            for key in ['availableKeybindings', 'availablePronunciations']:
                value.pop(key)
            out_dict[profile] = value

            value = self._get_voices(path)
            out_dict[profile]['voices'] = value

            value = self._get_pronunciations_dict(path)
            out_dict[profile]['pronunciations'] = value

            value = self._get_keybindings_dict(path)
            out_dict[profile]['keybindings'] = value

        return out_dict

    def _set_profiles_dict(self, dict_in):
        g_settings = GSettings(schema=BASE_SCHEMA)

        for profile in dict_in.keys():
            availableProfiles = g_settings.get_strv('availableProfiles')
            if not profile in availableProfiles:
                availableProfiles.append(profile)
                g_settings.set_strv('availableProfiles', availableProfiles)

            path = '%s%s/' % (PROFILES_PATH, profile)

            self._set_schema_to_path(SETTINGS_SCHEMA, path, dict_in[profile])

            if dict_in[profile].has_key('voices'):
                self._set_voices(path, dict_in[profile]['voices'])

            self._set_pronunciations_dict(path, dict_in[profile]['pronunciations'])

            self._set_keybindings_dict(path, dict_in[profile]['keybindings'])


    def _get_voices(self, path=None):
        out_dict = {}

        for voice in ['default', 'hyperlink', 'system', 'uppercase']:
            voice_path = '%sVoices/%s/' % (path, voice)
            value = self._get_dict_path(VOICES_SCHEMA, voice_path)
            out_dict[voice] = value

            family_path = '%sfamily/' % voice_path
            family = self._get_dict_path(FAMILY_SCHEMA, family_path)
            out_dict[voice]['family'] = family

        return out_dict

    def _set_voices(self, path, dict_in):
        root_path = path

        voices_dict = self._get_voices(path)
        voices_dict.update(dict_in)

        for voice in ['default', 'hyperlink', 'system', 'uppercase']:
            path = '%sVoices/%s/' % (root_path, voice)
            self._set_schema_to_path(VOICES_SCHEMA, path, dict_in[voice])

            if 'family' in dict_in[voice]:
                path = '%sfamily/' % path
                self._set_schema_to_path(FAMILY_SCHEMA, path, dict_in[voice]['family'])

    def _get_pronunciations_dict(self, path):
        g_settings = GSettings(schema=SETTINGS_SCHEMA, path=path)
        schema = PRONUNCIATIONS_SCHEMA
        root_path = path

        out_dict = {}

        for pronunciation in g_settings.get_strv('availablePronunciations'):
            path = '%sPronunciations/%s/' % (root_path, pronunciation)
            value = self._get_dict_path(schema, path)
            out_dict[pronunciation] = [value['word'], value['pronunciation']]

        return out_dict

    def _set_pronunciations_dict(self, path, dict_in):
        g_settings = GSettings(schema=SETTINGS_SCHEMA, path=path)
        schema = PRONUNCIATIONS_SCHEMA
        root_path = path

        for pronunciation in dict_in.keys():
            path = '%sPronunciations/%s/' % (root_path, pronunciation)
            pron_dict = {'word': dict_in[pronunciation][0],
                    'pronunciation': dict_in[pronunciation][1]}
            self._set_schema_to_path(schema, path, pron_dict)

        pronunciations = dict_in.keys()
        g_settings.set_strv('availablePronunciations', pronunciations)

    def _get_keybindings_dict(self, path=None):
        g_settings = GSettings(schema=SETTINGS_SCHEMA, path=path)
        schema = KEYBINDINGS_SCHEMA
        root_path = path

        out_dict = {}

        for keybinding in g_settings.get_strv('availableKeybindings'):
            path = '%sKeybindings/%s/' % (root_path, keybinding)
            value = self._get_dict_path(schema, path)
            out_dict[keybinding] = [(value['modifierMask'], \
                                    value['defaultModifierMask'], \
                                    value['handler'], \
                                    value['click']), \
                                    (value['modifierMaskAlt'], \
                                    value['defaultModifierMaskAlt'], \
                                    value['handlerAlt'], \
                                    value['clickAlt'])]

        return out_dict

    def _set_keybindings_dict(self, path, dict_in):
        g_settings = GSettings(schema=SETTINGS_SCHEMA, path=path)

        schema = KEYBINDINGS_SCHEMA
        root_path = path
        keybindings = []

        for keybinding in dict_in.keys():
            if dict_in[keybinding][0] == '' and dict_in[keybinding][1] == '': continue
            path = '%sKeybindings/%s/' % (root_path, keybinding)
            keybs_dict = {'modifierMask' : dict_in[keybinding][0][0], \
                          'defaultModifierMask': dict_in[keybinding][0][1], \
                          'handler': dict_in[keybinding][0][2], \
                          'click': dict_in[keybinding][0][3], \
                          'modifierMaskAlt' : dict_in[keybinding][1][0], \
                          'defaultModifierMaskAlt': dict_in[keybinding][1][1], \
                          'handlerAlt': dict_in[keybinding][1][2], \
                          'clickAlt': dict_in[keybinding][1][3]}

            self._set_schema_to_path(schema, path, keybs_dict)
            keybindings.append(keybinding)
            
        g_settings.set_strv('availableKeybindings', keybindings)


