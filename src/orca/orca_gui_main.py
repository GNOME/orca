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

"""Displays a GUI for the Orca main window."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import os
import sys
import gtk
import locale

import orca
import orca_gtkbuilder
import platform

OS = None

class OrcaMainGUI(orca_gtkbuilder.GtkBuilderWrapper):

    def init(self):
        pass

    def showGUI(self):
        """Show the Orca main window GUI. This assumes that the GUI has 
        already been created.
        """

        mainWindow = self.get_widget("mainWindow")

        accelGroup = gtk.AccelGroup()
        mainWindow.add_accel_group(accelGroup)
        helpButton = self.get_widget("helpButton")
        (keyVal, modifierMask) = gtk.accelerator_parse("F1")
        helpButton.add_accelerator("clicked",
                                   accelGroup,
                                   keyVal,
                                   modifierMask,
                                   0)

        mainWindow.show()

    def hideGUI(self):
        """Hide the Orca main window GUI. This assumes that the GUI has
        already been created.
        """

        self.get_widget("mainWindow").hide()

    def helpButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the helpButton
           GtkButton widget. The user has clicked the Help button.
           Call the method to bring up the Orca help window.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca.helpForOrca()

    def quitButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the quitButton
           GtkButton widget. The user has clicked the Quit button.
           Call the method to bring up the Quit dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca.quitOrca()

    def preferencesButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the preferencesButton
           GtkButton widget. The user has clicked the Preferences button.
           Call the method to bring up the Preferences dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca.showPreferencesGUI()

    def mainWindowDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the mainWindow
           GtkWindow widget. Reset OS to None, then call the method to 
           bring up the quit dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        global OS

        OS = None
        orca.quitOrca()

def showMainUI():
    global OS

    if not OS:
        uiFile = os.path.join(platform.prefix,
                              platform.datadirname,
                              platform.package,
                              "ui",
                              "orca-mainwin.ui")
        OS = OrcaMainGUI(uiFile, "mainWindow")
        OS.init()

    OS.showGUI()

def hideMainUI():
    if OS:
        OS.hideGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showMainUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
