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

from orca import focus_manager
from orca import input_event_manager
from orca import spellcheck
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


class SpellCheck(spellcheck.SpellCheck):

    def __init__(self, script):
        super(SpellCheck, self).__init__(script)

    def isAutoFocusEvent(self, event):
        if event.source != self._changeToEntry:
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not AXUtilities.is_push_button(focus):
            return False

        return input_event_manager.get_manager().last_event_was_shortcut_for(focus)

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
                    and AXUtilities.object_is_unrelated(x)

        return AXObject.find_descendant(root, isError)

    def _findSuggestionsList(self, root):
        def isList(x):
            if not AXObject.supports_selection(x):
                return False
            return AXUtilities.is_list_box(x) or AXUtilities.is_list(x)

        return AXObject.find_descendant(root, isList)

    def _getSuggestionIndexAndPosition(self, suggestion):
        attrs = AXObject.get_attributes_dict(suggestion)
        index = attrs.get("posinset")
        total = attrs.get("setsize")
        if index is None or total is None:
            return super()._getSuggestionIndexAndPosition(suggestion)

        return int(index), int(total)
