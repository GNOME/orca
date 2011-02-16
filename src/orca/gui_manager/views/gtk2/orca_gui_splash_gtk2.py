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
import gtk
import gobject
import locale

from orca import orca_gtkbuilder
from orca import orca_state
from orca import orca_platform
from orca import debug
from orca.orca_i18n import _           # for gettext support
from orca.gui_manager.abstract_view import AbstractView

OS = None

class OrcaSplashGUI(orca_gtkbuilder.GtkBuilderWrapper, AbstractView):

    def __init__(self, fileName, windowName):
        """
        Initialize the Orca splash GUI.

        Arguments:
        - fileName: name of the GtkBuilder file.
        - windowName: name of the component to get from the GtkBuilder file.
        """

        orca_gtkbuilder.GtkBuilderWrapper.__init__(self, fileName, windowName)

    def init(self):
        """ Initialize the splash screen dialog. """

        self.activeScript = orca_state.activeScript

    def showGUI(self):
        """ Show the splash screen dialog. """

        imageFile = os.path.join(orca_platform.prefix,
                    orca_platform.datadirname,
                    orca_platform.package,
                    "gui_manager",
                    "views",
                    orca_platform.library,
                    "gfx",
                    "orca-splash.png")

        image = gtk.Image()
        image.set_from_file(imageFile)

        splashScreen = self.get_widget("splashWindow")
        box = self.get_widget("splash_vbox")
        box.pack_start(image, True, True)

        try:
            splashScreen.realize()
        except:
            debug.printException(debug.LEVEL_FINEST)

        splashScreen.set_transient_for(None)
        box.grab_focus()
        splashScreen.show_all()

        while gtk.events_pending():
            gtk.main_iteration()

        gobject.timeout_add(3000, splashScreen.hide)

        return splashScreen

    def hideGUI(self):
        """Hide the Orca splash screen GUI. This assumes that the GUI has
        already been created.
        """

        self.get_widget("splashWindow").hide()

