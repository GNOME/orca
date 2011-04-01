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

class Slider(AbstractWidget):

    SIGNAL_VALUE_CHANGED = None

    def __init__(self):
        super(Slider, self).__init__()

    def _getHandlerForSignal(self, signal):
        if signal == self.SIGNAL_VALUE_CHANGED:
            return self.onValueChanged

        return None

    def bind(self, signal, function, *args, **kwargs):
        pass

    def onValueChanged(self, widget, function, *args, **kwargs):
        pass

    def getRange(self):
        pass

    def setRange(self, minimum, maximum):
        pass

    def getIncrements(self):
        pass

    def setIncrements(self, step, page):
        pass

    def getValue(self):
        pass

    def setValue(self, value):
        pass

    def getPrecision(self):
        pass

    def setPrecision(self, digits):
        pass

    def getShowCurrentValue(self):
        pass

    def setShowCurrentValue(self, showCurrent):
        pass

    def getValuePosition(self):
        pass

    def setValuePosition(self, position):
        pass

class HSlider(Slider):

    def __init__(self):
        super(HSlider, self).__init__()

class VSlider(Slider):

    def __init__(self):
        super(VSlider, self).__init__()
