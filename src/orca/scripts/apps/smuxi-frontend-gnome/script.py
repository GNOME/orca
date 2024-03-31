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

from orca.scripts.toolkits import gtk
from .chat import Chat

class Script(gtk.Script):

    def get_chat(self):
        """Returns the 'chat' class for this script."""

        return Chat(self)

    def setup_input_event_handlers(self):
        """Defines the input event handlers for this script."""

        super().setup_input_event_handlers()
        self.input_event_handlers.update(self.chat.input_event_handlers)

    def get_app_key_bindings(self):
        """Returns the application-specific keybindings for this script."""

        return self.chat.key_bindings

    def get_app_preferences_gui(self):
        """Return a GtkGrid containing the application unique configuration."""

        return self.chat.get_app_preferences_gui()

    def get_preferences_from_gui(self):
        """Returns a dictionary with the app-specific preferences."""

        return self.chat.get_preferences_from_gui()

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if self.chat.presentInsertedText(event):
            return

        super().on_text_inserted(event)
