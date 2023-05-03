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

"""Customized support for spellcheck in Thunderbird."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.orca_state as orca_state
import orca.spellcheck as spellcheck
from orca.ax_object import AXObject


class SpellCheck(spellcheck.SpellCheck):

    def __init__(self, script):
        super(SpellCheck, self).__init__(script)

    def isAutoFocusEvent(self, event):
        if event.source != self._changeToEntry:
            return False

        locusOfFocus = orca_state.locusOfFocus
        if not locusOfFocus:
            return False

        role = AXObject.get_role(locusOfFocus)
        if not role == Atspi.Role.PUSH_BUTTON:
            return False

        lastKey, mods = self._script.utilities.lastKeyAndModifiers()
        keys = self._script.utilities.mnemonicShortcutAccelerator(locusOfFocus)
        for key in keys:
            if key.endswith(lastKey.upper()):
                return True

        return False

    def _isCandidateWindow(self, window):
        if not (window and AXObject.get_role(window) == Atspi.Role.DIALOG):
            return False

        roles = [Atspi.Role.PAGE_TAB_LIST, Atspi.Role.SPLIT_PANE]
        isNonSpellCheckChild = lambda x: x and AXObject.get_role(x) in roles
        if AXObject.find_descendant(window, isNonSpellCheckChild):
            return False

        return True

    def _findChangeToEntry(self, root):
        isEntry = lambda x: x and AXObject.get_role(x) == Atspi.Role.ENTRY \
                  and x.getState().contains(Atspi.StateType.SINGLE_LINE)
        return AXObject.find_descendant(root, isEntry)

    def _findErrorWidget(self, root):
        isError = lambda x: x and AXObject.get_role(x) == Atspi.Role.LABEL \
                  and not ":" in AXObject.get_name(x) and not x.getRelationSet()
        return AXObject.find_descendant(root, isError)

    def _findSuggestionsList(self, root):
        isList = lambda x: AXObject.get_role(x) in [Atspi.Role.LIST, Atspi.Role.LIST_BOX] \
                  and AXObject.supports_selection(x)
        return AXObject.find_descendant(root, isList)

    def _getSuggestionIndexAndPosition(self, suggestion):
        attrs = self._script.utilities.objectAttributes(suggestion)
        index = attrs.get("posinset")
        total = attrs.get("setsize")
        if index is None or total is None:
            return super()._getSuggestionIndexAndPosition(suggestion)

        return int(index), int(total)
