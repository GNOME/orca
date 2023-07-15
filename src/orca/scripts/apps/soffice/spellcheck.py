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
        if self._script.utilities.isDead(window):
            msg = "SOFFICE: %s is not spellcheck window because it's dead." % window
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        rv = self._windows.get(hash(window))
        if rv is not None:
            msg = "SOFFICE: %s is spellcheck window: %s" % (window, rv)
            debug.println(debug.LEVEL_INFO, msg, True)
            return rv

        dialog = self._findChildDialog(window)
        if not dialog:
            self._windows[hash(window)] = False
            msg = "SOFFICE: %s is not spellcheck window because the dialog was not found." % window
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if AXObject.find_descendant(dialog, AXUtilities.is_page_tab_list) is not None:
            self._windows[hash(window)] = False
            self._windows[hash(dialog)] = False
            msg = "SOFFICE: %s is not spellcheck dialog because a page tab list was found." % dialog
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        rv = AXObject.find_descendant(dialog, AXUtilities.is_combo_box) is not None
        msg = "SOFFICE: %s is spellcheck dialog based on combobox descendant: %s" % (dialog, rv)
        debug.println(debug.LEVEL_INFO, msg, True)
        self._windows[hash(dialog)] = rv
        return rv

    def _findErrorWidget(self, root):
        def isError(x):
            if not AXObject.supports_editable_text(x):
                return False
            return AXUtilities.is_focusable(x) and AXUtilities.is_multi_line(x)

        rv = AXObject.find_descendant(root, isError)
        msg = "SOFFICE: Error widget for: %s is: %s" % (root, rv)
        debug.println(debug.LEVEL_INFO, msg, True)
        return rv

    def _findSuggestionsList(self, root):
        def isSelectableList(x):
            if not AXObject.supports_selection(x):
                return False
            return AXUtilities.is_list(x) \
                or AXUtilities.is_list_box(x) \
                or AXUtilities.is_tree_table(x)

        rv = AXObject.find_descendant(root, isSelectableList)
        msg = "SOFFICE: Suggestions list for: %s is: %s" % (root, rv)
        debug.println(debug.LEVEL_INFO, msg, True)
        return rv

    def _getSuggestionIndexAndPosition(self, suggestion):
        index, total = self._script.utilities.getPositionAndSetSize(suggestion)
        return index + 1, total

    def getMisspelledWord(self):
        try:
            text = self._errorWidget.queryText()
        except Exception:
            return ""

        offset, string = 0, ""
        while 0 <= offset < text.characterCount:
            attributes, start, end = text.getAttributeRun(offset, False)
            attrs = dict([attr.split(":", 1) for attr in attributes])
            if attrs.get("fg-color", "").replace(" ", "") == "255,0,0":
                return text.getText(start, end)
            offset = max(end, offset + 1)

        return string

    def presentContext(self):
        if not self.isActive():
            return False

        try:
            text = self._errorWidget.queryText()
        except Exception:
            return False

        string = text.getText(0, -1)
        if not string:
            return False

        msg = messages.MISSPELLED_WORD_CONTEXT % string
        voice = self._script.speechGenerator.voice(string=msg)
        self._script.speakMessage(msg, voice=voice)
        return True
