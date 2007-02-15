# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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

""" Custom script for Gnome Power Manager.
"""

__id__        = ""
__version__   = ""
__date__      = ""
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.orca as orca
import orca.default as default
import orca.debug as debug
import orca.speech as speech
import orca.util as util

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

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST
        self._lastSpeech = ""
        self._debug("__init__")

        default.Script.__init__(self, app)
        

    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "gnome-power-manager.py: "+msg)


    def onBoundsChanged(self, event):
        """Called whenever an object's bounds change. This happens
        when the Gnome Power Manager balloon is displayed on the
        desktop.

        Arguments:
        - event: the Event
        """
        self._debug("onBoundsChanged")
        obj = event.source
        self._debug("'%s' src='%s'" % (event.type, obj.role))
        
        self._searchChildrenForDisplayedText(obj, "")


    def _searchChildrenForDisplayedText(self, parent, indent):
        """
        Recursively descends the Gnome Power Manage and
        speaks the displayed text it finds.
        """

        self._debug("_searchChildrenForDisplayedText")

        text = self._getObjText(parent)

        self._debug("%s role='%s', text='%s'" % \
                    (indent, parent.role, text))

        if text and len(text) > 0:
            if text != self._lastSpeech:
                self._lastSpeech = text
                speech.speak(text, None, True)
        
        for i in range(0, parent.childCount):
            self._searchChildrenForDisplayedText(parent.child(i), indent+"  ")


    def _getObjText(self, obj):
        """
        Returns the text for an object.
        """
        retval = ""
        text = util.getDisplayedText(obj)
        if not text:
            text = obj.description
            
        if text and text != "None":
            retval = text
            
        self._debug("_getObjText: text='%s', desc='%s', label='%s'" % \
                    (util.getDisplayedText(obj), obj.description,
                     util.getDisplayedLabel(obj)))
        return retval

    
