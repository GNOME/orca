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

# pylint: disable=duplicate-code
# pylint: disable=too-many-public-methods

"""Custom script for Thunderbird."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from orca import cmdnames
from orca import debug
from orca import focus_manager
from orca import input_event
from orca.scripts import default
from orca import settings_manager
from orca.scripts.toolkits import Gecko
from orca.ax_object import AXObject
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

from .spellcheck import SpellCheck

class Script(Gecko.Script):
    """The script for Thunderbird."""

    def __init__(self, app):
        if settings_manager.get_manager().get_setting('sayAllOnLoad') is None:
            settings_manager.get_manager().set_setting('sayAllOnLoad', False)
        if settings_manager.get_manager().get_setting('pageSummaryOnLoad') is None:
            settings_manager.get_manager().set_setting('pageSummaryOnLoad', False)

        super().__init__(app)

    def setup_input_event_handlers(self):
        """Defines the input event handlers for this script."""

        super().setup_input_event_handlers()

        self.input_event_handlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.togglePresentationMode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.input_event_handlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyFocusMode,
                cmdnames.SET_FOCUS_MODE_STICKY)

        self.input_event_handlers["enableStickyBrowseModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyBrowseMode,
                cmdnames.SET_BROWSE_MODE_STICKY)

    def get_spellcheck(self):
        """Returns the spellcheck support for this script."""

        return SpellCheck(self)

    def get_app_preferences_gui(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = super().get_app_preferences_gui()

        self._sayAllOnLoadCheckButton.set_active(
            settings_manager.get_manager().get_setting('sayAllOnLoad'))
        self._pageSummaryOnLoadCheckButton.set_active(
            settings_manager.get_manager().get_setting('pageSummaryOnLoad'))

        spellcheck = self.spellcheck.get_app_preferences_gui()
        grid.attach(spellcheck, 0, len(grid.get_children()), 1, 1)
        grid.show_all()

        return grid

    def get_preferences_from_gui(self):
        """Returns a dictionary with the app-specific preferences."""

        prefs = super().get_preferences_from_gui()
        prefs['sayAllOnLoad'] = self._sayAllOnLoadCheckButton.get_active()
        prefs['pageSummaryOnLoad'] = self._pageSummaryOnLoadCheckButton.get_active()
        prefs.update(self.spellcheck.get_preferences_from_gui())

        return prefs

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Handles changes of focus of interest to the script."""

        if self.spellcheck.is_suggestions_item(new_focus):
            include_label = not self.spellcheck.is_suggestions_item(old_focus)
            self.update_braille(new_focus)
            self.spellcheck.present_suggestion_list_item(include_label=include_label)
            return

        super().locus_of_focus_changed(event, old_focus, new_focus)

    def useFocusMode(self, obj, prevObj=None):
        if self.utilities.isEditableMessage(obj):
            tokens = ["THUNDERBIRD: Using focus mode for editable message", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["THUNDERBIRD:", obj, "is not an editable message."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return super().useFocusMode(obj, prevObj)

    def enableStickyBrowseMode(self, inputEvent, forceMessage=False):
        if self.utilities.isEditableMessage(focus_manager.get_manager().get_locus_of_focus()):
            return

        super().enableStickyBrowseMode(inputEvent, forceMessage)

    def enableStickyFocusMode(self, inputEvent, forceMessage=False):
        if self.utilities.isEditableMessage(focus_manager.get_manager().get_locus_of_focus()):
            return

        super().enableStickyFocusMode(inputEvent, forceMessage)

    def togglePresentationMode(self, inputEvent, documentFrame=None):
        if self._inFocusMode \
           and self.utilities.isEditableMessage(focus_manager.get_manager().get_locus_of_focus()):
            return

        super().togglePresentationMode(inputEvent, documentFrame)

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        # TODO - JD: Can this logic be moved to the web script?
        if self.utilities.isEditableMessage(event.source):
            return

        if self.inFocusMode():
            return

        super().on_busy_changed(event)

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if self.utilities.isEditableMessage(event.source):
            if event.detail1 == -1:
                return
            self.spellcheck.set_document_position(event.source, event.detail1)
            if self.spellcheck.is_active():
                return

        super().on_caret_moved(event)

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        if self.spellcheck.is_autofocus_event(event):
            focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
            self.update_braille(event.source)

        super().on_focused_changed(event)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if AXObject.get_name(event.source) == self.spellcheck.get_misspelled_word():
            self.spellcheck.present_error_details()
            return

        super().on_name_changed(event)

    def on_selection_changed(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        # We present changes when the list has focus via focus-changed events.
        if event.source == self.spellcheck.get_suggestions_list():
            return

        parent = AXObject.get_parent(event.source)
        if AXUtilities.is_combo_box(parent) and not AXUtilities.is_focused(parent):
            return

        super().on_selection_changed(event)

    def on_sensitive_changed(self, event):
        """Callback for object:state-changed:sensitive accessibility events."""

        if event.source == self.spellcheck.get_change_to_entry() \
           and self.spellcheck.present_completion_message():
            return

        super().on_sensitive_changed(event)

    def on_showing_changed(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        # TODO - JD: Once there are separate scripts for the Gecko toolkit
        # and the Firefox browser, this method can be deleted. It's here
        # right now just to prevent the Gecko script from presenting non-
        # existent browsery autocompletes for Thunderbird.

        if event.detail1 and self.utilities.isMenuWithNoSelectedChild(event.source) \
           and self.utilities.topLevelObjectIsActiveWindow(event.source):
            focus_manager.get_manager().set_locus_of_focus(event, event.source, True)
            return

        default.Script.on_showing_changed(self, event)

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if AXUtilities.is_label(event.source) \
           and AXUtilities.is_status_bar(AXObject.get_parent(event.source)):
            return

        super().on_text_deleted(event)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        parent = AXObject.get_parent(event.source)
        if AXUtilities.is_label(event.source) and AXUtilities.is_status_bar(parent):
            return

        if len(event.any_data) > 1 and event.source == self.spellcheck.get_change_to_entry():
            return

        # Try to stop unwanted chatter when a message is being replied to.
        # See bgo#618484.
        if event.type.endswith("system") and self.utilities.isEditableMessage(event.source):
            return

        super().on_text_inserted(event)

    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if event.source == self.spellcheck.get_change_to_entry():
            return

        if self.utilities.isEditableMessage(event.source) and self.spellcheck.is_active():
            selection_start = AXText.get_selection_start_offset(event.source)
            if selection_start >= 0:
                self.spellcheck.set_document_position(event.source, selection_start)
            return

        super().on_text_selection_changed(event)

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        super().on_window_activated(event)
        if not self.spellcheck.is_spell_check_window(event.source):
            self.spellcheck.deactivate()
            return

        self.spellcheck.present_error_details()
        entry = self.spellcheck.get_change_to_entry()
        focus_manager.get_manager().set_locus_of_focus(None, entry, False)
        self.update_braille(entry)

    def on_window_deactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        super().on_window_deactivated(event)
        self.spellcheck.deactivate()
        self.utilities.clearContentCache()
