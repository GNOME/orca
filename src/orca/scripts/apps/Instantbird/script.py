# Orca
#
# Copyright 2010 Joanmarie Diggs.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
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

import orca.braille as braille
import orca.default as default
import orca.orca as orca
import orca.orca_state as orca_state
import orca.settings as settings
import orca.speech as speech


from chat import Chat

########################################################################
#                                                                      #
# The Instantbird script class.                                        #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application."""

        # So we can take an educated guess at identifying the buddy list.
        #
        self._buddyListAncestries = [[pyatspi.ROLE_LIST,
                                      pyatspi.ROLE_FRAME]]

        # We want the functionality of the default script without the
        # conflicting enhancements we'd pull in from the Gecko script.
        # (Widgets may be a different story, but for now let's try
        # subclassing the default script rather than the Gecko script.)
        #
        default.Script.__init__(self, app)

    def getChat(self):
        """Returns the 'chat' class for this script."""

        return Chat(self, self._buddyListAncestries)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. Here we need to add the
        handlers for chat functionality.
        """

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers.update(self.chat.inputEventHandlers)

    def getKeyBindings(self):
        """Defines the key bindings for this script. Here we need to add
        the keybindings associated with chat functionality.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = default.Script.getKeyBindings(self)

        bindings = self.chat.keyBindings
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        return keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkVBox contain the application unique configuration
        GUI items for the current application. The chat-related options
        get created by the chat module.
        """

        return self.chat.getAppPreferencesGUI()

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values. The chat-related options get written out by the chat
        module.

        Arguments:
        - prefs: file handle for application preferences.
        """

        self.chat.setAppPreferences(prefs)

    def onTextInserted(self, event):
        """Called whenever text is added to an object."""

        if self.chat.presentInsertedText(event):
            return

        default.Script.onTextInserted(self, event)

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

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
                braille.displayMessage(
                    room2, flashTime=settings.brailleFlashTime)
                orca.setLocusOfFocus(event, event.source)
                return

        default.Script.onFocus(self, event)

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated."""

        # Hack to "tickle" the accessible hierarchy. Otherwise, the
        # events we need to present text added to the chatroom are
        # missing.
        #
        allPageTabs = self.findByRole(event.source, pyatspi.ROLE_PAGE_TAB)

        default.Script.onWindowActivated(self, event)
