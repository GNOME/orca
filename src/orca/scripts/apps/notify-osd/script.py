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
import orca.settings as settings
import orca.settings_manager as settings_manager
import orca.notification_messages as notification_messages

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# The notify-osd script class.                                         #
#                                                                      #
########################################################################

class Script(default.Script):
    def onValueChanged(self, event):
        try:
            ivalue = event.source.queryValue()
            value = int(ivalue.currentValue)
        except NotImplementedError:
            value = -1

        if value >= 0:
            string = str(value)
            voice = self.speechGenerator.voice(obj=event.source, string=string)
            self.speakMessage(string, voice=voice)
            self.displayBrailleMessage(string,
                                       flashTime=settings.brailleFlashTime)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        try:
            ivalue = event.source.queryValue()
            value = ivalue.currentValue
        except NotImplementedError:
            value = -1
            
        utterances = []
        message = ""
        voices = _settingsManager.getSetting('voices')
        if value < 0:
            self.speakMessage(messages.NOTIFICATION)
            message = '%s %s' % (event.source.name, event.source.description)
        else:
            # A gauge notification, e.g. the Ubuntu volume notification that
            # appears when you press the multimedia keys.
            #
            message = '%s %d' % (event.source.name, value)
            self.speakMessage(message)

        voice = self.speechGenerator.voice(obj=event.source, string=message)
        self.speakMessage(message, voice=voice)
        self.displayBrailleMessage(message, flashTime=settings.brailleFlashTime)
        notification_messages.saveMessage(message)
