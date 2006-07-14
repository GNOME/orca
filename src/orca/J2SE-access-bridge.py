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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import atspi
import default
import debug
import orca
import keybindings
import settings
import speech
import util
import rolenames

from orca_i18n import _ # for gettext support

########################################################################
#                                                                      #
# The Java script class.                                               #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for Java applications.

        Arguments:
        - app: the application to create a script for.
        """
        default.Script.__init__(self, app)

    def consumesKeyboardEvent(self, keyboardEvent):
        """Called when a key is pressed on the keyboard.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event is of interest.
        """
        keysym = keyboardEvent.event_string
        keyboardEvent.hw_code = keybindings._getKeycode(keysym)
        return default.Script.consumesKeyboardEvent(self, keyboardEvent)

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # A JMenu has always selection.nSelectedChildren > 0
        #
        role = event.source.role
        if (role == rolenames.ROLE_MENU):
            orca.setLocusOfFocus(event, event.source)
        else:
            default.Script.onFocus(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # Hand state changes when JTree labels become expanded
        # or collapsed.
        #
        if ((event.source.role == "label") and \
            (event.type == "object:state-changed:expanded")):
            orca.visualAppearanceChanged(event, event.source)
        else:
            default.Script.onStateChanged(self, event)
