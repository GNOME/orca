# Orca
#
# Copyright 2010 Informal Informatica LTDA.
# Author: Jose Vilmar <vilmar@informal.com.br>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Custom script for Eclipse."""
__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Informal Informatica LTDA."
__license__   = "LGPL"

import orca.default as default
import orca.orca_state as orca_state

########################################################################
#                                                                      #
# The Eclipse script class.                                            #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application."""
        default.Script.__init__(self, app)

    def _presentTextAtNewCaretPosition(self, event, otherObj=None):
        """Updates braille, magnification, and outputs speech for the
        event.source or the otherObj. Overridden here so that we can
        speak the line when a breakpoint is reached."""

        # Let the default script's normal behavior do its thing
        #
        default.Script._presentTextAtNewCaretPosition(self, event, otherObj)
        debugKeys = ["F5", "F6", "F7", "F8", "F11"]
        #
        if orca_state.lastNonModifierKeyEvent \
           and orca_state.lastNonModifierKeyEvent.event_string in debugKeys:
            obj = otherObj or event.source
            self.sayLine(obj)

