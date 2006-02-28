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
import orca.atspi as atspi
import orca.default as default
import orca.rolenames as rolenames
import orca.orca as orca
import orca.braille as braille
import orca.speech as speech
import orca.keybindings as keybindings
import orca.util as util

########################################################################
#                                                                      #
# The StarOffice script class.                                         #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)


    def walkComponentHierarchy(self, obj):
        """Debug routine to print out the hierarchy of components for the
           given object.

        Arguments:
        - obj: the component to start from
        """

        print "<<<<---- Component Hierachy ---->>>>"
        print "START: Obj:", obj.name, obj.role
        parent = obj
        while parent:
            if parent != obj:
                if not parent.parent:
                    print "TOP: Parent:", parent.name, parent.role
                else:
                    print "Parent:", parent.name, parent.role
            parent = parent.parent
        print "<<<<============================>>>>"


    # This method tries to detect and handle the following cases:
    # 1) Writer: text paragraph.

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

        # self.walkComponentHierarchy(event.source)

        # 1) Writer: text paragraph.
        #
        # When the focus is on a paragraph in the Document view of the Writer,
        # then just speak/braille the current line (rather than speaking a
        # bogus initial "paragraph" utterance as well).

        rolesList = [rolenames.ROLE_PARAGRAPH, \
                     rolenames.ROLE_UNKNOWN, \
                     rolenames.ROLE_SCROLL_PANE, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_ROOT_PANE, \
                     rolenames.ROLE_FRAME]
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "StarOffice.onFocus - Writer: text paragraph.")

            result = atspi.getTextLineAtCaret(event.source)
            speech.speak(result[0])

            brailleRegions = []
            [cellRegions, focusedRegion] = \
                brailleGen.getBrailleRegions(event.source)
            brailleRegions.extend(cellRegions)
            braille.displayRegions(brailleRegions)

            orca.setLocusOfFocus(event, event.source, False)
            return

        # For everything else, pass the focus event onto the parent class
        # to be handled in the default way.

        default.Script.onFocus(self, event)

