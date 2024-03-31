# Orca
#
# Copyright 2015 Igalia, S.L.
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

"""Customized support for spellcheck in LibreOffice."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2015 Igalia, S.L."
__license__   = "LGPL"

from orca import debug
from orca import messages
from orca import spellcheck
from orca.ax_object import AXObject
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

class SpellCheck(spellcheck.SpellCheck):

    def __init__(self, script):
        super().__init__(script, hasChangeToEntry=False)
        self._windows = {}

    def _findChildDialog(self, root):
        if root is None:
            return None

        if AXUtilities.is_dialog(root):
            return root

        return self._findChildDialog(AXObject.get_child(root, 0))

    def _isCandidateWindow(self, window):
        if AXObject.is_dead(window):
            tokens = ["SOFFICE:", window, "is not spellcheck window because it's dead."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        rv = self._windows.get(hash(window))
        if rv is not None:
            tokens = ["SOFFICE:", window, "is spellcheck window:", rv]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return rv

        dialog = self._findChildDialog(window)
        if not dialog:
            self._windows[hash(window)] = False
            tokens = ["SOFFICE:", window,
                      "is not spellcheck window because the dialog was not found."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXObject.find_descendant(dialog, AXUtilities.is_page_tab_list) is not None:
            self._windows[hash(window)] = False
            self._windows[hash(dialog)] = False
            tokens = ["SOFFICE:", dialog,
                      "is not spellcheck dialog because a page tab list was found."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        rv = AXObject.find_descendant(dialog, AXUtilities.is_combo_box) is not None
        tokens = ["SOFFICE:", dialog, "is spellcheck dialog based on combobox descendant:", rv]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        self._windows[hash(dialog)] = rv
        return rv

    def _findErrorWidget(self, root):
        def isError(x):
            if not AXObject.supports_editable_text(x):
                return False
            return AXUtilities.is_focusable(x) and AXUtilities.is_multi_line(x)

        rv = AXObject.find_descendant(root, isError)
        tokens = ["SOFFICE: Error widget for:", root, "is:", rv]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return rv

    def _findSuggestionsList(self, root):
        def isSelectableList(x):
            if not AXObject.supports_selection(x):
                return False
            return AXUtilities.is_list(x) \
                or AXUtilities.is_list_box(x) \
                or AXUtilities.is_tree_table(x)

        rv = AXObject.find_descendant(root, isSelectableList)
        tokens = ["SOFFICE: Suggestions list for:", root, "is:", rv]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return rv

    def _getSuggestionIndexAndPosition(self, suggestion):
        index, total = self._script.utilities.getPositionAndSetSize(suggestion)
        return index + 1, total

    def getMisspelledWord(self):
        length = AXText.get_character_count(self._errorWidget)
        offset, string = 0, ""
        while 0 <= offset < length:
            attrs, start, end = AXText.get_text_attributes_at_offset(self._errorWidget, offset)
            if attrs.get("fg-color", "").replace(" ", "") == "255,0,0":
                return AXText.get_substring(self._errorWidget, start, end)
            offset = max(end, offset + 1)

        return string

    def presentContext(self):
        if not self.isActive():
            return False

        string = AXText.get_all_text(self._errorWidget)
        if not string:
            return False

        msg = messages.MISSPELLED_WORD_CONTEXT % string
        voice = self._script.speech_generator.voice(string=msg)
        self._script.speakMessage(msg, voice=voice)
        return True
