# Orca
#
# Copyright 2006 Sun Microsystems Inc.
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
# - Adjust routines names to start with _ when only used in this module.
# - Improve reclaimation of "old" speech servers in _setupServers().
# - Implement the Help button callback.
# - Need to add comments to each method.

"""Displays a GUI for the user to set Orca preferences."""

import os
import sys
import debug
import gettext
import gtk
import gtk.glade
import locale

import acss
import orca
import orca_prefs
import platform
import settings
import speech as speech
import speechserver as speechserver

from orca_i18n import _  # for gettext support

OS = None

class GladeWrapper:
    """
    Superclass for glade based applications. Just derive from this
    and your subclass should create methods whose names correspond to
    the signal handlers defined in the glade file. Any other attributes
    in your class will be safely ignored.

    This class will give you the ability to do:
        subclass_instance.GtkWindow.method(...)
        subclass_instance.widget_name...
    """

    def __init__(self, Filename, WindowName):
        # Load glade file.
        self.widgets = gtk.glade.XML(Filename, WindowName, gettext.textdomain())
        self.GtkWindow = getattr(self, WindowName)

        instance_attributes = {}
        for attribute in dir(self.__class__):
            instance_attributes[attribute] = getattr(self, attribute)
        self.widgets.signal_autoconnect(instance_attributes)

    def __getattr__(self, attribute):   # Called when no attribute in __dict__
        widget = self.widgets.get_widget(attribute)
        if widget is None:
            raise AttributeError("Widget [" + attribute + "] not found")
        self.__dict__[attribute] = widget   # Add reference to cache.

        return widget

