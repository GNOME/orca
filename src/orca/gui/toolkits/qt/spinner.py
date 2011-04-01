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

from PyQt4.QtGui import QSpinBox
from PyQt4.QtCore import QObject, SIGNAL
from orca.gui.toolkits import spinner

class Spinner(spinner.Spinner):

    SIGNAL_VALUE_CHANGED = SIGNAL('valueChanged(int)')
    SIGNAL_TEXT_CHANGED = SIGNAL('textChanged(QString)')

    def __init__(self):
        self._widget = QSpinBox()
        super(Spinner, self).__init__()

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        def wrappedFunction():
            handler(self._widget, function, *args, **kwargs)

        QObject.connect(self._widget, signal, wrappedFunction)

    def onValueChanged(self, widget, function, *args, **kwargs):
        function(self, *args, **kwargs)

    def onTextChanged(self, widget, function, *args, **kwargs):
        function(self, *args, **kwargs)

    def getRange(self):
        return self._widget.minimum(), self._widget.maximum()

    def setRange(self, minimum, maximum):
        self._widget.setRange(minimum, maximum)

    def getIncrements(self):
        # TODO: page?
        #self._widget.pageStep()
        return self._widget.singleStep(), self._widget.singleStep()

    def setIncrements(self, step, page):
        self._widget.setSingleStep(step)
        # TODO: page?

    def getValue(self):
        return self._widget.value()

    def setValue(self, value):
        self._widget.setValue(value)

    def getDisplayedText(self):
        return self._widget.text()

    def setDisplayedText(self, text):
        self._widget.setText(text)

    # TODO: Need to find the Qt equivalents
    def getPrecision(self):
        pass

    def setPrecision(self, digits):
        pass
