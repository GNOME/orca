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

from PyQt4.QtGui import QCheckBox
from PyQt4.QtCore import QObject, SIGNAL
from orca.gui.toolkits import checkbox

class Checkbox(checkbox.Checkbox):

    SIGNAL_TOGGLED = SIGNAL('stateChanged(int)')

    def __init__(self, label, state):
        self._widget = QCheckBox()
        super(Checkbox, self).__init__(label, state)

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        def wrappedFunction():
            handler(self._widget, function, *args, **kwargs)

        QObject.connect(self._widget, signal, wrappedFunction)

    def onToggled(self, widget, function, *args, **kwargs):
        function(self, *args, **kwargs)

    def getState(self):
        return self._widget.isChecked()

    def setState(self, checked):
        if self.getState() != checked:
            self._widget.toggle()

    def getUseUnderline(self):
        return True

    def setUseUnderline(self, setting):
        # Qt seems to do this by default
        pass

    def getDisplayedText(self):
        return str(self._widget.text())

    def setDisplayedText(self, displayedText):
        displayedText = displayedText.replace('_', '&')
        self._widget.setText(displayedText)
