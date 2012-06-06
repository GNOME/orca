# Orca
#
# Copyright 2007-2009 Sun Microsystems Inc.
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

"""Displays a GUI for the user to set Orca application-specific preferences."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2007-2009 Sun Microsystems Inc."
__license__   = "LGPL"

from gi.repository import Gtk
import locale
import os
import sys

from . import app_prefs
from . import braille
from . import debug
from . import input_event
from . import keybindings
from . import orca_gui_prefs
from . import orca_state
from . import orca_platform
from . import script_manager
from . import settings_manager
from . import settings
from . import speech
from .orca_i18n import _

_scriptManager = script_manager.getManager()
_settingsManager = settings_manager.getManager()

applicationName = None
appScript = None

class OrcaSetupGUI(orca_gui_prefs.OrcaSetupGUI):

    def __init__(self, fileName, windowName, prefsDict = None):
        """Initialize the application specific Orca configuration GUI.

        Arguments:
        - fileName: name of the GtkBuilder file.
        - windowName: name of the component to get from the GtkBuilder file.
        """

        orca_gui_prefs.OrcaSetupGUI.__init__(self, fileName, 
                                             windowName, prefsDict)

        # Initialize variables to None to keep pylint happy.
        #
        self.applicationName = None
        self.appScript = None
        self.app = None
        self.kbindings = None
        self.appKeyBindings = None
        self.defKeyBindings = None

    def _getGeneralSettings(self, prefsDict):
        if prefsDict is None:
            return orca_gui_prefs.OrcaSetupGUI.\
                _getGeneralSettings(self, prefsDict)

        return prefsDict

    def initAppGUIState(self, thisAppScript):
        """Before we show the GUI to the user we want to remove the
        General tab and gray out the Speech systems and servers 
        controls on the speech tab.

        Arguments:
        - thisAppScript: the application script.
        """

        # Save away the application script so that it can be used later
        # by writeUserPreferences().
        #
        self.appScript = thisAppScript

        # Don't remove the page because this tickles some strange bug
        # in gail or gtk+ (see bug #554002).  Instead, we'll just hide it.
        #
        # self.get_widget("notebook").remove_page(0)
        self.get_widget("generalGrid").hide()

        self.get_widget("speechSystemsLabel").set_sensitive(False)
        self.get_widget("speechSystems").set_sensitive(False)
        self.get_widget("speechServersLabel").set_sensitive(False)
        self.get_widget("speechServers").set_sensitive(False)

        appPage = self.appScript.getAppPreferencesGUI()
        if appPage:
            label = Gtk.Label(label=orca_state.activeScript.app.name)
            self.get_widget("notebook").append_page(appPage, label)

    def _createPronunciationTreeView(self, pronunciations=None):
        """Create the pronunciation dictionary tree view for this specific 
        application. We call the super class method passing in the 
        application specific pronunciation dictionary.

        Arguments:
        - pronunciations: an optional dictionary used to get the
          pronunciation from.
        """

        orca_gui_prefs.OrcaSetupGUI._createPronunciationTreeView( \
                              self, appScript.app_pronunciation_dict)

    def showGUI(self):
        """Show the app-specific Orca configuration GUI window. This 
        assumes that the GUI has already been created.
        """

        # Adjust the title of the app-specific Orca Preferences dialog to
        # include the name of the application.
        #
        self.app = orca_state.activeScript.app
        self.applicationName = self.app.name 
        title = _("Orca Preferences for %s") % self.applicationName
        self.get_widget("orcaSetupWindow").set_title(title)

        orca_gui_prefs.OrcaSetupGUI.showGUI(self)

    def writeUserPreferences(self):
        """Write out the user's application-specific Orca preferences.
        """
        moduleName = _scriptManager.getModuleName(self.app)
        app_prefs.writePreferences(self.prefsDict, moduleName,
                                   self.appScript, self.keyBindingsModel,
                                   self.pronunciationModel)
        _settingsManager.loadAppSettings(self.appScript)

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

        return self.appScript.getAppNameForAttribute(attributeName)

    def _markModified(self):
        """ Mark as modified the user application specific custom key bindings:
        """

        try:
            appScript.setupInputEventHandlers()
            keyBinds = keybindings.KeyBindings()
            keyBinds = appScript.overrideAppKeyBindings(appScript, keyBinds)
            keyBind = keybindings.KeyBinding(None, None, None, None)
            treeModel = self.keyBindingsModel

            myiter = treeModel.get_iter_first()
            while myiter != None:
                iterChild = treeModel.iter_children(myiter)
                while iterChild != None:
                    descrip = treeModel.get_value(iterChild, 
                                                  orca_gui_prefs.DESCRIP)
                    keyBind.handler = input_event.InputEventHandler(None,
                                                                    descrip)
                    if keyBinds.hasKeyBinding(keyBind,
                                              typeOfSearch="description"):
                        treeModel.set_value(iterChild, 
                                            orca_gui_prefs.MODIF, True)
                    iterChild = treeModel.iter_next(iterChild)
                myiter = treeModel.iter_next(myiter)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def _populateKeyBindings(self, clearModel=True):
        """Fills the TreeView with the list of Orca keybindings. The
        application specific ones are prepended to the list.

        Arguments:        
        - clearModel: if True, initially clear out the key bindings model. 
        """

        if clearModel:
            self.keyBindingsModel.clear()

        # Get the key bindings for the application script.
        #
        self.appKeyBindings = appScript.getKeyBindings()
        self.appKeyBindings = appScript.overrideAppKeyBindings(appScript, 
                                                     self.appKeyBindings)

        # Get the key bindings for the default script.
        #
        defScript = _scriptManager.getDefaultScript()
        self.defKeyBindings = defScript.getKeyBindings()

        iterApp = self._createNode(applicationName)
        iterOrca = self._createNode(_("Orca"))

        # Translators: this refers to commands that do not currently have
        # an associated key binding.
        #
        iterUnbound = self._createNode(_("Unbound"))

        # Find the key bindings that are in the application script but 
        # not in the default script.
        #
        for kb in self.appKeyBindings.keyBindings:
            if not self.defKeyBindings.hasKeyBinding(kb, "description"):
                node = iterApp
            elif kb.keysymstring:
                node = iterOrca
            else:
                node = iterUnbound
            handl = appScript.getInputEventHandlerKey(kb.handler)
            self._insertRow(handl, kb, node)

        if not self.keyBindingsModel.iter_has_child(iterApp):
            self.keyBindingsModel.remove(iterApp)

        # Call the parent class to add braille bindings and finish
        # setting up the tree view.
        #
        self.kbindings = self.appKeyBindings
        orca_gui_prefs.OrcaSetupGUI._populateKeyBindings(self, False)

    def okButtonClicked(self, widget=None):
        """Signal handler for the "clicked" signal for the okButton
           GtkButton widget. The user has clicked the OK button.
           Write out the users preferences. If GNOME accessibility hadn't
           previously been enabled, warn the user that they will need to
           log out. Shut down any active speech servers that were started.
           Reload the users preferences to get the new speech, braille and
           key echo value to take effect. Destroy the configuration window.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.applyButtonClicked(widget)
        self.get_widget("orcaSetupWindow").destroy()

    def windowDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the orcaSetupWindow
           GtkWindow widget. Reset orca_state.appOS to None, so that the 
           GUI can be rebuilt from the GtkBuilder file the next time the user
           wants to display the configuration GUI.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca_state.appOS = None

