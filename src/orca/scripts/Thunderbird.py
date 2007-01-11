# Orca
#
# Copyright 2004-2006 Sun Microsystems Inc.
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

""" Custom script for Thunderbird 3.
"""

__id__        = "$Id: gaim.py 1584 2006-10-19 18:16:54Z richb $"
__version__   = "$Revision: 1584 $"
__date__      = "$Date: 2006-10-19 11:16:54 -0700 (Thu, 19 Oct 2006) $"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.atspi as atspi
import orca.braille as braille
import orca.debug as debug
import orca.default as default
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.rolenames as rolenames
import orca.settings as settings
import orca.speech as speech
import orca.util as util
import orca.Gecko as Gecko

from orca.orca_i18n import _


########################################################################
#                                                                      #
# The Thunderbird script class.                                               #
#                                                                      #
########################################################################

class Script(Gecko.Script):

    def __init__(self, app):
        """ Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        Gecko.Script.__init__(self, app)


    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "Thunderbird.py: "+msg)


    def onFocus(self, event):
        """ Called whenever an object gets focus.

        Arguments:
        - event: the Event
        
        """
        obj = event.source
        top = util.getTopLevel(obj)

        # Handle preferences that contain editable text fields. If
        # the object with keyboard focus is editable text field,
        # examine the previous and next sibling to get the order
        # for speaking the preference objects,
        if top.name == _("Thunderbird Preferences"):
            if obj.role == rolenames.ROLE_ENTRY and obj.text:

                if obj.index > 0:
                    prev = obj.parent.child(obj.index - 1)

                if obj.parent.childCount > obj.index:
                    next = obj.parent.child(obj.index + 1)

                [word, startOffset, endOffset] = obj.text.getTextAtOffset(0,
                    atspi.Accessibility.TEXT_BOUNDARY_WORD_START)

                if len(word) > 0:
                    if prev and prev.role == rolenames.ROLE_LABEL:
                        if next and next.role == rolenames.ROLE_LABEL:
                            text = _("%s text %s %s") % (obj.name, word, next.name)
                        else:
                            text = _("%s text %s") % (obj.name, word)
                    else:
                        text = _("text %s %s") % (word, obj.name)
                    
                    speech.speakUtterances([text])
                    return

        Gecko.Script.onFocus(self, event)
