# Orca
#
# Copyright 2018-2019 Igalia, S.L.
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

# For the "AXUtilities has no ... member"
# pylint: disable=E1101

"""Custom script utilities for Chromium"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018-2019 Igalia, S.L."
__license__   = "LGPL"

import re

from orca import debug
from orca import focus_manager
from orca.scripts import web
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


class Utilities(web.Utilities):
    """Custom script utilities for Chromium"""

    def getFindResultsCount(self, root=None):
        root = root or self._findContainer
        if not root:
            return ""

        statusBars = AXUtilities.find_all_status_bars(root)
        if len(statusBars) != 1:
            return ""

        bar = statusBars[0]
        # TODO - JD: Is this still needed?
        AXObject.clear_cache(bar, False, "Ensuring we have correct name for find results.")
        if len(re.findall(r"\d+", AXObject.get_name(bar))) == 2:
            return AXObject.get_name(bar)

        return ""

    def isFindContainer(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        if obj == self._findContainer:
            return True

        result = self.getFindResultsCount(obj)
        if result:
            tokens = ["CHROMIUM:", obj, "believed to be find-in-page container (", result, ")"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._findContainer = obj
            return True

        # When there are no results due to the absence of a search term, the status
        # bar lacks a name. When there are no results due to lack of match, the name
        # of the status bar is "No results" (presumably localized). Therefore fall
        # back on the widgets. TODO: This would be far easier if Chromium gave us an
        # object attribute we could look for....

        if len(AXUtilities.find_all_entries(obj)) != 1:
            tokens = ["CHROMIUM:", obj, "not believed to be find-in-page container (entry count)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if len(AXUtilities.find_all_push_buttons(obj)) != 3:
            tokens = ["CHROMIUM:", obj, "not believed to be find-in-page container (button count)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if len(AXUtilities.find_all_separators(obj)) != 1:
            tokens = ["CHROMIUM:", obj,
                      "not believed to be find-in-page container (separator count)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["CHROMIUM:", obj, "believed to be find-in-page container (accessibility tree)"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._findContainer = obj
        return True

    def inFindContainer(self, obj=None):
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if not (AXUtilities.is_entry(obj) or AXUtilities.is_push_button(obj)):
            return False
        if self.inDocumentContent(obj):
            return False

        result = AXObject.find_ancestor(obj, self.isFindContainer)
        if result:
            tokens = ["CHROMIUM:", obj, "believed to be find-in-page widget"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result
