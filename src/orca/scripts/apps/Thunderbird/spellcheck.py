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

# pylint: disable=duplicate-code

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
    """Customized support for spellcheck in Thunderbird."""

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

        def is_non_spell_check_child(x):
            return AXUtilities.is_page_tab_list(x) or AXUtilities.is_split_pane(x)

        if AXObject.find_descendant(window, is_non_spell_check_child):
            return False

        return True

    def _findChangeToEntry(self, root):
        return AXObject.find_descendant(root, AXUtilities.is_single_line_entry)

    def _findErrorWidget(self, root):
        def is_error(x):
            return AXUtilities.is_label(x) \
                    and ":" not in AXObject.get_name(x) \
                    and AXUtilities.object_is_unrelated(x)

        return AXObject.find_descendant(root, is_error)

    def _findSuggestionsList(self, root):
        def is_list(x):
            if not AXObject.supports_selection(x):
                return False
            return AXUtilities.is_list_box(x) or AXUtilities.is_list(x)

        return AXObject.find_descendant(root, is_list)

    def _getSuggestionIndexAndPosition(self, suggestion):
        attrs = AXObject.get_attributes_dict(suggestion)
        index = attrs.get("posinset")
        total = attrs.get("setsize")
        if index is None or total is None:
            return super()._getSuggestionIndexAndPosition(suggestion)

        return int(index), int(total)
