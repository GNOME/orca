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

class Window(AbstractWidget):

    SIGNAL_CLOSE_EVENT = None

    def __init__(self, title):
        super(Window, self).__init__()
        self.setTitle(title)

    def _getHandlerForSignal(self, signal):
        if signal == self.SIGNAL_CLOSE_EVENT:
            return self.onClose

        return None

    def bind(self, signal, function, *args, **kwargs):
        pass

    def onClose(self, widget, event, function, *args, **kwargs):
        pass

    def getTitle(self):
        pass

    def setTitle(self, title):
        pass

    def getDefaultSize(self):
        pass

    def setDefaultSize(self, width, height):
        pass

    def getModal(self):
        pass

    def setModal(self, modal):
        pass

    def getKeepAbove(self):
        pass

    def setKeepAbove(self, setting):
        pass

    def getDestroyWithParent(self):
        pass

    def setDestroyWithParent(self, setting):
        pass

    def getSkipTaskbarHint(self):
        pass

    def setSkipTaskbarHint(self, setting):
        pass

    def getUrgencyHint(self):
        pass

    def setUrgencyHint(self, setting):
        pass

    def getSkipPagerHint(self):
        pass

    def setSkipPagerHint(self, setting):
        pass

    def getDecorated(self):
        pass

    def setDecorated(self, setting):
        pass

    def getResizable(self):
        pass

    def setResizable(self, resizable):
        pass

    def getTransientFor(self):
        pass

    def setTransientFor(self, parent):
        pass

    def add(self, obj):
        pass

    def display(self):
        pass

    def hide(self):
        pass

    def close(self):
        pass

    def destroy(self):
        pass
