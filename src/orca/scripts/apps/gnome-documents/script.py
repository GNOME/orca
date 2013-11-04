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

import pyatspi

import orca.scripts.default as default
import orca.orca_state as orca_state
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def onNameChanged(self, event):
        """Callback for accessible name change events."""

        try:
            eventRole = event.source.getRole()
            focusRole = orca_state.locusOfFocus.getRole()
        except:
            return

        # Present page changes in the previewer.
        if eventRole == pyatspi.ROLE_LABEL \
           and focusRole == pyatspi.ROLE_DOCUMENT_FRAME:
            self.presentMessage(event.any_data)

            # HACK: Reposition the caret offset from the last character to the
            # first so that SayAll will say all.
            try:
                text = orca_state.locusOfFocus.queryText()
            except NotImplementedError:
                pass
            else:
                text.setCaretOffset(0)
            return self.sayAll(None)

        default.Script.onNameChanged(self, event)

    def skipObjectEvent(self, event):
        # NOTE: This is here temporarily as part of the preparation for the
        # deprecation/removal of accessible "focus:" events. Once the change
        # has been completed, this method should be removed from this script.
        if event.type == "focus:":
            return True

        if event.type == "object:state-changed:focused":
            return False

        return default.Script.skipObjectEvent(self, event)
