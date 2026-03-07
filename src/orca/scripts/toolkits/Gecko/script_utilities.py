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

"""Custom script utilities for Gecko"""

from __future__ import annotations

from typing import TYPE_CHECKING

from orca import debug
from orca.ax_utilities import AXUtilities
from orca.scripts import web

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
