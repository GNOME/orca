# Orca
#
# Copyright 2010 Consorcio Fernando de los Rios.
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
"""Splash screen window."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import os
import sys
from . import debug
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject
import locale

from . import orca_state
from . import orca_platform
from .orca_i18n import _

OS = None

class OrcaSplashGUI(Gtk.Window):

    def __init__(self):
        """Initialize the Orca splash GUI."""

        Gtk.Window.__init__(self)
        self.activeScript = None
        self.set_title(_('Orca'))
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_modal(True)
        self.set_decorated(False)
        self.set_type_hint(Gdk.WindowTypeHint.SPLASHSCREEN)
        self.set_position(Gtk.WindowPosition.CENTER)

    def init(self):
        """Initialize the splash screen."""

        self.activeScript = orca_state.activeScript

    def showGUI(self):
        """Show the splash screen dialog."""

        imageFile = os.path.join(orca_platform.prefix,
                    orca_platform.datadirname,
                    orca_platform.package,
                    "gfx",
                    "orca-splash.png")

        image = Gtk.Image()
        image.set_from_file(imageFile)

        self.add(image)

        try:
            self.realize()
        except:
            debug.printException(debug.LEVEL_FINEST)

        self.set_transient_for(None)
        self.grab_focus()
        self.show_all()

        GObject.timeout_add(3000, self.hideGUI)

        while Gtk.events_pending():
            Gtk.main_iteration()

        return self

    def hideGUI(self):
        """Hide the Orca splash screen GUI. This assumes that the GUI has
        already been created.
        """

        self.hide()

def showSplashUI():
    global OS

    if not OS:
        OS = OrcaSplashGUI()
        OS.init()

    OS.showGUI()

def hideSplashUI():
    if OS:
        OS.hideGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showSplashUI()

    Gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
