# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

# pylint: disable=too-many-public-methods

"""Custom script for Thunderbird."""

from __future__ import annotations


from typing import TYPE_CHECKING

from orca import document_presenter
from orca.scripts.toolkits import Gecko
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from orca.scripts.toolkits.Gecko.script_utilities import Utilities


class Script(Gecko.Script):
    """The script for Thunderbird."""

    # Override the base class type annotations
    utilities: "Utilities"

    def on_busy_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:busy accessibility events."""

        # TODO - JD: Can this logic be moved to the web script?
        if self.utilities.is_editable_message(event.source):
            return True

        if document_presenter.get_presenter().in_focus_mode(self.app):
            return True

        return super().on_busy_changed(event)

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        if self.utilities.is_editable_message(event.source) and event.detail1 == -1:
            return True

        return super().on_caret_moved(event)

    def on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:selection-changed accessibility events."""

        parent = AXObject.get_parent(event.source)
        if AXUtilities.is_combo_box(parent) and not AXUtilities.is_focused(parent):
            return True

        return super().on_selection_changed(event)

    def on_text_deleted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:delete accessibility events."""

        if AXUtilities.is_label(event.source) and AXUtilities.is_status_bar(
            AXObject.get_parent(event.source)
        ):
            return True

        return super().on_text_deleted(event)

    def on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        parent = AXObject.get_parent(event.source)
        if AXUtilities.is_label(event.source) and AXUtilities.is_status_bar(parent):
            return True

        # Try to stop unwanted chatter when a message is being replied to.
        # See bgo#618484.
        if event.type.endswith("system") and self.utilities.is_editable_message(event.source):
            return True

        return super().on_text_inserted(event)

    def on_text_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-selection-changed accessibility events."""

        return super().on_text_selection_changed(event)

    def on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""

        self.utilities.clear_content_cache()
        return super().on_window_deactivated(event)
