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

"""Displays the Save Profile As dialog."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import locale
import sys
import time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import guilabels

OS = None
newProfile = None

class OrcaProfileGUI(Gtk.Dialog):

    def __init__(self):
        """Initialize the Orca profile configuration GUI."""

        Gtk.Dialog.__init__(self)
        self.set_title(guilabels.PROFILE_SAVE_AS_TITLE)
        self.set_has_resize_grip(False)

        self.add_button('gtk-cancel', Gtk.ResponseType.CANCEL)
        self.add_button('gtk-save', Gtk.ResponseType.ACCEPT)

        grid = Gtk.Grid()
        grid.set_property('margin', 12)
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)

        # Right now the content area is a GtkBox. We'll need to update
        # this once GtkBox is fully deprecated.
        contentArea = self.get_content_area()
        contentArea.pack_start(grid, True, True, 0)

        self.profileEntry = Gtk.Entry()
        self.profileEntry.set_property('hexpand', True)
        self.profileEntry.set_activates_default(True)
        grid.attach(self.profileEntry, 1, 0, 1, 1)

        label = Gtk.Label(guilabels.PROFILE_NAME_LABEL)
        label.set_use_underline(True)
        label.set_mnemonic_widget(self.profileEntry)
        grid.attach(label, 0, 0, 1, 1)

        defaultButton = self.get_widget_for_response(Gtk.ResponseType.ACCEPT)
        defaultButton.set_property('can-default', True)
        defaultButton.set_property('has-default', True)

        self.connect('response', self.onResponse)
        self.connect('destroy', self.onDestroy)

        self.searchString = None
        self.profileString = None
        self.prefsDialog = None

    def init(self):
        self.profileString = ''

    def showGUI(self, prefsDialog):
        """Show the Save Profile As dialog."""

        self.show_all()
        self.prefsDialog = prefsDialog
        self.profileEntry.set_text(self.profileString)
        self.present_with_time(time.time())

    def onResponse(self, widget, response):
        """Signal handler for the responses emitted by the dialog."""

        if response in [Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT]:
            self.hide()
            return

        if response == Gtk.ResponseType.ACCEPT:
            global newProfile

            newProfile = self.profileEntry.get_text()
            if newProfile:
                self.destroy()
            if self.prefsDialog:
                self.prefsDialog.saveProfile(newProfile)

    def onDestroy(self, widget):
        """Signal handler for the 'destroy' signal of the dialog."""

        global OS

        OS = None

def showProfileUI(prefsDialog=None):
    global OS
    global newProfile

    newProfile = None

    if not OS:
        OS = OrcaProfileGUI()
        OS.init()

    OS.showGUI(prefsDialog)

def main():
    locale.setlocale(locale.LC_ALL, '')

    showProfileUI()

    Gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
