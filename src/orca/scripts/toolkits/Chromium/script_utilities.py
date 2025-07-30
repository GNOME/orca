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

# pylint: disable=too-many-return-statements

"""Custom script utilities for Chromium"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018-2019 Igalia, S.L."
__license__   = "LGPL"

import re
from typing import TYPE_CHECKING

from orca import debug
from orca import focus_manager
from orca.scripts import web
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Utilities(web.Utilities):
    """Custom script utilities for Chromium"""

    def get_find_results_count(self, root: Atspi.Accessible | None = None) -> str:
        """Returns a string description of the number of find-in-page results in root."""

        root = root or self._find_container
        if not root:
            return ""

        status_bars = AXUtilities.find_all_status_bars(root)
        if len(status_bars) != 1:
            return ""

        status_bar = status_bars[0]
        # TODO - JD: Is this still needed?
        AXObject.clear_cache(status_bar, False, "Ensuring we have correct name for find results.")
        if len(re.findall(r"\d+", AXObject.get_name(status_bar))) == 2:
            return AXObject.get_name(status_bar)

        return ""

    def _is_find_container(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns True if obj is a find-in-page container."""

        if not obj or self.in_document_content(obj):
            return False

        if obj == self._find_container:
            return True

        result = self.get_find_results_count(obj)
        if result:
            tokens = ["CHROMIUM:", obj, "believed to be find-in-page container (", result, ")"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._find_container = obj
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
        self._find_container = obj
        return True

    def in_find_container(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns True if obj is in a find-in-page container."""

        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if not (AXUtilities.is_entry(obj) or AXUtilities.is_push_button(obj)):
            return False
        if self.in_document_content(obj):
            return False

        result = AXObject.find_ancestor(obj, self._is_find_container)
        if result:
            tokens = ["CHROMIUM:", obj, "believed to be find-in-page widget"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return bool(result)
