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

from gi.repository.Gtk import Button as gtkButton
from orca.gui.toolkits import push_button

class PushButton(push_button.PushButton):

    SIGNAL_CLICKED = 'clicked'

    def __init__(self, label='', stock=None):
        self._widget = gtkButton(label, stock)
        super(PushButton, self).__init__(label, stock)
        self.setUseUnderline(True)

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        self._widget.connect(signal, handler, function, *args, **kwargs)

    def onClicked(self, widget, function, *args, **kwargs):
        function(self, *args, **kwargs)

    def getIsDefault(self):
        return self._widget.get_property('has-default')

    def setIsDefault(self, isDefault):
        if isDefault:
            self._widget.set_can_default(True)
            self._widget.set_property('has-default', True)

    def getUseUnderline(self):
        return self._widget.get_use_underline()

    def setUseUnderline(self, setting):
        self._widget.set_use_underline(setting)

    def getDisplayedText(self):
        return self._widget.get_label()

    def setDisplayedText(self, displayedText):
        self._widget.set_label(displayedText)

    def getUseStock(self):
        return self._widget.get_use_stock()

    def setUseStock(self, useStock):
        self._widget.set_use_stock(useStock)
