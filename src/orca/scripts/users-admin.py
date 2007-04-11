# Orca
#
# Copyright 2006 Sun Microsystems Inc.
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

"""Custom script for users-admin"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.default as default
import orca.braille as braille
import orca.braillegenerator as braillegenerator
import orca.speechgenerator as speechgenerator

from orca.orca_i18n import _ # for gettext support

class BrailleGenerator(braillegenerator.BrailleGenerator):
    """Overrides _getBrailleRegionsForTableCellRow to ignore the value of 
    settings.readTableCellRow and always get the braille for a single table 
    cell.
    Overrides _getBrailleRegionsForTableCell so that, we can properly 
    handle the table cells on the User Privileges pane (which contains two 
    more table cells).
    """

    def __init__(self, script):
        braillegenerator.BrailleGenerator.__init__(self, script)

    def _getBrailleRegionsForTableCellRow(self, obj):
        """Ignore the value of settings.readTableCellRow and always get 
        the braille for a single table cell.

        Arguments:
        - obj: the table

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        return self._getBrailleRegionsForTableCell(obj)

    def _getBrailleRegionsForTableCell(self, obj):
        """Get the braille for a table cell. Check to see if the table cell 
        has any children. If it does, then call 
        _getBrailleRegionsForTableCell() for each of them. If it doesn't, 
        then just return the utterances returned by the default table cell 
        braille handler.

        Arguments:
        - obj: the table cell

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        regions = []
        brailleGen = braillegenerator.BrailleGenerator

        if obj and obj.childCount:
            i = obj.childCount - 1
            while i >= 0:
                child = obj.child(i)
                [cellRegions, focusRegion] = \
                                self._getBrailleRegionsForTableCell(child)

                if len(regions):
                    regions.append(braille.Region(" "))
                else:
                    cellFocusedRegion = focusRegion
                regions.append(cellRegions[0])
                i -= 1
            regions = [regions, cellFocusedRegion]
        else:
            regions = brailleGen._getBrailleRegionsForTableCell(self, obj)

        return regions

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """ Overrides _getSpeechForTableCell so that, we can properly handle
    the table cells on the User Privileges pane (which contains two more
    table cells).
    """

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech for a table cell. Check to see if the table cell 
        has any children. If it does, then call _getSpeechForTableCell() 
        for each of them. If it doesn't, then just return the utterances 
        returned by the default table cell speech handler.

        Arguments:
        - obj: the table cell
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        speechGen = speechgenerator.SpeechGenerator 

        if obj and obj.childCount:
            i = obj.childCount - 1
            while i >= 0:
                child = obj.child(i)
                utterances.extend(self._getSpeechForTableCell(child, 
                                                         already_focused))
                i -= 1
        else:
            utterances = speechGen._getSpeechForTableCell(self, \
                self._script.getRealActiveDescendant(obj), already_focused)

        return utterances

########################################################################
#                                                                      #
# The users-admin script class.                                        #
#                                                                      #
########################################################################

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
