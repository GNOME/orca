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

"""Custom script for Gajim."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

from orca import chat
from orca.scripts import default
from orca.ax_utilities import AXUtilities

class Script(default.Script):

    def get_chat(self):
        """Returns the 'chat' class for this script."""

        return chat.Chat(self)

    def setup_input_event_handlers(self):
        """Defines the input event handlers for this script."""

        default.Script.setup_input_event_handlers(self)
        self.input_event_handlers.update(self.chat.input_event_handlers)

    def get_app_key_bindings(self):
        """Returns the application-specific keybindings for this script."""

        return self.chat.key_bindings

    def get_app_preferences_gui(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application. The chat-related options get
        created by the chat module."""

        return self.chat.get_app_preferences_gui()

    def get_preferences_from_gui(self):
        """Returns a dictionary with the app-specific preferences."""

        return self.chat.get_preferences_from_gui()

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if self.chat.presentInsertedText(event):
            return

        default.Script.on_text_inserted(self, event)

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        # Hack to "tickle" the accessible hierarchy. Otherwise, the
        # events we need to present text added to the chatroom are
        # missing.
        AXUtilities.find_all_page_tabs(event.source)
        default.Script.on_window_activated(self, event)
