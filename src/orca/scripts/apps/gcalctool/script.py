# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

"""Provides a custom script for gcalctool."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from orca import messages
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts.toolkits import gtk

class Script(gtk.Script):
    """The gcalctool script."""

    def __init__(self, app):
        super().__init__(app)
        self._results_display = None
        self._status_line = None

    def onWindowActivated(self, event):
        """Callback for window:active accessibility events."""

        if self._results_display and self._status_line:
            super().onWindowActivated(event)
            return

        if not AXUtilities.is_frame(event.source):
            super().onWindowActivated(event)
            return

        self._results_display = AXObject.find_descendant(event.source, AXUtilities.is_editbar)
        if not self._results_display:
            self.presentMessage(messages.CALCULATOR_DISPLAY_NOT_FOUND)

        def is_status_line(x):
            return AXUtilities.is_text(x) and not AXUtilities.is_editable(x)

        self._status_line = AXObject.find_descendant(event.source, is_status_line)
        super().onWindowActivated(event)

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if self.utilities.isSameObject(event.source, self._status_line):
            self.presentMessage(self.utilities.displayedText(self._status_line))
            return

        super().onTextInserted(event)
