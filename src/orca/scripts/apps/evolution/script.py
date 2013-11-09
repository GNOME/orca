# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2013 Igalia, S.L.
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

"""Custom script for Evolution."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2013 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

import orca.scripts.default as default
import orca.scripts.toolkits.WebKitGtk as WebKitGtk
import orca.settings as settings
import orca.settings_manager as settings_manager

from .formatting import Formatting
from .speech_generator import SpeechGenerator

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# The Evolution script class.                                          #
#                                                                      #
########################################################################

class Script(WebKitGtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        WebKitGtk.Script.__init__(self, app)
        self.presentIfInactive = False

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return SpeechGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def isActivatableEvent(self, event):
        """Returns True if the given event is one that should cause this
        script to become the active script.  This is only a hint to
        the focus tracking manager and it is not guaranteed this
        request will be honored.  Note that by the time the focus
        tracking manager calls this method, it thinks the script
        should become active.  This is an opportunity for the script
        to say it shouldn't.
        """

        window = self.utilities.topLevelObject(event.source)
        if window and not window.getState().contains(pyatspi.STATE_ACTIVE):
            return False

        return True

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in onActiveDescendantChanged.

        Arguments:
        - event: the Event

        Returns True if speech should be stopped; False otherwise.
        """

        return False

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        # Every time the selected mail folder changes, Evolution's frame is
        # updated to display the newly-selected folder. We need to ignore
        # this event so as not to double-present the selected folder.
        if event.source.getRole() == pyatspi.ROLE_FRAME:
            return

        default.Script.onNameChanged(self, event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""
 
        if not event.detail1:
            default.Script.onShowingChanged(self, event)
            return

        obj = event.source

        # Present text in the Account Assistant
        try:
            role = obj.getRole()
            relationSet = obj.getRelationSet()
        except:
            return

        if role != pyatspi.ROLE_LABEL or relationSet:
            default.Script.onShowingChanged(self, event)
            return

        window = self.utilities.topLevelObject(obj)
        focusedObj = self.utilities.focusedObject(window)
        if self.utilities.spatialComparison(obj, focusedObj) >= 0:
            return
 
        # TODO - JD: The very last screen results in a crazy-huge number
        # of events, and they come in an order that is not good for this
        # approach. So we'll need to handle this particular case elsewhere.
        if focusedObj.getRole() == pyatspi.ROLE_CHECK_BOX:
            labels = self.utilities.unrelatedLabels(window)
            if len(labels) > 15:
                return

        voice = self.voices.get(settings.DEFAULT_VOICE)
        text = self.utilities.displayedText(obj)
        self.presentMessage(text, voice=voice)
