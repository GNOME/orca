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

class Label(AbstractWidget):

    def __init__(self, text):
        super(Label, self).__init__()
        self.setDisplayedText(text)
        self.setUseUnderline(True)
        self.setUseMarkup(True)

    def getDisplayedText(self):
        pass

    def setDisplayedText(self, displayedText):
        pass

    def getUseUnderline(self):
        pass

    def setUseUnderline(self, setting):
        pass

    def setDisplayedText(self, displayedText):
        pass

    def getUseMarkup(self):
        pass

    def setUseMarkup(self, setting):
        pass

    def getWrapText(self):
        pass

    def setWrapText(self, setting):
        pass

    def getMnemonicWidget(self):
        pass

    def setMnemonicWidget(self, widget):
        pass
