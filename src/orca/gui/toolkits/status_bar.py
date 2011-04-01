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

class StatusBar(AbstractWidget):

    def __init__(self, numberOfAreas=1):
        super(StatusBar, self).__init__()
        self.createLabels(numberOfAreas)

    def createLabels(self, numberOfAreas):
        pass

    def setLabelWidth(self, index, width):
        pass

    def setLabelWidth(self, index, width):
        pass

    def setLabelWidthInChars(self, index, nChars):
        pass

    def getCurrentMessage(self, index=0):
        pass

    def setMessage(self, text, index=0):
        pass

    def clearMessage(self, index=0):
        pass

    def enableSizeGrip(self, enable):
        pass

    def setSpacing(self, spacing):
        pass
