# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""A script to do nothing.  This is for self-voicing apps."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.scripts.default as default

class Script(default.Script):
    """A script to do nothing.  This is for self-voicing apps."""
    
    def __init__(self, app):
        """Creates a script for the given application, if necessary.
        This method should not be called by anyone except the
        script manager.

        Arguments:
        - app: the Python Accessible application to create a script for
        """

        default.Script.__init__(self, app)

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """
        return None

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return None

    def processObjectEvent(self, event):
        """Does nothing.

        Arguments:
        - event: the Event
        """
        pass

    def processKeyboardEvent(self, keyboardEvent):
        """Does nothing.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns False to indicate the event was not consumed.
        """
        return False

    def processBrailleEvent(self, brailleEvent):
        """Does nothing.

        Arguments:
        - brailleEvent: an instance of input_event.BrailleEvent

        Returns False to indicate the event was not consumed.
        """
        return False
