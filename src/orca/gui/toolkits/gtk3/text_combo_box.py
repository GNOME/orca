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

from gi.repository.Gtk import ComboBoxText as gtkComboBoxText
from orca.gui.toolkits import text_combo_box

class TextComboBox(text_combo_box.TextComboBox):

    SIGNAL_SELECTION_CHANGED = 'changed'

    def __init__(self, isEditable=False):
        if not isEditable:
            self._widget = gtkComboBoxText.new()
        else:
            self._widget = gtkComboBoxText.new_with_entry()
        super(TextComboBox, self).__init__(isEditable)

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        self._widget.connect(signal, handler, function, *args, **kwargs)

    def onSelectionChanged(self, widget, function, *args, **kwargs):
        function(self, *args, **kwargs)

    def addItemAtPosition(self, item, position):
        self._widget.insert_text(position, item)

    def removeItemFromPosition(self, position):
        self._widget.text_remove(position)

    def getSelectedItemPosition(self):
        return self._widget.get_active()

    def setSelectedItem(self, position):
        self._widget.set_active(position)

    def getSelectedText(self):
        return self._widget.get_active_text()

    def setTextColumn(self, column):
        self._widget.set_entry_text_column(column)

    def getIsEditable(self):
        pass

    def setIsEditable(self, setting):
        pass
