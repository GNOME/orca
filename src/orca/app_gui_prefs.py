# Orca
#
# Copyright 2007 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or# modify it under the terms of the GNU Library General Public
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

"""Displays a GUI for the user to set Orca application-specific preferences."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2007 Sun Microsystems Inc."
__license__   = "LGPL"

import gettext
import gtk
import locale
import os
import sys

import app_prefs
import braille
import debug
import default
import focus_tracking_presenter
import input_event
import keybindings
import orca_gui_prefs
import orca_prefs
import orca_state
import platform
import settings
import speech

from orca_i18n import _  # for gettext support

applicationName = None
appScript = None
OS = None

class orcaSetupGUI(orca_gui_prefs.orcaSetupGUI):

    def _initAppGUIState(self, appScript):
        """Before we show the GUI to the user we want to remove the
        General tab and gray out the Speech systems and servers 
        controls on the speech tab.

        Arguments:
        - appScript: the application script.
        """

        # Save away the application script so that it can be used later
        # by writeUserPreferences().
        #
        self.appScript = appScript

        self.notebook.remove_page(0)
        self.speechSystemsLabel.set_sensitive(False)
        self.speechSystems.set_sensitive(False)
        self.speechServersLabel.set_sensitive(False)
        self.speechServers.set_sensitive(False)

        vbox = appScript.getAppPreferencesGUI()
        if vbox:
            label = gtk.Label(orca_state.locusOfFocus.app.name)
            self.notebook.append_page(vbox, label)

    def _createPronunciationTreeView(self, pronunciations=None):
        """Create the pronunciation dictionary tree view for this specific 
        application. We call the super class method passing in the 
        application specific pronunciation dictionary.

        Arguments:
        - pronunciations: an optional dictionary used to get the
          pronunciation from.
        """

        orca_gui_prefs.orcaSetupGUI._createPronunciationTreeView( \
                              self, appScript.app_pronunciation_dict)

    def _showGUI(self):
        """Show the app-specific Orca configuration GUI window. This 
        assumes that the GUI has already been created.
        """

        # Adjust the title of the app-specific Orca Preferences dialog to
        # include the name of the application.
        #
        self.app = orca_state.locusOfFocus.app
        self.applicationName = self.app.name 
        title = _("Orca Preferences for %s") % self.applicationName
        self.orcaSetupWindow.set_title(title)

        orca_gui_prefs.orcaSetupGUI._showGUI(self)

    def writeUserPreferences(self):
        """Write out the user's application-specific Orca preferences.
        """
        moduleName = settings.getScriptModuleName(self.app)
        app_prefs.writePreferences(self.prefsDict, moduleName,
                                   self.appScript, self.keyBindingsModel,
                                   self.pronunciationModel)
        ftp = focus_tracking_presenter.FocusTrackingPresenter()
        ftp.loadAppSettings(self.appScript)

    def _markModified(self):
        """ Mark as modified the user application specific custom key bindings:
        """

        global appScript

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

        global applicationName, appScript

        # Get the key bindings for the application script.
        #
        self.appKeyBindings = appScript.getKeyBindings()
        self.appKeyBindings = appScript.overrideAppKeyBindings(appScript, 
                                                     self.appKeyBindings)

        # Get the key bindings for the default script.
        #
        defScript = default.Script(None)
        self.defKeyBindings = defScript.getKeyBindings()

        nodeCreated = False

        # Find the key bindings that are in the application script but 
        # not in the default script.
        #
        for kb in self.appKeyBindings.keyBindings:
            if not self.defKeyBindings.hasKeyBinding(kb, "strict"):
                if not self._addAlternateKeyBinding(kb):
                    handl = appScript.getInputEventHandlerKey(kb.handler)
                    if not nodeCreated:
                        iterOrca = self._createNode(applicationName)
                        nodeCreated = True
                    self._insertRow(handl, kb, iterOrca)

        # Call the parent class to add in the default key bindings.
        #
        orca_gui_prefs.orcaSetupGUI._populateKeyBindings(self, False)


    def okButtonClicked(self, widget):
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
        self.orcaSetupWindow.destroy()

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
    global applicationName, appScript, OS

    # There must be an application with focus for this to work.
    #
    if not orca_state.locusOfFocus or not orca_state.locusOfFocus.app:
        message = _("No application has focus.")
        braille.displayMessage(message)
        speech.speak(message)
        return

    appScript = orca_state.activeScript

    # The name of the application that currently has focus.
    #
    applicationName = orca_state.locusOfFocus.app.name

    # Translators: Orca Preferences in this case, is a configuration GUI 
    # for allowing users to set application specific settings from within
    # Orca for the application that currently has focus.
    #
    line = _("Starting Orca Preferences for %s. This may take a while.") % \
           applicationName
    braille.displayMessage(line)
    speech.speak(line)

    removeGeneralPane = False
    if not OS:
        gladeFile = os.path.join(platform.prefix,
                                 platform.datadirname,
                                 platform.package,
                                 "glade",
                                 "orca-setup.glade")
        OS = orcaSetupGUI(gladeFile, "orcaSetupWindow")
        removeGeneralPane = True

    OS._init()
    if removeGeneralPane:
        OS._initAppGUIState(appScript)
    OS._showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showPreferencesUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
