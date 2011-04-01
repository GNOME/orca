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

from gi.repository.Gtk import Label as gtkLabel
from orca.gui.toolkits import label

class Label(label.Label):
    def __init__(self, text):
        self._widget = gtkLabel()
        super(Label, self).__init__(text)

    def getDisplayedText(self):
        return self._widget.get_text()

    def setDisplayedText(self, text):
        self._widget.set_text(text)

    def getUseUnderline(self):
        return self._widget.get_use_underline()

    def setUseUnderline(self, setting):
        self._widget.set_use_underline(setting)

    def getUseMarkup(self):
        return self._widget.get_use_markup()

    def setUseMarkup(self, setting):
        self._widget.set_use_markup(setting)

    def getWrapText(self):
        return self._widget.get_line_wrap()

    def setWrapText(self, setting):
        self._widget.set_line_wrap(setting)

    def getMnemonicWidget(self):
        return self._widget.get_mnemonic_widget()

    def setMnemonicWidget(self, widget):
        self._widget.set_mnemonic_widget(widget._widget)
