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

"""Custom script utilities for Chromium"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from orca import debug, focus_manager
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts import web

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

    def in_find_container(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns True if obj is in a find-in-page container."""

        if not obj:
            obj = focus_manager.get_manager().get_locus_of_focus()

        if not obj or self.in_document_content(obj):
            return False

        if not (AXUtilities.is_entry(obj) or AXUtilities.is_push_button(obj)):
            return False

        def is_find_bar(x: Atspi.Accessible) -> bool:
            return AXObject.get_attribute(x, "class") == "FindBarView"

        container = AXUtilities.find_ancestor(obj, is_find_bar)
        if container == self._find_container:
            return True

        if container:
            tokens = ["CHROMIUM:", obj, "believed to be find-in-page widget"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._find_container = container
            return True

        return False
