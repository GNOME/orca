# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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

""" Custom script for Gnome Power Manager.
"""

__id__        = ""
__version__   = ""
__date__      = ""
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.orca as orca
import orca.default as default
import orca.debug as debug
import orca.settings as settings
import orca.speech as speech

from orca.orca_i18n import _

########################################################################
#                                                                      #
# The gnome-power-manager script class.                                #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST
        self._lastInfo = ""

        # The power manager does not send events indication
        # that the accessible description has changed.
        # Disabling the caching of accessible descriptions, 
        # forces the power manager to return a new description 
        # with the latest power management information.
        settings.cacheDescriptions = False

        default.Script.__init__(self, app)
        

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["object:bounds-changed"] = \
            self.onBoundsChanged

        return listeners


    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "gnome-power-manager.py: "+msg)


    def onBoundsChanged(self, event):
        """ Called whenever an object's bounds change. This happens
        when the Gnome Power Manager balloon is displayed on the
        desktop.

        Arguments:
        - event: the Event
        """
        info = event.source.description
        self._debug("onBoundsChanged: '%s'" % info)

        if info != self._lastInfo:
            self._lastInfo = info
            if len(info) > 0:
                speech.speak(info, None, True)

