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

from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QObject, SIGNAL
from orca.gui.toolkits import message_dialog

class MessageDialog(message_dialog.MessageDialog):

    SIGNAL_CLOSE    = SIGNAL('closeEvent(QEvent)')
    SIGNAL_RESPONSE = SIGNAL('buttonClicked(QAbstractButton)')

    MESSAGE_INFO     = QMessageBox.Information
    MESSAGE_WARNING  = QMessageBox.Warning
    MESSAGE_QUESTION = QMessageBox.Question
    MESSAGE_ERROR    = QMessageBox.Critical

    BUTTON_OK     = QMessageBox.Ok
    BUTTON_CLOSE  = QMessageBox.Close
    BUTTON_CANCEL = QMessageBox.Cancel
    BUTTON_YES    = QMessageBox.Yes
    BUTTON_NO     = QMessageBox.No

    RESPONSE_OK     = QMessageBox.AcceptRole
    RESPONSE_CLOSE  = QMessageBox.RejectRole
    RESPONSE_CANCEL = QMessageBox.RejectRole
    RESPONSE_YES    = QMessageBox.YesRole
    RESPONSE_NO     = QMessageBox.NoRole

    def __init__(self):
        self._widget = QMessageBox()
        super(MessageDialog, self).__init__()

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        def wrappedFunction():
            handler(self._widget, function, *args, **kwargs)

        QObject.connect(self._widget, signal, wrappedFunction)

    def onResponse(self, widget, button, function, *args, **kwargs):
        function(self, button, *args, **kwargs)
        self.hide()

    def setDefaultSize(self, width, height):
        self._widget.setMinimumSize(width, height)

    def setSize(self, width, height):
        self._widget.adjustSize(width, height)

    def setType(self, messageType):
        self._widget.setIcon(messageType)

    def setMainText(self, text):
        self._widget.setText('<b>%s</b>' % text)

    def setSecondaryText(self, text):
        self._widget.setInformativeText(text)

    def addButton(self, button):
        self._widget.addButton(button)

    def display(self):
        self._widget.show()

    def hide(self):
        self._widget.hide()

    def destroy(self):
        self._widget.destroy()

