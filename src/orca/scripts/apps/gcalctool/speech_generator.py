# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Provides a custom script for gcalctool."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.speechgenerator as speechgenerator
import pyatspi

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForPushButton to handle 'unspeakable'
    button labels displayed on the screen.
    """
    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForObjectName(self, obj):
        """Gives preference to the object name versus what is being
        displayed on the screen.  This helps accomodate the naming
        hints being given to us by gcalctool for it's mathematical
        operator buttons."""

        if obj.getRole() != pyatspi.ROLE_PUSH_BUTTON:
            return speechgenerator.SpeechGenerator._getSpeechForObjectName(\
                self, obj)

        if obj.name:
            name = obj.name
        else:
            name = self._script.getDisplayedText(obj)

        if name:
            return [name]
        elif obj.description:
            return [obj.description]
        else:
            return []
