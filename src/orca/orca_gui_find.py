# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Displays a GUI for the Orca Find window"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import os
import sys
from gi.repository import Gtk
import locale

from . import find
from . import guilabels
from . import orca_gtkbuilder
from . import orca_state
from . import orca_platform

OS = None

class OrcaFindGUI(orca_gtkbuilder.GtkBuilderWrapper):

    def __init__(self, fileName, windowName):
        """Initialize the Orca configuration GUI.

        Arguments:
        - fileName: name of the GtkBuilder file.
        - windowName: name of the component to get from the GtkBuilder file.
        """

        orca_gtkbuilder.GtkBuilderWrapper.__init__(self, fileName, windowName)

        # Initialize variables to None to keep pylint happy.
        #
        self.activeScript = None
        self.caseSensitive = None
        self.matchEntireWord = None
        self.searchBackwards = None
        self.searchString = None
        self.startAtTop = None
        self.windowWrap = None

    def init(self):
        # Initialize the dialog box controls.
        self.searchString = ""
        self.searchBackwards = False
        self.caseSensitive = False
        self.matchEntireWord = False
        self.windowWrap = True
        self.startAtTop = False

        self.activeScript = orca_state.activeScript

    def showGUI(self):
        """Show the Orca Find dialog. This assumes that the GUI has
        already been created.
        """

        findDialog = self.get_widget("findDialog")
        ts = orca_state.lastInputEvent.timestamp
        if ts == 0:
            ts = Gtk.get_current_event_time()
        findDialog.present_with_time(ts)

        # Populate the dialog box from the previous searchQuery, should
        # one exist.  Note:  This is necessary because we are destroying
        # the dialog (rather than merely hiding it) before performing the
        # search.

        try:
            searchForEntry = self.get_widget("searchForEntry")
            searchForEntry.set_text(orca_state.searchQuery.searchString)
            searchForEntry.select_region(0, len(searchForEntry.get_text()))
            if orca_state.searchQuery.startAtTop:
                self.get_widget("topRadioButton").set_active(True)
            self.get_widget("matchCaseCheckbox").set_active(\
                orca_state.searchQuery.caseSensitive)
            self.get_widget("matchEntireWordCheckbox").set_active(\
                orca_state.searchQuery.matchEntireWord)
            self.get_widget("wrapAroundCheckbox").set_active(\
                orca_state.searchQuery.windowWrap)
            self.get_widget("searchBackwardsCheckbox").set_active(\
                orca_state.searchQuery.searchBackwards)
        except:
            pass

    def searchForEntryChanged(self, widget):
        """Signal handler for the "changed" signal for the
           searchForEntry GtkEntry widget. The user has changed
           the string to be searched for.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.searchString = widget.get_text()
        findButton = self.get_widget("findButton")
        if len(self.searchString) > 0:
            findButton.set_sensitive(True)
        else:
            findButton.set_sensitive(False)

    def startingPointChanged(self, widget):
        """Signal handler for the "toggled" signal for the
           currentLocationRadioButton or topRadioButton GtkRadioButton
           widgets. The user has toggled the starting point for the search.

        Arguments:
        - widget: the component that generated the signal.
        """

        if widget.get_active():
            if widget.get_label() == guilabels.FIND_START_AT_CURRENT_LOCATION:
                self.startAtTop = False
            else:
                self.startAtTop = True

    def matchCaseChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           matchCaseCheckbox GtkCheckButton widget. The user has
           [un]checked the "Match Case" checkbox.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.caseSensitive = widget.get_active()

    def matchEntireWordChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           matchEntireWordCheckbox GtkCheckButton widget.
           The user has [un]checked the "Match entire word"
           checkbox.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.matchEntireWord = widget.get_active()

    def searchBackwardsChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           searchBackwardsCheckbox GtkCheckButton widget.
           The user has [un]checked the "Search backwards"
           checkbox.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.searchBackwards = widget.get_active()

    def wrapAroundChecked(self, widget):
        """Signal handler for the "toggled" signal for the
           wrapAroundCheckbox GtkCheckButton widget. The user has
           [un]checked the "Wrap around" checkbox.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.windowWrap = widget.get_active()

    def closeButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the cancelButton
           GtkButton widget. The user has clicked the Cancel button.
           Hide the dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        self.get_widget("findDialog").hide()

    def findButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the findButton
           GtkButton widget. The user has clicked the Find button.
           Call the method to begin the search.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca_state.searchQuery = find.SearchQuery()
        orca_state.searchQuery.searchString = self.searchString
        orca_state.searchQuery.searchBackwards = self.searchBackwards
        orca_state.searchQuery.caseSensitive = self.caseSensitive
        orca_state.searchQuery.matchEntireWord = self.matchEntireWord
        orca_state.searchQuery.startAtTop = self.startAtTop
        orca_state.searchQuery.windowWrap = self.windowWrap

        self.activeScript.findCommandRun = True

        # Merely hiding the dialog causes the find to take place before
        # the original window has fully regained focus.
        self.get_widget("findDialog").destroy()


    def findDialogDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the findDialog
           GtkWindow widget. Reset OS to None.

        Arguments:
        - widget: the component that generated the signal.
        """

        global OS

        OS = None

def showFindUI():
    global OS

    if not OS:
        uiFile = os.path.join(orca_platform.datadir,
                              orca_platform.package,
                              "ui",
                              "orca-find.ui")
        OS = OrcaFindGUI(uiFile, "findDialog")
        OS.init()

    OS.showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showFindUI()

    Gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
