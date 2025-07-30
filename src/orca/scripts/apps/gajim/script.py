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

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import keybindings
from orca.ax_utilities import AXUtilities
from orca.chat import Chat
from orca.scripts import default

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    gi.require_version("Gtk", "3.0")
    from gi.repository import Atspi
    from gi.repository import Gtk

class Script(default.Script):
    """Custom script for Gajim."""

    def get_chat(self) -> Chat:
        """Returns the 'chat' class for this script."""

        return Chat(self)

    def setup_input_event_handlers(self) -> None:
        """Defines the input event handlers for this script."""

        default.Script.setup_input_event_handlers(self)
        assert self.chat is not None
        self.input_event_handlers.update(self.chat.input_event_handlers)

    def get_app_key_bindings(self) -> keybindings.KeyBindings:
        """Returns the application-specific keybindings for this script."""

        assert self.chat is not None
        return self.chat.key_bindings

    def get_app_preferences_gui(self) -> Gtk.Grid:
        """Return a GtkGrid containing app-specific settings."""

        assert self.chat is not None
        return self.chat.get_app_preferences_gui()

    def get_preferences_from_gui(self) -> dict:
        """Returns a dictionary with the app-specific preferences."""

        assert self.chat is not None
        return self.chat.get_preferences_from_gui()

    def on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        assert self.chat is not None
        if self.chat.presentInsertedText(event):
            return True

        return default.Script.on_text_inserted(self, event)

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        # Hack to "tickle" the accessible hierarchy. Otherwise, the
        # events we need to present text added to the chatroom are
        # missing.
        AXUtilities.find_all_page_tabs(event.source)
        return default.Script.on_window_activated(self, event)
