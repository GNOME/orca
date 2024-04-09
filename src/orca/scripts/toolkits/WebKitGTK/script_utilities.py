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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

from orca import focus_manager
from orca.scripts import web
from orca.ax_object import AXObject

class Utilities(web.Utilities):

    def isWebKitGTK(self, obj):
        """Returns True if this object is a WebKitGTK object."""

        if not obj:
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get('toolkit', '') in ['WebKitGtk', 'WebKitGTK']

    def _attemptBrokenTextRecovery(self, obj, **args):
        """Returns True if we should sanity-check text at offset and try to recover."""

        # TODO - JD: Remove this once we've verified the text implementation is correct.
        return True

    def inDocumentContent(self, obj=None):
        """Returns True if obj is in document content."""
        obj = obj or focus_manager.get_manager().get_locus_of_focus()

        rv = self._inDocumentContent.get(hash(obj))
        if rv is not None:
            return rv

        rv = self.isWebKitGTK(obj)
        self._inDocumentContent[hash(obj)] = rv
        return rv
