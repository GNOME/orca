# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

"""Custom script for gedit.  [[[TODO: WDW - HACK because tickling gedit
when it is starting can cause gedit to issue the following message:

     (gedit:31434): GLib-GObject-WARNING **: invalid cast from `SpiAccessible' to `BonoboControlAccessible'

It seems as though whenever this message is issued, gedit will hang when
you try to exit it.  Debugging has shown that the iconfied state in
particular seems to indicate that an object is telling all assistive
technologies to just leave it alone or it will pull the trigger on the
application.]]]
"""

import orca.a11y as a11y
import orca.braille as braille
import orca.default as default
import orca.rolenames as rolenames
import orca.speech as speech
import orca.speechgenerator as speechgenerator

from orca.orca_i18n import _
from orca.rolenames import getRoleName

########################################################################
#                                                                      #
# The GEdit script class.                                              #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForFrame so as to avoid digging into the
    gedit hierarchy and tickling a bug in gedit.
    """

    def _getSpeechForFrame(self, obj, already_focused):
        """Get the speech for a frame.  [[[TODO: WDW - This avoids
        digging into the component hierarchy so as to avoid tickling
        a bug in GEdit (see module comment above).]]]

        Arguments:
        - obj: the frame
        - already_focused: if False, the obj just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        # This will dig deep into the hierarchy, causing issues with
        # gedit.  So, we won't do this.
        #
        #utterances = self._getSpeechForAlert(obj, already_focused)

        self._debugGenerator("GEditSpeechGenerator._getSpeechForFrame",
                             obj,
                             already_focused,
                             utterances)

        return utterances

class Script(default.Script):

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator()
