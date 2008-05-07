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

""" Custom script for The notification daemon.
"""

__id__        = ""
__version__   = ""
__date__      = ""
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.default as default
import orca.speech as speech
import pyatspi

from orca.orca_i18n import _

########################################################################
#                                                                      #
# The notification-daemon script class.                                #
#                                                                      #
########################################################################

class Script(default.Script):
    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["window:create"] = \
            self.onWindowCreate

        return listeners

    def onWindowCreate(self, event):
        """Called whenever a window is created in the notification-daemon
        application.

        Arguments:
        - event: the Event.
        """
        a = self.findByRole(event.source, pyatspi.ROLE_LABEL)
        print a
        texts = [self.getDisplayedText(acc) for acc in a]
        # Translators: This denotes a notification to the user of some sort.
        #
        text = _('Notification %s') % ' '.join(texts)
        speech.speak(text, None, True)

