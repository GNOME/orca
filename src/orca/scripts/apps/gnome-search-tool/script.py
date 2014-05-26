# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
# Copyright 2014 Igalia, S.L.
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

"""Custom script for gnome-search-tool"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

import orca.event_manager as event_manager
import orca.scripts.toolkits.gtk as gtk

########################################################################
#                                                                      #
# The gnome-search-tool script class.                                  #
#                                                                      #
########################################################################

class Script(gtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        gtk.Script.__init__(self, app)
        self._floodEvents = ['object:children-changed:add',
                             'object:property-change:accessible-name',
                             'object:text-changed:insert',
                             'object:text-changed:delete']

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing events."""

        obj = event.source
        if obj.getRole() == pyatspi.ROLE_ANIMATION:
            _manager = event_manager.getManager()
            if event.detail1:
                _manager.ignoreEventTypes(self._floodEvents)
            else:
                _manager.unignoreEventTypes(self._floodEvents)
            self.presentTitle(None)
            return

        gtk.Script.onShowingChanged(self, event)
