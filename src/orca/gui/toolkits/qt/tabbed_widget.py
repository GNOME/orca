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

from PyQt4.QtGui import QTabWidget, QWidget, QLayout
from PyQt4.QtCore import QObject, SIGNAL
from orca.gui.toolkits import tabbed_widget

class TabbedWidget(tabbed_widget.TabbedWidget):

    SIGNAL_PAGE_CHANGED = SIGNAL('currentChanged(int)')

    def __init__(self):
        self._widget = QTabWidget()
        super(TabbedWidget, self).__init__()
        self.setScrollable(False)

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        def wrappedFunction(index=-1):
            handler(self._widget, index, function, *args, **kwargs)

        QObject.connect(self._widget, signal, wrappedFunction)

    def onPageChanged(self, widget, index, function, *args, **kwargs):
        function(self, index, *args, **kwargs)

    def addPage(self, widget, label):
        position = self.getNPages()
        self.insertPage(widget, label, position)

    def insertPage(self, widget, label, position=0):
        widget = widget._widget
        qwidget = widget
        if not isinstance(qwidget, QWidget):
            qwidget = QWidget()

        self._widget.insertTab(position, qwidget, label._widget.text())
        if isinstance(widget, QLayout):
            qwidget.setLayout(widget)

    def removePage(self, position):
        self._widget.removeTab(position)

    def getCurrentPosition(self):
        return self._widget.currentIndex()

    def getNthPage(self, index):
        return self._widget.widget(index)

    def getNPages(self):
        return self._widget.count()

    def pageNum(self, widget):
        return self._widget.indexOf(widget)

    def gotoPage(self, index):
        page = self._widget.widget(index)
        self._widget.setCurrentWidget(page)

    def gotoNextPage(self):
        index = self._widget.getCurrentPosition()
        self._widget.gotoPage(index+1)

    def gotoPrevPage(self):
        index = self._widget.getCurrentPosition()
        self._widget.gotoPage(index-1)

    def getScrollable(self):
        return self._widget.usesScrollButtons()

    def setScrollable(self, scrollable):
        self._widget.setUsesScrollButtons(scrollable)
