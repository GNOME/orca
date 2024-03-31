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

from orca import debug
from orca import messages
from orca.scripts.toolkits import gtk
from orca import settings
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

from .chat import Chat
from .script_utilities import Utilities
from .speech_generator import SpeechGenerator

class Script(gtk.Script):

    def get_chat(self):
        """Returns the 'chat' class for this script."""

        return Chat(self)

    def get_speech_generator(self):
        """Returns the speech generator for this script. """

        return SpeechGenerator(self)

    def get_utilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def setup_input_event_handlers(self):
        """Defines the input event handlers for this script."""

        super().setup_input_event_handlers()
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

    def on_children_added(self, event):
        """Callback for object:children-changed:add accessibility events."""

        super().on_children_added(event)
        if not AXUtilities.is_page_tab_list(event.source):
            return

        AXObject.clear_cache(event.source, True, "to ensure tab info is current.")

        if AXUtilities.is_selected(event.any_data):
            msg = "PIDGIN: Not presenting addition of already-selected tab"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        # In the chat window, the frame name changes to reflect the active chat.
        # So if we don't have a matching tab, this isn't the chat window.
        frame = AXObject.find_ancestor(event.source, AXUtilities.is_frame)
        frame_name = AXObject.get_name(frame)
        for child in AXObject.iter_children(event.source):
            if frame_name == AXObject.get_name(child):
                break
        else:
            tokens = ["PIDGIN:", frame, "does not seem to be a chat window"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        line = messages.CHAT_NEW_TAB % AXObject.get_name(event.any_data)
        voice = self.speech_generator.voice(obj=event.any_data, string=line)
        self.speakMessage(line, voice=voice)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if self.chat.isInBuddyList(event.source):
            return

        super().on_name_changed(event)

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if self.chat.isInBuddyList(event.source):
            return

        super().on_text_deleted(event)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if self.chat.presentInsertedText(event):
            return

        super().on_text_inserted(event)

    def on_value_changed(self, event):
        """Callback for object:property-change:accessible-value accessibility events."""

        if self.chat.isInBuddyList(event.source):
            return

        super().on_value_changed(event)

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        if not settings.enableSadPidginHack:
            msg = "PIDGIN: Hack for missing events disabled"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            super().on_window_activated(event)
            return

        msg = "PIDGIN: Starting hack for missing events"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        # Hack to "tickle" the accessible hierarchy. Otherwise, the
        # events we need to present text added to the chatroom are
        # missing.
        AXUtilities.find_all_page_tabs(event.source)

        msg = "PIDGIN: Hack to work around missing events complete"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        super().on_window_activated(event)

    def on_expanded_changed(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        # Overridden here because the event.source is in a hidden column.
        obj = event.source
        if self.chat.isInBuddyList(obj):
            obj = AXObject.get_next_sibling(obj)
            self.presentObject(obj, alreadyFocused=True)
            return

        super().on_expanded_changed(event)
