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
import orca.speechgenerator as speechgenerator
import orca.util as util

from orca.orca_i18n import _ # for gettext support

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """ Overrides _getSpeechForTableCell so that, we can properly handle
    the table cells on the User Privileges pane (which contains two more
    table cells).
    """

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech for a table cell. If this isn't inside a
        spread sheet, just return the utterances returned by the default
        table cell speech handler.

        Arguments:
        - obj: the table cell
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        speechGen = speechgenerator.SpeechGenerator 

        # Check to see if the table cell has any children. If it does,
        # then call _getSpeechForTableCell() for each of them. Otherwise
        # just call the default method to handle the table cell.
        #
        if obj and obj.childCount:
            for i in range(0, obj.childCount):
                child = obj.child(i)
                utterances.extend(self._getSpeechForTableCell(child, 
                                                         already_focused))
        else:
            utterances = speechGen._getSpeechForTableCell(self, \
                           util.getRealActiveDescendant(obj), already_focused)

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

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return SpeechGenerator(self)
