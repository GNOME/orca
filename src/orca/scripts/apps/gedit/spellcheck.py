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

"""Customized support for spellcheck in Gedit."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import orca.spellcheck as spellcheck

class SpellCheck(spellcheck.SpellCheck):

    def __init__(self, script):
        super(SpellCheck, self).__init__(script)

    def _isCandidateWindow(self, window):
        if not window:
            return False

        role = window.getRole()
        if role == pyatspi.ROLE_DIALOG:
            return True
        if role != pyatspi.ROLE_FRAME:
            return False

        isSplitPane = lambda x: x and x.getRole() == pyatspi.ROLE_SPLIT_PANE
        if pyatspi.findDescendant(window, isSplitPane):
            return False

        return True

    def _findChangeToEntry(self, root):
        isEntry = lambda x: x and x.getRole() == pyatspi.ROLE_TEXT \
                  and x.getState().contains(pyatspi.STATE_SINGLE_LINE)
        return pyatspi.findDescendant(root, isEntry)

    def _findErrorWidget(self, root):
        isPanel = lambda x: x and x.getRole() == pyatspi.ROLE_PANEL
        panel = pyatspi.findAncestor(self._changeToEntry, isPanel)
        if not panel:
            return None

        isError = lambda x: x and x.getRole() == pyatspi.ROLE_LABEL \
                  and not ":" in x.name and not x.getRelationSet()
        return pyatspi.findDescendant(panel, isError)

    def _findSuggestionsList(self, root):
        isTable = lambda x: x and x.getRole() == pyatspi.ROLE_TABLE \
                  and 'Selection' in x.get_interfaces()
        return pyatspi.findDescendant(root, isTable)

    def _getSuggestionIndexAndPosition(self, suggestion):
        index, total = self._script.utilities.getPositionAndSetSize(suggestion)
        total -= 1
        return index, total
