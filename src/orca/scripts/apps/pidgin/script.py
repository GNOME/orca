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

from __future__ import annotations

from typing import TYPE_CHECKING

from orca import chat_presenter, debug, messages, presentation_manager
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts.toolkits import gtk

from .script_utilities import Utilities
from .speech_generator import SpeechGenerator

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Script(gtk.Script):
    """Custom script for pidgin."""

    # Override the base class type annotation
    utilities: Utilities

    def _create_speech_generator(self) -> SpeechGenerator:
        """Creates and returns the speech generator for this script."""

        return SpeechGenerator(self)

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def _on_children_added(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:add accessibility events."""

        super()._on_children_added(event)
        if not AXUtilities.is_page_tab_list(event.source):
            return True

        AXObject.clear_cache(event.source, True, "to ensure tab info is current.")

        if AXUtilities.is_selected(event.any_data):
            msg = "PIDGIN: Not presenting addition of already-selected tab"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        # In the chat window, the frame name changes to reflect the active chat.
        # So if we don't have a matching tab, this isn't the chat window.
        frame = AXUtilities.find_ancestor(event.source, AXUtilities.is_frame)
        frame_name = AXObject.get_name(frame)
        for child in AXObject.iter_children(event.source):
            if frame_name == AXObject.get_name(child):
                break
        else:
            tokens = ["PIDGIN:", frame, "does not seem to be a chat window"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        line = messages.CHAT_NEW_TAB % AXObject.get_name(event.any_data)
        presentation_manager.get_manager().speak_accessible_text(event.any_data, line)
        return True

    def _on_expanded_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:expanded accessibility events."""

        # Overridden here because the event.source is in a hidden column.
        obj = event.source
        if self.chat.is_in_buddy_list(obj):
            obj = AXObject.get_next_sibling(obj)
            self.present_object(obj, alreadyFocused=True)
            return True

        return super()._on_expanded_changed(event)

    def _on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        if chat_presenter.get_presenter().present_inserted_text(self, event):
            return True

        return super()._on_text_inserted(event)
