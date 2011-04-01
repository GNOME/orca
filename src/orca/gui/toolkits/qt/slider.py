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

from PyQt4.QtGui import QSlider
from PyQt4.QtCore import Qt, QObject, SIGNAL
from orca.gui.toolkits import slider

class Slider(slider.Slider):

    SIGNAL_VALUE_CHANGED = SIGNAL('valueChanged(int)')

    def __init__(self, orientation):
        self._widget = QSlider(orientation)
        super(Slider, self).__init__()

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        def wrappedFunction():
            handler(self._widget, function, *args, **kwargs)

        QObject.connect(self._widget, signal, wrappedFunction)

    def onValueChanged(self, widget, function, *args, **kwargs):
        function(self, *args, **kwargs)

    def getRange(self):
        return self._widget.minimum(), self._widget.maximum()

    def setRange(self, minimum, maximum):
        self._widget.setMinimum(minimum)
        self._widget.setMaximum(maximum)

    def getIncrements(self):
        return self._widget.singleStep(), self._widget.pageStep()

    def setIncrements(self, step, page):
        self._widget.setSingleStep(step)
        self._widget.setPageStep(page)

    def getValue(self):
        return self._widget.value()

    def setValue(self, value):
        super(Slider, self).setValue(value)

    def getValuePosition(self):
        return self._widget.tickPosition()

    def setValuePosition(self, position):
        self._widget.setTickPosition(position)

    # TODO: Need to find the Qt equivalents
    def getPrecision(self):
        pass

    def setPrecision(self, digits):
        pass

    def getShowCurrentValue(self):
        pass

    def setShowCurrentValue(self, showCurrent):
        pass

class HSlider(Slider):

    def __init__(self):
        super(HSlider, self).__init__(Qt.Horizontal)

class VSlider(Slider):

    def __init__(self):
        super(VSlider, self).__init__(Qt.Vertical)
