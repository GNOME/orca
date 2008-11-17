# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Utilities to manage the writing of the user application specific
preferences files.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2007-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import os

import orca_prefs
import settings

class OrcaPrefs(orca_prefs.OrcaPrefs):

    def __init__(self, prefsDict, appName=None, appScript=None,
                 keyBindingsTreeModel=None,
                 pronunciationTreeModel=None):
        """Creates a new OrcaPrefs instance that will be used to write out
        application specific preferences.

        Arguments:
        - prefsDict: a dictionary where the keys are orca preferences
          names and the values are the values for the preferences.
        - appName: the application these preferences are for.
        - appScript: the application script.
        - keyBindingsTreeModel - key bindings tree model, or None if we are
          writing out console preferences.
        - pronunciationTreeModel - pronunciation dictionary tree model, or
          None if we are writing out console preferences.
        """

        orca_prefs.OrcaPrefs.__init__(self, prefsDict, keyBindingsTreeModel,
                                      pronunciationTreeModel)
        self.appName = appName
        self.appScript = appScript

    def _writeKeyBindingsPreamble(self, prefs):
        """Writes the preamble to the  ~/.orca/app-settings/<APPNAME>.py
        keyBindings section."""

        prefs.writelines("\n")
        prefs.writelines("# Set up a user key-bindings profile\n")
        prefs.writelines("#\n")
        prefs.writelines('def overrideAppKeyBindings(script, keyB):\n')

    def _writeAppKeyBindingsPostamble(self, prefs, appName, appScript):
        """Writes the postamble to the ~/.orca/app-settings/<APPNAME>.py
        keyBindings section.

        Arguments:
        - prefs: file handle for application preferences.
        - appName: the application these preferences are for.
        - appScript: the application script.
        """

        prefs.writelines('   return keyB')
        prefs.writelines("\n\n")

    def _writeAppKeyBindingsMap(self, prefs, appName, appScript, treeModel):
        """Write to an application specific configuration file 'prefs', the
        key bindings passed in the model treeModel.

        Arguments:
        - prefs: file handle for application preferences.
        - appName: the application these preferences are for.
        - appScript: the application script.
        - treeModel: key bindings treemodel.
        """

        self._writeKeyBindingsPreamble(prefs)
        self._iterateKeyBindings(prefs, treeModel)
        self._writeAppKeyBindingsPostamble(prefs, appName, appScript)

    def _writePronunciationsPreamble(self, prefs):
        """Writes the preamble to the  ~/.orca/app-settings/<APPNAME>.py
        pronunciations section."""

        prefs.writelines("\n")
        prefs.writelines("# User customized application specific ")
        prefs.writelines("pronunciation dictionary settings\n")
        prefs.writelines("#\n")
        prefs.writelines("import orca.pronunciation_dict\n\n")
        prefs.writelines( \
                    'def overridePronunciations(script, pronunciations):\n')

    def _writePronunciationsPostamble(self, prefs):
        """Writes the postamble to the ~/.orca/app-settings/<APPNAME>.py
        pronunciations section."""

        prefs.writelines('    return pronunciations')
        prefs.writelines("\n\n")
        prefs.writelines( \
            'orca.settings.overridePronunciations = overridePronunciations')
        prefs.writelines("\n")

    def _writePronunciation(self, prefs, word, value):
        """Write out a single pronunciation entry to the
        ~/.orca/app-settings/<APPNAME>.py settings file.

        Arguments:
        - prefs: file handle for application specific preferences.
        - word: the actual word to be pronunced.
        - value: the replace string to use.
        """

        prefs.writelines("    orca.pronunciation_dict.setPronunciation(" + \
                    repr(word) + ", " + repr(value) + ", pronunciations)\n")

    def _writePronunciationMap(self, prefs, treeModel):
        """Write to configuration file 'prefs' the new application specific
        pronunciation dictionary entries passed in the model treeModel.

        Arguments:
        - prefs: file handle for application preferences.
        - treeModel: pronunciation dictionary tree model.
        """

        self._writePronunciationsPreamble(prefs)
        self._iteratePronunciations(prefs, treeModel)
        self._writePronunciationsPostamble(prefs)

    def _writeAppPreferencesPreamble(self, prefs, appName):
        """Writes the preamble to the ~/.orca/app-settings/<APPNAME>.py file.

        Arguments:
        - prefs: file handle for application preferences.
        - appName: the application name.
        """

        prefs.writelines("# -*- coding: utf-8 -*-\n")
        prefs.writelines( \
                   "# %s.py - custom Orca application settings\n" % appName)
        prefs.writelines("# Generated by orca.  DO NOT EDIT THIS FILE!!!\n")
        prefs.writelines( \
                   "# If you want permanent customizations that will not\n")
        prefs.writelines( \
                 "# be overwritten, edit %s-customizations.py.\n" % appName)
        prefs.writelines("#\n")
        prefs.writelines("import orca.settings\n")
        prefs.writelines("import orca.acss\n")
        prefs.writelines("\n")

    def _writeAppPreferencesPostamble(self, prefs, appName):
        """Writes the postamble to the ~/.orca/app-settings/<APPNAME>.py file.

        Arguments:
        - prefs: file handle for application preferences.
        - appName: the application name.
        """

        prefs.writelines("\ntry:\n")
        prefs.writelines( \
           "    __import__(\"app-settings.%s-customizations\")\n" % appName)
        prefs.writelines("except ImportError:\n")
        prefs.writelines("    pass\n")

    def writePreferences(self):
        """Creates the directory and files to hold application specific
        user preferences.  Write out any preferences that are different
        from the generic Orca preferences for this user. Note that callers
        of this method may want to consider using an ordered dictionary so
        that the keys are output in a deterministic order.

        Returns True if the user needs to log out for accessibility
        settings to take effect.
        """

        self._setupPreferencesDirs()

        oldPrefsDict = orca_prefs.readPreferences()

        # Write ~/.orca/app-settings/<APPNAME>.py
        #
        orcaDir = settings.userPrefsDir
        orcaSettingsDir = os.path.join(orcaDir, "app-settings")
        appFileName = "%s.py" % self.appName
        prefs = open(os.path.join(orcaSettingsDir, appFileName), "w")
        self._writeAppPreferencesPreamble(prefs, self.appName)

        for key in settings.userCustomizableSettings:
            value = self._getValueForKey(self.prefsDict, key)
            oldValue = self._getValueForKey(oldPrefsDict, key)
            if oldValue != value:
                prefs.writelines("orca.settings.%s = %s\n" % (key, value))

        if self.keyBindingsTreeModel:
            self._writeAppKeyBindingsMap(prefs, self.appName, self.appScript,
                                         self.keyBindingsTreeModel)

        if self.pronunciationTreeModel:
            self._writePronunciationMap(prefs, self.pronunciationTreeModel)

        # Write out the application unique preferences (if any) and set the
        # new values.
        #
        self.appScript.setAppPreferences(prefs)

        self._writeAppPreferencesPostamble(prefs, self.appName)
        prefs.close()
        return False # no logout is needed

def writePreferences(prefsDict, appName=None, appScript=None,
                     keyBindingsTreeModel=None,
                     pronunciationTreeModel=None):
    """Creates the directory and files to hold application specific
    user preferences.  Write out any preferences that are different
    from the generic Orca preferences for this user. Note that callers
    of this method may want to consider using an ordered dictionary so
    that the keys are output in a deterministic order.

    Arguments:
    - prefsDict: a dictionary where the keys are orca preferences
    names and the values are the values for the preferences.
    - appName: the application these preferences are for.
    - appScript: the application script.
    - keyBindingsTreeModel - key bindings tree model, or None if we are
    writing out console preferences.
    - pronunciationTreeModel - pronunciation dictionary tree model, or
    None if we are writing out console preferences.

    Returns True if the user needs to log out for accessibility settings
    to take effect.
    """

    orcaPrefs = OrcaPrefs(prefsDict, appName, appScript, 
                          keyBindingsTreeModel, pronunciationTreeModel)
    return orcaPrefs.writePreferences()
