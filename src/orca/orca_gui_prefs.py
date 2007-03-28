# Orca
#
# Copyright 2006-2007 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# TODO:
#
# - Improve reclaimation of "old" speech servers in _setupSpeechServers().
# - Implement the Help button callback.

"""Displays a GUI for the user to set Orca preferences."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import os
import sys
import debug
import gettext
import gtk
import gtk.glade
import gobject
import pango   # for ellipsize property constants of CellRendererText
import locale

import acss
import orca
import orca_glade
import orca_prefs
import orca_state
import platform
import settings
import default    # for the default keyBindings
import input_event
import keybindings
import braille
import speech
import speechserver

from orca_i18n import _  # for gettext support

OS = None

(HANDLER, DESCRIP, MOD_MASK1, MOD_USED1, KEY1, TEXT1, MOD_MASK2, MOD_USED2, KEY2, TEXT2, MODIF, EDITABLE) = range(12)


class orcaSetupGUI(orca_glade.GladeWrapper):

    def _init(self):
        """Initialize the Orca configuration GUI. Read the users current
        set of preferences and set the GUI state to match. Setup speech
        support and populate the combo box lists on the Speech Tab pane
        accordingly.
        """

        self.prefsDict = orca_prefs.readPreferences()

        # ***** Key Bindings treeview initialization *****

        self.keyBindView = self.widgets.get_widget("keyBindingsTreeview")
        self.keyBindingsModel = gtk.TreeStore(
            gobject.TYPE_STRING,  # Handler name
            gobject.TYPE_STRING,  # Human Readable Description
            gobject.TYPE_STRING,  # Modifier mask 1
            gobject.TYPE_STRING,  # Used Modifiers 1
            gobject.TYPE_STRING,  # Modifier key name 1
            gobject.TYPE_STRING,  # Text of the Key Binding Shown 1
            gobject.TYPE_STRING,  # Modifier mask 2
            gobject.TYPE_STRING,  # Used Modifiers 2
            gobject.TYPE_STRING,  # Modifier key name 2
            gobject.TYPE_STRING,  # Text of the Key Binding Shown 2
            gobject.TYPE_BOOLEAN, # Key Modified by User
            gobject.TYPE_BOOLEAN) # Row with fields editable or not
        self.keyBindView.set_model(self.keyBindingsModel)
        self.keyBindView.set_headers_visible(True)

        # Treeview Column Implementation:
        #      (HANDLER,    DESCRIP,
        #       MOD_MASK1,  MOD_USED1,  KEY1,   TEXT1,
        #       MOD_MASK2,  MOD_USED2,  KEY2,   TEXT2,
        #       MODIF,      EDITABLE)

        # HANDLER
        #
        column = gtk.TreeViewColumn(_("Handler"),
                                    gtk.CellRendererText(),
                                    text=HANDLER)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(HANDLER)
        self.keyBindView.append_column(column)

        # DESCRIP
        #
        rendererText = gtk.CellRendererText()
        rendererText.set_property("ellipsize", pango.ELLIPSIZE_END)
        column = gtk.TreeViewColumn(_("Function"), rendererText, text=DESCRIP)
        column.set_resizable(True)
        column.set_min_width(380)
        column.set_sort_column_id(DESCRIP)
        self.keyBindView.append_column(column)

        # MOD_MASK1
        #
        column = gtk.TreeViewColumn(_("Mod.Mask 1"),
                                    gtk.CellRendererText(),
                                    text=MOD_MASK1)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MOD_MASK1)
        self.keyBindView.append_column(column)

        # MOD_USED1
        #
        column = gtk.TreeViewColumn(_("Use Mod.1"),
                                    gtk.CellRendererText(),
                                    text=MOD_USED1)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MOD_USED1)
        self.keyBindView.append_column(column)

        # KEY1
        #
        column = gtk.TreeViewColumn(_("Key1"),
                                    gtk.CellRendererText(),
                                    text=KEY1)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(KEY1)
        self.keyBindView.append_column(column)

        # TEXT1
        #
        rendererText = gtk.CellRendererText()
        rendererText.connect("editing-started",
                             self.editingKey,
                             self.keyBindingsModel)
        rendererText.connect('edited',
                             self.editedKey,
                             self.keyBindingsModel,
                             MOD_MASK1, MOD_USED1, KEY1, TEXT1)
        column = gtk.TreeViewColumn(_("Key Binding"),
                                    rendererText,
                                    text=TEXT1,
                                    editable=EDITABLE)
        column.set_resizable(True)
        column.set_sort_column_id(TEXT1)
        self.keyBindView.append_column(column)

        # MOD_MASK2
        #
        column = gtk.TreeViewColumn(_("Mod.Mask 2"),
                                    gtk.CellRendererText(),
                                    text=MOD_MASK2)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MOD_MASK2)
        self.keyBindView.append_column(column)

        # MOD_USED2
        #
        column = gtk.TreeViewColumn(_("Use Mod.2"),
                                    gtk.CellRendererText(),
                                    text=MOD_USED2)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MOD_USED2)
        self.keyBindView.append_column(column)

        # KEY2
        #
        column = gtk.TreeViewColumn(_("Key2"), rendererText, text=KEY2)
        column.set_resizable(True)
        column.set_visible(False)
        column.set_sort_column_id(KEY2)
        self.keyBindView.append_column(column)

        # TEXT2
        #
        rendererText = gtk.CellRendererText()
        rendererText.connect("editing-started",
                             self.editingKey,
                             self.keyBindingsModel)
        rendererText.connect('edited',
                             self.editedKey,
                             self.keyBindingsModel,
                             MOD_MASK2, MOD_USED2, KEY2, TEXT2)
        column = gtk.TreeViewColumn(_("Alternate"),
                                    rendererText,
                                    text=TEXT2,
                                    editable=EDITABLE)
        column.set_resizable(True)
        column.set_sort_column_id(TEXT2)
        self.keyBindView.append_column(column)

        # MODIF
        #
        rendererToggle = gtk.CellRendererToggle()
        rendererToggle.connect('toggled',
                               self.keyModifiedToggle,
                               self.keyBindingsModel,
                               MODIF)
        column = gtk.TreeViewColumn(_("Modified"),
                                    rendererToggle,
                                    active=MODIF,
                                    activatable=EDITABLE)
        #column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(MODIF)
        self.keyBindView.append_column(column)

        # EDITABLE
        #
        rendererToggle = gtk.CellRendererToggle()
        rendererToggle.set_property('activatable',False)
        column = gtk.TreeViewColumn(_("Modified"),
                                    rendererToggle,
                                    active=EDITABLE)
        column.set_visible(False)
        column.set_resizable(True)
        column.set_sort_column_id(EDITABLE)
        self.keyBindView.append_column(column)

        # Populates the treeview with all the keybindings:
        #
        self._populateKeyBindings()

        self.keyBindView.show()

        self.window = self.widgets.get_widget("orcaSetupWindow")
        self.window.resize(790,580);

        self._setKeyEchoItems()

        self.speechSystemsModel  = self._initComboBox(self.speechSystems)
        self.speechServersModel  = self._initComboBox(self.speechServers)
        self.speechFamiliesModel = self._initComboBox(self.speechFamilies)
        self._initSpeechState()

        self._initGUIState()

    def _getACSSForVoiceType(self, voiceType):
        """Return the ACSS value for the the given voice type.

        Arguments:
        - voiceType: the voice type ("Default", "Uppercase" or "Hyperlink",
        where the string is localized).

        Returns the voice dictionary for the given voice type.
        """

        if voiceType == _("Default"):
            voiceACSS = self.defaultVoice
        elif voiceType == _("Uppercase"):
            voiceACSS = self.uppercaseVoice
        elif voiceType == _("Hyperlink"):
            voiceACSS = self.hyperlinkVoice
        else:
            voiceACSS = self.defaultVoice

        return voiceACSS

    def _getKeyValueForVoiceType(self, voiceType, key, useDefault=True):
        """Look for the value of the given key in the voice dictionary
           for the given voice type.

        Arguments:
        - voiceType: the voice type ("Default", "Uppercase" or "Hyperlink").
        - key: the key to look for in the voice dictionary.
        - useDefault: if True, and the key isn't found for the given voice
                      type, the look for it in the default voice dictionary
                      as well.

        Returns the value of the given key, or None if it's not set.
        """

        if voiceType == _("Default"):
            voice = self.defaultVoice
        elif voiceType == _("Uppercase"):
            voice = self.uppercaseVoice
            if not voice.has_key(key):
                if not useDefault:
                    return None
                voice = self.defaultVoice
        elif voiceType == _("Hyperlink"):
            voice = self.hyperlinkVoice
            if not voice.has_key(key):
                if not useDefault:
                    return None
                voice = self.defaultVoice
        else:
            voice = self.defaultVoice

        if voice.has_key(key):
            return voice[key]
        else:
            return None

    def _getFamilyNameForVoiceType(self, voiceType):
        """Gets the name of the voice family for the given voice type.

        Arguments:
        - voiceType: the voice type ("Default", "Uppercase" or "Hyperlink").

        Returns the name of the voice family for the given voice type,
        or None if not set.
        """

        familyName = None
        family = self._getKeyValueForVoiceType(voiceType, acss.ACSS.FAMILY)

        if family and family.has_key(speechserver.VoiceFamily.NAME):
            familyName = family[speechserver.VoiceFamily.NAME]

        return familyName

    def _setFamilyNameForVoiceType(self, voiceType, name, language):
        """Sets the name of the voice family for the given voice type.

        Arguments:
        - voiceType: the voice type ("Default", "Uppercase" or "Hyperlink").
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
            voiceACSS[acss.ACSS.FAMILY][speechserver.VoiceFamily.LOCALE] = language

        #voiceACSS = self._getACSSForVoiceType(voiceType)
        #settings.voices[voiceType] = voiceACSS

    def _getRateForVoiceType(self, voiceType):
        """Gets the speaking rate value for the given voice type.

        Arguments:
        - voiceType: the voice type ("Default", "Uppercase" or "Hyperlink").

        Returns the rate value for the given voice type, or None if
        not set.
        """

        return self._getKeyValueForVoiceType(voiceType, acss.ACSS.RATE)

    def _setRateForVoiceType(self, voiceType, value):
        """Sets the speaking rate value for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).
        - value: the rate value to set.
        """

        voiceACSS = self._getACSSForVoiceType(voiceType)
        voiceACSS[acss.ACSS.RATE] = value
        #settings.voices[voiceType] = voiceACSS

    def _getPitchForVoiceType(self, voiceType):
        """Gets the pitch value for the given voice type.

        Arguments:
        - voiceType: the voice type ("Default", "Uppercase" or "Hyperlink").

        Returns the pitch value for the given voice type, or None if
        not set.
        """

        return self._getKeyValueForVoiceType(voiceType,
                                             acss.ACSS.AVERAGE_PITCH)

    def _setPitchForVoiceType(self, voiceType, value):
        """Sets the pitch value for the given voice type.

        Arguments:
        - voiceType: the voice type ("Default", "Uppercase" or "Hyperlink").
        - value: the pitch value to set.
        """

        voiceACSS = self._getACSSForVoiceType(voiceType)
        voiceACSS[acss.ACSS.AVERAGE_PITCH] = value
        #settings.voices[voiceType] = voiceACSS

    def _getVolumeForVoiceType(self, voiceType):
        """Gets the volume (gain) value for the given voice type.

        Arguments:
        - voiceType: the voice type ("Default", "Uppercase" or "Hyperlink").

        Returns the volume (gain) value for the given voice type, or
        None if not set.
        """

        return self._getKeyValueForVoiceType(voiceType, acss.ACSS.GAIN)

    def _setVolumeForVoiceType(self, voiceType, value):
        """Sets the volume (gain) value for the given voice type.

        Arguments:
        - voiceType: the voice type ("Default", "Uppercase" or "Hyperlink").
        - value: the volume (gain) value to set.
        """

        voiceACSS = self._getACSSForVoiceType(voiceType)
        voiceACSS[acss.ACSS.GAIN] = value
        #settings.voices[voiceType] = voiceACSS

    def _setVoiceSettingsForVoiceType(self, voiceType):
        """Sets the family, rate, pitch and volume GUI components based
        on the given voice type.

        Arguments:
        - voiceType: the voice type ("Default", "Uppercase" or "Hyperlink").
        """

        familyName = self._getFamilyNameForVoiceType(voiceType)
        self._setSpeechFamiliesChoice(familyName)

        rate = self._getRateForVoiceType(voiceType)
        if rate:
            self.rateScale.set_value(rate)

        pitch = self._getPitchForVoiceType(voiceType)
        if pitch:
            self.pitchScale.set_value(pitch)

        volume = self._getVolumeForVoiceType(voiceType)
        if volume:
            self.volumeScale.set_value(volume)

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
                self.speechFamilies.set_active(i)
                self.speechFamiliesChoice = self.speechFamiliesChoices[i]
                valueSet = True
                break
            i += 1

        if not valueSet:
            debug.println(debug.LEVEL_FINEST,
                          "Could not find speech family match for %s" \
                          % familyName)
            self.speechFamilies.set_active(0)
            self.speechFamiliesChoice = self.speechFamiliesChoices[0]

    def _setupFamilies(self):
        """Gets the list of voice families for the current speech server.
        If there aren't any families, set the 'enableSpeech' to False and
        return, otherwise get the information associated with each voice
        family and add an entry for it to the families GtkComboBox list.
        """

        self.speechFamiliesModel.clear()
        families = self.speechServersChoice.getVoiceFamilies()
        self.speechFamiliesChoices = []
        if len(families) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_FINEST)
            self.prefsDict["enableSpeech"] = False
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
        self.voiceTypes.set_active(0)
        voiceType = self.voiceTypes.get_active_text()
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
            serverInfo = speech._speechserver.getInfo()

        valueSet = False
        i = 0
        for server in self.speechServersChoices:
            if serverInfo == server.getInfo():
                self.speechServers.set_active(i)
                self.speechServersChoice = server
                valueSet = True
                break
            i += 1

        if not valueSet:
            debug.println(debug.LEVEL_FINEST,
                          "Could not find speech server match for %s" \
                          %  repr(serverInfo))
            self.speechServers.set_active(0)
            self.speechServersChoice = self.speechServersChoices[0]

        self._setupFamilies()

    def _setupSpeechServers(self):
        """Gets the list of speech servers for the current speech factory.
        If there aren't any servers, set the 'enableSpeech' to False and
        return, otherwise get the information associated with each speech
        server and add an entry for it to the speechServers GtkComboBox list.
        Set the current choice to be the first item.
        """

        self.speechServersModel.clear()
        self.speechServersChoices = \
                self.speechSystemsChoice.SpeechServer.getSpeechServers()
        if len(self.speechServersChoices) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_FINEST)
            self.prefsDict["enableSpeech"] = False
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
            return

        valueSet = False
        i = 0
        for speechSystem in self.speechSystemsChoices:
            name = speechSystem.__name__
            if name.endswith(systemName):
                self.speechSystems.set_active(i)
                self.speechSystemsChoice = self.speechSystemsChoices[i]
                valueSet = True
                break
            i += 1

        if not valueSet:
            debug.println(debug.LEVEL_FINEST,
                          "Could not find speech system match for %s" \
                          % systemName)
            self.speechSystems.set_active(0)
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
                pass

        self.speechSystemsChoices = []
        if len(self.workingFactories) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_FINEST)
            self.prefsDict["enableSpeech"] = False
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

        self._setSpeechSystemsChoice(self.prefsDict["speechServerFactory"])

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
            self.prefsDict["enableSpeech"] = False
            return

        speech.init()

        # This cascades into systems->servers->voice_type->families...
        #
        self.initializingSpeech = True
        self._setupSpeechSystems(factories)
        self.initializingSpeech = False

    def _initGUIState(self):
        """Adjust the settings of the various components on the
        configuration GUI depending upon the users preferences.
        """

        prefs = self.prefsDict

        # Speech pane.
        #
        enable = prefs["enableSpeech"]
        self.speechSupportCheckbutton.set_active(enable)
        self.speechTable.set_sensitive(enable)

        if prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_NONE:
            self.noneButton.set_active(True)
        elif prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_SOME:
            self.someButton.set_active(True)
        elif prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_MOST:
            self.mostButton.set_active(True)
        else:
            self.allButton.set_active(True)

        if prefs["speechVerbosityLevel"] == settings.VERBOSITY_LEVEL_BRIEF:
            self.speechBriefButton.set_active(True)
        else:
            self.speechVerboseButton.set_active(True)

        if prefs["readTableCellRow"]:
            self.rowSpeechButton.set_active(True)
        else:
            self.cellSpeechButton.set_active(True)

        self.speechIndentationCheckbutton.set_active(\
            prefs["enableSpeechIndentation"])

        self.speakBlankLinesCheckButton.set_active(\
            prefs["speakBlankLines"])

        # Braille pane.
        #
        self.brailleSupportCheckbutton.set_active(prefs["enableBraille"])
        self.brailleMonitorCheckbutton.set_active(prefs["enableBrailleMonitor"])
        state = prefs["brailleRolenameStyle"] == \
                            settings.BRAILLE_ROLENAME_STYLE_SHORT
        self.abbrevRolenames.set_active(state)
        if prefs["brailleVerbosityLevel"] == settings.VERBOSITY_LEVEL_BRIEF:
            self.brailleBriefButton.set_active(True)
        else:
            self.brailleVerboseButton.set_active(True)

        # Key Echo pane.
        #
        self.keyEchoCheckbutton.set_active(prefs["enableKeyEcho"])
        self.printableCheckbutton.set_active(prefs["enablePrintableKeys"])
        self.modifierCheckbutton.set_active(prefs["enableModifierKeys"])
        self.lockingCheckbutton.set_active(prefs["enableLockingKeys"])
        self.functionCheckbutton.set_active(prefs["enableFunctionKeys"])
        self.actionCheckbutton.set_active(prefs["enableActionKeys"])
        self.echoByWordCheckbutton.set_active(prefs["enableEchoByWord"])

        # Magnifier pane.
        #
        # Set the sensitivity of the items on the magnifier pane, depending
        # upon whether the "Enable Magnifier" checkbox is checked.
        #
        enable = prefs["enableMagnifier"]
        self.magnifierSupportCheckbutton.set_active(enable)
        self.magnifierTable.set_sensitive(enable)

        # Get the 'Cursor on/off' preference and set the checkbox accordingly.
        #
        value = prefs["enableMagCursor"]
        self.magCursorOnOffCheckButton.set_active(value)

        # Get the 'Explicit cursor size' preference and set the checkbox
        # accordingly. If the value is not checked, then the cursor size
        # spin button and label need to be set insensitive.
        #
        explicitSizeChecked = prefs["enableMagCursorExplicitSize"]
        self.magCursorSizeCheckButton.set_active(explicitSizeChecked)
        self.magCursorSizeSpinButton.set_sensitive(explicitSizeChecked)
        self.magCursorSizeLabel.set_sensitive(explicitSizeChecked)

        # Get the cursor size preference and set the cursor size spin
        # button value accordingly.
        #
        cursorSize = prefs["magCursorSize"]
        self.magCursorSizeSpinButton.set_value(cursorSize)

        # Get the cursor color preference and set the cursor color button
        # accordingly.
        #
        cursorColor = prefs["magCursorColor"]
        color = gtk.gdk.color_parse(cursorColor)
        self.magCursorColorButton.set_color(color)

        # Get the 'Cross-hair on/off' preference and set the checkbox
        # accordingly.
        #
        value = prefs["enableMagCrossHair"]
        self.magCrossHairOnOffCheckButton.set_active(value)

        # Get the 'Cross-hair clip on/off' preference and set the checkbox
        # accordingly.
        #
        value = prefs["enableMagCrossHairClip"]
        self.magCrossHairClipCheckButton.set_active(value)

        # Get the cross-hair size preference and set the cross-hair size
        # spin button value accordingly.
        #
        crosshairSize = prefs["magCrossHairSize"]
        self.magCrossHairSizeSpinButton.set_value(crosshairSize)

        # Get the width and the height of the screen.
        #
        self.screenWidth = gtk.gdk.screen_get_default().get_width()
        self.screenHeight = gtk.gdk.screen_get_default().get_height()

        # Get the zoomer placement top preference and set the top spin
        # button value accordingly. Set the top spin button "max size" to
        # the height of the screen.
        #
        topPosition = prefs["magZoomerTop"]
        self.magZoomerTopSpinButton.set_value(topPosition)
        self.magZoomerTopSpinButton.set_range(0, self.screenHeight)

        # Get the zoomer placement left preference and set the left spin
        # button value accordingly. Set the left spin button "max size" to
        # the width of the screen.
        #
        leftPosition = prefs["magZoomerLeft"]
        self.magZoomerLeftSpinButton.set_value(leftPosition)
        self.magZoomerLeftSpinButton.set_range(0, self.screenWidth)

        # Get the zoomer placement right preference and set the right spin
        # button value accordingly. Set the right spin button "max size" to
        # the width of the screen.
        #
        rightPosition = prefs["magZoomerRight"]
        self.magZoomerRightSpinButton.set_value(rightPosition)
        self.magZoomerRightSpinButton.set_range(0, self.screenWidth)

        # Get the zoomer placement bottom preference and set the bottom
        # spin button value accordingly. Set the bottom spin button "max size"
        # to the height of the screen.
        #
        bottomPosition = prefs["magZoomerBottom"]
        self.magZoomerBottomSpinButton.set_value(bottomPosition)
        self.magZoomerBottomSpinButton.set_range(0, self.screenHeight)

        # Get the zoom factor preference and set the zoom factor spin
        # button value accordingly.
        #
        zoomFactor = prefs["magZoomFactor"]
        self.magZoomFactorSpinButton.set_value(zoomFactor)

        # Get the 'Invert Colors' preference and set the checkbox accordingly.
        #
        value = prefs["enableMagZoomerColorInversion"]
        self.magInvertColorsCheckBox.set_active(value)

        # Get the smoothing preference and set the active value for the
        # smoothing combobox accordingly.
        #
        smoothingMode = prefs["magSmoothingMode"]
        if smoothingMode == settings.MAG_SMOOTHING_MODE_BILINEAR:
            mode = _("Bilinear")
        elif smoothingMode == settings.MAG_SMOOTHING_MODE_NONE:
            mode = _("None")
        else:
            mode = _("Bilinear")
        index = self._getComboBoxIndex(self.magSmoothingComboBox, mode)
        self.magSmoothingComboBox.set_active(index)

        # Get the mouse tracking preference and set the active value for
        # the mouse tracking combobox accordingly.
        #
        mouseTrackingMode = prefs["magMouseTrackingMode"]
        if mouseTrackingMode == settings.MAG_MOUSE_TRACKING_MODE_CENTERED:
            mode = _("Centered")
        elif mouseTrackingMode == settings.MAG_MOUSE_TRACKING_MODE_NONE:
            mode = _("None")
        elif mouseTrackingMode == settings.MAG_MOUSE_TRACKING_MODE_PROPORTIONAL:
            mode = _("Proportional")
        elif mouseTrackingMode == settings.MAG_MOUSE_TRACKING_MODE_PUSH:
            mode = _("Push")
        else:
            mode = _("Centered")
        index = self._getComboBoxIndex(self.magMouseTrackingComboBox, mode)
        self.magMouseTrackingComboBox.set_active(index)

        # Get the magnification source and target displays.
        #
        sourceDisplay = prefs["magSourceDisplay"]
        self.magSourceDisplayEntry.set_text(sourceDisplay)

        targetDisplay = prefs["magTargetDisplay"]
        self.magTargetDisplayEntry.set_text(targetDisplay)

        # General pane.
        #
        self.showMainWindowCheckButton.set_active(prefs["showMainWindow"])

        self.disableKeyGrabPref = settings.isGKSUGrabDisabled()
        self.disableKeyGrabCheckButton.set_active(self.disableKeyGrabPref)

        if prefs["keyboardLayout"] == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            self.generalDesktopButton.set_active(True)
        else:
            self.generalLaptopButton.set_active(True)

    def _getComboBoxIndex(self, combobox, str):
        """ For each of the entries in the given combo box, look for str.
            Return the index of the entry if str is found.

        Arguments:
        - combobox: the GtkComboBox to search.
        - str: the string to search for.

        Returns the index of the first entry in combobox with str, or
        0 if not found.
        """

        model = combobox.get_model()
        iter = model.get_iter_first()
        for i in range(0, len(model)):
            name = model.get_value(iter, 0)
            if name == str:
                return i
            iter = model.iter_next(iter)

        return 0

    def _showGUI(self):
        """Show the Orca configuration GUI window. This assumes that
        the GUI has already been created.
        """

        # We want the Orca preferences window to have focus when it is
        # shown. First try using the present() call. If this isn't present
        # in the version of pygtk that the user is using, fall back to
        # trying to set the current time on the Preferences window using
        # set_user_time. If that isn't found, then catch the exception and
        # fail gracefully.
        #
        self.orcaSetupWindow.realize()
        try:
            if settings.showMainWindow:
                self.orcaSetupWindow.present()
            else:
                self.orcaSetupWindow.window.set_user_time(\
                    orca_state.lastInputEventTimestamp)
        except:
            try:
                self.orcaSetupWindow.window.set_user_time(\
                    orca_state.lastInputEventTimestamp)
            except AttributeError:
                debug.printException(debug.LEVEL_FINEST)

        self.orcaSetupWindow.show()

    def _initComboBox(self, combobox):
        """Initialize the given combo box to take a list of int/str pairs.

        Arguments:
        - combobox: the GtkComboBox to initialize.
        """

        cell = gtk.CellRendererText()
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 1)
        model = gtk.ListStore(int, str)
        combobox.set_model(model)

        return model

    def _setKeyEchoItems(self):
        """[In]sensitize the checkboxes for the various types of key echo,
        depending upon whether the value of the key echo check button is set.
        """

        enable = self.keyEchoCheckbutton.get_active()
        self.printableCheckbutton.set_sensitive(enable)
        self.modifierCheckbutton.set_sensitive(enable)
        self.lockingCheckbutton.set_sensitive(enable)
        self.functionCheckbutton.set_sensitive(enable)
        self.actionCheckbutton.set_sensitive(enable)

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

        iter = model.append(None)
        model.set(iter,
                  DESCRIP, appName,
                  MODIF, False)

        return iter

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

    def _addAlternateKeyBinding(self, kb):
        """Adds an alternate keybinding to the existing handler and
        returns true.  In case it doesn't exist yet, just returns
        false.

        Argument:
        - kb: the keybinding to be added as an alternate keybinding.
        """

        model = self.keyBindingsModel
        iter = model.get_iter_first()
        exist = False

        while iter != None:
            iterChild = model.iter_children(iter)
            while iterChild != None:
                if model.get(iterChild,DESCRIP)[0] == kb.handler._description:
                    exist = True
                    model.set(iterChild,
                              MOD_MASK2, kb.modifier_mask,
                              MOD_USED2, kb.modifiers,
                              KEY2, kb.keysymstring,
                              TEXT2,keybindings.getModifierNames(kb.modifiers)\
                                  + kb.keysymstring)
                iterChild = model.iter_next(iterChild)
            iter = model.iter_next(iter)

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
            model.set (myiter,
                       HANDLER,   handl,
                       DESCRIP,   kb.handler._description,
                       MOD_MASK1, kb.modifier_mask,
                       MOD_USED1, kb.modifiers,
                       KEY1,      kb.keysymstring,
                       TEXT1,     keybindings.getModifierNames(kb.modifiers) \
                                  + kb.keysymstring,
                       MODIF,     modif,
                       EDITABLE,  True)
            return myiter
        else:
            return None

    def _insertRowBraille(self, handl, com, inputEvHand, parent=None, modif=False):
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
            parent = self._getIterOf(_("Braille Bindings"))

        if parent != None:
            myiter = model.append(parent)
            model.set (myiter,
                       HANDLER,  handl,
                       DESCRIP,  inputEvHand._description,
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
            keyBinds = settings.overrideKeyBindings(defScript,keyBinds)
            keyBind = keybindings.KeyBinding(None,None,None,None)
            treeModel = self.keyBindingsModel

            iter = treeModel.get_iter_first()
            while iter != None:
                iterChild = treeModel.iter_children(iter)
                while iterChild != None:
                    descrip = treeModel.get_value(iterChild, DESCRIP)
                    keyBind.handler=input_event.InputEventHandler(None,descrip)
                    if keyBinds.hasKeyBinding(keyBind,
                                              typeOfSearch="description"):
                        treeModel.set_value(iterChild, MODIF, True)
                    iterChild = treeModel.iter_next(iterChild)
                iter = treeModel.iter_next(iter)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def _populateKeyBindings(self):
        """Fills the TreeView with the list of Orca keybindings
        """
        self.keyBindingsModel.clear()

        self.kbindings = keybindings.KeyBindings()

        # KeyBindings from the default script, in default.py (Orca's default)
        #
        iterOrca = self._createNode(_("Orca"))
        defScript = default.Script(None)
        self.kbindingsDef = defScript.getKeyBindings()

        for kb in self.kbindingsDef.keyBindings:
            if not self.kbindings.hasKeyBinding(kb, typeOfSearch="strict"):
                if not self._addAlternateKeyBinding(kb):
                    handl = defScript.getInputEventHandlerKey(kb.handler)
                    self._insertRow(handl, kb, iterOrca)

        self.orcaModKeyEntry = self.widgets.get_widget("orcaModKeyEntry")
        self.orcaModKeyEntry.set_text(
            str(settings.orcaModifierKeys)[1:-1].replace("'",""))

        self._markModified()

        # Braille Bindings from default script, in default.py
        #
        iterBB = self._createNode(_("Braille Bindings"))

        self.bbindings = defScript.getBrailleBindings()
        for com, inputEvHand in self.bbindings.iteritems():
            handl = defScript.getInputEventHandlerKey(inputEvHand)
            self._insertRowBraille(handl, com, inputEvHand, iterBB)

        self.keyBindView.expand_all()
        self.keyBindingsModel.set_sort_column_id(TEXT1, gtk.SORT_ASCENDING)

    def speechSupportChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           speechSupportCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Speech" checkbox. Set the 'enableSpeech'
           preference to the new value. Set the rest of the speech pane items
           [in]sensensitive depending upon whether this checkbox is checked.

        Arguments:
        - widget: the component that generated the signal.
        """

        enable = widget.get_active()
        self.prefsDict["enableSpeech"] = enable
        self.speechTable.set_sensitive(enable)

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
            voiceType = self.voiceTypes.get_active_text()
            self._setFamilyNameForVoiceType(voiceType, name, language)
        except:
            debug.printException(debug.LEVEL_SEVERE)
            pass

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

        voiceType = widget.get_active_text()
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
        voiceType = self.voiceTypes.get_active_text()
        self._setRateForVoiceType(voiceType, rate)

    def pitchValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the pitchScale
           GtkHScale widget. The user has changed the current pitch value.
           Save the new pitch value based on the currently selected voice
           type.

        Arguments:
        - widget: the component that generated the signal.
        """

        pitch = widget.get_value()
        voiceType = self.voiceTypes.get_active_text()
        self._setPitchForVoiceType(voiceType, pitch)

    def volumeValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the voiceScale
           GtkHScale widget. The user has changed the current volume value.
           Save the new volume value based on the currently selected voice
           type.

        Arguments:
        - widget: the component that generated the signal.
        """

        volume = widget.get_value()
        voiceType = self.voiceTypes.get_active_text()
        self._setVolumeForVoiceType(voiceType, volume)

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

    def brailleSupportChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           brailleSupportCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Braille support" checkbox. Set the
           'enableBraille' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableBraille"] = widget.get_active()

    def brailleMonitorChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           brailleMonitorCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Braille monitor" checkbox. Set the
           'enableBrailleMonitor' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableBrailleMonitor"] = widget.get_active()

    def keyEchoChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           keyEchoCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Key Echo" checkbox. Set the
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
           [un]checked the 'Enable alphanumeric and punctuation keys"
           checkbox. Set the 'enablePrintableKeys' preference to the
           new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enablePrintableKeys"] = widget.get_active()

    def modifierKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           modifierCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable modifier keys" checkbox. Set the
           'enableModifierKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableModifierKeys"] = widget.get_active()

    def lockingKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           lockingCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable locking keys" checkbox. Set the
           'enableLockingKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableLockingKeys"] = widget.get_active()

    def functionKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           functionCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable locking keys" checkbox. Set the
           'enableLockingKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableFunctionKeys"] = widget.get_active()

    def actionKeysChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           actionCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable action keys" checkbox. Set the
           'enableActionKeys' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """
        self.prefsDict["enableActionKeys"] = widget.get_active()

    def echoByWordChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           echoByWordCheckbutton GtkCheckButton widget. The user has
           [un]checked the 'Enable Echo by Word" checkbox. Set the
           'enableEchoByWord' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableEchoByWord"] = widget.get_active()

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
            if widget.get_label() == _("_None"):
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_NONE
            elif widget.get_label() == _("So_me"):
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_SOME
            elif widget.get_label() == _("M_ost"):
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_MOST
            else:
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_ALL

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
            if widget.get_label() == _("Speak current _cell"):
                self.prefsDict["readTableCellRow"] = False
            else:
                self.prefsDict["readTableCellRow"] = True

    def abbrevRolenamesChecked(self, widget):
        """Signal handler for the "toggled" signal for the abbrevRolenames
           GtkCheckButton widget. The user has [un]checked the 'Abbreviated
           Rolenames" checkbox. Set the 'brailleRolenameStyle' preference
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
            if widget.get_label() == _("Brie_f"):
                self.prefsDict["brailleVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_BRIEF
            else:
                self.prefsDict["brailleVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_VERBOSE

    def magnifierSupportChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magnifierSupportCheckbutton GtkCheckButton widget.
           The user has [un]checked the 'Enable Magnification" checkbox.
           Set the 'enableMagnifier' preference to the new value.
           Set the rest of the magnifier pane items [in]sensensitive
           depending upon whether this checkbox is checked.

        Arguments:
        - widget: the component that generated the signal.
        """

        enable = widget.get_active()
        self.prefsDict["enableMagnifier"] = enable
        self.magnifierTable.set_sensitive(enable)

    def magCursorOnOffChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magCursorOnOffCheckButton GtkCheckButton widget.
           The user has [un]checked the magnification cursor settings
           'Cursor on/off' checkbox. Set the 'enableMagCursor' preference
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableMagCursor"] = widget.get_active()

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
        self.prefsDict["enableMagCursorExplicitSize"] = enable
        self.magCursorSizeSpinButton.set_sensitive(enable)
        self.magCursorSizeLabel.set_sensitive(enable)

    def magCursorSizeValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magCursorSizeSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           cursor settings cursor size spin button. Set the
           'magCursorSize' preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["magCursorSize"] = widget.get_value_as_int()

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
        self.prefsDict["magCursorColor"] = cursorColor

    def magCrossHairOnOffChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magCrossHairOnOffCheckButton GtkCheckButton widget.
           The user has [un]checked the magnification cross-hair settings
           'Cross-hair on/off' checkbox. Set the 'enableMagCrossHair'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableMagCrossHair"] = widget.get_active()

    def magCrossHairClipOnOffChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magCrossHairClipCheckButton GtkCheckButton widget.
           The user has [un]checked the magnification cross-hair settings
           'Cross-hair clip on/off' checkbox. Set the 'enableMagCrossHairClip'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableMagCrossHairClip"] = widget.get_active()

    def magCrossHairSizeValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magCrossHairSizeSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           cross-hair settings cross-hair size spin button. Set the
           'magCrossHairSize' preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["magCrossHairSize"] = widget.get_value_as_int()

    def magZoomerTopValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magZoomerTopSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           zoomer placement top spin button. Set the 'magZoomerTop'
           preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["magZoomerTop"] = widget.get_value_as_int()

    def magZoomerBottomValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magZoomerBottomSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           zoomer placement bottom spin button. Set the 'magZoomerBottom'
           preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["magZoomerBottom"] = widget.get_value_as_int()

    def magZoomerLeftValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magZoomerLeftSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           zoomer placement left spin button. Set the 'magZoomerLeft'
           preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["magZoomerLeft"] = widget.get_value_as_int()

    def magZoomerRightValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magZoomerRightSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           zoomer placement right spin button. Set the 'magZoomerRight'
           preference to the new integer value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["magZoomerRight"] = widget.get_value_as_int()

    def magZoomFactorValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the
           magZoomFactorSpinButton GtkSpinButton widget.
           The user has changed the value of the magnification
           zoom factor spin button. Set the 'magZoomFactor'
           preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["magZoomFactor"] = widget.get_value_as_int()

    def magSmoothingChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magSmoothingComboBox GtkComboBox widget. The user has
           selected a different magnification smoothing style.
           Set the 'magSmoothingMode' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        smoothingMode = widget.get_active_text()
        if smoothingMode ==  _("Bilinear"):
            mode = settings.MAG_SMOOTHING_MODE_BILINEAR
        elif smoothingMode == _("None"):
            mode = settings.MAG_SMOOTHING_MODE_NONE
        else:
            mode = settings.MAG_SMOOTHING_MODE_BILINEAR
        self.prefsDict["magSmoothingMode"] = mode

    def magMouseTrackingChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magMouseTrackingComboBox GtkComboBox widget. The user has
           selected a different magnification mouse tracking style.
           Set the 'magMouseTrackingMode' preference to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        mouseTrackingMode = widget.get_active_text()
        if mouseTrackingMode ==  _("Centered"):
            mode = settings.MAG_MOUSE_TRACKING_MODE_CENTERED
        elif mouseTrackingMode == _("Push"):
            mode = settings.MAG_MOUSE_TRACKING_MODE_PUSH
        elif mouseTrackingMode == _("Proportional"):
            mode = settings.MAG_MOUSE_TRACKING_MODE_PROPORTIONAL
        elif mouseTrackingMode == _("None"):
            mode = settings.MAG_MOUSE_TRACKING_MODE_NONE
        else:
            mode = settings.MAG_MOUSE_TRACKING_MODE_CENTERED
        self.prefsDict["magMouseTrackingMode"] = mode

    def magInvertColorsChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           magCrossHairOnOffCheckButton GtkCheckButton widget.
           The user has [un]checked the magnification 'Invert Colors'
           checkbox. Set the 'enableMagZoomerColorInversion' preference
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["enableMagZoomerColorInversion"] = widget.get_active()

    def keyModifiedToggle(self, cell, path, model, col):
        """When the user changes a checkbox field (boolean field)"""

        model[path][col] = not model[path][col]
        return

    def editingKey(self, cell, editable, path, treeModel):
        """Starts user input of a Key for a selected key binding"""

        editable.set_text(_("enter new key"))
        orca_state.capturingKeys = True
        return

    def editedKey(self, cell, path, new_text, treeModel, modMask, modUsed, key, text):
        """The user changes the key for a Keybinding:
            update the model of the treeview
        """

        newKeyEvent = orca_state.lastCapturedKey
        newKey = str(orca_state.lastCapturedKey.event_string)
        mods = keybindings.getModifierNames(newKeyEvent.modifiers)

        orca_state.capturingKeys = False

        if (newKey != treeModel[path][key]) \
           or (newKeyEvent.modifiers != int(treeModel[path][modUsed])):
            iter = treeModel.get_iter_from_string(path)
            treeModel.set(iter,
                          modMask, newKeyEvent.modifiers,
                          modUsed, newKeyEvent.modifiers,
                          key, newKey,
                          text, mods + newKey,
                          MODIF, True)
            speech.stop()
            speech.speak(_("The new key is: %s") % newKey)
        else:
            speech.stop()
            speech.speak(_("The key entered is the same. Nothing changed."))

        return

    def magSourceDisplayChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magSourceDisplayDisplayEntry GtkEntry widget.
           The user has changed the value of the magnification source
           display. Set the 'magSourceDisplay' preference
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["magSourceDisplay"] = widget.get_text()

    def magTargetDisplayChanged(self, widget):
        """Signal handler for the "changed" signal for the
           magTargetDisplayEntry GtkEntry widget.
           The user has changed the value of the magnification target
           display. Set the 'magTargetDisplay' preference
           to the new value.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.prefsDict["magTargetDisplay"] = widget.get_text()

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

    def helpButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the helpButton
           GtkButton widget. The user has clicked the Help button.

        Arguments:
        - widget: the component that generated the signal.
        """

        print "Help not currently implemented."

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

        enable = self.speechSupportCheckbutton.get_active()
        self.prefsDict["enableSpeech"] = enable
        self.prefsDict["speechServerFactory"] = \
            self.speechSystemsChoice.__name__
        self.prefsDict["speechServerInfo"] = self.speechServersChoice.getInfo()
        self.prefsDict["voices"] = {
            settings.DEFAULT_VOICE   : acss.ACSS(self.defaultVoice),
            settings.UPPERCASE_VOICE : acss.ACSS(self.uppercaseVoice),
            settings.HYPERLINK_VOICE : acss.ACSS(self.hyperlinkVoice)
        }

        settings.setGKSUGrabDisabled(self.disableKeyGrabPref)

        if orca_prefs.writePreferences(self.prefsDict, self.keyBindingsModel):
            self._say(_("Accessibility support for GNOME has just been enabled."))
            self._say(_("You need to log out and log back in for the change to take effect."))

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

        self.orcaSetupWindow.destroy()

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
        self.orcaSetupWindow.hide()

    def windowDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the orcaSetupWindow
           GtkWindow widget. Reset OS to None, so that the GUI can be rebuilt
           from the Glade file the next time the user wants to display the
           configuration GUI.

        Arguments:
        - widget: the component that generated the signal.
        """

        global OS

        OS = None

def showPreferencesUI():
    global OS

    line = _("Starting Orca Preferences. This may take a while.")
    braille.displayMessage(line)
    speech.speak(line)

    if not OS:
        gladeFile = os.path.join(platform.prefix,
                                 platform.datadirname,
                                 platform.package,
                                 "glade",
                                 "orca-setup.glade")
        OS = orcaSetupGUI(gladeFile, "orcaSetupWindow")
        OS._init()

    OS._showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showPreferencesUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
