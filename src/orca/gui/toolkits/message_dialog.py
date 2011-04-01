# Orca
#
# Copyright 2011 The Orca Team.
# Author: Joanmarie Diggs <joanmarie.diggs@gmail.com>
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

from abstract_widget import AbstractWidget

class MessageDialog(AbstractWidget):

    SIGNAL_CLOSE = None
    SIGNAL_RESPONSE = None

    MESSAGE_INFO = None
    MESSAGE_WARNING = None
    MESSAGE_QUESTION = None
    MESSAGE_ERROR = None

    BUTTON_OK     = None
    BUTTON_CLOSE  = None
    BUTTON_CANCEL = None
    BUTTON_YES    = None
    BUTTON_NO     = None

    RESPONSE_OK     = None
    RESPONSE_CLOSE  = None
    RESPONSE_CANCEL = None
    RESPONSE_YES    = None
    RESPONSE_NO     = None

    def __init__(self):
        super(MessageDialog, self).__init__()
        self.setDefaultSize(400, 100)

    def _getHandlerForSignal(self, signal):
        if signal == self.SIGNAL_CLOSE:
            return self.onClose
        if signal == self.SIGNAL_RESPONSE:
            return self.onResponse

        return None

    def bind(self, signal, function, *args, **kwargs):
        pass

    def onClose(self, widget, function, *args, **kwargs):
        pass

    def onResponse(self, widget, responseID, function, *args, **kwargs):
        pass

    def setDefaultSize(self, width, height):
        pass

    def setSize(self, width, height):
        pass

    def setType(self, messageType):
        pass

    def setMainText(self, text):
        pass

    def setSecondaryText(self, text):
        pass

    def addButton(self, button):
        pass

    def display(self):
        pass

    def hide(self):
        pass

    def destroy(self):
        pass
