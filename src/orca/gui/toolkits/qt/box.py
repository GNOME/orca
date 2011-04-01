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

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QMargins
from orca.gui.toolkits import box

class Box(box.Box):
    def __init__(self, direction):
        self._widget = QtGui.QBoxLayout(direction)
        super(Box, self).__init__()

    def add(self, obj, expand=False, fill=False, padding=0):
        # TODO: Find the equivalent in Qt to expand, fill, and padding.
        # Look at stretch and spacers
        child = obj._widget
        if isinstance(child, QtGui.QLayout):
            self._widget.addLayout(child)
        elif isinstance(child, QtGui.QWidget):
            self._widget.addWidget(child)
        else:
            self._widget.addItem(child)

    def getHomogeneous(self):
        pass

    def setHomogeneous(self, setting):
        pass

    def getSpacing(self):
        return self._widget.spacing()

    def setSpacing(self, spacing):
        self._widget.setSpacing(spacing)

    def getPadding(self):
        m = self._widget.contentsMargins()
        return m.top(), m.bottom(), m.left(), m.right()

    def setPadding(self, top, bottom, left, right):
        self._widget.setContentsMargins(left, top, right, bottom)

    def setTopPadding(self, amount):
        m = self._widget.contentsMargins()
        m.setTop(amount)

    def setLeftPadding(self, amount):
        m = self._widget.contentsMargins()
        m.setLeft(amount)

    def setBottomPadding(self, amount):
        m = self._widget.contentsMargins()
        m.setBottom(amount)

    def setRightPadding(self, amount):
        m = self._widget.contentsMargins()
        m.setRight(amount)

    def setAlignment(self, xalign, yalign, xscale, yscale):
        pass

    def alignLeft(self):
        self._widget.setAlignment(Qt.AlignLeft)

    def alignHCenter(self):
        self._widget.setAlignment(Qt.AlignHCenter)

    def alignRight(self):
        self._widget.setAlignment(Qt.AlignRight)

    def alignTop(self):
        self._widget.setAlignment(Qt.AlignTop)

    def alignVCenter(self):
        self._widget.setAlignment(Qt.AlignVCenter)

    def alignBottom(self):
        self._widget.setAlignment(Qt.AlignBottom)

class HBox(Box):

    def __init__(self):
        super(HBox, self).__init__(QtGui.QBoxLayout.LeftToRight)

class VBox(Box):

    def __init__(self):
        super(VBox, self).__init__(QtGui.QBoxLayout.TopToBottom)
