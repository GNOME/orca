# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""Displays a GUI for the user to quit Orca."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import locale
import sys
from gi.repository import Gtk

from . import orca
from . import orca_state
from . import settings
from .orca_i18n import _

OS = None

class OrcaQuitGUI(Gtk.MessageDialog):

    def __init__(self):
        Gtk.MessageDialog.__init__(self)
        self.set_property('message-type', Gtk.MessageType.QUESTION)

        self.set_property('text', _('Quit Orca?'))
        self.format_secondary_text(
            _('This will stop all speech and braille output.'))

        self.add_button('gtk-cancel', Gtk.ResponseType.CANCEL)
        self.add_button('gtk-quit', Gtk.ResponseType.ACCEPT)

        self.connect('response', self.onResponse)
        self.connect('destroy', self.onDestroy)

    def init(self):
        pass

    def showGUI(self):
        """Show the Quit dialog."""

        ts = orca_state.lastInputEventTimestamp
        if ts == 0:
            ts = Gtk.get_current_event_time()
        self.present_with_time(ts)

    def onResponse(self, widget, response):
        """Signal handler for the responses emitted by the dialog."""

        if response == Gtk.ResponseType.ACCEPT:
            orca.shutdown()
            return

        if response in [Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT]:
            self.hide()
            if settings.showMainWindow:
                orca.showMainWindowGUI()

    def onDestroy(self, widget):
        """Signal handler for the 'destroy' signal of the dialog."""

        global OS

        OS = None

def showQuitUI():
    global OS

    if not OS:
        OS = OrcaQuitGUI()
        OS.init()

    OS.showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showQuitUI()

    Gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
