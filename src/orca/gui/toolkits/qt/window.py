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

from PyQt4.QtGui import QWidget, QLayout, QBoxLayout
from PyQt4.QtCore import Qt, QObject, QSize, SIGNAL
from orca.gui.toolkits import window

class Window(window.Window):

    SIGNAL_CLOSE_EVENT = SIGNAL('closeEvent(QEvent)')

    def __init__(self, title):
        self._widget = QWidget()
        self._container = QBoxLayout(QBoxLayout.TopToBottom)
        self._widget.setLayout(self._container)
        super(Window, self).__init__(title)

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        def wrappedFunction(event=None):
            handler(self._widget, event, function, *args, **kwargs)

        QObject.connect(self._widget, signal, wrappedFunction)

    def onClose(self, widget, event, function, *args, **kwargs):
        function(self, event, *args, **kwargs)

    def getTitle(self):
        return str(self._widget.windowTitle())

    def setTitle(self, title):
        self._widget.setWindowTitle(title)

    def getDefaultSize(self):
        pass

    def setDefaultSize(self, width, height):
        size = QSize(width, height)
        self._widget.setMaximumSize(size)

    def getModal(self):
        return self._widget.isModal()

    def setModal(self, modal):
        if modal:
            self._widget.setWindowModality(Qt.Modal)
        else:
            self._widget.setWindowModality(Qt.NonModal)

    def getKeepAbove(self):
        pass

    def setKeepAbove(self, setting):
        pass

    def getDestroyWithParent(self):
        pass

    def setDestroyWithParent(self, setting):
        pass

    def getSkipTaskbarHint(self):
        pass

    def setSkipTaskbarHint(self, setting):
        pass

    def getUrgencyHint(self):
        pass

    def setUrgencyHint(self, setting):
        pass

    def getSkipPagerHint(self):
        pass

    def setSkipPagerHint(self, setting):
        pass

    def getDecorated(self):
        pass

    def setDecorated(self, setting):
        pass

    def getResizable(self):
        pass

    def setResizable(self, resizable):
        pass

    def getTransientFor(self):
        pass

    def setTransientFor(self, parent):
        pass

    def add(self, obj):
        widget = obj._widget
        if isinstance(widget, QLayout):
            self._container.addLayout(widget)
        elif isinstance(widget, QWidget):
            self._container.addWidget(widget)
        else:
            self._container.addItem(widget)

    def display(self):
        self._widget.show()

    def hide(self):
        self._widget.hide()

    def close(self):
        self._widget.close()

    def destroy(self):
        self._widget.destroy()

