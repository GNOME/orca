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

from gi.repository.Gtk import Notebook as gtkNotebook
from orca.gui.toolkits import tabbed_widget

class TabbedWidget(tabbed_widget.TabbedWidget):

    SIGNAL_PAGE_CHANGED = 'switch-page'

    def __init__(self):
        self._widget = gtkNotebook()
        super(TabbedWidget, self).__init__()

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        self._widget.connect(signal, handler, function, *args, **kwargs)

    def onPageChanged(self, widget, page, index, function, *args, **kwargs):
        function(self, index, *args, **kwargs)

    def addPage(self, widget, label=None):
        if label:
            label = label._widget
        self._widget.append_page(widget._widget, label)

    def insertPage(self, widget, label=None, position=0):
        if label:
            label = label._widget
        self._widget.insert_page(widget._widget, label, position)

    def removePage(self, position):
        self._widget.remove_page(position)

    def getCurrentPosition(self):
        return self._widget.get_current_page()

    def getNthPage(self, index):
        return self._widget.get_nth_page(index)

    def getNPages(self):
        return self._widget.get_n_pages()

    def pageNum(self, widget):
        return self._widget.page_num(widget)

    def gotoPage(self, index):
        self._widget.set_current_page(index)

    def gotoNextPage(self):
        self._widget.next_page()

    def gotoPrevPage(self):
        self._widget.prev_page()

    def getScrollable(self):
        return self._widget.get_scrollable()

    def setScrollable(self, scrollable):
        self._widget.set_scrollable(scrollable)
