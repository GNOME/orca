# Orca
#
# Copyright 2007 Sun Microsystems Inc.
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

""" Custom script for Gnome System Monitor.
"""

__id__        = ""
__version__   = ""
__date__      = ""
__copyright__ = "Copyright (c) 2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.braille as braille
import orca.default as default
import orca.debug as debug
import orca.rolenames as rolenames
import orca.speech as speech

from orca.orca_i18n import _

########################################################################
#                                                                      #
# The gnome-power-manager script class.                                #
#                                                                      #
########################################################################

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

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        # First pass the event onto the parent class to be handled in 
        # the default way.
        #
        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

        # Correctly handle the "System" tab (see Orca bug #433818).
        # If the locus of focus is on a page tab in the main GNOME
        # System Monitor window, then get a list of all the panels
        # on that page. For all of the panels that have a name, find
        # all the unrelated labels and speak them.
        #
        rolesList = [rolenames.ROLE_PAGE_TAB, \
                     rolenames.ROLE_PAGE_TAB_LIST, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FRAME]
        if self.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                  "GNOME System Monitor.locusOfFocusChanged - page tab.")
            line = braille.getShowingLine()
            utterances = []
            panels = self.findByRole(newLocusOfFocus, rolenames.ROLE_PANEL)
            for panel in panels:
                if panel.name and len(panel.name) > 0:
                    line.addRegion(braille.Region(" " + panel.name))
                    utterances.append(panel.name)
                    labels = self.findUnrelatedLabels(panel)
                    for label in labels:
                        line.addRegion(braille.Region(" " + label.name))
                        utterances.append(label.name)

            speech.speakUtterances(utterances)
            braille.refresh()
