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

"""Custom script for liferea."""

import orca.debug as debug
import orca.default as default
import orca.braille as braille
import orca.orca_state as orca_state
import orca.speech as speech
import orca.eventsynthesizer as eventsynthesizer
import pyatspi

from orca.orca_i18n import _ # for gettext support

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"


class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

    def onNameChanged(self, event):
        # Since we haven't feed back informationb when the 
        # "work online/offline" status changes, we speech/braille the 
        # statusbar content which is the the information that sets the 
        # work online or work offline mode.
        #
        if event.source.getRole() != pyatspi.ROLE_STATUS_BAR:
            default.Script.onNameChanged(self, event)
            return

        rolesList = [pyatspi.ROLE_PUSH_BUTTON,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_FRAME]

        # We only speak the statusbar's changes when the application is 
        # with the focus and is the "work online/offline button is focused.
        #
        if self.isDesiredFocusedItem(orca_state.locusOfFocus, rolesList):
            speech.stop()
            speech.speak(event.source.name)
            braille.displayMessage(event.source.name)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

        # Here we handle the case when focus is in the "Work online/offline" 
        # button near the status bar that has an image without a description.
        # We speak and braille "Online/Offline button" here, until the 
        # developer of the application adds a description to the images 
        # associated with the button, which shows the online or offline 
        # work mode.
        #
        rolesList = [pyatspi.ROLE_PUSH_BUTTON,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_FRAME]

        # We are checking if the button with the focus is the button to 
        # turn on/off the work mode in liferea. This push button is
        # hierarchically located in the main window of the application 
        # (frame), inside a filler and inside another filler.
        #
        if self.isDesiredFocusedItem(event.source, rolesList):
            # If we are focusing this button we construct a utterance and 
            # a braille region to speak/braille "online/offline button".
            # Here we declare utterances and add the localized string 
            # "online/offline".
            #
            utterances = []
            utterances.append(_("Work online / offline")) 

            # Here we extend the utterances with the speech generator for 
            # the object with focus (the push button).
            #
            utterances.extend(speechGen.generateSpeech(event.source))

            # Finally we speak/braille the utterances/regions.
            #
            speech.speak(utterances)
           
            regions = brailleGen.generateBraille(event.source)
            regions[0].insert(0, braille.Region(utterances[0] + " "))
            braille.displayRegions(regions)
           
            return

        # Here we handle the case when the focus is in the headlines table.
        # See comment #3 of bug #350233.
        # http://bugzilla.gnome.org/show_bug.cgi?id=350233
        #
        if orca_state.locusOfFocus.getRole() == \
                                        pyatspi.ROLE_TABLE_COLUMN_HEADER:
            table = event.source.parent
            cells = self.findByRole(table, pyatspi.ROLE_TABLE_CELL)
            eventsynthesizer.clickObject(cells[1], 1)

        default.Script.locusOfFocusChanged(self, event, 
                                           oldLocusOfFocus, newLocusOfFocus)
