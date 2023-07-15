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

import orca.orca_state as orca_state
import orca.spellcheck as spellcheck
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


class SpellCheck(spellcheck.SpellCheck):

    def __init__(self, script):
        super(SpellCheck, self).__init__(script)

    def isAutoFocusEvent(self, event):
        if event.source != self._changeToEntry:
            return False

        if not AXUtilities.is_push_button(orca_state.locusOfFocus):
            return False

        lastKey, mods = self._script.utilities.lastKeyAndModifiers()
        keys = self._script.utilities.mnemonicShortcutAccelerator(orca_state.locusOfFocus)
        for key in keys:
            if key.endswith(lastKey.upper()):
                return True

        return False

    def _isCandidateWindow(self, window):
        if not AXUtilities.is_dialog(window):
            return False

        def isNonSpellCheckChild(x):
            return AXUtilities.is_page_tab_list(x) or AXUtilities.is_split_pane(x)

        if AXObject.find_descendant(window, isNonSpellCheckChild):
            return False

        return True

    def _findChangeToEntry(self, root):
        def isSingleLineEntry(x):
            return AXUtilities.is_entry(x) and AXUtilities.is_single_line(x)

        return AXObject.find_descendant(root, isSingleLineEntry)

    def _findErrorWidget(self, root):
        def isError(x):
            return AXUtilities.is_label(x) \
                    and ":" not in AXObject.get_name(x) \
                    and not AXObject.get_relations(x)

        return AXObject.find_descendant(root, isError)

    def _findSuggestionsList(self, root):
        def isList(x):
            if not AXObject.supports_selection(x):
                return False
            return AXUtilities.is_list_box(x) or AXUtilities.is_list(x)

        return AXObject.find_descendant(root, isList)

    def _getSuggestionIndexAndPosition(self, suggestion):
        attrs = self._script.utilities.objectAttributes(suggestion)
        index = attrs.get("posinset")
        total = attrs.get("setsize")
        if index is None or total is None:
            return super()._getSuggestionIndexAndPosition(suggestion)

        return int(index), int(total)
