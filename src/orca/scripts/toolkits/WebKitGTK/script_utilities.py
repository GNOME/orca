# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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


"""Script utilities for WebKitGTK."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import focus_manager
from orca.ax_object import AXObject
from orca.scripts import web

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Utilities(web.Utilities):
    """Script utilities for WebKitGTK."""

    def is_webkit_gtk(self, obj: Atspi.Accessible | None) -> bool:
        """Returns True if this object is a WebKitGTK object."""

        if obj is None:
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get('toolkit', '') in ['WebKitGtk', 'WebKitGTK']

    def in_document_content(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns True if obj is in document content."""

        obj = obj or focus_manager.get_manager().get_locus_of_focus()

        rv = self._cached_in_document_content.get(hash(obj))
        if rv is not None:
            return rv

        rv = self.is_webkit_gtk(obj)
        self._cached_in_document_content[hash(obj)] = rv
        return rv
