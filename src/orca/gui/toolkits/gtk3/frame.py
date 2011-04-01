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
from orca.gui.toolkits import frame

class Frame(frame.Frame):

    SHADOW_NONE       = Gtk.ShadowType.NONE
    SHADOW_IN         = Gtk.ShadowType.IN
    SHADOW_OUT        = Gtk.ShadowType.OUT
    SHADOW_ETCHED_IN  = Gtk.ShadowType.ETCHED_IN
    SHADOW_ETCHED_OUT = Gtk.ShadowType.ETCHED_OUT

    def __init__(self, labelText):
        self._widget = Gtk.Frame()
        super(Frame, self).__init__(labelText)

    def getLabel(self):
        return self._widget.get_label()

    def setLabel(self, labelText):
        self._widget.set_label('<b>%s</b>' % labelText)
        labelWidget = self._widget.get_label_widget()
        labelWidget.set_use_markup(True)

    def getShadowType(self):
        return self._widget.get_shadow_type()

    def setShadowType(self, shadowType):
        self._widget.set_shadow_type(shadowType)

    def add(self, child):
        self._widget.add(child._widget)

    def getBorderWidth(self):
        return self._widget.get_border_width()

    def setBorderWidth(self, width):
        self._widget.set_border_width(width)
