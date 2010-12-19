# Orca
#
# Copyright 2010 Consorcio Fernando de los Rios.
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

"""Common utilities to manage the store user preferences over gconf."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import os

from orca import settings, keybindings
import gconf
import types

# The same fields than in orca_gui_prefs.py:
(HANDLER, DESCRIP, MOD_MASK1, MOD_USED1, KEY1, CLICK_COUNT1, OLDTEXT1, \
 TEXT1, MOD_MASK2, MOD_USED2, KEY2, CLICK_COUNT2, OLDTEXT2, TEXT2, MODIF, \
 EDITABLE) = range(16)

(ACTUAL, REPLACEMENT) = range(2)

class Backend:
    # set gconf configuration properties
    GCONF_BASE_DIR = '/apps/gnome-orca'
    VALID_KEY_TYPES = (bool, str, int, list, tuple)

    def __init__(self):
        """Creates a new Backend instance that will be used to load/store
        application specific preferences.
        """

        # init gconf
        self.__app_key = self.GCONF_BASE_DIR
        self._client = gconf.client_get_default()
        self._client.add_dir(self.GCONF_BASE_DIR[:-1],
                             gconf.CLIENT_PRELOAD_RECURSIVE)
        self._notifications = []

        self.general = {}
        self.pronunciations = {}
        self.keybindings = {}
        self.profiles = {}

        if not self._client.dir_exists(self.__app_key):
            self.prefsDict = self.options
            self.writePreferences()

    def _checkProfile(self, profile=None):
        if profile is None:
            profile = ['Default', 'default']
        activeProfilePath = '%s/activeProfile' % basePath
        if not self._client.dir_exists(basePath):
            self._client.set_list(activeProfilePath,
                                  gconf.VALUE_STRING,
                                  profile)
            startingProfilePath = '%s/startingProfile' % basePath
            self._client.set_list(startingProfilePath,
                                  gconf.VALUE_STRING,
                                  profile)
        else:
            profile = self._client.get_list(activeProfilePath,
                                            gconf.VALUE_STRING)
        profilePath = '%s/%s' % (basePath, profile[1])
        if not self._client.dir_exists(profilePath):
            self._client.add_dir(profilePath,
                                 gconf.CLIENT_PRELOAD_RECURSIVE)
        return profile

    def _getGeneralPrefs(self, profilePath):
        gconfEntries = client.all_entries(profilePath)
        generalPrefs = {}
        for entry in gconfEntries:
            gconfPathKey = entry.get_key()
            key = gconfPathKey.split('/')[-1]
            value = entry.get_value()
            if value.type == gconf.VALUE_STRING:
                generalPrefs[key] = value.get_string()
            elif value.type == gconf.VALUE_INT:
                generalPrefs[key] = value.get_int()
            elif value.type == gconf.VALUE_FLOAT:
                generalPrefs[key] = value.get_float()
            elif value.type == gconf.VALUE_BOOL:
                generalPrefs[key] = value.get_bool()
            elif value.type == gconf.VALUE_LIST:
                values = [item.get_string() for item in value.get_list()]
                generalPrefs[key] = values
            else:
                generalPrefs[key] = None
        return generalPrefs

    def _getVoicesPrefs(self, voicesPath):
        from orca.acss import ACSS
        gconfEntries = self._client.all_entries(voicesPath)
        voicesPrefs = {}
        for entry in gconfEntries:
            gconfPathKey = entry.get_key()
            key = gconfPathKey.split('/')[-1]
            key = getattr(settings, key)
            value = entry.get_value()
            _value = value.get_string()
            voicesPrefs[key] = eval(_value)
        return voicesPrefs

    def _getSettings(self):
        if profile is None:
           profile = self.checkProfile()
        profilePath = '%s/%s' % (basePath, profile[1])
        voicesPath = '%s/voices' % profilePath
        generalPrefs = self._getGeneralPrefs(profilePath)
        voicesPrefs = self._getVoicesPrefs(voicesPath)
        prefsDict = generalPrefs
        prefsDict['voices'] = voicesPrefs
        return prefsDict



    def __format_gconf_dir(self, path, entry):
        formatDir = path.split('/')

        for item in range(4):
            formatDir.pop(0)
        dictString = 'self.options'

        for item in formatDir:
            dictString += repr([item])
        dictString += repr([entry.key.split('/')[-1]])

        return dictString


    def gconf_save(self, key = None, keyDictionary = None):
        casts = {types.BooleanType: gconf.Client.set_bool,
                 types.IntType:     gconf.Client.set_int,
                 types.FloatType:   gconf.Client.set_float,
                 types.StringType:  gconf.Client.set_string,
                 types.ListType:    gconf.Client.set_list,
                 types.TupleType:   gconf.Client.set_list}

        if key and keyDictionary:
            self.__app_key += '/%s' % key
            keyDict = keyDictionary
        else:
            if not self.prefsDict:
                keyDict = self.options = self.DEFAULTS
            else:
                keyDict = self.options = self.prefsDict
 
        for name, value in keyDict.items():
            if name in ['activeProfile', 'startingProfile']:
                continue
            if isinstance(value, dict) and len(value) != 0:
                self.gconf_save(name, value)
                self.__app_key = \
                    self.__app_key[:len(self.__app_key) - (len(name) + 1)]
                continue

            if type(value) in (list, tuple) and value != 0:
                string_value = [str(item) for item in value]
                casts[type(value)](self._client, self.__app_key + '/' + name,
                    gconf.VALUE_STRING, string_value)
            else:
                if name in self.need2repr and value != None:
                    value = self._fix_quotes(value)
                if value != None and not isinstance(value, dict):
                    casts[type(value)](self._client, self.__app_key + '/' + \
                                       name, value)

    def writePreferences(self):
        """Creates the gconf schema and files to hold user preferences.  Note
        that callers of this method may want to consider using an ordered
        dictionary so that the keys are output in a deterministic order.

        Returns True if accessibility was enabled as a result of this
        call.
        """

        self._setupPreferencesDirs()
        
        # JD -> JH: Another sanity check: self.prefsDict['activeProfile']
        # might exist with a value of None.
        #
        defaultValue = ['Default', 'default']
        if not self.prefsDict.get('activeProfile'):
            self.prefsDict['activeProfile'] = defaultValue
            self._client.set_bool('/apps/gnome-orca/firstStart', True)
        if not self.prefsDict.get('startingProfile'):
            self.prefsDict['startingProfile'] = defaultValue

        if self.prefsDict:
            self._client.set_list('/apps/gnome-orca/activeProfile',
                                    gconf.VALUE_STRING,
                                    self.prefsDict['activeProfile'])
            self._client.set_list('/apps/gnome-orca/startingProfile',
                                    gconf.VALUE_STRING,
                                    self.prefsDict['startingProfile'])
            activeProfileName = self.prefsDict['activeProfile'][1]
            self._client.set_list('/apps/gnome-orca/%s/profile' % activeProfileName,
                                    gconf.VALUE_STRING,
                                    self.prefsDict['activeProfile'])
            self.__app_key += '/%s' % activeProfileName

            for key in settings.userCustomizableSettings:
                if key not in ['voices', 'firstStart', 'speechServerInfo']:
                    self.prefsDict[key] = self._getValueForKey(self.prefsDict, key)
                if key in self.need2repr:
                    self.prefsDict[key] = self._fix_quotes(self.prefsDict[key])

        if self.keyBindingsTreeModel:
            self.prefsDict['overridenKeyBindings'] = {}
            thisIter = self.keyBindingsTreeModel.get_iter_first()
            while thisIter != None:
                iterChild = self.keyBindingsTreeModel.iter_children(thisIter)
                while iterChild != None:
                    values = self.keyBindingsTreeModel.get(iterChild,
                                       0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
                    if values[MODIF] and not values[KEY1]  == None:
                        key = values[HANDLER]                         
                        self.prefsDict['overridenKeyBindings'][key] = [values[DESCRIP], \
                            values[MOD_MASK1], values[MOD_USED1], values[KEY1], \
                            values[CLICK_COUNT1], values[OLDTEXT1], values[TEXT1], \
                            values[MOD_MASK2], values[MOD_USED2], values[KEY2], \
                            values[CLICK_COUNT2], values[OLDTEXT2], values[TEXT2], \
                            values[MODIF], values[EDITABLE]]
                    iterChild = self.keyBindingsTreeModel.iter_next(iterChild)

                thisIter = self.keyBindingsTreeModel.iter_next(thisIter)
            # Clear overridenkeybindings gconf's dir for a safe store/load 
            self._client.recursive_unset(self.GCONF_BASE_DIR + '/overridenKeyBindings', 
                gconf.UNSET_INCLUDING_SCHEMA_NAMES)           
            self._client.suggest_sync()

        if self.pronunciationTreeModel:
            self.prefsDict['pronunciations'] = {}
            thisIter = self.pronunciationTreeModel.get_iter_first()

            while thisIter != None:
                values = self.pronunciationTreeModel.get(thisIter, ACTUAL, REPLACEMENT)
                word = values[ACTUAL]
                value = values[REPLACEMENT]

                if word != "" and value != "":
                    self.prefsDict['pronunciations'][word] = value
 
                thisIter = self.pronunciationTreeModel.iter_next(thisIter)

            # Clear pronunciations gconf's dir for a safe store/load 
            self._client.recursive_unset(self.GCONF_BASE_DIR + '/pronunciations',
                gconf.UNSET_INCLUDING_SCHEMA_NAMES)
            self._client.suggest_sync()
            

        self.gconf_save()

        self.prefsDict = self.options

        return self._enableAccessibility()

    def loadSettings(self):
        """Load settings"""
        
        # if not settings to load, save defaults
        #

        ## Now, if this the first orca exec, orca should
        #  show preferences dialog
        if not self._client.all_entries(self.__app_key):
            return False
        elif isFirstStart():
            path = '/apps/gnome-orca/startingProfile'
        else:
            path = '/apps/gnome-orca/activeProfile'
        profileKey = self._client.get_list(path, gconf.VALUE_STRING)
        self.__app_key += '/%s' % profileKey[1]
 
        self.gconf_load()

        # JD -> JO: What's up with these? Why are they (all) necessary?
        #
        self.settingsDict = self.prefsDict = self.options

        import orca.debug
        from orca import acss
        orca.debug.debugLevel = orca.debug.LEVEL_SEVERE

        voiceSettings = ['speechServerFactory', 'speechServerInfo', 'voices']
        for key in settings.userCustomizableSettings:
            value = self.settingsDict.get(key)
            #value = self._getValueForKey(self.settingsDict, key)
            if key in voiceSettings and not value:
                value = eval('settings.%s' % key)
            if value == None:
                continue

            if value in ['true', 'false']:
                value = value.capitalize()
            if key in self.need2repr:
                value = self._fix_quotes(value)
            setting = 'orca.settings.%s = %s' % (key, value)
            exec setting

        # Load orca.pronunciation_dict
        #
        import orca.pronunciation_dict

        if self.settingsDict.has_key('pronunciations'):
            orca.pronunciation_dict.pronunciation_dict = {}
            for key, value in self.settingsDict['pronunciations'].items():
                orca.pronunciation_dict.setPronunciation(str(key), str(value))

        import orca.orca_state

        # Load keybindings
        #
        #FIXME: This make no sense, we need to do another thing to overwrite
        # the overrideKeyBindings
        #settings.overrideKeyBindings = self.__loadOverridenKeyBindings

        try:
            reload(orca.orca_state.orcaCustomizations)
        except AttributeError:
            try:
                orca.orca_state.orcaCustomizations = __import__("orca-customizations")
            except ImportError:
                pass

        self.prefsDict = self.settingsDict

        return True

    def __loadOverridenKeyBindings(self, script, keyB):
        """Load overriden keybindings defined by user"""

        if len(self.prefsDict['overridenKeyBindings']) == 0: return keyB

        for key in self.prefsDict['overridenKeyBindings']:
            keyB.removeByHandler(script.inputEventHandlers[key])
            keyB.add(keybindings.KeyBinding(
                str(self.prefsDict['overridenKeyBindings'][key][3]),
                int(self.prefsDict['overridenKeyBindings'][key][1]),
                int(self.prefsDict['overridenKeyBindings'][key][2]),
                script.inputEventHandlers[key],
                int(self.prefsDict['overridenKeyBindings'][key][4])))
            if self.prefsDict['overridenKeyBindings'][key][9] != 'None' :
                keyB.add(keybindings.KeyBinding(
                    str(self.prefsDict['overridenKeyBindings'][key][9]),
                    int(self.prefsDict['overridenKeyBindings'][key][7]),
                    int(self.prefsDict['overridenKeyBindings'][key][8]),
                    script.inputEventHandlers[key],
                    int(self.prefsDict['overridenKeyBindings'][key][10])))

        return keyB

    def _fix_quotes(self, value):
        """Checks for quotes and return a valid loadable setting"""

        new_value = value.replace("\'", "").replace("\"", "").replace("\\", "")
        if value.startswith("\""):
            return "\"%s\"" % new_value
        else:
            return "'%s'" % new_value
        
    def availableProfiles(self):
        """Returns a list of available profiles
        It will be a list of strings list like this:
        ['Label', 'name']
        """

        profilesKeys = self._client.all_dirs(self.GCONF_BASE_DIR)
        profiles = []
        for profileKey in profilesKeys:
            name = profileKey.split('/')[-1]
            key = path + '/%s/profile' % name
            profile = self._client.get_list(key, gconf.VALUE_STRING)
            profiles.append(profile)
    
        return profiles

    def isFirstStart(self):
        """Check if the firstStart key is True or false"""
        firstStartPath = self.GCONF_BASE_DIR + '/firstStart'
        return self._client.get_bool(firstStartPath)
    
    def setFirstStart(self, value=False):
        """Set firstStart. This user-configurable settting is primarily
        intended to serve as an indication as to whether or not initial
        configuration is needed."""
        firstStartPath = self.GCONF_BASE_DIR + '/firstStart'
        self._client.set_bool(firstStartPath, value)
