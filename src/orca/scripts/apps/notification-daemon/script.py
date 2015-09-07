# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

""" Custom script for The notification daemon."""

__id__        = ""
__version__   = ""
__date__      = ""
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.messages as messages
import orca.scripts.default as default
import orca.settings as settings
import orca.speech as speech
import orca.notification_messages as notification_messages

########################################################################
#                                                                      #
# The notification-daemon script class.                                #
#                                                                      #
########################################################################

class Script(default.Script):

    def onWindowCreated(self, event):
        """Callback for window:create accessibility events."""

        hasRole = lambda x: x and x.getRole() == pyatspi.ROLE_LABEL
        allLabels = pyatspi.findAllDescendants(event.source, hasRole)
        texts = [self.utilities.displayedText(acc) for acc in allLabels]
        text = '%s %s' % (messages.NOTIFICATION, ' '.join(texts))
        speech.speak(text, None, True)
        self.displayBrailleMessage(text, flashTime=settings.brailleFlashTime)
        notification_messages.saveMessage(text)
