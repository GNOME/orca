# Orca
#
# Copyright 2010 Joanmarie Diggs.
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

"""Custom script for Empathy."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import pyatspi

import orca.chat as chat
import orca.scripts.toolkits.gtk as gtk

from .script_utilities import Utilities

########################################################################
#                                                                      #
# The Empathy script class.                                            #
#                                                                      #
########################################################################

class Script(gtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application."""

        # So we can take an educated guess at identifying the buddy list.
        #
        self._buddyListAncestries = [[pyatspi.ROLE_TREE_TABLE,
                                      pyatspi.ROLE_SCROLL_PANE,
                                      pyatspi.ROLE_FILLER,
                                      pyatspi.ROLE_FRAME]]

        gtk.Script.__init__(self, app)

    def getChat(self):
        """Returns the 'chat' class for this script."""

        return chat.Chat(self, self._buddyListAncestries)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. Here we need to add the
        handlers for chat functionality.
        """

        gtk.Script.setupInputEventHandlers(self)
        self.inputEventHandlers.update(self.chat.inputEventHandlers)

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        return self.chat.keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application. The chat-related options get
        created by the chat module."""

        return self.chat.getAppPreferencesGUI()

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        return self.chat.getPreferencesFromGUI()

    def skipObjectEvent(self, event):
        """Gives us, and scripts, the ability to decide an event isn't
        worth taking the time to process under the current circumstances.

        Arguments:
        - event: the Event

        Returns True if we shouldn't bother processing this object event.
        """

        if self.chat.isChatRoomMsg(event.source):
            return False

        return gtk.Script.skipObjectEvent(self, event)

    def onTextInserted(self, event):
        """Called whenever text is added to an object."""

        if event.source.getRole() == pyatspi.ROLE_LABEL:
            # The is the timer of a call.
            #
            return

        if self.chat.presentInsertedText(event):
            return

        gtk.Script.onTextInserted(self, event)

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated."""

        # Hack to "tickle" the accessible hierarchy. Otherwise, the
        # events we need to present text added to the chatroom are
        # missing.
        hasRole = lambda x: x and x.getRole() == pyatspi.ROLE_PAGE_TAB
        allPageTabs = pyatspi.findAllDescendants(event.source, hasRole)
        gtk.Script.onWindowActivated(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        if event.source.getRole() == pyatspi.ROLE_WINDOW:
            # The is the timer of a call.
            #
            return

        gtk.Script.onValueChanged(self, event)
