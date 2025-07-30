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

from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca.scripts.toolkits import gtk
from .chat import Chat

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    gi.require_version("Gtk", "3.0")
    from gi.repository import Atspi, Gtk

    from orca import keybindings

class Script(gtk.Script):
    """Custom script for Smuxi."""

    # Override the base class type annotation since this script always has chat
    chat: Chat

    def get_chat(self) -> Chat:
        """Returns the 'chat' class for this script."""

        return Chat(self)

    def setup_input_event_handlers(self) -> None:
        """Defines the input event handlers for this script."""

        super().setup_input_event_handlers()
        self.input_event_handlers.update(self.chat.input_event_handlers)

    def get_app_key_bindings(self) -> "keybindings.KeyBindings":
        """Returns the application-specific keybindings for this script."""

        return self.chat.key_bindings

    def get_app_preferences_gui(self) -> "Gtk.Grid":
        """Return a GtkGrid containing the application unique configuration."""

        return self.chat.get_app_preferences_gui()

    def get_preferences_from_gui(self) -> dict[str, bool | int]:
        """Returns a dictionary with the app-specific preferences."""

        return self.chat.get_preferences_from_gui()

    def on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        if self.chat.presentInsertedText(event):
            return True

        return super().on_text_inserted(event)
