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
import orca.speech as speech
import orca.notification_messages as notification_messages

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
            speech.speak(str(value), None, True)
            self.displayBrailleMessage("%s" % value,
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
        if value < 0:
            utterances.append(messages.NOTIFICATION)
            utterances.append(self.voices.get(settings.SYSTEM_VOICE))
            message = '%s %s' % (event.source.name, event.source.description)
            utterances.append(message)
            utterances.append(self.voices.get(settings.DEFAULT_VOICE))
        else:
            # A gauge notification, e.g. the Ubuntu volume notification that
            # appears when you press the multimedia keys.
            #
            message = '%s %d' % (event.source.name, value)
            utterances.append(message)
            utterances.append(self.voices.get(settings.SYSTEM_VOICE))

        speech.speak(utterances, None, True)
        self.displayBrailleMessage(message, flashTime=settings.brailleFlashTime)
        notification_messages.saveMessage(message)
