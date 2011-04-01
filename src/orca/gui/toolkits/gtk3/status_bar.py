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
from orca.gui.toolkits import status_bar

class StatusBar(status_bar.StatusBar):

    def __init__(self, numberOfAreas=1):
        self._widget = Gtk.Statusbar()
        self._widget.connect('map', self.onMap)
        self._messageArea = self._widget.get_message_area()
        self._labels = self._messageArea.get_children()
        super(StatusBar, self).__init__(numberOfAreas)

    def createLabels(self, numberOfAreas):
        labels = [Gtk.Label() for i in range(numberOfAreas - 1)]
        map(lambda l: self._messageArea.pack_start(l, True, True, 0), labels)
        self._labels.extend(labels)

    def setLabelWidth(self, index, width):
        self._labels[index].set_size_request(width, -1)

    def setLabelWidthInChars(self, index, nChars):
        self._labels[index].set_width_chars(nChars)

    def getCurrentMessage(self, index=0):
        return self._labels[index].get_text()

    def setMessage(self, text, index=0):
        self._labels[index].set_text(text)

    def clearMessage(self, index=0):
        self.setMessage(self, '', index)

    def setSpacing(self, spacing):
        map(lambda l: l.set_padding(spacing, 0), self._labels)

    def onMap(self, widget):
        parent = widget.get_parent()
        while parent and not isinstance(parent, Gtk.Window):
            parent = parent.get_parent()

        if parent:
            parent.set_has_resize_grip(False)
