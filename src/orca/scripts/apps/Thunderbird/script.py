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

import orca.cmdnames as cmdnames
import orca.debug as debug
import orca.focus_manager as focus_manager
import orca.input_event as input_event
import orca.scripts.default as default
import orca.settings_manager as settings_manager
import orca.scripts.toolkits.Gecko as Gecko
from orca.ax_document import AXDocument
from orca.ax_object import AXObject
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

from .spellcheck import SpellCheck

########################################################################
#                                                                      #
# The Thunderbird script class.                                        #
#                                                                      #
########################################################################

class Script(Gecko.Script):
    """The script for Thunderbird."""

    def __init__(self, app):
        """ Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Store the last autocompleted string for the address fields
        # so that we're not too 'chatty'.  See bug #533042.
        #
        self._lastAutoComplete = ""

        if settings_manager.getManager().getSetting('sayAllOnLoad') is None:
            settings_manager.getManager().setSetting('sayAllOnLoad', False)
        if settings_manager.getManager().getSetting('pageSummaryOnLoad') is None:
            settings_manager.getManager().setSetting('pageSummaryOnLoad', False)

        super().__init__(app)

    def setupInputEventHandlers(self):
        super().setupInputEventHandlers()

        self.inputEventHandlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.togglePresentationMode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.inputEventHandlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyFocusMode,
                cmdnames.SET_FOCUS_MODE_STICKY)

        self.inputEventHandlers["enableStickyBrowseModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyBrowseMode,
                cmdnames.SET_BROWSE_MODE_STICKY)

    def getSpellCheck(self):
        """Returns the spellcheck support for this script."""

        return SpellCheck(self)

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = super().getAppPreferencesGUI()

        self._sayAllOnLoadCheckButton.set_active(
            settings_manager.getManager().getSetting('sayAllOnLoad'))
        self._pageSummaryOnLoadCheckButton.set_active(
            settings_manager.getManager().getSetting('pageSummaryOnLoad'))

        spellcheck = self.spellcheck.getAppPreferencesGUI()
        grid.attach(spellcheck, 0, len(grid.get_children()), 1, 1)
        grid.show_all()

        return grid

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        prefs = super().getPreferencesFromGUI()
        prefs['sayAllOnLoad'] = self._sayAllOnLoadCheckButton.get_active()
        prefs['pageSummaryOnLoad'] = self._pageSummaryOnLoadCheckButton.get_active()
        prefs.update(self.spellcheck.getPreferencesFromGUI())

        return prefs

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if self.spellcheck.isSuggestionsItem(newFocus):
            includeLabel = not self.spellcheck.isSuggestionsItem(oldFocus)
            self.updateBraille(newFocus)
            self.spellcheck.presentSuggestionListItem(includeLabel=includeLabel)
            return

        super().locusOfFocusChanged(event, oldFocus, newFocus)

    def useFocusMode(self, obj, prevObj=None):
        if self.utilities.isEditableMessage(obj):
            tokens = ["THUNDERBIRD: Using focus mode for editable message", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["THUNDERBIRD:", obj, "is not an editable message."]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return super().useFocusMode(obj, prevObj)

    def enableStickyBrowseMode(self, inputEvent, forceMessage=False):
        if self.utilities.isEditableMessage(focus_manager.getManager().get_locus_of_focus()):
            return

        super().enableStickyBrowseMode(inputEvent, forceMessage)

    def enableStickyFocusMode(self, inputEvent, forceMessage=False):
        if self.utilities.isEditableMessage(focus_manager.getManager().get_locus_of_focus()):
            return

        super().enableStickyFocusMode(inputEvent, forceMessage)

    def togglePresentationMode(self, inputEvent, documentFrame=None):
        if self._inFocusMode \
           and self.utilities.isEditableMessage(focus_manager.getManager().get_locus_of_focus()):
            return

        super().togglePresentationMode(inputEvent, documentFrame)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        self._lastAutoComplete = ""
        obj = event.source
        if self.spellcheck.isAutoFocusEvent(event):
            focus_manager.getManager().set_locus_of_focus(event, event.source, False)
            self.updateBraille(event.source)

        if not self.utilities.inDocumentContent(obj):
            super().onFocusedChanged(event)
            return

        if self.utilities.isEditableMessage(obj):
            super().onFocusedChanged(event)
            return

        super().onFocusedChanged(event)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if self.utilities.isEditableMessage(event.source):
            return

        if self.inFocusMode():
            return

        obj = event.source
        if self.utilities.isDocument(obj) and not event.detail1:
            focus = focus_manager.getManager().get_locus_of_focus()
            if AXObject.get_name(focus) \
                and (AXUtilities.is_frame(focus) or AXUtilities.is_page_tab(focus)):
                focus_manager.getManager().set_locus_of_focus(event, event.source, False)

            if self.utilities.inDocumentContent():
                self.speakMessage(AXObject.get_name(obj))
                self._presentMessage(obj)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if self.utilities.isEditableMessage(event.source):
            if event.detail1 == -1:
                return
            self.spellcheck.setDocumentPosition(event.source, event.detail1)
            if self.spellcheck.isActive():
                return

        super().onCaretMoved(event)

    def onSelectionChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        # We present changes when the list has focus via focus-changed events.
        if event.source == self.spellcheck.getSuggestionsList():
            return

        parent = AXObject.get_parent(event.source)
        if AXUtilities.is_combo_box(parent) and not AXUtilities.is_focused(parent):
            return

        super().onSelectionChanged(event)

    def onSensitiveChanged(self, event):
        """Callback for object:state-changed:sensitive accessibility events."""

        if event.source == self.spellcheck.getChangeToEntry() \
           and self.spellcheck.presentCompletionMessage():
            return

        super().onSensitiveChanged(event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        # TODO - JD: Once there are separate scripts for the Gecko toolkit
        # and the Firefox browser, this method can be deleted. It's here
        # right now just to prevent the Gecko script from presenting non-
        # existent browsery autocompletes for Thunderbird.

        if event.detail1 and self.utilities.isMenuWithNoSelectedChild(event.source) \
           and self.utilities.topLevelObjectIsActiveWindow(event.source):
            focus_manager.getManager().set_locus_of_focus(event, event.source, True)
            return

        default.Script.onShowingChanged(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is from an object.

        Arguments:
        - event: the Event
        """

        if AXUtilities.is_label(event.source) \
           and AXUtilities.is_status_bar(AXObject.get_parent(event.source)):
            return

        super().onTextDeleted(event)

    def onTextInserted(self, event):
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
                default.Script.onTextInserted(self, event)
                return

            if self._lastAutoComplete and self._lastAutoComplete in event.any_data:
                return

            # Mozilla cannot seem to get their ":system" suffix right
            # to save their lives, so we'll add yet another sad hack.
            if isSystemEvent or AXText.has_selected_text(event.source):
                voice = self.speechGenerator.voice(obj=event.source, string=event.any_data)
                self.speakMessage(event.any_data, voice=voice)
                self._lastAutoComplete = event.any_data
                return

        super().onTextInserted(event)

    def onTextSelectionChanged(self, event):
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

        super().onTextSelectionChanged(event)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if AXObject.get_name(event.source) == self.spellcheck.getMisspelledWord():
            self.spellcheck.presentErrorDetails()
            return

        super().onNameChanged(event)

    def _presentMessage(self, documentFrame):
        """Presents the first line of the message, or the entire message,
        depending on the user's sayAllOnLoad setting."""

        [obj, offset] = self.utilities.findFirstCaretContext(documentFrame, 0)
        self.utilities.setCaretPosition(obj, offset)
        self.updateBraille(obj)

        if settings_manager.getManager().getSetting('pageSummaryOnLoad'):
            tokens = ["THUNDERBIRD: Getting page summary for", documentFrame]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            summary = AXDocument.get_document_summary(documentFrame)
            if summary:
                self.presentMessage(summary)

        if not settings_manager.getManager().getSetting('sayAllOnLoad'):
            msg = "THUNDERBIRD: SayAllOnLoad is False. Presenting line."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(obj, offset)
            self.speakContents(contents)
            return

        if settings_manager.getManager().getSetting('enableSpeech'):
            msg = "THUNDERBIRD: SayAllOnLoad is True and speech is enabled"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.sayAll(None)

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        super().onWindowActivated(event)
        if not self.spellcheck.isCheckWindow(event.source):
            self.spellcheck.deactivate()
            return

        self.spellcheck.presentErrorDetails()
        entry = self.spellcheck.getChangeToEntry()
        focus_manager.getManager().set_locus_of_focus(None, entry, False)
        self.updateBraille(entry)

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        super().onWindowDeactivated(event)
        self.spellcheck.deactivate()
        self.utilities.clearContentCache()
