# Orca
#
# Copyright 2010 Consorcio Fernando de los Rios.
# Author: Javier Hernandez Antunez <jhernandez@emergya.es>
# Author: Alejandro Leiva <aleiva@emergya.es>
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

"""Displays a GUI for the Orca profiles window"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import os
import sys
import debug
import gtk
import locale

import orca_gtkbuilder
import orca_state
import orca_platform

OS = None
newProfile = None


class OrcaProfileGUI(orca_gtkbuilder.GtkBuilderWrapper):

    def __init__(self, fileName, windowName):
        """Initialize the Orca profile configuration GUI.

        Arguments:
        - fileName: name of the GtkBuilder file.
        - windowName: name of the component to get from the GtkBuilder file.
        """

        orca_gtkbuilder.GtkBuilderWrapper.__init__(self, fileName, windowName)

        # Initialize variables to None to keep pylint happy.
        #
        self.searchString = None
        self.profileString = None

    def init(self):
        # Initialize the dialog box controls.
        self.profileString = ""

    def showGUI(self):
        """Show the Orca profile dialog. This assumes that the GUI has
        already been created.
        """

        profileDialog = self.get_widget("profileDialog")

        # Set the current time on the Find GUI dialog so that it'll
        # get focus. set_user_time is a new call in pygtk 2.9.2 or later.
        # It's surronded by a try/except block here so that if it's not found,
        # then we can fail gracefully.
        #
        try:
            profileDialog.realize()
            ts = orca_state.lastInputEventTimestamp
            if ts == 0:
                ts = gtk.get_current_event_time()
            profileDialog.window.set_user_time(ts)
        except AttributeError:
            debug.printException(debug.LEVEL_FINEST)

        try:
            profileEntry = self.get_widget("profileEntry")
            profileEntry.set_text(self.profileString)
        except:
            pass

        profileDialog.run()

    def cancelButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the cancelButton
           GtkButton widget. The user has clicked the Cancel button.
           Hide the dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.get_widget("profileDialog").hide()

    def on_saveProfileButton_clicked(self, widget):
        """Signal handler for the "clicked" signal for the findButton
           GtkButton widget. The user has clicked the Find button.
           Call the method to begin the search.

        Arguments:
        - widget: the component that generated the signal.
        """

        # Merely hiding the dialog causes the find to take place before
        # the original window has fully regained focus.
        global newProfile

        if self.get_widget("profileEntry").get_text() != '':
            newProfile = self.get_widget("profileEntry").get_text()
            self.get_widget("profileDialog").destroy()


    # From now, this method can't have sense ...
    def onProfileEntryChanged(self, widget, data=None):
        """Signal handler for the "changed" signal for the ProfileEntry
           GtkEntry widget."""

        if self.get_widget("profileEntry").get_text() != '':
            self.get_widget('availableProfilesCombo').set_sensitive(False)
        else:
            self.get_widget('availableProfilesCombo').set_sensitive(True)


    def profileDialogDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the findDialog
           GtkWindow widget. Reset OS to None.

        Arguments:
        - widget: the component that generated the signal.
        """

        global OS

        OS = None

    def __getAvailableProfiles(self):
        """Get available user profiles"""

        import orca

        _settingsManager = getattr(orca, '_settingsManager')

        return _settingsManager.availableProfiles()

def showProfileUI():
    global OS
    global newProfile

    newProfile = None

    if not OS:
        uiFile = os.path.join(orca_platform.prefix,
                              orca_platform.datadirname,
                              orca_platform.package,
                              "ui",
                              "orca-profile.ui")
        OS = OrcaProfileGUI(uiFile, "profileDialog")
        OS.init()

    OS.showGUI()

    return newProfile
 

def main():
    locale.setlocale(locale.LC_ALL, '')

    showProfileUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
