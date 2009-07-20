# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""Displays a GUI for the user to quit Orca."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import os
import sys
import debug
import gtk
import locale

import orca
import orca_gtkbuilder
import orca_state
import platform
import settings

OS = None

class OrcaQuitGUI(orca_gtkbuilder.GtkBuilderWrapper):

    def init(self):
        pass

    def showGUI(self):
        """Show the Orca quit GUI dialog. This assumes that the GUI has 
        already been created.
        """

        quitDialog = self.get_widget("quitDialog")

        # Set the current time on the quit GUI dialog so that it'll
        # get focus. set_user_time is a new call in pygtk 2.9.2 or later.
        # It's surronded by a try/except block here so that if it's not found,
        # then we can fail gracefully.
        #
        try:
            quitDialog.realize()
            ts = orca_state.lastInputEventTimestamp
            if ts == 0:
                ts = gtk.get_current_event_time()
            quitDialog.window.set_user_time(ts)
        except AttributeError:
            debug.printException(debug.LEVEL_FINEST)

        quitDialog.hide()
        quitDialog.show()

    def quitNoButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the quitNoButton
           GtkButton widget. The user has clicked the No button.
           Don't quit Orca. Just hide the quit dialog and recreate the
           Orca main window.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.get_widget("quitDialog").hide()
        if settings.showMainWindow:
            orca.showMainWindowGUI()

    def quitYesButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the quitYesButton
           GtkButton widget. The user has clicked the Yes button.
           Call the orca.shutdown() method to gracefully terminate Orca.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca.shutdown()

    def quitDialogDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the quitDialog
           GtkWindow widget. Reset OS to None, so that the GUI can be rebuilt
           from the GtkBuilder file the next time the user wants to display
           the quit dialog GUI.

        Arguments:
        - widget: the component that generated the signal.
        """

        global OS

        OS = None

def showQuitUI():
    global OS

    if not OS:
        uiFile = os.path.join(platform.prefix,
                              platform.datadirname,
                              platform.package,
                              "ui",
                              "orca-quit.ui")
        OS = OrcaQuitGUI(uiFile, "quitDialog")
        OS.init()

    OS.showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showQuitUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
