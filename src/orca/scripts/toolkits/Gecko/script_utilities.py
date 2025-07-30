# Orca
#
# Copyright 2010 Joanmarie Diggs.
# Copyright 2014-2015 Igalia, S.L.
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

"""Custom script utilities for Gecko"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs." \
                "Copyright (c) 2014-2015 Igalia, S.L."
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
    """Custom script utilities for Gecko"""

    def is_editable_message(self, obj: Atspi.Accessible) -> bool:
        """Returns True if this is an editable message."""

        if not AXUtilities.is_editable(obj):
            return False

        document = self.get_document_for_object(obj)
        if AXUtilities.is_editable(document):
            tokens = ["GECKO:", obj, "is in an editable document:", document]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["GECKO: Editable", obj, "not in an editable document"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    def _is_quick_find(self, obj: Atspi.Accessible | None) -> bool:
        if not obj or self.in_document_content(obj):
            return False

        if obj == self._find_container:
            return True

        if not AXUtilities.is_tool_bar(obj):
            return False

        # TODO: This would be far easier if Gecko gave us an object attribute to look for....

        if len(AXUtilities.find_all_entries(obj)) != 1:
            tokens = ["GECKO:", obj, "not believed to be quick-find container (entry count)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if len(AXUtilities.find_all_push_buttons(obj)) != 1:
            tokens = ["GECKO:", obj, "not believed to be quick-find container (button count)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["GECKO:", obj, "believed to be quick-find container (accessibility tree)"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._find_container = obj
        return True

    def _is_find_container(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns True if obj is a find-in-page container."""

        if not obj or self.in_document_content(obj):
            return False

        if obj == self._find_container:
            return True

        if not AXUtilities.is_tool_bar(obj):
            return False

        result = self.get_find_results_count(obj)
        if result:
            tokens = ["GECKO:", obj, "believed to be find-in-page container (", result, ")"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._find_container = obj
            return True

        # TODO: This would be far easier if Gecko gave us an object attribute to look for....

        if len(AXUtilities.find_all_entries(obj)) != 1:
            tokens = ["GECKO:", obj, "not believed to be find-in-page container (entry count)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if len(AXUtilities.find_all_push_buttons(obj)) < 5:
            tokens = ["GECKO:", obj, "not believed to be find-in-page container (button count)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["GECKO:", obj, "believed to be find-in-page container (accessibility tree)"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._find_container = obj
        return True

    def in_find_container(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns True if obj is in a find-in-page container."""

        if not obj:
            obj = focus_manager.get_manager().get_locus_of_focus()

        if not obj or self.in_document_content(obj):
            return False

        if not (AXUtilities.is_entry(obj) or AXUtilities.is_push_button(obj)):
            return False

        toolbar = AXObject.find_ancestor(obj, AXUtilities.is_tool_bar)
        result = self._is_find_container(toolbar)
        if result:
            tokens = ["GECKO:", obj, "believed to be find-in-page widget (toolbar)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if self._is_quick_find(toolbar):
            tokens = ["GECKO:", obj, "believed to be find-in-page widget (quick find)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def get_find_results_count(self, root: Atspi.Accessible | None = None) -> str:
        """Returns a string description of the number of find-in-page results in root."""

        root = root or self._find_container
        if not root:
            return ""

        def is_match(x: Atspi.Accessible) -> bool:
            return len(re.findall(r"\d+", AXObject.get_name(x))) == 2

        labels = AXUtilities.find_all_labels(root, is_match)
        if len(labels) != 1:
            return ""

        label = labels[0]
        AXObject.clear_cache(label, False, "Ensuring we have correct name for find results.")
        return AXObject.get_name(label)

    def unrelated_labels(
        self,
        root: Atspi.Accessible | None = None,
        only_showing: bool = True,
        minimum_words: int = 3
    ) -> list[Atspi.Accessible]:
        """Returns a list of labels in root that lack a relationship."""

        return super().unrelated_labels(root, only_showing, minimum_words=1)
