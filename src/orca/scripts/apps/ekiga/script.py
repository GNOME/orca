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

"""Custom script for Ekiga."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.scripts.default as default
from orca.ax_object import AXObject

########################################################################
#                                                                      #
# The Ekiga script class.                                              #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

    def isChatRoomMsg(self, obj):
        """Returns True if the given accessible is the text object for
        associated with a chat room conversation.

        Arguments:
        - obj: the accessible object to examine.
        """

        if obj and AXObject.get_role(obj) == Atspi.Role.TEXT \
           and AXObject.get_role(obj.parent) == Atspi.Role.SCROLL_PANE:
            state = obj.getState()
            if not state.contains(Atspi.StateType.EDITABLE) \
               and state.contains(Atspi.StateType.MULTI_LINE):
                return True

        return False

    def onTextInserted(self, event):
        """Called whenever text is inserted into one of Ekiga's text objects.
        Overridden here so that we can present new messages to the user.

        Arguments:
        - event: the Event
        """

        if self.isChatRoomMsg(event.source):
            self.presentMessage(event.any_data)
            return

        default.Script.onTextInserted(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes. Overridden here because
        new chat windows are not issuing text-inserted events for the chat
        history until we "tickle" the hierarchy. However, we do seem to get
        object:property-change:accessible-value events on the split pane. So
        we'll use that as our trigger to do the tickling.

        Arguments:
        - event: the Event
        """

        if AXObject.get_role(event.source) == Atspi.Role.SPLIT_PANE:
            hasRole = lambda x: x and AXObject.get_role(x) == Atspi.Role.TEXT
            textObjects = self.utilities.findAllDescendants(event.source, hasRole)
            return

        default.Script.onValueChanged(self, event)
