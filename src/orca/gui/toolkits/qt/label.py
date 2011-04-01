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

from PyQt4.QtGui import QLabel
from orca.gui.toolkits import label

class Label(label.Label):
    def __init__(self, text):
        self._widget = QLabel()
        super(Label, self).__init__(text)

    def getDisplayedText(self):
        return self._widget.text()

    def setDisplayedText(self, text):
        text = text.replace('_', '&')
        self._widget.setText(text)

    def getUseUnderline(self):
        return True

    def setUseUnderline(self, setting):
        # Qt seems to do this by default
        pass

    def getUseMarkup(self):
        # TODO: Find equivalent for Qt
        pass

    def setUseMarkup(self, setting):
        # TODO: Find equivalent for Qt
        pass

    def getWrapText(self):
        return self._widget.wordWrap()

    def setWrapText(self, setting):
        self._widget.setWordWrap(setting)

    def getMnemonicWidget(self):
        return self._widget.buddy()

    def setMnemonicWidget(self, widget):
        self._widget.setBuddy(widget._widget)
