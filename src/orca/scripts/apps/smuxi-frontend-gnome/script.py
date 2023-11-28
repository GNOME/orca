# Orca
#
# Copyright 2018 Igalia, S.L.
#
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

"""Custom script for Smuxi."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.scripts.toolkits.gtk as gtk
from .chat import Chat

class Script(gtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application."""

        # So we can take an educated guess at identifying the buddy list.
        self._buddyListAncestries = [[Atspi.Role.TREE_TABLE,
                                      Atspi.Role.SCROLL_PANE,
                                      Atspi.Role.SPLIT_PANE,
                                      Atspi.Role.SPLIT_PANE,
                                      Atspi.Role.FILLER,
                                      Atspi.Role.FRAME]]

        super().__init__(app)

    def getChat(self):
        """Returns the 'chat' class for this script."""

        return Chat(self, self._buddyListAncestries)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script."""

        super().setupInputEventHandlers()
        self.inputEventHandlers.update(self.chat.inputEventHandlers)

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        return self.chat.keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration."""

        return self.chat.getAppPreferencesGUI()

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        return self.chat.getPreferencesFromGUI()

    def onTextInserted(self, event):
        """Called whenever text is added to an object."""

        if self.chat.presentInsertedText(event):
            return

        super().onTextInserted(event)
