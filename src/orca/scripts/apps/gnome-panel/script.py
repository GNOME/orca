# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

""" Custom script for gnome-panel
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.scripts.default as default
from .speech_generator import SpeechGenerator

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

        default.Script.__init__(self, app)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        obj = event.source

        # If focus moves to something within a panel and focus was not
        # already in the containing panel, the panel will issue its
        # own state-changed:focused event with detail1 == 1 after the
        # event for the item with focus.  The panel is not focused,
        # plus the extraneous event results in unnecessary chattiness
        # and updates the braille display to "panel."
        #
        if obj.getRole() == pyatspi.ROLE_PANEL and \
             event.type.startswith("object:state-changed:focused") and \
             event.detail1 == 1 \
             and not obj.getState().contains(pyatspi.STATE_FOCUSED):
            return

        default.Script.onStateChanged(self, event)
