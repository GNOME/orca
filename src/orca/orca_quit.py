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

"""Displays a GUI for the user to quit Orca."""

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

class orcaQuitGUI(orca_glade.GladeWrapper):

    def _init(self):
        pass

    def _showGUI(self):
        """Show the Orca quit GUI dialog. This assumes that the GUI has 
        already been created.
        """

        # Set the current time on the quit GUI dialog so that it'll
        # get focus. set_user_time is a new call in pygtk 2.9.2 or later.
        # It's surronded by a try/except block here so that if it's not found,
        # then we can fail gracefully.
        #
        try:
            self.quitDialog.realize()
            self.quitDialog.window.set_user_time(\
                orca_state.lastInputEventTimestamp)
        except AttributeError:
            debug.printException(debug.LEVEL_FINEST)

        self.quitDialog.show()

    def quitNoButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the quitNoButton
           GtkButton widget. The user has clicked the No button.
           Don't quit Orca. Just hide the quit dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.quitDialog.hide()

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
           from the Glade file the next time the user wants to display the
           quit dialog GUI.

        Arguments:
        - widget: the component that generated the signal.
        """

        global OS

        OS = None

def showQuitUI():
    global OS

    if not OS:
        gladeFile = os.path.join(platform.prefix,
                                 platform.datadirname,
                                 platform.package,
                                 "glade",
                                 "orca-quit.glade")
        OS = orcaQuitGUI(gladeFile, "quitDialog")
        OS._init()

    OS._showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showQuitUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
