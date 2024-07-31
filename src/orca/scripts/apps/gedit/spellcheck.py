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

from orca import spellcheck
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


class SpellCheck(spellcheck.SpellCheck):

    def __init__(self, script):
        super(SpellCheck, self).__init__(script)

    def _isCandidateWindow(self, window):
        if not window:
            return False

        if AXUtilities.is_dialog(window):
            return True

        if not AXUtilities.is_frame(window):
            return False

        if AXObject.find_descendant(window, AXUtilities.is_split_pane):
            return False

        return True

    def _findChangeToEntry(self, root):
        def isEntry(x):
            return AXUtilities.is_text(x) and AXUtilities.is_single_line(x)

        return AXObject.find_descendant(root, isEntry)

    def _findErrorWidget(self, root):
        panel = AXObject.find_ancestor(self._changeToEntry, AXUtilities.is_panel)
        if panel is None:
            return None

        def isError(x):
            return AXUtilities.is_label(x) \
                  and ":" not in AXObject.get_name(x) and AXUtilities.object_is_unrelated(x)

        return AXObject.find_descendant(panel, isError)

    def _findSuggestionsList(self, root):
        def isTable(x):
            return AXUtilities.is_table(x) and AXObject.supports_selection(x)

        return AXObject.find_descendant(root, isTable)

    def _getSuggestionIndexAndPosition(self, suggestion):
        index = AXUtilities.get_position_in_set(suggestion)
        total = AXUtilities.get_set_size(suggestion)
        total -= 1
        return index, total
