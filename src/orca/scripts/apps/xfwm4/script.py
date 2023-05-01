# Orca
#
# Copyright 2011 The Orca Team.
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

"""Custom script for xfwm4."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.scripts.default as default

########################################################################
#                                                                      #
# The xfwm4 script class.                                              #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object. Overridden
        here so that we will speak each item as the user is switching
        windows.

        Arguments:
        - event: the Event
        """

        if Atspi.Accessible.get_role(event.source) != Atspi.Role.LABEL:
            default.Script.onTextInserted(self, event)
            return

        self.presentMessage(event.source.name)

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object. Overridden
        here because we wish to ignore text deletion events associated
        with window switching.

        Arguments:
        - event: the Event
        """

        if Atspi.Accessible.get_role(event.source) != Atspi.Role.LABEL:
            default.Script.onTextDeleted(self, event)
