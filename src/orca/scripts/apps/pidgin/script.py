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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.debug as debug
import orca.messages as messages
import orca.scripts.toolkits.GAIL as GAIL
import orca.settings as settings
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_utilities import AXUtilities

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
        self._buddyListAncestries = [[Atspi.Role.TREE_TABLE,
                                      Atspi.Role.SCROLL_PANE,
                                      Atspi.Role.FILLER,
                                      Atspi.Role.PAGE_TAB,
                                      Atspi.Role.PAGE_TAB_LIST,
                                      Atspi.Role.FILLER,
                                      Atspi.Role.FRAME]]

        GAIL.Script.__init__(self, app)

    def getChat(self):
        """Returns the 'chat' class for this script."""

        return Chat(self, self._buddyListAncestries)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script. """

        return SpeechGenerator(self)

    def getUtilities(self):
        """Returns the utilities for this script."""

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

        if AXUtilities.is_table_related(event.source):
            AXTable.clear_cache_now("children-changed event.")

        # Check to see if a new chat room tab has been created and if it
        # has, then announce its name. See bug #469098 for more details.
        #
        if event.type.startswith("object:children-changed:add"):
            rolesList = [Atspi.Role.PAGE_TAB_LIST,
                         Atspi.Role.FILLER,
                         Atspi.Role.FRAME]
            if self.utilities.hasMatchingHierarchy(event.source, rolesList):
                # As it's possible to get this component hierarchy in other
                # places than the chat room (i.e. the Preferences dialog),
                # we check to see if the name of the frame is the same as one
                # of its children. If it is, then it's a chat room tab event.
                # For a final check, we only announce the new chat tab if the
                # last child has a name.
                #
                nameFound = False
                frame = AXObject.find_ancestor(event.source,
                                               lambda x: AXObject.get_role(x) == Atspi.Role.FRAME)
                frameName = AXObject.get_name(frame)
                if not frameName:
                    return
                for child in AXObject.iter_children(event.source):
                    if frameName == AXObject.get_name(child):
                        nameFound = True
                        break
                if nameFound:
                    child = AXObject.get_child(event.source, -1)
                    childName = AXObject.get_name(child)
                    if childName:
                        line = messages.CHAT_NEW_TAB % childName
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
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            GAIL.Script.onWindowActivated(self, event)
            return

        msg = "PIDGIN: Starting hack for missing events"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        # Hack to "tickle" the accessible hierarchy. Otherwise, the
        # events we need to present text added to the chatroom are
        # missing.
        AXUtilities.find_all_page_tabs(event.source)

        msg = "PIDGIN: Hack to work around missing events complete"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        GAIL.Script.onWindowActivated(self, event)

    def onExpandedChanged(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        # Overridden here because the event.source is in a hidden column.
        obj = event.source
        if self.chat.isInBuddyList(obj):
            obj = AXObject.get_next_sibling(obj)
            self.presentObject(obj, alreadyFocused=True)
            return

        GAIL.Script.onExpandedChanged(self, event)
