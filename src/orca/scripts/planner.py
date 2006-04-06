# Orca
#
# Copyright 2005 Sun Microsystems Inc.
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

import orca.debug as debug
import orca.default as default
import orca.atspi as atspi
import orca.rolenames as rolenames
import orca.orca as orca
import orca.braille as braille
import orca.speech as speech
import orca.settings as settings
import orca.util as util

from orca.orca_i18n import _ # for gettext support

########################################################################
#                                                                      #
# The planner script class.                                            #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)


    # This method tries to detect and handle the following cases:
    # 1) Main window: one of the four graphic toggle buttons.

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        debug.printObjectEvent(debug.LEVEL_FINEST,
                               event,
                               event.source.toString())

        # atspi.printAncestry(event.source)

        # 1) Main window: one of the four graphic toggle buttons.
        #
        # If the focus is on one of the four graphic toggle buttons on
        # the left side of the main window, then get the label associated
        # with it, and speak it. Then fall through to provide the default
        # action for this focus event.

        rolesList = [rolenames.ROLE_TOGGLE_BUTTON, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_PANEL]
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "planner.onFocus - main window: " \
                      + "one of the four graphic toggle buttons.")

            filler = event.source.parent
            allLabels = atspi.findByRole(filler, rolenames.ROLE_LABEL)
            speech.speak(allLabels[0].name)


        # For everything else, pass the focus event onto the parent class 
        # to be handled in the default way.

        default.Script.onFocus(self, event)
