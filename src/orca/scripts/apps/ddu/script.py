# Orca
#
# Copyright 2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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

"""Custom script for the Device Driver Utility."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import pyatspi

import orca.scripts.default as default
import orca.orca_state as orca_state
import orca.speech as speech

from .script_utilities import Utilities

########################################################################
#                                                                      #
# The DDU script class.                                                #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)
        self._progressBarShowing = False
        self._resultsLabel = None

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def _presentResults(self):
        """Presents the results found by the DDU. If we present the results
        also resets self._resultsLabel so that we don't present it twice.

        Returns True if the results were presented; False otherwise.
        """

        if self._resultsLabel:
            text = self.utilities.displayedText(self._resultsLabel)
            if text:
                # TODO - JD: Might be a good candidate for a flash
                # braille message.
                #
                speech.speak(text)
                self._resultsLabel = None
                return True

        return False

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in onActiveDescendantChanged.

        Arguments:
        - event: the Event

        Returns True if speech should be stopped; False otherwise.
        """

        # Intentionally doing an equality check for performance
        # purposes.
        #
        if event.any_data == orca_state.locusOfFocus:
            return False

        return True

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        if event.type.startswith("object:state-changed:showing") \
           and event.detail1 == 1 and self._progressBarShowing \
           and event.source.getRole() == pyatspi.ROLE_FILLER:
            self._progressBarShowing = False
            labels = self.utilities.descendantsWithRole(
                event.source, pyatspi.ROLE_LABEL)
            if len(labels) == 1:
                # Most of the time, the label has its text by the time
                # the progress bar disappears. On occasion, we have to
                # wait for a text inserted event. So we'll store the
                # results label, try to present it now, and be ready
                # to present it later.
                #
                self._resultsLabel = labels[0]
                self._presentResults()
                return

        default.Script.onStateChanged(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        if self.utilities.isSameObject(event.source, self._resultsLabel):
            if self._presentResults():
                return

        default.Script.onTextInserted(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.

        Arguments:
        - event: the Event
        """

        # When the progress bar appears, its events are initially emitted
        # by an object of ROLE_SPLIT_PANE. Looking for it is sufficient
        # hierarchy tickling to cause it to emit the expected events.
        #
        if event.source.getRole() == pyatspi.ROLE_SPLIT_PANE:
            if self.utilities.descendantsWithRole(
                  event.source.parent, pyatspi.ROLE_PROGRESS_BAR):
                self._progressBarShowing = True

        default.Script.onValueChanged(self, event)
