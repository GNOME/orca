# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

""" Custom script for Thunderbird 3.
"""

__id__        = "$Id: $"
__version__   = "$Revision: $"
__date__      = "$Date: $"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.scripts.toolkits.Gecko as Gecko

from orca.orca_i18n import _

########################################################################
#                                                                      #
# Custom SpeechGenerator for Thunderbird                               #
#                                                                      #
########################################################################

class SpeechGenerator(Gecko.SpeechGenerator):
    """Provides a speech generator specific to Thunderbird.
    """

    def __init__(self, script):
        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        self._debug("__init__")
        Gecko.SpeechGenerator.__init__(self, script)

    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "Thunderbird.SpeechGenerator: "+msg)

    def _getSpeechForAlert(self, obj, already_focused):
        """Gets the title of the dialog and the contents of labels inside the
        dialog that are not associated with any other objects.

        Arguments:
        - obj: the Accessible dialog
        - already_focused: False if object just received focus

        Returns a list of utterances be spoken.
        """

        # If this is the spell checking dialog, then just return the title
        # of the dialog. See bug #535192 for more details.
        #
        rolesList = [pyatspi.ROLE_DIALOG, \
                     pyatspi.ROLE_APPLICATION]
        if self._script.isDesiredFocusedItem(obj, rolesList):
            # Translators: this is what the name of the spell checking
            # dialog in Thunderbird begins with. The translated form
            # has to match what Thunderbird is using.  We hate keying
            # off stuff like this, but we're forced to do so in this case.
            #
            if obj.name.startswith(_("Check Spelling")):
                utterances = []
                utterances.extend(self._getSpeechForObjectName(obj))

                self._debugGenerator("Thunderbird: _getSpeechForAlert",
                                     obj,
                                     already_focused,
                                     utterances)

                return utterances

        return Gecko.SpeechGenerator._getSpeechForAlert(self, obj,
                                                        already_focused)
