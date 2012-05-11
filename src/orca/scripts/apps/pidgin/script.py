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

import orca.scripts.default as default
import orca.speech as speech

from orca.orca_i18n import _

from .chat import Chat
from .script_utilities import Utilities
from .speech_generator import SpeechGenerator

########################################################################
#                                                                      #
# The Pidgin script class.                                             #
#                                                                      #
########################################################################

class Script(default.Script):

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

        default.Script.__init__(self, app)

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

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers.update(self.chat.inputEventHandlers)

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        return self.chat.keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application. The chat-related options get
        created by the chat module."""

        return self.chat.getAppPreferencesGUI()

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values. The chat-related options get written out by the chat
        module.

        Arguments:
        - prefs: file handle for application preferences.
        """

        self.chat.setAppPreferences(prefs)

    def onChildrenChanged(self, event):
        """Called whenever a child object changes in some way.

        Arguments:
        - event: the text inserted Event
        """

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
                        line = _("New chat tab %s") % child.name
                        speech.speak(line)

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        if self.chat.isInBuddyList(event.source):
            return
        else:
            default.Script.onNameChanged(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

        if self.chat.isInBuddyList(event.source):
            return
        else:
            default.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Called whenever text is added to an object."""

        if self.chat.presentInsertedText(event):
            return

        default.Script.onTextInserted(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        if self.chat.isInBuddyList(event.source):
            return
        else:
            default.Script.onValueChanged(self, event)

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated."""

        # Hack to "tickle" the accessible hierarchy. Otherwise, the
        # events we need to present text added to the chatroom are
        # missing.
        #
        allPageTabs = self.utilities.descendantsWithRole(
            event.source, pyatspi.ROLE_PAGE_TAB)

        default.Script.onWindowActivated(self, event)

    def visualAppearanceChanged(self, event, obj):
        """Called when the visual appearance of an object changes.
        Overridden here because we get object:state-changed:expanded
        events for the buddy list, but the obj is in a hidden column.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """

        if self.chat.isInBuddyList(obj) \
           and event.type.startswith("object:state-changed:expanded"):

            # The event is associated with the invisible cell. Set it
            # to the visible cell and then let the default script do
            # its thing.
            #
            obj = obj.parent[obj.getIndexInParent() + 1]
            
        default.Script.visualAppearanceChanged(self, event, obj)

