# Orca
#
# Copyright 2009 Eitan Isaacson
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

""" Custom script for The notify-osd"""

__id__        = ""
__version__   = ""
__date__      = ""
__copyright__ = "Copyright (c) 2009 Eitan Isaacson"
__license__   = "LGPL"

import orca.messages as messages
import orca.scripts.default as default
from orca.ax_object import AXObject
from orca.ax_value import AXValue


########################################################################
#                                                                      #
# The notify-osd script class.                                         #
#                                                                      #
########################################################################

class Script(default.Script):
    def onValueChanged(self, event):
        if not AXValue.did_value_change(event.source):
            return

        # TODO - JD: See if this can be merged into the default script.
        value = AXValue.get_current_value(event.source)
        string = str(value)
        voice = self.speechGenerator.voice(obj=event.source, string=string)
        self.presentMessage(string, voice=voice)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        message = ""
        if not AXObject.supports_value(event.source):
            self.speakMessage(messages.NOTIFICATION)
            message = f"{AXObject.get_name(event.source)} {AXObject.get_description(event.source)}"
        else:
            # A gauge notification, e.g. the Ubuntu volume notification that
            # appears when you press the multimedia keys.
            message = f"{AXObject.get_name(event.source)} {AXValue.get_current_value(event.source)}"

        voice = self.speechGenerator.voice(obj=event.source, string=message)
        self.presentMessage(message, voice=voice)
        self.notificationPresenter.save_notification(message)
