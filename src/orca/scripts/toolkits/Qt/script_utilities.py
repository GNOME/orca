# Orca
#
# Copyright (C) 2023 Igalia, S.L.
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

"""Custom script utilities for Qt"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import debug
from orca import script_utilities
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Utilities(script_utilities.Utilities):
    """Custom script utilities for Qt"""

    def _is_top_level_object(self, obj: Atspi.Accessible) -> bool:
        # This is needed because Qt apps might insert some junk (e.g. a filler) in
        # between the window/frame/dialog and the application.
        return AXUtilities.is_application(AXObject.get_parent(obj))

    def top_level_object(
        self,
        obj: Atspi.Accessible,
        use_fallback_search: bool = False
    ) -> Atspi.Accessible | None:
        """Returns the top level object for obj."""

        # The fallback search is needed because sometimes we can ascend the accessibility
        # tree all the way to the top; other times, we cannot get the parent, but can still
        # get the children. The fallback search handles the latter scenario.
        result = super().top_level_object(obj, use_fallback_search=True)
        if result is not None and AXObject.get_role(result) not in self._top_level_roles():
            tokens = ["QT: Top level object", result, "lacks expected role."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

    def frame_and_dialog(
        self,
        obj: Atspi.Accessible | None = None
    ) -> list[Atspi.Accessible | None]:
        """Returns the frame and (possibly) the dialog containing obj."""

        frame, dialog = super().frame_and_dialog(obj)
        if frame or dialog:
            return [frame, dialog]

        # https://bugreports.qt.io/browse/QTBUG-129656
        tokens = ["QT: Could not find frame or dialog for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        top_level = self.top_level_object(obj, True)

        tokens = ["QT: Returning", top_level, "as frame for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return [top_level, None]

    def has_meaningful_toggle_action(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj has a meaningful toggle action."""

        # https://bugreports.qt.io/browse/QTBUG-116204
        if AXUtilities.is_table_cell_or_header(obj):
            tokens = ["QT: Ignoring toggle action on", obj, "."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        return super().has_meaningful_toggle_action(obj)
