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
# - Improve reclaimation of "old" speech servers in _setupServers().
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

        debug.println(debug.LEVEL_FINEST, 
                      "orca_gui_prefs._init: workingFactories: %s" \
                      % self.workingFactories)

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

        debug.println(debug.LEVEL_FINEST, 
                      "orca_gui_prefs._init: factoryChoices: %s" \
                      % self.factoryChoices)
        debug.println(debug.LEVEL_FINEST, 
                      "orca_gui_prefs._init: factory: %s" \
                      % self.factory)
        debug.println(debug.LEVEL_FINEST, 
                      "orca_gui_prefs._init: servers: %s" \
                      % servers)

        self.serverChoices = None
        self._setupServers()
        self._setupVoices()
        self.prefsDict["enableSpeech"] = True
        self._initGUIState()
        self.initializing = False

    def _setVoiceSettingForVoiceType(self, voiceType):
        """Set the family, rate, pitch and volume GUI components based 
        on the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).
        """

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
        """Adjust the settings of the various components on the 
        configuration GUI depending upon the users preferences.
        """

        prefs = self.prefsDict

        # Speech pane.
        #
        enable = prefs["enableSpeech"]
        self.speechSupportCheckbutton.set_active(enable)
        self.speechTable.set_sensitive(enable)

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
        elif prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_MOST:
            self.mostButton.set_active(True)
        else:
            self.allButton.set_active(True)

        if prefs["speechVerbosityLevel"] == _("Brief"):
            self.speechBriefButton.set_active(True)
        else:
            self.speechVerboseButton.set_active(True)

        if prefs["readTableCellRow"] == True:
            self.rowSpeechButton.set_active(True)
        else:
            self.cellSpeechButton.set_active(True)

        self.speechIndentationCheckbutton.set_active(\
            prefs["enableSpeechIndentation"])

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

    def _getComboBoxIndex(self, combobox, str):
        """ For each of the entries in the given combo box, look for str.
            Return the index of the entry if str is found.
 
        Arguments:
        - combobox: the GtkComboBox to search.
        - str: the string to search for.
 
        Returns the index of the first entry in combobox with str, on 
        None if not found.
        """
 
        model = combobox.get_model()
        iter = model.get_iter_first()
        for i in range(0, len(model)):
            name = model.get_value(iter, 0)
            if name == str:
                return i
            iter = model.iter_next(iter)
 
        return None

    def _setupServers(self):
        """Get the list of speech servers for the current speech factory.
        If there aren't any servers, set the 'enableSpeech' to False and 
        return, otherwise get the information associated with each speech 
        server and add an entry for it to the speechServers GtkComboBox list.
        Set the current choice to be the first item.
        """

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

        debug.println(debug.LEVEL_FINEST, 
                      "orca_gui_prefs._init: serverChoices: %s" \
                      % self.serverChoices)
        debug.println(debug.LEVEL_FINEST, 
                      "orca_gui_prefs._init: server: %s" \
                      % self.server)

    def _setupVoices(self):
        """Get the list of voice families for the current speech server.
        If there aren't any voices, set the 'enableSpeech' to False and 
        return, otherwise get the information associated with each voice
        family and add an entry for it to the voices GtkComboBox list.
        If we are not doing graphics initialisation (i.e. the user has
        deliberately changed the current value in the voices combo box),
        then set the current choice to be the first item.
        """

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

        debug.println(debug.LEVEL_FINEST, 
                      "orca_gui_prefs._init: voiceChoices: %s" \
                      % self.voiceChoices)

    def _getVoiceForVoiceType(self, voiceType):
        """Return the dictionary of voice preferences for the given 
        voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).

        Returns the voice dictionary for the given voice type.
        """

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
        """Return the name of the voice family for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).

        Returns the name of the voice family for the given voice type,
        or None if not set.
        """

        familyName = None
        family = self._getKeyForVoiceType(voiceType, "family")

        if family:
            if family.has_key("name"):
                familyName = family["name"]

        return familyName

    def _setFamilyNameForVoiceType(self, voiceType, value):
        """Set the name of the voice family for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).
        - value: the name of the voice family to set.
        """

        family = self._getKeyForVoiceType(voiceType, "family", False)
        if family:
            family["name"] = value
        else:
            voice = self._getVoiceForVoiceType(voiceType)
            voice["family"] = {}
            voice["family"]["name"] = value

    def _getRateForVoiceType(self, voiceType):
        """Get the rate value for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).

        Returns the rate value for the given voice type, or None if 
        not set.
        """

        return self._getKeyForVoiceType(voiceType, "rate", True)

    def _setRateForVoiceType(self, voiceType, value):
        """Set the rate value for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).
        - value: the rate value to set.
        """

        voice = self._getVoiceForVoiceType(voiceType)
        voice["rate"] = value

    def _getPitchForVoiceType(self, voiceType):
        """Get the pitch value for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).

        Returns the pitch value for the given voice type, or None if
        not set.
        """

        return self._getKeyForVoiceType(voiceType, "average-pitch", True)

    def _setPitchForVoiceType(self, voiceType, value):
        """Set the pitch value for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).
        - value: the pitch value to set.
        """

        voice = self._getVoiceForVoiceType(voiceType)
        voice["average-pitch"] = value

    def _getVolumeForVoiceType(self, voiceType):
        """Get the volume (gain) value for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).

        Returns the volume (gain) value for the given voice type, or 
        None if not set.
        """

        return self._getKeyForVoiceType(voiceType, "gain", True)

    def _setVolumeForVoiceType(self, voiceType, value):
        """Set the volume (gain) value for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).
        - value: the volume (gain) value to set.
        """

        voice = self._getVoiceForVoiceType(voiceType)
        voice["gain"] = value

    def _setSystemChoice(self, factoryChoices, systemName):
        """Set the active item in the speech systems combo box to the
        given system name.

        Arguments:
        - factoryChoices: the list of available speech factories (systems).
        - value: the speech system name to use to set the active combo 
        box item.
        """

        model = self.speechSystemsModel
        i = 1
        for factory in factoryChoices.values():
            name = factory.__name__
            if name == systemName:
                self.speechSystems.set_active(i-1)
                return
            i += 1

    def _setServerChoice(self, serverChoices, serverName):
        """Set the active item in the speech servers combo box to the
        given server name.

        Arguments:
        - serverChoices: the list of available speech servers.
        - value: the speech server name to use to set the active combo
        box item.
        """

        model = self.speechServersModel
        i = 1
        for server in serverChoices.values():
            name = server.getInfo()[0]
            if name == serverName:
                self.speechServers.set_active(i-1)
                return
            i += 1

    def _setVoiceChoice(self, families, voiceName):
        """Set the active item in the voices combo box to the given 
        voice name.

        Arguments:
        - families: the list of available voice families.
        - value: the voice name to use to set the active combo box item.
        """

        model = self.voicesModel
        i = 1
        for family in families:
            name = family[speechserver.VoiceFamily.NAME]
            if name == voiceName:
                self.voices.set_active(i-1)
                return
            i += 1

    def _showGUI(self):
        """Show the Orca configuration GUI window. This assumes that
        the GUI has already been created.
        """

        # Set the current time on the Configuration GUI window so that it'll
        # get focus. set_user_time is a new call in pygtk 2.9.2 or later.
        # It's surronded by a try/except block here so that if it's not found,
        # then we can fail gracefully.
        #
        try:
            self.orcaSetupWindow.window.set_user_time(0)
        except AttributeError:
            debug.printException(debug.LEVEL_OFF)

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

        iter = widget.get_active_iter()
        model = widget.get_model()

        index = model.get_value(iter, 0)
        self.factory = self.factoryChoices[index]
        self.speechServersModel.clear()
        self._setupServers()

        self.server = self.serverChoices[1]
        self.voicesModel.clear()
        self._setupVoices()

    def speechServersChanged(self, widget):
        """Signal handler for the "changed" signal for the speechServers
           GtkComboBox widget. The user has selected a different speech
           server. Clear the existing list of voices, and setup a new 
           list of voices based on the new choice.

        Arguments:
        - widget: the component that generated the signal.
        """

        iter = widget.get_active_iter()
        model = widget.get_model()

        index = model.get_value(iter, 0)
        self.voicesModel.clear()
        self.server = self.serverChoices[index]
        self._setupVoices()

    def voiceFamilyChanged(self, widget):
        """Signal handler for the "value_changed" signal for the voices
           GtkComboBox widget. The user has selected a different voice
           family. Save the new voice family name based on the new choice.

        Arguments:
        - widget: the component that generated the signal.
        """

        iter = widget.get_active_iter()
        model = widget.get_model()

        name = model.get_value(iter, 1)
        voiceType = self.voiceType.get_active_text()
        self._setFamilyNameForVoiceType(voiceType, name)

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

    def voiceTypeChanged(self, widget):
        """Signal handler for the "changed" signal for the voiceType
           GtkComboBox widget. The user has selected a different voice
           type. Setup the new family, rate, pitch and volume component
           values based on the new choice.

        Arguments:
        - widget: the component that generated the signal.
        """

        voiceType = widget.get_active_text()
        self._setVoiceSettingForVoiceType(voiceType)

    def rateValueChanged(self, widget):
        """Signal handler for the "value_changed" signal for the rateScale
           GtkHScale widget. The user has changed the current rate value.
           Save the new rate value based on the currently selected voice
           type.

        Arguments:
        - widget: the component that generated the signal.
        """

        rate = widget.get_value()
        voiceType = self.voiceType.get_active_text()
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
        voiceType = self.voiceType.get_active_text()
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
        voiceType = self.voiceType.get_active_text()
        self._setVolumeForVoiceType(voiceType, volume)

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
            if widget.get_label() == _("_cell"):
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

    def helpButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the helpButton 
           GtkButton widget. The user has clicked the Help button.

        Arguments:
        - widget: the component that generated the signal.
        """

        print "Help not currently implemented."

    def cancelButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the cancelButton
           GtkButton widget. The user has clicked the Cancel button.
           Don't write out the preferences. Hide the configuration window.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.orcaSetupWindow.hide()

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

        self.prefsDict["enableSpeech"] = True
        self.prefsDict["speechServerFactory"] = self.factory
        self.prefsDict["speechServerInfo"] = self.server
        self.prefsDict["voices"] = {
            settings.DEFAULT_VOICE   : self.defaultVoice,
            settings.UPPERCASE_VOICE : self.uppercaseVoice,
            settings.HYPERLINK_VOICE : self.hyperlinkVoice
        }

        if orca_prefs.writePreferences(self.prefsDict):
            self._say(_("Accessibility support for GNOME has just been enabled."))
            self._say(_("You need to log out and log back in for the change to take effect."))

        for factory in self.workingFactories:
            factory.SpeechServer.shutdownActiveServers()
        orca.loadUserSettings()
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
