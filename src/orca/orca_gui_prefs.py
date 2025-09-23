# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Displays a GUI for the user to set Orca preferences."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atspi

import os
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Pango
import time

from . import acss
from . import debug
from . import event_manager
from . import guilabels
from . import messages
from . import orca
from . import orca_gtkbuilder
from . import orca_gui_profile
from . import orca_platform # pylint: disable=no-name-in-module
from . import script_manager
from . import settings
from . import settings_manager
from . import input_event
from . import input_event_manager
from . import keybindings
from . import pronunciation_dict
from . import braille
from . import speech_and_verbosity_manager
from . import speechserver
from .ax_object import AXObject
from .ax_text import AXText, AXTextAttribute

try:
    import louis
except ImportError:
    louis = None
from .orca_platform import tablesdir  # pylint: disable=import-error
if louis and not tablesdir:
    louis = None

(HANDLER, DESCRIP, MOD_MASK1, MOD_USED1, KEY1, CLICK_COUNT1, OLDTEXT1, \
 TEXT1, MODIF, EDITABLE) = list(range(10))

(NAME, IS_SPOKEN, IS_BRAILLED, VALUE) = list(range(4))

(ACTUAL, REPLACEMENT) = list(range(2))

# Must match the order of voice types in the GtkBuilder file.
#
(DEFAULT, UPPERCASE, HYPERLINK, SYSTEM) = list(range(4))

# Must match the order that the timeFormatCombo is populated.
#
(TIME_FORMAT_LOCALE, TIME_FORMAT_12_HM, TIME_FORMAT_12_HMS, TIME_FORMAT_24_HMS,
 TIME_FORMAT_24_HMS_WITH_WORDS, TIME_FORMAT_24_HM,
 TIME_FORMAT_24_HM_WITH_WORDS) = list(range(7))

# Must match the order that the dateFormatCombo is populated.
#
(DATE_FORMAT_LOCALE, DATE_FORMAT_NUMBERS_DM, DATE_FORMAT_NUMBERS_MD,
 DATE_FORMAT_NUMBERS_DMY, DATE_FORMAT_NUMBERS_MDY, DATE_FORMAT_NUMBERS_YMD,
 DATE_FORMAT_FULL_DM, DATE_FORMAT_FULL_MD, DATE_FORMAT_FULL_DMY,
 DATE_FORMAT_FULL_MDY, DATE_FORMAT_FULL_YMD, DATE_FORMAT_ABBREVIATED_DM,
 DATE_FORMAT_ABBREVIATED_MD, DATE_FORMAT_ABBREVIATED_DMY,
 DATE_FORMAT_ABBREVIATED_MDY, DATE_FORMAT_ABBREVIATED_YMD) = list(range(16))

