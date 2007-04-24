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

import braille
import orca_gui_prefs
import orca_prefs
import orca_state
import platform
import settings
import speech

from orca_i18n import _  # for gettext support

OS = None

class orcaSetupGUI(orca_gui_prefs.orcaSetupGUI):

    def _initAppGUIState(self):
        """Before we show the GUI to the user we want to remove the
        General tab and gray out the Speech systems and servers 
        controls on the speech tab.
        """

        self.notebook.remove_page(0)
        self.speechSystemsLabel.set_sensitive(False)
        self.speechSystems.set_sensitive(False)
        self.speechServersLabel.set_sensitive(False)
        self.speechServers.set_sensitive(False)

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
        orca_prefs.writeAppPreferences(self.prefsDict, moduleName,
                                       self.keyBindingsModel)

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
    global OS

    # There must be an application with focus for this to work.
    #
    if not orca_state.locusOfFocus or not orca_state.locusOfFocus.app:
        message = _("No application has focus.")
        braille.displayMessage(message)
        speech.speak(message)
        return

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
        OS._initAppGUIState()
    OS._showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showPreferencesUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
