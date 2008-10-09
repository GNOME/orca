# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

"""Custom script for rhythmbox."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import orca.speechgenerator as speechgenerator

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

    def _getDefaultSpeech(self, obj, already_focused, role=None):
        """Gets a list of utterances to be spoken for the current
        object's name, role, and any accelerators.  This is usually the
        fallback speech generator should no other specialized speech
        generator exist for this object.

        The default speech will be of the following form:

        label name role availability

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus
        - role: A role that should be used instead of the Accessible's 
          possible role.

        Returns a list of utterances to be spoken for the object.
        """

        # When the rating widget changes values, it emits an accessible
        # name changed event. Because it is of ROLE_UNKNOWN, the default
        # speechgenerator's _getDefaultSpeech handles it. And because
        # the widget is already focused, it doesn't speak anything. We
        # want to speak the widget's name as it contains the number of
        # stars being displayed.
        #
        if obj.getRole() == pyatspi.ROLE_UNKNOWN and already_focused:
            utterances = self._getSpeechForObjectName(obj)
            self._debugGenerator("rhythmbox _getDefaultSpeech",
                                 obj,
                                 already_focused,
                                 utterances)
            return utterances

        return speechgenerator.SpeechGenerator.\
                        _getDefaultSpeech(self, obj, already_focused, role)
