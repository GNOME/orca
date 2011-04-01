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

__id__    = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

import gtk
from orca.gui.toolkits import message_dialog

class MessageDialog(message_dialog.MessageDialog):

    SIGNAL_CLOSE    = 'close'
    SIGNAL_RESPONSE = 'response'

    MESSAGE_INFO     = gtk.MESSAGE_INFO
    MESSAGE_WARNING  = gtk.MESSAGE_WARNING
    MESSAGE_QUESTION = gtk.MESSAGE_QUESTION
    MESSAGE_ERROR    = gtk.MESSAGE_ERROR

    BUTTON_OK     = (gtk.STOCK_OK, gtk.RESPONSE_OK)
    BUTTON_CLOSE  = (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
    BUTTON_CANCEL = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    BUTTON_YES    = (gtk.STOCK_YES, gtk.RESPONSE_YES)
    BUTTON_NO     = (gtk.STOCK_NO, gtk.RESPONSE_NO)

    RESPONSE_OK     = gtk.RESPONSE_OK
    RESPONSE_CLOSE  = gtk.RESPONSE_CLOSE
    RESPONSE_CANCEL = gtk.RESPONSE_CANCEL
    RESPONSE_YES    = gtk.RESPONSE_YES
    RESPONSE_NO     = gtk.RESPONSE_NO

    def __init__(self):
        self._widget = gtk.MessageDialog()
        super(MessageDialog, self).__init__()

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        self._widget.connect(signal, handler, function, *args, **kwargs)

    def onClose(self, widget, function, *args, **kwargs):
        function(self, *args, **kwargs)

    def onResponse(self, widget, responseID, function, *args, **kwargs):
        function(self, responseID, *args, **kwargs)
        self.hide()

    def setDefaultSize(self, width, height):
        self._widget.set_default_size(width, height)

    def setSize(self, width, height):
        self._widget.resize(width, height)

    def setType(self, messageType):
        self._widget.set_property('message-type', messageType)

    def setMainText(self, text):
        self._widget.set_markup('<b>%s</b>' % text)

    def setSecondaryText(self, text):
        self._widget.format_secondary_markup(text)

    def addButton(self, button):
        self._widget.add_button(button[0], button[1])

    def display(self):
        self._widget.show_all()

    def hide(self):
        self._widget.hide()

    def destroy(self):
        self._widget.destroy()

