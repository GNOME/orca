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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import cmdnames
from orca import debug
from orca import focus_manager
from orca import input_event
from orca import settings_manager
from orca.scripts.toolkits import Gecko
from orca.ax_object import AXObject
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

from .spellcheck import SpellCheck

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    gi.require_version("Gtk", "3.0")
    from gi.repository import Atspi, Gtk

    from orca.scripts.toolkits.Gecko.script_utilities import Utilities

class Script(Gecko.Script):
    """The script for Thunderbird."""

    # Override the base class type annotations
    spellcheck: SpellCheck
    utilities: "Utilities"

    def __init__(self, app: Atspi.Accessible) -> None:
        if settings_manager.get_manager().get_setting('sayAllOnLoad') is None:
            settings_manager.get_manager().set_setting('sayAllOnLoad', False)
        if settings_manager.get_manager().get_setting('pageSummaryOnLoad') is None:
            settings_manager.get_manager().set_setting('pageSummaryOnLoad', False)

        super().__init__(app)

    def setup_input_event_handlers(self) -> None:
        """Defines the input event handlers for this script."""

        super().setup_input_event_handlers()

        self.input_event_handlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.toggle_presentation_mode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.input_event_handlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enable_sticky_focus_mode,
                cmdnames.SET_FOCUS_MODE_STICKY)

        self.input_event_handlers["enableStickyBrowseModeHandler"] = \
            input_event.InputEventHandler(
                Script.enable_sticky_browse_mode,
                cmdnames.SET_BROWSE_MODE_STICKY)

    def get_spellcheck(self) -> SpellCheck:
        """Returns the spellcheck support for this script."""

        return SpellCheck(self)

    def get_app_preferences_gui(self) -> Gtk.Grid:
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = super().get_app_preferences_gui()

        assert self._say_all_on_load_check_button is not None
        assert self._page_summary_on_load_check_button is not None
        self._say_all_on_load_check_button.set_active(
            settings_manager.get_manager().get_setting("sayAllOnLoad"))
        self._page_summary_on_load_check_button.set_active(
            settings_manager.get_manager().get_setting("pageSummaryOnLoad"))

        spellcheck = self.spellcheck.get_app_preferences_gui()
        grid.attach(spellcheck, 0, len(grid.get_children()), 1, 1)
        grid.show_all()

        return grid

    def get_preferences_from_gui(self) -> dict[str, bool | int]:
        """Returns a dictionary with the app-specific preferences."""

        prefs = super().get_preferences_from_gui()
        assert self._say_all_on_load_check_button is not None
        assert self._page_summary_on_load_check_button is not None
        prefs["sayAllOnLoad"] = self._say_all_on_load_check_button.get_active()
        prefs["pageSummaryOnLoad"] = self._page_summary_on_load_check_button.get_active()
        prefs.update(self.spellcheck.get_preferences_from_gui())

        return prefs

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        if self.spellcheck.is_suggestions_item(new_focus):
            include_label = not self.spellcheck.is_suggestions_item(old_focus)
            self.update_braille(new_focus)
            self.spellcheck.present_suggestion_list_item(include_label=include_label)
            return True

        return super().locus_of_focus_changed(event, old_focus, new_focus)

    def use_focus_mode(
        self,
        obj: Atspi.Accessible,
        prev_obj: Atspi.Accessible | None = None
    ) -> bool:
        if self.utilities.is_editable_message(obj):
            tokens = ["THUNDERBIRD: Using focus mode for editable message", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["THUNDERBIRD:", obj, "is not an editable message."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return super().use_focus_mode(obj, prev_obj)

    def enable_sticky_browse_mode(
        self,
        event: input_event.InputEvent | None = None,
        force_message: bool = False
    ) -> bool:
        if self.utilities.is_editable_message(focus_manager.get_manager().get_locus_of_focus()):
            return True

        return super().enable_sticky_browse_mode(event, force_message)

    def enable_sticky_focus_mode(
        self,
        event: input_event.InputEvent | None = None,
        force_message: bool = False
    ) -> bool:
        if self.utilities.is_editable_message(focus_manager.get_manager().get_locus_of_focus()):
            return True

        return super().enable_sticky_focus_mode(event, force_message)

    def toggle_presentation_mode(
        self,
        event: input_event.InputEvent | None = None,
        document: Atspi.Accessible | None = None,
        notify_user: bool = True
    ) -> bool:
        if self._in_focus_mode \
           and self.utilities.is_editable_message(focus_manager.get_manager().get_locus_of_focus()):
            return True

        return super().toggle_presentation_mode(event, document)

    def on_busy_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:busy accessibility events."""

        # TODO - JD: Can this logic be moved to the web script?
        if self.utilities.is_editable_message(event.source):
            return True

        if self.in_focus_mode():
            return True

        return super().on_busy_changed(event)

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        if self.utilities.is_editable_message(event.source):
            if event.detail1 == -1:
                return True
            self.spellcheck.set_document_position(event.source, event.detail1)
            if self.spellcheck.is_active():
                return True

        return super().on_caret_moved(event)

    def on_name_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-name events."""

        if AXObject.get_name(event.source) == self.spellcheck.get_misspelled_word():
            self.spellcheck.present_error_details()
            return True

        return super().on_name_changed(event)

    def on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:showing accessibility events."""

        # We present changes when the list has focus via focus-changed events.
        if event.source == self.spellcheck.get_suggestions_list():
            return True

        parent = AXObject.get_parent(event.source)
        if AXUtilities.is_combo_box(parent) and not AXUtilities.is_focused(parent):
            return True

        return super().on_selection_changed(event)

    def on_sensitive_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:sensitive accessibility events."""

        if event.source == self.spellcheck.get_change_to_entry() \
           and self.spellcheck.present_completion_message():
            return True

        return super().on_sensitive_changed(event)

    def on_text_deleted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:delete accessibility events."""

        if AXUtilities.is_label(event.source) \
           and AXUtilities.is_status_bar(AXObject.get_parent(event.source)):
            return True

        return super().on_text_deleted(event)

    def on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        parent = AXObject.get_parent(event.source)
        if AXUtilities.is_label(event.source) and AXUtilities.is_status_bar(parent):
            return True

        if len(event.any_data) > 1 and event.source == self.spellcheck.get_change_to_entry():
            return True

        # Try to stop unwanted chatter when a message is being replied to.
        # See bgo#618484.
        if event.type.endswith("system") and self.utilities.is_editable_message(event.source):
            return True

        return super().on_text_inserted(event)

    def on_text_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-selection-changed accessibility events."""

        if event.source == self.spellcheck.get_change_to_entry():
            return True

        _reason = AXUtilities.get_text_event_reason(event)
        if self.utilities.is_editable_message(event.source) and self.spellcheck.is_active():
            selection_start = AXText.get_selection_start_offset(event.source)
            if selection_start >= 0:
                self.spellcheck.set_document_position(event.source, selection_start)
            return True

        return super().on_text_selection_changed(event)

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        super().on_window_activated(event)
        if not self.spellcheck.is_spell_check_window(event.source):
            self.spellcheck.deactivate()
            return True

        self.spellcheck.present_error_details()
        entry = self.spellcheck.get_change_to_entry()
        focus_manager.get_manager().set_locus_of_focus(None, entry, False)
        self.update_braille(entry)
        return True

    def on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""

        self.spellcheck.deactivate()
        self.utilities.clear_content_cache()
        return super().on_window_deactivated(event)
