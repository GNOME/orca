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

""" Custom script for gnome-panel
"""

__id__        = "$Id: gnome-panel.py 2251 2007-04-05 01:42:41Z lmonsanto $"
__version__   = "$Revision: 2251 $"
__date__      = "$Date: 2007-04-04 18:42:41 -0700 (Wed, 04 Apr 2007) $"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.orca as orca
import orca.atspi as atspi
import orca.default as default
import orca.debug as debug
import orca.braille as braille
import orca.speech as speech
import orca.rolenames as rolenames

from orca.orca_i18n import _

########################################################################
#                                                                      #
# The gnome-panel script class.                                        #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for gnome-panel

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        self._debug("__init__")
        default.Script.__init__(self, app)

    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "gnome-panel.py: "+msg)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """
        obj = event.source

        self._debug("onStateChanged: '%s' %s (%d, %d)" % \
                    (obj.name, event.type, event.detail1, event.detail2))

        # Handle tooltip popups.
        #
        if obj.role == rolenames.ROLE_TOOL_TIP:
            if event.type.startswith("object:state-changed:showing") and \
               event.detail1 == 1:
                braille.displayMessage(obj.name)
                speech.speak(obj.name)
            # Delete the cached accessible to force the AT-SPI to update
            # the accessible cache. Otherwise, the event references the
            # previous popup object.
            #
            atspi.Accessible.deleteAccessible(obj._acc)

        # If focus moves to something within a panel and focus was not
        # already in the containing panel, the panel will issue its
        # own state-changed:focused event with detail1 == 1 after the
        # event for the item with focus.  The panel is not focused,
        # plus the extraneous event results in unnecessary chattiness
        # and updates the braille display to "panel."
        #
        elif obj.role == rolenames.ROLE_PANEL and \
             event.type.startswith("object:state-changed:focused") and \
             event.detail1 == 1 and not \
             event.source.state.count(atspi.Accessibility.STATE_FOCUSED):
            return

        else:
            default.Script.onStateChanged(self, event)
