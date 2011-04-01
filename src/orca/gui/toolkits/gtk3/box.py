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

from gi.repository import Gtk
from orca.gui.toolkits import box

class Box(box.Box):

    def __init__(self):
        super(Box, self).__init__()

    def add(self, child, expand=False, fill=False, padding=0):
        self._innerContainer.pack_start(child._widget, expand, fill, padding)

    def getHomogeneous(self):
        return self._innerContainer.get_homogeneous()

    def setHomogeneous(self, setting):
        self._innerContainer.set_homogeneous(setting)

    def getSpacing(self):
        return self._innerContainer.get_spacing()

    def setSpacing(self, spacing):
        self._innerContainer.set_spacing(spacing)

    def getPadding(self):
        return self._innerContainer.get_padding()

    def setPadding(self, top, bottom, left, right):
        self._alignment.set_padding(top, bottom, left, right)

    def setTopPadding(self, amount):
        self._alignment.set_property('top-padding', amount)

    def setLeftPadding(self, amount):
        self._alignment.set_property('left-padding', amount)

    def setBottomPadding(self, amount):
        self._alignment.set_property('bottom-padding', amount)

    def setRightPadding(self, amount):
        self._alignment.set_property('right-padding', amount)

    def setAlignment(self, xalign, yalign, xscale, yscale):
        self._alignment.set(xalign, yalign, xscale, yscale)

    def alignLeft(self):
        self._alignment.set_property('xalign', 0.0)

    def alignHCenter(self):
        self._alignment.set_property('xalign', 0.5)

    def alignRight(self):
        self._alignment.set_property('xalign', 1.0)

    def alignTop(self):
        self._alignment.set_property('yalign', 0.0)

    def alignVCenter(self):
        self._alignment.set_property('yalign', 0.5)

    def alignBottom(self):
        self._alignment.set_property('yalign', 1.0)

class HBox(box.HBox, Box):

    def __init__(self):
        self._widget = Gtk.HBox()
        self._alignment = Gtk.Alignment()
        self._widget.pack_start(self._alignment, True, True, 0)
        self._innerContainer = Gtk.HBox()
        self._alignment.add(self._innerContainer)
        super(HBox, self).__init__()

class VBox(box.VBox, Box):

    def __init__(self):
        self._widget = Gtk.VBox()
        self._alignment = Gtk.Alignment()
        self._widget.pack_start(self._alignment, True, True, 0)
        self._innerContainer = Gtk.VBox()
        self._alignment.add(self._innerContainer)
        super(VBox, self).__init__()
