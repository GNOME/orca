# Orca
#
# Copyright 2008 Sun Microsystems Inc.
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

"""Custom script for gnome-screensaver-dialog."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.scripts.toolkits.gtk as gtk
import orca.speech as speech

class Script(gtk.Script):

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        obj = event.source

        # If we are focused in a password text area, we need to check if
        # there are any useful messages displayed in a couple of labels that
        # are visually below that password area. If there are, then speak
        # them for the user. See bug #529655 for more details.
        #
        if obj.getRole() == pyatspi.ROLE_PASSWORD_TEXT:
            obj = obj.parent.parent.parent
            for child in obj:
                if child.getRole() == pyatspi.ROLE_LABEL and child.name:
                    speech.speak(child.name)
                return

        gtk.Script.onFocusedChanged(self, event)
