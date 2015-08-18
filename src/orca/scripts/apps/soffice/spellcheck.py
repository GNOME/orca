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

import pyatspi

from orca import debug
from orca import messages
from orca import settings
from orca import spellcheck


class SpellCheck(spellcheck.SpellCheck):

    def __init__(self, script):
        super().__init__(script, hasChangeToEntry=False)

    def _isCandidateWindow(self, window):
        if window and window.childCount and window.getRole() == pyatspi.ROLE_FRAME:
            child = window[0]
            if child.getRole() == pyatspi.ROLE_DIALOG:
                isPageTabList = lambda x: x and x.getRole() == pyatspi.ROLE_PAGE_TAB_LIST
                if not pyatspi.findDescendant(child, isPageTabList):
                    return True

        return False

    def _findErrorWidget(self, root):
        isError = lambda x: x and x.getRole() == pyatspi.ROLE_TEXT and x.name \
                  and x.parent.getRole() != pyatspi.ROLE_COMBO_BOX
        return pyatspi.findDescendant(root, isError)

    def _findSuggestionsList(self, root):
        isList = lambda x: x and x.getRole() == pyatspi.ROLE_LIST and x.name \
                  and 'Selection' in x.get_interfaces() \
                  and x.parent.getRole() != pyatspi.ROLE_COMBO_BOX
        return pyatspi.findDescendant(root, isList)

    def _getSuggestionIndexAndPosition(self, suggestion):
        index, total = self._script.utilities.getPositionAndSetSize(suggestion)
        return index + 1, total

    def getMisspelledWord(self):
        try:
            text = self._errorWidget.queryText()
        except:
            return ""

        for i in range(text.characterCount):
            attributes, start, end = text.getAttributeRun(i, False)
            if attributes and start != end:
                string = text.getText(start, end)
                break
        else:
            msg = "INFO: No text attributes for word in %s." % self._errorWidget
            debug.println(debug.LEVEL_INFO, msg)
            string = text.getText(0, -1)

        return string

    def presentContext(self):
        if not self.isActive():
            return False

        try:
            text = self._errorWidget.queryText()
        except:
            return False

        string = text.getText(0, -1)
        if not string:
            return False

        voice = self._script.voices.get(settings.DEFAULT_VOICE)
        self._script.speakMessage(messages.MISSPELLED_WORD_CONTEXT % string, voice=voice)
        return True
