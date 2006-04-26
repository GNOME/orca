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
# - Implement the Help button callback.
# - Need to setup the speech lists from the initial preferences.
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
        self.prefsDict = orca_prefs.readPreferences()
        self.initGUIState()

        self.speechSystemsModel = self.initList(self.speechSystems)
        selection = self.speechSystems.get_selection()
        selection.connect("changed", self.systemsSelectionChanged)

        self.speechServersModel = self.initList(self.speechServers)
        selection = self.speechServers.get_selection()
        selection.connect("changed", self.serversSelectionChanged)

        self.voicesModel = self.initList(self.voices)
        selection = self.voices.get_selection()
        selection.connect("changed", self.voicesSelectionChanged)

        self.setKeyEchoItems()

        # Use this because callbacks will often hang when not running
        # with bonobo main in use.
        #
        settings.enableSpeechCallbacks = False

        factories = speech.getSpeechServerFactories()
        if len(factories) == 0:
            self.prefsDict["enableSpeech"] = False
            return

        speech.init()

        workingFactories = []
        for self.factory in factories:
            try:
                self.factoryInfos = \
                    self.factory.SpeechServer.getSpeechServerInfos()
                workingFactories.append([self.factory, self.factoryInfos])
            except:
                pass

        self.factoryChoices = {}
        if len(workingFactories) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_SEVERE)
            self.prefsDict["enableSpeech"] = False
            return
        elif len(workingFactories) > 1:
            i = 1
            for workingFactory in workingFactories:
                self.factoryChoices[i] = workingFactory
                iter = self.speechSystemsModel.append()
                self.speechSystemsModel.set(iter, 0,
                               workingFactory[0].SpeechServer.getFactoryName())
                i += 1
            [self.factory, self.factoryInfos] = self.factoryChoices[1]
        else:
            self.factoryChoices[1] = workingFactories[0]
            iter = self.speechSystemsModel.append()
            self.speechSystemsModel.set(iter, 0,
                         workingFactories[0][0].SpeechServer.getFactoryName())
            [self.factory, self.factoryInfos] = workingFactories[0]

        self.setupServers(self.factory)
        self.setupVoices(self.server)
        self.prefsDict["enableSpeech"] = True

    def initGUIState(self):
        prefs = self.prefsDict

        self.brailleSupportCheckbutton.set_active(prefs["enableBraille"])
        self.brailleMonitorCheckbutton.set_active(prefs["enableBrailleMonitor"])

        self.keyEchoCheckbutton.set_active(prefs["enableKeyEcho"])
        self.printableCheckbutton.set_active(prefs["enablePrintableKeys"])
        self.modifierCheckbutton.set_active(prefs["enableModifierKeys"])
        self.lockingCheckbutton.set_active(prefs["enableLockingKeys"])
        self.functionCheckbutton.set_active(prefs["enableFunctionKeys"])
        self.actionCheckbutton.set_active(prefs["enableActionKeys"])
        self.echoByWordCheckbutton.set_active(prefs["enableEchoByWord"])


    def setupServers(self, factory):
        self.servers = []
        for info in self.factoryInfos:
            try:
                self.server = self.factory.SpeechServer.getSpeechServer(info)
                if self.server:
                    self.servers.append(self.server)
            except:
                pass

        self.serverChoices = {}
        if len(self.servers) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_SEVERE)
            self.prefsDict["enableSpeech"] = False
            return
        if len(self.servers) > 1:
            i = 1
            for self.server in self.servers:
                self.serverChoices[i] = self.server
                iter = self.speechServersModel.append()
                self.speechServersModel.set(iter, 0, self.server.getInfo()[0])
                i += 1
            self.server = self.serverChoices[1]
        else:
            self.serverChoices[1] = self.servers[0]
            iter = self.speechServersModel.append()
            self.speechServersModel.set(iter, 0, self.servers[0].getInfo()[0])
            self.server = self.servers[0]

    def setupVoices(self, server):
        self.families = server.getVoiceFamilies()

        self.voiceChoices = {}
        if len(self.families) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_SEVERE)
            self.prefsDict["enableSpeech"] = False
            return
        if len(self.families) > 1:
            i = 1
            for family in self.families:
                name = family[speechserver.VoiceFamily.NAME]
                self.acss = acss.ACSS({acss.ACSS.FAMILY : family})
                self.voiceChoices[i] = self.acss
                iter = self.voicesModel.append()
                self.voicesModel.set(iter, 0, name)
                i += 1
            self.defaultACSS = self.voiceChoices[1]
        else:
            name = self.families[0][speechserver.VoiceFamily.NAME]
            iter = self.voicesModel.append()
            self.voicesModel.set(iter, 0, name)
            self.defaultACSS = \
                acss.ACSS({acss.ACSS.FAMILY : self.families[0]})
            self.voiceChoices[1] = self.defaultACSS

    def getSystemChoiceIndex(self, factoryChoices, result):
        i = 1
        for factory in factoryChoices.values():
            name = factory[0].SpeechServer.getFactoryName()
            if name == result:
                return i
            i += 1

        return -1

    def getServerChoiceIndex(self, serverChoices, result):
        i = 1
        for server in serverChoices.values():
            name = server.getInfo()[0]
            if name == result:
                return i
            i += 1

        return -1

    def getVoiceChoiceIndex(self, families, result):
        i = 1
        for family in families:
            name = family[speechserver.VoiceFamily.NAME]
            if name == result:
                return i
            i += 1

        return -1

    def showGUI(self):
        self.orcaSetupWindow.show()

    def initList(self, list):
        model = gtk.ListStore(str)
        list.set_model(model)
        column = gtk.TreeViewColumn("", gtk.CellRendererText(), text=0)
        list.append_column(column)

        return model

    def setKeyEchoItems(self):
        if self.keyEchoCheckbutton.get_active():
            enable = True
        else:
            enable = False
        self.printableCheckbutton.set_sensitive(enable)
        self.modifierCheckbutton.set_sensitive(enable)
        self.lockingCheckbutton.set_sensitive(enable)
        self.functionCheckbutton.set_sensitive(enable)
        self.actionCheckbutton.set_sensitive(enable)

    def systemsSelectionChanged(self, selection):
        model, iter = selection.get_selected()
        if iter:
            results = model.get_value(iter, 0)
            index = self.getSystemChoiceIndex(self.factoryChoices, results)

            self.factory = self.factoryChoices[index][0]
            self.speechServersModel.clear()
            self.setupServers(self.factory)

            self.server = self.serverChoices[1]
            self.setupVoices(self.server)

    def serversSelectionChanged(self, selection):
        model, iter = selection.get_selected()
        if iter:
            results = model.get_value(iter, 0)
            index = self.getServerChoiceIndex(self.serverChoices, results)

            self.voicesModel.clear()
            self.server = self.serverChoices[index]
            self.setupVoices(self.server)

    def voicesSelectionChanged(self, selection):
        model, iter = selection.get_selected()
        if iter:
            results = model.get_value(iter, 0)
            index = self.getVoiceChoiceIndex(self.families, results)
            self.defaultACSS = self.voiceChoices[index]

    def brailleSupportChecked(self, widget):
        self.prefsDict["enableBraille"] = widget.get_active()

    def brailleMonitorChecked(self, widget):
        self.prefsDict["enableBrailleMonitor"] = widget.get_active()

    def keyEchoChecked(self, widget):
        self.prefsDict["enableKeyEcho"] = widget.get_active()
        self.setKeyEchoItems()

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

    def helpButtonClicked(self, widget):
        print "Help not currently implemented."

    def cancelButtonClicked(self, widget):
        self.orcaSetupWindow.hide()

    def applyButtonClicked(self, widget):

        # Force the rate to 50 so it will be set to something
        # and output to the user settings file.  50 is chosen
        # here, BTW, since it is the default value.  The same
        # goes for gain (volume) and average-pitch, but they
        # range from 0-10 instead of 0-100.
        #
        self.defaultACSS[acss.ACSS.RATE] = 50
        self.defaultACSS[acss.ACSS.GAIN] = 9
        self.defaultACSS[acss.ACSS.AVERAGE_PITCH] = 5
        self.uppercaseACSS = acss.ACSS({acss.ACSS.AVERAGE_PITCH : 6})
        self.hyperlinkACSS = acss.ACSS({acss.ACSS.AVERAGE_PITCH : 2})

        self.voices = {
            settings.DEFAULT_VOICE   : self.defaultACSS,
            settings.UPPERCASE_VOICE : self.uppercaseACSS,
            settings.HYPERLINK_VOICE : self.hyperlinkACSS
        }

        self.prefsDict["enableSpeech"] = True
        self.prefsDict["speechServerFactory"] = self.factory
        self.prefsDict["speechServerInfo"] = self.server
        self.prefsDict["voices"] = self.voices

        if orca_prefs.writePreferences(self.prefsDict):
            self.say(_("Accessibility support for GNOME has just been enabled."))
            self.say(_("You need to log out and log back in for the change to take effect."))

        orca.loadUserSettings()
        self.orcaSetupWindow.hide()

    def windowDestroyed(self, widget):
        self.orcaSetupWindow.hide()

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
        OS.showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showPreferencesUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
