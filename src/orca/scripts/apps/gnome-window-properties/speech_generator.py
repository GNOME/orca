# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""Custom script for gnome-window-properties."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.speechgenerator as speechgenerator

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForFrame so as to avoid digging into the
    gedit hierarchy and tickling a bug in gedit.
    """
    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForAlert(self, obj, already_focused):
        """Gets the title of the dialog.  Do NOT get the contents
        of labels inside the dialog that are not associated with any
        other objects.

        Arguments:
        - obj: the Accessible dialog
        - already_focused: False if object just received focus

        Returns a list of utterances be spoken.
        """

        utterances = []
        utterances.extend(self._getSpeechForObjectLabel(obj))
        utterances.extend(self._getSpeechForObjectName(obj))
        utterances.extend(self.getSpeechForObjectRole(obj))

        self._debugGenerator("gnome-window-properties._getSpeechForAlert",
                             obj,
                             already_focused,
                             utterances)

        return utterances
