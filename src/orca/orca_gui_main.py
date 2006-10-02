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

"""Displays a GUI for the Orca main window."""

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

import orca
import orca_glade
import orca_state
import platform

from orca_i18n import _  # for gettext support

OS = None

class orcaMainGUI(orca_glade.GladeWrapper):

    def _init(self):
        pass

    def _setMainWindowIcon(self):
        """Set the "orca.png" icon as the icon for the Orca main window."""

        icon_theme = gtk.icon_theme_get_default()
        try:
            icon = icon_theme.load_icon("orca", 48, 0)
        except:
            return

        self.mainWindow.set_icon(icon)

    def _showGUI(self):
        """Show the Orca main window GUI. This assumes that the GUI has 
        already been created.
        """

        self._setMainWindowIcon()
        self.mainWindow.show()

    def quitButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the quitButton
           GtkButton widget. The user has clicked the Quit button.
           Call the method to bring up the Quit dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca._showQuitGUI()

    def preferencesButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the preferencesButton
           GtkButton widget. The user has clicked the Preferences button.
           Call the method to bring up the Preferences dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca._showPreferencesGUI()

    def mainWindowDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the mainWindow
           GtkWindow widget. Reset OS to None, then call the method to 
           bring up the quit dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        global OS

        OS = None
        orca._showQuitGUI()

def showMainUI():
    global OS

    if not OS:
        gladeFile = os.path.join(platform.prefix,
                                 platform.datadirname,
                                 platform.package,
                                 "glade",
                                 "orca-mainwin.glade")
        OS = orcaMainGUI(gladeFile, "mainWindow")
        OS._init()

    OS._showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showMainUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
