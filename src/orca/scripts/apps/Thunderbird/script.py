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
from orca.ax_document import AXDocument
from orca.ax_object import AXObject
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

from .spellcheck import SpellCheck

class Script(Gecko.Script):
    """The script for Thunderbird."""

    def __init__(self, app):
        # Store the last autocompleted string for the address fields
        # so that we're not too 'chatty'.  See bug #533042.
        #
        self._lastAutoComplete = ""

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

        if self.spellcheck.isSuggestionsItem(new_focus):
            includeLabel = not self.spellcheck.isSuggestionsItem(old_focus)
            self.update_braille(new_focus)
            self.spellcheck.presentSuggestionListItem(includeLabel=includeLabel)
            return

        super().locus_of_focus_changed(event, old_focus, new_focus)

    def useFocusMode(self, obj, prevObj=None):
        if self.utilities.isEditableMessage(obj):
            tokens = ["THUNDERBIRD: Using focus mode for editable message", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["THUNDERBIRD:", obj, "is not an editable message."]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
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

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        self._lastAutoComplete = ""
        obj = event.source
        if self.spellcheck.isAutoFocusEvent(event):
            focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
            self.update_braille(event.source)

        if not self.utilities.inDocumentContent(obj):
            super().on_focused_changed(event)
            return

        if self.utilities.isEditableMessage(obj):
            super().on_focused_changed(event)
            return

        super().on_focused_changed(event)

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if self.utilities.isEditableMessage(event.source):
            return

        if self.inFocusMode():
            return

        obj = event.source
        if self.utilities.isDocument(obj) and not event.detail1:
            focus = focus_manager.get_manager().get_locus_of_focus()
            if AXObject.get_name(focus) \
                and (AXUtilities.is_frame(focus) or AXUtilities.is_page_tab(focus)):
                focus_manager.get_manager().set_locus_of_focus(event, event.source, False)

            if self.utilities.inDocumentContent():
                self.speakMessage(AXObject.get_name(obj))
                self._presentMessage(obj)

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if self.utilities.isEditableMessage(event.source):
            if event.detail1 == -1:
                return
            self.spellcheck.setDocumentPosition(event.source, event.detail1)
            if self.spellcheck.isActive():
                return

        super().on_caret_moved(event)

    def on_selection_changed(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        # We present changes when the list has focus via focus-changed events.
        if event.source == self.spellcheck.getSuggestionsList():
            return

        parent = AXObject.get_parent(event.source)
        if AXUtilities.is_combo_box(parent) and not AXUtilities.is_focused(parent):
            return

        super().on_selection_changed(event)

    def on_sensitive_changed(self, event):
        """Callback for object:state-changed:sensitive accessibility events."""

        if event.source == self.spellcheck.getChangeToEntry() \
           and self.spellcheck.presentCompletionMessage():
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

        if len(event.any_data) > 1 and event.source == self.spellcheck.getChangeToEntry():
            return

        isSystemEvent = event.type.endswith("system")

        # Try to stop unwanted chatter when a message is being replied to.
        # See bgo#618484.
        if isSystemEvent and self.utilities.isEditableMessage(event.source):
            return

        # Speak the autocompleted text, but only if it is different
        # address so that we're not too "chatty." See bug #533042.
        if AXUtilities.is_autocomplete(parent):
            if len(event.any_data) == 1:
                default.Script.on_text_inserted(self, event)
                return

            if self._lastAutoComplete and self._lastAutoComplete in event.any_data:
                return

            # Mozilla cannot seem to get their ":system" suffix right
            # to save their lives, so we'll add yet another sad hack.
            if isSystemEvent or AXText.has_selected_text(event.source):
                voice = self.speech_generator.voice(obj=event.source, string=event.any_data)
                self.speakMessage(event.any_data, voice=voice)
                self._lastAutoComplete = event.any_data
                return

        super().on_text_inserted(event)

    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        obj = event.source
        spellCheckEntry = self.spellcheck.getChangeToEntry()
        if obj == spellCheckEntry:
            return

        if self.utilities.isEditableMessage(obj) and self.spellcheck.isActive():
            selStart = AXText.get_selection_start_offset(obj)
            if selStart >= 0:
                self.spellcheck.setDocumentPosition(obj, selStart)
            return

        super().on_text_selection_changed(event)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if AXObject.get_name(event.source) == self.spellcheck.getMisspelledWord():
            self.spellcheck.presentErrorDetails()
            return

        super().on_name_changed(event)

    def _presentMessage(self, documentFrame):
        """Presents the first line of the message, or the entire message,
        depending on the user's sayAllOnLoad setting."""

        [obj, offset] = self.utilities.findFirstCaretContext(documentFrame, 0)
        self.utilities.setCaretPosition(obj, offset)
        self.update_braille(obj)

        if settings_manager.get_manager().get_setting('pageSummaryOnLoad'):
            tokens = ["THUNDERBIRD: Getting page summary for", documentFrame]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            summary = AXDocument.get_document_summary(documentFrame)
            if summary:
                self.presentMessage(summary)

        if not settings_manager.get_manager().get_setting('sayAllOnLoad'):
            msg = "THUNDERBIRD: SayAllOnLoad is False. Presenting line."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(obj, offset)
            self.speakContents(contents)
            return

        if settings_manager.get_manager().get_setting('enableSpeech'):
            msg = "THUNDERBIRD: SayAllOnLoad is True and speech is enabled"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.say_all(None)

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        super().on_window_activated(event)
        if not self.spellcheck.isCheckWindow(event.source):
            self.spellcheck.deactivate()
            return

        self.spellcheck.presentErrorDetails()
        entry = self.spellcheck.getChangeToEntry()
        focus_manager.get_manager().set_locus_of_focus(None, entry, False)
        self.update_braille(entry)

    def on_window_deactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        super().on_window_deactivated(event)
        self.spellcheck.deactivate()
        self.utilities.clearContentCache()
