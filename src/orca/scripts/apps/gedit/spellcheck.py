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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.spellcheck as spellcheck
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


class SpellCheck(spellcheck.SpellCheck):

    def __init__(self, script):
        super(SpellCheck, self).__init__(script)

    def _isCandidateWindow(self, window):
        if not window:
            return False

        role = AXObject.get_role(window)
        if role == Atspi.Role.DIALOG:
            return True
        if role != Atspi.Role.FRAME:
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
                  and ":" not in AXObject.get_name(x) and not AXObject.get_relations(x)

        return AXObject.find_descendant(panel, isError)

    def _findSuggestionsList(self, root):
        isTable = lambda x: x and AXObject.get_role(x) == Atspi.Role.TABLE \
                  and AXObject.supports_selection(x)
        return AXObject.find_descendant(root, isTable)

    def _getSuggestionIndexAndPosition(self, suggestion):
        index, total = self._script.utilities.getPositionAndSetSize(suggestion)
        total -= 1
        return index, total
