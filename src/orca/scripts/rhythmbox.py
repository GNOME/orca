# Orca
#
# Copyright 2008 Sun Microsystems Inc.
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

"""Custom script for rhythmbox."""

__id__ = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.braillegenerator as braillegenerator
import orca.debug as debug
import orca.default as default
import orca.speechgenerator as speechgenerator

class BrailleGenerator(braillegenerator.BrailleGenerator):
    """Overrides _getBrailleRegionsForTableCell to correctly handle 
    the table cells in the Library table.
    """

    def __init__(self, script):
        braillegenerator.BrailleGenerator.__init__(self, script)

    def _getBrailleRegionsForTableCell(self, obj):
        """Get the braille for a single table cell

        Arguments:
        - obj: the table

        Returns a list where the first element is a list of Regions to 
        display and the second element is the Region which should get focus.
        """

        # Check to see if this is a table cell from the Library table.
        # If so, it'll have five children and we are interested in the
        # penultimate one. See bug #512639 for more details.
        #
        if obj.childCount == 5:
            obj = obj[3]

        return braillegenerator.BrailleGenerator.\
                    _getBrailleRegionsForTableCell(self, obj)


class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForTableCell to correctly handle the table
    cells in the Library table.
    """

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech utterances for a single table cell

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Check to see if this is a table cell from the Library table.
        # If so, it'll have five children and we are interested in the
        # penultimate one. See bug #512639 for more details.
        #
        if obj.childCount == 5:
            obj = obj[3]
        return speechgenerator.SpeechGenerator.\
                    _getSpeechForTableCell(self, obj, already_focused)

        return utterances

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """
        default.Script.__init__(self, app)

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """

        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)
