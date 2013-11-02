# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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

"""Custom script for rhythmbox."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."  \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import orca.scripts.default as default
from .formatting import Formatting

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """
        default.Script.__init__(self, app)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def skipObjectEvent(self, event):
        # NOTE: This is here temporarily as part of the preparation for the
        # deprecation/removal of accessible "focus:" events. Once the change
        # has been complete, this method should be removed from this script.
        if event.type == "focus:":
            return True

        if event.type == "object:state-changed:focused":
            return False

        return default.Script.skipObjectEvent(self, event)
