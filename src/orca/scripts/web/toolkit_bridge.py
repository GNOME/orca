# Orca
#
# Copyright 2025 Igalia, S.L.
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

# pylint: disable=too-many-public-methods

"""Bridges web.Script event handlers to the appropriate script."""

from __future__ import annotations

from orca import debug
from orca.ax_utilities import AXUtilities
from orca.scripts import web


class ToolkitBridge(web.Script):
    """Bridges web.Script event handlers to the appropriate script."""

    @staticmethod
    def bridge(func):
        """Decorator that dispatches to web script then base script, with logging."""

        name = func.__name__

        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if result is not None:
                tokens = ["TOOLKIT BRIDGE:", name, "handled by bridge:", result]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return result

            web_method = getattr(web.Script, name)
            if web_method(self, *args, **kwargs):
                tokens = ["TOOLKIT BRIDGE:", name, "handled by web script"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return True

            base_super = super(web.Script, self)
            base_method = getattr(base_super, name)
            tokens = ["TOOLKIT BRIDGE:", name, "passing to", base_method]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return base_method(*args, **kwargs)

        return wrapper

    @bridge
    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Handles changes of focus of interest."""
        return None

    @bridge
    def on_active_changed(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if (
            event.detail1
            and AXUtilities.is_frame(event.source)
            and not AXUtilities.can_be_active_window(event.source)
        ):
            return True
        return None

    @bridge
    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""
        return None

    @bridge
    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""
        return None

    @bridge
    def on_checked_changed(self, event):
        """Callback for object:state-changed:checked accessibility events."""
        return None

    @bridge
    def on_children_added(self, event):
        """Callback for object:children-changed:add accessibility events."""
        return None

    @bridge
    def on_children_removed(self, event):
        """Callback for object:children-changed:removed accessibility events."""
        return None

    @bridge
    def on_column_reordered(self, event):
        """Callback for object:column-reordered accessibility events."""
        return None

    @bridge
    def on_document_load_complete(self, event):
        """Callback for document:load-complete accessibility events."""
        return None

    @bridge
    def on_document_load_stopped(self, event):
        """Callback for document:load-stopped accessibility events."""
        return None

    @bridge
    def on_document_reload(self, event):
        """Callback for document:reload accessibility events."""
        return None

    @bridge
    def on_expanded_changed(self, event):
        """Callback for object:state-changed:expanded accessibility events."""
        return None

    @bridge
    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""
        return None

    @bridge
    def on_mouse_button(self, event):
        """Callback for mouse:button accessibility events."""
        return None

    @bridge
    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""
        return None

    @bridge
    def on_row_reordered(self, event):
        """Callback for object:row-reordered accessibility events."""
        return None

    @bridge
    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""
        return None

    @bridge
    def on_selection_changed(self, event):
        """Callback for object:selection-changed accessibility events."""
        return None

    @bridge
    def on_showing_changed(self, event):
        """Callback for object:state-changed:showing accessibility events."""
        return None

    @bridge
    def on_text_attributes_changed(self, event):
        """Callback for object:text-attributes-changed accessibility events."""
        return None

    @bridge
    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""
        return None

    @bridge
    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""
        return None

    @bridge
    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""
        return None

    @bridge
    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        if not AXUtilities.can_be_active_window(event.source):
            return True
        return None

    @bridge
    def on_window_deactivated(self, event):
        """Callback for window:deactivate accessibility events."""
        return None
