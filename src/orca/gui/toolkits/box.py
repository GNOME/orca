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

class Box(AbstractWidget):

    def __init__(self):
        super(Box, self).__init__()

    def add(self, child, expand=False, fill=False, padding=0):
        pass

    def getHomogeneous(self):
        pass

    def setHomogeneous(self, setting):
        pass

    def getSpacing(self):
        pass

    def setSpacing(self, spacing):
        pass

    def getPadding(self):
        pass

    def setPadding(self, top, bottom, left, right):
        pass

    def setTopPadding(self, amount):
        pass

    def setLeftPadding(self, amount):
        pass

    def setBottomPadding(self, amount):
        pass

    def setRightPadding(self, amount):
        pass

    def setAlignment(self, xalign, yalign, xscale, yscale):
        pass

    def alignLeft(self):
        pass

    def alignHCenter(self):
        pass

    def alignRight(self):
        pass

    def alignTop(self):
        pass

    def alignVCenter(self):
        pass

    def alignBottom(self):
        pass

class HBox(Box):

    def __init__(self):
        super(HBox, self).__init__()

class VBox(Box):

    def __init__(self):
        super(VBox, self).__init__()
