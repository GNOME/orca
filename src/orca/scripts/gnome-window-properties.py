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

"""Custom script for gnome-window-properties."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.default as default
import orca.speechgenerator as speechgenerator

########################################################################
#                                                                      #
# The gnome-window-properties script class.                            #
#                                                                      #
########################################################################

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
        utterances.extend(self._getSpeechForObjectRole(obj))

        self._debugGenerator("gnome-window-properties._getSpeechForAlert",
                             obj,
                             already_focused,
                             utterances)

        return utterances

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
