# Orca
#
# Copyright 2014 Igalia, S.L.
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

"""Script-customizable support for application spellcheckers."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import re

from orca import guilabels
from orca import messages
from orca import object_properties
from orca import orca_state
from orca import settings
from orca import settings_manager

_settingsManager = settings_manager.getManager()

class SpellCheck:

    def __init__(self, script, hasChangeToEntry=True):
        self._script = script
        self._hasChangeToEntry = hasChangeToEntry
        self._window = None
        self._errorWidget = None
        self._changeToEntry = None
        self._suggestionsList = None
        self._activated = False
        self._documentPosition = None, -1

        self.spellErrorCheckButton = None
        self.spellSuggestionCheckButton = None
        self.presentContextCheckButton = None

    def activate(self, window):
        if not self._isCandidateWindow(window):
            return False

        if self._hasChangeToEntry:
            self._changeToEntry = self._findChangeToEntry(window)
            if not self._changeToEntry:
                return False

        self._errorWidget = self._findErrorWidget(window)
        if not self._errorWidget:
            return False

        self._suggestionsList = self._findSuggestionsList(window)
        if not self._suggestionsList:
            return False

        self._window = window
        self._activated = True
        return True

    def deactivate(self):
        self._clearState()

    def getDocumentPosition(self):
        return self._documentPosition

    def setDocumentPosition(self, obj, offset):
        self._documentPosition = obj, offset

    def getErrorWidget(self):
        return self._errorWidget

    def getMisspelledWord(self):
        if not self._errorWidget:
            return ""

        return self._script.utilities.displayedText(self._errorWidget)

    def getCompletionMessage(self):
        if not self._errorWidget:
            return ""

        return self._script.utilities.displayedText(self._errorWidget)

    def getChangeToEntry(self):
        return self._changeToEntry

    def getSuggestionsList(self):
        return self._suggestionsList

    def isActive(self):
        return self._activated

    def isCheckWindow(self, window):
        if window and window == self._window:
            return True

        return self.activate(window)

    def isComplete(self):
        try:
            state = self._changeToEntry.getState()
        except:
            return False
        return not state.contains(pyatspi.STATE_SENSITIVE)

    def isAutoFocusEvent(self, event):
        return False

    def isSuggestionsItem(self, obj):
        return obj and obj.parent == self._suggestionsList

    def presentContext(self):
        if not self.isActive():
            return False

        obj, offset = self._documentPosition
        if not (obj and offset >= 0):
            return False

        try:
            text = obj.queryText()
        except:
            return False

        # This should work, but some toolkits are broken.
        boundary = pyatspi.TEXT_BOUNDARY_SENTENCE_START
        string, start, end = text.getTextAtOffset(offset, boundary)

        if not string:
            boundary = pyatspi.TEXT_BOUNDARY_LINE_START
            string, start, end = text.getTextAtOffset(offset, boundary)
            sentences = re.split(r'(?:\.|\!|\?)', string)
            word = self.getMisspelledWord()
            if string.count(word) == 1:
                match = list(filter(lambda x: x.count(word), sentences))
                string = match[0]

        if not string:
            return False

        voice = self._script.voices.get(settings.DEFAULT_VOICE)
        self._script.speakMessage(messages.MISSPELLED_WORD_CONTEXT % string, voice=voice)
        return True

    def presentCompletionMessage(self):
        if not (self.isActive() and self.isComplete()):
            return False

        self._script.clearBraille()
        voice = self._script.voices.get(settings.DEFAULT_VOICE)
        self._script.presentMessage(self.getCompletionMessage(), voice=voice)
        return True

    def presentErrorDetails(self, detailed=False):
        if self.isComplete():
            return False

        if self.presentMistake(detailed):
            self.presentSuggestion(detailed)
            if detailed or _settingsManager.getSetting('spellcheckPresentContext'):
                self.presentContext()
            return True

        return False

    def presentMistake(self, detailed=False):
        if not self.isActive():
            return False

        word = self.getMisspelledWord()
        if not word:
            return False

        voice = self._script.voices.get(settings.DEFAULT_VOICE)
        self._script.speakMessage(messages.MISSPELLED_WORD % word, voice=voice)
        if detailed or _settingsManager.getSetting('spellcheckSpellError'):
            self._script.spellCurrentItem(word)

        return True

    def presentSuggestion(self, detailed=False):
        if not self._hasChangeToEntry:
            return self.presentSuggestionListItem(detailed, includeLabel=True)

        if not self.isActive():
            return False

        entry = self._changeToEntry
        if not entry:
            return False

        label = self._script.utilities.displayedLabel(entry) or entry.name
        string = self._script.utilities.substring(entry, 0, -1)
        voice = self._script.voices.get(settings.DEFAULT_VOICE)
        self._script.speakMessage("%s %s" % (label, string), voice=voice)
        if detailed or _settingsManager.getSetting('spellcheckSpellSuggestion'):
            self._script.spellCurrentItem(string)

        return True

    def presentSuggestionListItem(self, detailed=False, includeLabel=False):
        if not self.isActive():
            return False

        suggestions = self._suggestionsList
        if not suggestions:
            return False

        items = self._script.utilities.selectedChildren(suggestions)
        if not len(items) == 1:
            return False

        if includeLabel:
            label = self._script.utilities.displayedLabel(suggestions) or suggestions.name
        else:
            label = ""
        string = items[0].name
        voice = self._script.voices.get(settings.DEFAULT_VOICE)
        self._script.speakMessage(("%s %s" % (label, string)).strip(), voice=voice)
        if detailed or _settingsManager.getSetting('spellcheckSpellSuggestion'):
            self._script.spellCurrentItem(string)

        if _settingsManager.getSetting('enablePositionSpeaking') \
           and items[0] == orca_state.locusOfFocus:
            index, total = self._getSuggestionIndexAndPosition(items[0])
            msg = object_properties.GROUP_INDEX_SPEECH % {"index": index, "total": total}
            self._script.speakMessage(msg)

        return True

    def _clearState(self):
        self._window = None
        self._errorWidget = None
        self._changeToEntry = None
        self._suggestionsList = None
        self._activated = False

    def _isCandidateWindow(self, window):
        return False

    def _findChangeToEntry(self, root):
        return None

    def _findErrorWidget(self, root):
        return None

    def _findSuggestionsList(self, root):
        return None

    def _getSuggestionIndexAndPosition(self, suggestion):
        return -1, -1

    def getAppPreferencesGUI(self):

        from gi.repository import Gtk

        frame = Gtk.Frame()
        label = Gtk.Label(label="<b>%s</b>" % guilabels.SPELL_CHECK)
        label.set_use_markup(True)
        frame.set_label_widget(label)

        alignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        alignment.set_padding(0, 0, 12, 0)
        frame.add(alignment)

        grid = Gtk.Grid()
        alignment.add(grid)

        label = guilabels.SPELL_CHECK_SPELL_ERROR
        value = _settingsManager.getSetting('spellcheckSpellError')
        self.spellErrorCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.spellErrorCheckButton.set_active(value)
        grid.attach(self.spellErrorCheckButton, 0, 0, 1, 1)

        label = guilabels.SPELL_CHECK_SPELL_SUGGESTION
        value = _settingsManager.getSetting('spellcheckSpellSuggestion')
        self.spellSuggestionCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.spellSuggestionCheckButton.set_active(value)
        grid.attach(self.spellSuggestionCheckButton, 0, 1, 1, 1)

        label = guilabels.SPELL_CHECK_PRESENT_CONTEXT
        value = _settingsManager.getSetting('spellcheckPresentContext')
        self.presentContextCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.presentContextCheckButton.set_active(value)
        grid.attach(self.presentContextCheckButton, 0, 2, 1, 1)

        return frame

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        return {
            'spellcheckSpellError': self.spellErrorCheckButton.get_active(),
            'spellcheckSpellSuggestion': self.spellSuggestionCheckButton.get_active(),
            'spellcheckPresentContext': self.presentContextCheckButton.get_active()
        }
