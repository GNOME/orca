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
from orca.gui.toolkits import frame

class Frame(frame.Frame):

    SHADOW_NONE       = QtGui.QFrame.Plain
    SHADOW_IN         = QtGui.QFrame.Sunken
    SHADOW_OUT        = QtGui.QFrame.Raised
    SHADOW_ETCHED_IN  = QtGui.QFrame.Sunken
    SHADOW_ETCHED_OUT = QtGui.QFrame.Raised

    def __init__(self, labelText):
        self._widget = QtGui.QGroupBox()
        super(Frame, self).__init__(labelText)

    def getLabel(self):
        self._widget.title()

    def setLabel(self, label):
        self._widget.setTitle(label)

    def getShadowType(self):
        pass

    def setShadowType(self, shadowType):
        pass

    def getBorderWidth(self):
        pass

    def setBorderWidth(self, width):
        pass

    def add(self, obj):
        child = obj._widget
        if isinstance(child, QtGui.QLayout):
            self._widget.setLayout(child)
        elif isinstance(child, QtGui.QWidget):
            self._widget.addWidget(child)
        else:
            self._widget.addItem(child)
