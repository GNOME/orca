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

class Entry(AbstractWidget):

    SIGNAL_TEXT_CHANGED = None

    def __init__(self, text, isPasswordText):
        super(Entry, self).__init__()
        self.setDisplayedText(text)
        self.setIsPasswordText(isPasswordText)

    def _getHandlerForSignal(self, signal):
        if signal == self.SIGNAL_TEXT_CHANGED:
            return self.onTextChanged

        return None

    def bind(self, signal, function, *args, **kwargs):
        pass

    def onTextChanged(self, widget, function, *args, **kwargs):
        pass

    def getIsPasswordText(self):
        pass

    def setIsPasswordText(self, isPasswordText):
        pass

    def getDisplayedText(self):
        pass

    def setDisplayedText(self, displayedText):
        pass

    def getActivatesDefault(self):
        pass

    def setActivatesDefault(self, activatesDefault):
        pass

    def setSelection(self):
        pass