class OrcaSetupGUI(orca_gtkbuilder.GtkBuilderWrapper):

    DIALOG = None

    def __init__(self, script, prefsDict):
        """Initialize the Orca configuration GUI."""

        if OrcaSetupGUI.DIALOG is not None:
            return

        fileName = os.path.join(orca_platform.datadir, orca_platform.package, "ui","orca-setup.ui")
        orca_gtkbuilder.GtkBuilderWrapper.__init__(self, fileName, "orcaSetupWindow")
        self.prefsDict = prefsDict

        self._defaultProfile = ['Default', 'default']
        self.bbindings = None
        self.cellRendererText = None
        self.defaultVoice = None
        self.disableKeyGrabPref = None
        self.getTextAttributesView = None
        self.hyperlinkVoice = None
        self.initializingSpeech = None
        self.kbindings = None
        self.keyBindingsModel = None
        self.keyBindView = None
        self.newBinding = None
        self.pendingKeyBindings = None
        self.planeCellRendererText = None
        self.pronunciationModel = None
        self.pronunciationView = None
        self.screenHeight = None
        self.screenWidth = None
        self.speechFamiliesChoice = None
        self.speechFamiliesChoices = None
        self.speechFamiliesModel = None
        self.speechLanguagesChoice = None
        self.speechLanguagesChoices = None
        self.speechLanguagesModel = None
        self.speechFamilies = []
        self.speechServersChoice = None
        self.speechServersChoices = None
        self.speechServersModel = None
        self.speechSystemsChoice = None
        self.speechSystemsChoices = None
        self.speechSystemsModel = None
        self.systemVoice = None
        self.uppercaseVoice = None
        self.window = None
        self.workingFactories = None
        self.savedGain = None
        self.savedPitch = None
        self.savedRate = None
        self.typing_echo_grid = None
        self._isInitialSetup = False
        self.selectedFamilyChoices = {}
        self.selectedLanguageChoices = {}
        self.profilesCombo = None
        self.profilesComboModel = None
        self.startingProfileCombo = None
        self._capturedKey = []
        self.script = script
        self.init()
        self._pending_already_bound_message_id = None

    def init(self):
        """Initialize the Orca configuration GUI. Read the users current
        set of preferences and set the GUI state to match. Setup speech
        support and populate the combo box lists on the Speech Tab pane
        accordingly.
        """

        if OrcaSetupGUI.DIALOG is not None:
            return

        # Restore the default rate/pitch/gain,
        # in case the user played with the sliders.
        #
        try:
            voices = settings_manager.get_manager().get_setting('voices')
            defaultVoice = voices[settings.DEFAULT_VOICE]
        except KeyError:
            defaultVoice = {}
        try:
            self.savedGain = defaultVoice[acss.ACSS.GAIN]
        except KeyError:
            self.savedGain = 10.0
        try:
            self.savedPitch = defaultVoice[acss.ACSS.AVERAGE_PITCH]
        except KeyError:
            self.savedPitch = 5.0
        try:
            self.savedRate = defaultVoice[acss.ACSS.RATE]
        except KeyError:
            self.savedRate = 50.0

        # ***** Key Bindings treeview initialization *****

        self.keyBindView = self.get_widget("keyBindingsTreeview")

        if self.keyBindView.get_columns():
            for column in self.keyBindView.get_columns():
                self.keyBindView.remove_column(column)

        self.keyBindingsModel = Gtk.TreeStore(
            GObject.TYPE_STRING,  # Handler name
            GObject.TYPE_STRING,  # Human Readable Description
            GObject.TYPE_STRING,  # Modifier mask 1
            GObject.TYPE_STRING,  # Used Modifiers 1
            GObject.TYPE_STRING,  # Modifier key name 1
            GObject.TYPE_STRING,  # Click count 1
            GObject.TYPE_STRING,  # Original Text of the Key Binding Shown 1
            GObject.TYPE_STRING,  # Text of the Key Binding Shown 1
            GObject.TYPE_BOOLEAN, # Key Modified by User
            GObject.TYPE_BOOLEAN) # Row with fields editable or not

        self.planeCellRendererText = Gtk.CellRendererText()

        self.cellRendererText = Gtk.CellRendererText()
        self.cellRendererText.set_property("ellipsize", Pango.EllipsizeMode.END)

        # HANDLER - invisble column
        #
        column = Gtk.TreeViewColumn("Handler",
                                    self.planeCellRendererText,
                                    text=HANDLER)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(HANDLER)
        self.keyBindView.append_column(column)

        # DESCRIP
        #
        column = Gtk.TreeViewColumn(guilabels.KB_HEADER_FUNCTION,
                                    self.cellRendererText,
                                    text=DESCRIP)
        column.set_resizable(True)
        column.set_min_width(380)
        column.set_sort_column_id(DESCRIP)
        self.keyBindView.append_column(column)

        # MOD_MASK1 - invisble column
        #
        column = Gtk.TreeViewColumn("Mod.Mask 1",
                                    self.planeCellRendererText,
                                    text=MOD_MASK1)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MOD_MASK1)
        self.keyBindView.append_column(column)

        # MOD_USED1 - invisble column
        #
        column = Gtk.TreeViewColumn("Use Mod.1",
                                    self.planeCellRendererText,
                                    text=MOD_USED1)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MOD_USED1)
        self.keyBindView.append_column(column)

        # KEY1 - invisble column
        #
        column = Gtk.TreeViewColumn("Key1",
                                    self.planeCellRendererText,
                                    text=KEY1)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(KEY1)
        self.keyBindView.append_column(column)

        # CLICK_COUNT1 - invisble column
        #
        column = Gtk.TreeViewColumn("ClickCount1",
                                    self.planeCellRendererText,
                                    text=CLICK_COUNT1)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(CLICK_COUNT1)
        self.keyBindView.append_column(column)

        # OLDTEXT1 - invisble column which will store a copy of the
        # original keybinding in TEXT1 prior to the Apply or OK
        # buttons being pressed.  This will prevent automatic
        # resorting each time a cell is edited.
        #
        column = Gtk.TreeViewColumn("OldText1",
                                    self.planeCellRendererText,
                                    text=OLDTEXT1)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(OLDTEXT1)
        self.keyBindView.append_column(column)

        # TEXT1
        #
        rendererText = Gtk.CellRendererText()
        rendererText.connect("editing-started",
                             self.editingKey,
                             self.keyBindingsModel)
        rendererText.connect("editing-canceled",
                             self.editingCanceledKey)
        rendererText.connect('edited',
                             self.editedKey,
                             self.keyBindingsModel,
                             MOD_MASK1, MOD_USED1, KEY1, CLICK_COUNT1, TEXT1)

        column = Gtk.TreeViewColumn(guilabels.KB_HEADER_KEY_BINDING,
                                    rendererText,
                                    text=TEXT1,
                                    editable=EDITABLE)

        column.set_resizable(True)
        column.set_sort_column_id(OLDTEXT1)
        self.keyBindView.append_column(column)

        # MODIF
        #
        rendererToggle = Gtk.CellRendererToggle()
        rendererToggle.connect('toggled',
                               self.keyModifiedToggle,
                               self.keyBindingsModel,
                               MODIF)
        column = Gtk.TreeViewColumn(guilabels.KB_MODIFIED,
                                    rendererToggle,
                                    active=MODIF,
                                    activatable=EDITABLE)
        #column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MODIF)
        self.keyBindView.append_column(column)

        # EDITABLE - invisble column
        #
        rendererToggle = Gtk.CellRendererToggle()
        rendererToggle.set_property('activatable', False)
        column = Gtk.TreeViewColumn("Modified",
                                    rendererToggle,
                                    active=EDITABLE)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(EDITABLE)
        self.keyBindView.append_column(column)

        # Populates the treeview with all the keybindings:
        #
        self._populateKeyBindings()

        self.window = self.get_widget("orcaSetupWindow")

        presenter = self.script.get_typing_echo_presenter()
        self.typing_echo_grid = presenter.create_preferences_grid()
        notebook = self.get_widget("notebook")
        echo_label = Gtk.Label(label=guilabels.TABS_ECHO)
        echo_label.show()
        notebook.insert_page(self.typing_echo_grid, echo_label, 4)

        self.speechSystemsModel  = \
                        self._initComboBox(self.get_widget("speechSystems"))
        self.speechServersModel  = \
                        self._initComboBox(self.get_widget("speechServers"))
        self.speechLanguagesModel = \
                        self._initComboBox(self.get_widget("speechLanguages"))
        self.speechFamiliesModel = \
                        self._initComboBox(self.get_widget("speechFamilies"))
        self._initSpeechState()

        # TODO - JD: Will this ever be the case??
        self._isInitialSetup = \
            not os.path.exists(settings_manager.get_manager().get_prefs_dir())

        appPage = self.script.get_app_preferences_gui()
        if appPage:
            label = Gtk.Label(label=AXObject.get_name(self.script.app))
            self.get_widget("notebook").append_page(appPage, label)

        self._initGUIState()

    def _getACSSForVoiceType(self, voiceType):
        """Return the ACSS value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM

        Returns the voice dictionary for the given voice type.
        """

        if voiceType == DEFAULT:
            voiceACSS = self.defaultVoice
        elif voiceType == UPPERCASE:
            voiceACSS = self.uppercaseVoice
        elif voiceType == HYPERLINK:
            voiceACSS = self.hyperlinkVoice
        elif voiceType == SYSTEM:
            voiceACSS = self.systemVoice
        else:
            voiceACSS = self.defaultVoice

        return voiceACSS

    def writeUserPreferences(self):
        """Write out the user's generic Orca preferences.
        """
        settings.speechSystemOverride = None
        pronunciationDict = self.getModelDict(self.pronunciationModel)
        keyBindingsDict = self.getKeyBindingsModelDict(self.keyBindingsModel)

        self.prefsDict.update(self.script.get_preferences_from_gui())
        settings_manager.get_manager().save_settings(
            self.script, self.prefsDict, pronunciationDict, keyBindingsDict)

    def _getKeyValueForVoiceType(self, voiceType, key, useDefault=True):
        """Look for the value of the given key in the voice dictionary
           for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM
        - key: the key to look for in the voice dictionary.
        - useDefault: if True, and the key isn't found for the given voice
                      type, the look for it in the default voice dictionary
                      as well.

        Returns the value of the given key, or None if it's not set.
        """

        if voiceType == DEFAULT:
            voice = self.defaultVoice
        elif voiceType == UPPERCASE:
            voice = self.uppercaseVoice
            if key not in voice:
                if not useDefault:
                    return None
                voice = self.defaultVoice
        elif voiceType == HYPERLINK:
            voice = self.hyperlinkVoice
            if key not in voice:
                if not useDefault:
                    return None
                voice = self.defaultVoice
        elif voiceType == SYSTEM:
            voice = self.systemVoice
            if key not in voice:
                if not useDefault:
                    return None
                voice = self.defaultVoice
        else:
            voice = self.defaultVoice

        if key in voice:
            return voice[key]
        else:
            return None

    def _getFamilyNameForVoiceType(self, voiceType):
        """Gets the name of the voice family for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM

        Returns the name of the voice family for the given voice type,
        or None if not set.
        """

        familyName = None
        family = self._getKeyValueForVoiceType(voiceType, acss.ACSS.FAMILY)

        if family and speechserver.VoiceFamily.NAME in family:
            familyName = family[speechserver.VoiceFamily.NAME]

        return familyName

    def _setFamilyNameForVoiceType(self, voiceType, name, language, dialect, variant):
        """Sets the name of the voice family for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM
        - name: the name of the voice family to set.
        - language: the locale of the voice family to set.
        - dialect: the dialect of the voice family to set.
        """

        family = self._getKeyValueForVoiceType(voiceType,
                                               acss.ACSS.FAMILY,
                                               False)

        voiceACSS = self._getACSSForVoiceType(voiceType)
        if family:
            family[speechserver.VoiceFamily.NAME] = name
            family[speechserver.VoiceFamily.LANG] = language
            family[speechserver.VoiceFamily.DIALECT] = dialect
            family[speechserver.VoiceFamily.VARIANT] = variant
        else:
            voiceACSS[acss.ACSS.FAMILY] = {}
            voiceACSS[acss.ACSS.FAMILY][speechserver.VoiceFamily.NAME] = name
            voiceACSS[acss.ACSS.FAMILY][speechserver.VoiceFamily.LANG] = language
            voiceACSS[acss.ACSS.FAMILY][speechserver.VoiceFamily.DIALECT] = dialect
            voiceACSS[acss.ACSS.FAMILY][speechserver.VoiceFamily.VARIANT] = variant
        voiceACSS['established'] = True

        #settings.voices[voiceType] = voiceACSS

    def _getRateForVoiceType(self, voiceType):
        """Gets the speaking rate value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM

        Returns the rate value for the given voice type, or None if
        not set.
        """

        return self._getKeyValueForVoiceType(voiceType, acss.ACSS.RATE)

    def _setRateForVoiceType(self, voiceType, value):
        """Sets the speaking rate value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM
        - value: the rate value to set.
        """

        voiceACSS = self._getACSSForVoiceType(voiceType)
        voiceACSS[acss.ACSS.RATE] = value
        voiceACSS['established'] = True
        #settings.voices[voiceType] = voiceACSS

    def _getPitchForVoiceType(self, voiceType):
        """Gets the pitch value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM

        Returns the pitch value for the given voice type, or None if
        not set.
        """

        return self._getKeyValueForVoiceType(voiceType,
                                             acss.ACSS.AVERAGE_PITCH)

    def _setPitchForVoiceType(self, voiceType, value):
        """Sets the pitch value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM
        - value: the pitch value to set.
        """

        voiceACSS = self._getACSSForVoiceType(voiceType)
        voiceACSS[acss.ACSS.AVERAGE_PITCH] = value
        voiceACSS['established'] = True
        #settings.voices[voiceType] = voiceACSS

    def _getVolumeForVoiceType(self, voiceType):
        """Gets the volume (gain) value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM

        Returns the volume (gain) value for the given voice type, or
        None if not set.
        """

        return self._getKeyValueForVoiceType(voiceType, acss.ACSS.GAIN)

    def _setVolumeForVoiceType(self, voiceType, value):
        """Sets the volume (gain) value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM
        - value: the volume (gain) value to set.
        """

        voiceACSS = self._getACSSForVoiceType(voiceType)
        voiceACSS[acss.ACSS.GAIN] = value
        voiceACSS['established'] = True
        #settings.voices[voiceType] = voiceACSS

    def _setVoiceSettingsForVoiceType(self, voiceType):
        """Sets the family, rate, pitch and volume GUI components based
        on the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK, SYSTEM
        """

        familyName = self._getFamilyNameForVoiceType(voiceType)
        self._setSpeechFamiliesChoice(familyName)

        rate = self._getRateForVoiceType(voiceType)
        if rate is not None:
            self.get_widget("rateScale").set_value(rate)
        else:
            self.get_widget("rateScale").set_value(50.0)

        pitch = self._getPitchForVoiceType(voiceType)
        if pitch is not None:
            self.get_widget("pitchScale").set_value(pitch)
        else:
            self.get_widget("pitchScale").set_value(5.0)

        volume = self._getVolumeForVoiceType(voiceType)
        if volume is not None:
            self.get_widget("volumeScale").set_value(volume)
        else:
            self.get_widget("volumeScale").set_value(10.0)

    def _setSpeechFamiliesChoice(self, familyName):
        """Sets the active item in the families ("Person:") combo box
        to the given family name.

        Arguments:
        - familyName: the family name to use to set the active combo box item.
        """

        if len(self.speechFamilies) == 0:
            return

        languageSet = False
        familySet = False
        for family in self.speechFamilies:
            name = family[speechserver.VoiceFamily.NAME]
            if name == familyName:
                lang = family[speechserver.VoiceFamily.LANG]
                dialect = family[speechserver.VoiceFamily.DIALECT]

                if dialect:
                    language = lang + '-' + dialect
                else:
                    language = lang

                i = 0
                for languageChoice in self.speechLanguagesChoices:
                    if languageChoice == language:
                        self.get_widget("speechLanguages").set_active(i)
                        self.speechLanguagesChoice = self.speechLanguagesChoices[i]
                        languageSet = True

                        self._setupFamilies()

                        i = 0
                        for familyChoice in self.speechFamiliesChoices:
                            name = familyChoice[speechserver.VoiceFamily.NAME]
                            if name == familyName:
                                self.get_widget("speechFamilies").set_active(i)
                                self.speechFamiliesChoice = self.speechFamiliesChoices[i]
                                familySet = True
                                break
                            i += 1

                        break

                    i += 1

                break

        if not languageSet:
            tokens = ["PREFERENCES DIALOG: Could not find speech language match for", familyName]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.get_widget("speechLanguages").set_active(0)
            self.speechLanguagesChoice = self.speechLanguagesChoices[0]

        if languageSet:
            self.selectedLanguageChoices[self.speechServersChoice] = i

        if not familySet:
            tokens = ["PREFERENCES DIALOG: Could not find speech family match for", familyName]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.get_widget("speechFamilies").set_active(0)
            self.speechFamiliesChoice = self.speechFamiliesChoices[0]

        if familySet:
            self.selectedFamilyChoices[self.speechServersChoice,
                    self.speechLanguagesChoice] = i

    def _setupFamilies(self):
        """Gets the list of voice variants for the current speech server and
        current language.
        If there are variants, get the information associated with
        each voice variant and add an entry for it to the variants
        GtkComboBox list.
        """

        combobox = self.get_widget("speechFamilies")
        combobox.set_model(None)
        self.speechFamiliesModel.clear()

        currentLanguage = self.speechLanguagesChoice

        i = 0
        self.speechFamiliesChoices = []
        for family in self.speechFamilies:
            lang = family[speechserver.VoiceFamily.LANG]
            dialect = family[speechserver.VoiceFamily.DIALECT]

            if dialect:
                language = lang + '-' + dialect
            else:
                language = lang

            if language != currentLanguage:
                continue

            name = family[speechserver.VoiceFamily.NAME]
            variant = family[speechserver.VoiceFamily.VARIANT]
            if variant and variant not in ("none", "None"):
                name = variant

            self.speechFamiliesChoices.append(family)
            self.speechFamiliesModel.append((i, name))
            i += 1

        combobox.set_model(self.speechFamiliesModel)
        if i == 0:
            tokens = ["No speech family was available for", str(currentLanguage), "."]
            debug.print_tokens(debug.LEVEL_SEVERE, tokens, True, True)
            self.speechFamiliesChoice = None
            return

        # If user manually selected a family for the current speech server
        # this choice it's restored. In other case the first family
        # (usually the default one) is selected
        #
        selectedIndex = 0
        if (self.speechServersChoice, self.speechLanguagesChoice) \
                in self.selectedFamilyChoices:
            selectedIndex = self.selectedFamilyChoices[self.speechServersChoice,
                    self.speechLanguagesChoice]

        self.get_widget("speechFamilies").set_active(selectedIndex)

    def _setSpeechLanguagesChoice(self, languageName):
        """Sets the active item in the languages ("Language:") combo box
        to the given language name.

        Arguments:
        - languageName: the language name to use to set the active combo box item.
        """

        if len(self.speechLanguagesChoices) == 0:
            return

        valueSet = False
        i = 0
        for language in self.speechLanguagesChoices:
            if language == languageName:
                self.get_widget("speechLanguages").set_active(i)
                self.speechLanguagesChoice = self.speechLanguagesChoices[i]
                valueSet = True
                break
            i += 1

        if not valueSet:
            tokens = ["PREFERENCES DIALOG: Could not find speech language match for", languageName]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.get_widget("speechLanguages").set_active(0)
            self.speechLanguagesChoice = self.speechLanguagesChoices[0]

        if valueSet:
            self.selectedLanguageChoices[self.speechServersChoice] = i

        self._setupFamilies()

    def _setupVoices(self):
        """Gets the list of voices for the current speech server.
        If there are families, get the information associated with
        each voice family and add an entry for it to the families
        GtkComboBox list.
        """

        combobox = self.get_widget("speechLanguages")
        combobox.set_model(None)
        self.speechLanguagesModel.clear()
        self.speechFamilies = self.speechServersChoice.get_voice_families()

        def _get_sort_key(family):
            variant = family.get(speechserver.VoiceFamily.VARIANT)
            name = family.get(speechserver.VoiceFamily.NAME, "")
            if "default" in name.lower():
                return (0, "")
            if variant not in (None, "none", "None"):
                return (1, variant.lower())
            return (1, name.lower())

        self.speechFamilies.sort(key=_get_sort_key)
        self.speechLanguagesChoices = []

        if len(self.speechFamilies) == 0:
            include_stack = debug.debugLevel >= debug.LEVEL_INFO
            debug.print_message(debug.LEVEL_SEVERE, "No voice available.", True, include_stack)
            self.speechLanguagesChoice = None
            return

        done = {}
        i = 0
        for family in self.speechFamilies:
            lang = family[speechserver.VoiceFamily.LANG]
            dialect = family[speechserver.VoiceFamily.DIALECT]
            if (lang,dialect) in done:
                continue
            done[lang,dialect] = True

            if dialect:
                language = lang + '-' + dialect
            else:
                language = lang

            # TODO: get translated language name from CLDR or such
            msg = language
            if msg == "":
                # Unsupported locale
                msg = "default language"

            self.speechLanguagesChoices.append(language)
            self.speechLanguagesModel.append((i, msg))
            i += 1

        # If user manually selected a language for the current speech server
        # this choice it's restored. In other case the first language
        # (usually the default one) is selected
        #
        selectedIndex = 0
        if self.speechServersChoice in self.selectedLanguageChoices:
            selectedIndex = self.selectedLanguageChoices[self.speechServersChoice]

        combobox.set_model(self.speechLanguagesModel)

        self.get_widget("speechLanguages").set_active(selectedIndex)
        if self.initializingSpeech:
            self.speechLanguagesChoice = self.speechLanguagesChoices[selectedIndex]

        self._setupFamilies()

        # The family name will be selected as part of selecting the
        # voice type.  Whenever the families change, we'll reset the
        # voice type selection to the first one ("Default").
        #
        comboBox = self.get_widget("voiceTypesCombo")
        types = [guilabels.SPEECH_VOICE_TYPE_DEFAULT,
                 guilabels.SPEECH_VOICE_TYPE_UPPERCASE,
                 guilabels.SPEECH_VOICE_TYPE_HYPERLINK,
                 guilabels.SPEECH_VOICE_TYPE_SYSTEM]
        self.populateComboBox(comboBox, types)
        comboBox.set_active(DEFAULT)
        voiceType = comboBox.get_active()
        self._setVoiceSettingsForVoiceType(voiceType)

    def _setSpeechServersChoice(self, serverInfo):
        """Sets the active item in the speech servers combo box to the
        given server.

        Arguments:
        - serversChoices: the list of available speech servers.
        - serverInfo: the speech server to use to set the active combo
        box item.
        """

        if len(self.speechServersChoices) == 0:
            return

        # We'll fallback to whatever we happen to be using in the event
        # that this preference has never been set.
        #
        if not (serverInfo and serverInfo[0]):
            serverInfo = speech_and_verbosity_manager.get_manager().get_current_speech_server_info()

        valueSet = False
        i = 0
        for server in self.speechServersChoices:
            if serverInfo == server.get_info():
                self.get_widget("speechServers").set_active(i)
                self.speechServersChoice = server
                valueSet = True
                break
            i += 1

        if not valueSet:
            tokens = ["PREFERENCES DIALOG: Could not find speech server match for", serverInfo]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.get_widget("speechServers").set_active(0)
            self.speechServersChoice = self.speechServersChoices[0]

        self._setupVoices()

    def _setupSpeechServers(self):
        """Gets the list of speech servers for the current speech factory.
        If there are servers, get the information associated with each
        speech server and add an entry for it to the speechServers
        GtkComboBox list.  Set the current choice to be the first item.
        """

        combobox = self.get_widget("speechServers")
        combobox.set_model(None)
        self.speechServersModel.clear()
        self.speechServersChoices = \
                self.speechSystemsChoice.SpeechServer.get_speech_servers()
        if len(self.speechServersChoices) == 0:
            include_stack = debug.debugLevel >= debug.LEVEL_INFO
            debug.print_message(debug.LEVEL_SEVERE, "Speech not available.", True, include_stack)
            self.speechServersChoice = None
            self.speechLanguagesChoices = []
            self.speechLanguagesChoice = None
            self.speechFamiliesChoices = []
            self.speechFamiliesChoice = None
            combobox.set_model(self.speechServersModel)
            return

        i = 0
        for server in self.speechServersChoices:
            name = server.get_info()[0]
            self.speechServersModel.append((i, name))
            i += 1

        combobox.set_model(self.speechServersModel)
        if settings.speechSystemOverride:
            self._setSpeechServersChoice([guilabels.DEFAULT_SYNTHESIZER, 'default'])
        else:
            self._setSpeechServersChoice(self.prefsDict["speechServerInfo"])

    def _setSpeechSystemsChoice(self, systemName):
        """Set the active item in the speech systems combo box to the
        given system name.

        Arguments:
        - factoryChoices: the list of available speech factories (systems).
        - systemName: the speech system name to use to set the active combo
        box item.
        """

        systemName = systemName.strip("'")

        if len(self.speechSystemsChoices) == 0:
            self.speechSystemsChoice = None
            return

        valueSet = False
        i = 0
        for speechSystem in self.speechSystemsChoices:
            name = speechSystem.__name__
            if name.endswith(systemName):
                self.get_widget("speechSystems").set_active(i)
                self.speechSystemsChoice = self.speechSystemsChoices[i]
                valueSet = True
                break
            i += 1

        if not valueSet:
            tokens = ["PREFERENCES DIALOG: Could not find speech system match for", systemName]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.get_widget("speechSystems").set_active(0)
            self.speechSystemsChoice = self.speechSystemsChoices[0]

        self._setupSpeechServers()

    def _setupSpeechSystems(self, factories):
        """Sets up the speech systems combo box and sets the selection
        to the preferred speech system.

        Arguments:
        -factories: the list of known speech factories (working or not)
        """

        combobox = self.get_widget("speechSystems")
        combobox.set_model(None)
        self.speechSystemsModel.clear()
        self.workingFactories = []
        for factory in factories:
            try:
                servers = factory.SpeechServer.get_speech_servers()
                if len(servers):
                    self.workingFactories.append(factory)
            except Exception:
                debug.print_exception(debug.LEVEL_INFO)

        self.speechSystemsChoices = []
        if len(self.workingFactories) == 0:
            include_stack = debug.debugLevel >= debug.LEVEL_INFO
            debug.print_message(debug.LEVEL_SEVERE, "Speech not available.", True, include_stack)
            self.speechSystemsChoice = None
            self.speechServersChoices = []
            self.speechServersChoice = None
            self.speechLanguagesChoices = []
            self.speechLanguagesChoice = None
            self.speechFamiliesChoices = []
            self.speechFamiliesChoice = None
            combobox.set_model(self.speechSystemsModel)
            return

        i = 0
        for workingFactory in self.workingFactories:
            self.speechSystemsChoices.append(workingFactory)
            name = workingFactory.SpeechServer.get_factory_name()
            self.speechSystemsModel.append((i, name))
            i += 1

        combobox.set_model(self.speechSystemsModel)
        if settings.speechSystemOverride:
            self._setSpeechSystemsChoice(settings.speechSystemOverride)
        elif self.prefsDict["speechServerFactory"]:
            self._setSpeechSystemsChoice(self.prefsDict["speechServerFactory"])
        else:
            self.speechSystemsChoice = None

    def _initSpeechState(self):
        """Initialize the various speech components.
        """

        voices = self.prefsDict["voices"]
        self.defaultVoice   = acss.ACSS(voices.get(settings.DEFAULT_VOICE))
        self.uppercaseVoice = acss.ACSS(voices.get(settings.UPPERCASE_VOICE))
        self.hyperlinkVoice = acss.ACSS(voices.get(settings.HYPERLINK_VOICE))
        self.systemVoice    = acss.ACSS(voices.get(settings.SYSTEM_VOICE))

        # Just a note on general naming pattern:
        #
        # *        = The name of the combobox
        # *Model   = the name of the comobox model
        # *Choices = the Orca/speech python objects
        # *Choice  = a value from *Choices
        #
        # Where * = speechSystems, speechServers, speechLanguages, speechFamilies
        #
        factories = settings_manager.get_manager().get_speech_server_factories()
        if len(factories) == 0 or not self.prefsDict.get('enableSpeech', True):
            self.workingFactories = []
            self.speechSystemsChoice = None
            self.speechServersChoices = []
            self.speechServersChoice = None
            self.speechLanguagesChoices = []
            self.speechLanguagesChoice = None
            self.speechFamiliesChoices = []
            self.speechFamiliesChoice = None
            return

        speech_and_verbosity_manager.get_manager().start_speech()

        # This cascades into systems->servers->voice_type->families...
        #
        self.initializingSpeech = True
        self._setupSpeechSystems(factories)
        self.initializingSpeech = False

    def _setSpokenTextAttributes(self, view, setAttributes, state, moveToTop=False):
        """Given a set of spoken text attributes, update the model used by the
        text attribute tree view.

        Arguments:
        - view: the text attribute tree view.
        - setAttributes: the list of spoken text attributes to update.
        - state: the state (True or False) that they all should be set to.
        - moveToTop: if True, move these attributes to the top of the list.
        """

        model = view.get_model()
        view.set_model(None)
        allAttrList = AXText.get_all_supported_text_attributes()
        for i, key in enumerate(setAttributes):
            for path in range(len(allAttrList)):
                attribute = AXTextAttribute.from_string(key)
                if attribute is None:
                    continue
                localizedKey = attribute.get_localized_name()
                if localizedKey == model[path][NAME]:
                    thisIter = model.get_iter(path)
                    model.set_value(thisIter, NAME, localizedKey)
                    model.set_value(thisIter, IS_SPOKEN, state)
                    if moveToTop:
                        try:
                            thisIter = model.get_iter(path)
                            otherIter = model.get_iter(i)
                        except ValueError:
                            pass
                        else:
                            model.move_before(thisIter, otherIter)
                    break

        view.set_model(model)

    def _setBrailledTextAttributes(self, view, setAttributes, state):
        """Given a set of brailled text attributes, update the model used
        by the text attribute tree view.

        Arguments:
        - view: the text attribute tree view.
        - setAttributes: the list of brailled text attributes to update.
        - state: the state (True or False) that they all should be set to.
        """

        model = view.get_model()
        view.set_model(None)
        allAttrList = AXText.get_all_supported_text_attributes()
        for key in setAttributes:
            for path in range(len(allAttrList)):
                attribute = AXTextAttribute.from_string(key)
                if attribute is None:
                    continue
                localizedKey = attribute.get_localized_name()
                if localizedKey == model[path][NAME]:
                    thisIter = model.get_iter(path)
                    model.set_value(thisIter, IS_BRAILLED, state)
                    break

        view.set_model(model)

    def _updateTextDictEntry(self):
        """The user has updated the text attribute list in some way. Update
        the preferences to reflect the current state of the corresponding
        text attribute lists.
        """

        model = self.getTextAttributesView.get_model()
        spoken_attributes = []
        brailled_attributes = []
        noRows = model.iter_n_children(None)
        for path in range(0, noRows):
            localizedKey = model[path][NAME]
            attribute = AXTextAttribute.from_localized_string(localizedKey)
            if attribute is None:
                continue
            key = attribute.get_attribute_name()
            if model[path][IS_SPOKEN]:
                spoken_attributes.append(key)
            if model[path][IS_BRAILLED]:
                brailled_attributes.append(key)

        self.prefsDict["textAttributesToSpeak"] = spoken_attributes
        self.prefsDict["textAttributesToBraille"] = brailled_attributes

    def contractedBrailleToggled(self, checkbox):
        grid = self.get_widget('contractionTableGrid')
        grid.set_sensitive(checkbox.get_active())
        self.prefsDict["enableContractedBraille"] = checkbox.get_active()

    def contractionTableComboChanged(self, combobox):
        model = combobox.get_model()
        myIter = combobox.get_active_iter()
        self.prefsDict["brailleContractionTable"] = model[myIter][1]

    def flashPersistenceToggled(self, checkbox):
        grid = self.get_widget('flashMessageDurationGrid')
        grid.set_sensitive(not checkbox.get_active())
        self.prefsDict["flashIsPersistent"] = checkbox.get_active()

    def textAttributeSpokenToggled(self, cell, path, model):
        """The user has toggled the state of one of the text attribute
        checkboxes to be spoken. Update our model to reflect this, then
        update the preference.

        Arguments:
        - cell: the cell that changed.
        - path: the path of that cell.
        - model: the model that the cell is part of.
        """

        thisIter = model.get_iter(path)
        model.set(thisIter, IS_SPOKEN, not model[path][IS_SPOKEN])
        self._updateTextDictEntry()

    def textAttributeBrailledToggled(self, cell, path, model):
        """The user has toggled the state of one of the text attribute
        checkboxes to be brailled. Update our model to reflect this,
        then update the preference.

        Arguments:
        - cell: the cell that changed.
        - path: the path of that cell.
        - model: the model that the cell is part of.
        """

        thisIter = model.get_iter(path)
        model.set(thisIter, IS_BRAILLED, not model[path][IS_BRAILLED])
        self._updateTextDictEntry()

    def textAttrCursorChanged(self, widget):
        """Set the search column in the text attribute tree view
        depending upon which column the user currently has the cursor in.
        """

        [path, focusColumn] = self.getTextAttributesView.get_cursor()
        if focusColumn:
            noColumns = len(self.getTextAttributesView.get_columns())
            for i in range(0, noColumns):
                col = self.getTextAttributesView.get_column(i)
                if focusColumn == col:
                    self.getTextAttributesView.set_search_column(i)
                    break

    def _createTextAttributesTreeView(self):
        """Create the text attributes tree view. The view is the
        textAttributesTreeView GtkTreeView widget. The view will consist
        of a list containing three columns:
          IS_SPOKEN - a checkbox whose state indicates whether this text
                      attribute will be spoken or not.
          NAME      - the text attribute name.
          VALUE     - if set, (and this attributes is enabled for speaking),
                      then this attribute will be spoken unless it equals
                      this value.
        """

        self.getTextAttributesView = self.get_widget("textAttributesTreeView")

        if self.getTextAttributesView.get_columns():
            for column in self.getTextAttributesView.get_columns():
                self.getTextAttributesView.remove_column(column)

        model = Gtk.ListStore(GObject.TYPE_STRING,
                              GObject.TYPE_BOOLEAN,
                              GObject.TYPE_BOOLEAN,
                              GObject.TYPE_STRING)

        # Initially setup the list store model based on the values of all
        # the known text attributes.
        for attribute in AXText.get_all_supported_text_attributes():
            thisIter = model.append()
            model.set_value(thisIter, NAME, attribute.get_localized_name())
            model.set_value(thisIter, IS_SPOKEN, False)
            model.set_value(thisIter, IS_BRAILLED, False)

        self.getTextAttributesView.set_model(model)

        # Attribute Name column (NAME).
        column = Gtk.TreeViewColumn(guilabels.TEXT_ATTRIBUTE_NAME)
        column.set_min_width(250)
        column.set_resizable(True)
        renderer = Gtk.CellRendererText()
        column.pack_end(renderer, True)
        column.add_attribute(renderer, 'text', NAME)
        self.getTextAttributesView.insert_column(column, 0)

        # Attribute Speak column (IS_SPOKEN).
        speakAttrColumnLabel = guilabels.PRESENTATION_SPEAK
        column = Gtk.TreeViewColumn(speakAttrColumnLabel)
        renderer = Gtk.CellRendererToggle()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'active', IS_SPOKEN)
        renderer.connect("toggled",
                         self.textAttributeSpokenToggled,
                         model)
        self.getTextAttributesView.insert_column(column, 1)
        column.clicked()

        # Attribute Mark in Braille column (IS_BRAILLED).
        markAttrColumnLabel = guilabels.PRESENTATION_MARK_IN_BRAILLE
        column = Gtk.TreeViewColumn(markAttrColumnLabel)
        renderer = Gtk.CellRendererToggle()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'active', IS_BRAILLED)
        renderer.connect("toggled",
                         self.textAttributeBrailledToggled,
                         model)
        self.getTextAttributesView.insert_column(column, 2)
        column.clicked()

        # Get a dictionary of text attributes that the user cares about, falling back on the
        # default presentable attributes if the user has not specified any.
        attr_list = settings_manager.get_manager().get_setting("textAttributesToSpeak")
        if not attr_list:
            attr_list = [
                attr.get_attribute_name()
                for attr in AXText.get_all_supported_text_attributes()
                if attr.should_present_by_default()
            ]
        self._setSpokenTextAttributes(self.getTextAttributesView, attr_list, True, True)

        # For braille none should be enabled by default. So only set those the user chose.
        attr_list = settings_manager.get_manager().get_setting("textAttributesToBraille")
        self._setBrailledTextAttributes(self.getTextAttributesView, attr_list, True)

        # TODO - JD: Is this still needed (for the purpose of the search column)?
        self.getTextAttributesView.connect("cursor_changed", self.textAttrCursorChanged)

    def pronActualValueEdited(self, cell, path, new_text, model):
        """The user has edited the value of one of the actual strings in
        the pronunciation dictionary. Update our model to reflect this.

        Arguments:
        - cell: the cell that changed.
        - path: the path of that cell.
        - new_text: the new pronunciation dictionary actual string.
        - model: the model that the cell is part of.
        """

        thisIter = model.get_iter(path)
        model.set(thisIter, ACTUAL, new_text)

    def pronReplacementValueEdited(self, cell, path, new_text, model):
        """The user has edited the value of one of the replacement strings
        in the pronunciation dictionary. Update our model to reflect this.

        Arguments:
        - cell: the cell that changed.
        - path: the path of that cell.
        - new_text: the new pronunciation dictionary replacement string.
        - model: the model that the cell is part of.
        """

        thisIter = model.get_iter(path)
        model.set(thisIter, REPLACEMENT, new_text)

    def pronunciationFocusChange(self, widget, event, isFocused):
        """Callback for the pronunciation tree's focus-{in,out}-event signal."""

        settings_manager.get_manager().set_setting('usePronunciationDictionary', not isFocused)

    def pronunciationCursorChanged(self, widget):
        """Set the search column in the pronunciation dictionary tree view
        depending upon which column the user currently has the cursor in.
        """

        [path, focusColumn] = self.pronunciationView.get_cursor()
        if focusColumn:
            noColumns = len(self.pronunciationView.get_columns())
            for i in range(0, noColumns):
                col = self.pronunciationView.get_column(i)
                if focusColumn == col:
                    self.pronunciationView.set_search_column(i)
                    break

    def _createPronunciationTreeView(self):
        """Create the pronunciation dictionary tree view. The view is the
        pronunciationTreeView GtkTreeView widget. The view will consist
        of a list containing two columns:
          ACTUAL      - the actual text string (word).
          REPLACEMENT - the string that is used to pronounce that word.
        """

        self.pronunciationView = self.get_widget("pronunciationTreeView")

        if self.pronunciationView.get_columns():
            for column in self.pronunciationView.get_columns():
                self.pronunciationView.remove_column(column)

        model = Gtk.ListStore(GObject.TYPE_STRING,
                              GObject.TYPE_STRING)

        # Initially setup the list store model based on the values of all
        # existing entries in the pronunciation dictionary -- unless it's
        # the default script.
        #
        if not self.script.app:
            _profile = self.prefsDict.get('activeProfile')[1]
            pronDict = settings_manager.get_manager().get_pronunciations(_profile)
        else:
            pronDict = pronunciation_dict.pronunciation_dict
        for pronKey in sorted(pronDict.keys()):
            thisIter = model.append()
            try:
                actual, replacement = pronDict[pronKey]
            except Exception:
                # Try to do something sensible for the previous format of
                # pronunciation dictionary entries. See bug #464754 for
                # more details.
                #
                actual = pronKey
                replacement = pronDict[pronKey]
            model.set(thisIter,
                      ACTUAL, actual,
                      REPLACEMENT, replacement)

        self.pronunciationView.set_model(model)

        # Pronunciation Dictionary actual string (word) column (ACTUAL).
        column = Gtk.TreeViewColumn(guilabels.DICTIONARY_ACTUAL_STRING)
        column.set_min_width(250)
        column.set_resizable(True)
        renderer = Gtk.CellRendererText()
        renderer.set_property('editable', True)
        column.pack_end(renderer, True)
        column.add_attribute(renderer, 'text', ACTUAL)
        renderer.connect("edited", self.pronActualValueEdited, model)
        self.pronunciationView.insert_column(column, 0)

        # Pronunciation Dictionary replacement string column (REPLACEMENT)
        column = Gtk.TreeViewColumn(guilabels.DICTIONARY_REPLACEMENT_STRING)
        renderer = Gtk.CellRendererText()
        renderer.set_property('editable', True)
        column.pack_end(renderer, True)
        column.add_attribute(renderer, 'text', REPLACEMENT)
        renderer.connect("edited", self.pronReplacementValueEdited, model)
        self.pronunciationView.insert_column(column, 1)

        self.pronunciationModel = model

        # Connect a handler for when the user changes columns within the
        # view, so that we can adjust the search column for item lookups.
        #
        self.pronunciationView.connect("cursor_changed",
                                       self.pronunciationCursorChanged)

        self.pronunciationView.connect(
            "focus_in_event", self.pronunciationFocusChange, True)
        self.pronunciationView.connect(
            "focus_out_event", self.pronunciationFocusChange, False)

    def _initGUIState(self):
        """Adjust the settings of the various components on the
        configuration GUI depending upon the users preferences.
        """

        prefs = self.prefsDict

        self.typing_echo_grid.reload()

        # Speech pane.
        #
        enable = prefs.get("enableSpeech", settings.enableSpeech)
        self.get_widget("speechSupportCheckButton").set_active(enable)
        self.get_widget("speechOptionsGrid").set_sensitive(enable)

        enable = prefs.get("onlySpeakDisplayedText", settings.onlySpeakDisplayedText)
        self.get_widget("onlySpeakDisplayedTextCheckButton").set_active(enable)
        self.get_widget("contextOptionsGrid").set_sensitive(not enable)

        style = prefs.get("verbalizePunctuationStyle", settings.verbalizePunctuationStyle)
        if style == settings.PUNCTUATION_STYLE_NONE:
            self.get_widget("noneButton").set_active(True)
        elif style == settings.PUNCTUATION_STYLE_SOME:
            self.get_widget("someButton").set_active(True)
        elif style == settings.PUNCTUATION_STYLE_MOST:
            self.get_widget("mostButton").set_active(True)
        else:
            self.get_widget("allButton").set_active(True)

        level = prefs.get("speechVerbosityLevel", settings.speechVerbosityLevel)
        if level == settings.VERBOSITY_LEVEL_BRIEF:
            self.get_widget("speechBriefButton").set_active(True)
        else:
            self.get_widget("speechVerboseButton").set_active(True)
        self.get_widget("onlySpeakDisplayedTextCheckButton").set_active(
            prefs.get("onlySpeakDisplayedText", settings.onlySpeakDisplayedText))
        self.get_widget("enableSpeechIndentationCheckButton").set_active(
            prefs.get("enableSpeechIndentation", settings.enableSpeechIndentation))
        self.get_widget("speakBlankLinesCheckButton").set_active(
            prefs.get("speakBlankLines", settings.speakBlankLines))
        self.get_widget("speakNumbersAsDigitsCheckButton").set_active(
            prefs.get("speakNumbersAsDigits", settings.speakNumbersAsDigits))
        self.get_widget("enableTutorialMessagesCheckButton").set_active(
            prefs.get("enableTutorialMessages", settings.enableTutorialMessages))
        self.get_widget("enablePauseBreaksCheckButton").set_active(
            prefs.get("enablePauseBreaks", settings.enablePauseBreaks))
        self.get_widget("enablePositionSpeakingCheckButton").set_active(
            prefs.get("enablePositionSpeaking", settings.enablePositionSpeaking))
        self.get_widget("enableMnemonicSpeakingCheckButton").set_active(
            prefs.get("enableMnemonicSpeaking", settings.enableMnemonicSpeaking))
        self.get_widget("speakMisspelledIndicatorCheckButton").set_active(
            prefs.get("speakMisspelledIndicator", settings.speakMisspelledIndicator))
        self.get_widget("speakDescriptionCheckButton").set_active(
            prefs.get("speakDescription", settings.speakDescription))
        self.get_widget("speakContextBlockquoteCheckButton").set_active(
            prefs.get("speakContextBlockquote", settings.speakContextList))
        self.get_widget("speakContextLandmarkCheckButton").set_active(
            prefs.get("speakContextLandmark", settings.speakContextLandmark))
        self.get_widget("speakContextNonLandmarkFormCheckButton").set_active(
            prefs.get("speakContextNonLandmarkForm", settings.speakContextNonLandmarkForm))
        self.get_widget("speakContextListCheckButton").set_active(
            prefs.get("speakContextList", settings.speakContextList))
        self.get_widget("speakContextPanelCheckButton").set_active(
            prefs.get("speakContextPanel", settings.speakContextPanel))
        self.get_widget("speakContextTableCheckButton").set_active(
            prefs.get("speakContextTable", settings.speakContextTable))

        enable = prefs.get("messagesAreDetailed", settings.messagesAreDetailed)
        self.get_widget("messagesAreDetailedCheckButton").set_active(enable)

        enable = prefs.get("useColorNames", settings.useColorNames)
        self.get_widget("useColorNamesCheckButton").set_active(enable)

        enable = prefs.get("readFullRowInGUITable", settings.readFullRowInGUITable)
        self.get_widget("readFullRowInGUITableCheckButton").set_active(enable)

        enable = prefs.get("readFullRowInDocumentTable", settings.readFullRowInDocumentTable)
        self.get_widget("readFullRowInDocumentTableCheckButton").set_active(enable)

        enable = prefs.get("readFullRowInSpreadSheet", settings.readFullRowInSpreadSheet)
        self.get_widget("readFullRowInSpreadSheetCheckButton").set_active(enable)

        style = prefs.get("capitalizationStyle", settings.capitalizationStyle)
        combobox = self.get_widget("capitalizationStyle")
        options = [guilabels.CAPITALIZATION_STYLE_NONE,
                   guilabels.CAPITALIZATION_STYLE_ICON,
                   guilabels.CAPITALIZATION_STYLE_SPELL]
        self.populateComboBox(combobox, options)
        if style == settings.CAPITALIZATION_STYLE_ICON:
            value = guilabels.CAPITALIZATION_STYLE_ICON
        elif style == settings.CAPITALIZATION_STYLE_SPELL:
            value = guilabels.CAPITALIZATION_STYLE_SPELL
        else:
            value = guilabels.CAPITALIZATION_STYLE_NONE
        combobox.set_active(options.index(value))

        combobox2 = self.get_widget("dateFormatCombo")
        sdtime = time.strftime
        ltime = time.localtime
        self.populateComboBox(combobox2,
          [sdtime(messages.DATE_FORMAT_LOCALE, ltime()),
           sdtime(messages.DATE_FORMAT_NUMBERS_DM, ltime()),
           sdtime(messages.DATE_FORMAT_NUMBERS_MD, ltime()),
           sdtime(messages.DATE_FORMAT_NUMBERS_DMY, ltime()),
           sdtime(messages.DATE_FORMAT_NUMBERS_MDY, ltime()),
           sdtime(messages.DATE_FORMAT_NUMBERS_YMD, ltime()),
           sdtime(messages.DATE_FORMAT_FULL_DM, ltime()),
           sdtime(messages.DATE_FORMAT_FULL_MD, ltime()),
           sdtime(messages.DATE_FORMAT_FULL_DMY, ltime()),
           sdtime(messages.DATE_FORMAT_FULL_MDY, ltime()),
           sdtime(messages.DATE_FORMAT_FULL_YMD, ltime()),
           sdtime(messages.DATE_FORMAT_ABBREVIATED_DM, ltime()),
           sdtime(messages.DATE_FORMAT_ABBREVIATED_MD, ltime()),
           sdtime(messages.DATE_FORMAT_ABBREVIATED_DMY, ltime()),
           sdtime(messages.DATE_FORMAT_ABBREVIATED_MDY, ltime()),
           sdtime(messages.DATE_FORMAT_ABBREVIATED_YMD, ltime())
          ])

        indexdate = DATE_FORMAT_LOCALE
        dateFormat = self.prefsDict.get("presentDateFormat", settings.presentDateFormat)
        if dateFormat == messages.DATE_FORMAT_LOCALE:
            indexdate = DATE_FORMAT_LOCALE
        elif dateFormat == messages.DATE_FORMAT_NUMBERS_DM:
            indexdate = DATE_FORMAT_NUMBERS_DM
        elif dateFormat == messages.DATE_FORMAT_NUMBERS_MD:
            indexdate = DATE_FORMAT_NUMBERS_MD
        elif dateFormat == messages.DATE_FORMAT_NUMBERS_DMY:
            indexdate = DATE_FORMAT_NUMBERS_DMY
        elif dateFormat == messages.DATE_FORMAT_NUMBERS_MDY:
            indexdate = DATE_FORMAT_NUMBERS_MDY
        elif dateFormat == messages.DATE_FORMAT_NUMBERS_YMD:
            indexdate = DATE_FORMAT_NUMBERS_YMD
        elif dateFormat == messages.DATE_FORMAT_FULL_DM:
            indexdate = DATE_FORMAT_FULL_DM
        elif dateFormat == messages.DATE_FORMAT_FULL_MD:
            indexdate = DATE_FORMAT_FULL_MD
        elif dateFormat == messages.DATE_FORMAT_FULL_DMY:
            indexdate = DATE_FORMAT_FULL_DMY
        elif dateFormat == messages.DATE_FORMAT_FULL_MDY:
            indexdate = DATE_FORMAT_FULL_MDY
        elif dateFormat == messages.DATE_FORMAT_FULL_YMD:
            indexdate = DATE_FORMAT_FULL_YMD
        elif dateFormat == messages.DATE_FORMAT_ABBREVIATED_DM:
            indexdate = DATE_FORMAT_ABBREVIATED_DM
        elif dateFormat == messages.DATE_FORMAT_ABBREVIATED_MD:
            indexdate = DATE_FORMAT_ABBREVIATED_MD
        elif dateFormat == messages.DATE_FORMAT_ABBREVIATED_DMY:
            indexdate = DATE_FORMAT_ABBREVIATED_DMY
        elif dateFormat == messages.DATE_FORMAT_ABBREVIATED_MDY:
            indexdate = DATE_FORMAT_ABBREVIATED_MDY
        elif dateFormat == messages.DATE_FORMAT_ABBREVIATED_YMD:
            indexdate = DATE_FORMAT_ABBREVIATED_YMD
        combobox2.set_active (indexdate)

        combobox3 = self.get_widget("timeFormatCombo")
        self.populateComboBox(combobox3,
          [sdtime(messages.TIME_FORMAT_LOCALE, ltime()),
           sdtime(messages.TIME_FORMAT_12_HM, ltime()),
           sdtime(messages.TIME_FORMAT_12_HMS, ltime()),
           sdtime(messages.TIME_FORMAT_24_HMS, ltime()),
           sdtime(messages.TIME_FORMAT_24_HMS_WITH_WORDS, ltime()),
           sdtime(messages.TIME_FORMAT_24_HM, ltime()),
           sdtime(messages.TIME_FORMAT_24_HM_WITH_WORDS, ltime())])
        indextime = TIME_FORMAT_LOCALE
        timeFormat = self.prefsDict["presentTimeFormat"]
        if timeFormat == messages.TIME_FORMAT_LOCALE:
            indextime = TIME_FORMAT_LOCALE
        elif timeFormat == messages.TIME_FORMAT_12_HM:
            indextime = TIME_FORMAT_12_HM
        elif timeFormat == messages.TIME_FORMAT_12_HMS:
            indextime = TIME_FORMAT_12_HMS
        elif timeFormat == messages.TIME_FORMAT_24_HMS:
            indextime = TIME_FORMAT_24_HMS
        elif timeFormat == messages.TIME_FORMAT_24_HMS_WITH_WORDS:
            indextime = TIME_FORMAT_24_HMS_WITH_WORDS
        elif timeFormat == messages.TIME_FORMAT_24_HM:
            indextime = TIME_FORMAT_24_HM
        elif timeFormat == messages.TIME_FORMAT_24_HM_WITH_WORDS:
            indextime = TIME_FORMAT_24_HM_WITH_WORDS
        combobox3.set_active (indextime)

        self.get_widget("speakProgressBarUpdatesCheckButton").set_active(
            prefs.get("speakProgressBarUpdates", settings.speakProgressBarUpdates))
        self.get_widget("brailleProgressBarUpdatesCheckButton").set_active(
            prefs.get("brailleProgressBarUpdates", settings.brailleProgressBarUpdates))
        self.get_widget("beepProgressBarUpdatesCheckButton").set_active(
            prefs.get("beepProgressBarUpdates", settings.beepProgressBarUpdates))

        interval = prefs["progressBarUpdateInterval"]
        self.get_widget("progressBarUpdateIntervalSpinButton").set_value(interval)

        comboBox = self.get_widget("progressBarVerbosity")
        levels = [guilabels.PROGRESS_BAR_ALL,
                  guilabels.PROGRESS_BAR_APPLICATION,
                  guilabels.PROGRESS_BAR_WINDOW]
        self.populateComboBox(comboBox, levels)
        comboBox.set_active(prefs["progressBarVerbosity"])

        enable = prefs["enableMouseReview"]
        self.get_widget("enableMouseReviewCheckButton").set_active(enable)

        # Braille pane.
        #
        self.get_widget("enableBrailleCheckButton").set_active( \
                        prefs["enableBraille"])
        state = prefs["brailleRolenameStyle"] == \
                            settings.BRAILLE_ROLENAME_STYLE_SHORT
        self.get_widget("abbrevRolenames").set_active(state)

        self.get_widget("disableBrailleEOLCheckButton").set_active(
            prefs["disableBrailleEOL"])

        if louis is None:
            self.get_widget( \
                "contractedBrailleCheckButton").set_sensitive(False)
        else:
            self.get_widget("contractedBrailleCheckButton").set_active( \
                prefs["enableContractedBraille"])
            # Set up contraction table combo box and set it to the
            # currently used one.
            #
            tablesCombo = self.get_widget("contractionTableCombo")
            tableDict = braille.list_tables()
            selectedTableIter = None
            selectedTable = prefs["brailleContractionTable"] or braille.get_default_table()
            if tableDict:
                tablesModel = Gtk.ListStore(str, str)
                names = sorted(tableDict.keys())
                for name in names:
                    fname = tableDict[name]
                    it = tablesModel.append([name, fname])
                    if os.path.join(braille.tablesdir, fname) == \
                            selectedTable:
                        selectedTableIter = it
                cell = self.planeCellRendererText
                tablesCombo.clear()
                tablesCombo.pack_start(cell, True)
                tablesCombo.add_attribute(cell, 'text', 0)
                tablesCombo.set_model(tablesModel)
                if selectedTableIter:
                    tablesCombo.set_active_iter(selectedTableIter)
                else:
                    tablesCombo.set_active(0)
            else:
                tablesCombo.set_sensitive(False)
        if prefs["brailleVerbosityLevel"] == settings.VERBOSITY_LEVEL_BRIEF:
            self.get_widget("brailleBriefButton").set_active(True)
        else:
            self.get_widget("brailleVerboseButton").set_active(True)

        self.get_widget("enableBrailleWordWrapCheckButton").set_active(
            prefs.get("enableBrailleWordWrap", settings.enableBrailleWordWrap))

        selectionIndicator = prefs["brailleSelectorIndicator"]
        if selectionIndicator == settings.BRAILLE_UNDERLINE_7:
            self.get_widget("brailleSelection7Button").set_active(True)
        elif selectionIndicator == settings.BRAILLE_UNDERLINE_8:
            self.get_widget("brailleSelection8Button").set_active(True)
        elif selectionIndicator == settings.BRAILLE_UNDERLINE_BOTH:
            self.get_widget("brailleSelectionBothButton").set_active(True)
        else:
            self.get_widget("brailleSelectionNoneButton").set_active(True)

        linkIndicator = prefs["brailleLinkIndicator"]
        if linkIndicator == settings.BRAILLE_UNDERLINE_7:
            self.get_widget("brailleLink7Button").set_active(True)
        elif linkIndicator == settings.BRAILLE_UNDERLINE_8:
            self.get_widget("brailleLink8Button").set_active(True)
        elif linkIndicator == settings.BRAILLE_UNDERLINE_BOTH:
            self.get_widget("brailleLinkBothButton").set_active(True)
        else:
            self.get_widget("brailleLinkNoneButton").set_active(True)

        enable = prefs.get("enableFlashMessages", settings.enableFlashMessages)
        self.get_widget("enableFlashMessagesCheckButton").set_active(enable)

        enable = prefs.get("flashIsPersistent", settings.flashIsPersistent)
        self.get_widget("flashIsPersistentCheckButton").set_active(enable)

        enable = prefs.get("flashIsDetailed", settings.flashIsDetailed)
        self.get_widget("flashIsDetailedCheckButton").set_active(enable)

        duration = prefs["brailleFlashTime"]
        self.get_widget("brailleFlashTimeSpinButton").set_value(duration / 1000)

        # Text attributes pane.
        #
        self._createTextAttributesTreeView()

        brailleIndicator = prefs["textAttributesBrailleIndicator"]
        if brailleIndicator == settings.BRAILLE_UNDERLINE_7:
            self.get_widget("textBraille7Button").set_active(True)
        elif brailleIndicator == settings.BRAILLE_UNDERLINE_8:
            self.get_widget("textBraille8Button").set_active(True)
        elif brailleIndicator == settings.BRAILLE_UNDERLINE_BOTH:
            self.get_widget("textBrailleBothButton").set_active(True)
        else:
            self.get_widget("textBrailleNoneButton").set_active(True)

        # Pronunciation dictionary pane.
        #
        self._createPronunciationTreeView()

        # General pane.
        #
        self.get_widget("presentToolTipsCheckButton").set_active(
            prefs["presentToolTips"])

        if prefs["keyboardLayout"] == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            self.get_widget("generalDesktopButton").set_active(True)
        else:
            self.get_widget("generalLaptopButton").set_active(True)

        combobox = self.get_widget("sayAllStyle")
        self.populateComboBox(combobox, [guilabels.SAY_ALL_STYLE_LINE,
                                         guilabels.SAY_ALL_STYLE_SENTENCE])
        combobox.set_active(prefs["sayAllStyle"])
        self.get_widget("rewindAndFastForwardInSayAllCheckButton").set_active(
            prefs.get("rewindAndFastForwardInSayAll", settings.rewindAndFastForwardInSayAll))
        self.get_widget("structNavInSayAllCheckButton").set_active(
            prefs.get("structNavInSayAll", settings.structNavInSayAll))
        self.get_widget("sayAllContextBlockquoteCheckButton").set_active(
            prefs.get("sayAllContextBlockquote", settings.sayAllContextBlockquote))
        self.get_widget("sayAllContextLandmarkCheckButton").set_active(
            prefs.get("sayAllContextLandmark", settings.sayAllContextLandmark))
        self.get_widget("sayAllContextNonLandmarkFormCheckButton").set_active(
            prefs.get("sayAllContextNonLandmarkForm", settings.sayAllContextNonLandmarkForm))
        self.get_widget("sayAllContextListCheckButton").set_active(
            prefs.get("sayAllContextList", settings.sayAllContextList))
        self.get_widget("sayAllContextPanelCheckButton").set_active(
            prefs.get("sayAllContextPanel", settings.sayAllContextPanel))
        self.get_widget("sayAllContextTableCheckButton").set_active(
            prefs.get("sayAllContextTable", settings.sayAllContextTable))

        # Orca User Profiles
        #
        self.profilesCombo = self.get_widget('availableProfilesComboBox1')
        self.startingProfileCombo = self.get_widget('availableProfilesComboBox2')
        self.profilesComboModel = self.get_widget('model9')
        self.__initProfileCombo()
        if self.script.app:
            self.get_widget('profilesFrame').set_sensitive(False)

    def __initProfileCombo(self):
        """Adding available profiles and setting active as the active one"""

        available_profiles = self.__getAvailableProfiles()
        self.profilesComboModel.clear()

        if not len(available_profiles):
            self.profilesComboModel.append(self._defaultProfile)
        else:
            for profile in available_profiles:
                self.profilesComboModel.append(profile)

        activeProfile = self.prefsDict.get('activeProfile') or self._defaultProfile
        startingProfile = self.prefsDict.get('startingProfile') or self._defaultProfile

        activeProfileIter = self.getComboBoxIndex(self.profilesCombo,
                                                  activeProfile[0])
        startingProfileIter = self.getComboBoxIndex(self.startingProfileCombo,
                                                  startingProfile[0])
        self.profilesCombo.set_active(activeProfileIter)
        self.startingProfileCombo.set_active(startingProfileIter)

    def __getAvailableProfiles(self):
        """Get available user profiles."""
        return settings_manager.get_manager().available_profiles()

    def _updateOrcaModifier(self):
        combobox = self.get_widget("orcaModifierComboBox")
        keystring = ", ".join(self.prefsDict["orcaModifierKeys"])
        combobox.set_active(self.getComboBoxIndex(combobox, keystring))

    def populateComboBox(self, combobox, items):
        """Populates the combobox with the items provided.

        Arguments:
        - combobox: the GtkComboBox to populate
        - items: the list of strings with which to populate it
        """

        model = Gtk.ListStore(str)
        for item in items:
            model.append([item])
        combobox.set_model(model)

    def getComboBoxIndex(self, combobox, searchStr, col=0):
        """ For each of the entries in the given combo box, look for searchStr.
            Return the index of the entry if searchStr is found.

        Arguments:
        - combobox: the GtkComboBox to search.
        - searchStr: the string to search for.

        Returns the index of the first entry in combobox with searchStr, or
        0 if not found.
        """

        model = combobox.get_model()
        myiter = model.get_iter_first()
        for i in range(0, len(model)):
            name = model.get_value(myiter, col)
            if name == searchStr:
                return i
            myiter = model.iter_next(myiter)

        return 0

    def getComboBoxList(self, combobox):
        """Get the list of values from the active combox
        """
        active = combobox.get_active()
        model = combobox.get_model()
        activeIter = model.get_iter(active)
        activeLabel = model.get_value(activeIter, 0)
        activeName = model.get_value(activeIter, 1)
        return [activeLabel, activeName]

    def getKeyBindingsModelDict(self, model, modifiedOnly=True):
        modelDict = {}
        node = model.get_iter_first()
        while node:
            child = model.iter_children(node)
            while child:
                key, modified = model.get(child, HANDLER, MODIF)
                if modified or not modifiedOnly:
                    value = []
                    value.append(list(model.get(
                            child, KEY1, MOD_MASK1, MOD_USED1, CLICK_COUNT1)))
                    modelDict[key] = value
                child = model.iter_next(child)
            node = model.iter_next(node)

        return modelDict

    def getModelDict(self, model):
        """Get the list of values from a list[str,str] model
        """
        pronunciation_dict.pronunciation_dict = {}
        currentIter = model.get_iter_first()
        while currentIter is not None:
            key, value = model.get(currentIter, ACTUAL, REPLACEMENT)
            if key and value:
                pronunciation_dict.set_pronunciation(key, value)
            currentIter = model.iter_next(currentIter)
        modelDict = pronunciation_dict.pronunciation_dict
        return modelDict

    def showGUI(self):
        """Show the Orca configuration GUI window. This assumes that
        the GUI has already been created.
        """

        if OrcaSetupGUI.DIALOG is not None:
            OrcaSetupGUI.DIALOG.present()
            return

        OrcaSetupGUI.DIALOG = self.get_widget("orcaSetupWindow")
        accelGroup = Gtk.AccelGroup()
        OrcaSetupGUI.DIALOG.add_accel_group(accelGroup)
        helpButton = self.get_widget("helpButton")
        (keyVal, modifierMask) = Gtk.accelerator_parse("F1")
        helpButton.add_accelerator("clicked", accelGroup, keyVal, modifierMask, 0)

        # We always want to re-order the text attributes page so that enabled
        # items are consistently at the top.
        self._setSpokenTextAttributes(
                self.getTextAttributesView,
                settings_manager.get_manager().get_setting("textAttributesToSpeak"),
                True, True)

        if self.script.app:
            title = guilabels.PREFERENCES_APPLICATION_TITLE % AXObject.get_name(self.script.app)
            OrcaSetupGUI.DIALOG.set_title(title)

        OrcaSetupGUI.DIALOG.show_all()
        OrcaSetupGUI.DIALOG.present_with_time(time.time())

    def _initComboBox(self, combobox):
        """Initialize the given combo box to take a list of int/str pairs.

        Arguments:
        - combobox: the GtkComboBox to initialize.
        """

        cell = Gtk.CellRendererText()
        combobox.pack_start(cell, True)
        # We only want to display one column; not two.
        #
        try:
            columnToDisplay = combobox.get_cells()[0]
            combobox.add_attribute(columnToDisplay, 'text', 1)
        except Exception:
            combobox.add_attribute(cell, 'text', 1)
        model = Gtk.ListStore(int, str)
        combobox.set_model(model)

        # Force the display comboboxes to be left aligned.
        #
        if isinstance(combobox, Gtk.ComboBoxText):
            size = combobox.size_request()
            cell.set_fixed_size(size[0] - 29, -1)

        return model

    def _presentMessage(self, text, interrupt=False):
        """If the text field is not None, presents the given text, optionally
        interrupting anything currently being spoken.

        Arguments:
        - text: the text to present
        - interrupt: if True, interrupt any speech currently being spoken
        """

        # TODO - JD: Eliminate this function.

        self.script.speak_message(text, interrupt=interrupt)
        self.script.display_message(text, flash_time=-1)

    def _createNode(self, appName):
        """Create a new root node in the TreeStore model with the name of the
            application.

        Arguments:
        - appName: the name of the TreeStore Node (the same of the application)
        """

        model = self.keyBindingsModel

        myiter = model.append(None)
        model.set_value(myiter, DESCRIP, appName)
        model.set_value(myiter, MODIF, False)

        return myiter

    def _getIterOf(self, appName):
        """Returns the Gtk.TreeIter of the TreeStore model
        that matches the application name passed as argument

        Arguments:
        - appName: a string with the name of the application of the node wanted
                    it's the same that the field DESCRIP of the model treeStore
        """

        model = self.keyBindingsModel

        for row in model:
            if ((model.iter_depth(row.iter) == 0) \
                and (row[DESCRIP] == appName)):
                return row.iter

        return None

    def _clickCountToString(self, clickCount):
        """Given a numeric clickCount, returns a string for inclusion
        in the list of keybindings.

        Argument:
        - clickCount: the number of clicks associated with the keybinding.
        """

        clickCountString = ""
        if clickCount == 2:
            clickCountString = f" ({guilabels.CLICK_COUNT_DOUBLE})"
        elif clickCount == 3:
            clickCountString = f" ({guilabels.CLICK_COUNT_TRIPLE})"

        return clickCountString

    def _insertRow(self, handl, kb, parent=None, modif=False):
        """Appends a new row with the new keybinding data to the treeview

        Arguments:
        - handl:  the name of the handler associated to the keyBinding
        - kb:     the new keybinding.
        - parent: the parent node of the treeview, where to append the kb
        - modif:  whether to check the modified field or not.

        Returns a Gtk.TreeIter pointing at the new row.
        """

        model = self.keyBindingsModel

        if not kb.handler:
            return None

        if parent is None:
            parent = self._getIterOf(guilabels.KB_GROUP_DEFAULT)

        if parent is not None:
            myiter = model.append(parent)
            if not kb.keysymstring:
                text = None
            else:
                clickCount = self._clickCountToString(kb.click_count)
                keysymstring = kb.keysymstring
                text = keybindings.get_modifier_names(kb.modifiers) \
                       + keysymstring \
                       + clickCount

            model.set_value(myiter, HANDLER, handl)
            model.set_value(myiter, DESCRIP, kb.handler.description)
            model.set_value(myiter, MOD_MASK1, str(kb.modifier_mask))
            model.set_value(myiter, MOD_USED1, str(kb.modifiers))
            model.set_value(myiter, KEY1, kb.keysymstring)
            model.set_value(myiter, CLICK_COUNT1, str(kb.click_count))
            if text is not None:
                model.set_value(myiter, OLDTEXT1, text)
                model.set_value(myiter, TEXT1, text)
            model.set_value(myiter, MODIF, modif)
            model.set_value(myiter, EDITABLE, True)

            return myiter
        else:
            return None

    def _insertRowBraille(self, handl, com, inputEvHand,
                          parent=None, modif=False):
        """Appends a new row with the new braille binding data to the treeview

        Arguments:
        - handl:       the name of the handler associated to the brailleBinding
        - com:         the BrlTTY command
        - inputEvHand: the inputEventHandler with the new brailleBinding
        - parent:      the parent node of the treeview, where to append the kb
        - modif:       whether to check the modified field or not.

        Returns a Gtk.TreeIter pointing at the new row.
        """

        model = self.keyBindingsModel

        if parent is None:
            parent = self._getIterOf(guilabels.KB_GROUP_BRAILLE)

        if parent is not None:
            myiter = model.append(parent)
            model.set_value(myiter, HANDLER, handl)
            model.set_value(myiter, DESCRIP, inputEvHand.description)
            model.set_value(myiter, KEY1, str(com))
            model.set_value(myiter, TEXT1, braille.command_name[com])
            model.set_value(myiter, MODIF, modif)
            model.set_value(myiter, EDITABLE, False)
            return myiter
        else:
            return None

    def _markModified(self):
        """ Mark as modified the user custom key bindings:
        """

        try:
            self.script.setup_input_event_handlers()
            keyBinds = keybindings.KeyBindings()
            keyBinds = settings_manager.get_manager().override_key_bindings(
                self.script.input_event_handlers, keyBinds, enabled_only=False)
            keyBind = keybindings.KeyBinding(None, None, None, None)
            treeModel = self.keyBindingsModel

            myiter = treeModel.get_iter_first()
            while myiter is not None:
                iterChild = treeModel.iter_children(myiter)
                while iterChild is not None:
                    descrip = treeModel.get_value(iterChild, DESCRIP)
                    keyBind.handler = \
                        input_event.InputEventHandler(None, descrip)
                    if keyBinds.has_key_binding(keyBind,
                                              type_of_search="description"):
                        treeModel.set_value(iterChild, MODIF, True)
                    iterChild = treeModel.iter_next(iterChild)
                myiter = treeModel.iter_next(myiter)
        except Exception:
            debug.print_exception(debug.LEVEL_SEVERE)

    def _get_input_event_handler_key(self, event_handler):
        for key_name, handler in self.script.input_event_handlers.items():
            if handler == event_handler:
                return key_name

        return None

    def _populateKeyBindings(self, clearModel=True):
        """Fills the TreeView with the list of Orca keybindings

        Arguments:
        - clearModel: if True, initially clear out the key bindings model.
        """

        self.keyBindView.set_model(None)
        self.keyBindView.set_headers_visible(False)
        self.keyBindView.hide()
        if clearModel:
            self.keyBindingsModel.clear()
            self.kbindings = None

        appName = AXObject.get_name(self.script.app)
        iterApp = self._createNode(appName)
        iterOrca = self._createNode(guilabels.KB_GROUP_DEFAULT)
        iterNotificationPresenter = self._createNode(guilabels.KB_GROUP_NOTIFICATIONS)
        iterClipboardPresenter = self._createNode(guilabels.KB_GROUP_CLIPBOARD)
        iterFlatReviewPresenter = self._createNode(guilabels.KB_GROUP_FLAT_REVIEW)
        iterFind = self._createNode(guilabels.KB_GROUP_FIND)
        iterSpeechAndVerbosity = self._createNode(guilabels.KB_GROUP_SPEECH_VERBOSITY)
        iterSystemInfo = self._createNode(guilabels.KB_GROUP_SYSTEM_INFORMATION)
        iterSleepMode = self._createNode(guilabels.KB_GROUP_SLEEP_MODE)
        iterBookmarks = self._createNode(guilabels.KB_GROUP_BOOKMARKS)
        iterObjectNav = self._createNode(guilabels.KB_GROUP_OBJECT_NAVIGATION)
        iterCaretNav = self._createNode(guilabels.KB_GROUP_CARET_NAVIGATION)
        iterStructNav = self._createNode(guilabels.KB_GROUP_STRUCTURAL_NAVIGATION)
        iterTableNav = self._createNode(guilabels.KB_GROUP_TABLE_NAVIGATION)
        iterWhereAmIPresenter = self._createNode(guilabels.KB_GROUP_WHERE_AM_I)
        iterLearnMode = self._createNode(guilabels.KB_GROUP_LEARN_MODE)
        iterMouseReviewer = self._createNode(guilabels.KB_GROUP_MOUSE_REVIEW)
        iterActionPresenter = self._createNode(guilabels.KB_GROUP_ACTIONS)
        iterDebuggingTools = self._createNode(guilabels.KB_GROUP_DEBUGGING_TOOLS)

        if not self.kbindings:
            layout = settings_manager.get_manager().get_setting('keyboardLayout')
            isDesktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP

            self.kbindings = keybindings.KeyBindings()
            self.script.setup_input_event_handlers()
            allKeyBindings = self.script.get_key_bindings(False)
            defKeyBindings = self.script.get_default_keybindings_deprecated()
            npKeyBindings = self.script.get_notification_presenter().get_bindings(
                is_desktop=isDesktop)
            cbKeyBindings = self.script.get_clipboard_presenter().get_bindings(
                is_desktop=isDesktop)
            svKeyBindings = self.script.get_speech_and_verbosity_manager().get_bindings(
                is_desktop=isDesktop)
            sysKeyBindings = self.script.get_system_information_presenter().get_bindings(
                is_desktop=isDesktop)
            smKeyBindings = self.script.get_sleep_mode_manager().get_bindings(
                is_desktop=isDesktop)
            bmKeyBindings = self.script.get_bookmarks().get_bindings(
                is_desktop=isDesktop)
            onKeyBindings = self.script.get_object_navigator().get_bindings(
                is_desktop=isDesktop)
            cnKeyBindings = self.script.get_caret_navigator().get_bindings(
                is_desktop=isDesktop)
            snKeyBindings = self.script.get_structural_navigator().get_bindings(
                is_desktop=isDesktop)
            tnKeyBindings = self.script.get_table_navigator().get_bindings(
                is_desktop=isDesktop)
            lmKeyBindings = self.script.get_learn_mode_presenter().get_bindings(
                is_desktop=isDesktop)
            mrKeyBindings = self.script.get_mouse_reviewer().get_bindings(
                is_desktop=isDesktop)
            acKeyBindings = self.script.get_action_presenter().get_bindings(
                is_desktop=isDesktop)
            frKeyBindings = self.script.get_flat_review_presenter().get_bindings(
                is_desktop=isDesktop)
            findKeyBindings = self.script.get_flat_review_finder().get_bindings(
                is_desktop=isDesktop)
            waiKeyBindings = self.script.get_where_am_i_presenter().get_bindings(
                is_desktop=isDesktop)
            debuggingKeyBindings = self.script.get_debugging_tools_manager().get_bindings(
                is_desktop=isDesktop)

            for kb in allKeyBindings.key_bindings:
                if not self.kbindings.has_key_binding(kb, "strict"):
                    handl = self._get_input_event_handler_key(kb.handler)
                    if npKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterNotificationPresenter)
                    elif cbKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterClipboardPresenter)
                    elif onKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterObjectNav)
                    elif cnKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterCaretNav)
                    elif snKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterStructNav)
                    elif tnKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterTableNav)
                    elif frKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterFlatReviewPresenter)
                    elif findKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterFind)
                    elif waiKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterWhereAmIPresenter)
                    elif svKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterSpeechAndVerbosity)
                    elif sysKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterSystemInfo)
                    elif smKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterSleepMode)
                    elif bmKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterBookmarks)
                    elif lmKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterLearnMode)
                    elif acKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterActionPresenter)
                    elif mrKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterMouseReviewer)
                    elif debuggingKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterDebuggingTools)
                    elif not defKeyBindings.has_key_binding(kb, "description"):
                        self._insertRow(handl, kb, iterApp)
                    else:
                        self._insertRow(handl, kb, iterOrca)
                    self.kbindings.add(kb)

        if not self.keyBindingsModel.iter_has_child(iterApp):
            self.keyBindingsModel.remove(iterApp)

        self._updateOrcaModifier()
        self._markModified()
        iterBB = self._createNode(guilabels.KB_GROUP_BRAILLE)
        self.bbindings = self.script.get_braille_bindings()
        for com, inputEvHand in self.bbindings.items():
            handl = self._get_input_event_handler_key(inputEvHand)
            self._insertRowBraille(handl, com, inputEvHand, iterBB)

        self.keyBindView.set_model(self.keyBindingsModel)
        self.keyBindView.set_headers_visible(True)
        self.keyBindingsModel.set_sort_column_id(OLDTEXT1, Gtk.SortType.ASCENDING)
        self.keyBindView.show()

        # Keep track of new/unbound keybindings that have yet to be applied.
        #
        self.pendingKeyBindings = {}

    def _cleanupSpeechServers(self):
        """Remove unwanted factories and drivers for the current active
        factory, when the user dismisses the Orca Preferences dialog."""

        for workingFactory in self.workingFactories:
            if not (workingFactory == self.speechSystemsChoice):
                workingFactory.SpeechServer.shutdown_active_servers()
            else:
                servers = workingFactory.SpeechServer.get_speech_servers()
                for server in servers:
                    if not (server == self.speechServersChoice):
                        server.shutdown()

    def speechSupportChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           speechSupportCheckButton GtkCheckButton widget. The user has
           [un]checked the 'Enable Speech' checkbox. Set the 'enableSpeech'
           preference to the new value. Set the rest of the speech pane items
           [in]sensensitive depending upon whether this checkbox is checked.

        Arguments:
        - widget: the component that generated the signal.
        """

        enable = widget.get_active()
        self.prefsDict["enableSpeech"] = enable
        self.get_widget("speechOptionsGrid").set_sensitive(enable)

    def onlySpeakDisplayedTextToggled(self, widget):
        """Signal handler for the "toggled" signal for the GtkCheckButton
        onlySpeakDisplayedText. In addition to updating the preferences,
        set the sensitivity of the contextOptionsGrid.

        Arguments:
        - widget: the component that generated the signal.
        """

        enable = widget.get_active()
        self.prefsDict["onlySpeakDisplayedText"] = enable
        self.get_widget("contextOptionsGrid").set_sensitive(not enable)

    def speechSystemsChanged(self, widget):
        """Signal handler for the "changed" signal for the speechSystems
           GtkComboBox widget. The user has selected a different speech
           system. Clear the existing list of speech servers, and setup
           a new list of speech servers based on the new choice. Setup a
           new list of voices for the first speech server in the list.

        Arguments:
        - widget: the component that generated the signal.
        """

        if self.initializingSpeech:
            return

        selectedIndex = widget.get_active()
        self.speechSystemsChoice = self.speechSystemsChoices[selectedIndex]
        self._setupSpeechServers()

    def speechServersChanged(self, widget):
        """Signal handler for the "changed" signal for the speechServers
           GtkComboBox widget. The user has selected a different speech
           server. Clear the existing list of voices, and setup a new
           list of voices based on the new choice.

        Arguments:
        - widget: the component that generated the signal.
        """

        if self.initializingSpeech:
            return

        selectedIndex = widget.get_active()
        self.speechServersChoice = self.speechServersChoices[selectedIndex]

        # Whenever the speech servers change, we need to make sure we
        # clear whatever family was in use by the current voice types.
        # Otherwise, we can end up with family names from one server
        # bleeding over (e.g., "Paul" from Fonix ends up getting in
        # the "Default" voice type after we switch to eSpeak).
        #
        try:
            del self.defaultVoice[acss.ACSS.FAMILY]
            del self.uppercaseVoice[acss.ACSS.FAMILY]
            del self.hyperlinkVoice[acss.ACSS.FAMILY]
            del self.systemVoice[acss.ACSS.FAMILY]
        except Exception:
            pass

        self._setupVoices()

    def speechLanguagesChanged(self, widget):
        """Signal handler for the "value_changed" signal for the languages
           GtkComboBox widget. The user has selected a different voice
           language. Save the new voice language name based on the new choice.

        Arguments:
        - widget: the component that generated the signal.
        """

        if self.initializingSpeech:
            return

        selectedIndex = widget.get_active()
        try:
            self.speechLanguagesChoice = self.speechLanguagesChoices[selectedIndex]
            if (self.speechServersChoice, self.speechLanguagesChoice) in \
                    self.selectedFamilyChoices:
                i = self.selectedFamilyChoices[self.speechServersChoice, \
                        self.speechLanguagesChoice]
                family = self.speechFamiliesChoices[i]
                name = family[speechserver.VoiceFamily.NAME]
                language = family[speechserver.VoiceFamily.LANG]
                dialect = family[speechserver.VoiceFamily.DIALECT]
                variant = family[speechserver.VoiceFamily.VARIANT]
                voiceType = self.get_widget("voiceTypesCombo").get_active()
                self._setFamilyNameForVoiceType(voiceType, name, language, dialect, variant)
        except Exception:
            debug.print_exception(debug.LEVEL_SEVERE)

        # Remember the last family manually selected by the user for the
        # current speech server.
        #
        if not selectedIndex == -1:
            self.selectedLanguageChoices[self.speechServersChoice] = selectedIndex

        self._setupFamilies()

    def speechFamiliesChanged(self, widget):
        """Signal handler for the "value_changed" signal for the families
           GtkComboBox widget. The user has selected a different voice
           family. Save the new voice family name based on the new choice.

        Arguments:
        - widget: the component that generated the signal.
        """

        if self.initializingSpeech:
            return

        selectedIndex = widget.get_active()
        try:
            family = self.speechFamiliesChoices[selectedIndex]
            name = family[speechserver.VoiceFamily.NAME]
            language = family[speechserver.VoiceFamily.LANG]
            dialect = family[speechserver.VoiceFamily.DIALECT]
            variant = family[speechserver.VoiceFamily.VARIANT]
            voiceType = self.get_widget("voiceTypesCombo").get_active()
            self._setFamilyNameForVoiceType(voiceType, name, language, dialect, variant)
        except Exception:
            debug.print_exception(debug.LEVEL_SEVERE)

        # Remember the last family manually selected by the user for the
        # current speech server.
        #
        if not selectedIndex == -1:
            self.selectedFamilyChoices[self.speechServersChoice, \
                    self.speechLanguagesChoice] = selectedIndex

    def voiceTypesChanged(self, widget):
        """Signal handler for the "changed" signal for the voiceTypes
           GtkComboBox widget. The user has selected a different voice
           type. Setup the new family, rate, pitch and volume component
           values based on the new choice.

        Arguments:
        - widget: the component that generated the signal.
        """

        if self.initializingSpeech:
            return

        voiceType = widget.get_active()
        self._setVoiceSettingsForVoiceType(voiceType)

    def rateValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the rateScale
           GtkScale widget. The user has changed the current rate value.
           Save the new rate value based on the currently selected voice
           type.

        Arguments:
        - widget: the component that generated the signal.
        """

        rate = widget.get_value()
        voiceType = self.get_widget("voiceTypesCombo").get_active()
        self._setRateForVoiceType(voiceType, rate)
        voices = settings_manager.get_manager().get_setting('voices')
        voices.get(settings.DEFAULT_VOICE, {})[acss.ACSS.RATE] = rate
        settings_manager.get_manager().set_setting('voices', voices)

    def pitchValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the pitchScale
           GtkScale widget. The user has changed the current pitch value.
           Save the new pitch value based on the currently selected voice
           type.

        Arguments:
        - widget: the component that generated the signal.
        """

        pitch = widget.get_value()
        voiceType = self.get_widget("voiceTypesCombo").get_active()
        self._setPitchForVoiceType(voiceType, pitch)
        voices = settings_manager.get_manager().get_setting('voices')
        voices.get(settings.DEFAULT_VOICE, {})[acss.ACSS.AVERAGE_PITCH] = pitch
        settings_manager.get_manager().set_setting('voices', voices)

    def volumeValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the voiceScale
           GtkScale widget. The user has changed the current volume value.
           Save the new volume value based on the currently selected voice
           type.

        Arguments:
        - widget: the component that generated the signal.
        """

        volume = widget.get_value()
        voiceType = self.get_widget("voiceTypesCombo").get_active()
        self._setVolumeForVoiceType(voiceType, volume)
        voices = settings_manager.get_manager().get_setting('voices')
        voices.get(settings.DEFAULT_VOICE, {})[acss.ACSS.GAIN] = volume
        settings_manager.get_manager().set_setting('voices', voices)

    def checkButtonToggled(self, widget):
        """Signal handler for "toggled" signal for basic GtkCheckButton
           widgets. The user has altered the state of the checkbox.
           Set the preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        # To use this default handler please make sure:
        # The name of the setting that will be changed is: settingName
        # The id of the widget in the ui should be: settingNameCheckButton
        #
        settingName = Gtk.Buildable.get_name(widget)
        # strip "CheckButton" from the end.
        settingName = settingName[:-11]
        self.prefsDict[settingName] = widget.get_active()

    def brailleSelectionChanged(self, widget):
        """Signal handler for the "toggled" signal for the
           brailleSelectionNoneButton, brailleSelection7Button,
           brailleSelection8Button or brailleSelectionBothButton
           GtkRadioButton widgets. The user has toggled the braille
           selection indicator value. If this signal was generated
           as the result of a radio button getting selected (as
           opposed to a radio button losing the selection), set the
           'brailleSelectorIndicator' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        if widget.get_active():
            if widget.get_label() == guilabels.BRAILLE_DOT_7:
                self.prefsDict["brailleSelectorIndicator"] = \
                    settings.BRAILLE_UNDERLINE_7
            elif widget.get_label() == guilabels.BRAILLE_DOT_8:
                self.prefsDict["brailleSelectorIndicator"] = \
                    settings.BRAILLE_UNDERLINE_8
            elif widget.get_label() == guilabels.BRAILLE_DOT_7_8:
                self.prefsDict["brailleSelectorIndicator"] = \
                    settings.BRAILLE_UNDERLINE_BOTH
            else:
                self.prefsDict["brailleSelectorIndicator"] = \
                    settings.BRAILLE_UNDERLINE_NONE

    def brailleLinkChanged(self, widget):
        """Signal handler for the "toggled" signal for the
           brailleLinkNoneButton, brailleLink7Button,
           brailleLink8Button or brailleLinkBothButton
           GtkRadioButton widgets. The user has toggled the braille
           link indicator value. If this signal was generated
           as the result of a radio button getting selected (as
           opposed to a radio button losing the selection), set the
           'brailleLinkIndicator' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        if widget.get_active():
            if widget.get_label() == guilabels.BRAILLE_DOT_7:
                self.prefsDict["brailleLinkIndicator"] = \
                    settings.BRAILLE_UNDERLINE_7
            elif widget.get_label() == guilabels.BRAILLE_DOT_8:
                self.prefsDict["brailleLinkIndicator"] = \
                    settings.BRAILLE_UNDERLINE_8
            elif widget.get_label() == guilabels.BRAILLE_DOT_7_8:
                self.prefsDict["brailleLinkIndicator"] = \
                    settings.BRAILLE_UNDERLINE_BOTH
            else:
                self.prefsDict["brailleLinkIndicator"] = \
                    settings.BRAILLE_UNDERLINE_NONE

    def brailleIndicatorChanged(self, widget):
        """Signal handler for the "toggled" signal for the
           textBrailleNoneButton, textBraille7Button, textBraille8Button
           or textBrailleBothButton GtkRadioButton widgets. The user has
           toggled the text attributes braille indicator value. If this signal
           was generated as the result of a radio button getting selected
           (as opposed to a radio button losing the selection), set the
           'textAttributesBrailleIndicator' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        if widget.get_active():
            if widget.get_label() == guilabels.BRAILLE_DOT_7:
                self.prefsDict["textAttributesBrailleIndicator"] = \
                    settings.BRAILLE_UNDERLINE_7
            elif widget.get_label() == guilabels.BRAILLE_DOT_8:
                self.prefsDict["textAttributesBrailleIndicator"] = \
                    settings.BRAILLE_UNDERLINE_8
            elif widget.get_label() == guilabels.BRAILLE_DOT_7_8:
                self.prefsDict["textAttributesBrailleIndicator"] = \
                    settings.BRAILLE_UNDERLINE_BOTH
            else:
                self.prefsDict["textAttributesBrailleIndicator"] = \
                    settings.BRAILLE_UNDERLINE_NONE

    def punctuationLevelChanged(self, widget):
        """Signal handler for the "toggled" signal for the noneButton,
           someButton or allButton GtkRadioButton widgets. The user has
           toggled the speech punctuation level value. If this signal
           was generated as the result of a radio button getting selected
           (as opposed to a radio button losing the selection), set the
           'verbalizePunctuationStyle' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        if widget.get_active():
            if widget.get_label() == guilabels.PUNCTUATION_STYLE_NONE:
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_NONE
            elif widget.get_label() == guilabels.PUNCTUATION_STYLE_SOME:
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_SOME
            elif widget.get_label() == guilabels.PUNCTUATION_STYLE_MOST:
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_MOST
            else:
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_ALL

    def orcaModifierChanged(self, widget):
        """Signal handler for the changed signal for the orcaModifierComboBox
           Set the 'orcaModifierKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        model = widget.get_model()
        myIter = widget.get_active_iter()
        orcaModifier = model[myIter][0]
        self.prefsDict["orcaModifierKeys"] = orcaModifier.split(', ')

    def progressBarVerbosityChanged(self, widget):
        """Signal handler for the changed signal for the progressBarVerbosity
           GtkComboBox widget. Set the 'progressBarVerbosity' preference to
           the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        model = widget.get_model()
        myIter = widget.get_active_iter()
        progressBarVerbosity = model[myIter][0]
        if progressBarVerbosity == guilabels.PROGRESS_BAR_ALL:
            self.prefsDict["progressBarVerbosity"] = \
                settings.PROGRESS_BAR_ALL
        elif progressBarVerbosity == guilabels.PROGRESS_BAR_WINDOW:
            self.prefsDict["progressBarVerbosity"] = \
                settings.PROGRESS_BAR_WINDOW
        else:
            self.prefsDict["progressBarVerbosity"] = \
                settings.PROGRESS_BAR_APPLICATION

    def capitalizationStyleChanged(self, widget):
        model = widget.get_model()
        myIter = widget.get_active_iter()
        capitalizationStyle = model[myIter][0]
        if capitalizationStyle == guilabels.CAPITALIZATION_STYLE_ICON:
            self.prefsDict["capitalizationStyle"] = settings.CAPITALIZATION_STYLE_ICON
        elif capitalizationStyle == guilabels.CAPITALIZATION_STYLE_SPELL:
            self.prefsDict["capitalizationStyle"] = settings.CAPITALIZATION_STYLE_SPELL
        else:
            self.prefsDict["capitalizationStyle"] = settings.CAPITALIZATION_STYLE_NONE
        self.script.get_speech_and_verbosity_manager().update_capitalization_style()

    def sayAllStyleChanged(self, widget):
        """Signal handler for the "changed" signal for the sayAllStyle
           GtkComboBox widget. Set the 'sayAllStyle' preference to the
           new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        model = widget.get_model()
        myIter = widget.get_active_iter()
        sayAllStyle = model[myIter][0]
        if sayAllStyle == guilabels.SAY_ALL_STYLE_LINE:
            self.prefsDict["sayAllStyle"] = settings.SAYALL_STYLE_LINE
        elif sayAllStyle == guilabels.SAY_ALL_STYLE_SENTENCE:
            self.prefsDict["sayAllStyle"] = settings.SAYALL_STYLE_SENTENCE

    def dateFormatChanged(self, widget):
        """Signal handler for the "changed" signal for the dateFormat
           GtkComboBox widget. Set the 'dateFormat' preference to the
           new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        dateFormatCombo = widget.get_active()
        newFormat = messages.DATE_FORMAT_LOCALE
        if dateFormatCombo == DATE_FORMAT_NUMBERS_DM:
            newFormat = messages.DATE_FORMAT_NUMBERS_DM
        elif dateFormatCombo == DATE_FORMAT_NUMBERS_MD:
            newFormat = messages.DATE_FORMAT_NUMBERS_MD
        elif dateFormatCombo == DATE_FORMAT_NUMBERS_DMY:
            newFormat = messages.DATE_FORMAT_NUMBERS_DMY
        elif dateFormatCombo == DATE_FORMAT_NUMBERS_MDY:
            newFormat = messages.DATE_FORMAT_NUMBERS_MDY
        elif dateFormatCombo == DATE_FORMAT_NUMBERS_YMD:
            newFormat = messages.DATE_FORMAT_NUMBERS_YMD
        elif dateFormatCombo == DATE_FORMAT_FULL_DM:
            newFormat = messages.DATE_FORMAT_FULL_DM
        elif dateFormatCombo == DATE_FORMAT_FULL_MD:
            newFormat = messages.DATE_FORMAT_FULL_MD
        elif dateFormatCombo == DATE_FORMAT_FULL_DMY:
            newFormat = messages.DATE_FORMAT_FULL_DMY
        elif dateFormatCombo == DATE_FORMAT_FULL_MDY:
            newFormat = messages.DATE_FORMAT_FULL_MDY
        elif dateFormatCombo == DATE_FORMAT_FULL_YMD:
            newFormat = messages.DATE_FORMAT_FULL_YMD
        elif dateFormatCombo == DATE_FORMAT_ABBREVIATED_DM:
            newFormat = messages.DATE_FORMAT_ABBREVIATED_DM
        elif dateFormatCombo == DATE_FORMAT_ABBREVIATED_MD:
            newFormat = messages.DATE_FORMAT_ABBREVIATED_MD
        elif dateFormatCombo == DATE_FORMAT_ABBREVIATED_DMY:
            newFormat = messages.DATE_FORMAT_ABBREVIATED_DMY
        elif dateFormatCombo == DATE_FORMAT_ABBREVIATED_MDY:
            newFormat = messages.DATE_FORMAT_ABBREVIATED_MDY
        elif dateFormatCombo == DATE_FORMAT_ABBREVIATED_YMD:
            newFormat = messages.DATE_FORMAT_ABBREVIATED_YMD
        self.prefsDict["presentDateFormat"] = newFormat

    def timeFormatChanged(self, widget):
        """Signal handler for the "changed" signal for the timeFormat
           GtkComboBox widget. Set the 'timeFormat' preference to the
           new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        timeFormatCombo = widget.get_active()
        newFormat = messages.TIME_FORMAT_LOCALE
        if timeFormatCombo == TIME_FORMAT_12_HM:
            newFormat = messages.TIME_FORMAT_12_HM
        elif timeFormatCombo == TIME_FORMAT_12_HMS:
            newFormat = messages.TIME_FORMAT_12_HMS
        elif timeFormatCombo == TIME_FORMAT_24_HMS:
            newFormat = messages.TIME_FORMAT_24_HMS
        elif timeFormatCombo == TIME_FORMAT_24_HMS_WITH_WORDS:
            newFormat = messages.TIME_FORMAT_24_HMS_WITH_WORDS
        elif timeFormatCombo == TIME_FORMAT_24_HM:
            newFormat = messages.TIME_FORMAT_24_HM
        elif timeFormatCombo == TIME_FORMAT_24_HM_WITH_WORDS:
            newFormat  = messages.TIME_FORMAT_24_HM_WITH_WORDS
        self.prefsDict["presentTimeFormat"] =  newFormat

    def speechVerbosityChanged(self, widget):
        """Signal handler for the "toggled" signal for the speechBriefButton,
           or speechVerboseButton GtkRadioButton widgets. The user has
           toggled the speech verbosity level value. If this signal was
           generated as the result of a radio button getting selected
           (as opposed to a radio button losing the selection), set the
           'speechVerbosityLevel' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        if widget.get_active():
            if widget.get_label() == guilabels.VERBOSITY_LEVEL_BRIEF:
                self.prefsDict["speechVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_BRIEF
            else:
                self.prefsDict["speechVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_VERBOSE

    def progressBarUpdateIntervalValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           progressBarUpdateIntervalSpinButton GtkSpinButton widget.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["progressBarUpdateInterval"] = widget.get_value_as_int()

    def brailleFlashTimeValueChanged(self, widget):
        self.prefsDict["brailleFlashTime"] = widget.get_value_as_int() * 1000

    def abbrevRolenamesChecked(self, widget):
        """Signal handler for the "toggled" signal for the abbrevRolenames
           GtkCheckButton widget. The user has [un]checked the 'Abbreviated
           Rolenames' checkbox. Set the 'brailleRolenameStyle' preference
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        if widget.get_active():
            self.prefsDict["brailleRolenameStyle"] = \
                settings.BRAILLE_ROLENAME_STYLE_SHORT
        else:
            self.prefsDict["brailleRolenameStyle"] = \
                settings.BRAILLE_ROLENAME_STYLE_LONG

    def brailleVerbosityChanged(self, widget):
        """Signal handler for the "toggled" signal for the brailleBriefButton,
           or brailleVerboseButton GtkRadioButton widgets. The user has
           toggled the braille verbosity level value. If this signal was
           generated as the result of a radio button getting selected
           (as opposed to a radio button losing the selection), set the
           'brailleVerbosityLevel' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        if widget.get_active():
            if widget.get_label() == guilabels.VERBOSITY_LEVEL_BRIEF:
                self.prefsDict["brailleVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_BRIEF
            else:
                self.prefsDict["brailleVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_VERBOSE

    def keyModifiedToggle(self, cell, path, model, col):
        """When the user changes a checkbox field (boolean field)"""

        model[path][col] = not model[path][col]
        return

    def editingKey(self, cell, editable, path, treeModel):
        """Starts user input of a Key for a selected key binding"""

        self._presentMessage(messages.KB_ENTER_NEW_KEY)
        script_manager.get_manager().get_active_script().remove_key_grabs("Capturing keys")
        input_event_manager.get_manager().unmap_all_modifiers()
        editable.connect('key-press-event', self.kbKeyPressed)
        return

    def editingCanceledKey(self, editable):
        """Stops user input of a Key for a selected key binding"""

        self._capturedKey = []
        script_manager.get_manager().get_active_script().refresh_key_grabs("Done capturing keys")
        return

    def _processKeyCaptured(self, keyPressedEvent):
        """Called when a new key event arrives and we are capturing keys.
        (used for key bindings redefinition)
        """

        # We want the keyname rather than the printable character.
        # If it's not on the keypad, get the name of the unshifted
        # character. (i.e. "1" instead of "!")
        #
        keycode = keyPressedEvent.hardware_keycode
        keymap = Gdk.Keymap.get_default()
        entries_for_keycode = keymap.get_entries_for_keycode(keycode)
        entries = entries_for_keycode[-1]
        eventString = Gdk.keyval_name(entries[0])
        eventState = keyPressedEvent.state

        orcaMods = settings.orcaModifierKeys
        if eventString in orcaMods:
            self._capturedKey = ['', keybindings.ORCA_MODIFIER_MASK, 0]
            return False

        modifierKeys =  ['Alt_L', 'Alt_R', 'Control_L', 'Control_R',
                         'Shift_L', 'Shift_R', 'Meta_L', 'Meta_R',
                         'Num_Lock', 'Caps_Lock', 'Shift_Lock']
        if eventString in modifierKeys:
            return False

        eventState = eventState & Gtk.accelerator_get_default_mod_mask()
        if not self._capturedKey \
           or eventString in ['Return', 'Escape']:
            self._capturedKey = [eventString, eventState, 1]
            return True

        string, modifiers, clickCount = self._capturedKey
        is_orca_modifier = modifiers & keybindings.ORCA_MODIFIER_MASK
        if is_orca_modifier:
            eventState |= keybindings.ORCA_MODIFIER_MASK
            self._capturedKey = [eventString, eventState, clickCount + 1]

        return True

    def kbKeyPressed(self, editable, event):
        """Special handler for the key_pressed events when editing the
        keybindings.  This lets us control what gets inserted into the
        entry.
        """

        keyProcessed = self._processKeyCaptured(event)
        if not keyProcessed:
            return True

        if not self._capturedKey:
            return False

        keyName, modifiers, clickCount = self._capturedKey
        if not keyName or keyName in ["Return", "Escape"]:
            return False

        is_orca_modifier = modifiers & keybindings.ORCA_MODIFIER_MASK
        if keyName in ["Delete", "BackSpace"] and not is_orca_modifier:
            editable.set_text("")
            self._presentMessage(messages.KB_DELETED)
            self._capturedKey = []
            self.newBinding = None
            return True

        self.newBinding = keybindings.KeyBinding(keyName,
                                                 keybindings.DEFAULT_MODIFIER_MASK,
                                                 modifiers,
                                                 None,
                                                 clickCount)
        modifierNames = keybindings.get_modifier_names(modifiers)
        clickCountString = self._clickCountToString(clickCount)
        newString = modifierNames + keyName + clickCountString
        description = self.pendingKeyBindings.get(newString)

        if description is None:

            def match(x):
                return x.keysymstring == keyName and x.modifiers == modifiers \
                    and x.click_count == clickCount and x.handler

            matches = list(filter(match, self.kbindings.key_bindings))
            if matches:
                description = matches[0].handler.description

        if description:
            msg = messages.KB_ALREADY_BOUND % description
            delay = int(1000 * settings.doubleClickTimeout)
            self._pending_already_bound_message_id = GLib.timeout_add(
                delay, self._presentMessage, msg)

        else:
            if self._pending_already_bound_message_id is not None:
                GLib.source_remove(self._pending_already_bound_message_id)
                self._pending_already_bound_message_id = None
            msg = messages.KB_CAPTURED % newString
            editable.set_text(newString)
            self._presentMessage(msg)

        return True

    def editedKey(self, cell, path, new_text, treeModel,
                  modMask, modUsed, key, click_count, text):
        """The user changed the key for a Keybinding: update the model of
        the treeview.
        """

        self._capturedKey = []
        script_manager.get_manager().get_active_script().refresh_key_grabs("Done capturing keys")
        myiter = treeModel.get_iter_from_string(path)
        try:
            originalBinding = treeModel.get_value(myiter, text)
        except Exception:
            originalBinding = ''
        modified = (originalBinding != new_text)

        try:
            string = self.newBinding.keysymstring
            mods = self.newBinding.modifiers
            clickCount = self.newBinding.click_count
        except Exception:
            string = ''
            mods = 0
            clickCount = 1

        mods = mods & Gdk.ModifierType.MODIFIER_MASK
        if mods & (1 << Atspi.ModifierType.SHIFTLOCK) \
           and mods & keybindings.ORCA_MODIFIER_MASK:
            mods ^= (1 << Atspi.ModifierType.SHIFTLOCK)

        treeModel.set(myiter,
                      modMask, str(keybindings.DEFAULT_MODIFIER_MASK),
                      modUsed, str(int(mods)),
                      key, string,
                      text, new_text,
                      click_count, str(clickCount),
                      MODIF, modified)
        if new_text:
            message = messages.KB_CAPTURED_CONFIRMATION % new_text
            description = treeModel.get_value(myiter, DESCRIP)
            self.pendingKeyBindings[new_text] = description
        else:
            message = messages.KB_DELETED_CONFIRMATION

        if modified:
            self._presentMessage(message)
            self.pendingKeyBindings[originalBinding] = ""

        return

    def presentToolTipsChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           presentToolTipsCheckButton GtkCheckButton widget.
           The user has [un]checked the 'Present ToolTips'
           checkbox. Set the 'presentToolTips'
           preference to the new value if the user can present tooltips.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["presentToolTips"] = widget.get_active()

    def keyboardLayoutChanged(self, widget):
        """Signal handler for the "toggled" signal for the generalDesktopButton,
           or generalLaptopButton GtkRadioButton widgets. The user has
           toggled the keyboard layout value. If this signal was
           generated as the result of a radio button getting selected
           (as opposed to a radio button losing the selection), set the
           'keyboardLayout' preference to the new value. Also set the
           matching list of Orca modifier keys

        Arguments:
        - widget: the component that generated the signal.
        """

        if widget.get_active():
            if widget.get_label() == guilabels.KEYBOARD_LAYOUT_DESKTOP:
                self.prefsDict["keyboardLayout"] = \
                    settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP
                self.prefsDict["orcaModifierKeys"] = \
                    settings.DESKTOP_MODIFIER_KEYS
            else:
                self.prefsDict["keyboardLayout"] = \
                    settings.GENERAL_KEYBOARD_LAYOUT_LAPTOP
                self.prefsDict["orcaModifierKeys"] = \
                    settings.LAPTOP_MODIFIER_KEYS

    def pronunciationAddButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        pronunciationAddButton GtkButton widget. The user has clicked
        the Add button on the Pronunciation pane. A new row will be
        added to the end of the pronunciation dictionary list. Both the
        actual and replacement strings will initially be set to an empty
        string. Focus will be moved to that row.

        Arguments:
        - widget: the component that generated the signal.
        """

        model = self.pronunciationView.get_model()
        thisIter = model.append()
        model.set(thisIter, ACTUAL, "", REPLACEMENT, "")
        path = model.get_path(thisIter)
        col = self.pronunciationView.get_column(0)
        self.pronunciationView.grab_focus()
        self.pronunciationView.set_cursor(path, col, True)

    def pronunciationDeleteButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        pronunciationDeleteButton GtkButton widget. The user has clicked
        the Delete button on the Pronunciation pane. The row in the
        pronunciation dictionary list with focus will be deleted.

        Arguments:
        - widget: the component that generated the signal.
        """

        model, oldIter = self.pronunciationView.get_selection().get_selected()
        model.remove(oldIter)

    def textMoveToTopButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        textMoveToTopButton GtkButton widget. The user has clicked
        the Move to top button. Move the selected rows in the text
        attribute view to the very top of the list and then update
        the preferences.

        Arguments:
        - widget: the component that generated the signal.
        """

        textSelection = self.getTextAttributesView.get_selection()
        [model, paths] = textSelection.get_selected_rows()
        for path in paths:
            thisIter = model.get_iter(path)
            model.move_after(thisIter, None)
        self._updateTextDictEntry()

    def textMoveUpOneButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        textMoveUpOneButton GtkButton widget. The user has clicked
        the Move up one button. Move the selected rows in the text
        attribute view up one row in the list and then update the
        preferences.

        Arguments:
        - widget: the component that generated the signal.
        """

        textSelection = self.getTextAttributesView.get_selection()
        [model, paths] = textSelection.get_selected_rows()
        for path in paths:
            thisIter = model.get_iter(path)
            indices = path.get_indices()
            if indices[0]:
                otherIter = model.iter_nth_child(None, indices[0]-1)
                model.swap(thisIter, otherIter)
        self._updateTextDictEntry()

    def textMoveDownOneButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        textMoveDownOneButton GtkButton widget. The user has clicked
        the Move down one button. Move the selected rows in the text
        attribute view down one row in the list and then update the
        preferences.

        Arguments:
        - widget: the component that generated the signal.
        """

        textSelection = self.getTextAttributesView.get_selection()
        [model, paths] = textSelection.get_selected_rows()
        noRows = model.iter_n_children(None)
        for path in paths:
            thisIter = model.get_iter(path)
            indices = path.get_indices()
            if indices[0] < noRows-1:
                otherIter = model.iter_next(thisIter)
                model.swap(thisIter, otherIter)
        self._updateTextDictEntry()

    def textMoveToBottomButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        textMoveToBottomButton GtkButton widget. The user has clicked
        the Move to bottom button. Move the selected rows in the text
        attribute view to the bottom of the list and then update the
        preferences.

        Arguments:
        - widget: the component that generated the signal.
        """

        textSelection = self.getTextAttributesView.get_selection()
        [model, paths] = textSelection.get_selected_rows()
        for path in paths:
            thisIter = model.get_iter(path)
            model.move_before(thisIter, None)
        self._updateTextDictEntry()

    def helpButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the helpButton
           GtkButton widget. The user has clicked the Help button.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.script.get_learn_mode_presenter().show_help(page="preferences")

    def restoreSettings(self):
        """Restore the settings we saved away when opening the preferences
           dialog."""
        # Restore the default rate/pitch/gain,
        # in case the user played with the sliders.
        #
        voices = settings_manager.get_manager().get_setting('voices')
        defaultVoice = voices.get(settings.DEFAULT_VOICE)
        if defaultVoice is not None:
            defaultVoice[acss.ACSS.GAIN] = self.savedGain
            defaultVoice[acss.ACSS.AVERAGE_PITCH] = self.savedPitch
            defaultVoice[acss.ACSS.RATE] = self.savedRate

    def saveBasicSettings(self):
        if not self._isInitialSetup:
            self.restoreSettings()

        enable = self.get_widget("speechSupportCheckButton").get_active()
        self.prefsDict["enableSpeech"] = enable

        if self.speechSystemsChoice:
            self.prefsDict["speechServerFactory"] = \
                self.speechSystemsChoice.__name__

        if self.speechServersChoice:
            self.prefsDict["speechServerInfo"] = \
                self.speechServersChoice.get_info()

        if self.defaultVoice is not None:
            self.prefsDict["voices"] = {
                settings.DEFAULT_VOICE: acss.ACSS(self.defaultVoice),
                settings.UPPERCASE_VOICE: acss.ACSS(self.uppercaseVoice),
                settings.HYPERLINK_VOICE: acss.ACSS(self.hyperlinkVoice),
                settings.SYSTEM_VOICE: acss.ACSS(self.systemVoice),
            }

    def applyButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the applyButton
           GtkButton widget. The user has clicked the Apply button.
           Write out the users preferences. If GNOME accessibility hadn't
           previously been enabled, warn the user that they will need to
           log out. Shut down any active speech servers that were started.
           Reload the users preferences to get the new speech, braille and
           key echo value to take effect. Do not dismiss the configuration
           window.

        Arguments:
        - widget: the component that generated the signal.
        """

        msg = "PREFERENCES DIALOG: Apply button clicked"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        self.saveBasicSettings()
        updated_values = self.typing_echo_grid.save_settings()
        self.prefsDict.update(updated_values)
        activeProfile = self.getComboBoxList(self.profilesCombo)
        startingProfile = self.getComboBoxList(self.startingProfileCombo)

        self.prefsDict['profile'] = activeProfile
        self.prefsDict['activeProfile'] = activeProfile
        self.prefsDict['startingProfile'] = startingProfile
        settings_manager.get_manager().set_starting_profile(startingProfile)

        self.writeUserPreferences()
        orca.load_user_settings(self.script)
        self.typing_echo_grid.reload()
        braille.checkBrailleSetting()
        self._initSpeechState()
        self._populateKeyBindings()
        self.__initProfileCombo()

        msg = "PREFERENCES DIALOG: Handling Apply button click complete"
        debug.print_message(debug.LEVEL_ALL, msg, True)

    def cancelButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the cancelButton
           GtkButton widget. The user has clicked the Cancel button.
           Don't write out the preferences. Destroy the configuration window.

        Arguments:
        - widget: the component that generated the signal.
        """

        msg = "PREFERENCES DIALOG: Cancel button clicked"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        self.windowClosed(widget)
        self.get_widget("orcaSetupWindow").destroy()

        msg = "PREFERENCES DIALOG: Handling Cancel button click complete"
        debug.print_message(debug.LEVEL_ALL, msg, True)

    def okButtonClicked(self, widget=None):
        """Signal handler for the "clicked" signal for the okButton
           GtkButton widget. The user has clicked the OK button.
           Write out the users preferences. If GNOME accessibility hadn't
           previously been enabled, warn the user that they will need to
           log out. Shut down any active speech servers that were started.
           Reload the users preferences to get the new speech, braille and
           key echo value to take effect. Hide the configuration window.

        Arguments:
        - widget: the component that generated the signal.
        """

        msg = "PREFERENCES DIALOG: OK button clicked"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        self.applyButtonClicked(widget)
        self._cleanupSpeechServers()
        self.get_widget("orcaSetupWindow").destroy()

        msg = "PREFERENCES DIALOG: Handling OK button click complete"
        debug.print_message(debug.LEVEL_ALL, msg, True)

    def windowClosed(self, widget):
        """Signal handler for the "closed" signal for the orcaSetupWindow
           GtkWindow widget. This is effectively the same as pressing the
           cancel button, except the window is destroyed for us.

        Arguments:
        - widget: the component that generated the signal.
        """

        msg = "PREFERENCES DIALOG: Window is being closed"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        self.suspendEvents()

        if not settings.speechSystemOverride:
            factory = settings_manager.get_manager().get_setting('speechServerFactory')
            if factory:
                self._setSpeechSystemsChoice(factory)

            server = settings_manager.get_manager().get_setting('speechServerInfo')
            if server:
                self._setSpeechServersChoice(server)

        self._cleanupSpeechServers()
        self.restoreSettings()

        GObject.timeout_add(1000, self.resumeEvents)

        msg = "PREFERENCES DIALOG: Window closure complete"
        debug.print_message(debug.LEVEL_ALL, msg, True)

    def windowDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the Preferences dialog."""

        msg = "PREFERENCES DIALOG: Window is being destroyed"
        debug.print_message(debug.LEVEL_ALL, msg, True)

        self.keyBindView.set_model(None)
        self.getTextAttributesView.set_model(None)
        self.pronunciationView.set_model(None)
        self.keyBindView.set_headers_visible(False)
        self.getTextAttributesView.set_headers_visible(False)
        self.pronunciationView.set_headers_visible(False)
        self.keyBindView.hide()
        self.getTextAttributesView.hide()
        self.pronunciationView.hide()
        OrcaSetupGUI.DIALOG = None

        msg = "PREFERENCES DIALOG: Window destruction complete"
        debug.print_message(debug.LEVEL_ALL, msg, True)

    def resumeEvents(self):
        msg = "PREFERENCES DIALOG: Re-registering floody events."
        debug.print_message(debug.LEVEL_ALL, msg, True)

        manager = event_manager.get_manager()
        manager.register_listener("object:state-changed:showing")
        manager.register_listener("object:children-changed:remove")
        manager.register_listener("object:selection-changed")
        manager.register_listener("object:property-change:accessible-name")

    def suspendEvents(self):
        msg = "PREFERENCES DIALOG: Deregistering floody events."
        debug.print_message(debug.LEVEL_ALL, msg, True)

        manager = event_manager.get_manager()
        manager.deregister_listener("object:state-changed:showing")
        manager.deregister_listener("object:children-changed:remove")
        manager.deregister_listener("object:selection-changed")
        manager.deregister_listener("object:property-change:accessible-name")

    def showProfileGUI(self, widget):
        """Show profile Dialog to add a new one"""

        orca_gui_profile.showProfileUI(self)

    def saveProfile(self, profileToSaveLabel):
        """Creates a new profile based on the name profileToSaveLabel and
        updates the Preferences dialog combo boxes accordingly."""

        if not profileToSaveLabel:
            return
        profileToSave = profileToSaveLabel.replace(' ', '_').lower()
        profile = [profileToSaveLabel, profileToSave]

        def saveActiveProfile(newProfile = True):
            if newProfile:
                activeProfileIter = self.profilesComboModel.append(profile)
                self.profilesCombo.set_active_iter(activeProfileIter)

            self.prefsDict['profile'] = profile
            self.prefsDict['activeProfile'] = profile
            self.saveBasicSettings()
            self.writeUserPreferences()

        available_profiles = [p[1] for p in self.__getAvailableProfiles()]
        if isinstance(profileToSave, str) \
                and profileToSave != '' \
                and profileToSave not in available_profiles \
                and profileToSave != self._defaultProfile[1]:
            saveActiveProfile()
        else:
            if profileToSave is not None:
                message = guilabels.PROFILE_CONFLICT_MESSAGE % \
                    f"<b>{GLib.markup_escape_text(profileToSaveLabel)}</b>"
                dialog = Gtk.MessageDialog(None,
                        Gtk.DialogFlags.MODAL,
                        type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.YES_NO)
                dialog.set_markup(f"<b>{guilabels.PROFILE_CONFLICT_LABEL}</b>")
                dialog.format_secondary_markup(message)
                dialog.set_title(guilabels.PROFILE_CONFLICT_TITLE)
                response = dialog.run()
                if response == Gtk.ResponseType.YES:
                    dialog.destroy()
                    saveActiveProfile(False)
                else:
                    dialog.destroy()


    def removeProfileButtonClicked(self, widget):
        """Remove profile button clicked handler

        If we removed the last profile, a default one will automatically get
        added back by the settings manager.
        """

        oldProfile = self.getComboBoxList(self.profilesCombo)

        message = guilabels.PROFILE_REMOVE_MESSAGE % \
            f"<b>{GLib.markup_escape_text(oldProfile[0])}</b>"
        dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.YES_NO)
        dialog.set_markup(f"<b>{guilabels.PROFILE_REMOVE_LABEL}</b>")
        dialog.format_secondary_markup(message)
        if dialog.run() == Gtk.ResponseType.YES:
            # If we remove the currently used starting profile, fallback on
            # the first listed profile, or the default one if there's
            # nothing better
            newStartingProfile = self.prefsDict.get('startingProfile')
            if not newStartingProfile or newStartingProfile == oldProfile:
                newStartingProfile = self._defaultProfile
                for row in self.profilesComboModel:
                    rowProfile = row[:]
                    if rowProfile != oldProfile:
                        newStartingProfile = rowProfile
                        break
            # Update the current profile to the active profile unless we're
            # removing that one, in which case we use the new starting
            # profile
            newProfile = self.prefsDict.get('activeProfile')
            if not newProfile or newProfile == oldProfile:
                newProfile = newStartingProfile

            settings_manager.get_manager().remove_profile(oldProfile[1])
            self.loadProfile(newProfile)

            # Make sure nothing is referencing the removed profile anymore
            startingProfile = self.prefsDict.get('startingProfile')
            if not startingProfile or startingProfile == oldProfile:
                self.prefsDict['startingProfile'] = newStartingProfile
                settings_manager.get_manager().set_starting_profile(newStartingProfile)
                self.writeUserPreferences()

        dialog.destroy()

    def loadProfileButtonClicked(self, widget):
        """Load profile button clicked handler"""

        if self._isInitialSetup:
            return

        dialog = Gtk.MessageDialog(None,
                Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.YES_NO)

        dialog.set_markup(f"<b>{guilabels.PROFILE_LOAD_LABEL}</b>")
        dialog.format_secondary_markup(guilabels.PROFILE_LOAD_MESSAGE)
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            dialog.destroy()
            self.loadSelectedProfile()
        else:
            dialog.destroy()

    def loadSelectedProfile(self):
        """Load selected profile"""

        activeProfile = self.getComboBoxList(self.profilesCombo)
        self.loadProfile(activeProfile)

    def loadProfile(self, profile):
        """Load profile"""

        self.saveBasicSettings()

        self.prefsDict['activeProfile'] = profile
        settings_manager.get_manager().set_profile(profile[1])
        self.prefsDict = settings_manager.get_manager().get_general_settings(profile[1])

        orca.load_user_settings(skip_reload_message=True)
        self.typing_echo_grid.reload()

        self._initGUIState()

        braille.checkBrailleSetting()

        self._initSpeechState()

        self._populateKeyBindings()

        self.__initProfileCombo()
