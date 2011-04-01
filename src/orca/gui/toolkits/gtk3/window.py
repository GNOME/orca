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

__id__    = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

from gi.repository.Gtk import Window as gtkWindow, VBox as gtkVBox
from orca.gui.toolkits import window

class Window(window.Window):

    SIGNAL_CLOSE_EVENT = 'delete-event'

    def __init__(self, title):
        self._widget = gtkWindow()
        self._container = gtkVBox()
        self._widget.add(self._container)
        self._isEmpty = True
        super(Window, self).__init__(title)

    def bind(self, signal, function, *args, **kwargs):
        handler = self._getHandlerForSignal(signal)
        if not handler:
            return

        self._widget.connect(signal, handler, function, *args, **kwargs)

    def onClose(self, widget, event, function, *args, **kwargs):
        function(self, event, *args, **kwargs)

    def getTitle(self):
        return self._widget.get_title()

    def setTitle(self, title):
        self._widget.set_title(title)

    def getDefaultSize(self):
        return self._widget.get_default_size()

    def setDefaultSize(self, width, height):
        self._widget.set_default_size(width, height)

    def getModal(self):
        return self._widget.get_modal()

    def setModal(self, modal):
        return self._widget.get_modal(modal)

    def getKeepAbove(self):
        return self._widget.get_keep_above()

    def setKeepAbove(self, setting):
        self._widget.set_keep_above(setting)

    def getDestroyWithParent(self):
        return self._widget.get_destroy_with_parent()

    def setDestroyWithParent(self, setting):
        self._widget.set_destroy_with_parent(setting)

    def getSkipTaskbarHint(self):
        return self._widget.get_skip_taskbar_hint()

    def setSkipTaskbarHint(self, setting):
        self._widget.set_skip_taskbar_hint(setting)

    def getUrgencyHint(self):
        return self._widget.get_urgency_hint()

    def setUrgencyHint(self, setting):
        self._widget.set_urgency_hint(setting)

    def getSkipPagerHint(self):
        return self._widget.get_skip_pager_hint()

    def setSkipPagerHint(self, setting):
        self._widget.set_skip_pager_hint(setting)

    def getDecorated(self):
        return self._widget.get_decorated()

    def setDecorated(self, setting):
        self._widget.set_decorated(setting)

    def getResizable(self):
        return self._widget.get_resizable()

    def setResizable(self, resizable):
        self._widget.set_resizable(resizable)

    def getTransientFor(self):
        return self._widget.get_transient_for()

    def setTransientFor(self, parent):
        self._widget.set_transient_for(parent)

    def add(self, obj):
        expand = self._isEmpty
        fill = self._isEmpty
        self._container.pack_start(obj._widget, expand, fill, 0)
        self._isEmpty = False

    def display(self):
        self._widget.show_all()

    def hide(self):
        self._widget.hide()

    def close(self):
        self._widget.close()

    def destroy(self):
        self._widget.destroy()
