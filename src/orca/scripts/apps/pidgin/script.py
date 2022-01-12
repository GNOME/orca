# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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

"""Custom script for pidgin."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.messages as messages
import orca.scripts.toolkits.GAIL as GAIL
import orca.settings as settings

from .chat import Chat
from .script_utilities import Utilities
from .speech_generator import SpeechGenerator

########################################################################
#                                                                      #
# The Pidgin script class.                                             #
#                                                                      #
########################################################################

class Script(GAIL.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # So we can take an educated guess at identifying the buddy list.
        #
        self._buddyListAncestries = [[pyatspi.ROLE_TREE_TABLE,
                                      pyatspi.ROLE_SCROLL_PANE,
                                      pyatspi.ROLE_FILLER,
                                      pyatspi.ROLE_PAGE_TAB,
                                      pyatspi.ROLE_PAGE_TAB_LIST,
                                      pyatspi.ROLE_FILLER,
                                      pyatspi.ROLE_FRAME]]

        GAIL.Script.__init__(self, app)

    def getChat(self):
        """Returns the 'chat' class for this script."""

        return Chat(self, self._buddyListAncestries)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script. """

        return SpeechGenerator(self)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. Here we need to add the
        handlers for chat functionality.
        """

        GAIL.Script.setupInputEventHandlers(self)
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

    def onChildrenAdded(self, event):
        """Callback for object:children-changed:add accessibility events."""

        # Check to see if a new chat room tab has been created and if it
        # has, then announce its name. See bug #469098 for more details.
        #
        if event.type.startswith("object:children-changed:add"):
            rolesList = [pyatspi.ROLE_PAGE_TAB_LIST,
                         pyatspi.ROLE_FILLER,
                         pyatspi.ROLE_FRAME]
            if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                # As it's possible to get this component hierarchy in other
                # places than the chat room (i.e. the Preferences dialog),
                # we check to see if the name of the frame is the same as one
                # of its children. If it is, then it's a chat room tab event.
                # For a final check, we only announce the new chat tab if the
                # last child has a name.
                #
                nameFound = False
                frameName = event.source.parent.parent.name
                for child in event.source:
                    if frameName and (frameName == child.name):
                        nameFound = True
                if nameFound:
                    child = event.source[-1]
                    if child.name:
                        line = messages.CHAT_NEW_TAB % child.name
                        voice = self.speechGenerator.voice(obj=child, string=line)
                        self.speakMessage(line, voice=voice)

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        if self.chat.isInBuddyList(event.source):
            return
        else:
            GAIL.Script.onNameChanged(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

        if self.chat.isInBuddyList(event.source):
            return
        else:
            GAIL.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Called whenever text is added to an object."""

        if self.chat.presentInsertedText(event):
            return

        GAIL.Script.onTextInserted(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        if self.chat.isInBuddyList(event.source):
            return
        else:
            GAIL.Script.onValueChanged(self, event)

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated."""

        if not settings.enableSadPidginHack:
            msg = "PIDGIN: Hack for missing events disabled"
            debug.println(debug.LEVEL_INFO, msg, True)
            GAIL.Script.onWindowActivated(self, event)
            return

        msg = "PIDGIN: Starting hack for missing events"
        debug.println(debug.LEVEL_INFO, msg, True)

        # Hack to "tickle" the accessible hierarchy. Otherwise, the
        # events we need to present text added to the chatroom are
        # missing.
        hasRole = lambda x: x and x.getRole() == pyatspi.ROLE_PAGE_TAB
        allPageTabs = pyatspi.findAllDescendants(event.source, hasRole)
        msg = "PIDGIN: Hack to work around missing events complete"
        debug.println(debug.LEVEL_INFO, msg, True)
        GAIL.Script.onWindowActivated(self, event)

    def onExpandedChanged(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        # Overridden here because the event.source is in a hidden column.
        obj = event.source
        if self.chat.isInBuddyList(obj):
            obj = obj.parent[obj.getIndexInParent() + 1]
            self.presentObject(obj, alreadyFocused=True)
            return
            
        GAIL.Script.onExpandedChanged(self, event)
