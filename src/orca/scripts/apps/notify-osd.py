# Orca
#
# Copyright 2009 Eitan Isaacson
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

""" Custom script for The notify-osd
"""

__id__        = ""
__version__   = ""
__date__      = ""
__copyright__ = "Copyright (c) 2009 Eitan Isaacson"
__license__   = "LGPL"

import orca.default as default
import orca.speech as speech
import pyatspi

from orca.orca_i18n import _

########################################################################
#                                                                      #
# The notify-osd script class.                                         #
#                                                                      #
########################################################################

class Script(default.Script):
    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["window:create"] = \
            self.onWindowCreate

        listeners["object:property-change:accessible-value"] = \
            self.onValueChange

        return listeners
    
    def onValueChange(self, event):
        try:
            ivalue = event.source.queryValue()
            value = int(ivalue.currentValue)
        except NotImplementedError:
            value = -1

        if value >= 0:
            speech.speak(str(value), None, True)
            

    def onWindowCreate(self, event):
        """Called whenever a window is created in the notify-osd
        application.

        Arguments:
        - event: the Event.
        """
        try:
            ivalue = event.source.queryValue()
            value = ivalue.currentValue
        except NotImplementedError:
            value = -1
            
        if value < 0:
            # Not a gauge notification.
            texts = [event.source.name, event.source.description]
            # Translators: This denotes a notification to the user of some sort.
            #
            text = _('Notification %s') % ' '.join(texts)
        else:
            text = '%s %d' % (event.source.name, value)
        
        speech.speak(text, None, True)