class orcaSetupGUI(GladeWrapper):

    def _init(self):
        """Initialize the Orca configuration GUI. Read the users current
        set of preferences and set the GUI state to match. Setup speech
        support and populate the combo box lists on the Speech Tab pane
        accordingly.
        """

        self.initializing = True
        self.prefsDict = orca_prefs.readPreferences()
        self.defaultVoice   = self.prefsDict["voices"]["default"]
        self.uppercaseVoice = self.prefsDict["voices"]["uppercase"]
        self.hyperlinkVoice = self.prefsDict["voices"]["hyperlink"]

        self.speechSystemsModel = self._initComboBox(self.speechSystems)
        self.speechServersModel = self._initComboBox(self.speechServers)
        self.voicesModel        = self._initComboBox(self.voices)

        self._setKeyEchoItems()

        factories = speech.getSpeechServerFactories()
        if len(factories) == 0:
            self.prefsDict["enableSpeech"] = False
            return

        speech.init()

        self.workingFactories = []
        for factory in factories:
            try:
                servers = factory.SpeechServer.getSpeechServers()
                if len(servers):
                    self.workingFactories.append(factory)
            except:
                debug.printException(debug.LEVEL_FINEST)
                pass

        if debug.debugLevel <= debug.LEVEL_FINEST:
            print "orca_gui_prefs._init: workingFactories: ", \
                  self.workingFactories

        self.factoryChoices = {}
        if len(self.workingFactories) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_FINEST)
            self.prefsDict["enableSpeech"] = False
            return
        elif len(self.workingFactories) > 1:
            i = 1
            for workingFactory in self.workingFactories:
                self.factoryChoices[i] = workingFactory
                name = workingFactory.SpeechServer.getFactoryName()
                self.speechSystemsModel.append((i, name))
                i += 1
            self.factory = self.factoryChoices[1]
        else:
            self.factoryChoices[1] = self.workingFactories[0]
            name = self.workingFactories[0].SpeechServer.getFactoryName()
            self.speechSystemsModel.append((1, name))
            self.factory = self.workingFactories[0]

        if debug.debugLevel <= debug.LEVEL_FINEST:
            print "orca_gui_prefs._init: factoryChoices: ", self.factoryChoices
            print "orca_gui_prefs._init: factory: ", self.factory
            print "orca_gui_prefs._init: servers: ", servers

        self.serverChoices = None
        self._setupServers()
        self._setupVoices()
        self.prefsDict["enableSpeech"] = True
        self._initGUIState()
        self.initializing = False

    def _setVoiceSettingForVoiceType(self, voiceType):
        familyName = self._getFamilyNameForVoiceType(voiceType)
        if familyName:
            self._setVoiceChoice(self.families, familyName)

        rate = self._getRateForVoiceType(voiceType)
        if rate:
            self.rateScale.set_value(rate)

        pitch = self._getPitchForVoiceType(voiceType)
        if pitch:
            self.pitchScale.set_value(pitch)

        volume = self._getVolumeForVoiceType(voiceType)
        if volume:
            self.volumeScale.set_value(volume)

    def _initGUIState(self):
        prefs = self.prefsDict

        # Speech pane.
        #
        self._setSystemChoice(self.factoryChoices, prefs["speechServerFactory"])

        serverPrefs = prefs["speechServerInfo"]
        if serverPrefs:
            self._setServerChoice(self.serverChoices, serverPrefs[0])

        voiceType = self.voiceType.get_active_text()
        self.voiceType.set_active(0)
        self._setVoiceSettingForVoiceType(voiceType)

        if prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_NONE:
            self.noneButton.set_active(True)
        elif prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_SOME:
            self.someButton.set_active(True)
        else:
            self.allButton.set_active(True)

        if prefs["speechVerbosityLevel"] == _("Brief"):
            self.speechBriefButton.set_active(True)
        else:
            self.speechVerboseButton.set_active(True)

        # Braille pane.
        #
        self.brailleSupportCheckbutton.set_active(prefs["enableBraille"])
        self.brailleMonitorCheckbutton.set_active(prefs["enableBrailleMonitor"])
        state = prefs["brailleRolenameStyle"] == \
                            settings.BRAILLE_ROLENAME_STYLE_SHORT
        self.abbrevRolenames.set_active(state)
        if prefs["brailleVerbosityLevel"] == _("Brief"):
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

    def _setupServers(self):
        self.servers = self.factory.SpeechServer.getSpeechServers()
        self.serverChoices = {}
        if len(self.servers) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_FINEST)
            self.prefsDict["enableSpeech"] = False
            self.server = None
            return
        if len(self.servers) > 1:
            i = 1
            for self.server in self.servers:
                self.serverChoices[i] = self.server
                name = self.server.getInfo()[0]
                self.speechServersModel.append((i, name))
                i += 1
            self.server = self.serverChoices[1]
        else:
            self.serverChoices[1] = self.servers[0]
            name = self.servers[0].getInfo()[0]
            self.speechServersModel.append((1, name))
            self.server = self.servers[0]

        self.speechServers.set_active(0)

        if debug.debugLevel <= debug.LEVEL_FINEST:
            print "orca_gui_prefs._setupServers: serverChoices: ", \
                   self.serverChoices
            print "orca_gui_prefs._setupServers: server: ", self.server

    def _setupVoices(self):
        self.families = self.server.getVoiceFamilies()

        self.voiceChoices = {}
        if len(self.families) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_FINEST)
            self.prefsDict["enableSpeech"] = False
            return
        if len(self.families) > 1:
            i = 1
            for family in self.families:
                name = family[speechserver.VoiceFamily.NAME]
                self.acss = acss.ACSS({acss.ACSS.FAMILY : family})
                self.voiceChoices[i] = self.acss
                self.voicesModel.append((i, name))
                i += 1
            self.defaultACSS = self.voiceChoices[1]
        else:
            name = self.families[0][speechserver.VoiceFamily.NAME]
            self.voicesModel.append((1, name))
            self.defaultACSS = \
                acss.ACSS({acss.ACSS.FAMILY : self.families[0]})
            self.voiceChoices[1] = self.defaultACSS

        if not self.initializing:
            self.voices.set_active(0)

        if debug.debugLevel <= debug.LEVEL_FINEST:
            print "orca_gui_prefs._setupVoices: voiceChoices: ", \
                   self.voiceChoices

    def _getVoiceForVoiceType(self, voiceType):
        if voiceType == _("Default"):
            voice = self.defaultVoice
        elif voiceType == _("Uppercase"):
            voice = self.uppercaseVoice
        elif voiceType == _("Hyperlink"):
            voice = self.hyperlinkVoice
        else:
            voice = self.defaultVoice

        return voice

    def _getKeyForVoiceType(self, voiceType, key, useDefault=True):
        """Look for the value of the given key, in the voice dictionary
           for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).
        - key: the key to look for in the voice dictionary.
        - useDefault: if True, and the key isn't found for the given voice
                      type, the look for it in the default voice dictionary
                      as well.

        Returns the value of the given key.
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
        familyName = None
        family = self._getKeyForVoiceType(voiceType, "family")

        if family:
            if family.has_key("name"):
                familyName = family["name"]

        return familyName

    def _setFamilyNameForVoiceType(self, voiceType, value):
        family = self._getKeyForVoiceType(voiceType, "family", False)
        if family:
            family["name"] = value
        else:
            voice = self._getVoiceForVoiceType(voiceType)
            voice["family"] = {}
            voice["family"]["name"] = value

    def _getRateForVoiceType(self, voiceType):
        return self._getKeyForVoiceType(voiceType, "rate", True)

    def _setRateForVoiceType(self, voiceType, value):
        voice = self._getVoiceForVoiceType(voiceType)
        voice["rate"] = value

    def _getPitchForVoiceType(self, voiceType):
        return self._getKeyForVoiceType(voiceType, "average-pitch", True)

    def _setPitchForVoiceType(self, voiceType, value):
        voice = self._getVoiceForVoiceType(voiceType)
        voice["average-pitch"] = value

    def _getVolumeForVoiceType(self, voiceType):
        return self._getKeyForVoiceType(voiceType, "gain", True)

    def _setVolumeForVoiceType(self, voiceType, value):
        voice = self._getVoiceForVoiceType(voiceType)
        voice["gain"] = value

    def _setSystemChoice(self, factoryChoices, systemName):
        model = self.speechSystemsModel
        i = 1
        for factory in factoryChoices.values():
            name = factory.__name__
            if name == systemName:
                self.speechSystems.set_active(i-1)
                return
            i += 1

    def _setServerChoice(self, serverChoices, serverName):
        model = self.speechServersModel
        i = 1
        for server in serverChoices.values():
            name = server.getInfo()[0]
            if name == serverName:
                self.speechServers.set_active(i-1)
                return
            i += 1

    def _setVoiceChoice(self, families, voiceName):
        model = self.voicesModel
        i = 1
        for family in families:
            name = family[speechserver.VoiceFamily.NAME]
            if name == voiceName:
                self.voices.set_active(i-1)
                return
            i += 1

    def _showGUI(self):
        self.orcaSetupWindow.show()

    def _initComboBox(self, combobox):
        cell = gtk.CellRendererText()
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 1)
        model = gtk.ListStore(int, str)
        combobox.set_model(model)

        return model

    def _setKeyEchoItems(self):
        if self.keyEchoCheckbutton.get_active():
            enable = True
        else:
            enable = False
        self.printableCheckbutton.set_sensitive(enable)
        self.modifierCheckbutton.set_sensitive(enable)
        self.lockingCheckbutton.set_sensitive(enable)
        self.functionCheckbutton.set_sensitive(enable)
        self.actionCheckbutton.set_sensitive(enable)

    def speechSystemsChanged(self, widget):
        iter = widget.get_active_iter()
        model = widget.get_model()

        index = model.get_value(iter, 0)
        self.factory = self.factoryChoices[index]
        self.speechServersModel.clear()
        self._setupServers()

        self.server = self.serverChoices[1]
        self._setupVoices()

    def speechServersChanged(self, widget):
        iter = widget.get_active_iter()
        model = widget.get_model()

        index = model.get_value(iter, 0)
        self.voicesModel.clear()
        self.server = self.serverChoices[index]
        self._setupVoices()

    def voiceFamilyChanged(self, widget):
        iter = widget.get_active_iter()
        model = widget.get_model()

        name = model.get_value(iter, 1)
        voiceType = self.voiceType.get_active_text()
        self._setFamilyNameForVoiceType(voiceType, name)

    def brailleSupportChecked(self, widget):
        self.prefsDict["enableBraille"] = widget.get_active()

    def brailleMonitorChecked(self, widget):
        self.prefsDict["enableBrailleMonitor"] = widget.get_active()

    def keyEchoChecked(self, widget):
        self.prefsDict["enableKeyEcho"] = widget.get_active()
        self._setKeyEchoItems()

    def printableKeysChecked(self, widget):
        self.prefsDict["enablePrintableKeys"] = widget.get_active()

    def modifierKeysChecked(self, widget):
        self.prefsDict["enableModifierKeys"] = widget.get_active()

    def lockingKeysChecked(self, widget):
        self.prefsDict["enableLockingKeys"] = widget.get_active()

    def functionKeysChecked(self, widget):
        self.prefsDict["enableFunctionKeys"] = widget.get_active()

    def actionKeysChecked(self, widget):
        self.prefsDict["enableActionKeys"] = widget.get_active()

    def echoByWordChecked(self, widget):
        self.prefsDict["enableEchoByWord"] = widget.get_active()

    def voiceTypeChanged(self, widget):
        voiceType = widget.get_active_text()
        self._setVoiceSettingForVoiceType(voiceType)

    def rateValueChanged(self, widget):
        rate = widget.get_value()
        voiceType = self.voiceType.get_active_text()
        self._setRateForVoiceType(voiceType, rate)

    def pitchValueChanged(self, widget):
        pitch = widget.get_value()
        voiceType = self.voiceType.get_active_text()
        self._setPitchForVoiceType(voiceType, pitch)

    def volumeValueChanged(self, widget):
        volume = widget.get_value()
        voiceType = self.voiceType.get_active_text()
        self._setVolumeForVoiceType(voiceType, volume)

    def punctuationLevelChanged(self, widget):
        if widget.get_active():
            if widget.get_label() == _("None"):
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_NONE
            elif widget.get_label() == _("Some"):
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_SOME
            else:
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_ALL

    def speechVerbosityChanged(self, widget):
        if widget.get_active():
            if widget.get_label() == _("Brief"):
                self.prefsDict["speechVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_BRIEF
            else:
                self.prefsDict["speechVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_VERBOSE

    def abbrevRolenamesChecked(self, widget):
        if widget.get_active():
            self.prefsDict["brailleRolenameStyle"] = \
                settings.BRAILLE_ROLENAME_STYLE_SHORT
        else:
            self.prefsDict["brailleRolenameStyle"] = \
                settings.BRAILLE_ROLENAME_STYLE_LONG

    def brailleVerbosityChanged(self, widget):
        if widget.get_active():
            if widget.get_label() == _("Brief"):
                self.prefsDict["brailleVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_BRIEF
            else:
                self.prefsDict["brailleVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_VERBOSE

    def helpButtonClicked(self, widget):
        print "Help not currently implemented."

    def cancelButtonClicked(self, widget):
        self.orcaSetupWindow.hide()

    def applyButtonClicked(self, widget):

        self.prefsDict["enableSpeech"] = True
        self.prefsDict["speechServerFactory"] = self.factory
        self.prefsDict["speechServerInfo"] = self.server
        self.prefsDict["voices"] = {
            settings.DEFAULT_VOICE   : self.defaultVoice,
            settings.UPPERCASE_VOICE : self.uppercaseVoice,
            settings.HYPERLINK_VOICE : self.hyperlinkVoice
        }

        if orca_prefs.writePreferences(self.prefsDict):
            self.say(_("Accessibility support for GNOME has just been enabled."))
            self.say(_("You need to log out and log back in for the change to take effect."))

        for factory in self.workingFactories:
            factory.SpeechServer.shutdownActiveServers()
        orca.loadUserSettings()
        self.orcaSetupWindow.hide()

    def windowDestroyed(self, widget):
        global OS

        OS = None

    def say(text, stop=False):
        if stop:
            speech.stop()

        speech.speak(text)

def showPreferencesUI():
    global OS

    if not OS:
        gladeFile = os.path.join(platform.prefix,
                                 platform.datadirname,
                                 platform.package,
                                 "glade",
                                 "orca-setup.glade")
        OS = orcaSetupGUI(gladeFile, "orcaSetupWindow")
        OS._init()
    else:
        OS._showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showPreferencesUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
