# Orca
#
# Copyright 2013 The Orca Team.
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

"""Custom script for gnome-documents."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013 The Orca Team"
__license__   = "LGPL"

import orca.focus_manager as focus_manager
import orca.scripts.toolkits.gtk as gtk
from orca.ax_utilities import AXUtilities

from .speech_generator import SpeechGenerator
from .script_utilities import Utilities

_focusManager = focus_manager.getManager()

class Script(gtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        gtk.Script.__init__(self, app)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getUtilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def onNameChanged(self, event):
        """Callback for accessible name change events."""

        focus = _focusManager.get_locus_of_focus()

        # Present page changes in the previewer.
        if AXUtilities.is_label(event.source) and self.utilities.isDocument(focus):
            self.presentMessage(event.any_data)

            # HACK: Reposition the caret offset from the last character to the
            # first so that SayAll will say all.
            try:
                text = focus.queryText()
            except NotImplementedError:
                pass
            else:
                text.setCaretOffset(0)
            return self.sayAll(None)

        gtk.Script.onNameChanged(self, event)
