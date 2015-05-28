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

"""Custom script for Instantbird."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import pyatspi

import orca.bookmarks as bookmarks
import orca.scripts.default as default
import orca.orca as orca
import orca.settings_manager as settings_manager
import orca.orca_state as orca_state
import orca.scripts.toolkits.Gecko as Gecko
import orca.speech as speech

from .chat import Chat
from .script_utilities import Utilities

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# The Instantbird script class.                                        #
#                                                                      #
########################################################################

class Script(Gecko.Script):

    def __init__(self, app):
        """Creates a new script for the given application."""

        # So we can take an educated guess at identifying the buddy list.
        #
        self._buddyListAncestries = [[pyatspi.ROLE_LIST,
                                      pyatspi.ROLE_FRAME]]

        Gecko.Script.__init__(self, app)

    def getBookmarks(self):
        """Returns the "bookmarks" class for this script."""

        # This is a copy of orca.script.getBookmarks(). It's here to
        # prevent the Gecko script's from being used.
        #
        try:
            return self.bookmarks
        except AttributeError:
            self.bookmarks = bookmarks.Bookmarks(self)
            return self.bookmarks

    def getChat(self):
        """Returns the 'chat' class for this script."""

        return Chat(self, self._buddyListAncestries)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def getEnabledStructuralNavigationTypes(self):
        """Returns a list of the structural navigation object types
        enabled in this script.
        """

        return []

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. Here we need to add the
        handlers for chat functionality.
        """

        Gecko.Script.setupInputEventHandlers(self)
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

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

        default.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Called whenever text is added to an object."""

        if self.chat.presentInsertedText(event):
            return

        default.Script.onTextInserted(self, event)

    def onCaretMoved(self, event):
        """Caret movement in Gecko is somewhat unreliable and
        unpredictable, but we need to handle it.  When we detect caret
        movement, we make sure we update our own notion of the caret
        position: our caretContext is an [obj, characterOffset] that
        points to our current item and character (if applicable) of
        interest.  If our current item doesn't implement the
        accessible text specialization, the characterOffset value
        is meaningless (and typically -1)."""

        if self.utilities.inDocumentContent(event.source):
            orca.setLocusOfFocus(event, event.source)
            Gecko.Script.onCaretMoved(self, event)
        else:
            default.Script.onCaretMoved(self, event)

    def onChildrenChanged(self, event):
        """Called when a child node has changed.  In particular, we are looking
        for addition events often associated with Javascipt insertion. One such
        such example would be the programmatic insertion of a tooltip or alert
        dialog."""

        return

    def onDocumentLoadComplete(self, event):
        """Called when a web page load is completed."""

        return

    def onDocumentLoadStopped(self, event):
        """Called when a web page load is interrupted."""

        return

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        default.Script.onNameChanged(self, event)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        # This seems to be the most reliable way to identify that the
        # active chatroom was changed via keyboard from within the entry.
        # In this case, speak and flash braille the new room name.
        #
        if orca_state.locusOfFocus and event.source \
           and orca_state.locusOfFocus.getRole() == pyatspi.ROLE_ENTRY \
           and event.source.getRole() == pyatspi.ROLE_ENTRY \
           and orca_state.locusOfFocus != event.source:
            room1 = self.chat.getChatRoomName(orca_state.locusOfFocus)
            room2 = self.chat.getChatRoomName(event.source)
            if room1 != room2:
                speech.speak(room2)
                flashTime = _settingsManager.getSetting('brailleFlashTime')
                self.displayBrailleMessage(room2, flashTime)
                orca.setLocusOfFocus(event, event.source)
                return

        if self.utilities.inDocumentContent(event.source):
            Gecko.Script.onFocusedChanged(self, event)
        else:
            default.Script.onFocusedChanged(self, event)

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated."""

        # Hack to "tickle" the accessible hierarchy. Otherwise, the
        # events we need to present text added to the chatroom are
        # missing.
        hasRole = lambda x: x and x.getRole() == pyatspi.ROLE_PAGE_TAB
        allPageTabs = pyatspi.findAllDescendants(event.source, hasRole)
        default.Script.onWindowActivated(self, event)
