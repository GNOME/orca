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

from gi.repository.Gtk import Scale as gtkScale
from gi.repository.Gtk import HScale as gtkHScale
from gi.repository.Gtk import VScale as gtkVScale
from orca.gui.toolkits import slider

class Slider(slider.Slider):

    SIGNAL_VALUE_CHANGED = 'value-changed'

    def __init__(self):
        super(Slider, self).__init__()

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        self._widget.connect(signal, handler, function, *args, **kwargs)

    def onValueChanged(self, widget, function, *args, **kwargs):
        function(self, *args, **kwargs)

    def getRange(self):
        return self._widget.get_range()

    def setRange(self, minimum, maximum):
        self._widget.set_range(minimum, maximum)

    def getIncrements(self):
        return self._widget.get_increments()

    def setIncrements(self, step, page):
        self._widget.set_increments(step, page)

    def getValue(self):
        return self._widget.get_value()

    def setValue(self, value):
        self._widget.set_value(value)

    def getPrecision(self):
        return self._widget.get_digits()

    def setPrecision(self, digits):
        self._widget.set_digits(digits)

    def getShowCurrentValue(self):
        return self._widget.get_draw_value()

    def setShowCurrentValue(self, showCurrent):
        self._widget.set_draw_value(showCurrent)

    def getValuePosition(self):
        return self._widget.get_value_position()

    def setValuePosition(self, position):
        self._widget.set_value_position(position)

class HSlider(slider.HSlider, Slider):

    def __init__(self):
        self._widget = gtkHScale()
        super(HSlider, self).__init__()

class VSlider(slider.VSlider, Slider):

    def __init__(self):
        self._widget = gtkVScale()
        super(VSlider, self).__init__()
