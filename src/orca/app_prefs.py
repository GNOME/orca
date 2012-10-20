# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

"""Utilities to manage the writing of the user application specific
preferences files.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2007-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import os
import pprint

from . import debug
from . import settings
from . import settings_manager

_settingsManager = settings_manager.getManager()

# The same fields than in orca_gui_prefs.py:
#
(HANDLER, DESCRIP, MOD_MASK1, MOD_USED1, KEY1, CLICK_COUNT1, OLDTEXT1, \
 TEXT1, MODIF, EDITABLE) = list(range(10))

(ACTUAL, REPLACEMENT) = list(range(2))

class OrcaPrefs:

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

        self.prefsDict = prefsDict
        self.keyBindingsTreeModel = keyBindingsTreeModel
        self.pronunciationTreeModel = pronunciationTreeModel
        self.appName = appName
        self.appScript = appScript

    def _writeKeyBindingsPreamble(self, prefs):
        """Writes the preamble to the
        XDG_DATA_HOME/orca/app-settings/<APPNAME>.py keyBindings section."""

        prefs.writelines("\n")
        prefs.writelines("# Set up a user key-bindings profile\n")
        prefs.writelines("#\n")
        prefs.writelines('def overrideAppKeyBindings(script, keyB):\n')

    def _writeKeyBinding(self, prefs, tupl):
        """Writes a single keyBinding to the user-settings.py
        keyBindings section.

        Arguments:
        - prefs: text string - file to write the key binding to.
        - tupl:    tuple     - a tuple with the values of the
                                 keybinding (Gtk.TreeStore model columns)
        """

        prefs.writelines("   keyB.removeByHandler(script.inputEventHandlers['" \
                         + str(tupl[HANDLER])+"'])\n")
        if not (tupl[TEXT1]):
            prefs.writelines("   keyB.add(orca.keybindings.KeyBinding(\n")
            prefs.writelines("      '',\n")
            prefs.writelines("      %d,\n" % settings.defaultModifierMask)
            prefs.writelines("      0,\n")
            prefs.writelines('      script.inputEventHandlers["' + \
                             str(tupl[HANDLER]) +'"]))\n\n')

        if (tupl[TEXT1]):
            prefs.writelines("   keyB.add(orca.keybindings.KeyBinding(\n")
            prefs.writelines("      '" + str(tupl[KEY1]) + "',\n")
            if tupl[MOD_MASK1] or tupl[MOD_USED1]:
                prefs.writelines("      " + str(tupl[MOD_MASK1]) + ",\n")
                prefs.writelines("      " + str(tupl[MOD_USED1]) + ",\n")
            else:
                prefs.writelines("      0,\n")
                prefs.writelines("      0,\n")
            if (tupl[CLICK_COUNT1] == "1"):
                prefs.writelines('      script.inputEventHandlers["' + \
                                 str(tupl[HANDLER]) +'"]))\n\n')
            else:
                prefs.writelines('      script.inputEventHandlers["' + \
                                 str(tupl[HANDLER]) +'"],\n')
                prefs.writelines("      " + str(tupl[CLICK_COUNT1])  + \
                                 "))\n\n")

    def _writeAppKeyBindingsPostamble(self, prefs, appName, appScript):
        """Writes the postamble to the
        XDG_DATA_HOME/orca/app-settings/<APPNAME>.py keyBindings section.

        Arguments:
        - prefs: file handle for application preferences.
        - appName: the application these preferences are for.
        - appScript: the application script.
        """

        prefs.writelines('   return keyB')
        prefs.writelines("\n\n")

    def _iterateKeyBindings(self, prefs, treeModel):
        """Iterate over all the key bindings in the tree model and write
        out all that the user has modified.
        """

        thisIter = treeModel.get_iter_first()
        while thisIter != None:
            iterChild = treeModel.iter_children(thisIter)
            while iterChild != None:
                values = treeModel.get(iterChild, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
                if values[MODIF]:
                    self._writeKeyBinding(prefs, values)
                iterChild = treeModel.iter_next(iterChild)
            thisIter = treeModel.iter_next(thisIter)

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
        try:
            self._iterateKeyBindings(prefs, treeModel)
        except:
            debug.println(debug.LEVEL_FINEST, "FAILURE: _iterateKeyBindings")
            debug.printException(debug.LEVEL_FINEST)
        self._writeAppKeyBindingsPostamble(prefs, appName, appScript)

    def _writePronunciationsPreamble(self, prefs):
        """Writes the preamble to the
        XDG_DATA_HOME/orca/app-settings/<APPNAME>.py pronunciations section."""

        prefs.writelines("\n")
        prefs.writelines("# User customized application specific ")
        prefs.writelines("pronunciation dictionary settings\n")
        prefs.writelines("#\n")
        prefs.writelines("import orca.pronunciation_dict\n\n")
        prefs.writelines( \
                    'def overridePronunciations(script, pronunciations):\n')

    def _writePronunciationsPostamble(self, prefs):
        """Writes the postamble to the
        XDG_DATA_HOME/orca/app-settings/<APPNAME>.py pronunciations section."""

        prefs.writelines('    return pronunciations')
        prefs.writelines("\n\n")
        prefs.writelines( \
            'orca.settings.overridePronunciations = overridePronunciations')
        prefs.writelines("\n")

    def _writePronunciation(self, prefs, word, value):
        """Write out a single pronunciation entry to the
        XDG_DATA_HOME/orca/app-settings/<APPNAME>.py settings file.

        Arguments:
        - prefs: file handle for application specific preferences.
        - word: the actual word to be pronunced.
        - value: the replace string to use.
        """

        prefs.writelines("    orca.pronunciation_dict.setPronunciation(" + \
                    repr(word) + ", " + repr(value) + ", pronunciations)\n")

    def _iteratePronunciations(self, prefs, treeModel):
        """Iterate over each of the entries in the tree model and write out
        a pronunciation diction entry for them.  If any strings with an
        actual string of "" are found, they are ignored.
        """

        thisIter = treeModel.get_iter_first()
        while thisIter != None:
            values = treeModel.get(thisIter, ACTUAL, REPLACEMENT)
            word = values[ACTUAL]
            value = values[REPLACEMENT]

            if word != "":
                self._writePronunciation(prefs, word, value)

            thisIter = treeModel.iter_next(thisIter)

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
        """Writes the preamble to the
        XDG_DATA_HOME/orca/app-settings/<APPNAME>.py file.

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
        prefs.writelines("import importlib\n")
        prefs.writelines("import orca.settings\n")
        prefs.writelines("import orca.acss\n")
        prefs.writelines("\n")

    def _writeAppPreferencesPostamble(self, prefs, appName):
        """Writes the postamble to the
        XDG_DATA_HOME/orca/app-settings/<APPNAME>.py file.

        Arguments:
        - prefs: file handle for application preferences.
        - appName: the application name.
        """

        prefs.writelines("\ntry:\n")
        prefs.writelines( \
           "    importlib.import_module(\"app-settings.%s-customizations\")\n" % appName)
        prefs.writelines("except ImportError:\n")
        prefs.writelines("    pass\n")

    def _getSpeechServerFactoryString(self, factory):
        """Returns a string that represents the speech server factory passed in.

        Arguments:
        - factory: the speech server factory

        Returns a string suitable for the preferences file.
        """

        if not factory:
            return None
        elif isinstance(factory, basestring):
            return "'%s'" % factory
        else:
            return "'%s'" % factory.__name__

    def _getSpeechServerString(self, server):
        """Returns a string that represents the speech server passed in.

        Arguments:
        - server: a speech server

        Returns a string suitable for the preferences file.
        """
        if not server:
            return None
        elif isinstance(server, [].__class__):
            return repr(server)
        else:
            return repr(server.getInfo())

    def _getVoicesString(self, voices):
        """Returns a string that represents the list of voices passed in.

        Arguments:
        - voices: a list of ACSS instances.

        Returns a string suitable for the preferences file.
        """

        voicesStr = "{\n"
        for voice in voices:
            # Hack to deal with the fact that we're creating a string from
            # a setting in which dictionary keys may be in unicode. This
            # later causes equality checks to fail. Such nonsense should
            # go away when app settings are also fully managed by the
            # settings manager.
            voiceDict = voices[voice]
            newDict = {}
            for key, value in list(voiceDict.items()):
                newDict[str(key)] = value
            voicesStr += "'%s' : orca.acss.ACSS(" % voice
            voicesStr += pprint.pformat(newDict) + "),\n"
        voicesStr += "}"

        return voicesStr

    def _getKeyboardLayoutString(self, keyboardLayout):
        """Returns a string that represents the keyboard layout passed in."""

        if keyboardLayout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            return "orca.settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP"
        else:
            return "orca.settings.GENERAL_KEYBOARD_LAYOUT_LAPTOP"

    def _getOrcaModifierKeysString(self, orcaModifierKeys):
        """Returns a string that represents the Orca modifier keys passed in."""

        return "%s" % orcaModifierKeys

    def _getSpokenTextAttributesString(self, enabledSpokenTextAttributes):
        """ Returns a string that represents the enabled spoken text attributes
        passed in.
        """

        return "\"" + enabledSpokenTextAttributes + "\""

    def _getBrailledTextAttributesString(self, enabledBrailledTextAttributes):
        """ Returns a string that represents the enabled brailled text
        attributes passed in.
        """

        return "\"" + enabledBrailledTextAttributes + "\""

    def _getTextAttributesBrailleIndicatorString(self, brailleIndicator):
        """Returns a string that represents the text attribute braille indicator
        value passed in."""

        if brailleIndicator == settings.TEXT_ATTR_BRAILLE_NONE:
            return "orca.settings.TEXT_ATTR_BRAILLE_NONE"
        elif brailleIndicator == settings.TEXT_ATTR_BRAILLE_7:
            return "orca.settings.TEXT_ATTR_BRAILLE_7"
        elif brailleIndicator == settings.TEXT_ATTR_BRAILLE_8:
            return "orca.settings.TEXT_ATTR_BRAILLE_8"
        elif brailleIndicator == settings.TEXT_ATTR_BRAILLE_BOTH:
            return "orca.settings.TEXT_ATTR_BRAILLE_BOTH"
        else:
            return "orca.settings.TEXT_ATTR_BRAILLE_NONE"

    def _getBrailleSelectionIndicatorString(self, selectionIndicator):
        """Returns a string that represents the braille selection indicator
        value passed in."""

        if selectionIndicator == settings.BRAILLE_SEL_NONE:
            return "orca.settings.BRAILLE_SEL_NONE"
        elif selectionIndicator == settings.BRAILLE_SEL_7:
            return "orca.settings.BRAILLE_SEL_7"
        elif selectionIndicator == settings.BRAILLE_SEL_8:
            return "orca.settings.BRAILLE_SEL_8"
        elif selectionIndicator == settings.BRAILLE_SEL_BOTH:
            return "orca.settings.BRAILLE_SEL_BOTH"
        else:
            return "orca.settings.BRAILLE_SEL_NONE"

    def _getBrailleLinkIndicatorString(self, linkIndicator):
        """Returns a string that represents the braille link indicator
        value passed in."""

        if linkIndicator == settings.BRAILLE_LINK_NONE:
            return "orca.settings.BRAILLE_LINK_NONE"
        elif linkIndicator == settings.BRAILLE_LINK_7:
            return "orca.settings.BRAILLE_LINK_7"
        elif linkIndicator == settings.BRAILLE_LINK_8:
            return "orca.settings.BRAILLE_LINK_8"
        elif linkIndicator == settings.BRAILLE_LINK_BOTH:
            return "orca.settings.BRAILLE_LINK_BOTH"
        else:
            return "orca.settings.BRAILLE_LINK_NONE"

    def _getVerbosityString(self, verbosityLevel):
        """Returns a string that represents the verbosity level passed in."""

        if verbosityLevel == settings.VERBOSITY_LEVEL_BRIEF:
            return "orca.settings.VERBOSITY_LEVEL_BRIEF"
        elif verbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            return "orca.settings.VERBOSITY_LEVEL_VERBOSE"
        else:
            return "orca.settings.VERBOSITY_LEVEL_VERBOSE"

    def _getBrailleRolenameStyleString(self, rolenameStyle):
        """Returns a string that represents the rolename style passed in."""

        if rolenameStyle == settings.BRAILLE_ROLENAME_STYLE_SHORT:
            return "orca.settings.BRAILLE_ROLENAME_STYLE_SHORT"
        elif rolenameStyle == settings.BRAILLE_ROLENAME_STYLE_LONG:
            return "orca.settings.BRAILLE_ROLENAME_STYLE_LONG"
        else:
            return "orca.settings.BRAILLE_ROLENAME_STYLE_LONG"

    def _getBrailleAlignmentStyleString(self, brailleAlignmentStyle):
        """Returns a string that represents the brailleAlignmentStyle
         passed in."""

        if brailleAlignmentStyle == settings.ALIGN_BRAILLE_BY_WORD:
            return "orca.settings.ALIGN_BRAILLE_BY_WORD"
        if brailleAlignmentStyle == settings.ALIGN_BRAILLE_BY_MARGIN:
            return "orca.settings.ALIGN_BRAILLE_BY_MARGIN"
        else:
            return "orca.settings.ALIGN_BRAILLE_BY_EDGE"

    def _getVerbalizePunctuationStyleString(self, punctuationStyle):
        """Returns a string that represents the punctuation style passed in."""

        if punctuationStyle == settings.PUNCTUATION_STYLE_NONE:
            return "orca.settings.PUNCTUATION_STYLE_NONE"
        elif punctuationStyle == settings.PUNCTUATION_STYLE_SOME:
            return "orca.settings.PUNCTUATION_STYLE_SOME"
        elif punctuationStyle == settings.PUNCTUATION_STYLE_MOST:
            return "orca.settings.PUNCTUATION_STYLE_MOST"
        elif punctuationStyle == settings.PUNCTUATION_STYLE_ALL:
            return "orca.settings.PUNCTUATION_STYLE_ALL"
        else:
            return "orca.settings.PUNCTUATION_STYLE_ALL"

    def _getPresentTimeString(self, val):
        if val == settings.TIME_FORMAT_24_HMS:
            return "orca.settings.TIME_FORMAT_24_HMS"
        elif val == settings.TIME_FORMAT_24_HMS_WITH_WORDS:
            return "orca.settings.TIME_FORMAT_24_HMS_WITH_WORDS"
        elif val == settings.TIME_FORMAT_24_HM:
            return "orca.settings.TIME_FORMAT_24_HM"
        elif val == settings.TIME_FORMAT_24_HM_WITH_WORDS:
            return "orca.settings.TIME_FORMAT_24_HM_WITH_WORDS"
        else:
            return "orca.settings.TIME_FORMAT_LOCALE"

    def _getPresentDateString(self, val):
        if val == settings.DATE_FORMAT_NUMBERS_DM:
            return "orca.settings.DATE_FORMAT_NUMBERS_DM"
        elif val == settings.DATE_FORMAT_NUMBERS_MD:
            return "orca.settings.DATE_FORMAT_NUMBERS_MD"
        elif val == settings.DATE_FORMAT_NUMBERS_DMY:
            return "orca.settings.DATE_FORMAT_NUMBERS_DMY"
        elif val == settings.DATE_FORMAT_NUMBERS_MDY:
            return "orca.settings.DATE_FORMAT_NUMBERS_MDY"
        elif val == settings.DATE_FORMAT_NUMBERS_YMD:
            return "orca.settings.DATE_FORMAT_NUMBERS_YMD"
        elif val == settings.DATE_FORMAT_FULL_DM:
            return "orca.settings.DATE_FORMAT_FULL_DM"
        elif val == settings.DATE_FORMAT_FULL_MD:
            return "orca.settings.DATE_FORMAT_FULL_MD"
        elif val == settings.DATE_FORMAT_FULL_DMY:
            return "orca.settings.DATE_FORMAT_FULL_DMY"
        elif val == settings.DATE_FORMAT_FULL_MDY:
            return "orca.settings.DATE_FORMAT_FULL_MDY"
        elif val == settings.DATE_FORMAT_FULL_YMD:
            return "orca.settings.DATE_FORMAT_FULL_YMD"
        elif val == settings.DATE_FORMAT_ABBREVIATED_DM:
            return "orca.settings.DATE_FORMAT_ABBREVIATED_DM"
        elif val == settings.DATE_FORMAT_ABBREVIATED_MD:
            return "orca.settings.DATE_FORMAT_ABBREVIATED_MD"
        elif val == settings.DATE_FORMAT_ABBREVIATED_DMY:
            return "orca.settings.DATE_FORMAT_ABBREVIATED_DMY"
        elif val == settings.DATE_FORMAT_ABBREVIATED_MDY:
            return "orca.settings.DATE_FORMAT_ABBREVIATED_MDY"
        elif val == settings.DATE_FORMAT_ABBREVIATED_YMD:
            return "orca.settings.DATE_FORMAT_ABBREVIATED_YMD"
        else:
            return "orca.settings.DATE_FORMAT_LOCALE"

    def _getSayAllStyleString(self, sayAllStyle):
        """Returns a string that represents the say all style passed in."""

        if sayAllStyle == settings.SAYALL_STYLE_LINE:
            return "orca.settings.SAYALL_STYLE_LINE"
        elif sayAllStyle == settings.SAYALL_STYLE_SENTENCE:
            return "orca.settings.SAYALL_STYLE_SENTENCE"

    def _getProgressBarVerbosityString(self, verbosityLevel):
        """Returns a string that represents the progress bar verbosity level
        passed in.

        Arguments:
        - verbosityLevel: verbosity level for progress bars.

        Returns a string suitable for the preferences file.
        """

        if verbosityLevel == settings.PROGRESS_BAR_ALL:
            return "orca.settings.PROGRESS_BAR_ALL"
        elif verbosityLevel == settings.PROGRESS_BAR_WINDOW:
            return "orca.settings.PROGRESS_BAR_WINDOW"
        else:
            return "orca.settings.PROGRESS_BAR_APPLICATION"

    def _getValueForKey(self, prefsDict, key):
        """Return the value associated with this preferences dictionary key

        Arguments:
        - prefsDict: a dictionary where the keys are orca preferences
        names and the values are the values for the preferences.
        - key: the preferences dictionary key.

        Return the value of the given preferences dictionary key.
        """

        value = None
        if key in prefsDict:
            if key == "voices":
                value = self._getVoicesString(prefsDict[key])
            elif key == "speechServerInfo":
                value = self._getSpeechServerString(prefsDict[key])
            elif key == "speechServerFactory":
                value = self._getSpeechServerFactoryString(prefsDict[key])
            elif key.endswith("VerbosityLevel"):
                value = self._getVerbosityString(prefsDict[key])
            elif key == "brailleRolenameStyle":
                value = self._getBrailleRolenameStyleString(prefsDict[key])
            elif key == "brailleSelectorIndicator":
                value = self._getBrailleSelectionIndicatorString(prefsDict[key])
            elif key == "brailleLinkIndicator":
                value = self._getBrailleLinkIndicatorString(prefsDict[key])
            elif key == "brailleAlignmentStyle":
                value = self._getBrailleAlignmentStyleString(prefsDict[key])
            elif key == "verbalizePunctuationStyle":
                value = self._getVerbalizePunctuationStyleString(prefsDict[key])
            elif key == "presentDateFormat":
                value = self._getPresentDateString(prefsDict[key])
            elif key == "presentTimeFormat":
                value = self._getPresentTimeString(prefsDict[key])
            elif key == "sayAllStyle":
                value = self._getSayAllStyleString(prefsDict[key])
            elif key == "keyboardLayout":
                value = self._getKeyboardLayoutString(prefsDict[key])
            elif key == "orcaModifierKeys":
                value = self._getOrcaModifierKeysString(prefsDict[key])
            elif key == "enabledSpokenTextAttributes":
                value = self._getSpokenTextAttributesString(prefsDict[key])
            elif key == "enabledBrailledTextAttributes":
                value = self._getBrailledTextAttributesString(prefsDict[key])
            elif key == "textAttributesBrailleIndicator":
                value = self._getTextAttributesBrailleIndicatorString( \
                                                              prefsDict[key])
            elif key == "progressBarVerbosity":
                value = self._getProgressBarVerbosityString(prefsDict[key])
            elif key == "brailleContractionTable":
                value = "'%s'" % prefsDict[key]
            elif key == "brailleEOLIndicator":
                value = "'%s'" % prefsDict[key]
            elif key == "brailleRequiredStateString":
                value = "'%s'" % prefsDict[key]
            elif key == "speechRequiredStateString":
                value = "'%s'" % prefsDict[key]
            else:
                value = prefsDict[key]

        return value

    @staticmethod
    def valueChanged(oldValue, newValue):
        """Work around for the fact that some settings are lists/dictionaries
        stored as strings in which the original list/dictionary contents might
        be strings or might be unicode."""

        if oldValue == newValue:
            return False

        try:
            return eval(oldValue) != eval(newValue)
        except:
            return True

    @staticmethod
    def readPreferences():
        """Returns a dictionary containing the names and values of the
        customizable features of Orca."""

        prefsDict = {}
        for key in settings.userCustomizableSettings:
            try:
                prefsDict[key] = getattr(settings, key)
            except:
                pass

        return prefsDict

    def writePreferences(self):
        """Creates the directory and files to hold application specific
        user preferences.  Write out any preferences that are different
        from the generic Orca preferences for this user. Note that callers
        of this method may want to consider using an ordered dictionary so
        that the keys are output in a deterministic order.

        Returns True if the user needs to log out for accessibility
        settings to take effect.
        """

        oldPrefsDict = self.readPreferences()

        # Write XDG_DATA_HOME/orca/app-settings/<APPNAME>.py
        #
        orcaDir = _settingsManager.getPrefsDir()
        orcaSettingsDir = os.path.join(orcaDir, "app-settings")
        appFileName = "%s.py" % self.appName
        prefs = open(os.path.join(orcaSettingsDir, appFileName), "w")
        self._writeAppPreferencesPreamble(prefs, self.appName)

        for key in settings.userCustomizableSettings:
            value = self._getValueForKey(self.prefsDict, key)
            oldValue = self._getValueForKey(oldPrefsDict, key)
            if self.valueChanged(oldValue, value):
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
