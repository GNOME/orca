# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Displays a GUI for the user to set Orca preferences."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import os
import sys
import debug
import gtk
import gobject
import pango   # for ellipsize property constants of CellRendererText
import locale

import acss
import mag
import orca
import orca_gtkbuilder
import orca_prefs
import orca_state
import platform
import settings
import default    # for the default keyBindings
import input_event
import keybindings
import pronunciation_dict
import braille
import speech
import speechserver
import text_attribute_names

try:
    import louis
except ImportError:
    louis = None

from orca_i18n import _  # for gettext support
from orca_i18n import C_ # to provide qualified translatable strings

(HANDLER, DESCRIP, MOD_MASK1, MOD_USED1, KEY1, CLICK_COUNT1, OLDTEXT1, \
 TEXT1, MOD_MASK2, MOD_USED2, KEY2, CLICK_COUNT2, OLDTEXT2, TEXT2, MODIF, \
 EDITABLE) = range(16)

(NAME, IS_SPOKEN, IS_BRAILLED, VALUE) = range(4)

(ACTUAL, REPLACEMENT) = range(2)

# Must match the order of voice types in the GtkBuilder file.
#
(DEFAULT, UPPERCASE, HYPERLINK) = range(3)

class OrcaSetupGUI(orca_gtkbuilder.GtkBuilderWrapper):

    # Translators: this is an algorithm for tracking an object
    # of interest (mouse pointer, caret, or widget) with the
    # magnifier.  Centered means that Orca attempts to keep
    # the object of interest in the center of the magnified window.
    #
    magTrackingCenteredStr = _("Centered")

    # Translators: there is no special algorithm used for tracking an
    # object of interest (mouse pointer, caret, or widget) with the
    # magnifier.
    #
    magTrackingNoneStr = _("None")

    # Translators: this is an algorithm for tracking the mouse
    # with the magnifier.  Proportional means that Orca attempts
    # to position the mouse in the magnifier window in a way
    # such that it helps represent where on the desktop the mouse
    # is.  For example, if the mouse is 25% from the left edge of
    # the desktop, Orca positions the mouse 25% from the left edge
    # of the magnified region.
    #
    magTrackingProportionalStr = _("Proportional")

    # Translators: this is an algorithm for tracking an object
    # of interest (mouse pointer, caret, or widget) with the
    # magnifier.  Push means that Orca will move the magnified
    # region just enough to display the object of interest.
    #
    magTrackingPushStr = _("Push")

    def __init__(self, fileName, windowName, prefsDict = None):
        """Initialize the Orca configuration GUI.

        Arguments:
        - fileName: name of the GtkBuilder file.
        - windowName: name of the component to get from the GtkBuilder
          file.
        """

        orca_gtkbuilder.GtkBuilderWrapper.__init__(self, fileName, windowName)

        self.prefsDict = prefsDict
        self.enableLiveUpdating = settings.enableMagLiveUpdating

        # Initialize variables to None to keep pylint happy.
        #
        self.bbindings = None
        self.cellRendererText = None
        self.defaultVoice = None
        self.defKeyBindings = None
        self.disableKeyGrabPref = None
        self.enableAutostart = None
        self.getTextAttributesView = None
        self.hyperlinkVoice = None
        self.initializingSpeech = None
        self.kbindings = None
        self.keyBindingsModel = None
        self.keyBindView = None
        self.newBinding = None
        self.orcaModKeyEntry = None
        self.pendingKeyBindings = None
        self.planeCellRendererText = None
        self.pronunciationModel = None
        self.pronunciationView = None
        self.screenHeight = None
        self.screenWidth = None
        self.speechFamiliesChoice = None
        self.speechFamiliesChoices = None
        self.speechFamiliesModel = None
        self.speechServersChoice = None
        self.speechServersChoices = None
        self.speechServersModel = None
        self.speechSystemsChoice = None
        self.speechSystemsChoices = None
        self.speechSystemsModel = None
        self.uppercaseVoice = None
        self.window = None
        self.workingFactories = None
        self.savedGain = None
        self.savedPitch = None
        self.savedRate = None

    def init(self):
        """Initialize the Orca configuration GUI. Read the users current
        set of preferences and set the GUI state to match. Setup speech
        support and populate the combo box lists on the Speech Tab pane
        accordingly.
        """

        # Restore the default rate/pitch/gain,
        # in case the user played with the sliders.
        #        
        try:
            defaultVoice = settings.voices[settings.DEFAULT_VOICE]
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
        self.keyBindingsModel = gtk.TreeStore(
            gobject.TYPE_STRING,  # Handler name
            gobject.TYPE_STRING,  # Human Readable Description
            gobject.TYPE_STRING,  # Modifier mask 1
            gobject.TYPE_STRING,  # Used Modifiers 1
            gobject.TYPE_STRING,  # Modifier key name 1
            gobject.TYPE_STRING,  # Click count 1
            gobject.TYPE_STRING,  # Original Text of the Key Binding Shown 1
            gobject.TYPE_STRING,  # Text of the Key Binding Shown 1
            gobject.TYPE_STRING,  # Modifier mask 2
            gobject.TYPE_STRING,  # Used Modifiers 2
            gobject.TYPE_STRING,  # Modifier key name 2
            gobject.TYPE_STRING,  # Click count 2
            gobject.TYPE_STRING,  # Original Text of the Key Binding Shown 2
            gobject.TYPE_STRING,  # Text of the Key Binding Shown 2
            gobject.TYPE_BOOLEAN, # Key Modified by User
            gobject.TYPE_BOOLEAN) # Row with fields editable or not

        self.planeCellRendererText = gtk.CellRendererText()

        self.cellRendererText = gtk.CellRendererText()
        self.cellRendererText.set_property("ellipsize", pango.ELLIPSIZE_END)

        # HANDLER - invisble column
        #
        column = gtk.TreeViewColumn("Handler",
                                    self.planeCellRendererText,
                                    text=HANDLER)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(HANDLER)
        self.keyBindView.append_column(column)

        # DESCRIP
        #

        # Translators: Function is a table column header where the
        # cells in the column are a sentence that briefly describes
        # what action Orca will take when the user invokes an Orca-specific
        # keyboard command.
        #
        column = gtk.TreeViewColumn(_("Function"),
                                    self.cellRendererText,
                                    text=DESCRIP)
        column.set_resizable(True)
        column.set_min_width(380)
        column.set_sort_column_id(DESCRIP)
        self.keyBindView.append_column(column)

        # MOD_MASK1 - invisble column
        #
        column = gtk.TreeViewColumn("Mod.Mask 1",
                                    self.planeCellRendererText,
                                    text=MOD_MASK1)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MOD_MASK1)
        self.keyBindView.append_column(column)

        # MOD_USED1 - invisble column
        #
        column = gtk.TreeViewColumn("Use Mod.1",
                                    self.planeCellRendererText,
                                    text=MOD_USED1)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MOD_USED1)
        self.keyBindView.append_column(column)

        # KEY1 - invisble column
        #
        column = gtk.TreeViewColumn("Key1",
                                    self.planeCellRendererText,
                                    text=KEY1)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(KEY1)
        self.keyBindView.append_column(column)

        # CLICK_COUNT1 - invisble column
        #
        column = gtk.TreeViewColumn("ClickCount1",
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
        column = gtk.TreeViewColumn("OldText1",
                                    self.planeCellRendererText,
                                    text=OLDTEXT1)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(OLDTEXT1)
        self.keyBindView.append_column(column)

        # TEXT1
        #
        rendererText = gtk.CellRendererText()
        rendererText.connect("editing-started",
                             self.editingKey,
                             self.keyBindingsModel)
        rendererText.connect("editing-canceled",
                             self.editingCanceledKey)
        rendererText.connect('edited',
                             self.editedKey,
                             self.keyBindingsModel,
                             MOD_MASK1, MOD_USED1, KEY1, CLICK_COUNT1, TEXT1)

        # Translators: Key Binding is a table column header where
        # the cells in the column represent keyboard combinations
        # the user can press to invoke Orca commands.
        #
        column = gtk.TreeViewColumn(_("Key Binding"),
                                    rendererText,
                                    text=TEXT1,
                                    editable=EDITABLE)
        column.set_resizable(True)
        column.set_sort_column_id(OLDTEXT1)
        self.keyBindView.append_column(column)

        # MOD_MASK2 - invisble column
        #
        column = gtk.TreeViewColumn("Mod.Mask 2",
                                    self.planeCellRendererText,
                                    text=MOD_MASK2)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MOD_MASK2)
        self.keyBindView.append_column(column)

        # MOD_USED2 - invisble column
        #
        column = gtk.TreeViewColumn("Use Mod.2",
                                    self.planeCellRendererText,
                                    text=MOD_USED2)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MOD_USED2)
        self.keyBindView.append_column(column)

        # KEY2 - invisble column
        #
        column = gtk.TreeViewColumn("Key2", rendererText, text=KEY2)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(KEY2)
        self.keyBindView.append_column(column)

        # CLICK_COUNT2 - invisble column
        #
        column = gtk.TreeViewColumn("ClickCount2",
                                    self.planeCellRendererText,
                                    text=CLICK_COUNT2)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(CLICK_COUNT2)
        self.keyBindView.append_column(column)

        # OLDTEXT2 - invisble column which will store a copy of the
        # original keybinding in TEXT1 prior to the Apply or OK
        # buttons being pressed.  This will prevent automatic
        # resorting each time a cell is edited.
        #
        column = gtk.TreeViewColumn("OldText2",
                                    self.planeCellRendererText,
                                    text=OLDTEXT2)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(OLDTEXT2)
        self.keyBindView.append_column(column)

        # TEXT2
        #
        rendererText = gtk.CellRendererText()
        rendererText.connect("editing-started",
                             self.editingKey,
                             self.keyBindingsModel)
        rendererText.connect("editing-canceled",
                             self.editingCanceledKey)
        rendererText.connect('edited',
                             self.editedKey,
                             self.keyBindingsModel,
                             MOD_MASK2, MOD_USED2, KEY2, CLICK_COUNT2, TEXT2)

        # Translators: Alternate is a table column header where
        # the cells in the column represent keyboard combinations
        # the user can press to invoke Orca commands.  These
        # represent alternative key bindings that are used in
        # addition to the key bindings in the "Key Bindings"
        # column.
        #
        column = gtk.TreeViewColumn(_("Alternate"),
                                    rendererText,
                                    text=TEXT2,
                                    editable=EDITABLE)
        column.set_resizable(True)
        column.set_sort_column_id(OLDTEXT2)
        self.keyBindView.append_column(column)

        # MODIF
        #
        rendererToggle = gtk.CellRendererToggle()
        rendererToggle.connect('toggled',
                               self.keyModifiedToggle,
                               self.keyBindingsModel,
                               MODIF)

        # Translators: Modified is a table column header where the
        # cells represent whether a key binding has been modified
        # from the default key binding.
        #
        column = gtk.TreeViewColumn(_("Modified"),
                                    rendererToggle,
                                    active=MODIF,
                                    activatable=EDITABLE)
        #column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MODIF)
        self.keyBindView.append_column(column)

        # EDITABLE - invisble column
        #
        rendererToggle = gtk.CellRendererToggle()
        rendererToggle.set_property('activatable', False)
        column = gtk.TreeViewColumn("Modified",
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
        self.window.resize(790, 580)

        self._setKeyEchoItems()

        self.speechSystemsModel  = \
                        self._initComboBox(self.get_widget("speechSystems"))
        self.speechServersModel  = \
                        self._initComboBox(self.get_widget("speechServers"))
        self.speechFamiliesModel = \
                        self._initComboBox(self.get_widget("speechFamilies"))
        self._initSpeechState()

        self._initGUIState()

    def _getACSSForVoiceType(self, voiceType):
        """Return the ACSS value for the the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK

        Returns the voice dictionary for the given voice type.
        """

        if voiceType == DEFAULT:
            voiceACSS = self.defaultVoice
        elif voiceType == UPPERCASE:
            voiceACSS = self.uppercaseVoice
        elif voiceType == HYPERLINK:
            voiceACSS = self.hyperlinkVoice
        else:
            voiceACSS = self.defaultVoice

        return voiceACSS

    def writeUserPreferences(self):
        """Write out the user's generic Orca preferences.
        """

        if orca_prefs.writePreferences(self.prefsDict, self.keyBindingsModel,
                                       self.pronunciationModel):
            self._say( \
                _("Accessibility support for GNOME has just been enabled."))
            self._say( \
                _("You need to log out and log back in for the change to " \
                  "take effect."))

    def _getKeyValueForVoiceType(self, voiceType, key, useDefault=True):
        """Look for the value of the given key in the voice dictionary
           for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK
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
        else:
            voice = self.defaultVoice

        if key in voice:
            return voice[key]
        else:
            return None

    def _getFamilyNameForVoiceType(self, voiceType):
        """Gets the name of the voice family for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK

        Returns the name of the voice family for the given voice type,
        or None if not set.
        """

        familyName = None
        family = self._getKeyValueForVoiceType(voiceType, acss.ACSS.FAMILY)

        if family and speechserver.VoiceFamily.NAME in family:
            familyName = family[speechserver.VoiceFamily.NAME]

        return familyName

    def _setFamilyNameForVoiceType(self, voiceType, name, language):
        """Sets the name of the voice family for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK
        - name: the name of the voice family to set.
        - language: the locale of the voice family to set.
        """

        family = self._getKeyValueForVoiceType(voiceType,
                                               acss.ACSS.FAMILY,
                                               False)
        if family:
            family[speechserver.VoiceFamily.NAME] = name
            family[speechserver.VoiceFamily.LOCALE] = language
        else:
            voiceACSS = self._getACSSForVoiceType(voiceType)
            voiceACSS[acss.ACSS.FAMILY] = {}
            voiceACSS[acss.ACSS.FAMILY][speechserver.VoiceFamily.NAME] = name
            voiceACSS[acss.ACSS.FAMILY][speechserver.VoiceFamily.LOCALE] = \
                                                                     language

        #voiceACSS = self._getACSSForVoiceType(voiceType)
        #settings.voices[voiceType] = voiceACSS

    def _getRateForVoiceType(self, voiceType):
        """Gets the speaking rate value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK

        Returns the rate value for the given voice type, or None if
        not set.
        """

        return self._getKeyValueForVoiceType(voiceType, acss.ACSS.RATE)

    def _setRateForVoiceType(self, voiceType, value):
        """Sets the speaking rate value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK
        - value: the rate value to set.
        """

        voiceACSS = self._getACSSForVoiceType(voiceType)
        voiceACSS[acss.ACSS.RATE] = value
        #settings.voices[voiceType] = voiceACSS

    def _getPitchForVoiceType(self, voiceType):
        """Gets the pitch value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK

        Returns the pitch value for the given voice type, or None if
        not set.
        """

        return self._getKeyValueForVoiceType(voiceType,
                                             acss.ACSS.AVERAGE_PITCH)

    def _setPitchForVoiceType(self, voiceType, value):
        """Sets the pitch value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK
        - value: the pitch value to set.
        """

        voiceACSS = self._getACSSForVoiceType(voiceType)
        voiceACSS[acss.ACSS.AVERAGE_PITCH] = value
        #settings.voices[voiceType] = voiceACSS

    def _getVolumeForVoiceType(self, voiceType):
        """Gets the volume (gain) value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK

        Returns the volume (gain) value for the given voice type, or
        None if not set.
        """

        return self._getKeyValueForVoiceType(voiceType, acss.ACSS.GAIN)

    def _setVolumeForVoiceType(self, voiceType, value):
        """Sets the volume (gain) value for the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK
        - value: the volume (gain) value to set.
        """

        voiceACSS = self._getACSSForVoiceType(voiceType)
        voiceACSS[acss.ACSS.GAIN] = value
        #settings.voices[voiceType] = voiceACSS

    def _setVoiceSettingsForVoiceType(self, voiceType):
        """Sets the family, rate, pitch and volume GUI components based
        on the given voice type.

        Arguments:
        - voiceType: one of DEFAULT, UPPERCASE, HYPERLINK
        """

        familyName = self._getFamilyNameForVoiceType(voiceType)
        self._setSpeechFamiliesChoice(familyName)

        rate = self._getRateForVoiceType(voiceType)
        if rate != None:
            self.get_widget("rateScale").set_value(rate)
        else:
            self.get_widget("rateScale").set_value(50.0)
            
        pitch = self._getPitchForVoiceType(voiceType)
        if pitch != None:
            self.get_widget("pitchScale").set_value(pitch)
        else:
            self.get_widget("pitchScale").set_value(5.0)

        volume = self._getVolumeForVoiceType(voiceType)
        if volume != None:
            self.get_widget("volumeScale").set_value(volume)
        else:
            self.get_widget("volumeScale").set_value(10.0)

    def _setSpeechFamiliesChoice(self, familyName):
        """Sets the active item in the families ("Person:") combo box
        to the given family name.

        Arguments:
        - families: the list of available voice families.
        - familyName: the family name to use to set the active combo box item.
        """

        if len(self.speechFamiliesChoices) == 0:
            return

        valueSet = False
        i = 0
        for family in self.speechFamiliesChoices:
            name = family[speechserver.VoiceFamily.NAME]
            if name == familyName:
                self.get_widget("speechFamilies").set_active(i)
                self.speechFamiliesChoice = self.speechFamiliesChoices[i]
                valueSet = True
                break
            i += 1

        if not valueSet:
            debug.println(debug.LEVEL_FINEST,
                          "Could not find speech family match for %s" \
                          % familyName)
            self.get_widget("speechFamilies").set_active(0)
            self.speechFamiliesChoice = self.speechFamiliesChoices[0]

    def _setupFamilies(self):
        """Gets the list of voice families for the current speech server.
        If there are families, get the information associated with
        each voice family and add an entry for it to the families
        GtkComboBox list.
        """

        self.speechFamiliesModel.clear()
        families = self.speechServersChoice.getVoiceFamilies()
        self.speechFamiliesChoices = []
        if len(families) == 0:
            debug.println(debug.LEVEL_SEVERE, "Speech not available.")
            debug.printStack(debug.LEVEL_FINEST)
            self.speechFamiliesChoice = None
            return

        i = 0
        for family in families:
            name = family[speechserver.VoiceFamily.NAME] \
                   + " (%s)" % family[speechserver.VoiceFamily.LOCALE]
            self.speechFamiliesChoices.append(family)
            self.speechFamiliesModel.append((i, name))
            i += 1

        # The family name will be selected as part of selecting the
        # voice type.  Whenever the families change, we'll reset the
        # voice type selection to the first one ("Default").
        #
        comboBox = self.get_widget("voiceTypes")
        types = []
        # Translators: This refers to the default/typical voice used
        # by Orca when presenting the content of the screen and other
        # messages.
        #
        types.append(C_("VoiceType", "Default"))
        # Translators: This refers to the voice used by Orca when
        # presenting one or more characters which is in uppercase.
        #
        types.append(C_("VoiceType", "Uppercase"))
        # Translators: This refers to the voice used by Orca when
        # presenting one or more characters which is part of a
        # hyperlink.
        #
        types.append(C_("VoiceType", "Hyperlink"))
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
        if not serverInfo:
            serverInfo = speech.getInfo()

        valueSet = False
        i = 0
        for server in self.speechServersChoices:
            if serverInfo == server.getInfo():
                self.get_widget("speechServers").set_active(i)
                self.speechServersChoice = server
                valueSet = True
                break
            i += 1

        if not valueSet:
            debug.println(debug.LEVEL_FINEST,
                          "Could not find speech server match for %s" \
                          %  repr(serverInfo))
            self.get_widget("speechServers").set_active(0)
            self.speechServersChoice = self.speechServersChoices[0]

        self._setupFamilies()

    def _setupSpeechServers(self):
        """Gets the list of speech servers for the current speech factory.
        If there are servers, get the information associated with each
        speech server and add an entry for it to the speechServers
        GtkComboBox list.  Set the current choice to be the first item.
        """

        self.speechServersModel.clear()
        self.speechServersChoices = \
                self.speechSystemsChoice.SpeechServer.getSpeechServers()
        if len(self.speechServersChoices) == 0:
            debug.println(debug.LEVEL_SEVERE, "Speech not available.")
            debug.printStack(debug.LEVEL_FINEST)
            self.speechServersChoice = None
            self.speechFamiliesChoices = []
            self.speechFamiliesChoice = None
            return

        i = 0
        for server in self.speechServersChoices:
            name = server.getInfo()[0]
            self.speechServersModel.append((i, name))
            i += 1

        self._setSpeechServersChoice(self.prefsDict["speechServerInfo"])

        debug.println(
            debug.LEVEL_FINEST,
            "orca_gui_prefs._setupSpeechServers: speechServersChoice: %s" \
            % self.speechServersChoice.getInfo())

    def _setSpeechSystemsChoice(self, systemName):
        """Set the active item in the speech systems combo box to the
        given system name.

        Arguments:
        - factoryChoices: the list of available speech factories (systems).
        - systemName: the speech system name to use to set the active combo
        box item.
        """

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
            debug.println(debug.LEVEL_FINEST,
                          "Could not find speech system match for %s" \
                          % systemName)
            self.get_widget("speechSystems").set_active(0)
            self.speechSystemsChoice = self.speechSystemsChoices[0]

        self._setupSpeechServers()

    def _setupSpeechSystems(self, factories):
        """Sets up the speech systems combo box and sets the selection
        to the preferred speech system.

        Arguments:
        -factories: the list of known speech factories (working or not)
        """
        self.speechSystemsModel.clear()
        self.workingFactories = []
        for factory in factories:
            try:
                servers = factory.SpeechServer.getSpeechServers()
                if len(servers):
                    self.workingFactories.append(factory)
            except:
                debug.printException(debug.LEVEL_FINEST)

        self.speechSystemsChoices = []
        if len(self.workingFactories) == 0:
            debug.println(debug.LEVEL_SEVERE, "Speech not available.")
            debug.printStack(debug.LEVEL_FINEST)
            self.speechSystemsChoice = None
            self.speechServersChoices = []
            self.speechServersChoice = None
            self.speechFamiliesChoices = []
            self.speechFamiliesChoice = None
            return

        i = 0
        for workingFactory in self.workingFactories:
            self.speechSystemsChoices.append(workingFactory)
            name = workingFactory.SpeechServer.getFactoryName()
            self.speechSystemsModel.append((i, name))
            i += 1

        if self.prefsDict["speechServerFactory"]:
            self._setSpeechSystemsChoice(self.prefsDict["speechServerFactory"])
        else:
            self.speechSystemsChoice = None

        debug.println(
            debug.LEVEL_FINEST,
            "orca_gui_prefs._setupSpeechSystems: speechSystemsChoice: %s" \
            % self.speechSystemsChoice)

    def _initSpeechState(self):
        """Initialize the various speech components.
        """

        voices = self.prefsDict["voices"]
        self.defaultVoice   = acss.ACSS(voices[settings.DEFAULT_VOICE])
        self.uppercaseVoice = acss.ACSS(voices[settings.UPPERCASE_VOICE])
        self.hyperlinkVoice = acss.ACSS(voices[settings.HYPERLINK_VOICE])

        # Just a note on general naming pattern:
        #
        # *        = The name of the combobox
        # *Model   = the name of the comobox model
        # *Choices = the Orca/speech python objects
        # *Choice  = a value from *Choices
        #
        # Where * = speechSystems, speechServers, speechFamilies
        #
        factories = speech.getSpeechServerFactories()
        if len(factories) == 0:
            self.workingFactories = []
            self.speechSystemsChoice = None
            self.speechServersChoices = []
            self.speechServersChoice = None
            self.speechFamiliesChoices = []
            self.speechFamiliesChoice = None
            return

        speech.init()

        # This cascades into systems->servers->voice_type->families...
        #
        self.initializingSpeech = True
        self._setupSpeechSystems(factories)
        self.initializingSpeech = False

    def _setSpokenTextAttributes(self, view, setAttributes,
                                 state, moveToTop=False):
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
        defScript = default.Script(None)

        [attrList, attrDict] = \
           defScript.textAttrsToDictionary(setAttributes)
        [allAttrList, allAttrDict] = \
           defScript.textAttrsToDictionary(settings.allTextAttributes)

        for i in range(0, len(attrList)):
            for path in range(0, len(allAttrList)):
                localizedKey = \
                        text_attribute_names.getTextAttributeName(attrList[i])
                localizedValue = \
                        text_attribute_names.getTextAttributeName( \
                                                        attrDict[attrList[i]])
                if localizedKey == model[path][NAME]:
                    thisIter = model.get_iter(path)
                    model.set(thisIter, 
                        NAME, localizedKey,
                        IS_SPOKEN, state,
                        VALUE, localizedValue)
                    if moveToTop:
                        thisIter = model.get_iter(path)
                        otherIter = model.get_iter(i)
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

        defScript = default.Script(None)
        [attrList, attrDict] = \
            defScript.textAttrsToDictionary(setAttributes)
        [allAttrList, allAttrDict] = \
            defScript.textAttrsToDictionary(settings.allTextAttributes)

        for i in range(0, len(attrList)):
            for path in range(0, len(allAttrList)):
                localizedKey = \
                        text_attribute_names.getTextAttributeName(attrList[i])
                if localizedKey == model[path][NAME]:
                    thisIter = model.get_iter(path)
                    model.set(thisIter, IS_BRAILLED, state)
                    break

        view.set_model(model)

    def _getAppNameForAttribute(self, attributeName):
        """Converts the given Atk attribute name into the application's
        equivalent. This is necessary because an application or toolkit
        (e.g. Gecko) might invent entirely new names for the same text
        attributes.

        Arguments:
        - attribName: The name of the text attribute

        Returns the application's equivalent name if found or attribName
        otherwise.
        """

        return attributeName

    def _updateTextDictEntry(self):
        """The user has updated the text attribute list in some way. Update
        the "enabledSpokenTextAttributes" and "enabledBrailledTextAttributes"
        preference strings to reflect the current state of the corresponding
        text attribute lists.
        """

        model = self.getTextAttributesView.get_model()
        spokenAttrStr = ""
        brailledAttrStr = ""
        noRows = model.iter_n_children(None)
        for path in range(0, noRows):
            localizedKey = model[path][NAME]
            key = text_attribute_names.getTextAttributeKey(localizedKey)

            # Convert the normalized, Atk attribute name back into what
            # the app/toolkit uses.
            #
            key = self._getAppNameForAttribute(key)

            localizedValue = model[path][VALUE]
            value = text_attribute_names.getTextAttributeKey(localizedValue)

            if model[path][IS_SPOKEN]:
                spokenAttrStr += key + ":" + value + "; "
            if model[path][IS_BRAILLED]:
                brailledAttrStr += key + ":" + value + "; "

        self.prefsDict["enabledSpokenTextAttributes"] = spokenAttrStr
        self.prefsDict["enabledBrailledTextAttributes"] = brailledAttrStr

    def contractedBrailleToggled(self, checkbox):
        hbox = self.get_widget('contractionTablesHBox')
        hbox.set_sensitive(checkbox.get_active())
        self.prefsDict["enableContractedBraille"] = checkbox.get_active()

    def contractionTableComboChanged(self, combobox):
        model = combobox.get_model()
        myIter = combobox.get_active_iter()
        self.prefsDict["brailleContractionTable"] = model[myIter][1]
        
    def textAttributeSpokenToggled(self, cell, path, model):
        """The user has toggled the state of one of the text attribute
        checkboxes to be spoken. Update our model to reflect this, then
        update the "enabledSpokenTextAttributes" preference string.

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
        then update the "enabledBrailledTextAttributes" preference string.

        Arguments:
        - cell: the cell that changed.
        - path: the path of that cell.
        - model: the model that the cell is part of.
        """

        thisIter = model.get_iter(path)
        model.set(thisIter, IS_BRAILLED, not model[path][IS_BRAILLED])
        self._updateTextDictEntry()

    def textAttrValueEdited(self, cell, path, new_text, model):
        """The user has edited the value of one of the text attributes.
        Update our model to reflect this, then update the
        "enabledSpokenTextAttributes" and "enabledBrailledTextAttributes"
        preference strings.

        Arguments:
        - cell: the cell that changed.
        - path: the path of that cell.
        - new_text: the new text attribute value string.
        - model: the model that the cell is part of.
        """

        thisIter = model.get_iter(path)
        model.set(thisIter, VALUE, new_text)
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
        model = gtk.ListStore(gobject.TYPE_STRING,
                              gobject.TYPE_BOOLEAN,
                              gobject.TYPE_BOOLEAN,
                              gobject.TYPE_STRING)

        # Initially setup the list store model based on the values of all
        # the known text attributes.
        #
        defScript = default.Script(None)
        [allAttrList, allAttrDict] = \
                defScript.textAttrsToDictionary(settings.allTextAttributes)
        for i in range(0, len(allAttrList)):
            thisIter = model.append()
            localizedKey = \
                text_attribute_names.getTextAttributeName(allAttrList[i])
            localizedValue = \
                text_attribute_names.getTextAttributeName( \
                                             allAttrDict[allAttrList[i]])
            model.set(thisIter, 
                NAME, localizedKey,
                IS_SPOKEN, False,
                IS_BRAILLED, False,
                VALUE, localizedValue)

        self.getTextAttributesView.set_model(model)

        # Attribute Name column (NAME).
        #
        # Translators: Attribute here refers to text attributes such
        # as bold, underline, family-name, etc.
        #
        column = gtk.TreeViewColumn(_("Attribute Name"))
        column.set_min_width(250)
        column.set_resizable(True)
        renderer = gtk.CellRendererText()
        column.pack_end(renderer, True)
        column.set_attributes(renderer, text=NAME)
        self.getTextAttributesView.insert_column(column, 0)

        # Attribute Speak column (IS_SPOKEN).
        #
        # Translators: the "Speak" column consists of a single checkbox
        # for each text attribute.  If the checkbox is checked, Orca
        # will speak that attribute, if it is present, when the user
        # presses Orca_Modifier+F.
        #
        speakAttrColumnLabel = _("Speak")
        column = gtk.TreeViewColumn(speakAttrColumnLabel)
        renderer = gtk.CellRendererToggle()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, active=IS_SPOKEN)
        renderer.connect("toggled",
                         self.textAttributeSpokenToggled,
                         model)
        self.getTextAttributesView.insert_column(column, 1)
        column.clicked()

        # Attribute Mark in Braille column (IS_BRAILLED).
        #
        # Translators: The "Mark in braille" column consists of a single
        # checkbox for each text attribute.  If the checkbox is checked,
        # Orca will "underline" that attribute, if it is present, on
        # the refreshable braille display.
        #
        markAttrColumnLabel = _("Mark in braille")
        column = gtk.TreeViewColumn(markAttrColumnLabel)
        renderer = gtk.CellRendererToggle()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, active=IS_BRAILLED)
        renderer.connect("toggled",
                         self.textAttributeBrailledToggled,
                         model)
        self.getTextAttributesView.insert_column(column, 2)
        column.clicked()

        # Attribute Value column (VALUE)
        #
        # Translators: "Present Unless" is a column header of the text
        # attributes pane of the Orca preferences dialog.  On this pane,
        # the user can select a set of text attributes that they would like
        # spoken and/or indicated in braille.  Because the list of attributes
        # could get quite lengthy, we provide the option to always speak/
        # braille a text attribute *unless* its value is equal to the value
        # given by the user in this column of the list.  For example, given
        # the text attribute "underline" and a present unless value of "none",
        # the user is stating that he/she would like to have underlined text
        # announced for all cases (single, double, low, etc.) except when the
        # value of underline is none (i.e. when it's not underlined).
        # "Present" here is being used as a verb.
        #
        column = gtk.TreeViewColumn(_("Present Unless"))
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        column.pack_end(renderer, True)
        column.set_attributes(renderer, text=VALUE)
        renderer.connect("edited", self.textAttrValueEdited, model)

        self.getTextAttributesView.insert_column(column, 4)

        # Check all the enabled (spoken) text attributes.
        #
        self._setSpokenTextAttributes(self.getTextAttributesView,
                            settings.enabledSpokenTextAttributes, True, True)

        # Check all the enabled (brailled) text attributes.
        #
        self._setBrailledTextAttributes(self.getTextAttributesView,
                                settings.enabledBrailledTextAttributes, True)

        # Connect a handler for when the user changes columns within the
        # view, so that we can adjust the search column for item lookups.
        #
        self.getTextAttributesView.connect("cursor_changed",
                                           self.textAttrCursorChanged)

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

    def _createPronunciationTreeView(self, pronunciations=None):
        """Create the pronunciation dictionary tree view. The view is the
        pronunciationTreeView GtkTreeView widget. The view will consist
        of a list containing two columns:
          ACTUAL      - the actual text string (word).
          REPLACEMENT - the string that is used to pronounce that word.

        Arguments:
        - pronunciations: an optional dictionary used to get the 
          pronunciation from.
        """

        self.pronunciationView = self.get_widget("pronunciationTreeView")
        model = gtk.ListStore(gobject.TYPE_STRING,
                              gobject.TYPE_STRING)

        # Initially setup the list store model based on the values of all
        # existing entries in the pronunciation dictionary.
        #
        if pronunciations != None:
            pronDict = pronunciations
        else:
            pronDict = pronunciation_dict.pronunciation_dict
        for pronKey in sorted(pronDict.keys()):
            thisIter = model.append() 
            try:
                actual, replacement = pronDict[pronKey]
            except:
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
        # 
        # Translators: "Actual String" here refers to a text string as it
        # actually appears in a text document. This might be an abbreviation
        # or a particular word that is pronounced differently then the way
        # that it looks.
        #
        column = gtk.TreeViewColumn(_("Actual String"))
        column.set_min_width(250)
        column.set_resizable(True)
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        column.pack_end(renderer, True) 
        column.set_attributes(renderer, text=ACTUAL)
        renderer.connect("edited", self.pronActualValueEdited, model)
        self.pronunciationView.insert_column(column, 0)

        # Pronunciation Dictionary replacement string column (REPLACEMENT)
        #
        # Translators: "Replacement String" here refers to the text string
        # that will actually be used to speak it's matching "actual string".
        # For example: if the actual string was "MHz", then the replacement
        # (spoken) string would be "megahertz".
        #
        column = gtk.TreeViewColumn(_("Replacement String"))
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        column.pack_end(renderer, True)
        column.set_attributes(renderer, text=REPLACEMENT)
        renderer.connect("edited", self.pronReplacementValueEdited, model)
        self.pronunciationView.insert_column(column, 1)

        self.pronunciationModel = model

        # Connect a handler for when the user changes columns within the
        # view, so that we can adjust the search column for item lookups.
        #
        self.pronunciationView.connect("cursor_changed",
                                       self.pronunciationCursorChanged)

    def _setZoomerSpinButtons(self):
        """Populate/update the values and ranges of the four zoomer
        spin buttons on the Magnifier pane.
        """

        # Get the width and the height of the target screen. If there is
        # no target screen set, use the default.
        #
        display = gtk.gdk.display_get_default()
        nScreens = display.get_n_screens()
        targetScreen = display.get_default_screen()
        targetDisplay = orca_state.advancedMag.get_widget(\
                             "magTargetDisplayEntry").get_active_text()
        if targetDisplay:
            t = targetDisplay.split(".")
            try:
                targetNumber = int(t[-1])
                if targetNumber in range(0, nScreens):
                    targetScreen = display.get_screen(targetNumber)
            except:
                pass

        targetWidth = targetScreen.get_width()
        targetHeight = targetScreen.get_height()

        prefs = self.prefsDict
        
        # Get the zoomer placement top preference and set the top spin
        # button value accordingly. Set the top spin button "max size" to
        # the height of the target screen.  If there is no target screen
        # set, use the default.
        #
        topPosition = prefs["magZoomerTop"]
        adjustment = gtk.Adjustment(
            min(topPosition, targetHeight), 
            0, targetHeight, 
            1,
            targetHeight / 16, 0)

        if orca_state.appOS:
            spinButton = orca_state.appOS.get_widget("magZoomerTopSpinButton")
        else:
            spinButton = orca_state.orcaOS.get_widget("magZoomerTopSpinButton")

        spinButton.set_adjustment(adjustment)
        if topPosition > targetHeight:
            spinButton.update()

        # Get the zoomer placement left preference and set the left spin
        # button value accordingly. Set the left spin button "max size" to
        # the width of the target screen. If there is no target screen set,
        # use the default.
        #
        leftPosition = prefs["magZoomerLeft"]
        adjustment = gtk.Adjustment(
            min(leftPosition, targetWidth),
            0, targetWidth, 
            1,
            targetWidth / 16, 0)

        if orca_state.appOS:
            spinButton = orca_state.appOS.get_widget("magZoomerLeftSpinButton")
        else:
            spinButton = orca_state.orcaOS.get_widget("magZoomerLeftSpinButton")

        spinButton.set_adjustment(adjustment)
        if leftPosition > targetWidth:
            spinButton.update()

        # Get the zoomer placement right preference and set the right spin
        # button value accordingly. Set the right spin button "max size" to
        # the width of the target screen. If there is no target screen set,
        # use the default.
        #
        rightPosition = prefs["magZoomerRight"]
        adjustment = gtk.Adjustment(
            min(rightPosition, targetWidth),
            0, targetWidth, 
            1,
            targetWidth / 16, 0)

        if orca_state.appOS:
            spinButton = \
                orca_state.appOS.get_widget("magZoomerRightSpinButton")
        else:
            spinButton = \
                orca_state.orcaOS.get_widget("magZoomerRightSpinButton")

        spinButton.set_adjustment(adjustment)
        if rightPosition > targetWidth:
            spinButton.update()

        # Get the zoomer placement bottom preference and set the bottom
        # spin button value accordingly. Set the bottom spin button "max size"
        # to the height of the target screen.  If there is no target screen
        # set, use the default.
        #
        bottomPosition = prefs["magZoomerBottom"]
        adjustment = gtk.Adjustment(
            min(bottomPosition, targetHeight),
            0, targetHeight, 
            1,
            targetHeight / 16, 0)

        if orca_state.appOS:
            spinButton = \
                orca_state.appOS.get_widget("magZoomerBottomSpinButton")
        else:
            spinButton = \
                orca_state.orcaOS.get_widget("magZoomerBottomSpinButton")
        spinButton.set_adjustment(adjustment)
        if bottomPosition > targetHeight:
            spinButton.update()

    def _initGUIState(self):
        """Adjust the settings of the various components on the
        configuration GUI depending upon the users preferences.
        """

        prefs = self.prefsDict

        # Speech pane.
        #
        enable = prefs["enableSpeech"]
        self.get_widget("speechSupportCheckbutton").set_active(enable)
        self.get_widget("speechVbox").set_sensitive(enable)

        if prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_NONE:
            self.get_widget("noneButton").set_active(True)
        elif prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_SOME:
            self.get_widget("someButton").set_active(True)
        elif prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_MOST:
            self.get_widget("mostButton").set_active(True)
        else:
            self.get_widget("allButton").set_active(True)

        if prefs["speechVerbosityLevel"] == settings.VERBOSITY_LEVEL_BRIEF:
            self.get_widget("speechBriefButton").set_active(True)
        else:
            self.get_widget("speechVerboseButton").set_active(True)

        if prefs["readTableCellRow"]:
            self.get_widget("rowSpeechButton").set_active(True)
        else:
            self.get_widget("cellSpeechButton").set_active(True)

        self.get_widget("speechIndentationCheckbutton").set_active(\
            prefs["enableSpeechIndentation"])

        self.get_widget("speakBlankLinesCheckButton").set_active(\
            prefs["speakBlankLines"])
        self.get_widget("speakMultiCaseAsWordsCheckButton").set_active(\
            prefs["speakMultiCaseStringsAsWords"])
        self.get_widget("speakTutorialMessagesCheckButton").set_active(\
            prefs["enableTutorialMessages"])

        self.get_widget("pauseBreaksCheckButton").set_active(\
            prefs["enablePauseBreaks"])

        # Translators: different speech systems and speech engines work
        # differently when it comes to handling pauses (e.g., sentence
        # boundaries). This property allows the user to specify whether
        # speech should be sent to the speech synthesis system immediately
        # when a pause directive is enountered or if it should be queued
        # up and sent to the speech synthesis system once the entire set
        # of utterances has been calculated.
        #
        label = _("Break speech into ch_unks between pauses")
        # TODO - JD: I did the above because GtkBuilder translator notes
        # (which we have for the above string) are not getting sucked in
        # to orca.pot. :-(

        self.get_widget("speakPositionCheckButton").set_active(\
            prefs["enablePositionSpeaking"])

        self.get_widget("speakMnemonicsCheckButton").set_active(\
            prefs["enableMnemonicSpeaking"])

        combobox = self.get_widget("sayAllStyle")
        self.populateComboBox(combobox, [_("Line"), _("Sentence")])
        combobox.set_active(prefs["sayAllStyle"])

        # Set the sensitivity of the "Update Interval" items, depending
        # upon whether the "Speak progress bar updates" checkbox is checked.
        #
        enable = prefs["enableProgressBarUpdates"]
        self.get_widget("speechProgressBarCheckbutton").set_active(enable)
        self.get_widget("speakUpdateIntervalHBox").set_sensitive(enable)

        interval = prefs["progressBarUpdateInterval"]
        self.get_widget("speakProgressBarSpinButton").set_value(interval)

        # Translators: Orca has a setting which determines which progress
        # bar updates should be announced. The options are all progress
        # bars, only progress bars in the active application, or only
        # progress bars in the current window.
        #
        label = _("Restrict progress bar updates to:")
        # TODO - JD: I did the above because GtkBuilder translator notes
        # (which we have for the above string) are not getting sucked in
        # to orca.pot. :-(
        #
        comboBox = self.get_widget("progressBarVerbosity")
        levels = []
        # Translators: Orca has a setting which determines which progress
        # bar updates should be announced. Choosing "All" means that Orca
        # will present progress bar updates regardless of what application
        # and window they happen to be in.
        #
        levels.append(C_("ProgressBar", "All"))
        # Translators: Orca has a setting which determines which progress
        # bar updates should be announced. Choosing "Application" means
        # that Orca will present progress bar updates as long as the
        # progress bar is in the active application (but not necessarily
        # in the current window).
        #
        levels.append(C_("ProgressBar", "Application"))
        # Translators: Orca has a setting which determines which progress
        # bar updates should be announced. Choosing "Window" means that
        # Orca will present progress bar updates as long as the progress
        # bar is in the active window.
        #
        levels.append(C_("ProgressBar", "Window"))
        self.populateComboBox(comboBox, levels)
        comboBox.set_active(prefs["progressBarVerbosity"])

        enable = prefs["enableMouseReview"]
        self.get_widget("speakUnderMouseCheckButton").set_active(enable)

        # Braille pane.
        #
        self.get_widget("brailleSupportCheckbutton").set_active( \
                        prefs["enableBraille"])
        self.get_widget("brailleMonitorCheckbutton").set_active( \
                        prefs["enableBrailleMonitor"])
        state = prefs["brailleRolenameStyle"] == \
                            settings.BRAILLE_ROLENAME_STYLE_SHORT
        self.get_widget("abbrevRolenames").set_active(state)

        self.get_widget("disableBrailleEOL").set_active(
            prefs["disableBrailleEOL"])

        if louis is None:
            self.get_widget( \
                "contractedBrailleCheckbutton").set_sensitive(False)
        else:
            self.get_widget("contractedBrailleCheckbutton").set_active( \
                prefs["enableContractedBraille"])
            # Set up contraction table combo box and set it to the
            # currently used one.
            # 
            tablesCombo = self.get_widget("contractionTableCombo")
            tableDict = braille.listTables()
            selectedTableIter = None
            selectedTable = prefs["brailleContractionTable"] or \
                             braille.getDefaultTable()
            if tableDict:
                tablesModel = gtk.ListStore(str, str)
                names = tableDict.keys()
                names.sort()
                for name in names:
                    fname = tableDict[name]
                    it = tablesModel.append([name, fname])
                    if os.path.join(braille.tablesdir, fname) == \
                            selectedTable:
                        selectedTableIter = it
                cell = self.planeCellRendererText
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

        selectionIndicator = prefs["brailleSelectorIndicator"]
        if selectionIndicator == settings.BRAILLE_SEL_7:
            self.get_widget("brailleSelection7Button").set_active(True)
        elif selectionIndicator == settings.BRAILLE_SEL_8:
            self.get_widget("brailleSelection8Button").set_active(True)
        elif selectionIndicator == settings.BRAILLE_SEL_BOTH:
            self.get_widget("brailleSelectionBothButton").set_active(True)
        else:
            self.get_widget("brailleSelectionNoneButton").set_active(True)

        linkIndicator = prefs["brailleLinkIndicator"]
        if linkIndicator == settings.BRAILLE_LINK_7:
            self.get_widget("brailleLink7Button").set_active(True)
        elif linkIndicator == settings.BRAILLE_LINK_8:
            self.get_widget("brailleLink8Button").set_active(True)
        elif linkIndicator == settings.BRAILLE_LINK_BOTH:
            self.get_widget("brailleLinkBothButton").set_active(True)
        else:
            self.get_widget("brailleLinkNoneButton").set_active(True)

        # Key Echo pane.
        #
        self.get_widget("keyEchoCheckbutton").set_active( \
                        prefs["enableKeyEcho"])
        self.get_widget("printableCheckbutton").set_active( \
                        prefs["enablePrintableKeys"])
        self.get_widget("modifierCheckbutton").set_active( \
                        prefs["enableModifierKeys"])
        self.get_widget("lockingCheckbutton").set_active( \
                        prefs["enableLockingKeys"])
        self.get_widget("functionCheckbutton").set_active( \
                        prefs["enableFunctionKeys"])
        self.get_widget("actionCheckbutton").set_active( \
                        prefs["enableActionKeys"])
        self.get_widget("navigationCheckbutton").set_active( \
                        prefs["enableNavigationKeys"])
        self.get_widget("diacriticalCheckbutton").set_active( \
                        prefs["enableDiacriticalKeys"])
        self.get_widget("echoByCharacterCheckbutton").set_active( \
                        prefs["enableEchoByCharacter"])
        self.get_widget("echoByWordCheckbutton").set_active( \
                        prefs["enableEchoByWord"])
        self.get_widget("echoBySentenceCheckbutton").set_active( \
                        prefs["enableEchoBySentence"])

        # Translators: When this option is enabled, dead keys will be
        # announced when pressed.
        #
        label = _("Enable non-spacing _diacritical keys")
        # TODO - JD: I did the above because GtkBuilder translator notes
        # (which we have for the above string) are not getting sucked in
        # to orca.pot. :-(

        # Translators: When this option is enabled, inserted text of length
        # 1 is spoken.
        #
        label = _("Enable echo by cha_racter")
        # TODO - JD: I did the above because GtkBuilder translator notes
        # (which we have for the above string) are not getting sucked in
        # to orca.pot. :-(

        # Magnifier pane.
        #
        # Turn live updating off temporarily.
        #
        liveUpdating = self.enableLiveUpdating
        self.enableLiveUpdating = False
        
        # Set the sensitivity of the items on the magnifier pane, depending
        # upon whether the "Enable Magnifier" checkbox is checked.
        #
        enable = prefs["enableMagnifier"]
        self.get_widget("magnifierSupportCheckbutton").set_active(enable)
        self.get_widget("magnifierTable").set_sensitive(enable)

        # Get the 'Cursor on/off' preference and set the checkbox accordingly.
        # Set the sensitivity of the other cursor items depending upon this
        # value.
        #
        value = prefs["enableMagCursor"]
        self.get_widget("magCursorOnOffCheckButton").set_active(value)
        self.get_widget("magCursorTable").set_sensitive(value)

        # Get the 'Hide system cursor' preference and set the checkbox 
        # accordingly.
        #
        value = prefs["magHideCursor"]
        self.get_widget("magHideCursorCheckButton").set_active(value)

        # Get the 'Explicit cursor size' preference and set the checkbox
        # accordingly. If the value is not checked, then the cursor size
        # spin button and label need to be set insensitive.
        #
        explicitSizeChecked = prefs["enableMagCursorExplicitSize"]
        self.get_widget("magCursorSizeCheckButton").set_active( \
                        explicitSizeChecked)
        self.get_widget("magCursorSizeSpinButton").set_sensitive( \
                        explicitSizeChecked)
        self.get_widget("magCursorSizeLabel").set_sensitive( \
                        explicitSizeChecked)

        # Get the cursor size preference and set the cursor size spin
        # button value accordingly.
        #
        cursorSize = prefs["magCursorSize"]
        self.get_widget("magCursorSizeSpinButton").set_value(cursorSize)

        # Get the cursor color preference and set the cursor color button
        # accordingly.
        #
        cursorColor = prefs["magCursorColor"]
        color = gtk.gdk.color_parse(cursorColor)
        self.get_widget("magCursorColorButton").set_color(color)

        # Get the 'Cross-hair on/off' preference and set the checkbox
        # accordingly. Set the sensitivity of the other cross-hair items
        # depending upon this value.
        #
        value = prefs["enableMagCrossHair"]
        self.get_widget("magCrossHairOnOffCheckButton").set_active(value)
        self.get_widget("magCrossHairTable").set_sensitive(value)

        # Get the 'Cross-hair clip on/off' preference and set the checkbox
        # accordingly.
        #
        value = prefs["enableMagCrossHairClip"]
        self.get_widget("magCrossHairClipCheckButton").set_active(value)

        # Get the cross-hair size preference and set the cross-hair size
        # spin button value accordingly.
        #
        crosshairSize = prefs["magCrossHairSize"]
        self.get_widget("magCrossHairSizeSpinButton").set_value(crosshairSize)

        # Get the cross-hair color preference and set the cross-hair color
        # button accordingly.
        #
        crosshairColor = prefs["magCrossHairColor"]
        color = gtk.gdk.color_parse(crosshairColor)
        self.get_widget("magCrossHairColorButton").set_color(color)

        # Get the "Enable border" preference and set the checkbox
        # accordingly. Set the sensitivity of the other items in the 
        # border settings frame, depending upon whether this checkbox
        # is checked.
        #
        value = prefs["enableMagZoomerBorder"]
        self.get_widget("magBorderCheckButton").set_active(value)
        self.get_widget("magBorderTable").set_sensitive(value)

        # Get the border size preference and set the border size spin
        # button value accordingly.
        #
        borderSize = prefs["magZoomerBorderSize"]
        self.get_widget("magBorderSizeSpinButton").set_value(borderSize)

        # Get the border color preference and set the border color button
        # accordingly.
        #
        borderColor = prefs["magZoomerBorderColor"]
        color = gtk.gdk.color_parse(borderColor)
        self.get_widget("magBorderColorButton").set_color(color)

        # Get the Brightness level and set its spin button value
        # accordingly.
        #
        level = prefs["magBrightnessLevel"]
        self.get_widget("magColorBrightnessSpinButton").set_value(level)

        # Get the Contrast level and set its spin button value accordingly.
        #
        level = prefs["magContrastLevel"]
        self.get_widget("magColorContrastSpinButton").set_value(level)

        # Get the width and the height of the source screen. If there is
        # no source screen set, use the default.
        #
        display = gtk.gdk.display_get_default()
        nScreens = display.get_n_screens()
        sourceScreen = display.get_default_screen()
        sourceDisplay = orca_state.advancedMag.get_widget(\
                              "magSourceDisplayEntry").get_active_text()
        if sourceDisplay:
            s = sourceDisplay.split(".")
            try:
                sourceNumber = int(s[-1])
                if sourceNumber in range(0, nScreens):
                    sourceScreen = display.get_screen(sourceNumber)
            except:
                pass

        self.screenWidth = sourceScreen.get_width()
        self.screenHeight = sourceScreen.get_height()

        # Get the zoomer position type and set the active value for the
        # zoomer position combobox accordingly.
        #
        zoomerPref = prefs["magZoomerType"]
        if zoomerPref == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
            # Translators: magnification will use the full screen.
            #
            zoomerType = _("Full Screen")
        elif zoomerPref == settings.MAG_ZOOMER_TYPE_TOP_HALF:
            # Translators: magnification will use the top half of the screen.
            #
            zoomerType = _("Top Half")
        elif zoomerPref == settings.MAG_ZOOMER_TYPE_BOTTOM_HALF:
            # Translators: magnification will use the bottom half of the screen.
            #
            zoomerType = _("Bottom Half")
        elif zoomerPref == settings.MAG_ZOOMER_TYPE_LEFT_HALF:
            # Translators: magnification will use the left half of the screen.
            #
            zoomerType = _("Left Half")
        elif zoomerPref == settings.MAG_ZOOMER_TYPE_RIGHT_HALF:
            # Translators: magnification will use the right half of the screen.
            #
            zoomerType = _("Right Half")
        elif zoomerPref == settings.MAG_ZOOMER_TYPE_CUSTOM:
            # Translators: the user has selected a custom area of the screen
            # to use for magnification.
            #
            zoomerType = _("Custom")
        else:
            # Translators: this is an algorithm for magnifying pixels
            # on the screen.
            #
            zoomerType = _("Full Screen")

        magZoomerPositionComboBox = self.get_widget("magZoomerPositionComboBox")
        types = [_("Full Screen"),
                 _("Top Half"),
                 _("Bottom Half"),
                 _("Left Half"),
                 _("Right Half"),
                 _("Custom")]
        self.populateComboBox(magZoomerPositionComboBox, types)
        index = self.getComboBoxIndex(magZoomerPositionComboBox, zoomerType)
        magZoomerPositionComboBox.set_active(index)

        # Set the magnifier zoomer position items [in]sensensitive,
        # depending upon the zoomer position type.
        #
        self.get_widget("magZoomerCustomPositionTable").\
                set_sensitive(zoomerPref == settings.MAG_ZOOMER_TYPE_CUSTOM)

        # Populate the zoomer spin buttons based on the size of the target
        # display.
        #
        self._setZoomerSpinButtons()

        # Get the zoom factor preference and set the zoom factor spin
        # button value accordingly.
        #
        zoomFactor = prefs["magZoomFactor"]
        self.get_widget("magZoomFactorSpinButton").set_value(zoomFactor)

        # Get the 'Invert Colors' preference and set the checkbox accordingly.
        #
        value = prefs["enableMagZoomerColorInversion"]
        self.get_widget("magInvertColorsCheckBox").set_active(value)

        # Get the mouse tracking preference and set the active value for
        # the mouse tracking combobox accordingly.
        #
        mouseTrackingMode = prefs["magMouseTrackingMode"]
        if mouseTrackingMode == settings.MAG_TRACKING_MODE_CENTERED:
            mode = self.magTrackingCenteredStr
        elif mouseTrackingMode == settings.MAG_TRACKING_MODE_NONE:
            mode = self.magTrackingNoneStr
        elif mouseTrackingMode == settings.MAG_TRACKING_MODE_PROPORTIONAL:
            mode = self.magTrackingProportionalStr
        elif mouseTrackingMode == settings.MAG_TRACKING_MODE_PUSH:
            mode = self.magTrackingPushStr
        else:
            mode = self.magTrackingCenteredStr
        magMouseTrackingComboBox = self.get_widget("magMouseTrackingComboBox")
        trackingTypes = \
            [_("Centered"), _("Proportional"), _("Push"), _("None")]
        self.populateComboBox(magMouseTrackingComboBox, trackingTypes)
        index = self.getComboBoxIndex(magMouseTrackingComboBox, mode)
        magMouseTrackingComboBox.set_active(index)

        # Get the control and menu item tracking preference and set the 
        # active value for the control and menu item tracking combobox 
        # accordingly.
        #
        controlTrackingMode = prefs["magControlTrackingMode"]
        if controlTrackingMode == settings.MAG_TRACKING_MODE_CENTERED:
            mode = self.magTrackingCenteredStr
        elif controlTrackingMode == settings.MAG_TRACKING_MODE_NONE:
            mode = self.magTrackingNoneStr
        elif controlTrackingMode == settings.MAG_TRACKING_MODE_PUSH:
            mode = self.magTrackingPushStr
        else:
            mode = self.magTrackingPushStr
        magControlTrackingComboBox = \
                         self.get_widget("magControlTrackingComboBox")
        trackingTypes = [_("Centered"), _("Push"), _("None")]
        self.populateComboBox(magControlTrackingComboBox, trackingTypes)
        index = self.getComboBoxIndex(magControlTrackingComboBox, mode)
        magControlTrackingComboBox.set_active(index)

        # Get the text cursor tracking preference and set the active value
        # for the text cursor tracking combobox accordingly.
        #
        textCursorTrackingMode = prefs["magTextTrackingMode"]
        if textCursorTrackingMode == settings.MAG_TRACKING_MODE_CENTERED:
            mode = self.magTrackingCenteredStr
        elif textCursorTrackingMode == settings.MAG_TRACKING_MODE_NONE:
            mode = self.magTrackingNoneStr
        elif textCursorTrackingMode == settings.MAG_TRACKING_MODE_PUSH:
            mode = self.magTrackingPushStr
        else:
            mode = self.magTrackingPushStr
        magTextCursorTrackingComboBox = \
                         self.get_widget("magTextCursorTrackingComboBox")
        self.populateComboBox(magTextCursorTrackingComboBox, trackingTypes)
        index = self.getComboBoxIndex(magTextCursorTrackingComboBox, mode)
        magTextCursorTrackingComboBox.set_active(index)
        self.get_widget("magEdgeMarginHBox").\
            set_sensitive(textCursorTrackingMode == \
                                       settings.MAG_TRACKING_MODE_PUSH)

        # Get the edge margin preference for cursor tracking and set the
        # value of the edge margin spin button accordingly.
        #
        edgeMargin = prefs["magEdgeMargin"]
        magEdgeMarginSpinButton = self.get_widget("magEdgeMarginSpinButton")
        adjustment = gtk.Adjustment(edgeMargin, 0, 50, 1, 5, 0)
        self.get_widget("magEdgeMarginSpinButton").set_adjustment(adjustment)

        # Get the preferences for what the pointer "follows" and set the
        # values of the pointer follows focus and pointer follows zoomer
        # checkboxes accordingly.
        #
        value = prefs["magPointerFollowsFocus"]
        self.get_widget("magPointerFocusCheckButton").set_active(value)
        value = prefs["magPointerFollowsZoomer"]
        self.get_widget("magPointerZoomerCheckButton").set_active(value)

        # Text attributes pane.
        #
        self._createTextAttributesTreeView()

        brailleIndicator = prefs["textAttributesBrailleIndicator"]
        if brailleIndicator == settings.TEXT_ATTR_BRAILLE_7:
            self.get_widget("textBraille7Button").set_active(True)
        elif brailleIndicator == settings.TEXT_ATTR_BRAILLE_8:
            self.get_widget("textBraille8Button").set_active(True)
        elif brailleIndicator == settings.TEXT_ATTR_BRAILLE_BOTH:
            self.get_widget("textBrailleBothButton").set_active(True)
        else:
            self.get_widget("textBrailleNoneButton").set_active(True)

        # Pronunciation dictionary pane.
        #
        self._createPronunciationTreeView()

        # General pane.
        #
        self.get_widget("showMainWindowCheckButton").set_active( \
                        prefs["showMainWindow"])
        self.get_widget("confirmQuitCheckButton").set_active( \
                        prefs["quitOrcaNoConfirmation"])
        self.get_widget("presentToolTipsCheckButton").set_active( \
            prefs["presentToolTips"] and settings.canPresentToolTips)

        self.disableKeyGrabPref = settings.isGKSUGrabDisabled()
        self.get_widget("disableKeyGrabCheckButton").set_active( \
                        self.disableKeyGrabPref)

        if prefs["keyboardLayout"] == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            self.get_widget("generalDesktopButton").set_active(True)
        else:
            self.get_widget("generalLaptopButton").set_active(True)

        self.enableLiveUpdating = liveUpdating

        self.enableAutostart = settings.isOrcaAutostarted()
        self.get_widget("autostartOrcaCheckbutton").set_active( \
                         self.enableAutostart)

    def populateComboBox(self, combobox, items):
        """Populates the combobox with the items provided.

        Arguments:
        - combobox: the GtkComboBox to populate
        - items: the list of strings with which to populate it
        """

        model = gtk.ListStore(str)
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

    def showGUI(self):
        """Show the Orca configuration GUI window. This assumes that
        the GUI has already been created.
        """

        orcaSetupWindow = self.get_widget("orcaSetupWindow")

        accelGroup = gtk.AccelGroup()
        orcaSetupWindow.add_accel_group(accelGroup)
        helpButton = self.get_widget("helpButton")
        (keyVal, modifierMask) = gtk.accelerator_parse("F1")
        helpButton.add_accelerator("clicked",
                                   accelGroup,
                                   keyVal,
                                   modifierMask,
                                   0)

        # We want the Orca preferences window to have focus when it is
        # shown. First try using the present() call. If this isn't present
        # in the version of pygtk that the user is using, just catch the
        # exception. Then try to set the current time on the Preferences 
        # window using set_user_time. If that isn't found, then catch the 
        # exception and fail gracefully.
        #
        orcaSetupWindow.realize()
        try:
            if settings.showMainWindow:
                orcaSetupWindow.present()
        except:
            pass
        try:
            ts = orca_state.lastInputEventTimestamp
            if ts == 0:
                ts = gtk.get_current_event_time()
            orcaSetupWindow.window.set_user_time(ts)
        except AttributeError:
            debug.printException(debug.LEVEL_FINEST)

        # We always want to re-order the text attributes page so that enabled
        # items are consistently at the top.
        #
        self._setSpokenTextAttributes(self.getTextAttributesView,
                            settings.enabledSpokenTextAttributes, True, True)

        orcaSetupWindow.show()

    def _initComboBox(self, combobox):
        """Initialize the given combo box to take a list of int/str pairs.

        Arguments:
        - combobox: the GtkComboBox to initialize.
        """

        cell = gtk.CellRendererText()
        combobox.pack_start(cell, True)
        # We only want to display one column; not two.
        #
        try:
            columnToDisplay = combobox.get_cells()[0]
            combobox.add_attribute(columnToDisplay, 'text', 1)
        except:
            combobox.add_attribute(cell, 'text', 1)
        model = gtk.ListStore(int, str)
        combobox.set_model(model)

        # Force the display comboboxes to be left aligned.
        #
        if isinstance(combobox, gtk.ComboBoxEntry):
            size = combobox.size_request()
            cell.set_fixed_size(size[0] - 29, -1)

        return model

    def _setKeyEchoItems(self):
        """[In]sensitize the checkboxes for the various types of key echo,
        depending upon whether the value of the key echo check button is set.
        """

        enable = self.get_widget("keyEchoCheckbutton").get_active()
        self.get_widget("printableCheckbutton").set_sensitive(enable)
        self.get_widget("modifierCheckbutton").set_sensitive(enable)
        self.get_widget("lockingCheckbutton").set_sensitive(enable)
        self.get_widget("functionCheckbutton").set_sensitive(enable)
        self.get_widget("actionCheckbutton").set_sensitive(enable)
        self.get_widget("navigationCheckbutton").set_sensitive(enable)
        self.get_widget("diacriticalCheckbutton").set_sensitive(enable)

    def _say(self, text, stop=False):
        """If the text field is not None, speaks the given text, optionally
        interrupting anything currently being spoken.

        Arguments:
        - text: the text to print and speak
        - stop: if True, interrupt any speech currently being spoken
        """

        if stop:
            speech.stop()

        speech.speak(text)

    def _createNode(self, appName):
        """Create a new root node in the TreeStore model with the name of the
            application.

        Arguments:
        - appName: the name of the TreeStore Node (the same of the application)
        """

        model = self.keyBindingsModel

        myiter = model.append(None)
        model.set(myiter,
                  DESCRIP, appName,
                  MODIF, False)

        return myiter

    def _getIterOf(self, appName):
        """Returns the gtk.TreeIter of the TreeStore model
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
            # Translators: Orca keybindings support double
            # and triple "clicks" or key presses, similar to
            # using a mouse. 
            #
            clickCountString = " " + _("(double click)")
        elif clickCount == 3:
            # Translators: Orca keybindings support double
            # and triple "clicks" or key presses, similar to
            # using a mouse. 
            #
            clickCountString = " " + _("(triple click)")

        return clickCountString

    def _addAlternateKeyBinding(self, kb):
        """Adds an alternate keybinding to the existing handler and
        returns true.  In case it doesn't exist yet, just returns
        false.

        Argument:
        - kb: the keybinding to be added as an alternate keybinding.
        """

        model = self.keyBindingsModel
        myiter = model.get_iter_first()
        exist = False

        while myiter != None:
            iterChild = model.iter_children(myiter)
            while iterChild != None:
                if model.get(iterChild, DESCRIP)[0] == kb.handler.description:
                    exist = True
                    if not kb.keysymstring:
                        text = None
                    else:
                        clickCount = self._clickCountToString(kb.click_count)
                        text = keybindings.getModifierNames(kb.modifiers) \
                               + kb.keysymstring \
                               + clickCount
                    model.set(iterChild,
                              MOD_MASK2, kb.modifier_mask,
                              MOD_USED2, kb.modifiers,
                              KEY2, kb.keysymstring,
                              CLICK_COUNT2, kb.click_count,
                              OLDTEXT2, text,
                              TEXT2, text)
                iterChild = model.iter_next(iterChild)
            myiter = model.iter_next(myiter)

        return exist

    def _insertRow(self, handl, kb, parent=None, modif=False):
        """Appends a new row with the new keybinding data to the treeview

        Arguments:
        - handl:  the name of the handler associated to the keyBinding
        - kb:     the new keybinding.
        - parent: the parent node of the treeview, where to append the kb
        - modif:  whether to check the modified field or not.

        Returns a gtk.TreeIter pointing at the new row.
        """

        model = self.keyBindingsModel

        if parent == None:
            parent = self._getIterOf(_("Orca"))

        if parent != None:
            myiter = model.append(parent)
            if not kb.keysymstring:
                text = None
            else:
                clickCount = self._clickCountToString(kb.click_count)
                text = keybindings.getModifierNames(kb.modifiers) \
                       + kb.keysymstring \
                       + clickCount
            model.set (myiter,
                       HANDLER,      handl,
                       DESCRIP,      kb.handler.description,
                       MOD_MASK1,    kb.modifier_mask,
                       MOD_USED1,    kb.modifiers,
                       KEY1,         kb.keysymstring,
                       CLICK_COUNT1, kb.click_count,
                       OLDTEXT1,     text,
                       TEXT1,        text,
                       MODIF,        modif,
                       EDITABLE,     True)
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

        Returns a gtk.TreeIter pointing at the new row.
        """

        model = self.keyBindingsModel

        if parent == None:
            # Translators: an external braille device has buttons on it that
            # permit the user to create input gestures from the braille device.
            # The braille bindings are what determine the actions Orca will
            # take when the user presses these buttons.
            #
            parent = self._getIterOf(_("Braille Bindings"))

        if parent != None:
            myiter = model.append(parent)
            model.set (myiter,
                       HANDLER,  handl,
                       DESCRIP,  inputEvHand.description,
                       KEY1,     com,
                       TEXT1,    braille.command_name[com],
                       MODIF,    modif,
                       EDITABLE, False)
            return myiter
        else:
            return None

    def _markModified(self):
        """ Mark as modified the user custom key bindings:
        """

        try:
            defScript = default.Script(None)
            defScript.setupInputEventHandlers()
            keyBinds = keybindings.KeyBindings()
            keyBinds = settings.overrideKeyBindings(defScript, keyBinds)
            keyBind = keybindings.KeyBinding(None, None, None, None)
            treeModel = self.keyBindingsModel

            myiter = treeModel.get_iter_first()
            while myiter != None:
                iterChild = treeModel.iter_children(myiter)
                while iterChild != None:
                    descrip = treeModel.get_value(iterChild, DESCRIP)
                    keyBind.handler = \
                        input_event.InputEventHandler(None,descrip)
                    if keyBinds.hasKeyBinding(keyBind,
                                              typeOfSearch="description"):
                        treeModel.set_value(iterChild, MODIF, True)
                    iterChild = treeModel.iter_next(iterChild)
                myiter = treeModel.iter_next(myiter)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def _populateKeyBindings(self, clearModel=True):
        """Fills the TreeView with the list of Orca keybindings

        Arguments:
        - clearModel: if True, initially clear out the key bindings model.
        """

        self.keyBindView.set_model(None)
        self.keyBindView.set_headers_visible(False)
        self.keyBindView.hide_all()
        self.keyBindView.hide()
        if clearModel:
            self.keyBindingsModel.clear()
            self.kbindings = None

        iterOrca = self._getIterOf("Orca") or self._createNode(_("Orca"))

        # Translators: this refers to commands that do not currently have
        # an associated key binding.
        #
        iterUnbound = self._getIterOf("Unbound") \
                      or self._createNode(_("Unbound"))

        defScript = default.Script(None)

        # If we are in the app-specific preferences, we already have
        # populated our tree with bindings.  Otherwise, we need to
        # start from scratch.
        #
        if not self.kbindings:
            self.kbindings = keybindings.KeyBindings()
            self.defKeyBindings = defScript.getKeyBindings()
            for kb in self.defKeyBindings.keyBindings:
                if not self.kbindings.hasKeyBinding(kb, "strict"):
                    if not self._addAlternateKeyBinding(kb):
                        handl = defScript.getInputEventHandlerKey(kb.handler)
                        if kb.keysymstring:
                            self._insertRow(handl, kb, iterOrca)
                        else:
                            self._insertRow(handl, kb, iterUnbound)
                self.kbindings.add(kb)

        if not self.keyBindingsModel.iter_has_child(iterUnbound):
            self.keyBindingsModel.remove(iterUnbound)

        self.orcaModKeyEntry = self.get_widget("orcaModKeyEntry")
        self.orcaModKeyEntry.set_text(
            str(settings.orcaModifierKeys)[1:-1].replace("'",""))

        self._markModified()

        # Translators: an external braille device has buttons on it that
        # permit the user to create input gestures from the braille device.
        # The braille bindings are what determine the actions Orca will
        # take when the user presses these buttons.
        #
        iterBB = self._createNode(_("Braille Bindings"))
        self.bbindings = defScript.getBrailleBindings()
        for com, inputEvHand in self.bbindings.iteritems():
            handl = defScript.getInputEventHandlerKey(inputEvHand)
            self._insertRowBraille(handl, com, inputEvHand, iterBB)

        self.keyBindView.set_model(self.keyBindingsModel)
        self.keyBindView.set_headers_visible(True)
        self.keyBindView.expand_all()
        self.keyBindingsModel.set_sort_column_id(OLDTEXT1, gtk.SORT_ASCENDING)
        self.keyBindView.show()

        # Keep track of new/unbound keybindings that have yet to be applied.
        #
        self.pendingKeyBindings = {}

    def _cleanupSpeechServers(self):
        """Remove unwanted factories and gnome-speech drivers for the current
        active factory, when the user dismisses the Orca Preferences dialog.
        """

        for workingFactory in self.workingFactories:
            if not (workingFactory == self.speechSystemsChoice):
                workingFactory.SpeechServer.shutdownActiveServers()
            else:
                servers = workingFactory.SpeechServer.getSpeechServers()
                for server in servers:
                    if not (server == self.speechServersChoice):
                        server.shutdown()

    def speechSupportChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           speechSupportCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Speech' checkbox. Set the 'enableSpeech'
           preference to the new value. Set the rest of the speech pane items
           [in]sensensitive depending upon whether this checkbox is checked.

        Arguments:
        - widget: the component that generated the signal.
        """

        enable = widget.get_active()
        self.prefsDict["enableSpeech"] = enable
        self.get_widget("speechVbox").set_sensitive(enable)

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
        except:
            pass

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
            language = family[speechserver.VoiceFamily.LOCALE]
            voiceType = self.get_widget("voiceTypes").get_active()
            self._setFamilyNameForVoiceType(voiceType, name, language)
        except:
            debug.printException(debug.LEVEL_SEVERE)

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
           GtkHScale widget. The user has changed the current rate value.
           Save the new rate value based on the currently selected voice
           type.

        Arguments:
        - widget: the component that generated the signal.
        """

        rate = widget.get_value()
        voiceType = self.get_widget("voiceTypes").get_active()
        self._setRateForVoiceType(voiceType, rate)
        settings.voices[settings.DEFAULT_VOICE][acss.ACSS.RATE] = rate

    def pitchValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the pitchScale
           GtkHScale widget. The user has changed the current pitch value.
           Save the new pitch value based on the currently selected voice
           type.

        Arguments:
        - widget: the component that generated the signal.
        """

        pitch = widget.get_value()
        voiceType = self.get_widget("voiceTypes").get_active()
        self._setPitchForVoiceType(voiceType, pitch)
        settings.voices[settings.DEFAULT_VOICE][acss.ACSS.AVERAGE_PITCH] = pitch

    def volumeValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the voiceScale
           GtkHScale widget. The user has changed the current volume value.
           Save the new volume value based on the currently selected voice
           type.

        Arguments:
        - widget: the component that generated the signal.
        """

        volume = widget.get_value()
        voiceType = self.get_widget("voiceTypes").get_active()
        self._setVolumeForVoiceType(voiceType, volume)
        settings.voices[settings.DEFAULT_VOICE][acss.ACSS.GAIN] = volume

    def speechIndentationChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           speechIndentationCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Speak indentation and justification' checkbox.
           Set the 'enableSpeechIndentation' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        enable = widget.get_active()
        self.prefsDict["enableSpeechIndentation"] = enable

    def speakBlankLinesChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           speakBlankLinesCheckButton GtkCheckButton widget. The user has
           [un]checked the 'Speak blank lines' checkbox.
           Set the 'speakBlankLines' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["speakBlankLines"] = widget.get_active()

    def speakMultiCaseStringsToggled(self, widget):
        """Signal handler for the "toggled" signal for the
           speakMultiCaseAsWordsCheckButton GtkCheckButton widget. The user has
           [un]checked the checkbox.
           Set the 'speakMultiCaseStringsAsWords' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["speakMultiCaseStringsAsWords"] = widget.get_active()

    def speakTutorialMessagesToggled(self, widget):
        """Signal handler for the "toggled" signal for the
           speakTutorialMessagesCheckButton GtkCheckButton widget.
           Set the 'enableTutorialMessages' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableTutorialMessages"] = widget.get_active()

    def pauseBreaksToggled (self, widget):
        """Signal handler for the "toggled" signal for the
           pauseBreaksCheckButton GtkCheckButton widget.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enablePauseBreaks"] = widget.get_active()

    def speakPositionToggled(self, widget):
        """Signal handler for the "toggled" signal for the
           speakPositionCheckButton GtkCheckButton widget.
           Set the 'enablePositionSpeaking' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enablePositionSpeaking"] = widget.get_active()

    def mnemonicSpeakingChecked (self, widget):
        """Signal handler for the "toggled" signal for the
           speakMnemonicsCheckButton GtkCheckButton widget.
           Set the 'Speak mnemonics automaticaly' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableMnemonicSpeaking"] = widget.get_active()

    def brailleSupportChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           brailleSupportCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Braille support' checkbox. Set the
           'enableBraille' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableBraille"] = widget.get_active()

    def brailleMonitorChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           brailleMonitorCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Braille monitor' checkbox. Set the
           'enableBrailleMonitor' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableBrailleMonitor"] = widget.get_active()

    def keyEchoChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           keyEchoCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Key Echo' checkbox. Set the
           'enableKeyEcho' preference to the new value. [In]sensitize
           the checkboxes for the various types of key echo, depending
           upon whether this value is checked or unchecked.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableKeyEcho"] = widget.get_active()
        self._setKeyEchoItems()

    def printableKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           printableCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable alphanumeric and punctuation keys'
           checkbox. Set the 'enablePrintableKeys' preference to the
           new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enablePrintableKeys"] = widget.get_active()

    def modifierKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           modifierCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable modifier keys' checkbox. Set the
           'enableModifierKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableModifierKeys"] = widget.get_active()

    def lockingKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           lockingCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable locking keys' checkbox. Set the
           'enableLockingKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableLockingKeys"] = widget.get_active()

    def functionKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           functionCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable locking keys' checkbox. Set the
           'enableLockingKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableFunctionKeys"] = widget.get_active()

    def actionKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           actionCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable action keys' checkbox. Set the
           'enableActionKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """
        self.prefsDict["enableActionKeys"] = widget.get_active()

    def navigationKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           navigationCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable navigation keys' checkbox. Set the
           'enableNavigationKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """
        self.prefsDict["enableNavigationKeys"] = widget.get_active()

    def diacriticalKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           diacriticalCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable diacritical keys' checkbox. Set the
           'enableDiacriticalKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """
        self.prefsDict["enableDiacriticalKeys"] = widget.get_active()

    def echoByCharacterChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           echoByCharacterCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Echo by Character' checkbox. Set the
           'enableEchoByCharacter' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableEchoByCharacter"] = widget.get_active()

    def echoByWordChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           echoByWordCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Echo by Word' checkbox. Set the
           'enableEchoByWord' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableEchoByWord"] = widget.get_active()

    def echoBySentenceChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           echoBySentenceCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Echo by Sentence' checkbox. Set the
           'enableEchoBySentence' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableEchoBySentence"] = widget.get_active()

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
            # Translators: A single braille cell on a refreshable
            # braille display consists of 8 dots.  If the user
            # chooses this setting, the dot in the bottom left
            # corner will be used to 'underline' text of interest.
            #
            if widget.get_label() == _("Dot _7"):
                self.prefsDict["brailleSelectorIndicator"] = \
                    settings.BRAILLE_SEL_7
            # Translators: If the user chooses this setting, the
            # dot in the bottom right corner of the braille cell
            # will be used to 'underline' text of interest.
            #
            elif widget.get_label() == _("Dot _8"):
                self.prefsDict["brailleSelectorIndicator"] = \
                    settings.BRAILLE_SEL_8
            # Translators: If the user chooses this setting, the
            # two dots at the bottom of the braille cell will be
            # used to 'underline' text of interest.
            #
            elif widget.get_label() == _("Dots 7 an_d 8"):
                self.prefsDict["brailleSelectorIndicator"] = \
                    settings.BRAILLE_SEL_BOTH
            else:
                self.prefsDict["brailleSelectorIndicator"] = \
                    settings.BRAILLE_SEL_NONE

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
            # Translators: A single braille cell on a refreshable
            # braille display consists of 8 dots.  If the user
            # chooses this setting, the dot in the bottom left
            # corner will be used to 'underline' text of interest.
            #
            if widget.get_label() == _("Dot _7"):
                self.prefsDict["brailleLinkIndicator"] = \
                    settings.BRAILLE_LINK_7
            # Translators: If the user chooses this setting, the
            # dot in the bottom right corner of the braille cell
            # will be used to 'underline' text of interest.
            #
            elif widget.get_label() == _("Dot _8"):
                self.prefsDict["brailleLinkIndicator"] = \
                    settings.BRAILLE_LINK_8
            # Translators: If the user chooses this setting, the
            # two dots at the bottom of the braille cell will be
            # used to 'underline' text of interest.
            #
            elif widget.get_label() == _("Dots 7 an_d 8"):
                self.prefsDict["brailleLinkIndicator"] = \
                    settings.BRAILLE_LINK_BOTH
            else:
                self.prefsDict["brailleLinkIndicator"] = \
                    settings.BRAILLE_LINK_NONE

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
            # Translators: A single braille cell on a refreshable
            # braille display consists of 8 dots.  If the user
            # chooses this setting, the dot in the bottom left
            # corner will be used to 'underline' text of interest.
            #
            if widget.get_label() == _("Dot _7"):
                self.prefsDict["textAttributesBrailleIndicator"] = \
                    settings.TEXT_ATTR_BRAILLE_7
            # Translators: If the user chooses this setting, the
            # dot in the bottom right corner of the braille cell
            # will be used to 'underline' text of interest.
            #
            elif widget.get_label() == _("Dot _8"):
                self.prefsDict["textAttributesBrailleIndicator"] = \
                    settings.TEXT_ATTR_BRAILLE_8
            # Translators: If the user chooses this setting, the
            # two dots at the bottom of the braille cell will be
            # used to 'underline' text of interest.
            #
            elif widget.get_label() == _("Dots 7 an_d 8"):
                self.prefsDict["textAttributesBrailleIndicator"] = \
                    settings.TEXT_ATTR_BRAILLE_BOTH
            else:
                self.prefsDict["textAttributesBrailleIndicator"] = \
                    settings.TEXT_ATTR_BRAILLE_NONE

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
            # Translators: If this setting is chosen, no punctuation
            # symbols will be spoken as a user reads a document.
            #
            if widget.get_label() == _("_None"):
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_NONE
            # Translators: If this setting is chosen, common punctuation
            # symbols (like comma, period, question mark) will not be
            # spoken as a user reads a document, but less common symbols
            # (such as #, @, $) will.
            #
            elif widget.get_label() == _("So_me"):
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_SOME
            # Translators: If this setting is chosen, the majority of
            # punctuation symbols will be spoken as a user reads a
            # document.
            #
            elif widget.get_label() == _("M_ost"):
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_MOST
            else:
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_ALL

    def progressBarVerbosityChanged(self, widget):
        """Signal handler for the changed signal for the progressBarVerbosity
           GtkComboBox widget. Set the 'progressBarVerbosity' preference to
           the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        progressBarVerbosity = widget.get_active_text()
        # Translators: Orca has a setting which determines which progress
        # bar updates should be announced. Choosing "All" means that Orca
        # will present progress bar updates regardless of what application
        # and window they happen to be in.
        #
        if progressBarVerbosity == C_("ProgressBar", "All"):
            self.prefsDict["progressBarVerbosity"] = \
                settings.PROGRESS_BAR_ALL
        # Translators: Orca has a setting which determines which progress
        # bar updates should be announced. Choosing "Window" means that
        # Orca will present progress bar updates as long as the progress
        # bar is in the active window.
        #
        elif progressBarVerbosity == C_("ProgressBar", "Window"):
            self.prefsDict["progressBarVerbosity"] = \
                settings.PROGRESS_BAR_WINDOW
        # Translators: Orca has a setting which determines which progress
        # bar updates should be announced. Choosing "Application" means
        # that Orca will present progress bar updates as long as the
        # progress bar is in the active application (but not necessarily
        # in the current window).
        #
        else:
            self.prefsDict["progressBarVerbosity"] = \
                settings.PROGRESS_BAR_APPLICATION

    def sayAllStyleChanged(self, widget):
        """Signal handler for the "changed" signal for the sayAllStyle
           GtkComboBox widget. Set the 'sayAllStyle' preference to the
           new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        sayAllStyle = widget.get_active_text()
        # Translators: If this setting is chosen and the user is reading
        # over an entire document, Orca will pause at the end of each
        # line.
        #
        if sayAllStyle == _("Line"):
            self.prefsDict["sayAllStyle"] = settings.SAYALL_STYLE_LINE
        # Translators: If this setting is chosen and the user is reading
        # over an entire document, Orca will pause at the end of each
        # sentence.
        #
        elif sayAllStyle == _("Sentence"):
            self.prefsDict["sayAllStyle"] = settings.SAYALL_STYLE_SENTENCE

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
            # Translators: This refers to the amount of information
            # Orca provides about a particular object that receives
            # focus.
            #
            if widget.get_label() == _("Brie_f"):
                self.prefsDict["speechVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_BRIEF
            else:
                self.prefsDict["speechVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_VERBOSE

    def tableSpeechChanged(self, widget):
        """Signal handler for the "toggled" signal for the cellSpeechButton,
           or rowSpeechButton GtkRadioButton widgets. The user has
           toggled the table row speech type value. If this signal was
           generated as the result of a radio button getting selected
           (as opposed to a radio button losing the selection), set the
           'readTableCellRow' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        if widget.get_active():
            # Translators: when users are navigating a table, they
            # sometimes want the entire row of a table read, or
            # they just want the current cell to be presented to them.
            #
            if widget.get_label() == _("Speak current _cell"):
                self.prefsDict["readTableCellRow"] = False
            else:
                self.prefsDict["readTableCellRow"] = True

    def speechProgressBarChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           speechProgressBarCheckbutton GtkCheckButton widget.
           The user has [un]checked the "Speak progress bar updates" checkbox.
           Set the 'enableProgressBarUpdates' preference to the new value.
           Set the rest of the 'update interval' hbox items [in]sensensitive
           depending upon whether this checkbox is checked.

        Arguments:
        - widget: the component that generated the signal.
        """

        enable = widget.get_active()
        self.prefsDict["enableProgressBarUpdates"] = enable
        self.get_widget("speakUpdateIntervalHBox").set_sensitive(enable)
        self.get_widget("progressBarVerbosityHBox").set_sensitive(enable)

    def speakProgressBarValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           speakProgressBarSpinButton GtkSpinButton widget.
           The user has changed the value of the "speak progress bar
           updates" spin button. Set the 'progressBarUpdateInterval'
           preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["progressBarUpdateInterval"] = widget.get_value_as_int()


    def speakUnderMouseChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           speakUnderMouseCheckButton GtkCheckButton widget.
           The user has [un]checked the "Speak object under mouse" checkbox.
           Set the 'enableMouseReview' preference to the new value.
           Set the rest of the 'dwell time' hbox items [in]sensensitive
           depending upon whether this checkbox is checked.

        Arguments:
        - widget: the component that generated the signal.
        """

        enable = widget.get_active()
        self.prefsDict["enableMouseReview"] = enable

    def autostartOrcaChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           autoStartOrcaCheckbutton GtkCheckButton widget.
           The user has [un]checked the 'Start Orca when you login'
           checkbox. Remember the new setting so that it can be used
           to create or remove ~/.config/autostart/orca.desktop, if 
           the user presses the Apply or OK button.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.enableAutostart = widget.get_active()

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

    def disableBrailleEOLChecked(self, widget):
        """Signal handler for the "toggled" signal for the disableBrailleEOL
           GtkCheckButton widget. The user has [un]checked the 'Disable
           braille end of line symbol' checkbox. Set the 'disableBrailleEOL'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["disableBrailleEOL"] = widget.get_active()

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
            if widget.get_label() == _("Brie_f"):
                self.prefsDict["brailleVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_BRIEF
            else:
                self.prefsDict["brailleVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_VERBOSE

    def magnifierSupportChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magnifierSupportCheckbutton GtkCheckButton widget.
           The user has [un]checked the 'Enable Magnification' checkbox.
           Set the 'enableMagnifier' preference to the new value.
           Set the rest of the magnifier pane items [in]sensensitive
           depending upon whether this checkbox is checked.

        Arguments:
        - widget: the component that generated the signal.
        """

        enable = widget.get_active()
        if self.enableLiveUpdating and widget.is_focus():
            if enable:
                mag.init()
                # If the Zoomer settings position is full screen, and
                # we are full screen capable and we are capable of
                # hiding or showing the system pointer, then show the
                # Hide system cursor checkbox.
                #
                isFullScreen = (self.prefsDict["magZoomerType"] \
                                == settings.MAG_ZOOMER_TYPE_FULL_SCREEN)
                self.get_widget("magHideCursorCheckButton").set_sensitive(
                    mag.isFullScreenCapable() and isFullScreen)
            else:
                mag.shutdown()
        self.prefsDict["enableMagnifier"] = enable
        self.get_widget("magnifierTable").set_sensitive(enable)

    def magCursorOnOffChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magCursorOnOffCheckButton GtkCheckButton widget.
           The user has [un]checked the magnification cursor settings
           'Cursor on/off' checkbox. Set the 'enableMagCursor' preference
           to the new value. Set the sensitivity of the other cursor items
           depending upon this new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        enableCursor = widget.get_active()
        if self.enableLiveUpdating and widget.is_focus():
            custom = self.get_widget("magCursorSizeCheckButton").get_active()
            size = \
                 self.get_widget("magCursorSizeSpinButton").get_value_as_int()
            mag.setMagnifierCursor(enableCursor, custom, size)
        self.prefsDict["enableMagCursor"] = enableCursor
        self.get_widget("magCursorTable").set_sensitive(enableCursor)

    def magCursorExplicitSizeChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magCursorSizeCheckButton GtkCheckButton widget.
           The user has [un]checked the magnification cursor settings
           'Explicit cursor size' checkbox. Set the
           'enableMagCursorExplicitSize' preference to the new value.
           [Un]sensitize the cursor size spin button and label depending
           upon whether this checkbox is checked.

        Arguments:
        - widget: the component that generated the signal.
        """

        enable = widget.get_active()
        if self.enableLiveUpdating and widget.is_focus():
            size = \
                 self.get_widget("magCursorSizeSpinButton").get_value_as_int()
            mag.setMagnifierCursor(True, enable, size)
        self.prefsDict["enableMagCursorExplicitSize"] = enable
        self.get_widget("magCursorSizeSpinButton").set_sensitive(enable)
        self.get_widget("magCursorSizeLabel").set_sensitive(enable)

    def magCursorSizeValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magCursorSizeSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           cursor settings cursor size spin button. Set the
           'magCursorSize' preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        size = widget.get_value_as_int()
        if self.enableLiveUpdating and widget.is_focus():
            mag.setMagnifierCursor(True, True, size)
        self.prefsDict["magCursorSize"] = size

    def magCursorColorSet(self, widget):
        """Signal handler for the "color_set" signal for the
           magCursorColorButton GtkColorButton widget.
           The user has changed the value of the magnification
           cursor settings cursor color button. Set the 'magCursorColor'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        color = widget.get_color()
        cursorColor = "#%04X%04X%04X" % (color.red, color.green, color.blue)
        if self.enableLiveUpdating and widget.is_focus():
            mag.setMagnifierObjectColor("cursor-color", cursorColor)

            # For some reason, live updating of the cursor color is not
            # working. Toggling the visibility with setMagnifierCursor()
            # seems to force the updating we want.
            #
            size = \
                 self.get_widget("magCursorSizeSpinButton").get_value_as_int()
            mag.setMagnifierCursor(False, False, 0)
            mag.setMagnifierCursor(True, True, size)

        self.prefsDict["magCursorColor"] = cursorColor

    def magCrossHairOnOffChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magCrossHairOnOffCheckButton GtkCheckButton widget.
           The user has [un]checked the magnification cross-hair settings
           'Cross-hair on/off' checkbox. Set the 'enableMagCrossHair'
           preference to the new value. Set the sensitivity of the other
           cross-hair items depending upon this new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = widget.get_active()
        if self.enableLiveUpdating and widget.is_focus():
            mag.setMagnifierCrossHair(value)
        self.prefsDict["enableMagCrossHair"] = value
        self.get_widget("magCrossHairTable").set_sensitive(value)

    def magCrossHairClipOnOffChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magCrossHairClipCheckButton GtkCheckButton widget.
           The user has [un]checked the magnification cross-hair settings
           'Cross-hair clip on/off' checkbox. Set the 'enableMagCrossHairClip'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = widget.get_active()
        if self.enableLiveUpdating and widget.is_focus():
            mag.setMagnifierCrossHairClip(value)
        self.prefsDict["enableMagCrossHairClip"] = value

    def magCrossHairSizeValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magCrossHairSizeSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           cross-hair settings cross-hair size spin button. Set the
           'magCrossHairSize' preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = widget.get_value_as_int()
        if self.enableLiveUpdating and widget.is_focus():
            mag.setMagnifierObjectSize("crosswire-size", value)
        self.prefsDict["magCrossHairSize"] = value

    def magCrossHairColorSet(self, widget):
        """Signal handler for the "color_set" signal for the
           magCrossHairColorButton GtkColorButton widget.
           The user has changed the value of the magnification
           cross-hair settings cross-hair color button. Set the 
           'magCrossHairColor' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        color = widget.get_color()
        crossHairColor = "#%04X%04X%04X" % (color.red, color.green, color.blue)
        if self.enableLiveUpdating and widget.is_focus():
            mag.setMagnifierObjectColor("crosswire-color", crossHairColor)
        self.prefsDict["magCrossHairColor"] = crossHairColor

    def magZoomerPositionChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magZoomerPositionComboBox GtkComboBox widget.
           The user has changed the zoomer position type. Set the 
           'magZoomerType' preference to the new value. 
           Set the magnifier zoomer position items [in]sensensitive, 
           depending upon the new zoomer position type.

        Arguments:
        - widget: the component that generated the signal.
        """

        zoomerType = widget.get_active()
        self.prefsDict["magZoomerType"] = zoomerType

        self.get_widget("magZoomerCustomPositionTable").\
                set_sensitive(zoomerType == settings.MAG_ZOOMER_TYPE_CUSTOM)

        enableBorder = (zoomerType != settings.MAG_ZOOMER_TYPE_FULL_SCREEN)
        checkButton = self.get_widget("magBorderCheckButton")
        checkButton.set_sensitive(enableBorder)

        checked = checkButton.get_active()
        size = 0
        if checked and enableBorder:
            self.get_widget("magBorderTable").set_sensitive(enableBorder)
            size = \
                 self.get_widget("magBorderSizeSpinButton").get_value_as_int()

        # If the Zoomer settings position is full screen, and we are full
        # screen capable and we are capable of hiding or showing the system
        # pointer, then show the Hide system cursor checkbox.
        #
        isFullScreen = (zoomerType == settings.MAG_ZOOMER_TYPE_FULL_SCREEN)
        self.get_widget("magHideCursorCheckButton").set_sensitive(
            mag.isFullScreenCapable() and isFullScreen)

        # Also if it's not full screen, then automatically clear the 
        # 'hide cursor' preference and check box.
        #
        if not isFullScreen:
            self.prefsDict["magHideCursor"] = False
            self.get_widget("magHideCursorCheckButton").set_active(False)

        if not self.enableLiveUpdating:
            return

        if zoomerType == settings.MAG_ZOOMER_TYPE_CUSTOM:
            top = \
                self.get_widget("magZoomerTopSpinButton").get_value_as_int()
            left = \
                 self.get_widget("magZoomerLeftSpinButton").get_value_as_int()
            right = \
                  self.get_widget("magZoomerRightSpinButton").get_value_as_int()
            bottom = \
               self.get_widget("magZoomerBottomSpinButton").get_value_as_int()
            if not (top == bottom == left == right):
                mag.setupMagnifier(zoomerType, left, top, right, bottom,
                                   self.prefsDict)
        else:
            mag.setupMagnifier(zoomerType, restore=self.prefsDict)
        mag.setZoomerObjectSize("border-size", size)

    def magHideCursorChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magHideCursorCheckButton GtkCheckButton widget. The user
           has [un]checked the hide system cursor checkbox. Set the
           'magHideCursor' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        checked = widget.get_active()
        self.prefsDict["magHideCursor"] = checked

        if self.enableLiveUpdating:
            mag.hideSystemPointer(checked)

    def magZoomerTopValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magZoomerTopSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           zoomer placement top spin button. Set the 'magZoomerTop'
           preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        top = widget.get_value_as_int()
        self.prefsDict["magZoomerTop"] = top
        if not (self.enableLiveUpdating and widget.is_focus()):
            return

        left = self.get_widget("magZoomerLeftSpinButton").get_value_as_int()
        right = self.get_widget("magZoomerRightSpinButton").get_value_as_int()
        bottom = \
               self.get_widget("magZoomerBottomSpinButton").get_value_as_int()
        mag.setupMagnifier(settings.MAG_ZOOMER_TYPE_CUSTOM,
                           left, top, right, bottom, self.prefsDict)

    def magZoomerBottomValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magZoomerBottomSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           zoomer placement bottom spin button. Set the 'magZoomerBottom'
           preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        bottom = widget.get_value_as_int()
        self.prefsDict["magZoomerBottom"] = bottom
        if not (self.enableLiveUpdating and widget.is_focus()):
            return

        left = self.get_widget("magZoomerLeftSpinButton").get_value_as_int()
        top = self.get_widget("magZoomerTopSpinButton").get_value_as_int()
        right = self.get_widget("magZoomerRightSpinButton").get_value_as_int()
        mag.setupMagnifier(settings.MAG_ZOOMER_TYPE_CUSTOM,
                           left, top, right, bottom, self.prefsDict)

    def magZoomerLeftValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magZoomerLeftSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           zoomer placement left spin button. Set the 'magZoomerLeft'
           preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        left = widget.get_value_as_int()
        self.prefsDict["magZoomerLeft"] = left
        if not (self.enableLiveUpdating and widget.is_focus()):
            return

        top = self.get_widget("magZoomerTopSpinButton").get_value_as_int()
        right = self.get_widget("magZoomerRightSpinButton").get_value_as_int()
        bottom = \
               self.get_widget("magZoomerBottomSpinButton").get_value_as_int()
        mag.setupMagnifier(settings.MAG_ZOOMER_TYPE_CUSTOM,
                           left, top, right, bottom, self.prefsDict)

    def magZoomerRightValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magZoomerRightSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           zoomer placement right spin button. Set the 'magZoomerRight'
           preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        right = widget.get_value_as_int()
        self.prefsDict["magZoomerRight"] = right
        if not (self.enableLiveUpdating and widget.is_focus()):
            return

        left = self.get_widget("magZoomerLeftSpinButton").get_value_as_int()
        top = self.get_widget("magZoomerTopSpinButton").get_value_as_int()
        bottom = \
               self.get_widget("magZoomerBottomSpinButton").get_value_as_int()
        mag.setupMagnifier(settings.MAG_ZOOMER_TYPE_CUSTOM,
                           left, top, right, bottom, self.prefsDict)

    def magZoomFactorValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magZoomFactorSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           zoom factor spin button. Set the 'magZoomFactor'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = widget.get_value()
        if self.enableLiveUpdating and widget.is_focus():
            mag.setZoomerMagFactor(value, value)
        self.prefsDict["magZoomFactor"] = value

    def magBorderChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magBorderCheckButton GtkCheckButton widget.
           The user has [un]checked the magnification border settings
           'Enable border' checkbox. Set the 'enableMagZoomerBorder'
           preference to the new value and set the sensitivity of the
           other magnification border items depending upon this new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = widget.get_active()
        self.prefsDict["enableMagZoomerBorder"] = value
        self.get_widget("magBorderTable").set_sensitive(value)
        if not (self.enableLiveUpdating and widget.is_focus()):
            return

        size = self.get_widget("magBorderSizeSpinButton").get_value_as_int()
        if not value:
            size = 0
        mag.setZoomerObjectSize("border-size", size)

    def magBorderSizeValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magBorderSizeSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           border settings border size spin button. Set the
           'magZoomerBorderSize' preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = widget.get_value_as_int()
        if self.enableLiveUpdating and widget.is_focus():
            mag.setZoomerObjectSize("border-size", value)
        self.prefsDict["magZoomerBorderSize"] = value

    def magBorderColorSet(self, widget):
        """Signal handler for the "color_set" signal for the
           magBorderColorButton GtkColorButton widget.
           The user has changed the value of the magnification
           cursor settings cursor color button. Set the 'magZoomerBorderColor'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        color = widget.get_color()
        borderColor = "#%04X%04X%04X" % (color.red, color.green, color.blue)
        if self.enableLiveUpdating and widget.is_focus():
            mag.setZoomerObjectColor("border-color", borderColor)
        self.prefsDict["magZoomerBorderColor"] = borderColor

    def magColorBrightnessValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magColorBrightnessSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           color settings brightness spin button. Set the 'magBrightnessLevel'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = round(widget.get_value(), 2)
        self.prefsDict["magBrightnessLevel"] = value
        if not (self.enableLiveUpdating and widget.is_focus()):
            return

        r = self.prefsDict["magBrightnessLevelRed"] + value
        g = self.prefsDict["magBrightnessLevelGreen"] + value
        b = self.prefsDict["magBrightnessLevelBlue"] + value
        mag.setZoomerBrightness(r, g, b)

    def magColorContrastValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magColorContrastSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           color settings contrast spin button. Set the 'magContrastLevel'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = round(widget.get_value(), 2)
        self.prefsDict["magContrastLevel"] = value
        if not (self.enableLiveUpdating and widget.is_focus()):
            return

        r = self.prefsDict["magContrastLevelRed"] + value
        g = self.prefsDict["magContrastLevelGreen"] + value
        b = self.prefsDict["magContrastLevelBlue"] + value
        mag.setZoomerContrast(r, g, b)

    def magAdvancedButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the magAdvancedButton
           GtkButton widget. The user has clicked the Advanced Settings
           button.  Save the current state of the preferences for the settings
           on the dialog, and show it.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca_state.advancedMag.saveAdvancedSettings(self.prefsDict)
        orca_state.advancedMagDialog.show()

    def magMouseTrackingChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magMouseTrackingComboBox GtkComboBox widget. The user has
           selected a different magnification mouse tracking style.
           Set the 'magMouseTrackingMode' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        mouseTrackingMode = widget.get_active_text()
        if mouseTrackingMode == self.magTrackingCenteredStr:
            mode = settings.MAG_TRACKING_MODE_CENTERED

        elif mouseTrackingMode == self.magTrackingPushStr:
            mode = settings.MAG_TRACKING_MODE_PUSH

        elif mouseTrackingMode == self.magTrackingProportionalStr:
            mode = settings.MAG_TRACKING_MODE_PROPORTIONAL

        elif mouseTrackingMode == self.magTrackingNoneStr:
            mode = settings.MAG_TRACKING_MODE_NONE

        else:
            mode = settings.MAG_TRACKING_MODE_CENTERED

        self.prefsDict["magMouseTrackingMode"] = mode
        mag.updateMouseTracking(mode)

    def magControlTrackingChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magControlTrackingComboBox GtkComboBox widget. The user has
           selected a different magnification control and menu item
           tracking style. Set the 'magControlTrackingMode' preference 
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        controlTrackingMode = widget.get_active_text()
        if controlTrackingMode == self.magTrackingCenteredStr:
            mode = settings.MAG_TRACKING_MODE_CENTERED

        elif controlTrackingMode == self.magTrackingPushStr:
            mode = settings.MAG_TRACKING_MODE_PUSH

        elif controlTrackingMode == self.magTrackingNoneStr:
            mode = settings.MAG_TRACKING_MODE_NONE

        else:
            mode = settings.MAG_TRACKING_MODE_PUSH

        self.prefsDict["magControlTrackingMode"] = mode
        mag.updateControlTracking(mode)

    def magTextTrackingChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magTextCursorTrackingComboBox GtkComboBox widget. The user has
           selected a different magnification text cursor tracking style.
           Set the 'magTextCursorTrackingMode' preference to the new value
           and grey out the edge margin widget unless the mode is "Push".

        Arguments:
        - widget: the component that generated the signal.
        """

        textCursorTrackingMode = widget.get_active_text()
        if textCursorTrackingMode == self.magTrackingCenteredStr:
            mode = settings.MAG_TRACKING_MODE_CENTERED

        elif textCursorTrackingMode == self.magTrackingPushStr:
            mode = settings.MAG_TRACKING_MODE_PUSH

        elif textCursorTrackingMode == self.magTrackingNoneStr:
            mode = settings.MAG_TRACKING_MODE_NONE

        else:
            mode = settings.MAG_TRACKING_MODE_PUSH

        self.prefsDict["magTextTrackingMode"] = mode
        self.get_widget("magEdgeMarginHBox").\
                set_sensitive(mode == settings.MAG_TRACKING_MODE_PUSH)

        mag.updateTextTracking(mode)

    def magEdgeMarginValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magEdgeMarginSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           edge margin spin button. Set the 'magEdgeMargin' preference 
           to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = widget.get_value_as_int()
        self.prefsDict["magEdgeMargin"] = value
        mag.updateEdgeMargin(value)

    def magPointerFocusChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magPointerFocusCheckButton GtkCheckButton widget. The user
           has [un]checked the pointer follows focus checkbox. Set the
           'magPointerFollowsFocus' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        enabled = widget.get_active()
        self.prefsDict["magPointerFollowsFocus"] = enabled
        if self.enableLiveUpdating and widget.is_focus():
            mag.updatePointerFollowsFocus(enabled)

    def magPointerZoomerChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magPointerZoomerCheckButton GtkCheckButton widget. The user
           has [un]checked the pointer follows zoomer checkbox. Set the
           'magPointerFollowsZoomer' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        enabled = widget.get_active()
        self.prefsDict["magPointerFollowsZoomer"] = enabled
        if self.enableLiveUpdating and widget.is_focus():
            mag.updatePointerFollowsZoomer(enabled)

    def magInvertColorsChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magCrossHairOnOffCheckButton GtkCheckButton widget.
           The user has [un]checked the magnification 'Invert Colors'
           checkbox. Set the 'enableMagZoomerColorInversion' preference
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = widget.get_active()
        if self.enableLiveUpdating and widget.is_focus():
            mag.setZoomerColorInversion(value)
        self.prefsDict["enableMagZoomerColorInversion"] = value

    def keyModifiedToggle(self, cell, path, model, col):
        """When the user changes a checkbox field (boolean field)"""

        model[path][col] = not model[path][col]
        return

    def editingKey(self, cell, editable, path, treeModel):
        """Starts user input of a Key for a selected key binding"""

        # Translators: this is a spoken prompt asking the user to press
        # a new key combination (e.g., Alt+Ctrl+g) to create a new
        # key bindings.
        #
        speech.speak(_("enter new key"))
        orca_state.capturingKeys = True
        editable.connect('key-press-event', self.kbKeyPressed)
        return

    def editingCanceledKey(self, editable):
        """Stops user input of a Key for a selected key binding"""

        orca_state.capturingKeys = False
        return

    def kbKeyPressed(self, editable, event):
        """Special handler for the key_pressed events when editing the
        keybindings.  This lets us control what gets inserted into the
        entry.
        """

        captured = orca_state.lastCapturedKey
        if not captured or captured.event_string in ["Return", "Escape"]:
            return False

        keyName = captured.event_string
        isOrcaModifier = captured.modifiers & settings.ORCA_MODIFIER_MASK
        if keyName in ["Delete", "BackSpace"] and not isOrcaModifier:
            editable.set_text("")
            # Translators: this is a spoken prompt letting the user know
            # Orca has deleted an existing key combination based upon
            # their input.
            #
            speech.speak(_("Key binding deleted. Press enter to confirm."))
            return True

        clickCount = orca_state.clickCount
        self.newBinding = keybindings.KeyBinding(keyName,
                                                 settings.defaultModifierMask,
                                                 captured.modifiers,
                                                 None,
                                                 clickCount)
        modifierNames = keybindings.getModifierNames(captured.modifiers)
        clickCount = self._clickCountToString(clickCount)
        newString = modifierNames + keyName + clickCount
        description = self.pendingKeyBindings.get(newString)
        if description is None \
           and self.kbindings.hasKeyBinding(self.newBinding, "keysNoMask"):
            handler = self.kbindings.getInputHandler(captured)
            if handler:
                description = handler.description

        if description:
            # Translators: this is a spoken prompt letting the user know
            # that the key combination (e.g., Ctrl+Alt+f) they just
            # entered has already been bound to another command.
            #
            speech.speak(_("The key entered is already bound to %s") % \
                         description)
        else:
            # Translators: this is a spoken prompt letting the user know Orca
            # know Orca has recorded a new key combination (e.g., Alt+Ctrl+g)
            # based upon their input.
            #
            speech.speak(_("Key captured: %s. Press enter to confirm.") % \
                         newString)
            editable.set_text(newString)

        return True
            
    def editedKey(self, cell, path, new_text, treeModel, 
                  modMask, modUsed, key, click_count, text):
        """The user changed the key for a Keybinding: update the model of
        the treeview.
        """

        orca_state.capturingKeys = False
        myiter = treeModel.get_iter_from_string(path)
        originalBinding = treeModel.get_value(myiter, text)
        modified = (originalBinding != new_text)

        try:
            string = self.newBinding.keysymstring
            mods = self.newBinding.modifiers
            clickCount = self.newBinding.click_count
        except:
            string = None
            mods = 0
            clickCount = 1

        treeModel.set(myiter,
                      modMask, settings.defaultModifierMask,
                      modUsed, mods,
                      key, string,
                      text, new_text,
                      click_count, clickCount,
                      MODIF, modified)
        speech.stop()
        if new_text:
            # Translators: this is a spoken prompt confirming the key
            # combination (e.g., Ctrl+Alt+f) the user just typed when
            # creating a new key binding.
            #
            message = _("The new key is: %s") % new_text
            description = treeModel.get_value(myiter, DESCRIP)
            self.pendingKeyBindings[new_text] = description
        else:
            # Translators: this is a spoken prompt confirming that an
            # existing key combination (e.g., Ctrl+Alt+f) that was
            # associated with a command has been deleted.
            #
            message = _("The keybinding has been removed.")

        if modified:
            speech.speak(message)
            self.pendingKeyBindings[originalBinding] = ""

        return

    def showMainWindowChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           showMainWindowCheckButton GtkCheckButton widget.
           The user has [un]checked the 'Show Orca main window'
           checkbox. Set the 'showMainWindow' preference
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["showMainWindow"] = widget.get_active()

    def confirmQuitChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           confirmQuitCheckButton GtkCheckButton widget.
           The user has [un]checked the 'Quit Orca without
           confirmation' checkbox. Set the 'quitOrcaNoConfirmation'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["quitOrcaNoConfirmation"] = widget.get_active()

    def presentToolTipsChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           presentToolTipsCheckButton GtkCheckButton widget.
           The user has [un]checked the 'Present ToolTips'
           checkbox. Set the 'presentToolTips'
           preference to the new value if the user can present tooltips.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["presentToolTips"] = widget.get_active() and \
                                            settings.canPresentToolTips

    def disableKeyGrabChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           disableKeyGrabCheckButton GtkCheckButton widget.
           The user has [un]checked the 'Disable gksu keyboard grab'
           checkbox. Set the gconf '/apps/gksu/disable-grab' resource
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.disableKeyGrabPref = widget.get_active()

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
            # Translators: this refers to the keyboard layout (desktop
            # or laptop).
            #
            if widget.get_label() == _("_Desktop"):
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

        model, oldIter = self.pronunciationView.get_selection().get_selected()
        thisIter = model.append()

        model.set(thisIter, ACTUAL, "", REPLACEMENT, "")
        noRows = model.iter_n_children(None)
        col = self.pronunciationView.get_column(0)
        self.pronunciationView.grab_focus()
        self.pronunciationView.set_cursor(noRows-1, col, True) 

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

    def textSelectAllButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        textSelectAllButton GtkButton widget. The user has clicked
        the Speak all button.  Check all the text attributes and
        then update the "enabledSpokenTextAttributes" and
        "enabledBrailledTextAttributes" preference strings.

        Arguments:
        - widget: the component that generated the signal.
        """

        self._setSpokenTextAttributes(self.getTextAttributesView,
                                settings.allTextAttributes, True)
        self._setBrailledTextAttributes(self.getTextAttributesView,
                                settings.allTextAttributes, True)
        self._updateTextDictEntry()

    def textUnselectAllButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        textUnselectAllButton GtkButton widget. The user has clicked
        the Speak none button. Uncheck all the text attributes and
        then update the "enabledSpokenTextAttributes" and
        "enabledBrailledTextAttributes" preference strings.

        Arguments:
        - widget: the component that generated the signal.
        """

        self._setSpokenTextAttributes(self.getTextAttributesView,
                                settings.allTextAttributes, False)
        self._setBrailledTextAttributes(self.getTextAttributesView,
                                settings.allTextAttributes, False)
        self._updateTextDictEntry()

    def textResetButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        textResetButton GtkButton widget. The user has clicked
        the Reset button. Reset all the text attributes to their
        initial state and then update the "enabledSpokenTextAttributes"
        and "enabledBrailledTextAttributes" preference strings.

        Arguments:
        - widget: the component that generated the signal.
        """

        self._setSpokenTextAttributes(self.getTextAttributesView,
                                settings.allTextAttributes, False)
        self._setSpokenTextAttributes(self.getTextAttributesView,
                                settings.enabledSpokenTextAttributes, True)
        self._setBrailledTextAttributes(self.getTextAttributesView,
                                settings.enabledBrailledTextAttributes, True)
        self._updateTextDictEntry()

    def textMoveToTopButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        textMoveToTopButton GtkButton widget. The user has clicked
        the Move to top button. Move the selected rows in the text
        attribute view to the very top of the list and then update
        the "enabledSpokenTextAttributes" and "enabledBrailledTextAttributes"
        preference strings.

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
        "enabledSpokenTextAttributes" and "enabledBrailledTextAttributes"
        preference strings.

        Arguments:
        - widget: the component that generated the signal.
        """

        textSelection = self.getTextAttributesView.get_selection()
        [model, paths] = textSelection.get_selected_rows()
        for path in paths:
            thisIter = model.get_iter(path)
            if path[0]:
                otherIter = model.iter_nth_child(None, path[0]-1)
                model.swap(thisIter, otherIter)
        self._updateTextDictEntry()

    def textMoveDownOneButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        textMoveDownOneButton GtkButton widget. The user has clicked
        the Move down one button. Move the selected rows in the text
        attribute view down one row in the list and then update the
        "enabledSpokenTextAttributes" and "enabledBrailledTextAttributes"
        preference strings.

        Arguments:
        - widget: the component that generated the signal.
        """

        textSelection = self.getTextAttributesView.get_selection()
        [model, paths] = textSelection.get_selected_rows()
        noRows = model.iter_n_children(None)
        for path in paths:
            thisIter = model.get_iter(path)
            if path[0] < noRows-1:
                otherIter = model.iter_next(thisIter)
                model.swap(thisIter, otherIter)
        self._updateTextDictEntry()

    def textMoveToBottomButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        textMoveToBottomButton GtkButton widget. The user has clicked
        the Move to bottom button. Move the selected rows in the text
        attribute view to the bottom of the list and then update the
        "enabledSpokenTextAttributes" and "enabledBrailledTextAttributes"
        preference strings.

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

        orca.helpForOrca()

    def restoreSettings(self):
        """Restore the settings we saved away when opening the preferences
           dialog."""
        # Restore the default rate/pitch/gain,
        # in case the user played with the sliders.
        #
        defaultVoice = settings.voices[settings.DEFAULT_VOICE]
        defaultVoice[acss.ACSS.GAIN] = self.savedGain
        defaultVoice[acss.ACSS.AVERAGE_PITCH] = self.savedPitch
        defaultVoice[acss.ACSS.RATE] =  self.savedRate

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

        self.restoreSettings()

        enable = self.get_widget("speechSupportCheckbutton").get_active()
        self.prefsDict["enableSpeech"] = enable

        if self.speechSystemsChoice:
            self.prefsDict["speechServerFactory"] = \
                self.speechSystemsChoice.__name__

        if self.speechServersChoice:
            self.prefsDict["speechServerInfo"] = \
                self.speechServersChoice.getInfo()

        if self.defaultVoice != None:
            self.prefsDict["voices"] = {
                settings.DEFAULT_VOICE   : acss.ACSS(self.defaultVoice),
                settings.UPPERCASE_VOICE : acss.ACSS(self.uppercaseVoice),
                settings.HYPERLINK_VOICE : acss.ACSS(self.hyperlinkVoice)
            }

        settings.setGKSUGrabDisabled(self.disableKeyGrabPref)

        try:
            status = settings.setOrcaAutostart(self.enableAutostart)
            self.get_widget("autostartOrcaCheckbutton").set_active(\
                settings.isOrcaAutostarted())
        except:
            # If we are pressing Apply or OK from an application preferences
            # dialog (rather than the general Orca preferences), then there
            # won't be a general pane, so we won't be able to adjust this
            # checkbox.
            #
            pass

        self.writeUserPreferences()

        orca.loadUserSettings()

        self._initSpeechState()

        self._populateKeyBindings()

    def cancelButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the cancelButton
           GtkButton widget. The user has clicked the Cancel button.
           Don't write out the preferences. Destroy the configuration window.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.windowClosed(widget)
        self.get_widget("orcaSetupWindow").destroy()

    def okButtonClicked(self, widget):
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

        self.applyButtonClicked(widget)
        self._cleanupSpeechServers()
        self.get_widget("orcaSetupWindow").destroy()

    def windowClosed(self, widget):
        """Signal handler for the "closed" signal for the orcaSetupWindow
           GtkWindow widget. This is effectively the same as pressing the
           cancel button, except the window is destroyed for us.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.restoreSettings()
        mag.finishLiveUpdating()
        self._cleanupSpeechServers()

    def windowDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the orcaSetupWindow
           GtkWindow widget. Reset orca_state.orcaOS to None, so that the 
           GUI can be rebuilt from the GtkBuilder file the next time the user
           wants to display the configuration GUI.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.keyBindView.set_model(None)
        self.getTextAttributesView.set_model(None)
        self.pronunciationView.set_model(None)
        self.keyBindView.set_headers_visible(False)
        self.getTextAttributesView.set_headers_visible(False)
        self.pronunciationView.set_headers_visible(False)
        self.keyBindView.hide_all()
        self.getTextAttributesView.hide_all()
        self.pronunciationView.hide_all()
        self.keyBindView.hide()
        self.getTextAttributesView.hide()
        self.pronunciationView.hide()
        mag.finishLiveUpdating()
        orca_state.orcaOS = None

    def getAdvancedMagDialog(self):
        """Return a handle to the Orca Preferences advanced magnification
        settings dialog.
        """

        return self.orcaMagAdvancedDialog

class OrcaAdvancedMagGUI(OrcaSetupGUI):

    def __init__(self, fileName, windowName, prefsDict = None):
        """Initialize the Orca configuration GUI.

        Arguments:
        - fileName: name of the GtkBuilder file.
        - windowName: name of the component to get from the GtkBuilder file.
        """

        OrcaSetupGUI.__init__(self, fileName, windowName)

        self.prefsDict = prefsDict
        self.enableLiveUpdating = settings.enableMagLiveUpdating

        # To make pylint happy.
        #
        self.savedSettings = None
        self.sourceDisplayModel = None
        self.targetDisplayModel = None

    def init(self):
        """Initialize the magnification Advanced Settings dialog GUI.
        Read the users current set of preferences and set the GUI state 
        to match. 
        """

        if not self.sourceDisplayModel:
            self.sourceDisplayModel = \
                self._initComboBox(self.get_widget("magSourceDisplayEntry"))
        if not self.targetDisplayModel:
            self.targetDisplayModel = \
                self._initComboBox(self.get_widget("magTargetDisplayEntry"))
        self._initGUIState()

    def _initGUIState(self):
        """Adjust the settings of the various components on the
        configuration GUI depending upon the users preferences.
        """

        liveUpdating = self.enableLiveUpdating
        self.enableLiveUpdating = False

        prefs = self.prefsDict

        # Get the smoothing preference and set the active value for the
        # smoothing combobox accordingly.
        #
        self.setSmoothingMode(prefs["magSmoothingMode"])

        # Get the Brightness RGB levels and set their spin button values
        # accordingly.
        #
        self.setRGBBrightnessValues(prefs["magBrightnessLevelRed"],
                                           prefs["magBrightnessLevelGreen"],
                                           prefs["magBrightnessLevelBlue"])

        # Get the Contrast RGB levels and set their spin button values
        # accordingly.
        #
        self.setRGBContrastValues(prefs["magContrastLevelRed"],
                                         prefs["magContrastLevelGreen"],
                                         prefs["magContrastLevelBlue"])

        # Get the color filtering mode preference and set the active value
        # for the color filtering combobox accordingly.
        #
        self.setColorFilteringMode(prefs["magColorFilteringMode"])

        # Get the magnification source and target displays.
        #
        display = gtk.gdk.display_get_default()
        nScreens = display.get_n_screens()
        sourceScreen = display.get_default_screen()

        self.sourceDisplayModel.clear()
        self.targetDisplayModel.clear()
        for screenNo in range(0, nScreens):
            screenName = ":0." + str(screenNo)
            self.sourceDisplayModel.append((screenNo, screenName))
            self.targetDisplayModel.append((screenNo, screenName))

        sourceDisplay = prefs["magSourceDisplay"]
        sourceComboBox = self.get_widget("magSourceDisplayEntry")
        if sourceComboBox.get_text_column() == -1:
            sourceComboBox.set_text_column(1)
        index = self.getComboBoxIndex(sourceComboBox, sourceDisplay, 1)
        model = sourceComboBox.get_model()
        displayIter = model.get_iter(index)
        if displayIter:
            value = model.get_value(displayIter, 1)
            sourceComboBox.get_child().set_text(value)

        targetDisplay = prefs["magTargetDisplay"]
        targetComboBox = self.get_widget("magTargetDisplayEntry")
        if targetComboBox.get_text_column() == -1:
            targetComboBox.set_text_column(1)
        index = self.getComboBoxIndex(targetComboBox, targetDisplay, 1)
        model = targetComboBox.get_model()
        displayIter = model.get_iter(index)
        if displayIter:
            value = model.get_value(displayIter, 1)
            targetComboBox.get_child().set_text(value)

        self.enableLiveUpdating = liveUpdating
        self.updateRGBBrightness()
        self.updateRGBContrast()

    def setSmoothingMode(self, smoothingMode):
        """Get the smoothing preference and set the active value for the
           smoothing combobox accordingly.

        Arguments:
        - smoothingMode: the smoothing mode.
        """

        if smoothingMode == settings.MAG_SMOOTHING_MODE_BILINEAR:
            # Translators: this is an algorithm for magnifying pixels
            # on the screen.
            #
            mode = _("Bilinear")
        elif smoothingMode == settings.MAG_SMOOTHING_MODE_NONE:
            # Translators: this is an algorithm for tracking the mouse
            # with the magnifier.  None means that Orca does nothing to
            # track the mouse.
            #
            mode = _("None")
        else:
            # Translators: this is an algorithm for magnifying pixels
            # on the screen.
            #
            mode = _("Bilinear")
        magSmoothingComboBox = self.get_widget("magSmoothingComboBox")
        self.populateComboBox(magSmoothingComboBox, [_("None"), _("Bilinear")])
        index = self.getComboBoxIndex(magSmoothingComboBox, mode)
        magSmoothingComboBox.set_active(index)

        if self.enableLiveUpdating:
            mag.setZoomerSmoothingType(smoothingMode)

    def magSmoothingChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magSmoothingComboBox GtkComboBox widget. The user has
           selected a different magnification smoothing style.
           Set the 'magSmoothingMode' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        smoothingMode = widget.get_active_text()
        # Translators: this is an algorithm for magnifying pixels
        # on the screen.
        #
        if smoothingMode ==  _("Bilinear"):
            mode = settings.MAG_SMOOTHING_MODE_BILINEAR
        elif smoothingMode == _("None"):
            mode = settings.MAG_SMOOTHING_MODE_NONE
        else:
            mode = settings.MAG_SMOOTHING_MODE_BILINEAR

        if self.enableLiveUpdating:
            mag.setZoomerSmoothingType(mode)

        self.prefsDict["magSmoothingMode"] = mode

    def setRGBBrightnessValues(self, red, green, blue):
        """Set the spin button values for the Brightness RGB levels.

        Arguments:
        - red:   the red brightness value.
        - green: the green brightness value.
        - blue:  the blue brightness value.
        """

        self.get_widget("magBrightnessRedSpinButton").set_value(red)
        self.get_widget("magBrightnessGreenSpinButton").set_value(green)
        self.get_widget("magBrightnessBlueSpinButton").set_value(blue)

    def updateRGBBrightness(self):
        """Gets the RGB brightness spin button values and live-updates
        the brightness level in gnome-mag.
        """

        if not self.enableLiveUpdating:
            return

        r = self.get_widget("magBrightnessRedSpinButton").get_value()
        g = self.get_widget("magBrightnessGreenSpinButton").get_value()
        b = self.get_widget("magBrightnessBlueSpinButton").get_value()

        brightness = self.prefsDict["magBrightnessLevel"]
        r = round(r + brightness, 2)
        g = round(g + brightness, 2)
        b = round(b + brightness, 2)

        mag.setZoomerBrightness(r, g, b)

    def magBrightnessRedValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magBrightnessRedSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           brightness Red spin button. Set the 'magBrightnessLevelRed'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = round(widget.get_value(), 2)
        self.prefsDict["magBrightnessLevelRed"] = value
        self.updateRGBBrightness()

    def magBrightnessGreenValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magBrightnessGreenSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           brightness Green spin button. Set the 'magBrightnessLevelGreen'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = round(widget.get_value(), 2)
        self.prefsDict["magBrightnessLevelGreen"] = value
        self.updateRGBBrightness()

    def magBrightnessBlueValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magBrightnessBlueSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           brightness Blue spin button. Set the 'magBrightnessLevelBlue'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = round(widget.get_value(), 2)
        self.prefsDict["magBrightnessLevelBlue"] = value
        self.updateRGBBrightness()

    def setRGBContrastValues(self, red, green, blue):
        """Set the spin button values for the Contrast RGB levels.

        Arguments:
        - red:   the red contrast value.
        - green: the green contrast value.
        - blue:  the blue contrast value.
        """

        self.get_widget("magContrastRedSpinButton").set_value(red)
        self.get_widget("magContrastGreenSpinButton").set_value(green)
        self.get_widget("magContrastBlueSpinButton").set_value(blue)

    def updateRGBContrast(self):
        """Gets the RGB Contrast spin button values and live-updates
        the contrast level in gnome-mag.
        """

        if not self.enableLiveUpdating:
            return

        r = self.get_widget("magContrastRedSpinButton").get_value()
        g = self.get_widget("magContrastGreenSpinButton").get_value()
        b = self.get_widget("magContrastBlueSpinButton").get_value()
        contrast = self.prefsDict["magContrastLevel"]

        r = round(r + contrast, 2)
        g = round(g + contrast, 2)
        b = round(b + contrast, 2)

        mag.setZoomerContrast(r, g, b)

    def magContrastRedValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magContrastRedSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           contrast Red spin button. Set the 'magContrastLevelRed'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = round(widget.get_value(), 2)
        self.prefsDict["magContrastLevelRed"] = value
        self.updateRGBContrast()

    def magContrastGreenValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magContrastGreenSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           contrast Green spin button. Set the 'magContrastLevelGreen'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = round(widget.get_value(), 2)
        self.prefsDict["magContrastLevelGreen"] = value
        self.updateRGBContrast()

    def magContrastBlueValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magContrastBlueSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           contrast Blue spin button. Set the 'magContrastLevelBlue'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        value = round(widget.get_value(), 2)
        self.prefsDict["magContrastLevelBlue"] = value
        self.updateRGBContrast()

    def setColorFilteringMode(self, mode):
        """Set the active value for the color filtering mode combobox
           preference.

        Arguments:
        - mode: the color filtering mode.
        """

        if mode == settings.MAG_COLOR_FILTERING_MODE_NONE:
            filteringMode = _("None")

        elif mode == settings.MAG_COLOR_FILTERING_MODE_SATURATE_RED:
            # Translators: this refers to a color filter for people with
            # color blindness. It will maximize the red value for all
            # pixels on the screen. For example, an RGB value of
            # (75, 100, 125) would be become (255, 100, 125).
            #
            filteringMode = _("Saturate red")

        elif mode == settings.MAG_COLOR_FILTERING_MODE_SATURATE_GREEN:
            # Translators: this refers to a color filter for people with
            # color blindness. It will maximize the green value for all
            # pixels on the screen.  For example, an RGB value of
            # (75, 100, 125) would become (75, 255, 125).
            #
            filteringMode = _("Saturate green")

        elif mode == settings.MAG_COLOR_FILTERING_MODE_SATURATE_BLUE:
            # Translators: this refers to a color filter for people with
            # color blindness. It will maximize the blue value for all
            # pixels on the screen. For example, an RGB value of
            # (75, 100, 125) would become (75, 100, 255).
            #
            filteringMode = _("Saturate blue")

        elif mode == settings.MAG_COLOR_FILTERING_MODE_DESATURATE_RED:
            # Translators: this refers to a color filter for people with
            # color blindness. It will eliminate the red value for all
            # pixels on the screen. For example, an RGB value of
            # (75, 100, 125) would be become (0, 100, 125).
            #
            filteringMode = _("Desaturate red")

        elif mode == settings.MAG_COLOR_FILTERING_MODE_DESATURATE_GREEN:
            # Translators: this refers to a color filter for people with
            # color blindness. It will eliminate the green value for all
            # pixels on the screen. For example, an RGB value of
            # (75, 100, 125) would become (75, 0, 125).
            #
            filteringMode = _("Desaturate green")

        elif mode == settings.MAG_COLOR_FILTERING_MODE_DESATURATE_BLUE:
            # Translators: this refers to a color filter for people with
            # color blindness. It will eliminate the blue value for all
            # pixels on the screen. For example, an RGB value of
            # (75, 100, 125) would become (75, 100, 0).
            #
            filteringMode = _("Desaturate blue")

        elif mode == settings.MAG_COLOR_FILTERING_MODE_POSITIVE_HUE_SHIFT:
            # Translators: this refers to a color filter for people with
            # color blindness. It shifts RGB values to the right. For
            # example, an RGB value of (75, 100, 125) would become
            # (125, 75, 100).
            #
            filteringMode = _("Positive hue shift")

        elif mode == settings.MAG_COLOR_FILTERING_MODE_NEGATIVE_HUE_SHIFT:
            # Translators: this refers to a color filter for people with
            # color blindness. It shifts RGB values to the left. For
            # example, an RGB value of (75, 100, 125) would become
            # (100, 125, 75).
            #
            filteringMode = _("Negative hue shift")

        else:
            filteringMode = _("None")

        comboBox = self.get_widget("magColorFilteringComboBox")
        types = [_("None"),
                 _("Saturate red"),
                 _("Saturate green"),
                 _("Saturate blue"),
                 _("Desaturate red"),
                 _("Desaturate blue"),
                 _("Positive hue shift"),
                 _("Negative hue shift")]
        self.populateComboBox(comboBox, types)
        index = self.getComboBoxIndex(comboBox, filteringMode)
        comboBox.set_active(index)
        enable = mag.isFilteringCapable()
        self.get_widget("magColorFilteringHbox").set_sensitive(enable)

        if enable and self.enableLiveUpdating:
            mag.setZoomerColorFilter(mode)

    def magColorFilteringChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magColorFilteringComboBox GtkComboBox widget. The user has
           selected a different magnification color filtering mode.
           Set the 'magColorFilteringMode' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        filteringMode = widget.get_active_text()
        if filteringMode ==  _("None"):
            mode = settings.MAG_COLOR_FILTERING_MODE_NONE

        # Translators: this refers to a color filter for people with
        # color blindness. It will maximize the red value for all
        # pixels on the screen. For example, an RGB value of
        # (75, 100, 125) would be become (255, 100, 125).
        #
        elif filteringMode == _("Saturate red"):
            mode = settings.MAG_COLOR_FILTERING_MODE_SATURATE_RED

        # Translators: this refers to a color filter for people with
        # color blindness. It will maximize the green value for all
        # pixels on the screen.  For example, an RGB value of
        # (75, 100, 125) would become (75, 255, 125).
        #
        elif filteringMode == _("Saturate green"):
            mode = settings.MAG_COLOR_FILTERING_MODE_SATURATE_GREEN

        # Translators: this refers to a color filter for people with
        # color blindness. It will maximize the blue value for all
        # pixels on the screen. For example, an RGB value of
        # (75, 100, 125) would become (75, 100, 255).
        #
        elif filteringMode == _("Saturate blue"):
            mode = settings.MAG_COLOR_FILTERING_MODE_SATURATE_BLUE

        # Translators: this refers to a color filter for people with
        # color blindness. It will eliminate the red value for all
        # pixels on the screen. For example, an RGB value of
        # (75, 100, 125) would be become (0, 100, 125).
        #
        elif filteringMode == _("Desaturate red"):
            mode = settings.MAG_COLOR_FILTERING_MODE_DESATURATE_RED

        # Translators: this refers to a color filter for people with
        # color blindness. It will eliminate the green value for all
        # pixels on the screen. For example, an RGB value of
        # (75, 100, 125) would become (75, 0, 125).
        #
        elif filteringMode == _("Desaturate green"):
            mode = settings.MAG_COLOR_FILTERING_MODE_DESATURATE_GREEN

        # Translators: this refers to a color filter for people with
        # color blindness. It will eliminate the blue value for all
        # pixels on the screen. For example, an RGB value of
        # (75, 100, 125) would become (75, 100, 0).
        #
        elif filteringMode == _("Desaturate blue"):
            mode = settings.MAG_COLOR_FILTERING_MODE_DESATURATE_BLUE

        # Translators: this refers to a color filter for people with
        # color blindness. It shifts RGB values to the right. For
        # example, an RGB value of (75, 100, 125) would become
        # (125, 75, 100).
        #
        elif filteringMode == _("Positive hue shift"):
            mode = settings.MAG_COLOR_FILTERING_MODE_POSITIVE_HUE_SHIFT

        # Translators: this refers to a color filter for people with
        # color blindness. It shifts RGB values to the left. For
        # example, an RGB value of (75, 100, 125) would become
        # (100, 125, 75).
        #
        elif filteringMode == _("Negative hue shift"):
            mode = settings.MAG_COLOR_FILTERING_MODE_NEGATIVE_HUE_SHIFT

        else:
            mode = settings.MAG_COLOR_FILTERING_MODE_NONE

        if self.enableLiveUpdating:
            mag.setZoomerColorFilter(mode)

        self.prefsDict["magColorFilteringMode"] = mode

    def magSourceDisplayChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magSourceDisplayDisplayEntry GtkEntry widget.
           The user has changed the value of the magnification source
           display. Set the 'magSourceDisplay' preference
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        model = widget.get_model()
        displayIter = widget.get_active_iter()
        if displayIter:
            value = model.get_value(displayIter, 1)
            widget.get_child().set_text(value)
        else:
            value = widget.get_child().get_text()
            index = self.getComboBoxIndex(widget, value, 1)
            firstIter = model.get_iter_first()
            if firstIter:
                firstValue = model.get_value(firstIter, 1)
                if index or (value == firstValue):
                    widget.set_active(index)

        self.prefsDict["magSourceDisplay"] = value

    def magTargetDisplayChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magTargetDisplayEntry GtkEntry widget.
           The user has changed the value of the magnification target
           display. Set the 'magTargetDisplay' preference
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        model = widget.get_model()
        displayIter = widget.get_active_iter()
        if displayIter:
            value = model.get_value(displayIter, 1)
            widget.get_child().set_text(value)
        else:
            value = widget.get_child().get_text()
            index = self.getComboBoxIndex(widget, value, 1)
            firstIter = model.get_iter_first()
            if firstIter:
                firstValue = model.get_value(firstIter, 1)
                if index or (value == firstValue):
                    widget.set_active(index)

        self.prefsDict["magTargetDisplay"] = value
        if orca_state.orcaOS:
            self._setZoomerSpinButtons()

    def restoreAdvancedSettings(self):
        """Restores the previously saved values of the settings on the 
        magnification advanced settings dialog.
        """

        self.prefsDict["magSmoothingMode"] = \
                             self.savedSettings["magSmoothingMode"]
        self.prefsDict["magBrightnessLevelRed"] = \
                             self.savedSettings["magBrightnessLevelRed"]
        self.prefsDict["magBrightnessLevelGreen"] = \
                             self.savedSettings["magBrightnessLevelGreen"]
        self.prefsDict["magBrightnessLevelBlue"] = \
                             self.savedSettings["magBrightnessLevelBlue"]
        self.prefsDict["magContrastLevelRed"] = \
                             self.savedSettings["magContrastLevelRed"]
        self.prefsDict["magContrastLevelGreen"] = \
                             self.savedSettings["magContrastLevelGreen"]
        self.prefsDict["magContrastLevelBlue"] = \
                             self.savedSettings["magContrastLevelBlue"]
        self.prefsDict["magColorFilteringMode"] = \
                             self.savedSettings["magColorFilteringMode"]
        self.prefsDict["magSourceDisplay"] = \
                             self.savedSettings["magSourceDisplay"]
        self.prefsDict["magTargetDisplay"] = \
                             self.savedSettings["magTargetDisplay"]

    def saveAdvancedSettings(self, prefsDict):
        """Save the current values of the settings on the magnification
        advanced settings dialog.

        Arguments:
        - prefsDict: the preferences dictionary containing the current state.
        """

        self.savedSettings = {}
        self.savedSettings["magSmoothingMode"] = \
                                         prefsDict["magSmoothingMode"]
        self.savedSettings["magBrightnessLevelRed"] = \
                                         prefsDict["magBrightnessLevelRed"]
        self.savedSettings["magBrightnessLevelGreen"] = \
                                         prefsDict["magBrightnessLevelGreen"]
        self.savedSettings["magBrightnessLevelBlue"] = \
                                         prefsDict["magBrightnessLevelBlue"]
        self.savedSettings["magContrastLevelRed"] = \
                                         prefsDict["magContrastLevelRed"]
        self.savedSettings["magContrastLevelGreen"] = \
                                         prefsDict["magContrastLevelGreen"]
        self.savedSettings["magContrastLevelBlue"] = \
                                         prefsDict["magContrastLevelBlue"]
        self.savedSettings["magColorFilteringMode"] = \
                                         prefsDict["magColorFilteringMode"]
        self.savedSettings["magSourceDisplay"] = \
                                         prefsDict["magSourceDisplay"]
        self.savedSettings["magTargetDisplay"] = \
                                         prefsDict["magTargetDisplay"]

    def magAdvancedCancelButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
           magAdvancedCancelButton GtkButton widget. The user has clicked
           the Cancel button. We restore the preferences for the settings
           on the Advanced Settings dialog, back to what they we when it
           was initially displayed and hide it.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.restoreAdvancedSettings()
        self.init()
        self.setSmoothingMode(self.prefsDict["magSmoothingMode"])
        self.setColorFilteringMode(self.prefsDict["magColorFilteringMode"])
        liveUpdating = self.enableLiveUpdating
        self.enableLiveUpdating = False
        self.updateRGBBrightness()
        self.updateRGBContrast()
        self.enableLiveUpdating = liveUpdating
        orca_state.advancedMagDialog.hide()

    def magAdvancedOkButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the magAdvancedOKButton
           GtkButton widget. The user has clicked the OK button.  We don't
           want to write out any preferences until the main window's apply
           or OK button has been clicked. Just hide the advanced window.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca_state.advancedMagDialog.hide()

    def magAdvancedDialogDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the
        orcaMagAdvancedDialog GtkWindow widget. Instead of destroying
        the dialog, rebuild it, reinitialize it and hide it.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.restoreAdvancedSettings()
        orca_state.advancedMag = OrcaAdvancedMagGUI(orca_state.prefsUIFile,
                                   "orcaMagAdvancedDialog", self.prefsDict)
        orca_state.advancedMag.init()
        orca_state.advancedMagDialog = \
                                orca_state.advancedMag.getAdvancedMagDialog()

    def magAdvancedDialogKeyPressed(self, widget, event):
        """Signal handler for the "key_press" signal for the
        orcaMagAdvancedDialog GtkWindow widget. If the user has pressed the
        Escape key, then just hide the window.

        Arguments:
        - widget: the component that generated the signal.
        - event: the event for the key that the user pressed.
        """

        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            if orca_state.lastInputEvent.event_string == "Escape":
                self.restoreAdvancedSettings()
                self.init()
                self.setSmoothingMode(self.prefsDict["magSmoothingMode"])
                self.setColorFilteringMode(\
                    self.prefsDict["magColorFilteringMode"])
                liveUpdating = self.enableLiveUpdating
                self.enableLiveUpdating = False
                self.updateRGBBrightness()
                self.updateRGBContrast()
                self.enableLiveUpdating = liveUpdating
                orca_state.advancedMagDialog.hide()

        return False

class WarningDialogGUI(orca_gtkbuilder.GtkBuilderWrapper):

    def getPrefsWarningDialog(self):
        """Return a handle to the Orca Preferences warning dialog.
        """

        return self.orcaPrefsWarningDialog

    def orcaPrefsWarningDialogDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the 
        orcaPrefsWarningDialog GtkWindow widget. Reset orca_state.orcaWD
        to None, so that the GUI can be rebuilt from the GtkBuilder file the
        next time that this warning dialog has to be displayed.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca_state.orcaWD = None

    def orcaPrefsWarningDialogOKButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the
        orcaPrefsWarningDialogOKButton GtkButton widget. The user has clicked
        the OK button in the Orca Application Preferences warning dialog.
        This dialog informs the user that they already have an instance
        of an Orca preferences dialog open, and that they will need to 
        close it before opening a new one.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.orcaPrefsWarningDialog.destroy()

def showPreferencesUI():
    if not orca_state.appOS and not orca_state.orcaOS:
        # Translators: Orca Preferences is the configuration GUI for Orca.
        #
        line = _("Starting Orca Preferences.")
        braille.displayMessage(line)
        speech.speak(line)

        prefsDict = orca_prefs.readPreferences()
        orca_state.prefsUIFile = \
            os.path.join(platform.prefix,
                         platform.datadirname,
                         platform.package,
                         "ui",
                         "orca-setup.ui")
        orca_state.advancedMagUIFile = \
            os.path.join(platform.prefix,
                         platform.datadirname,
                         platform.package,
                         "ui",
                         "orca-advanced-magnification.ui")
        orca_state.advancedMag = \
            OrcaAdvancedMagGUI(orca_state.advancedMagUIFile,
                               "orcaMagAdvancedDialog", prefsDict)
        orca_state.advancedMag.init()
        orca_state.advancedMagDialog = \
                              orca_state.advancedMag.getAdvancedMagDialog()

        orca_state.orcaOS = OrcaSetupGUI(orca_state.prefsUIFile,
                                         "orcaSetupWindow", prefsDict)
        orca_state.orcaOS.init()
    else:
        if not orca_state.orcaWD:
            orca_state.orcaWarningDialogUIFile = \
                os.path.join(platform.prefix,
                             platform.datadirname,
                             platform.package,
                             "ui",
                             "orca-preferences-warning.ui")
            orca_state.orcaWD = \
                WarningDialogGUI(orca_state.orcaWarningDialogUIFile,
                                 "orcaPrefsWarningDialog")
            warningDialog = orca_state.orcaWD.getPrefsWarningDialog()
            warningDialog.realize()
            warningDialog.show()
        return

    orca_state.orcaOS.showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showPreferencesUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
