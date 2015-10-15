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

""" Custom script for Thunderbird 3."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.orca as orca
import orca.cmdnames as cmdnames
import orca.debug as debug
import orca.input_event as input_event
import orca.scripts.default as default
import orca.settings_manager as settings_manager
import orca.orca_state as orca_state
import orca.speech as speech
import orca.scripts.toolkits.Gecko as Gecko

from .speech_generator import SpeechGenerator
from .spellcheck import SpellCheck

_settingsManager = settings_manager.getManager()

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

        if _settingsManager.getSetting('sayAllOnLoad') == None:
            _settingsManager.setSetting('sayAllOnLoad', False)

        Gecko.Script.__init__(self, app)

    def setupInputEventHandlers(self):
        Gecko.Script.setupInputEventHandlers(self)

        self.inputEventHandlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.togglePresentationMode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getSpellCheck(self):
        """Returns the spellcheck support for this script."""

        return SpellCheck(self)

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = Gecko.Script.getAppPreferencesGUI(self)

        self._sayAllOnLoadCheckButton.set_active(
            _settingsManager.getSetting('sayAllOnLoad'))

        spellcheck = self.spellcheck.getAppPreferencesGUI()
        grid.attach(spellcheck, 0, len(grid.get_children()), 1, 1)
        grid.show_all()

        return grid

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        prefs = Gecko.Script.getPreferencesFromGUI(self)
        prefs['sayAllOnLoad'] = self._sayAllOnLoadCheckButton.get_active()
        prefs.update(self.spellcheck.getPreferencesFromGUI())

        return prefs

    def doWhereAmI(self, inputEvent, basicOnly):
        """Performs the whereAmI operation."""

        if self.spellcheck.isActive():
            self.spellcheck.presentErrorDetails(not basicOnly)

        super().doWhereAmI(inputEvent, basicOnly)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if self.spellcheck.isSuggestionsItem(newFocus):
            includeLabel = not self.spellcheck.isSuggestionsItem(oldFocus)
            self.updateBraille(newFocus)
            self.spellcheck.presentSuggestionListItem(includeLabel=includeLabel)
            return

        super().locusOfFocusChanged(event, oldFocus, newFocus)

    def _useFocusMode(self, obj):
        if self.isEditableMessage(obj):
            return True

        return Gecko.Script._useFocusMode(self, obj)

    def togglePresentationMode(self, inputEvent):
        if self._inFocusMode and self.isEditableMessage(orca_state.locusOfFocus):
            return

        Gecko.Script.togglePresentationMode(self, inputEvent)

    def useStructuralNavigationModel(self):
        """Returns True if structural navigation should be enabled here."""

        if self.isEditableMessage(orca_state.locusOfFocus):
            return False

        return Gecko.Script.useStructuralNavigationModel(self)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        self._lastAutoComplete = ""
        self.pointOfReference['lastAutoComplete'] = None

        obj = event.source
        if self.spellcheck.isAutoFocusEvent(event):
            orca.setLocusOfFocus(event, event.source, False)
            self.updateBraille(orca_state.locusOfFocus)

        if not self.utilities.inDocumentContent(obj):
            default.Script.onFocusedChanged(self, event)
            return

        if self.isEditableMessage(obj):
            default.Script.onFocusedChanged(self, event)
            return

        Gecko.Script.onFocusedChanged(self, event)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        obj = event.source
        if obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME and not event.detail1:
            try:
                role = orca_state.locusOfFocus.getRole()
                name = orca_state.locusOfFocus.name
            except:
                pass
            else:
                if role in [pyatspi.ROLE_FRAME, pyatspi.ROLE_PAGE_TAB] and name:
                    orca.setLocusOfFocus(event, event.source, False)

            if self.utilities.inDocumentContent():
                self.speakMessage(obj.name)
                self._presentMessage(obj)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if self.isEditableMessage(event.source):
            if event.detail1 == -1:
                return
            self.spellcheck.setDocumentPosition(event.source, event.detail1)
            if self.spellcheck.isActive():
                return

        Gecko.Script.onCaretMoved(self, event)

    def onChildrenChanged(self, event):
        """Callback for object:children-changed accessibility events."""

        default.Script.onChildrenChanged(self, event)

    def onSelectionChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        # We present changes when the list has focus via focus-changed events.
        if event.source == self.spellcheck.getSuggestionsList():
            return

        parent = event.source.parent
        if parent and parent.getRole() == pyatspi.ROLE_COMBO_BOX \
           and not parent.getState().contains(pyatspi.STATE_FOCUSED):
            return

        Gecko.Script.onSelectionChanged(self, event)

    def onSensitiveChanged(self, event):
        """Callback for object:state-changed:sensitive accessibility events."""

        if event.source == self.spellcheck.getChangeToEntry() \
           and self.spellcheck.presentCompletionMessage():
            return

        Gecko.Script.onSensitiveChanged(self, event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        # TODO - JD: Once there are separate scripts for the Gecko toolkit
        # and the Firefox browser, this method can be deleted. It's here
        # right now just to prevent the Gecko script from presenting non-
        # existent browsery autocompletes for Thunderbird.

        default.Script.onShowingChanged(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is from an an object.

        Arguments:
        - event: the Event
        """

        obj = event.source
        parent = obj.parent

        try:
            role = event.source.getRole()
            parentRole = parent.getRole()
        except:
            return

        if role == pyatspi.ROLE_LABEL and parentRole == pyatspi.ROLE_STATUS_BAR:
            return

        Gecko.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        obj = event.source
        try:
            role = obj.getRole()
            parentRole = obj.parent.getRole()
        except:
            return

        if role == pyatspi.ROLE_LABEL and parentRole == pyatspi.ROLE_STATUS_BAR:
            return

        if len(event.any_data) > 1 and obj == self.spellcheck.getChangeToEntry():
            return

        isSystemEvent = event.type.endswith("system")

        # Try to stop unwanted chatter when a message is being replied to.
        # See bgo#618484.
        if isSystemEvent and self.isEditableMessage(obj):
            return

        # Speak the autocompleted text, but only if it is different
        # address so that we're not too "chatty." See bug #533042.
        if parentRole == pyatspi.ROLE_AUTOCOMPLETE:
            if len(event.any_data) == 1:
                default.Script.onTextInserted(self, event)
                return

            if self._lastAutoComplete and self._lastAutoComplete in event.any_data:
                return

            # Mozilla cannot seem to get their ":system" suffix right
            # to save their lives, so we'll add yet another sad hack.
            try:
                text = event.source.queryText()
            except:
                hasSelection = False
            else:
                hasSelection = text.getNSelections() > 0
            if hasSelection or isSystemEvent:
                speech.speak(event.any_data)
                self._lastAutoComplete = event.any_data
                self.pointOfReference['lastAutoComplete'] = hash(obj)
                return

        Gecko.Script.onTextInserted(self, event)

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        obj = event.source
        spellCheckEntry = self.spellcheck.getChangeToEntry()
        if obj == spellCheckEntry:
            return

        if self.isEditableMessage(obj) and self.spellcheck.isActive():
            text = obj.queryText()
            selStart, selEnd = text.getSelection(0)
            self.spellcheck.setDocumentPosition(obj, selStart)
            return

        default.Script.onTextSelectionChanged(self, event)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if event.source.name == self.spellcheck.getMisspelledWord():
            self.spellcheck.presentErrorDetails()
            return

        obj = event.source

        # If the user has just deleted an open mail message, then we want to
        # try to speak the new name of the open mail message frame and also
        # present the first line of that message to be consistent with what
        # we do when a new message window is opened. See bug #540039 for more
        # details.
        #
        rolesList = [pyatspi.ROLE_DOCUMENT_FRAME,
                     pyatspi.ROLE_INTERNAL_FRAME,
                     pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_APPLICATION]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            lastKey, mods = self.utilities.lastKeyAndModifiers()
            if lastKey == "Delete":
                speech.speak(obj.name)
                [obj, offset] = self.utilities.findFirstCaretContext(obj, 0)
                self.utilities.setCaretPosition(obj, offset)
                return

    def _presentMessage(self, documentFrame):
        """Presents the first line of the message, or the entire message,
        depending on the user's sayAllOnLoad setting."""

        [obj, offset] = self.utilities.findFirstCaretContext(documentFrame, 0)
        self.utilities.setCaretPosition(obj, offset)
        self.updateBraille(obj)
        if not _settingsManager.getSetting('sayAllOnLoad'):
            contents = self.utilities.getLineContentsAtOffset(obj, offset)
            self.speakContents(contents)
        elif _settingsManager.getSetting('enableSpeech'):
            self.sayAll(None)

    def sayCharacter(self, obj):
        """Speaks the character at the current caret position."""

        if self.isEditableMessage(obj):
            text = self.utilities.queryNonEmptyText(obj)
            if text and text.caretOffset + 1 >= text.characterCount:
                default.Script.sayCharacter(self, obj)
                return

        Gecko.Script.sayCharacter(self, obj)

    def sayWord(self, obj):
        """Speaks the word at the current caret position."""

        contextObj, offset = self.utilities.getCaretContext(documentFrame=None)
        if contextObj != obj:
            Gecko.Script.sayWord(self, obj)
            return

        wordContents = self.utilities.getWordContentsAtOffset(obj, offset)
        textObj, startOffset, endOffset, word = wordContents[0]
        self.speakMisspelledIndicator(textObj, startOffset)
        self.speakContents(wordContents)

    def toggleFlatReviewMode(self, inputEvent=None):
        """Toggles between flat review mode and focus tracking mode."""

        # If we're leaving flat review dump the cache. See bug 568658.
        #
        if self.flatReviewContext:
            pyatspi.clearCache()

        return default.Script.toggleFlatReviewMode(self, inputEvent)

    def isNonHTMLEntry(self, obj):
        """Checks for ROLE_ENTRY areas that are not part of an HTML
        document.  See bug #607414.

        Returns True is this is something like the Subject: entry
        """
        result = obj and obj.getRole() == pyatspi.ROLE_ENTRY \
            and not self.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_DOCUMENT_FRAME], [pyatspi.ROLE_FRAME])
        return result

    def isEditableMessage(self, obj):
        """Returns True if this is a editable message."""

        if not obj:
            return False

        if not obj.getState().contains(pyatspi.STATE_EDITABLE):
            return False

        if self.isNonHTMLEntry(obj):
            return False

        return True

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        Gecko.Script.onWindowActivated(self, event)
        if not self.spellcheck.isCheckWindow(event.source):
            self.spellcheck.deactivate()
            return

        self.spellcheck.presentErrorDetails()
        orca.setLocusOfFocus(None, self.spellcheck.getChangeToEntry(), False)
        self.updateBraille(orca_state.locusOfFocus)

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        Gecko.Script.onWindowDeactivated(self, event)
        self.spellcheck.deactivate()