def showPreferencesUI():
    global applicationName, appScript

    # There must be an application with focus for this to work.
    #
    if not orca_state.locusOfFocus or \
       not orca_state.locusOfFocus.getApplication():
        message = _("No application has focus.")
        braille.displayMessage(message)
        speech.speak(message)
        return

    appScript = orca_state.activeScript

    # The name of the application that currently has focus.
    #
    applicationName = orca_state.activeScript.app.name
    if not orca_state.appOS and not orca_state.orcaOS:
        # Translators: Orca Preferences in this case, is a configuration GUI
        # for allowing users to set application specific settings from within
        # Orca for the application that currently has focus.
        #
        line = _("Starting Orca Preferences for %s.") % applicationName
        appScript.presentMessage(line)

        prefsDict = {}
        for key in settings.userCustomizableSettings:
            prefsDict[key] = _settingsManager.getSetting(key)

        orca_state.prefsUIFile = \
            os.path.join(orca_platform.prefix,
                         orca_platform.datadirname,
                         orca_platform.package,
                         "ui",
                         "orca-setup.ui")

        orca_state.appOS = \
            OrcaSetupGUI(orca_state.prefsUIFile, "orcaSetupWindow", prefsDict)
        orca_state.appOS.initAppGUIState(appScript)

        orca_state.appOS.init()
        orca_state.appOS.showGUI()
    else:
        if not orca_state.orcaWD:
            orca_state.orcaWD = orca_gui_prefs.WarningDialogGUI()
        orca_state.orcaWD.showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showPreferencesUI()

    Gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
