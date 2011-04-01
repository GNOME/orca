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

from gi.repository import Gtk
from orca.gui.toolkits import message_dialog

class MessageDialog(message_dialog.MessageDialog):

    SIGNAL_CLOSE    = 'close'
    SIGNAL_RESPONSE = 'response'

    MESSAGE_INFO     = Gtk.MessageType.INFO
    MESSAGE_WARNING  = Gtk.MessageType.WARNING
    MESSAGE_QUESTION = Gtk.MessageType.QUESTION
    MESSAGE_ERROR    = Gtk.MessageType.ERROR

    BUTTON_OK     = (Gtk.STOCK_OK, Gtk.ResponseType.OK)
    BUTTON_CLOSE  = (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
    BUTTON_CANCEL = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
    BUTTON_YES    = (Gtk.STOCK_YES, Gtk.ResponseType.YES)
    BUTTON_NO     = (Gtk.STOCK_NO, Gtk.ResponseType.NO)

    RESPONSE_OK     = Gtk.ResponseType.OK
    RESPONSE_CLOSE  = Gtk.ResponseType.CLOSE
    RESPONSE_CANCEL = Gtk.ResponseType.CANCEL
    RESPONSE_YES    = Gtk.ResponseType.YES
    RESPONSE_NO     = Gtk.ResponseType.NO

    def __init__(self):
        self._widget = Gtk.MessageDialog()
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
        self._widget.set_size_request(width, height)
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

